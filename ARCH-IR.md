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
**Binary:** E_ADD, E_SUB, E_MUL, E_DIV, E_EXP, E_SEQ, E_CAT, E_ALT, E_CAPT_COND_ASGN, E_CAPT_IMM_ASGN, E_IDX, E_CHOICE (Icon/Prolog), E_CLAUSE (Prolog), E_UNIFY (Prolog), E_CUT (Prolog)
**N-ary:** E_FNC (function call), E_CONCAT (string concat chain), E_LIST, E_APPLY
**Pattern:** E_ARBNO, E_ARBN, E_SCAN, E_POS, E_RPOS, E_LEN, E_RLEN

## STMT_t — the statement

⚠️ Field names vary across doc versions — verify against `src/ir/ir.h`
before coding.  Older internal docs used `replacement` and
`SnoGoto *go`; current ir.h is the source of truth.

```c
struct STMT_t {
    char    *label;
    EXPR_t  *subject;
    EXPR_t  *pattern;
    EXPR_t  *replacement;  /* NULL if no replacement */
    EXPR_t  *goto_s;       /* :S(label) — verify field name in ir.h */
    EXPR_t  *goto_f;       /* :F(label) — verify field name in ir.h */
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

---

## Polyglot Program* (U-12 through U-19)

A single `Program*` may contain statements from multiple source languages.
`parse_scrip_polyglot()` in `scrip.c` parses a `.scrip` fenced-block file,
compiling each block with its own frontend, and appends all `STMT_t` chains
in source order into one `Program*`.

Fence syntax:

````
```SNOBOL4
  ... snobol4 source ...
```
```Icon
  ... icon source ...
```
```Prolog
  ... prolog source ...
```
````

Tags are matched case-insensitively: `SNOBOL4`, `Icon`, `Prolog`.
Unknown tags are skipped. Each block is compiled independently by its
frontend; the resulting `STMT_t` chains are linked together in order.

### STMT_t.lang — language tag (U-12)

`STMT_t` carries an `int lang` field (defined in `scrip_cc.h`):

```c
#define LANG_SNO  0   /* SNOBOL4 (default — zero from calloc) */
#define LANG_ICN  1   /* Icon */
#define LANG_PL   2   /* Prolog */
```

Set by each frontend:
- SNOBOL4: `0` by default (calloc zero-initialises).
- Icon: `icon_driver.c` sets `st->lang = LANG_ICN` for every Icon statement.
- Prolog: `prolog_lower.c` sets `s->lang = LANG_PL` at both lowering sites.

The `lang` field is the sole discriminator used by `execute_program` and
`polyglot_init` to dispatch each statement to the correct runtime.

### polyglot_init — unified initialisation (U-14)

```c
static void polyglot_init(Program *prog);
```

Single walk over `prog->head`. Populates all three runtime tables at once:

| Language | What it does |
|----------|-------------|
| LANG_SNO | `label_table_build` + `prescan_defines` |
| LANG_ICN | zero icn_* state; collect `E_FNC` subjects → `icn_proc_table` |
| LANG_PL  | `prolog_atom_init`; `trail_init`; collect `E_CHOICE`/`E_CLAUSE` → `g_pl_pred_table`; set `g_pl_active=1` if any PL stmts present |

All three entry points (`--ir-run`, `--sm-run`, single-language modes) call
`polyglot_init`. Individual per-language init sequences have been removed.

### execute_program dispatch (U-15)

Inside the statement loop, `st->lang` selects the execution path:

```
LANG_SNO → existing SNOBOL4 path (subject / pattern / replacement / goto)
LANG_ICN → skip inline (E_FNC defs registered by polyglot_init);
            call icn_call_proc(main) after the loop
LANG_PL  → call interp_eval(st->subject) with g_pl_active=1;
            call pl main/0 after the loop if present
```

---

## The Three Broker Modes — One SM (U-16)

The stack machine has three statement-level opcodes, one per broker mode:

```
SM_EXEC_STMT  →  exec_stmt()  →  bb_broker(root, BB_SCAN, ...)   SNOBOL4
SM_BB_PUMP    →  bb_broker(root, BB_PUMP, body_fn, arg)           Icon
SM_BB_ONCE    →  bb_broker(root, BB_ONCE, NULL, NULL)             Prolog
```

Defined in `src/runtime/x86/sm_prog.h`. Handled in `src/runtime/x86/sm_interp.c`.

`SM_BB_PUMP` and `SM_BB_ONCE` are stubbed in the interpreter (set `last_ok=0`)
pending full `sm_lower` support — the `--ir-run` path is the active polyglot path.
`BB_SCAN` is already fully wired via `SM_EXEC_STMT` → `exec_stmt` → `bb_broker(BB_SCAN)`.

### BrokerMode — the three drive modes

Defined in `src/runtime/x86/bb_box.h`:

```c
typedef enum { BB_SCAN, BB_PUMP, BB_ONCE } BrokerMode;
```

| Mode | Language | Drive behaviour |
|------|----------|----------------|
| `BB_SCAN` | SNOBOL4 | Try cursor positions 0..Ω; stop on first match |
| `BB_PUMP` | Icon | Call `body_fn` for every value produced until ω |
| `BB_ONCE` | Prolog | Call α once; report γ or ω; OR-box handles retry |

All three modes share one `bb_broker()` entry point in
`src/runtime/x86/bb_broker.c` and one value type `DESCR_t` (16 bytes).

### Architectural insight

`SM_EXEC_STMT`, `SM_BB_PUMP`, and `SM_BB_ONCE` are the same machine
driven three different ways. SNOBOL4 pattern boxes, Icon generator boxes,
and Prolog clause boxes are all `bb_node_t` nodes returning `DESCR_t`.
The broker does not know or care which language built the box graph —
cross-language box composition works at the IR level without any special
casing. See `test/cross_lang.scrip` for a working end-to-end demonstration.
