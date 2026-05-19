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

- [x] **PST-SC-4k** — `goto LABEL` → `TT_GOTO_U`. `sc_append_goto_label` deleted. one4all `4017b525` 2026-05-19. ⚠ MIRROR-GAP-SC-4k.

- [x] **PST-SC-4l** — `sc_split_subject_pattern` → lower. `lower_subj_pat_split` added to `lower.c`; call removed from `sc_append_stmt`. one4all `a70cb5df` 2026-05-19. ⚠ MIRROR-GAP-SC-4l.

- [x] **PST-SC-4m** — Delete dead cluster (`sc_make_label_stmt`, `sc_make_cond_fail_stmt`, `sc_make_goto_uncond_stmt`, `sc_splice_after`, `sc_finalize_if_no_else`, `sc_finalize_if_else`, `sc_make_cond_succ_stmt`, `sc_split_subject_pattern`). Thin `sc_append_stmt`: TT_ASSIGN unpack removed; just `stmt_new()+s->subject=top+sc_append_chain`. one4all `e7c907a5` 2026-05-19. ⚠ MIRROR-GAP-SC-4m.

- [x] **PST-SC-4n** — `ScParseState` shrunk. Removed `label_seq`, `if_before_body`, `func_before_body`. `func_before_body` moved into `FuncHead.before_body`. `ScParseState` now: ctx, code, filename, nerrors, cur_func_name, loop_top, cur_switch. (cur_func_name stays pending PST-SC-RET-IN-FN.) one4all `b79b93b2` 2026-05-19. ⚠ MIRROR-GAP-SC-4n.

### Promoted from `PST-LR-AUDIT.md § Scan 1` (2026-05-19)

These are the 10 unowned audit violations. Each maps to a clear fix; group them by mechanism. Audit-row IDs in parens.

- [x] **PST-SC-FLATTEN** *(audit V1–V7)* — `sc_flatten_arith` deleted; `exprlist_ne` fresh-copy on each reduction. V1 TT_ALT, V2 TT_SEQ, V3 TT_ADD, V4 TT_SUB, V5 TT_MUL, V6 TT_DIV: `expr_binary(OP,$1,$3)`. V7 exprlist_ne: fresh TT_NUL + copy $1 children + append $3. one4all `678d7b9e` 2026-05-19. ⚠ MIRROR-GAP-SC-FLATTEN.

- [x] **PST-SC-LABELS** *(audit V13)* ✅ 2026-05-19 (Sonnet 4.6, one4all `6a880716`) — `while_head` / `do_head` / `for_head` grammar actions: `sc_label_new` calls removed; `sc_loop_push(st, NULL, NULL, 1)`. Finalize functions: QLIT label children removed from TT_WHILE/TT_DO_WHILE/TT_FOR. lower.c: `lower_fresh_label()` helper + `g_loop_label_seq` counter; `lower_while_until`/`lower_do_while`/`lower_for` generate labels internally via `labtab_define`. Gates: smoke_snocone 2/3 floor (pre-existing LE segfault), scrip_all_modes 2/0, crosscheck 5/1.

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
watermark:    2026-05-19 (Sonnet 4.6) — PST-SC-LABELS ✅ one4all 6a880716.
status:       ⏳ Phase 1 NOT clean — 2 §⛔ violations remaining (was 3).
              PST-SC-4k ✅ PST-SC-4l ✅ PST-SC-4m ✅ PST-SC-4n ✅ PST-SC-FLATTEN ✅ PST-SC-LABELS ✅.
              Active: PST-SC-RET-IN-FN (next smallest).
next:         PST-SC-RET-IN-FN — simple_stmt T_RETURN emits one TT_RETURN($2) not two
              synthesized stmts; lower_return handles func-name assign.
mirror gaps:  ⚠ MIRROR-GAP-SC-4k/4l/4m/4n/FLATTEN/LABELS. Phase 2 BLOCKED.
heads:        .github @ (pending push) · one4all @ 6a880716 · corpus (no changes)
```

### Session-end note — 2026-05-19 (Opus 4.7 session 4)

HQ session — PST-LR-AUDIT-1 closed and three-facet block added across all six
PST goal files. No Snocone-specific code changes this session. Next session:
open `snocone_parse.y:398`, apply PST-SC-4k fix sketch above. **Critical
gate:** beauty.sno self-host (Milestone 1) — never commit a Snocone change
without confirming beauty md5 is preserved.

---

## Authorship

Drafted by Claude Opus 4.7, 2026-05-19. Snocone Phase 1 content extracted from `GOAL-PARSER-PURE-SYNTAX-TREE.md § Step 4` (which retains only a forwarder to this file). PST-SC-FLATTEN, PST-SC-LABELS, PST-SC-RET-IN-FN, PST-SC-FOR-INIT promoted from `PST-LR-AUDIT.md § Scan 1 Rollup` per LR-AUDIT-1j. Closed-rung table compacted from the original 10-bullet ladder. Phase 2 stop-line made explicit per Lon's 2026-05-19 directive: every per-language file does C work first and stops at the Snocone-mirror rung.
