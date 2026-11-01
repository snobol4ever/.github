#!/usr/bin/env python3
# after_table.py <SCRIP root> <harness/scripts> -- the measured AFTER of ARCH-HEADER-SPLIT 3.7: fan-in and users of the headers the paragraph names, from util_header_fanin.py on the built tree
import sys, subprocess
R, H = sys.argv[1], sys.argv[2]
out = subprocess.run(['python3', '-I', H + '/util_header_fanin.py', '--root', R], capture_output=True, text=True).stdout
rows = {}
for ln in out.split('\n'):
    p = ln.split('\t')
    if len(p) >= 7 and p[0].isdigit(): rows[p[6]] = (int(p[0]), int(p[2]))
NAMES = [('ct_arena.h', 'ir/ct_arena.h'), ('g_runtime.h', 'runtime/core/g_runtime.h'), ('descr.h', 'ir/descr.h'), ('core.h', 'runtime/core/core.h'), ('ir_node.h', 'ir/ir_node.h'), ('ir_graph.h', 'ir/ir_graph.h'), ('plan_facts.h', 'planner/plan_facts.h'), ('emit.h', 'emitter/emit.h'), ('emit_state.h', 'emitter/emit_state.h'), ('x86_ops.h', 'templates/x86/x86_ops.h'), ('rt_pl_trail.h', 'runtime/rt/rt_pl_trail.h'), ('rtcc.h', 'runtime/rt/rtcc.h'), ('stage2.h', 'ir/stage2.h'), ('bb_box.h', 'ir/bb_box.h'), ('lower_pascal_tree.h', 'lower/lower_pascal_tree.h'), ('pl_trail_layout.h', 'runtime/rt/pl_trail_layout.h')]
parts = []
for short, path in NAMES:
    hit = rows.get(path) or next((v for k, v in rows.items() if k.endswith('/' + short)), None)
    parts.append('%s %s' % (short, ('%d (users %d)' % hit) if hit else 'absent'))
print('; '.join(parts))
base = subprocess.run(['python3', '-I', H + '/util_header_fanin.py', '--root', R, '--ceiling'], capture_output=True, text=True).stdout.strip().split('\n')[-1]
print(base)
