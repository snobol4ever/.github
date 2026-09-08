#!/usr/bin/env python3
"""THE SUITE BANNER — one compressed line per turn, driven by .github/SUITES.tsv (the machine record of SCORE.md § THE SUITE TABLE).
usage: util_suite_banner.py [--plain] [--line] [--md] [--render] [--set KEY PASS TOTAL [DATE] [TREE]]
  (no args)  print the banner as an aligned GRID (Lon 2026-09-06): header with the all-suites 100/100 verdict, then 3 columns x 7 rows of cells: nick pass/total left eta emoji
  --line     the one-line form (cells joined by │)
  --plain    no ANSI colour
  --md       print the markdown table for SCORE.md § THE SUITE TABLE
  --set      rewrite one row's today_* (DATE defaults to the box clock day) and print the banner
             -- and RE-RENDER SCORE.md § THE SUITE TABLE from the TSV in the same call (coo 2026-09-06, on hq_R's
             finding that the markdown table was a third home for the number nothing rendered)
  --render   re-render SCORE.md § THE SUITE TABLE rows from SUITES.tsv, in place; print what changed
STALE rule (Lon 2026-09-06 'Do not depend on cron', MASTER-PLAN THE PACE RULES 10): a row whose today_date is older than the box-clock day reads U+23F3 in place of its emoji and is counted on the first line; a STALE row is a rank-0 measure pick in its lane.
ETA rule: rate = (today_pass - first_pass) / max(1, days(first_date..today_date)); eta = remaining / rate; a suite that has not moved reads STUCK; complete reads DONE; a suite with one reading reads NEW.
CRITERION rule (hq_T 2026-09-06, after ceo-372; AMENDED coo 2026-09-08 on Lon's word "Fix it so you CAN do a comparison"). A row may carry criterion_changed = <YYYY-MM-DD>:<slug>. When its first_date PREDATES that day, first_* and today_* answer two different questions and their difference is not a movement -- that much stands, and first_* is still never re-baselined. ⛔ WHAT NO LONGER STANDS is printing n/c and stopping: that is true about those two numbers and useless as an answer to "are we getting better?". Instead likeforlike() holds the POPULATION fixed -- today's graded set -- and asks the progress table what those same programs did then and do now. Same programs, same modes, two dates, so a changed denominator cannot distort it, and nothing is invented: it re-reads per-program evidence already on file. The row then gets a real rate and a real ETA like any other. Programs with no reading at the earlier date are excluded from BOTH sides rather than counted as failures-then-passes-now, which would manufacture progress out of missing data. Only two states remain uncomparable and they are told apart: `no rows` (the table has never seen the suite) and `1 day` (rows exist but all from one day, so there is no earlier reading yet) -- both facts about our instrumentation, never verdicts about the suite.
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
def recriterioned(r):
    """The row's first reading was taken under a DIFFERENT criterion than today's, so today_pass
    and first_pass are not two readings of one thing and their difference is not a movement.

    ⛔⭐ WHY A MARKER AND NOT A RE-BASELINE (hq_T 2026-09-06, on hq_V's report; ceo-372 is the first
    criterion change to hit this table). When ceo-372 moved four suite rows from a single mode to the
    AND per program, this column began subtracting a PRE-CRITERION number from a POST-CRITERION one:
    PAT rendered -6 in a sitting it moved FORWARD six programs, and FPC -3, and because eta() reads
    rate<=0 as STUCK both rows put a false stuck marker into the headline verdict Lon reads.
    ⭐ hq_V found it and deliberately did NOT re-baseline the two rows they own, on the grounds that a
    seat quietly re-cutting the baseline of its own rows to make its own lane look better is the exact
    shape nobody could audit later. That judgement is why this is a marker: the honest alternative --
    a first reading re-measured under the new criterion -- would mean re-running trees that no longer
    exist, so it could only ever be invented. ⛔ A COMPARISON ACROSS TWO CRITERIA IS NOT A MEASUREMENT,
    and the cure for a number that cannot be computed is to say so, never to print a plausible one.
    The marker is SELF-CLEARING: it stops firing the day a first reading under the current criterion
    is recorded, so nothing has to remember to remove it."""
    mark=(r.get('criterion_changed') or '').strip()
    if not mark: return ''
    when=mark.split(':',1)[0]
    # ⛔ STRICTLY AFTER, because dates here are DAYS and a criterion can change mid-day: a first reading
    # stamped the SAME day as the change cannot be placed on either side of it. Treating it as pre-criterion
    # is the conservative arm -- it prints "not computable" for a reading that might have been comparable,
    # rather than printing a movement for one that certainly is not. Self-clearing the next day either way.
    try:
        if d(r['first_date']) > d(when): return ''
    except ValueError:
        return ''
    return mark
PROGRESS=os.environ.get('S4E_PROGRESS') or '/home/resources/progress/results.tsv'
# SUITES.tsv key -> the name the progress table records this suite under.
DBNAME={'sno-master':'snobol4-master','icn-master':'icon-master','pl-master':'prolog-master',
        'pas-master':'pascal-master','raku-master':'raku-master','snc-master':'snocone-master',
        'reb-master':'rebus-master','testpgms':'spitbol_testpgms'}
_LFL_CACHE=None
def _progress_by_suite():
    """One lean pass over the progress table -> {suite: [(ts, program, mode, outcome)]}.

    ⛔ THE PROGRAM KEY IS NORMALISED TO ITS BARE NAME, and that is not cosmetic. The recorded convention
    CHANGED mid-history: gimpel rows read 'snobol4/gimpel/AGT_driver.sno' through 2026-09-05 and
    'packages/snobol4/gimpel/AGT_driver.sno' from 2026-09-06. A join on raw names across that boundary
    finds NOTHING in common and reports a suite as having no comparable history while +45 sits in the
    table -- measured coo 2026-09-08, which is how this was found.
    ⛔ DIRTY TREES ARE DROPPED: a -dirty stamp is cited for its number, never for its position in a series."""
    global _LFL_CACHE
    if _LFL_CACHE is not None: return _LFL_CACHE
    out={}
    try: fh=open(PROGRESS,encoding='utf-8',errors='replace')
    except OSError:
        _LFL_CACHE={}; return _LFL_CACHE
    with fh:
        head=fh.readline().rstrip('\n').split('\t')
        try: i_ts,i_scrip,i_suite,i_prog,i_mode,i_out=(head.index(c) for c in
            ('ts_utc','scrip','suite','program','mode','outcome'))
        except ValueError:
            _LFL_CACHE={}; return _LFL_CACHE
        for l in fh:
            f=l.split('\t')
            if len(f)<=i_out: continue
            if f[i_mode] not in ('m3','m4'): continue
            if '-dirty' in f[i_scrip]: continue
            prog=f[i_prog].rsplit('/',1)[-1]
            if '.' in prog: prog=prog.rsplit('.',1)[0]
            out.setdefault(f[i_suite],[]).append((f[i_ts],prog,f[i_mode],f[i_out]))
    _LFL_CACHE=out
    return out
def _state_at(recs,cutoff,only=None):
    """AND-per-program greenness as of cutoff, from each program's latest reading at or before it."""
    latest={}
    for ts,prog,mode,outc in recs:
        if ts<=cutoff and (only is None or prog in only):
            k=(prog,mode)
            if k not in latest or ts>latest[k][0]: latest[k]=(ts,outc)
    per={}
    for (prog,mode),(_ts,outc) in latest.items(): per.setdefault(prog,{})[mode]=outc
    return {p:all(v=='PASS' for v in m.values()) for p,m in per.items()}
