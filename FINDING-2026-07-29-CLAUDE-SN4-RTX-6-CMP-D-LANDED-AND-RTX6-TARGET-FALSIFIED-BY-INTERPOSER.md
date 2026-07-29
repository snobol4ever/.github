# FINDING-2026-07-29-CLAUDE-SN4-RTX-6-CMP-D-LANDED-AND-RTX6-TARGET-FALSIFIED-BY-INTERPOSER.md

**Session:** s203 · **Date:** 2026-07-29 · **Commit:** SCRIP `70198a9d`

---

## THE FINDING: STEP 0(d) FALSIFIED THE RTX-6 RUNG'S OWN NAMED TARGET

The RTX-6 rung names `rt_num_arith` as its primary target (5 template call sites, described as the "int-int inline fast path"). A signature-agnostic LD_PRELOAD counting interposer (asm trampolines chained via `dlsym(RTLD_NEXT)`, resolving each symbol independently) measured `rt_num_arith` at **ZERO calls** in `arith_loop` at both N=100,000 and N=200,000. `rt_cmp_d` scaled exactly 100,000→200,000 in the same runs, proving the interposer as a positive control.

**Root cause:** integer arithmetic is fully inlined by the emitter. `N = N + 1` never reaches the C runtime at all. `rt_num_arith` is reachable only from real/mixed arithmetic — a probe with `X = X + 1.5` measured 50,000 calls at N=50,000. The RTX-6 rung's static template call-site count (2 in `arith_loop.s`) is a CALL BOUNDARY count, which measures program TEXT, not execution. ARCH §7 step 0(d) says exactly this and was published at RTX-2; it was not applied to RTX-6.

**This is the `rt_call_arr` flat-8 vacuity of s188, repeating on a new family.**

---

## WHAT WAS PORTED INSTEAD

`rt_cmp_d` — the #1 hottest C runtime call in every stable benchmark, entirely unported and ungated (zero references in `src/runtime/rtx/`).

| benchmark | `rt_cmp_d` calls (measured, N=nominal) |
|---|---|
| var_access | **10,000,001** |
| func_call | **10,000,001** |
| string_manip | 5,000,001 |
| table_access | 5,016,003 |
| fibonacci | 2,692,537 |
| op_dispatch | 2,081,407 |

`roman` and `mixed_workload` both segfault at rc=139 on pristine main (pre-existing, not the interposer).

---

## THE PORT: `rt_cmp_d`

**C of record:** `src/runtime/rt/rt.c:296` (renamed `c_rt_cmp_d` same commit). Args are POINTERS to DESCR_t pairs, not descriptor register pairs: `rdi = a, rsi = b`, result `int` in `eax`.

**Branch order is deliberately reversed from the C.** The C tests the string pair first, the integer pair second. This port tests the integer pair first — that is the measured hot shape (LT/GT on loop counters). The reorder is semantics-preserving because the two guards are MUTUALLY EXCLUSIVE (string arm requires both tags ≤ 1 = DT_S; integer arm requires both == 6 = DT_I; no descriptor pair can satisfy both).

**String arm:** inlined byte-compare loop instead of a libc `strcmp` call. The string arm is COLD in every measured benchmark; the `RTX_CALL_ALIGN` ceremony for a single libc boundary would cost more than the comparison itself.

**IEEE trap in the real/fallthrough arm:** `comisd x,y` sets CF=1 for both below AND unordered (NaN), so a single `seta`/`setb` pair would misclassify NaN. This port issues `comisd` in BOTH directions (xmm0,xmm1 then xmm1,xmm0) and uses `seta` both times — `seta` is (CF=0 AND ZF=0), which is false for unordered in both directions, so NaN → 0−0 = 0, matching the C exactly. Same class as `rt_is_truthy`'s −0.0/NaN traps.

**File:** `src/runtime/rtx/rtx_arith.S`. Gate: `SCRIP_RTX_ARITH` (default ON). `rtx_gate_arith` declared in `rtx_init.c`, wired in Makefile.

---

## GATES

| measurement | gate ON | gate OFF |
|---|---|---|
| crosscheck m3 | 268/47 | 268/47 |
| crosscheck m4 | 267/46 | 267/46 |
| DIVERGE | 2 | 2 |

Both arms byte-identical to s202 baseline of record.

**Two-sided falsification:** corrupted DT_I result (`setg`/`setl` swapped) ⇒ gate ON **245/70 (23 movers)**; gate OFF ⇒ exact watermark. The asm executes; the gate reaches C.

STR battery 8426/0 · RTX UNIT ALL PASS.

---

## PERF — NO-REGRESSION ONLY, STATED PLAINLY

`var_access` 1.036× · `func_call` 1.014× (RT_OPT=-O0, R=5 interleaved, medians).

Both numbers are inside the ±3% AGG null floor. **This is not a demonstrated speedup.** The expected board was not pre-stated before porting, which by s188's rule makes the result uninformative either way. Reason for the null: at -O0 the C body of `rt_cmp_d` is already small; 10M boundary crossings still occur; the boundary dominates. Eliminating the boundary (RTX-11 / emitter inlining of the DT_I compare) is the right lever but is phase-2 and touches `x86_asm.h`.

---

## COLLATERAL: ARITH FAMSET IS UNUSABLE

`bench_sno_rtx.sh:51` records ARITH FAMSET as `mixed_workload arith_loop # rt_num_arith 500K`. This is a false null on two independent axes: `arith_loop` calls `rt_num_arith` zero times (measured); `mixed_workload` segfaults on pristine main (rc=139, pre-existing). The FAMSET comment has been annotated in-place. A correct FAMSET requires a benchmark that mixes integer and real arithmetic; `rt_num_arith` fires at ~50,000/run for `X = X + 1.5` over 50,000 iterations. Creating that benchmark is the prereq for any honest RTX-6 ARITH speed claim.

---

## COLLATERAL: FIVE PHANTOMS IN THE RTX-6 RUNG SYMBOL LIST

`rt_incr` · `rt_decr` · `rt_exp` · `rt_neg` · `rt_coerce_num` — all declaration-only in `src/runtime/rt/rt.h`, zero definitions in `src/`, zero call sites. ARCH §5 table corrected in this session; the RTX-6 rung text (`GOAL-SNOBOL4-RTX.md`) still carries them and must have them struck. Same shape as RTX-3's `rt_concat`/`rt_lcomp`/`rt_acomp` phantoms. The rung-text correction is OWED next session.

---

## REGISTER NOTE FOR ζ COORDINATION

`rtx_arith.S` touches only the RTX volatile working set (rax rcx rdx rsi rdi r8 r9 r10 xmm0 xmm1). It never reads or writes rbx · rbp · r12 · r13 · r14 · r15. The port is forward-compatible with any ζ register consolidation (R12 island / RSP hardware stack / RBX GC top) by construction. All phase-1 RTX ports confined to the volatile nine share this property.
