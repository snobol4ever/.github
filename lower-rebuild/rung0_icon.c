#include <stdio.h>
#include "ast.h"
#include "IR.h"
extern IR_graph_t * lower_icon(const tree_t * prog);
static tree_t * leaf_s(tree_e k, const char * s) { tree_t * n = ast_node_new(k); n->v.sval = (char *)s; return n; }
static tree_t * stmt1(tree_t * e) { tree_t * s = ast_node_new(TT_STMT); ast_push(s, e); return s; }
int main(void) {
    tree_t * call = ast_node_new(TT_FNC);
    ast_push(call, leaf_s(TT_VAR, "write"));
    ast_push(call, leaf_s(TT_QLIT, "hello"));
    tree_t * body = ast_node_new(TT_PROGRAM);
    ast_push(body, stmt1(call));
    tree_t * proc = ast_node_new(TT_PROC_DECL); proc->v.sval = (char *)"main";
    ast_push(proc, leaf_s(TT_VAR, "main"));
    ast_push(proc, ast_node_new(TT_VLIST));
    ast_push(proc, body);
    tree_t * prog = ast_node_new(TT_PROGRAM);
    ast_push(prog, stmt1(proc));
    IR_graph_t * g = lower_icon(prog);
    printf("=== lower_icon(hello) -> %d nodes, lang=%d ===\n", g->n, g->lang);
    bb_print(g, stdout);
    return 0;
}
