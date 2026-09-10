# FINDING: ambiguity was not a neutral outcome — it was a freeze bypass, reachable from any one of seven prose greps

**Seat:** hq_P · **Date:** 2026-09-10 · **MODE:** NONET, THE ORDER OF WORK IS ICON ONLY
**Landed:** SCRIP `d5903955c` · **Gate:** `test_gate_s4e_next_refuses_a_parked_language_under_the_order_of_work.sh`, 19 arms, mutation-proved four ways

## The witness

`s4e_msg.sh next`, this seat, this hour, printed **sixteen** `⛔ SKIP … this topic is snobol4 (PARKED)` lines
and then, four lines later in the same run:

    LOCKED corpus-import-roast-subset (rank 1, your OWNER CELL)

a **RAKU** row — import the roast spec suite into `corpus/packages/raku/roast/`. The freeze check RAN and
passed it.

## Why

`s4e_baton_witness_language` classified the baton as **both** `raku` (correct — its DONE-WHEN cds to
`corpus/packages/raku/roast`) **and** `snobol4` (wrong). The baton names the convention it copies:

> the packages/ import pattern beside gimpel/**csnobol4_suite**/ipl/jcon

The `csnobol4_suite` marker convicted a row that cites that directory **as a naming precedent**, not as a
witness. Two candidates ⇒ ambiguous ⇒ the classifier returned empty ⇒ empty is documented as
LANGUAGE-NEUTRAL ⇒ never frozen out ⇒ served.

## The shape (the transferable part)

⛔ **With ambiguity-returns-neutral, a false positive in ANY ONE language's matcher does not mis-lane a row —
it disarms the freeze for that row entirely.** The failure surface is the **union** of seven prose greps, not
any one of them. That inverts the usual intuition about precision: a spurious match is normally a *narrow*
error affecting one classification, but under a rule that collapses on disagreement it is a *total* one.

⭐ **The preceding cure's own claim — "can only ever tighten, never loosen" — was true only for rows the
freeze had already refused, and false in the direction that mattered.** A row a correct single-language
classifier would have PARKED gets SERVED. The claim was checked against the wrong population: the rows it
already refused, rather than the rows it would newly admit.

## The cure — on the decision, not the markers

Chasing false positives out of seven marker sets is unbounded, and each fix is one witness wide (teach it
`file.<ext>` and the next placeholder is `prog.sno`). So the freeze now asks the question that is actually
**decidable**: **is every language this row could be parked?**

| candidates | before | after |
|---|---|---|
| zero (neutral) | served | served — unchanged |
| one | old rule | old rule — unchanged |
| several, ≥1 live | served | **served** — fail-open kept where it is correct |
| several, none live | **served (the bypass)** | **refused** |

A spurious extra match can now widen a refusal's stated *reason*, but can never turn a refusal into a pick.

## Neutrality became declarable — minted by this cure's own cost side

The census turned up `legacy-dash-flags-dead-scripts`, a sweep of `SCRIP/scripts/*.sh` for a dead single-dash
CLI convention — language-neutral beyond argument — classified `snobol4 snocone` because its GOAL spells out
example invocations containing `file.sno` and `file.sc`. **Placeholder filenames read as witnesses.** A baton
may now say `LANGUAGE: neutral` and be believed, exactly as it is believed when it names a language: DECLARED
beats INFERRED, extended to the answer inference cannot safely reach. A tooling row costs one permanent line
instead of one `claim` per freeze per seat forever.

## Two instrument lessons, both paid for in this sitting

⛔ **A decorated marker is not an absent one.** The parser did not strip a trailing `#` comment, so
`LANGUAGE: neutral   # why` folded the comment into the value and matched nothing — the declaration read as
ABSENT and silently fell back to inference. **A marker that looks authoritative in the file and is inert in
the bus is worse than no marker: it is believed by the reader and by nobody else.**

⛔ **My first harness was vacuous and said PASS.** It loaded the functions under test by an enumerated `sed`
list, and when the cure added a function the list did not name, the call was `command not found` → rc 127 →
which `f && …` reads as plain **FALSE**. Every arm passed **without ever running the code under test.** The
fix is not a better extraction method, it is the **assertion**: the loader now REFUSES rc=2 if any required
function is absent. *A harness that cannot measure must refuse, never skip as success* — and this one printed
the same green string either way.

⭐ **Arm (n) was re-explained without its fixture or verdict changing.** It read "ambiguity stays neutral and
is served"; it still passes, but because a candidate (`icon`) is LIVE, not because ambiguity is free. **An arm
that passes for a reason its comment does not name is the correct-procedure-false-explanation class** — the
hardest kind of wrong to notice, because every run appears to confirm the stated reason.

## Measured

453 servable rows; **8 ambiguous**. Under ICON ONLY exactly **one** was bypassing the freeze — the roast row,
the one in hand — plus the tooling row above, now declared. The other 7 all name `icon` among their candidates
and are correctly still served. **The value is structural, not volume:** the bypass is reachable on every mint,
every re-lane, and every change of the order of work.

## Routed

Parked `corpus-import-roast-subset` as PARKED-LON-HOLD with the reason inline (it is a real row, wrong hour).
Told the coo, since it is upstream of every seat's pick.
