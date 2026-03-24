# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.**

→ Rules: [RULES.md](RULES.md) · Beauty plan: [BEAUTY.md](BEAUTY.md) · History: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `main` — B-276 (BEAUTY) · F-217 (Prolog) concurrent
**HEAD:** `b76a81d` F-217 prolog (main) / `f721492` B-276 beauty (main)
**B-session:** M-BEAUTY-OMEGA ❌ — driver+ref ready (10/10 CSN+SPL); SPITBOL+SO crash: strip UTF-8 from driver comments
**F-session:** M-PROLOG-R10 ❌ — emitter bug fixed; puzzle_02 matches SWI-Prolog; puzzle_02 puzzle itself has singleton-var bug (Lon's WIP)
**Invariants:** 106/106 ASM corpus ALL PASS ✅

**⚡ CRITICAL NEXT ACTION — F-218 (M-PROLOG-R10):**

```bash
cd /home/claude/snobol4x && make -C src

# puzzle_01 PASS, puzzle_06 PASS, puzzle_02 matches SWI-Prolog.
# puzzle_02.pro has a singleton variable warning (line 18, doesEarnMore clause 3)
# and never prints WINNER — the puzzle logic itself is incomplete (Lon's WIP).
# puzzle_05.pro is also WIP.
#
# To fire M-PROLOG-R10: Lon must fix/complete puzzle_02 or declare current
# behaviour (matching SWI-Prolog) as PASS. Then update PLAN.md and advance
# to M-PROLOG-CORPUS (all 10 rungs via -pl -asm).
#
# Compile any puzzle:
# ./sno2c -pl test/frontend/prolog/corpus/rung10_programs/puzzle_NN.pro -o /tmp/t.c
# gcc -g -I src/frontend/prolog -o /tmp/t /tmp/t.c \
#     src/frontend/prolog/prolog_unify.c src/frontend/prolog/prolog_atom.c \
#     src/frontend/prolog/prolog_builtin.c -lm && /tmp/t
```

---

## Last Two Sessions (3 lines each)

**F-217 (2026-03-23) — emit_body cut-after-user-call bug fixed:**
`emit_body` emitted suffix goals `[!, fail]` with `ω=retry_lbl`, causing `fail` after cut to retry the user call instead of failing the predicate. Fix: scan suffix for E_CUT; goals after cut use outer ω. puzzle_01 PASS, puzzle_02 matches SWI-Prolog, puzzle_06 PASS. HEAD `b76a81d`.

**F-216 (2026-03-23) — compound emit \\n fix; rung09 PASS:**
Bug in `prolog_emit.c` line 185: `\\n` (literal backslash-n) emitted inside GNU statement expression for compound term construction; replaced with `\n`. Rung09 builtins now compile and match expected output exactly. HEAD `128dd2c`.

---

## Beauty Subsystem Status

See [BEAUTY.md](BEAUTY.md) for full sequence. Summary:
- ✅ 1–16: global/is/FENCE/io/case/assign/match/counter/stack/tree/SR/TDump/Gen/Qize/ReadWrite/XDump
- ❌ 17: semantic ← **now**
- ❌ 18: omega
- ❌ 19: trace
