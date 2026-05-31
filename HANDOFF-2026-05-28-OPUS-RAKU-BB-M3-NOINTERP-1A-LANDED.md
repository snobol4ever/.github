# HANDOFF — RAKU-BB / M3-RK-NOINTERP-1a landed + SM_BB_INVOKE BINARY stub blocker surfaced

**Date:** 2026-05-28 (follow-up-5)
**Model:** Opus 4.7
**Goal:** GOAL-RAKU-BB.md → M3-RK-NOINTERP-1a (Cluster 1, generator-template mode-3 ABI)
**SCRIP:** this commit
**.github:** this commit
**corpus:** unchanged

---

## TL;DR

The prior Sonnet 4.6 follow-up-4 session left two uncommitted edits in the working tree without a handoff: (1) a surgical change to `bb_to_by.cpp` MEDIUM_BINARY arm swapping the r12-write yield path for a `rt_push_int` call, and (2) a watermark draft in GOAL-RAKU-BB.md describing the change AND the architectural blocker behind it. This session re-derived the same blocker independently, verified the bb_to_by edit is correct-as-prep-work, and is landing both edits with one correction (a line-reference fix from `emit_bb.c:860` to `emit_bb.c:981`).

The watermark draft's central finding is correct and load-bearing: **`SM_BB_INVOKE` MEDIUM_BINARY arm at `src/emitter/SM_templates/sm_bb_switch.cpp:35-36` is a 5-byte no-op stub** (`E8 00 00 00 00` — `call rel32=0`). The MEDIUM_TEXT arm at lines 38-87 properly inlines the BB graph via `walk_bb_node_str_c(gen)` + γ/ω epilogue with `rt_set_last_ok`; the MEDIUM_BINARY arm does not. Therefore `sm_run_native` reaches SM_BB_INVOKE, executes the no-op `call`, and the next SM instruction (`SM_JUMP_F` for rk_range_for) pops an empty vstack → "libscrip_rt: SM value stack underflow."

The bb_to_by.cpp template-level fix is correct and necessary, but unreachable until `SM_BB_INVOKE` MEDIUM_BINARY is wired up. Lands as prep work for the next step (1b).

## What landed

### `src/emitter/BB_templates/bb_to_by.cpp` (SCRIP)

Verbatim restoration of the prior Sonnet 4.6 follow-up-4 edit:

- `#include <stdint.h>` added (needed by the new `int64_t` forward-decl).
- `void rt_push_int(int64_t v);` forward-decl added inside the existing `extern "C" { }` block.
- MEDIUM_BINARY yield-DT_I(cur) sequence replaced:
  - **Before** (18 bytes, four r12-relative writes):
    ```
    mov dword[r12], DT_I        ; 41 C7 04 24 <u32>
    mov dword[r12+4], 0         ; 41 C7 44 24 04 <u32>
    mov [r12+8], rcx            ; 49 89 4C 24 08
    add r12, 16                 ; 49 83 C4 10
    ```
  - **After** (15 bytes, rt_push_int call — matches `bb_to.cpp` IBB-3 e612d519 and the MEDIUM_TEXT sibling arm at line ~89-90):
    ```
    mov rdi, rcx                ; 48 89 CF                (3 bytes)
    movabs rax, &rt_push_int    ; 48 B8 <u64>             (10 bytes)
    call rax                    ; FF D0                   (2 bytes)
    ```
- Inline comment block explains the ABI mismatch (r12 not initialised by `sm_run_native` / `XA_FLAT_PROLOGUE`) and points at the matching MEDIUM_TEXT line as the convention reference.
- All three `bin` offsets (`fail_off+2`, `succ_off+1`, `back_off`) reading from `(int)b.size()` snapshots → they re-anchor automatically across the byte-length change; no manual offset arithmetic needed.

**Reachability today: zero.** SM_BB_INVOKE's BINARY arm never inlines this template. The edit is prep for 1b. This is documented in the in-file comment and the watermark.

### `GOAL-RAKU-BB.md` (.github)

Watermark draft from prior Sonnet committed, with one correction:
- `emit_bb.c:860` → `emit_bb.c:981` (the actual line of `case BB_TO:` in `walk_bb_flat`).