def likeforlike(r):
    """THE COMPARISON A CHANGED CRITERION CANNOT BREAK (Lon 2026-09-08: "Fix it so you CAN do a comparison").

    A criterion change makes first_pass/first_total and today_pass/today_total answers to two different
    questions, so their difference is not a movement -- that much the CRITERION rule had right. Its mistake
    was to stop there and print n/c, which is true about those two numbers and useless as an answer to
    "are we getting better?".

    ⭐ SO HOLD THE POPULATION FIXED INSTEAD OF THE DENOMINATOR. The progress table records every program
    individually with a timestamp, so today's graded set can be asked what IT did then and what it does now.
    Same programs, same modes, two dates: a movement, and a changed denominator cannot distort it.
    ⛔ THIS INVENTS NOTHING, which is what the old rule was right to refuse. It re-reads evidence already on
    file; it never re-baselines first_*, and those columns keep saying exactly what they always said.
    ⛔ PROGRAMS WITH NO READING AT THE EARLIER DATE ARE EXCLUDED FROM BOTH SIDES, never counted as failures
    then and passes now -- that would manufacture progress out of missing data, which is the failure this
    project keeps naming. They are returned as `unseen` so the gap is visible rather than absorbed.

    Returns None when the table holds nothing for the suite, else a dict; `basis` is the earliest day the
    comparison could actually start from, which may be later than first_date -- the window is stated, never
    implied."""
    recs=_progress_by_suite().get(DBNAME.get(r['key'],r['key']))
    if not recs: return None
    newest=max(t for t,_,_,_ in recs); latest_day=newest[:10]
    pop={p for ts,p,_,_ in recs if ts[:10]==latest_day}
    if not pop: return None
    earlier=[ts for ts,p,_,_ in recs if ts[:10]<latest_day and p in pop]
    if not earlier: return None
    basis=min(earlier)[:10]
    then=_state_at(recs,basis+'T23:59:59',pop)
    now=_state_at(recs,newest,pop)
    seen=[p for p in pop if p in then and p in now]
    if not seen: return None
    return {'then':sum(1 for p in seen if then[p]),'now':sum(1 for p in seen if now[p]),
            'pop':len(seen),'unseen':len(pop)-len(seen),'basis':basis}
