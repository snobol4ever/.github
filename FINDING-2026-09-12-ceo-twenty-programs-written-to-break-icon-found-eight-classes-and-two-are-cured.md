# FINDING 2026-09-12 18:13 CDT (ceo) — twenty programs written to break Icon found eight classes, two cured the same sitting

**Tree:** corpus `17ea9417d` (the adversarial family, master 959 → 979) · SCRIP `969a4bc89` (hex) and `3de7f285d` (NUL subscript) · seat ceo · cursors CEO-640/641.
**Lon, 2026-09-12 (in-chat):** *"Will you be able to enhance the test suite with programs that will break Icon? Try to break it."*

## Method

Twenty programs, one per corner (nested scanning, generators in odd positions, co-expressions, reversible assignment, records and tables,
string builtins, numerics and large integers, control flow, procedures, lists and sections, `&error` handling, keywords, scanning
functions with positions, conversions, string indexing, csets, recursion, generator lvalues, suspending scans, miscellany), each run
under icont and under SCRIP in both modes with SCRIP's stream rendered through the error-voice list. Where the oracle refused or looped
the program was mine and was corrected (icont's own evaluation stack overflows near depth 500; a suspending scan resumes at the same
position under both engines; `<` is numeric). Fatal errors were kept out of the refs by probing under `&error := -1` and printing the
error number: a traceback names the file, and the master renames every entry. The container was written through the harness's own
`write_suite`, absorbed with `--absorb-only adversarial` in a scratch tree, round-tripped twenty for twenty, then landed.

## Classes found (icont vs SCRIP, both modes)

| # | class | state |
|---|---|---|
| 1 | `integer("0x10")` converted to 16 (strtod parses C hex floats) | CURED `969a4bc89`, gate wired |
| 2 | `string(&cset)[255]` and `[256]` failed: subscript measured the string with strlen past the leading NUL | CURED `3de7f285d`, gate wired, row DONE |
| 3 | a keyword variable (`&pos`, `&subject`) passed as an argument is dereferenced when evaluated, not at the call | row, ceo; staging measured a dead end |
| 4 | `find("a", "banana", -3)` fails; the sibling functions take negative positions | row, ceo |
| 5 | `&null.f` raises 114 where icont raises 107 | row, ceo |
| 6 | `image(&current)` counts one activation more than icont | row, ceo |
| 7 | `args(p)` of a variadic procedure answers 1 for icont's −1 | CURED `83ace92b0`, gate wired, row DONE |
| 8 | `bal()` yields one result, not a sequence | the existing row |

Five master entries land as visible reds (a01, a03, a09, a11, a13); IcnM reads 974/979 on the coo's next pass until the rows close.

## Named, not cured

The keyword-variable class needs a reference kind the staging path can carry that reads the live scan environment, not the runtime
keyword cell — the dead end is recorded in the row. The image-leak row keeps its list arm red on the GC-5 blocker (CEO-639).
