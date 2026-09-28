#!/usr/bin/env python3
"""propagate_no_delimited_aggregates_ceo_1349.py -- the NO DELIMITER-JOINED AGGREGATES digest block (Lon 2026-09-28 08:5x to hq_pascal, CEO-1349)
under the ONE TESTING OFFICER block at the head of every root's CLAUDE.md. Idempotent (marker CEO-1349), LF-only, dated backups.
Usage: python3 propagate_no_delimited_aggregates_ceo_1349.py [--dry-run] [ROOT ...]"""
import sys, os, datetime
ROOTS = ['/home/claude_%s' % s for s in ('ceo', 'cto', 'coo', 'cfo', 'icon', 'prolog', 'pascal', 'snocone', 'snobol4', 'raku', 'templates')]
MARK = b'CEO-1349'
ANCHOR = 'ONE TESTING OFFICER, ONE SCORE BOARD, THE AREA SMOKE (Lon 2026-09-27'.encode('utf-8')
BLOCK = ("⛔⭐⭐⭐ **NO DELIMITER-JOINED AGGREGATES (Lon 2026-09-28 08:5x CDT, in-chat to hq_pascal, verbatim: *\"Do not store records like that.\"* · *\"Get rid of ALL delimited based processing like the one I just discovered.\"*; ruled fleet-wide at CEO-1349; RULES.md § FACT RULE — NO DELIMITER-JOINED AGGREGATES):** a record, array, list or hash is typed DESCR-slot storage on the collected heap, walked by the collector's typed visitors, never a string with separator bytes (SOH, `\\001`, `\\x05`) taken apart by scanning; Pascal's (hq_pascal) and Raku's (hq_raku) rank-0 rows convert theirs; the census ratchet `audit_delimited_aggregates_census.py` is the cfo's; a landing that adds a separator-joined value is refused in review.\n\n").encode('utf-8')
def main(argv):
    dry = '--dry-run' in argv; roots = [a for a in argv if not a.startswith('--')] or ROOTS
    stamp = datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S'); rc = 0
    for r in roots:
        p = os.path.join(r, 'CLAUDE.md')
        if not os.path.isfile(p): print('SKIP %s: no CLAUDE.md' % r); continue
        b = open(p, 'rb').read()
        if MARK in b: print('SKIP %s: already carries %s' % (p, MARK.decode())); continue
        if b'\r' in b: print('REFUSE(2) %s: CR bytes' % p); rc = 2; continue
        i = b.find(ANCHOR)
        if i < 0: print('REFUSE(2) %s: the CEO-1342 block is missing (run propagate_one_testing_officer_ceo_1342.py first)' % p); rc = 2; continue
        j = b.find(b'\n\n', i)
        if j < 0: print('REFUSE(2) %s: no paragraph end after the anchor' % p); rc = 2; continue
        new = b[:j+2] + BLOCK + b[j+2:]
        if dry: print('WOULD WRITE %s (+%d bytes)' % (p, len(new)-len(b))); continue
        open(p + '.bak-%s-ceo-1349' % stamp, 'wb').write(b); open(p, 'wb').write(new); print('WROTE %s' % p)
    return rc
if __name__ == '__main__': sys.exit(main(sys.argv[1:]))
