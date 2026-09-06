#!/usr/bin/env python3
"""Rewrite every sibling root's CLAUDE.md where it states the ceo root as a CURRENT FACT at /home/claude, which
Lon moved to /home/claude_ceo on 2026-09-06 11:29 CDT ("I just moved /home/claude to /home/claude_ceo and created
anew /home/claude_cto"). Exact-substring replacements only -- historical prose ("older docs hardcode /home/claude")
and Lon's verbatim quotes are left alone. Dated backup beside each changed file. The ceo's digest-propagation grant
(Lon 2026-08-27) covers this; if the ceo's harness refuses the cross-root write, Lon runs:
  python3 /home/claude_ceo/.github/scripts/rename_ceo_root_in_digests.py [--dry-run]
rc 0 = done (changed files listed) · rc 1 = nothing matched anywhere (the census is stale; re-measure before trusting)."""
import glob, sys, time, shutil
dry = '--dry-run' in sys.argv
stamp = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
roots = sorted(glob.glob('/home/claude[0-9][0-9]/CLAUDE.md') + glob.glob('/home/claude_[A-Z]/CLAUDE.md'))
REPL = [
    ("under the ceo at `/home/claude` ", "under the ceo at `/home/claude_ceo` (renamed from `/home/claude` 2026-09-06) "),
    ("under the ceo at `/home/claude`.", "under the ceo at `/home/claude_ceo` (renamed from `/home/claude` 2026-09-06)."),
    ("`ceo` at `/home/claude` (escalate there", "`ceo` at `/home/claude_ceo` (renamed from `/home/claude` 2026-09-06; escalate there"),
    ("CEO = Claude **Fable** at `/home/claude` (identity `ceo`", "CEO = Claude **Fable** at `/home/claude_ceo` (renamed from `/home/claude` 2026-09-06; identity `ceo`"),
    ("only HQ (`/home/claude`) carries it", "only the ceo root (`/home/claude_ceo`, renamed from `/home/claude` 2026-09-06) carries it"),
    # second class (hq_T 2026-09-06 11:5x): the same string spelled as a LOCATION -- files that moved with the root.
    # /home/claude/x64 is left alone on purpose: every digest already says that path is gone (Lon s261, oracle at /home/resources).
    ("/home/claude/.tools/docs", "/home/claude_ceo/.tools/docs"),
    ("/home/claude/csnobol4", "/home/claude_ceo/csnobol4"),
]
changed = 0
for p in roots:
    s = open(p, encoding='utf-8').read(); t = s
    for a, b in REPL:
        t = t.replace(a, b)
    if t != s:
        n = sum(s.count(a) for a, _ in REPL)
        print(('DRY ' if dry else '') + f'{p}: {n} line fragment(s)')
        if not dry:
            shutil.copy2(p, p + '.bak-rename-' + stamp); open(p, 'w', encoding='utf-8').write(t)
        changed += 1
print(f'{changed} of {len(roots)} digests {"would change" if dry else "rewritten"}')
sys.exit(0 if changed else 1)
