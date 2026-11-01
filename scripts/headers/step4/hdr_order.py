#!/usr/bin/env python3
# hdr_order.py -- the include-order instrument of the header split: for every compile line of `make -B -n build-all`, run the
# preprocessor with -H and record, per unit, the ordered list of (depth, header-under-src) as the compiler FIRST OPENS them.
# A static inline function is emitted in definition order, so the order in which inline-bearing headers are first reached decides
# the .text layout of the object (the lower_raku.o and lower_snobol4.o swaps of headers step 6B); this file is the measure.
#   hdr_order.py --root W --cmds make-n.txt --out order.json
import sys, os, re, json, shlex, subprocess, argparse, concurrent.futures
ap = argparse.ArgumentParser(); ap.add_argument('--root', required=True); ap.add_argument('--cmds', required=True); ap.add_argument('--out', required=True); ap.add_argument('--jobs', type=int, default=8)
a = ap.parse_args()
W = os.path.abspath(a.root); SRC = W + '/src/'
cmds = []
for line in open(a.cmds, errors='replace'):
    if ' -c ' not in line: continue
    m = re.search(r'(?:^|\s)((?:ccache\s+)?(?:gcc|g\+\+|cc|c\+\+)\s.*)$', line.rstrip('\n'))
    if not m: continue
    cmds.append(m.group(1))
def run(cmd):
    try: args = shlex.split(cmd)
    except ValueError: return None
    if args and args[0] == 'ccache': args = args[1:]
    out = []; skip = 0; src = None
    for i, t in enumerate(args):
        if skip: skip -= 1; continue
        if t == '-o': out.append(t); out.append('/dev/null'); skip = 1; continue
        if t in ('-MMD', '-MP', '-MD'): continue
        if t in ('-MF', '-MT', '-MQ'): skip = 1; continue
        if t.startswith('-MF'): continue
        if re.search(r'\.(c|cpp|cc|S)$', t) and not t.startswith('-'): src = t
        out.append(t)
    if not src: return None
    out += ['-E', '-H']
    p = subprocess.run(out, cwd=W, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, errors='replace')
    seq = []
    for l in p.stderr.split('\n'):
        m = re.match(r'^(\.+) (.*)$', l)
        if not m: 
            if l.startswith('Multiple include guards'): break
            continue
        path = os.path.normpath(os.path.join(W, m.group(2)) if not os.path.isabs(m.group(2)) else m.group(2))
        if path.startswith(SRC): seq.append([len(m.group(1)), path[len(SRC):]])
    rel = os.path.relpath(os.path.normpath(os.path.join(W, src)) if not os.path.isabs(src) else src, W)
    return rel, seq, p.returncode
res = {}; bad = []
with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
    for r in ex.map(run, cmds):
        if r is None: continue
        rel, seq, rc = r
        if rc: bad.append(rel)
        if rel in res: res[rel] = res[rel] if len(res[rel]) >= len(seq) else seq
        else: res[rel] = seq
json.dump(res, open(a.out, 'w'))
print('units=%d preprocess-failed=%d -> %s' % (len(res), len(bad), a.out))
if bad: print('FAILED:', ' '.join(bad[:10]))
