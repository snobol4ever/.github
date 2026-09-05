#!/usr/bin/env python3
"""Apply Lon's 2026-09-05 11:1x ruling to the user-scope Claude Code settings (GOAL-CEO CEO-288):
 - drop the allow rule for the private clone that lived under /home/resources (the clone itself is removed: /home/resources
   holds shared global resources only; a repo is modified in a clone inside the seat's own root, pushed, then installed);
 - reword the Source control trust line the same way.
Lon-run: the ceo seat is refused edits of this file by the classifier.
  python3 settings_after_lons_clone_ruling.py --dry-run    # print the change, write nothing
  python3 settings_after_lons_clone_ruling.py              # dated backup beside the file, then rewrite
rc 0 = done · rc 2 = refused: an anchor was not found exactly once, nothing written."""
import json, sys, shutil, time

PATH = '/home/satirical/.claude/settings.json'
DROP_RULE = 'Bash(git -C /home/resources/x64-private-ceo:*)'
OLD = ("**Source control**: github.com/snobol4ever is the org — every root under /home/claude* holds clones of SCRIP, corpus and .github with snobol4ever origins, "
       "and /home/resources/x64 (with x64-private-ceo) is the org's SPITBOL fork; fetch/pull/push to snobol4ever remotes over SSH is routine on every seat; "
       "upstream clones (spitbol/spitbol, philbudne/csnobol4, fpc, MoarVM, nqp, Pascal-P5, SWI-Prolog/bench, atdt/snoflake) are fetch-only and never pushed")
NEW = ("**Source control**: github.com/snobol4ever is the org — every root under /home/claude* holds clones of SCRIP, corpus and .github with snobol4ever origins; "
       "fetch/pull/push to snobol4ever remotes over SSH is routine on every seat. /home/resources/x64 is the org's SPITBOL fork as a SHARED INSTALL, never a development clone: "
       "to modify any repo a seat clones it inside its own root (e.g. /home/claude_B/x64), fixes and pushes there, then installs the result into /home/resources (Lon 2026-09-05: "
       "\"Do not clone into /home/resources … clone it local … after you made the fix you would install it into /home/resources\"); "
       "upstream clones (spitbol/spitbol, philbudne/csnobol4, fpc, MoarVM, nqp, Pascal-P5, SWI-Prolog/bench, atdt/snoflake) are fetch-only and never pushed")

def main(argv):
    dry = '--dry-run' in argv
    path = argv[argv.index('--file') + 1] if '--file' in argv else PATH
    d = json.load(open(path, encoding='utf-8'))
    allow = d.get('permissions', {}).get('allow', [])
    env = d.get('autoMode', {}).get('environment', [])
    if allow.count(DROP_RULE) != 1:
        print('REFUSED rc=2: rule found %d times, expected 1: %s' % (allow.count(DROP_RULE), DROP_RULE)); return 2
    if env.count(OLD) != 1:
        print('REFUSED rc=2: Source control anchor found %d times, expected 1' % env.count(OLD)); return 2
    print('- rule ' + DROP_RULE); print('- ' + OLD); print('+ ' + NEW)
    if dry:
        print('DRY RUN: 1 rule dropped, 1 line replaced, nothing written (%s)' % path); return 0
    bak = path + '.bak-' + time.strftime('%Y%m%dT%H%M%S'); shutil.copy2(path, bak)
    allow.remove(DROP_RULE); env[env.index(OLD)] = NEW
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(d, f, indent=2, ensure_ascii=False); f.write('\n')
    json.load(open(path, encoding='utf-8'))
    print('WRITTEN %s; backup %s' % (path, bak)); return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
