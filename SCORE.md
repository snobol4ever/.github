# SCORE.md — THE CURRENT SCOREBOARD (all languages, all suites)

## ⭐ THE STANDARDIZED DISPLAY (Lon 2026-08-29: one grid, all seven languages; detail tables below)

⭐⭐ **COMPUTED, NOT TYPED (row `score-md-master-driven-display`, seat08 2026-08-30).** The grid below is the
literal output of `SCRIP/scripts/util_build_score_md.py` — regenerate it with `python3 scripts/util_build_score_md.py`
(from `SCRIP/`, after `make pristine`) rather than hand-editing a cell. It reads each language's
`corpus/tests/<lang>/ALL.csv` master for entry/xfail counts, invokes that language's own existing,
unmodified floor/smoke gate script for PASS/FAIL — no duplicated grading logic, no fabricated numbers —
**and (since 2026-09-01, ceo → hq_B) runs every language's MASTER BOARD with one instrument, the harness's own
`corpus_suite_harness.py run ALL.<ext> ALL.ref --modes m3,m4`, reported PER MODE and never summed** — and
the stamp line names the exact per-repo commit every number was measured against (never a session label like
the `s283h tree` this section used to carry — see the two paragraphs below for why that mattered and still
matters for the detail tables). **The last two columns answer DIFFERENT questions and must not be read as a pair of attempts at one:**
`Floor/smoke gate` is that language's own hand-built floor — a small curated set that must never regress —
while `Master board` is the whole `ALL.<ext>` suite run end to end. A language can be green on its floor and
carry hundreds of master crashes; that is not a contradiction, it is the two questions doing their jobs.
`MASTER PENDING` means no master exists yet for that language — ⛔ **as of 2026-09-02 that applies to NONE of
the seven: every one has both `ALL.<ext>` and `ALL.ref`** (this sentence read "(Icon, Pascal as of this
writing)" until then, and both acquired masters after it was written — verify with
`ls corpus/tests/*/ALL.ref`, do not trust this clause either). `UNPROVEN(2)` means the gate script is missing,
its output didn't match the expected pattern, or it timed out — the generator refuses to guess rather than
print a number it didn't measure. ⭐ **A timeout is the likeliest cause of an UNPROVEN cell here and it is
load-dependent, not a property of the suite:** the seven master boards take ~30–40 min on a loaded box, so an
UNPROVEN cell means *re-run it quieter*, never *that language is broken*.
**Live catch, not a demo of the format (kept for the record — since resolved):** an earlier run this same day
found `test_corpus_snobol4.sh` REFUSING (`corpus/demos/snobol4` vs. the then-real `corpus/demo/snobol4`, a
rename that had reached 16 scripts but not yet the corpus tree) — flagged to hq_C
(`snobol4-floor-gate-refuses-demos-vs-demo-path-mismatch`) rather than guessed at. hq_C independently confirmed
the rename completed shortly after (corpus went TO `demos`, matching the scripts) and sent the real verdict
line below rather than taking directory-existence as proof of a pass — exactly the discipline this generator
exists to enforce. **XFAIL/XPASS are reported PER MODE, never summed**, per hq_C's live catch:
`simple_output_63` is m3 PASS / m4 SKIP, not an m4 XPASS — a summed or maxed count would have hidden that and
invited promoting a non-promotable entry.

| Language | Master suite (`ALL.csv`) | Floor/smoke gate | Master board (`ALL.<ext>` via `corpus_suite_harness.py run`, m3 · m4) |
|---|---|---|---|
| snobol4 | 1726 entries, 80 xfail | m3 1679/0 · m4 1679/0 SKIP=0 · master total=1726 xfail/xpass m3=70/0 m4=70/0 (PER MODE, never summed -- an XPASS in one mode can be a SKIP in the other, e.g. simple_output_63) | total=1726 · m3 pass=1656 fail=0 crash=0 xfail=70 · m4 pass=1656 fail=0 crash=0 xfail=70 (PER MODE, never summed) |
| icon | 534 entries, 1 xfail | interp PASS=263 FAIL=7 XFAIL=27 TOTAL=298 | total=534 · m3 pass=398 fail=120 crash=13 hang=2 xfail=1 · m4 pass=398 fail=120 crash=1 hang=2 skip=12 xfail=1 (PER MODE, never summed) |
| prolog | 371 entries, 9 xfail | m2 PASS=5 FAIL=0 / 5 (HARD GATE) | total=371 · m3 pass=217 fail=137 crash=8 xfail=1 xpass=8 · m4 pass=217 fail=138 crash=7 xfail=1 xpass=8 (PER MODE, never summed) |
| raku | 129 entries, 14 xfail | m3 PASS=722 FAIL=0 REFUSED=2 / 724 | total=129 · m3 pass=31 fail=83 crash=0 hang=1 xfail=14 · m4 pass=31 fail=41 crash=0 hang=1 skip=42 xfail=14 (PER MODE, never summed) |
| pascal | 149 entries | m3 PASS=161 FAIL=2 NOREF=0 XFAIL=1 | total=149 · m3 pass=148 fail=0 crash=1 · m4 pass=148 fail=0 crash=1 (PER MODE, never summed) |
| snocone | 273 entries, 24 xfail | PASS=5 FAIL=0 | total=273 · m3 pass=175 fail=70 crash=0 hang=4 xfail=18 xpass=6 · m4 pass=175 fail=64 crash=0 hang=4 skip=6 xfail=18 xpass=6 (PER MODE, never summed) |
| rebus | 48 entries | PASS=4 FAIL=0 | total=48 · m3 pass=0 fail=45 crash=0 hang=3 · m4 pass=0 fail=43 crash=0 hang=3 skip=2 (PER MODE, never summed) |

