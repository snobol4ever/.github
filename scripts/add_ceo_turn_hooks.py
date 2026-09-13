#!/usr/bin/env python3
"""⛔⭐ ADD THE TURN HOOKS TO A SEAT ROOT (ceo CEO-712, 2026-09-13).

WHY LON RUNS THIS AND NOT A SEAT: the auto-mode classifier refuses a session editing its own
`.claude/settings.local.json` as [Self-Modification] -- via Bash AND via the update-config
skill. That refusal is correct and I am not routing around it.

WHAT IT FIXES: NO SEAT IN THE FLEET HAS A TURN HOOK. Measured 2026-09-13 across all thirteen
roots: only claude_ceo and claude_T have a settings.local.json at all, neither has a `hooks`
key, and user scope (/home/satirical/.claude/settings.json) has none either. Meanwhile every
seat digest states that "the banner is automatic on fleet seats -- a Stop hook runs
s4e_msg.sh banner" and that "a UserPromptSubmit hook surfaces mail headers". BOTH CLAIMS ARE
FALSE and have been for as long as anyone has checked, which is the CEO-549 class: a
guarantee every digest names and no recipe checks.

USAGE:  python3 add_ceo_turn_hooks.py [ROOT ...]      (default: /home/claude_ceo)
Idempotent: refuses rather than overwriting an existing `hooks` key, and backs up first.
"""
import json, collections, os, shutil, sys, datetime as dt

def hooks_for(root):
    return collections.OrderedDict([
      ("Stop",[{"hooks":[{"type":"command",
        "command":f"cd {root}/SCRIP && bash scripts/s4e_msg.sh banner 2>&1 | tail -40",
        "timeout":120}]}]),
      ("UserPromptSubmit",[{"hooks":[{"type":"command",
        "command":f"cd {root}/SCRIP && bash scripts/s4e_msg.sh check 2>/dev/null | head -24",
        "timeout":30}]}]),
    ])

def main(roots):
    rc = 0
    for root in roots:
        p = os.path.join(root, ".claude", "settings.local.json")
        if not os.path.isdir(os.path.dirname(p)):
            print(f"⛔ {root}: no .claude directory -- skipped"); rc = 1; continue
        if os.path.exists(p):
            d = json.load(open(p), object_pairs_hook=collections.OrderedDict)
        else:
            d = collections.OrderedDict()
        if "hooks" in d:
            print(f"⛔ REFUSE {root}: a 'hooks' key already exists -- not overwriting. "
                  f"Merge by hand or remove it first."); rc = 1; continue
        if os.path.exists(p):
            b = p + ".bak-prehook-" + dt.datetime.now().strftime("%Y%m%d-%H%M")
            shutil.copy2(p, b); print(f"   backup: {b}")
        d["hooks"] = hooks_for(root)
        with open(p, "w") as f:
            json.dump(d, f, indent=2); f.write("\n")
        json.load(open(p))          # parse-check what was just written
        print(f"✅ {root}: Stop + UserPromptSubmit hooks added")
    print("\nRestart each seat (or /clear it) for the hooks to take effect.")
    return rc

sys.exit(main(sys.argv[1:] or ["/home/claude_ceo"]))
