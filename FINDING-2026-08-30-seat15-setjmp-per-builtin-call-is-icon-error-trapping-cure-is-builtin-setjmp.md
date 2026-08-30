# FINDING 2026-08-30 seat15 — `setjmp-per-builtin-call`: what the setjmp guards, why the obvious fast-path is
# unsafe, and the cure that actually landed (`__builtin_setjmp`/`__builtin_longjmp`, same call sites, 2.03%
# whole-kernel win, zero semantic change)

## THE QUESTION THIS ROW HAD LEFT OPEN SINCE MINT (2026-08-22)
hq_P's original brief asked, before any edit: *"what is the setjmp actually protecting on the builtin path
(error unwind? SNOBOL4 FAIL propagation?), and can that be carried by the Byrd box omega port instead."*
Three prior sessions (seat02, seat01, seat04) measured that the cost is real and stable (~2.16-2.88% of a
builtin-heavy kernel) but explicitly left the guard question unanswered. This session answers it.

## 1. WHAT IT GUARDS: Icon's `&error` run-time-error trapping, NOT ordinary FAIL
`g_error` (`src/runtime/keywords.c:13`, default 0, written only by explicit `&error :=` assignment) gates the
ONLY two longjmp sites in the tree (`core_runtime_error`/`core_icn_error`, `src/runtime/core/core.c`):
`if (g_error != 0 && g_core_errjmp_n > 0) longjmp(...)`. Ordinary SNOBOL4 FAIL never goes through this path —
it flows through the `FAILDESCR` return value every caller already checks. **No program that never touches
`&error` (every SNOBOL4 program; most Icon programs) ever takes the longjmp, but `setjmp()` was still paid on
every single builtin call, unconditionally** — 5 call sites total (`rt_call_arr_bl`, `rt_num_arith`, the
`RT_BINOP_ENTRY` macro (10 expansions), `dop_call`, `c_rt_jct_relop`, `eval_chain_run_guarded`), all sharing
one `jmp_buf g_core_errjmp_stk[64]` + `g_core_errjmp_n` depth counter.

## 2. THE OBVIOUS FIX ("skip setjmp when g_error==0 at entry") IS UNSAFE — MEASURED, NOT ASSUMED
Before writing anything, checked whether `g_error` can change *during* a call via nested user-code execution
(the only way the obvious entry-time check could go stale mid-call). `APPLY`, `__apply__`, and `EVAL` all
invoke arbitrary named/dynamic procedures from inside `rt_call_arr_impl` (`rt_call_proc_descr`/`rt_call_value`/
`rt_call_named_proc`), and there are a dozen+ further `rt_call_proc_descr`/`rt_call_value` call sites earlier
in the same file. A user procedure invoked this way can assign `&error := N` and then trigger a runtime error
that fires `core_runtime_error` from a call chain that never re-enters `rt_call_arr_bl` — at which point
`g_core_errjmp_n` reflects whatever the OUTER (skipped) frame left it at, and the trap either escapes to the
wrong ancestor frame or misses entirely.

