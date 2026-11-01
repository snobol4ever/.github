#!/usr/bin/env bash
set -u
S4=/tmp/claude-1000/-home-claude-cto/b1caac4c-9b75-4393-9260-1c72f906f86b/scratchpad; SO=/tmp/claude-1000/-home-claude-cto/25cbd82c-ea4e-46bc-9ee6-3c52fc5dcc1f/scratchpad; W=$SO/hdr/SCRIP; HW=$SO/hdr/harness; HS=$HW/scripts
cp $HS/util_header_fanin.py $S4/fanin_hop_consuming.py
python3 - "$HS" <<'PY' || exit 2
import sys; HS = sys.argv[1]
p = HS + '/util_header_fanin.py'; t = open(p).read()
old = "    for m in re.finditer(r'[;{]\\s*(?:const\\s+)?(?:struct\\s+)?(\\w+)\\s*\\*+\\s*(\\w+)\\s*;', text):\n        ptrs.append((m.group(2), m.group(1)))"
new = "    for m in re.finditer(r'(?<=[;{])\\s*(?:const\\s+)?(?:struct\\s+)?(\\w+)\\s*\\*+\\s*(\\w+)\\s*;', text):\n        ptrs.append((m.group(2), m.group(1)))"
assert t.count(old) == 1, t.count(old); open(p, 'w').write(t.replace(old, new)); print('instrument: the pointer-member scan looks behind for the separator instead of consuming it (every member, not every other)')
g = HS + '/test_gate_no_header_reaches_more_units_than_its_users.sh'; t = open(g).read()
old2 = "typedef struct { struct rec_t * p; } hold_t;"
new2 = "typedef struct { struct rec_t * q; struct rec_t * p; } hold_t;"
assert t.count(old2) == 1; open(g, 'w').write(t.replace(old2, new2)); print('gate ARM 9: hold_t carries two pointer members, p second')
PY
cp $HS/util_header_fanin.py $S4/fanin_hop_lookbehind.py
cd $W || exit 2
echo "== fail-once: the two-member control against the consuming scan"; cp $S4/fanin_hop_consuming.py $HS/util_header_fanin.py; S4E_DONE_WHEN_RUN=1 bash $HS/test_gate_no_header_reaches_more_units_than_its_users.sh 2>&1 | grep -E 'ARM 9|m5.c|m6.c|rec.h does' | cut -c1-160
cp $S4/fanin_hop_lookbehind.py $HS/util_header_fanin.py; echo "== with the lookbehind"; S4E_DONE_WHEN_RUN=1 bash $HS/test_gate_no_header_reaches_more_units_than_its_users.sh 2>&1 | grep -E 'ARM 9|m5.c|m6.c|rec.h does' | cut -c1-160
S4E_DONE_WHEN_RUN=1 bash $HS/test_gate_no_header_reaches_more_units_than_its_users.sh 2>&1 | grep -q '^  ok   ARM 9' || { echo "ARM 9 not green with the lookbehind; stop"; exit 2; }
echo "== the unused arm on the root (6C, fully built): datatype.h readers"; python3 -I $HS/util_header_fanin.py --root /home/claude_cto/SCRIP --unused 2>/dev/null | tail -1; python3 -I $HS/util_header_fanin.py --root /home/claude_cto/SCRIP --unused 2>/dev/null | grep -cE '^runtime/(aggregates|pl_rat)\.c' | sed 's/^/aggregates+pl_rat unused lines: /'
git checkout -- src/runtime/pl_rat.c && echo "pl_rat.c keeps datatype.h"; git status --short | cut -c1-60
bash $S4/s7-fix.sh > $S4/s7-fix.log 2>&1; echo "chain rc=$?"
