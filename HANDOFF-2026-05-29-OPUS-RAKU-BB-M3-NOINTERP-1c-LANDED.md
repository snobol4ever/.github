# HANDOFF-2026-05-29-OPUS-RAKU-BB-M3-NOINTERP-1c-LANDED

**Session:** 2026-05-29 Opus 4.7
**Goal:** GOAL-RAKU-BB — M3-RK-NOINTERP-1c
**Result:** ✅ LANDED — mode-3 native 19→25 PASS (+6 CRASH→PASS), 13→7 CRASH

## Step closed

**M3-RK-NOINTERP-1c** — `bb_iterate.cpp` Raku-path MEDIUM_BINARY arm wired. Was a
1-line stub:

```cpp
if (MEDIUM_BINARY) {
    return s_comment("# bb_iterate BINARY Raku — TODO");
}
```

Now a full ~110-line raw-x86 mirror of the existing MEDIUM_TEXT arm. The TEXT arm
already used `@PLT` calls for the four helpers; in BINARY those become absolute
`movabs rax, &fn ; call rax` because mode-3 native (`sm_run_native`) is not PLT-
resolved (matches the bb_to.cpp / bb_to_by.cpp pattern for rt_push_int from 1a/1b).

## What flipped

Mode-3 native (`SCRIP_M3_NATIVE=1 ./scrip --run test/raku/*.raku`):

| Test | Before | After |
|---|---|---|
| `rk_fileio38` | CRASH | **PASS** |
| `rk_for_array` | CRASH | **PASS** |
| `rk_for_array_simple` | CRASH | **PASS** |
| `rk_for_array_underscore` | CRASH | **PASS** |
| `rk_given18` | CRASH | **PASS** |
| `rk_map_grep_sort24` | CRASH | **PASS** |

**6 tests flipped, not the 4 the predecessor watermark predicted.** The extra two
(rk_fileio38, rk_given18) also route through `bb_iterate` because lower_every's
TT_ITERATE(TT_FNC) arm and `given` over array iterables both materialize into a
__arr_N temp and call lower_raku_iterate_arr.

## Architecture (terse)

`SM_BB_INVOKE` (mode-3 scratch flush, from 1b) → walk_bb_node(gen, NULL) →
bb_iterate.cpp Raku BINARY arm. The wrapper:

- pre-allocates `lβ`/`lγ`/`lω` labels via `emit_label_initf` and sets
  `g_emit.lbl_{β,γ,ω}_p`
- defines γ post-amble (sets last_ok=1, jumps to done) AFTER the inner template
- defines ω post-amble (resets entry_flag, last_ok=0, falls through to done)
- requires the inner template to (a) define lβ at the retry-entry offset via
  `bin.sites` with is_def=true, (b) emit rel32 patches against lγ/lω with
  is_def=false, (c) keep bin.sites in **ascending offset order** (per the 1b
  M3-RK-NOINTERP-1b post-mortem on bb_to_by:142)

## Byte layout written

