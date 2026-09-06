#!/usr/bin/env python3
"""THE SUITE BANNER — one compressed line per turn, driven by .github/SUITES.tsv (the machine record of SCORE.md § THE SUITE TABLE).
usage: util_suite_banner.py [--plain] [--line] [--md] [--set KEY PASS TOTAL [DATE] [TREE]]
  (no args)  print the banner as an aligned GRID (Lon 2026-09-06): header with the all-suites 100/100 verdict, then 3 columns x 7 rows of cells: nick pass/total left eta emoji
  --line     the one-line form (cells joined by │)
  --plain    no ANSI colour
  --md       print the markdown table for SCORE.md § THE SUITE TABLE
  --set      rewrite one row's today_* (DATE defaults to the box clock day) and print the banner
STALE rule (Lon 2026-09-06 'Do not depend on cron', MASTER-PLAN THE PACE RULES 10): a row whose today_date is older than the box-clock day reads U+23F3 in place of its emoji and is counted on the first line; a STALE row is a rank-0 measure pick in its lane.
ETA rule: rate = (today_pass - first_pass) / max(1, days(first_date..today_date)); eta = remaining / rate; a suite that has not moved reads STUCK; complete reads DONE; a suite with one reading reads NEW.
"""
import sys, os, datetime as dt, unicodedata as _ud
def dw(s):
    """DISPLAY columns, not len(). The grid misaligned because padding counted CHARACTERS (Lon 2026-09-06:
    "get the suites banner to line up vertically; most likely your length counts are off due to unicode").
    Three independent ways len() lies here, all live in this banner:
      - a WIDE char is 1 char and 2 columns: U+2705 done, U+26D4 stuck, U+1F195 new, and every W emoji;
      - a VARIATION SELECTOR is 1 char and 0 columns, and it makes its NARROW base render wide: ❄️ and 🏛️
        are U+2744/U+1F3DB + U+FE0F, len()==2, one 2-column glyph;
      - a REGIONAL INDICATOR PAIR is 2 chars and one 2-column glyph: 🇫🇷 is U+1F1EB U+1F1F7.
    U+2192 (the ETA arrow) is east_asian_width 'A' (ambiguous) and renders NARROW, which is why the ETA cells
    were the ones that lined up and the done/stuck/new cells were not."""
    w = 0; i = 0; n = len(s)
    while i < n:
        ch = s[i]; o = ord(ch)
        if o in (0xFE0F, 0xFE0E) or _ud.combining(ch): i += 1; continue
        if 0x1F1E6 <= o <= 0x1F1FF:
            w += 2; i += 2 if (i + 1 < n and 0x1F1E6 <= ord(s[i + 1]) <= 0x1F1FF) else 1; continue
        if i + 1 < n and ord(s[i + 1]) == 0xFE0F: w += 2; i += 2; continue
        if _ud.east_asian_width(ch) in ('W', 'F') or 0x1F300 <= o <= 0x1FAFF: w += 2
        else: w += 1
        i += 1
    return w
def pad(s, width):
    """left-justify to WIDTH display columns; never truncates, so a wide cell pushes its row instead of lying."""
    d = dw(s)
    return s + ' ' * (width - d) if d < width else s
HERE=os.path.dirname(os.path.abspath(__file__))
# ⛔ S4E_SUITES_TSV EXISTS SO A SCRATCH HARNESS CAN BE SCRATCH IN BOTH OF ITS OUTPUTS (hq_T 2026-09-06,
# ceo CEO-363).  util_score_row.py now mirrors a V/M write into the suite table by calling this script,
# so its selftest -- which grades a COPY of SCORE.md -- was writing its fake rebus numbers into the REAL
# SUITES.tsv, the file the banner and Lon read, while printing that it works on a scratch copy.  A
# redirect that covers one of two outputs is not a redirect; measured live, it moved a real row.
TSV=os.environ.get('S4E_SUITES_TSV') or os.path.join(HERE,'..','SUITES.tsv')
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
    head,rows=load(); today=dt.date.today(); cells=[]; worst=None; stuck=[]; new=[]; done=0; stale=[]
    for r in rows:
        k,e=eta(r,today); frac=f"{r['today_pass']}/{r['today_total']}"; left=int(r['today_total'])-int(r['today_pass'])
        if (today-d(r['today_date'])).days>=1: stale.append(r['nick'])
        if k=='DONE': col=G; tail='✅ done'; done+=1
        elif k=='STUCK': col=R; tail='⛔ stuck'; stuck.append(r['nick'])
        elif k=='NEW': col=C; tail='🆕 new'; new.append(r['nick'])
        else:
            col=Y if e>dt.date(2026,9,10) else G; tail='→ '+e.strftime('%m-%d'); worst=e if (worst is None or e>worst) else worst
        mark='⏳' if r['nick'] in stale else r['emoji']
        if grid: cell=pad(f"{r['nick']:<7}{r['today_pass']:>5}/{r['today_total']:<5}Δ{left:<4} " + pad(tail, 9) + f" {mark}", 36)
        else: cell=f"{mark}{r['nick']} {frac} {tail}"
        cells.append(cell if plain else f"{col}{cell}{Z}")
    n=len(rows)
    if stuck: verdict=f"ALL {n} SUITES 100/100: NOT ON THE CURVE — {len(stuck)} stuck ({', '.join(stuck)})"; vc=R
    elif new: verdict=f"ALL {n} SUITES 100/100: unknown — {len(new)} suites have one reading"; vc=C
    elif worst: verdict=f"ALL {n} SUITES 100/100 → {worst.strftime('%Y-%m-%d')} at today's rates"; vc=G
    else: verdict=f"ALL {n} SUITES 100/100: DONE"; vc=G
    hdr=f"🏁 {today.strftime('%m-%d')} {verdict} · {done}/{n} done" + (f" · ⏳ {len(stale)} STALE >24h ({', '.join(stale)})" if stale else '')
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
