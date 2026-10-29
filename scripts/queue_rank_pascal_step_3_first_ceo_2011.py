"""CEO-2011 (the cto, 2026-10-29 16:2x CDT, answering Lon's in-chat question whether Pascal was re-designed properly; ARCH-PASCAL-REDESIGN 8.9):
the design is right and half landed, and the redesign itself (one type model, the name-keyed tables deleted) waits behind step 3, which 8.7's
order flip had staged behind the features. The cto reversed it: step 3 is next for hq_pascal, before 5, 6, 9 and any further feature landing on
the legacy. pascal-front-end-step-3-every-predicate-asks-the-typer-and-the-tables-go-ceo-2005 moves to rank 1. FREE rows only (a live claim's
cells are never rewritten by script, CEO-755c); the bus's mint lock held for the write (CEO-1708); a dated QUEUE.tsv backup first.
--dry-run | --apply"""
import sys, os, time, atexit, shutil, datetime
PO = '/home/resources/postoffice'; Q = PO + '/QUEUE.tsv'; apply = '--apply' in sys.argv; RANK = '1'; LK = PO + '/.mint.lock'
TOPICS = ('pascal-front-end-step-3-every-predicate-asks-the-typer-and-the-tables-go-ceo-2005',)
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
    shutil.copy2(Q, Q + '.bak.' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '-ceo2011-pascal-step-3-first')
    open(Q, 'wb').write('\n'.join(out).encode('utf-8')); print('applied')
