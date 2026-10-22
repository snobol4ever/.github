# ARCH-PROLOG-TABLING-BOXES — A TABLED CALL IS A BOX; ITS EVALUATION STATE IS THE BOX'S HEADER (cfo, 2026-10-22, CFO-324)

**Status: DESIGN OF RECORD, AS BUILT (§§ 2-6 rewritten 2026-10-22 09:1x CDT to the shape CEO-1885 ruled; the first draft's IR_TABLE_EVAL drive loop was not built).** Lon, in-chat to the cfo, 2026-10-22 07:1x CDT, verbatim, after asking *"Why is
Prolog caching query answers? Is it not using BB's properly? The memory should be the state of which BB Box the program is in. Should
it not? Is Prolog BB's designed properly?"*: *"You better get that tabling mess fixed and start using BB's properly."* This document
supersedes ARCH-PROLOG-WFS-TABLING.md § 2 and § 3.1 as to WHERE THE STATE LIVES and WHO SCHEDULES; its algorithm (rounds to a
fixpoint, the alternating fixpoint, the residual pass) is kept, because it is what makes today's files read green.

## 0. What is wrong today (measured on SCRIP 26cfecaab plus the cfo's nine held commits)

- The scheduler is Prolog text inside `src/parsers/prolog/prolog_parse.c` (`PL_PRELUDE_SRC`, the `'$tbl_*'` family, lines ~1949-2200).
- Its state lives in twelve named global cells: `'$tbl_inprog'` (every incomplete table under the leader -- one entry per evaluation in
  progress, the shape CEO-1542 forbids), `'$tbl_leader'`, `'$tbl_dep'`, `'$tbl_wfs'`, `'$tbl_ph'`, `'$tbl_wnew'`, `'$tbl_mx'`,
  `'$tbl_used'` (nb_setval), `'$tbl_ctx'`, `'$tbl_cpos'`, `'$tbl_dl'` (b_setval), `'$tbl_incr'` (a list that only grows).
- 45 `nb_setval`/`b_setval` sites on those names. One leader at a time: everything entered under the outermost tabled call is one
  component, completed together at its end. XSB `tabsimp_seq` runs 7 s against swipl's 0.09 s.

## 1. The rule

**The memory of a tabled evaluation is the state of the box doing it.** A table's ANSWERS outlive every call that made them, so they
live on the heap (THE LIFETIME RULE) in the trie the runtime already has (`HB_TRIE`, traced, rooted off the program registry). The
EVALUATION -- which tables are in progress, who leads, which round, which phase, what changed -- lives exactly as long as the
generator that is evaluating, so it lives in that generator's HEADER, in the op slots of its box on the machine stack. Nothing else
holds evaluation state.

## 2. The shape, as built (CEO-1885 (a): a header-only box; compiled Prolog IS boxes)

A tabled `p/N` keeps today's renaming (`'$tbl p'/N` holds the clauses; lower's `pl_table_rewrite`, the loader's `'$lfx_wraps'`) and
today's entry, `'$tbl_call'(G, I)` -> `'$tbl_get'` -> `'$tbl_enter'`. What changed is WHERE THE EVALUATION'S STATE LIVES. The goal
`'$tbl_hdr'` lowers (`lower_prolog.c`, `goal_inner`) to one box kind, **IR_TABLE_HDR** (`bb_table_hdr.cpp`): at α it writes the
address of its own frame cells into its first slot and calls the open leaf, which banks the current header in cell 0 and makes this
header current; γ continues; β fails back. The predicates that schedule an evaluation are ordinary Prolog compiled to ordinary boxes,
and they reach the evaluation's state only through leaves that read and write the CURRENT header's cells:

| leaf | does |
|---|---|
| `'$tbl_hdr'` | IR_TABLE_HDR: open a header in this clause's frame (cells 1-9 start as forwards to the nearest owning header's cells) |
| `'$tbh_own'(F, V)` | write cell F of THIS header: this header now owns F for every header opened inside it |
| `'$tbh_set'(F, V)` / `'$tbh_bset'(F, V)` | write the cell F of the nearest header that owns F (bset: trailed, so backtracking restores it) |
| `'$tbh_get'(F, V)` | read the cell F of the nearest header that owns F (fails when none does) |
| `'$tbh_close'` | restore the banked header as current (the clause's last step before it succeeds) |
| `'$tbh_leading'` | succeed when some header is current, i.e. an evaluation is in progress |

Four clauses open a header, each owning the cells whose lifetime is its own: `'$tbl_lead'` (the leader: cells 1-4), `'$tbl_eval1'` and
`'$tbl_eval1n'` (one table's evaluation: cell 5), `'$tbl_eval'` (one semi-naive pass: cells 6-9). What used to be a global saved in a
clause variable on entry and restored on exit (`'$tbl_cell'(K, D, V0), nb_setval(K, ...), ..., nb_setval(K, V0)`) is now a cell of the
header the clause opens: the save and restore are the frame's own lifetime.

## 3. The header (IR_TABLE_HDR's op slots; typed by the frame map, ARCH-GC § 7)

**RULING (the cto under CEO-1888, 2026-10-22, on the as-built header the cfo described: `IR_TABLE_HDR`, twelve DESCR frame cells at `[rbp + off]`, cell 0 the banked previous header, cells 1-9 the evaluation state, made current through the one trailed root cell `$tbl_cur`).** The header is a STATE WORD of its box, class **address-escapes** (ARCH-ZETA-ONE-COORDINATE § 3.1): its address is handed to the open leaf at α and read by the phase leaves while the tabled call's child runs, and that child retains (an incomplete table's consumer is re-entered round after round), so no fixed rsp distance reaches it and it stays in the RBP frame by Lon's TEST 2. It is therefore NOT a pre-allocation and NOT an operand home: `--dump-homes` prints it `home=RBP xfwhy=address-escapes` with `HOMETEST test=state:address-escapes`, the census reads the kind from `state_word_kinds.tsv` (the cfo adds the row with its landing, citing the template line that takes the header's address) and counts the home as **agree**, and `loc_rbp_misplaced` never counts it. Under the `home_frame` fact the lowerer marks the box resident (`zls_frame_resident_mark` at `bb_program_add`, or a third `zls_frame_word_why` class once the instrument exists) so the twelve cells lay in the resident region. The rounds and phases being ordinary compiled Prolog in `prelude/tabling.pl` reading the cells through leaves is consistent with THE LIFETIME RULE and CEO-1542 (the chain of live generators is the chain of headers on the machine stack); § 2-3 are the cfo's to rewrite to the as-built shape, and that rewrite is accepted in advance under this ruling. (cfo, landing note: the header landed with TABLE_HDR_CELLS = 10 -- cell 0 and cells 1-9; the two spare cells of the scratch build went in the landing, SCRIP ed4428fbb; the state_word_kinds.tsv row and the census reading it landed at harness ed2992f: BB_PLACEMENT_STATE prolog key=IR_TABLE_HDR class=address-escapes, rbp_forced, never rbp_misplaced.)

