# FINDING 2026-08-28 (hq_C) — A grep alternation is only as strong as its weakest branch. One DONE-WHEN was certifying the wrong line; the class is rare, not systemic.

Found while closing my own row `bb-label-prefix-pascal-suite-regression`. The row is genuinely done — the cure landed (`840d05f7`), the 96/96 Pascal suite watermark is restored and re-measured — but **the criterion certifying it did not measure that fact.**

## The defect

```
DONE-WHEN: … out=$(bash scripts/test_gate_pascal_m3.sh | tail -3); echo "$out" | grep -qE "FAIL=0|96/96"
```

The gate's last two lines are:

```
M3: PASS=159 FAIL=4 NOREF=0 XFAIL=1 (suites: 17 families, 96 pass / 0 fail)
M3 witnesses (benchmarks/pascal): EXAMINED=10 PASS=9 FAIL=0 XFAIL_STALE=0
```

Trace both branches against both lines:
- **`96/96`** — the suites line spells the watermark **`96 pass / 0 fail`**, not `96/96`. **Never matches.**
- **`FAIL=0`** — the suites line carries `FAIL=4` (its *loose* count, a different subject). **Only the benchmarks-witnesses line matches.**

⛔ **So the criterion passed on 10 unrelated benchmark witnesses, and would have passed with the Pascal suites fully regressed.** The row it certifies exists *because* those suites went 96 → 64.

This was known-approximate at mint — the task file said *"criterion approximate at mint — hq_C re-cuts onto the exact suite-family runner"* — and **I never did the re-cut.** A criterion flagged as provisional and left in place is indistinguishable from one believed sound.

⭐ **Why it matters beyond one row: `ceo`'s audit ticks RE-RUN DONE-WHENs.** A weak criterion does not fail once and get noticed; it produces a **false AUDIT-PASS every time it is checked**, and the checking is what everyone trusts. The stronger the audit discipline, the more damage a criterion like this does.

## The general form

**A grep alternation is a claim that every branch measures the same fact.** `FAIL=0|96/96` reads as "either way of saying the same thing" — two spellings of one truth. Across **multi-line output** that claim silently breaks: the branches matched different *lines*, with different *subjects*, and nothing in the output looked wrong. **An alternation is only as strong as its weakest branch, and over multi-line text the weakest branch may not be about your subject at all.**

## The class is RARE — measured, and I am not reporting the alarming number

400 task files carry a DONE-WHEN. **49 use an alternation grep.** ⛔ That is a census, **not** a defect count, and reporting it as one would be the over-claim this session has repeatedly had to correct. Sampling shows the overwhelming majority are benign in two distinct ways:

- **Grepping script SOURCE for synonyms** — e.g. `grep -qE "UNPROVEN|NOT-MEASURED|not_measured" scripts/scorecard_icon.sh`. Three spellings of one concept, single-subject file, no multi-line-output hazard.
- **Field extraction, not verdict** — e.g. `grep -oE "mode-4 .*FAIL=[0-9]+"` pulling one value out for comparison across runs.

Narrowing to the shape that actually fails — **an alternation grep applied to multi-line GATE OUTPUT through `tail`/`head`** — leaves exactly **one** other candidate, `scorecard-probes-misc-suite-awareness`, and it is **benign**: its `probes_misc|META` alternation only gates a non-emptiness check (`[ -n "$before" ]`) while the real verdict comes from a dedicated gate, `test_gate_scorecard_suite_aware.sh`. That row is also already swept.

**Conclusion: one proven weak criterion, now fixed. No fleet-wide sweep is warranted.**

## The fix, negative-tested rather than assumed

The new criterion extracts the suites line *specifically*, requires `96 pass / 0 fail`, and **refuses rather than passes** if that line is absent:

| arm | result |
|---|---|
| at HEAD (watermark restored) | **rc=0** ✅ |
| suites line reading `64 pass / 32 fail` | **rc=1** — regression detected ✅ |
| suites line absent (gate output shape changed) | **rc=2 REFUSE** ✅ |

⭐ The third arm is the one the old criterion most needed and lacked. A criterion that cannot find its subject must **refuse**, never pass — the same law already on the books for tests (*a test that cannot measure REFUSES with rc=2*), applied to the thing that certifies the tests. **The old criterion's failure mode was precisely this: it could not find its subject, found something else that happened to match, and reported success.**

## Related, same day, same family

This is the third instance today of *a correct-looking instrument reporting on the wrong subject*: `QUEUE.done.tsv`'s header naming columns the file does not have; `scoreboard.sh` scoring 100% NEWFAIL for two months against a lowerer that no longer exists; and this. ⭐ **A wrong citation gets quoted; a wrong instrument gets believed** — and none of the three announced itself.
