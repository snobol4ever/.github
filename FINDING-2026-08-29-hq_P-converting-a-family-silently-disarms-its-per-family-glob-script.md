# FINDING — converting a family silently DISARMS its per-family test script, and the commonest failure is a FALSE GREEN

**hq_P · 2026-08-29 · SCRIP `bb350a4f` · corpus `c7f86c089` · row `tests-consolidate-prolog`**

## What happened

Nine Prolog families were converted to suite pairs and their loose originals deleted, per
`byte-equal-or-no-delete` (every entry re-validated in both directions, both modes, before any
delete). Each family also had a per-family runner, `scripts/test_prolog_<fam>.sh`, whose body is:

```bash
CORPUS=$S4E/corpus/tests/prolog/rung27        # <- the directory the conversion empties
for f in "$CORPUS"/*.pl; do ... done
echo "PASS=$PASS FAIL=$FAIL"; [ "$FAIL" -eq 0 ]
```

Deleting the originals broke **nine scripts in three different ways at once**, none of which
announced itself:

| families | after conversion | why |
|---|---|---|
| `rung27` `rung28` `rung39_atom_iso` | `PASS=0 FAIL=0`, **rc=0** | ⛔ **FALSE GREEN** — unmatched glob runs nothing, `FAIL` stays 0, `[ "$FAIL" -eq 0 ]` exits 0 |
| `rung31` `rung33` `rung34` `rung38` | `PASS=0 FAIL=N`, rc=1 | dir held *only* the deliberately-skipped red witnesses, so the script graded the exclusions as the family |
| `rung32` `rung35` | rc=0, no `PASS=` line | glob empty, loop never ran |

⭐ **The middle column is the whole finding: the same deletion produced a false GREEN and a false RED
depending only on whether that family happened to have a skipped red witness.** Neither is a verdict
about the code under test, and the green one is the dangerous half — it reads exactly like success.

## Why it is a class, not an incident

An empty glob is indistinguishable from a passing suite in any script whose verdict is
`[ "$FAIL" -eq 0 ]`. The count of things tested is never checked, so **zero tested and zero failed
collapse to the same exit code**. Every remaining `tests/prolog` family — 102 loose files still
undeclared — has the same shape, so this fires again on each future conversion.

The tree already knew: `test_prolog_rung_suite.sh` carries a comment naming the *"empty-glob
false-green — the exact bug this same task found and fixed in 7 other per-rung scripts."* It was
fixed seven times and never turned into a rule, so it recurred nine more times in one commit.

## The cure

All nine rewritten to the established post-conversion pattern (`test_prolog_rung26.sh`): delegate to
`corpus_suite_harness.py run --lang prolog --modes m3,m4` (the modes the conversion proved
byte-equal under), sum `fail+crash+hang+unproven` across both modes, and — the load-bearing part —

```bash
if [ ! -f "$SNO" ] || [ ! -f "$REF" ]; then
    echo "REFUSE (rc=2): $FAMILY suite not found ... -- cannot measure, not a pass"; exit 2
fi
[ -n "$board" ] || { echo "REFUSE (rc=2): harness produced no SUITE_BOARD line ..."; exit 2; }
```

**After:** 9/9 rc=0, PASS = 2× entry count, FAIL=0 — **74 real assertions where the old form made 0.**

**Negative-tested** (a gate minted without one is the same class wearing a different hat): suite
hidden → `rc=2 REFUSE`; suite restored → `rc=0`.

## ⛔ Standing instruction

**Before deleting a family's loose originals, run `grep -l "$FAMILY" scripts/test_prolog_*.sh` and
rewrite the runner in the SAME commit.** A conversion that lands without it leaves a green board and
a dead test — and the board is what everyone reads.

⭐ The general form, which is why this is worth a FINDING rather than a commit message: **a test whose
verdict is derived only from a failure count cannot distinguish "nothing was wrong" from "nothing was
run." Any such test must assert a nonzero denominator or refuse.** That is the same law as the
`make test` false-green trap and the vacuous-gate sweep, reached from a third direction.
