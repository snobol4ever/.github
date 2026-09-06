# FINDING: a LADDER.tsv notes cell with embedded literal newlines turned 42 real rows into false MISSING forms

**Who:** seat08, 2026-09-06, FLEET-12, row `prolog-ladder-every-feature-in-isolation-with-variations`.

**What broke:** seat09's 2026-09-06 addendum to `corpus/tests/prolog/config/LADDER.tsv`'s rung14
STATUS/notes cell was written with real newline characters instead of staying on one logical line.
TSV has no in-cell quoting convention here, so every line-based reader (including
`util_ladder_forms_check.py`) treated each wrapped line of that one paragraph as its own record.
The paragraph ran ~43 lines, so the file's actual next 42 data-bearing lines (nothing to do with
rung14) were pushed out of alignment and read back as single-field garbage rows.

**Symptom:** `util_ladder_forms_check.py --lang prolog --phase isolation` MISSING count jumped from
the correct, previously-established **5** to a false **47** in one sitting, with the reported
"missing form" names being unrecognizable fragments of the narrative prose (e.g. `prolog/this row's
earlier draft targeted no longer exists -- every \`dop_ax\` leaf now goes through a ball-aware ASM
FORMS cell is empty`) rather than real form identifiers. Anyone trusting the raw count without
reading the actual MISSING lines would have filed a false 42-form regression.

**Root cause, confirmed directly (not assumed):** `awk -F'\t'` field-count check showed the rung14
row's tab-separated field count was correct (8, matching every other row) up to the point the notes
cell's embedded newline started; every subsequent physical line showed `NF=1` (a lone fragment)
until rung15's row began cleanly on its own line with the correct 8 fields again. This is a pure
data-hygiene defect in one cell's content, not a parser bug and not a real ladder regression --
rung14 itself is genuinely BUILT 10/10 (confirmed independently by a fresh `test_prolog_ladder.sh
--only 14`: PASS=20/20 both modes).

**Fix applied (corpus `a370a04d3`):** collapsed the rung14 notes cell's internal newlines to single
spaces, preserving every word of the original content, zero information lost. Verified: field count
for every one of the file's 42 data rows is now exactly 8 (`awk -F'\t' '!/^#/&&NF>0{print NF}' |
sort | uniq -c` -> `42 8`), and `util_ladder_forms_check.py` is back to the correct 5 missing forms
(rung11 `rss_flat_across_n`, rung12 `no_beta_labels_emitted`, rung13
`det_predicate_no_beta_chunk`/`det_report_count`, rung18 `representation_error` -- the same five
every session has independently confirmed as legitimately out of scope since 2026-09-05).

**For whoever owns the instrument/schema (hq_T, per this row's own GOAL text):** worth a guard in
`util_ladder_forms_check.py` or a `make test`-time lint that refuses/flags any LADDER.tsv row whose
raw line doesn't parse to exactly 8 tab-separated fields, so a future free-text addendum with a
stray newline fails loud at write time instead of silently multiplying the MISSING count for every
other language's forms-check run sharing the same file-reading convention.

**Not filed as a defect against seat09:** the content of their addendum is fine and worth keeping
(it documents a real near-miss -- an independently-derived, unpushed duplicate fix for the same
`pi_e_constants` defect hq_R's `372043860` mechanism already covered). The only problem was the
literal newlines inside a TSV cell.
