#!/usr/bin/env python3
"""Update the auto-mode trust description in the user-scope Claude Code settings after Lon moved the ceo root
(2026-09-06 11:29 CDT: "I just moved /home/claude to /home/claude_ceo and created anew /home/claude_cto"): the
Trusted roots line named /home/claude (ceo), four HQs and sixteen seats; the fleet is now /home/claude_ceo (ceo),
/home/claude_cto (cto), eight HQs and twenty seats -- thirty roots. Exact-anchor replacement, dated backup beside
the file. Lon-run: the ceo seat's harness classifier REFUSED this write on 2026-09-06 11:47 CDT (the CEO-287
precedent held for settings.json even though the same sitting's cross-root clone and digest rewrites were allowed):
  python3 /home/claude_ceo/.github/scripts/settings_after_the_rename.py [--dry-run]
rc 0 = written (or dry run) · rc 2 = refused: the anchor was not found exactly once, nothing written."""
import json, sys, shutil, time
PATH = '/home/satirical/.claude/settings.json'
OLD = "**Trusted roots**: /home/claude (ceo), /home/claude_B /home/claude_C /home/claude_P /home/claude_T (the four HQs), /home/claude01 … /home/claude16 (fleet seats) — twenty sibling roots of ONE fleet under one OS user"
NEW = ("**Trusted roots**: /home/claude_ceo (ceo; it was /home/claude until Lon moved it 2026-09-06), /home/claude_cto (cto, the CTO seat), "
       "/home/claude_B /home/claude_C /home/claude_P /home/claude_T /home/claude_U /home/claude_S /home/claude_I /home/claude_R (the eight HQs), "
       "/home/claude01 … /home/claude20 (fleet seats) — thirty sibling roots of ONE fleet under one OS user")
dry = '--dry-run' in sys.argv
s = open(PATH, encoding='utf-8').read()
if s.count(OLD) != 1:
    print(f'REFUSED rc=2: anchor found {s.count(OLD)} times (need exactly 1); nothing written'); sys.exit(2)
t = s.replace(OLD, NEW)
json.loads(t)
if dry:
    print('DRY: would rewrite the Trusted roots line to:\n  ' + NEW[:160] + ' …'); sys.exit(0)
bak = PATH + '.bak-rename-' + time.strftime('%Y%m%dT%H%M%S')
shutil.copy2(PATH, bak); open(PATH, 'w', encoding='utf-8').write(t)
print(f'written; backup {bak}')
