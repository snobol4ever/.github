# HANDOFF — session 2026-05-11 (lower.c cleanup + GOAL-STMT-INTO-AST created)

## State

**one4all `fedf1e87`** · **`.github` `3faca8a`**

## What landed this session

GOAL-SM-LOWER-REFACTOR complete (SR-1..SR-15c):
- SR-14: silent default eliminated; explicit handler per AST kind
- SR-15: lower.c 1854→1142 lines (factored helpers, e→t rename)
- SR-15b: g_handlers table → direct switch in lower_expr
- SR-15c: LowerCtx struct eliminated; file-scope statics (g_p, g_labtab,
  g_in_proc_body, g_proc_scope, g_unhandled_kinds)
- lower_ctx.h: 170→59 lines; lower_ctx.c: 232→108 lines
- local var labtab→tbl in lower_stmt

New goal created: GOAL-STMT-INTO-AST (SI-1..SI-8) — collapse CODE_t+STMT_t
into AST_t. All 24 steps open. GOAL-AST-RENAME tombstoned (complete).

## Next

**GOAL-STMT-INTO-AST, SI-1** — add `AST_PROGRAM`, `AST_STMT`, `AST_GOTO_S/F/U`
to `ast.h` enum and `ast_e_name[]`. Gate: build only.

## Session start

```bash
git clone https://TOKEN@github.com/snobol4ever/.github.git /home/claude/.github
git clone https://TOKEN@github.com/snobol4ever/one4all.git /home/claude/one4all
git clone https://TOKEN@github.com/snobol4ever/corpus.git /home/claude/corpus
```

Read PLAN.md → GOAL-STMT-INTO-AST.md → RULES.md.
Run session setup from REPO-one4all.md (interp/compiler category).

## Notes

- lower.c handler signatures: `(const AST_t *t)` — no context pointer
- lower.c naming: p=SM_Program*, t=AST_t*, s=STMT_t*
- g_labtab is the LabelTable global (function API still labtab_*)
- GOAL-SM-LOWER-REFACTOR: tombstone it next session (all rungs done)
