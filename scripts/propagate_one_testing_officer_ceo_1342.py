#!/usr/bin/env python3
"""propagate_one_testing_officer_ceo_1342.py -- write the ONE TESTING OFFICER digest block (Lon 2026-09-27 18:4x-18:5x, CEO-1342)
at the head of every root's CLAUDE.md. Idempotent (skips a root whose digest already carries the CEO-1342 marker), LF-only,
dated backup beside each file. Usage: python3 propagate_one_testing_officer_ceo_1342.py [--dry-run] [ROOT ...]
Default roots: the four officers, the six language HQs and hq_templates. The ceo runs it on its own root; Lon runs it for the
sibling roots (a Bash write into a sibling root from a seat is refused by the harness classifier)."""
import sys, os, datetime
ROOTS = ['/home/claude_%s' % s for s in ('ceo', 'cto', 'coo', 'cfo', 'icon', 'prolog', 'pascal', 'snocone', 'snobol4', 'raku', 'templates')]
MARK = b'CEO-1342'
BLOCK = ("⛔⭐⭐⭐⭐ **ONE TESTING OFFICER, ONE SCORE BOARD, THE AREA SMOKE (Lon 2026-09-27 18:4x–18:5x CDT, in-chat to the ceo, verbatim: "
 "*\"It time to stop all this parallel test runs where each seat is running there own tests. This load of 30-40 on a 16 CPU machine is STOPPING NOW!!!!\"* · "
 "*\"Have one OFFICER mandated to testing on behalf of the entire fleet. Keep ONE SCORE BOARD!!!!\"*; ruled fleet-wide at CEO-1342; RULES.md § ONE TESTING OFFICER, ONE SCORE BOARD, THE AREA SMOKE):** "
 "THE COO IS THE FLEET'S TESTING OFFICER — it alone runs every suite, package, bench and demo pass and the blocking set, one run at a time in a standing loop over origin HEAD, and alone writes SCORE.md § THE SUITE TABLE; "
 "MODE's `LANES:` line names coo for every language, so every other seat's runner and score-row write REFUSE rc=2 by law, not by defect. A seat runs PER LANDING only its row's DONE-WHEN, the gates its diff touched, `make preflight` and THE AREA SMOKE "
 "(`test_area_smoke.sh`, the coo's rank-0 row: the rungs and package entries whose `ALL.csv` attribute row marks the feature the diff touched — Lon: *\"if you change the SPAN function, then run every program that has SPAN as a reference\"* — selected from the diff itself through `scripts/area_map.tsv` and run as the last arm of preflight once it lands; until then, extract the entries of the features your commit names through `corpus_suite_harness.py` by hand, both modes). "
 "A red the coo's loop finds reaches the lane by telegram with the range of landings since the row's last green reading; the lane bisects it in a scratch worktree and cures or reverts within the tick (Lon: *\"We might miss a bug introduced on a first cut, be we will catch it soon after it is cut.\"*). "
 "No seat runs a whole suite, a board, a corpus census, the blocking set, `make test-arena`, a stress plant or an A/B sweep. Every \"one runner per language\", \"runs ONLY its own language's suites\", \"once per batch of three to four\", \"SNOBOL4 boards one pass per day\" and \"Rebus keep-green\" below is HISTORY as to WHO RUNS; the mechanisms named beside them stand.\n\n").encode('utf-8')
def main(argv):
    dry = '--dry-run' in argv
    roots = [a for a in argv if not a.startswith('--')] or ROOTS
    stamp = datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')
    rc = 0
    for r in roots:
        p = os.path.join(r, 'CLAUDE.md')
        if not os.path.isfile(p):
            print('SKIP %s: no CLAUDE.md' % r); continue
        b = open(p, 'rb').read()
        if MARK in b:
            print('SKIP %s: already carries %s' % (p, MARK.decode())); continue
        if b'\r' in b:
            print('REFUSE(2) %s: carries CR bytes; not touched' % p); rc = 2; continue
        lines = b.split(b'\n')
        if not lines or not lines[0].startswith(b'# '):
            print('REFUSE(2) %s: first line is not a # heading (%r)' % (p, lines[0][:40])); rc = 2; continue
        new = lines[0] + b'\n\n' + BLOCK + b'\n'.join(lines[1:])
        if dry:
            print('WOULD WRITE %s (+%d bytes)' % (p, len(new) - len(b))); continue
        bak = p + '.bak-%s-ceo-1342' % stamp
        open(bak, 'wb').write(b)
        open(p, 'wb').write(new)
        print('WROTE %s (backup %s)' % (p, os.path.basename(bak)))
    return rc
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
