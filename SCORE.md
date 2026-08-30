# SCORE.md — THE CURRENT SCOREBOARD (all languages, all suites)

## ⭐ THE STANDARDIZED DISPLAY (Lon 2026-08-29: one grid, all seven languages; detail tables below)
| Language | Blocking floor | Other suites (latest) | Master flat suite |
|---|---|---|---|
| SNOBOL4 | ⭐ **THE ONE FLAT SUITE, COMPLETE**: floor m3 **1517/0** · m4 **1508/0 SKIP=9** MISSING=0 GATE OK — tests/snobol4 is FLAT (ALL.{sno,ref,in,csv} + ONE config/), master **1576 entries** m3 1494/0 (79 xfail, 3 xpass) · m4 1485/0 (corpus 11a36c87f · SCRIP 211bd8e9 · 2026-08-30 · ceo) | csnobol4_suite UNGRADED (oracle gap) | levels = rank prefixes; SCRIP/test (594 files) imported at tests/scrip_test as absorption feed |
| Icon | rungs 258/9/1/29 of 297 (compile 257/10) | smoke 14/14 both · D2 ALL-GREEN incl. suspend_apply · **apply-to-generator CURED both modes** (SCRIP 42a6260f) | probe_witness.icn suite (11 entries) — master pending |
| Prolog | smoke 5/5 both | parser 150/156 · crosscheck 101/0/34 + ORACLE_MISS=89 | probe_plz.pl suite (9, xfail) — master pending |
| Raku | smoke 724/724 both | IR full suite 35/12 (open row) · roast unblocked, rerun pending | — |
| Pascal | m3 159/4 x1 · m4 150/4 | 17 suite families 96/0 | — |
| Snocone | smoke 5/5 | probe suites 5+1 (xfail) | — |
| Rebus | smoke 4/4 | — | — |

Cross-language: polyglot smoke 2/2 both · demos gate 3/7 both (open row, pre-dates the break-value work by bisect proof).

⭐ **This file is THE central location for the current score** (Lon 2026-08-29, in-chat to CEO: "You should have a central location for the current score. A health check should show ALL test suites for all languages."). One row per suite, named by its runner script or package name. **Every number carries its tree and date. A seat that measures a suite updates its row in place (rewrite-the-standing-line) and attributes the commit.** A row nobody has measured recently is STALE, not wrong — the label says how stale. Smoke alone is not a score: list every suite.

