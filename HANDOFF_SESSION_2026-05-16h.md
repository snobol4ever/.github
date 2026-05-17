# Handoff — PST-SC-4c through 4h complete (session 2026-05-16h)

**Goal:** GOAL-PARSER-PURE-SYNTAX-TREE.md — PST-SC-4i next
**Repos:** one4all @ `e1a902a7` · corpus @ `6a68f49` · .github @ `4debbf65`

---

## What was done this session

### PST-SC-4c ✅ (one4all `e95a5c2e`, corpus `a8e957b`)
`WhileHead`/`sc_while_head_new`/`sc_finalize_while` deleted. `while_head` type → `<expr>`. `while_before_body` snapshot. `sc_finalize_while_pst` builds `TT_WHILE(cond, TT_PROGRAM(body), QLIT(cont), QLIT(end))`. `lower_while_until` dispatches `TT_PROGRAM` body via `lower_stmt` (break-safe). `lower_if_stmt` added. SCRIP mirrored.

### PST-SC-4d ✅ (one4all `0c51b493`, corpus `36d3d44`)
`TT_DO_WHILE` added to `ast.h`. `DoHead`/`sc_do_head_new`/`sc_finalize_do_while` deleted. `do_before_body` snapshot. `sc_finalize_do_while_pst` builds `TT_DO_WHILE(TT_PROGRAM(body), cond, QLIT(cont), QLIT(end))`. `lower_do_while` added. SCRIP mirrored.

### PST-SC-4e ✅ (one4all `c276b48c`, corpus `d4b3f6b`)
`ForHead` slimmed to `{cond, step}`. `for_before_body` snapshot. `sc_finalize_for_pst` builds `TT_FOR(cond, step, TT_PROGRAM(body), QLIT(cont), QLIT(end))`. `lower_for` added. SCRIP mirrored.

### PST-SC-4f ✅ (one4all `960dfc01`, corpus `e068fc2`)
`CaseEntry` gains `before_body` snapshot. `sc_switch_case_label`/`sc_switch_default_label` snapshot instead of emitting label STMTs. `sc_switch_emit_implicit_break` → no-op. `sc_switch_head_new` no longer emits tmp-assign. `sc_finalize_switch_pst` collects bodies in reverse, builds `TT_CASE(disc, val1, TT_PROGRAM(body1), …, QLIT(end))`. `TT_NUL` child = default arm. `lower_case` updated for Snocone QLIT-last detection. SCRIP mirrored.

### PST-SC-4g ✅ (one4all `0c0c22d9`, corpus `6889e67`)
`TT_DEFINE` added to `ast.h`. `FuncHead` slimmed to `{name, argstr, prev_func}`. `func_before_body` snapshot. `sc_finalize_function_pst` builds `TT_DEFINE(QLIT(name), QLIT(sig), TT_PROGRAM(body))`. `lower_stmt` dispatches `TT_DEFINE` at top. SCRIP mirrored.

### PST-SC-4h ✅ (one4all `e1a902a7`, corpus `6a68f49`)
`sc_append_break`/`sc_append_continue` emit `TT_LOOP_BREAK`/`TT_LOOP_NEXT` tree nodes (optional `QLIT(user_label)` child) instead of goto STMT_t nodes. `lower.c`: `g_loop_stack[64]` + `loop_push`/`loop_pop` globals. `lower_while_until`/`lower_do_while`/`lower_for` push cont/end labels around body. `lower_loop_break`/`lower_loop_next` resolve via stack (Snocone) or fall back to Icon legacy. `lower_stmt` dispatches `TT_LOOP_BREAK`/`TT_LOOP_NEXT` directly. SCRIP mirrored.

### Also done
- `snobol4.l`: `AST_t` → `tree_t` (3 occurrences, one4all `a8cbbc03`).

---

## Gates confirmed green

`snocone_smoke 5/0`, `crosscheck_snocone 8/0`, `scrip_all_modes 2/0`.

---

## PST-SC-4i — Next step (labels)

Grammar rule currently:
```c
label_decl : T_IDENT T_COLON  { sc_emit_label_pad(st, $1); free($1); }
```

`sc_emit_label_pad` calls `sc_pending_label_add` (accumulates label names into `ScParseState.pending_user_labels`), which get transferred to the next `LoopFrame` via `sc_loop_push`. The label STMT_t then appears in CODE_t and produces `SM_LABEL` in `lower_stmt`.

**PST-SC-4i plan:**
1. `sc_emit_label_pad` → emit `TT_LABEL(QLIT(name))` directly via `sc_append_stmt`. No `sc_pending_label_add`.
2. `lower_stmt` at top: `if (s->t == TT_LABEL) { sm_label_named(g_p, s->c[0]->v.sval); labtab_define(…); return; }`
3. The `pending_user_labels`/`stash_for_pending_labels` machinery can be deleted — user-labeled break/continue after 4h uses `QLIT(user_label)` in the `TT_LOOP_BREAK`/`TT_LOOP_NEXT` node, resolved by `emit_goto(SM_JUMP, user_lbl)` → `labtab_find`. So `LoopFrame.user_labels` is already dead code.
4. Remove all `sc_pending_label_clear()` calls (from `sc_append_break`, `sc_append_continue`, `sc_append_return`, `sc_append_freturn`, `sc_append_nreturn`, `sc_switch_case_label`, `sc_switch_default_label`).
5. `TT_LABEL` needs adding to `ast.h`.
6. SCRIP mirror: `lower_stmt` in `lower.sc` gains `TT_LABEL` dispatch.

**After 4i:** `sc_pending_label_add`, `sc_pending_label_clear`, `sc_pending_to_stash`, `pending_user_labels*`, `stash_for_pending_labels*` fields and functions all deleted. `LoopFrame.user_labels`/`user_labels_count` fields deleted.

---

## Remaining PST-SC-4* steps

- **PST-SC-4j** — `return`/`freturn`/`nreturn`: `sc_append_return`/`sc_append_freturn`/`sc_append_nreturn` emit `TT_RETURN(value?)` / `TT_PROC_FAIL` directly. `lower_stmt` already handles these via `lower_expr` dispatch.
- **PST-SC-4k** — `goto LABEL`: `sc_append_goto_label` → emit `TT_GOTO_U(QLIT(label))`. `lower_stmt` resolves via `emit_goto(SM_JUMP, label)`.
- **PST-SC-4l** — `sc_split_subject_pattern` → lower.
- **PST-SC-4m–4n** — Final cleanup: `sc_append_stmt`/`sc_splice_after`/`sc_make_label_stmt`/`sc_make_goto_uncond_stmt` deleted. `ScParseState` shrunk to lexer+filename+error count.

---

## Session setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh
```

Gates:
- `bash scripts/test_smoke_snocone.sh` → PASS=5 FAIL=0
- `bash scripts/test_crosscheck_snocone.sh` → PASS=8 FAIL=0 SKIP=0
- `bash scripts/test_smoke_scrip_all_modes.sh` → PASS=2 FAIL=0
