# PLAN.md — snobol4ever HQ

**Product:** SCRIP — SNOBOL4, Snocone, Rebus, Icon, Prolog. Ten times faster.
**Team:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6

---

## ⛔ SESSION START — every session, no exceptions


Lon names a goal. You:

1. Clone `.github`:
   ```bash
   git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github.git /home/claude/.github
   ```
2. Read `PLAN.md` (this file). Find the named goal in the table below.
3. Read `RULES.md` in full — commit rules, push rules, oracle, naming. No exceptions.
4. Open that Goal file. It names the repo. Open that repo's REPO file.
5. Run the scripts listed in the Goal file's `## Session Setup` section. If the Goal file has no `## Session Setup` yet, fall back to the matching category in `REPO-one4all.md ## Session Setup`.
6. Find the first incomplete Step (`- [ ]`) in the Goal file. Do it.

Do not read `archive/` unless a step explicitly says to.



---

## Active Goals

| Goal | File | Repo | Current Step | Done? |
|------|------|------|--------------|-------|
| SNOBOL4 Frontend Ladder | `GOAL-LANG-SNOBOL4.md` | one4all | SN-6 IN PROGRESS: PASS=215/228; next: 1113 array→table int key SM/JIT, 212, demo suite; HEAD 31bb2268 | ☐ |
| Icon Frontend Ladder | `GOAL-LANG-ICON.md` | one4all | IC-6 IN PROGRESS: rung01-29 PASS=156/156; next: rung16-29 recount | ☐ |
| Prolog Frontend Ladder | `GOAL-LANG-PROLOG.md` | one4all | PL-12 IN PROGRESS: SWI suite 71% (41/57); need 5 more for 80% gate; HEAD 372f5309 | ☐ |
| Raku Frontend Ladder | `GOAL-LANG-RAKU.md` | one4all | RK-47 next: last/next/redo; file I/O done, PASS=29 | ☐ |
| Rebus Frontend Ladder | `GOAL-LANG-REBUS.md` | one4all | RB-2 next (control flow verification) | ☐ |
| Unified Broker | `GOAL-UNIFIED-BROKER.md` | one4all | U-24 next (family.scrip cross-call demo) | ☐ |
| Raku Frontend | `GOAL-RAKU-FRONTEND.md` | one4all | RK-16 next (for @arr -> $x real array) | ☐ |
| Polyglot Calc Demo | `GOAL-POLYGLOT-CALC-DEMO.md` | one4all | PC-1 (Icon generator) | ☐ |
| Scrip Interp Split | `GOAL-SCRIP-INTERP-SPLIT.md` | one4all | IS-1 (create ir_interp.c) | ☐ |
| Snocone IR+BB | `GOAL-SNOCONE-IR-BB.md` | one4all | SC-1 (8/14 PASS; next: arith while-loop) | ☐ |
| Snocone Beauty | `GOAL-SNOCONE-BEAUTY.md` | one4all | SB-4 IN PROGRESS: PASS=42; BLOCKER: struct link dedup + Qize/TDump/omega; HEAD 9e81b9da | ☐ |
| Silly Forward Sweep | `GOAL-SILLY-SWEEP-FORWARD.md` | one4all | watermark 6927, next: RPLACE | ☐ |
| Silly Backward Sweep | `GOAL-SILLY-SWEEP-BACKWARD.md` | one4all | watermark 6427, next: CMA2 | ☐ |
| Silly Sync Monitor | `GOAL-SILLY-SYNC-MONITOR.md` | one4all | S-1 (infrastructure) | ☐ |
| Silly Complete | `GOAL-SILLY-COMPLETE.md` | one4all | P1-A1 (RECOMJ/CODER/CONVE) | ☐ |
| Prolog IR-run | `GOAL-PROLOG-IR-RUN.md` | one4all | S-10e next: assertz/retract/abolish | ☐ |
| Cross-Lang Verify | `GOAL-CROSS-LANG-VERIFY.md` | one4all | S-1 (prereq: Prolog Phase 1C) | ☐ |
| Sub-Expression Oracle | `GOAL-SUBEXPR-ORACLE.md` | one4all+corpus | S-2 (rewrite generator) | ☐ |
| Remove CMPILE | `GOAL-REMOVE-CMPILE.md` | one4all | S-7 (omega 15/15 ✅; next: S-7/S-8 gate) | ☐ |
| Two-Step Bug Hunt | `GOAL-TWO-STEP-HUNT.md` | one4all | S-1 (fix omega EVAL(string)) | ☐ |
| Scrip Beauty Suite | `GOAL-SCRIP-BEAUTY.md` | one4all | S-6 (ROOT CAUSE: spec_t→DESCR_t mismatch in stmt_exec.c) | ☐ |
| &STCOUNT All Languages | `GOAL-STCOUNT-ALL-LANGS.md` | one4all | ST-1 (audit keyword dispatch in interp.c) | ☐ |
| NET Beauty 18/18 | `GOAL-NET-BEAUTY-19.md` | snobol4dotnet | S-8B (error 22 open: MSIL PushExpr index misalignment) | ☐ |
| NET Beauty Self-Host | `GOAL-NET-BEAUTY-SELF.md` | snobol4dotnet | S-2 IN PROGRESS: beauty 17/17; next: Reduce(Stmt,7) crash; HEAD ec59eeb | ☐ |
| NET Snippets | `GOAL-NET-SNIPPETS.md` | snobol4dotnet | S-1 (@N fix) | ☐ |
| NET Optimize | `GOAL-NET-OPTIMIZE.md` | snobol4dotnet | S-1 (ExecutionCache) | ☐ |
| NET DATATYPE Lowercase | `GOAL-NET-DATATYPE-LOWERCASE.md` | snobol4dotnet | S-1 (unit test) | ☐ |
| No Symlinks | `GOAL-NO-SYMLINKS.md` | corpus/harness/all | S-1 (audit) | ☐ |
| DATATYPE Portable Tests | `GOAL-DATATYPE-PORTABLE-TESTS.md` | corpus | S-1 (audit) | ☐ |
| READMEs (all repos) | GOAL-README-*.md | various | S-1 (audit) — profile, one4all, dotnet, jvm, corpus, harness, python, csharp, artifact | ☐ |

