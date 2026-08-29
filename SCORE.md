# SCORE.md — THE CURRENT SCOREBOARD (all languages, all suites)

⭐ **This file is THE central location for the current score** (Lon 2026-08-29, in-chat to CEO: "You should have a central location for the current score. A health check should show ALL test suites for all languages."). One row per suite, named by its runner script or package name. **Every number carries its tree and date. A seat that measures a suite updates its row in place (rewrite-the-standing-line) and attributes the commit.** A row nobody has measured recently is STALE, not wrong — the label says how stale. Smoke alone is not a score: list every suite.

Shared axes: counts are PASS/FAIL over the suite's own printed denominator, mode-3 and mode-4 separately where the runner grades both. Oracles: SPITBOL `-bf` (SNOBOL4/Snocone), Arizona icont/iconx (Icon), SWI/GNU Prolog (Prolog), rakudo (Raku), `.ref` files (Pascal/Rebus/polyglot). "s283h tree" = ceo working tree 2026-08-29, the apply-call-cure commit (see FINDING-2026-08-29-ceo-apply-call-generator-cured-*).

## SNOBOL4
| Suite | Result | Tree · date · by |
|---|---|---|
| test_corpus_snobol4.sh (broad corpus, THE blocking floor) | m3 1377/1377 FAIL=0 · m4 1377/1377 FAIL=0 SKIP=0 MISSING=0 — re-run on s283h tree IN FLIGHT | 358a88d6 · 2026-08-29 · ceo |
| test_gate_emit_no_lang.sh · test_gate_template_medium_invisible.sh | rc=0 · rc=0 (re-proving on s283h pristine, in flight) | 358a88d6/d1a447ea · 2026-08-29 |
| packages/snobol4/csnobol4_suite (Phil's 120 .ref pairs) | UNGRADED — oracle is csnobol4, not sbl; no resolver in lib_oracle_flags.sh yet | standing (s261 FACT RULE) |

## Icon
| Suite | Result | Tree · date · by |
|---|---|---|
| test_icon_rung_suite.sh (297 rungs) | interp PASS=258 FAIL=9 BADEXIT=1 XFAIL=29 · run 258/9/1/29 · compile 257/10/1/29 (denominator 281→297 moved with reorg — read the printed total) | s283h tree · 2026-08-29 · ceo |
| test_smoke_icon.sh | 14/14 m3 · 14/14 m4 (both HARD zero-FAIL bars) | s283h tree · 2026-08-29 · ceo |
| test_icn_d2_suspend_witness.sh (N-2 acceptance instrument) | ⭐ EXTENDED with `suspend_apply` (the `!`-apply hole hq_B named); armed re-run in flight | s283h tree · 2026-08-29 · ceo |
| ⭐ apply-call to generator (`gen ! [10]`) | **CURED: 10 11 12 rc=0, m3 5/5 runs, m4 standalone 3/3** — never green before in ANY regime (killswitch-off also crashed). Nested (generator apply-calling a generator) REFUSES LOUDLY pending row icon-n2-apply-nested-coexpr | s283h tree · 2026-08-29 · ceo |
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
| m3-passes-m4-fails-three-polyglot-demos | OPEN defect row (seat15; seat is on a pre-rewrite corpus clone, must re-clone first) | board 2026-08-29 |
