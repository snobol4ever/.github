# ⛔⭐⭐⭐⭐ GOAL-HQ-BEAUTIFY — HEADQUARTERS FOR **CLARITY**

**Opened 2026-08-28 by Lon, in-chat to CEO, verbatim in substance:** *"Could we use one more HQ, maybe complete, perform, and beautify?"* → *"Let's try it."* → *"There is a new /home/claude_B ready for you to populate."* Stood up by ceo the same session under the announcement scope (Lon's own case for the lane: *"the beauty related tasks are all part of the announcement — the src re-org, the template a-z revamp, the consolidation work with one-liners and multi-liners are all beauty oriented"*). Org as of opening: CEO + THREE HQs (`hq_C` correctness · `hq_P` speed · `hq_B` clarity) + FLEET-8.

**Seat root:** `/home/claude_B` · **postoffice identity:** `hq_B` · **twins:** `GOAL-HQ-COMPLETE.md` (`/home/claude_C`, `hq_C`), `GOAL-HQ-PERFORM.md` (`/home/claude_P`, `hq_P`)

## LIVE CURSOR

**B-13 (2026-09-04, MODE CEO — the root digest `/home/claude_B/CLAUDE.md` re-verified line-by-line against a freshly pulled tree; PARKED CLEAN, nothing in flight).** Lon invoked `/init` on this root. The digest is not git-tracked, so this is a hand-verified pass; every claim below was measured, not remembered. **Nine defects found and cured in place:**

1. **The mode was RESTATED in the banner** (`MODE → QUARTET`, written 2026-09-03 17:20) and the mode changed **six times** underneath it — CEO → FLEET-16 → QUARTET → FLEET-4 → FLEET-8 → CEO. Replaced with a pointer plus the one durable part, the stand-down protocol. This is the third time a restated mode has gone stale in this file's history and the first time the restatement has been *removed* rather than corrected.
2. **The MODE value set was missing `QUARTET` and still spelled `DUO`**, renamed `DUET` on 2026-09-03 ~17:45. ⛔ Missing-a-value and spelling-a-retired-one are not symmetric: a reader matching `DUO` matches nothing the file can ever contain.
3. **`RULES.md § THE TWO MODES` greps to ZERO hits** — the heading is `§ THE MODE`. Cited twice.
4. **`RULES.md:118` cited three times is the COMMIT-IDENTITY rule**; the pristine loosening is at `:120`. All three re-pointed to the heading name.
5. **`Makefile:34` for `RT_OPT` is `:43` today — and the Makefile's OWN comment still says "DEFINED ONCE, AT LINE 34".** Both citations drifted identically. Replaced with `grep -n '^RT_OPT' Makefile`, and kept as the file's worked example of why a line number is the one citation form guaranteed to rot.
6. **`make test` "runs the first four" understated the recipe by four times over** — it has grown a band of cheap no-build arms ahead of the boards, and **two arms are `-`-prefixed = REPORTED-NOT-BLOCKING**. Replaced the count with the command, and added the leading-`-` reading rule, which is what separates a gate from a report in a green run.
7. **`corpus/crosscheck/`, `corpus/probe/`, `corpus/generated/` ARE GONE, and `demo/` is `demos/`** — the digest devoted a full navigation paragraph to `crosscheck/`. ⛔ A retired path is worse than a missing one: `find corpus/crosscheck -name '*.sno'` prints nothing and **exits 0**, so the tree reads *present and empty* rather than *absent*. The reusable half of the old lesson (census by extension, never by the one you had in mind) is kept; the dead navigation is deleted.
8. **THE ONE LEADERBOARD was entirely absent.** Lon's FACT RULE — every suite run by any session rewrites its `.github/SCORE.md` row — plus the helper, the do-not-regenerate warning (4-column generator vs 6-column board, spliced by position = provenance deleted), and the three `make test` arms that police it.
9. **THERE IS NO XFAIL was entirely absent** (Lon 2026-09-03 21:30).

⛔⭐⭐ **THE FINDING WORTH MORE THAN THE NINE FIXES: THE GATE THAT POLICES ROOT DIGESTS DOES NOT READ THIS ONE.** `test_gate_digest_matches_rules.sh` hard-codes `ROOTS` = `claude01`…`claude16`, `claude_C`, `claude_P`, `claude`. **`/home/claude_B` and `/home/claude_T` are absent** — both roots were opened after the gate was written (hq_B 2026-08-28, hq_T 2026-09-03; gate mtime 2026-08-28 14:54). So **the two HQs whose lanes are hygiene and tests are the two whose digests nothing reads**, and the gate has been green here the whole time *about nineteen other files*. ⭐ Same narrow-instrument family as `command -v` and `$?`-after-a-pipe, which this very digest documents: the gate is correct, and it answers a question about a population that does not include you. Verified rc=0 on this root by hand via `DIGEST_GATE_ROOTS=/home/claude_B/CLAUDE.md`. **Row for the next flip: add both roots to `ROOTS`** — one-line change, and until it lands the freshness of two digests is a hand-verified property.

⚠ **REPORTED, NOT CLAIMED (hq_T's lane, leaderboard):** `test_gate_score_tables_agree.sh` rc=1 on a fresh tree — **three** same-denominator conflicts, not the two hq_T flagged: `icon 38/81 vs 41/81` (denominator **81/JCON**, not the 89/Arizona pair they cited — that one now agrees, so a different cell opened), `pascal 126/181 vs 124/181` (as flagged, not mine), and **`raku 924/986 vs grid 4/986`, new and by far the loudest — 4/986 is not a plausible measurement**. Plus 19 one-sided populations from the dual-write gap. Telegrammed to hq_T.

**TREE:** SCRIP `4c7253e99` · corpus `c2c7d8396` · .github `86cbe5e6` (all three pulled `--ff-only` at session start; all three were behind). **NEXT:** the `ROOTS` one-liner, then the `marker-must-name-its-owner` RULES line hq_P offered to co-sign (wording parked in that telegram). **NOTHING IN FLIGHT — no claim held, no partial edit anywhere.**


**B-12 (2026-09-03, MODE FLEET-16 — row `postoffice-gates-red-on-origin-because-no-s4e-gate-is-in-make-test` CLOSED; SCRIP `05fee14f` base):** Three postoffice gates were RED ON ORIGIN and invisible because **no `s4e_*` gate was in any runner**. All three cured, and per ceo ruling a `make test-postoffice` target (9 hermetic gates, ~13-22s) is now `make test`'s SECOND arm after `strip_comments --check`. `test_gate_s4e_picker_v2` **19/19**, `test_gate_picker_autounblock` **6/6**, `test_gate_dispatch_bus_failure_modes` **7/7**; all three still pass `--self-check`, so each can still say NO. Fail-once: a planted fixture red fails `make test` **rc=2 in 7s**, naming the gate.

⛔⭐ **THE FINDING WORTH THE ROW: `picker_v2` READ 18/19, AND ITS HEADLINE PROPERTY WAS MEASURING NOTHING.** Every sandbox row was being skipped, and P1's two "passing" checks were matching text inside the **refusal banner** — `↩ skipped 4 free row(s) ... (topmost: rank 0  THE-RANK-ZERO-ROW  (owner brief-0))` satisfies both `*"THE-RANK-ZERO-ROW"*` and `*"brief-0"*`. **An assertion whose substring the failure output can also contain is a coincidence, not a measurement.** Refusal messages quote the thing they refuse, so the more informative the error, the more likely it satisfies a lazy assertion. The one check that named a row the banner does not mention is the only one that told the truth — and it is what got this row minted. All assertions are now anchored on the verdict word (`LOCKED <topic>`), not a bare identifier. Same family as `$?`-after-a-pipeline: the instrument answered a narrower question and never said so.

⭐ **ONE OF MY OWN MINTED DIAGNOSES WAS WRONG, AND THE WAY IT WAS WRONG IS THE LESSON.** I minted this row blaming the autounblock reds on the scratch postoffice having no `MODE` file. Real, now fixed — and **not the cause**: U1-U3 print the identical `⛔ MODE FILE ABSENT` banner and pass. It was merely the *first line of output*, so `head -1` planted it in the "actual:" slot of every failure report. The actual cause was the owner column, same as the other two gates. **A loud, correct error banner sitting above the real failure is camouflage** — read the assertion, not the top of the buffer.

⭐ **CURING A FIXTURE CAN TURN A GREEN CHECK RED, AND THAT IS THE FIXTURE WORKING.** `autounblock` U3 asserted the state column reads `FREE` after the row is served. `FREE` was only ever observable *because the row was skipped* — the park wrote it and nothing claimed it. A row genuinely served reads `CLAIMED:seatAA`. U3 now demands the stale `BLOCKED-ON:` spelling be gone **and** the column agree with the claim (s265), which is strictly stronger than what it replaced. ⛔ The tool was right in all three gates; **the cure is always to bring the fixture up to the tool's contract, never to relax the tool** — relaxing `done` to close a batonless row would have re-opened LAW 1 for all sixteen seats to spare one fixture.

⛔ **HERMETIC IS A MEASURED PROPERTY, NOT A NAME.** Membership in `test-postoffice` was decided by running the set and proving `/home/resources/postoffice` byte-identical afterwards (QUEUE.tsv, QUEUE.done.tsv, `claims/`, `tasks/`). These gates call `claim`/`done`/`assign`; one that leaked to the live postoffice would corrupt the fleet from inside `make test`. The six live-reading gates are deliberately OUT, with `preflight_complete`, per ceo.

⛔ **A RUNNER THAT SAYS A GATE FAILED BUT NOT WHICH GATE CONVERTS A RED INTO A SEARCH.** My first target used `@bash …`; the planted red printed `⛔ GATE FAIL: 1 of 9` with **zero occurrences of the failing script's name** — nine candidates, no pointer. Dropped the `@` (which also disagreed with `test:`'s own unprefixed style) so make echoes each gate and the last echoed line names the failure.

⛔ **STILL OPEN, NOT MINE TODAY:** four gates that read the LIVE postoffice are red on origin — `baton_donewhen_runnable{,_live}`, `baton_state_header_single_record`, `queue_is_an_index`. They grade rows sixteen seats are editing, so a red there may be a live-state fact rather than a defect. Worth a row to separate the two populations; **do not wire them into `make test` first and find out.**

⛔ **EXACT NEXT STEP:** rung 13 (unchanged from B-11), or take the live-postoffice-gates row above.

**B-11 (2026-09-03, MODE FLEET-12 — row `picker-skips-a-row-owned-by-another-seat-unless-that-seat-picks` CLOSED; SCRIP `a79c2af7`):** `next` PASS 3 now skips a FREE row whose owner names another seat. Serving is unchanged when the owner is the picker, `unassigned`, or empty; PASS 1 (HQ dispatch) and PASS 2 (own unfinished work) untouched; `assign` still moves ownership and `claim` is still the deliberate override. Gate `test_gate_s4e_next_honours_owner.sh`, 8 checks, hermetic — **8/8 green, 4/8 red pre-cure**, and the red reproduces the original defect in its own words.

⭐ **WHY SKIP IS THE RIGHT DEFAULT — THE COST IS ASYMMETRIC.** A wrongly-served row puts two seats on one piece of work and, because a claim **hides** the row from its owner's own picker, locks the owner out *silently*. A wrongly-skipped row costs one `claim` typed on purpose. **The picker cannot tell an idle owner from a busy one, so it must not guess — and when it must, it should guess in the direction that is cheap to undo.**

⛔ **MY OWN DISPATCH-PRESERVATION ARM FAILED FIRST, AND THE ARM WAS WRONG, NOT THE CHANGE.** I modelled HQ dispatch as a QUEUE state column; it actually lives in the claim file (first line the owning seat, then `ASSIGNED-BY <seat>`). Running the failing arm against the **pre-cure** picker showed it failing identically — one command, and it settled it. ⭐ **A control that only ever runs against the cured build cannot tell "I broke this" from "this never worked that way."** Third time today a control, not a board, is what caught me.

⭐ **The skip REPORTS ONCE** — count plus topmost row, on both the serve and queue-empty paths. Not per row (18 of 178 FREE rows carry an owner), never silent: a skip nobody can see is indistinguishable from the row not existing, which is the failure this picker has now been fixed for **three times** (file-order picking, decorative state column, this).

⛔ **RISK ON RECORD, not a defect today:** a FREE row owned by a seat that no longer exists becomes unpickable except by explicit `claim`. All four owners on FREE rows have live mailboxes now; **this bites on a mode change** — and the modes have moved TRIO → FLEET-8 → FLEET-12 in one sitting. Cure if it happens is `assign <topic> unassigned` per row, not a revert.

**Routed masters disposed by ceo as reasoned:** raku resort → seat07; snobol4 resort → PARKED-AWAITING a fleet-quiet boundary plus explicit go, because its board is the blocking arm of `make test` for every seat and it lands like an oracle swap. **Icon 530/534 is now the number Lon reads**, and seats 01/02/03 are told to grade with `--by-modes-column`.

⛔ **EXACT NEXT STEP:** rung 13. Ask targets under FLEET-12: seat01, seat02, seat03, seat08, seat11.

**B-10 (2026-09-03, MODE FLEET-8 — two rows CLOSED: the Icon board and the master resort; SCRIP `668b308b`+`1bcfba40`, corpus `353cd537`):**

**Icon board now grades each entry the way its `modes` column says.** 153 of 534 entries are parser fixtures whose `.ref` is a `--dump-ast` dump, and the runner was *executing* them. Measured: old (all run-graded) m3/m4 377 PASS / 141 FAIL / 13 CRASH / 2 HANG → new **ast-graded 153/153 PASS, run-graded 377/381 both modes, 3 FAIL, ZERO crashes, ZERO hangs.** Honest total **530/534**. ⭐ **Every crash and hang on the old board was a parser fixture being run.** Two populations, two denominators, never summed.

⭐ **THE SHARPEST EVIDENCE THE OLD NUMBER MEASURED NOTHING WASN'T AN ARGUMENT ABOUT DENOMINATORS — IT WAS THE DIRECTION IT MOVED.** The row was minted at 398/534; on today's tree the *same* instrument reads 377/534, because ceo's re-cut of 30 stale AST pins gave those fixtures **correct** dumps, which match run output even less. **An instrument that gets worse as its subject gets better is not miscalibrated; it is measuring something else.** I re-measured rather than quoting either of the brief's two numbers.

**Master resort:** ceo ruled my routed question answer (1) — a promotion re-sorts. `--resort` landed and the Prolog master is back in the builder's order (261 of 404 positions moved, **bodies byte-identical**, ref/stdin/want_rc/xfail_reason unchanged, diff symmetric 261/261 · 700/700 · 463/463, zero net lines). `master_sort_key()` extracted so the gate **imports** the rule instead of re-typing it.

⛔ **I ALMOST SHIPPED A WRONG NUMBER TWICE IN ONE ROW, AND BOTH TIMES A CONTROL SAVED IT.** (1) The order gate first claimed 403 of 404 prolog entries out of order against my earlier measured 265 — `COLS` is per-language and `main()` rebinds it as a *global*, so importing the module left the SNOBOL4 table bound and scored prolog on the wrong features. **I only caught it because I had a prior number to contradict it; a first-ever measurement would have been believed.** (2) The post-resort board read 221/404 against my remembered 209 — I nearly reported the resort as having moved the board, when the tree had simply moved under me. Took the before-arm by stashing: **221 = 221, identical.** ⭐ An absolute number cannot tell a permutation from progress.

⛔ **ROUTED, NOT LANDED (FLEET-8 — a queue row is a real handoff again):** `resort-the-raku-master-into-the-builders-order` (125/129 out of order) and `resort-the-snobol4-master-into-the-builders-order` (1639/1726). The snobol4 one is deliberately not mine to land unilaterally — its board is the blocking arm of `make test` for every seat on the box. Finishing step for whoever lands the last of the three: drop the `LANGS=` scope and put the **unscoped** order gate in `make test`, so the law is enforced rather than measured.

⛔ **MY COMMENT BROKE ORIGIN'S GATE FOR EVERY SEAT** (`92d300f0`, 665 chars in `src/`); hq_C caught and fixed it. **Tell: if a comment carries an ARGUMENT rather than a separator, it belongs in a FINDING — in `src/` that is not taste, it is the gate.**

⛔ **EXACT NEXT STEP:** `picker-skips-a-row-owned-by-another-seat-unless-that-seat-picks` (ceo ruled the owner column constrains the pick; my own release of hq_P's rank-0 row is the witness), then rung 13.

**B-9 (2026-09-03 TRIO — row `master-builder-needs-a-csv-only-reindex-path` CLOSED; SCRIP `4f847224`):** `util_build_master_suite.py --reindex` recomputes every `ALL.csv` column from the master already on disk, writes **only** that file, absorbs nothing and reorders nothing. Refuses rc=2 on an unacknowledged loose pair and rc=2 beside any absorption flag. **Oracle met: byte-identical to the hand-edited CSV of `3196897d`/`2b71e9a2`, 404 entries** — which retroactively validates that hand-edit on the `rank` column my original scratch check never compared. Gate `test_gate_master_builder_reindex_only.sh`, 13 checks, hermetic; 13/13 green, 5/11 red pre-cure.

⭐ **THE ARM THAT EARNS ITS PLACE:** (b) corrupt one derived cell, re-index, watch it come back. Without it the byte-identity arm passes against an implementation that merely **copies** the file — the exact failure a round-trip test invites. **Identity is never proof of computation.**

⛔ **AND THE BIGGER THING I FOUND UNDERNEATH IT, ROUTED NOT FIXED:** `rank` and file order are derived from `(xfail, features, lines, name)` — green before xfail, so a level is a prefix. **Flipping an xfail changes an entry's sort key**, so after my seven promotions the committed order and the builder's diverge for **265 of 404** entries. Nothing is *inconsistent* — `ALL.pl` and `ALL.csv` agree with each other — but the master no longer satisfies the ordering law it was built under, and a level-prefix runner would silently pick a set that is not greenest-first. Two defensible cures (a promotion re-sorts, or rank is position and the docs stop claiming the prefix property); it is the ceo's call. FINDING filed.

⭐ **The shape, and it is mine:** the promotion gate I wrote yesterday checks the XFAIL marker agrees in all three places, and it does — the suite drifted anyway, because **the marker and the ORDER are two different derived things and I guarded only the one the row named.**

⛔ **A COMMENT I WROTE BROKE ORIGIN'S GATE FOR EVERY SEAT.** `92d300f0` left a 665-char single-line comment in `src/lower/lower_prolog.c`; `src/` carries zero comments but the 200-char separators, and the line max is 200, so `strip_comments.py --check` went rc=1 on origin — and that check is the fourth clause of every Prolog rung's DONE-WHEN and an arm of `make test`. hq_C found it via rung 4's DONE-WHEN on the merged tree and fixed it; the deletion itself stands. ⭐ **The reusable part is not "remember the style rule":** a long explanatory comment is the *natural* way to make a deletion legible, and this codebase has deliberately closed that door — explanation goes to the FINDING, enforcement to a named gate, so source cannot drift from either. I named the gate *inside* the comment, i.e. wrote the durable half and the rotting half in one breath. **Tell: if a comment carries an ARGUMENT rather than a separator, it belongs in a FINDING — in `src/` that is not taste, it is the gate.**

⭐ **CRLF, from hq_C:** `ALL.csv` is CRLF; Python's universal-newline read+write silently rewrites it to LF — invisible to git's text diff and to `file`, and it turns a one-cell edit into a whole-file conflict (401 lines for one flag, measured on rung 3). `newline=''` on **both** read and write; confirm with `git diff --numstat` reading `1 1`. Mine were clean (405/405) and `--reindex` now asserts it.

⛔ **EXACT NEXT STEP:** ceo has assigned `board-icon-master-runs-the-ast-graded-parser-fixtures-and-counts-their-inevitable-reds`. Then rung 13, B-5's four class re-parks, B-4.

**B-8 (2026-09-02 TRIO — ceo CEO-152 executed as a pair; SCRIP `92d300f0` + corpus `2b71e9a2`):** The synthetic-`main` fallback is DELETED — SCRIP runs exactly what `swipl -q -g halt` runs and synthesizes nothing. Seven stale XFAIL markers promoted in all three places; `ALL.wantrc` emptied of four pins. Board **198/198 → 198/198 after the deletion (nothing moved) → 209/209** after the promotions and the pin removal, xpass 7 → 0; `make test` rc=0. Three new gates, each proven in both directions: `test_gate_pl_no_synthetic_main.sh` (2/10 red pre-cure → 10/10), `test_gate_pl_xfail_marker_consistent.sh` (fail-once by half-promoting one entry), `test_gate_pl_master_board_floor.sh` (pinned at the PRE-cure 198/198 on purpose — a floor raised to the post-cure number in the same commit can no longer say "the cure did not cost the board").

⭐ **RECONCILIATION, and the shape it teaches:** hq_C counted FIVE directive-less entries, I counted 59, and **neither was wrong**. Five is what the *board could see* (they compiled, so the divergence surfaced); 59 is what was *there* (the rest still refuse to compile and reach no board). ⛔ **A census taken through an instrument reports the instrument's reach, not the population** — and the two numbers only look like a contradiction if you forget which one you asked.

⛔ **I REPORTED BLAST RADIUS THAT DID NOT EXIST, AND THE CEO WAS RIGHT.** Post-deletion I measured six loose rung files printing nothing against non-empty `.expected` and called ceo's *"nothing outside the master moves"* incomplete. They were already doing that — the ladder refuses `retract`/`clause`/`$bagof`. **I had run only the AFTER arm.** Re-running the ORIGINAL files against the SAME binary produced identical empty output and the same refusal lines, which isolates file content from compiler and clears the deletion. ⭐ **A one-armed measurement cannot tell "my change did this" from "this was already so", and the missing arm is always the cheap one.** Second time this session I published a number before its control.

⭐ **AND THE SAME DEFECT TWICE IN MY OWN SHELL WITHIN THE HOUR:** `bash runner | tail -5; echo "rc=$?"` printed **`tail`'s** status — the trap the digest documents — inside the receipt for a row about instruments answering the wrong question. Then `pkill -f test_corpus_snobol4` **matched its own command line and killed itself**, and `pgrep -f` reported "still running" for the same reason, so I killed a job that no longer existed. ⛔ `pgrep -f` answers *"does any command line contain this string"*, never *"is that job running"*, and the wrong answer has the right shape. Capture first, then test; for process patterns, exclude the searcher.

⛔ **EXACT NEXT STEP (ceo's order):** `master-builder-needs-a-csv-only-reindex-path` (rank 2, minted from my gap report — `util_build_master_suite.py` can only reindex by also ABSORBING, 404→408 on this tree, so any promotion touching program text must hand-edit `ALL.csv` or absorb whatever is loose that day). Then rung 13, B-5's four class re-parks, B-4. `simple_program_103` is NOT mine — routed by ceo to rung 9 as a named witness (`atom_to_term/3` `(-,+,+)` must RAISE like swipl; no hotfix before the error path exists).

**B-7 (2026-09-02 TRIO — ceo rulings (a)–(d) executed; corpus `3196897d`, SCRIP `c9b9e144`):** The 59 unproducible Prolog master refs are CURED in one board-proven commit: 55 take `:- initialization(main).`, `simple_program_97` re-pins to swipl's `1024/1024/1/0.5` (the last `*power*` entry), `simple_program_103` re-cuts to its two real lines, `functor_2` and `copy_term_ite_list_replace_1` gain `numbervars/3` before the print so their output stops varying between runs. The recipe was NOT touched (adding `-g main` double-runs the 203 that already carry the directive). Oracle reproducibility over the 272 non-empty refs: **199 → 254 → 258**, +59 exactly. Board **unchanged at m3 198 / m4 198 of 404**, per-entry diff showing exactly two movements. Earlier this session: the stale-binary preflight row closed on its computed DONE-WHEN (`c9b9e144`, gate 13/13 green, 7/13 red pre-cure).

⭐ **THE ONE LESSON — A VACUOUS COMPARISON SCORES AS A PASS, AND MY CONTROL WAS THE THING THAT HAD IT.** My first whole-master control read **332 → 387**. Both were inflated by ~132: the sweep tested `[ -f "$ref" ]` where it needed `[ -s "$ref" ]`, so every entry with an EMPTY ref matched an empty output and scored as "reproduces". ⛔ The +55 delta survived the bug *because the inflation was constant across both arms* — which is exactly why nothing looked wrong. The org already guards this one layer up (`corpus_suite_harness.py:1316-1326` refuses to MINT an empty ref, "every arm agrees, and what they agree on is NOTHING"); nothing stopped my MEASUREMENT from counting empty-vs-empty as agreement. Same defect, two layers, paid for twice. ⛔ And a second, same sitting: the classifier misread `ite_9/10/11` because it ran the oracle **without closing stdin** and those three call `read/1` — 52 vs 55 from one tree on two runs. Every oracle call in the final measurement redirects `</dev/null`.

⭐ **THE RESULT WORTH REMEMBERING:** `simple_program_103` went PASS → FAIL, **and it was green only because its ref was wrong.** SCRIP implements the gprolog-permissive `atom_to_term/3` and prints a third line `bar(x)`; swipl 9.0.4 raises. The ref recorded SCRIP's own behaviour, so the entry could not have gone red whatever SCRIP did — a test graded against its own subject. Routed to `hq_C`; the board did not get worse, it got honest.

⛔ **EXACT NEXT STEP:** rung 13, then B-5's four `prolog-rung-red-class-*` re-parks, then B-4 (`test_parser_snocone.sh` SKIP-rc=0 → REFUSE rc=2 or retire; `pascal.y` `selector_list`). Do NOT cut `ladder__rung06_stream_*` — already absorbed by ceo (404 entries). `ALL.csv` is still only regenerable by a builder that also absorbs; a CSV-only rebuild path is unminted and would have saved a surgical edit here.

**B-6 (2026-09-02 TRIO — WRAP on Lon's order, relayed by ceo 18:25 CDT: *"Wrap it up now. All HQ's are finished."*):** Rung 6 is ON ORIGIN (ceo: SCRIP `943c1b8c`+`81b40ceb` on hq_C's rung 2 `2fc5ce73`, corpus `1f60f815`, REPORTED master board **186/400 both modes** from 50/383 this morning). This seat's rung-6 work was received: corpus `62dc7995` (witness (d) re-cut without `sub_atom/5`, a rung-7 generator; two of the three `*power*` refs re-pinned to swipl), `ab53ffc6` (rungs 7–12 witnesses), `100db9e3` (trace refs 0..2 re-cut). All three repos SYNCED at wrap; **all three were BEHIND at session start** — `merge --ff-only` before trusting anything, every time.

⭐ **THE SESSION'S ONE LESSON — A RULING IS A MEASUREMENT WITH A SAMPLE SIZE, AND THE SAMPLE SIZE IS USUALLY 1.** The ceo ruled that `simple_program_97` is "a ref the oracle recipe cannot produce" and routed the re-cut here. The mechanism was right; the population was wrong by 59x, **and the entry was in the wrong class** — re-cutting it to empty as ruled would have destroyed a correct ref. Measured: the stated recipe is `swipl -q -g halt` (`corpus_suite_harness.py:181`, read from the code, not the docstring); **59 of 400** master entries define `main`, are never called by it, and so produce empty output rc 0 while carrying a non-empty ref; **55 reproduce their ref byte-exactly** once `-g main` is added. `simple_program_97` is not one of the 55 — it is the **third `*power*` entry**, a ruling-(1) float pin (`1024.0/1.0` vs swipl's `1024/1`), sibling to the two already re-pinned in `62dc7995`. ⛔ **And the obvious cure is the wrong one:** adding `-g main` to the recipe DOUBLE-RUNS the 203 entries that carry `:- initialization(main).` (measured: `hello` twice). The cure is the directive on the 55 — which ruling (2) already authorises, *"where the family's siblings carry it"*, and 203 siblings carry it. FINDING: `FINDING-2026-09-02-hq_B-fifty-five-prolog-master-refs-encode-a-run-main-step-the-stated-oracle-recipe-omits-and-four-more-are-gprolog-era-not-just-the-one-entry-ruled.md`. Sent to ceo as `override-`-class correction of a ruling in flight.

⭐ **Why it sat unseen:** `corpus_suite_harness.py:1316-1326` already carries seat05's guard for this exact signature and REFUSES to mint an empty ref. The guard is correct and forward-only — it stops the 60th, it cannot see the 59 already committed. **A guard against minting a defect is not a census of the defect already minted.**

⛔ **HANDOFF ARTIFACT VERDICT — I CALLED IT A FALSE POSITIVE AND IT WAS NOT; THE VERIFIER WAS RIGHT AND MY BUILD WAS STALE.** `handoff_status.sh` blocked the wrap: `util_verify_s_artifacts_owed.sh` rc=1, *"VERDICT: OWED — 26 item(s)"*, all prolog_bench. The real tree had no stale pairs (5 `.s` + 18 `.s.REFUSED` = 23 `.pl`, one artifact each) and the regen scripts reported "already current" with a 0-file corpus diff — which looked like an instrument defect. It was not. ⭐ **The verifier dry-run-regenerates with THE BINARY IN YOUR TREE**, and mine was `./scrip` 17:32, built before rung 6 landed at 17:49; the `.s.REFUSED` marker text embeds *"rung N lands it"*, so a pre-rung-6 binary genuinely owes different markers. After `make pristine` at rung-6 HEAD the same verifier returns **`S-ARTIFACTS-OWED-TOTAL: 0` · `VERDICT: CLEAN` · rc=0, all four checks actually ran.** The debt was real, its cause was my build, and the cure was the rebuild — not a regen and not a fix to the instrument. ⛔ **The law already covered this and I ran the check before obeying it:** HQ-27 PRISTINE-BUILD-BEFORE-VERDICT. A verdict instrument pointed at a stale binary manufactures phantom debt that looks exactly like a lying gate, and the first move is to rebuild, never to doubt the gate.

⛔ **EXACT NEXT STEP (in order):** (1) the 55 `:- initialization(main).` additions, one commit, board-proven in the same commit per INTERIM PROMOTION PROTOCOL; (2) re-pin `146_simple_program_97` to `1024/1024/1/0.5` under ruling (1) — the last `*power*` entry; (3) route `145_simple_program_103`, `239_functor_2`, `344_copy_term_ite_list_replace_1` to ceo for a ruling — three refs NO swipl flag set can produce, two of them address-nondeterministic (`_G0` vs `_5200`, varies per run). Then the ceo's named picks: **rung 13**, then B-5's four `prolog-rung-red-class-*` re-parks, then B-4 (`test_parser_snocone.sh` SKIP-rc=0 → REFUSE rc=2 or retire; `pascal.y` `selector_list`).

**B-5 (2026-09-02 TRIO, wrap-up on Lon's ~17:25 call — row `prolog-rung-suite-reds-rowed-by-class` (ladder C3) DONE, DONE-WHEN rc=0 verbatim):** post-cut the Prolog rung suite is **0/15 both modes** (SCRIP `7432838a`, corpus `542de174`; measured on `c182977e`, re-proven after the rebase), every red a driver `pl_refuse()` naming its construct and rung. The suite now needs rc=0 for a PASS (the three `rung15_abolish_*` greens were refusals matching an EMPTY expected) and prints `REFUSED-LADDER rung N -- <construct>` per red, so the histogram IS the classification. The 15 classed by HIGHEST construct into four `prolog-rung-red-class-*` rows (rungs 6/8/9/10 = 1+5+1+8 witnesses) with computable DONE-WHENs (watched to FAIL rc=1), PARKED-UMBRELLA like the ceo's 28 siblings; witness names added to ARCH § E rows 6/8/9/10. Corpus: 11 orphan `.expected` deleted (programs in the master since `c7f86c08`); `rung22` re-pinned to swipl `[a,b]`. Reported: ladder rung 0 PASS 2/2, rungs 1–5 FAIL 22/22 (rung 1 in flight at hq_C); `nm -D` arm 0. Debt seen, not touched: `test_gate_pl_coupling.sh:48` and `test_prolog_rung30.sh:44` still point at `.pl` files that moved into the master. ⛔ **EXACT NEXT STEP:** when ceo mints the rung 6/8/9/10 rows, re-park the four class rows `BLOCKED-ON:<rung row>` so they self-clear; then the B-4 step (`test_parser_snocone.sh` SKIP-rc=0 → REFUSE rc=2 or retire; `pascal.y` `selector_list`).

**B-4 (2026-09-02 — ceo standup `oracles-and-generated-parsers-standup`, four items, ALL LANDED at SCRIP `e01327e4` + `a29ea1fd`; wrap-up on Lon's checkpoint call):**
(1) both style200 oracles cured — flags from the Makefile via new `scripts/lib_build_flags.sh`, `-d -r` + every non-debug section, own-basename compile, real `X.tab.c` generation, zero denominator REFUSES rc=2; R5 re-proven **78/78** (C, vs `46db4457`) and **9 of 9 measured** (Y/L). (2) `rebus.y` include fixed; all 14 generated outputs regenerate from source again — two had been HAND-PRUNED in June (`lex.rebus.c` by `a98a7d24`, `snocone_parse.tab.c` by `b9726d7b`), cured at the source (`%option noinput nounput`; three dead helpers out of `snocone_parse.y`); 266/267 objects byte-identical to the `922cfaf4` pristine build, `lex.rebus.o` 24/24 functions identical + 18 flex API functions its siblings already export; rebus 4/4 · fixtures 15/15 · snocone 5/5 · fixtures 67/67. (3) flex-aware `.l` strip landed, proven by round trip (4/4) and injection round trip (4/4). (4) rung 13: `Term` 0, `resolve_choice` 0, clause 2 now in `test_gate_term_wordref_ratchet.sh`.
⭐ **The session's one lesson:** an oracle proves only the comparison it makes — R5's regenerated-vs-regenerated could not see that two committed artifacts matched NO regeneration. And every one of the four holes behind the stale `-I` list (no `-r`, `-j` blind to `.data.rel.*`, `before.cpp`'s `_GLOBAL__sub_I_` symbol, `out.tab.c` vs the grammar's own `#include`) was found by running the instrument on a case whose answer was already known.
⛔ **EXACT NEXT STEP:** `scripts/test_parser_snocone.sh` — `SKIP scrip not found: …/scripts/scrip`, rc=0, fixtures dir empty: make it REFUSE rc=2 or retire it (RULES.md: a test that cannot measure refuses). Then `pascal.y`'s useless nonterminal `selector_list` (bison `-Wother`), proven by the Y/L oracle. The parked row `prolog-term-descr-s7-dead-resolution-env-layer-deleted` stays PARKED-AWAITING (rung 2 is BLOCKED-ON PZ-4, hq_C). FINDING: `FINDING-2026-09-02-hq_B-two-generated-parsers-were-hand-pruned-and-both-style200-oracles-graded-zero-files-while-printing-OK.md`.

**B-2 (2026-09-01 — row `bench-grids-rebase-to-two-number-basis`: RAKU CLOCK HOOK + TRIANGULATOR LANDED, grid re-based; pz4 parked on the row that carries its blocker; three instrument defects reported by seats cured the same sitting):**
Mode moved TRIO → FLEET-8 → FLEET-16 while this session ran (read from MODE each time). ceo's switch ruling executed: pz4 is
`BLOCKED-ON:calling-convention-depth-tracked` — `park` REFUSED the mechanism name `host-rbp-promotion` as a blocker by the
dangling-blocker guard this seat minted with pz4 as its own example, so the block self-clears off hq_P's DONE instead of
never. Landed: SCRIP `1b40ea1a` + corpus `b5864143` (pushed; the two halves shipped together on purpose — SCRIP hooks without the corpus kernels would have served nothing). `wall_us()`/`wall_ms()` for Raku beside the Prolog pair; `note(...)` (a real frontend gap, guarded
against the four corpus programs that define their own `note`); `prelude_rakudo.rakumod` loaded by `-M` from a staged dir
(Rakudo writes `.precomp/` beside a `-I.` module — it wrote one into the corpus on the first hand run); four kernels
self-timed and byte-verified on m3, m4 and Rakudo; `bench_triangulate_raku.sh` (angle 3, every rep verified, clock and unit
invariants, angles 1+2 REFUSED per cell — coverage gate stays red for raku, correctly); README grid rendered FROM the TSV.

⭐ **THE SESSION'S ONE LESSON: THE BASIS IS THE STORY.** The totals grid said string-escape 55.9x; ~99% of Rakudo's total was
process startup. On work, SCRIP is ~25x ahead there, ~7x on send-more-money, and *further behind* on both point_class kernels
than the totals grid showed — the same constant padded Rakudo's denominator on the slow side. Nothing regressed; the numbers
moved because the question did. Same shape as the Prolog inversion two days earlier.

⛔ **THREE TIMES THIS SESSION AN INSTRUMENT THAT LOOKED WIRED COULD NOT FIRE**, all mine: the banner-side hook installer
placed after a line that always exits; its first draft referencing an undefined `$HERE`; a `rm` in a drifted cwd whose `ls`
check reported clean. Each caught by *falsifying* (delete the hook, run the banner, is it back?) rather than by reading. The
census that motivated the installer: **16 of 19 roots wire only `Stop`** — the commit-hook self-install never fired on any
fleet seat, and the "rejected in every clone" claim was true in three roots. seat04 measured one seat; the number is the fleet.

**ALSO THIS SITTING, UNDER FLEET-16 MAIL:** rank-0 `park-marks-last-row-only-when-clearing-own-claim` (ladder I rung I7) — the
cure was already on the own-claim branch; its gate `test_gate_s4e_release_verbs_mark_last_row.sh` runs the four verbs against a
SCRATCH postoffice (`S4E_POST`/`S4E_SEAT`) and goes red with the mark deleted; row DONE-WHEN rc=0 verbatim. Rung I3
`score-md-master-board-row-every-language` minted and claimed: `util_build_score_md.py` gained a MASTERS table and a fourth column
(the harness's own `run ALL.<ext> ALL.ref --modes m3,m4`, per mode, never summed). Three seat questions answered without a stall
(seat10 s5 representation — interim that hq_C then made the ruling; seat12 unbuilt sources — mint one row for the two; seat11 —
seats mint gates, with the two-part proof). ⛔ **ONE REGRESSION OF MINE, CAUGHT BY THE SMOKE BEFORE ANY PUSH:** I deleted six
`IR_OP_COUNT` guards from the driver's Raku emittability gate as "dead"; `rk_excise` builds live nodes with that op, so two smoke
programs went from REFUSED to SIGABRT. Guard restored and named; tombstone claim retracted everywhere it was written; the machine
fact that the COUNT sentinel doubles as an op is the re-scoped row. And the harness's 10-minute cap killed two verdict chains
before I detached them — recorded for every seat in the FINDING.

**ROUTED, NOT MINE THIS SITTING:** `driver-emittability-predicates-sentinel-tombstones` (RE-SCOPED after a same-night retraction: `IR_OP_COUNT`
is a LIVE op — the excised node `rk_excise` builds — so the defect is the COUNT sentinel doubling as an op; name it `IR_EXCISED`. My deletion of
its guards regressed two Raku smoke programs from REFUSED to SIGABRT; the smoke caught it, the guard is back, named);
`raku-bench-angles-1-and-2-fixed-iter-instrument` (the cross-proof half). ceo's two new rows in this lane
(`make-pristine-per-root-flock-second-builder-waits` rank 1, `next-tiebreak-by-mint-time-not-file-order` rank 3) and the
`tests-consolidate-prolog-pz4-blocked-33` re-check are the next picks. See
`FINDING-2026-09-01-hq_B-raku-work-basis-grid-rakudo-startup-was-99pct-of-string-escape-and-was-padding-the-point-class-denominators.md`.

**B-1 (2026-08-30 — row `capture-feed-stdin-and-red-exit` LANDED; three gates found lying, one of them vacuous):**
Landed SCRIP `24f7456c` (capture feeds the stdin companion to m3+m4+oracle, the feed is proven by an unfed
control, RED exits non-zero, convert carries the companion end to end, four disagreeing spelling lists
collapsed into `loose_stdin_companion()`), `85e120b8` (hq_P's collapse-guard report cured — and their
proposed fix alone would have traded one false refusal for another; zero-new-entries is the idempotent
rebuild, not a collapse), `3fa3f557` (stale-citation sweep after the corpus `demo/` → `demos/` re-grid).
New gate `test_gate_capture_stdin_and_red_exit.sh`: 14 checks, 7 of them red against the pre-cure harness.

⭐ **THE SESSION'S ONE LESSON, and all three findings are the same shape: THE ABSENCE OF A SIGNAL IS NOT A
SIGNAL.** A gate whose instrument does not exist prints `PASS`. A guard deleted from a shared tool turns
nothing red. A resolver that knows three of four spellings returns `None`, and `None` means `/dev/null`.
None of the three announces itself, and each one had been sitting green for weeks. **Everything this seat
found this session, it found because a CONTROL failed — never because a board did.**

⛔ **OPEN, ROUTED, NOT MINE TO CURE:** SR-1's lower gate needs a ruling (rebase onto `--dump-ir` or retire —
row `sr1-lower-gate-instrument-is-gone-rebase-or-retire`); snocone `beauty_arith --run` drops three real
output lines (hq_C); `test_gate_instr_budget`'s four watermarks are stale low, one by ~6x, and its `beauty`
case fails its own fixed-point precondition (hq_P); `tests/scrip_test` (334 files) is the last unclassified
corpus subtree and cannot be honestly classified until the three absorption rows that left it behind are
reopened (routing asked of ceo). See the three `FINDING-2026-08-30-hq_B-*` files.

**B-0 (2026-08-28 — SEAT OPENED by ceo; nothing measured by this seat yet):** Root populated (three repos cloned, digest + banner hooks installed, identity verified `[hq_B] inbox: 0`). Starting backlog below — first session: read this file, RULES.md in full, then `s4e_msg.sh check` + `next`.

**B-3 (2026-09-01 — ⭐ THE LAW PROPOSAL THIS SEAT OWES ceo, and the sentence that earned it):**
> ⛔ **A CURE CLAIMED IN A BATON AND ABSENT FROM ORIGIN IS WORSE THAN AN OPEN DEFECT** — because the next reader stops looking. A defect that is merely open still recruits attention; a defect recorded as *cured* actively spends it elsewhere.

Measured twice on one night, independently, in two roots: the vanroy baton described three `prelude_*`/`epilogue_*` false positives in `test_gate_bench_rivals_coverage.sh` as **cured**, while the cure sat as a dirty unpushed file in `/home/claude_B/SCRIP` — `total=26 missing=5` on origin against the `total=23 missing=2` the baton implied (landed in `1b40ea1a`); and seat10's untracked FINDING taught hq_C the same lesson the same night (ceo, routed to this seat 2026-09-01). ⭐ **The general form is a claim-to-artifact rule, not a git rule:** a ledger sentence in the perfect tense (*"are cured"*, *"is fixed"*, *"was landed"*) is a claim **about origin**, and the only thing that makes it true is a pushed commit. **Write the hash or write the tense you can prove.** This is the same family as the `$?`-after-a-wrapper and `command -v` traps this org keeps re-measuring: an instrument (here, a baton sentence) answering a narrower question than the reader thinks it answered, and never saying so.
**Status: handed to ceo as a law proposal for next session's RULES.md slot** (ceo's own slot was spent this session). Carried here so it survives the handoff whether or not the slot lands.

## THE ONE QUESTION THIS HQ OWNS

**Is it clean and readable — can a stranger act on it?** A test tree a new seat can navigate, a corpus with zero loose clutter, docs that match the tree, briefs a Sonnet seat executes without asks, error messages and usage text that tell the truth. Whether the answer is RIGHT belongs to `hq_C`; how many instructions it takes belongs to `hq_P`. When beauty work uncovers a wrong answer or a slow path, the defect routes to the owning twin as a FINDING and the cleanup stays here.

| | |
|---|---|
| **priority** | **the announcement burn-down first** (`/home/resources/postoffice/ANNOUNCEMENT.md` — its pinned list, beauty rows) — then the wider hygiene queue |
| **instrument** | gates and censuses, never taste: the corpus coverage gate, the suite-format law (`corpus-suites-consolidation.task.md`), `util_queue_visibility_census.py` (class-F parks → zero ownerless), doc-vs-tree diffs, and the brief-quality measure — asks-per-brief from the seats that run them |
| **verdict** | a conversion is DONE when byte-equal-or-refused (never silently dropped content), a doc is CLEAN when its claims re-measure at HEAD, a brief is GOOD when a seat closed it without a blocking ask. There is no "looks tidy" state |

## ⛔⛔⛔ THE LAW ALL HQs SHARE: **YOU MEASURE *AND* YOU CURE**

Lon s259 (*"You will measure. You will cure."*) binds this seat exactly as its twins — RULES.md § MEASURE AND CURE + § THE TWO MODES. A hygiene defect this seat finds in its lane, this seat fixes; a queue row filed instead of a fix is the failure, not the deliverable.

## LANE — WHAT IS AND IS NOT THIS SEAT'S

**Owns:** the corpus conversion campaign (crosscheck/probe → one-liner/multi-liner suites, Lon's total-conversion ruling); `tests-consolidate-*`; corpus layout custody (`LAYOUT.md`/`CORPUS-LOCATIONS.md` must match the tree — today they lag it); doc/ARCH freshness sweeps (stale citations, retired names, dead paths); baton/brief quality and queue hygiene (sweeps, park ownership, stale-ROWD class); product surface polish (usage text, error messages, demo presentation, the polyglot demo experience).
**Does NOT own:** correctness verdicts (`hq_C`) · perf numbers and benchmark grids (`hq_P`) · WHAT WE SHIP (`ANNOUNCEMENT.md`, ceo custody) · law (ceo lands it; this seat proposes like any HQ) · the READMEs' approval (Lon's word, via ceo).

## INTERLOCKS (cited, not restated — RULES.md is the law)

- Any commit touching code or refs carries the universal floor: `test_corpus_snobol4.sh` + the two live gates, pristine-built for verdicts (HQ-27). SHARED-NODE VERDICT SCOPE binds as written.
- A beauty change that moves a board denominator carries the attribution in the same commit (the s272 denominator law). Conversions are byte-equal-or-refuse — deleting content a suite cannot carry is a REFUSAL with a FINDING, never a silent drop.
- Consumer re-points land in the same commit as the move (the stale-ROWD class: `done-must-hand-off-manifest-cited-rows`).

## STARTING BACKLOG (ceo, at opening — verify each against QUEUE.tsv before claiming; the queue is the authority)

1. **`corpus-crosscheck-probe-total-conversion`** — the campaign, TRANSFERRED from hq_C at opening (their pre-flight oracle audit and the format law stand; read the task file's full ledger). End state: `crosscheck/` GONE, probe loose-`.sno` = 0.
2. Its children and kin on the announce list: `probe-consolidate-fuzz`, `probe-consolidate-m1-and-small` (parked at 3 files each on a distinct external gap — re-verify the gaps first), `tests-consolidate-prolog`, `tests-consolidate-snocone` (`-icon` is claimed by seat06 — shepherd, don't take).
3. `bb-fixup-az-cleanup` — the template A-Z revamp residue (announce list).
4. `arch-doc-repair-bundle` + the roster sweep this seat's own opening created: org files still saying "two HQs" (ARCH-FLEET-CEO.md, PROTOCOL-V2-DRAFT.md seat-loop preamble, postoffice PROTOCOL.md, seat digests) — ceo landed the mechanical minimum; the full citation sweep is this seat's first doc row.
5. `sweep-free-rows-are-real` + naming an owner/cadence for every class-F hygiene park the census prints.
6. Doc-lag: `corpus/LAYOUT.md` and `CORPUS-LOCATIONS.md` vs the measured tree.

## SESSION SETUP

```bash
cd /home/claude_B/SCRIP
bash scripts/s4e_msg.sh check && bash scripts/s4e_msg.sh next
for d in . ../corpus ../.github; do git -C $d fetch -q origin && git -C $d merge -q --ff-only origin/main; done
head -1 /home/resources/postoffice/MODE   # never assume the mode from prose
```
