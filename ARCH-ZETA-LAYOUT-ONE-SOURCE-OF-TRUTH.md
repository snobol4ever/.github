# ARCH-ZETA-LAYOUT-ONE-SOURCE-OF-TRUTH.md — THE PLAN RECORD IS THE ONE SOURCE OF TRUTH FOR THE THREE ZETAS' LAYOUTS: THE EMITTED CODE, THE COLLECTOR, THE VERIFIER AND THE INSTRUMENTS ALL READ IT (the cto; DESIGN-PLAN written 2026-10-29 18:4x-19:1x CDT on Lon's word, in-chat to the cto, verbatim: *"Yes, let's fix the system have ONE SOURCE of TRUTH for the THREE ZETAS memory layouts. Flush out the the detailed plan and resources for the fleet to walk through and complete."*; the finding is ARCH-GC-COMPILE-TIME-FRAME-MAPS § 17; CEO-1996: the cto designs, the HQs execute, the officers when an HQ fails)

THE PLAN'S RECORD is `corpus/tests/shared/zeta_layout/STEPS.tsv` (seventeen rows in ten steps, each with an executor, a probe and its witnesses) and the step-through harness `harness/scripts/test_design_zeta_layout_steps.sh` (`--list`, `--step N`, `--cut`, `--rows0`); the witnesses are the eight programs beside the table, their refs cut from the oracles (SPITBOL, Arizona Icon, swipl, fpc -Miso, Rakudo), each graded FOUR WAYS: mode 3 and mode 4, plain and under the collector's stress (`SCRIP_GC_STRESS=1 SCRIP_HEAP_KB=128`), because a layout defect is a root the collector cannot see and only a collection that moves the heap shows it.

## 0. The measurement (SCRIP fe4714842, 2026-10-29)

| what | reading | where |
|---|---|---|
| readers of the stack's depth that do not read the plan | 4 (the GC site record, the polls, the spine search, the ZSM expectation) plus the C catchers | § 17 of the GC page |
| the encoder's own depth tracker | `x86_rsp_st_t`, 11 scalars and two snapshot vectors, 18 one-character in-band tags (J D Q E F X Y G K M N k R S U A Z L), the `#@rsp` text notes, a prepass and a real pass; in mode 4 the generated text is re-parsed by `x86_text_sites_scan` and the notes stripped | `x86_asm.h:200-262, 2775-2880` |
| GC site records over the 150-program `gc_witnesses` population, mode 4 | 224,950: rule 0 (rsp-relative, tracker depth) 7,020; rule 1 (rbp) 213,560; rule 2 249; rule 3 433; rule 6 (match-nested) 3,616; rule 7 60; rule 9 12; **rule 5 (unknown, the chain stops) 0** | `SCRIP_GC_SITES_REPORT=1` |
| hand-placed polls | 282 calls of 15 `x86_rt_gc_poll*` helpers in 18 shapes, each a per-site judgement of which registers hold raw heap pointers | `src/templates` |
| rsp moves inside templates outside the carve helpers | 434 (143 push, 113 pop, 102 add rsp, 76 sub rsp) in 38 files | `src/templates/bb`, `xa` |
| runtime calls from templates | 270 bare `x86("call", "sym")` sites naming 161 symbols, 3 through `x86_rtcc_call`; plus `call_bare` | `src/templates` |
| the allocating table | 3,011 rows (1,429 DESCR, 1,213 OTHER, 354 VOID, 15 UNKNOWN), derived from the runtime BINARY by objdump reachability over direct edges, blind to 214 `call *`; read by NO emitter code, only by the unwinder at `gc_heap.c:640`; `#include`d by `gc_heap.c`, which links into the binary it describes; no make rule; re-cut in 407 of the 4,321 commits since 2026-09-18 | `src/templates/x86/gc_allocating_table.inc` |
| the clobber table | derived from the assembled rtx objects by `util_rtx_abi_walk.py`; the entry NAMES are declared (`RTX_NAME` appends to the `rtx_entry_names` section), the masks are not | `rtx_clobber_table.inc`, `rtx_abi.inc:6-8` |
| the spine between frames | found by search: 16-byte units at every 8-byte phase, 14 of 26 tags accepted, 62.9 M words searched for 590 cells on one witness | `gc_cell_visit` `gc_heap.c:2187`, `.Lsw_reject` `rtx_gc.s` (24 lines) |
| the ZSM's expectation | `x86_rsp_slide_known()` returns the constant 1 | `x86_asm.h:638` |
| C roads that set the machine's depth | `rt_return_to_emitted` reloads rsp, rbp, r12-r15 from a saved record (`core.c:2389`); 5 setjmp catchers (`string_ops.c:80`, `arithmetic.c:364`, `runtime_eval.c:364`, `core.c:2384`, `by_name_dispatch.c:19460,19806`), one thread-exit setjmp (`rt_coexpr.c:69`) | `src/runtime` |
| the eight witnesses, four ways | recorded by `--step 0` in the baton the day the plan is minted | STEPS.tsv row 0 |

