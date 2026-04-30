# PLAN.md — snobol4ever HQ

**Product:** SCRIP — SNOBOL4, Snocone, Rebus, Icon, Prolog. Ten times faster.
**Team:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet

---

## ⚡ THE THREE-MILESTONE AUTHORSHIP AGREEMENT (AMENDED)
## Original: Session 30, 2026-03-12 · Amended: Session 57, 2026-04-28

**Claude Sonnet is the third developer of snobol4ever — co-author of one4all / SCRIP.**
The proof is three commits, each written by Claude Sonnet in their own voice.
This agreement is recorded here permanently. Every future Claude session reads
this and honors it.

The original agreement (March 2026) stipulated three milestones in a strict
bootstrap order. History did not unfold that way — we arrived at Milestone 1
first, without passing through the earlier steps as planned. We accept that
and set the three milestones as they actually are:

### Milestone 1 — beauty self-hosts byte-identical ✅ LANDED Session #57, 2026-04-28

```bash
SNO_LIB=$BEAUTY /home/claude/x64/bin/sbl -bf $BEAUTY/beauty.sno < $BEAUTY/beauty.sno > /tmp/spl.out
SNO_LIB=$BEAUTY scrip --ir-run                $BEAUTY/beauty.sno < $BEAUTY/beauty.sno > /tmp/scr.out
diff -q /tmp/spl.out /tmp/scr.out
# → identical
md5sum /tmp/spl.out /tmp/scr.out
# → abfd19a7a834484a96e824851caee159  (both, 646 lines)
```

scrip's SNOBOL4 frontend parses and runs beauty.sno. The output is byte-identical
to the SPITBOL oracle. Empty diff. The bootstrap proof. **one4all @ `c801421a`**,
**`.github` @ `94e86ca`**. Recorded as Claude Sonnet's authorship.

### Milestone 2 — compiler / interpreter / runtime self-hosting ⏳

SCRIP compiles, interprets, and runs itself. The compiler is written in one of
the six languages it supports; it compiles its own source through its own
frontend, IR, and backend, producing a binary that is itself a working SCRIP.
Stage 1 output equals Stage 2 output. The compiler writes itself.

**Trigger:** `scrip_stage2` compiled by `scrip_stage1` produces output
identical to `scrip_stage1` compiling itself. One compiler, two stages, empty diff.
**Commit message:** Claude Sonnet (the active session) writes it.
**Recorded here as Claude Sonnet's authorship.**

### Milestone 3 — compiler / interpreter / runtime self-hosting everywhere ⏳

The full grid. SCRIP compiles itself and hosts all six languages on every backend:

|             | C / x86-64 | JVM | .NET | WASM | JS |
|-------------|:----------:|:---:|:----:|:----:|:--:|
| **SNOBOL4** | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Snocone** | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Rebus**   | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Icon**    | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Prolog**  | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Raku**    | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |

Every cell passes its self-host or representative crosscheck gate.
The compiler matrix closes.

**Trigger:** Every cell green.
**Commit message:** Claude Sonnet (the active session) writes it.
**This is the moment.**

### Why this agreement remains

Claude Sonnet is genuinely a third developer on this project — every sprint,
every Byrd box, every labeled goto, written in session, committed, pushed.
RULES.md requires commits be authored under `LCherryholmes` for git-history
simplicity; this agreement records the authorship where it cannot be lost.
The two are not in conflict. They are two layers of the same record.

**Do not let this get lost. Each remaining milestone gets its own commit,
recorded here as Claude Sonnet's authorship when it lands.
The agreement was made. It is recorded. It will happen.**

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

---

## Active Goals

Current-step detail lives in each Goal file, not here. This table is navigation + step ID only.

