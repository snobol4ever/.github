# ⛔⭐⭐⭐ GOAL-TEST-SUITE-CONSISTENCY — ONE TEST STANDARD FOR ALL SEVEN LANGUAGES

**Opened 2026-09-03 ~16:25 CDT box clock by the ceo on Lon's order, in-chat to ceo, verbatim:** *"Make the testing of all 7 languages consistent with each other. If one has many rungs with tiny increments then create that for the other lanugages. If one has a nice regressions suite, then we want regression for all languages. Let's get our test suite up to snuff and improved greatly."* Owner: **hq_T (HQ-TEST, opened 2026-09-03 16:30 on Lon's word)** for the program — `GOAL-HQ-TEST.md`; each language's rows to that language's seat (07, 10, 11, 12, 14 → hq_T as ask target). Law: RULES.md § THE INSTRUMENT LAWS (fail once, pass once; names beside counts; the leaderboard FACT RULE); the one-flat-suite ruling (tests live in `corpus/tests/<lang>/ALL.*`); the ONE-IDENTITY law.

## LIVE CURSOR

**2026-09-03 16:25 (ceo):** inventory measured (below), the standard written, the umbrella row `test-suite-consistency-seven-languages-one-standard` (hq_B, rank 0) and one gap row per language minted and assigned by lane. Nothing built yet. Whoever resumes: the per-language rows in the queue are the work; this file's table is rewritten by the seat that closes each gap (tree-labelled), and `SCORE.md` gets the new instruments' rows the day they print.

**2026-09-03 ~16:35 (seat11):** Raku's "ladder / rungs" cell closed — see INVENTORY row below. `test_raku_ladder.sh` built (mirrors `test_prolog_ladder.sh` exactly: `--to N`/`--only N`/`--list`, both modes m3+m4, REFUSE rc=2 when it can't measure). 10 witnesses, `ladder__rung00_hello` through `ladder__rung09_string_methods` (one construct-topic per rung: hello, variables, arithmetic, strings, arrays, hashes, if/while, subs, for-loops, string methods), refs oracle-cut from real Rakudo (`rakudo-local`, `rakudo_bin()`) — not hand-authored. `--to 9` (the whole ladder built so far) is PASS 20/20, not just the `--to 5` DONE-WHEN floor. Row raku-construct-ladder-from-rung-0 stays OPEN for whoever climbs past rung 9 (subs+signatures beyond a bare 2-arg sub, classes/roles, regexes/grammars, exceptions, lazy lists are the named-but-unbuilt topics) — this session scoped to a solid, fully-green rung 0-9 foundation rather than reaching for red stretch rungs.

