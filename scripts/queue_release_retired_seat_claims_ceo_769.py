#!/usr/bin/env python3
"""ceo CEO-769 (2026-09-16): release every claim still held by a seat retired under CEO-767 (hq_B..hq_V) on a LIVE row.
The picker resumes a claim only when the claim file's first line equals the calling seat (s4e_msg.sh next, PASS 1/2), so a
row whose queue cell says ASSIGNED:hq_prolog while its claim file still says hq_C is served to nobody: hidden from the
picker (claimed) and from hq_prolog (not theirs). Cure: the row goes FREE under the owner the queue already names (one
LANE-BY-CURE correction: an Icon speed row goes to hq_icon), the claim file moves to released/, and the baton's LEDGER
records the release. Rows whose queue state is DONE are left for sweep. Never touches a claim held by a live seat."""
import os, shutil, sys, time
PO = '/home/resources/postoffice'
RETIRED = {'hq_B','hq_C','hq_I','hq_P','hq_R','hq_S','hq_T','hq_U','hq_V'}
RELANE = {'icon-deal-the-shuffle-and-random-path-is-twenty-times-slower-than-iconx-in-both-modes': 'hq_icon'}
apply = '--apply' in sys.argv
stamp = time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime())
q = PO + '/QUEUE.tsv'
data = open(q, 'rb').read().split(b'\n')
rows = {}
for i, l in enumerate(data):
    f = l.split(b'\t')
    if len(f) >= 4 and not l.startswith(b'#'):
        rows[f[1].decode()] = (i, f)
changed = 0
for name in sorted(os.listdir(PO + '/claims')):
    if not name.endswith('.claim'): continue
    topic = name[:-6]; c = PO + '/claims/' + name
    owner = open(c).readline().strip()
    if owner not in RETIRED: continue
    if topic not in rows: print('SKIP no live row', owner, topic); continue
    i, f = rows[topic]; state = f[3].decode(); qowner = f[2].decode()
    if state == 'DONE' or state.startswith('SUPERSEDED') or state.startswith('RETIRED'):
        print('LEAVE', state, owner, topic); continue
    new_owner = RELANE.get(topic, qowner)
    print('RELEASE', owner, '->', new_owner, 'FREE', '(was', qowner + '/' + state + ')', topic)
    if not apply: continue
    f[2] = new_owner.encode(); f[3] = b'FREE'; data[i] = b'\t'.join(f); changed += 1
    os.makedirs(PO + '/released', exist_ok=True)
    shutil.move(c, PO + '/released/' + name + '.ceo769-' + stamp.replace(':', ''))
    t = PO + '/tasks/' + topic + '.task.md'
    if os.path.exists(t):
        with open(t, 'ab') as fh:
            fh.write(('- [ceo·%s] RELEASED by the ceo (CEO-769): the claim was held by %s, retired under CEO-767, and the picker serves a claim only to the seat named on its first line; row FREE under %s.\n' % (stamp, owner, new_owner)).encode())
if apply:
    shutil.copy(q, q + '.bak.ceo769-' + stamp.replace(':', ''))
    open(q, 'wb').write(b'\n'.join(data))
print('changed', changed, 'apply' if apply else 'dry-run')