---

## Repos

| Repo | File |
|------|------|
| one4all | `REPO-one4all.md` |
| snobol4dotnet | `REPO-snobol4dotnet.md` |
| snobol4jvm | `REPO-snobol4jvm.md` |
| snobol4python | `REPO-snobol4python.md` |
| snobol4csharp | `REPO-snobol4csharp.md` |
| csnobol4 | `REPO-csnobol4.md` |
| corpus | `REPO-corpus.md` |
| harness | `REPO-harness.md` |

---

## Oracle

**SPITBOL x64 is the primary oracle for all testing.** Use `/home/claude/x64/bin/sbl`. See RULES.md for details.

---

## Architecture (one paragraph)

Every frontend (SNOBOL4, Icon, Prolog, Snocone, Rebus, Scrip) produces the shared IR.
SM-LOWER compiles IR to SM_Program — a flat array of stack machine instructions.
The INTERP executes SM_Program. The EMITTER walks SM_Program and emits native code
(x86, JVM, .NET, JS, WASM). Interpreter and emitter share one instruction set.

---

*archive/ holds all prior HQ docs. Full git history is the permanent record.*
*RULES.md — commit identity, handoff checklist, oracle, naming conventions.*

---

## Session trigger phrases

| Lon says | Meaning |
|----------|---------|
| "perform hand off" | End of session — update goal state, commit all repos, push .github last, write clear commit message |
| "perform emergency hand off" | Same as above but something is broken or incomplete — note the breakage explicitly in the commit message and goal file state |
| "here we go" | Session is starting — Lon has named a goal, proceed with session start protocol |
| "grand master reorg" | HQ system work — the goal is improving the HQ itself |
