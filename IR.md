# IR.md — Intermediate Representation (one4all / all4one)

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Status:** CANONICAL — updated DYN-44 (2026-04-03). Do not duplicate elsewhere.

---

## What It Is

One IR for all frontends. Every lexer/parser (SNOBOL4, Icon, Prolog, Snocone,
Rebus, Scrip) produces this IR. Every SM-LOWER pass compiles this IR to
SM_Program instructions.

The IR is a `Program*` — a linked list of `STMT_t` nodes, each carrying
n-ary `EXPR_t*` trees for subject, pattern, replacement, and goto expressions.

---

## EXPR_t — the node

```c
struct EXPR_t {
    EKind    kind;       /* node type — EKind enum */
    char    *sval;       /* string payload: E_QLIT text, E_VAR/E_FNC/E_IDX name */
    long     ival;       /* integer payload: E_ILIT value */
    double   dval;       /* float payload: E_FLIT value */
    EXPR_t **children;   /* realloc-grown child array */
    int      nchildren;
};
```

Accessor macros (never index children[] directly):
```c
expr_left(e)      // children[0]
expr_right(e)     // children[1]
expr_arg(e, i)    // children[i]
expr_nargs(e)     // nchildren
```

---

## EKind — all node kinds

### Leaves (nchildren = 0)

| Kind | Meaning | Payload |
|------|---------|---------|
| `E_QLIT` | Quoted string literal | sval |
| `E_ILIT` | Integer literal | ival |
| `E_FLIT` | Float literal | dval |
| `E_NUL` | Null / empty | — |
| `E_VAR` | Variable reference | sval=name |
| `E_KEYWORD` | &KEYWORD | sval=name |

### Unary (nchildren = 1)

| Kind | Meaning |
|------|---------|
| `E_MNS` | Unary minus |
| `E_INDIRECT` | $ indirect |
| `E_CAPT_CURSOR` | @ cursor capture |
| `E_NAME` | . name-of |
| `E_DEFER` | * deferred pattern |
| `E_ITERATE` | ! iterate (Icon/Rebus) |
| `E_NULL` | / succeed-if-null |

### Binary (nchildren = 2)

| Kind | Meaning |
|------|---------|
| `E_ADD` | + |
| `E_SUB` | - |
| `E_MUL` | * |
| `E_DIV` | / |
| `E_EXP` | ** |
| `E_SEQ` | juxtaposition (string concat or pattern cat — resolved at runtime) |
| `E_CAT` | explicit concat (Icon \|\|, Snocone) |
| `E_ALT` | \| alternation |
| `E_CAPT_COND_ASGN` | . conditional assignment |
| `E_CAPT_IMM_ASGN` | $ immediate assignment |
| `E_IDX` | subscript |
| `E_CHOICE` | Icon/Prolog choice point |
| `E_CLAUSE` | Prolog clause |
| `E_UNIFY` | Prolog unification |
| `E_CUT` | Prolog cut |

### N-ary (nchildren = N)

| Kind | Meaning |
|------|---------|
| `E_FNC` | function call — sval=name, children=args |
| `E_CONCAT` | string concat chain |
| `E_LIST` | list literal |
| `E_APPLY` | APPLY() call |

---

## STMT_t — one statement

```c
struct STMT_t {
    char    *label;     /* source label or NULL */
    EXPR_t  *subject;   /* subject expression or NULL */
    EXPR_t  *pattern;   /* pattern expression or NULL */
    EXPR_t  *repl;      /* replacement expression or NULL */
    char    *go_s;      /* :S(label) or NULL */
    char    *go_f;      /* :F(label) or NULL */
    STMT_t  *next;      /* linked list */
};
```

---

## Program* — the compiled unit

```c
struct Program {
    STMT_t  *head;     /* first statement */
    STMT_t  *tail;     /* last statement */
    int      nstmts;
};
```

---

## What Comes From IR

The IR is the input to `SM-LOWER`, which produces a `SM_Program`
(see `SCRIP-SM.md`). The IR is **not** directly interpreted or emitted.
Any component that tree-walks IR directly (instead of going through
SM-LOWER) is doing it wrong.

---

## SIL Heritage

The `E_*` node names derive from the SIL (SNOBOL4 Implementation Language)
token type codes in CSNOBOL4 `v311.sil`. See `ARCH-sil-heritage.md` for
the full lineage table connecting every `E_*` to its SIL origin.

---

## Files

| File | Role |
|------|------|
| `src/ir/ir.h` | EKind enum, EXPR_t struct |
| `src/frontend/snobol4/scrip_cc.h` | allocators, STMT_t, Program |
| `src/frontend/snobol4/parse.c` | SNOBOL4 → IR |
| `src/frontend/icon/icon_parse.c` | Icon → IR |
| `src/frontend/prolog/prolog_parse.c` | Prolog → IR |

---

## References

- `SCRIP-SM.md` — SM-LOWER compiles IR → SM_Program
- `PARSER-SNOBOL4.md` through `PARSER-SCRIP.md` — produce this IR
- `ARCH-sil-heritage.md` → `MISC-SIL-HERITAGE.md` — E_* name origins
