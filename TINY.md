# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.**

→ Rules: [RULES.md](RULES.md) · Beauty plan: [BEAUTY.md](BEAUTY.md) · History: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `main` — B-276 (BEAUTY) · F-218 (Prolog) concurrent
**HEAD:** `80978ea` F-218 prolog (main) / `f721492` B-276 beauty (main)
**B-session:** M-BEAUTY-OMEGA ❌ — driver+ref ready (10/10 CSN+SPL); SPITBOL+SO crash: strip UTF-8 from driver comments
**F-session:** M-PROLOG-R10 ❌ — singleton-var bug fixed in puzzle_02.pro; puzzle_01/06 PASS; WINNER blocked pending Lon adding earnsMore facts
**Invariants:** 106/106 ASM corpus ALL PASS ✅

**⚡ CRITICAL NEXT ACTION — F-219 (M-PROLOG-R10):**

```bash
cd /home/claude/snobol4x && make -C src

# puzzle_01 PASS, puzzle_06 PASS.
# puzzle_02: doesEarnMore/3 clause 3 singleton bug fixed (earnsMore(X,Z)->earnsMore(Y,Z)).
# WINNER still not printed — puzzle_02 needs earnsMore(fuller, daw) fact (or chain)
# to satisfy doesEarnMore(Plumber=fuller, Painter=daw). Lon must supply this fact.
# puzzle_05: constraint checks commented out (all 24 permutations print). Lon's WIP.
#
# To fire M-PROLOG-R10: Lon adds missing earnsMore facts to puzzle_02 (and/or
# uncomments puzzle_05 constraints), then declare PASS.
#
# Compile any puzzle:
# ./sno2c -pl test/frontend/prolog/corpus/rung10_programs/puzzle_NN.pro -o /tmp/t.c
# gcc -g -I src/frontend/prolog -o /tmp/t /tmp/t.c \
#     src/frontend/prolog/prolog_unify.c src/frontend/prolog/prolog_atom.c \
#     src/frontend/prolog/prolog_builtin.c -lm && /tmp/t
```

---

## Last Two Sessions (3 lines each)

**F-218 (2026-03-23) — singleton var bug fixed in puzzle_02.pro:**
`doesEarnMore/3` clause 3 had `earnsMore(X,Y), earnsMore(X,Z)` — Y singleton, wrong pivot. Fixed to `earnsMore(X,Y), earnsMore(Y,Z)` for correct 2-hop transitivity. puzzle_01/06 still PASS. HEAD `80978ea`.

**F-217 (2026-03-23) — emit_body cut-after-user-call bug fixed:**
`emit_body` emitted suffix goals `[!, fail]` with `ω=retry_lbl`, causing `fail` after cut to retry the user call instead of failing the predicate. Fix: scan suffix for E_CUT; goals after cut use outer ω. puzzle_01 PASS, puzzle_02 matches SWI-Prolog, puzzle_06 PASS. HEAD `b76a81d`.

---

## Beauty Subsystem Status

See [BEAUTY.md](BEAUTY.md) for full sequence. Summary:
- ✅ 1–16: global/is/FENCE/io/case/assign/match/counter/stack/tree/SR/TDump/Gen/Qize/ReadWrite/XDump
- ❌ 17: semantic ← **now**
- ❌ 18: omega
- ❌ 19: trace
