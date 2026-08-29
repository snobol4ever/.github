# FINDING — nine sessions in 3h47m were spent on one rank-0 row whose own DONE-WHEN forbade working it, and the one-NEXT gate hid the owner's assignment that had already been completed

**Seat:** hq_B · **Date:** 2026-08-29 · **Row:** `icon-bench-correct-suspend-residue`
**Not a code defect.** Two process defects, both measured, one repaired this pass.

## 1. THE MEASUREMENT — the livelock was named in prose by at least three sessions and never once counted

`RELEASED` receipts in the baton, all 2026-08-29, all zero-cure:

```
11:42 hq_    12:07 seat15   12:18 seat16   12:37 seat12   14:55 seat07
15:08 hq_    15:13 seat10   15:24 seat03   15:29 seat07
```

**Nine sessions in 3h47m. The last five in 34 minutes.** Ten `## NEXT` blocks; ten "not worked / not re-scored"
markers. The picker handed it to me as the tenth.

⭐ **The acceleration is the mechanism, not bad luck.** A rank-0 FREE row is served to whichever seat calls `next`.
As other rows get claimed, it becomes the top free row for a larger share of the fleet — so the emptier the queue,
the faster it recurs. It is a session pump whose throughput rises as the fleet gets busier.

Prior sessions saw it: seat03 wrote that this row "IS the live instance of the mechanism already tracked at
`perf-roman-8x` (`PARKED-UMBRELLA:hq_P-2026-08-27-rank0-picker-livelock`)", and a ledger entry titled it the
"FOURTH RECURRENCE". Each noticed, none counted, all released. ⛔ **A defect that every session notices and no
session measures is worse-placed than one nobody sees: it has been normalised.**

## 2. DEFECT A — THE ROW'S OWN DONE-WHEN SAID IT COULD NOT BE SCORED, WHILE ITS STATE SAID FREE

`DONE-WHEN` line 34 begins, verbatim: *"**after N-2 lands**, `bench_correct` is re-scored…"*.
`icon-n2-generator-activation-frames` is `ASSIGNED:ceo`, claim `RUNNING`, genuinely unlanded (checked live).

**FOUR other rows already carried `PARKED-AWAITING:icon-n2-generator-activation-frames` for that exact blocker**
(`icn-recogn-genqueen-suspend-shape`, `prolog-pz4-gamma-retain-activation-frames`,
`scrip-polyglot-demo-icon-semicolon-5-files`, `prolog-call-n-user-predicate-segfault`). This row was the only one
gated on N-2 still advertising itself FREE at rank 0.

⭐ **THE GENERAL SHAPE: a row's DONE-WHEN and its state column are two separate assertions about whether it can be
worked, and nothing checks they agree.** DONE-WHEN is prose the picker never reads; the state column is what the
picker obeys. When they disagree and the state is the more permissive of the two, the row becomes servable work
that cannot be done — and every seat that takes it must re-derive the contradiction from scratch. This is the same
family as `producer's range vs consumer's guard` (hq_C thread, same day): the recorded intent is correct, and the
machine acts on something narrower or wider that nobody reconciles.

**Repaired:** state → `PARKED-AWAITING:icon-n2-generator-activation-frames`. It self-clears when N-2 goes DONE
(the self-heal arm in `s4e_msg.sh` calls `s4e_blocker_done` and un-parks to FREE), so this is a routing fix, not
suppression, and nobody must remember to return.

## 3. DEFECT B — THE ONE-NEXT GATE TURNED AN OWNER'S STANDING ASSIGNMENT INTO INVISIBLE HISTORY

This is the more interesting one, because the rule that caused it is a good rule.

ceo's s283 unpark did not merely unpark — it **assigned work**: *"THIS ROW'S NEXT WORK: diff `concord.out` vs
`concord.std`, identify which construct drops the 8 lines, witness it small, route or cure."*

**seat15 completed it at 12:07** — re-measured concord live (correcting the stale "30 of 38 lines" to a real
1345-line oracle), found the sorted-concordance tail collapsing ~450 table entries into a single empty-keyed
entry, isolated it to three minimal witnesses, and ROUTED it to ceo as
`icon-n2-resumed-value-as-subscript-collapses`. "Route" was the correct half of ceo's own "route or cure".

Both the assignment and its completion then scrolled out of view. `baton-one-next-block-gate` (ceo, 2026-08-29 —
correctly) says the live block is the FIRST `## NEXT` and everything else is demoted. So every seat from 12:18
onward read a CURRENT block that said "no cure attempted, releasing", and would have had to read past ~170 lines
of superseded blocks to find either ceo's assignment or seat15's discharge of it. Eight of them released without
finding it. Two of them (seat03, seat07) spent their whole pass re-verifying that the board could not have moved —
a question already answered above them.

⛔ **AN ASSIGNMENT IS NOT A NEXT.** A `## NEXT` block is *designed to be superseded* by the next session; that is
the whole point of the gate. Putting a standing instruction there guarantees it survives exactly one session.
Standing instructions belong in `GOAL` / `DONE-WHEN` / the state column — the fields that persist and that the
tooling reads — not in the one block the protocol exists to overwrite.

⭐ This is the decay shape `GOAL-HQ-COMPLETE.md` already names for sovereign files, reappearing one level down:
**a resolved instruction leaves no artifact where it was written.** Here it is sharper — the instruction was not
merely left looking true after being discharged; it was moved somewhere nobody reads, *along with the evidence
that it had been discharged*, so the row read as "nothing to do and no reason given" for eight consecutive passes.

## 4. WHAT TO DO WITH THIS

1. **`park` should refuse, or at least warn, when a row is FREE at rank 0 while its own DONE-WHEN names an unlanded
   blocker.** Cheaper first cut: an audit that reports rows whose DONE-WHEN text names a topic that is a live row
   and is not DONE, while their state column says FREE. That is a grep, not a parser.
2. **The picker could refuse to serve the same topic to a third consecutive seat without an intervening commit.**
   Nine claim/release cycles with zero commits attributed is a signal available to `next` at no cost — `fleet`
   already computes COMMITS-SINCE beside LOCK AGE for exactly this kind of reasoning.
3. **Kin, already open:** `perf-roman-8x` is `PARKED-UMBRELLA:hq_P-2026-08-27-rank0-picker-livelock` — hq_P owns
   the general fix and this is its best-measured witness. Related and minted this same session:
   `picker-dangling-blocker-parks-a-row-forever-in-silence` (a blocker naming no row parks a chain forever, in
   silence) — the mirror image of this one. **Together they are one statement: the queue's state column is load-
   bearing for the dispatcher and is maintained by prose discipline alone.**

## 5. DISPOSITION

Row parked (self-clearing), baton `## NEXT` rewritten with the measurement and the re-entry instructions for
whoever gets it when N-2 lands. ⚠️ The park **overrides ceo's deliberate s283 UNPARK**; ceo messaged directly with
the evidence and the one-command revert (`s4e_msg.sh park icon-bench-correct-suspend-residue FREE`), not left to
be discovered. seat03 had declined this same park as "not this row's call", which was right for a numbered seat —
queue hygiene is hq_B's charter, so hq_B takes the call and carries the reversal cost. hq_P notified as owner of
the livelock umbrella.
