#!/usr/bin/env python3
"""CEO-1931 (Lon 2026-10-23 13:1x CDT, in-chat to the ceo, verbatim: "Seeing as Raku needs to be re-designed and is basically ONE BIG BUG.
I've stopped HQ-RAKU and place Raku work as LOWEST priority until it is re-written."): every FREE row that cures Raku -- a raku- topic, or a
runtime-, instruments- or cto row naming raku -- moves to rank 9, below every other row, so the any-lane pass of `next` serves it last.
FREE rows only (a live claim's cells are never rewritten by script, CEO-755c); the bus's mint lock held for the write (CEO-1708); a dated
QUEUE.tsv backup first. --dry-run | --apply"""
import sys, shutil, datetime, fcntl
PO = '/home/resources/postoffice'; Q = PO + '/QUEUE.tsv'; apply = '--apply' in sys.argv; LOW = '9'
SHARED = ('instruments-the-coos-loop-runs-the-four-auditor-master-passes',)
def is_raku(topic):
    if topic.startswith(SHARED):
        return False
    return topic.startswith('raku-') or '-raku-' in topic or topic.endswith('-raku')
lock = open(PO + '/.mint.lock', 'a')
fcntl.flock(lock, fcntl.LOCK_EX)
data = open(Q, 'rb').read().decode('utf-8'); rows = data.split('\n'); out = []; moved = []
for l in rows:
    f = l.split('\t')
    if len(f) >= 4 and f[0].isdigit() and f[3] == 'FREE' and is_raku(f[1]) and f[0] != LOW:
        moved.append('%s->%s %s (%s)' % (f[0], LOW, f[1][:110], f[2])); f[0] = LOW; l = '\t'.join(f)
    out.append(l)
print(len(moved), 'Raku rows to rank', LOW); [print('  ', m) for m in moved]
if apply and moved:
    shutil.copy2(Q, Q + '.bak.' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '-ceo1931-raku-lowest')
    open(Q, 'wb').write('\n'.join(out).encode('utf-8')); print('applied')
fcntl.flock(lock, fcntl.LOCK_UN)