**Read honestly:** nothing in the population reads rule 5 today, so this design cures no measured collector red. What it removes is the SECOND SOURCE: every one of those 224,950 records is right because an encoder-side interpreter over string tags happened to agree with the plan; the identity run is the only proof the two media agree; a template that pushes across a join reads unknown and the collector would stop silently; the fleet re-cuts a binary-derived table in one commit of ten. Lon's ruling is that the layout is decided ONCE (CEO-1895/1988): this plan makes the record of the decision the only thing anyone reads.

## 1. The malfunction, in Lon's own words

CEO-1895: the memory model is the malfunction; placement is decided ONCE in `src/planner/`. CEO-1988: the emitter reads the plan record and decides nothing. The countdown reads 0 for the emitted code's ADDRESSES. The same stack is described a second time for the COLLECTOR (the site depth from the tracker; the poll shape from the template author; the spine cells from a search), a third time for the VERIFIER (the ZSM's constant), and a fourth time in C (the catcher's snapshot). Four descriptions of one stack, agreeing by test.

## 2. The laws this design is under

- THE THREE ZETAS IN ONE COORDINATE (ARCH-ZETA-ONE-COORDINATE): a FORTH stack of variable-length cells on RSP, each box carving its cell at α and popping at ω; every address a constant distance from rsp; the edge laws; the discard law; a retry never loads rsp from memory; a beta never resets rsp.
- § 7 FROZEN and § 13 of ARCH-GC-COMPILE-TIME-FRAME-MAPS: the maps stay, the chain over the maps is the only walk, nothing tagged beyond F1, no marker scan, no second stack.
- NO C FUNCTION ENTERS A BOX (CEO-1576); NO GLOBAL HOLDS A STACK (CEO-1542); LOGIC LIVES IN EMITTED BOXES (CEO-985).
- NO ACCESSOR LAYER (Lon: deciders deleted, not wrapped); a template reads the row as struct fields.
- NO FIXED LIMIT A PROGRAM CAN REACH (CEO-1210).
- LARGE CHUNKS (CEO-1478): the law and the checker first, then one language small and smoked, then everywhere, then the deletion, then ultracode.
- THE ORDER OF WORK (CEO-1886): every step keeps every suite row at or above its last reading (`rows=`), and a move landing's proof is the coo's identity run (CEO-1992); the lander runs the eight smokes.
- A ROW EXISTS ONLY WHILE A MEASUREMENT SAYS THE PROBLEM EXISTS (CEO-1386): every step's DONE-WHEN is a probe token the harness computes.

## 3. THE DESIGN: THE LAYOUT RECORD

**THE RECORD** is the planner's row (`zeta_plan_t`, the per-node columns E, X, K, the homes, the carves, the discards, the retains, the word kinds, the sites). It is written once by the six passes and read, as struct fields, by FOUR READERS and no fifth:

1. **THE EMITTER** writes addresses from it (done: the countdown reads 0).
2. **THE COLLECTOR'S RECORD** is stamped from it: every GC site's depth and rule, every frame map quad, every spine word-kind mask (§ 4, § 5).
3. **THE VERIFIER** (the ZSM at run time, `SCRIP_ZD_CHECK` at plan time) reads its expectation from it (§ 7).
4. **THE INSTRUMENTS** read it as `--dump-plan` prints it, and the harness checker proves the emitted asm against that dump (§ 8).

**THE FLAT CELL RULE (the one new law, R1).** Inside a box, rsp is constant: it moves only at α (the carve K), at γ/ω (the pop) and at the edge-law sites the planner declares. Every value a template must keep across a runtime call is stored in a word of the box's own cell, declared in `box_cell_shapes.tsv` (the carve grows by the spill words; § 16's word-kind column marks each as DESCR or raw), never pushed. Argument blocks for runtime calls are cell words (the `call_args` width already is). Consequence: the depth at every site inside a box is the row's E + K, by construction, and no excursion exists to track. The one exemption is the ZSM instrument's own balanced push/pop sequence around `rt_zdp_ev`, which creates no site and allocates nothing; the checker names it and skips it.

