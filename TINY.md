# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.**

→ Rules: [RULES.md](RULES.md) · Beauty plan: [BEAUTY.md](BEAUTY.md) · History: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `main` — B-276 (BEAUTY) · F-220 (Prolog) concurrent
**HEAD:** `5e6b872` F-220 prolog (main) / `f721492` B-276 beauty (main)
**B-session:** M-BEAUTY-OMEGA ❌ — driver+ref ready (10/10 CSN+SPL); SPITBOL+SO crash: strip UTF-8 from driver comments
**F-session:** M-PROLOG-R10 ✅ — all 4 puzzles PASS (01/02/05/06); \+ NAF implemented
**Invariants:** 106/106 ASM corpus ALL PASS ✅

**⚡ CRITICAL NEXT ACTION — F-221 (M-PROLOG-CORPUS):**

```bash
cd /home/claude/snobol4x && make -C src

# All rung10 puzzles PASS:
#   puzzle_01: Cashier=smith Manager=brown Teller=jones ✅
#   puzzle_02: WINNER Carpenter:clark Painter:daw Plumber:fuller ✅
#   puzzle_05: Accountant=jones Cashier=brown Manager=clark President=smith ✅
#   puzzle_06: Clark=druggist Jones=grocer Morgan=butcher Smith=policeman ✅
#
# M-PROLOG-R10 fires. Next: M-PROLOG-CORPUS — all 10 rungs PASS via -pl (C backend).
# Compile any puzzle:
# ./sno2c -pl test/frontend/prolog/corpus/rung10_programs/puzzle_NN.pro -o /tmp/t.c
# gcc -g -I src/frontend/prolog -o /tmp/t /tmp/t.c \
#     src/frontend/prolog/prolog_unify.c src/frontend/prolog/prolog_atom.c \
#     src/frontend/prolog/prolog_builtin.c -lm && /tmp/t
```

---

## Last Two Sessions (3 lines each)

**F-220 (2026-03-23) — \+ NAF implemented; puzzle_05 PASS:**
`\+` in `prolog_emit.c` was a stub (always succeeded). Fixed: copies trail, tries subgoal via `_r` call, unwinds, succeeds iff subgoal failed. Added missing `betterAtChess(brown,smith/jones)` facts to puzzle_05. Single solution prints. M-PROLOG-R10 ✅. HEAD `5e6b872`.

**F-219 (2026-03-23) — missing earnsMore fact added to puzzle_02.pro:**
`earnsMore(fuller, daw)` was absent. Added. WINNER now prints for `Carpenter:clark Painter:daw Plumber:fuller`. puzzle_01/06 still PASS. HEAD `0c2119a`.

---

## Beauty Subsystem Status

See [BEAUTY.md](BEAUTY.md) for full sequence. Summary:
- ✅ 1–16: global/is/FENCE/io/case/assign/match/counter/stack/tree/SR/TDump/Gen/Qize/ReadWrite/XDump
- ❌ 17: semantic ← **now**
- ❌ 18: omega
- ❌ 19: trace
