# FINDING — 2026-09-05 (hq_T, QUARTET; umbrella row `test-suite-consistency-seven-languages-one-standard`, and the census hq_B asked for)
# A CHECK THAT CANNOT SEE ITS SUBJECT SAYS NOTHING, AND NOTHING READS AS A PASS — MEASURED IN TWO INDEPENDENT TOOLS ON ONE DAY

**Tree at measurement:** SCRIP `4c70284dd` + this change, built with **incremental `make`** (the loosened-pristine FACT RULE, `RULES.md:118`; no stale-binary refusal fired), `RT_OPT` `-O0` read from `Makefile:43`. corpus `d58a796fa`. .github `064df505`. Box clock 2026-09-05. Measurer `hq_T`.

Two cures landed, and they are the same defect in two tools that share no code: **a guard's evidence was out of reach, so it said nothing, and its silence was indistinguishable from a pass.** Both were found by reproducing somebody else's incident rather than by reading the source.

## 1. hq_B's INCIDENT, REPRODUCED — AND THE CURE OF ONE READER HAD NEVER REACHED ITS TWIN

hq_B pasted a minimized Icon witness into a `SCORE.md` cell. **Icon's concatenation operator is two pipes and this is a markdown table**, so the row widened and every tool that splits on `|` stopped seeing that language's row. `test_gate_score_tables_agree.sh` went **from RED to `GATE PASS(0)` in the same edit**. Nothing was fixed: `agree` compares mirrored cell *pairs*, an unparseable row yields no pairs, and a population that cannot be READ scores exactly like a population with no conflicts.

**Reproduced on a scratch copy of the live board** (never the real one), widening the icon grid row from 7 cells to 9 with `write("a"||"b")`:

| | verdict | what it said |
|---|---|---|
| clean copy (control) | **RED rc=1** | `icon: display vendor says 40/81, grid V says 38/81` — the real, pre-existing conflict |
| one widened grid row | **PASS rc=0** | `GATE PASS(0): 10 mirrored cell pair(s), 0 same-denominator conflicts` |
| every grid row widened | **PASS rc=0** | `GATE PASS(0): 0 mirrored cell pair(s), 0 same-denominator conflicts` |
| …and the column gate | **PASS rc=0** | `GATE PASS(0): 0 runner citation(s) all match their column's kind` |

⛔ **The last two lines are the whole argument: both gates printed the number ZERO in their own success sentence and exited 0.**

⭐ **THE CAUSE IS A CURE THAT STOPPED AT THE FUNCTION IT WAS REPORTED ON.** `find_table`'s row loop was given its missing `else` on 2026-09-04 (`cc054250f`, *"a malformed row is SKIPPED, never ABSENT — say which"*) after one stray `|` deleted snobol4 from every reader of the DISPLAY table. **`find_grid` — same file, same shape, same consequence — was left exactly as it was**, so a malformed row in the September-10 grid still vanished in silence. The report named one function; the defect was in the file.

⭐ **AND THE REFUSAL THAT SAVED hq_B WAS IN A THIRD TOOL** (`util_score_row.py progress`: *"the September-10 grid has no row for icon — refusing to publish a progress line over a partial grid"*). That message is also the one that cost seat07 an hour on 2026-09-04, because **"no row for X" is well-formed, confident, and points away from a row that is present and unreadable.** It now says **MALFORMED, NOT ABSENT**, with the line number and both column counts.

**Landed** (SCRIP `4c70284dd`): `find_grid` returns `skipped` and warns per row · `agree` REDs on a malformed row in **either** table · `agree` **REFUSES rc=2 when it compared zero pairs** · `columns` REDs on a malformed row, REFUSES on an empty grid, and prints its denominator · `progress` distinguishes malformed from absent · `write` says when the grid twin of the cell it just wrote is unreadable. Three arms added to `test_gate_score_row_rewrites_in_place.sh` (blocking, in `make test`): the incident replayed, the zero-population floor for both subcommands, and a re-assertion that the real board was untouched. **Each proven to fail on the pre-cure code first**; gate now 18 arms, PASS(0).

⛔ **THE POPULATION FLOOR IS NOT A COROLLARY OF THE MALFORMED-ROW CHECKS AND IS DELIBERATELY SEPARATE.** Two perfectly well-formed tables can share no comparable cell. The floor is the independent bar: a gate that graded zero REFUSES rc=2 and never prints the success shape.

## 2. THE CROSS-LANGUAGE CENSUS — THE `modes` DECLARATION DID NOT TRAVEL WITH THE SUITE

This is the census named-but-not-done in §5 of yesterday's optbypass FINDING and endorsed by hq_B: *is the ast-graded-by-execution class live in other tooling?*

**The class:** every master declares per entry how it is graded. An `ast` entry's `.ref` is a `--dump-ast` dump; execute it and you manufacture a red that means nothing. Witnesses to date: **28** (the optbypass census tool), **42** (raku), **175 of 273** (snocone), **5 of 11** (pascal) — four seats, four lanes, one shared harness.

