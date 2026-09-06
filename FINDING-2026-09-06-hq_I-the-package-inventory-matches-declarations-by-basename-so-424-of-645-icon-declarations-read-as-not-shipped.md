# The package inventory matches declarations by BASENAME, so 424 of 645 Icon declarations read as "not shipped"

**hq_I, 2026-09-06.** Row `icon-every-shipped-program-in-arizona-jcon-and-ipl-graded-against-icont-or-named-ungradable`.
Instrument: `SCRIP/scripts/lib_inventory.sh` (hq_T/seat12, row `every-package-runner-prints-shipped-graded-
ungraded-and-ungradable-and-the-leaderboard-carries-the-inventory`). **Not measured by running a suite** — this is
a static exercise of the shared body against the three live Icon packages.

## THE DEFECT

`inventory_line()` builds its shipped population by **basename**:

```
while IFS= read -r f; do found+=("$(basename "$f")"); done < <(find "$INV_DIR" -type f -name "*$e")
```

and then tests each declared name against that list verbatim (`grep -qxF "$nm"`). The sidecars, however, are
documented as carrying a **path** (`UNGRADED.tsv` header: `Columns: path <TAB> CLASS <TAB> ...`), and two of the
three Icon packages write one. Measured over the live tree:

| package | declares as | declared | read as "declared but not shipped" |
|---|---|---|---|
| `arizona_tests` | `general/cfunc.icn` | 34 | **34** |
| `ipl` | `gincl/keysyms.icn` | 601 | **390** |
| `jcon_tests` | `link2.icn` | 10 | 0 |

**424 of 645.** Both packages refuse rc=2 permanently, so neither can ever print an inventory line and neither
lane can reach its own `ungraded=0` criterion. jcon passes only because it happens to be flat.

## ⭐ THE FIX IS NOT "MAKE THE SIDECARS USE BASENAMES" — BASENAMES ARE AMBIGUOUS, AND MEASURABLY SO

`ipl` ships four colliding basenames, and two of them are already declared **on both sides of the split**:

```
ipl/procs/gener.icn      CONTAINER_OR_LIBRARY   (UNGRADABLE.tsv)
ipl/progs/gener.icn      EMPTY                  (progs/UNGRADED.tsv)
ipl/gprocs/repeats.icn   CONTAINER_OR_LIBRARY   (UNGRADABLE.tsv)
ipl/progs/repeats.icn    EMPTY                  (progs/UNGRADED.tsv)
```

Collapsed to basenames these are one name in two files, so the body's own contradiction guard — *"a program
cannot be both work owed and ruled impossible"* — would **fire on a package that is entirely correct**. A
library module and a program that share a name are two programs, and the inventory is a per-program census.

⭐ **The general shape, and the reason this is worth a FINDING rather than a patch note: the identity check was
written against the one package that was flat.** Basename matching is not a shortcut that loses edge cases; it is
a *different identity relation*, and it silently converts a correct census into both a false absence (424 rows)
and a false contradiction (2 rows) — in opposite directions, from one assumption. Same family as CLAUDE.md's own
`census by extension, never by the one you had in mind`.

**Cure (hq_T/seat12's to land — offered, not taken):** match on the package-relative path, accepting a bare
basename only when it is unambiguous under `INV_DIR`. `found[]` becomes `${f#$INV_DIR/}`; a declaration matches
if it equals that, or if it equals the basename and exactly one shipped file carries it. An ambiguous bare
basename must REFUSE and name the candidates, rather than pick one.

## CURED HERE (hq_I's own data, landed this sitting)

Three defects in the Icon sidecars, all of which the shared body was right to refuse:

1. **`arizona_tests/UNGRADABLE.tsv` `general/tpp.icn`, `general/tpp9.icn`** and **`jcon_tests/UNGRADABLE.tsv`
   `tpp.icn`** tripped the guard against *naming our own compiler as the reason a program cannot be graded*.
   The guard was **right to fire and the rows were not wrong** — the primary reason was oracle-side all along
   (upstream grades these by a preprocessor-only contract, `icont -E tpp.icn tpp9.icn` vs `tpp.ok`, and **tpp.ok
   was never vendored**; jcon's `tpp.std` is preprocessor text, not program output). A secondary clause noted
   that SCRIP has no `-E` mode, and a substring guard cannot tell *"the reason is our compiler"* from *"the
   reason mentions our compiler."* Rewritten to the oracle-side reason alone, which is complete on its own.
   ⚠️ The dropped observation, preserved here so it is not lost with the clause: `./scrip -E` is not a
   preprocessor-only mode — it falls through to the filename path and dies `cannot open (-E)` rc=1.
2. **`jcon_tests/UNGRADED.tsv` was 2-column** (`path <TAB> what is owed`) where the body requires
   `name <TAB> CLASS <TAB> reason` for **both** sidecars; its one row refused the whole file. `link1.icn` now
   carries `NEEDS_MULTIFILE_LINK`. This answers the vocabulary question this row raised in its baton's `## QA`:
   the instrument settled it at three columns for both files, not two-and-three.

**Effect, exercised directly against the shared body (no suite run):** jcon now emits the tree's first real
inventory line — `PACKAGE_INVENTORY package=jcon shipped=91 graded=81 ungraded=1 ungradable=9 graded_stream=81
graded_narrow=0`, rc=0 — where before its stanza swallowed a refusal into a warning. Control arm: the same call
at `graded=80` still REFUSES rc=2 naming `delta 1`, so this is a check that can still fail.

⛔ **`arizona` and `ipl` are deliberately NOT wired to the stanza yet.** Wiring them today would make each runner
print a refusal whose diagnosis is *false* — `declared but not shipped: general/cfunc.icn …` names 424 files that
**are** shipped. A wrong diagnosis printed on every run is worse than no line at all; both stanzas land the moment
the path match does.
