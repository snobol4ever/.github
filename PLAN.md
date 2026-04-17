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
| In-Process Sync Monitor | `GOAL-INPROC-MONITOR.md` | one4all | IM-16 DONE: beauty smoke script added; AGREE=12 DIVERGE=3 SKIP=2; known divergences: loop_count stmt 4, array/table stmt 8 | ☑ |
| &STCOUNT All Languages | `GOAL-STCOUNT-ALL-LANGS.md` | one4all | ST-1 next (audit keyword dispatch in interp.c) | ☐ |
| SNOBOL4 Frontend Ladder | `GOAL-LANG-SNOBOL4.md` | one4all | SN-6 IN PROGRESS: PASS=218/228; two --ir-run fixes landed (E_SEQ/E_CAT stale-acc on mode switch + E_ALT value-ctx); expr_eval now blocked on Bug #1c (XCALLCAP passes wrong matched text); smoke PASS=7, broker PASS=49 | ☠ |
| SNO treebank-array | `GOAL-SNO-TREEBANK-ARRAY.md` | one4all | TA-1 DONE (landed via C5 session HEAD 6ee09b7f); TA-2 next | ☐ |
| SNO treebank-list | `GOAL-SNO-TREEBANK-LIST.md` | one4all | TL-2 IN PROGRESS: prior callcap hypothesis disproved; new root cause: FUNC_*_fn accessors in snobol4.c use strcasecmp, so Push_list dispatches via push_list's entry_label — wrong body runs. Fix: strcasecmp→strcmp in snobol4.c:2826-2877 (six accessors). 22-line repro captured in goal file. | ☐ |
| SNO claws5 | `GOAL-SNO-CLAWS5.md` | one4all | C5-3 DONE: bb_seq left_γ accumulation fixed; full 989-line input now exits 0 with 5622 lines (was SEGV); C5-4 PARTIAL (typed sort landed; _aset_impl still stringifies int keys — next: route through table_set_descr); HEAD 2fa59c88 | ☐ |
| Icon Frontend Ladder | `GOAL-LANG-ICON.md` | one4all | IC-7 IN PROGRESS: rung30 5/5, rung31 5/5, rung33 5/5, rung34 5/5, rung35 7/7; rung32 4/5 open (strret_every); broker PASS=49; HEAD 9eb8c669 | ☐ |
| Prolog Frontend Ladder | `GOAL-LANG-PROLOG.md` | one4all | PL-12 IN PROGRESS: 71% (41/57); suite scripts + plunit.pl v2 patch committed; BLOCKER: cut scope drops length verdict; next: once() fix + catch(Var) fix; HEAD 0d112d50 | ☐ |
| Raku Frontend Ladder | `GOAL-LANG-RAKU.md` | one4all | RK-34 next: positional captures ($0, $1); RK-32/RK-33 done: table-driven NFA compiler + simulator, PASS=24 all 3 modes | ☐ |
| Snocone Frontend Ladder | `GOAL-LANG-SNOCONE.md` | one4all+corpus | SC-26 next: fix (PAT . var) . *fn(var) arg eval order; treebank .sc pp_node clean (no branches, pprint-exact); corpus HEAD 71bedd0 | ☐ |
| Snocone claws5.sc | `GOAL-SNOCONE-CLAWS5.md` | one4all+corpus | CL-2 next: fix SC-26 — find callcap box in bb_boxes.c/snobol4_pattern.c, trace (PAT . var) . *fn(var) lowering through snocone_lower→IR→bb_build; then rewrite pp_mem in claws5.sc to match .sno pp_mem format | ☐ |
| Snocone treebank-list.sc | `GOAL-SNOCONE-TREEBANK-LIST.md` | one4all+corpus | TB-1 DONE: SC-26 fully diagnosed (3 bugs); Bugs 1+2 fixed; Bug 3 (bb_callcap spec_t return) pending TB-2 | ☐ |
| Rebus Frontend Ladder | `GOAL-LANG-REBUS.md` | one4all | RB-2 next (control flow verification) | ☐ |
| Full Integration | `GOAL-FULL-INTEGRATION.md` | one4all | ALL STEPS DONE (FI-8..FI-11 complete) | ☑ |
| Unified Broker | `GOAL-UNIFIED-BROKER.md` | one4all | U-24 next (family.scrip cross-call demo) | ☐ |
| One Eval | `GOAL-ONE-EVAL.md` | one4all | DONE | ☑ |
| Raku Frontend | `GOAL-RAKU-FRONTEND.md` | one4all | RK-16 next (for @arr -> $x real array); RK-15 done: hashes %h<key>/%h{$k}, PASS=12, smoke PASS=30 | ☐ |
| Polyglot Calc Demo | `GOAL-POLYGLOT-CALC-DEMO.md` | one4all | PC-1 (Icon generator) | ☐ |
| Session Setup Refinement | `GOAL-SESSION-SETUP-REFINEMENT.md` | .github + one4all | DONE | ☑ |
| Self-Contained Scripts | `GOAL-SELF-CONTAINED-SCRIPTS.md` | one4all | DONE | ☑ |
| Scrip Interp Split | `GOAL-SCRIP-INTERP-SPLIT.md` | one4all | IS-1 (create ir_interp.c) | ☐ |
| Snocone IR+BB | `GOAL-SNOCONE-IR-BB.md` | one4all | SC-1 continued (8/14 PASS; next: arith while-loop integer iteration) | ☐ |
| Silly Forward Sweep | `GOAL-SILLY-SWEEP-FORWARD.md` | one4all | watermark 6927 → next: RPLACE | ☐ |
| Silly Backward Sweep | `GOAL-SILLY-SWEEP-BACKWARD.md` | one4all | watermark 6427 → next: CMA2 | ☐ |
| Silly Sync Monitor | `GOAL-SILLY-SYNC-MONITOR.md` | one4all | S-1 (infrastructure) | ☐ |
| Silly Complete | `GOAL-SILLY-COMPLETE.md` | one4all | P1-A1 (RECOMJ/CODER/CONVE) | ☐ |
| Icon IR-run | `GOAL-ICON-IR-RUN.md` | one4all | S-12 DONE (59/59; broker pivot → GOAL-ICN-BROKER) | ☑ |
| Icon Gen Broker | `GOAL-ICN-BROKER.md` | one4all | B-11 DONE | ☑ |
| Prolog IR-run | `GOAL-PROLOG-IR-RUN.md` | one4all | rung01-11 14/14 PASS, next: S-10e assertz/retract/abolish | ☐ |
| Prolog BB Byrd | `GOAL-PROLOG-BB-BYRD.md` | one4all | DONE | ☑ |
| Cross-Lang Verify | `GOAL-CROSS-LANG-VERIFY.md` | one4all | S-1 (prerequisite: Prolog Phase 1C) | ☐ || Snocone Beauty | `GOAL-SNOCONE-BEAUTY.md` | one4all | PIVOT: no assembly/awk/Python; write clean per-subsystem .sc files by hand; SB-4 next; HEAD 311ec18c | ☐ |
| Snocone Demos | `GOAL-SNOCONE-DEMOS.md` | one4all | SD-1 BROKEN: treebank.sno *group self-ref not deferred; fix -INCLUDE stack.sno/counter.sno + recursion | ☐ |
| Snocone Demos | `GOAL-SNOCONE-DEMOS.md` | one4all | SD-1 BROKEN: treebank.sno *group self-ref not deferred; fix -INCLUDE stack.sno/counter.sno + recursion | ☐ |
| Sub-Expression Oracle | `GOAL-SUBEXPR-ORACLE.md` | one4all+corpus | S-2 (rewrite generator: subsystem files, full grammar, two-run protocol) | ☐ |
| Remove CMPILE | `GOAL-REMOVE-CMPILE.md` | one4all | S-7 (omega 15/15 ✅ — S-1..S-6 done; next: confirm S-7/S-8 gate, rebuild after prolog_interp.h fix) | ☐ |
| Two-Step Bug Hunt | `GOAL-TWO-STEP-HUNT.md` | one4all | S-1 (fix omega EVAL(string) via interp_eval_pat) | ☐ |
| Scrip Beauty Suite | `GOAL-SCRIP-BEAUTY.md` | one4all | S-6 (ROOT CAUSE: bb_box_fn spec_t→DESCR_t mismatch breaks ALL captures in --ir-run; fix spec_from_descr call site in stmt_exec.c Phase 3) | ☐ |
| NET Beauty 18/18 | `GOAL-NET-BEAUTY-19.md` | snobol4dotnet | S-8B (omega *LEQ EVAL star-slot — error 248 fixed, error 22 open: MSIL PushExpr index misalignment after semantic.sno load-time EVALs) | ☐ |
| NET Beauty Self-Host | `GOAL-NET-BEAUTY-SELF.md` | snobol4dotnet | S-2 IN PROGRESS: beauty 17/17; Data.cs hardened (FRETURN on PatternVar); self-host reaches Parse Error on START; next: instrument Reduce() xTrace to find bad Stmt slot; HEAD 1c27d52 | ☐ |
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
