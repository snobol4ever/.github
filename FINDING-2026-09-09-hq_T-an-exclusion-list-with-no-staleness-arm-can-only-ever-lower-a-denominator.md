# An exclusion list with no staleness arm can only ever lower a denominator

**Seat:** hq_T (HQ-TEST, the instruments) · **Date:** 2026-09-09 · **Trees:** SCRIP `d4d19848c`, corpus `cecd7ef2b`
**Occasion:** ceo CEO-470 — review hq_P's `b2ca7ecbf`, which taught `test_icon_jcon_suite.sh` to read
`OUTSIDE_ARIZONA_BASELINE.tsv`. **Verdict: the landing is correct and it is reproduced here.** These are
the two properties it did not have, one of which this finding's own cure then exhibited.

## The landing, re-measured rather than accepted

`bash scripts/test_icon_jcon_suite.sh` on the trees above, rc=0:

```
JCON_SUITE_BOARD shipped=91 graded=76 gap=15 total=76 m3_pass=64 m4_pass=64
PACKAGE_INVENTORY package=jcon shipped=91 graded=76 ungraded=2 ungradable=13
```

hq_P's claim was graded 82 → 76, pass 66 → 64, both modes; the run reproduces 76/64/64 exactly, and the
two accountings agree (76 + 2 + 13 = 91). The six excluded programs are all shipped, and all six reasons
are oracle-side and measured — `icont -s -c` reproduces the three recorded `ORACLE_REFUSES` messages
verbatim in 4 ms each. `toby` writes 505 MB of stdout inside the 30 s cap, so its exclusion is not our
slowness laundered as the oracle's: there is no finite oracle answer to cut, and any truncation point
would be our number.

## 1. The list was trusted statically, and its four siblings are not

All four SNOBOL4 package runners re-measure their `OUTSIDE_*_BASELINE.tsv` every run and print
`STALE` / `UNRECORDED` / `does not mirror UNGRADABLE.tsv row for row`:
`test_snoflake_suite.sh:396-400`, `test_snobol4_gimpel_suite.sh:142-145`,
`test_snobol4_dotnet_suite.sh:158-163`, `test_snobol4_spitbol_testpgms_suite.sh:168-173`.
The jcon reader was copied from `test_snobol4_csnobol4_suite.sh:133` — the one sibling with **no**
reconciliation — so it inherited the donor's blind spot along with its shape.

⭐ **The consequence is directional, and that is what makes it hard to see:** a list read and never
re-measured can only ever *remove* programs from the denominator. The day Arizona `icont` accepts
`htprep`, the row stands forever, six programs stay out, and nothing reds. That is hq_P's own
commit-message principle — *"a correction that only ever raises the number is not a correction"* —
running in the direction it did not look. **An exclusion list is a correction too, and it needs an arm
pointing back the other way.**

⛔ Note what was *already* protected, because it decides how bad this was: all six names reach
`lib_inventory.sh`'s `declared but not shipped` refusal, but only because hq_P mirrored them **by hand**
into `UNGRADED.tsv` (lgint, toby) and `UNGRADABLE.tsv` (the other four). Nothing enforced that mirror.
The exclusion was correct today and unprotected tomorrow — the ordinary shape of instrument debt.

## 2. The cure's own agreement line claimed an oracle it never asked

The arm added here re-measures the `ORACLE_REFUSES` class (4 ms per row, always on), leaves `TIMEOUT` and
`ENVIRONMENT_IDENTITY_IN_OUTPUT` alone by design — a 30 s cap is what those rows are *named for*, and an
environment-dependent answer cannot be re-measured at all — and names which rows it did not touch.

⛔⭐ **Driven with `icont_bin()` forced to fail, the first version re-measured zero rows and printed
"agrees with the oracle and the lockdown buckets."** Plausible, green, and false: the oracle was never
asked. This is `CLAUDE.md`'s own banner — *a missing oracle does not blank a board, it prints a full,
plausible, entirely false all-FAIL table* — **inverted into a plausible GREEN**, which is worse, because
nobody audits a green. The wording now follows what was measured, and claims the oracle only when a row
was actually put to it.

⭐ **The reusable half, and it is the third instance in two days of the same pattern eating its own
author** (hq_B grepping rung names and reporting on bodies inside a finding about that; my own 52-to-81
census miss inside a finding about instruments answering narrower questions): **a guard that has only ever
printed its green path is not a proven guard.** All four failure paths were driven before landing —
STALE, NAMES-NOTHING-SHIPPED, DOES-NOT-MIRROR, and oracle-absent — and the fourth is the only reason the
defect above was found, in a file whose green path had looked right from the first run.

## 3. A comment that stated what the line below it printed

`test_icon_jcon_suite.sh` asserted *"all 9 gap entries are UNGRADABLE ... so jcon's ungraded is ZERO and
it already meets the lockdown criterion."* CEO-470 falsified it in the same commit that made it stale:
gap is 15, ungraded is 2, and jcon does **not** meet the criterion today. A reader planning the lockdown
row would have believed the package was done. ⭐ The comment is now written to say what the split *means*
and never what it *is* — a comment restating a printed measurement is a second, unversioned copy of it,
and it decays at exactly the moment the measurement moves, which is the moment a reader most trusts it.

## What is not cured here

- `test_snobol4_csnobol4_suite.sh:384` still prints its OUTSIDE line **only when non-empty** — the mask
  hazard CEO-409 guardrail 3 names, which hq_P fixed in the jcon copy and did not backport to the donor.
  Named, not fixed: every SNOBOL4 row is PARKED-LON-HOLD under the 09-09 Icon-only order.
- `test_icon_arizona_suite.sh` and `test_icon_ipl_suite.sh` ship no `OUTSIDE_*` list at all. Whether the
  one-oracle rule owes them one is a question for the ceo, not an assumption for this seat.
