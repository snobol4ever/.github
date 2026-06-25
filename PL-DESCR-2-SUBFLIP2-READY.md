# PL-DESCR-2 SUB-FLIP 2 — READY-TO-APPLY (companion to PL-DESCR-2-SUBFLIP2-MAP.md)

Paste-ready bodies for the DETERMINISTIC parts (no codegen debugging). Apply in one batch with the template
edits from the MAP, build, then fail-fast on fib. `82d4c4d` is the recovery point.

Includes both runtime files need at top:
```c
#include "../parser/prolog/pl_cell.h"
#define PL_CELL_ALLOC(n) GC_MALLOC(n)
#include "../parser/prolog/pl_cell_conv.h"
```
(adjust the relative path per file; `unification.c` and `rt_runtime.c` are in `src/runtime/`, so `../parser/...`.)

---

## A. The trail global (define ONCE — put next to g_resolve_trail's definition)
```c
pl_trail_t g_pl_trail = { 0, 0, 0 };
```

## B. rt_runtime.c — rt_trail_mark / rt_trail_unwind (retarget to g_pl_trail)
```c
int rt_trail_mark(void) {
    extern pl_trail_t g_pl_trail;
    return pl_trail_mark(&g_pl_trail);
}
void rt_trail_unwind(int mark) {
    extern pl_trail_t g_pl_trail;
    pl_trail_unwind(&g_pl_trail, mark);
}
```
(rt_trail_mark_push / rt_trail_unwind_top: same swap — `trail_mark/trail_unwind(&g_resolve_trail,...)` →
`pl_trail_mark/pl_trail_unwind(&g_pl_trail,...)`.)

