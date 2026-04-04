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
token type codes in CSNOBOL4 `v311.sil`. See `GENERAL-SIL-HERITAGE.md` for
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

---

## STMT_t — SNOBOL4 Detail

The `has_eq` field distinguishes four statement forms (mirrors instaparse grammar `body`):

| Form | subject | pattern | replacement | has_eq |
|------|---------|---------|-------------|--------|
| invoking | present | NULL | NULL | 0 |
| matching | present | present | NULL | 0 |
| assigning | present | NULL | present | 1 |
| replacing | present | present | present | 1 |

Full STMT_t fields for SNOBOL4:

```c
struct STMT_t {
    char    *label;       // NULL if no label
    EXPR_t  *subject;     // always present (E_NUL for null-subject stmts)
    EXPR_t  *pattern;     // NULL if no pattern field
    EXPR_t  *replacement; // NULL if no replacement field
    SnoGoto *go;          // NULL if no goto field
    int      lineno;
    int      is_end;      // 1 if this is the END statement
    int      has_eq;      // 1 if '=' was present
    STMT_t  *next;        // linked list
};
```

---

## SNOBOL4 Parse → IR Mapping

```
parse_expr0   →  E_ASSIGN (binary: subject=children[0], replace=children[1])
                 or  E_SCAN + conditional assign (mch level)
parse_expr2   →  binary &  (E_AND — currently folded into E_FNC("and",...))
parse_expr3   →  E_ALT  n-ary  (|)
parse_expr4   →  E_CAT  n-ary  (whitespace juxtaposition)
parse_expr5   →  binary @  (E_CAPT_CURSOR context)
parse_expr6   →  binary + -
parse_expr7   →  binary #
parse_expr8   →  binary /
parse_expr9   →  binary *
parse_expr10  →  binary %
parse_expr11  →  binary ^ ! **  → E_POW (right-assoc)
parse_expr12  →  binary $ .     → E_CAPT_IMMED_ASGN / E_CAPT_COND_ASGN (right-assoc)
parse_expr13  →  binary ~  (E_TILDE — user-defined binary)
parse_expr14  →  unary prefix (@, ~, ?, &, +, -, *, $, ., !, %, /, #, =, |)
parse_expr15  →  E_IDX postfix subscript  (children[0]=base, [1..]=indices)
parse_expr17  →  atoms: E_QLIT / E_ILIT / E_FLIT / E_NUL / E_VAR / E_KEYWORD
                        E_FNC (function call, n-ary args)
                        E_IDX (array name with subscript)
                        grouped (E) / conditional (E,list) / invoke E()
```

---

## E_SEQ vs E_CAT — SNOBOL4 Juxtaposition

Both are n-ary juxtaposition. E_SEQ is pattern context (can fail, wired to Byrd boxes).
E_CAT is value context (string concatenation, cannot fail). The parser emits E_CAT from
`parse_expr4`; the backend/lowerer promotes to E_SEQ in pattern context.

**Planned fix (M-DYN-SEQ):** Remove `fixup_val_tree` from SNOBOL4 frontend. Keep a
single `E_SEQ` node. Add `stmt_seq(DESCR_t, DESCR_t)` runtime dispatcher that branches
on DT_P at runtime. This correctly handles variables holding DT_P in juxtaposition.

---

## Why N-ary (not binary)

Binary trees for E_ALT and E_CAT would require either left-skewed chains (poor cache
locality) or a dedicated list-spine node (extra indirection). N-ary children[] with
realloc gives flat child arrays. The BB-DRIVER and emitters iterate
`children[0..nchildren-1]` directly — no recursive unwinding of binary spines needed.

---

## Relationship to flex/bison Plan (M-LEX-1, M-PARSE-1)

The IR tree shape does NOT change when `lex.c → lex.l` and `parse.c → parse.y`.
The bison grammar emits the same EKind nodes via the same `expr_new` / `expr_add_child`
/ `expr_binary` / `expr_unary` calls. The body-reconstruction bridge (bbuf/body_toks →
re-lex) is eliminated. IDENT immediately followed by LPAREN (no T_WS) will be
unambiguously E_FNC in the grammar rule, fixing 1013/003.

---

## References

- `SCRIP-SM.md` — SM-LOWER compiles IR → SM_Program
- `PARSER-SNOBOL4.md` through `PARSER-SCRIP.md` — produce this IR
- `MISC-SIL-HERITAGE.md` — E_* name origins
- `RUNTIME.md` — how CODE_t wraps Program* for runtime execution

---

## EKind — node kinds by arity

### Leaves (nchildren = 0)

| Kind | Meaning | Payload |
|------|---------|---------|
| `E_QLIT` | Quoted string / pattern literal | sval=text |
| `E_ILIT` | Integer literal | ival |
| `E_FLIT` | Float literal | dval |
| `E_NUL` | Null / empty value | — |
| `E_VAR` | Variable reference | sval=name |
| `E_KEYWORD` | &IDENT keyword | sval=name |

### Unary (nchildren = 1)

