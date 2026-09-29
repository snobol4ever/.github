import sys; p = sys.argv[1] + '/src/lower/lower_snobol4.c'
s = open(p, encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:80], s.count(a)); s = s.replace(a, b)
helpers = '''static long g_patdiag_line; static int g_patdiag_depth;
static int patdiag_on(void) { static int v = -1; if (v < 0) { const char * e = getenv("SCRIP_PATDIAG"); v = (e && *e == '1') ? 1 : 0; } return v; }
static void patdiag_set_line(const tree_t * s) { long l = s ? (long) lp_s_int(s, ":line") : 0; if (!l && s) l = (long) lp_s_int(s, ":lline"); if (l) g_patdiag_line = l; }
extern void ir_dump_tree(const tree_t * e, FILE * f);
static void patdiag_emit(const char * route, const char * why, const tree_t * t) {
    char * buf = 0; size_t sz = 0; FILE * m = open_memstream(&buf, &sz); if (!m) return; ir_dump_tree(t, m); fclose(m);
    char one[200]; int o = 0; int sp = 0;
    for (size_t k = 0; buf && k < sz && o < 180; k++) { char c = buf[k]; if (c == '\\n' || c == ' ' || c == '\\t') { if (!sp && o) { one[o++] = ' '; sp = 1; } continue; } one[o++] = c; sp = 0; }
    one[o] = 0; free(buf);
    fprintf(stderr, "[PATDIAG] line=%ld route=%s depth=%d decision=%s tree=%s\\n", g_patdiag_line, route, g_patdiag_depth, why, one);
}
'''
anchor = 'static IR_t * sx_lower(scx_t * cx, const tree_t * t, IR_t * γ, IR_t * ω, IR_t ** res) {\n    if (!t) {'
rep(anchor, helpers + 'static IR_t * sx_lower_body(scx_t * cx, const tree_t * t, IR_t * γ, IR_t * ω, IR_t ** res);\n'
    'static int sno_null_lit(const tree_t * t);\n'
    'static int sno_is_pattern_rhs(const tree_t * t);\n'
    'static IR_t * sx_lower(scx_t * cx, const tree_t * t, IR_t * γ, IR_t * ω, IR_t ** res) {\n'
    '    if (patdiag_on() && t && t->t != TT_VAR && t->t != TT_KEYWORD && t->t != TT_INDIRECT && t->t != TT_DEFER && sno_is_pattern_rhs(t)) {\n'
    '        int pre = sno_mkpat_here(t);\n'
    '        const char * why = pre ? "PRE" : !sno_pat_supported(t) ? "UNSUPPORTED" : ((t->t == TT_SEQ || t->t == TT_CAT) && t->n > 1 && (sno_null_lit(t->c[0]) || sno_null_lit(t->c[1]))) ? "NULLCAT" : "VARIANT";\n'
    '        patdiag_emit("value", why, t);\n'
    '        if (!pre) { g_patdiag_depth++; IR_t * r = sx_lower_body(cx, t, γ, ω, res); g_patdiag_depth--; return r; }\n'
    '    }\n'
    '    return sx_lower_body(cx, t, γ, ω, res);\n'
    '}\n'
    'static IR_t * sx_lower_body(scx_t * cx, const tree_t * t, IR_t * γ, IR_t * ω, IR_t ** res) {\n    if (!t) {')
rep('        const tree_t * s = pg->c[i];\n', '        const tree_t * s = pg->c[i]; patdiag_set_line(s);\n')
rep('        const tree_t * s = st[i]; if (!s) continue;\n', '        const tree_t * s = st[i]; if (!s) continue; patdiag_set_line(s);\n')
rep('        const tree_t * s = st[i];\n', '        const tree_t * s = st[i]; patdiag_set_line(s);\n')
rep('        if (subj->t == TT_VAR && sno_is_pattern_rhs(repl) && sno_pat_supported(repl)) {\n',
    '        if (patdiag_on() && subj->t == TT_VAR && sno_is_pattern_rhs(repl)) patdiag_emit("stmt", sno_pat_supported(repl) ? "PRE" : "UNSUPPORTED", repl);\n'
    '        if (subj->t == TT_VAR && sno_is_pattern_rhs(repl) && sno_pat_supported(repl)) {\n')
rep('#include "snobol4_system_fns.h"\n', '#include "snobol4_system_fns.h"\nstatic void patdiag_set_line(const tree_t * s);\n')
open(p, 'w', encoding='utf-8').write(s)
print('patdiag patch applied')
