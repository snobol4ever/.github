# ARCH-PROLOG-TABLING-BOXES — A TABLED CALL IS A BOX; ITS EVALUATION STATE IS THE BOX'S HEADER (cfo, 2026-10-22, CFO-324)

**Status: DESIGN OF RECORD, being built by the cfo.** Lon, in-chat to the cfo, 2026-10-22 07:1x CDT, verbatim, after asking *"Why is
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

## 2. The shape

A tabled `p/N` keeps today's renaming (`'$tbl p'/N` holds the clauses; lower's `pl_table_rewrite`, the loader's `'$lfx_wraps'`). The
wrapper becomes three steps, of which only the middle one is new:

```
p(A1..An) :- '$tbl_find'(p(A1..An), T, S),          % leaf: find or make the variant's table; S = complete | consume | eval
             '$tbl_go'(S, T, p(A1..An), '$tbl p'(A1..An)).
'$tbl_go'(complete, T, G, _) :- '$tbl_answer'(T, G).                      % iterate a complete table: an ordinary generator
'$tbl_go'(consume,  T, G, _) :- '$tbl_answer'(T, G).                      % the answers found so far (the leaf marked the leader)
'$tbl_go'(eval,     T, G, I) :- '$tbl_eval'(T, G, I), '$tbl_answer'(T, G). % THE BOX, then iterate
```

`'$tbl_eval'(T, G, I)` is a CONTROL CONSTRUCT, lowered by `lower_prolog.c` the way `findall/3` is (ARCH-PROLOG-BYRD-BOX-TRANSLATION
§ B.14: a γ→β drive loop), into one new box kind, **IR_TABLE_EVAL**, with the goal `I` as its child:

| port | does |
|---|---|
| α | `lea rdi, header` → leaf `rt_tbl_open`: bank the current generator in the header, make this header current, set depth, low, round, phase, pending; then → `I.α` |
| `I.γ` | → `'$tbl_add'(T, G)` (stateless: store the answer, moded aggregation, delays) → leaf `rt_tbl_changed` if it was new → `I.β` (forced failure, as findall) |
| `I.ω` | `lea rdi, header` → leaf `rt_tbl_close`: returns AGAIN (the next semi-naive pass, or the leader's next round or phase) → `I.α`; or DONE → γ |
| β | → ω (the box is bounded: one evaluation, then the answers are iterated by `'$tbl_answer'`) |
| ball | `I.ω` with r15 armed → leaf `rt_tbl_abort`: drop the header's incomplete tables, restore the banked generator → ω |

## 3. The header (op slots of IR_TABLE_EVAL; typed by the frame map, ARCH-GC § 7)

| word | type | holds |
|---|---|---|
| +0 | raw | the generator that was current at α (the previous header's address, or 0) |
| +8 | DESCR | T, this evaluation's table |
| +16 | raw | depth: the banked header's depth + 1 |
| +24 | raw | low: the least depth of an incomplete table any consumer under this header read (starts = depth) |
| +32 | DESCR | pending: the follower tables handed up to this header, still incomplete (a heap list) |
| +40 | raw | flags: changed this round, raised to the alternating fixpoint, a phase pass met a table with no snapshot |
| +48 | raw | phase (0, t, u, r) and the semi-naive pass number and its highest consumer position |
| +56 | raw | the consumer position counter of this pass |

**The one register.** The address of the CURRENT header lives in one word of the program registry (`pl_db_reg_t`, off the root
frame), beside a round counter. It is a single "current X" cell exactly as B (r13) is for choice points: every header banks the
previous value and restores it, so the chain of live generators IS the chain of headers on the machine stack (CEO-1542: a reader that
needs every live activation walks the frames). No list of evaluations exists anywhere.

## 4. The algorithm, in box terms (linear tabling: Zhou, Shen and Sato, TPLP 8(1) 2008; the rounds are today's)

1. **Find.** `'$tbl_find'` looks the call's variant up. Complete → `complete`. Incomplete and its generator is live (on the header
   chain) → `consume`, and the leaf lowers the CURRENT header's `low` to that table's depth: every generator between here and there
   is a FOLLOWER of that table's generator. Incomplete and not evaluated in this round, or absent → `eval`.
2. **Evaluate.** The box drives `I` to exhaustion, adding each answer. Consumers read the answers found so far (today's semi-naive
   slices, their snapshots in the table's own meta slot, their positions in header +56).
3. **Close.** `low == depth`: this header LEADS its component. If any table of the component changed this round, start the next round
   (bump the round counter, → `I.α`); a raised component runs the alternating fixpoint and the residual pass the same way, the phase
   in +48; then complete T and every table in `pending`. `low < depth`: a FOLLOWER: hand T and `pending` to the banked header,
   lower its `low`, pass `changed` up, → γ. The answers it returns are re-derived in the leader's next round.
4. **Answer.** `'$tbl_answer'` iterates the table (complete: all; consumed or followed: the answers so far) as an ordinary
   nondeterministic predicate, its choice in its own frame.

Independent components nest naturally: a generator whose evaluation consumed nothing older completes on its own, inside its caller's
round, exactly as `'$tbl_done'`'s early completion does today but for every depth.

## 5. What stays Prolog and what goes

- **Goes:** the scheduler (`'$tbl_enter'`, `'$tbl_lead'`, `'$tbl_eval1'`, `'$tbl_done'`, `'$tbl_rounds'`, `'$tbl_round'`, `'$tbl_eval'`,
  `'$tbl_runs'`, `'$tbl_run'`, `'$tbl_wfsrun'`, `'$tbl_alt'`, `'$tbl_alt2'`, `'$tbl_use'`, `'$tbl_range'`) and every one of the twelve
  cells. `'$tbl_incr'` becomes a property of the predicate's registry entry.
- **Stays, as ordinary predicates compiled to boxes and holding no state:** storing an answer (`'$tbl_add'`, the moded and residual
  forms), reading answers, `tnot/1` (it reads the phase through a leaf that reads the current header's leader), the residual program,
  introspection (`get_residual/2`, `current_table/2`, `get_calls/3` ...), abolishing, incremental invalidation.
- **The delay list** stays one current value replaced on backtracking (the cto's 2026-10-14 ruling, ARCH-PROLOG-WFS-TABLING § 3.1,
  conditions 1-3), moved from `b_setval` into a trailed registry word.

## 6. How it is graded

The landing closes on the files today's engine reads green, both modes, unchanged: SWI `tabling/test_wfs` 8/8,
`tabling/test_tabling` 35/35, `tabling/test_answer_subsumption` 2/2; XSB `delay` 87/87 graded, `neg` 24/24, `wfs` 72/72, `nonmt` 9/9;
hq_packages' six XSB files unchanged (ptq, attv, basics, ai, sub, tables); plus `tabsimp_seq`'s clock against today's 7 s; plus zero
`nb_setval`/`b_setval` on a `'$tbl_` name in `src/` paired with IR_TABLE_EVAL present in `src/ir/IR.h` (an absence is never graded
alone). LARGE CHUNKS: built whole; smoked once on `tabling/test_tabling` and `test_answer_subsumption` (plain and moded tables, no
negation); then every tabled program at once.
