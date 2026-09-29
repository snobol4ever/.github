# usage: patdiag-census-grid-2026-09-29.py <worktree>/bootstrap <census-outdir> <lang>... -- renders the per-parser worklist from patdiag-census-run's TSVs
import collections, re, sys
B = sys.argv[1]; OUT = sys.argv[2]
def ingr(parts):
    out=[]
    for p in [x.strip() for x in parts.split(' ; ') if x.strip()]:
        k,_,v=p.partition(':')
        if k=='primarg':
            vs=re.findall(r'\(TT_VAR (\S+?) ?\)',v) or ([v] if not v.startswith('(') else [])
            fs=re.findall(r'\(TT_FNC (\S+)',v)
            out += [f'{x} (as an argument)' for x in vs] + [f'{x}() (as an argument)' for x in fs]
        elif k=='call': out.append(v+'()')
        else: out.append(v)
    return out
def disp(nm): return nm if re.match(r'^[A-Za-z_][A-Za-z0-9_]*$',nm) else "$'"+nm+"'"
for L in sys.argv[3:]:
    src=open(f'{B}/parser_{L}.sc',encoding='utf-8').read().split('\n')
    def start(nm, last):
        d=disp(nm); rx=re.compile(r'^\s*'+re.escape(d)+r'\s*=')
        for i in range(last-1, -1, -1):
            if rx.match(src[i]): return i+1
        return last
    rows=[l.rstrip('\n').split('\t') for l in open(f'{OUT}/{L}.tsv')]
    pr=[r for r in rows if r[0].startswith('parser_')]
    stmt=[r for r in pr if r[2]=='stmt']
    nf=[r for r in stmt if r[6]!='PRE']
    print(f'### parser_{L}.sc — {len(stmt)} named patterns: {len(stmt)-len(nf)} folded, {len(nf)} not')
    groups=collections.OrderedDict()
    for r in nf:
        key=', '.join(sorted(set(ingr(r[8])), key=lambda s:(s!='epsilon', s))) if r[6]=='VARIANT' else 'UNSUPPORTED'
        groups.setdefault(key,[]).append(f'{disp(r[3])}:{start(r[3], int(r[1]))}')
    for k,v in sorted(groups.items(), key=lambda kv:-len(kv[1])):
        print(f'- **{k}** ({len(v)}): '+' '.join(v))
    for r in pr:
        if r[2]!='stmt' and r[6]!='PRE':
            print(f'- match `{r[4].replace("(TT_VAR ","").replace(")","").strip()} ? ...` line {r[1]}: bare '+', '.join(ingr(r[8])))
    print()