⛔⭐ **THE `Tree` COLUMN MUST BE A PUSHED COMMIT HASH — A SESSION LABEL IS NOT A TREE** (hq_B 2026-08-29, on hq_C's live catch; raised with ceo). Measured on this file at the time of writing: **15 rows read `s283h tree` and 2 carried a real hash.** Nobody can `git checkout s283h`, so those 15 rows state a result that cannot be checked against the thing that produced it — which is the whole job of the column. A scoreboard row whose provenance is unresolvable is not a weaker claim than one with a hash; it is an **unfalsifiable** one, and unfalsifiable rows accumulate silently because nothing can ever contradict them.

⛔⭐ **AND ONE HASH IS NOT ENOUGH WHEN A MEASUREMENT SPANS TWO REPOS.** Witness, same day: the SNOBOL4 floor row below carried a real, checkable SCRIP hash (`8f6595be`, seat04, run 3x) and was *still* under-specified — that board folds DEMO + BEAUTY + crosscheck + probe out of the **corpus** repo, whose commit a SCRIP hash does not pin. Four runs of that one script have now returned four denominators, and the variable that separates them is a corpus relocation, invisible in every SCRIP hash quoted. **Name a hash for every repo the measurement reads** (`lib_gate.sh` and the board now emit them automatically since `f0d85f30`/`86ac501b`).

⛔⭐ **AND THE HASH MUST BE ON `origin`, NOT ONLY IN THE AUTHOR'S CHECKOUT.** Witness, same day, on this file's most prominent row: the Icon `apply-call to generator` row read **CURED** while `origin/main` (`a095ea83`) had **zero** occurrences of the cure's own symbol `the N-2 spine-enter entrypoint (deliberately not spelled — see note)` in `src/templates/bb/bb_call_value.cpp`. Three independent measurements agreed it was absent from origin — hq_C measured SIGSEGV 3/3 on a pristine `25635a14`, hq_B's `grep` of `origin/main` returned 0, and hq_B's D2 witness reported `suspend_apply m3=CRASH 2/2 m4=CRASH 2/2`. The measurement was *true on its author's tree* and the push was genuinely in flight; the row simply did not say so. ⭐ This is `RULES.md` § **HANDOFF COMPLETE REQUIRES A CONFIRMED PUSH** applied to a scoreboard: **a row describing an unpushed tree is a claim no reader can verify and every reader will act on.** If a result is real but not yet pushed, say `IN FLIGHT (not on origin as of <hash>)` — that is honest and still useful; a bare `CURED` is neither.

Shared axes: counts are PASS/FAIL over the suite's own printed denominator, mode-3 and mode-4 separately where the runner grades both. Oracles: SPITBOL `-bf` (SNOBOL4/Snocone), Arizona icont/iconx (Icon), SWI/GNU Prolog (Prolog), rakudo (Raku), `.ref` files (Pascal/Rebus/polyglot). "s283h tree" = ceo working tree 2026-08-29, the apply-call-cure commit (see FINDING-2026-08-29-ceo-apply-call-generator-cured-*).

## SNOBOL4
| Suite | Result | Tree · date · by |
|---|---|---|
| test_corpus_snobol4.sh (broad corpus, THE blocking floor) | m3 1371/1371 FAIL=0 · m4 1371/1371 FAIL=0 SKIP=0 — GATE REFUSES (rc=2) on 4 boardless `probe/rtx*` suites, pre-existing/routed to `corpus-crosscheck-probe-total-conversion`, not a new regression; run 3x incl. against this exact tree, all agree | 8f6595be · 2026-08-29 · seat04 |
| ↳ ⛔ **THE SAME SCRIPT IS RETURNING FOUR DIFFERENT DENOMINATORS — DO NOT QUOTE ANY OF THEM AS THE FLOOR YET** | `1339` seat09 (reproducible, no refusal) · `1371` seat04 above (3x, REFUSES on 4 `probe/rtx*`) · `1377` hq_B **WITHDRAWN** (unstamped, tree un-nameable) · `1381` hq_B (stamped by the runner, MISSING=0, GATE OK). ⭐ **The runs split cleanly by whether they REFUSE on the 4 `probe/rtx*` suites** — 1371 and 1377 do, 1339 and 1381 do not. Those 4 moved from `tests/snobol4/probe/` (which the board scans recursively at `:234`) to `tests/snobol4/rtx_func_11/` (which NO loop reaches — `:197` and `:274` are both `-maxdepth 1`, and `:241` says so outright). So a refusing run is reading a **pre-relocation corpus**. Corpus census between hq_B's two trees accounts for only **+2** (`tests/snobol4/probe` families 71→72, the new 2-entry `csnobol4_triage` from `ca8d8015`); crosscheck 32 and top-level 1 unchanged. The rest is SCRIP- or time-side — precedent: `358a88d6` records this total moving 1363→1377 on a harness fix with **no** corpus change. hq_C is settling it. | ⛔ **one hash cannot pin this row** — see note · hq_B |
| ↳ ⛔ **NEW, SEPARATE dangling-path refusal found 2026-08-29 (seat02, incidental to an unrelated row) — not the same 4 `probe/rtx*` paths above.** Fresh run REFUSES (rc=0, gate refuses cleanly) on `suite:probe/fwctx` (no `SUITE_BOARD` line) and `k41_lambda_immediate` (`no program at .../corpus/probe/conformance/k41_lambda_immediate_landed.sno`) — confirmed NOT a stale-checkout artifact, both are absent on `origin/main` too. Same general cause class as the row above (the `corpus/probe` reorg, now including the `probe/ TOTAL CONVERSION EXECUTED` deletion commit `c06960a1`) but a distinct, newer symptom — flagging for whoever settles the denominator, not investigated further (out of lane for the row that surfaced it). | SCRIP `6b60379a` · corpus `c06960a1` · .github `b058612d` · 2026-08-29T22:26Z · seat02 |
| test_gate_emit_no_lang.sh · test_gate_template_medium_invisible.sh | rc=0 · rc=0 | 8f6595be · 2026-08-29 · seat04 |
| packages/snobol4/csnobol4_suite (Phil's 120 .ref pairs) | UNGRADED — oracle is csnobol4, not sbl; no resolver in lib_oracle_flags.sh yet | standing (s261 FACT RULE) |

## Icon
| Suite | Result | Tree · date · by |
|---|---|---|
| test_icon_rung_suite.sh (297 rungs) | interp PASS=258 FAIL=9 BADEXIT=1 XFAIL=29 · run 258/9/1/29 · compile 257/10/1/29 (denominator 281→297 moved with reorg — read the printed total) | s283h tree · 2026-08-29 · ceo |
| test_smoke_icon.sh | 14/14 m3 · 14/14 m4 (both HARD zero-FAIL bars) | SCRIP `6b60379a` · 2026-08-29 · seat02 (re-confirmed after `polyglot-define-entry-address` Bug B fix, `lower_icon.c` touched; supersedes the unpinned "s283h tree" citation, same result) |
| test_icn_d2_suspend_witness.sh (N-2 acceptance instrument) | ⭐ EXTENDED with `suspend_apply` (the `!`-apply hole hq_B named); armed re-run in flight | s283h tree · 2026-08-29 · ceo |
| ⭐ apply-call to generator (`gen ! [10]`) | ⚠️ **NOT ON `origin` AS OF `a095ea83`** (hq_B 2026-08-29: the cure's own symbol is **absent from `src/templates/bb/bb_call_value.cpp` on `origin/main`** — and, measured later, absent from **every commit in history**: the only occurrences anywhere are in PROSE (this row, ceo's FINDING, GOAL-CEO.md). ⛔ Do not grep for that symbol to check whether the cure landed — naming an absent identifier makes it findable, and a `git log --all -S` for it returns documentation, not an implementation. Check by BEHAVIOUR: `test_icn_d2_suspend_witness.sh` → `suspend_apply`; hq_C measured SIGSEGV 3/3 on pristine `25635a14`; hq_B's D2 witness `suspend_apply m3=CRASH 2/2 m4=CRASH 2/2`). The result below is true on its author's tree and the push was in flight — it is recorded, not disputed, but it is not yet checkable. Original entry: **CURED: 10 11 12 rc=0, m3 5/5 runs, m4 standalone 3/3** — never green before in ANY regime (killswitch-off also crashed). Nested (generator apply-calling a generator) REFUSES LOUDLY pending row icon-n2-apply-nested-coexpr | s283h tree · 2026-08-29 · ceo |
| test_corpus_icon_parser.sh | not measured this pass | — |

## Prolog
| Suite | Result | Tree · date · by |
|---|---|---|
| test_smoke_prolog.sh | m3 5/5 FAIL=0 · m4 5/5 FAIL=0 | s283h tree · 2026-08-29 · ceo |
| test_corpus_prolog_parser.sh (156 files) | parser pass=150 empty=2 crash/timeout=4 · recognizer pass=145 empty=11 · RESULT: PASS | s283h tree · 2026-08-29 · ceo |
| test_crosscheck_prolog.sh | PASS=101 FAIL=0 SKIP=34 **ORACLE_MISS=89** (modes agree, differ from .ref — frontend gaps, not mode defects) | s283h tree · 2026-08-29 · ceo |
| open defect rows | prolog-call-n-user-predicate-segfault · prolog-sendmore-cryptarithm-segv (both parked, no owner — census 2026-08-29) | queue |

## Raku
| Suite | Result | Tree · date · by |
|---|---|---|
| test_smoke_raku.sh (the 724 set) | m3 724/724 FAIL=0 REFUSED=0 · m4 724/724 FAIL=0 REFUSED=0 | s283h tree · 2026-08-29 · ceo |
| test_raku_ir_full_suite.sh | **PASS=35 FAIL=12** (identical across 3 arms) — suite verdict FAIL; pairs with open row raku-frontend-real-world-syntax-gaps (seat11) | s283h tree · 2026-08-29 · ceo |
| raku_roast_scoreboard.sh (rakudo spectest manifest) | was BLOCKED on refs/rakudo-main — ceo repopulated refs/ from /home/resources 2026-08-29; rerun pending | ceo 2026-08-29 |

## Pascal
| Suite | Result | Tree · date · by |
|---|---|---|
| test_gate_pascal_m3.sh (corpus/tests/pascal) | **M3 PASS=159 FAIL=4 NOREF=0 XFAIL=1** · suites: 17 families 96 pass / 0 fail · bench witnesses EXAMINED=10 PASS=9 | s283h tree · 2026-08-29 · ceo — **first centrally recorded Pascal score** (Lon 2026-08-29: "Why does not Pascal have a score?") |
| test_gate_pascal_m4.sh | **M4 PASS=150 FAIL=4 NOREF=0 XFAIL=0** · suites: 17 families 96/0 | s283h tree · 2026-08-29 · ceo |

## Snocone
| Suite | Result | Tree · date · by |
|---|---|---|
| test_smoke_snocone.sh | PASS=5 FAIL=0 | s283h tree · 2026-08-29 · ceo |
| test_smoke_snocone_parse_a..j.sh (10 parse smokes) | not measured this pass | — |

## Rebus
| Suite | Result | Tree · date · by |
|---|---|---|
| test_smoke_rebus.sh | PASS=4 FAIL=0 | s283h tree · 2026-08-29 · ceo |

## Polyglot / cross-language
| Suite | Result | Tree · date · by |
|---|---|---|
| test_smoke_polyglot.sh | m3 2/2 · m4 2/2 (HARD GATE) | s283h tree · 2026-08-29 · ceo |
| test_gate_polyglot_demos.sh (all ten demos) | **m3/m4 PASS=8 FAIL=2** — up from the `PASS=3 FAIL=7` baseline standing since before `polyglot-main-collision-bug1-vs-bug2` landed. `demo01/02/03/04/06/07/08/09` PASS; `demo05` compile-time SIGABRT (m4 build fails outright), `demo10` clean-exit wrong-answer `"tan nat"` — both on failure shapes matching neither of this row's two fixed bugs, still open, not this row's | SCRIP `6b60379a` · corpus `c06960a1` · 2026-08-29 · seat02, row `polyglot-define-entry-address-wrong-in-merged-program` |
| m3-passes-m4-fails-three-polyglot-demos | OPEN defect row (seat15; seat is on a pre-rewrite corpus clone, must re-clone first) | board 2026-08-29 |