## C. rt_runtime.c — the HOT is/cmp helpers (cell-native; pl_unify trails internally, mark/unwind for partial-fail)
```c
int rt_pl_is_cell_int(void *lhs_cell, long val) {
    extern pl_trail_t g_pl_trail;
    pl_cell_t *lhs = (pl_cell_t *)lhs_cell; if (!lhs) return 0;
    pl_cell_t w = pl_make_int((int64_t)val);
    int m = pl_trail_mark(&g_pl_trail);
    if (!pl_unify(lhs, &w, &g_pl_trail)) { pl_trail_unwind(&g_pl_trail, m); return 0; }
    return 1;
}
int rt_pl_is_cell_float(void *lhs_cell, double val) {
    extern pl_trail_t g_pl_trail;
    pl_cell_t *lhs = (pl_cell_t *)lhs_cell; if (!lhs) return 0;
    pl_cell_t w = pl_make_float(val);
    int m = pl_trail_mark(&g_pl_trail);
    if (!pl_unify(lhs, &w, &g_pl_trail)) { pl_trail_unwind(&g_pl_trail, m); return 0; }
    return 1;
}
int rt_pl_arith_cmp_cell_val(const char *op, void *lhs_cell, long lhs_ival, void *rhs_cell, long rhs_ival) {
    if (!op) return 0;
    double l = (double)lhs_ival, r = (double)rhs_ival;
    if (lhs_cell) { pl_cell_t *t = pl_deref((pl_cell_t *)lhs_cell);
        if ((int)t->v == DT_I) l = (double)t->i; else if ((int)t->v == DT_R) l = t->r; else return 0; }
    if (rhs_cell) { pl_cell_t *t = pl_deref((pl_cell_t *)rhs_cell);
        if ((int)t->v == DT_I) r = (double)t->i; else if ((int)t->v == DT_R) r = t->r; else return 0; }
    if (strcmp(op,"=:=")==0) return (l==r); if (strcmp(op,"=\\=")==0) return (l!=r);
    if (strcmp(op,"<")==0)   return (l< r); if (strcmp(op,">")==0)   return (l> r);
    if (strcmp(op,"=<")==0||strcmp(op,"<=")==0) return (l<=r); if (strcmp(op,">=")==0) return (l>=r);
    return 0;
}
int rt_pl_is_cell_arith(void *lhs_cell, void *rhs_cell, const char *op, long rhs_ival) {
    extern pl_trail_t g_pl_trail;
    pl_cell_t *lhs = (pl_cell_t *)lhs_cell; if (!lhs) return 0;
    double rv = (double)rhs_ival;
    if (rhs_cell) {
        pl_cell_t *t = pl_deref((pl_cell_t *)rhs_cell);
        if ((int)t->v == DT_I) rv = (double)t->i; else if ((int)t->v == DT_R) rv = t->r; else return 0;
        if (!op) {}
        else if (strcmp(op,"+")==0) rv = rv + (double)rhs_ival;
        else if (strcmp(op,"-")==0) rv = rv - (double)rhs_ival;
        else if (strcmp(op,"*")==0) rv = rv * (double)rhs_ival;
        else if (strcmp(op,"mod")==0||strcmp(op,"rem")==0) { long li=(long)rv; if(!rhs_ival) return 0; rv=(double)(li%rhs_ival); }
        else if (strcmp(op,"//")==0||strcmp(op,"div")==0)  { long li=(long)rv; if(!rhs_ival) return 0; rv=(double)(li/rhs_ival); }
        else if (strcmp(op,"/")==0) { if(!rhs_ival) return 0; rv = rv / (double)rhs_ival; }
    }
    long ival = (long)rv;
    pl_cell_t w = ((double)ival == rv) ? pl_make_int(ival) : pl_make_float(rv);
    int m = pl_trail_mark(&g_pl_trail);
    if (!pl_unify(lhs, &w, &g_pl_trail)) { pl_trail_unwind(&g_pl_trail, m); return 0; }
    return 1;
}
int rt_pl_is_cell_bivar(void *lhs_cell, void *cell1, void *cell2, const char *op) {
    extern pl_trail_t g_pl_trail;
    pl_cell_t *lhs = (pl_cell_t *)lhs_cell; if (!lhs || !cell1 || !cell2) return 0;
    pl_cell_t *t1 = pl_deref((pl_cell_t *)cell1), *t2 = pl_deref((pl_cell_t *)cell2);
    double a = ((int)t1->v==DT_I) ? (double)t1->i : ((int)t1->v==DT_R) ? t1->r : -1e300;
    double b = ((int)t2->v==DT_I) ? (double)t2->i : ((int)t2->v==DT_R) ? t2->r : -1e300;
    if (a==-1e300 || b==-1e300) return 0;
    double rv;
    if (!op || strcmp(op,"+")==0) rv=a+b; else if (strcmp(op,"-")==0) rv=a-b; else if (strcmp(op,"*")==0) rv=a*b;
    else if (strcmp(op,"/")==0) { if(!b) return 0; rv=a/b; }
    else if (strcmp(op,"//")==0||strcmp(op,"div")==0) { long la=(long)a,lb=(long)b; if(!lb) return 0; rv=(double)(la/lb); }
    else if (strcmp(op,"mod")==0||strcmp(op,"rem")==0) { long la=(long)a,lb=(long)b; if(!lb) return 0; rv=(double)(la%lb); }
    else return 0;
    long ival = (long)rv;
    pl_cell_t w = ((double)ival == rv) ? pl_make_int(ival) : pl_make_float(rv);
    int m = pl_trail_mark(&g_pl_trail);
    if (!pl_unify(lhs, &w, &g_pl_trail)) { pl_trail_unwind(&g_pl_trail, m); return 0; }
    return 1;
}
```

## D. rt_runtime.c — the @</@> structural compare (BRIDGE: cell→Term view ×2)
```c
int rt_term_cmp_terms(const char *op, void *t0, void *t1) {
    if (!op) return 0;
    int c = resolve_term_compare(pl_cell_to_term((pl_cell_t *)t0), pl_cell_to_term((pl_cell_t *)t1));
    if (strcmp(op,"==")==0)   return (c==0); if (strcmp(op,"\\==")==0) return (c!=0);
    if (strcmp(op,"@<")==0)   return (c< 0); if (strcmp(op,"@>")==0)   return (c> 0);
    if (strcmp(op,"@=<")==0)  return (c<=0); if (strcmp(op,"@>=")==0)  return (c>=0);
    return 0;
}
```
(Confirm bb_det_cmp passes BOTH arith `=:=` cmps (→ rt_pl_arith_cmp_cell_val, native) and standard-order `@<`
cmps (→ rt_term_cmp_terms, bridge). The template chooses by op; both call sites become `lea`.)