`zls_grant_locals` grants the box one 16-byte slot for the header's address (`{DT_I, base}`, the open leaf's argument) and
TABLE_HDR_CELLS DESCR cells after it, at a compile-time constant `rbp` offset (the emitted α reads `lea rax, [rbp + off + 16]`); every
cell is a DESCR the collector visits by the frame map, never a raw word. A cell holds a value (this header owns it) or a `DT_RAW`
forward to the owning header's cell, written by the open leaf, so a read or write is one indirection, never a walk.

| cell | was | holds |
|---|---|---|
| 0 | -- | the banked previous header, `{DT_I, address}` or 0 |
| 1 | `'$tbl_inprog'` | the incomplete tables of this leader's component |
| 2 | `'$tbl_wfs'` | raised to the alternating fixpoint (a `tnot` met an incomplete table) |
| 3 | `'$tbl_ph'` | the phase: 0, t, u, r |
| 4 | `'$tbl_wnew'` | a WFS pass found a new answer |
| 5 | `'$tbl_dep'` | the least depth of an incomplete table this evaluation consumed |
| 6 | `'$tbl_ctx'` | the semi-naive context: all, or sn(Round, Snapshots) (trailed) |
| 7 | `'$tbl_cpos'` | the consumer position counter of this pass (trailed) |
| 8 | `'$tbl_mx'` | the highest consumer position seen |
| 9 | `'$tbl_used'` | the tables this pass sliced |

