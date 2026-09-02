# ⛔⭐⭐⭐⭐ MASTER-PLAN — THE LADDERS THE FLEET WALKS (FLEET-16 · PROLOG #1)

**Opened 2026-09-01 by ceo on Lon's order, in-chat, verbatim in substance:** *"We are going to mode FLEET-16. Prolog is the #1 priority. All around test, performance, Term struct eradication."* → *"Make a master plan and being CEO ensure the fleet walks along the ladders."*
**Authority:** RULES.md is law; GOAL-PROLOG-100.md (s273 DESCR ruling + the 2026-09-01 blocks), GOAL-HQ-COMPLETE.md, GOAL-HQ-PERFORM.md, GOAL-HQ-BEAUTIFY.md stay sovereign for their lanes. **This file is sovereign for one thing only: THE ORDER OF THE WORK** — which rows are rungs, on which ladder, and what "walking" means for the picker, the HQs and the ceo. It is rewritten in place by ceo every sitting from the walk instrument's output (never appended; the standing table is the record — see [[rewrite-the-standing-line]] discipline in GOAL-CEO).
**Instrument:** `python3 SCRIP/scripts/util_ladder_walk.py` — joins the rung tables below with `/home/resources/postoffice/{QUEUE.tsv,QUEUE.done.tsv,claims,tasks}` and prints every rung's state plus the violations (V1 rung without row · V2 off-ladder seat · V3 stale park · V4 rank inversion · V5 unowned block · V6 orphan Prolog row). Exit 0 clean · 1 violations · 2 refuse. It answers *does the QUEUE agree with the PLAN*; `s4e_msg.sh fleet` answers *is the seat working*. Read both.

## HOW THE FLEET WALKS (the rules; the ladders are below)

