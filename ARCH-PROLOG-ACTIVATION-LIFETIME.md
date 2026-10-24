# ARCH-PROLOG-ACTIVATION-LIFETIME.md -- THE PROLOG ACTIVATION'S LIFETIME AND THE PLACEMENT OF EVERY CELL OF THE PROLOG REGIME, UNDER ONE PAGE

Written by the cfo 2026-10-24 13:2x CDT as Prolog's design seat (the ceo's word of 13:1x on Lon's: *"I have CTO and CFO seated as Fable 5.1 for a purpose, give it re-design and the toughest problems."*; the cfo rules the Prolog activation's lifetime and every D3 placement decision, the cto is told each ruling and nobody waits on review). Under RULES.md: THE LIFETIME RULE (CEO-1354), THE MEMORY MODEL IS THE MALFUNCTION (CEO-1895: placement decided ONCE, in the planner), RSP IS THE DEFAULT HOME OF EVERY CELL (CEO-1942), THE SPINE (ARCH-ZETA-ONE-COORDINATE.md, CEO-1826/1830), THE THREE ZETAS (ARCH-THREE-ZETAS-EMISSION.md, the cto's page: a template reaches a cell through ZALPHA, ZOMEGA, ZGAMMA, ZDISCARD, ZCELL and nothing else). This page says what the Prolog regime's cells ARE and WHERE each lives; the cto's page says how a template reaches them. A ruling here changes only by a later ruling here, dated.

## 1. THE ACTIVATION

A Prolog ACTIVATION is one clause of one predicate entered once: the construct whose lifetime the clause's cells are tied to. It is born at the clause's entry (the frame header is written, rbp links to the caller's frame) and it DIES at the last of three moments: (a) its deterministic exit -- the clause succeeded and left no choice point of its own or of any callee below it; (b) the failure that backtracks past its entry; (c) the cut or the construct exit that drops its last choice point. Between (a) and the later of (b)/(c) an activation that left a choice point is RETAINED: its frame stays live on the machine stack below the caller's continuation while the caller runs on. That retention is the whole difficulty of the regime and the single source of every unbounded situation in it:

- after a RETAINING CALL (the callee's activation retained) the caller's rsp is NOT the rsp it had before the call: the callee's live frame and cells sit between -- the depth is INDEFINITE for the rest of the caller's continuation until the retained frame is dropped;
- a GENERATOR'S RESUMPTION (a range `between/3`, a db walk over clauses, a disjunction's next arm, a retained callee's next solution) re-enters a box at a depth the box did not leave it at -- a retry never restores rsp (CEO-1755/1759);
- a RECURSION is a retaining call by nature when any clause of the predicate leaves a choice point.

Lon's CEO-1942 names these three as the ONLY reasons a cell leaves rsp: *a generator's resumption, a retry after an unknown number of pushes, a recursion*. The Prolog regime has nothing else.

## 2. THE THREE HOMES IN THE PROLOG REGIME

- **ζ-SPINE** `[rsp + c]`: THE DEFAULT. Each box carves exactly the cell it needs at its α and pops it at its ω; a local is carved at first use; every address is a compile-time constant distance from rsp. A cell lives here when every read of it happens at a KNOWN DEPTH relative to its carve -- no unbounded excursion between the write and the read.
- **ζ-ACT** `[rbp - off]`: the ACTIVATION FRAME, one block per clause activation, carrying the frame header and ONLY the cells the spine cannot reach: a cell written before an unbounded excursion and read after it, or a generator's own resumption state. A cell here is RESIDENT: `zls_hf_resident(g, nd)` admits its box, the layout grants its words inside the frame region (`zls_build`, below `zls_hf_key_base`), and `FRQ(off)` addresses it through rbp. A key granted ABOVE the resident region on a home-frame graph has NO FRAME BYTES behind it (`zls_key_unbacked`), and a read of one is the FATAL in `x86_zop` -- the scream that is the work list of D3.
- **ζ-STANDING**: the root frame (mode-3 main's or the program's), reached by walking the rbp links to the null link. Prolog's standing cells are the trail header's and the database's handles; none of the clause's own.

THE SWITCH: every Prolog graph is a HOME-FRAME graph (`g->home_frame = 1` in `pl_graph_stamp`, lower_prolog.c, kept at SCRIP 4edf4b785 and never restored: Lon, CEO-1945, *"keep it whacked and fix the misplaced ones by changing that carve logic to be proper"*). The frame is sized by its RESIDENT words, never by keys (CEO-1895's 338,540-slot frames were keys).

## 3. THE ONE DECIDER

A cell's home is decided ONCE, in the planner, from a FULLY CLASSIFIED program, by ONE test:

**THE UNBOUNDED-EXCURSION TEST.** A node is an excursion when `zd_edge_retains(nd)` (planner_retains codes PR_UNKNOWN_CALLEE, PR_GATE_HOLDS, PR_DISJUNCTION_HOLDS, PR_DB_GENERATOR, PR_RETAINING_TARGET on a resumable frame), when it is an IR_SUSPEND, or when it is a retaining IR_DISJUNCTION (`zls_dj_retains`). A SPAN of a graph carries an excursion when any node in it does: `planner_span_retains(g, from_ai, to_ai)`, exported from src/planner/zeta_plan.cpp (the cfo, 2026-10-24), is the one function that answers it, for the home pass, the cell shape and the variable rule alike. A second copy of this test anywhere is a defect of this page's class.

**THE FULLY-CLASSIFIED-PROGRAM RULE** (hq_prolog's finding, 2026-10-24; the cto carries it on ARCH-THREE-ZETAS section 6): every placement predicate is a function of a program whose EVERY graph is classified -- `fl_derive_tier` (zframe_graph), the retains facts, `zls_build`'s hf -- never of the graph order. Three instances of two deciders were found and cured on 2026-10-24: (i) `drive_slots_all` laid out graph 1 before graph 59 was classified, so `bb_proc_target_retains(main/0)` read 0 at layout and 1 at emit (cured on main at SCRIP 72c59a9d6: every home-frame graph classified before any is laid out); (ii) `zls_build` assigned `r->hf` AFTER the resident and key loops that read it through `zls_g_home_frame`, so no home-frame residency clause ever fired during the layout (cured on the D3 branch at b0136fbb3); (iii) `planner_home_dyn` demoted PR_RETAINING_TARGET to a dyn only when `zls_fcn_hret` said the callee locally retained -- false for a one-clause fact -- so findall's accumulator, written before the call and read after its γ, was read from a popped spine and `findall(x, c0, L)` gave `[]` (cured on the branch at 5161a8e01: a home-frame graph's IR_CALL_PROC_STAGED whose `planner_edge_retains` is true is a dyn, why 5). The census instrument cannot see class (iii): the reads are backed; only output can, which is why the real grade (section 6) runs beside the census.

## 4. THE RULINGS BY KIND (the Prolog regime's cell-shape rows, harness/scripts/box_cell_shapes.tsv; K is the spine carve in bytes)

| Kind | Cell(s) | Home | Ruling and its measurement |
|---|---|---|---|
| IR_CALL_PROC_STAGED, definite callee | header 32 + act 16n | SPINE | batch 1 / kind 1 (hq_prolog, 11b001abc): a call whose callee leaves no choice point keeps header and act on the spine |
| IR_CALL_PROC_STAGED, RETAINING callee | header 32 on the spine; the act RESIDENT | SPINE + ACT | kind 1: the act is read at γ across the retaining excursion (CEO-1942: a retry after unknown pushes); granted resident through the retains table's row, never a wider K; cef8cac8b: the tail arm declines a variable fast path on a slot no frame byte backs |
| a VALUE produced before a retaining call and read after it | its producer's result | ACT (home local) | hq_prolog 5161a8e01, why 5: the home pass homes it; the generalization to every excursion kind reads planner_span_retains |
| IR_CALL_VALUE (call/N) | result 16 | SPINE | kind 2 (hq_prolog): nothing to carve; a 22-goal call/N probe byte-equal to swipl in m3 and m4 |
| IR_BOUND + IR_GATE (if-then-else, negation: pl_lower_ite) | the construct's RECORD: mark, rsp at entry, banked B, the live-arm index -- 32 bytes | SPINE record carved at the BOUND's α, popped at the GATE's ω; ACT when the construct's span carries an excursion | RULING of 13:1x (the cto's shape of its review, kept as the cfo's): the fence's UNMARK restores from the plan to the depth ABOVE the record (the discard law: a restore lands at the depth its continuation is entered at), the THEN arm runs at record+0, GATE_ARM writes the index at a fixed distance into the record, the GATE's β reads it there. Decided per construct through planner_span_retains over [BOUND, GATE]. INTERIM on the branch (batch 2, b0136fbb3): the record RESIDENT by TEST 2 -- correct, not yet the default shape; batch 3 (the cfo) lands the ruling |
| IR_UNMARK, IR_GATE_ARM | none | -- | K 0 (control: the fence's whack-pop and the arm's index write) |
| IR_TO, range (between/3, integer ranges) | cursor, limit, step: the 64-byte range state | ACT, wholesale for the kind | RULING of 13:1x: a generator's resumption state is written at α and read at β across the whole continuation; a generator's resumption is CEO-1942's named unbounded situation, so no per-construct test. Measured by hq_prolog: resident, between-in-a-disjunction prints 1 2 3 and findall over between gives [1,2,3] (branch before: 1 and [1]). The TO's OPERANDS (the packet at op_sa+8) are values read after the excursion: home locals (why 6). hq_prolog's kind 4 |
| IR_TO, db walk (retract/1, clause/2) | the enumeration state and the packet | ACT | the same ruling; a second defect in bb_to_db's packet read against the carve: hq_prolog 24546d67e (core 31 -> 37 of 52) |
| a CLAUSE VARIABLE (read by IR_VAR, IR_VAR_REF, IR_UNIFY_CONST, written by IR_UNIFY_FIRST / IR_ASSIGN) | one 16-byte DESCR slot | SPINE, carved at first use at the α of the first box that writes it; ACT when the span from its first write to any read carries an excursion | RULING of 13:1x, built by hq_snobol4 (kind 3): decided per variable through planner_span_retains; in Prolog most variables come out ACT because nearly every body has a call between a write and a read -- that is the measurement, not a shortcut. Today a non-home variable is granted slot -2 (a pure key) and its read is the FATAL: 24 of the 31 unbacked reads left on the 52 cores |
| IR_CLEANUP (setup_call_cleanup) | the record: link, B_s, state, the cleanup goal C | ACT | by construction: its goal is the excursion; 7 of the 31 reads left |
| IR_DISJUNCTION | arm header (arm_spine_hdr) | SPINE | batch 1: `arm_spine_hdr` when the box has operands; a retaining disjunction is itself an excursion for the span test; its own cells' residency is OPEN (section 7) |
| IR_CUT | none | -- | the cut drops choice points on the r12 island (Lon's second island, CEO-1542); no cell |

THE TWO ISLANDS (Lon, CEO-1542): the Prolog TRAIL and CHOICE POINTS live on the r12 mmap'd slab, LIFO with a choice point, never with a frame; nothing of them is a frame cell, and a frame cell never holds a choice point. A box that needs the trail's cleanup cell (bb_cleanup) reads it through the trail header at +32, never through a frame.

## 5. THE ORDER OF THE WORK (D3, row 233)

1. The switch kept; every unbacked read a scream (SCRIP 4edf4b785). 2. Each screaming kind its proper carve by this page's rulings, one kind per landing, each kind a row under one HQ (hq_prolog: calls and the generators; hq_snobol4: the variables and the cleanup record; the cfo: the constructs BOUND/GATE/UNMARK/GATE_ARM/DISJUNCTION and the planner). 3. When the census reads 0 everywhere: the REAL GRADE -- test_smoke_prolog.sh in all three modes, the Prolog core in m3 and m4 (progress off), every red bisected to its kind. 4. Large chunks to origin (CEO-1478), the coo grading on request; row 233's DONE-WHEN: `test_gate_no_spine_preallocation.sh --lang prolog && test_gate_frame_homes_agree_with_lons_tests.sh --lang prolog`. 5. ZCELL: when the cto's accessor contract is on origin, the Prolog templates are re-pointed at ZCELL and the FRQ/ZRES forms fall (util_zeta_accessor_census.py).

## 6. THE MEASUREMENTS (the branch wip/cfo/prolog-switch-2026-10-24, SCRIP and harness)

The INSTRUMENT: `harness/scripts/util_zop_unbacked_census.py` -- a scratch git worktree of the seat's SCRIP (never a link) with the FATAL swapped for a count line (`ZOP_UNBACKED off= op= regime= zres= own= k_own= gs= ai=`), built and run over a program set; `--core prolog` materializes the 52 core entries by name (CEO-1676), `--op K` grades one kind; rc 0 iff the graded count is 0. It is a script's own switch, never a seam in SCRIP (CEO-1680).

| Reading | prelude (empty program) | six smoke programs | 52 cores |
|---|---|---|---|
| the switch alone (4edf4b785^) | 1,431 | -- | -- |
| batch 1 (4edf4b785) | 34 (UNMARK 11, GATE_ARM 8, CALL_PROC_STAGED 8, GATE 7) | -- | -- |
| batch 2 with r->hf still late | 136 | -- | -- |
| batch 2 (b0136fbb3) | 8, all CALL_PROC_STAGED | 8,8,8,0,0,8 | UNMARK 866, GATE_ARM 639, GATE 520 before batch 2 |
| kind 1 + batch 2 (2c36a604f) | 0 | 0 | 27: VAR_REF 11, VAR 8, CLEANUP 7, UNIFY_CONST 1 |
| + cef8cac8b, 55 programs incl. the two demos | 0 | 0 | 31: VAR_REF 15, VAR 8, CLEANUP 7, UNIFY_CONST 1 |

THE REAL GRADE (hq_prolog, S4E_PROGRESS_OFF=1): test_smoke_prolog.sh 6/6 in all three modes at 5161a8e01; the Prolog core by corpus_suite_harness.py m3 31/52 and m4 31/52 at 5161a8e01 (base 9934db1be 51/52), 37/52 at 24546d67e (the db walk); the branch reds: 5 ABORTS (the variable and cleanup kinds, hq_snobol4's) and the rest SILENT mismatches, the bulk the range-TO cluster (hq_prolog's kind 4), the remainder unbisected. The 8 silent mismatches of class (iii) are exactly the mode-3 corruption CEO-1895 named: corrupted memory grading as FAIL, not segv.

## 7. OPEN, IN THE ORDER THEY ARE TAKEN

- Batch 3 (the cfo): the ite record to the spine as ruled; the fence's restore from the plan; the per-construct ACT decision through planner_span_retains; the unarmed gate road (`flat_drive_gate` under `g_zd_arm=0`) named and left: with the index in the BOUND's record the GATE's K stays 0.
- The negation construct (`\+`, pl_lower_negation ~1005) shares the ite's shape and takes the same ruling in the same batch.
- IR_DISJUNCTION's own cells on a home-frame graph: measured 0 unbacked reads on the prelude and the cores after batch 1; a silent class may remain -- the core grade says.
- findall's BOUND with a generator inside (`findall(X, between(1,3,X), L)`): cured by the TO ruling or by the ite ruling's ACT arm -- the real grade after kind 4 says which.
- The planner core (the ceo's hand-over of 13:1x, the cfo): the generator's γ law (h3), the arm-run base (a6), DISJUNCTION admission with a shared tail (ipl based), Raku's generator-graph locals; written on ARCH-THREE-ZETAS-EMISSION and landed as one planner change after D3's kinds are in. Site 2 (the CLASS-C parameter block) behind it.
