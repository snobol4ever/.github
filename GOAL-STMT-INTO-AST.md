# GOAL-STMT-INTO-AST — Collapse CODE_t + STMT_t into AST_t

**Repo:** one4all + corpus + .github
**Prereq:** GOAL-AST-RENAME complete.

## Why

`CODE_t` is a linked list of `STMT_t`. `STMT_t` is named pointers to `AST_t`
children plus scalars. Both are trees wearing struct clothing. Flatten into:

```
AST_PROGRAM                    ← was CODE_t
  AST_STMT  sval=label ival=lang a[0].i=lineno a[1].i=stno a[2].i=flags
    children[0] = subject
    children[1] = pattern      (NULL if absent)
    children[2] = replacement  (NULL if absent)
    children[3] = AST_GOTO_S   sval=target (NULL if absent)
    children[4] = AST_GOTO_F   sval=target
    children[5] = AST_GOTO_U   sval=target
    children[6] = goto_s_expr  (computed goto AST, NULL if absent)
    children[7] = goto_f_expr
    children[8] = goto_u_expr
```

`lower()` takes `const AST_t *prog`. `lower_stmt` takes `const AST_t *s`.
`CODE_t` and `STMT_t` cease to exist — names freed for runtime use.

## Done when

1. No `CODE_t` or `STMT_t` in `one4all/src/`.
2. `lower()` signature: `SM_Program *lower(const AST_t *prog)`.
3. All six frontends emit `AST_PROGRAM`/`AST_STMT` nodes directly.
4. Snocone `parser_*.sc` emit `'AST_PROGRAM'`/`'AST_STMT'` tags.
5. All gates byte-identical throughout.

## New AST kinds

Add to `ast.h` before `AST_KIND_COUNT`:

```c
AST_PROGRAM,   /* root: children = AST_STMT list */
AST_STMT,      /* sval=label ival=lang a[0].i=lineno a[1].i=stno a[2].i=flags(is_end|has_eq) */
AST_GOTO_S,    /* sval=target label */
AST_GOTO_F,
AST_GOTO_U,
```

## Rungs

**SI-1** — Add `AST_PROGRAM`, `AST_STMT`, `AST_GOTO_S/F/U` to `ast.h` enum +
`ast_e_name[]`. Gate: build only.

- [ ] Add kinds to `ast.h`
- [ ] Gate: build

**SI-2** — Write shim helpers in `src/driver/stmt_ast.c`:

```c
AST_t *stmt_to_ast(const STMT_t *s);   /* wraps one STMT_t as AST_STMT */
AST_t *code_to_ast(const CODE_t *prog); /* wraps CODE_t as AST_PROGRAM  */
```

Declare in `scrip_cc.h`. These allow frontends to migrate one at a time.

- [ ] Write `stmt_ast.c`, declare in `scrip_cc.h`
- [ ] Gate: build + smoke snobol4

**SI-3** — `lower()` and `lower_stmt` take `AST_t*`. Call sites use
`code_to_ast()` shim temporarily. `lower_stmt` reads children/scalars
instead of `STMT_t` members.

- [ ] Change `lower()` to `SM_Program *lower(const AST_t *prog)`; update `lower.h`
- [ ] Rewrite `lower_stmt(const AST_t *s)` reading children[0..8] + a[*]
- [ ] Shim call sites: `lower(code_to_ast(prog))`
- [ ] Gate: all smokes + broker byte-identical

**SI-4** — SNOBOL4 frontend emits `AST_STMT` directly; remove shim from that path.

- [ ] Add `ast_stmt_new()` helper
- [ ] Update `snobol4.y` grammar actions
- [ ] Gate: smoke snobol4 byte-identical

**SI-5** — Migrate remaining five frontends (Icon, Prolog, Raku, Rebus, Snocone).

- [ ] icon
- [ ] prolog
- [ ] raku
- [ ] rebus
- [ ] snocone
- [ ] Gate after each: that frontend's smoke + broker

**SI-6** — Delete `CODE_t`, `STMT_t`, `stmt_to_ast`, `code_to_ast`, `stmt_ast.c`,
all `stmt_new`/`code_append` helpers. Verify no references remain.

- [ ] Delete structs and helpers
- [ ] Gate: all smokes + broker byte-identical

**SI-7** — Snocone parsers: emit `'AST_PROGRAM'`/`'AST_STMT'` tags; update `.ref` oracles.

- [ ] Update `corpus/SCRIP/parser_*.sc`
- [ ] Regenerate `.ref` oracles
- [ ] Gate: PARSER-* fixtures pass

**SI-8** — Doc pass: `PLAN.md`, `RULES.md`, `scrip_cc.h` header comment.

- [ ] Update docs
- [ ] Gate: doc-only

## Gate (every rung)

```bash
bash scripts/test_smoke_scrip_all_modes.sh && bash scripts/test_smoke_snobol4.sh
bash scripts/test_smoke_icon.sh && bash scripts/test_smoke_prolog.sh
bash scripts/test_smoke_raku.sh && bash scripts/test_smoke_snocone.sh
bash scripts/test_smoke_rebus.sh && bash scripts/test_smoke_unified_broker.sh
```

Byte-identical SM output at every rung.

## Risks

| Risk | Mitigation |
|------|------------|
| `ExportEntry`/`ImportEntry` in `CODE_t` | Add `AST_EXPORT`/`AST_IMPORT` kinds in SI-1 if needed |
| `interp.c` also walks `CODE_t` | Update alongside `lower.c` in SI-3 |
| 73 C files include `scrip_cc.h` | SI-6 errors are mechanical; fix after all frontends migrated |
| Snocone parsers emit program-level differently | Survey before SI-7 |
