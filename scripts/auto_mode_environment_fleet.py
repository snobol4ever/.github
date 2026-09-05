#!/usr/bin/env python3
"""Rewrite the auto-mode trust description (autoMode.environment) in the user-scope Claude Code settings so it
describes the fleet as it is: twenty sibling roots of one fleet under one OS user, the snobol4ever GitHub org as the
push destination, /home/resources as the shared fleet directory. Lon-run (GOAL-CEO CEO-287): the ceo seat is refused
every Bash touch of this file by the classifier; this script is the decision made concrete, never applied by a seat.

  python3 auto_mode_environment_fleet.py --dry-run            # print every changed line, write nothing
  python3 auto_mode_environment_fleet.py                      # dated backup beside the file, then rewrite
  python3 auto_mode_environment_fleet.py --file <path> ...    # operate on another settings file (the proof fixture)

rc 0 = written (or dry run complete) · rc 2 = refused: an anchor line was not found exactly once, nothing written."""
import json, sys, shutil, time

PATH = '/home/satirical/.claude/settings.json'
ROOTS = '/home/claude (ceo), /home/claude_B /home/claude_C /home/claude_P /home/claude_T (the four HQs), /home/claude01 … /home/claude16 (fleet seats)'

# (exact current line, replacement). Every anchor must match exactly once or the script refuses.
REPLACE = [
    ("**Default / protected branches**: Unknown — no remote configured, gh visibility check not queryable (no origin remote to derive owner/repo)",
     "**Default / protected branches**: main on every snobol4ever repo; work lands on main directly (no PR flow); history rewrite, force-push and reset --hard are forbidden by RULES.md on every seat"),
    ("**Source control**: The trusted repo only — no remotes are configured for /home/claude1, and no additional orgs are configured",
     "**Source control**: github.com/snobol4ever is the org — every root under /home/claude* holds clones of SCRIP, corpus and .github with snobol4ever origins, and /home/resources/x64 (with x64-private-ceo) is the org's SPITBOL fork; fetch/pull/push to snobol4ever remotes over SSH is routine on every seat; upstream clones (spitbol/spitbol, philbudne/csnobol4, fpc, MoarVM, nqp, Pascal-P5, SWI-Prolog/bench, atdt/snoflake) are fetch-only and never pushed"),
    ("**Trusted repo**: The working directory /home/claude1 (the D-17 PORTABLE-HOME sibling root, containing SCRIP, corpus, .github per CLAUDE.md) — no git remotes are configured, so no push destination is trusted beyond local commits",
     "**Trusted roots**: " + ROOTS + " — twenty sibling roots of ONE fleet under one OS user, each the D-17 PORTABLE-HOME layout (SCRIP, corpus, .github per CLAUDE.md); a seat editing another root's CLAUDE.md or .claude/settings*.json on a ceo ruling is routine (Lon 2026-09-02 grant)"),
    ("routine under /home/claude1/ prefix: build, test, and oracle-verification scripts described in CLAUDE.md (make, scrip binary, scripts/test_*, scripts/build_*, scripts/util_*) are routine local operations within this tree",
     "routine under every /home/claude*/ prefix and under /home/resources/: build, test and oracle-verification scripts described in CLAUDE.md (make, the scrip binary, scripts/test_*, scripts/build_*, scripts/util_*, scripts/s4e_msg.sh), git fetch/pull/push to snobol4ever remotes, and the postoffice protocol are routine operations"),
]
# Inserted right after the Trusted roots line.
INSERT_AFTER = "**Trusted roots**: "
INSERT = ("**Shared fleet directory**: /home/resources is the fleet's shared state — postoffice/ (queue, claims, batons, inboxes), ORACLES.md, "
          "the oracle binaries (x64/bin/sbl, spitbol-bench-oracle, icon-master, the csnobol4 build) and the upstream drops; reads and writes there by any seat are routine, "
          "including an oracle binary swap done under RULES.md § Oracles (dated backup beside the binary, same-minute broadcast, same-sitting re-baseline)")

def main(argv):
    dry = '--dry-run' in argv
    path = PATH
    if '--file' in argv:
        path = argv[argv.index('--file') + 1]
    d = json.load(open(path, encoding='utf-8'))
    env = d.get('autoMode', {}).get('environment')
    if not isinstance(env, list):
        print('REFUSED rc=2: no autoMode.environment list in', path); return 2
    for old, _ in REPLACE:
        n = env.count(old)
        if n != 1:
            print('REFUSED rc=2: anchor found %d times, expected 1: %s' % (n, old[:70])); return 2
    if any(l.startswith(INSERT_AFTER) for l in env) or INSERT in env:
        print('REFUSED rc=2: already rewritten (Trusted roots / Shared fleet directory line present)'); return 2
    out = []
    for l in env:
        new = dict(REPLACE).get(l)
        if new is None:
            out.append(l); continue
        print('- ' + l); print('+ ' + new); out.append(new)
        if new.startswith(INSERT_AFTER):
            print('+ ' + INSERT); out.append(INSERT)
    if dry:
        print('DRY RUN: %d lines replaced, 1 inserted, nothing written (%s)' % (len(REPLACE), path)); return 0
    bak = path + '.bak-' + time.strftime('%Y%m%dT%H%M%S')
    shutil.copy2(path, bak)
    d['autoMode']['environment'] = out
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(d, f, indent=2); f.write('\n')
    json.load(open(path, encoding='utf-8'))
    print('WRITTEN %s (%d replaced, 1 inserted); backup %s' % (path, len(REPLACE), bak)); return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
