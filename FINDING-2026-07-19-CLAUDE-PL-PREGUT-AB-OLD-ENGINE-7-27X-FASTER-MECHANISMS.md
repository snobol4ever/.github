# FINDING 2026-07-19 (Claude Fable 5, s100) — PL PREGUT A/B: the 63c666ba GZ engine is 7–27× faster than HEAD on identical work; six measured mechanisms; PL-REGAIN ladder minted

Session ask (Lon): find the README checkin whose Prolog numbers beat today's, build it, reproduce, analyze why, mint the recovery rung.

## 1. The commits

| What | Commit | Date |
|---|---|---|
| README benchmark table, geomean m4/GNU = 3.28× | `7ec7305a` | 2026-06-27 |
| Documented last-green engine head (FINDING-2026-07-08 §1) | `63c666ba` | 2026-06-27 |
| Amputation (GZ#5): 119 IR members + codegen out | `8de0fb46` + `e1ec0679` | 2026-06-29 |

`7ec7305a` is an ancestor of `63c666ba`; the 6 intervening commits are SNOBOL4-side only (indirect-ref/field-accessor/array-OOB) — **Prolog-identical**. The A/B pins `7ec7305a` (the tree whose table we reproduce; verified built in-container). The 2026-07-08 restore was FEATURES ONLY — its own inventory §5: the performance track was "untouched by this reconstruction."

## 2. Reproduction (this container, gprolog 1.4.5 apt, identical wrappers, single-run cells)

Rail: `scripts/bench_prolog_ab_pregut.sh` (landed this session, = PL-REGAIN-0). Method: failure-driven fact-table loop (`a/1`×8 × `b/1`×64 conjuncts → N ∈ {8..262144}) because the GZ engine **fences `between/3`**; full enumeration per iteration (the PL-SPEED-0 no-once method); `GC_INITIAL_HEAP_SIZE=1G` for OLD per its README's own "pre-sized GC heap" note; lpi column catches silent truncation.

| prog | GNU ms/it | OLD ms/it | old/GNU | NEW ms/it | new/GNU | **new/old** |
|---|--:|--:|--:|--:|--:|--:|
| fib | 3.81 | 5.70 | 1.5× | 102.2 | 26.8× | **17.9×** |
| tak | 13.08 | 16.63 | 1.3× | 440.5 | 33.7× | **26.5×** |
| qsort | 0.046 | 0.287 | 6.2× | 4.35 | 94× | **15.1×** |
| nrev | 0.010 | 0.282 | 28× | 3.72 | 372× | **13.2×** |
| deriv | 0.005 | 0.039 | 7.8× | 0.265 | 53× | **6.8×** |
| queens_8 | 4.48 | 15.23 | 3.4× | **SIGSEGV** | — | ∞ (defect-c) |

Second pass (the landed rail, NEW=`0226580f`): same class; OLD tak beat GNU (8.7 vs 10.3); NEW cells swing multi-× run-to-run (fib 102→144, tak 440→602 — the s98 "ham swings" family), ratios stable in class. OLD absolute times match the 2026-06-27 table closely where method matches (deriv 0.055 vs table 0.073; qsort 0.377 vs 0.515; queens_8 differs because full-enumeration ≠ their loop). **The 3.28×-class regime is real and reproduced; the lost factor is 7–27×.**

Method land mines hit and defused, recorded so they are not re-stepped-on: (a) a RECURSION loop DNFs gprolog (no heap GC — the PL-SPEED-0 warning, re-proven); (b) unpresized libgc turned OLD fib into 86 ms/it (15×) — collection storms; the presized heap was load-bearing in the 2026-06-27 method; (c) NEW qsort/nrev SIGSEGV under a recursion loop even at N≤512, and queens_8 m4 SIGSEGVs under fail-driven full-enum ×64 — fresh defect-(c) reproducers, m4, small N.

## 3. Why it was faster — six mechanisms, measured in the emitted `.s` (identical fib wrapper)

OLD emits **1,829 lines**; NEW **6,957** (3.8×). Call profiles: OLD = 71 `rt_trail_unwind` + 69 `rt_pl_unify_cell_const` + 6 direct `call gzpN_*` + 5 `rt_trail_mark` + 3 `rt_pl_cells_init` + 2 `rt_pl_is_cell_arith`; NEW = **172 `rt_call_arr` + 89 `rt_var_ref_cell`** + rt_arg_stage/rt_proc_call_open/rt_proc_open_fn per call + gen-spine machinery.

1. **DIRECT FOUR-PORT CALLS.** `call gzp278_α`, redo = `call gzp278_β`; arg CELL POINTERS in SysV registers (`lea rdi,[r12+40]; lea rsi,[r12+24]; lea rdx,[r12+8]`); status in `eax`; `je ω`. Zero name path, zero staging, zero C trampoline.
2. **DET-SPECIALIZED OPCODES, ZERO DISPATCH.** Old path vocabulary: `IR_DET_IS` `IR_DET_CMP` `IR_DET_WRITE` `IR_DET_NL` `IR_CELL_UNIFY` `IR_CELL_CALL` `IR_CELL_CUT` `IR_CALLEE_FRAME` `IR_QUERY_FRAME` — ONE tight helper per goal (`rt_pl_is_cell_arith(dst,src,opstr,imm)`, `rt_pl_arith_cmp_cell_val`), operands in regs + `[rip+…]` RO. NEW routes every goal (incl. `>`, `is`, `write`) through `rt_call_arr`; the s98 $-gate made that walk cheaper — OLD had NO walk.
3. **FIXED COMPILE-TIME CELL SLOTS** `[r12+8/24/40/56…]` per clause var. NEW: 89× `rt_var_ref_cell` = the s99 VCELL flood (~1.37M allocs / 8 fib iters), each a C call + heap cell.
4. **ONE-CALL FRAME CARVE.** `rt_enter(area,nslots)` — one bump per activation. NEW: open + stage + set×4 + `rt_jmp_frame_lexprep` + whole-frame memset (SPEED-2's target).
5. **SPECIALIZED CONST HEAD-UNIFY.** `rt_pl_unify_cell_const` per const head arg; trail mark/unwind the only backtracking cost.
6. **Caveats — what the old engine did NOT have and how it cheated:** hard `pl_gz_admit` per-program FENCE (≤2048 slots; between/3 out), GC-pressure sensitivity (see §2b), and NO first-arg indexing / NO LCO (its own meta_qsort row was 12×). Recovery = the mechanisms on the new spine WITHOUT the fence (fast path per construct, general fallback stays); SPEED-5/6 remain net-new.

## 4. Disposition

PL-REGAIN ladder minted at the head of LADDER B in `GOAL-PROLOG-BB.md` (REGAIN-0 rail LANDED+GREEN this session; REGAIN-1 direct port calls; REGAIN-2 det builtin opcodes; REGAIN-3 fixed cell slots; REGAIN-4 one-call carve; REGAIN-5 const head-unify; REGAIN-GATE parity ≤1.3× vs OLD, then the standing ≤1.2×/≤1.0× GNU gates). SPEED-1(ii) and SPEED-2 ABSORBED (pointers left in place). Defect-(c) SIGSEGV rung is a rail-completeness PREREQ (queens_8 NEW m4 DNF at N=64). Old-code reading rule per the resurrection inventory stands: port ALGORITHMS into DESCR world; never link the old cell bodies; `SCRIP-pregut` worktree is a SEMANTICS/CODEGEN REFERENCE only.
