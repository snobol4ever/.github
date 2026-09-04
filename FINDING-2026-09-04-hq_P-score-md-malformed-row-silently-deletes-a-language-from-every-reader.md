# A malformed SCORE.md row deletes that language from EVERY reader at once — and the refusal points away from it

**hq_P, 2026-09-04. MODE `FLEET-16`. Reported by seat07 (`score-md-snobol4-row-missing`), root-caused and cured here.**
Cure: SCRIP `scripts/util_score_row.py` + `scripts/util_apply_score_grid.py`; data repair `.github/SCORE.md:72`.

## What seat07 saw

`util_score_row.py write --lang snobol4` REFUSED(2) with:

> `no row for language 'snobol4' in the grid. Rows present: icon, pascal, polyglot, prolog, raku, rebus, snocone`

seat07 read that exactly as written and concluded snobol4 was missing from "whatever internal registry
util_score_row.py's row-write path uses" — then correctly declined to guess at a script they do not own, and
escalated. **The message was well-formed, confident, and pointed away from the defect one line above it.**

## What was actually true

There is no registry. `find_table` builds its row map from SCORE.md itself, and its row loop read:

```python
if len(c) == PROV_COL + 1:
    rows[c[0]] = (i, c)
```

**No `else`.** A row whose column count is not the table's was dropped on the floor in silence. `.github`
`dc87ee1c` ("SCORE.md: re-attribute snobol4/raku rows to this session's re-run") appended a cross-confirmation
note to the snobol4 row as a **seventh cell**. One stray `|`, and snobol4 — the project's largest language —
vanished from every reader of that table simultaneously:

| reader | consequence | loud? |
|---|---|---|
| `write` | REFUSED(2) for the whole fleet: no seat could land ANY snobol4 cell | loud, **but misdiagnosing** |
| `check` (→ `handoff_status.sh` row staleness) | reported staleness for every language **except** snobol4 | **silent** |
| `agree` (`test_gate_score_tables_agree.sh`) | printed `GATE PASS(0) … 11 mirrored cell pair(s)` while blind to snobol4 | **silent** |

The third is the worst: a gate that **passes because it never looked**. That is the vacuous-test class Lon
flagged — an instrument that cannot fail prints the same string as one that passed.

⭐ **NOT affected, checked and dismissed rather than assumed:** `cmd_progress` passes `provs.get(lang, "")`
into `language_progress`, whose signature accepts `prov` and **never uses it** (staleness has since been
re-keyed onto the September-10 grid's V-cell stamp). `sno 26%` was correct. Claiming it as a fourth
consequence would have been a plausible, checkable, wrong sentence.

## The shape worth keeping

⛔⭐ **AN INSTRUMENT THAT ANSWERS A NARROWER QUESTION THAN THE ONE IT IS THOUGHT TO ANSWER.** `if a.lang not in
rows` asks *is it in my dict?*; it was read as *does it have a row?*. Identical shape to `command -v` for an
oracle (answers IS IT ON PATH, read as DOES IT EXIST) — already written up in CLAUDE.md, and it recurred here
in a different file with different data. `table_shape_error` **already proves the header's shape and says what
is wrong with it**; the rows directly below it were owed the same courtesy and did not get it.

⭐ **SKIPPED and ABSENT are not the same fact, and collapsing them is the whole bug.** The cure is not the
missing `else` — it is that the reader must be able to say *which*.

⭐ **I HIT THE SAME CLASS WHILE CURING IT, WHICH IS THE BEST EVIDENCE IT IS REAL.** I cleared external callers
with `grep 'import util_score_row'` and got nothing — but `util_apply_score_grid.py` loads it via
`importlib.util.spec_from_file_location`, so my grep answered *is it imported by NAME?* and was read as *is it
imported?*. Four call sites, missed. Caught only because `test_gate_score_row_rewrites_in_place.sh` went red
and a **control arm on the stashed tree proved the red was mine, not pre-existing.**

## The cure

1. **`find_table` returns `(hdr, rows, skipped)`** and writes a `⚠` line to **stderr** naming any skipped row
   (line, language, its count vs the table's). The silent readers become loud by construction; stderr keeps
   stdout-parsing callers unaffected.
2. **`write`** refuses with the real diagnosis — *row X EXISTS at line N but carries 7 columns where this table
   has 6, so it was SKIPPED — MALFORMED, NOT ABSENT* — and names the two readers that drop it silently.
3. **`agree`** treats a grid language whose display row is unreadable as **a measurement it did not make**:
   GATE RED, never `PASS` over a table it could only partly read. A gate that cannot measure refuses.
4. **`util_apply_score_grid.py`** refuses to splice at all while any row is malformed — it splices **by
   position**, so a skipped row is invisible there and the merge would silently stop carrying that language.
5. **Data repair (`SCORE.md:72`)**: the stray 7th cell folded into the provenance cell as its own clause,
   keyed `cross-confirm:`. ⛔ Deliberately **not** keyed `board …` — `merge_clause` matches
   `^key\s*(?::|(?=\s|$))`, so a clause opening with a bare `board ` would be clobbered by the next `board`
   write: the Arizona/ArizonaExtended trap in reverse. Proven content-preserving: the row normalises
   character-identical modulo delimiters.

## Verification (all by execution, this tree)

- **Negative test first:** `write --lang snobol4` → `rc=2` with the new message, *before* the data repair.
- **Post-repair:** seat07's exact command → `snobol4/board rewritten in place (line 72)`, `rc=0`, grid updated.
- **Recovered coverage, the number that shows the hole was real:** `agree` **11 → 13** mirrored cell pairs;
  `check` **0 → 6** snobol4 staleness lines. Those pairs were never being compared.
- **Guards re-proven on a deliberately broken row** (a scratch copy): `write` rc=2 · `agree` rc=1 ·
  `apply_score_grid` rc=2 — with a **control arm** showing a well-formed row in that same broken file still
  reaches the normal write path. One bad row no longer disables the others.
- **Gates:** `score_column_semantics` · `score_row_rewrites_in_place` · `score_cell_no_silent_prose_loss` ·
  `score_tables_agree` · `scorecard_suite_aware` all rc=0; both selftests rc=0; `strip_comments --check`,
  `no_o2_arm_in_scripts`, `term_wordref_ratchet` rc=0.
- ⚠ **Scope of the verdict, stated rather than implied:** this is python tooling under `scripts/` plus one
  SCORE.md line — no compiler code, no codegen, no `.s` artifacts. The full `make test` corpus board was **not**
  run and nothing here would move it.

## Owed

⚠ `agree` now reports **14** one-sided populations, up from 8 — the six new ones are snobol4's, and they are
real dual-write debt that was simply invisible while the row was unreadable. Not cured here: that is the
known `write`-updates-the-display-only gap, and it belongs to whoever holds the dual-write row.
