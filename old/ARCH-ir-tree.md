# ARCH-ir-tree.md — SNOBOL4 IR Tree (n-ary, as-built)

**Status:** Canonical reference. Updated DYN-44 (2026-04-03).

---

## Overview

The IR is a single n-ary tree of `EXPR_t` nodes, defined in
`src/ir/ir.h` (EKind enum + EXPR_t struct) and
`src/frontend/snobol4/scrip_cc.h` (allocators, accessors, STMT_t, Program).

A compiled SNOBOL4 program is a `Program` — a linked list of `STMT_t`
nodes, each carrying n-ary `EXPR_t*` trees for subject, pattern,
replacement, and goto.

---

## EXPR_t — the node

```c
struct EXPR_t {
    EKind    kind;       /* node type — see EKind below */
    char    *sval;       /* E_QLIT text; E_VAR/E_FNC/E_IDX name; E_KEYWORD name */
    long     ival;       /* E_ILIT value */
    double   dval;       /* E_FLIT value  (fval in ir.h's copy) */
    EXPR_t **children;   /* realloc-grown child array */
    int      nchildren;
};
```

**Key rule:** children[] is the ONLY structural array. There are no
`left`/`right` pointer fields. Everything — binary ops, n-ary ops,
function args, subscript indices — lives in `children[]`.

Accessor macros (never index children[] directly):

```c
expr_left(e)      // children[0]
expr_right(e)     // children[1]
expr_arg(e, i)    // children[i]
expr_nargs(e)     // nchildren
```

Allocators:

```c
expr_new(EKind k)                    // leaf
expr_unary(EKind k, EXPR_t *operand) // nchildren=1
expr_binary(EKind k, EXPR_t *l, EXPR_t *r) // nchildren=2
expr_add_child(EXPR_t *e, EXPR_t *child)    // grow any node
```

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

## Program

```c
typedef struct {
    STMT_t      *head;
    STMT_t      *tail;
    int          nstmts;
    ExportEntry *exports;
    ImportEntry *imports;
} Program;
```

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

## Why n-ary (not binary)

Binary trees for E_ALT and E_CAT would require either:
- left-skewed chains (poor cache locality for long patterns)
- or a dedicated list-spine node (extra indirection)

N-ary children[] with realloc gives flat child arrays. The Byrd-box
executor (`stmt_exec_dyn`) and emitters (`emit_x64.c`, `emit_jvm.c`)
iterate `children[0..nchildren-1]` directly — no recursive unwinding
of binary spines needed.

E_FNC is always n-ary: TRIM(s) → nchildren=1; DUPL(s,n) → nchildren=2;
zero-arg builtins → nchildren=0.

E_IDX is always n-ary: A<i> → nchildren=2; A<i,j> → nchildren=3.

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

## Relationship to flex/bison plan (M-LEX-1, M-PARSE-1)

The IR tree shape does NOT change when lex.c → lex.l and parse.c →
parse.y. The bison grammar emits the same EKind nodes via the same
`expr_new` / `expr_add_child` / `expr_binary` / `expr_unary` calls.
The only change: the body-reconstruction bridge (bbuf/body_toks →
re-lex) is eliminated. IDENT immediately followed by LPAREN (no T_WS)
will be unambiguously E_FNC in the grammar rule, fixing 1013/003.

See `SESSION-dynamic-byrd-box.md` §NOW for M-LEX-1 / M-PARSE-1 plan.
