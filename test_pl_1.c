#ifdef __GNUC__
#define __kernel
#define __global
#include <malloc.h>
#include <string.h>
#include <stdbool.h>
extern int printf(const char *, ...);
#endif
/*------------------------------------------------------------------------------------------------*/
/*  test_pl_1.c — PL-GZ-0 SEED: Proebsting four-port translation of PROLOG, written down for      */
/*  the first time.  The paper (§4.6) never gave the procedure-call template and never gave ANY    */
/*  Prolog template; gprolog/swipl are PRINT oracles only.  Source program:                        */
/*                                                                                                 */
/*      edge(a,b).  edge(b,c).  edge(b,d).                                                         */
/*      path(X,Y) :- edge(X,Y).                                                                    */
/*      path(X,Z) :- edge(X,Y), path(Y,Z).                                                         */
/*      firstpath(Q) :- path(a,Q), !.                                                              */
/*      ?- path(a,Q), write(Q), nl, fail.        % prints b c d (all solutions)                    */
/*      ?- firstpath(Q), write(Q), nl.           % prints b     (cut commits to first)             */
/*                                                                                                 */
/*  THE LAWS EMBODIED (one per former PL-BBL ledger row):                                          */
/*    clause cursor + trail-mark  = slots in the choice's OWN frame row (test_sno_1 ARBNO arena)   */
/*    activation env              = ζ-TREE: call site owns child-frame ptr, enter()-reset on α     */
/*    verdict                     = THE RETURN VALUE (test_sno_3 empty-str idiom) — no last_ok     */
/*    cut                         = pure WIRING (firstpath_β routes to ω, never resumes path)      */
/*    trail                       = the ONE shared spine; logic vars = frame cells; ALL trailed    */
/*    recursion spine             = the C call stack (the NO-VALUE-STACK carve-out)                */
/*                                                                                                 */
/*  SEED → EMITTED PROJECTION.  C cannot jump to a label inside another function, so this seed     */
/*  prints cross-predicate α/β entry as a C call — the SAME convention as test_sno_2/3/4.c.        */
/*  This is NOT license for brokered `(ζ, int entry)` boxes in src/ — that signature stays         */
/*  FORBIDDEN there (NO C BYRD-BOX FUNCTIONS fact rule).  The mapping the emitter must realize:    */
/*      v = path(&ζ->p2_ζ, α, …)      ⇒  jmp path_α   (callee frame slots reset at α)              */
/*      v = path(&ζ->p2_ζ, β, …)      ⇒  jmp path_β                                                */
/*      return 1 / return 0 + λ-test  ⇒  callee jumps to the caller's γ / ω continuation           */
/*      the `int entry` dispatch      ⇒  does not exist — α and β ARE the two emitted labels       */
/*------------------------------------------------------------------------------------------------*/
typedef struct { unsigned int pos; __global char * buffer; } output_t;
/*------------------------------------------------------------------------------------------------*/
void    write_nl(output_t * out)                 { printf("%s", "\n"); }
void    write_sz(output_t * out, const char * s) { printf("%s", s); }
void    write_atom(output_t * out, long a)       { printf("%c", (char) a); }
void    write_flush(output_t * out)              {}
/*------------------------------------------------------------------------------------------------*/
static const int α = 0;
static const int β = 1;
static output_t * out = (output_t *) 0;
/*------------------------------------------------------------------------------------------------*/
#define ENTER(ref, size) enter((void **) (ref), (size))
static inline void * enter(void ** ζζ, size_t size) {
    void * ζ = *ζζ;
    if (size)
        if (ζ) memset(ζ, 0, size);
        else ζ = *ζζ = calloc(1, size);
    return ζ;
}
/*------------------------------------------------------------------------------------------------*/
/*  LOGIC VARIABLES — frame cells.  UNBOUND / ATOM / REF chain.  deref + bind, EVERY bind trailed. */
/*------------------------------------------------------------------------------------------------*/
typedef struct _cell cell_t;
typedef struct _cell { int tag; long atom; cell_t * ref; } cell_t;
static const int UNBOUND = 0;
static const int ATOM    = 1;
static const int REF     = 2;
/*------------------------------------------------------------------------------------------------*/
/*  THE TRAIL — the ONE shared spine (a binding-undo ledger, NOT a value stack).                   */
/*------------------------------------------------------------------------------------------------*/
static cell_t * g_trail[256];
static int      g_trail_top = 0;
static inline int  trail_mark(void)         { return g_trail_top; }
static inline void trail_unwind(int mark)   { while (g_trail_top > mark) { cell_t * c = g_trail[--g_trail_top]; c->tag = UNBOUND; c->ref = (cell_t *) 0; } }
static inline cell_t * deref(cell_t * c)    { while (c->tag == REF) c = c->ref; return c; }
static inline int  unify_atom(cell_t * c, long a) {
    c = deref(c);
    if (c->tag == ATOM) return c->atom == a;
    c->tag = ATOM; c->atom = a; g_trail[g_trail_top++] = c;
    return 1;
}
static inline int  unify(cell_t * l, cell_t * r) {
    l = deref(l); r = deref(r);
    if (l == r) return 1;
    if (l->tag == UNBOUND) { l->tag = REF; l->ref = r; g_trail[g_trail_top++] = l; return 1; }
    if (r->tag == UNBOUND) { r->tag = REF; r->ref = l; g_trail[g_trail_top++] = r; return 1; }
    return l->atom == r->atom;
}
/*------------------------------------------------------------------------------------------------*/
typedef struct _edge      edge_t;
typedef struct _path      path_t;
typedef struct _firstpath firstpath_t;
/*------------------------------------------------------------------------------------------------*/
/*  edge/2 — three ground facts = a 3-clause CHOICE.  Cursor (i) and trail-mark live in the        */
/*  box's OWN frame row; pre[i>0] unwinds to the entry mark (the bb_choice/test_sno_1 ALT shape).  */
/*------------------------------------------------------------------------------------------------*/
typedef struct _edge {
    int i;
    int mark;
} edge_t;
/*------------------------------------------------------------------------------------------------*/
int edge(edge_t ** ζζ, int entry, cell_t * a0, cell_t * a1) {
    edge_t * ζ = *ζζ;
    if (entry == α)     { ζ = ENTER(ζζ, sizeof(edge_t));             goto edge_α; }
    if (entry == β)     {                                            goto edge_β; }
    /*--------------------------------------------------------------------------------------------*/
    edge_α:             ζ->mark = trail_mark(); ζ->i = 1;            goto f1_α;
    edge_β:             if (ζ->i == 1)                               goto f1_ω;
                        if (ζ->i == 2)                               goto f2_ω;
                                                                     goto f3_ω;
    /*---------------- edge(a,b). ----------------------------------------------------------------*/
    f1_α:               if (!unify_atom(a0, 'a'))                    goto f1_ω;
                        if (!unify_atom(a1, 'b'))                    goto f1_ω;
                                                                     goto edge_γ;
    f1_ω:               ζ->i = 2; trail_unwind(ζ->mark);             goto f2_α;
    /*---------------- edge(b,c). ----------------------------------------------------------------*/
    f2_α:               if (!unify_atom(a0, 'b'))                    goto f2_ω;
                        if (!unify_atom(a1, 'c'))                    goto f2_ω;
                                                                     goto edge_γ;
    f2_ω:               ζ->i = 3; trail_unwind(ζ->mark);             goto f3_α;
    /*---------------- edge(b,d). ----------------------------------------------------------------*/
    f3_α:               if (!unify_atom(a0, 'b'))                    goto f3_ω;
                        if (!unify_atom(a1, 'd'))                    goto f3_ω;
                                                                     goto edge_γ;
    f3_ω:               trail_unwind(ζ->mark);                       goto edge_ω;
    /*--------------------------------------------------------------------------------------------*/
    edge_γ:             return 1;
    edge_ω:             return 0;
}
/*------------------------------------------------------------------------------------------------*/
/*  path/2 — two clauses = a 2-clause CHOICE; clause 2 is a CONJUNCTION with RECURSION.            */
/*  Head vars ARE the params (var-only heads need no head-unify boxes); clause-2's local Y is a    */
/*  frame cell; child activations are ζ-TREE pointer slots (e1, e2, p2), enter()-reset on each α.  */
/*------------------------------------------------------------------------------------------------*/
typedef struct _path {
    int       i;
    int       mark;
    cell_t    Y;
    edge_t  * e1_ζ;
    edge_t  * e2_ζ;
    path_t  * p2_ζ;
} path_t;
/*------------------------------------------------------------------------------------------------*/
int path(path_t ** ζζ, int entry, cell_t * a0, cell_t * a1) {
    int v;
    path_t * ζ = *ζζ;
    if (entry == α)     { ζ = ENTER(ζζ, sizeof(path_t));             goto path_α; }
    if (entry == β)     {                                            goto path_β; }
    /*--------------------------------------------------------------------------------------------*/
    path_α:             ζ->mark = trail_mark(); ζ->i = 1;            goto c1_α;
    path_β:             if (ζ->i == 1)                               goto c1_β;
                                                                     goto c2_β;
    /*---------------- clause 1:  path(X,Y) :- edge(X,Y). ----------------------------------------*/
    c1_α:               v = edge(&ζ->e1_ζ, α, a0, a1);               goto c1_λ;
    c1_β:               v = edge(&ζ->e1_ζ, β, a0, a1);               goto c1_λ;
    c1_λ:               if (v)                                       goto path_γ;
                        ζ->i = 2; trail_unwind(ζ->mark);             goto c2_α;
    /*---------------- clause 2:  path(X,Z) :- edge(X,Y), path(Y,Z). -----------------------------*/
    c2_α:               v = edge(&ζ->e2_ζ, α, a0, &ζ->Y);            goto c2e_λ;
    c2e_λ:              if (!v)                                      goto path_ω_;
                        v = path(&ζ->p2_ζ, α, &ζ->Y, a1);            goto c2p_λ;
    c2_β:               v = path(&ζ->p2_ζ, β, &ζ->Y, a1);            goto c2p_λ;
    c2p_λ:              if (v)                                       goto path_γ;
                        v = edge(&ζ->e2_ζ, β, a0, &ζ->Y);            goto c2e_λ;
    /*--------------------------------------------------------------------------------------------*/
    path_ω_:            trail_unwind(ζ->mark);                       goto path_ω;
    path_γ:             return 1;
    path_ω:             return 0;
}
/*------------------------------------------------------------------------------------------------*/
/*  firstpath/1 — firstpath(Q) :- path(a,Q), !.                                                    */
/*  CUT AS PURE WIRING: the barrier is lexical, so cut needs NO flag and NO gate — firstpath_β     */
/*  (the redo entry) is wired straight to ω and NEVER resumes path.  Bindings made before the cut  */
/*  survive (they unwind only when an ENCLOSING choice unwinds to its own mark).                   */
/*------------------------------------------------------------------------------------------------*/
typedef struct _firstpath {
    int       mark;
    cell_t    A;
    path_t  * p1_ζ;
} firstpath_t;
/*------------------------------------------------------------------------------------------------*/
int firstpath(firstpath_t ** ζζ, int entry, cell_t * a0) {
    int v;
    firstpath_t * ζ = *ζζ;
    if (entry == α)     { ζ = ENTER(ζζ, sizeof(firstpath_t));        goto firstpath_α; }
    if (entry == β)     {                                            goto firstpath_β; }
    /*--------------------------------------------------------------------------------------------*/
    firstpath_α:        ζ->mark = trail_mark();
                        ζ->A.tag = ATOM; ζ->A.atom = 'a';            goto b1_α;
    firstpath_β:                                                     goto firstpath_ω;
    /*---------------- body:  path(a,Q), ! -------------------------------------------------------*/
    b1_α:               v = path(&ζ->p1_ζ, α, &ζ->A, a0);            goto b1_λ;
    b1_λ:               if (v)                                       goto cut_α;
                        trail_unwind(ζ->mark);                       goto firstpath_ω;
    cut_α:                                                           goto firstpath_γ;
    /*--------------------------------------------------------------------------------------------*/
    firstpath_γ:        return 1;
    firstpath_ω:        return 0;
}
/*------------------------------------------------------------------------------------------------*/
__kernel void prolog(
    __global const char * in,
    __global       char * buffer,
             const int    num_chars) {
    /*--------------------------------------------------------------------------------------------*/
    const char cszFailure[9] = "Failure.";
    const char cszSuccess[10] = "Success: ";
    output_t output = {0, buffer};
    out = &output;
    for (int i = 0; i < num_chars; i++)
        buffer[i] = 0;
    int v;
    /*--------------------------------------------------------------------------------------------*/
    /*  ?- path(a,Q), write(Q), nl, fail.                                                          */
    /*  The fail-driver: write/nl succeed deterministically; fail's α IS its ω, which re-enters    */
    /*  path at β — the standard all-solutions pump.                                               */
    /*--------------------------------------------------------------------------------------------*/
    cell_t        A1;
    cell_t        Q1;
    path_t      * q1_ζ;
    q1_α:               q1_ζ = (path_t *) 0;
                        A1.tag = ATOM; A1.atom = 'a'; A1.ref = 0;
                        Q1.tag = UNBOUND; Q1.atom = 0; Q1.ref = 0;
                        v = path(&q1_ζ, α, &A1, &Q1);                goto q1_λ;
    q1_β:               v = path(&q1_ζ, β, &A1, &Q1);                goto q1_λ;
    q1_λ:               if (!v)                                      goto q1_ω;
                        write_atom(out, deref(&Q1)->atom);
                        write_nl(out);                               goto q1_β;
    q1_ω:                                                            goto q2_α;
    /*--------------------------------------------------------------------------------------------*/
    /*  ?- firstpath(Q), write(Q), nl.                                                             */
    /*--------------------------------------------------------------------------------------------*/
    cell_t        Q2;
    firstpath_t * q2_ζ;
    q2_α:               q2_ζ = (firstpath_t *) 0;
                        Q2.tag = UNBOUND; Q2.atom = 0; Q2.ref = 0;
                        v = firstpath(&q2_ζ, α, &Q2);                goto q2_λ;
    q2_λ:               if (!v)                                      goto q2_ω;
                        write_atom(out, deref(&Q2)->atom);
                        write_nl(out);                               goto main9;
    q2_ω:               write_sz(out, cszFailure);
                        write_nl(out);                               goto main9;
    /*--------------------------------------------------------------------------------------------*/
    main9:              write_flush(out);                            return;
}
/*------------------------------------------------------------------------------------------------*/
#ifdef __GNUC__
static char szOutput[1024] = {0};
int main() {
    prolog((const char *) 0, szOutput, sizeof(szOutput));
    return 0;
}
#endif
