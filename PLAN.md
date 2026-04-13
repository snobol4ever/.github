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
5. Follow the REPO file `## Session Start` section to clone and build.
6. Find the first incomplete Step (`- [ ]`) in the Goal file. Do it.

Do not read `archive/` unless a step explicitly says to.



---

## Active Goals

| Goal | File | Repo | Current Step | Done? |
|------|------|------|--------------|-------|
| Silly Forward Sweep | `GOAL-SILLY-SWEEP-FORWARD.md` | one4all | watermark 6927 → next: RPLACE | ☐ |
| Silly Backward Sweep | `GOAL-SILLY-SWEEP-BACKWARD.md` | one4all | watermark 6427 → next: CMA2 | ☐ |
| Silly Sync Monitor | `GOAL-SILLY-SYNC-MONITOR.md` | one4all | S-1 (infrastructure) | ☐ |
| Silly Complete | `GOAL-SILLY-COMPLETE.md` | one4all | P1-A1 (RECOMJ/CODER/CONVE) | ☐ |
| Icon IR-run | `GOAL-ICON-IR-RUN.md` | one4all | S-7 (find() generator; 47/59 PASS) | ☐ |
| Prolog IR-run | `GOAL-PROLOG-IR-RUN.md` | one4all | S-10d (findall/3; Phase 1B complete) | ☐ |
| Snocone Beauty | `GOAL-SNOCONE-BEAUTY.md` | one4all | S-5 (fix subsystem failures; 3/14 PASS) | ☐ |
| Sub-Expression Oracle | `GOAL-SUBEXPR-ORACLE.md` | one4all+corpus | S-2 (rewrite generator: subsystem files, full grammar, two-run protocol) | ☐ |
| Remove CMPILE | `GOAL-REMOVE-CMPILE.md` | one4all | S-1 (fix parse_expr_pat_from_str: pass src direct, return subject/pattern) | ☐ |
| Two-Step Bug Hunt | `GOAL-TWO-STEP-HUNT.md` | one4all | S-1 (fix omega EVAL(string) via interp_eval_pat) | ☐ |
| Scrip Beauty Suite | `GOAL-SCRIP-BEAUTY.md` | one4all | S-6 (parser fix done; E_INDIRECT capture write-back bug — BREAK captures empty, REM write-back silent) | ☐ |
| NET Beauty 18/18 | `GOAL-NET-BEAUTY-19.md` | snobol4dotnet | S-8B (omega *LEQ EVAL star-slot — error 248 fixed, error 22 open: MSIL PushExpr index misalignment after semantic.sno load-time EVALs) | ☐ |
| NET Beauty Self-Host | `GOAL-NET-BEAUTY-SELF.md` | snobol4dotnet | S-1 (diagnose error 021) | ☐ |
| NET Snippets | `GOAL-NET-SNIPPETS.md` | snobol4dotnet | S-1 (@N fix) | ☐ |
| NET Optimize | `GOAL-NET-OPTIMIZE.md` | snobol4dotnet | S-1 (ExecutionCache) | ☐ |
| No Symlinks | `GOAL-NO-SYMLINKS.md` | corpus/harness/all | S-1 (audit corpus) | ☐ |
| NET DATATYPE Lowercase | `GOAL-NET-DATATYPE-LOWERCASE.md` | snobol4dotnet | S-1 (unit test) | ☐ |
| DATATYPE Portable Tests | `GOAL-DATATYPE-PORTABLE-TESTS.md` | corpus | S-1 (audit) | ☐ |
| Remove CMPILE | `GOAL-REMOVE-CMPILE.md` | one4all | S-3 (CODE() builtin; S-1/S-2 done) | ☐ |
| SNOBOL4 Pat IR | `GOAL-SNOBOL4-PAT-IR.md` | one4all | S-2 (grammar actions done; S-1 skipped) | ☐ |
| README: profile | `GOAL-README-PROFILE.md` | .github | S-1 (audit) | ☐ |
| README: one4all | `GOAL-README-ONE4ALL.md` | one4all | S-1 (audit) | ☐ |
| README: snobol4dotnet | `GOAL-README-SNOBOL4DOTNET.md` | snobol4dotnet | S-1 (audit) | ☐ |
| README: snobol4jvm | `GOAL-README-SNOBOL4JVM.md` | snobol4jvm | S-1 (audit) | ☐ |
| README: corpus | `GOAL-README-CORPUS.md` | corpus | S-1 (audit) | ☐ |
| README: harness | `GOAL-README-HARNESS.md` | harness | S-1 (audit) | ☐ |
| README: snobol4python | `GOAL-README-SNOBOL4PYTHON.md` | snobol4python | S-1 (audit) | ☐ |
| README: snobol4csharp | `GOAL-README-SNOBOL4CSHARP.md` | snobol4csharp | S-1 (audit) | ☐ |
| README: snobol4artifact | `GOAL-README-SNOBOL4ARTIFACT.md` | snobol4artifact | S-1 (audit) | ☐ |
| CSNOBOL4 FENCE(P) | `GOAL-CSNOBOL4-FENCE.md` | csnobol4 | DONE | ☑ |
| CSNOBOL4 Harness | `GOAL-CSNOBOL4-HARNESS.md` | harness | S-9 complete + scrip-cc→scrip | ☑ |
| Archive Cleanup | `GOAL-ARCHIVE-CLEANUP.md` | .github | S-12 complete | ☑ |

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
