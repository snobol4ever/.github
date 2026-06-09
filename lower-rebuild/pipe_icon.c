#include <stdio.h>
#include "ast.h"
#include "IR.h"
#include "icon_lex.h"
#include "icon_parse.h"
int g_jcon = 0;
extern IR_graph_t * lower_icon(const tree_t * prog);
int main(void) {
    const char * src = "procedure main()\n  write(\"hello\")\nend\n";
    IcnLexer lex; icn_lex_init(&lex, src);
    IcnParser p; icn_parse_init(&p, &lex);
    tree_t * ast = NULL;
    icn_parse_file(&p, &ast);
    if (!ast) { printf("PARSE FAILED\n"); return 1; }
    IR_graph_t * g = lower_icon(ast);
    printf("=== real parse -> lower_icon -> %d nodes, lang=%d ===\n", g->n, g->lang);
    bb_print(g, stdout);
    return 0;
}
