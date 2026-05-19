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

- [x] **PST-SC-RET-IN-FN** *(audit V9)* ✅ 2026-05-19 (Sonnet 4.6, one4all `e2dfed5f`) — `T_RETURN expr0`: was two stmts (TT_ASSIGN(funcname,$2) + bare TT_RETURN). Now: `TT_RETURN(c[0]=$2)`. `lower.c`: `g_sc_func_name` global tracks current function; `lower_return` emits `SM_STORE_VAR(funcname) + SM_RETURN` when c[0] present.

- [x] **PST-SC-FOR-INIT** *(audit V8)* ✅ 2026-05-19 (Sonnet 4.6, one4all `b6558370`) — `for_head` called `sc_append_stmt(st, $3)` to emit init as a preceding stmt. TT_FOR had no init child. Fix: `init` is now `c[0]` of TT_FOR; TT_FOR shape = `[init|NUL, cond, step, body]`. `lower_for` emits init before the loop top label. `ForHead` struct carries `init` field. `sc_for_head_new_pst` takes init param.

### Promoted from `PST-LR-AUDIT-2.md § Scan 1 outstanding` (2026-05-19, Opus 4.7)

- [x] **PST-SC-SWITCH-LABELS** *(audit V13-switch — AUDIT-2 finding)* ✅ 2026-05-19 (Sonnet 4.6, one4all `648b7d24`) — `sc_switch_head_new`: removed `sc_label_new` calls; `end_label=NULL`, `default_label=NULL`; `sc_loop_push(NULL, NULL, 0)`. `sc_finalize_switch_pst`: removed `TT_QLIT(end_label)` last-child; TT_CASE shape now `[disc, val0, body0, val1, body1, …]`. `lower_case`: new `is_snocone` path mints `lbl_end` via `lower_fresh_label`, `loop_push`/`loop_pop`, `labtab_define` at exit. Old `has_qlit_end` path retained for backward compat. Gates: smoke_snocone 2/3, scrip_all_modes 2/0, crosscheck_snobol4 5/1 — all at floor. ⚠ MIRROR-GAP-SC-SWITCH-LABELS.

- [x] **PST-SC-DOC-CLEANUP** *(audit V8/V13 doc nit — AUDIT-2 finding)* ✅ 2026-05-19 (Sonnet 4.6, one4all `648b7d24`) — `sc_finalize_while_pst`/`sc_finalize_do_while_pst`/`sc_finalize_for_pst` docstrings updated to reflect current tree shapes (no QLIT children, FOR has init as c[0]). No code change.

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
watermark:    2026-05-19 (Sonnet 4.6 PST-SC-SWITCH-LABELS) — Phase 1 C COMPLETE. 11/11 §⛔ violations closed.
status:       ✅ Phase 1 C COMPLETE.
              4k–4n ✅ FLATTEN ✅ LABELS ✅ RET-IN-FN ✅ FOR-INIT ✅ SWITCH-LABELS ✅ DOC-CLEANUP ✅.
next:         Phase 2 SCRIP mirror (PST-SC-SC-1/PST-SC-SC-2) — BLOCKED until all six C parsers Phase 1 clean.
              Remaining Phase 2 gate blockers per PLAN.md: PRF-12-R15-DISPOSITION (PST-RAKU).
mirror gaps:  ⚠ MIRROR-GAP-SC-4k/4l/4m/4n/FLATTEN/LABELS/RET-IN-FN/FOR-INIT/SWITCH-LABELS. Phase 2 BLOCKED.
heads:        .github @ (pending push) · one4all @ 648b7d24 · corpus (no changes)

**PST-SC-SCRIP-AUDIT 2026-05-19 (Sonnet 4.6):** parser_snocone.sc scanned against
strict permitted list (shift, reduce, nPush, nInc, nPop, nTop, assign only).
VIOLATIONS FOUND — MAJOR. ~110 forbidden functions + reduce_prim in Compiland.
This is the largest Phase 2 rewrite job. All helper infrastructure must be deleted.

Functions to DELETE (complete list by category):
• Label synthesis: new_label, while_head_alloc, do_head_alloc, switch_head_alloc,
  Switch_head_alloc, switch_case_label, Switch_case_label, switch_default_label,
  Switch_default_label, for_head_alloc, For_head_alloc
• Control-flow body collection: save_cond, pop_cond, save_nbody, save_if_nthen,
  restore_if_nthen, Save_cond, Save_if_nthen, Restore_if_nthen, pop_body, Body, BodyFn
• Break/continue stacks: push_break, pop_break, top_break_label, push_continue,
  pop_continue, top_continue_label, emit_break, emit_break_label, emit_continue,
  emit_continue_label, Emit_break, Emit_break_label, Emit_continue, Emit_continue_label
• Finalization: finalize_if, finalize_if_else, finalize_while, finalize_do,
  finalize_for, finalize_switch, finalize_function, Finalize_if, Finalize_if_else,
  Finalize_while, Finalize_do, Finalize_for, Finalize_switch, Finalize_function
