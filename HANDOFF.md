# HANDOFF — session 2026-05-11

## State

**one4all `fedf1e87`** · **`.github` ab35d6a+**

## What landed this session

GOAL-SM-LOWER-REFACTOR SR-1..SR-15c complete:
- lower.c: 1854→1142 lines, LowerCtx removed, g_handlers→switch
- lower_ctx.h: 170→59 lines; lower_ctx.c: 232→108 lines
- File-scope statics: g_p, g_labtab, g_in_proc_body, g_proc_scope, g_unhandled_kinds
- Handler signatures: (const AST_t *t) — no context pointer
- local var labtab→tbl

Phase 5 (SI-1..SI-8) added to GOAL-SM-LOWER-REFACTOR:
collapse CODE_t+STMT_t into AST_t.

## Next

**GOAL-SM-LOWER-REFACTOR, SI-1** — add AST_PROGRAM, AST_STMT, AST_GOTO_S/F/U
to ast.h enum and ast_e_name[]. Gate: build only.

## Session start

```bash
git clone https://TOKEN@github.com/snobol4ever/.github.git /home/claude/.github
git clone https://TOKEN@github.com/snobol4ever/one4all.git /home/claude/one4all
git clone https://TOKEN@github.com/snobol4ever/corpus.git /home/claude/corpus
```

Read PLAN.md → GOAL-SM-LOWER-REFACTOR.md (Phase 5) → RULES.md.
Run session setup from REPO-one4all.md (interp/compiler category).

## Notes

- lower.c: p=SM_Program*, t=AST_t*, s=STMT_t* (local only, STMT_t still exists)
- g_labtab is the global LabelTable; API functions still named labtab_*
- Stale open checkboxes from SR-9/SR-10/SR-15 removed this handoff
- GOAL-SM-LOWER-REFACTOR: do NOT tombstone — Phase 5 (SI-*) still active
