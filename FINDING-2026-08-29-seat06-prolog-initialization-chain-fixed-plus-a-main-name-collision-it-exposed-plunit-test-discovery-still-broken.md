# FINDING — Prolog multi-`:- initialization/1` fixed (in-file AND cross-file), plus a `main`-name
# collision the fix exposed and had to fix too; SWI plunit suite still 0/57 — a SEPARATE, deeper
# test-discovery defect, confirmed content-independent

**seat06 · 2026-08-29 · row `prolog-only-the-last-initialization-directive-runs` · SCRIP HEAD `32a2d9df`**

## What changed

`src/lower/lower_prolog.c`'s `lower_pl_stage2` collected every `:- initialization(Goal).` directive
into a single scalar `goal_key`, last one silently winning. Fixed: goals now accumulate in a `static`
(cross-call) array and, when 2+ are found, get chained as `G1, G2, ..., Gn` and lowered as one combined
entry. `static` is necessary, not a style choice — `sm_preamble()` (`src/driver/scrip_sm.c:29`) calls
`lower_pl_stage2` **once per Prolog segment** (once per `.pl` file on the command line, or per polyglot
section), all sharing one `g_stage2`. The row's own DONE-WHEN is a **two-file** case
(`./scrip 1.pl 2.pl`); a per-call-local accumulator would only ever fix the within-one-file shape and
silently miss the cross-file one, which is what actually broke the SWI suite (`plunit.pl`'s own
`:- initialization(pj_suites_init).` racing the test wrapper file's `:- initialization(main).`).

Two design points worth flagging for whoever touches this next:

1. **Chained goals are INLINED (resolved via `resolve_pred_table_lookup`, body spliced in), never CALLED
   by name.** First attempt spliced the raw goal-reference terms into a `,`-chain and lowered that
   normally, relying on the standard call-lowering path to resolve each by name. That is what a normal
   multi-goal clause body already does, so it looked like the more "correct" choice (it would also fix a
   latent limitation where a compound `initialization(foo(X))` goal's arguments were never actually bound)
   — but it reintroduced a genuine bug: see next point. Reverted to inlining, matching the
   pre-existing single-goal path's own semantics exactly, just threaded across N goals instead of 1.
2. **A `main`-name collision, found via this fix, not present before it.** The combined entry point is
   registered in `proc_table` under the literal name `"main"` (pre-existing convention, unchanged). The
   overwhelmingly common Prolog idiom is `:- initialization(main).` — i.e. the *thing being chained in* is
   *also* very often a user predicate literally named `main`. With the by-name-call design (point 1),
   calling that "main" from inside the synthesized chain could resolve back to the chain's own entry
   point instead of the user's clause — self-referential, not the intended target.
   Switching to inline-not-call (point 1's revert) removed the *by-name-call* half of the collision, but a
   second half remained: `lower_pl_register_all_preds()` (called later in the same function, for `.pl`
   files with no PRIOR per-key resolve_bb registration) independently re-lowers and re-registers **every**
   `resolve_pred_table` entry, `main/0` included, producing a **second, unaware-of-the-chain** `proc_table`
   row also named `"main"`. Mode-3's own entry-point lookup (`src/driver/scrip.c:1761`, deliberately
   last-registration-wins per a standing, already-ruled-on comment there — see
   `polyglot-define-entry-address-wrong-in-merged-program`'s trace for why that site is guarded the way it
   is) then picks whichever "main" was registered **last** — which, since `lower_pl_register_all_preds()`
   runs after this fix's own registration, was always the *plain, unchained* one. Net effect: the seeding
   goal silently never ran, even though the chain was built correctly. Fixed by calling
   `resolve_bb_register("main/0", 0, bb_idx)` for the chain's own `bb_idx` (mirroring exactly what
   `lower_pl_register_all_preds()` itself does for ordinary predicates), so that function's own
   `if (resolve_bb_lookup(key, ar)) continue;` guard correctly skips the shadowing re-registration. Scoped
   to the N>=1 (a real chain was built) case only — the N==0 fallback path already had this same
   *harmless* duplicate before this fix (verified: both rows lower the identical unmodified user clause,
   so it doesn't matter which one wins) and was left untouched.

Also excluded from the goal list: `prolog_lower.c`'s own `pj_dir_<N>` synthetic wrapper predicates (see
`src/frontend/prolog/prolog_lower.c:780-806`) — a bare `:- dynamic/use_module/module/ensure_loaded/
discontiguous/meta_predicate/begin_tests/end_tests/nb_setval Goal.` directive gets silently rewritten by
the frontend into a synthetic `pj_dir_N :- Goal.` clause plus an `initialization(pj_dir_N)` statement,
indistinguishable at the AST level from a real user directive except for that name prefix. These were
**never individually called before** (the old scalar-overwrite bug meant at most one thing ever ran, and
in every case observed here it happened to be a real directive, never a `pj_dir_N`) — chaining them in as
real calls surfaces `rt_ab_undef_fn_stub` / `Error 22 Undefined function called`, an unrelated by-name
dispatch gap for whatever mechanism (if any) is supposed to make e.g. `dynamic/1` itself callable. Not
fixed here — excluded from the goal list by name prefix instead, matching what "nothing called them
before" already implied was safe.

## Verified

- Row's own DONE-WHEN: **PASS** (`1.pl`/`2.pl`, `fst`/`snd` in order, both as separate CLI args).
- Single-file single-directive (`:- initialization(main).`, the overwhelmingly common case): unchanged
  output, byte-for-byte same code path as before this fix for N==1... except it is no longer a *literally*
  separate code path (see design point 1/2 above) — verified behaviorally identical output regardless.
- Single-file 2 directives, no-directive default-to-`main/0` fallback, mode-4 two-file: all verified by
  hand, all correct.
- hq_C's own repro (`plunit.pl` + a `chk :- (nb_getval(pj_suites,X)->write(seeded(X));write(not_seeded))`
  wrapper): now prints `seeded([])` (was `not_seeded`) — the exact root-cause chain in this row's own brief
  is confirmed closed.
