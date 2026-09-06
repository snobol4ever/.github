# FINDING: `util_unabsorbed_census.py`'s bare-name exclusion check is tree-blind — a `tests/<lang>/X.ext` and `benchmarks/<lang>/X.ext` sharing a stem silently mask each other

**Who/when:** seat02, 2026-09-06, FLEET-12, row `pascal-every-non-package-source-that-runs-with-output-absorbed-into-the-master-with-oracle-refs`.

## What was found

Absorbing `corpus/tests/pascal/sieve.pas` into the master (deleting the loose pair, per normal
`util_build_master_suite.py --delete-absorbed` behavior) writes a bare `sieve` reason line into
`corpus/tests/pascal/ALL.excluded.txt`. `util_unabsorbed_census.py`'s `accounted` check
(`base in excluded[lang]`, unqualified by tree) then treated **`benchmarks/pascal/sieve.pas`** —
an unrelated file, same basename, never itself absorbed or excluded — as accounted too. `pascal`'s
owed count silently dropped from 11 to 10, undercounting by exactly the file the collision hid.

Same class of bug already found and partially fixed once before, for the **additive** exclusion
path (`additive_excluded`, keyed `(name, category)` pairs specifically to stop
`demos/snobol4/calculator/calculator-1.sno` cross-crediting `benchmarks/snobol4/demo/calculator-1.sno`
— see this file's own header comment). The **plain** `excluded[lang]` set used by the ordinary
(non-additive) loose-pair path was never given the same tree-qualified treatment.

## Scope, measured

A `tests/<lang>/` vs `benchmarks/<lang>/` same-stem sweep across all seven languages found one live
collision on disk at measurement time (`icon: queens`) — but the bug is latent, not limited to
files that happen to collide *right now*: `pascal: sieve` only became a live collision once this
session's own absorption deleted `tests/pascal/sieve.pas`, which is exactly what makes it dangerous
(a census can go from correct to silently wrong as a *side effect of unrelated absorption work*,
with no signal at the point it happens).

**Before fix** (`util_unabsorbed_census.py`, no `--lang`): `OWED=327` (icon 72, pascal 10, prolog 4,
raku 129, snobol4 34, snocone 78 — rebus printed 0, omitted from the per-language summary).
**After fix:** `OWED=333` (+6): icon 72→74, pascal 10→11, **rebus 0→3** (previously fully masked —
every rebus owed item was hidden behind a cross-tree collision), prolog/raku/snobol4/snocone
unchanged (confirms the fix is scoped: only genuine collisions moved, nothing else shifted).

## Fix

`scripts/util_unabsorbed_census.py`, the `accounted` branch: `path in excluded[lang]` (a
corpus-relative path is unique by construction, kept unscoped) stays available for every tree;
the bare `base`/`f`/`fam` checks — which key off `ALL.excluded.txt`'s bare-name column, a file
`util_build_master_suite.py`'s loose-pair path only ever writes meaning "this name under
`tests/<lang>/`" — are now gated `top == 'tests'`. Verified: full before/after census diff above;
`benchmarks/pascal/sieve.pas` reappears as owed; nothing outside the three affected languages moved.

## Disposition

Fixed inline (same file already carrying the sibling fix for the identical bug class; low risk,
directly blocking this row's own DONE-WHEN measurement, verified across all languages before and
after). Not investigated further: **why rebus's entire owed set was masked** — worth a follow-up
census read for whoever next works a rebus absorption row, now that the number is real.
