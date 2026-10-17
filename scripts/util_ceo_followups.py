#!/usr/bin/env python3
# util_ceo_followups.py -- A ROW IS NOT DONE WHEN IT IS MINTED (Lon 2026-10-15 17:0x CDT, in-chat to the ceo, verbatim: "Why do you keep not
# completing work items? What then would be the purpose of making a work item? Do you see the problem, dummy?"; CEO-1803). The ceo minted
# rows and moved on: at 17:0x, 296 ceo-minted rows were open, 234 with batons untouched for four days or more, and CEO-1676's loop row had sat
# ASSIGNED and untouched since 10-11 under a criterion that read green while the work was absent. This instrument runs in the ceo's hook every
# turn and prints what the ceo must chase that turn:
#   FOLLOWUP stale=N held=M      (N claimed/assigned rows whose baton is untouched over 24 h; M seats holding more than two claims)
#   STALE <state> <age>h <topic>  (oldest first, at most 6)
#   HELD <seat> claims=<n>
# A seat counts only while MODE admits it (the bus's own s4e_mode_stands guard, read live); a stood-down seat's claims are kept in place
# by MODE and are summarised on the FOLLOWUP line, never chased.
# rc 0 nothing to chase, rc 1 something to chase, rc 2 the queue is unreadable.
import os, sys, time, collections
PO = '/home/resources/postoffice'
try:
    rows = [l.rstrip('\n').split('\t') for l in open(PO + '/QUEUE.tsv', encoding='utf-8') if l.strip() and not l.startswith('#')]
except Exception as e:
    print('⛔ REFUSED (rc=2): util_ceo_followups: %s' % e); sys.exit(2)
now = time.time(); stale = []; held = collections.Counter(); down = collections.Counter()
import subprocess
try: MODE = open(PO + '/MODE', encoding='utf-8').readline().strip()
except Exception: MODE = ''
_GUARD = 'PO="%s"; eval "$(sed -n "/^s4e_mode_stands()/,/^}/p" /home/claude_ceo/harness/scripts/s4e_msg.sh)"; _dr(){ return 1; }; s4e_mode_stands "$1" "$2"' % PO
_stand = {}
def standing(seat):
    if seat not in _stand:
        try: _stand[seat] = subprocess.run(['bash', '-c', _GUARD, '_', seat, MODE], capture_output=True, timeout=10).returncode == 0
        except Exception: _stand[seat] = False
    return _stand[seat]
for r in rows:
    if len(r) < 4: continue
    topic, st = r[1], r[3]
    if not (st.startswith('CLAIMED:') or st.startswith('ASSIGNED:')): continue
    seat = st.split(':', 1)[1]
    if not standing(seat): down[seat] += 1; continue
    held[seat] += 1
    try: age = (now - os.stat('%s/tasks/%s.task.md' % (PO, topic)).st_mtime) / 3600
    except OSError: continue
    if age > 24: stale.append((age, st, topic))
over = [(s, n) for s, n in held.items() if n > 2]
stale.sort(reverse=True)
print('FOLLOWUP stale=%d held=%d' % (len(stale), len(over)) + ('  (seats down, rows kept by MODE: %s)' % ' '.join('%s=%d' % kv for kv in sorted(down.items())) if down else ''))
for age, st, topic in stale[:6]: print('STALE %s %dh %s' % (st, age, topic[:90]))
for s, n in sorted(over, key=lambda x: -x[1]): print('HELD %s claims=%d' % (s, n))
sys.exit(1 if stale or over else 0)
