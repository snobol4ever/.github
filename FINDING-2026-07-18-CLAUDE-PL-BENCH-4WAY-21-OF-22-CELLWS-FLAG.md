# FINDING 2026-07-18 — PL BENCH 4-WAY: 21/22 vs GNU+SWI; stack-limit root cause; env-gated CELLWS reclaim landed; queensn = THREE-STREAM leak (mapped, not yet closed)

Session: Claude (Fable 5), 2026-07-18. Clean clone + `install_system_packages.sh` + `make -j4 scrip && make libscrip_rt` (both rc=0), gprolog 1.4.5 (apt, the goal-file version) + swipl 9.0.4 (apt), `refs/` symlinked from Lon's uploaded gprolog-master/swipl-devel-master zips.

## 1. HEADLINE: 4-way benchmark result (scripts/test_bench_prolog_4way.sh)
- **As-shipped (default 8 MB C-stack): consensus=18/22.** fib/tak/meta_qsort/queensn all SIGSEGV, empty output, m3≡m4 identical.
- **Root cause A (3 of the 4): C-stack overflow.** Every Prolog call nests a C frame (`rt_proc_call_gen_h` trampoline). Measured: fib correct ≤N=15, SIGSEGV ≥N=18 at 8 MB; with `ulimit -s unlimited` fib/tak/meta_qsort all produce oracle-exact answers. **Real fix = PL-SPEED-3/7** (DET no-C-frame spine); until then both bench scripts now raise the soft stack limit at top (2-file script diff, commented with the rung pointer).
- **Result with the script fix: consensus=21/22, m3≡m4 parity on every program, GNU and SWI 22/22.** modes gate: green=21 fenced=0 broken=1.
- NOTE vs tracked state: goal file said broken=2 (queens/queensn); clean build measures queens/queens_8 PASS and the stack-class as the actual breakage — tracked numbers drifted again (same lesson as s61).

## 2. queensn (the 1 remaining): measured to the mechanism
- N=8: 1s correct (oracle-exact), peak RSS ~114 MB. N=9: 2s correct, ~285 MB. N=10: >300 s timeout. gprolog/swipl N=10: <1 s.
- **Sizing cannot fix it:** ZC_HEAP_MB 512→2048 experiment (reverted): RSS plateaus 2.48 GB at t=65 s, still times out at 280 s. GC triggers only on span exhaustion (gc_heap.c:89) and HB_WS is blanket-pinned → futile collect storm once full.
- **THREE per-branch allocation streams leak into WS, all `rt_ws_alloc`:**
  1. `pl_cell_t` compound blocks — `unification.c` rt_pl_compound_cell (:67,:70) + rt_pl_unify_struct (:82). **CLOSED this session (flag-gated, below).**
  2. ZLS v1 activation frames — `zeta_alloc.c:47` ("release leaves WS blocks in place — immortal"). OPEN. Note `--zeta=zh` reclaims frames via rt_zh_kill_since, but combined zh+cellws STILL plateaus ~563 MB → stream 3 (and/or residual v1 path) still fills WS.
  3. Per-activation `pcells` arrays — `rt.c:791`. OPEN.
- Next rung = route streams 2+3 the same way (or land PL-SPEED-3 which subsumes stream 2), then queensn should complete in bounded memory.

## 3. LANDED: env-gated CELLWS island (PL-WS-2 step 2, first slice)
`SCRIP_PL_WS_RECLAIM=1` routes the pl_cell_t builder stream to a NEW 64 MB rewindable island (`rt_pl_cellws_*`, rt_arena.{c,h}) — SEPARATE from the s58 cterm island, which keeps holding survivor Terms (findall deep-copies land there via term_new_*) and is never rewound → **findall/dyn-DB safe by construction, no escape-copy needed in this slice**. Rewind anchored at every existing choice-point site by riding INSIDE `plw_zh_mark_push/kill_to` (by_name_dispatch.c, +2 hook lines + mirrored pair stack; release is skip-on-stale, never abort). Default path: one cached-int check then the identical rt_ws_alloc — behavior-identical with flag off.

**Validation matrix (this tree):**
| gate | flag OFF | flag ON |
|---|---|---|
| prolog rung suite ×3 (interp/run/compile) | 138/138 | **138/138** |
| 4-way bench | 21/22 | 21/22 |
| smoke/fib/queensn N=8 | green | green |

Icon rung runner: PASS=242 FAIL=15 XFAIL=32 — **baseline for THIS runner not re-measured via stash-rebuild (context budget); flag-off behavioral identity argued from the diff, not proven by A/B.** Next session: stash-diff A/B if suspicious.

## 4. Files changed (LOCAL, not pushed)
- SCRIP: `scripts/test_bench_prolog_4way.sh`, `scripts/test_bench_prolog_modes.sh` (stack raise), `src/runtime/rt/rt_arena.{c,h}` (cellws island), `src/runtime/unification.c` (3 sites → PL_CELL_ALLOC + flag-switch macro), `src/runtime/by_name_dispatch.c` (cw pair stack + 2 hooks).
- Deliberately NOT touched: `rt_runtime.c:20` PL_CELL_ALLOC (pl_cell_conv.h stream — separate blast radius, follow-up), ZC_HEAP_MB (reverted to 512).
- ⚠ Makefile gap found: `out/libscrip_rt.so` deps omit `zeta_choices.h` (and headers generally) — stale-.so split-brain risk the goal file warns about; `rm out/libscrip_rt.so` before rebuild until fixed.