1. **A rung is a row.** Every unit of fleet work under this plan is a `QUEUE.tsv` row with a baton under `tasks/`, and every such row is exactly one rung of exactly one ladder. A Prolog row on no ladder is an ORPHAN the owning HQ places or retires the same sitting (V6).
2. **Rank encodes the ladder.** Rank 0 = the CURRENT rung(s) of a ladder (marked ⭐ below); rank 1 = every other rung; rank ≥ 2 = off-ladder work. `next()` serves the topmost FREE row, so a seat that runs `next` steps onto a rung by construction. The ceo re-ranks each sitting from the walk (V4).
3. **A seat on an off-ladder row** lands it if its DONE-WHEN is within reach this sitting; otherwise pushes its progress, writes the LEDGER/NEXT, `unclaim`s (or `park`s on a real blocker) and runs `next`. Nobody rips a dirty tree (V2 is a notice, not a purge).
4. **HQs own ladders; the ceo owns the plan.** hq_C: T and C · hq_P: P · hq_B + ceo: I. An HQ minting a Prolog row writes `LADDER:<T|C|P|I> RUNG:<id>` on its LINKS line and tells ceo the rung; ceo adds the row to the table the same sitting. A rung marked `TO-MINT:<lane>` is a mint the lane OWES (V1).
5. **Rung exit = the row's DONE-WHEN. Ladder exit = the gate in its header.** The plan is done when all four ladder gates are green over their PRINTED denominators, both modes where the instrument grades both. SNOBOL4's blocking floor (`make test`) is the control arm on every landing regardless of ladder (RULES § SHARED-NODE VERDICT SCOPE); Icon's pinned watermark likewise.
6. **Parallelism is per rung, never per row.** Rungs on one ladder may run concurrently when they touch disjoint function families (the T ladder's seams are the table in the umbrella's `## NEXT`); two seats never hold one rung. A blocked rung is spelled `BLOCKED-ON:<row>` / `PARKED-AWAITING:<row>` so `next()` un-parks it by itself when the blocker lands (V3 catches the ones spelled otherwise).
7a. **Modes.** The plan is mode-independent: under FLEET-n the seats are the walkers and V2 (off-ladder seat) is live; under DUO/TRIO the HQs are the walkers of their own ladders (hq_C: T, C · hq_P: P · hq_B: I), V2 is moot, and the rank rule still orders the work. Lon 2026-09-01 evening: *"Time to wrap it up on all fleet workers. Go to mode TRIO."* — the seats wrapped to clean pushes and their rungs returned to FREE with ledgers; the HQs resume them by rank.
7. **The ceo walks every sitting:** run the instrument · fix V4/V5 by rank/owner edits (snapshot `QUEUE.tsv.bak.ceo-walk-*` first) · route V1/V6 to the owning HQ as one telegram with the list · note V2/V3 · rewrite the tables below in place · audit ~3 DONE rungs by re-running their DONE-WHENs (the CEO LOOP's AUDIT step, now aimed at rungs).

## MEASURED STATE AT OPENING (2026-09-01, SCRIP `43e30f0d`, corpus `e2f3496f`, RT_OPT=-O0; every number's command is named)

- **T:** `grep -rcw Term src --include='*.c' --include='*.h' --include='*.cpp'` = **490** word-refs (s273 baseline 448; 08-27 mint 469). `term.h` and `pl_cell_conv.h` exist. Six of eight slices claimed within 90 minutes of minting.
- **C:** Prolog master board (`python3 scripts/corpus_suite_harness.py run corpus/tests/prolog/ALL.pl corpus/tests/prolog/ALL.ref --lang prolog --modes m3,m4`, at 8eac17da): `total=371 · m3 pass=218 fail=5 crash=139 xfail=1 xpass=8 · m4 pass=218 fail=5 crash=7 skip=132 xfail=1 xpass=8` — the 139 crashes are ONE driver class (`[IBB] FATAL: mode-3 driver: main BB graph not found` on clause-only entries; witness `foo(X,Y) :- X @>= Y.`); the 132 m4 compile-failed skips are the same population. `bash scripts/test_prolog_rung_suite.sh`: `PASS=4 FAIL=11 TOTAL=15` in BOTH modes — ⛔ the runner prints no red names (rung I4). `test_smoke_prolog.sh` 5/5 both modes. `test_corpus_prolog_parser.sh` RESULT: PASS (Parser pass=44 empty=1; Recognizer pass=45). `test_gate_pl_coupling.sh` PASS (choice 19 · goal 10). `test_crosscheck_prolog.sh` last labeled reading PASS=101 FAIL=0 SKIP=34 ORACLE_MISS=89 (s283h, 2026-08-29, ceo) — re-measure at C2. Vendored conformance: `packages/prolog/gnu_prolog` 62 `.pl`, `packages/prolog/swi_tests` 249 `.pl`; runners `test_prolog_gnu_suite.sh`, `test_prolog_swi_suite.sh` — their boards are the C-ladder's conformance rungs (numbers land in the table's gate column at the first walk that has them).
- **P:** the published Prolog rivals grid excludes 12 of 22 van Roy kernels for WRONG OUTPUT under m4 (crypt, ham, meta_qsort, mu, nreverse, nrev, qsort, queens_8, queensn, queens, query, zebra — row `prolog-bench-12-kernels-output-diverge`); `calling-convention-depth-tracked` is the critical path (PZ-4 and the 12-kernels row wait on it; hq_P ETA this session); `bench_prolog_vanroy.sh` is the rail (gprolog · swipl · m3 · m4, per-iteration ms, auto-ranged N); the two-number basis and three angles are law (RULES § THE TWO-NUMBER BENCHMARK BASIS).
- **I:** `util_queue_visibility_census.py` CLEAN; `util_ladder_walk.py` landed this sitting; SCORE.md's Prolog section carries smoke/parser/crosscheck but NO master-board row.
- **Conformance (C27/C28), measured at opening:** GNU `total=62 lib=45 ok=15 ok_pass=6 ok_fail=9 reject=2` · SWI `PASS=92 FAIL=22 TOTAL=114` suite-lines, `--run` only.
- **Evening walk (TRIO, ~19:30):** C1 DONE (seat05, 18:54) — the master board re-runs for C2; C8, C13, C19 DONE by seats before the stand-down; I7 and I9 DONE by hq_B (19:03); Term word-refs 490 → **371**; ten seat claims mid-wrap (census B under TRIO) — HQs resume them by rank once released; corpus banner torn at 2d75933ec (every SNOBOL4 board refuses) — hq_P lands the one-line fix.
- **First walk (2026-09-01, 37 violations, all real):** 13 TO-MINT rungs routed to their lanes · 3 orphan Prolog rows minted by hq_P minutes earlier placed as P5/P9/P10 · **14 off-ladder FREE rows demoted from rank 1 to rank 2** on Lon's priority (beauty-byname-dispatch-linear-scan, beauty-runtime-recompiles-patterns-emitter-resident, corpus-runner-master-suite-exceeds-single-call-cap, dead-suite-path-consumer-sweep, icon-vendor-fail-crash-triage, pascal-iso7185-pat-suite-import-and-run, pascal-p4-selfhost-compile-and-report, pascal-rivals-grid-two-number-basis, raku-array-params-pass-by-copy, raku-eager-materialization-family, raku-silent-wrong-answers, snobol4-board-must-refuse-stale-binary, snobol4-csnobol4-suite-graded, snocone-beauty-selfhost — snapshot `QUEUE.tsv.bak.ceo-walk-*`; they are not cancelled, they queue behind the rungs) · I2 promoted 3→1 · four seats noted on off-ladder rows (seat02 port-exit sentinel, seat03 coexpr stacks, seat04 bb-fixup A–Z, seat16 icon scan residue) — they land or park per rule 3, nobody is ripped.