_tree: SCRIP=e182a71a corpus=e7bbc675 .github=8e4fc55d-DIRTY  generated 2026-09-02T02:35Z_

Cross-language: polyglot smoke 2/2 both · demos gate 3/7 both (open row, pre-dates the break-value work by bisect proof). The richer per-suite detail this grid used to cram in — open rows, FINDING links, "other suites" — lives in the per-language tables below, unchanged; this top grid is deliberately just the computed at-a-glance floor now.

⭐ **This file is THE central location for the current score** (Lon 2026-08-29, in-chat to CEO: "You should have a central location for the current score. A health check should show ALL test suites for all languages."). One row per suite, named by its runner script or package name. **Every number carries its tree and date. A seat that measures a suite updates its row in place (rewrite-the-standing-line) and attributes the commit.** A row nobody has measured recently is STALE, not wrong — the label says how stale. Smoke alone is not a score: list every suite. (The top grid above is now exempt from hand-editing entirely — regenerate it instead.)

⛔⭐ **THE `Tree` COLUMN MUST BE A PUSHED COMMIT HASH — A SESSION LABEL IS NOT A TREE** (hq_B 2026-08-29, on hq_C's live catch; raised with ceo). Measured on this file **before** the top grid above went computed: **15 rows read `s283h tree` and 2 carried a real hash.** Nobody can `git checkout s283h`, so those 15 rows state a result that cannot be checked against the thing that produced it — which is the whole job of the column. A scoreboard row whose provenance is unresolvable is not a weaker claim than one with a hash; it is an **unfalsifiable** one, and unfalsifiable rows accumulate silently because nothing can ever contradict them. **This defect is now structurally impossible in the top grid** (the generator can only print a hash it just read); the detail tables below still carry `s283h tree` citations and still need the same discipline applied by hand — out of this row's own immediate scope, a natural follow-up.

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
| test_icon_jcon_suite.sh (jcon test suite, 82 graded pairs, NEW row) | m3 PASS=1 REJECT=79 CRASH=1 HANG=1 · m4 PASS=1 REJECT=79 CRASH=1 HANG=1 (identical both modes) — REJECT is the semicolon-required dialect gap on real unmodified upstream Icon, dominant and expected, not a regression signal; CRASH=recogn matches the already-tracked mutual-recursion gap (icn-recogn-genqueen-suspend-shape); HANG=toby matches seat01's already-ruled finding that the REAL icont/iconx oracle hangs on it too | SCRIP `6c7b5846` · corpus `ddfa6deb` · 2026-08-30 · seat15 |
| test_icon_rung_suite.sh (297 rungs) | interp PASS=258 FAIL=9 BADEXIT=1 XFAIL=29 · run 258/9/1/29 · compile 257/10/1/29 (denominator 281→297 moved with reorg — read the printed total) | s283h tree · 2026-08-29 · ceo |
| tests/icon master suite (ALL.icn — 434 entries / 208 families) | m3 300/118 · m4 unchanged by the rebuild — **14 false FAILs cured** by the clean rebuild under the generalized stdin guards (ALL.in born, 10967B/15 entries; the whole rung27_read family had been graded with no stdin against refs captured with it; suite text byte-identical, only the never-written input file moved) | corpus `b8aae8f1b` · 2026-08-30 · hq_P |
| test_smoke_icon.sh | 14/14 m3 · 14/14 m4 (both HARD zero-FAIL bars) | SCRIP `6b60379a` · 2026-08-29 · seat02 (re-confirmed after `polyglot-define-entry-address` Bug B fix, `lower_icon.c` touched; supersedes the unpinned "s283h tree" citation, same result) |
| test_icn_d2_suspend_witness.sh (N-2 acceptance instrument) | ⭐ EXTENDED with `suspend_apply` (the `!`-apply hole hq_B named); armed re-run in flight | s283h tree · 2026-08-29 · ceo |
| ⭐ apply-call to generator (`gen ! [10]`) | **CURED — the real fix is seat06's SCRIP `5f4b2d4c`** (row closed via computed `done` by seat14 2026-08-30 after fresh skeptical re-verification: witness rc=0 3/3, D2 `suspend_apply` ALL-GREEN 0/10 crashes both modes, smoke 14/14, SNOBOL4 blocking set 1517/0 both modes at `1587eac4`). ⛔ PROVENANCE CORRECTED: the earlier "ceo cure" narrative (FINDING d2191cc3 / the 42a6260f push) was REFUTED by seat03 (FINDING bc22dcc9 — neither cited function ever existed in history; the interim refusal was reverted with nothing replacing it) and two seats bounced the row off that stale text before seat14 re-checked. Check by BEHAVIOUR, not narrative. Nested apply: seat06's `icon-n2-apply-nested-coexpr` close (audit pending) | SCRIP `5f4b2d4c` verified at `1587eac4` · 2026-08-30 · seat14 |
| test_corpus_icon_parser.sh | not measured this pass | — |
| test_icon_arizona_suite.sh (upstream Arizona 9.5, `general/`, vendored `corpus/packages/icon/arizona_tests/`) | m3/m4 identical: PASS=1 (`primes`) REJECT=87 FAIL=1 (`recogn`, an already-tracked N-2 generator-activation-frame gap, not new) / 89 gradable of 99 vendored. REJECT = fails to *parse* (SCRIP Icon's semicolon-required dialect vs. upstream's unmodified newline-style source), spot-verified against 3 files' exact parser diagnostics, never conflated with FAIL. `ARIZONA_SUITE_BOARD total=89 m3_pass=1 m3_reject=87 m3_fail=1 m4_pass=1 m4_reject=87 m4_fail=1` | SCRIP `475b46a3` · corpus `fd2f141e` · 2026-08-30 · seat13 |

## Prolog
| Suite | Result | Tree · date · by |
|---|---|---|
| test_smoke_prolog.sh | m3 5/5 FAIL=0 · m4 5/5 FAIL=0 | s283h tree · 2026-08-29 · ceo |
| test_corpus_prolog_parser.sh (156 files) | parser pass=150 empty=2 crash/timeout=4 · recognizer pass=145 empty=11 · RESULT: PASS | s283h tree · 2026-08-29 · ceo |
| test_crosscheck_prolog.sh | PASS=101 FAIL=0 SKIP=34 **ORACLE_MISS=89** (modes agree, differ from .ref — frontend gaps, not mode defects) | s283h tree · 2026-08-29 · ceo |
| open defect rows | prolog-call-n-user-predicate-segfault · prolog-sendmore-cryptarithm-segv (both parked, no owner — census 2026-08-29) | queue |
| test_prolog_gnu_suite.sh (`packages/prolog/gnu_prolog`, GNU Prolog's OWN vendored compiler/library source, 62 files — previously ZERO runner, row `gnu-prolog-suite-runner-and-score`, Lon direct) | `GNU_SUITE_BOARD total=62 lib=56 ok=4 ok_pass=3 ok_fail=1 reject=2 unexpected=0` — 56 no-main library modules reach the correct compile-only terminal state; of 4 files with their own entry point, 3 triangulate clean (SCRIP m3 = SCRIP m4 = real `gprolog`) and 1 (`Pl2Wam/ciaolib.pl`) is a real, isolated, understood divergence — its `use_module(library(prolog_sys), [statistics/2])` directive is a FATAL consult-time error under real `gprolog` but SCRIP tolerates it (genuine dialect difference, not a harness bug); 2 REJECT (already-known hang-after-parse-error class, `misc-single-witness-parser-crashes`); 0 UNEXPECTED. Runner's own gprolog invocation was found and fixed mid-row: `--init-goal halt` silently skips the file's own `:- initialization(...)` (runs before consult) — same false-agreement shape as tonight's earlier swipl `-g halt` discovery — corrected to the already-proven `--query-goal` pattern from `test_bench_prolog_modes.sh`. | SCRIP `97023758` · corpus `b9c77963` · .github `f270d56d` · 2026-08-30T02:08Z · seat05 |

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
| test_pascal_fpc_suite.sh (`packages/pascal/fpc_tests`, vendored from Free Pascal's own 7618-file test suite, row `fpc-tests-vendor-script-run`, Lon direct — previously ZERO runner) | `FPC_SUITE_BOARD total=181 m3_pass=114 m3_fail=67 m4_pass=114 m4_fail=67 reject=0` — of 7618 FPCSource files, 298 compile under SCRIP (55 from FPC's own tbf/webtbf "expected to fail" categories, reported separately as a front-end leniency finding, not vendored); of the remaining 243, 181 vendored clean against real `fpc -Miso` oracle refs, 62 could not (≈24 specifically because -Miso is pure ISO 7185 and rejects `string`, a Delphi-lineage extension SCRIP itself supports — open mode question, not resolved here). **m3 and m4 fail on the exact same 67 files** — traced the dominant shared cause: SCRIP requires exact-lowercase `writeln` (`WriteLn`/`Writeln`/`WRITELN` all fail with "Undefined function or operation", confirmed by a 4-line minimal repro); standard/FPC Pascal treats identifiers as case-insensitive, and FPC's own source style commonly writes `WriteLn` mixed-case — reported to hq_C with the repro, not fixed here (front-end lane). | SCRIP `a9defbae` · corpus `ce39447d0` · .github `2cd57d30` · 2026-08-30T02:45Z · seat05 |

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
