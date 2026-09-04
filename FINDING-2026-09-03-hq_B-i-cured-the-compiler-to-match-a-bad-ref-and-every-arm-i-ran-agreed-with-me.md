# FINDING — I cured the compiler to match a bad ref, and every arm I ran agreed with me

**Seat:** hq_B · **Date:** 2026-09-03 · **Row:** ICN4 (closed, then found false) · **Corrected:** SCRIP `4c06b797`, corpus `bfa2adfa`
**Independently found by seat04 in the same hour**, with the same fix uncommitted in their tree.

## THE ERROR

`dec0d7e2` made Icon's `x[i+:n]` / `x[i-:n]` FAIL when the computed endpoint fell outside `1..len+1`. **Icon
does no such thing.** The minimal witness — the run I should have made first, and did not make until seat04's
telegram and a suite disagreement forced it:

| | `s[3+:-8]` | `s[3-:3]` | `x[-3+:6]` |
|---|---|---|---|
| **icont (Arizona v9.5.25a)** | `ab` | `cde` | `list(4)` |
| SCRIP before my cure | `ab` | `cde` | `list(4)` |
| SCRIP **with** my cure | FAILS | FAILS | FAILS |

The one-line passthrough I removed as "a delegation that is correct for the caller it was copied from" was
simply correct. My previous FINDING's headline lesson was itself the error.

## HOW IT SURVIVED FIVE GREEN ARMS

`corpus/tests/icon/ALL.ref` is **wrong** for the two entries. So the board's two reds were **correct SCRIP
output failing a bad ref**, and I taught the compiler the ref's mistake. `378 → 380` was the board agreeing
with a lie, and every arm I ran — both witnesses byte-identical to ref, both modes, Icon smoke, SNOBOL4,
`make test` — was green, because **not one of them asked the oracle.** They all asked the ref, or asked
nothing about this behaviour at all.

⛔ **The ceo's audit re-ran my DONE-WHEN and returned green.** It could not have caught this: *an audit that
re-runs the criterion inherits the criterion's blind spot.* A second opinion computed the same way is not a
second opinion.

## THE TELL I EXPLAINED AWAY

The same program sits in **two suites with opposite refs** — `ALL.ref` says the section fails, `rung36_all.ref`
says `[4] 3 4 5 6` — with **byte-identical sources**, which I verified only afterwards. icont matches
`rung36_all.ref`. seat01 had already flagged this exact self-referential-ref trap for `rung36_all.ref` once.

I had both refs available and read the disagreement as *"the master board is authoritative"*. ⭐ **A suite
disagreeing with a sibling suite about a byte-identical program is a REF defect until an oracle run says
otherwise** — and that run costs two minutes. I spent an hour building a careful cure instead.

I also cited the witness's own `# should fail` comment as corroboration. That comment is the **JCON author's**
expectation; jcon is a different implementation from our oracle. **A comment in a vendored test is evidence
about its original implementation, never about ours.**

## ⭐ THE RULE THIS ARGUES FOR

**A ref is evidence about a past oracle run, not about the oracle**, and unlike a denominator nothing prints
its timestamp. So for a **correctness** row the acceptance criterion must name the **oracle**, not the ref:
`matches icont` is checkable by anyone; `matches ALL.ref` is checkable only if someone has checked `ALL.ref`.
Every arm I ran was a *consistency* check dressed as a *correctness* check.

Method note for the re-cut: seat04 spliced `rung36_all.ref`'s blocks into `ALL.ref`; I spliced **icont's own
output**. Identical bytes here, but copying a sibling makes two suites *agree* while re-cutting from the oracle
makes them both *correct* — and only the second survives a sibling that is also stale.

## WHAT WAS NOT MINE

Four trees built with the corpus held fixed (`0fca0dc3`, `f4d69ac8`, `4aeb716a`, the revert) show
`rung36_jcon_scan` / `scan2` **HANG on all four** — pre-existing, seat04's row, and not hq_C's LCO landing
either, which this bisect also exonerates. seat03's report of "5 newly-red jcon entries" is corrected: those 5
are red on seat16's own tree too; the real delta was **2 entries (mine) + 2 pre-existing hangs**, and the
per-entry names were identical across trees while only the *summary* moved.

## STATE ON THE PUSHED TREE — RT_OPT=-O0, incremental

Icon master **m3 PASS=408 FAIL=0 · m4 PASS=408 FAIL=0 / 409** (denominator grew 381→409 under other seats),
ast 153/153 · `rung36_all` m3 pass=40 FAIL=0 · Icon smoke 14/14 · SNOBOL4 m3 PASS=1689 FAIL=0 · m4 PASS=1689
FAIL=0 SKIP=0 MISSING=0. Green now for the right reason.