## THE LADDERS

### LADDER T — Term→DESCR eradication (owner hq_C · umbrella `prolog-term-to-descr-eradication` · GATE: the umbrella DONE-WHEN — `term.h` and `pl_cell_conv.h` deleted, tree-wide `Term` word-refs 0, prolog smoke 5/5 both modes, parser suite PASS, master board not worse than its baseline)

| rung | row | lane | gate |
|---|---|---|---|
| ⭐T1 | prolog-term-descr-s1-write-format-printers | seat | slice DONE-WHEN (78 Term lines → 0: write/format/atom_op/char_type + prolog_builtin.{c,h}) |
| ⭐T2 | prolog-term-descr-s2-compare-sort-pairs | seat | slice DONE-WHEN (65 → 0: compare/sort/keysort/pairs/bag + rt_runtime.c compare helpers) |
| ⭐T3 | prolog-term-descr-s3-copy-findall-nb-aggregate | seat | slice DONE-WHEN (34 → 0: copy_term/findall/nb_/aggregate) |
| ⭐T4 | prolog-term-descr-s4-typetest-functor-univ-succ | seat | slice DONE-WHEN (57 → 0; deletes prolog_unify.c) |
| ⭐T5 | prolog-term-descr-s5-dynamic-db-flags-streams | seat | slice DONE-WHEN (41 → 0: assert/retract/clause/flags/streams) |
| ⭐T6 | prolog-term-descr-s6-parser-builds-tree-t-directly | seat | slice DONE-WHEN (112 → 0: prolog_parse.c, prolog_lower.c, prolog_atom.c) |
| ⭐T7 | prolog-term-descr-s7-dead-resolution-env-layer-deleted | seat | slice DONE-WHEN (22 → 0: resolution.{h,c} env layer, zero callers) |
| T8 | prolog-term-descr-s8-term-h-and-converters-deleted | seat | umbrella DONE-WHEN; BLOCKED-ON T1–T7 (spelled BLOCKED-ON s6; ledger carries the rest) |
| T9 | prolog-term-to-descr-eradication | hq_C | umbrella closes on T8's green; hq_C sweeps the ledger and tells ceo |

### LADDER C — Prolog correctness and tests (owner hq_C · GATE: master board `fail=0 crash=0` both modes over the printed denominator (371 today) · rung suite 15/15 both modes with red names printed · GNU and SWI conformance suites graded on SCORE.md with their denominators · crosscheck ORACLE_MISS 89 → 0 or each miss a row · PZ-4/PZ-5 landed so the multi-clause classes die)

