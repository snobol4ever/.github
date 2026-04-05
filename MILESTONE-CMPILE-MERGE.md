# MILESTONE-CMPILE-MERGE.md — CMPILE.c → IR merge

**Track:** C (scrip-interp / SIL)
**Sprint introduced:** 104
**Priority:** NEW TOP — supersedes EVAL fix as first action

---

## What this milestone is

`CMPILE.c` is `sno4parse.c` renamed and lightly updated in a parallel session.
It has been parse-validated on 500+ SNO corpus files.  It is now the authoritative
SNOBOL4 lex/parser for ALL uses, including `EVAL()`.

The merge task: replace the old `node_to_expr()` bridge (which mapped `NODE*` stype
integers to `EXPR_t*` E_* kinds) with a direct `cmpile_to_expr()` function that maps
CMPILE's SIL stype codes to the canonical `EKind` values in `ir.h`.

This is mechanical — every CMPILE stype has a 1:1 `EKind` counterpart.
The E_* names in ir.h were already derived from SIL, so the mapping is exact.

---

## The stype → EKind mapping (complete)

| CMPILE stype | Value | EKind | Notes |
|---|---|---|---|
| `QLITYP` | 1 | `E_QLIT` | quoted literal |
| `ILITYP` | 2 | `E_ILIT` | integer literal |
| `VARTYP` | 3 | `E_VAR` | variable reference |
| `FNCTYP` | 5 | `E_FNC` | function call (nchildren=args) |
| `FLITYP` | 6 | `E_FLIT` | float literal |
| `ARYTYP` | 7 | `E_IDX` | array/table subscript |
| `SELTYP` | 50 | `E_ALT` | alternative eval `(e1,e2,en)` |
| `ADDFN` | 201 | `E_ADD` | binary `+` |
| `SUBFN` | 202 | `E_SUB` | binary `-` |
| `MPYFN` | 203 | `E_MUL` | binary `*` |
| `DIVFN` | 204 | `E_DIV` | binary `/` |
| `EXPFN` | 205 | `E_POW` | binary `**` |
| `ORFN` | 206 | `E_ALT` | pattern alternation `|` |
| `NAMFN` | 207 | `E_CAPT_COND_ASGN` | conditional capture `.var` |
| `DOLFN` | 208 | `E_CAPT_IMMED_ASGN` | immediate capture `$var` |
| `BIATFN` | 209 | `E_OPSYN` | `@` user-definable binary |
| `BIPDFN` | 210 | `E_OPSYN` | `#` user-definable binary |
| `BIPRFN` | 211 | `E_OPSYN` | `%` user-definable binary |
| `BIAMFN` | 212 | `E_OPSYN` | `&` user-definable binary |
| `BINGFN` | 213 | `E_OPSYN` | `~` user-definable binary |
| `BIQSFN` | 214 | `E_SCAN` | `?` scan/interrogate binary |
| `PLSFN` | 301 | `E_PLS` | unary `+` |
| `MNSFN` | 302 | `E_MNS` | unary `-` |
| `DOTFN` | 303 | `E_NAME` | unary `.X` name-of |
| `INDFN` | 304 | `E_INDIRECT` | unary `$X` indirect ref |
| `STRFN` | 305 | `E_DEFER` | unary `*X` deferred expr |
| `ATFN` | 308 | `E_CAPT_CURSOR` | unary `@X` cursor capture |
| `NEGFN` | 311 | `E_INTERROGATE` | unary `?X` interrogation |
| `NSTTYP` | 4 | *(transparent)* | parenthesized — use single child |
| concatenation | *(implicit)* | `E_CAT` | CMPILE emits children on VARTYP node with nchildren>0 for implicit concat |

**Note on `ORFN` vs `SELTYP`:** Both map to `E_ALT`. `ORFN` is pattern context;
`SELTYP` is value/control context. The eval path handles both identically for now.

**Note on `NSTTYP`:** CMPILE wraps parenthesized sub-expressions in a NSTTYP node
with exactly one child. `cmpile_to_expr()` must unwrap (return the child directly).

**Note on implicit concat:** In CMPILE, bare juxtaposition of terms produces a VARTYP
root with multiple children (the concatenand terms). Detect by `stype==VARTYP &&
nchildren>0` → emit `E_CAT`.