```
α:    movabs rax, &pBB->counter         48 B8 [u64]
      mov qword ptr [rax], 0            48 C7 00 [u32]
      jmp .Lload (rel32 self-patch)     E9 [rel32]
β-def (= .Lload):
      movabs rdi, pBB->sval             48 BF [u64]
      movabs rax, NV_GET_fn ; call rax  48 B8 [u64] ; FF D0
      mov rsi, rax ; shr rsi, 32        48 89 C6 ; 48 C1 EE 20
      mov r10, rdx                      49 89 D2
      test esi, esi ; jnz .Lhave        85 F6 ; 0F 85 [rel32 self-patch]
      test r10, r10 ; jz  .Lhave        4D 85 D2 ; 0F 84 [rel32 self-patch]
      push r10 ; sub rsp, 8             41 52 ; 48 83 EC 08
      mov rdi, r10                      4C 89 D7
      movabs rax, strlen ; call rax     48 B8 [u64] ; FF D0
      mov rsi, rax                      48 89 C6
      add rsp, 8 ; pop r10              48 83 C4 08 ; 41 5A
.Lhave:
      movabs rax, &cnt ; mov rcx, [rax] 48 B8 [u64] ; 48 8B 08
      cmp rcx, rsi                      48 39 F1
      jge lω (rel32 bin.sites)          0F 8D [rel32 → lω]
      mov r9, rcx                       49 89 C9
.Lscan:
      cmp rcx, rsi                      48 39 F1
      jge .Lsend (rel32 self-patch)     0F 8D [rel32]
      cmp byte [r10+rcx], 1             41 80 3C 0A 01
      je .Lsend (rel32 self-patch)      0F 84 [rel32]
      inc rcx                           48 FF C1
      jmp .Lscan (rel32 backward)       E9 [rel32]
.Lsend:
      mov r8, rcx ; sub r8, r9          49 89 C8 ; 4D 29 C8
      lea r11, [r10+r9]                 4F 8D 1C 0A
      inc rcx                           48 FF C1
      movabs rax, &cnt ; mov [rax], rcx 48 B8 [u64] ; 48 89 08
      push r8 ; push r11                41 50 ; 41 53
      mov rdi, r8 ; add rdi, 1          4C 89 C7 ; 48 83 C7 01
      movabs rax, GC_malloc ; call rax  48 B8 [u64] ; FF D0
      pop r11 ; pop r8                  41 5B ; 41 58
      mov rdi, rax ; mov rsi, r11       48 89 C7 ; 4C 89 DE
      mov rcx, r8                       4C 89 C1
      push rax ; rep movsb ; pop rax    50 ; F3 A4 ; 58
      mov byte [rax+r8], 0              42 C6 04 00 00
      mov rdi, rax ; mov rsi, r8        48 89 C7 ; 4C 89 C6
      movabs rax, rt_push_str ; call    48 B8 [u64] ; FF D0
      jmp lγ (rel32 bin.sites)          E9 [rel32 → lγ]
```

bin.sites ascending: `{beta_off, fail_off+2, succ_off+1}` paired with
`{lβ_p (define), lω_p, lγ_p}`.

## Header changes

```cpp
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
extern "C" {
#include "descr.h"                      // for DESCR_t in NV_GET_fn signature
extern DESCR_t NV_GET_fn(const char *name);
extern void    rt_push_str(const char *s, uint32_t slen);
extern void *  GC_malloc(size_t n);
extern size_t  strlen(const char *);
}
```

## Verification

```bash
cd /home/claude/SCRIP
make -j4 scrip libscrip_rt
bash scripts/test_raku_ir_rungs.sh       # GATE-RK   23/33   HOLD
bash scripts/test_raku_mode4_rung.sh     # GATE-RK4  26/33   HOLD
bash scripts/test_smoke_raku.sh          # smoke      5/5    HOLD
bash /tmp/gate_rk3.sh                     # GATE-RK3 25/33   PASS  (was 19/33)
```

All smokes HOLD: prolog 5/5, icon 5/5, snobol4 13/13. FACT RULE grep = 0.
Build clean.

## Pruned GOAL-RAKU-BB.md

Same session — collapsed verbose completed-rung prose to one-liners
(RK-BB-1..3, RK-BB-SEGFAULT-CLUSTER, RK-BB-SM-FRAME-MODE4, RK-GIVEN-MODE4,
RK-HASH, RK-IO, RK-EXCEPTIONS, RK-CLASS, MODE3-NO-INTERP-3, 1a, 1b each
~one line each). Watermark replaced with 1c content. Mode-3 PASS/CRASH
inventory removed (regenerable from /tmp/gate_rk3.sh; one-shot recreate
in this handoff appendix). Open Qs section pruned to truly pending only
(Q5, Q9-Q12). Headers and rule-sections kept verbatim.

## gate_rk3.sh (recreate if absent)