## E. unification.c — rt_unify_terms (now two cell ADDRESSES) + the const/float unifiers
```c
int rt_unify_terms(void *l, void *r) {
    extern pl_trail_t g_pl_trail;
    pl_cell_t *a = (pl_cell_t *)l, *b = (pl_cell_t *)r; if (!a || !b) return 0;
    int m = pl_trail_mark(&g_pl_trail);
    if (!pl_unify(a, b, &g_pl_trail)) { pl_trail_unwind(&g_pl_trail, m); return 0; }
    return 1;
}
int rt_pl_unify_cell_const(void *cell, int kind, long ival, const char *sval) {
    extern pl_trail_t g_pl_trail;
    pl_cell_t *c = (pl_cell_t *)cell; if (!c) return 0;
    pl_cell_t w;
    switch (kind) {
        case IR_ATOM:  w = pl_make_atom(prolog_atom_intern(sval ? sval : "[]")); break;
        case IR_LIT_I: w = pl_make_int(ival); break;
        default:       w = pl_make_int(ival); break;
    }
    int m = pl_trail_mark(&g_pl_trail);
    if (!pl_unify(c, &w, &g_pl_trail)) { pl_trail_unwind(&g_pl_trail, m); return 0; }
    return 1;
}
int rt_pl_unify_cell_float(void *cell, double dval) {
    extern pl_trail_t g_pl_trail;
    pl_cell_t *c = (pl_cell_t *)cell; if (!c) return 0;
    pl_cell_t w = pl_make_float(dval);
    int m = pl_trail_mark(&g_pl_trail);
    if (!pl_unify(c, &w, &g_pl_trail)) { pl_trail_unwind(&g_pl_trail, m); return 0; }
    return 1;
}
```

## F. unification.c — write / type-test (BRIDGE; read-only materialise + existing Term printer/tester)
```c
void rt_pl_write_cell(void *cell)           { extern void pl_write(Term *);           pl_write(pl_cell_to_term((pl_cell_t *)cell)); }
void rt_pl_writeq_cell(void *cell)          { extern void pl_writeq(Term *);          pl_writeq(pl_cell_to_term((pl_cell_t *)cell)); }
void rt_pl_write_canonical_cell(void *cell) { extern void pl_write_canonical(Term *); pl_write_canonical(pl_cell_to_term((pl_cell_t *)cell)); }
int  rt_pl_type_test_cell(void *cell, const char *fn) { extern int rt_type_test_term(const char *, void *); return rt_type_test_term(fn, pl_cell_to_term((pl_cell_t *)cell)); }
```

## G. unification.c — frame init (inline var cells; drop the g_resolve_env sync)
```c
void rt_pl_cells_init(void **cells, int n) {
    char *base = (char *)cells;
    for (int i = 0; i < n; i++) pl_init_var((pl_cell_t *)(base + (size_t)16 * (size_t)i), i);
}
void rt_pl_gz_init(void *frame, int nslots) {
    prolog_atom_init();
    char *base = (char *)frame;
    for (int i = 0; i < nslots; i++) pl_init_var((pl_cell_t *)(base + 8 + (size_t)16 * (size_t)i), i);
}
```
(`rt_enter` UNCHANGED: alloc `8 + 16*nslots`.)

## H. The new cell compound builder (used by the gzu_build compound arm) — put in unification.c
```c
void *rt_pl_compound_cell(const char *functor_name, int arity, void *arg_words) {
    pl_cell_t *src = (pl_cell_t *)arg_words;
    pl_cell_t *blk = (pl_cell_t *)GC_MALLOC((size_t)(arity > 0 ? arity : 1) * sizeof(pl_cell_t));
    for (int i = 0; i < arity; i++) blk[i] = src[i];           /* copy the 16-byte words (self-ref var → ref alias) */
    int fid = prolog_atom_intern(functor_name ? functor_name : "[]");
    pl_cell_t *out = (pl_cell_t *)GC_MALLOC(sizeof(pl_cell_t));
    *out = pl_make_compound(fid, arity, blk);                  /* {DT_PLREF, fid<<16|arity, blk} */
    return out;                                                /* returns a cell ADDRESS (operand for unify) */
}
```