| rung | row | lane | gate |
|---|---|---|---|
| ⭐C1 | prolog-directive-only-file-fatals-no-main-bb-graph | seat | the 139-entry driver class dies; master board re-run, printed denominator |
| C2 | prolog-master-board-remaining-reds-classified-by-stderr-signature | hq_C | after C1: re-run the master board, classify every remaining red by stderr signature, one row per class (the 5 `fail` entries included); re-measure crosscheck ORACLE_MISS (REFUSES rc=2 until C1 is DONE, by construction) |
| C3 | prolog-rung-suite-reds-rowed-by-class | hq_C | rung suite: the 11 reds named (needs I4) and rowed by class (REFUSES rc=2 until I4 is DONE) |
| C4 | prolog-backtracking-yields-first-solution-only | seat | row DONE-WHEN |
| C5 | prolog-call-n-multiarg-target-wrong | seat | row DONE-WHEN |
| C6 | prolog-existence-error-not-catchable-iso | seat | row DONE-WHEN |
| C7 | prolog-forall-wrong-answer-rung57 | seat | row DONE-WHEN |
| C8 | prolog-missing-string-pairs-builtins | seat | row DONE-WHEN |
| C9 | prolog-var-goal-dispatch-through-catch-call-silently-fails | seat | row DONE-WHEN |
| C10 | prolog-variable-goal-dispatch-to-user-predicate | seat | row DONE-WHEN |
| C11 | prolog-abolish-leaves-predicate-defined-but-empty | seat | row DONE-WHEN |
| C12 | prolog-write-canonical-prints-dot-functor-form-for-lists | seat | row DONE-WHEN (coordinate with T1: the writer is being rewritten) |
| C13 | prolog-two-programs-broken-post-churn | seat | row DONE-WHEN |
| C14 | prolog-queens-and-sentences-segv-are-more-rt-jmp-frame-lexprep2-witnesses | seat | row DONE-WHEN |
| C15 | prolog-plw-unify-cells-var-nonvar-trail-smash | seat | row DONE-WHEN (coordinate with T2) |
| C16 | prolog-findall-directive-replace-segv | hq_C | row DONE-WHEN (coordinate with T3) |
| C17 | prolog-bench-12-kernels-output-diverge | hq_C | 12 kernels output-exact vs `.expected`; PARKED-AWAITING P1 |
| C18 | test-gate-pl-gz-dead-instruments-measure-a-retired-path | seat | dead gates retired or re-pointed, named in the commit |
| C19 | prolog-bak-files-dead-code-sweep | seat | row DONE-WHEN |
| C20 | prolog-next | seat | GOAL-PROLOG-100 LIVE CURSOR's first incomplete step (a pointer rung; the seat names what it did) |
| C21 | prolog-pz4-gamma-retain-activation-frames | hq_C | PZ-4 keystone; BLOCKED-ON P1 |
| C22 | prolog-multiclause-uninit-lexprep-frame | hq_C | PARKED-AWAITING C21 |
| C23 | prolog-sendmore-cryptarithm-segv | hq_C | PARKED-AWAITING C21 |
| C24 | prolog-between-generator-backtrack-crash | hq_C | PARKED-AWAITING C21 |
| C25 | prolog-pz5-in-frame-resume-delete-pending-mailbox | hq_C | PZ-5, BLOCKED (spell the blocker) |
| C26 | tests-consolidate-prolog-pz4-blocked-33 | hq_B | 33 entries join the master suite; re-check whether still PZ-4-gated |
| C27 | prolog-gnu-conformance-ok-fail-print-zero-bytes-both-modes | seat | GNU conformance suite `test_prolog_gnu_suite.sh` — at 43e30f0d (reproduced live at 54cf54fd): `GNU_SUITE_BOARD total=62 lib=45 ok=15 ok_pass=6 ok_fail=9 reject=2 unexpected=0` (rc=1); the 9 ok_fail entries print 0 bytes in both modes vs gprolog's output — rowed by class, SCORE.md row |
| C28 | prolog-swi-conformance-22-reds-rowed-by-class | seat | SWI conformance suite `test_prolog_swi_suite.sh` — at 43e30f0d: `Suite totals: PASS=92 FAIL=22 TOTAL=114 mode=--run` (m3 only — the m4 arm is owed by the runner); 22 reds rowed by class, SCORE.md row |
| C30 | prolog-bare-directive-loses-conjuncts-after-the-first-at-parse-time | hq_C | row DONE-WHEN (hq_C mint 2026-09-01; parse-time conjunct loss in a bare directive) |
| C29 | prolog-iso-coverage-missing-builtins-rowed-by-family | seat | ISO coverage (`audit_prolog_iso_coverage.sh`): step one wires the gprolog builtin list from /home/resources/gprolog-master (the audit prints "MISSING canonical source" on this root today), then the missing-builtin list becomes rows by family |

