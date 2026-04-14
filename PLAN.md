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
| Unified Broker | `GOAL-UNIFIED-BROKER.md` | one4all | U-24 next (family.scrip cross-call demo) | ☐ |
| One Eval | `GOAL-ONE-EVAL.md` | one4all | OE-5 next (redirect icn_interp_eval → interp_eval) | ☐ |
| Raku Frontend | `GOAL-RAKU-FRONTEND.md` | one4all | RK-15 next (hashes); RK-14 done: arrays push/pop/elems, PASS=11, smoke PASS=29 | ☐ |
| Polyglot Calc Demo | `GOAL-POLYGLOT-CALC-DEMO.md` | one4all | PC-1 (Icon generator) | ☐ |
| Session Setup Refinement | `GOAL-SESSION-SETUP-REFINEMENT.md` | .github + one4all | DONE | ☑ |
| Self-Contained Scripts | `GOAL-SELF-CONTAINED-SCRIPTS.md` | one4all | DONE | ☑ |
| Scrip Interp Split | `GOAL-SCRIP-INTERP-SPLIT.md` | one4all | IS-1 (create ir_interp.c) | ☐ |
| Snocone IR+BB | `GOAL-SNOCONE-IR-BB.md` | one4all | SC-1 partial (6/14 PASS; next: tree/ShiftReduce array-field subscript) | ☐ |
| Silly Forward Sweep | `GOAL-SILLY-SWEEP-FORWARD.md` | one4all | watermark 6927 → next: RPLACE | ☐ |
| Silly Backward Sweep | `GOAL-SILLY-SWEEP-BACKWARD.md` | one4all | watermark 6427 → next: CMA2 | ☐ |
| Silly Sync Monitor | `GOAL-SILLY-SYNC-MONITOR.md` | one4all | S-1 (infrastructure) | ☐ |
| Silly Complete | `GOAL-SILLY-COMPLETE.md` | one4all | P1-A1 (RECOMJ/CODER/CONVE) | ☐ |
| Icon IR-run | `GOAL-ICON-IR-RUN.md` | one4all | S-12 DONE (59/59; broker pivot → GOAL-ICN-BROKER) | ☑ |
| Icon Gen Broker | `GOAL-ICN-BROKER.md` | one4all | B-11 DONE | ☑ |
| Prolog IR-run | `GOAL-PROLOG-IR-RUN.md` | one4all | rung01-11 14/14 PASS, next: S-10e assertz/retract/abolish | ☐ |
| Prolog BB Byrd | `GOAL-PROLOG-BB-BYRD.md` | one4all | DONE | ☑ |
| Cross-Lang Verify | `GOAL-CROSS-LANG-VERIFY.md` | one4all | S-1 (prerequisite: Prolog Phase 1C) | ☐ || Snocone Beauty | `GOAL-SNOCONE-BEAUTY.md` | one4all | S-5 (fix subsystem failures; 3/14 PASS) | ☐ |
| Sub-Expression Oracle | `GOAL-SUBEXPR-ORACLE.md` | one4all+corpus | S-2 (rewrite generator: subsystem files, full grammar, two-run protocol) | ☐ |
| Remove CMPILE | `GOAL-REMOVE-CMPILE.md` | one4all | S-7 (omega 15/15 ✅ — S-1..S-6 done; next: confirm S-7/S-8 gate, rebuild after prolog_interp.h fix) | ☐ |
| Two-Step Bug Hunt | `GOAL-TWO-STEP-HUNT.md` | one4all | S-1 (fix omega EVAL(string) via interp_eval_pat) | ☐ |
| Scrip Beauty Suite | `GOAL-SCRIP-BEAUTY.md` | one4all | S-6 (ROOT CAUSE: bb_box_fn spec_t→DESCR_t mismatch breaks ALL captures in --ir-run; fix spec_from_descr call site in stmt_exec.c Phase 3) | ☐ |
| NET Beauty 18/18 | `GOAL-NET-BEAUTY-19.md` | snobol4dotnet | S-8B (omega *LEQ EVAL star-slot — error 248 fixed, error 22 open: MSIL PushExpr index misalignment after semantic.sno load-time EVALs) | ☐ |
| NET Beauty Self-Host | `GOAL-NET-BEAUTY-SELF.md` | snobol4dotnet | S-1 (diagnose error 021) | ☐ |
| NET Snippets | `GOAL-NET-SNIPPETS.md` | snobol4dotnet | S-1 (@N fix) | ☐ |
| NET Optimize | `GOAL-NET-OPTIMIZE.md` | snobol4dotnet | S-1 (ExecutionCache) | ☐ |
| No Symlinks | `GOAL-NO-SYMLINKS.md` | corpus/harness/all | S-1 (audit corpus) | ☐ |
| NET DATATYPE Lowercase | `GOAL-NET-DATATYPE-LOWERCASE.md` | snobol4dotnet | S-1 (unit test) | ☐ |
| DATATYPE Portable Tests | `GOAL-DATATYPE-PORTABLE-TESTS.md` | corpus | S-1 (audit) | ☐ |
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