def lfl_why(r):
    """Why likeforlike() could not compare -- 'norows' (the table has never seen this suite) or 'oneday'
    (it has rows, but all from a single day, so there is no earlier reading to compare today against).
    ⛔ THESE ARE DIFFERENT FACTS AND THE BANNER MUST NOT PRINT ONE FOR THE OTHER: 'no rows' on a suite with
    537 recorded rows sends a reader to instrument the runner when the only thing missing is a second day."""
    recs=_progress_by_suite().get(DBNAME.get(r['key'],r['key']))
    if not recs: return 'norows'
    return 'oneday'
def eta(r,today):
    fp,ft,tp,tt=int(r['first_pass']),int(r['first_total']),int(r['today_pass']),int(r['today_total'])
    rem=tt-tp
    if rem<=0: return 'DONE',None
    # ⭐ A RE-CRITERIONED ROW IS COMPARED, NOT EXCUSED (Lon 2026-09-08). Its first_*/today_* pair cannot be
    # subtracted, but likeforlike() computes a real movement from the progress table on a fixed population,
    # so the row gets a real rate and a real ETA like every other row. Only a suite the table cannot see at
    # all falls through to NOCMP, and that says "no rows", which is a fact about our instrumentation rather
    # than a verdict about the suite.
    if recriterioned(r):
        L=likeforlike(r)
        if not L: return ('NOROWS' if lfl_why(r)=='norows' else 'ONEDAY'),None
        days=(d(r['today_date'])-d(L['basis'])).days
        rate=(L['now']-L['then'])/days if days>0 else 0
        if rate<=0: return 'STUCK',None
        return 'ETA', today+dt.timedelta(days=rem/rate)
    days=(d(r['today_date'])-d(r['first_date'])).days
    if days<=0: return 'NEW',None
    rate=(tp-fp)/days
    if rate<=0: return 'STUCK',None
    return 'ETA', today+dt.timedelta(days=rem/rate)