- The `main`-collision repro (`plunit.pl` + `main :- run_tests.` + `:- initialization(main).`): now prints
  `% 0 passed, 0 failed, 0 skipped` cleanly (was `Error 22 Undefined function called`, rc=1, before the
  inline-not-call fix; was silent rc=1 zero-output, the OTHER already-scoped-out defect's own signature,
  before the `resolve_bb_register` fix).
- Regression, all measured against an identical-baseline stash/rebuild comparison, not assumed:
  `test_prolog_rung_suite.sh` — **identical** `PASS=216 FAIL=13` (interp) / `PASS=22 FAIL=13` (compile)
  with and without this fix (same 13 pre-existing failures, confirmed unrelated). `test_smoke_prolog.sh` —
  5/5 all three modes. `test_crosscheck_prolog.sh` — `PASS=110 FAIL=0 SKIP=25 ORACLE_MISS=75` (ORACLE_MISS
  is a pre-existing, separate bucket, not a fail). `test_gate_polyglot_demos.sh` —
  `m3 PASS=7 FAIL=3 · m4 PASS=3 FAIL=7`, **identical** to the baseline this exact gate already had on
  record (`polyglot-define-entry-address-wrong-in-merged-program`'s own FINDING), confirming this
  Prolog-only change has zero effect on the separately-tracked polyglot DEFINE defect.

## NOT achieved: the row's own "0/57 → 57/57" SWI plunit payoff claim

`test_prolog_swi_suite.sh`: **still 0/57**, unchanged by this fix. Traced past the seeding bug (confirmed
fixed, above) to a SEPARATE, deeper defect: **`run_tests` completes without crashing and without any
diagnostic, but reports `0 passed, 0 failed, 0 skipped` — meaning nothing inside any `:- begin_tests(S).
... :- end_tests(S).` block is ever discovered as a runnable test**, independent of which suite file is
used. Confirmed content-independent with a minimal, hand-written repro (no plunit.pl content involved
beyond the shim itself):
```prolog
:- begin_tests(mysuite).
test(simple) :- 1 =:= 1.
:- end_tests(mysuite).
main :- run_tests.
:- initialization(main).
```
This ALSO prints `% 0 passed, 0 failed, 0 skipped` — zero tests found. This is not the initialization-
ordering bug (seeding is confirmed working via the `chk`/`nb_getval` repro above) and not either of the
two defects this row's own brief already named as riding along (silent-rc=1-on-failure;
`nb_getval`-on-unset-key). It is a third thing: whatever mechanism is supposed to collect `test(Name) :-
Body.` clauses written between a suite's `begin_tests`/`end_tests` pair (most likely: term/clause-level
introspection during the `pj_dir_N`-style directive rewrite, or a missing hook in how `test/1`-shaped
clauses get associated with the currently-open suite) never runs, or runs and finds nothing, for every
suite tried. **Needs its own row** — this session did not trace further than confirming the symptom is
general and reproducible in isolation; the plunit.pl shim's own suite-registration code
(`begin_tests`/`pj_suites_add`/`pj_run_suite`/wherever `test/1` clauses are supposed to get associated
with a suite — not yet located) is where to start.

## What's actually needed, for whoever picks up the SWI-suite payoff

1. Start from the minimal `begin_tests`/`test`/`end_tests` repro above (already confirmed to reproduce
   "0 passed" with zero suite-file content involved) — much smaller surface than any of the 57-test files.
2. Trace `pj_run_suite`/`pj_run_pairs` (`corpus/tests/prolog/plunit.pl`, search from `run_tests` at line 47
   onward) to find where it's supposed to enumerate a suite's registered tests, and compare against
   whatever `begin_tests(Suite)`/individual `test(Name) :- Body.` clauses actually leave behind at
   runtime — the seeding mechanism (`nb_setval`/`nb_getval` on `pj_suites`) is proven working now; the
   analogous mechanism for **individual tests within a suite** (there may not be an `nb_setval`-based one
   at all — `test/1` clauses might need to be found by clause/predicate introspection instead, which is a
   different kind of mechanism than what this row fixed) is the next unknown.
3. Grade against `swipl` directly (`lib_oracle_flags.sh`) on the minimal repro first, before touching any
   of the 57 real suite files — cheaper to iterate on and already confirmed to reproduce the defect.