```bash
#!/bin/bash
cd /home/claude/SCRIP
PASS=0; FAIL=0; CRASH=0; PL=""; FL=""; CL=""
for f in test/raku/*.raku; do
    b=$(basename "$f" .raku)
    e="test/raku/${b}.expected"; [ -f "$e" ] || continue
    a=$(timeout 8s bash -c "SCRIP_M3_NATIVE=1 ./scrip --run '$f' < /dev/null 2>&1")
    rc=$?
    if [ $rc -ne 0 ] && [ $rc -ne 1 ]; then CRASH=$((CRASH+1)); CL="$CL $b"
    elif [ "$a" = "$(cat $e)" ]; then PASS=$((PASS+1)); PL="$PL $b"
    else FAIL=$((FAIL+1)); FL="$FL $b"; fi
done
echo "PASS ($PASS):$PL"
echo "FAIL ($FAIL):$FL"
echo "CRASH ($CRASH):$CL"
echo "--- GATE-RK3 mode-3 native: PASS=$PASS FAIL=$FAIL CRASH=$CRASH TOTAL=33 ---"
```

## NEXT — M3-RK-NOINTERP-1d (rk_gather)

Last Cluster-1 native test. **NOT a mechanical mirror like 1c was.** The
gather/take pipeline has a different shape: `lower_fnc` for `__gather_N`
emits `SM_BB_INVOKE` pointing at the proc's BB graph; that graph is
rooted at BB_SEQ which is a multi-yield driver depending on `g_emit.
xa_bb_emit_pair_*[]` being populated by `flat_drive_seq` before child
emission. But the mode-3 path is SM_BB_INVOKE → `walk_bb_node(gen, NULL)`
(in sm_bb_switch.cpp:128), NOT `walk_bb_flat`. So the pair arrays may
be unpopulated when bb_seq's BINARY arm fires (line 268 of bb_seq.cpp).

Current crash for rk_gather (mode-3): same shape as 1c's starting state —

```
bb_emit_end: 1 unresolved forward reference(s):
  site=20 label='.Lbbinv0_β'
Aborted
```

The β-label is `.Lbbinv0_β` from the SM_BB_INVOKE wrapper — meaning the
inner BB template emitted no bytes (or didn't define β). bb_seq's BINARY
arm at line 268 iterates over `g_emit.xa_bb_emit_pair_n` — likely 0 here.

**Investigation paths:**

1. Audit what walks the gather's BB graph in mode-3 vs mode-2 vs mode-4
   and where the pair arrays get populated. Mode-2 uses `bb_exec.c`
   directly (no pairs needed). Mode-4 uses `flat_drive_seq` from
   `emit_bb.c` (populates pairs). Mode-3 SM_BB_INVOKE scratch flush
   calls `walk_bb_node(gen, NULL)` — does it route through anything that
   populates pairs?

2. Option A: extend the scratch-flush wrapper in `sm_bb_switch.cpp` to
   call `flat_drive_seq`/equivalent for SEQ-rooted graphs before
   `walk_bb_node`.

3. Option B: author a self-contained gather-driver in bb_seq's BINARY
   arm that doesn't depend on pair arrays — walks pBB->α's γ-chain
   directly and emits the multi-yield x86 inline. More invasive but
   keeps the SM_BB_INVOKE wrapper uniform.

4. bb_suspend.cpp BINARY arm (line 75) also has a non-stub but it's
   small — verify it cooperates with whichever path is chosen.

5. bb_upto.cpp BINARY arm (line 72) already exists; check whether it's
   reachable from the gather pipeline (probably not — upto is the
   `for $x..$y` lazy range, separate from gather/take).

**Recommended:** start with path (1) — instrument bb_seq.cpp BINARY at
line 268 with a fprintf showing `g_emit.xa_bb_emit_pair_n` to confirm
the hypothesis, then either populate the pairs in the wrapper or write
a self-contained driver. Should be a ~50-150 line surgery.

After 1d closes rk_gather, Cluster 1 is fully done and only Cluster 3
(6 regex tests) remains in mode-3 native — those are DEFERRED to
GOAL-RAKU-PAT-BB.

## Files touched

```
SCRIP:
  src/emitter/BB_templates/bb_iterate.cpp   (+ ~110 lines, BINARY arm wired)

.github:
  GOAL-RAKU-BB.md                            (pruned + 1c entry + new watermark)
  PLAN.md                                    (Raku BB row updated)
  HANDOFF-2026-05-29-OPUS-RAKU-BB-M3-NOINTERP-1c-LANDED.md   (new, this file)

corpus:  (unchanged)
```

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
