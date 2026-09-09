#!/usr/bin/env python3
"""propagate_mode_nonet_digests.py -- ceo CEO-403, 2026-09-08.

Lon moved the fleet to four officers plus nine HQs (MODE NONET, 19:50 CDT). Thirteen seats were
telegrammed the same minute, but a telegram is read once and a digest is read at every session
start -- and four HQ digests still RESTATE a dead mode value in their own prose. hq_P's says
`EXECUTIVE`, which is a digest telling a seated HQ that it is stood down.

⛔ THIS SCRIPT DOES NOT WRITE A VALUE INTO A DIGEST, AND THAT IS THE POINT. Rewriting EXECUTIVE
to NONET would buy exactly one mode flip of accuracy and leave the same trap armed for the next
one -- which is how these four went stale in the first place. It rewrites a RESTATEMENT into a
POINTER at /home/resources/postoffice/MODE, the same principle as "digests never restate law".
hq_B, hq_S and hq_V already carry pointers and are left untouched by design; the script reports
them as ALREADY-POINTING, never as failures.

Per file: back up, edit, print a git-style numstat. REFUSES (rc=2) any file whose anchor is not
unique -- a blind rewrite across nine unversioned digests is not something to do two days before
an announcement. Run from the ceo root; Lon runs it because a ceo path may not write a sibling
root (the harness classifier refuses).
"""
import re, sys, shutil, datetime

STAMP = datetime.datetime.now().strftime('%Y-%m-%d-%H%M')
POINTER = ("⛔⭐ **MODE IS THE FIRST LINE OF `/home/resources/postoffice/MODE`, AND ITS ROSTER IS THE HEADER "
           "COMMENT ON LINE 2 — READ BOTH, NEVER A VALUE RESTATED HERE.** `head -1` for the value, "
           "`sed -n '2p'` for the standing seats and their lanes, verbatim as the ceo wrote them at the "
           "declaration. It has changed twenty-two times since 08-29 and twice on 2026-09-08 alone "
           "(EXECUTIVE → QUARTET 19:09, QUARTET → NONET 19:50, Lon: *\"Move to 4 officers plus 9 HQ's.\"* "
           "— four officers and all nine HQs, thirteen working seats). A digest that names a mode is a "
           "digest that is wrong within the day; this line is deliberately the only mode sentence in this file.")

ROOTS = ['C', 'P', 'U', 'T', 'B', 'I', 'R', 'S', 'V']
# The anchor is the digest's own standing mode sentence -- the whole bullet or heading line that
# restates a value. Matched as: a line naming MODE that also names a dead value token.
DEAD = re.compile(r'\b(EXECUTIVE|QUARTET|QUATRO|OCTET|CEO MODE|FLEET-\d+)\b')

rc = 0
for r in ROOTS:
    path = '/home/claude_%s/CLAUDE.md' % r
    try:
        text = open(path, encoding='utf-8').read()
    except OSError as e:
        print('⛔ REFUSED hq_%s: %s' % (r, e)); rc = 2; continue
    lines = text.split('\n')
    hits = [i for i, l in enumerate(lines) if 'MODE' in l and DEAD.search(l)]
    if not hits:
        print('ok  hq_%-3s ALREADY-POINTING: no line restates a mode value; untouched by design' % r)
        continue
    if len(hits) > 1:
        print('⛔ REFUSED hq_%s: %d lines restate a mode value (%s) -- anchor is not unique, '
              'refusing a blind rewrite; fix by hand' % (r, len(hits), ', '.join(str(h + 1) for h in hits)))
        rc = 2; continue
    i = hits[0]
    old = lines[i]
    lead = re.match(r'^(\s*(?:[-*]\s+|#{1,6}\s+)?)', old).group(1)
    lines[i] = lead + POINTER
    shutil.copy2(path, path + '.bak-mode-nonet-' + STAMP)
    open(path, 'w', encoding='utf-8').write('\n'.join(lines))
    print('ok  hq_%-3s line %d rewritten  1 1  (backup %s.bak-mode-nonet-%s)' % (r, i + 1, path, STAMP))
    print('       was: ' + old[:150])

print('\nRun the digest gate next: bash scripts/test_gate_digest_matches_rules.sh')
sys.exit(rc)