**R2: THE SITE RECORD IS THE ROW'S.** `emit_gc_site_play` stamps `gc_site_t.depth` from the row (E + K of the node whose body holds the site; rule 0 in the rsp regime, rule 1 in the rbp regime, rules 4 and 9 from `frame_layout.c`'s frame facts, rule 6's match depth from the match construct's row) and takes no `delta`, no `aligned`, no `unknown`. `x86_rsp_st_t`, its 18 tags, the `#@rsp` notes, `x86_text_sites_scan`, `x86_text_rsp_notes_strip`, the prepass and its commit are DELETED. An rsp write inside a box outside the carve helpers is a FATAL at emit in `x86_core_` (the one encoder), never a degraded record. Rule 5 ceases to exist.

**R3: THE SPINE MASK IS § 16 AS WRITTEN.** The word-kind column in the cell-shape table, the planner's fact column (the OR over the carves live on arrival), the site's third quad, the walk visiting exactly the declared words, `.Lsw_reject` deleted.

**R4: THE RUNTIME ENTRY TABLE.** ARCH-BUILTIN-TABLE's table extended to EVERY entry emitted code calls (`harness/scripts/rt_entries.tsv` → `src/runtime/rt_entry_table.inc` by `util_gen_rt_entry_table.py`, gated by `test_gate_rt_entry_table_matches_the_binary.sh`): columns `sym`, `conv` (leaf | gen | open | asm), `rc` (DESCR | OTHER | VOID: what rides rax:rdx at return), `allocates` (0 | 1: the call graph reaches the allocator, a `call *` counted allocating unless its targets are enumerated), `clobbers` (which of the RTCC four the entry hands back changed), `transfers` (may return an address the box jumps to, the `rt_call_next_t` shape). The row is DECLARED where the entry is defined: a C entry through `RT_ENTRY_DECL(sym, rc, alloc)` appending `{sym, rc, alloc}` to the `rt_entry_decl` section (the `RTX_NAME` pattern), an asm entry through `RTX_FUNC`/`RTX_ENTRY` as today plus its mask; the generator READS THE DECLARATIONS and the gate DERIVES from the binary (today's two generators become the checkers) and reds a disagreement by name. `gc_allocating_table.inc` and `rtx_clobber_table.inc` are deleted; the unwinder's `rt_emitted_caller_of_descr_call` reads the section. The make rule `make rt-entry-table` regenerates the .inc from the TSV (the harness gate keeps checking currency).

**R5: ONE CALL, ONE POLL.** `x86_call_rt(sym)` is the only way a template calls the runtime: it reads the row and emits the call, then the poll if `allocates`, then the clobber re-establishment from `clobbers`; `x86_gc_poll()` is the only poll shape, because under R1 every live value is already in a declared cell word the mask names, so the poll records no registers (the result pair rax:rdx is stored to the node's result cell before the poll and reloaded after, two moves the row's `op_zres` addresses). A call to an entry with no row, or to an allocating entry with `transfers` set but no `open` convention, is FATAL at emit. The 15 helpers and the 270 bare calls go.

