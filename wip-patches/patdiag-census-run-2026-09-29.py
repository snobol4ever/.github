# usage: patdiag-census-run-2026-09-29.py <worktree with the census patch applied and built> <outdir> [langs] -- one TSV per parser chain
import re, subprocess, sys, os, collections
WT = sys.argv[1]; OUT = sys.argv[2]; langs = sys.argv[3:] or ['snobol4','snocone','icon','prolog','rebus','pascal']
B = WT + '/bootstrap'
chain = ['global','case','assign','match','counter','stack','tree','ShiftReduce','tdump','gen','qize','semantic','omega','trace']
os.makedirs(OUT, exist_ok=True)
pat = re.compile(r'\[PATDIAG\] line=(\d+) route=(\w+) (?:name=(\S*) |subj=(.*?) |depth=(\d+) )?decision=(\w+) nparts=(\d+) parts=\[(.*?)\] tree=(.*)$')
allrows = {}
for L in langs:
    files = [f'{B}/{c}.sc' for c in chain] + [f'{B}/parser_{L}.sc']
    offs = []; text = ''; n = 0
    for f in files:
        t = open(f, encoding='utf-8').read()
        if not t.endswith('\n'): t += '\n'
        k = t.count('\n'); offs.append((n, n + k, os.path.basename(f))); n += k; text += t
    src = f'{OUT}/{L}.sc'; open(src, 'w', encoding='utf-8').write(text)
    env = dict(os.environ, SCRIP_PATDIAG='1')
    r = subprocess.run([f'{WT}/scrip', '--compile', '-o', f'{OUT}/{L}.s', src], stdin=subprocess.DEVNULL, capture_output=True, text=True, env=env, timeout=300)
    rows = []
    for l in r.stderr.splitlines():
        if not l.startswith('[PATDIAG]'): continue
        m = pat.match(l)
        if not m: print('UNPARSED', l[:160]); continue
        line, route, name, subj, depth, dec, np, parts, tree = m.groups(); line = int(line)
        fl = next(((fn, line - a) for a, b, fn in offs if a < line <= b), ('?', line))
        rows.append(dict(file=fl[0], line=fl[1], route=route, name=name or '', subj=subj or '', depth=depth or '', dec=dec, np=int(np), parts=parts, tree=tree))
    allrows[L] = rows
    with open(f'{OUT}/{L}.tsv', 'w', encoding='utf-8') as w:
        for x in rows: w.write('\t'.join(str(x[k]) for k in ('file','line','route','name','subj','depth','dec','np','parts','tree')) + '\n')
    c = collections.Counter((x['route'], x['dec']) for x in rows)
    print(L, 'rc', r.returncode, 'rows', len(rows), dict(c))
