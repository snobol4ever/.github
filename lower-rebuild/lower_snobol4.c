#include <string.h>
#include "ast.h"
#include "IR.h"
/*========================================================================================================================*/
typedef struct { IR_graph_t * g; } scx_t;
/*--------------------------------------------------------------------------------------------------------------------*/
static const tree_t * stmt_subj(const tree_t * s) { for (int i = 0; i < s->n; i++) { const tree_t * a = s->c[i]; if (a && a->t == TT_ATTR && a->v.sval && !strcmp(a->v.sval, ":subj")) return (a->n > 0) ? a->c[0] : NULL; } return NULL; }
/*------------------------------------------------------------------------------------------------------------------------*/
static void γ_to(IR_t * nd, IR_t * t) { if (nd) { nd->γ.node = t; memcpy(nd->γ.sz, "α", 3); nd->γ.sz[3] = 0; } }
/*------------------------------------------------------------------------------------------------------------------------*/
static void ω_to(IR_t * nd, IR_t * t) { if (nd) { nd->ω.node = t; memcpy(nd->ω.sz, "α", 3); nd->ω.sz[3] = 0; } }
/*------------------------------------------------------------------------------------------------------------------------*/
static IR_t * emit(scx_t * cx, IR_e op, IR_t * γ, IR_t * ω) { IR_t * nd = IR_node_alloc(cx->g, op); γ_to(nd, γ); ω_to(nd, ω); return nd; }
/*------------------------------------------------------------------------------------------------------------------------*/
static IR_t * lower(scx_t * cx, const tree_t * t, IR_t * γ, IR_t * ω);
static IR_t * lower_decl(scx_t * cx, const tree_t * t);
static IR_t * lower_block(scx_t * cx, const tree_t * t, IR_t * γ, IR_t * ω);
/*------------------------------------------------------------------------------------------------------------------------*/
static void push_kids(scx_t * cx, IR_t * nd, const tree_t * t, int from) { for (int i = from; i < t->n; i++) ir_operand_push(nd, lower(cx, t->c[i], NULL, NULL)); }
/*------------------------------------------------------------------------------------------------------------------------*/
static IR_t * lower_nary(scx_t * cx, const tree_t * t, IR_e op, IR_t * γ, IR_t * ω) { IR_t * nd = emit(cx, op, γ, ω); push_kids(cx, nd, t, 0); return nd; }
/*------------------------------------------------------------------------------------------------------------------------*/
static IR_t * lower_binop(scx_t * cx, const tree_t * t, const char * opn, IR_t * γ, IR_t * ω) { IR_t * nd = emit(cx, IR_BINOP, γ, ω); IR_LIT(nd).sval = opn; ir_operand_push(nd, lower(cx, t->c[0], NULL, NULL)); ir_operand_push(nd, lower(cx, t->c[1], NULL, NULL)); return nd; }
/*------------------------------------------------------------------------------------------------------------------------*/
static IR_t * lower_unop(scx_t * cx, const tree_t * t, const char * opn, IR_t * γ, IR_t * ω) { IR_t * nd = emit(cx, IR_UNOP, γ, ω); IR_LIT(nd).sval = opn; ir_operand_push(nd, lower(cx, t->c[0], NULL, NULL)); return nd; }
/*========================================================================================================================*/
static IR_t * lower(scx_t * cx, const tree_t * t, IR_t * γ, IR_t * ω) {
    if (!t) return emit(cx, IR_SUCCEED, γ, ω);
    switch (t->t) {
    case TT_ILIT: { IR_t * nd = emit(cx, IR_LIT_I, γ, ω); IR_LIT(nd).ival = t->v.ival; return nd; }
    case TT_FLIT: { IR_t * nd = emit(cx, IR_LIT_F, γ, ω); IR_LIT(nd).dval = t->v.dval; return nd; }
    case TT_QLIT: { IR_t * nd = emit(cx, IR_LIT_S, γ, ω); IR_LIT(nd).sval = t->v.sval; return nd; }
    case TT_NUL: return emit(cx, IR_LIT_NUL, γ, ω);
    case TT_VAR: { IR_t * nd = emit(cx, IR_VAR, γ, ω); IR_LIT(nd).sval = t->v.sval; return nd; }
    case TT_NAME: return lower_unop(cx, t, ".", γ, ω);
    case TT_KEYWORD: { IR_t * nd = emit(cx, IR_KEYWORD, γ, ω); IR_LIT(nd).sval = t->v.sval; return nd; }
    case TT_INDIRECT: return lower_unop(cx, t, "$", γ, ω);
    case TT_ADD: return lower_binop(cx, t, "+", γ, ω);
    case TT_SUB: return lower_binop(cx, t, "-", γ, ω);
    case TT_MUL: return lower_binop(cx, t, "*", γ, ω);
    case TT_DIV: return lower_binop(cx, t, "/", γ, ω);
    case TT_MOD: return lower_binop(cx, t, "%", γ, ω);
    case TT_POW: return lower_binop(cx, t, "^", γ, ω);
    case TT_PLS: return lower_unop(cx, t, "+", γ, ω);
    case TT_MNS: return lower_unop(cx, t, "-", γ, ω);
    case TT_LT: return lower_binop(cx, t, "<", γ, ω);
    case TT_LE: return lower_binop(cx, t, "<=", γ, ω);
    case TT_GT: return lower_binop(cx, t, ">", γ, ω);
    case TT_GE: return lower_binop(cx, t, ">=", γ, ω);
    case TT_EQ: return lower_binop(cx, t, "=", γ, ω);
    case TT_NE: return lower_binop(cx, t, "~=", γ, ω);
    case TT_LLT: return lower_binop(cx, t, "<<", γ, ω);
    case TT_LLE: return lower_binop(cx, t, "<<=", γ, ω);
    case TT_LGT: return lower_binop(cx, t, ">>", γ, ω);
    case TT_LGE: return lower_binop(cx, t, ">>=", γ, ω);
    case TT_LEQ: return lower_binop(cx, t, "==", γ, ω);
    case TT_LNE: return lower_binop(cx, t, "~==", γ, ω);
    case TT_NOT: return lower_unop(cx, t, "not", γ, ω);
    case TT_NONNULL: return lower_unop(cx, t, "\\", γ, ω);
    case TT_INTERROGATE: return lower_unop(cx, t, "?", γ, ω);
    case TT_CAT: return lower_binop(cx, t, "||", γ, ω);
    case TT_FNC: return lower_nary(cx, t, IR_CALL, γ, ω);
    case TT_IDX: return lower_nary(cx, t, IR_IDX, γ, ω);
    case TT_ARB: return emit(cx, IR_PATTERN_ARB, γ, ω);
    case TT_ARBNO: return lower_nary(cx, t, IR_PATTERN_ARBNO, γ, ω);
    case TT_ANY: return lower_nary(cx, t, IR_PATTERN_ANY, γ, ω);
    case TT_NOTANY: return lower_nary(cx, t, IR_PATTERN_NOTANY, γ, ω);
    case TT_SPAN: return lower_nary(cx, t, IR_PATTERN_SPAN, γ, ω);
    case TT_BREAK: return lower_nary(cx, t, IR_PATTERN_BREAK, γ, ω);
    case TT_BREAKX: return lower_nary(cx, t, IR_PATTERN_BREAKX, γ, ω);
    case TT_LEN: return lower_nary(cx, t, IR_PATTERN_LEN, γ, ω);
    case TT_TAB: return lower_nary(cx, t, IR_PATTERN_TAB, γ, ω);
    case TT_RTAB: return lower_nary(cx, t, IR_PATTERN_RTAB, γ, ω);
    case TT_REM: return emit(cx, IR_PATTERN_REM, γ, ω);
    case TT_POS: return lower_nary(cx, t, IR_PATTERN_POS, γ, ω);
    case TT_RPOS: return lower_nary(cx, t, IR_PATTERN_RPOS, γ, ω);
    case TT_BAL: return emit(cx, IR_PATTERN_BAL, γ, ω);
    case TT_FENCE: return emit(cx, IR_PATTERN_FENCE, γ, ω);
    case TT_ABORT: return emit(cx, IR_PATTERN_ABORT, γ, ω);
    case TT_FAIL: return emit(cx, IR_PATTERN_FAIL, γ, ω);
    case TT_SUCCEED: return emit(cx, IR_PATTERN_SUCCEED, γ, ω);
    case TT_ALT: return lower_nary(cx, t, IR_PATTERN_ALT, γ, ω);
    case TT_DEFER: return lower_nary(cx, t, IR_PATTERN_DEFER, γ, ω);
    case TT_CAPT_COND_ASGN: { IR_t * nd = lower_nary(cx, t, IR_PATTERN_CAPTURE, γ, ω); IR_LIT(nd).ival = 0; return nd; }
    case TT_CAPT_IMMED_ASGN: { IR_t * nd = lower_nary(cx, t, IR_PATTERN_CAPTURE, γ, ω); IR_LIT(nd).ival = 1; return nd; }
    case TT_CAPT_CURSOR: { IR_t * nd = lower_nary(cx, t, IR_PATTERN_CAPTURE, γ, ω); IR_LIT(nd).ival = 2; return nd; }
    case TT_SCAN: return lower_nary(cx, t, IR_SCAN, γ, ω);
    case TT_OPSYN: return emit(cx, IR_SUCCEED, γ, ω);
    case TT_ASSIGN: return lower_nary(cx, t, IR_ASSIGN, γ, ω);
    case TT_AUGOP: { IR_t * nd = lower_nary(cx, t, IR_AUGOP, γ, ω); IR_LIT(nd).ival = t->v.ival; return nd; }
    case TT_SWAP: return lower_nary(cx, t, IR_SWAP, γ, ω);
    case TT_ITERATE: return lower_nary(cx, t, IR_ITERATE, γ, ω);
    case TT_IF: return lower_nary(cx, t, IR_IF, γ, ω);
    case TT_UNLESS: return lower_nary(cx, t, IR_IF, γ, ω);
    case TT_WHILE: return lower_nary(cx, t, IR_WHILE, γ, ω);
    case TT_UNTIL: return lower_nary(cx, t, IR_UNTIL, γ, ω);
    case TT_REPEAT: return lower_nary(cx, t, IR_REPEAT, γ, ω);
    case TT_DO_WHILE: return lower_nary(cx, t, IR_DO_WHILE, γ, ω);
    case TT_FOR: return lower_nary(cx, t, IR_TO_BY, γ, ω);
    case TT_CASE: return lower_nary(cx, t, IR_CASE, γ, ω);
    case TT_RETURN: return lower_nary(cx, t, IR_RETURN, γ, ω);
    case TT_NRETURN: { IR_t * nd = lower_nary(cx, t, IR_RETURN, γ, ω); IR_LIT(nd).ival = 1; return nd; }
    case TT_PROC_FAIL: return emit(cx, IR_FAIL, γ, ω);
    case TT_LOOP_BREAK: return emit(cx, IR_BREAK, γ, ω);
    case TT_LOOP_NEXT: return emit(cx, IR_NEXT, γ, ω);
    case TT_GOTO_S: { IR_t * nd = emit(cx, IR_GOTO, γ, ω); IR_LIT(nd).sval = t->v.sval; IR_LIT(nd).ival = 0; return nd; }
    case TT_GOTO_F: { IR_t * nd = emit(cx, IR_GOTO, γ, ω); IR_LIT(nd).sval = t->v.sval; IR_LIT(nd).ival = 1; return nd; }
    case TT_GOTO_U: { IR_t * nd = emit(cx, IR_GOTO, γ, ω); IR_LIT(nd).sval = t->v.sval; IR_LIT(nd).ival = 2; return nd; }
    case TT_LABEL_DEF: { IR_t * nd = emit(cx, IR_SUCCEED, γ, ω); IR_LIT(nd).sval = t->v.sval; return nd; }
    case TT_VLIST: return lower_nary(cx, t, IR_LIST_BANG, γ, ω);
    case TT_SEQ: return lower_block(cx, t, γ, ω);
    case TT_PROGRAM: return lower_block(cx, t, γ, ω);
    case TT_STMT: { const tree_t * sub = stmt_subj(t); return sub ? lower(cx, sub, γ, ω) : emit(cx, IR_SUCCEED, γ, ω); }
    case TT_DEFINE: return lower_decl(cx, t);
    case TT_FUNCTION: return lower_decl(cx, t);
    case TT_RECORD_DECL: return lower_decl(cx, t);
    case TT_END: return emit(cx, IR_SUCCEED, γ, ω);
    default: return emit(cx, IR_SUCCEED, γ, ω);
    }
}
/*========================================================================================================================*/
static IR_t * lower_block(scx_t * cx, const tree_t * t, IR_t * γ, IR_t * ω) {
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
static IR_t * lower_decl(scx_t * cx, const tree_t * t) {
    switch (t->t) {
    case TT_DEFINE: { IR_t * nd = IR_node_alloc(cx->g, IR_PROC); IR_LIT(nd).sval = t->v.sval; IR_t * body = (t->n > 2) ? lower_block(cx, t->c[2], NULL, NULL) : emit(cx, IR_SUCCEED, NULL, NULL); ir_operand_push(nd, body); return nd; }
    case TT_FUNCTION: { IR_t * nd = IR_node_alloc(cx->g, IR_PROC); IR_LIT(nd).sval = t->v.sval; IR_t * body = (t->n > 2) ? lower_block(cx, t->c[2], NULL, NULL) : emit(cx, IR_SUCCEED, NULL, NULL); ir_operand_push(nd, body); return nd; }
    case TT_RECORD_DECL: { IR_t * nd = IR_node_alloc(cx->g, IR_RECORD_DEF); IR_LIT(nd).sval = t->v.sval; push_kids(cx, nd, t, 0); return nd; }
    default: return lower(cx, t, NULL, NULL);
    }
}
/*========================================================================================================================*/
IR_graph_t * lower_snobol4(const tree_t * prog) {
    IR_graph_t * g = IR_alloc(8192, IR_LANG_SNO);
    scx_t cx; cx.g = g;
    IR_t * top = IR_node_alloc(g, IR_PROG);
    for (int i = 0; i < prog->n; i++) {
        const tree_t * d = prog->c[i];
        if (d->t == TT_STMT) { const tree_t * sub = stmt_subj(d); if (!sub) continue; d = sub; }
        ir_operand_push(top, lower_decl(&cx, d));
    }
    g->entry = top;
    return g;
}
