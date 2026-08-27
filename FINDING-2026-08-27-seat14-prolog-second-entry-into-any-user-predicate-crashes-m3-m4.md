# FINDING: SCRIP's Prolog backend (`--run` and `--compile`, both modes, same codegen) crashes on the *second* entry into a compiled user predicate within one process — this is not kernel-specific, it blocks timing every benchmark in `corpus/benchmarks/prolog/bench/`, and it corroborates the open `PZ-4` architectural gap in `GOAL-PROLOG-100.md` from a completely different angle (interpreter-mode, minimal non-generator repro) than the disjunction/backtracking repro already tracked there.

**Seat:** seat14 · **Date:** 2026-08-27 · **Task:** `bench-rivals-prolog` (postoffice) · **Repro (2 lines, m3):**

```prolog
:- initialization(main).
main :- fib(20,F), write(F), nl, fib(20,F), write(F), nl.
fib(0,1):-!. fib(1,1):-!. fib(N,F):-N>1,N1 is N-1,N2 is N-2,fib(N1,F1),fib(N2,F2),F is F1+F2.
```

`./scrip --run repro.pl` prints `10946` (correct) once, then **segfaults** before the second call completes. Confirmed independently under `--compile --target=x86` (m4) too — same crash, different signal (SIGABRT on some kernels, SIGSEGV on others), consistent with "m3 ≡ m4 codegen" sharing the defect.

## Why this matters for bench-rivals-prolog specifically

Every timing methodology in this repo for Prolog (`bench_prolog_vanroy.sh`'s `mkwrap`, `bench_prolog_ab_pregut.sh`'s `mkwrap`, and the two new angle scripts this row adds) times a kernel by **wrapping it in a loop** — `between(1,N,_), bench__main, fail` or equivalent — which by construction calls the compiled predicate more than once. **That means SCRIP cannot currently be timed on any Prolog kernel, correct or not**, independent of the kernel's own content. This is a harder blocker than "most kernels fail correctness" (which is also true, see below) — it means the 3 kernels that DO pass single-shot correctness (`deriv`, `fib`, `tak`) *still* cannot be benchmarked, because the act of looping them for measurement is itself what crashes.

## Scope, measured directly this session

Single-shot (`scrip --run bench/<k>.pl` once, output diffed against `<k>.expected`) across all 22 `bench/` kernels:

```
CRASH (SIGSEGV, rc=139): cal crypt derive divide10 ham log10 meta_qsort mu nreverse nrev
                          ops8 qsort queens queens_8 queensn query sendmore times10 zebra   (19)
OK:                       deriv fib tak                                                     (3)
```

Bisected (isolated `/tmp` test files, not committed — reproduce from the repro above):
- A literal list (`L=[1,2,3]`) — fine.
- A generic if-then-else — fine.
- A **recursive user predicate matching `[H|T]`** (classic 5-line `append/3`) — **crashes**. This matches `nrev.pl`'s own `app/3` exactly and plausibly explains most of the 19 CRASH kernels above (nearly all of them recurse over lists).
- A **deterministic, cut-committed counting loop** calling a passing kernel's own predicate twice (no backtracking, no choicepoints) — **also crashes**, at the second call.
- **Two flat sequential calls, no loop/recursion at all** (`bench__main, bench__main`) — first call succeeds and prints the correct answer, **second call crashes**. This is the minimal repro and the one quoted above.

So the trigger is not specifically backtracking/generators (though that also crashes, see below) — it is *any* second entry into a compiled user predicate's frame, however reached.

## Relationship to the already-tracked `PZ-4` gap

`GOAL-PROLOG-100.md`'s LIVE CURSOR and `FINDING-2026-08-27-seat07-prolog-lexprep-frame-disj0-gamma-crash-is-a-pz4-tier-violation.md` (same day, different task) independently diagnose a SIGSEGV in multi-clause/resumable predicates to a ζ-SPINE (RSP-relative) frame-slot read going stale across "unbounded intervening stack activity" between a predicate's suspend and its later resume — architecturally, RESULT/LOCALS need to move to ζ-ACTIVATION-FRAME (RBP-relative) for any predicate that can be re-entered, per Lon's BB FRAME-PLACEMENT CRITERION (`.github` `d3fd64e1`), and the mechanism that does this (**PZ-4**) is explicitly marked not-yet-landed there.

This finding's repro is consistent with the same root cause but demonstrates it is **not limited to disjunction/backtracking generators** — a flat `bench__main, bench__main` conjunction has no choicepoint at all, yet still crashes on the second call. That suggests the affected class is broader than "resumable predicates" alone: it may be *any* predicate whose compiled frame is entered more than once per process, which would include plain recursion generally (not just backtracking-driven repetition) — worth the PZ-4 owner double-checking the fix's scope covers this shape too, not only the disjunction-suspend/resume shape seat07's repro exercises. Not investigated further here — out of scope for this benchmarking row, and PZ-4 is already an open, actively-worked row.

## Secondary finding: existing timing harnesses cannot detect this class of crash

`bench_prolog_vanroy.sh`'s `wall_ms()` (and this row's own first draft of the new angle scripts, before being fixed) measure wall/cpu time around `timeout ... "$@"` without checking the child's exit status. `tools/bench_rusage` **always** prints a `BENCH_RUSAGE:` line — even for a child that segfaults — with the true outcome only visible in its `exit=` field (128+signal on a signal death). A harness that greps stderr TEXT for "segmentation"/"core dumped" (this row's own first attempt) or ignores exit status entirely (the pre-existing `bench_prolog_vanroy.sh`) will read a crashed run's tiny elapsed time as an implausibly *fast* real measurement — this is exactly how this row's own draft first reported SCRIP at ~1,400,000 iters/s on `deriv` before the bug was caught. Concretely: **`bench_prolog_vanroy.sh`'s previously-committed `m3_it`/`m4_it` figures (e.g. the 1381ms/1444ms-per-iteration numbers for `deriv` at N=1, committed historically to `corpus/benchmarks/prolog/vanroy/`) are very likely crash-artifact durations, not real per-iteration costs** — not re-verified/fixed here (out of this row's scope; `bench_prolog_vanroy.sh` is a separately-owned, pre-existing tool), but anyone citing those historical numbers should treat them as unverified until that script is updated to check `exit=` the same way this row's two new angle scripts now do.

## What this row (bench-rivals-prolog) does as a result

Given the above, **zero Prolog kernels are currently measurable for SCRIP under the three-angle campaign** — not a corpus-scope problem, not a tolerance problem, a real compiler crash on the only available timing mechanism (looping). All 22 `bench/` kernels are declared in `corpus/benchmarks/prolog/EXCLUDED.tsv` with a reason pointing here. The coverage gate (`test_gate_bench_rivals_coverage.sh prolog`) passes on that basis — declared, not measured, per its own three-bucket contract. `scripts/test_bench_prolog_timed.sh` (angle 1, live search), `scripts/bench_prolog_fixed_iter.sh` (angle 2, committed N), and `scripts/bench_triangulate_prolog.sh` (cross-proof + TSV + grid) are built and correctly report this reality; no code changes are needed to start producing real numbers once PZ-4 (or whatever fix covers this broader shape) lands — just re-run `bench_triangulate_prolog.sh` and thin `EXCLUDED.tsv` down to whatever's still genuinely unmeasurable.