| Kind | Meaning | children[0] |
|------|---------|-------------|
| `E_MNS` | Unary minus | operand |
| `E_INDIRECT` | $expr indirect reference | operand |
| `E_CAPT_CURSOR` | @var cursor capture | var |
| `E_ITERATE` | !E iterate (Icon/Rebus) | expr |
| `E_NULL` | /E succeed-if-null | expr |

### Binary (nchildren = 2)

| Kind | Meaning | [0] | [1] |
|------|---------|-----|-----|
| `E_ASSIGN` | subject = replacement | subject | replacement |
| `E_SCAN` | subject ? pattern | subject | pattern |
| `E_POW` | exponentiation ^ ! ** | base | exp |
| `E_CAPT_COND_ASGN` | .var conditional capture | pattern | var |
| `E_CAPT_IMMED_ASGN` | $var immediate capture | pattern | var |
| `E_ALTERNATE` | Icon alt generator | left | right |

### N-ary (nchildren ≥ 0, grown with expr_add_child)

| Kind | Meaning | children[] |
|------|---------|------------|
| `E_SEQ` | Goal-directed sequence (Byrd-box wiring) | elements in order |
| `E_CAT` | String concatenation (value context) | elements in order |
| `E_ALT` | Pattern alternation \| | alternatives |
| `E_FNC` | Function call / builtin | args [0..n-1] |
| `E_IDX` | Array/table subscript | [0]=base, [1..]=indices |

**E_SEQ vs E_CAT:** Both are n-ary juxtaposition. E_SEQ is pattern
context (can fail, wired to Byrd boxes). E_CAT is value context
(string concatenation, cannot fail). The parser emits E_CAT from
`parse_expr4`; the backend/lowerer promotes to E_SEQ in pattern
context.

**E_ALT:** Built in `parse_expr3`. Each `|`-separated child is
appended with `expr_add_child`. Three alternatives → nchildren=3.

**E_FNC:** `sval` = function name. Each argument appended with
`expr_add_child`. Zero-arg call → nchildren=0.

**E_IDX:** `sval` = array/table name. `children[0]` = base expression.
`children[1..nchildren-1]` = index expressions (one per `<i,j>` slot).

---


---

## STMT_t — the statement node

```c
struct STMT_t {
    char    *label;       // NULL if no label
    EXPR_t  *subject;     // always present (E_NUL for null-subject stmts)
    EXPR_t  *pattern;     // NULL if no pattern field
    EXPR_t  *replacement; // NULL if no replacement field
    SnoGoto *go;          // NULL if no goto field
    int      lineno;
    int      is_end;      // 1 if this is the END statement
    int      has_eq;      // 1 if '=' was present (distinguishes assigning vs matching)
    STMT_t  *next;        // linked list
};
```

Four statement forms (mirrors instaparse grammar `body`):

| Form | subject | pattern | replacement | has_eq |
|------|---------|---------|-------------|--------|
| invoking | present | NULL | NULL | 0 |
| matching | present | present | NULL | 0 |
| assigning | present | NULL | present | 1 |
| replacing | present | present | present | 1 |

---


---

## Parse → IR mapping (SNOBOL4 frontend)

```
parse_expr0   →  E_ASSIGN (binary: subject=children[0], replace=children[1])
                 or  E_SCAN + conditional assign (mch level)
parse_expr2   →  binary &  (E_AND — currently folded into E_FNC("and",...))
parse_expr3   →  E_ALT  n-ary  (|)
parse_expr4   →  E_CAT  n-ary  (whitespace juxtaposition)
parse_expr5   →  binary @  (E_CAPT_CURSOR context)
parse_expr6   →  binary + -
parse_expr7   →  binary #
parse_expr8   →  binary /
parse_expr9   →  binary *
parse_expr10  →  binary %
parse_expr11  →  binary ^ ! **  → E_POW (right-assoc)
parse_expr12  →  binary $ .     → E_CAPT_IMMED_ASGN / E_CAPT_COND_ASGN (right-assoc)
parse_expr13  →  binary ~  (E_TILDE — user-defined binary)
parse_expr14  →  unary prefix (@, ~, ?, &, +, -, *, $, ., !, %, /, #, =, |)
parse_expr15  →  E_IDX postfix subscript  (children[0]=base, [1..]=indices)
parse_expr17  →  atoms: E_QLIT / E_ILIT / E_FLIT / E_NUL / E_VAR / E_KEYWORD
                        E_FNC (function call, n-ary args)
                        E_IDX (array name with subscript)
                        grouped (E) / conditional (E,list) / invoke E()
```

---


---

## File locations

| File | Role |
|------|------|
| `src/ir/ir.h` | EKind enum, EXPR_t struct, EKind name table |
| `src/frontend/snobol4/scrip_cc.h` | STMT_t, Program, expr_new/add_child/binary/unary |
| `src/frontend/snobol4/parse.c` | Parser: source → EXPR_t/STMT_t/Program |
| `src/frontend/snobol4/lex.c` | One-pass lexer: source → token queue |
| `src/ir/ir_print.c` | Debug printer (walks children[]) |
| `src/driver/scrip-interp.c` | Tree-walk interpreter (DYN session) |

---

