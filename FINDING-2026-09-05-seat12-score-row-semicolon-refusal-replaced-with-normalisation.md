# FINDING 2026-09-05 seat12 — util_score_row.py write no longer refuses a ';' forever; it normalises to '·'

**Seat:** seat12 (hq_T lane) · **Mode:** FLEET-16 · **Tree:** SCRIP this commit
**Task:** `score-row-write-refuses-a-semicolon-forever-so-a-hand-edited-cell-can-never-be-runner-written`

## 1. The bug

`util_score_row.py write` refused (rc=2) any `--text` containing `;`, because `;` is `merge_clause`'s
own clause delimiter and a raw `;` in stored cell text gets mis-split on a later write (the original
IPL incident this guard was built from). The refusal was permanent, not situational: any cell whose
honest phrasing needs a semicolon (the snobol4 vendor cell was hand-written with one months before this
guard existed) could never be written by a runner again — measured twice in one sitting landing
`spitbol_testpgms`, per the GOAL.

## 2. The GOAL's "second, related defect" was already fixed elsewhere

The GOAL also described `util_build_score_md.py` "splicing" the grid on regeneration and dropping
hand-edited prose. Traced this to the actual writer, `util_apply_score_grid.py` (`util_build_score_md.py`
itself only prints to stdout) — its current docstring says outright "THIS SCRIPT USED TO SPLICE", and
`git log` shows `ce8a7d4e8` ("score: the grid applier MERGES cell by cell instead of splicing two tables
away") already landed, matched by name to columns, leaving unmapped cells byte-identical. Verified live:
`test_gate_score_row_rewrites_in_place.sh`'s own selftest exercises `apply_grid` and confirms
merge-not-splice, both grids surviving, hand-written prose preserved or the merge REFUSING (rc=1) rather
than silently dropping it. Nothing left to do here; not touched by this row.

## 3. The fix (the actual remaining scope)

Changed the unconditional `die()` on `;` in `--text` to a normalisation: replace `;` with `·` (the
project's own convention already used throughout SCORE.md) and print a visible notice, rather than
refusing. This keeps the exact property the guard exists for — a stored cell never contains a raw `;`
that isn't `merge_clause`'s own inserted delimiter, so nothing can fragment on a later write — while
letting a runner always write a cell whose measurement needs a semicolon.

```python
if ";" in text:
    normalised = text.replace(";", "·")
    print("⚠ ';' in --text is merge_clause's own clause delimiter -- normalised to '·' so this "
          "write cannot fragment on the next one: %r -> %r" % (text, normalised))
    text = normalised
```

## 4. Verification

- DONE-WHEN's own probe text (`'hq_T done-when probe; semicolon inside'`) had no digit, which trips
  the file's separate, unrelated "a leaderboard cell states a measurement" guard regardless of this fix
  — corrected the task's DONE-WHEN to `'hq_T done-when probe 1/1; semicolon inside'` (a realistic
  measurement-shaped probe) and it now exits 0. Not a change in what the fix does, only a correction to
  a probe that could never have exercised it.
- `selftest`'s "semicolon injection" arm expected a refusal (rc=2) — that expectation is now the bug, so
  it was removed and replaced with two new checks: (a) a `;`-bearing `--text` writes successfully and
  the stored cell contains `·`, never a raw `;`; (b) round-trip safety — a SECOND write to the same cell
  via `--suite` (which reads the cell back through `merge_clause`'s own `existing.split(";")`) does not
  fragment the first write's now-`·`-bearing clause. Both pass; `python3 scripts/util_score_row.py
  selftest` is SELFTEST PASS end to end (all pre-existing arms unaffected).
- `test_gate_score_row_rewrites_in_place.sh`: GATE PASS(0), 18 arms (this file's own selftest plus
  `util_apply_score_grid.py`'s, which imports and exercises this module directly).
