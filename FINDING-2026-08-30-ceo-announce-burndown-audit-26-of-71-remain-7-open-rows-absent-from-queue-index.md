# FINDING 2026-08-30 (ceo) — Announce burn-down audit: 26 of 71 remain; 7 of those are OPEN but ABSENT from QUEUE.tsv (invisible to the picker)

**Method (census-backed, not by-eye):** every row on the frozen ANNOUNCEMENT.md burn-down list (71 rows) graded against QUEUE.tsv state; the 31 rows absent from the queue index were settled by task-file close receipts plus **fresh computed DONE-WHEN re-runs this session** (S4E_HOME=/home/claude, fresh battery green: corpus GATE OK m3 PASS=1672 FAIL=0 · m4 PASS=1672 FAIL=0). `util_queue_visibility_census.py` run same sitting: 15 hygiene findings, unchanged class.

## The numbers
- **Burn-down: 45 landed, 26 remain** (list pinned at 53, grew to 71 by sanctioned entries; remaining can only go down).
- **Queue in general: 211 open rows of 305** — 163 FREE (0 at rank 0; 6 rank-1, 99 rank-2, 58 rank 3–8), 18 CLAIMED, 4 ASSIGNED, 17 PARKED (3 of them PARKED-LON-HOLD), 7 BLOCKED, 1 GRANT-NEEDED, 1 RESTRICTED. Plus the 7 index-lost rows below → ~218 open items total.

## The 26 remaining burn-down rows
**In queue (19):** FREE 3 (bb-fixup-az-cleanup · polyglot-scrip-demos-10-working · tests-consolidate-icon) · CLAIMED 2 (pascal-m4-for-spine-leak-64b-per-iter @seat04 · prolog-pz4-gamma-retain-activation-frames @seat05) · PARKED-AWAITING 5 (2 behind icon-n2: icn-recogn-genqueen-suspend-shape, icon-bench-correct-suspend-residue; 3 behind pz4: prolog-multiclause-uninit-lexprep-frame, prolog-sendmore-cryptarithm-segv, prolog-term-to-descr-eradication) · PARKED-LON-HOLD 3 (bench-match-lambda-twins · lang-lambda-pattern-primitives · perf-nv-set-fn-o0-overhead) · PARKED 2 (bench-triangulation-rerun-fixed-harness · sweep-free-rows-are-real) · PARKED-UMBRELLA 1 (perf-roman-8x) · BLOCKED 2 (bench-rivals-raku-pascal on raku frontend gaps · prolog-pz5-in-frame-resume-delete-pending-mailbox) · RESTRICTED 1 (defect-c-zop-flat-regime-depth-compensate @hq_P).

**⛔ OPEN but ABSENT from QUEUE.tsv (7)** — rank-0 announcement work invisible to the picker (RANK LAW violation class; also absent from the newest .bak snapshot, so the loss predates 08-29T16:22Z):
1. `m4-static-link-arm` — DONE-WHEN NOT-MET (no static arm in harnesses, newest perf-attribution TSV carries no static rows)
2. `rtx-startup-touch-rewrites` — NOT-MET (no fault/RSS delta in newest TSV)
3. `perf-calc-match-remainder-dig` — NOT-MET (newest dated TSV does not carry the witness)
4. `probe-consolidate-conformance` — NOT-MET (loose files beyond KEEP.md remain)
5. `bb-label-prefix-pascal-suite-regression` — gate output shape DRIFTED from its DONE-WHEN (no "suites: … 96 pass" line any more; criterion REFUSES) and the gate is substantively red: **m3 PASS=161 FAIL=2**, fresh this session
6. `pascal-refs-regen-refs-half` — same drift; **m4 PASS=153 FAIL=1** fresh this session
7. `pascal-refs-regen-from-fpc-oracle` — code+KEEP.md greps MET but its gate half cites the same drifted "96 pass / 0 fail" line; m3 FAIL=2 stands

## Rows verified LANDED among the 31 index-absent (24)
Close receipts in task ledgers: probe-consolidate-passthru · probe-consolidate-bb · bench-rep-loop-demo-harness · corpus-import-{pascal,prolog}-bench-remainder · snocone-restore-prezeta · class-c-epilogue-kt-offset · opsyn-apply-alias-sigsegv · pascal-benchmarks-coverage-gate-red · conform-line-lastline-crash (SUPERSEDED). DONE-WHEN re-run MET this session: gate-mode-arms-rescope · emit-type-size-directives · perf-per-statement-loc-emission · perf-symbol-attribution-tooling · icn-every-expr-context-discards-gamma · icn-cset-embedded-nul (converted to tests/icon/rung38_all, green) · bench-run1-gives-oracle-tuning-flags · corpus-import-raku-bench · pascal-quick-wrong-checksum-m3 · tests-consolidate-snocone · bench-rivals-prolog · scorecard-probes-misc-suite-awareness · snocone-nested-while-in-function-segv (cure 748f7698, re-verified by seat02 08-28 on pristine; witness moved by consolidation) · **perf-patmatch-gap-vs-spitbol — its written DONE-WHEN is MET (FINDING with instrument attribution + FACT-RULE multiple exists), but Lon's 08-27 in-ledger reassignment widened scope beyond the criterion; treating the ROW as met and the widened perf campaign as the live perf-* lane, per the ledger.**

## Consequence
The picker currently has ZERO rank-0 FREE rows while 7 rank-0 announcement rows exist only in ANNOUNCEMENT.md and task files — the exact 08-29 failure shape (seats drain housekeeping, announcement stalls). Cure is mechanical CEO custody: re-add the 7 index rows at rank 0 (rows 5–7 first re-pointing their DONE-WHEN at the gate's current output shape, per the row's own REFUSE clause). Awaiting Lon's word before mutating QUEUE.tsv, since this audit was answered mid-question.
