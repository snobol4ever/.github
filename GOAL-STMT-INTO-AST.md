# GOAL-STMT-INTO-AST — Collapse CODE_t + STMT_t into AST_t

**Repo:** one4all (primary) + corpus (.sc parsers) + .github
**Prerequisite:** GOAL-AST-RENAME complete (AR-1..AR-3 done — AST_t / AST_e / AST_* landed).
**Unlocks:** GOAL-SNOCONE-SM-LOWER (SL-1) benefits; names CODE_t / STMT_t freed for runtime use.

---

## Why

`CODE_t` is a linked list of `STMT_t`. `STMT_t` is a struct of named pointers to
`AST_t` children plus scalar fields (label, lineno, stno, lang, is_end, has_eq, gotos).
Both are trees wearing struct clothing. There is no structural reason they cannot be
`AST_t` nodes with children:

```
AST_PROGRAM                         (was CODE_t)
  AST_STMT  sval=label ival=lang    (was STMT_t)
    children[0] = subject AST_t
    children[1] = pattern AST_t     (or AST_NUL if absent)
    children[2] = replacement AST_t (or AST_NUL if absent)
    children[3] = AST_GOTO_S  sval="label" | AST_NUL
    children[4] = AST_GOTO_F  sval="label" | AST_NUL
    children[5] = AST_GOTO_U  sval="label" | AST_NUL
    a[0].i = lineno
    a[1].i = stno
    a[2].i = is_end | has_eq flags
  AST_STMT ...
```

`lower()` then takes `const AST_t *prog` instead of `const CODE_t *prog`.
`lower_stmt` takes `const AST_t *s` instead of `const STMT_t *s`.
The six frontends build `AST_STMT` / `AST_PROGRAM` nodes instead of `STMT_t`.
`CODE_t` and `STMT_t` cease to exist as compile-time structs — freeing those
names for runtime use.

---

## Done when

1. `CODE_t` and `STMT_t` do not exist anywhere in `one4all/src/`.
2. `lower()` signature is `SM_Program *lower(const AST_t *prog)`.
3. `lower_stmt` takes `const AST_t *s`; reads children[0..5] and scalar fields.
4. All six frontends emit `AST_PROGRAM` / `AST_STMT` nodes.
5. The Snocone `parser_*.sc` files emit `'AST_PROGRAM'` / `'AST_STMT'` tags.
6. All gates byte-identical to baseline: smoke ×6, broker 49/49, isolation.

---

## New AST kinds needed

Add to `ast.h` (after existing kinds, before `AST_KIND_COUNT`):

```c
AST_PROGRAM,   /* root node: children = AST_STMT list             */
AST_STMT,      /* one statement:
                *   sval      = label string (NULL if no label)
                *   ival      = lang (LANG_SNO / LANG_ICN / etc.)
                *   a[0].i    = lineno
                *   a[1].i    = stno
                *   a[2].i    = flags: bit0=is_end, bit1=has_eq
                *   children[0] = subject   (AST_t* or NULL)
                *   children[1] = pattern   (AST_t* or NULL)
                *   children[2] = replacement (AST_t* or NULL)
                *   children[3] = goto_s    (AST_QLIT sval or NULL)
                *   children[4] = goto_f    (AST_QLIT sval or NULL)
                *   children[5] = goto_u    (AST_QLIT sval or NULL)
                *   children[6] = goto_s_expr (AST_t* or NULL)
                *   children[7] = goto_f_expr (AST_t* or NULL)
                *   children[8] = goto_u_expr (AST_t* or NULL)
                */
AST_GOTO_S,    /* success goto — sval = target label              */
AST_GOTO_F,    /* failure goto — sval = target label              */
AST_GOTO_U,    /* unconditional goto — sval = target label        */
```

---

## Rung sequence

### SI-1 — Add AST_PROGRAM / AST_STMT / AST_GOTO_* to ast.h

- [ ] Add `AST_PROGRAM`, `AST_STMT`, `AST_GOTO_S`, `AST_GOTO_F`, `AST_GOTO_U`
      to the `AST_e` enum in `ast.h` (before `AST_KIND_COUNT`).
- [ ] Add entries to `ast_e_name[]` in `ast.h`.
- [ ] Build passes (no behaviour change yet — new kinds unused).
- [ ] Gate: build only.

### SI-2 — Add helper: stmt_to_ast() in scrip_cc.h / a new stmt_ast.c

Write a single conversion function that wraps a `STMT_t` as an `AST_STMT` node.
This lets frontends migrate one at a time without a flag day.

```c
/* Convert a STMT_t to an AST_STMT node (GC-allocated). */
AST_t *stmt_to_ast(const STMT_t *s);

/* Build an AST_PROGRAM from a CODE_t linked list. */
AST_t *code_to_ast(const CODE_t *prog);
```

`code_to_ast` walks `prog->head` calling `stmt_to_ast` for each, appends as
children of a new `AST_PROGRAM` node. `ExportEntry`/`ImportEntry` lists can
be encoded as `AST_QLIT` children with a distinguishing kind (or deferred).

- [ ] Write `stmt_to_ast()` and `code_to_ast()` in `src/driver/stmt_ast.c`.
- [ ] Declare in `scrip_cc.h`.
- [ ] Build and unit-test: round-trip one .sno file through `code_to_ast` +
      verify child count matches statement count.
- [ ] Gate: build + smoke snobol4.

### SI-3 — lower.c: accept AST_t* prog; write lower_stmt(AST_t*)

Change `lower()` to take `const AST_t *prog` (must be `AST_PROGRAM`).
Change `lower_stmt` to take `const AST_t *s` (must be `AST_STMT`).
Extract fields from children and scalar slots instead of `STMT_t` members.

