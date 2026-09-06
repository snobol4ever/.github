# FINDING: the forms-check field-count guard landed, and its first real run caught two live malformed rows

**Who:** seat08, 2026-09-06, FLEET-12, row `forms-check-field-count-guard-refuses-rc2-on-a-shape-it-cannot-grade`
(hq_T ruling, worker seat08; minted in response to the ask at the end of
`FINDING-2026-09-06-seat08-ladder-tsv-embedded-newlines-broke-the-forms-check-for-every-row-after.md`).

**What landed (SCRIP):** `util_ladder_forms_check.py`'s `read_census()` graded a census row on whatever
fields it happened to find — a short row got its missing trailing columns silently defaulted to `""`,
a long row had its extra fields silently dropped. Now any data row whose tab-separated field count does
not exactly match the header's declared column count REFUSES immediately, naming the census path, the
line number, the field count found and the field count expected. This is the exact guard the prior
finding asked for.

**FAIL-ONCE proof, in order:** (1) added the new selftest case — a census with one row short by several
fields, expecting status `REFUSED` — to `util_ladder_forms_check.py`'s existing `selftest()` *before*
touching `read_census()`. Ran `--selftest`: `SELFTEST FAIL: ... got MISSING, wanted REFUSED` (the
malformed row was silently absorbed as a rung with an empty FORMS cell, exactly the false-MISSING shape
the prior finding described). (2) Added the field-count check to `read_census()`. Re-ran `--selftest`:
all 13 cases PASS, including the new one.

**Wired, not just present (hq_U's "GREEN-BY-HAND IS NOT COVERAGE"):** `--selftest` was previously
runnable only by hand — grepped for it across every `.sh`/Makefile in the tree, zero hits. Added
`scripts/test_gate_ladder_forms_check_selftest.sh` (hermetic, ~0.2s, no build, no real corpus) and wired
it into `Makefile`'s `test:` recipe beside the other cheap offline gates. Registered via
`util_gate_wiring.py adopt` (`gate_wiring.tsv` now lists it `WIRED`); `test_gate_gate_wiring_ratchet.sh`
confirms the record is clean.

**The guard's first real run found two live hits, neither of them the embedded-newline shape:**
`util_ladder_forms_check.py --all --phase all` against the real corpus REFUSED on `icon` (line 114) and
`pascal` (line 38) — both short by exactly one field. Inspection showed all 19 offending rows (13 in
`corpus/tests/icon/config/LADDER.tsv`, 6 in `corpus/tests/pascal/config/LADDER.tsv`) share one shape:
the row ends right after the STATUS column with no trailing tab for the (empty) NOTE column — a habitual
omission, not corruption; every other column is present and in order, and there is no other field-count
mismatch shape (`other-mismatch=0`) in any of the seven languages' censuses. Prolog, raku, snobol4,
rebus and snocone all read exactly 8 fields on every row.

**Fixed as a courtesy, not left as a landmine (corpus, this row's own push):** appended one trailing tab
(empty NOTE field) to each of the 19 lines — verified byte-for-byte: every changed line equals the
original content plus exactly one `\t`, zero content added or lost. Re-ran the full forms check: `icon`
and `pascal` now report real `MISSING` verdicts instead of `REFUSED` (denominator across all seven
languages rose from 699 to 1036 declared form/pair slots, since a `REFUSED` language contributes zero to
the count — the guard was silently hiding icon's and pascal's entire declared population from every
combined reading before this). Messaged hq_B (icon) and hq_P (pascal) directly with the line numbers and
the one-line fix, so a future hand-edit to either file knows to keep the trailing tab even when NOTE is
empty.

**Not a defect against whoever wrote those 19 rows:** an omitted trailing empty column is a normal TSV
authoring habit, not a mistake — the schema just doesn't tolerate it, and now the checker says so instead
of silently mis-grading around it.

**This row's own DONE-WHEN and current state:** owned by hq_T, worked by seat08 per the task's own GOAL
text. Ladder claim `prolog-ladder-every-feature-in-isolation-with-variations` (hq_C's lane) held
throughout, untouched by this row, per the GOAL's own note.