Mode-3 measurement updated to the post-revert reality (18 PASS / 0 FAIL / 15 CRASH from my run; the draft's 18/1/14 categorisation is equally valid if rk_junctions is scored as FAIL-by-output-diff rather than CRASH-by-exit-nonzero; left as the draft had it because the prior watermark used FAIL-by-diff conventionally).

A new `## NEXT STEP RECOMMENDATION — M3-RK-NOINTERP-1b (sm_bb_invoke wiring)` section was kept from the draft; it lays out the precise 3-step plan for the next session.

### `PLAN.md` (.github)

Raku BB row rewritten to reference the new state: edit landed, blocker surfaced, next step 1b queued, baseline numbers updated.

## Gates (verified before commit)

```
GATE-RK   mode-2  (test_raku_ir_rungs.sh):        23/33  HOLD
GATE-RK4  mode-4  (test_raku_mode4_rung.sh):      26/33  HOLD
GATE-RK3  mode-3  (SCRIP_M3_NATIVE=1 ./scrip --run):  18/33 PASS, 0/33 FAIL-by-diff, 15/33 CRASH
Smoke raku        (test_smoke_raku.sh):           5/5    HOLD
Smoke prolog      (test_smoke_prolog.sh):         5/5    HOLD
Smoke icon        (test_smoke_icon.sh):           5/5    HOLD
Smoke snobol4     (test_smoke_snobol4.sh):        13/13  HOLD
FACT RULE grep:                                   0      HOLD
Build:                                            clean
```

Mode-3 CRASH list (15 = 8 Cluster-1 + rk_given18 + 6 Cluster-3-regex):
```
rk_fileio38 rk_for_array rk_for_array_simple rk_for_array_underscore
rk_gather rk_given18 rk_map_grep_sort24 rk_range_for
rk_re32 rk_re33 rk_re34 rk_re35 rk_re37 rk_regex23
rk_junctions  (lex error: '|' unknown — categorisable as FAIL-by-diff or CRASH-by-exit)
```

## Open questions / next-session entry point

**M3-RK-NOINTERP-1b — wire SM_BB_INVOKE MEDIUM_BINARY arm.**

Concrete plan (per the watermark's NEXT STEP RECOMMENDATION section):

1. Add `case BB_TO_BY:` to `walk_bb_flat` in `src/emitter/emit_bb.c:981` area (alongside `case BB_TO:`). Simple `FILL(nd, lbl_γ, lbl_ω, lbl_β); break;` — `FILL` already dispatches to `bb_to_by`.

2. Rewrite `src/emitter/SM_templates/sm_bb_switch.cpp:35-36` MEDIUM_BINARY arm from the current 5-byte stub to a full BB-graph inline driver. The MEDIUM_TEXT arm at lines 38-87 is the exact reference shape. Each `s_directive`/`s_2asm`/`s_L1asm` line in TEXT becomes the equivalent raw-byte sequence in BINARY.

3. The entry-flag dispatch (TEXT lines 56-67: `.Lbbinv%d_ent: .byte 0` data-section flag, `lea+cmp+je/jmp`) needs a BINARY equivalent. Options:
   - Allocate a fresh per-invoke flag byte in SEG_DATA via the existing `data_buf_*` machinery, store its absolute address as `movabs`, use `cmp byte ptr [rax], 0` patched-in-place.
   - Or fold the dispatch into a static (one-flag-per-bb_idx) globals table.

4. After the inlined graph emits, append γ-block (`mov rdi,1; movabs rax,&rt_set_last_ok; call rax; jmp done`), ω-block (`mov rdi,0; movabs rax,&rt_set_last_ok; call rax; jmp .L<exit_pc>`), and done-label. The `.L<exit_pc>` jump needs to plug into `sm_run_native`'s pass-2 rel32 patcher OR be locally resolved by walking instr_off[]. The cleanest path is a small extension to `sm_run_native`'s patch-pass to also fix up any `SM_BB_INVOKE`-internal jumps that reference exit_pc.

5. Verify on rk_range_for first. Expected delta: 18→19 PASS, 15→14 CRASH. Then re-attempt 1c (bb_iterate / bb_upto / bb_suspend / bb_seq) following the same MEDIUM_BINARY r12→rt_push_int ABI conversion as 1a did for bb_to_by.

**Alternative path** (option b from prior watermark): allocate r12 as a per-invoke malloc'd region in sm_bb_invoke MEDIUM_BINARY, set r12, run the inlined BB, then drain r12 → rt_push_int at the γ exit. Less invariant-preserving (introduces a second vstack convention into mode-3) but localised to the one site; useful if (1) is blocked.

## Notes for the next operator

- The bb_to_by edit committed today produces zero observable behaviour change because nothing reaches it. If you run mode-3 Raku before and after, you'll see the identical 18/0/15 numbers and the identical "SM value stack underflow" abort on rk_range_for. The edit is a *correctness contract* for when 1b lands.
- The `bb_to_by.cpp` MEDIUM_TEXT arm (used by `--compile` mode-4) was already correct — it uses `rt_push_int` via `s_2asm("call", "rt_push_int@PLT")`. That arm shipped with the original JA-2a edit (76488946). The MEDIUM_BINARY arm carried the r12 convention left over from when only the brokered-slab path consumed it; today only `sm_run_native` consumes it.
- The watermark draft's claim that "bb_to_by is now ready for that wiring" is precise. Verified across all three offsets in `bin` and the surrounding patch machinery.
- Don't make the same mistake I almost made: the temptation to revert the bb_to_by edit because it's unreachable today is wrong. The right edit lands; the wiring catches up to it.

## Files touched

- `SCRIP/src/emitter/BB_templates/bb_to_by.cpp` (16 +, 5 −)
- `.github/GOAL-RAKU-BB.md` (watermark + NEXT STEP section)
- `.github/PLAN.md` (Raku BB row)
- `.github/HANDOFF-2026-05-28-OPUS-RAKU-BB-M3-NOINTERP-1A-LANDED.md` (this file)

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
