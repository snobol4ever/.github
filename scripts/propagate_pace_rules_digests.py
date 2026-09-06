#!/usr/bin/env python3
"""Append THE PACE RULES pointer (MASTER-PLAN sec THE FLEET-12 PLAN rules 5-10, THE 35 HOURS) to every seat, HQ and cto digest
(CLAUDE.md in each root), with a dated backup beside each. Idempotent: a digest already carrying the marker is skipped.
ceo 2026-09-06 on Lon: "Please go implement all your suggestions regarding doing your job properly. I expect that." (CEO-342)."""
import os,sys,datetime,shutil
MARK='THE PACE RULES (MASTER-PLAN'
stamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
para=f'''

## ⛔⭐ THE PACE RULES (MASTER-PLAN § THE FLEET-12 PLAN rules 5–10, .github `3ef62ca1`; PROTOCOL.md `e44c7319`; THE 35 HOURS `505d0064`) — appended {stamp} CDT by the ceo on Lon's order (CEO-342)

Lon 2026-09-06 15:1x, verbatim: *"Please go implement all your suggestions regarding doing your job properly. I expect that."* · 15:2x: *"Do not depend on cron."* · 15:2x: *"So when I say September 10th, it translates to 35 hours."* The rules, one line each — the plan file is sovereign: (5) ONE BOARD PER TREE — cite a clean board of your tree from the progress database instead of re-running it; never start a board another measurer is running on the same tree; never leave a board running when your sitting ends. (6) `done` runs the SNOBOL4 master arm for any codegen row (hq_B's row); until it lands the HQ runs it before `done`. (7) SEATS CURE ONE-PROGRAM FLIPS when the cure is LOCAL (one builtin, lexer/parser rule, fixture, ref or runtime helper, ONE file, the program as the DONE-WHEN, the suite board as the arm); a class goes up to the HQ by name; never a template, never the shared engine, never rank ≥ 6. (8) THE CLAUSE DATABASE FIRST for hq_C, hq_R, seats 08–10. (9) RECEIPTS GO TO THE BATON LEDGER; a telegram to the ceo or an HQ is ONE PARAGRAPH and is an ASK, a FLIP (`suite pass/total tree runner`) or a BLOCKER. (10) EVERY SUITE ROW MEASURED EVERY DAY WITHOUT CRON — the banner marks rows older than 24 h ⏳ STALE; a STALE row is a rank-0 measure pick in its lane. THE 35 HOURS: the September 10 announcement is 35 hours of USAGE from 2026-09-06 15:12 CDT — plan the next 35 hours, not four days.
'''
roots=[f'/home/claude{n:02d}' for n in range(1,13)]+[f'/home/claude_{h}' for h in 'BCPTUSIR']+['/home/claude_cto','/home/claude_coo']
done=[];skipped=[];refused=[]
for r in roots:
    p=os.path.join(r,'CLAUDE.md')
    if not os.path.isfile(p): refused.append((r,'no CLAUDE.md')); continue
    s=open(p,encoding='utf-8',errors='replace').read()
    if MARK in s: skipped.append(r); continue
    try:
        shutil.copy2(p,p+'.bak-'+datetime.datetime.now().strftime('%Y-%m-%d-%H%M')+'-pace-rules')
        open(p,'a',encoding='utf-8').write(para); done.append(r)
    except Exception as e: refused.append((r,str(e)[:60]))
print('written',len(done),'skipped',len(skipped),'refused',len(refused))
for r,e in refused: print('  REFUSED',r,e)
