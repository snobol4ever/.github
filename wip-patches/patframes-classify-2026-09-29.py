import re, sys, collections
# patframes2.py <file.s>... -- Lon 2026-09-29: "The purpose of RBP will be an activation frame, since the RSP SPINE was not enough for
# essentially the complexity." A PAT$ thunk needs its RBP frame only where it must reach its own state (continuations or zeta) AFTER a
# nested pattern call has SUCCEEDED -- the callee leaves its frame and record on the stack, an amount no compile-time offset knows.
def functions(L):
    starts = [i for i, s in enumerate(L) if re.match(r'^FN__PAT\$\d+:', s)]
    for i in starts:
        name = L[i][4:-1]; j = i + 1
        while j < len(L) and not L[j].startswith('.Lgcmap_%s_s:' % name): j += 1
        yield name, L[i:j + 1]
def boxes(fn):
    cur = None; out = []
    for s in fn:
        m = re.search(r'\.type\s+(n\d+)_(\w+)_bx', s)
        if m: cur = [m.group(1), m.group(2), []]; out.append(cur); continue
        if cur is not None:
            if re.search(r'\.size\s+%s_%s_bx' % (cur[0], cur[1]), s): cur = None; continue
            cur[2].append(s)
    return out
def gamma_targets(name, fn, bx):
    # the gamma-return label a nested call pushes last, and where that label jumps
    body = bx[2]; tg = []
    for k in range(len(body) - 4):
        a = re.search(r'lea\s+rcx, \[rip \+ (\S+)\]', body[k + 2]); b = re.search(r'jmp\s+rax', body[k + 3])
        if a and b and 'push' in body[k + 1] and 'push' in body[k + 3]:
            lab = a.group(1)
            for t, s in enumerate(fn):
                if s.startswith(lab + ':'):
                    m = re.search(r'jmp\s+(\S+)\s*$', fn[t + 1]) or re.search(r'jmp\s+(\S+)\s*$', s)
                    tg.append(m.group(1) if m else '?'); break
    return tg
def writes_r12(s):
    ins = s.split('#')[0]
    return bool(re.search(r'^\s*(mov|lea|pop|add|sub|xor|and|or|movsxd|movzx|inc|dec|imul|shl|shr|xchg)\s+r12\b', ins))
res = collections.Counter(); per = {}
for p in sys.argv[1:]:
    L = open(p, encoding='utf-8', errors='replace').read().split('\n'); c = collections.Counter(); lang = p.split('/')[-1][:-2]
    for name, fn in functions(L):
        bx = boxes(fn); kinds = [b[1] for b in bx]
        nested = [b for b in bx if b[1] in ('match_defer', 'match_arbno', 'call')]
        tail = True
        for b in nested:
            if b[1] != 'match_defer': tail = False; continue
            tg = gamma_targets(name, fn, b)
            if not tg or any(t != name + '_γ' for t in tg[:1]): tail = False
        if not nested: cls = 'A-no-nested-call'
        elif tail: cls = 'B-nested-only-as-tail-call'
        else: cls = 'C-work-after-a-nested-call'
        c[cls] += 1; c['pat'] += 1
        whole = '\n'.join(fn)
        c['rdx-slot-read'] += bool(re.search(r'(mov|lea)\s+\w+,\s+qword ptr \[rbp \+ -24\]', whole))
        c['body-writes-r12'] += any(writes_r12(s) for b in bx for s in b[2])
        c['dead-mov-eax-0'] += bool(re.search(r'mov\s+eax, 0\n\s+lea\s+rdi, \[rbp \+ -\d+\]\n\s+xor\s+eax, eax', whole))
        m = re.search(r'mov\s+ecx, (\d+)\n\s+rep\s+stosb', whole); c['zero-fill-bytes'] += int(m.group(1)) if m else 0
    print('%-8s PAT$=%4d  A no nested call=%4d  B nested call only in tail position=%4d  C work after a nested call=%4d | saved rdx ever read=%d  body writes r12=%d  dead mov eax,0=%d  zero-fill bytes=%d'
          % (lang, c['pat'], c['A-no-nested-call'], c['B-nested-only-as-tail-call'], c['C-work-after-a-nested-call'], c['rdx-slot-read'], c['body-writes-r12'], c['dead-mov-eax-0'], c['zero-fill-bytes']))
    res.update(c)
c = res
print('%-8s PAT$=%4d  A no nested call=%4d  B nested call only in tail position=%4d  C work after a nested call=%4d | saved rdx ever read=%d  body writes r12=%d  dead mov eax,0=%d'
      % ('TOTAL', c['pat'], c['A-no-nested-call'], c['B-nested-only-as-tail-call'], c['C-work-after-a-nested-call'], c['rdx-slot-read'], c['body-writes-r12'], c['dead-mov-eax-0']))