---

## Files to touch

| File | Change |
|---|---|
| `src/frontend/snobol4/CMPILE.c` | Expose `cmpile_parse_expr()` or existing parse entry point |
| `src/frontend/snobol4/sno4parse.c` | **DELETED** — CMPILE.c is the replacement |
| `src/runtime/snobol4/snobol4_pattern.c` | Replace `node_to_expr()` with `cmpile_to_expr()` |
| `src/driver/scrip-interp.c` | Update `eval_via_sno4parse()` → `eval_via_cmpile()` call site |

**Do NOT touch ir.h** — EKind is already correct.  
**Do NOT touch sil_macros.h** — unchanged.  
**Do NOT touch eval_node()** — it consumes EXPR_t and is correct.

---

## Implementation steps

### Step 1 — Write `cmpile_to_expr()`

In `snobol4_pattern.c` (or a new `cmpile_lower.c` if preferred), write:

```c
/* cmpile_to_expr — convert CMPILE NODE* to EXPR_t* for eval_node().
 * Uses SIL stype codes directly — no integer guessing.
 * NODE and EXPR_t are both in scope via their respective headers. */
static EXPR_t *cmpile_to_expr(NODE *n) {
    if (!n) return expr_new(E_NUL);

    /* Transparent wrapper — parenthesized sub-expression */
    if (n->stype == NSTTYP) {
        return n->nchildren == 1 ? cmpile_to_expr(n->children[0]) : expr_new(E_NUL);
    }

    /* Implicit concatenation: VARTYP root with >1 child */
    if (n->stype == VARTYP && n->nchildren > 0) {
        EXPR_t *e = expr_new(E_CAT);
        for (int i = 0; i < n->nchildren; i++)
            expr_add(e, cmpile_to_expr(n->children[i]));
        return e;
    }

    EKind k = stype_to_ekind(n->stype);  /* table lookup — see below */
    EXPR_t *e = expr_new(k);

    /* Leaf payloads */
    if (k == E_QLIT || k == E_VAR)  e->sval = n->text;
    if (k == E_ILIT)                 e->ival  = n->ival;
    if (k == E_FLIT)                 e->fval  = n->fval;

    /* Children (binary ops, function args, subscripts, alt-list) */
    for (int i = 0; i < n->nchildren; i++)
        expr_add(e, cmpile_to_expr(n->children[i]));

    return e;
}
```

`stype_to_ekind()` is a `switch` over the stype → EKind table above.
Default case: `return E_NUL` (log unknown stype in debug mode).

### Step 2 — Replace `eval_via_sno4parse()`

Rename to `eval_via_cmpile()`.  Replace the `node_to_expr(n)` call with
`cmpile_to_expr(n)`.  No other changes to the call site.

### Step 3 — Build

```bash
cd /home/claude/one4all && make scrip-interp 2>&1 | grep "error:" | head -20
```

Fix any include/symbol errors.  CMPILE.c is a self-contained translation unit;
`snobol4_pattern.c` `#include`s it, so NODE typedef is already in scope.

### Step 4 — Test

```bash
CORPUS=/home/claude/corpus bash test/run_interp_broad.sh
```

**Gate:** PASS ≥ 190 (= current baseline — do not break anything).
`expr_eval` passing → PASS=191 is the hoped-for outcome but not required to declare done.

---

## Why EVAL() is also fixed by this

The old `node_to_expr()` guessed at stype integers without the `#define` constants,
causing arithmetic nodes (ADDFN=201, etc.) to fall through to a default string-concat
case.  `cmpile_to_expr()` uses the named constants directly, so `EVAL('1 + 2')` will
correctly produce `E_ADD(E_ILIT(1), E_ILIT(2))` → eval_node returns 3.

---

## Gate summary

| Condition | Result |
|---|---|
| PASS ≥ 190 | ✅ milestone done |
| PASS ≥ 191 (`expr_eval` passes) | ✅ bonus — EVAL fixed too |
| PASS < 190 | ❌ regression — revert and debug |

---

*Introduced sprint 104 · Track C · Lon Jones Cherryholmes + Claude Sonnet 4.6*
