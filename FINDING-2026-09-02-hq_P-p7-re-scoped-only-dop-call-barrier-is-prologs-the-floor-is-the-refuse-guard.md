# FINDING 2026-09-02 hq_P — P7 re-scoped by measurement: only `dop_call`'s barrier is Prolog's (and it is never taken); the plw floor is the REFUSE guard and must outlive the global trail

**Row:** P7 `prolog-failure-and-cut-are-wired-ports-not-setjmp` (ARCH-PROLOG-THREE-ZETAS.md § 4). **Tree:** SCRIP `309f5414`, read-only.
**Written at wrap-up (Lon 11:20, MODE → CEO); nothing was cut.** Gate re-scoped to match: `test_gate_p7_prolog_setjmp_gone.sh` (SCRIP `28a75f03`).

## 1. `dop_call`'s setjmp is Prolog-only and is NEVER TAKEN for Prolog

`core_runtime_error` (core.c:2107) longjmps **only** when `g_error != 0 && g_core_errjmp_n > 0`; otherwise it prints `** Error N in
statement M` and `exit(1)`s — three exit paths, no return. `g_error` is armed by SNOBOL4's `&ERROR` (keywords.c:528), the EVAL guard
(runtime_eval.c:268, `g_error = -1` around EVAL) and gen_runtime.c:254 — and has **zero references** under `src/parsers/prolog/` or in
`lower_prolog.c`. The `dop_*` bodies (:1335–:1487) raise nothing directly (28 `return FAILDESCR`, 2 `rt_pl_throw_pending`). A Prolog
builtin that does raise (arithmetic.c:95/99/109/115, division by zero) exits before any barrier matters.
✅ **P7a — delete `dop_call`'s errjmp push/pop + setjmp: behavior-free by construction.** Lands the minute `by_name_dispatch.c` is free.

## 2. § 4's "three live setjmp barriers" overcounts by two — the other two are shared nodes

- `rt_call_arr_bl` (:4913) is emitted by `bb_call_fn.cpp:510/596` and `bb_call.cpp`, and referenced from `lower_snobol4.c`. Its setjmp is
  SNOBOL4/Icon `&ERROR`-to-failure trapping (history: `12dc1714` PL-REGAIN-2; `aadd86c4` *"GOAL-ICON-BB: drive FAILs 14→9"*). **Only its two
  `g_plw_unwind_floor` lines are Prolog's.**
- `c_rt_jct_relop` (:5070): its veneer `rt_jct_relop` is called from `bb_binop_relop.cpp`, `bb_binop_relop_val.cpp`, `bb_to.cpp`, `bb_to_by.cpp`
  — Icon/SNOBOL4 boxes. `lower_prolog.c` has **zero** relop/to references: Prolog never reaches it. Its setjmp is Icon `&error` (`core_icn_error`).
⛔ Deleting either is a SHARED-NODE change graded on the SNOBOL4 board and the Icon watermark, for no Prolog gain. **Leave both.** A
whole-file setjmp count (the gate's first form) would have ordered two other languages' error trapping deleted under a Prolog row.

## 3. The plw floor IS the REFUSE producer — it guards the GLOBAL trail and cannot go before the trail lives in the frame

`pl_cell.h:66–74` classifies a trail pointer below `g_plw_unwind_floor + 16` as dead C-stack; `:81 pl_trail_unwind` prints every van Roy
`refuses corrupt trail mark`. That defends the **global** `g_pl_trail` (rt_runtime.c:117–245, unification.c:23) against marks left on dead
stack. Lon (11:00) ruled the trail becomes each activation's own binding log in its frame (hq_C PZ-4 clauses (b)+). Once that lands the
floor is meaningless and goes. **Until then, deleting it deletes the only guard: REFUSE becomes CRASH or silent corruption** — precisely
what the van Roy gate's safety half exists to catch (FINDING `5c7d2254`). hq_C relied on the floor **this morning**: `72c7ec09` *"dop_call_nothrow
arms its own dead-cstack floor (fixes 4 SIGABRTs)"*.
⛔ **P7b — `g_plw_unwind_floor`, `g_plw_floor_bypass`, `rt_plw_floor_bypass_on`, `dop_call_nothrow` + its two wrappers `rt_pl_dop_trail_unwind`
/ `rt_pl_dop_unwind_nothrow` + the `$unwind_nothrow` arm — is sequenced behind PZ-4 (b), not behind the T9 Term push.** The pull-forward
stands for P7a; for P7b it would land a regression the gate is built to catch. Row parked `PARKED-AWAITING:prolog-pz4-gamma-retain-activation-frames`.

## 4. Milestone-1 reading on `309f5414` (clause (a) landed): flapping unchanged — the expected null

Van Roy worst-of-3: CLEAN=3 REFUSE=2 CRASH=14, **nine** kernels still flip between reps (was eleven on `fa12d7cb`; within noise). Clause (a)
is a pure rebase (hq_C: 10 pin/restore lines, zero ζ offsets moved), so the memory the frame occupies did not change and the prediction
(*per-rep strings go constant when the frame is PROTECTED*) is about (b)+. A rebase leaving the nondeterminism exactly where it was is
what a rebase should do; the instrument distinguishes rebase from protection, which is what it is for. Sent to hq_C.

## 5. Two nulls recorded so nobody re-runs them

- `bench_triangulate_prolog.sh` with `KERNELS="fib nrev queens_8"` on `309f5414` returned in 6 s with **all 12 cells UNPROVEN (gnu/swi too)** and
  wrote a TSV that would have become the *latest* one `--two-number` reads — replacing the informative 08-27 board with an empty one.
  Deleted, not committed. The `KERNELS` filter or angle 1 is not matching under this invocation; not chased under wrap-up.
- The 08-27 two-number board (last informative one): fib 0.526x vs GNU, 0.386x vs SWI; deriv 0.069x vs SWI — stale SCRIP, quoted as history.
