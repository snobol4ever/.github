"""CEO-2020: TreallaTests is ordered BEHIND XsbTests in hq_packages' lane (CEO-2019: XSB group 6 first, then Trealla), so its rank-1 FREE row
read to the census as an HQ-lane row unserved past 24 h while the same seat works the row ranked ahead of it; it moves to rank 2 to say the
order the ceo ruled. FREE rows only (a live claim's cells are never rewritten by script, CEO-755c); the bus's mint lock held for the write
(CEO-1708); a dated QUEUE.tsv backup first. --dry-run | --apply"""
import sys, os, time, atexit, shutil, datetime
PO = '/home/resources/postoffice'; Q = PO + '/QUEUE.tsv'; apply = '--apply' in sys.argv; RANK = '2'; LK = PO + '/.mint.lock'
TOPICS = ('prolog-treallatests-to-100-the-81-failing-programs-ceo-1926',)
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
    shutil.copy2(Q, Q + '.bak.' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '-ceo2020-trealla-behind-xsb')
    open(Q, 'wb').write('\n'.join(out).encode('utf-8')); print('applied')
