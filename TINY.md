# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.**

→ Rules: [RULES.md](RULES.md) · Beauty plan: [BEAUTY.md](BEAUTY.md) · History: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `main` — B-276 (BEAUTY) · F-219 (Prolog) concurrent
**HEAD:** `0c2119a` F-219 prolog (main) / `f721492` B-276 beauty (main)
**B-session:** M-BEAUTY-OMEGA ❌ — driver+ref ready (10/10 CSN+SPL); SPITBOL+SO crash: strip UTF-8 from driver comments
**F-session:** M-PROLOG-R10 ❌ — puzzle_01/02/06 PASS with WINNER; puzzle_05 constraints commented out (Lon's WIP)
**Invariants:** 106/106 ASM corpus ALL PASS ✅

**⚡ CRITICAL NEXT ACTION — F-220 (M-PROLOG-R10):**

```bash
cd /home/claude/snobol4x && make -C src

# puzzle_01 PASS, puzzle_02 PASS (WINNER: Carpenter=clark Painter=daw Plumber=fuller), puzzle_06 PASS.
# puzzle_05: constraint checks still commented out — all 24 permutations print. Lon's WIP.
# To fire M-PROLOG-R10: uncomment puzzle_05 constraints and confirm single solution.
# \+ (negation-as-failure) likely needed for puzzle_05 — check if implemented.
#
# Compile any puzzle:
# ./sno2c -pl test/frontend/prolog/corpus/rung10_programs/puzzle_NN.pro -o /tmp/t.c
# gcc -g -I src/frontend/prolog -o /tmp/t /tmp/t.c \
#     src/frontend/prolog/prolog_unify.c src/frontend/prolog/prolog_atom.c \
#     src/frontend/prolog/prolog_builtin.c -lm && /tmp/t
```

---

## Last Two Sessions (3 lines each)

**F-219 (2026-03-23) — missing earnsMore fact added to puzzle_02.pro:**
`earnsMore(fuller, daw)` was absent; puzzle states plumber(fuller) > painter(daw) > clark. Added fact. WINNER now prints for `Carpenter:clark Painter:daw Plumber:fuller`. puzzle_01/06 still PASS. HEAD `0c2119a`.

**F-218 (2026-03-23) — singleton var bug fixed in puzzle_02.pro:**
`doesEarnMore/3` clause 3 had `earnsMore(X,Y), earnsMore(X,Z)` — Y singleton, wrong pivot. Fixed to `earnsMore(X,Y), earnsMore(Y,Z)` for correct 2-hop transitivity. puzzle_01/06 still PASS. HEAD `80978ea`.

---

## Beauty Subsystem Status

See [BEAUTY.md](BEAUTY.md) for full sequence. Summary:
- ✅ 1–16: global/is/FENCE/io/case/assign/match/counter/stack/tree/SR/TDump/Gen/Qize/ReadWrite/XDump
- ❌ 17: semantic ← **now**
- ❌ 18: omega
- ❌ 19: trace
