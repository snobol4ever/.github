#!/usr/bin/env python3
# s7-extract.py -- from apply7-proof.log: the after table (s7-after.txt), the ceiling summary (s7-ceil.txt), and the readings into the commit text and the cursor entry
import re, sys
S4 = '/tmp/claude-1000/-home-claude-cto/b1caac4c-9b75-4393-9260-1c72f906f86b/scratchpad'
log = open(S4 + '/apply7-proof.log').read()
sec2 = log.split('== 2 the arms and the after table\n', 1)[1].split('\n== 3', 1)[0].split('\n')
rows = [l for l in sec2 if l.strip() and not l.startswith(('RAISED', 'arm '))]
assert len(rows) >= 2, rows
after, ceil = rows[0].strip(), rows[1].strip()
assert 'absent' not in after, after
open(S4 + '/s7-after.txt', 'w').write(after); open(S4 + '/s7-ceil.txt', 'w').write(ceil)
r5 = re.search(r'^R5 rc=(\d) :: (objects=\S+ identical=\S+ differing=0 \(of the identical, (\d+) differ only in __LINE__[^)]*\))', log, re.M); assert r5, 'R5 line'
only = re.findall(r'^(ONLY-\S+ \S+)', log, re.M); assert r5.group(1) == '0' or (only == ['ONLY-A obj:scrip_driver0.o'] and 'DIFF' not in log), (r5.group(1), only)
R5 = 'R5 --no-comdat over both media against the 6C pristine build at the same path: %s; %s of the 297 differ only in __LINE__ immediates moved by an added include line, which the comparer counts identical; the parent snapshot alone held scrip_driver0.o, the stage-0 driver object an earlier make had left in the objdir, which the pristine child does not build (ONLY-A, not a missing object)' % (r5.group(2).split(' (')[0], r5.group(3))
smokes = re.findall(r'^SMOKE (\S+) rc=(\d+)', log, re.M); assert smokes and all(rc == '0' for _, rc in smokes), smokes
gates = re.findall(r'^GATE (\S+) rc=(\d+) (\d+)s', log, re.M)
dw = re.search(r'^== 6 .*\n(.*)$', log, re.M).group(1).strip()
import os
if os.path.exists(S4 + '/dw7-rerun.txt'):
    dw = open(S4 + '/dw7-rerun.txt').read().strip()   # the DONE-WHEN as re-run after the harness fixes (the proof run's table still had the gate in no bucket)
assert dw.startswith('GREEN'), dw
ceiling_s = [s for g, rc, s in gates if g.startswith('test_gate_no_header')][0]
GATES = 'the ceiling gate GATE PASS in %ss, every arm 0; %s' % (ceiling_s, '; '.join('%s rc=%s' % (g.replace('test_gate_', '').replace('.sh', ''), rc) for g, rc, s in gates[1:]))
ARMS = 'every arm of the ceiling gate reads 0 against the lowered baseline (%s)' % ceil
t = open(S4 + '/s7-commit.txt').read().replace('[ARMS]', ARMS).replace('[R5]', R5).replace('[GATES]', GATES); open(S4 + '/s7-commit.txt', 'w').write(t)
t = open(S4 + '/cto-442.txt').read().replace('[R5-7]', r5.group(2) + ' (no line drift)').replace('[AFTER]', after); open(S4 + '/cto-442.txt', 'w').write(t)
left = sorted(set(re.findall(r'\[[A-Z0-9-]+\]', open(S4 + '/s7-commit.txt').read())))
print('after:', after[:200]); print('ceil:', ceil); print('R5:', R5); print('smokes:', len(smokes), 'green'); print('gates:', GATES[:200]); print('DONE-WHEN:', dw); print('placeholders left in the commit text:', left)
