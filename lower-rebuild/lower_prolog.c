#include <string.h>
#include "ast.h"
#include "IR.h"
/*========================================================================================================================*/
typedef struct { IR_graph_t * g; } lcx_t;
/*--------------------------------------------------------------------------------------------------------------------*/
static const tree_t * stmt_subj(const tree_t * s) { for (int i = 0; i < s->n; i++) { const tree_t * a = s->c[i]; if (a && a->t == TT_ATTR && a->v.sval && !strcmp(a->v.sval, ":subj")) return (a->n > 0) ? a->c[0] : NULL; } return NULL; }
/*------------------------------------------------------------------------------------------------------------------------*/
static void γ_to(IR_t * nd, IR_t * t) { if (nd) { nd->γ.node = t; memcpy(nd->γ.sz, "α", 3); nd->γ.sz[3] = 0; } }
/*------------------------------------------------------------------------------------------------------------------------*/
static void ω_to(IR_t * nd, IR_t * t) { if (nd) { nd->ω.node = t; memcpy(nd->ω.sz, "α", 3); nd->ω.sz[3] = 0; } }
/*------------------------------------------------------------------------------------------------------------------------*/
static IR_t * build(lcx_t * cx, IR_e op, IR_t * γ, IR_t * ω) { IR_t * nd = IR_node_alloc(cx->g, op); γ_to(nd, γ); ω_to(nd, ω); return nd; }
/*------------------------------------------------------------------------------------------------------------------------*/
static IR_t * lower(lcx_t * cx, const tree_t * t, IR_t * γ, IR_t * ω);
static IR_t * lower_decl(lcx_t * cx, const tree_t * t);
static IR_t * lower_block(lcx_t * cx, const tree_t * t, IR_t * γ, IR_t * ω);
/*------------------------------------------------------------------------------------------------------------------------*/
static void push_kids(lcx_t * cx, IR_t * nd, const tree_t * t, int from) { for (int i = from; i < t->n; i++) ir_operand_push(nd, lower(cx, t->c[i], NULL, NULL)); }
/*------------------------------------------------------------------------------------------------------------------------*/
static IR_t * lower_nary(lcx_t * cx, const tree_t * t, IR_e op, IR_t * γ, IR_t * ω) { IR_t * nd = build(cx, op, γ, ω); push_kids(cx, nd, t, 0); return nd; }
/*------------------------------------------------------------------------------------------------------------------------*/
static IR_t * lower_binop(lcx_t * cx, const tree_t * t, const char * opn, IR_t * γ, IR_t * ω) { IR_t * nd = build(cx, IR_STRUCT, γ, ω); IR_LIT(nd).sval = opn; ir_operand_push(nd, lower(cx, t->c[0], NULL, NULL)); ir_operand_push(nd, lower(cx, t->c[1], NULL, NULL)); return nd; }
/*------------------------------------------------------------------------------------------------------------------------*/
static IR_t * lower_unop(lcx_t * cx, const tree_t * t, const char * opn, IR_t * γ, IR_t * ω) { IR_t * nd = build(cx, IR_STRUCT, γ, ω); IR_LIT(nd).sval = opn; ir_operand_push(nd, lower(cx, t->c[0], NULL, NULL)); return nd; }
/*========================================================================================================================*/
static IR_t * lower(lcx_t * cx, const tree_t * t, IR_t * γ, IR_t * ω) {
    if (!t) return build(cx, IR_SUCCEED, γ, ω);
    switch (t->t) {
    case TT_ILIT: { IR_t * nd = build(cx, IR_LIT_I, γ, ω); IR_LIT(nd).ival = t->v.ival; return nd; }
    case TT_FLIT: { IR_t * nd = build(cx, IR_LIT_F, γ, ω); IR_LIT(nd).dval = t->v.dval; return nd; }
    case TT_QLIT: { IR_t * nd = build(cx, IR_ATOM, γ, ω); IR_LIT(nd).sval = t->v.sval; return nd; }
    case TT_NUL: return build(cx, IR_LIT_NUL, γ, ω);
    case TT_VAR: { IR_t * nd = build(cx, IR_LOGICVAR, γ, ω); IR_LIT(nd).sval = t->v.sval; return nd; }
    case TT_KEYWORD: { IR_t * nd = build(cx, IR_KEYWORD, γ, ω); IR_LIT(nd).sval = t->v.sval; return nd; }
    case TT_ADD: return lower_binop(cx, t, "+", γ, ω);
    case TT_SUB: return lower_binop(cx, t, "-", γ, ω);
    case TT_MUL: return lower_binop(cx, t, "*", γ, ω);
    case TT_DIV: return lower_binop(cx, t, "/", γ, ω);
    case TT_CSET: { IR_t * nd = build(cx, IR_LIT_S, γ, ω); IR_LIT(nd).sval = t->v.sval; return nd; }
    case TT_FNC: { IR_t * nd = build(cx, IR_STRUCT, γ, ω); IR_LIT(nd).sval = (t->n > 0 && t->c[0]) ? t->c[0]->v.sval : t->v.sval; push_kids(cx, nd, t, 1); return nd; }
    case TT_IDX: return lower_nary(cx, t, IR_IDX, γ, ω);
    case TT_MAKELIST: return lower_nary(cx, t, IR_STRUCT, γ, ω);
    case TT_UNIFY: return lower_nary(cx, t, IR_UNIFY, γ, ω);
    case TT_CLAUSE: return lower_nary(cx, t, IR_GOAL, γ, ω);
    case TT_CHOICE: return lower_nary(cx, t, IR_DISJ, γ, ω);
    case TT_CUT: return build(cx, IR_CUT, γ, ω);
    case TT_IF: return lower_nary(cx, t, IR_ITE, γ, ω);
    case TT_ATTR: return build(cx, IR_SUCCEED, γ, ω);
    case TT_SEQ: return lower_block(cx, t, γ, ω);
    case TT_PROGRAM: return lower_block(cx, t, γ, ω);
    case TT_STMT: { const tree_t * sub = stmt_subj(t); return sub ? lower(cx, sub, γ, ω) : build(cx, IR_SUCCEED, γ, ω); }
    default: return build(cx, IR_SUCCEED, γ, ω);
    }
}
/*========================================================================================================================*/
static IR_t * lower_block(lcx_t * cx, const tree_t * t, IR_t * γ, IR_t * ω) {
    IR_t * head = NULL; IR_t * prev = NULL;
    for (int i = 0; i < t->n; i++) {
        const tree_t * s = t->c[i];
        if (s->t == TT_STMT) { const tree_t * sub = stmt_subj(s); if (!sub) continue; s = sub; }
        IR_t * nd = lower(cx, s, NULL, ω);
        if (!head) head = nd;
        if (prev) γ_to(prev, nd);
        prev = nd;
    }
    if (prev) γ_to(prev, γ);
    if (!head) head = build(cx, IR_SUCCEED, γ, ω);
    return head;
}
/*========================================================================================================================*/
static IR_t * lower_decl(lcx_t * cx, const tree_t * t) {
    switch (t->t) {
    case TT_CLAUSE: return lower_nary(cx, t, IR_GOAL, NULL, NULL);
    default: return lower(cx, t, NULL, NULL);
    }
}
/*========================================================================================================================*/
IR_graph_t * lower_prolog(const tree_t * prog) {
    IR_graph_t * g = IR_alloc(8192, IR_LANG_PL);
    lcx_t cx; cx.g = g;
    IR_t * top = IR_node_alloc(g, IR_PROG);
    for (int i = 0; i < prog->n; i++) {
        const tree_t * d = prog->c[i];
        if (d->t == TT_STMT) { const tree_t * sub = stmt_subj(d); if (!sub) continue; d = sub; }
        ir_operand_push(top, lower_decl(&cx, d));
    }
    g->entry = top;
    return g;
}
