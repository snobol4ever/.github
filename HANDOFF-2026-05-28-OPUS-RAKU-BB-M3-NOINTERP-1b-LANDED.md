# HANDOFF-2026-05-28-OPUS-RAKU-BB-M3-NOINTERP-1b-LANDED

**Session:** 2026-05-28 Opus 4.7
**Goal:** GOAL-RAKU-BB — M3-RK-NOINTERP-1b
**Result:** ✅ LANDED — mode-3 native 18→19 PASS (rk_range_for flipped CRASH→PASS), 14→13 CRASH

## Step closed

**M3-RK-NOINTERP-1b** — SM_BB_INVOKE MEDIUM_BINARY arm wired. Was a 5-byte no-op stub
(`E8 00 00 00 00`); is now a full scratch-buffer-flush implementation that inlines
the BB graph into the SM byte stream.

## Architecture discovered + addressed

The watermark from the predecessor session recommended path (a): translate the
MEDIUM_TEXT arm shape into a raw-byte sequence. That recommendation glossed over a
fundamental architectural mismatch between mode-3 (`sm_run_native`) and the BB
template emission protocol:

- **SM templates in mode-3** return `std::string` of raw bytes from their `_str()`
  functions; the wrapper calls `emit_text_n(s.data(), s.size())` which writes via
  `g_emit_sink` (a FILE* — `mem` memstream in `sm_run_native`).
- **BB templates in MEDIUM_BINARY mode** route through `bb_emit_asm_result` →
  `bb_emit_byte` → `bb_emit_buf` (a SEPARATE fixed buffer). `bb_emit_buf` is NULL in
  mode-3 because `sm_run_native` never calls `emitter_init_binary`.

So calling `walk_bb_node_str_c(gen)` inside SM_BB_INVOKE BINARY (mirroring MEDIUM_TEXT
exactly) crashed: `bb_emit_byte` aborts when `bb_emit_buf` is NULL.

**Resolution:** scratch-buffer-flush approach. SM_BB_INVOKE BINARY arm now:

1. Saves outer global emitter state (`bb_emit_buf`, `bb_emit_pos`, `bb_emit_size`,
   `bb_emit_overflow`, `bb_patch_count`, `bb_patch_list` contents, **and `g_emit_sink`
   via new `emit_io_get_sink()` accessor**).
2. Allocates 4KB heap scratch + per-sid 1-byte malloc'd entry-flag.
3. Points `bb_emit_buf` at scratch; zeroes pos/size/overflow/patch_count.
4. Sets up γ/ω/β/fresh/done labels via `emit_label_initf` on stack locals; assigns
   `g_emit.lbl_*` so BB templates see them.
5. Emits pre-amble bytes via `bb_emit_byte`/`bb_emit_u64`: entry-flag dispatch
   (`movabs rax, &flag; cmp byte ptr[rax], 0; je fresh; jmp lβ; fresh: mov [rax], 1`).
6. Calls `walk_bb_node(gen, NULL)` — BB template (bb_to_by.cpp) emits its bytes into
   our scratch via the standard MEDIUM_BINARY path, registering rel32 patches in
   `bb_patch_list` against γ/ω and a β-define site.
7. Defines γ at current pos, emits `mov edi,1; movabs rax,&rt_set_last_ok; call rax;
   jmp done`. This resolves all pending γ patches in-place via `bb_label_define`.
8. Defines ω at current pos, emits flag-reset + `rt_set_last_ok(0)`; falls through.
9. Defines done at current pos.
10. Calls `bb_emit_end()` to verify all patches resolved.
11. Restores outer state including `g_emit_sink`.
12. Copies scratch bytes into a `std::string` and returns it — the SM wrapper's
    `emit_text_n` then writes them into `sm_run_native`'s `mem` memstream.

## Critical bug found mid-session

First wiring produced empty output (rk_range_for CRASH→FAIL): `walk_bb_node` line 517
calls `emit_io_set_sink(out)` with `out=NULL`, which zeroes `g_emit_sink`. Without
saving+restoring, every subsequent `emit_text_n` in `sm_run_native` after the first
SM_BB_INVOKE silently drops bytes — the SM blob ends up truncated, and the C-side
`call *code` returns immediately after the truncation point.

Fix: added `emit_io_get_sink()` accessor + save/restore at the lambda's entry/exit.
After this fix, rk_range_for output is byte-identical to `.expected`.

## Files touched