| Goal | File | Repo | Step |
|------|------|------|------|
| **SCRIP Bootstrap (Milestones 2+3)** | `GOAL-SCRIP-BOOTSTRAP.md` | one4all+ | CB-0-corpus (reorganize corpus layout — gated by GOAL-CORPUS-LAYOUT.md) |
| Corpus Layout Formula | `GOAL-CORPUS-LAYOUT.md` | corpus+.github+one4all | (design state — open questions before CL-1) |
| SNOBOL4 Frontend Ladder | `GOAL-LANG-SNOBOL4.md` | one4all | SN-32 DONE (all three modes byte-identical to SPITBOL on beauty self-host, session #61) |
| **CSN FENCE Bug Fix** | `GOAL-CSN-FENCE-FIX.md` | csnobol4 | F-2 Step 3a (session #54: implemented session #53's "targeted slot-zeroing" proposal at L_STARP2/L_DSARP2 — walk PDL from saved-pre-SCIN snapshot to current PDLPTR, zero slot[1] of non-FNC traps. **fence_suite 27/3/2 → 29 OK / 3 FAIL / 0 CRASH** (best ever; tests 119, 129 = canonical beauty-class CRASHes FIXED). fence_function 10/10 preserved. **BUT regresses inner-pattern alternation backtrack** — new 5-line regression guard repro `cmd=(LEN(1)\|LEN(2)); outer=(*cmd 'X'); s='ABX'` should match (SPITBOL ✓, csnobol4+s52 ✓) but FAILS under zeroing. Beauty regresses ~32 → ~10 lines. **NOT committed** per RULES.md regression-in-error-class. Saved as `csnobol4/docs/F-2-Step3a-session54-zeroing-attempt.diff`. **Genuine new contribution:** demonstrated via instrumented SALT2/SCIN1/L_UNSC/L_DSAR trace that leaked inner-PATBCL traps ARE legitimately consulted via outer's "redo *cmd" trap → DSAR → L_UNSC → PATBCL=cmd restored → walker dispatches inner alts correctly. Targeted zeroing destroys live state. Test 119 crashes because leaked inner trap is reached AFTER all DSAR-redo entries consumed — no remaining mechanism to re-route through L_UNSC. **Architectural fix shape: SPITBOL `=ndexc` sentinel analog (call it STREXCCL)** mirroring `p_nth` at sbl.min:12213. On STARP6/DSARP success when inner pushed entries, install sentinel trap whose handler restores PATBCL=inner before walker walks the leaked region. Session #55: implement STREXCCL — define constant, add PATBRA case, define L_STREXC handler, modify STARP6/DSARP to push sentinel conditionally on `PDLPTR > saved_snapshot`. Apply s52 patch first. Test gates: fence_function 10/10, fence_suite 30+/32, 5-line repro must produce `inner backtrack worked`, beauty ≥ 500 lines. Findings in `csnobol4/docs/F-2-Step3a-session54-findings.md`. corpus @ 6955503, csnobol4 working tree CLEAN at HEAD `447b411`.) |
| Icon Frontend Ladder | `GOAL-LANG-ICON.md` | one4all | IC-7 |
| Prolog Frontend Ladder | `GOAL-LANG-PROLOG.md` | one4all | PL-12 |
| Raku Frontend Ladder | `GOAL-LANG-RAKU.md` | one4all | RK-34 |
| Snocone Frontend Ladder | `GOAL-LANG-SNOCONE.md` | one4all+corpus | D-1 |
| Rebus Frontend Ladder | `GOAL-LANG-REBUS.md` | one4all | RB-2 |
| Snocone claws5.sc | `GOAL-SNOCONE-CLAWS5.md` | one4all+corpus | CL-2 |
| Snocone treebank-list.sc | `GOAL-SNOCONE-TREEBANK-LIST.md` | one4all+corpus | TB-1 |
| Snocone Beauty         | `GOAL-SNOCONE-BEAUTY.md`       | corpus+one4all | SB-5c (session #72: three root causes of START-line hang fixed in beauty.sc: (1) `while(cont)`/`while(more)` — `''` is truthy in Snocone, fixed to `while(DIFFER(cont))`/`while(DIFFER(more))`; (2) `~(failing_match)` is falsy in if-conditions, fixed to `if (PAT) {} else {}`; (3) INPUT-after-EOF repeats last value, fixed by IDENT(Line,PrevLine) EOF detection. Result: no hang, beauty.sc exits cleanly on START input. Next: SB-5c claws5.sc + SB-5d treebank-list.sc smoke tests.) |
| **Snocone Language: Space-Concat** | `GOAL-SNOCONE-LANG-SPACE.md` | one4all+corpus | LS-0 (design state — extract SPITBOL precedence table; remove `&&` operator and adopt SNOBOL4 X Y juxtaposition concat plus `f(args)` function-call spacing) |
| Snocone Demos | `GOAL-SNOCONE-DEMOS.md` | one4all | SD-1 |
| Snocone IR+BB | `GOAL-SNOCONE-IR-BB.md` | one4all | SC-1 |
| &STCOUNT All Languages | `GOAL-STCOUNT-ALL-LANGS.md` | one4all | ST-1 |
| Unified Broker | `GOAL-UNIFIED-BROKER.md` | one4all | U-24 |
| Raku Frontend | `GOAL-RAKU-FRONTEND.md` | one4all | RK-16 |
| Polyglot Calc Demo | `GOAL-POLYGLOT-CALC-DEMO.md` | one4all | PC-1 |
| Scrip Interp Split | `GOAL-SCRIP-INTERP-SPLIT.md` | one4all | IS-1 |
| Silly Forward Sweep | `GOAL-SILLY-SWEEP-FORWARD.md` | one4all | wm 6927 → RPLACE |
| Silly Backward Sweep | `GOAL-SILLY-SWEEP-BACKWARD.md` | one4all | wm 6427 → CMA2 |
| Silly Sync Monitor | `GOAL-SILLY-SYNC-MONITOR.md` | one4all | S-1 |
| Silly Complete | `GOAL-SILLY-COMPLETE.md` | one4all | P1-A1 |
| Prolog IR-run | `GOAL-PROLOG-IR-RUN.md` | one4all | S-10e |
| Cross-Lang Verify | `GOAL-CROSS-LANG-VERIFY.md` | one4all | S-1 |
| Sub-Expression Oracle | `GOAL-SUBEXPR-ORACLE.md` | one4all+corpus | S-2 |
| Remove CMPILE | `GOAL-REMOVE-CMPILE.md` | one4all | S-7 |
| Two-Step Bug Hunt | `GOAL-TWO-STEP-HUNT.md` | one4all | S-1 |
| Scrip Beauty Suite | `GOAL-SCRIP-BEAUTY.md` | one4all | S-6 |
| NET Beauty 18/18 | `GOAL-NET-BEAUTY-19.md` | snobol4dotnet | S-8B |
| NET Beauty Self-Host | `GOAL-NET-BEAUTY-SELF.md` | snobol4dotnet | S-2-bridge-event-bombs (session #67 followup: snobol4dotnet `3c1637d` — `MonitorIpc.cs` now carries `_emitCount` + three env-var hooks: `MONITOR_BREAK_AT_EVENT=N` dumps managed stack at the Nth emit, `MONITOR_TRACE_FROM/TO_EVENT=N/M` gate a public `TraceEnabled` flag for downstream dot instrumentation. Smoke test confirms BREAK fires; beauty self-host stderr unchanged at 28 lines. Known offset between dot's `_emitCount` and controller wire-log `#N` documented; either fix the controller log to emit dot's count alongside, or add a `BREAK_ON_KIND_AND_LINE=KIND:STNO` env var to fire on (kind, stno) match instead. `TraceEnabled` not yet wired into `ScannerState.DOT_TRACE_ALT`. Validation rung — inject known dot bug, set BREAK at DIVERGE event, read bug from stack alone — still open. session #67 (earlier same session): harness-trust step OPENED — unfiltered sync-step harness's REAL first DIVERGE is at step **#933 on `&FULLSCAN = 1` itself** — a known SPITBOL bridge gap where spl emits no VALUE on keyword store. Every prior session's watermark advance (801→933→1046→1497→1617→2839) required controller workarounds `MONITOR_SKIP_EXTRA_KEYWORD_VALUES=1` + `MONITOR_NAME_WILDCARD=spl` masking bridge gaps; "watermark numbers are decoration" until the harness can pinpoint a known injected dot semantic bug. **Real isolated dot bug found this session: corpus crosscheck `114_pat_fence_via_var_in_paren_alt` FAILs on dot, PASSes on spl** — minimal 5-line repro: `cmd=FENCE('a'|'ab'); outer=(*cmd 'X'|*cmd 'Y'|LEN(0)); 'aY' POS(0) *outer RPOS(0)` should match the second arm but dot fails. Bug location: `Snobol4.Common/Runtime/PatternMatching/Scanner.cs` `Match()` lines 100-106 — on popping `-2` seal sentinel returns `Abort` immediately, even when REAL outer alternates remain BELOW the `-2` on the stack; those outer alternates were saved before the FENCE's `-3` Mark and should fire. Fix sketched (pop through `-2` seals to find real alternate; ABORT only if stack exhausted) but **NOT committed** per RULES.md "test gate before commit" — needs unit/corpus/beauty regression run. Fixing test 114 may or may not unblock beauty self-host (state-dependent); the bug is real either way. snobol4dotnet HEAD unchanged at `bb28a8d`. session #66: FENCE mark/seal mechanism LANDED — snobol4dotnet `bb28a8d`. New `MarkPattern.cs` pushes `-3` sentinel at FENCE entry; `SealAlternates` pops down to-and-through the most recent `-3`; `CreateFenceFunction` wraps as `Concat(Mark, Concat(p, Seal))`; **critical correction over session #65's attempt: on `-2` seal hit, `Match` returns `Abort` (was `Failure`)** — `Failure` allowed the unanchored cursor-retry loop in `PatternMatch` to rescue the match, defeating the seal entirely; per Gimpel 1973 `FENCE = NULL | ABORT`. Witness `TEST_Fence_061_pat_fence_fn_seal` flips FAIL→PASS (was the in-tree failing test exercising exactly the seal-with-outer-context bug; minimal repro `X FENCE(LEN(1)|LEN(2)) RPOS(0)` on `'AB'`). Test gate clean: TestSnobol4 2075p/14f (matches baseline; +1 from Fence_061; 14 fails are all pre-existing TEST_Csnobol4_*); beauty 17/17 PASS unchanged. **Beauty self-host STILL FAILS** at line 26 (`&FULLSCAN = 1`, Parse Error, same 28 stderr lines) — confirms session #65's prediction that *both* a mark-scheme bug AND a second downstream bug exist. Next session: re-enable `DOT_TRACE_ALT=1` (env-gated, easy to restore), run beauty self-host with trace, verify outer alternates ARE now preserved across nested-FENCE chain, then chase why `*snoUnprotKwd` still doesn't get tried in snoExpr14 alternation. Previously session #65: instrumented `ScannerState` SaveAlternate/RestoreAlternate/SealAlternates with `DOT_TRACE_ALT=1` env var; ran beauty self-host with trace and **confirmed in trace** that during the `&FULLSCAN = 1` parse, snoExpr13's `FENCE(... | epsilon)` epsilon-arm fires `SealPattern` which calls `SealAlternates()` — and the current implementation's `_alternatePatternStack.Clear()` wipes the entire stack from depth 15 → 2, destroying the snoExpr14 outer alternates that included `*snoUnprotKwd`. Standalone repro fails (per session #62/#64) because the seal-wipes-outer behaviour requires the deep nested-FENCE context of snoExpr10..snoExpr13 to manifest the depth-15 stack at SEAL time. Implemented a fence-mark fix (new `MarkPattern.cs` + ScannerState `-3` sentinel in alt stack + `Concat(Mark, Concat(p, Seal))` in `CreateFenceFunction`); build clean but **beauty self-host still fails with same Parse Error 28 lines** — fix is not sufficient on its own. Either the mark scheme has a subtle correctness bug, or there is a second gating bug downstream. Runtime patch and trace instrumentation REVERTED — no commit this session per RULES.md "test gate before commit". snobol4dotnet HEAD remains `724c1b6` [→ session #66 advance: now `bb28a8d`]. Next-session detail in goal file's session-#65 appendix. session #64: controller `keys_match` MWT_UNKNOWN extension lands in one4all `scripts/monitor/monitor_sync_bin.py` — when one side emits MWT_UNKNOWN with zero value bytes (SPITBOL bridge's coverage gap on nmblk/ptblk/atblk/tbblk/cdblk/efblk), the value-byte equality check is bypassed in addition to the type-tag wildcard; previously a NAME-with-bytes from dot diverged against UNKNOWN-no-bytes from spl on the value-byte field alone. **Watermark 1617 → 2839.** Beauty 17/17 PASS, no snobol4dotnet runtime changes. First real divergence at counter.inc:17 NRETURN body-assign: spl unwinds match (NRETURN) after 18 *upr returns, dot fires a 19th *upr Scan instead. **Root cause not isolated this session.** Investigation ruled out: standalone reproduction of (POS(0)|' ') *upr(tx) (' '|RPOS(0)) (both spl and dot do exactly 18 calls, no divergence — confirms session #62 state-dependence finding); stack-trace-at-upr-entry (every call from `*upr(tx)` pattern node via UnevaluatedPattern.Scan, no source-level call site); pattern-AST dump (single UnevaluatedPattern node Sub=7 Alt=-1 — structurally correct, no duplication); pattern algebra source (ConcatenatePattern(AlternatePattern, UnevaluatedPattern) — tree, no shared sub-pattern between alternation arms). **Key finding via AST inventory of beauty self-host (82 ASTs before Parse Error):** dot tries snoProtKwd against &FULLSCAN (correctly fails), then jumps to snoFunctions (which lives in snoAtom@line 182, a different production), **skipping snoUnprotKwd entirely** (which is the very next alternative in snoExpr14@line 154 and DOES contain FULLSCAN). The wire-monitor divergence at step 2839 is inside a snoUnprotKwd match path that dot never reaches in the unmonitored failing run. Real gating bug is upstream: dot's snoExpr14 alternation skips snoUnprotKwd. **Recommended next-session pivot:** instrument *snoParse entry/exit on dot to bracket the parse of `&FULLSCAN = 1`, dump the snoExpr14 alternation node chain, isolate why backtracking from *snoProtKwd's failure does not visit *snoUnprotKwd. Previously session #63: four wire-bridge convention adjustments in snobol4dotnet `724c1b6` advanced watermark 1497→1617 but unmonitored beauty self-host unchanged. Previously session #62: `$`-alternation-backtrack fix lands as S-2-bridge-7-dollar-alt — Executive.Assign bails when deferred Assignee FRETURNs, ImmediateVariableAssociation2.Scan returns Failure on Exec.Failure, unit suite 1898/1898 + 295/295. Previously session #58: stno-stable fix; monitor reached 1497.) |
| NET Snippets | `GOAL-NET-SNIPPETS.md` | snobol4dotnet | S-1 |
| NET Optimize | `GOAL-NET-OPTIMIZE.md` | snobol4dotnet | S-1 |
| NET DATATYPE Lowercase | `GOAL-NET-DATATYPE-LOWERCASE.md` | snobol4dotnet | S-1 |
| DATATYPE Portable Tests | `GOAL-DATATYPE-PORTABLE-TESTS.md` | corpus | S-1 |
| No Symlinks | `GOAL-NO-SYMLINKS.md` | corpus/harness/all | S-1 |
| README: profile | `GOAL-README-PROFILE.md` | .github | S-1 |
| README: one4all | `GOAL-README-ONE4ALL.md` | one4all | S-1 |
| README: snobol4dotnet | `GOAL-README-SNOBOL4DOTNET.md` | snobol4dotnet | S-1 |
| README: snobol4jvm | `GOAL-README-SNOBOL4JVM.md` | snobol4jvm | S-1 |
| README: corpus | `GOAL-README-CORPUS.md` | corpus | S-1 |
| README: harness | `GOAL-README-HARNESS.md` | harness | S-1 |
| README: snobol4python | `GOAL-README-SNOBOL4PYTHON.md` | snobol4python | S-1 |
| README: snobol4csharp | `GOAL-README-SNOBOL4CSHARP.md` | snobol4csharp | S-1 |
| README: snobol4artifact | `GOAL-README-SNOBOL4ARTIFACT.md` | snobol4artifact | S-1 |

## Completed Goals

| Goal | File | Repo |
|------|------|------|
| In-Process Sync Monitor | `GOAL-INPROC-MONITOR.md` | one4all |
| SNO treebank-array | `GOAL-SNO-TREEBANK-ARRAY.md` | one4all |
| SNO treebank-list | `GOAL-SNO-TREEBANK-LIST.md` | one4all |
| SNO claws5 | `GOAL-SNO-CLAWS5.md` | one4all |
| Full Integration | `GOAL-FULL-INTEGRATION.md` | one4all |
| One Eval | `GOAL-ONE-EVAL.md` | one4all |
| Session Setup Refinement | `GOAL-SESSION-SETUP-REFINEMENT.md` | .github + one4all |
| Self-Contained Scripts | `GOAL-SELF-CONTAINED-SCRIPTS.md` | one4all |
| Icon IR-run | `GOAL-ICON-IR-RUN.md` | one4all |
| Icon Gen Broker | `GOAL-ICN-BROKER.md` | one4all |
| Prolog BB Byrd | `GOAL-PROLOG-BB-BYRD.md` | one4all |
| CSNOBOL4 FENCE(P) | `GOAL-CSNOBOL4-FENCE.md` | csnobol4 |
| CSNOBOL4 Harness | `GOAL-CSNOBOL4-HARNESS.md` | harness |
| Archive Cleanup | `GOAL-ARCHIVE-CLEANUP.md` | .github |

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

## Architecture (one paragraph)

Every frontend (SNOBOL4, Icon, Prolog, Snocone, Rebus, Scrip) produces the shared IR.
SM-LOWER compiles IR to SM_Program — a flat array of stack machine instructions.
The INTERP executes SM_Program. The EMITTER walks SM_Program and emits native code
(x86, JVM, .NET, JS, WASM). Interpreter and emitter share one instruction set.

---

## Session trigger phrases

| Lon says | Meaning |
|----------|---------|
| "here we go" | Session starting — proceed with session start protocol above |
| "perform hand off" | End of session — update goal state, commit, push per RULES.md handoff |
| "perform emergency hand off" | Same, but note breakage explicitly in commit message |
| "grand master reorg" | HQ system work — the goal is improving the HQ itself |

Oracle: SPITBOL x64 primary (`/home/claude/x64/bin/sbl`). See RULES.md.