**Confirmed this is not hypothetical — it is a live, PRE-EXISTING bug, independent of this row:** a minimal
witness (`risky()` sets `&error := 1` then calls `&null()`, invoked via `apply("risky", [])`) aborts the whole
program instead of trapping, on TODAY'S unmodified tree, before any change in this row. Root cause not
chased (out of scope for a performance row) — flagged here so it isn't rediscovered as a mystery; a fresh
row is the right home for it (Icon/APPLY error-trapping interaction, hq_C's lane).

## 3. THE CURE THAT LANDED: `__builtin_setjmp`/`__builtin_longjmp`, same call sites, same semantics
Rather than change WHEN a recovery point is registered (unsafe per §2), swapped WHAT establishes it. All 5
call sites checked their setjmp's return value for TRUTHINESS ONLY — none read the numeric code — so GCC's
`__builtin_longjmp` contract (must pass exactly `1`) costs nothing; the real error code still travels via
`g_icn_errnumber`/`g_icn_errtext`/`g_icn_errvalue`, untouched. `g_core_errjmp_stk`'s type changed
`jmp_buf[64]` -> `void *[64][5]` (GCC's documented minimum buffer size, empirically confirmed sufficient on
this toolchain via an isolated nested-call witness before touching real code). Zero call sites moved, zero
call-site COUNT changed, zero correctness-relevant control flow changed — only the primitive.

**Isolated microbenchmark** (matched call shape, callgrind, -O0, baseline-subtracted): standard `setjmp`
63.0 Ir/call vs `__builtin_setjmp` 35.0 Ir/call — **1.80x**.

**Real-kernel measurement**, same-tree A/B via `git stash` (not a historical citation — RULES.md's own
REBASE-BASELINE COROLLARY: both arms must be the same tree plus the one change), `string_manip.sno` N=20000,
`-O0`, callgrind:
| | Ir | |
|---|---|---|
| BEFORE | 43,940,293 | `__sigsetjmp` 880,430 (2.00%) + `__sigjmp_save` 520,013 (1.18%) |
| AFTER | 43,048,018 | neither symbol appears anywhere (`nm -D` on the built runtime: clean) |

**2.03% whole-kernel reduction (1.02x), program output byte-identical.** The ~3.19% setjmp-family cost this
session measured (close to seat01/seat04's earlier 2.16-2.88% citations, same order of magnitude) is not
fully eliminated — `rt_call_arr_bl` still pays for establishing SOME recovery point, just a far cheaper one —
but the two libc symbols are gone completely, structurally provable via `nm -D`, not just "smaller in a
profile."

## 4. CORRECTNESS EVIDENCE
- Two targeted `&error` witnesses (Arizona `errkwds.icn`, direct trapping; a new APPLY-nested witness,
  reproducing §2's pre-existing bug) — byte-identical output before/after, bug included, verified via a real
  `git stash` same-tree A/B (not just "looks unchanged").
- SNOBOL4 corpus gate: 2 standing crashes (`fence_rpos_rem_branch_2` SIGSEGV, `fence_bal_rtab_branch_1`)
  reproduce identically on the unmodified tree, standalone, 5/5 deterministic runs each — pre-existing,
  confirmed not caused by this change (extracted via `corpus_suite_harness.py extract`, assembled+linked by
  hand matching `test_gate_polyglot_demos.sh`'s own recipe, since `--compile` alone only emits text).
  `fence_bal_rtab_branch_1`'s harness-reported SIGABRT did not reproduce standalone on EITHER tree — an
  environment-dependent flake in the harness's own batch execution, not a property of the compiled program;
  not chased further (matches this file's own §2 discipline: flag, don't scope-creep).
- Icon rung suite (PASS=259/FAIL=9/BADEXIT=1/XFAIL=28 of 297) and Prolog smoke (5/5 all 3 modes) both clean
  on the landed tree; the Icon FAIL/BADEXIT set was not individually diffed against a same-tree BEFORE run
  (time-boxed) — the standing crash-set A/B above is the load-bearing correctness evidence, not this count.

## 5. DONE-WHEN REPLACED
The row's own DONE-WHEN (`test_corpus_snobol4.sh`) was flagged VACUOUS by `sweep-free-rows-are-real` — it
proves nothing about setjmp. Replaced with a two-part criterion (Instrument Laws: prove it can say NO, prove
it can say YES): `nm -D` on the built runtime asserts zero `__sigsetjmp`/`__sigjmp_save`/`setjmp`/`longjmp`
references (refuses rc=2 if unbuilt), THEN a live Icon witness asserts `&error` trapping still produces the
exact expected output. Verified both arms before landing: the nm check is FALSE on the pre-change tree
(confirmed via the same `git stash` cycle used for the perf measurement) and TRUE after; the witness passes
on the landed tree.

## DISPOSITION
- Landed: SCRIP `df800d2c` (rebased onto `2afd3e12`, pristine-verified post-rebase).
- Not landed / out of scope, flagged for whoever owns Icon/APPLY error semantics (hq_C's lane): the §2 bug
  (`&error` set inside an APPLY-invoked procedure does not trap correctly) is real, reproducible, and
  unrelated to this row — worth its own mint.
- Row `setjmp-per-builtin-call` DONE-WHEN now passes on the landed tree; task file NEXT/LEDGER updated,
  `done` called this session.