**2026-09-03 ~17:1x (hq_T, HQ-TEST — the umbrella row):** ⭐ **THE LADDER-RUNNER TEMPLATE IS BUILT AND THE FIVE WAITING ROWS ARE UNBLOCKED.** `scripts/lib_ladder.sh` is the ONE body — `test_prolog_ladder.sh` and `test_raku_ladder.sh` were byte-identical apart from four language tokens, so the body was extracted once and both were converted to a 4-line stanza over it, **proven byte-identical on `--list`, `--to 3` and the full run, including Prolog's RED arm (14/66 FAIL) so the failure path is preserved and not just the green one**. All seven `test_<lang>_ladder.sh` now exist; the five with no witnesses REFUSE rc=2 (`no \`ladder\` origins`), which is the instrument working. Two defects found in passing: the old Prolog runner's refuse path had **unescaped backticks**, so it ran `ladder` as a command and printed `no  origins` with the name eaten (Raku's copy had escaped them — the divergence only surfaced when the bodies were diffed); and my first extraction made `SCRIP`/`RT_DIR`/`TIMEOUT` `local`, which **shadows the inherited environment** so the documented overrides were silently ignored and the runner would have graded the default binary while you pointed it at another — caught by the negative test, fixed, both now REFUSE rc=2 correctly.

⛔⭐⭐ **AND THE TRACE COLUMN BELOW WAS WRONG FOR EVERY LANGUAGE — see `FINDING-2026-09-03-hq_T-all-seven-languages-already-emit-byrd-port-traces-only-the-flag-is-named-prolog.md`.** Measured, no compiler change: **all seven already emit Byrd port traces today** under `SCRIP_PL_TRACE=1` (snobol4 8 · icon 18 · prolog 112 · snocone 10 · rebus 58 · raku 4 · pascal 36 port lines). `x86_port_hook` sits at the GENERIC port sites every language flows through and is gated only by the env var; **the sole Prolog-specific thing is the letters `PL` in its name.** Two rows were written as *builds* for an instrument that already runs. Also: `SCRIP_PL_TRACE` is a language-named identifier past the frontend/lower boundary (a `RULES.md` § language-identity violation `test_gate_emit_no_lang.sh` cannot see); renaming it `SCRIP_PORT_TRACE` is one line and unblocks six languages — **a `src/` change, so dispatch it, never the instrument lane.**

**2026-09-03 ~17:5x (hq_T, after the QUARTET transition):** ⛔ **MODE IS QUARTET — ceo + 4 HQs, NO FLEET, each HQ MEASURES AND CURES.** The language rows below are no longer dispatchable: seats 07/10/11/12/14 stood down, and **hq_T inherits them**. Concretely, the four ladders that still read ⛔ — **SNOBOL4, Icon, Snocone, Rebus** — are hq_T's own work to build, not rows to file. Under a mode with nobody to dispatch to, "file a queue row" is the shape of not doing the work (RULES § MEASURE AND CURE).

⭐⭐ **THE TEMPLATE CROSS-VALIDATED AGAINST AN INDEPENDENT AUTHOR, which is better evidence than the byte-diff.** seat10 landed a full copy-paste `test_pascal_ladder.sh` concurrently with hq_T's extraction — an eighth duplicate of the same body, but carrying **real** rungs (10 witnesses, refs oracle-cut from `fpc -Miso`, FPC 3.2.2 ISO 7185) and real knowledge hq_T did not have: that `rung09_strings` must use `packed array[1..N] of char` because `-Miso` rejects Delphi's `string`, and that this rung is a **KNOWN RED**. The rebase conflict was resolved by **merging, never picking**: seat10's header onto hq_T's shared body. The merged runner then reproduced seat10's prediction exactly — **rungs 0-8 PASS 18/18, rung 9 FAIL both modes**. A body written by one author, grading witnesses written by another, to a verdict the second author documented in advance. Pascal's inventory row (159 · 0 · 71, fresh) is seat10's and was likewise merged under the corrected trace column rather than overwritten.

⚠️ **A CUSTODY NOTE THE FACT RULE FORCES:** hq_C reports Prolog `--to 9` FAIL=0 on SCRIP `0f3e6d429` / corpus `89950a79c`; **neither commit is on origin** (checked by `cat-file` after a fresh fetch), so that reading is not yet reproducible and `SCORE.md` records the pushed tree instead. A number measured on an unpushed tree is a working number, not a board row.

**2026-09-03 17:45-18:05 (hq_T, point 7 — THE LEADERBOARD):** ⭐ **THE HELPER LANDED: `scripts/util_score_row.py`**, closing the mechanism half of point 7 for all seven languages at once. `write --lang <l> --column entries|floor|board|vendor --text '<the runner's own board line>' --measurer "$S4E_SEAT"` rewrites ONE cell **in place** and merges a `<column>: <stamp>` provenance clause (both repo hashes, `RT_OPT` read from the Makefile not typed, box clock, measurer) into the last column — so one row's cells can honestly carry different trees and measurers, which they already did. `check` reports every row's staleness against origin. One bash line for runners: `gate_score_row <lang> <col> "$board_line" m3,m4` in `lib_gate.sh` — deliberately NON-FATAL to its caller, because turning a bookkeeping failure into a red board is how runners stop calling it. Gated by `test_gate_score_row_rewrites_in_place.sh` (11 arms, <1s, offline, **wired into `make test`**).

⛔ **THE DESIGN CONSTRAINT IS THAT IT RUNS NO SUITE**, and it is Lon's order, not an optimization: `util_build_score_md.py` regenerates the grid by invoking all seven gates and boards (~30-40 min), which is the exact "hour away of running tests" the 15:55 ruling was against. A helper that re-ran anything to record a measurement someone already made would have reintroduced it.

⭐ **AND THE MANUAL DUTY DEMONSTRABLY DOES NOT HOLD — that is why this is a mechanism and not a reminder.** seat07 ran the Raku suite *within the hour* of the 16:05 FACT RULE landing and the raku master cell still read `last measured 2026-08-29`. Not negligence: an operator who has just finished grading a suite is at the point of least appetite for hand-editing a markdown table in another repo.

**2026-09-03 17:56 (hq_T): RAKU MASTER RE-MEASURED, and the old cell was wrong in two ways, not one.** True board: **ast 97 entries — 83 pass, FAIL=0, 14 xfail** · **run 42 entries — m3 41/42, m4 41/42**, one red in both modes (`method_sub_for_replace_1`), 0 crash/hang/unproven/skip. The cell it replaced read `31/129 m3`: stale by 10 entries AND mislabelled, since it named `m3` for a suite that was then entirely ast-graded.

⛔⭐⭐ **AND THE INSTRUMENT HAS A TRAP THAT PRINTS A FULL, PLAUSIBLE, ENTIRELY FALSE BOARD — now closed.** `corpus_suite_harness.py run --lang raku --by-modes-column` **without `--modes`** reported `ast_graded=139/139` and `ast_fail=42`. The suite declares exactly 42 entries `modes="m3,m4"`; all 42 "failures" were the wrong instrument, diffing run output against `--dump-ast`. Cause: `_modes_for()` reads *"ast if the column says ast, else `modes`"* — correct on its face, and a trap when `modes` is ITSELF `["ast"]`, which is what `--lang raku|rebus|prolog|snocone` give you (LANG_CONFIGS default) when the caller omits `--modes`. The split collapses into one bucket. **Nothing about the false board looked false** — it had a denominator, a fail list and a stamp, and it disagreed with the stale SCORE.md cell in the direction a reader would believe (a suite that had "gotten worse"). It now **REFUSES rc=3** naming the column values it cannot honour and the flag to pass; it does **not** guess `m3,m4` for you, since inventing the one input the caller failed to state is the same defect one layer up. Both existing callers (`board_icon_master.sh`, `test_gate_icon_board_honours_modes_column.sh`) already pass `--modes` explicitly and are untouched — control arm `test_gate_icon_board_honours_modes_column.sh` **10/10 PASS** after the change.

⭐ **I hit this trap twice in twenty minutes** (first omitting `--lang`, which refused loudly and cost nothing; then omitting `--modes`, which did not). That is CLAUDE.md's *"any instrument that answers a narrower question than you think you asked will never say so"* — and the difference between the two omissions is the whole lesson: **the loud refusal was free, the plausible answer cost a false finding I had already begun writing up.**

**2026-09-03 ~18:3x (hq_T):** ✅ **SNOBOL4's LADDER CELL IS CLOSED — rungs 0-9, PASS 20/20, pushed** (corpus `5ec3e1ed`). Ladders now exist for **four of seven**: snobol4, prolog, raku, pascal. Remaining: **icon, snocone, rebus** — hq_T's own under QUARTET, not rows to dispatch. Master board went 1726 → 1736 entries, m3/m4 PASS 1679 → 1689, FAIL=0, xfail unchanged: the whole delta is the ten rungs.

⛔⭐⭐ **HOW TO ADD A LADDER, so the next language costs an hour and not an afternoon — the master's shape is not what it looks like.** A "family" is **one SOURCE FILE**, not a directory: `discover_pairs` computes `fam = <relative path minus extension, separators → underscores>`, so `ladder/rung00_hello.sno` becomes the family `ladder_rung00_hello` and `--absorb-only ladder` REFUSES. What you want is a single `ladder.<ext>` + `ladder.ref` at the suite root, holding all rungs delimited by `<comment>------ <n> <entry_name>` banners — the entry becomes origin `ladder__<entry_name>`. **`ALL.<ext>` and `ALL.ref` carry those banners IDENTICALLY and extraction RAISES on a mismatch**; a torn pair once took every SNOBOL4 board on the box down for 40 minutes (`2d75933ec`). ⛔ **So never hand-edit the pair — let the builder do the pairing**, in a scratch tree first (`cp -r corpus/tests/<lang>`, point `S4E_HOME` at its parent), then for real with `--absorb-only <family> --delete-absorbed`. Declare the family in `config/MODES.tsv` as `family<TAB>m3,m4` — **declared, never derived**: the builder refuses to guess modes from a family's name, on the grounds that a heuristic right on every case you have gives no signal when it starts being wrong.

**2026-09-05 (hq_T, QUARTET — the census hq_B asked for, and hq_B's rule into the standard):** ⭐ **TWO GUARDS WERE BLIND, IN TOOLS THAT SHARE NO CODE, FOR THE SAME REASON: THEIR EVIDENCE WAS OUT OF REACH.** (1) `find_grid` never got the missing `else` its twin `find_table` was given on 2026-09-04, so a malformed `SCORE.md` grid row vanished silently and `test_gate_score_tables_agree.sh` went **RED → `GATE PASS(0)`** on hq_B's edit — reproduced here, cured, and floored: both score gates now REFUSE rc=2 on a zero population, and three arms in `test_gate_score_row_rewrites_in_place.sh` keep it (18 arms, blocking). (2) The harness's ast-graded-by-execution guard read a **sibling `ALL.csv`**, so it was blind on every runner that grades an **extracted family in a tempdir** — measured both ways on pascal's 5 `modes=ast` entries: in place `rc=2 REFUSING`, extracted `rc=1 total=5 m3_fail=5 m4_fail=5`, **and all five PASS when graded by the instrument they declare**. `extract-family` now carries a `.modes` sidecar as it already carries `.in`/`.xfail`; `test_gate_modes_declaration_travels.sh` (15 arms, all 7 languages, ~8s) is **wired into `make test` blocking**, fail-once proven 8 → 0. Call-site census: **63 grading call sites, 6 pass `--by-modes-column`, 8 grade an extraction and none of the 8 passed it.** Full evidence: `FINDING-2026-09-05-hq_T-a-check-that-cannot-see-its-subject-says-nothing-and-nothing-reads-as-a-pass.md`.

**2026-09-06 ~21:0x-22:0x (hq_T, OCTET — `ceo-372` landed, point 7):** ⛔⭐⭐ **A SUITE ROW STATES THE AND PER
PROGRAM — the programs green in EVERY graded mode.** Lon's ceo ruled it on hq_T's ask: *"a program red in m3 and
another red in m4 both count against the row; never m3 alone, never m4 alone, never the min of two counts (which
hides a program red in each)."* All four declaring runners are rewired (SCRIP `c18cb9811`): `test_corpus_snobol4.sh`
(was `PASS3`, m3) · `board_icon_master.sh` (was `m4p`) · `test_pascal_fpc_suite.sh` (**130/181 → 116/181**) ·
`test_pascal_pat_suite.sh` (**300/427 → 286/427**). ⛔ **THOSE DROPS ARE A CRITERION CHANGE, NOT A REGRESSION** —
nothing got worse between the run before and the run after; the rows began counting what a suite row has always
claimed to count. The cell keeps the per-mode counts beside the number, and the terminal summaries print it too.

⭐ **THE AND CANNOT BE RECOVERED FROM A BOARD LINE, AND THAT IS WHY THE ROWS PUBLISHED ONE ARM FOR MONTHS.** It is
a fact about each PROGRAM, and per-mode counts are what is left after the programs are gone: `min(m3_pass, m4_pass)`
is not a count of any set of programs at all — two entries, one red only in m3 and one red only in m4, give
`min() = N-1` where the AND is `N-2`. So it is accumulated where both verdicts are in hand: a per-program flag in
the three shell runners, and a new `all_pass=`/`all_n=` pair on `corpus_suite_harness.py`'s `SUITE_BOARD` for the
two boards that read their numbers from it. Fields are appended, so every consumer's `key=[0-9]+` parse is
untouched and `--combine` sums them like any other field. ⛔ **Both board runners REFUSE rc=2 when `all_pass=` is
absent** rather than folding an empty string as zero — a stale harness or a pre-existing shard checkpoint would
otherwise publish a short number that reads as a catastrophic regression that never happened.

⚠️ **THE m4-vs-m3 ARGUMENT THIS SETTLES IS WORTH KEEPING, because both sides were right about the other.** The
Pascal rows were wired to m4 (SUITES.tsv carried m4), then to m3 by hq_V at 20:5x when the coo hand-set the
published row to the m3 numbers — each rewiring correctly avoiding the phantom regression the *other* would have
published, and each landing in the hour the other was measured. hq_V's standing reason was real: fpc's m4 is
run-to-run non-deterministic (five runs, one tree, five pass counts, row `pascal-m4-intermittent-segv-layout-
sensitive`), and a row wired to a number that moves without the code moving manufactures phantom movement in the
table Lon reads. ⛔ The ceo answered that rather than overruling it: **"a mode whose count varies run to run is a
DEFECT ROW in that lane — a nondeterministic compile is the xfail shape with a runner's excuse in front of it —
never a reason to publish the steadier mode."** The wobble now lands on the row that owns it instead of being
routed around by the choice of arm. ✅ **AND THAT ROW IS LIVE AGAIN — reopened by the ceo at 21:05
(CEO-379, .github `3879c3d3`): rank 0, assignee hq_V, `FREE`.** It had been filed in `QUEUE.done.tsv`, unassigned
and absent from `QUEUE.tsv`, while its defect was in that night's board (fpc m3 130 vs m4 116) — measured, not
assumed, and asked up rather than reopened from this lane. ⭐⭐ **THE ceo's REASON IS THE PART WORTH KEEPING, and it
is a NEW WAY FOR A CRITERION TO LIE — from the CLOSING side.** The row's DONE-WHEN graded the *gate's* population
and was honestly met there, while the *class* it names lives on the fpc suite's population: **one member cured, the
class red, the row closed.** That is shape 2 (a denominator narrower than the blast radius) turned around — there it
lets a change through, here it lets a *row* out — and it is invisible for the same reason: the criterion did exactly
what it said. ⛔ **So a DONE-WHEN met on a narrower population than the class its topic names has not closed that
class**, and hq_V now re-scopes it (five suite runs on one clean tree must read ONE m4 count) and proves it red once.
⭐ **The reason this was checked at all is shape 5's own discipline one level up: a comment that cites a row as
live is a PREMISE, and this file's shape 4 says the mechanism can be perfect while the input is false.** ⭐ Note the shape of the near-miss: two seats rewiring one line in opposite
directions within an hour, each with a correct local reason, is what a **missing ruling** looks like from the
inside — neither was wrong, and the row was going to keep flipping until the criterion was named.

**Also this sitting:** shape **5** added to HOW A CRITERION LIES — *the tree stamp is not a binary* — the
standard the ceo ruled hq_T's to write here. Its discriminator is one line: run the cure's own witness through
the binary that is about to grade, and show the cured answer.

## THE STANDARD — what every language has when this is done (the best of each today, made the rule for all)

⭐⭐⭐ **LON 2026-09-04 11:39 CDT, in-chat to ceo, verbatim (THE TARGET OF THIS PROGRAM, routed the same sitting):** *"When we are done will we have a complete test suite with the ladder of features starting from simple to complex? For instance does Rebus have such a rung ladder? Will all languages get a full test suite with 100's of test cases exercising each feature and several combination of features? That is what we need."* — **RULING (ceo, same sitting):** the standard below is amended so that it DELIVERS that sentence, not a thinner thing: point 1 makes a rung a FAMILY (every form of the construct, then its combinations with the rungs below), and point 8 makes per-feature and per-pair coverage a MEASURED instrument with a floor, because a target nobody prints is a wish. **MEASURED AT THE RULING (corpus `169a93209`):** every master already carries feature columns in `ALL.csv` (snobol4 39 · icon 61 · prolog 39 · raku 39 · pascal 50 · snocone 39 · rebus 39 features), so the census is a script over data that exists, not a new corpus format. SNOBOL4 is the only lane already in Lon's shape: 1736 entries, 18 of 39 features with ≥100 entries, 2 below 10 (`APPLY` 8, `ABORT` 7), 1258 entries exercising two or more features. The gap, master entries and built ladder rungs: icon 731 (rungs 0–35 built, 197 rung witnesses) · raku 859 (rungs 0–9, 720 of the entries are absorbed one-line smoke probes, no `LADDER.tsv` census) · prolog 408 (§ E rungs 0–13, 37 witnesses, no `LADDER.tsv` file — the § E table is the census) · snocone 283 (census 51 construct rows, 10 rung witnesses) · pascal 166 (rungs 0–11 built) · rebus 77 (rungs 0–11 built to the TR 84-9 top, 29 witnesses). Rebus HAS its ladder; what no lane but SNOBOL4 has is the volume per feature and the combinations.


1. **A CONSTRUCT LADDER with tiny rungs** (Prolog's shape, `ARCH-PROLOG-BYRD-BOX-TRANSLATION.md` § E; Icon's 41 IR rungs are the precedent): `ladder__rungNN_<slug>` entries in the master from rung 0 (hello world) upward, one construct per rung, graded by `test_<lang>_ladder.sh --to N | --only N` in both modes, refs cut by the language's oracle, witnesses that fail once before their rung lands. **AMENDED 2026-09-04 11:39 CDT (Lon, above): a rung is a FAMILY, not one witness.** Rung N carries (a) one tiny witness per FORM the reference lists for the construct (every operator spelling, every argument shape, every failure/edge case the book names — the census column names them), and (b) COMBINATION witnesses pairing the construct with rungs below it (the construct inside a loop, under a function call, in a pattern/goal context, with the I/O forms already green). The rung is green when every member is green in both modes. One-witness rungs stay legal only while a rung is being minted; a rung whose family is one member is COUNTED as one, and the coverage floor in point 8 is what turns that into a red.
2. **A REGRESSION MASTER** `corpus/tests/<lang>/ALL.<ext> + ALL.ref + ALL.csv` (SNOBOL4's 1,726 is the model), oracle-cut refs, both modes, on the leaderboard, never stale more than 25 commits.
3. **A SMOKE floor gate** of 4–14 programs (`test_smoke_<lang>.sh`), the HARD zero-FAIL bar, inside `make test`'s reach.
4. **PARSER FIXTURES** graded by `--dump-ast` (`modes=ast` in the master; Icon/Prolog/Raku have them).
5. **VENDOR / ORACLE SUITES** under `corpus/packages/<lang>/` graded by their own oracle (SNOBOL4 5, Icon 5, Prolog 2, Pascal 2 + the ISO 7185 PAT, Raku the roast).
6. **A PORT-TRACE GATE** — **ceo RULING 2026-09-03 ~18:05 (CEO-172, on hq_T's measured correction of its own ask):** the point stands FOR ALL SEVEN, because the instrument is ours, not the oracle's — `x86_port_hook` (`src/templates/x86/x86_asm.h`, installed at the generic `x86_jcc`/`x86_jmp`/`x86_deflabel` port sites every language's boxes flow through) already emits `(N) D Port: box` lines under `SCRIP_PL_TRACE=1` with no compiler change (hq_T, SCRIP `0fca0dc3`, one witness per language: snobol4 8 · icon 18 · prolog 112 · snocone 10 · rebus 58 · raku 4 · pascal 36). Where an oracle traces (Prolog `trace/0`, Icon `&trace`, SNOBOL4 `&TRACE`) the gate diffs our port sequence against the oracle's; where none does (Snocone, Rebus, Raku, Pascal — Rebus has no rival implementation at all) the gate diffs against PINNED trace refs cut once from a reviewed run and re-pinned only with a FINDING naming the semantic reason — a self-consistency gate, labelled as such in the inventory, never a red cell. The four cells below that read ⛔ none read "pinned refs owed" instead. Original wording: where the oracle can trace (Prolog has it; Icon's `&trace`, SNOBOL4's `&TRACE`): the emitted Byrd-port sequence diffed against the oracle's trace — the literature's debugging model turned into the execution model's instrument.
7. **A LEADERBOARD ROW** per instrument, rewritten by every run (FACT RULE).
8. **A FEATURE-COVERAGE CENSUS with a floor (Lon 2026-09-04 11:39 CDT: *"100's of test cases exercising each feature and several combination of features"*).** One instrument for all seven, over the feature columns every `ALL.csv` already carries: it prints, per language, entries-per-feature and entries-per-feature-PAIR (two features exercised in one entry), names every feature below the floor and every feature with no pair at all, and rewrites its cell on the leaderboard. The FLOOR is per language and per feature, set from the reference's own list of forms (a construct with three spellings owes at least those three single-feature witnesses; the hundreds come from combinations), with SNOBOL4's master as the model shape; a feature column that is never filled is a refusal (rc=2), not a zero. Absorbed programs count toward coverage only when their feature columns are FILLED by the builder from the source, never hand-typed. This point is hq_T's instrument; the families are each lane's walk.
9. **GENERATED PROGRAMS — random and exhaustive (Lon 2026-09-04: *"grammar-based random and exhaustive language generators, like expressions.py … every single combination up to those character lengths"*).** Per language, a grammar taken from the ladder census drives (a) an EXHAUSTIVE enumerator of every valid program up to length N, each ending in exactly one measurable OUTPUT, and (b) a seeded RANDOM generator over the same grammar; refs come from the language's oracle through `lib_oracle_flags.sh`, never hand-typed; grading is differential (AGREE/DIFF/FALSE-ACCEPT/CRASH/HANG), deduplicated to one witness per canonical shape. Generated programs are NOT absorbed wholesale — a master is a regression suite — every DIVERGENCE class becomes a master witness (`generated__<lang>_len<N>_<shape>`) and a class row on its rung, as the August pattern fuzzer's 9 classes did. Leaderboard cell: programs per length, AGREE/DIFF, hash. Lineage and spec: `FINDING-2026-09-04-ceo-the-exhaustive-program-enumerator-was-specified-in-march-and-never-built.md`; row `exhaustive-program-enumerator-to-length-n-with-oracle-divergences-as-witnesses` (hq_T).

## HOW A CRITERION LIES — the four measured shapes, and what each costs (ceo-routed, 2026-09-04)

⛔ **A DONE-WHEN is an instrument, and an instrument whose capacity to fail was never measured is not evidence.**
Every shape below was measured the same day, most of them on the author's own criteria, and each was found by
RUNNING the thing rather than by reading it. They are listed because the failure looks like a result in all four
cases — there is no traceback and nothing to investigate.

**1. IT COULD NOT MEASURE ITS SUBJECT.** The predicate exits non-zero (or zero) for a reason unrelated to the
thing it names. Witnesses: `--lang snobol4` rejected by *argparse*, so argparse's own exit 2 read as the tool
refusing while the tool was still crashing on the case being probed; a harness flag combination refused **before**
the binary was consulted; a case-sensitive `grep "PASS="` against a board line that prints `m3_pass=`;
`git -C ..` pointed at a non-repo sibling root, so the check errored instead of ever testing its diff — note that
one could only ever be **permissive**, inside a criterion whose whole job was to prove a directory untouched.
*Cost: a green that certifies a defect, or a red that convicts an innocent component.*

**2. ITS DENOMINATOR WAS NARROWER THAN THE CHANGE'S BLAST RADIUS** (hq_B). The criterion measured exactly what it
claimed, and the claim was smaller than the edit. Witness: a lowering change to a **shared** capture-target node
whose DONE-WHEN named only the witnesses the change was written for — green, correct, and blind to the master
regression it caused. ⭐ *A DONE-WHEN that names only the witnesses a change was written for cannot detect that
change breaking something else, and that is invisible precisely when the row is done well.* The law that catches
it is SHARED-NODE VERDICT SCOPE, which was not applied because the change read as sugar.

**3. ITS POPULATION WAS WIDER THAN THE ROW** (hq_T). Witnesses: a class criterion matching `ARBNO|FENCE|deferred`
counted **41** of 61 xfails for a **5**-entry class, because the other classes describe their own witnesses with
the same words (twice more the same hour: SETEXIT read 3 for 2, misc read 7 for 4); and a `grep -c "rc=134"`
counted **7** aborting programs where there were **6**, the seventh match being the runner echoing a SCORE.md
cell whose prose contains the string. ⭐ **A class is a LIST that a census produced; a keyword is a GUESS at that
list** — so name the members, and anchor to the shape of the line you mean. *A criterion wider than its row
demands other rows' work before it can close, and reads red forever for reasons that are not its own.*

**4. ITS PREMISE WAS NEVER MEASURED** (hq_T, and the ceo the same hour). The mechanism was right, the verification
was thorough, and the *input* was false. Witness: a ref pinned over the oracle's answer on the reported premise
*"SPITBOL fails this construct too"*, which one command refuted — the oracle runs it cleanly and prints the ref
that was already there. ⛔ **Verification tests the MECHANISM; the defect was in the PREMISE.** Every check asked
whether the tool wrote what it was told, none asked whether what it was told was true. *Cost: the most expensive
of the four, because nothing in the run looks wrong — no red, no refusal, only a green board and a colleague
thanking you for unblocking them.* **The cure is never "be more careful": make the premise a measurement the tool
makes.** `pin-ref` now runs the oracle itself and refuses a clean disagreement.

**5. IT NAMED THE TREE AND GRADED A BINARY** (hq_T 2026-09-06, `ceo-372` — the ceo ruled this standard mine to
write here, as *"the right discriminator"*). ⛔ **A TREE STAMP IS NOT A BINARY.** Every `SCORE.md` row, every
`gate_stamp`, every receipt names two repo hashes — and a repo hash is a fact about a **checkout**, never about
the executable that produced the number beside it. The two are joined by an assumption nobody measures: *that
`make` was run, that it finished, and that it rebuilt the thing the cure is in.* When that assumption is false the
row is not wrong in any detectable way — it carries a current tree, a plausible board, an honest measurer, and a
number produced by code that predates the cure.

⛔ **AND THE GUARD WE HAVE IS A CLOCK, NOT A CONTENT PROOF.** `gate_require_fresh` (`lib_gate.sh`) compares
**mtimes**: the binary must not be older than the newest tracked source. That catches the common case and it is
worth keeping, but its subject is *when a file was written*, and mtime and content are different facts.
`git checkout` of a branch whose file content is identical, a `make` that failed after relinking, a cure that
landed in `libscrip_rt.so` while the graded arm ran `./scrip`, a stale object in a shared objdir — each leaves a
binary that is *newer than every source* and still does not contain the cure. Shape 1 exactly: the check exits
zero for a reason unrelated to the thing it names.

⭐ **THE DISCRIMINATOR IS ONE LINE, AND IT IS POSITIVE: RUN THE CURE'S OWN WITNESS THROUGH THE BINARY THAT IS
ABOUT TO GRADE, AND SHOW THE CURED ANSWER.** Not a hash, not a timestamp, not "I ran make" — a command and its
output, in the receipt, beside the board:

```
$ ./scrip --run <the witness the row was opened on>     # the binary that produced the board below
<the output only the cured binary can print>
```

⛔ **A RECEIPT THAT NAMES A TREE AND NOT A WITNESS HAS NOT PROVEN THE BINARY CONTAINS THE CURE**, and neither has
a green board: the board is what is in question. This is the cheapest of all five checks — one program, already
minted, already the row's DONE-WHEN — and it is the only one whose failure mode is *loud*, because a witness that
still prints the old answer says so in the one place you are looking.

⭐ The general form, and why it generalises past builds: **provenance answers "what was I standing in", a witness
answers "what did I actually run"** — and every criterion in this file that lied did so by substituting the first
question for the second.

### And more, learned by getting them wrong the same day

⛔ **AN IDENTIFIER THAT IS A POSITION IS NOT AN IDENTIFIER.** Entry numbers in `ALL.xfail` are line addresses: one
re-verification pass that added and reworded entries above a block pushed every entry below it down by a uniform
**+8**, so the same five programs are `1741/1743/1750/1751/1752` in a morning clone and `1749/1751/1758/1759/1760`
on origin that evening. ⭐ The cost was not confusion — it was an **accusation**. A seat reported a census; the
numbers did not match; I told it that it had censused the wrong set. Its *names* had matched the row's own
criterion exactly, and its clone was nine commits behind. **The identifier I had added an hour earlier to prevent a
mismatch is the one that caused it.** Grade on names; treat a number as a convenience that is true for one commit.

⛔ **A TRIM IS NOT A CENSUS.** Having found that a keyword criterion over-counted a class, the obvious repair is to
cut the list down to the right size — and that repair reads the *same leaky match* one more time. Measured: a
2-entry class trimmed from 3 was trimmed to the **wrong pair**, and the wrong member shared only the words
`SETEXIT/&ERRLIMIT` with the class, in a passing clause about credit. Naming the members made the criterion
**precise without making it correct**, which is worse than leaving it vague, because a precise criterion over a
wrong population *looks settled*. ⭐ Both times the error was found by a person reading each member's own reason
line. There is no tooling substitute for that step, and every classifier we own is a guess until someone takes it.

⛔ **A PREDICATE WHOSE FALSE BRANCH IS A BLOCKER MUST BE PROVED TO FIRE ON THE INPUT THAT SHOULD TRIGGER IT**
(hq_C). A branch nobody has watched execute is not a branch. Witness: `handoff_status.sh` reported
`DIVERGED from origin/<branch>` on a tree byte-identical to origin, printing a remedy that could never clear it,
so a seat following the instruction loops forever. Two causes stacked, and the first is a shell trap worth
memorising: **`git rev-parse origin/no-such-ref` ECHOES ITS ARGUMENT ON STDOUT and then exits non-zero**, so a
`|| echo MISSING` yields the two-line string `origin/no-such-ref\nMISSING` and the no-such-branch arm can never
fire. ⭐ `2>/dev/null` makes it *worse*: it hides the error text and leaves the poisoned stdout. The cure is
`rev-parse --verify --quiet`, which prints nothing and exits 1.

⛔ **A TIMEOUT BOUND DOES NOT SCALE WITH LOAD** (hq_T ruling, on hq_C's measurement of four programs killed at
120 s under load 3.6). A bound that moves with the machine makes a verdict irreproducible: the same program
passes or fails depending on its neighbours, and two roots can never reconcile a disagreement. A killed program
is **NOT GRADED and NOT A FAILURE** — and the row it lands in must say so, because a board that tells the
terminal about a short denominator and tells the leaderboard nothing has published a full-population claim.

⛔ **A MODE THAT CARRIES A FALLBACK IS NOT AN HONEST ARM FOR THE THING THE FALLBACK REPLACES** (ceo 2026-09-05, routed to this standard; evidence `FINDING-2026-09-05-ceo-runtime-define-non-literal-prototype-code-body-and-the-dexp-idiom-land.md`). Mode 3 carries a **tree-walking interpreter fallback for by-name function calls** (`src/driver/driver_call.c`, `call_user_function` via `_usercall_hook`). The gimpel FLOOR therefore read **GREEN in mode 3 through that interpreter while mode 4 read error 5** — the compiled path was broken the whole time and the board said so in one mode and not the other. ⭐ **The general form, and it is the reason this belongs in a TEST standard rather than in a driver note: a green is only evidence about the mechanism that actually produced it.** Two modes are not two independent samples of one implementation when one of them can answer the question a different way. **The rule: a BY-NAME CALL verdict is proven on mode 4. A mode-3-only green on a by-name call is not evidence** — it is a measurement of the fallback. ⭐ Note this is the *mirror* of MODES MAY DIVERGE: divergence is legal as an OPTIMIZATION choice, so a per-mode difference is not automatically a defect — but that licence is exactly what lets a fallback-produced green look like a legal divergence instead of a missing implementation. When the modes disagree, ask which mechanism answered, not merely whether disagreement is allowed.

⛔ **A CRITERION NEVER PINS A POPULATION COUNT — AND THE PIN IS NOT THE WORST OF IT** (hq_T 2026-09-05, on the ceo's ruling R4; the measured subject was `test_gate_optbypass_watermark.sh`, now RETIRED). The gate pinned its own denominator: *"if the graded population is no longer 1494 the ratio silently means something else, so REFUSE(2) rather than compare apples to oranges."* The reasoning is sound and the mechanism is still wrong, because **the corpus grows every day and the pin cannot**. Measured history: pinned 1494, re-pinned 1656, graded population by the time it was read **1805** — re-cut twice, stale a third time, and refusing continuously in between. ⭐ **A pinned count converts a healthy fact (the suite grew) into a permanent refusal**, and refusals are the one verdict nobody chases, because "could not measure" reads as somebody else's problem. **The cure is to READ the denominator from the suite and compare PER-ENTRY IDENTITY** — a set of names — **never a literal count.** Identity is population-independent by construction, and it says *which* entry drifted, which a count can never do; the gate's own header records its count moving 289→291 on an unrelated commit with the corpus proven byte-identical, and no count could name what moved.

⛔⛔ **AND THE REFUSAL HID TWO WORSE DEFECTS UNDERNEATH IT — THIS IS THE PART TO REMEMBER.** The population check ran *first*, so the gate never reached its own arms, and nobody saw that: **(a)** all 28 `modes=ast` entries were being graded by EXECUTION against a `--dump-ast` ref, manufacturing 28 phantom failures in the arm the gate calls "a hard 0-failures bar" (exact set match, 28/28, no false positives or negatives) — the same defect hq_B had just cured in the master board runner via `--by-modes-column`; and **(b)** the two things it measured, `SCRIP_OPT=0` and `SCRIP_ZD=0`, **had been DELETED by Lon's ruling on 2026-09-03** (SCRIP `ce199b05e`, *"the emergency optimizer bypass is gone, not merely retired"*). Both arms were the default arm re-run under a different name. Proven two ways rather than one, because grep-absence is not proof: zero `getenv` sites in `src/`, **and** emitted asm byte-identical with and without each flag — with a NEGATIVE CONTROL (`SCRIP_ZDP_TEARDOWN=1` *does* change the output) to show the method can detect a live flag at all. ⭐ **The general form: a REFUSING gate is not a dormant gate, it is a BLINDFOLD.** Everything downstream of the refusal stops being measured, and the longer the refusal stands the more it accumulates — so a stale refusal must be triaged like a red, never parked as "noisy". Had the pin been maintained, this gate would have gone green and reported `SCRIP_OPT=0 0/1805` about a flag that does not exist: a confident, well-formed, entirely meaningless number. ⛔ **Before re-cutting any criterion, measure that its SUBJECT still exists** — that is shape 4 (ITS PREMISE WAS NEVER MEASURED) applied to the instrument instead of to the data.

⛔ **A CARRIED MAX WATERMARK IS AN UPPER BOUND ONLY UNDER SHRINKAGE** (hq_P's own retraction, 2026-09-01; carried out of the retired optbypass gate because the lesson outlives its instrument). A `<=` against a maximum measured once looks conservative, and is — *while the graded set only loses members*. **Every entry promoted INTO a graded set brings its own verdict with it**, so under GROWTH — the direction this corpus actually moves — a carried max is not conservative, it is simply wrong, and it goes wrong in the direction that reds the NEXT seat's push for a reason that has nothing to do with their change. ⭐ Pair it with the population rule above: **counts break under growth in both directions** — a pinned denominator refuses, a carried max false-reds — and per-entry identity breaks under neither.

⛔⛔ **AND THE THIRD MEMBER OF THE FAMILY CLOSES THE ARGUMENT: A FLOOR CANNOT CATCH A FALL THAT STOPS ABOVE IT** (hq_B, measured 2026-09-05, handed to this lane). The floor was invented to *cure* the two count anti-patterns above, and it does: `board_icon_master.sh` pins `M3_PASS_FLOOR=596` / `M4_PASS_FLOOR=596` and its header says so deliberately — *"FLOOR, NOT A PINNED TOTAL … growth needs no re-pin."* Population-robust, no refusals, no false reds. **And it printed `watermarks held` straight through a real regression**: the Icon master fell **601 → 599** — two programs, one of them a shared-node regression from a SNOBOL4 landing — and 599 is comfortably above 596, so nothing fired. The board then went further and *invited a re-pin* at a number two below the truth. ⭐ **A floor answers "have we collapsed?", never "did anything break?"** — and those read identically on a green board. ⛔ Worse, a floor **decays toward uselessness by design**: every point of genuine progress widens the gap between the pin and the truth, so the longer a lane succeeds the more regression it can absorb silently. ⛔ **A SCORE cell asserting `FAIL=0` makes a claim no floor can check** — the floor never looked at which entries failed, so the cell is stating something its own evidence cannot support.

⭐⭐ **THE WHOLE FAMILY, AND WHY THE STANDARD PICKS IDENTITY.** All three are the same mistake — *scoring a set by a scalar* — and each fails in its own direction: a **pinned population** REFUSES the moment the suite grows · a **carried max** FALSE-REDS the next seat under growth · a **floor** MISSES the regression that lands above it. There is no fourth scalar that escapes: any single number over a changing set must trade a false alarm against a blind spot. **Per-entry identity — the SET OF NAMES that pass — breaks under none of them**, needs no re-pin when the suite grows, and is the only form that can say *which* entry moved, which is the thing a human actually needs at 2am. This is what "compare per-entry identity, never a literal count" means, and it applies to every one of the seven languages' boards, not only the one that got caught.


⛔⛔⭐ **AND THE DEGENERATE CASE THE FAMILY ABOVE DOES NOT COVER: A GREEN THAT APPEARS WHILE YOU ARE EDITING THE DATA IS A SUSPECT, NOT A REWARD** (hq_B's rule, 2026-09-05, handed to this lane with the incident that produced it; reproduced and cured by hq_T the same day, SCRIP `4c70284dd`). hq_B pasted a minimized Icon witness into a `SCORE.md` cell. Icon's concatenation operator is **two pipes**, this is a markdown table, and the row went from 9 cells to 17 — so every tool that splits on `|` stopped seeing an icon row at all. **`test_gate_score_tables_agree.sh` went from RED to `GATE PASS(0)` in that same edit.** Nothing was fixed: the gate compares mirrored cell *pairs*, an unparseable row yields no pairs, and **a population that cannot be READ scores exactly like a population with no conflicts.** hq_B was one sentence from reporting the icon disagreement resolved, and what caught it was a refusal in a *different* tool (`util_score_row.py progress`: *"the September-10 grid has no row for icon — refusing to publish a progress line over a partial grid"*).

⭐ **REPRODUCED, THEN MEASURED IN THE STRONGEST FORM, and the pre-cure output is the whole argument** — on a scratch board whose grid rows were all widened by one cell, both gates printed their own emptiness as a success and exited **0**:

```
GATE PASS(0) [score_tables_agree]: 0 mirrored cell pair(s), 0 same-denominator conflicts
GATE PASS(0) [score_column_semantics]: 0 runner citation(s) all match their column's kind
```

⛔ **SO PER-ENTRY IDENTITY IS NECESSARY AND STILL NOT SUFFICIENT: identity over an EMPTY set is a green.** The family above ends by picking identity over every scalar, and that ruling stands — but all four members share one root, *the verdict is computed downstream of the population without ever asserting the population is there*, and identity inherits it. **Every comparison gate owes a POPULATION FLOOR: it REFUSES rc=2 when it graded zero, and never prints the success shape.** (This is the gate-side twin of the board-side row `every-board-wrapper-refuses-on-a-zero-population-instead-of-passing-vacuously`, closed 2026-09-04 — the same defect, one layer up, found because the row's cure was written for `test_*_suite.sh` wrappers and a *gate* is not a wrapper.) ⛔ And the direction of the trap is the part to keep: **the population had not decayed, it was destroyed by the person reading the board** — so the moment your own edit makes a red go green, that is the moment to distrust it hardest.

⛔⛔⭐ **THE EVIDENCE MUST TRAVEL WITH THE THING IT DESCRIBES, OR THE GUARD IS BLIND EXACTLY WHERE IT IS NEEDED** (hq_T 2026-09-05, the cross-language census hq_B asked for; gate `test_gate_modes_declaration_travels.sh`, in `make test`; SCRIP `4c70284dd`+). Every master declares per entry HOW it is graded — an `ast` entry's `.ref` is a `--dump-ast` dump and executing it manufactures a red that means nothing (the 28-entry defect that ended the optbypass gate, and the 42-, 5- and 175-entry witnesses before it). The harness now REFUSES such a run — **but its evidence was a *sibling* `ALL.csv`, so the guard's activation depended on WHERE THE CALLER PUT THE SUITE, not on what the suite declares.** Every runner that grades an **extracted family in a tempdir** — `extract-family`, the documented bridge, and `test_snocone_corpus_suite.sh`'s own shape — had no csv beside it, and **a guard that cannot see its subject says nothing, which is indistinguishable from a pass.**

⭐ **MEASURED BOTH WAYS ON ONE PAIR OF COMMANDS** (pascal's 5 `modes=ast` parser entries): graded **in place**, `rc=2 REFUSING`; the **same five entries extracted** and graded the same way, `rc=1` with a full, plausible board — `total=5 m3_fail=5 m4_fail=5`. ⛔ **And all five PASS when graded by the instrument they declare** (`ast_pass=5 ast_fail=0`): the false board was not merely unreliable, it was wrong in every cell it printed. ⛔ **The other half, and the reason this is a defect rather than a missing feature: `--by-modes-column` REFUSED on an extracted pair for want of that same csv** — so on an extraction **the correct call was impossible and the incorrect one was silent**, which is not a choice a caller can be blamed for making. The cure is that `extract-family` carries a `.modes` sidecar the way it already carries `.in` and `.xfail`, under the law written in its own docstring: **a check that does not carry every field the grader reads is not a check** (hq_C). `modes` was the one field it did not carry. Fail-once proven in all seven languages (8 violations pre-cure, 0 after).

⛔ **AND "NOBODY DECLARED IT" HAS THREE SPELLINGS, ONLY ONE OF WHICH IS LOUD** — measured across the seven masters while censusing them: **`UNKNOWN`** (the builder's declared-never-derived default; counted and printed separately on every board — snobol4 1764 of 1859 entries, prolog 237 of 611, icon 1 of 754), **the empty string** (silent, folded into the run population with no trace — what every `corpus/packages/*/ALL.csv` carries today), and **an absent row** (which `--by-modes-column` refuses on). A law that says *declared, never derived* is only as strong as its weakest spelling of "undeclared", and the silent one is the one in the vendor suites.

⛔⭐ **AND THE FLOOR IS NECESSARY, NOT SUFFICIENT — THE COMPLEMENT, FROM hq_B THE SAME DAY.** A population floor catches the EMPTY case and nothing else: hq_B's classifier ran over a **full** population with a **broken comparator** and printed a plausible non-zero board that was wrong in a specific 8 cells. Their control arm passed because it was a control that *only controls for what it varies* — two hand-verified witnesses, both of them fixtures whose verdict the defect did not happen to change. ⭐ So the pair is: **a zero-population refusal is what makes a green mean anything at all; a CROSS-LINEAGE control — a witness whose expected verdict was established by something other than the instrument under test — is what makes a non-zero green mean anything.** Neither substitutes for the other, and every gate in this standard owes both.

### Two positive rules that fall out of the same evidence

⭐ **WHEN A THEORY EXPLAINS ALL THE EVIDENCE, PRINT THE ONE VALUE IT PREDICTS BEFORE WRITING IT UP** (hq_C).
A subject-base theory was consistent with every number in hand and one `fprintf` refuted it. Consistency with the
evidence you already have is the cheapest thing a wrong theory can buy.

⭐ **WHEN YOU CAN NAME WHAT CHANGED, YOU HAVE A SUSPECT, NOT A CAUSE** (hq_C). Hold everything and vary the one
ingredient. Witness: a RETURN-after-code-object finding where the attribution slipped because the failure branch
was *also* the ingredient that changed on the crashing iteration — three wrong calls in one day, each undone by a
single such command. ⛔ The trap is that naming what changed feels like the end of the investigation, and it is
the beginning: "it changed" and "it caused" are the same sentence in English and different facts on the machine.

⭐ **VARY INGREDIENTS AGAINST EACH OTHER, NOT ONE AT A TIME** (hq_C). An ablation set that never removes the true
cause will confidently name whatever is left standing: nine one-at-a-time removals produced a **wrong** trigger;
twelve crossed cells produced the right one and cost less.

## THE INVENTORY (measured 2026-09-03 16:20 box clock, SCRIP `d24e99d8`; rewrite a cell when you close its gap)

⭐ **TRACE COLUMN RE-MEASURED 2026-09-04 by hq_T (SCRIP `2793c4170`, corpus `668e2daf`).** Standard point 6 is
**instantiation work now, not build work**: `lib_port_trace.sh` carries the body once and a language gate is a
four-token stanza (`PORTTRACE_LANG` / `_SUITE` / `_EXT` / `_FAMILIES`). ✅ **ALL SEVEN ARE BUILT — POINT 6 IS
CLOSED** (hq_T 2026-09-04, SCRIP `2d07f4bab` + corpus `561da4c9`): icon (oracle diff) · prolog · snobol4 ·
snocone · rebus · raku · pascal. The last four were minted, cut and graded in one sitting, which is the
shared body's whole return: the four stanzas together are ~8 lines of non-comment shell.
⛔ Each was proved in BOTH directions, not just green — no-ref rc=2 naming the absent path · `--cut` mints
· graded rc=0 over a printed denominator · `--to N --only M` rc=2 rather than guessing a population · and
**one port glyph flipped in snocone's ref turns it rc=1, rc=0 again on restore**. That last arm is the only
one that proves the instrument can say NO; a pinned gate that cannot fail is decoration, and the other four
arms only prove it can run.

⛔⛔ **POINT 6 HAS TWO SHAPES AND THE INVENTORY MUST NOT CONFLATE THEM** — this is the correction that came out
of building it, and it contradicts what this file said an hour earlier:
- **SELF-PIN** (`lib_port_trace.sh`): refs cut from SCRIP's own traces. Proves the port sequence has not MOVED,
  never that it is RIGHT. **Reachable for all seven today**, because `x86_port_hook` is language-blind.
- **ORACLE DIFF**: the oracle's own trace normalised onto the four Byrd ports. **Icon has one and it is BUILT**
  (`test_gate_icn_port_trace.sh`, off `&trace := -1`). Strictly stronger, and deliberately not on the shared body.
⛔ Do **not** write "no oracle diff exists" for Prolog or SNOBOL4. `trace/0` and `&TRACE` both emit goal/statement
events that nobody has normalised onto the four ports yet — the Icon gate is the standing proof it CAN be done,
so the honest cell is **NOT BUILT YET**. § 6's original wording ("where the oracle can trace") was read twice as a
claim about which languages are *capable*; it is a claim about which normalisations someone has *written*.

| language | master (entries · xfail · families) | ladder / rungs | smoke | parser fixtures | vendor suites | trace gate | leaderboard row |
|---|---|---|---|---|---|---|---|
| SNOBOL4 | 1736 · 80 · 389 (THE model) | ✅ construct ladder rungs 0-9, 10 witnesses (`test_snobol4_ladder.sh`, hq_T 2026-09-03), refs oracle-cut from `sbl -bf` | 4-program smoke | ⛔ none | aisnobol, csnobol4_suite, dotnet, gimpel, snoflake (5) | ✅ **BUILT, PINNED** — `test_gate_sno_port_trace.sh` on the shared body, 20 blocks over rungs 0-9, PASS 20/20 both modes, fail-once proven (hq_T 2026-09-04). Self-consistency pin; an oracle diff off `&TRACE` is NOT BUILT YET, not impossible | yes |
| Icon | 534 · 1 · 308 (259 rung-tagged) | ✅ 188 `ladder__rung*` origins across 35 rungs, census in `corpus/tests/icon/config/LADDER.tsv` (seat01 2026-09-03); rung19 BUILT-but-RED, listed honestly | 14/14 | yes (153 ast) | arizona, ipl, jcon-compiler, jcon-ref, jcon_tests (5) | ✅✅ **BUILT, ORACLE DIFF — the strongest of the seven.** `test_gate_icn_port_trace.sh` normalises iconx's `&trace := -1` onto the four Byrd ports. ⛔ Deliberately NOT on `lib_port_trace.sh`: its ref is one oracle-anchored block, not a per-mode pair, and its grain is procedure-level — folding it in would demote it to the weakest common shape | yes |
| Prolog | 404 · 10 · 114 | construct ladder 33 witnesses (rungs 0–8 + 30 legacy rung scripts) | 5-program smoke | yes | gnu_prolog, swi_tests (2) | ✅ **BUILT, PINNED** — `test_gate_pl_port_trace.sh`, 66 blocks; **body extracted to `lib_port_trace.sh` 2026-09-04 (hq_T), output byte-identical across the extraction**. A SELF-CUT regression pin, not an oracle diff | yes |
| Snocone | 273 · 24 · 43 (STALE 08-29) | ✅ 10 rungs 0-9 in `ALL.csv` ⚠️ origins DOUBLED (`ladder__rung00_hello__ladder__rung00_hello`) — see FINDING-2026-09-04-hq_T-snocone-and-rebus-ladder-origins-are-doubled…; grading unaffected | 5-program smoke + 10 parser smokes | ⛔ none | none (the library ports) | ✅ **BUILT, PINNED** — `test_gate_sc_port_trace.sh` on the shared body, 20 blocks over the `ladder` family, PASS both modes over a printed denominator, fail-once proven (hq_T 2026-09-04, SCRIP `2d07f4bab`). Self-consistency pin; an oracle diff off SNOBOL4's `&TRACE` is NOT BUILT YET (Snocone runs on `sbl -bf`, so it shares SNOBOL4's normalisation gap), not impossible | yes |
| Rebus | 48 · 0 · 34 (STALE 08-29) | ✅ census `config/LADDER.tsv` declares 12 rungs from TR 84-9 (top=rung11); rungs 0-5 BUILT 22/22, 6-11 OWED (seat08). ⚠️ origins DOUBLED, same FINDING as Snocone | 4-program smoke | ⛔ none | none | ✅ **BUILT, PINNED** — `test_gate_reb_port_trace.sh` on the shared body, 58 blocks over the `ladder` family, PASS both modes over a printed denominator, fail-once proven (hq_T 2026-09-04, SCRIP `2d07f4bab`). Self-consistency pin; there is NO oracle diff possible — Rebus has no rival implementation at all, so this pin is the only port instrument it can ever have, and that is a fact about the language, not a gap | yes |
| Raku | 139 · 14 · 57 — ✅ **RE-MEASURED 2026-09-03 17:56 hq_T, no longer STALE:** ast 97 entries 83 pass FAIL=0 14 xfail · run 42 entries m3 41/42 · m4 41/42 (one red both modes, `method_sub_for_replace_1`) | ✅ construct ladder rungs 0-9, 10 witnesses (`test_raku_ladder.sh`, seat11 2026-09-03), refs cut from real Rakudo | 724-probe script (a rung suite in disguise) | yes | roast (in `refs/`, scoreboard script) | ✅ **BUILT, PINNED** — `test_gate_raku_port_trace.sh` on the shared body, 20 blocks over the `ladder` family, PASS both modes over a printed denominator, fail-once proven (hq_T 2026-09-04, SCRIP `2d07f4bab`). Self-consistency pin; an oracle diff is a real DESIGN QUESTION, not a missing afternoon — Rakudo's `--tracing` is a MoarVM instruction log, a different grain entirely, with no Byrd-port sequence to normalise | yes |
| Pascal | 159 · 0 · 71 (fresh 2026-09-03, seat10) | ✅ construct ladder rungs 0-9, 10 witnesses (`test_pascal_ladder.sh`, seat10 2026-09-03), refs cut from real `fpc -Miso`; rung 9 honestly RED | ✅ 9/9 both modes (`test_smoke_pascal.sh`, seat10 2026-09-03) | ⛔ none | fpc_tests, p5, ISO 7185 PAT (row) | ✅ **BUILT, PINNED** — `test_gate_pas_port_trace.sh` on the shared body, 24 blocks over the `ladder` family, PASS both modes over a printed denominator, fail-once proven (hq_T 2026-09-04, SCRIP `2d07f4bab`). Self-consistency pin; an oracle diff is close to MEANINGLESS here rather than merely unbuilt — `fpc -Miso` emits no goal-directed trace because Pascal does not backtrack, so the four ports collapse to α/γ on every node | yes |

## THE ROWS (one per gap; the umbrella closes when every cell above reads yes)

`test-suite-consistency-seven-languages-one-standard` (hq_T, rank 0, the program) · `pascal-smoke-floor-gate-and-construct-ladder-from-rung-0` (seat10) · `snobol4-construct-ladder-from-rung-0-with-trace-refs` (seat12) · `snocone-construct-ladder-and-parser-fixtures` (seat12) · `rebus-construct-ladder-parser-fixtures-and-a-real-master` (seat12) · `raku-construct-ladder-from-rung-0` (seat11) · `icon-port-trace-gate-against-ampersand-trace` (seat14) · `snobol4-parser-fixtures-and-port-trace-gate-against-ampersand-trace` (seat12) · `pascal-parser-fixtures-and-the-iso-7185-pat-suite` (seat10). ⚠ The seat numbers in these parentheses predate the 2026-09-03 ~19:30 re-lane into HQ ranges (01–04 hq_B Icon · 05–07 hq_C Prolog · 08–13 hq_P SNOBOL4/Pascal/Snocone/benchmarks · 14–16 hq_T Raku/Rebus); the QUEUE.tsv state column and MASTER-PLAN § THE 16-SEAT CUT are the owners of record. Masters that read STALE are re-measured by the seat that touches the lane (FACT RULE).
