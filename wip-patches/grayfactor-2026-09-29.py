import re, sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
tok = {}
for op, body in re.findall(r"^\$'([^']+)'\s*=\s*(.*?);\s*$", s, re.M):
    m = re.fullmatch(r"\*\$'( +)' +'" + re.escape(op) + r"' +\*\$'( +)'", body.strip())
    if m and not re.fullmatch(r'[a-z]+', op): tok[op] = (m.group(1), m.group(2))
def scan_groups(t):
    out, i, n = [], 0, len(t)
    while i < n:
        ch = t[i]
        if ch in "'\"":
            j = t.find(ch, i + 1); j = n if j < 0 else j + 1; out.append(t[i:j]); i = j; continue
        if ch == '(':
            depth, q, j = 0, None, i
            while j < n:
                c = t[j]
                if q:
                    if c == q: q = None
                elif c in "'\"": q = c
                elif c == '(': depth += 1
                elif c == ')':
                    depth -= 1
                    if depth == 0: break
                j += 1
            inner = t[i + 1:j]
            out.append('(' + rewrite_alt(scan_groups(inner)) + ')'); i = j + 1; continue
        out.append(ch); i += 1
    return ''.join(out)
def split_top(t):
    parts, depth, q, cur = [], 0, None, ''
    for ch in t:
        if q:
            cur += ch
            if ch == q: q = None
            continue
        if ch in "'\"": q = ch; cur += ch; continue
        if ch == '(': depth += 1
        elif ch == ')': depth -= 1
        if ch == '|' and depth == 0: parts.append(cur); cur = ''
        else: cur += ch
    parts.append(cur); return parts
stats = {'groups': 0, 'alts': 0}
def rewrite_alt(inner):
    alts = split_top(inner)
    if len(alts) < 2: return inner
    info = []
    for a in alts:
        m = re.match(r"(\s*)\*\$'([^']+)'(.*)$", a, re.S)
        info.append((m.group(2), m.group(1), m.group(3)) if m and m.group(2) in tok else None)
    out, k = [], 0
    while k < len(alts):
        if info[k]:
            lead = tok[info[k][0]][0]; j = k
            while j < len(alts) and info[j] and tok[info[j][0]][0] == lead: j += 1
            if j - k >= 2:
                sub = [info[x][1] + "'" + info[x][0] + "' *$'" + tok[info[x][0]][1] + "'" + info[x][2] for x in range(k, j)]
                lw = re.match(r'\s*', alts[k]).group(0)
                out.append(lw + "*$'" + lead + "' (" + '|'.join(s2[len(lw):] if x == 0 else s2 for x, s2 in enumerate(sub)) + ")" + ('' if j == len(alts) else ' '))
                stats['groups'] += 1; stats['alts'] += j - k; k = j; continue
        out.append(alts[k]); k += 1
    return '|'.join(out)
res = []
for m in re.finditer(r"^([A-Za-z_][A-Za-z0-9_]*)(\s*=\s*)(.*?);(?=\s*\n)", s, re.M | re.S):
    pass
def fix(m):
    return m.group(1) + m.group(2) + scan_groups(m.group(3)) + ';'
s2 = re.sub(r"^([A-Za-z_][A-Za-z0-9_]*)(\s*=\s*)(.*?);(?=\s*\n)", fix, s, flags=re.M | re.S)
open(dst, 'w').write(s2); print('tokens', len(tok), 'groups hoisted', stats['groups'], 'alternatives inlined', stats['alts'])
