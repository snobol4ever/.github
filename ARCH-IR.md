# ARCH-IR.md — Intermediate Representation

The shared IR produced by all frontends. Every frontend compiles to this.
SM-LOWER compiles this IR to SM_Program instructions.

## EXPR_t — the node

```c
struct EXPR_t {
    EKind    kind;       /* node type */
    char    *sval;       /* string: E_QLIT text, E_VAR/E_FNC/E_IDX name */
    long     ival;       /* integer: E_ILIT value */
    double   dval;       /* float: E_FLIT value */
    EXPR_t **children;
    int      nchildren;
};
// Accessors: expr_left(e), expr_right(e), expr_arg(e,i), expr_nargs(e)
```

## EKind — node kinds

**Leaves:** E_QLIT, E_ILIT, E_FLIT, E_NUL, E_VAR, E_KEYWORD
**Unary:** E_MNS, E_NOT, E_IND (indirect $), E_NAME (.), E_ATP (@), E_STR (*), E_TILDE
**Binary:** E_ADD, E_SUB, E_MUL, E_DIV, E_POW, E_CAT, E_SEQ, E_OR, E_CONCAT, E_ASSIGN, E_COND_ASSIGN, E_IMM_ASSIGN, E_MATCH
**N-ary:** E_FNC (function call), E_IDX (subscript), E_SELECT (alternation)
**Pattern:** E_ARBNO, E_ARBN, E_SCAN, E_POS, E_RPOS, E_LEN, E_RLEN

## STMT_t — the statement

```c
struct STMT_t {
    char    *label;
    EXPR_t  *subject;
    EXPR_t  *pattern;
    EXPR_t  *replace;
    EXPR_t  *goto_s;    /* :S(label) */
    EXPR_t  *goto_f;    /* :F(label) */
    STMT_t  *next;
};
```

## Five phases of a SNOBOL4 statement

```
Label:  Subject  Pattern  =Replacement  :S(goto)  :F(goto)
```

| Phase | Name | Can Fail | Backtracks |
|-------|------|----------|------------|
| 1 | Subject eval | yes | no |
| 2 | Pattern build | yes | no |
| 3 | Match | yes | YES — BB-DRIVER → BB-GRAPH |
| 4 | Replacement eval | yes | no |
| 5 | Assign | no | no |

Phases 1,2,4,5: straight-line stack machine. Phase 3: Byrd box graph.