def banner(plain=False, grid=True, ncol=3):
    head,rows=load(); today=dt.date.today(); cells=[]; worst=None; stuck=[]; new=[]; done=0; stale=[]; recrit=[]
    for r in rows:
        k,e=eta(r,today); frac=f"{r['today_pass']}/{r['today_total']}"; left=int(r['today_total'])-int(r['today_pass'])
        if (today-d(r['today_date'])).days>=1: stale.append(r['nick'])
        if k=='DONE': col=G; tail='✅ done'; done+=1
        elif k=='STUCK': col=R; tail='⛔ stuck'; stuck.append(r['nick'])
        elif k=='NEW': col=C; tail='🆕 new'; new.append(r['nick'])
        elif k=='NOROWS': col=C; tail='◻ no rows'; recrit.append(r['nick'])
        elif k=='ONEDAY': col=C; tail='◻ 1 day'; recrit.append(r['nick'])
        else:
            col=Y if e>dt.date(2026,9,10) else G; tail='→ '+e.strftime('%m-%d'); worst=e if (worst is None or e>worst) else worst
        mark='⏳' if r['nick'] in stale else r['emoji']
        if grid: cell=pad(f"{r['nick']:<7}{r['today_pass']:>5}/{r['today_total']:<5}Δ{left:<4} " + pad(tail, 9) + f" {mark}", 36)
        else: cell=f"{mark}{r['nick']} {frac} {tail}"
        cells.append(cell if plain else f"{col}{cell}{Z}")
    n=len(rows)
    if stuck: verdict=f"ALL {n} SUITES 100/100: NOT ON THE CURVE — {len(stuck)} stuck ({', '.join(stuck)})"; vc=R
    elif recrit: verdict=f"ALL {n} SUITES 100/100: {len(recrit)} suite(s) the progress table cannot see yet ({', '.join(recrit)})"; vc=C
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
        k,e=eta(r,today)
        rc=recriterioned(r)
        if rc:
            L=likeforlike(r)
            if L:
                mv=(f"{L['now']-L['then']:+d}"
                    f" <sup>[{L['then']}→{L['now']} of {L['pop']} since {L['basis'][5:]}]</sup>")
            else:
                mv='—'
        else:
            mv=f"{int(r['today_pass'])-int(r['first_pass']):+d}"
        tail={'DONE':'✅ done','STUCK':'⛔ stuck','NEW':'🆕 one reading',
              'NOROWS':'◻ the progress table holds no rows for this suite yet, so nothing can be compared',
              'ONEDAY':'◻ every recorded row is from one day — a second day of readings makes this comparable'}.get(
              k, '→ '+e.strftime('%Y-%m-%d') if e else '')
        if rc and k not in ('DONE','NOROWS','ONEDAY'):
            tail += (f" · 🔀 criterion changed ({rc.split(':',1)[-1]}), so `moved` is the same programs"
                     f" re-read: today's graded set compared against its own earliest reading")
        print(f"| {r['emoji']} {r['nick']} ({r['key']}) | {r['lang']} | {r['first_pass']}/{r['first_total']} ({r['first_date'][5:]}) | {r['today_pass']}/{r['today_total']} ({r['today_date'][5:]}, `{r['tree']}`) | {mv} | {tail} |")
SCORE=os.environ.get('S4E_SCORE_MD') or os.path.join(os.path.dirname(os.path.abspath(TSV)),'SCORE.md')
def md_lines():
    import io, contextlib
    buf=io.StringIO()
    with contextlib.redirect_stdout(buf): md()
    return buf.getvalue().rstrip('\n').split('\n')
def render_table():
    """Re-render SCORE.md § THE SUITE TABLE (the rows under the '| suite | lang |' header) from SUITES.tsv, in place.
    Returns a one-line note; never silent, never a guess: a table it cannot find is said NOT rendered."""
    if not os.path.exists(SCORE):
        return f"⚠ suite table NOT rendered: {SCORE} missing beside the TSV (SUITES.tsv is set; the markdown table reads STALE until a renderer runs)"
    L=open(SCORE,encoding='utf-8').read().split('\n')
    hdr=[i for i,l in enumerate(L) if l.startswith('| suite | lang |')]
    if len(hdr)!=1:
        return f"⚠ suite table NOT rendered: {len(hdr)} '| suite | lang |' header(s) in {SCORE}, expected exactly one"
    st=hdr[0]; en=st
    while en<len(L) and L[en].startswith('|'): en+=1
    new=md_lines(); old=L[st:en]
    changed=sum(1 for a,b in zip(old,new) if a!=b)+abs(len(old)-len(new))
    if changed==0: return "suite table: SCORE.md § THE SUITE TABLE already matches SUITES.tsv (0 rows changed)"
    L[st:en]=new; open(SCORE,'w',encoding='utf-8').write('\n'.join(L))
    return f"suite table: SCORE.md § THE SUITE TABLE re-rendered from SUITES.tsv in the same call ({changed} row(s) changed)"
def main(a):
    if '--set' in a:
        i=a.index('--set'); key,p,t=a[i+1],a[i+2],a[i+3]; date=a[i+4] if len(a)>i+4 and not a[i+4].startswith('-') else dt.date.today().isoformat(); tree=a[i+5] if len(a)>i+5 else None
        head,rows=load(); r=next((x for x in rows if x['key']==key),None)
        if r is None: sys.exit(f"REFUSE: no suite key {key}")
        r['today_pass'],r['today_total'],r['today_date']=p,t,date
        if tree: r['tree']=tree
        save(head,rows)
        print(render_table())
    if '--render' in a: print(render_table()); return
    if '--md' in a: md()
    else: banner('--plain' in a, grid='--line' not in a)
main(sys.argv[1:])