## I. Dead-on-GZ helpers — gut so g_resolve_env can be deleted (m2 is unwired 0/115; behavior moot)
```c
/* arithmetic.c rt_arith: DELETE the two `if (lk==IR_LOGICVAR && g_resolve_env ...)` / `rk==...` blocks and the
   two `extern` lines; logicvar operands fall to the existing `lv=li` / `rv=ri` literal defaults. */

/* unification.c — these are slot-indexed, only the legacy bb_unify box calls them; gut to compile env-free: */
int rt_unify_const(int slot, int kind, long ival, const char *sval, double dval) { (void)slot;(void)kind;(void)ival;(void)sval;(void)dval; return 0; }
int rt_unify_var_var(int lslot, int rslot) { (void)lslot;(void)rslot; return 0; }

/* unification.c rt_node_to_term IR_LOGICVAR arm — env-free: */
case IR_LOGICVAR: { int slot = (int)ival; return term_new_var(slot); }

/* DELETE rt_pl_env_ensure entirely (def + the `extern void rt_pl_env_ensure` lines that referenced it). */
```

## J. Delete g_resolve_env + ratchet the gate
- `src/runtime/builtins/resolution.c:22` — delete `Term **g_resolve_env = NULL;`
- `src/runtime/builtins/resolution.h:35` — delete `extern Term **g_resolve_env;`
- `src/driver/polyglot.c:57` — delete `g_resolve_env = NULL;`
- `src/driver/scrip.c:3234` — delete `extern Term **g_resolve_env;` (verify the surrounding emit helper drops its use)
- `scripts/test_gate_pl_no_new_global.sh` — remove `g_resolve_env` from the LEGACY-DOOMED list; `DOOMED_FLOOR` 15 → 14.

---

## K. The DEEP builtins (functor/arg/univ/copy_term/sort/numbervars/term_string) — uniform 3-point bridge wrap
Each currently: `Term *x = term_deref((Term*)cell); ... build resultT ...; rt_unify_terms(dst_cell, resultT);` with an
internal `trail_mark(&g_resolve_trail)`. Apply the SAME three edits to each (they sit in unification.c 192–911):
1. INPUT:  `term_deref((Term*)cell)`  →  `pl_cell_to_term((pl_cell_t*)cell)`   (read-only Term view of the cell)
2. RESULT: `rt_unify_terms(dst_cell, resultT)`  →  `pl_unify_term_into_cell((pl_cell_t*)dst_cell, resultT, &g_pl_trail)`
3. TRAIL:  internal `trail_mark/trail_unwind(&g_resolve_trail,...)`  →  `pl_trail_mark/pl_trail_unwind(&g_pl_trail,...)`
UNBOUND output args (e.g. functor's name/arity when t0 is bound) are already handled by the result-unify path;
do NOT materialise an unbound input var and write back through it (the conv-header landmine). The clause store
(assertz/retract/dyniter) keeps Term clauses: cell→Term at assert, Term→cell (`pl_unify_term_into_cell`) at
unify-against-store.

## L. Template edits (from the MAP — apply with the above)
- Pattern A (~50 sites): `mov <reg>,FRQ(GZ_CELL_OFF(s))` → `lea <reg>,FR(GZ_CELL_OFF(s))` where the reg is a helper
  cell arg. (FR = lea-form of the frame ref; confirm the lea macro name — `FR(...)` is used at the existing lea
  sites bb_cell_call L24 etc.)
- `gzu_build` (bb_cell_unify.cpp): SPLIT — operand path returns a cell ADDRESS (var → `lea rax,[r12+off]`; literal →
  call a tiny `rt_pl_lit_cell(kind,ival,sval,dval)` returning a heap cell addr); compound arm builds an `arity*16`
  rsp word-array (per-arg `movdqu` of the operand cell word) then `call rt_pl_compound_cell` (§H) — NOT
  rt_compound_build_n. The bcu_sh==0 path stores the two operand ADDRESSES to rsp then calls rt_unify_terms.
- Pattern C arg seam (bb_cell_call + bb_callee_frame): args→cell ADDRESSES (lea); 16-byte `movdqu` copy into the
  formal cell. Child-slot (closure ptr) stays `mov`. See MAP §1 Pattern C for the exact instruction sequence.
- Patterns B/D: untouched.

## M. Build + fail-fast validate (MAP §6)
`make -j4 scrip && make libscrip_rt` → smoke → **fib first** → rung suite 115/115 m3+m4 → bench 16/0/0 →
no-new-global (doomed 14) → no-vstack 0. Regen `.s` only on full green, then commit/push/handoff_status.
RISK ORDER to debug: (1) arg copy on fib, (2) compound builder on zebra/qsort, (3) trail on queens_8, (4) deep
bridge on term-ops rungs.
