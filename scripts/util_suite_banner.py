#!/usr/bin/env python3
"""THE SUITE BANNER — one compressed line per turn, driven by .github/SUITES.tsv (the machine record of SCORE.md § THE SUITE TABLE).
usage: util_suite_banner.py [--plain] [--line] [--md] [--grid] [--check] [--render --only KEY | --render --all-rows] [--set KEY PASS TOTAL [DATE] [TREE] [--criterion-changed 'YYYY-MM-DD:reason']]
  (no args)  print the banner as an aligned GRID (Lon 2026-09-06): header with the suite count and how many are done, then 3 columns x N rows of cells: nick pass/total left state emoji
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
import sys, os, re, subprocess, datetime as dt, unicodedata as _ud
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
def rpad(s, width):
    """RIGHT-justify to WIDTH display columns (Lon 2026-09-13: "right justify the numbers"), for NUMERIC cells
    only. A column of right-aligned figures puts the units under the units, so 2619 and 6 and 1928 compare by
    eye down the column; left-aligned they do not, which is the whole reason a reader scans a score grid.
    Never truncates, same as pad(): a wide cell pushes its row rather than lying about its value."""
    d = dw(s)
    return ' ' * (width - d) + s if d < width else s
HERE=os.path.dirname(os.path.abspath(__file__))
# ⛔ S4E_SUITES_TSV EXISTS SO A SCRATCH HARNESS CAN BE SCRATCH IN BOTH OF ITS OUTPUTS (hq_T 2026-09-06,
# ceo CEO-363).  util_score_row.py now mirrors a V/M write into the suite table by calling this script,
# so its selftest -- which grades a COPY of SCORE.md -- was writing its fake rebus numbers into the REAL
# SUITES.tsv, the file the banner and Lon read, while printing that it works on a scratch copy.  A
# redirect that covers one of two outputs is not a redirect; measured live, it moved a real row.
TSV=os.environ.get('S4E_SUITES_TSV') or os.path.join(HERE,'..','SUITES.tsv')
R='\033[31m'; G='\033[32m'; Y='\033[33m'; C='\033[36m'; B='\033[1m'; Z='\033[0m'
# ⛔⭐ DEFERRED IS READ, NEVER INFERRED FROM AN EMPTY READING (hq_T 2026-09-12, ceo CEO-593). A row with no
# today_pass renders `◻ no runner`, which is the honest word for A POPULATION NOBODY GRADES YET -- and it is
# the WRONG word for one Lon has ruled DEFERRED (CEO-579, *"Do not count the FD as failures for us."*). The
# two look identical in this table and are opposite facts: "no runner" is a debt nobody has scheduled, and
# DEFERRED is a debt SCHEDULED OUT, on the record, with the work it waits on named. ⛔ So the discriminator is
# `.github/DEFERRED.tsv` and nothing else: never the emptiness of a cell, and never the suite's name.
DEFERRED_TSV=os.environ.get('S4E_DEFERRED_TSV') or os.path.join(HERE,'..','DEFERRED.tsv')
def deferred_rows():
    """{suite_key: {'count': N, 'ruled_by': str, 'waiting_on': str}} -- {} when the record is absent."""
    out={}
    if not os.path.exists(DEFERRED_TSV): return out
    head=None
    for l in open(DEFERRED_TSV,encoding='utf-8'):
        if l.startswith('#') or not l.strip(): continue
        f=l.rstrip('\n').split('\t')
        if head is None: head=f; continue
        r=dict(zip(head,f))
        k=r.get('suite','').strip()
        if not k: continue
        e=out.setdefault(k,{'count':0,'ruled_by':'','waiting_on':''})
        try: e['count'] += int(r.get('count','0') or 0)
        except ValueError: pass
        for col in ('ruled_by','waiting_on'):
            if r.get(col): e[col] = (e[col] + '; ' + r[col]) if e[col] else r[col]
    return out
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
    # ⛔⭐ ONE RECORD PER (suite, program, mode, DAY), NOT ONE PER ROW (coo 2026-09-23, the ceo's CEO-1212 under CEO-801): this
    # loaded every row of the table -- 4.18M, 684-716 MB for EVERY score-row write, seven arms of the blocking set -- while its one
    # consumer, likeforlike(), only ever asks for the last reading at or before the END OF A DAY (its basis) and the latest reading
    # overall (its newest), which is the last record of the last day. So each (suite, program, mode, day) keeps only its max-ts
    # record, the first seen on a tie exactly as _state_at() breaks ties, and every quantity likeforlike() computes -- newest,
    # latest_day, pop, basis, then, now -- reads the same on the kept records as on all of them (275k of 4.18M on the day this
    # changed). test_gate_progress_readers_stream_and_answer_the_same.sh holds the old and the new answer equal, suite by suite.
    groups={}
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
            ts=f[i_ts]; g=groups.get(f[i_suite])
            if g is None: g=groups[f[i_suite]]={}
            k=(prog,f[i_mode],ts[:10]); cur=g.get(k)
            if cur is None or ts>cur[0]: g[k]=(ts,prog,f[i_mode],f[i_out])
    out={s_:list(g.values()) for s_,g in groups.items()}
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
# ⛔⭐ AN XFAIL COUNTS AS A FAIL, SO A SUITE CARRYING ONE IS NOT DONE (ceo CEO-416, 2026-09-08,
# on Lon's own FACT RULE of 2026-09-03: "there is no such thing now as XFAIL. We are shooting for 100%").
# THE DEFECT THIS CLOSES, and the coo walked into it before the ruling: the SNOBOL4 master row read
# 1894/1894 FAIL=0 and this banner printed it "done", while 27 known-red entries sat OUTSIDE BOTH SIDES
# of that fraction. Dropping a red from the numerator AND the denominator renders it as if it did not
# exist -- wrong in the flattering direction, on the row Lon's 100% question gets answered from.
#
# ⛔ THE COUNT IS A UNION OF THREE SPELLINGS, NEVER A SUM. An xfail is spelled three ways -- ALL.csv's
# `xfail` column, banner lines in ALL.xfail, and per-entry *.xfail marker files -- and adding them
# double-counts: snobol4's ALL.xfail holds 54 LINES for 27 ENTRIES (a banner line plus a prose line
# each), naming the same 27 the CSV column names. MEASURED by the coo across all seven masters
# 2026-09-08: snobol4 csv 27 and ALL.xfail 27 overlapping 27 of 27; icon 20 markers only; raku 156,
# snocone 16, rebus 4, all csv-only; prolog and pascal 0. Six of the seven use a SINGLE spelling, so
# no overlap is possible there -- which is why the union is safe to take and the sum is not.
# ⛔ AN UNREADABLE CORPUS RETURNS None AND IS SAID ALOUD, NEVER 0: a census that cannot see its
# population must never print the success shape. That is the whole instrument law in one return value.
_XF_CACHE = {}
def xfail_by_lang(lang):
    """Distinct xfail ENTRIES for a master language: union of the three spellings, or None if unreadable."""
    if lang in _XF_CACHE: return _XF_CACHE[lang]
    import csv as _csv, glob as _glob
    d = os.path.join(os.path.dirname(os.path.abspath(TSV)), '..', 'corpus', 'tests', lang)
    d = os.path.normpath(d)
    if not os.path.isdir(d):
        _XF_CACHE[lang] = None; return None
    names = set()
    try:
        c = os.path.join(d, 'ALL.csv')
        if os.path.exists(c):
            with open(c, newline='', encoding='utf-8', errors='replace') as f:
                r = _csv.reader(f); hdr = next(r)
                if 'xfail' in hdr:
                    i = hdr.index('xfail')
                    for row in r:
                        if len(row) > i and row[i].strip() == '1': names.add(row[1])
        x = os.path.join(d, 'ALL.xfail')
        if os.path.exists(x):
            for l in open(x, encoding='utf-8', errors='replace'):
                m = re.match(r'^\*-+\s+\d+\s+(\S+)\s+XFAIL\s*$', l.rstrip('\n'))
                if m: names.add(m.group(1))
        for f in _glob.glob(os.path.join(d, '*.xfail')):
            if not f.endswith('ALL.xfail'): names.add(os.path.basename(f)[:-6])
    except Exception:
        _XF_CACHE[lang] = None; return None
    _XF_CACHE[lang] = len(names)
    return len(names)
def eta(r,today):
    """MEASURED MOVEMENT, NEVER A PROJECTION (Lon 2026-09-12 15:0x CDT, in-chat to cfo, verbatim: "I see that in your
    grid you will deliver some yesterday. Hmm?" -- the cells read "-> 09-12" on 09-12: a date computed as
    today + remaining/rate, i.e. an extrapolation, and one that could land in the past).  The economy rule of this
    seat is measured never projected, and a banner Lon reads is the last place a projection belongs.  What a cell
    can state is what was MEASURED: two readings of the same population and their difference.  Returns
    ('MOVE', (delta, basis_date)) where delta = today_pass - the earlier reading on the same criterion (the first
    reading, or the like-for-like basis when the criterion changed), or DONE / XFAIL / XFUNKNOWN / NEW / NOROWS /
    ONEDAY / NORUNNER exactly as before.  Nothing here is a rate, an ETA, or a curve."""
    if r['today_pass'].strip()=='' or r['today_date'].strip()=='': return 'NORUNNER',None
    fp,ft,tp,tt=int(r['first_pass']),int(r['first_total']),int(r['today_pass']),int(r['today_total'])
    rem=tt-tp
    if rem<=0:
        # CEO-416: a master carrying xfails is NOT done however the fraction reads (see xfail_by_lang).
        if 'master' in r['key']:
            xf = xfail_by_lang(r['lang'])
            if xf is None: return 'XFUNKNOWN', None
            if xf > 0:     return 'XFAIL', xf
        return 'DONE',None
    # ⭐ A RE-CRITERIONED ROW IS COMPARED, NOT EXCUSED (Lon 2026-09-08): likeforlike() reads the progress table on a
    # fixed population, so the movement is real; only a suite the table cannot see falls through to NOROWS/ONEDAY.
    if recriterioned(r):
        L=likeforlike(r)
        if not L: return ('NOROWS' if lfl_why(r)=='norows' else 'ONEDAY'),None
        return 'MOVE', (L['now']-L['then'], L['basis'])
    days=(d(r['today_date'])-d(r['first_date'])).days
    if days<=0: return 'NEW',None
    return 'MOVE', (tp-fp, r['first_date'])
def xfail_annotation(r, k):
    """The one sentence a master row carrying xfails must show when eta() is NOT already saying it.
    Returns '' for a non-master, an unreadable census, a zero count, or k=='XFAIL' (which says it itself)."""
    if k in ('XFAIL', 'XFUNKNOWN') or 'master' not in r['key']: return ''
    xf = xfail_by_lang(r['lang'])
    if not xf: return ''
    gap = int(r['today_total']) - int(r['today_pass'])
    same = ' — the whole gap' if gap == xf else f' of a {gap}-wide gap'
    return (f"{xf} xfail counted as FAIL{same} (CEO-416): they are in the denominator and not the "
            f"numerator, so this row can only close by CURING them, never by re-captioning")
# ⛔⛔⛔ THE PRINTED SUITE BANNER IS DELETED (Lon 2026-09-13, in-chat to hq_S, verbatim: "See that banner you
# just output. The header says suite pass/tot gap date state. Delete whatever produced that. I want it gone.
# I've ordered that removed." and, when the first cut took only the header row: "I want the entire text gone.
# Not just the header.").  banner() and grid() -- the two functions that rendered that table to STDOUT -- are
# GONE, and so is the dispatch that called them, so a no-arg run of this script now prints NOTHING and exits 0.
# ⛔ DO NOT RE-ADD A DISPLAY PATH HERE.  What survives is FILE WRITING ONLY: --set writes one SUITES.tsv row and
# re-renders that row in SCORE.md, --render and --md return the table TEXT for SCORE.md.  Those are the ONE
# LEADERBOARD Lon ordered kept ("so whenever we want to know the state it is there not an hour away of running
# tests") -- a file a reader opens on purpose, which is the opposite of text printed at someone every turn.
def md():
    head,rows=load(); today=dt.date.today(); DEF=deferred_rows()
    print('| suite | lang | result | graded | tree | state |'); print('|---|---|---|---|---|---|')
    for r in rows:
        k,e=eta(r,today)
        if k=='NORUNNER':
            why=r['criterion_changed'].split(':',1)[-1] if r['criterion_changed'] else 'no runner yet'
            dfr=DEF.get(r['key'])
            if dfr:
                # ⛔ DEFERRED PRINTS ITS RULING AND THE WORK IT WAITS ON, every time, because that is condition 3
                # of ARCH-PROGRAM-LEDGER § DEFERRED: a deferral that stops naming what it waits on has become an
                # abandonment, and nothing on the board would say so.
                # ⛔ THE RULING'S OWN TEXT IS DATA IN A MARKDOWN TABLE, so every `|` in it becomes `·`. Measured:
                # gnu_fd's waiting_on names the grep proving the substrate is absent (attr_var·put_attr·coroutin)
                # and those three pipes turned one 7-field row into nine -- the table stops parsing for every
                # reader downstream. ⭐ SUBSTITUTED, NOT BACKSLASH-ESCAPED: `\\|` satisfies a markdown renderer
                # and NOT an instrument that splits the row on '|', and the instruments are the harder reader.
                _w=dfr['waiting_on'][:400].replace('|','·'); _b=dfr['ruled_by'].replace('|','·')
                print(f"| {r['nick']} | {r['lang']} | -/{r['today_total']} ({dfr['count']} DEFERRED, not counted as failures) | never graded | - | DEFERRED by Lon ({_b}), IN SCOPE AND NOT A FAILURE - waiting on: {_w} |")
            else:
                print(f"| {r['nick']} | {r['lang']} | -/{r['today_total']} (vendored, no runner yet) | never graded | - | NO RUNNER, NO READING: {why} - a population with no grader is a debt on the board, never an absence from it |")
            continue
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
        named={'DONE':'done','XFAIL':f'{e} xfail=fail','XFUNKNOWN':'xfail unreadable'}
        tail=named[k] if k in named else ''
        # ⭐ AND THE CONVENTION IS STATED WHEREVER THE ROW IS READ, not only when the fraction closes.
        # eta() can only return 'XFAIL' when pass==total, so the moment a master row is corrected to the
        # honest 1871/1898 the xfail count VANISHES from the cell -- the reader then sees a 27-wide gap with
        # no way to know it IS the known-red set rather than 27 unmeasured entries. Four masters were in
        # exactly that state and said nothing (SnoM 27, RakM 156, SncM 16, RebM 4).
        # (ceo ruling to the coo, 2026-09-08: "Set it, state the convention in the cell.")
        xa = xfail_annotation(r, k)
        if xa: tail = (tail + ' · ' if tail else '') + xa
        _ago=(today-d(r['today_date'])).days; _age='today' if _ago==0 else ('yesterday' if _ago==1 else f'{_ago} days ago')
        # the CEO-749 shape: OUTSIDE named in the same row -- the last OUTSIDE=N token of the row's own criterion stamp (coo 2026-09-16,
        # row util-suite-banner-render-rewrites-rows-a-seat-did-not-measure-and-there-is-no-check-mode-that-writes-nothing: a render
        # used to drop a hand-written OUTSIDE clause, hq_raku measured SnoM 1961/1980 OUTSIDE=8 rendered to a plain 1961/1980)
        _ot=re.findall(r'OUTSIDE=(\d+)', r.get('criterion_changed') or '')
        _res=f"{r['today_pass']}/{r['today_total']}" + (f" OUTSIDE={_ot[-1]}" if _ot else "")
        print(f"| {r['nick']} | {r['lang']} | {_res} | {r['today_date']} ({_age}) | `{r['tree']}` | {tail} |")
SCORE=os.environ.get('S4E_SCORE_MD') or os.path.join(os.path.dirname(os.path.abspath(TSV)),'SCORE.md')
def md_lines():
    import io, contextlib
    buf=io.StringIO()
    with contextlib.redirect_stdout(buf): md()
    return buf.getvalue().rstrip('\n').split('\n')
_NICK2KEY=None
def _row_key(line):
    """The suite key a rendered markdown row belongs to: the row names the suite by its NICKNAME only (Lon
    2026-09-12: one name, not the nickname and the key), and the nickname resolves to the key through SUITES.tsv.
    None for the header and separator rows, and for any first cell that is not a nickname on file."""
    global _NICK2KEY
    if _NICK2KEY is None:
        _head,_rows=load(); _NICK2KEY={r['nick']:r['key'] for r in _rows}
    m = re.match(r'^\|\s*([^|]+?)\s*\|', line)
    return _NICK2KEY.get(m.group(1)) if m else None
def check_table():
    """--check: every suite-table row where SCORE.md and a fresh render from SUITES.tsv DISAGREE, printed side by side, WRITING
    NOTHING. rc 1 on a disagreement, 0 when the table agrees (population printed), 2 when the table cannot be found. The batch
    audit runs this every tick; a seat verifying after a rebase runs this, never --render (hq_raku 2026-09-16: --render as a
    verification step rewrote Zona, Jcon and SnoM rows it never measured, twice, and the only way to ask whether the files agreed
    was the command that made them agree)."""
    if not os.path.exists(SCORE):
        print(f"REFUSE(rc=2): {SCORE} missing beside the TSV"); return 2
    L=open(SCORE,encoding='utf-8').read().split('\n')
    hdr=[i for i,l in enumerate(L) if l.startswith('| suite | lang |')]
    if len(hdr)!=1:
        print(f"REFUSE(rc=2): {len(hdr)} '| suite | lang |' header(s) in {SCORE}, expected exactly one"); return 2
    st=hdr[0]; en=st
    while en<len(L) and L[en].startswith('|'): en+=1
    fresh={_row_key(l):l for l in md_lines() if _row_key(l)}
    cur={_row_key(l):l for l in L[st:en] if _row_key(l)}
    diff=[k for k in cur if k in fresh and cur[k]!=fresh[k]]
    only_score=[k for k in cur if k not in fresh]; only_tsv=[k for k in fresh if k not in cur]
    n=len(cur)
    for k in diff:
        print(f"DISAGREE {k}:"); print(f"  SCORE.md : {cur[k]}"); print(f"  SUITES.tsv renders: {fresh[k]}")
    for k in only_score: print(f"DISAGREE {k}: in SCORE.md's table, no SUITES.tsv row renders it")
    for k in only_tsv: print(f"DISAGREE {k}: SUITES.tsv row with no SCORE.md table row")
    bad=len(diff)+len(only_score)+len(only_tsv)
    print(f"population: {n} table row(s) checked against SUITES.tsv; {bad} disagree; nothing written")
    if bad:
        print("  a display row is rewritten only by the seat that measured it: util_suite_banner.py --render --only <key>  (or the runner's own write); --render --all-rows rewrites every row from the local TSV and is a different act")
        return 1
    print(f"CHECK OK: SCORE.md's suite table agrees with SUITES.tsv on all {n} rows")
    return 0
def render_table(only_key=None):
    """Re-render SCORE.md § THE SUITE TABLE (the rows under the '| suite | lang |' header) from SUITES.tsv, in place.
    Returns a one-line note; never silent, never a guess: a table it cannot find is said NOT rendered.

    ⛔⭐ only_key SCOPES THE WRITE TO THE ONE ROW THE CALLER ACTUALLY MEASURED, and `--set` always passes it
    (coo 2026-09-08, on hq_P's measured report; the unscoped re-render below was the coo's own 2026-09-06
    change and this is its correction). THE DEFECT: this function rebuilt EVERY row from the LOCAL
    SUITES.tsv, so a seat measuring one suite rewrote the display cells of suites its run never touched --
    with whatever its local TSV happened to hold. When that TSV was behind origin, the write was a SILENT
    REVERT of another seat's newer number, landing inside a commit whose message truthfully described
    something else entirely. hq_P measured it happening twice in one evening: their tree held
    `Budne 64/93 (0bd961e07)` while origin already held `Budne 66/93 (251693227)`, and only a rebase
    conflict caught it -- `git add -A` after a board would have pushed the revert silently.
    ⛔ The blast radius was the WHOLE TABLE and the trigger was ordinary: run any board, commit normally.
    A row nobody measured this session is left BYTE-IDENTICAL now, which is also what makes a genuine
    disagreement surface as a conflict instead of resolving itself in the wrong direction.
    `--render` keeps the unscoped whole-table behaviour, because asking for it explicitly is a different
    act from a board run doing it as a side effect nobody typed."""
    if not os.path.exists(SCORE):
        return f"⚠ suite table NOT rendered: {SCORE} missing beside the TSV (SUITES.tsv is set; the markdown table reads STALE until a renderer runs)"
    L=open(SCORE,encoding='utf-8').read().split('\n')
    hdr=[i for i,l in enumerate(L) if l.startswith('| suite | lang |')]
    if len(hdr)!=1:
        return f"⚠ suite table NOT rendered: {len(hdr)} '| suite | lang |' header(s) in {SCORE}, expected exactly one"
    st=hdr[0]; en=st
    while en<len(L) and L[en].startswith('|'): en+=1
    new=md_lines(); old=L[st:en]
    scope=""
    if only_key is not None:
        fresh={_row_key(l):l for l in new if _row_key(l)}
        if only_key not in fresh:
            return f"⚠ suite table NOT rendered: no rendered row for suite key {only_key!r} (SUITES.tsv is set; the markdown row reads STALE)"
        merged=[fresh[only_key] if _row_key(l)==only_key else l for l in old]
        if only_key not in {_row_key(l) for l in old}: merged.append(fresh[only_key])
        new=merged
        scope=f" (scoped to {only_key}; rows for suites this run did not measure left byte-identical)"
    changed=sum(1 for a,b in zip(old,new) if a!=b)+abs(len(old)-len(new))
    if changed==0: return "suite table: SCORE.md § THE SUITE TABLE already matches SUITES.tsv (0 rows changed)%s" % scope
    L[st:en]=new; open(SCORE,'w',encoding='utf-8').write('\n'.join(L))
    return f"suite table: SCORE.md § THE SUITE TABLE re-rendered from SUITES.tsv in the same call ({changed} row(s) changed){scope}"
def grid(plain=False):
    """THE SUITE SCORE GRID (Lon 2026-09-13, in-chat to cfo, verbatim, in order: "And a grid of the test suite
    scores." - "Ensure a grid is output not text from the shell script." - "No, the grid must not be text." -
    "I want a excel type grid with lines and cells." - "I mean border lines." - "make it smaller." - "Take the
    grid you had and make it smaller.").
    SCORE IS TWO COLUMNS, Pass and Total (Lon 2026-09-13: "break out score into two columns."), so both
    numbers right-align in their own cell and a reader can compare denominators down the column instead of
    parsing a slash out of a string.
    LANG IS THE FIRST COLUMN (Lon 2026-09-13: "Put lang column first."), which is also the sort key, so the
    column a reader scans and the order the rows are in are the same thing.
    ROWS ARE ORDERED BY LANG, THEN BY SUITE NAME (Lon 2026-09-13: "Put rows in order by lang and then suite
    name."). The TSV's own order is custody order, which is not a reading order.
    ONE SUITE PER ROW with its own columns, which is the grid Lon kept -- made SMALLER by spending less on
    whitespace and rules rather than by re-laying it out: cells are padded by one column instead of two, and
    the rule between every data row is gone, keeping the outer border and the header rule. 24 suites go from
    51 lines to 28 and the width drops with it. Widths come from dw(), this file's display-width authority."""
    head,rows=load()
    data=[]
    for r in rows:
        try: tp,tt=int(r['today_pass']),int(r['today_total'])
        except (ValueError,KeyError): continue
        # ⛔ `.0f` alone rounds 823/826 (99.64%) up to "100%" while the State column beside it correctly
        # reads not-DONE (tp<tt) -- a contradiction inside one row (Lon 2026-09-23, caught reading this
        # exact grid). 100% is reserved for tp>=tt (RULES.md: "100% only when FAIL=0 over the printed
        # denominator"); clamp a short suite's rounded display at 99% so it can never borrow that word.
        if not tt: pct="-"
        else:
            pv=round(100.0*tp/tt)
            if tp<tt and pv>=100: pv=99
            pct=f"{pv}%"
        data.append([r.get('lang',''), r['nick'], f"{tp}", f"{tt}", pct, "DONE" if tt and tp>=tt else ""])
    data.sort(key=lambda r: (r[0].lower(), r[1].lower()))
    if not data:
        print("SUITE GRID: no readable rows in SUITES.tsv"); return
    hdr=["Lang","Suite","Pass","Total","Pct","State"]
    cols=len(hdr)
    # ⭐ ONE EXTRA COLUMN OF ROOM PER CELL (Lon 2026-09-13: "Give one extra space in each column to give room
    # to breath."). Added to the WIDTH, so the rules that span each column widen with it and the box still
    # closes; pad() and rpad() then place the slack on the correct side -- left of a right-justified number,
    # right of a left-justified name -- which is why this is one number here and not a space glued onto a cell.
    w=[max(dw(hdr[c]), max(dw(r[c]) for r in data)) + 1 for c in range(cols)]
    def rule(l,m,rr): return l + m.join("\u2500"*(w[c]) for c in range(cols)) + rr
    NUM={2,3,4}   # Pass, Total, Pct -- the numeric cells, right-justified; Lang/Suite/State stay left.
    def line(cs, hdr_row=False):
        # ⭐ THE EXTRA COLUMN IS A TRAILING SPACE ON EVERY CELL, not slack handed to the justifier. Give it to
        # rpad() instead and a right-justified number lands FLUSH AGAINST THE RIGHT BORDER with the gap on its
        # far side, which is the opposite of room to breathe. So each cell is justified into w-1 and then gets
        # one space: names breathe on the right, numbers breathe on the right, and the columns still line up.
        def cell(c):
            j = rpad if (c in NUM and not hdr_row) else pad
            return j(cs[c], w[c]-1) + " "
        return "\u2502" + "\u2502".join(cell(c) for c in range(cols)) + "\u2502"
    done=sum(1 for r in data if r[5]=="DONE")
    print(rule("\u250c","\u252c","\u2510"))
    print(line(hdr, hdr_row=True))
    print(rule("\u251c","\u253c","\u2524"))
    for r in data: print(line(r))
    print(rule("\u2514","\u2534","\u2518"))
    print(f"{len(data)} suites, {done} at 100%")
# ⭐ THE README'S SUITE TABLE IS GENERATED FROM THIS RECORD, NEVER TYPED (Lon 2026-09-23 16:2x, in-chat to the ceo: "We want the
# test suite numbers and the benchmark numbers in the README."; CEO-1216; row instruments-the-readme-suite-table-is-written-from-the-
# suite-table-and-a-gate-holds-it-current, the coo). SCRIP/README.md read the leaderboard "on 2026-09-07" sixteen days later -- Gimpel
# 104/127 against 127/132, IPL 75/89 against 194/194 -- because a hand-kept copy has no writer. --readme renders the block between two
# marker lines from SUITES.tsv and stamps the .github commit it read (the PIN); --readme-check [--pinned] holds it: --pinned proves the
# block is exactly the render of SUITES.tsv AT ITS PIN (a hand edit or a corrupted cell reds, and it never flaps), the full check also
# proves every row matches SUITES.tsv as it stands now (the currency the other repo moves about fifty times a day, so it can lag).
# Raku is labelled IN DEVELOPMENT on Lon's word (CEO-1219) and no other language carries a label.
README_BEGIN = '<!-- SUITE-TABLE:BEGIN'
README_END = '<!-- SUITE-TABLE:END -->'
README_LANGS = [('snobol4', 'SNOBOL4'), ('icon', 'Icon'), ('prolog', 'Prolog'), ('pascal', 'Pascal'), ('raku', 'Raku'),
                ('snocone', 'Snocone'), ('rebus', 'Rebus')]
README_IN_DEVELOPMENT = {'raku'}
README_HEAD_N = 8   # the BEGIN line, four prose lines, a blank, the table header and its rule -- rows start here
README_RUNNER = {
    'gimpel': 'test_snobol4_gimpel_suite.sh', 'csnobol4': 'test_snobol4_csnobol4_suite.sh', 'snoflake': 'test_snoflake_suite.sh',
    'aisnobol': 'test_snobol4_aisnobol_suite.sh', 'dotnet': 'test_snobol4_dotnet_suite.sh',
    'testpgms': 'test_snobol4_spitbol_testpgms_suite.sh', 'x64tests': 'test_snobol4_spitbol_x64_suite.sh',
    'arizona': 'test_icon_arizona_suite.sh', 'jcon': 'test_icon_jcon_suite.sh', 'ipl': 'test_icon_ipl_suite.sh',
    'inria': 'test_prolog_inria_suite.sh', 'swi': 'test_prolog_swi_suite.sh', 'gnu': 'test_prolog_gnu_suite.sh',
    'logtalk': 'test_prolog_logtalk_suite.sh', 'fpc': 'test_pascal_fpc_suite.sh', 'pat': 'test_pascal_pat_suite.sh',
    'roast': 'raku_roast_scoreboard.sh --run', 'sno-master': 'test_corpus_snobol4.sh', 'icn-master': 'board_icon_master.sh',
    'pl-master': 'corpus_suite_harness.py run tests/prolog/ALL.pl', 'pas-master': 'corpus_suite_harness.py run tests/pascal/ALL.pas',
    'raku-master': 'corpus_suite_harness.py run tests/raku/ALL.raku', 'snc-master': 'corpus_suite_harness.py run tests/snocone/ALL.sc',
    'reb-master': 'corpus_suite_harness.py run tests/rebus/ALL.reb'}
def _readme_path():
    root = os.environ.get('S4E_HOME') or os.path.join(HERE, '..', '..')
    return os.path.join(root, 'SCRIP', 'README.md')
def _rows_from_text(text):
    rows=[]; head=None
    for l in text.split('\n'):
        if l.startswith('#') or not l.strip(): continue
        f=l.split('\t')
        if head is None: head=f; continue
        rows.append(dict(zip(head,f)))
    return rows
def readme_block(rows, pin):
    """The generated block, markers included. Refuses (SystemExit 2) on a suite with no runner named or a language it cannot place."""
    known = dict(README_LANGS)
    for r in rows:
        if r['key'] not in README_RUNNER:
            sys.stderr.write(f"REFUSE(rc=2): SUITES.tsv row {r['key']!r} has no runner named in README_RUNNER -- a README row must say what produced it\n"); sys.exit(2)
        if r.get('lang') not in known:
            sys.stderr.write(f"REFUSE(rc=2): SUITES.tsv row {r['key']!r} has language {r.get('lang')!r}, which the README does not place\n"); sys.exit(2)
    out = [f"{README_BEGIN} generated by .github/scripts/util_suite_banner.py --readme from .github/SUITES.tsv at .github@{pin} -- do not edit by hand; scripts/test_gate_readme_suite_table_matches_suites_tsv.sh holds it -->",
           "Every row is generated from the leaderboard's machine record, `.github/SUITES.tsv` (the SUITE TABLE of `.github/SCORE.md`),",
           "never typed by hand: the suite's latest reading, written by that suite's own runner in the landing that measured it, with the",
           "SCRIP tree and the day it was measured. A program counts only when it passes in BOTH modes. The seven masters are our own flat",
           "suites with refs cut from each oracle; the others are vendored third-party suites. Raku is IN DEVELOPMENT: its rows stand as measured.",
           "",
           "| Language | Suite | passing / graded (both modes, the AND per program) | tree | measured | runner |",
           "|---|---|---|---|---|---|"]
    for lang, name in README_LANGS:
        mine = [r for r in rows if r.get('lang') == lang]
        mine = [r for r in mine if not r['key'].endswith('-master')] + [r for r in mine if r['key'].endswith('-master')]
        label = name + (' — IN DEVELOPMENT' if lang in README_IN_DEVELOPMENT else '')
        for r in mine:
            suite = r['nick'] + (' (master)' if r['key'].endswith('-master') else '')
            p_, t_ = (r.get('today_pass') or '').strip(), (r.get('today_total') or '').strip()
            cell = f"**{p_}/{t_}**" if p_ and t_ else "not graded"
            tree = (r.get('tree') or '').strip()
            out.append(f"| {label} | {suite} | {cell} | {('`' + tree + '`') if tree else ''} | {(r.get('today_date') or '').strip()} | `{README_RUNNER[r['key']]}` |")
    out.append(README_END)
    return out
def _readme_split(path):
    L = open(path, encoding='utf-8').read().split('\n')
    b = [i for i, l in enumerate(L) if l.startswith(README_BEGIN)]
    e = [i for i, l in enumerate(L) if l == README_END]
    if len(b) != 1 or len(e) != 1 or e[0] < b[0]:
        return L, None, None
    return L, b[0], e[0]
def _suites_pin():
    gh = os.path.dirname(os.path.abspath(TSV))
    dirty = subprocess.run(['git', '-C', gh, 'status', '--porcelain', '--', os.path.basename(TSV)], capture_output=True, text=True)
    if dirty.returncode != 0:
        return None, f"cannot read git state of {gh}: {dirty.stderr.strip()}"
    if dirty.stdout.strip():
        return None, f"{TSV} has uncommitted changes -- commit the row first; a README must name a state anyone can re-read"
    h = subprocess.run(['git', '-C', gh, 'log', '-1', '--format=%h', '--', os.path.basename(TSV)], capture_output=True, text=True)
    return (h.stdout.strip() or None), (None if h.stdout.strip() else "no commit touches SUITES.tsv")
def readme_write(path):
    pin, why = _suites_pin()
    if not pin:
        sys.stderr.write(f"REFUSE(rc=2): --readme: {why}\n"); return 2
    L, b, e = _readme_split(path)
    if b is None:
        sys.stderr.write(f"REFUSE(rc=2): --readme: {path} needs exactly one '{README_BEGIN} ...' line and one '{README_END}' line after it\n"); return 2
    _h, rows = load()
    new = readme_block(rows, pin)
    if L[b:e + 1] == new:
        print(f"README suite table: already the render of SUITES.tsv at .github@{pin} (0 lines changed)"); return 0
    L[b:e + 1] = new
    open(path, 'w', encoding='utf-8').write('\n'.join(L))
    print(f"README suite table: rendered {len(new) - README_HEAD_N - 1} row(s) from SUITES.tsv at .github@{pin} into {path}"); return 0
def readme_check(path, pinned_only=False):
    """rc 0 the block is exactly its pin's render (and, unless pinned_only, every row matches SUITES.tsv now); 1 a cell differs; 2 unmeasurable."""
    if not os.path.exists(path):
        print(f"README-CHECK REFUSED(2): no README at {path}"); return 2
    L, b, e = _readme_split(path)
    if b is None:
        print(f"README-CHECK RED(1): {path} carries no single generated block ({README_BEGIN} ... {README_END}) -- the table is not generated"); return 1
    m = re.search(r'at \.github@([0-9a-f]{7,40}) ', L[b])
    if not m:
        print(f"README-CHECK RED(1): the block's first line names no .github@<commit> pin -- nobody can re-read what it was rendered from"); return 1
    pin = m.group(1); gh = os.path.dirname(os.path.abspath(TSV))
    old = subprocess.run(['git', '-C', gh, 'show', f'{pin}:{os.path.basename(TSV)}'], capture_output=True, text=True)
    if old.returncode != 0:
        print(f"README-CHECK REFUSED(2): the pin .github@{pin} is not in {gh}'s history -- pull .github, then re-check"); return 2
    got = L[b:e + 1]
    want = readme_block(_rows_from_text(old.stdout), pin)
    bad = [(i, g, w) for i, (g, w) in enumerate(zip(got, want)) if g != w] + ([(-1, f'{len(got)} lines', f'{len(want)} lines')] if len(got) != len(want) else [])
    if bad:
        print(f"README-CHECK RED(1): {len(bad)} line(s) of the README block are not the render of SUITES.tsv at its pin .github@{pin} -- a hand edit or a corrupted cell:")
        for i, g, w in bad[:10]: print(f"    README:   {g}\n    RENDERED: {w}")
        return 1
    print(f"README-CHECK PINNED OK: the block is exactly the render of SUITES.tsv at .github@{pin} ({len(got) - README_HEAD_N - 1} rows)")
    if pinned_only: return 0
    _h, rows = load()
    cur = readme_block(rows, pin)
    lag = [(g, w) for g, w in zip(got[README_HEAD_N:-1], cur[README_HEAD_N:-1]) if g != w] + ([('(row count)', f'{len(got)} vs {len(cur)} lines')] if len(got) != len(cur) else [])
    if lag:
        print(f"README-CHECK RED(1): {len(lag)} README row(s) lag SUITES.tsv as it stands now (the block reads .github@{pin}) -- regenerate: python3 .github/scripts/util_suite_banner.py --readme")
        for g, w in lag[:12]: print(f"    README: {g}\n    NOW:    {w}")
        return 1
    print(f"README-CHECK CURRENT OK: every README row matches SUITES.tsv as it stands now")
    return 0
def main(a):
    if '--readme' in a:
        j=a.index('--readme'); path=a[j+1] if len(a)>j+1 and not a[j+1].startswith('-') else _readme_path()
        sys.exit(readme_write(path))
    if '--readme-check' in a:
        j=a.index('--readme-check'); path=a[j+1] if len(a)>j+1 and not a[j+1].startswith('-') else _readme_path()
        sys.exit(readme_check(path, pinned_only=('--pinned' in a)))
    if '--set' in a:
        # ⛔ THE CRITERION STAMP (coo 2026-09-16, CEO-785; row instruments-util-score-row-cannot-stamp-a-criterion-change-so-
        # every-denominator-move-is-hand-edited-or-unstamped): `--criterion-changed '<YYYY-MM-DD>:<reason in words>'` APPENDS
        # to column 12 (criterion_changed) with the ' | ' separator the column already uses, and a --set whose TOTAL differs
        # from the row's previous today_total REFUSES rc=2 without it -- a denominator move without its stamp is the
        # dishonest-denominator class of CEO-546, and until today the only way to stamp one was a hand edit (the coo's Budne
        # stamp of 09-13, .github 11de13f9) or none at all (hq_pascal's PAT instrument change, SCRIP fe37edc72, 284 -> 296).
        stamp=None
        if '--criterion-changed' in a:
            j=a.index('--criterion-changed')
            if len(a)<=j+1 or not re.match(r'^\d{4}-\d{2}-\d{2}:\S', a[j+1]):
                sys.stderr.write("REFUSE(rc=2): --criterion-changed takes '<YYYY-MM-DD>:<reason in words>' (the day the criterion moved, a colon, then why)\n"); sys.exit(2)
            stamp=a[j+1]; a=a[:j]+a[j+2:]
        i=a.index('--set'); key,p,t=a[i+1],a[i+2],a[i+3]; date=a[i+4] if len(a)>i+4 and not a[i+4].startswith('-') else dt.date.today().isoformat(); tree=a[i+5] if len(a)>i+5 and not a[i+5].startswith('-') else None
        head,rows=load(); r=next((x for x in rows if x['key']==key),None)
        if r is None: sys.exit(f"REFUSE: no suite key {key}")
        prev=(r.get('today_total') or '').strip()
        if prev and str(t).strip()!=prev and not stamp:
            sys.stderr.write(f"REFUSE(rc=2): {key}'s denominator moves {prev} -> {t} and no --criterion-changed '<YYYY-MM-DD>:<reason>' names why. "
                             f"A denominator move without its stamp is the dishonest-denominator class (CEO-546, CEO-749): pass the stamp, or keep the total. "
                             f"NOTHING WAS WRITTEN.\n"); sys.exit(2)
        r['today_pass'],r['today_total'],r['today_date']=p,t,date
        if tree: r['tree']=tree
        if stamp:
            cur=(r.get('criterion_changed') or '').strip()
            r['criterion_changed']=(cur+' | '+stamp) if cur else stamp
        before=open(TSV,encoding='utf-8').read()
        save(head,rows)
        try:
            note=render_table(only_key=key)
        except Exception as ex:
            open(TSV,'w',encoding='utf-8').write(before)      # ⛔ the two sites move together or not at all
            sys.exit(f"REFUSE(rc=2): the row was NOT set. Rendering SCORE.md raised {type(ex).__name__}: {ex}. "
                     f"SUITES.tsv has been RESTORED to what it held before this call, because a written TSV "
                     f"beside an unwritten SCORE.md is the split state every board reader then has to guess at.")
        print(note)
    if '--check' in a: sys.exit(check_table())
    if '--render' in a:
        # ⛔ --render REWRITES EVERY ROW FROM THE LOCAL TSV: a different act from verifying, so it is asked for by name -- --all-rows,
        # or scoped to the one row the caller measured with --only KEY (coo 2026-09-16, hq_raku's finding).
        if '--only' in a:
            j=a.index('--only'); k=a[j+1] if len(a)>j+1 else ''
            head,rows=load()
            if k not in {r['key'] for r in rows}: sys.stderr.write(f"REFUSE(rc=2): --only {k!r} is no SUITES.tsv key\n"); sys.exit(2)
            print(render_table(only_key=k)); return
        if '--all-rows' not in a:
            sys.stderr.write("REFUSE(rc=2): --render rewrites EVERY suite-table row of SCORE.md from the local SUITES.tsv, rows you never measured included. "
                             "To verify, run --check (writes nothing). To rewrite one row you measured: --render --only <key>. To rewrite them all, say so: --render --all-rows. NOTHING WAS WRITTEN.\n"); sys.exit(2)
        print(render_table()); return
    if '--md' in a: md(); return
    grid(plain='--plain' in a)
    return
# ⛔⭐ AN IMPORT MUST NEVER BE A COMMAND (hq_B 2026-09-13). This module is the tree's ONE display-width
# authority -- dw() -- so any consumer that wants it must import this file; util_fit_columns.py does exactly
# that. A bare `main(sys.argv[1:])` at module scope RUNS ON IMPORT WITH THE IMPORTER'S OWN ARGV, so a caller
# whose command line happens to carry --md or --render would print a table by importing a width helper, and
# --set would WRITE SUITES.tsv. ⚠ STATED HONESTLY: that is LATENT, not live -- today's only importer passes
# a bare width, and the 3.1-SECOND import stall this guard was originally measured against died with
# banner(), which Lon deleted. What is left is a loaded gun with nobody currently in front of it, and the
# guard costs one line. The CLI is unchanged: run as a script, __name__ IS "__main__" and main() still runs.
if __name__ == "__main__":
    main(sys.argv[1:])