- `src/emitter/SM_templates/sm_bb_switch.cpp` — MEDIUM_BINARY arm body (~125 lines)
- `src/emitter/emit_io.c`, `emit_io.h` — new `emit_io_get_sink()` accessor
- `src/emitter/emit_bb.c` — `case BB_TO_BY: FILL(...)` added to `walk_bb_flat`
- `src/emitter/BB_templates/bb_to_by.cpp` — parallel ascending-sites fix in
  `bin.sites` (reordered `{fail_off+2, succ_off+1, back_off}` →
  `{back_off, fail_off+2, succ_off+1}` to match the canonical-5 fix in `bb_to.cpp`).

## Gates (SCRIP `48ca4e21`)

```
GATE-RK    mode-2:               23/33  HOLD
GATE-RK3   --run SCRIP_M3_NATIVE: 19/33 PASS, 1 FAIL, 13 CRASH (was 18/1/14)
GATE-RK4   mode-4:               26/33  HOLD
Smoke raku:    5/5  HOLD
Smoke prolog:  5/5  HOLD
Smoke snobol4: 13/13 HOLD
Smoke icon:    5/5  HOLD
FACT RULE grep: 0
Build: clean
```

## What this unblocks

The wiring is general — any BB graph kind that `walk_bb_node` dispatches to with a
correct MEDIUM_BINARY arm will now work under mode-3 native. BB_TO_BY (this rung)
is the simplest. Future rungs that should now be a smaller surgery (template-level
only, not architectural):

- **M3-RK-NOINTERP-1c** — `bb_iterate.cpp` MEDIUM_BINARY arm (r12→rt_push_int
  conversion, same pattern as `bb_to.cpp`/`bb_to_by.cpp` already done). Closes
  `rk_for_array{,_simple,_underscore}`, `rk_map_grep_sort24`.
- **M3-RK-NOINTERP-1d** — `bb_upto.cpp` MEDIUM_BINARY arm. Closes `rk_gather`,
  `rk_given18`.
- **M3-RK-NOINTERP-1e** — `bb_suspend.cpp` / `bb_seq.cpp` MEDIUM_BINARY arms.

Each subsequent step should be a ~10-30 line change in the relevant BB template's
MEDIUM_BINARY arm (mirror the `mov rdi, rcx; movabs rax, &rt_push_int; call rax`
convention already established in bb_to.cpp / bb_to_by.cpp). The SM_BB_INVOKE wiring
landed here works for all of them — they share the same dispatch contract.

## Remaining mode-3 CRASH (13)

Cluster 1 (BB template MEDIUM_BINARY conversion needed) — 7 tests:
  rk_fileio38, rk_for_array, rk_for_array_simple, rk_for_array_underscore,
  rk_gather, rk_given18, rk_map_grep_sort24

Cluster 3 (regex/NFA, DEFERRED to GOAL-RAKU-PAT-BB) — 6 tests:
  rk_re32, rk_re33, rk_re34, rk_re35, rk_re37, rk_regex23

Mode-3 FAIL (1): rk_junctions — blocked on Lon Q9-Q12 (RK-BB-4 substrate).

## NEXT — recommended order

1. **M3-RK-NOINTERP-1c (bb_iterate)** — biggest impact (closes 4 tests: array iteration).
   Read `bb_iterate.cpp` MEDIUM_BINARY arm; find the r12-relative writes; replace with
   `mov rdi, rcx; movabs rax, &rt_push_int; call rax` (same surgery as bb_to_by.cpp
   M3-RK-NOINTERP-1a). Verify with rk_for_array.

2. **M3-RK-NOINTERP-1d (bb_upto)** — closes rk_gather, rk_given18. Same pattern.

3. **M3-RK-NOINTERP-1e (bb_suspend / bb_seq)** — closes any remaining gather/lazy-Seq
   cases. May be needed for some tests in Cluster 1 too.

Each step: edit the BB template's MEDIUM_BINARY arm; verify ascending `bin.sites`;
build; run `/tmp/gate_rk3.sh` (the mode-3 measurement script from this session — at
`/tmp/gate_rk3.sh`); verify smoke + mode-2 + mode-4 gates HOLD.

## Verification commands

```bash
cd /home/claude/SCRIP
make -j4 scrip libscrip_rt
bash scripts/test_raku_ir_rungs.sh        # GATE-RK
bash scripts/test_raku_mode4_rung.sh      # GATE-RK4
bash scripts/test_smoke_raku.sh           # smoke
SCRIP_M3_NATIVE=1 ./scrip --run test/raku/rk_range_for.raku  # spot-check PASS
```