The call site in `interp.c` / `scrip_sm.c` (wherever `lower()` is called)
temporarily calls `code_to_ast(prog)` to produce the `AST_t*` — no frontend
change yet.

```c
/* lower.c after SI-3: */
SM_Program *lower(const AST_t *prog)   /* AST_PROGRAM */
{
    ...
    for (int i = 0; i < prog->nchildren; i++)
        lower_stmt(prog->children[i]);   /* AST_STMT */
    ...
}

static void lower_stmt(const AST_t *s)  /* AST_STMT */
{
    const char *label   = s->sval;
    int         lang    = (int)s->ival;
    int         lineno  = (int)s->a[0].i;
    int         stno    = (int)s->a[1].i;
    int         is_end  = (int)s->a[2].i & 1;
    int         has_eq  = (int)s->a[2].i & 2;
    const AST_t *subject     = s->nchildren > 0 ? s->children[0] : NULL;
    const AST_t *pattern     = s->nchildren > 1 ? s->children[1] : NULL;
    const AST_t *replacement = s->nchildren > 2 ? s->children[2] : NULL;
    /* goto children[3..8] ... */
    ...
}
```

- [ ] Change `lower()` signature; update `lower.h`.
- [ ] Write `lower_stmt(const AST_t *s)` reading from children.
- [ ] Temporary shim in call site: `lower(code_to_ast(prog))`.
- [ ] Gate: all smokes + broker byte-identical.

### SI-4 — Frontend migration: SNOBOL4 parser emits AST_STMT directly

Change the SNOBOL4 frontend (`snobol4.y` / `snobol4.l`) to build `AST_STMT`
nodes directly rather than `STMT_t`. The SNOBOL4 grammar actions currently
call `stmt_new()` / `code_append()` — replace with `ast_stmt_new()` /
`ast_program_append()`.

- [ ] Add `ast_stmt_new()` helper (allocates `AST_STMT`, fills children).
- [ ] Update `snobol4.y` grammar actions.
- [ ] Remove `code_to_ast()` shim from the SNOBOL4 path.
- [ ] Gate: smoke snobol4 byte-identical.

### SI-5 — Frontend migration: remaining five frontends

Repeat SI-4 for Icon, Prolog, Raku, Rebus, Snocone frontends — each emits
`AST_PROGRAM` / `AST_STMT` directly.

- [ ] icon frontend
- [ ] prolog frontend
- [ ] raku frontend
- [ ] rebus frontend
- [ ] snocone frontend
- [ ] Gate after each: that frontend's smoke byte-identical + broker.

### SI-6 — Delete CODE_t, STMT_t, related helpers

Once all frontends emit `AST_STMT` directly and `lower()` reads `AST_t*`:

- [ ] Delete `struct STMT_t`, `typedef CODE_t`, `stmt_new`, `code_append`,
      `code_to_ast`, `stmt_to_ast` from `scrip_cc.h` and source.
- [ ] Delete `stmt_ast.c` (shim no longer needed).
- [ ] Verify no `STMT_t` or `CODE_t` reference remains in `one4all/src/`.
- [ ] Gate: all smokes + broker byte-identical.

### SI-7 — Snocone parsers: emit AST_PROGRAM / AST_STMT tags

Update `corpus/SCRIP/parser_*.sc` to emit `'AST_PROGRAM'` / `'AST_STMT'`
instead of whatever they emit today for the program/statement level.
Update corresponding `.ref` oracle files.

- [ ] Survey: `grep -r "STMT\|CODE_T\|program" corpus/SCRIP/parser_*.sc`
- [ ] Update each parser.
- [ ] Regenerate `.ref` oracles.
- [ ] Gate: PARSER-* fixture tests pass.

### SI-8 — Documentation pass

- [ ] Update `PLAN.md` Architecture section.
- [ ] Update `RULES.md` §"Snocone parser style" (stmt/program tag names).
- [ ] Update `scrip_cc.h` header comment.
- [ ] Gate: doc-only, no build gate.

---

## Gate (every rung)

```bash
bash scripts/test_smoke_scrip_all_modes.sh   # PASS=2
bash scripts/test_smoke_snobol4.sh           # unchanged
bash scripts/test_smoke_icon.sh              # unchanged
bash scripts/test_smoke_prolog.sh            # unchanged
bash scripts/test_smoke_raku.sh              # unchanged
bash scripts/test_smoke_snocone.sh           # unchanged
bash scripts/test_smoke_rebus.sh             # unchanged
bash scripts/test_smoke_unified_broker.sh    # PASS=49 FAIL=0
```

Byte-identical output at every rung. This is a structural refactor —
the SM bytecode emitted must not change one byte.

---

## Risk register

| Risk | Mitigation |
|------|------------|
| `ExportEntry`/`ImportEntry` in `CODE_t` have no AST equivalent | Encode as `AST_QLIT` children with distinguishing kind, or add `AST_EXPORT`/`AST_IMPORT` kinds in SI-1 |
| `STMT_t.stno` used in `sm_stno_label_record` call site | Field moves to `a[1].i` on `AST_STMT`; same value, different accessor |
| `scrip_cc.h` included by many files (73 C files) | `CODE_t`/`STMT_t` deletion in SI-6 will produce many errors to fix; do SI-6 only after all frontends migrated |
| Snocone parsers emit program-level structure differently from C side | Survey in SI-7 before writing; may be simpler than expected |
| IR-interp path (interp.c) also walks `CODE_t` for label resolution | Must be updated in SI-3 alongside lower.c |

---

## Out of scope

- Renaming `LANG_*` constants (orthogonal; `ival` on `AST_STMT` carries the value).
- Changing the SM_Program instruction set.
- Touching `snobol4dotnet`, `snobol4jvm`, `snobol4python`, `snobol4csharp`.