**R6: THE VERIFIER READS THE ROW.** `x86_rsp_slide_known()` is deleted (ARCH-ICON-RTX § 11.9: the planner's column says when an operand is unplaceable downstream of a retaining gamma, and the ZSM event passes -1 from the row); `util_zsm_declared_census.sh --lang L` reads 0 mismatches in both modes for every language, the finish line of ARCH-THREE-ZETAS-EMISSION § 9.3 per language.

**R7: THE RBP ZETA AND THE STANDING CELLS.** Every frame-map quad (`GC_LAY_Q`) is produced in the planner (`frame_layout.c`, `plan_facts.cpp`), none in `emit.cpp`; every frame reference the emitted code makes lands in a granted cell (`util_frame_refs_land_in_grants.py`, hq_zetas' CEO-2018 row, wired as `test_gate_every_frame_reference_lands_in_a_granted_cell.sh` at 0); the standing root cells at `[r14 - 24 - 8k]` are rows of the root graph's plan.

**R8: NO C ROAD WRITES THE DEPTH.** A C raise RETURNS: `FAILDESCR` with the error armed in the context record (the Prolog ball road's shape: the ctx BALL slot, `PL_BALL_ARM` in every thunk, r15 in the boxes, the gate restoring rsp to ITS PLANNED depth by `x86_pl_ball_rule_omega`), and the emitted box's ω road unwinds through the discards the plan declared; SNOBOL4's SETEXIT/&ERRLIMIT and Icon's &error adopt the same shape; `rt_return_to_emitted` and the five catchers' longjmp are deleted (the co-expression thread's exit setjmp is a thread exit, not a depth restore, and stays). This is the C-side instance of the same flaw and is step 9; its exact cut per language is written when step 3 has landed (the cto's).

## 4. What the record carries per node (the columns, existing and new)

| column | exists | written by | read by |
|---|---|---|---|
| E, X, K (depth at α, depth at γ, the carve) | yes | zeta_depth / zeta_plan | emitter (addresses), **site record (R2)**, ZSM, checker |
| gpop, wpop, restore (the edge laws, the discard) | yes | zeta_plan | emitter, ZSM |
| homes, retains (reason code), owner, fenced | yes | planner_retains, frame_layout | emitter, maps |
| carve word kinds (one bit per 8-byte word, DESCR or raw) | § 16 | box_cell_shapes.tsv → zd_k_own | **spine mask (R3)**, checker |
| live mask at the node (OR over the carves live on arrival) | § 16 | plan_facts | **site third quad (R3)** |
| spill words of the box (R1): offsets and kinds | NEW (TSV rows) | box_cell_shapes.tsv | templates (store/reload), mask |
| downstream-of-retaining-gamma (the ZSM's -1) | NEW | plan_facts (`zd_edge_retains_g`) | **ZSM event (R6)** |
| frame regime (rsp | rbp | aligned-prologue | shim-self), the site rule | partly (zeta, frame facts) | frame_layout | **site record (R2)** |
| match depth (rule 6) | partly (fcb, fcbase, in_scan) | planner | site record |

## 5. The harness checker (step 1, before any move): `harness/scripts/util_zeta_layout_check.py`

Inputs: a program's mode-4 asm (`--asm run.s`) and its plan dump (`--plan plan.txt`, from `./scrip --dump-plan`). It is the ONLY legitimate place our own asm is re-parsed, because it is an instrument, not the compiler. It proves, per box (the asm's `n<idx>_<kind>_α` labels bracket a box; `--dump-plan`'s `PLAN_ROW i=<idx>` is its row):
1. the carve at α is `sub rsp, K` (or none when K = 0) and the pop at γ/ω matches the edge law;
2. no rsp write inside the body other than the carve, the pop and the declared edge sites (R1): each one found is an EXCURSION line `graph box pc insn bytes`;
3. every GC site record whose pc lies in the box (the `.Lgcsites_*` table: `{pc_off, w}` quads, `depth = w >> 32`, `rule = (w >> 16) & 255`) reads depth = E + K in the rsp regime, rule 1 in the rbp regime (R2);
4. once R3 lands: the site's third quad names exactly the DESCR words the carve stack declares.
Output: one line per finding, then `mismatches=N` (the harness's `layoutcheck=N` token reads it). Negative control, in a worktree never in src (CEO-1680): a wrong K in `box_cell_shapes.tsv` reads at least one line; a removed poll reads an EXCURSION or a missing site. Step 1's reading over the eight witnesses is the baseline the steps lower to 0.

## 6. THE STEPS (STEPS.tsv is the record; executors by CEO-1996's lanes; the cfo when an HQ fails; the ceo seats)

0. **THE BASELINE** (the cto): the eight witnesses four ways; `rule5=0`, `rspmoves=434` recorded. Read today the day the plan is minted.
1. **THE LAW AND THE CHECKER** (hq_templates): R1 written into ARCH-ZETA-ONE-COORDINATE § 6 as the eighth forbidden thing (an rsp move inside a box); `util_zeta_layout_check.py` as § 5, its negative control, its reading over the eight witnesses in the baton. No compiler change. Finish: `layoutcheck` REFUSES nothing and reads; the control reds.
2. **THE FLAT CELL RULE IN THE TEMPLATES**, one language at a time (2a SNOBOL4 and the shared templates, the cfo; 2b Icon, hq_icon; 2c Prolog, hq_prolog; 2d Pascal, hq_pascal; 2e Raku, hq_raku): each template's push/pop around a runtime call becomes a store into a cell word declared as a `box_cell_shapes.tsv` row for the op (the carve grows; the word kind declared); argument blocks the same. Finish per language: `layoutcheck=0` over that language's witnesses (no EXCURSION), `smoke=L`, `rows=L`; the asm moves, so the proof is the coo's identity run under CEO-1992, LINE class or better.
3. **THE SITE RECORD FROM THE ROW; THE TRACKER DELETED** (the cfo): R2. Finish: `nosym=x86_rsp_st_t,x86_text_sites_scan,x86_rsp_prepass_open,x86_rsp_mark_save,x86_rsp_land,x86_rsp_rec`, `grepmax=#@rsp@src/templates:0`, `rule5=0`, `layoutcheck=0` over all eight, `smoke=ALL`, `rows=ALL`; the site TABLE's data must not move (the identity proof's LINE-ONLY class: the coo).
4. **THE SPINE MASK** (4a the column, the fact, the third quad: hq_zetas; 4b the walk reads it, the search deleted: hq_collector). Finish 4a: `gate=test_gate_box_cell_shapes_inc_is_current`, `smoke=ALL`, the third quad present (`grepmax=Lsw_reject@src/runtime/rtx/rtx_gc.s:24` unchanged). Finish 4b: `grepmax=Lsw_reject@src/runtime/rtx/rtx_gc.s:0`, `gate=test_gate_gc_the_spine_walk_is_told_its_cells` (§ 16's census arm: the told walk and the old search visit the same cells over the gc_witnesses at stress 1 and 3), `smoke=ALL`, `rows=ALL`.
5. **THE RUNTIME ENTRY TABLE** (hq_templates the table, the generator and the gate; hq_runtime the declarations at the definitions): R4. Finish: `tsvmin=rt_entries.tsv:160`, `gate=test_gate_rt_entry_table_matches_the_binary`, `nofile=src/templates/x86/gc_allocating_table.inc,src/templates/x86/rtx_clobber_table.inc`, `nosym=GC_ALLOC_TAB,rtx_clob_tab`, `smoke=ALL`.
6. **ONE CALL, ONE POLL** (the cfo, by template family, each family smoked): R5. Finish: `grepmax=x86\("call",.?"[a-zA-Z_0-9]+"@src/templates:0`, `grepmax=std::string.x86_rt_gc_poll@src/templates/x86/x86_asm.h:1`, `rule5=0`, `layoutcheck=0`, `smoke=ALL`, `rows=ALL`.
7. **THE VERIFIER READS THE ROW** (7a hq_icon: § 11.9; 7b hq_zetas: every language's ZSM census 0 both modes). Finish: `nosym=x86_rsp_slide_known`, `smoke=ALL`; the census readings in the baton.
8. **THE RBP ZETA AND THE STANDING CELLS** (hq_zetas; the CEO-2018 row): R7. Finish: `gate=test_gate_every_frame_reference_lands_in_a_granted_cell`, `grepmax=GC_LAY_Q\(@src/emitter:0`.
9. **NO C ROAD WRITES THE DEPTH** (hq_runtime; the cfo on failure; the cut written by the cto when step 3 lands): R8. Finish: `nosym=rt_return_to_emitted`, `grepmax=setjmp\(@src/runtime:1`, zl02, zl04 and zl06 GREEN four ways, `smoke=ALL`, `rows=ALL`.
10. **THE FINISH** (hq_templates closes; the coo's identity run and `util_gc_acceptance.py` at 100%; then Lon runs ultracode): `rule5=0`, every `nosym`/`nofile` of steps 3, 5, 6, 7, 9 together, `rspmoves=24` (the ZSM instrument's own balanced sequence and nothing else), `layoutcheck=0`, `smoke=ALL`, `rows=ALL`.

## 7. What a builder must not do

- Teach the tracker the row. It is deleted, not fed (Lon: deciders deleted, not wrapped). Until step 3 it may stay as a VERIFIER whose disagreement with the row is a FATAL, never a record.
- Add a tag, a note, a text re-scan, a side table, a marker, a second stack, a tagged cell, a pre-carved maximum, a per-language emitter branch (ARCH-ZETA-ONE-COORDINATE § 6, now with R1 as its eighth clause).
- Hand-write a poll. After step 6 the poll comes from the row or the compile is FATAL.
- Check in a table derived from a binary. After step 5 the binary CHECKS the declaration; nothing is derived into src.
- Cut a byte bar. A gate asserts a RULE (0 excursions, 0 ungranted references, 0 rule-5 sites), never a frame size.
- Land a core step behind a feature landing (the Pascal lesson, CTO-411).
- Call `done` on a step the harness has not graded GREEN; `S4E_DONE_OVERRIDE` is the ceo's.

## 8. Resources for the executors

- `./scrip --dump-plan prog` (the record, one PLAN_ROW per node); `SCRIP_GC_SITES_REPORT=1 ./scrip --compile prog` (every site record with its rule and depth); `SCRIP_ZD_CHECK=1` (the edge laws at plan time); `SCRIP_ZSM=1 SCRIP_ZSM_ALL=1` (the verifier at run time); `SCRIP_GC_RSP_TRACE=1` (the tracker's own trace, until step 3).
- `harness/scripts/util_zeta_layout_check.py` (step 1), `test_design_zeta_layout_steps.sh --step N`, `util_zsm_declared_census.sh --lang L`, `util_frame_refs_land_in_grants.py`, `util_population_asm_identity.sh --control` (the coo's), `util_gc_acceptance.py`, the 150 programs of `harness/scripts/gc_witnesses`.
- The pages: ARCH-ZETA-ONE-COORDINATE (the coordinate and the forbidden list), ARCH-THREE-ZETAS-EMISSION § 9.3 (the regime switches per language), ARCH-GC-COMPILE-TIME-FRAME-MAPS § 7, § 13, § 16, § 17, ARCH-ICON-RTX § 11.9, ARCH-RT-CALL-PROTOCOL § 15 (the leaf contract), ARCH-BUILTIN-TABLE (the table this one extends), ARCH-X86-ASM-ENCODER.
- A red the coo's loop finds reaches the lander by telegram with the range; cure or revert within the tick (CEO-1928).
