#!/usr/bin/env python3
"""THE SUITE BANNER — one compressed line per turn, driven by .github/SUITES.tsv (the machine record of SCORE.md § THE SUITE TABLE).
usage: util_suite_banner.py [--plain] [--line] [--md] [--set KEY PASS TOTAL [DATE] [TREE]]
  (no args)  print the banner as an aligned GRID (Lon 2026-09-06): header with the all-suites 100/100 verdict, then 3 columns x 7 rows of cells: nick pass/total left eta emoji
  --line     the one-line form (cells joined by │)
  --plain    no ANSI colour
  --md       print the markdown table for SCORE.md § THE SUITE TABLE
  --set      rewrite one row's today_* (DATE defaults to the box clock day) and print the banner
ETA rule: rate = (today_pass - first_pass) / max(1, days(first_date..today_date)); eta = remaining / rate; a suite that has not moved reads STUCK; complete reads DONE; a suite with one reading reads NEW.
"""
import sys, os, datetime as dt
HERE=os.path.dirname(os.path.abspath(__file__)); TSV=os.path.join(HERE,'..','SUITES.tsv')
R='\033[31m'; G='\033[32m'; Y='\033[33m'; C='\033[36m'; B='\033[1m'; Z='\033[0m'
def load():
    rows=[]; head=None
    for l in open(TSV,encoding='utf-8'):
        if l.startswith('#') or not l.strip(): continue
        f=l.rstrip('\n').split('\t')
        if head is None: head=f; continue
        rows.append(dict(zip(head,f)))
    return head,rows
def save(head,rows):
    lines=[l for l in open(TSV,encoding='utf-8') if l.startswith('#')]
    lines.append('\t'.join(head)+'\n')
    for r in rows: lines.append('\t'.join(r[h] for h in head)+'\n')
    open(TSV,'w',encoding='utf-8').write(''.join(lines))
def d(s): return dt.date.fromisoformat(s)
def eta(r,today):
    fp,ft,tp,tt=int(r['first_pass']),int(r['first_total']),int(r['today_pass']),int(r['today_total'])
    rem=tt-tp
    if rem<=0: return 'DONE',None
    days=(d(r['today_date'])-d(r['first_date'])).days
    if days<=0: return 'NEW',None
    rate=(tp-fp)/days
    if rate<=0: return 'STUCK',None
    return 'ETA', today+dt.timedelta(days=rem/rate)
def banner(plain=False, grid=True, ncol=3):
    head,rows=load(); today=dt.date.today(); cells=[]; worst=None; stuck=[]; new=[]; done=0
    for r in rows:
        k,e=eta(r,today); frac=f"{r['today_pass']}/{r['today_total']}"; left=int(r['today_total'])-int(r['today_pass'])
        if k=='DONE': col=G; tail='✅ done'; done+=1
        elif k=='STUCK': col=R; tail='⛔ stuck'; stuck.append(r['nick'])
        elif k=='NEW': col=C; tail='🆕 new'; new.append(r['nick'])
        else:
            col=Y if e>dt.date(2026,9,10) else G; tail='→ '+e.strftime('%m-%d'); worst=e if (worst is None or e>worst) else worst
        if grid: cell=f"{r['nick']:<7}{r['today_pass']:>5}/{r['today_total']:<5}{left:>4} left  {tail:<8} {r['emoji']}"
        else: cell=f"{r['emoji']}{r['nick']} {frac} {tail}"
        cells.append(cell if plain else f"{col}{cell}{Z}")
    n=len(rows)
    if stuck: verdict=f"ALL {n} SUITES 100/100: NOT ON THE CURVE — {len(stuck)} stuck ({', '.join(stuck)})"; vc=R
    elif new: verdict=f"ALL {n} SUITES 100/100: unknown — {len(new)} suites have one reading"; vc=C
    elif worst: verdict=f"ALL {n} SUITES 100/100 → {worst.strftime('%Y-%m-%d')} at today's rates"; vc=G
    else: verdict=f"ALL {n} SUITES 100/100: DONE"; vc=G
    hdr=f"🏁 {today.strftime('%m-%d')} {verdict} · {done}/{n} done"
    print(hdr if plain else f"{B}{vc}{hdr}{Z}")
    if not grid: print(' │ '.join(cells)); return
    nrow=-(-len(cells)//ncol)
    for i in range(nrow): print(' │ '.join(cells[i+j*nrow] for j in range(ncol) if i+j*nrow<len(cells)))
def md():
    head,rows=load(); today=dt.date.today()
    print('| suite | lang | first graded reading | today | moved | at today\'s rate |'); print('|---|---|---|---|---|---|')
    for r in rows:
        k,e=eta(r,today); mv=int(r['today_pass'])-int(r['first_pass'])
        tail={'DONE':'✅ done','STUCK':'⛔ stuck','NEW':'🆕 one reading'}.get(k, '→ '+e.strftime('%Y-%m-%d') if e else '')
        print(f"| {r['emoji']} {r['nick']} ({r['key']}) | {r['lang']} | {r['first_pass']}/{r['first_total']} ({r['first_date'][5:]}) | {r['today_pass']}/{r['today_total']} ({r['today_date'][5:]}, `{r['tree']}`) | {mv:+d} | {tail} |")
def main(a):
    if '--set' in a:
        i=a.index('--set'); key,p,t=a[i+1],a[i+2],a[i+3]; date=a[i+4] if len(a)>i+4 and not a[i+4].startswith('-') else dt.date.today().isoformat(); tree=a[i+5] if len(a)>i+5 else None
        head,rows=load(); r=next((x for x in rows if x['key']==key),None)
        if r is None: sys.exit(f"REFUSE: no suite key {key}")
        r['today_pass'],r['today_total'],r['today_date']=p,t,date
        if tree: r['tree']=tree
        save(head,rows)
    if '--md' in a: md()
    else: banner('--plain' in a, grid='--line' not in a)
main(sys.argv[1:])