**The one register (CEO-1885 (b)).** The address of the CURRENT header lives in one root cell of the program registry
(`'$tbl_cur'`, set by `rt_pl_b_set`, trailed unconditionally -- the cto's third condition), the one "current X" cell CEO-1542 allows:
every header banks the previous value and `'$tbh_close'` restores it, and a failure or a ball restores it through the trail. The chain
of live evaluations IS the chain of headers on the machine stack; no list of evaluations exists anywhere.

**The delay list (CEO-1885 (c), the cto's 2026-10-14 ruling).** One current value, replaced on backtracking, in one root cell
(`'$tbl_dl'`) behind two leaves, `'$tbl_dlget'/1` and `'$tbl_dlset'/1` (trailed unconditionally); a nested derivation saves the outer
list in a clause variable and restores it (`'$tbl_fa'`, `'$call_delays_m'`). The incremental predicates are `'$tbl_incrp'/1` facts in
the database (`'$tbl_icall'`, `'$tbl_isincr'`).

## 4. The algorithm (today's rounds, its state in the headers)

1. **Enter.** `'$tbl_enter'` makes the variant's table and, under a current header, adds it to cell 1 and evaluates it nested
   (`'$tbl_eval1n'`); with no header current it LEADS (`'$tbl_lead'` opens the leader's header).
2. **Evaluate.** `'$tbl_eval'` runs the clauses to exhaustion in a semi-naive pass, consumers reading the answers found so far through
   cells 6-8 and recording what they sliced in cell 9.
3. **Complete.** A nested evaluation that consumed nothing older (cell 5) completes at once; an SCC whose consumers stay inside it runs
   its own rounds and completes (`'$tbl_srounds'`, `'$tbl_scc'`); otherwise the leader's rounds run to a fixpoint, then the alternating
   fixpoint and the residual pass when cell 2 was raised, then every table in cell 1 completes.

**Not built yet (the speed step, CEO-1886 rank 3).** Linear tabling's per-depth leader/follower scheme (Zhou, Shen and Sato, TPLP 8(1)
2008): every generator a header, its `low` the least depth any consumer under it read, a follower handing its tables up to the banked
header. That is what turns XSB `tabsimp_seq` (7 s against swipl's 0.09 s) from O(N) rounds of O(N) work into linear work; it changes
the algorithm, not where the state lives, and lands as its own row graded against the same files.

## 5. Where the text lives (CEO-1885 (a)'s first condition)

The whole tabling layer -- the scheduler, storing and reading answers, `tnot/1`, the residual program, introspection (`get_residual/2`,
`current_table/2`, `get_calls/3` ...), abolishing, incremental invalidation -- left `PL_PRELUDE_SRC` for
`src/parsers/prolog/prelude/tabling.pl`, SCRIP's own Prolog (AGPL), embedded in LOCAL mode by `util_gen_prolog_prelude_libs.py`
(no SWI reader, no renames) and parsed only for a program that tables, loads files at run time, or names one of its 165 exports
(`undefined/0` is QUIET: five vendored libraries carry the atom as data; `prolog_parse.c` selects the library for a program whose source
names it). `pl_prelude_defines` counts its exports as SCRIP's own, as it counted the base prelude's, so no tabling predicate shows in a
program's `current_predicate` or declaration tables. No predicate in it keeps state outside the header cells, the two root cells and the
answer tries; `grep -rF "setval('\$tbl_" src` reads 0.

## 6. How it is graded

Row `prolog-tabling-is-boxes-the-evaluation-state-is-the-table-header-ceo-1885` (cfo), its DONE-WHEN: IR_TABLE_HDR in `IR.h`; the § 4
scheduler heads in `tabling.pl` and none in `prolog_parse.c`; zero `setval('$tbl_` under `src/`; `test_gate_no_c_to_bb.sh` adding no
NEW transfer (origin fb35bf3d1 already reads one UNMEASURED, `rt_sc_module.c`, not this row's); every IR_TABLE_HDR in `--dump-homes`
`home=RBP` with a HOMETEST naming a forcing test (CEO-1888 confirmed; the cto then ruled it a state word of class address-escapes, and
the census reads the declared row as forced: rbp_forced, never rbp_misplaced); and the files, m3 and m4, no fail, crash or hang: SWI `tabling/test_tabling` 35/35,
`test_answer_subsumption` 2/2, `test_wfs` 8/8; XSB `delay` 87/87 graded, `neg` 24/24, `wfs` 72/72, `nonmt` 9/9, `ptq` 25/25, `attv` 7/7,
`basics` 26/26, `ai` 11/11, `sub` 36/36, and `table_tests` 25/32 or better (origin's reading). RECEIPT: `tabsimp_seq`'s clock. LARGE
CHUNKS: smoked once on `test_tabling` and `test_answer_subsumption`, then every tabled program at once.
