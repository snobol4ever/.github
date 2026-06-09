#include <string.h>
#include "ast.h"
#include "IR.h"
/*========================================================================================================================*/
typedef struct { IR_graph_t * g; } rcx_t;
/*--------------------------------------------------------------------------------------------------------------------*/
static const tree_t * stmt_subj(const tree_t * s) { for (int i = 0; i < s->n; i++) { const tree_t * a = s->c[i]; if (a && a->t == TT_ATTR && a->v.sval && !strcmp(a->v.sval, ":subj")) return (a->n > 0) ? a->c[0] : NULL; } return NULL; }
/*------------------------------------------------------------------------------------------------------------------------*/
static void γ_to(IR_t * nd, IR_t * t) { if (nd) { nd->γ.node = t; memcpy(nd->γ.sz, "α", 3); nd->γ.sz[3] = 0; } }
/*------------------------------------------------------------------------------------------------------------------------*/
static void ω_to(IR_t * nd, IR_t * t) { if (nd) { nd->ω.node = t; memcpy(nd->ω.sz, "α", 3); nd->ω.sz[3] = 0; } }
/*------------------------------------------------------------------------------------------------------------------------*/
static IR_t * emit(rcx_t * cx, IR_e op, IR_t * γ, IR_t * ω) { IR_t * nd = IR_node_alloc(cx->g, op); γ_to(nd, γ); ω_to(nd, ω); return nd; }
/*------------------------------------------------------------------------------------------------------------------------*/
static IR_t * lower(rcx_t * cx, const tree_t * t, IR_t * γ, IR_t * ω);
static IR_t * lower_decl(rcx_t * cx, const tree_t * t);
static IR_t * lower_block(rcx_t * cx, const tree_t * t, IR_t * γ, IR_t * ω);
/*------------------------------------------------------------------------------------------------------------------------*/
static void push_kids(rcx_t * cx, IR_t * nd, const tree_t * t, int from) { for (int i = from; i < t->n; i++) ir_operand_push(nd, lower(cx, t->c[i], NULL, NULL)); }
/*------------------------------------------------------------------------------------------------------------------------*/
static IR_t * lower_nary(rcx_t * cx, const tree_t * t, IR_e op, IR_t * γ, IR_t * ω) { IR_t * nd = emit(cx, op, γ, ω); push_kids(cx, nd, t, 0); return nd; }
/*------------------------------------------------------------------------------------------------------------------------*/
static IR_t * lower_binop(rcx_t * cx, const tree_t * t, const char * opn, IR_t * γ, IR_t * ω) { IR_t * nd = emit(cx, IR_BINOP, γ, ω); IR_LIT(nd).sval = opn; ir_operand_push(nd, lower(cx, t->c[0], NULL, NULL)); ir_operand_push(nd, lower(cx, t->c[1], NULL, NULL)); return nd; }
/*------------------------------------------------------------------------------------------------------------------------*/
static IR_t * lower_unop(rcx_t * cx, const tree_t * t, const char * opn, IR_t * γ, IR_t * ω) { IR_t * nd = emit(cx, IR_UNOP, γ, ω); IR_LIT(nd).sval = opn; ir_operand_push(nd, lower(cx, t->c[0], NULL, NULL)); return nd; }
/*========================================================================================================================*/
static IR_t * lower(rcx_t * cx, const tree_t * t, IR_t * γ, IR_t * ω) {
    if (!t) return emit(cx, IR_SUCCEED, γ, ω);
    switch (t->t) {
    case TT_ILIT: { IR_t * nd = emit(cx, IR_LIT_I, γ, ω); IR_LIT(nd).ival = t->v.ival; return nd; }
    case TT_FLIT: { IR_t * nd = emit(cx, IR_LIT_F, γ, ω); IR_LIT(nd).dval = t->v.dval; return nd; }
    case TT_QLIT: { IR_t * nd = emit(cx, IR_LIT_S, γ, ω); IR_LIT(nd).sval = t->v.sval; return nd; }
    case TT_NUL: return emit(cx, IR_LIT_NUL, γ, ω);
    case TT_VAR: { IR_t * nd = emit(cx, IR_VAR, γ, ω); IR_LIT(nd).sval = t->v.sval; return nd; }
    case TT_FIELD: { IR_t * nd = emit(cx, IR_FIELD_GET, γ, ω); IR_LIT(nd).sval = (t->n > 1 && t->c[1]) ? t->c[1]->v.sval : t->v.sval; ir_operand_push(nd, lower(cx, t->c[0], NULL, NULL)); return nd; }
    case TT_TWIGIL_FIELD: { IR_t * nd = emit(cx, IR_FIELD_GET, γ, ω); IR_LIT(nd).sval = t->v.sval; return nd; }
    case TT_ADD: return lower_binop(cx, t, "+", γ, ω);
    case TT_SUB: return lower_binop(cx, t, "-", γ, ω);
    case TT_MUL: return lower_binop(cx, t, "*", γ, ω);
    case TT_DIV: return lower_binop(cx, t, "/", γ, ω);
    case TT_MOD: return lower_binop(cx, t, "%", γ, ω);
    case TT_MNS: return lower_unop(cx, t, "-", γ, ω);
    case TT_LT: return lower_binop(cx, t, "<", γ, ω);
    case TT_LE: return lower_binop(cx, t, "<=", γ, ω);
    case TT_GT: return lower_binop(cx, t, ">", γ, ω);
    case TT_GE: return lower_binop(cx, t, ">=", γ, ω);
    case TT_EQ: return lower_binop(cx, t, "==", γ, ω);
    case TT_NE: return lower_binop(cx, t, "!=", γ, ω);
    case TT_LEQ: return lower_binop(cx, t, "eq", γ, ω);
    case TT_LNE: return lower_binop(cx, t, "ne", γ, ω);
    case TT_NOT: return lower_unop(cx, t, "not", γ, ω);
    case TT_CAT: return lower_binop(cx, t, "~", γ, ω);
    case TT_FNC: return lower_nary(cx, t, IR_CALL, γ, ω);
    case TT_ARR_GET: return lower_nary(cx, t, IR_IDX, γ, ω);
    case TT_ARR_SET: return lower_nary(cx, t, IR_IDX_SET, γ, ω);
    case TT_HASH_GET: return lower_nary(cx, t, IR_IDX, γ, ω);
    case TT_HASH_SET: return lower_nary(cx, t, IR_IDX_SET, γ, ω);
    case TT_HASH_EXISTS: { IR_t * nd = lower_nary(cx, t, IR_CALL, γ, ω); IR_LIT(nd).sval = "exists"; return nd; }
    case TT_HASH_DELETE: { IR_t * nd = lower_nary(cx, t, IR_CALL, γ, ω); IR_LIT(nd).sval = "delete"; return nd; }
    case TT_METHCALL: { IR_t * nd = lower_nary(cx, t, IR_CALL, γ, ω); IR_LIT(nd).sval = t->v.sval; return nd; }
    case TT_NEW: { IR_t * nd = lower_nary(cx, t, IR_CALL, γ, ω); IR_LIT(nd).sval = "new"; return nd; }
    case TT_ASSIGN: return lower_nary(cx, t, IR_ASSIGN, γ, ω);
    case TT_TO: return lower_nary(cx, t, IR_TO, γ, ω);
    case TT_ITERATE: return lower_nary(cx, t, IR_ITERATE, γ, ω);
    case TT_EVERY: return lower_nary(cx, t, IR_EVERY, γ, ω);
    case TT_MAP: return lower_nary(cx, t, IR_MAP, γ, ω);
    case TT_GREP: return lower_nary(cx, t, IR_GREP, γ, ω);
    case TT_SORT: { IR_t * nd = lower_nary(cx, t, IR_CALL, γ, ω); IR_LIT(nd).sval = "sort"; return nd; }
    case TT_GATHER: return lower_nary(cx, t, IR_GATHER, γ, ω);
    case TT_ALT: return lower_nary(cx, t, IR_ALT, γ, ω);
    case TT_SEQ_EXPR: return lower_nary(cx, t, IR_SEQ_EXPR, γ, ω);
    case TT_SAY: { IR_t * nd = lower_nary(cx, t, IR_CALL, γ, ω); IR_LIT(nd).sval = "say"; return nd; }
    case TT_SAY_FH: { IR_t * nd = lower_nary(cx, t, IR_CALL, γ, ω); IR_LIT(nd).sval = "say"; return nd; }
    case TT_PRINT: { IR_t * nd = lower_nary(cx, t, IR_CALL, γ, ω); IR_LIT(nd).sval = "print"; return nd; }
    case TT_PRINT_FH: { IR_t * nd = lower_nary(cx, t, IR_CALL, γ, ω); IR_LIT(nd).sval = "print"; return nd; }
    case TT_IF: return lower_nary(cx, t, IR_IF, γ, ω);
    case TT_UNLESS: return lower_nary(cx, t, IR_IF, γ, ω);
    case TT_WHILE: return lower_nary(cx, t, IR_WHILE, γ, ω);
    case TT_UNTIL: return lower_nary(cx, t, IR_UNTIL, γ, ω);
    case TT_REPEAT: return lower_nary(cx, t, IR_REPEAT, γ, ω);
    case TT_FOR_RANGE: return lower_nary(cx, t, IR_EVERY, γ, ω);
    case TT_CASE: return lower_nary(cx, t, IR_CASE, γ, ω);
    case TT_SUSPEND: return lower_nary(cx, t, IR_SUSPEND, γ, ω);
    case TT_RETURN: return lower_nary(cx, t, IR_RETURN, γ, ω);
    case TT_TRY: return lower_nary(cx, t, IR_CATCH, γ, ω);
    case TT_DIE: { IR_t * nd = lower_nary(cx, t, IR_CALL, γ, ω); IR_LIT(nd).sval = "die"; return nd; }
    case TT_SMATCH: return lower_nary(cx, t, IR_PAT_MATCH, γ, ω);
    case TT_CAPTURE: return lower_nary(cx, t, IR_PATTERN_CAPTURE, γ, ω);
    case TT_NAMED_CAPTURE: return lower_nary(cx, t, IR_PATTERN_CAPTURE, γ, ω);
    case TT_FH_CAPTURE: return lower_nary(cx, t, IR_PATTERN_CAPTURE, γ, ω);
    case TT_REGEX_DECL: { IR_t * nd = emit(cx, IR_SUCCEED, γ, ω); IR_LIT(nd).sval = t->v.sval; return nd; }
    case TT_GRAMMAR_DECL: { IR_t * nd = emit(cx, IR_SUCCEED, γ, ω); IR_LIT(nd).sval = t->v.sval; return nd; }
    case TT_DECL: return emit(cx, IR_SUCCEED, γ, ω);
    case TT_SEQ: return lower_block(cx, t, γ, ω);
    case TT_PROGRAM: return lower_block(cx, t, γ, ω);
    case TT_STMT: { const tree_t * sub = stmt_subj(t); return sub ? lower(cx, sub, γ, ω) : emit(cx, IR_SUCCEED, γ, ω); }
    case TT_SUB_DECL: return lower_decl(cx, t);
    case TT_CLASS_DECL: return lower_decl(cx, t);
    default: return emit(cx, IR_SUCCEED, γ, ω);
    }
}
/*========================================================================================================================*/
static IR_t * lower_block(rcx_t * cx, const tree_t * t, IR_t * γ, IR_t * ω) {
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
    if (!head) head = emit(cx, IR_SUCCEED, γ, ω);
    return head;
}
/*========================================================================================================================*/
static IR_t * lower_decl(rcx_t * cx, const tree_t * t) {
    switch (t->t) {
    case TT_SUB_DECL: { IR_t * nd = IR_node_alloc(cx->g, IR_PROC); IR_LIT(nd).sval = t->v.sval; IR_t * body = (t->n > 2) ? lower_block(cx, t->c[2], NULL, NULL) : emit(cx, IR_SUCCEED, NULL, NULL); ir_operand_push(nd, body); return nd; }
    case TT_CLASS_DECL: { IR_t * nd = IR_node_alloc(cx->g, IR_RECORD_DEF); IR_LIT(nd).sval = t->v.sval; push_kids(cx, nd, t, 0); return nd; }
    default: return lower(cx, t, NULL, NULL);
    }
}
/*========================================================================================================================*/
IR_graph_t * lower_raku(const tree_t * prog) {
    IR_graph_t * g = IR_alloc(8192, IR_LANG_RKU);
    rcx_t cx; cx.g = g;
    IR_t * top = IR_node_alloc(g, IR_PROG);
    for (int i = 0; i < prog->n; i++) {
        const tree_t * d = prog->c[i];
        if (d->t == TT_STMT) { const tree_t * sub = stmt_subj(d); if (!sub) continue; d = sub; }
        ir_operand_push(top, lower_decl(&cx, d));
    }
    g->entry = top;
    return g;
}
