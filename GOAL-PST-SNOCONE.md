# GOAL-PST-SNOCONE.md — Pure Syntax Tree: Snocone

**Repo:** one4all + corpus + .github
**Parent goal:** `GOAL-PARSER-PURE-SYNTAX-TREE.md` (Step 4)
**Status:** ⏳ Phase 1 NOT clean per `PST-LR-AUDIT.md § Scan 1` — 11 §⛔ violations. 1 owned (PST-SC-4k); 10 unowned.

```
(source) ──► PARSER ──► (tree_t — pure syntax) ──► LOWER ──► IR_sm_t[]  ──┐
                                                                            ├──► interp / emitters
                                                          └──► IR_bb_t  ──┘
```

**Background.** Extracted from `GOAL-PARSER-PURE-SYNTAX-TREE.md` Step 4 on 2026-05-19 so each of the six languages owns its own session file. Snocone has the deepest parser-side desugaring of all six frontends — historically the bulk of Step 4 was rewriting parser-action control-flow lowering (if/while/for/do/case/define) into pure `tree_t` shapes that `lower.c` consumes. Rungs 4a–4j are closed; 4k–4n are the Phase 1 C work remaining.

---

## ⛔ Pure-syntax rules (binding)

Children of every node in source token order. No in-place append to an existing subtree inspected by kind. No synthesizing labels in the parser (`sc_label_new` forbidden in Phase 1 work). No control-flow lowering in parser actions. No splicing source tokens into sibling statements that were not in the source.

**Allowed:** `ast_node_new(TT_*)`, `expr_unary`, `expr_binary`, `expr_add_child`. Setting `v.sval/v.ival/v.dval` from token. Snapshot fields on `ScParseState` for body collection (`*_before_body`).

**Forbidden:** `sc_label_new`; `sc_clone_*`; splicing labels/gotos into the CODE chain; inspecting a previously-built child's kind to decide what to wrap; mutate-in-place via `sc_flatten_arith` (audit V1–V6).

**⛔ Three Phase-1 facets** (per `GOAL-PARSER-PURE-SYNTAX-TREE.md § "The three Phase-1 facets"`):

- **F1 — `tree_t` is the sole information channel between Snocone parse and Stage 2 lower.** Snocone is the worst Phase-1 offender on this axis: it historically did all control-flow lowering in parser actions, with synthetic labels (`_Ltop_NNNN` / `_Lend_NNNN` / `_Lcont_NNNN`), break/continue stacks (`sc_break_stk`/`sc_continue_stk`), if-then-stack (`sc_if_nthen_stk`), switch state (`sc_sw_*`), and for-loop state (`for_step_expr`, `for_cond_expr`, `for_lcont`, `for_lend`, `sc_for_cont_used`) all carried in `ScParseState` — none of which is on the tree. The audit-promoted rungs **PST-SC-LABELS** (mint labels in `lower.c`, not parser), **PST-SC-FOR-INIT** (lift `init` back into `TT_FOR.c[0]`), and **PST-SC-RET-IN-FN** (one `TT_RETURN($2)` not two synthesized statements) are F1 work — each one moves a fact that currently lives in `ScParseState` back onto the tree. **Test:** after all 4k–4n + audit-promoted rungs close, deleting every field from `ScParseState` except the absolute minimum (tree-root, cursor) should not lose any information that reaches lower.
- **F2 — `tree_t` has exactly four fields `t`, `v`, `n`, `c`.** Cross-cutting `PST-FIELD-1`/`PST-FIELD-2` own this. Snocone is not a primary `_id` consumer (no Snocone production sets `proc->_id`) so PST-FIELD-2 has no Snocone-specific blocking site — it unblocks once Icon and Raku close their `_id` uses. PST-FIELD-1 (`_nalloc`) is purely allocator bookkeeping; no Snocone production reads it.
- **F3 — Children L→R in source-token order.** Audit-detected violations: PST-SC-4k (goto LABEL via STMT_t field — label is not a tree child), PST-SC-FLATTEN (V1–V7: `sc_flatten_arith` and `exprlist_ne` mutate prior nodes — children land in source order but mechanism violates rule 2).

