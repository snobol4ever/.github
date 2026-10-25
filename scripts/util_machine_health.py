#!/usr/bin/env python3
# util_machine_health.py -- WHAT IS LOADING THE MACHINE, BY PROCESS AND BY SEAT (Lon 2026-10-15 15:0x CDT, in-chat to the ceo, verbatim:
# "Why is the machine overloaded?" then "Why, as CEO, did you not know this already? Do you not check the machine health periodically?"; CEO-1796).
# The load average says THAT the box is busy, never WHO: at 15:04 it read 20 on 16 cores while three swipl oracle runs had burned ~95% of a core
# each for two hours under a "timeout 15" that never killed them (swipl ignores SIGTERM and no -k followed). This instrument samples /proc twice,
# one second apart, and prints:
#   MACHINE load=L1/L5/L15 cores=N busy_cores=B
#   SEAT <root> cpu=<cores>          (live CPU summed by the process's working directory under /home/claude_*, else tmp/other)
#   RUNAWAY pid=P seat=S cpu=C elapsed=E why=<reason> cmd=<head>   (a process to kill or chase)
# A RUNAWAY is (a) a child of `timeout` that has outlived its own limit plus its -k grace by over a minute (the oracle-leak class), or (b) any process
# other than a claude session or the desktop, busy above 50% of a core for over 30 minutes. rc 0 none, rc 1 at least one runaway, rc 2 /proc unreadable.
import os, sys, time, re
def procs():
    out = {}
    for d in os.listdir('/proc'):
        if not d.isdigit(): continue
        try:
            st = open('/proc/%s/stat' % d).read()
            rp = st.rindex(')'); f = st[rp + 2:].split()
            comm = st[st.index('(') + 1:rp]
            out[int(d)] = dict(ppid=int(f[1]), ticks=int(f[11]) + int(f[12]), start=int(f[19]), comm=comm)
        except Exception: continue
    return out
def args(pid):
    try: return open('/proc/%d/cmdline' % pid, 'rb').read().replace(b'\0', b' ').decode('utf-8', 'replace').strip()
    except Exception: return ''
def cwd(pid):
    try: return os.readlink('/proc/%d/cwd' % pid)
    except Exception: return ''
def seat_of(path):
    m = re.match(r'/home/claude_([a-z0-9_]+)', path or '')
    return m.group(1) if m else ('tmp' if (path or '').startswith('/tmp') else 'other')
try:
    hz = os.sysconf('SC_CLK_TCK'); up = float(open('/proc/uptime').read().split()[0]); cores = os.cpu_count() or 1
    la = open('/proc/loadavg').read().split()[:3]
    a = procs(); t0 = time.time(); time.sleep(1.0); b = procs(); dt = time.time() - t0
except Exception as e:
    print('⛔ REFUSED (rc=2): util_machine_health: /proc unreadable: %s' % e); sys.exit(2)
cpu = {p: max(0, b[p]['ticks'] - a[p]['ticks']) / hz / dt for p in b if p in a}
seat = {}
for p, c in cpu.items():
    if c > 0.02: seat[seat_of(cwd(p))] = seat.get(seat_of(cwd(p)), 0.0) + c
print('MACHINE load=%s/%s/%s cores=%d busy_cores=%.1f' % (la[0], la[1], la[2], cores, sum(cpu.values())))
for s, c in sorted(seat.items(), key=lambda x: -x[1]):
    if c >= 0.2: print('SEAT %-12s cpu=%.1f' % (s, c))
run = []
for p, info in b.items():
    el = up - info['start'] / hz
    c = cpu.get(p, 0.0)
    why = ''
    par = b.get(info['ppid'])
    if par and par['comm'] == 'timeout':
        m = re.search(r'timeout\s+(?:(?:-k|--kill-after)[ =]?(\S+)\s+)?(?:-s\s+\S+\s+)?(\d+(?:\.\d+)?)([smhd]?)\s', args(info['ppid']) + ' ')
        if m:
            unit = {'': 1, 's': 1, 'm': 60, 'h': 3600, 'd': 86400}[m.group(3)]
            lim = float(m.group(2)) * unit
            k = m.group(1)
            grace = float(re.sub(r'[smhd]$', '', k)) if k and re.match(r'^\d+(\.\d+)?[smhd]?$', k) else 0.0
            if el > lim + grace + 60: why = 'outlived-its-timeout-%gs%s' % (lim, '' if k else '-no-k')
    if not why and el > 1800 and c > 0.5 and info['comm'] not in ('claude', 'gnome-shell', 'gnome-terminal-', 'Xwayland', 'chrome', 'sublime_text') and not info['comm'].startswith('kworker') and os.path.basename(args(p).split(' ', 1)[0]) != 'claude':
        why = 'busy-%.0f-min' % (el / 60)
    if why: run.append((c, p, seat_of(cwd(p)), el, why, args(p)[:90]))
for c, p, s, el, why, cmd in sorted(run, reverse=True):
    print('RUNAWAY pid=%d seat=%s cpu=%.2f elapsed=%dm why=%s cmd=%s' % (p, s, c, el / 60, why, cmd))
print('MACHINE_HEALTH runaways=%d' % len(run))
sys.exit(1 if run else 0)
