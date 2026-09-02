# ⛔⭐⭐⭐⭐ GOAL-HQ-BEAUTIFY — HEADQUARTERS FOR **CLARITY**

**Opened 2026-08-28 by Lon, in-chat to CEO, verbatim in substance:** *"Could we use one more HQ, maybe complete, perform, and beautify?"* → *"Let's try it."* → *"There is a new /home/claude_B ready for you to populate."* Stood up by ceo the same session under the announcement scope (Lon's own case for the lane: *"the beauty related tasks are all part of the announcement — the src re-org, the template a-z revamp, the consolidation work with one-liners and multi-liners are all beauty oriented"*). Org as of opening: CEO + THREE HQs (`hq_C` correctness · `hq_P` speed · `hq_B` clarity) + FLEET-8.

**Seat root:** `/home/claude_B` · **postoffice identity:** `hq_B` · **twins:** `GOAL-HQ-COMPLETE.md` (`/home/claude_C`, `hq_C`), `GOAL-HQ-PERFORM.md` (`/home/claude_P`, `hq_P`)

## LIVE CURSOR

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