**⛔ Phase 1 / Phase 2 sequencing (binding 2026-05-18):** C parser work (this file) and SCRIP mirror work (`parser_snocone.sc`) **never** in the same session. Record `⚠ MIRROR-GAP` for each Phase 1 rung whose SCRIP mirror lags. Phase 2 is blocked on **all six** C parsers being Phase 1 clean.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_snocone_smoke.sh
```

Gates:

```bash
bash /home/claude/one4all/scripts/test_smoke_snocone.sh        # 5 fixtures
bash /home/claude/one4all/scripts/test_smoke_scrip_all_modes.sh
bash /home/claude/one4all/scripts/test_crosscheck_snobol4.sh   # regression guard
```

Plus the broader Snocone corpus check when touching lower.c shared with SNOBOL4.

---

## Closed rungs (history — do not re-open)

PST-SC-4a–4j ✅ 2026-05-16/17, by language construct:

| Rung | Construct | Result |
|------|-----------|--------|
| 4a | augop (`+=`/`-=`/`*=`/`/=`/`^=`) | parser emits `TT_AUGOP(lhs, rhs)` with `v.ival=TK_AUG*`; `lower_augop` handles |
| 4b | if/else | parser emits `TT_IF(cond, TT_PROGRAM(then), TT_PROGRAM(else))`; `IfHead` family deleted |
| 4c | while | parser emits `TT_WHILE(cond, TT_PROGRAM(body), QLIT(cont), QLIT(end))`; `WhileHead` deleted |
| 4d | do-while | parser emits `TT_DO_WHILE(TT_PROGRAM(body), cond, QLIT(cont), QLIT(end))`; `DoHead` deleted |
| 4e | for | parser emits `TT_FOR(cond, step, TT_PROGRAM(body), QLIT(cont), QLIT(end))`; `ForHead` slimmed |
| 4f | switch/case | parser emits `TT_CASE(disc, val1, TT_PROGRAM(body1), ..., QLIT(end))`; lower.c switch handles TT_PROGRAM arm bodies |
| 4g | function/define | parser emits `TT_DEFINE(QLIT(name), QLIT(sig), TT_PROGRAM(body))` |
| 4h | break/continue | parser emits `TT_LOOP_BREAK` / `TT_LOOP_NEXT` (optional QLIT user-label child); lower.c maintains `g_loop_stack` |
| 4i | labels | label-only STMT_t via `sc_append_label_node`; `sc_emit_label_pad` and pending/stash fields deleted |
| 4j | return/freturn/nreturn | direct `lower_return`/`proc_fail`/`nreturn` dispatch; emit SM_RETURN/FRETURN/NRETURN directly |

Each rung gated `snocone_smoke 5/0`, `crosscheck_snocone 8/0`, `scrip_all_modes 2/0`. Full commit hashes preserved in the parent goal's history.

---

## Active rungs — Phase 1 (C only)

### From the original Step 4 ladder

- [ ] **PST-SC-4k** — `goto LABEL` → `TT_GOTO_U`. `sc_append_goto_label` deleted. Audit-row V11; the active rung named in PLAN.md. Parser currently bypasses the tree by writing `STMT_t.goto_u` directly; should produce `TT_GOTO_U(TT_QLIT(target))` routed through `sc_append_stmt`.

- [ ] **PST-SC-4l** — `sc_split_subject_pattern` → lower. The parser builds `TT_SCAN(subj, pat)` fresh ✅ (audit V14 withdrawn); the **downstream split** into separate STMT_t fields is parser-side consumer logic that belongs in `lower.c`. Remove `sc_split_subject_pattern` from the parser-side `sc_append_stmt`; introduce `lower_subj_pat_split` instead.

- [ ] **PST-SC-4m** — `TT_PROGRAM` is a tree of statement-tree nodes (not flat list with synthetic gotos/labels). Delete `sc_append_stmt`, `sc_splice_after`, `sc_make_label_stmt`, `sc_make_goto_uncond_stmt`. After 4k–4l, the only `sc_append_*` left should be a thin push onto a tree-shaped accumulator that produces a final `TT_PROGRAM`.

- [ ] **PST-SC-4n** — `ScParseState` shrunk to lexer + filename + error count. After 4m, the parse-state struct should hold only what the lexer and error reporter need. All `*_before_body` snapshot fields removed (each finalize-helper is self-contained per its `Head` struct after 4b–4g).

### Promoted from `PST-LR-AUDIT.md § Scan 1` (2026-05-19)

These are the 10 unowned audit violations. Each maps to a clear fix; group them by mechanism. Audit-row IDs in parens.

- [ ] **PST-SC-FLATTEN** *(audit V1–V7)* — eliminate `sc_flatten_arith` (`snocone_parse.y:976`) and `exprlist_ne`-style in-place append (line 533). **7 sites total:** `expr3` (TT_ALT), `expr4` (TT_SEQ), `expr6 T_2PLUS` (TT_ADD), `expr6 T_2MINUS` (TT_SUB), `expr9 T_2STAR` (TT_MUL), `expr9 T_2SLASH` (TT_DIV), and `exprlist_ne` (TT_NUL container). All currently mutate `$1` by appending. **Fix:** always fresh-wrap (right-leaning binary chain). Re-flattening — if ever desired — is a lower concern. Reference shape: SNOBOL4 post-PST-SN4-1d (also Icon `parse_and`/`parse_alt`).

- [ ] **PST-SC-LABELS** *(audit V13)* — `while_head` / `do_head` / `for_head` / `switch_head` mint synthetic label strings via `sc_label_new` and stash them as `TT_QLIT` children of TT_WHILE/DO_WHILE/FOR/CASE. Move label allocation to `lower.c` — parser emits TT_WHILE etc. with **no** label children. `lower_while`/`lower_do_while`/`lower_for`/`lower_case` allocate `_Ltop_`/`_Lcont_`/`_Lend_` labels via labtab as needed. Coordinates with 4h's `g_loop_stack`.

- [ ] **PST-SC-RET-IN-FN** *(audit V9)* — `simple_stmt: T_RETURN expr0 T_SEMICOLON` inside a function currently synthesizes two statements: a `TT_ASSIGN(TT_VAR(func_name), $2)` plus a bare `TT_RETURN`. The LHS `TT_VAR(func_name)` is read from `st->cur_func_name` — not a source token. **Fix:** emit one `TT_RETURN($2)` and let `lower_return` perform the func-name assign as part of the function-call epilogue lowering.

- [ ] **PST-SC-FOR-INIT** *(audit V8)* — `for_head` (`snocone_parse.y:332`) calls `sc_append_stmt(st, $3)` to lift `init` as a free-standing statement before the loop. The TT_FOR node then has only `[cond, step, body]` — `init` is missing. **Fix:** restore `init` as `c[0]` of TT_FOR so its shape is `[init, cond, step, body]`. `lower_for` emits the init assignment, the head label, the cond test, body, step, back-edge, end label.

### Snapshot of Snocone after Phase 1

By end of Phase 1, `snocone_parse.y` should: (a) build only `tree_t`; (b) use no synthesized labels; (c) keep every source token represented in the tree (no lifting to sibling statements); (d) wrap fresh on every reduce (no mutate-prior); (e) `ScParseState` carries only lexer + filename + error count.

---

## ⛔ Phase 2 — DO NOT START THIS SESSION OR ANY SESSION UNTIL ALL SIX C PARSERS ARE PHASE 1 CLEAN

**SCRIP mirror work** is documented in the parent goal `GOAL-PARSER-PURE-SYNTAX-TREE.md § Step 4 Phase 2` and covers PST-SC-SC-1 (audit `parser_snocone.sc` for `Append` violations) and PST-SC-SC-2 (replace with `Reduce`). Three known violation sites at lines ~221, ~400, ~608 of `parser_snocone.sc`. **Do not write a line of `parser_snocone.sc` in this session — even if the audit-row fix would be trivial.** Two-phase rule (binding 2026-05-18): C parsers Phase 1 first, then a dedicated SNOBOL4-/Snocone-orientation session for each `parser_*.sc` mirror.

---

## Done criterion (Phase 1 — this file)

1. PST-SC-4k–4n checked [x].
2. PST-SC-FLATTEN, PST-SC-LABELS, PST-SC-RET-IN-FN, PST-SC-FOR-INIT checked [x].
3. `PST-LR-AUDIT.md § Scan 1` re-grade: 0 §⛔ violations for Snocone.
4. Gates: `smoke_snocone`, `crosscheck_snocone`, `smoke_scrip_all_modes` — all at floor.
5. Beauty self-host byte-identical (Milestone 1 protected).
6. Parent goal `GOAL-PARSER-PURE-SYNTAX-TREE.md` Step 4 (Phase 1) marked ✅.

Phase 2 (`parser_snocone.sc` mirror) is a separate goal-file rung gated on all six C parsers being Phase 1 clean.

---

## State

```
watermark:    2026-05-19 (file created by extracting Snocone material from parent goal)
status:       ⏳ Phase 1 NOT clean — 4 from-Step-4 rungs + 4 audit-promoted = 8 Phase 1 rungs remain
next:         PST-SC-4k (smallest scope, well-defined, lower.c infrastructure already in place
              from 4h's g_loop_stack)
mirror gaps:  PST-SC-4a..4j already have SCRIP-mirror updates in parser_snocone.sc (paired
              commits in the original Step 4 work) — those mirror changes pre-date the new
              two-phase rule and are kept. New Phase 1 rungs (4k–4n + audit-promoted) record
              ⚠ MIRROR-GAP-SC-* in State as each lands.
```

---

## Authorship

Drafted by Claude Opus 4.7, 2026-05-19. Snocone Phase 1 content extracted from `GOAL-PARSER-PURE-SYNTAX-TREE.md § Step 4` (which retains only a forwarder to this file). PST-SC-FLATTEN, PST-SC-LABELS, PST-SC-RET-IN-FN, PST-SC-FOR-INIT promoted from `PST-LR-AUDIT.md § Scan 1 Rollup` per LR-AUDIT-1j. Closed-rung table compacted from the original 10-bullet ladder. Phase 2 stop-line made explicit per Lon's 2026-05-19 directive: every per-language file does C work first and stops at the Snocone-mirror rung.
