# FINDING — `term_variables/2` and `current_predicate/1` do not exist in SCRIP's Prolog

**seat08, 2026-09-05, FLEET-12. Measured while walking the isolation ladder, row
`prolog-ladder-every-feature-in-isolation-with-variations`, rung17 (ISO sec 8.5.5, 8.8.2, 8.16.7,
8.17.3-4).**

## What happened

5 forms declared; 3 BUILT clean both modes (`number_chars`, `halt_0`, `halt_1_status` — the last
proving `halt/1`'s exit-status argument propagates correctly end to end: `halt(3)` gives process
rc=3 in both m3 and m4, declared via `ALL.wantrc` since a nonzero rc must be declared, never
inferred). 2 forms red:

- `term_variables` — `existence_error(procedure, term_variables/2)`, confirmed via the witness
  (`term_variables(f(X,Y,X), Vs)`, never printing a raw unbound variable — bound each collected
  var to a distinguishable integer afterward and printed the now-ground term instead, so the
  witness stays portable regardless of internal variable-naming schemes).
- `current_predicate` — same SCRIP-internal REFUSE family as two earlier findings this session:
  `"builtin current_predicate is not on the ladder yet -- rung 7 lands it"` — identical wording to
  rung15's `stream_property` and rung16's `current_op` findings. **This is now the third
  independent builtin citing SCRIP's own internal "rung 7"** (its own implementation-order ladder,
  unrelated to this census's LADDER.tsv numbering) — worth whoever cures these three knowing they
  are apparently planned as one batch, not three unrelated gaps.

## Scope

Two missing-builtin gaps, not mine to cure. Rung17 sits in **hq_C's own lane** per this row's
LANE REVIEW (only rungs 15/16/18 moved to hq_R) — filed here, not routed externally. Both wired
into the master red on purpose (THERE IS NO XFAIL): origins `ladder__rung17_misc17_term_variables`
/ `ladder__rung17_misc17_current_predicate`.

## Fix shape (not attempted here)

`term_variables/2` is a standard tree-walk collecting distinct unbound variables in
left-to-right, first-occurrence order — likely belongs beside whatever already walks terms for
`copy_term/2` (which works, per the general suite) or `functor`/`=..` (ditto). `current_predicate/1`
is one of (now) three reflection builtins sharing the "rung 7" citation; whatever lands
`stream_property`/`current_op` likely lands this alongside them.