### LADDER P — Prolog performance (owner hq_P · GATE: all 22 van Roy kernels output-exact and published on the two-number basis, three angles, vs swipl and gprolog (`bench_prolog_vanroy.sh` + `bench_triangulate_prolog.sh`); then the per-kernel multiples climb with the runtime services rewired — the T ladder's cell services are the substrate)

| rung | row | lane | gate |
|---|---|---|---|
| ⭐P1 | calling-convention-depth-tracked | hq_P | = the row's DONE-WHEN: sieve+bubble m4 rc=0, optbypass not regressed, SNOBOL4 FAIL=0 both modes over the printed denominator (the critical path: C17, C21, P8 wait on it). fbench is NOT this class — measured: still SEGVs after both arms inside transitxsurface_omega with walls=0 in every proc; it is the nested-proc epilogue-γ promotion site and belongs to the port-exit value-contract row's witness list (ceo ruling 2026-09-01 on hq_P's ask) |
| ⭐P11 | port-exit-value-contract-untagged-rax-forges-dt-fail | seat | a port exit may hand an UNTAGGED raw value into a calling convention whose failure sentinel ordinary data can forge — a SILENT WRONG ANSWER across three languages (18 sites; fbench.pas is its witness, not P1's); hq_P ruled the sentinel design ((c), taken whole) — cross-language doctrine of P1's family, hence rank 0 beside it |
| P2 | prolog-plw-floor-bypass-safety-unproven | seat | row DONE-WHEN once hq_P cuts it (REFUSE(2) today) |
| P3 | bench-grids-rebase-to-two-number-basis | hq_B | the two shipped grids republished on WORK/OVERHEAD |
| P4 | bench-triangulation-rerun-fixed-harness | hq_P | three angles re-run on the cured harness; PARKED-AWAITING P9 (the triangulation table is the MEASURED bucket P9's board reads); AGREE rows published, DISAGREE withheld |
| P5 | prolog-hot-services-by-ir-with-owning-slice | seat | ranked census of the Prolog runtime's hottest services by callgrind Ir at fixed work, each tagged with the T slice that owns it (hq_P mint 2026-09-01) |
| P6 | TO-MINT:hq_P | hq_P | Prolog builtins dispatched by NAME at run time → wired at compile time (Lon s264: the compiler does the extra work, not the runtime); measured on P5's top service first |
| P7 | builtin-setjmp-mechanism-and-perf-reland | hq_P | the setjmp win re-landed with its mechanism established (hq_C's FENCE revert stands until then) |
| P8 | optimizer-off-path-segvs-so-the-emergency-bypass-is-not-a-correct-path | seat | BLOCKED-ON P1 |
| P9 | prolog-vanroy-21-board-two-number-basis | seat | the van Roy board published on WORK/OVERHEAD, three angles, vs swipl and gprolog; a kernel joins the grid only output-exact (hq_P mint 2026-09-01) |
| P10 | prolog-trail-mark-crosses-call-boundary-in-fixed-rsp-slot | seat | the Prolog implementer of P1's doctrine — trail mark transported in the fixed [rsp+32] slot across the call boundary, measured witness set (hq_P mint 2026-09-01) |

### LADDER I — Instruments and dispatch (owners hq_B + ceo · GATE: every ladder gate above is a computed instrument with a SCORE.md row; the dispatcher serves rungs first; the walk runs clean)

| rung | row | lane | gate |
|---|---|---|---|
| ⭐I10 | optbypass-pin-stable-subset | hq_C | the optbypass watermark pins a STABLE subset, so an XFAIL-marker promotion (population 1654→1646→1726…) no longer re-breaks `make test` for every seat and no longer blocks a landing (P1 held by it 2026-09-01 evening); interim protocol: a promotion that moves the population re-pins in the same commit or is not pushed |
| I11 | donewhen-lines-that-cannot-parse-as-shell-so-done-can-never-close-them | hq_C | every live DONE-WHEN parses as shell (`bash -n` is the narrower question — the row grades that each can REACH a verdict: rc 0/1/2 on a probe, never a syntax error); hq_C mint from its own s8 slip |
| I12 | scoped-kill-helper-only-pids-under-my-root | seat | `s4e_kill_mine.sh <pattern>` signals only PIDs whose /proc cwd is under the caller's root, refuses box-wide forms; digests name it and ban `pkill -f` (seat07 self-report; hq_P 18:28) |
| ⭐I8 | master-suite-board-refuses-under-fleet-load-slot-lock-or-load-scaled-timeout | seat | WHO KILLS HARNESS RUNS BY NAME: four refusals across two seats in one 3-minute window (18:17–18:20) BEFORE the known 18:28 pkill → a FINDING names the sender with evidence, and a killed run prints its signal and cause (depends on I9). The capacity premise in the slug is RETRACTED by its author (seat06: board PASSED at loadavg 27 in 500 s); seat04's 748 s under load stands — callers' budgets exceed it or run detached |
| I9 | test-corpus-snobol4-refusal-discards-the-harness-stderr | seat | the board stops piping the harness through 2>/dev/null: a refusal, a kill and a crash print DIFFERENT things (precondition of I8's "who sent the SIGTERM" step; hq_C mint from seat11's finding) |
| ⭐I7 | park-marks-last-row-only-when-clearing-own-claim | hq_B | `park` marks `.last-row` only on the branch that clears the caller's own claim; gate proves unclaim/done/park-own each write it and park-not-owned leaves it (seat14 FINDING 0803ecca; rank 0 because the FLEET-16 all-hands told seats to park) |
| ⭐I1 | make-pristine-per-root-flock-second-builder-waits | seat | two concurrent `make pristine` in one root both exit 0 and the binary passes the smoke |
| I2 | next-tiebreak-by-mint-time-not-file-order | hq_B | a newer row at equal rank is served first; proven both ways by a gate |
| I3 | score-md-master-board-row-every-language | hq_B | SCORE.md carries the master-board row for every language that has an `ALL.*` suite (Prolog's was missing 2026-09-01) |
| I4 | prolog-rung-suite-prints-the-name-of-every-red-rung | seat | `test_prolog_rung_suite.sh` prints the NAME of every red rung beside its totals (proof at mint: "FAIL=11 but 0 RED lines name a rung") |
| I5 | prolog-term-wordref-ratchet-gate-in-make-test | seat | per-file `Term` word-ref ratchet gate in `make test` (pins from the 490 census; red on any rise; refuses rc=2 when it cannot see src/); hq_C checked: no T slice carries a make-test gate |
| I6 | sweep-free-rows-are-real | ceo | the standing ceo umbrella: every sitting runs the visibility census AND `util_ladder_walk.py`; the plan's tables are rewritten from the output (cadence widened 2026-09-01) |

## WHEN THE PLAN CHANGES

Lon's word changes it instantly and the ceo routes the change into this file the same sitting (MODE discipline). An HQ that needs a rung re-ordered, split, or added asks ceo with the measurement; the ceo rewrites the table in place and names the change in the commit. A rung that turns out to be a dead letter (its row SUPERSEDED/RETIRED) is removed from the table, never left as decoration — the instrument would otherwise report a MISSING rung forever, and a census that re-reports correctly-retired work trains its readers to skim it.
