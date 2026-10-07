#!/usr/bin/bash
# Lon runs it: ! /usr/bin/bash /home/claude_ceo/.github/scripts/free_tmp_finished_sessions.sh   (2026-10-07 17:2x: freed 31.7 GiB, /tmp 95% -> 38%)
# free_tmp_finished_sessions.sh -- /tmp emergency (Lon 2026-10-07 17:1x CDT): delete the Claude Code scratch dirs of FINISHED sessions under
# /tmp/claude-1000. Keeps every seat's live session (its newest transcript, and any session id on a running process) and any
# dir touched in the last hour. Prints the count and the bytes freed.
/usr/bin/df -h /tmp | /usr/bin/tail -1
/usr/bin/python3 - <<'PY'
import os, glob, time, shutil, subprocess, re
live=set()
for d in glob.glob('/home/satirical/.claude/projects/-home-claude-*'):
    js=sorted(glob.glob(d+'/*.jsonl'), key=os.path.getmtime, reverse=True)
    live |= {os.path.basename(j)[:-6] for j in js[:1]}
ps=subprocess.run(['/usr/bin/ps','-eo','args'],capture_output=True,text=True).stdout
live |= set(re.findall(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', ps))
def newest(p):
    m=os.lstat(p).st_mtime
    for r,ds,fs in os.walk(p):
        for x in ds+fs:
            try: m=max(m, os.lstat(os.path.join(r,x)).st_mtime)
            except OSError: pass
    return m
def du(p):
    r=subprocess.run(['/usr/bin/du','-sxb',p],capture_output=True,text=True).stdout.split()
    return int(r[0]) if r else 0
now=time.time(); freed=n=kept=0
for proj in glob.glob('/tmp/claude-1000/-home-claude-*'):
    for s in os.listdir(proj):
        p=os.path.join(proj,s)
        if not os.path.isdir(p) or os.path.islink(p): continue
        if s in live or now-newest(p) < 3600: kept+=1; continue
        b=du(p); shutil.rmtree(p, ignore_errors=True)
        if not os.path.exists(p): freed+=b; n+=1
print(f"deleted {n} finished-session scratch dirs, freed {freed/2**30:.1f} GiB; kept {kept} (live or touched in the last hour)")
PY
/usr/bin/df -h /tmp | /usr/bin/tail -1
