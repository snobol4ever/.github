#!/usr/bin/env python3
"""propagate_lifetime_rule_and_declared_sizes_ceo_1354.py -- write two digest blocks at the head of every root's CLAUDE.md:
THE LIFETIME RULE (Lon 2026-09-28 16:3x, CEO-1354) and EVERY PROGRAM STORES ITS NECESSARY STACK AND HEAP (Lon 2026-09-28 15:4x,
CEO-1353). Idempotent per block (a root whose digest already carries a block's marker keeps it), LF-only, dated backup beside
each file. Usage: python3 propagate_lifetime_rule_and_declared_sizes_ceo_1354.py [--dry-run] [ROOT ...]
Default roots: the four officers, the six language HQs and hq_templates. The ceo runs it on its own root; Lon runs it for the
sibling roots (a Bash write into a sibling root from a seat is refused by the harness classifier)."""
import sys, os, datetime
ROOTS = ['/home/claude_%s' % s for s in ('ceo', 'cto', 'coo', 'cfo', 'icon', 'prolog', 'pascal', 'snocone', 'snobol4', 'raku', 'templates')]
BLOCKS = [
 (b'CEO-1354', ("⛔⭐⭐⭐⭐ **THE LIFETIME RULE — STACK FOR A CONSTRUCT'S LIFETIME, HEAP FOR WHAT OUTLIVES ITS SCOPE (Lon 2026-09-28 16:3x CDT, in-chat to hq_prolog, verbatim: "
  "*\"Does the memory live for a lifetime directly tied to a program construct. If so it belongs on the stack. If the lifetime lives past the scope that data was created, then it belongs on the heap.\"* · "
  "*\"Also next time you run out of stack then change the command-line switch or the environment variable to allocate more memory to get what is needed.\"*; ruled fleet-wide at CEO-1354; RULES.md § FACT RULES — THE LIFETIME RULE):** "
  "every datum in every language's compiler and runtime whose lifetime is a program construct — a call, a clause activation, a pattern match, a loop body, one runtime call's own work — lives on the STACK "
  "(an emitted frame, or in C a stack array sized to its need at the construct's entry: a VLA or alloca, which neither the fixed-caps census nor the C-allocators ratchet counts); a value that outlives "
  "the scope that created it lives on the HEAP, reaching it at the moment it escapes. A program that runs out of stack gets a bigger declared `-s` / `SCRIP_STACK` on its attribute row (hard-cap clause 8 (g)); "
  "data is never moved to the heap to save stack. R2 (Prolog heap-only variable cells) is WITHDRAWN on this rule and its row retired — the ceo's CEO-1352 order to land it was wrong; hq_prolog runs "
  "Lon's source-wide lifetime scan and cures each site in its own landing.\n\n").encode('utf-8')),
 (b'CEO-1353', ("⛔⭐⭐⭐ **EVERY PROGRAM IN EVERY LANGUAGE STORES ITS NECESSARY STACK AND HEAP, AND EVERY HARNESS SCRIPT USES THEM (Lon 2026-09-28 15:4x CDT, in-chat to the ceo, verbatim: "
  "*\"Ensure that every program in every language as it necessary stack size and heap size values stored in the per-program attribute file, and ensure that those command-line switches and environment variable values are being used by the harness shell scripts which run all of them.\"*; "
  "CEO-1353; RULES.md hard-cap rule clause 8 (g)):** every test unit declares `heap_kb`/`stack_kb` in its attribute row or `<stem>.heap`/`<stem>.stack` sidecars "
  "(`.github/scripts/util_declared_sizes_census.py [--lang L]` counts them, no run); a unit that runs at the default keeps it, a unit that runs out gets its measured need with two readings; where the "
  "oracle needs more than its own default the unit declares the oracle's knob beside it (`oracle_env`: iconx `MSTKSIZE`/`BLKSIZE`/`STRSIZE`/`COEXPSIZE`, gprolog `GLOBALSZ`/`LOCALSZ`/`TRAILSZ`/`CSTRSZ`; "
  "`oracle_args`: sbl `-d`/`-s`, swipl `--stack-limit`, fpc `-Cs`/`-Ch`); every runner passes the declaration in both modes as `-d<kb>k -s<kb>k` (mode 4: at the head of the binary's argv before `--`) "
  "or `SCRIP_HEAP_CAP_KB` / `SCRIP_STACK` — NEVER `SCRIP_HEAP_KB` / `SCRIP_HEAP_MB`, which set the collector's WINDOW (seven grading paths did, grading Logtalk, the Icon packages, INRIA and IcnBench "
  "under a 128 MB window; the coo's rank-0 row cures them).\n\n").encode('utf-8')),
]
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
        if b'\r' in b:
            print('REFUSE(2) %s: carries CR bytes; not touched' % p); rc = 2; continue
        lines = b.split(b'\n')
        if not lines or not lines[0].startswith(b'# '):
            print('REFUSE(2) %s: first line is not a # heading (%r)' % (p, lines[0][:40])); rc = 2; continue
        add = b''.join(blk for mark, blk in BLOCKS if mark not in b)
        if not add:
            print('SKIP %s: already carries every block' % p); continue
        new = lines[0] + b'\n\n' + add + b'\n'.join(lines[1:])
        if dry:
            print('WOULD WRITE %s (+%d bytes)' % (p, len(new) - len(b))); continue
        bak = p + '.bak-%s-ceo-1354' % stamp
        open(bak, 'wb').write(b)
        open(p, 'wb').write(new)
        print('WROTE %s (backup %s)' % (p, os.path.basename(bak)))
    return rc
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
