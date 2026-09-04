# FINDING — CLASS FILED (not cured): a real-valued `to...by` generator prints results with a trailing
# `.0` in SCRIP; the real Icon oracle (icont/iconx v9.5.25a) prints the same values as plain integers.
# Isolated specifically to the `to`/`by` generator path — plain `write(3.0)` already agrees with the
# oracle in both compilers, so this is not the general real-to-string formatter.

**seat01 · 2026-09-03 · row `icon-ladder-top-rung-census-from-the-icon-book`** (LADDER RECIPE step 3:
a suite red, already reduced to a minimal witness by an earlier session, reasoned and filed here).

## What's wrong

`corpus/tests/icon/ALL.icn` entries 719/720 (`procedure_every_to_48`/`_49`, origins
`ladder__rung19_pow_toby_real_toby_neg`/`_pos`) are pre-existing rung19 witnesses. An earlier session had
already marked both `xfail=1` in `ALL.csv`, but `ALL.xfail` carried zero written reason for either name —
that gap (the xfail-reason gate) is closed by this FINDING plus the matching `ALL.xfail` entries.

Witness (already minimal, 3 lines):
```
procedure main(); every write(3.0 to 1.0 by -1.0); end
```

Oracle (`/home/resources/icon-master/bin/icont` + `iconx`, v9.5.25a, run fresh this session):
```
3
2
1
```
This matches the suite's own `.ref` exactly (`ALL.ref:5229-5232`) — confirming the `.ref` IS honestly
oracle-cut, not corrupted or hand-typed wrong.

SCRIP (tree SCRIP `380cc416`, both m3 `--run` and m4 `--compile`):
```
3.0
2.0
1.0
```

## Isolation

Plain `write(3.0)` (no `to`/`by` involved) prints `3.0` in **both** the oracle and SCRIP — they agree.
So this is not the shared real-to-string formatter in general (that formatter was already the subject of
`FINDING-2026-08-30-seat01-icon-cset-real-formatting-cured-and-ck-icn-further-characterized.md`, which is
a different symptom — a DROPPED trailing digit, `2.0` → `.2`, not an ADDED `.0` — and that finding already
confirms at least one similarly-shaped case has a distinct root cause; do not assume this is the same bug
reappearing).

The defect is specific to values produced by the `to`/`by` generator box. Not read/confirmed this
session which template owns it (`src/templates/bb/bb_to.cpp` / `bb_to_by.cpp` are the candidates by
name) — **walker scope ends here** per `MASTER-PLAN.md` § WHO FIXES WHAT: seats classify and file: "cure
only what is fixture-, xfail-, or instrument-level... a seat that finds itself editing `src/` for more
than one small, witnessed change hands the class to its HQ." This is a `src/` engine question, not
fixture-level, so it is not attempted here.

## Routing note

Not confirmed shared-node. Icon's `to`/`by` generator is not obviously SNOBOL4/Prolog-shared machinery,
but this was not checked against the actual template source. If hq_B's investigation shows the box (or
the real-value tagging it relies on) is shared with another frontend, re-route per RULES.md § SHARED-NODE
VERDICT SCOPE rather than assuming Icon-only.

## What this row did / didn't do

- Reasoned both `xfail=1` markers in `ALL.xfail` (previously bare flags, no written reason).
- Re-measured all rungs 00–35 (minus the pre-existing rung25 numbering gap, not chased) against
  `test_icon_ladder.sh` fresh this session (tree SCRIP `380cc416` corpus `88da45782`) rather than trusting
  `SCORE.md`'s stale "ZERO ladder__rung* origins" reading — every rung is genuinely BUILT and green
  **except** rung19's 2 witnesses named here.
- Did **not** touch `src/`. Did **not** attempt a cure. The fix and the shared-node question both belong
  to hq_B.

Verified: `bash scripts/test_icon_ladder.sh --to 35` (SCRIP `380cc416` / corpus `88da45782`, 2026-09-03) —
`graded=376 PASS=372 FAIL=4` (the 4 = these 2 witnesses × 2 modes; every other rung's witnesses PASS both
modes).
