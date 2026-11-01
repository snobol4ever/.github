#!/usr/bin/env python3
# hdr7b.py <SCRIP root> -- the second pass of headers step 7 after the build: hdr7.py gave the trail layout to the three readers the instrument's
# direct count named; the build (bb_unify_const.cpp: PL_TR_ENTRY_BYTES not declared) and then the full user count on the built 6C tree named
# six more -- five templates and by_name_dispatch.c -- that read the layout's macros through rt_pl_trail.h. Each gets the layout include where
# its carrier stands: before its own rt_pl_trail.h include, or (xa_flat.cpp, which has none) before the first include whose header carries it.
import sys, os, re
R = sys.argv[1].rstrip('/') + '/src/'
def rd(p): return open(R + p).read()
def wr(p, t): open(R + p, 'w').write(t)
for u in ('templates/bb/bb_unify_const.cpp', 'templates/bb/bb_call_pl_leaf.cpp', 'templates/bb/bb_unify_value.cpp', 'templates/bb/bb_call_proc_staged.cpp', 'runtime/by_name_dispatch.c'):
    t = rd(u); m = re.search(r'^#include "(runtime/rt/)?rt_pl_trail\.h"\n', t, re.M); assert m, u
    if 'pl_trail_layout.h' in t:
        print('  %s: already carries the layout' % u); continue
    wr(u, t[:m.start()] + '#include "%spl_trail_layout.h"\n' % (m.group(1) or '') + t[m.start():]); print('  %s: the layout before its rt_pl_trail.h include' % u)
def path_of(nm, who):
    return nm if os.path.exists(R + nm) else os.path.join(os.path.dirname(who), nm)
def reaches(p, target, seen):
    if p in seen: return None
    seen.add(p)
    for nm in re.findall(r'^#include "([^"]+)"', rd(p), re.M):
        q = path_of(nm, p)
        if not os.path.exists(R + q): continue
        if q == target: return [q]
        r = reaches(q, target, seen)
        if r: return [q] + r
    return None
u = 'templates/xa/xa_flat.cpp'; t = rd(u)
if 'pl_trail_layout.h' in t:
    print('  %s: already carries the layout' % u)
else:
    assert 'rt_pl_trail.h' not in t
    cands = []
    for m in re.finditer(r'^#include "([^"]+)"\n', t, re.M):
        p = path_of(m.group(1), u)
        if os.path.exists(R + p):
            chain = [p] if p == 'runtime/rt/pl_trail_layout.h' else reaches(p, 'runtime/rt/pl_trail_layout.h', set())
            if chain: cands.append((m, [p] + chain[1:] if chain[0] == p else [p] + chain))
    assert cands, 'xa_flat.cpp: no direct include reaches pl_trail_layout.h'
    m, chain = cands[0]; wr(u, t[:m.start()] + '#include "runtime/rt/pl_trail_layout.h"\n' + t[m.start():]); print('  %s: the layout before %s (it reaches the layout by %s)' % (u, chain[0], ' > '.join(chain)))