**Measured, all seven masters** (`ALL.csv`'s own `modes` column, corpus `d58a796fa`): every one carries a mixed column, so the class is reachable in all seven — icon 153 ast / 600 run · raku 97 / 820 · snocone 67 / 234 · rebus 96 / 43 · snobol4 28 / 67 · pascal 5 / 184 · prolog 0 / 374.

**The harness already refuses** a `--modes m3,m4` run over a suite declaring ast entries (landed 2026-09-04 after the three independent witnesses). ⛔ **But its evidence was a *sibling* `ALL.csv`, so the guard's activation depended on WHERE THE CALLER PUT THE SUITE.**

**MEASURED BOTH WAYS ON ONE PAIR OF COMMANDS** — pascal's 5 `modes=ast` parser entries:

| how the same five entries were graded | result |
|---|---|
| in place, `--modes m3,m4`, no flag | **rc=2 REFUSING** — evidence beside the suite |
| extracted to a tempdir, identical command | **rc=1, `total=5 m3_fail=5 m4_fail=5`** — a full, plausible board |
| extracted, `--by-modes-column` (post-cure) | **`ast_pass=5 ast_fail=0`** |

⛔ **All five "failures" are passes.** The false board was not merely unreliable; it was wrong in every cell it printed, and it looked exactly like a board.

⛔ **THE OTHER HALF IS WHY THIS IS A DEFECT AND NOT A MISSING FEATURE: `--by-modes-column` REFUSED on an extracted pair for want of that same csv.** On an extraction **the correct call was impossible and the incorrect call was silent** — not a choice a caller can be blamed for making.

**Call-site census** (`scripts/`, measured not typed): **63** grading call sites · **6** pass `--by-modes-column` (`board_icon_master.sh`, `test_corpus_snobol4.sh`, `test_raku_ir_full_suite.sh`, `test_gate_pascal_m3/m4.sh`) · **8** grade an EXTRACTED copy, **all 8 without the flag** — the blind set.

**The cure:** `extract-family` writes a `.modes` sidecar beside the pair, exactly as it already writes `.in` and `.xfail`, under the law stated in its own docstring — **a check that does not carry every field the grader reads is not a check** (hq_C). `modes` was the one field it did not carry. Both readers now go through one resolver (`modes_declarations`: sidecar first, sibling csv second, `({}, None)` when neither is reachable — an honest "no declaration", never a guess).

**Gated:** `scripts/test_gate_modes_declaration_travels.sh`, **wired into `make test`, blocking** — 15 arms across all 7 languages in ~8s. It picks each language's smallest all-ast family **by measurement, never by a pinned name**; asserts the sidecar matches the master's own csv; asserts the execution run REFUSES rc=2 **and names the ast declaration as its reason**; asserts `--by-modes-column` now works on an extraction; and **ARM D proves the scope** — a family declaring no ast entry must still grade normally, because a gate broader than its rule gets switched off by the first person it blocks for a good reason. **Fail-once proven in all seven languages: 8 violations on the pre-cure harness, 0 after.**

⭐ **THE GATE CAUGHT ME IN THE STANDARD'S OWN SHAPE #1 ON ITS FIRST RUN.** `--lang snobol4` is not an accepted choice (the default is the empty string), so **argparse exited 2 with its own usage text** and my arm read that as the tool refusing correctly. It only failed because the arm asserts the refusal **names its reason** rather than merely returning 2. Had I checked `rc=2` alone, the arm would have passed for entirely the wrong reason, in the one gate written to prevent exactly that. `snobol4` is now an accepted spelling of the default, normalised to `""` immediately after parsing (six downstream sites depend on `if args.lang:`).

## 3. ⛔ "NOBODY DECLARED IT" HAS THREE SPELLINGS AND ONLY ONE IS LOUD

Measured across the seven masters while censusing them: **`UNKNOWN`** — the builder's declared-never-derived default, counted and printed separately on every board (**snobol4 1764 of 1859 entries · prolog 237 of 611 · icon 1 of 754**); **the empty string** — silent, folded into the run population with no trace, and what **every** `corpus/packages/*/ALL.csv` carries today (aisnobol 2, csnobol4 62, gimpel 118); **an absent row** — which `--by-modes-column` refuses on. A law that says *declared, never derived* is only as strong as its weakest spelling of "undeclared", and the silent one is the one in the vendor suites.

## 4. WHAT THIS DOES NOT CLAIM, AND THREE OBSERVATIONS FOR OTHER LANES

- **No board number changed.** No suite was re-graded and no SCORE cell's value moved; what changed is which runs are *allowed to print a board at all*. The pre-existing icon `40/81` vs `38/81` conflict is **untouched and still RED** — it is not this change's subject and I did not re-measure JCON.
- **The 8 extracted-copy call sites are now covered, not audited.** I proved the property holds via the harness; I did not read each of the 63 call sites for other defects.
- **`test_snocone_corpus_suite.sh` grades family `corpus` = 10 entries** of snocone's 301-entry master (measured while building ARM D's control). Its declaration carries no ast entry, so nothing was false — but a board named for a master that grades 10 of 301 is a denominator question for the snocone lane, not a defect this row cures.
- **`test_gate_probe_suite_grading_path.sh` is RED on origin, before and after this change** (`zero suite families under corpus/tests/snobol4/probe`) — verified by re-running it on the pre-cure tree. Its subject moved out from under it; that is the optbypass shape again and belongs to whoever owns that probe tree.
- **`test_gate_master_family_selector.sh` printed `examined 0` beside a dozen ✓ checks** — `GATE_EXAMINED` was never set. Fixed in passing (13 assertions); a zero denominator beside a real population must not print like a zero denominator beside an empty one.
