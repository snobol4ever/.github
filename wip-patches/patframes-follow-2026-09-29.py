import re, sys, collections
exec(open(__file__.replace('patframes-follow', 'patframes-classify')).read().split('res = collections.Counter()')[0])
def label_index(fn):
    ix = {}
    for t, s in enumerate(fn):
        m = re.match(r'^(\S+):', s)
        if m: ix[m.group(1)] = t
    return ix
def follow(name, fn, ix, lab, depth=0):
    # from a gamma-return label, walk straight-line code: classify what runs before the thunk's own gamma
    seen = []; t = ix.get(lab); steps = 0
    while t is not None and steps < 40:
        s = fn[t]; steps += 1
        ins = s.split('#')[0]
        m = re.search(r'jmp\s+(\S+)\s*$', ins)
        body = re.sub(r'^\S+:\s*', '', ins).strip()
        if body and not body.startswith('jmp') and not body.startswith('.'):
            op = body.split()[0]
            if re.search(r'\[rbp \+ -\d+\]', body): seen.append('zeta-store' if re.search(r'mov\s+qword ptr \[rbp', body) or re.search(r'mov\s+dword ptr \[rbp', body) else 'zeta-read')
            elif op == 'lea': pass
            else: seen.append(op)
        if m:
            tgt = m.group(1)
            if tgt == name + '_γ': return 'tail' if not seen else 'tail-after:' + ','.join(sorted(set(seen)))
            if re.match(r'n\d+_\w+_α$', tgt): return 'next-box:' + re.match(r'n\d+_(\w+)_α$', tgt).group(1)
            if tgt in ix: t = ix[tgt]; continue
            return 'other:' + tgt
        t += 1
    return 'unresolved'
agg = collections.Counter(); cls = collections.Counter()
for p in sys.argv[1:]:
    L = open(p, encoding='utf-8', errors='replace').read().split('\n')
    for name, fn in functions(L):
        ix = label_index(fn); bx = boxes(fn); kinds = [b[1] for b in bx]
        nested = [b for b in bx if b[1] in ('match_defer', 'match_arbno', 'call')]
        if not nested: cls['A'] += 1; continue
        worst = 'B'
        for b in nested:
            if b[1] != 'match_defer': agg['nested ' + b[1]] += 1; worst = 'C'; continue
            for s in b[2]:
                pass
            tg = None
            for k in range(len(b[2]) - 4):
                a = re.search(r'lea\s+rcx, \[rip \+ (\S+)\]', b[2][k + 2])
                if a and 'push' in b[2][k + 1] and re.search(r'jmp\s+rax', b[2][k + 3]): tg = a.group(1); break
            r = follow(name, fn, ix, tg) if tg else 'no-call-found'
            agg[r.split(':')[0] + (':' + r.split(':')[1] if r.startswith(('next-box', 'tail-after')) else '')] += 1
            if r == 'tail': continue
            if r.startswith('tail-after') and set(r.split(':')[1].split(',')) <= {'zeta-store'}: worst = max(worst, 'B2'); continue
            worst = 'C'
        cls[worst] += 1
print('thunks:', dict(cls))
for k, v in agg.most_common(25): print('  %5d  %s' % (v, k))
