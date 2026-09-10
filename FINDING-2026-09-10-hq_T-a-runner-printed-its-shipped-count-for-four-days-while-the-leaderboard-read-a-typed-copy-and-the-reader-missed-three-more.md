# FINDING (hq_T, 2026-09-10) — a runner printed its shipped count on every run for four days while the leaderboard read a typed copy, and the reader that consumes those counts was missing three more

**Row:** `package-shipped-per-lane-printed-by-the-runner-not-transcribed` (rank 0, hq_T's owner cell; ceo CEO-301 order 2).
**Trees:** SCRIP `7d1b5347b` then `629160f3d`, corpus `021a16bf0`, `.github` at this commit. `RT_OPT=-O0`, incremental `make`. MODE NONET, order of work ICON.

## THE ROW'S PREMISE, RESTATED BECAUSE IT IS THE WHOLE FINDING

A number that travels by copy decays by copy; a number a runner PRINTS is re-derived every run and cannot. That is why `PACKAGE_SHIPPED` — three integers typed into `util_score_row.py` by a reader of somebody else's board — is a defect and not a convenience.

## PART ONE — PRINTING A NUMBER AND REPORTING IT ARE TWO JOBS

Twelve package runners are wired onto `lib_inventory.sh` and write a `SCORE.md` row. **Eleven capture their `PACKAGE_INVENTORY` line into a variable and splice it into the `--text` they hand `util_score_row.py`. `test_icon_jcon_suite.sh` was the twelfth**: it called `inventory_line` for its side effect alone, so the line went to stdout and nowhere else, and the cell it wrote said *"of 91 shipped, 76 graded, 15 ungraded"* in prose instead.

`inventory_clauses()` reads the **V CELL**, not the board. With no jcon clause in the cell the reader fell back to the typed dict. ⛔ **And this run proves the prose was stale:** the runner measures `shipped=91 graded=78 ungraded=3 ungradable=10`; the cell claimed 76 graded and 15 ungraded, and the fraction was `68/91` where the graded population is 78 and the pass count is 69.

⭐ **The reusable sentence:** a board line satisfies the *measuring*, not the *reporting*, and it scrolls off a terminal. The true numbers stood **one line above the transcription in the same script's own output** — nothing about a correct board line reveals that the cell beside it was typed.

Two further defects rode in the same `--text`, and both were **the pair already cured out of `test_icon_arizona_suite.sh`'s `--text` on 2026-09-06** — the same two defects, in the sibling runner, four days later. **That is what an uncopied cure looks like:** the denominator was `$SHIPPED` (a numerator measured over 78 graded programs published against a population including every program the suite never executed), and `$GAP` was labelled *"ungraded"* when jcon's 13 split 3 owed / 10 ruled — so the cell contradicted the clause now riding in it.

## PART TWO — THE JOIN WAS CURED AT ONE OF ITS THREE SITES

Found while verifying part one. `counted_fractions()` joins a table label in `PROGRESS_COUNTED` to a clause keyed by the runner's own `INV_PACKAGE` token, and **the two are different strings for three packages today: `pat`/`PAT`, `gnu_prolog`/`gnu`, `snoflake_suite`/`snoflake`.** A 2026-09-06 cure replaced the spelled join with one matched by the entry's own regex — **and applied it to the DENOMINATOR site only.** Two more sites kept `name in inv`: the shipped lookup and the missing-clause census.

Both consequences were measured on the live board:

1. **THE FALSE WORK ITEM.** For pascal the reader printed *"⚠ PAT carries NO PACKAGE_INVENTORY clause — their shipped population is still TRANSCRIBED … Retrofit the runner to `lib_inventory.sh` and paste its own line into the cell"* — about a clause standing in the very cell it had just parsed. A work item for work already done, issued by the only instrument that could have reported it, against a runner that had already done the thing it was being told to do.
2. ⛔ **THE QUIET ONE, AND THE WORSE ONE.** On a miss the shipped population fell through to `PACKAGE_SHIPPED`, which holds no pascal/prolog/snobol4 entry, so shipped read **0**, `shipped > graded` was false, and **the ungraded remainder was never booked as NOT-RUN.** Now booked: **PAT 2, gnu 51, snoflake 77.** Those programs were in no bucket at all — the never-graded business, hidden by a spelling, inside the function written to end it.

⭐⭐ **THE GENERAL FORM, and it is sharper than either bug:** **a cure that replaces a JOIN has to be applied wherever the join is performed, and `grep` finds those sites by the OLD spelling — the one string the author has just stopped thinking about.** Vigilance is not the fix. The fix is to compute the join **once**, name it, and leave no second way to spell it (`_matched`).

## THE INSTRUMENTS, BOTH RED-ONCE BEFORE THEIR CURE

- **ARM 17** of `test_gate_package_runners_print_the_inventory.sh` grades the **carriage** half over every censused package runner that writes a row, and counts as a **violation** rather than joining ARM 11's work list. It read **11 of 12 carrying** and named `test_icon_jcon_suite.sh`, then **12 of 12** after. It checks two properties: that the line is captured into a variable at all, and that the splice is guarded `${VAR:+…}` — an unconditional splice publishes an **empty clause** when `inventory_line` REFUSED, which the next reader cannot tell from a measured absence (the rc=2-as-zero collapse every other arm of this gate rejects). The variable name is lifted from the runner, never fixed by the gate.
- **ARM 18** grades the **reader**, where every other arm of that gate grades the writer — *carriage that nothing reads is not carriage.* Hermetic (a V cell built inside the arm, never the live board), four fixtures: the three real spellings plus `jcon` as an **exact-match control**. **MUTATION-PROVED:** ablating `_matched` back to the spelled join reds it **six times over** on exactly those three and leaves the control green. It REFUSES **rc=2** if a fixture's label is no longer a package of that language in `PROGRESS_COUNTED` — a stale fixture must not pass.

## WHAT MOVED ON THE BOARD

- jcon's V clause is now runner-written: `m3 69/78 · m4 69/78 graded · PACKAGE_INVENTORY package=jcon shipped=91 graded=78 ungraded=3 ungradable=10 graded_stream=78 graded_narrow=0`. **All three Icon packages now take their shipped population from a runner's own clause**, and the `PACKAGE_SHIPPED` dict is no longer reached for any of them.
- **NO ICON NUMBER MOVED IN PART TWO:** icon's three clause keys already matched their labels exactly, and its booked remainders read 34/13/762 before and after.
- Two **superseded** `JCON_SUITE_BOARD` clauses (`graded=81 … m3_pass=44 m4_pass=42`, 2026-09-06) still sat in **machine form** in both tables, competing in digits with the live reading. Spelled out per this file's own established remedy, with no `package=` shape and no numerals, so the note cannot recreate the conflict it describes. `test_gate_score_tables_agree.sh` reads **0 same-denominator conflicts** on this tree.

## GATES GREEN ON THIS TREE

`test_gate_package_runners_print_the_inventory.sh` (22 arms) · `test_gate_score_row_rewrites_in_place.sh` · `test_gate_score_inventory_clauses_never_vanish.sh` · `test_gate_score_md_parses_and_github_is_marker_free.sh` · `test_gate_score_row_denominator_includes_xfails.sh` · `test_gate_score_row_stamps_the_tree_it_graded.sh` · `test_gate_score_row_text_splices_are_assigned.sh` · `test_gate_seat_identity_one_map.sh` · `test_gate_score_tables_agree.sh`.

## STILL OPEN, NAMED NOT FIXED

Ten of fifteen packages carry no runner-written clause in their cell (`gimpel aisnobol dotnet testpgms` · `swi INRIA` · `roast`), so their shipped population is still transcribed or absent. Every one is a SNOBOL4/Prolog/Raku row and **PARKED-LON-HOLD** under the ICON-only order of work; the reader now names each of them correctly, which it did not for three of them before this landing.

## ONE MORE, CHEAP AND WORTH A LINE

A comment block inserted between a backslash-continued `python3 …` line and its `--measurer …` continuation **severs the invocation**: `argparse` printed a usage error and then the shell ran `--measurer` as a command (`--measurer: command not found`), after which the runner's own `|| echo` fallback said *"record this row by hand (the REFUSED line above says why)"* — pointing at a refusal that never happened. Caught in the same sitting by running the runner rather than reading it. ⭐ A `\` continuation is not a comment boundary, and the explanatory comment belongs **above** the command, never inside it.
