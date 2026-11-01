import sys, os, re, collections, importlib.util, json
W = sys.argv[1]
spec = importlib.util.spec_from_file_location('U', '/home/claude_cto/harness/scripts/util_header_fanin.py'); U = importlib.util.module_from_spec(spec); spec.loader.exec_module(U)
t = U.Tree(W, U.default_obj(W), 200)
H = sys.argv[4]
D = set(t.info[H][0])
# per-id line in emit.h (first declaring line) by a crude scan
raw = open(os.path.join(W, 'src', H)).read().split('\n')
line_of = {}
for i, l in enumerate(raw, 1):
    for w in set(U.WORD.findall(U.strip_strings(l))):
        if w in D and w not in line_of:
            line_of[w] = i
users = collections.defaultdict(set)
for u in t.units:
    for w in t.tokens(u) & D:
        users[w].add(u)
# headers as pseudo-units: own tokens plus the bodies of macros they name
hdrs = [h for h in t.headers if h != H and h.startswith(('emitter/', 'templates/', 'ir/', 'planner/', 'lower/', 'runtime/', 'driver/', 'parsers/', 'tools/', 'optimizer/'))]
for h in hdrs:
    txt = U.strip_strings(U.strip_comments(U.read(os.path.join(W, 'src', h))))
    toks = set(U.WORD.findall(txt)); todo = list(toks)
    while todo:
        w = todo.pop()
        for hh, body in t.macro_defs.get(w, ()):
            for x in body:
                if x not in toks:
                    toks.add(x); todo.append(x)
    for w in toks & D:
        users[w].add('H:' + h)
rows = []
for w in sorted(D, key=lambda w: line_of.get(w, 9999)):
    us = users.get(w, set())
    tpl = sorted(u for u in us if u.startswith('templates/'))
    oth = sorted(u for u in us if not u.startswith('templates/') and not u.startswith('H:'))
    hh = sorted(u[2:] for u in us if u.startswith('H:'))
    rows.append((line_of.get(w, 0), w, len(tpl), len(oth), len(hh), ' '.join(os.path.basename(x) for x in oth[:6]), ' '.join(os.path.basename(x) for x in hh[:6])))
with open(sys.argv[2], 'w') as f:
    f.write('line\tid\ttemplates\tothers\theaders\tothers_eg\theaders_eg\n')
    for r in rows:
        f.write('\t'.join(str(x) for x in r) + '\n')
json.dump({w: sorted(users.get(w, ())) for w in D}, open(sys.argv[3], 'w'))
print('ids=%d units=%d headers=%d; emit.h fanin=%d direct=%d users=%d' % (len(D), len(t.units), len(hdrs), t.fanin[H], t.direct_of[H], len(t.users_of[H])))
