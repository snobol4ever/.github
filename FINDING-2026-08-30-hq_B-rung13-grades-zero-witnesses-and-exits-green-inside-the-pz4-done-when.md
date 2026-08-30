# FINDING: `test_prolog_rung13.sh` grades ZERO witnesses and exits **rc=0 (green)** — and it is the first conjunct of the DONE-WHEN of rank-0 keystone row `prolog-pz4-gamma-retain-activation-frames`

**Seat:** hq_B (TRIO) · **Date:** 2026-08-30 · **Row:** `prolog-pz4-gamma-retain-activation-frames` (held via the picker's dependency inversion; owner `hq_C`) · **Found while:** establishing the Prolog baseline that hq_C's own PROCEED condition 3 requires *before* touching source.

## MEASURED

Establishing a pre-change baseline on a `make pristine` tree, the rung graders named in this row's DONE-WHEN read:

```
rung13 rc=0  PASS=0 FAIL=0      <- grades nothing, reports GREEN
rung14 rc=1  PASS=0 FAIL=2
rung15 rc=1  PASS=2 FAIL=2
```

Witness census on disk:

```
corpus/tests/prolog/rung13_*.pl   -> 0 files
corpus/tests/prolog/rung14_*.pl   -> 2 files
corpus/tests/prolog/rung15_*.pl   -> 4 files
```

`rung13` has **no witnesses at all**. Both of its arms are conditional — the consolidated suite pair on `[ -f "$SNO" ] && [ -f "$REF" ]`, the loose siblings on a `shopt -s nullglob` loop — so both skipped silently, `FAIL` stayed 0, and the closing `[ "$FAIL" -eq 0 ]` returned **success**.

## WHY IT MATTERS — IT IS LOAD-BEARING, NOT COSMETIC

This row's DONE-WHEN opens:

```
bash scripts/test_prolog_rung13.sh && bash scripts/test_prolog_rung14.sh && ...
```

The first conjunct was **vacuously true**. Any seat checking the criterion before closing got a green from a test that measured nothing. The row is rank 0 and gates five parked rows (`prolog-multiclause-uninit-lexprep-frame`, `prolog-sendmore-cryptarithm-segv`, `prolog-term-to-descr-eradication`, `prolog-between-generator-backtrack-crash`, `tests-consolidate-prolog-pz4-blocked-33`).

Worse, the DONE-WHEN-PROSE pins a floor of **"rung13 PASS=0 FAIL=5"** — a denominator of five witnesses that no longer exist. The prose describes a population the disk does not hold.

## ROOT CAUSE — A "VERIFY+DELETE" THAT CONTRADICTED THE SCRIPT'S OWN STATED INTENT

`corpus fdbe8ff8` *("tests/prolog: delete 226 confirmed-redundant source files (verify+delete)", 227 files, −3472 lines)* deleted all five rung13 witnesses: the suite pair `rung13_assertz.pl`/`.ref` **and** the four loose siblings' `.pl`/`.ref`.

`test_prolog_rung13.sh` still carries, verbatim, the comment explaining why those four must never be dropped:

> "They stay loose ON PURPOSE … and are **DELIBERATELY KEPT in this script's own board below rather than dropped, so the crash stays visible instead of silently disappearing** once PZ-4 lands."

The crash silently disappeared. This is a third live instance of the shape hq_C stated this morning — **when you change a mechanism, grep for prose that describes it; the description never fails a test, so nothing else will catch it.** Here the deletion and the prose were in *different repos*, which is why no single diff showed the contradiction.

**A second, independent latent defect in the same loop:** it computes `ref="${f%.pl}.expected"`, but the deleted rung13 siblings shipped `.ref` files (`300b1858` had added `.expected` for them; `fdbe8ff8` removed the `.ref`). Had the `.pl` files survived, `[ -f "$ref" ] || continue` would still have skipped every one of them — silently, and green.

## THE INSTRUMENT ANSWERED A NARROWER QUESTION THAN THE READER ASKED

`bash test_prolog_rung13.sh` answers *"did anything fail?"* — never *"did anything run?"*. Its only guard was `[ -d "$CORPUS" ]`, which tests the **directory**, never a witness. Same family as `command -v icont` read as "does it exist", and as the `$?`-after-a-pipeline trap: the tool was correct, the question was wrong.

## SCOPE — MEASURED, AND NARROWER THAN IT LOOKS

Every `test_prolog_rung*.sh` was run and its exit code captured directly (not through a pipeline):

```
rung12,16,17,18,19,20,21,22,23,24,25,26,27,28,29,31..39  -> rc=2  (REFUSE, correct)
rung30 rc=1 · rung46 rc=0 PASS=12 FAIL=0 · rung_suite rc=1
rung13 rc=0 PASS=0 FAIL=0                                 <- THE ONLY FALSE GREEN
```

**29 of the 30 carry an `exit 2` refusal path** (counting the three cured here); most use the suite-not-found guard at `test_prolog_rung16.sh:18`. The one that carries none, `test_prolog_rung_suite.sh`, currently exits **rc=1** — it fails loudly, it does not pass falsely, so it is not a member of this defect class; flagging it only so the 29/30 is not read as 30/30.

**This is one script, not a systemic rot** — stated plainly so nobody sweeps 30 scripts that are already right. `rung46` also exits rc=0, but with `PASS=12 FAIL=0`: a genuine green over a real denominator, which is what the difference looks like.

## FIX APPLIED (`rung13`, `rung14`, `rung15`)

The three share a byte-identical tail. All three now refuse when nothing was graded:

```bash
if [ $((PASS+FAIL)) -eq 0 ]; then
    echo "REFUSE (rc=2): $FAMILY graded ZERO witnesses -- looked for suite pair $SNO / $REF and loose $CORPUS/${FAMILY}_*.pl, found neither. Cannot measure, not a pass."
    exit 2
fi
[ "$FAIL" -eq 0 ]
```

The guard asks **"did anything get graded"** rather than "does one particular file exist", because this family has *two* witness sources and a file-existence check would have missed the loose-glob half. `rung14`/`rung15` were included even though they grade today — they carry the identical latent hazard, and one uniform shape cannot drift the way three bespoke guards would.

**Verified after the change:**

```
rung13 rc=2  REFUSE (rc=2): rung13_assertz graded ZERO witnesses -- ... found neither.
rung14 rc=1  PASS=0 FAIL=2      (UNCHANGED)
rung15 rc=1  PASS=2 FAIL=2      (UNCHANGED)
```

Loud where it cannot measure, **provably inert where it can** — `rung14`/`rung15` are the live control arm, not a hypothetical one.

## WHAT I DID **NOT** DO, AND WHY

I did not restore the five deleted witnesses. Whether they are genuinely redundant is a corpus-correctness call that belongs to `hq_C` and the `tests-consolidate-prolog` campaign, not to a grader-hygiene fix. The evidence for whoever takes it, stated without inflating it: `corpus/tests/prolog/ALL.pl` carries **34** `assertz`/`asserta` occurrences, but **none of the five deleted entry names** (`assertz_unify`, `asserta_order`, `assertz_atom`, `assertz_compound`, `static_dynamic_mix`) appears in it. That is consistent with the coverage having moved, and equally consistent with it having been lost — I did not resolve which, and the refusal now makes the gap loud rather than silent either way.

## CONSEQUENCE FOR THE ROW

`prolog-pz4-gamma-retain-activation-frames`'s DONE-WHEN can no longer be satisfied by a vacuous first term: `rung13` now returns **rc=2**, so the `&&` chain stops there until its witnesses are restored or the criterion is rewritten to a population that exists. **This makes the row harder to close, on purpose.** The DONE-WHEN-PROSE floor of "rung13 5/5" should be re-pinned to a measured denominator by whoever owns the restore decision.
