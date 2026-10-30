"""CEO-2049 (2026-10-30 12:2x CDT; the ceo, on hq_prolog's ask and the cqo's diagnosis): GNU source's one red, BipsPl/call, is the witness
of the LIFO plan's step 4 (call_cleanup over a goal retried through a disjunction: CLEANUP_TEST's gamma leaves rsp above the retained callee
frame, the next runtime call overwrites it, the retry segfaults; red already at e92462182). A SUITE TABLE red is rank 1 (CEO-1386), so
prolog-lifo-step-4-discard-restores-by-distance-or-hop-ceo-2000 moves 2 -> 1, the cfo's (CEO-2034), after its step 3. FREE rows only (a live
claim's cells are never rewritten by script, CEO-755c); the bus's mint lock held for the write (CEO-1708); a dated QUEUE.tsv backup first.
--dry-run | --apply"""
import sys, os, time, atexit, shutil, datetime
PO = '/home/resources/postoffice'; Q = PO + '/QUEUE.tsv'; apply = '--apply' in sys.argv; RANK = '1'; LK = PO + '/.mint.lock'
TOPICS = ('prolog-lifo-step-4-discard-restores-by-distance-or-hop-ceo-2000',)
for _i in range(100):
    try:
        os.mkdir(LK); break
    except FileExistsError:
        time.sleep(0.1)
else:
    print('REFUSE(2): %s is held by a bus verb for 10 s -- nothing written' % LK); sys.exit(2)
atexit.register(lambda: os.path.isdir(LK) and os.rmdir(LK))
data = open(Q, 'rb').read().decode('utf-8'); rows = data.split('\n'); out = []; moved = []
for l in rows:
    f = l.split('\t')
    if len(f) >= 4 and f[0].isdigit() and f[1] in TOPICS and f[3] == 'FREE' and f[0] != RANK:
        moved.append('%s->%s %s (%s)' % (f[0], RANK, f[1], f[2])); f[0] = RANK; l = '\t'.join(f)
    out.append(l)
print(len(moved), 'rows to rank', RANK); [print('  ', m) for m in moved]
if apply and moved:
    shutil.copy2(Q, Q + '.bak.' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '-ceo2049-lifo-step-4-rank-1')
    open(Q, 'wb').write('\n'.join(out).encode('utf-8')); print('applied')
