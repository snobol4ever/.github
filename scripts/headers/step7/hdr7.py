#!/usr/bin/env python3
# hdr7.py -- headers step 7, the cures (ARCH-HEADER-SPLIT section 5 row 7; CEO-2032; the cto 2026-10-31): the two fan-in raises and the two unused
# includes the ceiling gate still names after steps 4, 6 B1 and 6C. (1) g_lower.h embeds g_lower_pas_sem_t by value and included the whole Pascal
# tree header for that one record: the record moves into g_lower.h beside the other per-language records and the include goes (lower_pascal_tree.h
# 23 reachers against 5 users -> its three direct includers). (2) rt_pl_trail.h included pl_trail_layout.h and names nothing of it: the include goes,
# and the three units that read the layout through it include it themselves (21 reachers against 16 users -> under the ceiling). (3) aggregates.c
# and pl_rat.c include runtime/core/datatype.h and name nothing of it.   hdr7.py <SCRIP root> [--apply]
import os, re, sys
R = os.path.abspath(sys.argv[1]); S = R + '/src/'; APPLY = '--apply' in sys.argv
def rd(p): return open(S + p, errors='surrogateescape').read()
def wr(p, t): open(S + p, 'w', errors='surrogateescape').write(t) if APPLY else None
# (1) the Pascal lowerer's state moves into g_lower.h, where the other per-language records live. g_lower_pas_sem_t (208 lines) embeds PNodeList by value and
#     points at PasDef, PasFwd, pas_vt and pas_pend_frame -- anonymous typedefs a forward declaration cannot name -- so the record and its small types
#     (lines 3 to the record's end: PNodeList, the two PAS_ macros, pval, PasDef, PasFwd, pas_vt, pas_pend_frame, pas_sem_step_t) move together, to the
#     line where g_lower.h included lower_pascal_tree.h (no definition changes order); lower_pascal_tree.h keeps its one prototype with the forward
#     typedef g_lower.h itself uses for tree_t. The honest design is the pointer (g_lower_pas_sem_t * in the arena, the record back in the Pascal
#     lowerer's own header), which changes g_lower_t's layout and every unit after it: a design row, not an identity landing (the page says so).
lpt = rd('lower/lower_pascal_tree.h'); gl = rd('lower/g_lower.h')
e = lpt.index('} g_lower_pas_sem_t;\n') + len('} g_lower_pas_sem_t;\n'); s = lpt.index('#define LOWER_PASCAL_TREE_H\n') + len('#define LOWER_PASCAL_TREE_H\n')
block = lpt[s:e]; rest = lpt[e:]; assert rest.startswith('tree_t *lower_pascal_tree(') and rest.count('\n') == 2, rest
lpt2 = lpt[:s] + 'typedef struct tree_t tree_t;\n' + rest
old = '#include "lower_pascal_tree.h"\n'; assert gl.count(old) == 1
gl2 = gl.replace(old, block)
assert gl2.index('typedef struct tree_t tree_t;') < gl2.index(block), 'tree_t forward before the block'
print('(1) %d lines (PNodeList, the PAS_ macros, pval, PasDef, PasFwd, pas_vt, pas_pend_frame, pas_sem_step_t, g_lower_pas_sem_t) move from lower_pascal_tree.h into g_lower.h where the include stood; lower_pascal_tree.h keeps the prototype' % block.count('\n'))
wr('lower/lower_pascal_tree.h', lpt2); wr('lower/g_lower.h', gl2)
# (2) rt_pl_trail.h drops the layout; the three readers include it
t = rd('runtime/rt/rt_pl_trail.h'); old = '#include "runtime/rt/pl_trail_layout.h"\n'; assert t.count(old) == 1; wr('runtime/rt/rt_pl_trail.h', t.replace(old, ''))
for u in ('runtime/rt/gc_heap.c', 'runtime/rt/rt_pl_trail.c', 'templates/x86/x86_call.cpp'):
    t = rd(u); m = re.search(r'^#include "(runtime/rt/)?rt_pl_trail\.h"\n', t, re.M); assert m, u   # a same-directory include stays a bare name (6C), a cross-directory one is its path
    assert 'pl_trail_layout.h' not in t
    wr(u, t[:m.start()] + '#include "%spl_trail_layout.h"\n' % (m.group(1) or '') + t[m.start():])
print('(2) rt_pl_trail.h drops pl_trail_layout.h; gc_heap.c, rt_pl_trail.c and x86_call.cpp include it where rt_pl_trail.h stands')
# (3) the two unused includes
print('(3) no unused include is deleted: the instrument named aggregates.c and pl_rat.c for runtime/core/datatype.h, the build refused both (k->u->type, a.u->fields: DATINST_t through DESCR_t\'s union member u); the instrument follows that hop now (harness, hdr7_harness.py is before it; the hop landed by hand in util_header_fanin.py with its ARM 9 control)')
print('APPLIED' if APPLY else '(dry run; --apply writes)')