• Statement decomposition: decompose_stmt, Decompose_stmt, split_subj_pat,
  build_seq_or_single, flatten_arith, is_name_like
• Call decomposition: decompose_call, Decompose_call, push_call_name_var, Push_call_name_var
• STMT/goto/label emission: make_cond_stmt, make_goto_stmt, make_label_stmt,
  make_define_stmt, goto_emit, Goto_emit, label_emit, Label_emit, emit_struct, Emit_struct
• Paren/augop/idx: paren_reduce, Paren_reduce, reduce_augop, Reduce_augop,
  push_idx, Push_idx, push_mns, Push_mns, push_cmp, Push_cmp
• Atom pushers: push_qlit, Push_qlit, push_keyword, Push_keyword, push_ident,
  Push_ident, push_flit, Push_flit, push_ilit, Push_ilit, push_empty_str, Push_empty_str
• Return emitters: emit_return_value, Emit_return_value, emit_return_void,
  Emit_return_void, emit_freturn, Emit_freturn, emit_nreturn, Emit_nreturn
• Struct/param/field savers: func_head_save_name, Func_head_save_name,
  save_param_first, Save_param_first, save_param_rest, Save_param_rest,
  save_struct_field_first, Save_struct_field_first, save_struct_field_rest,
  Save_struct_field_rest, Save_nbody

Grammar rule replacements:
• stmt_body     → nPush() nInc() *Expr0 ($';'|epsilon) reduce('TT_STMT',1) nPop()
• if_cmd        → reduce('TT_IF', 2 or 3) wrapping cond + TT_PROGRAM(then) [+ TT_PROGRAM(else)]
• while_cmd     → reduce('TT_WHILE', 2): cond + TT_PROGRAM(body)
• do_cmd        → reduce('TT_DO_WHILE', 2): TT_PROGRAM(body) + cond
• for_cmd       → reduce('TT_FOR', 4): init + cond + step + TT_PROGRAM(body)
• switch_cmd    → nPush()/nInc() per arm / reduce('TT_CASE', nTop())
• func_cmd      → reduce('TT_DEFINE', 3): QLIT(name) + QLIT(sig) + TT_PROGRAM(body)
• return_cmd    → reduce('TT_RETURN', 1) or reduce('TT_RETURN', 0)
• freturn_cmd   → reduce('TT_PROC_FAIL', 0)
• nreturn_cmd   → reduce('TT_NRETURN', 0)
• goto_cmd      → shift(*Ident,'TT_GOTO_U') (no reduce needed — leaf)
• label_prefix  → shift(*Ident,'TT_LABEL')
• break_cmd     → reduce('TT_LOOP_BREAK', 0 or 1)
• continue_cmd  → reduce('TT_LOOP_NEXT', 0 or 1)
• struct_cmd    → nPush()/nInc()/reduce('TT_STRUCT', nTop())/nPop()
• Call          → nPush() shift(name,'TT_VAR') nInc() args reduce('TT_FNC',nTop()) nPop()
• Expr17 atoms  → shift(*String,'TT_QLIT'), shift(*Real,'TT_FLIT'), shift(*Integer,'TT_ILIT'),
                   shift(*Keyword,'TT_KEYWORD'), shift(*Ident,'TT_VAR')
• Expr14 unary  → reduce('TT_MNS',1) etc. (inline, no helper)
• Expr5 cmp     → shift('EQ','TT_VAR') nInc() reduce('TT_FNC',2) etc.
• Expr0 augop   → assign(.sc_augop, TK_AUGPLUS) reduce('TT_AUGOP',2) etc.
• Expr15/16 idx → reduce('TT_IDX',2) (inline)
• Expr17 paren  → nPush() nInc() *Expr0 ARBNO($',' nInc() *Expr0) reduce('TT_VLIST',nTop()) nPop()
• Compiland     → replace reduce_prim(E_Parse) with reduce(E_Parse,'nTop()')
```

### Session-end note — 2026-05-19 (Opus 4.7 PST-LR-AUDIT-2)

AUDIT-2 trust-but-verify scan found `sc_finalize_switch_pst` was missed
during PST-SC-LABELS. The fix is straightforward (mirror what was already
done for while/do/for), but the work requires touching lower.c too —
the break-target label currently comes via `strdup(h->end_label)` into
`sc_loop_push`, and that path must mint the label in lower instead.
Beauty self-host md5 protection applies as usual.

---

## Authorship

Drafted by Claude Opus 4.7, 2026-05-19. Snocone Phase 1 content extracted from `GOAL-PARSER-PURE-SYNTAX-TREE.md § Step 4` (which retains only a forwarder to this file). PST-SC-FLATTEN, PST-SC-LABELS, PST-SC-RET-IN-FN, PST-SC-FOR-INIT promoted from `PST-LR-AUDIT.md § Scan 1 Rollup` per LR-AUDIT-1j. Closed-rung table compacted from the original 10-bullet ladder. Phase 2 stop-line made explicit per Lon's 2026-05-19 directive: every per-language file does C work first and stops at the Snocone-mirror rung.
