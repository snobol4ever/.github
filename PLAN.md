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
| **CSN FENCE Bug Fix** | `GOAL-CSN-FENCE-FIX.md` | csnobol4 | F-2 Step 3a (session #54: implemented session #53's "targeted slot-zeroing" proposal at L_STARP2/L_DSARP2 — walk PDL from saved-pre-SCIN snapshot to current PDLPTR, zero slot[1] of non-FNC traps. **fence_suite 27/3/2 → 29 OK / 3 FAIL / 0 CRASH** (best ever; tests 119, 129 = canonical beauty-class CRASHes FIXED). fence_function 10/10 preserved. **BUT regresses inner-pattern alternation backtrack** — new 5-line regression guard repro `cmd=(LEN(1)\|LEN(2)); outer=(*cmd 'X'); s='ABX'` should match (SPITBOL ✓, csnobol4+s52 ✓) but FAILS under zeroing. Beauty regresses ~32 → ~10 lines. **NOT committed** per RULES.md regression-in-error-class. Saved as `csnobol4/docs/F-2-Step3a-session54-zeroing-attempt.diff`. **Genuine new contribution:** demonstrated via instrumented SALT2/SCIN1/L_UNSC/L_DSAR trace that leaked inner-PATBCL traps ARE legitimately consulted via outer's "redo *cmd" trap → DSAR → L_UNSC → PATBCL=cmd restored → walker dispatches inner alts correctly. Targeted zeroing destroys live state. Test 119 crashes because leaked inner trap is reached AFTER all DSAR-redo entries consumed — no remaining mechanism to re-route through L_UNSC. **Architectural fix shape: SPITBOL `=ndexc` sentinel analog (call it STREXCCL)** mirroring `p_nth` at sbl.min:12213. On STARP6/DSARP success when inner pushed entries, install sentinel trap whose handler restores PATBCL=inner before walker walks the leaked region. Session #55: implement STREXCCL — define constant, add PATBRA case, define L_STREXC handler, modify STARP6/DSARP to push sentinel conditionally on `PDLPTR > saved_snapshot`. Apply s52 patch first. Test gates: fence_function 10/10, fence_suite 30+/32, 5-line repro must produce `inner backtrack worked`, beauty ≥ 500 lines. Findings in `csnobol4/docs/F-2-Step3a-session54-findings.md`. corpus @ 6955503, csnobol4 working tree CLEAN at HEAD `447b411`. **Session #55**: did NOT implement STREXCCL. Added 16 depth-recursion stress tests (Tier F, IDs 132–147) to fence_suite/. Result: **all 16 PASS on csnobol4 baseline** — empirically confirms 119/129/130 bug class is narrow (requires `*var` + outer ARBNO + tail-anchor failure conjunction; NOT generic depth recursion, NOT generic FENCE-under-recursion, NOT double-fn dispatch, NOT mutual recursion). New baseline: fence_suite **40/2/6 of 48** (csnobol4) / 47/1 of 48 (SPITBOL). Tier F + 5-line guard5 = regression-prevention floor for session #56. corpus has 32 new untracked files (132–147 .sno/.ref); csnobol4 has Makefile/README.md/findings.md changes. NO runtime source touched. Findings in `csnobol4/docs/F-2-Step3a-session55-tier-f-findings.md`. Session #56 should implement STREXCCL with the 48-test gate.) **Session #56**: implemented STREXCCL in `isnobol4.c` (5 edits, ~50 lines): static descriptors + dispatch case 41 + L_STREXC handler + STARP6/DSARP2 PUSH(PDLPTR,YPTR) + STARP2 conditional install. **All floors preserved** (fence_function 10/10, Tier F 16/16, guard5 ✓) but **fence_suite did NOT improve**: same 43/3/2 as s52 alone. Trace evidence on test 114 (`STREXC_TRACE=1`) shows STREXCCL **does fire** but **PATBCL is already = inner-PATBCL** when walker reaches sentinel — refutes session #54's "leaked traps dispatched under wrong PATBCL" hypothesis. Some upstream handler sets PATBCL=inner during outer's failure walk before sentinel is reached. Saved as `csnobol4/docs/F-2-Step3a-session56-strexccl-attempt.diff` (combined with s52, 90 lines self-contained against HEAD `1b2e28a`, verified to reproduce gates). **Session #57** should apply session #56 patch and add a PATBCL-write logger at every `D(PATBCL) = ...` site to find which write sets PATBCL=inner during outer walk — that's the upstream bug. Then either fix that write or augment STREXCCL with a paired BOTTOM-of-region sentinel. Findings in `csnobol4/docs/F-2-Step3a-session56-findings.md`. csnobol4 working tree CLEAN at HEAD `1b2e28a`.) |
| Icon Frontend Ladder | `GOAL-LANG-ICON.md` | one4all | IC-8 (session #17, 2026-04-30: closed rung36_jcon_primes via two coupled fixes — (a) GDE-aware E_IF in icon-frame dispatch (interp.c L2591) pumps a generative test via icn_eval_gen α-tick, taking then-branch on first non-fail, else-branch on exhaustion; (b) E_LOOP_NEXT (`next`) wired with new IcnFrame.loop_next field — previously parsed but unhandled. E_SEQ_EXPR short-circuits on loop_next so `if cond then next; rest_of_block` skips rest_of_block; E_EVERY x3, E_WHILE, E_UNTIL, E_REPEAT save+clear+restore loop_next at iteration boundaries. **+1 in rung36 (4→5) but +28 across all rungs (160→188)** — many rung12–35 tests had GDE-in-if patterns silently consuming only the first generated value. **Wrong-site lesson recorded**: interp.c has TWO E_IF cases — icon-frame switch L2591 (live under `icn_frame_depth>0`) and shared switch L3732 (dead under same condition); patches MUST go in the upper (icon-frame) handler when fixing Icon-procedure semantics. Initial pass to L3732 produced empty `/tmp/dbg.txt` trace; relocated and patch fired immediately. **Build hazard recorded**: changes to icn_runtime.h require clean `find src -name '*.o' -delete` rebuild — incremental build does not detect header timestamp changes for cross-directory .o files. Adding `loop_next` shifted IcnFrame field offsets and produced a phantom 16-test broker regression (49→33) until a clean rebuild aligned both interp.o and icn_runtime.o against the new layout. All gates clean post-fix: smoke_icon 5/5, smoke_unified_broker 49/0, crosscheck_icon 4/0, test_icon_ir_all_rungs 188/45/30 of 263. one4all advanced from 8fe45feb. Next pivot: implement `!N` integer iteration (E_ITERATE for IS_INT_fn(av) — iterate decimal digits of abs(N) as 1-char string descriptors). ~20 lines, unblocks btrees/prefix/every xfails. Then rung36_jcon_table NONMEMBER-leak in image/print of un-set entries.) |
| Prolog Frontend Ladder | `GOAL-LANG-PROLOG.md` | one4all | PL-12 |
| Raku Frontend Ladder | `GOAL-LANG-RAKU.md` | one4all | RK-34 |
| Snocone Frontend Ladder | `GOAL-LANG-SNOCONE.md` | one4all+corpus | D-1 |
| Rebus Frontend Ladder | `GOAL-LANG-REBUS.md` | one4all | RB-2 |
| Snocone claws5.sc | `GOAL-SNOCONE-CLAWS5.md` | one4all+corpus | CL-2 |
| Snocone treebank-list.sc | `GOAL-SNOCONE-TREEBANK-LIST.md` | one4all+corpus | TB-1 |
| Snocone Beauty         | `GOAL-SNOCONE-BEAUTY.md`       | corpus+one4all | SB-5c.4 (session #75: SB-5c.1 LANDED — root cause was Snocone IR routing pattern builtins through value context. Snocone emits `(E_FNC ARBNO ...)` and `(E_FNC FENCE ...)` rather than `(E_ARBNO ...)` / `(E_FENCE ...)`; `interp_eval_pat` had explicit cases for the latter (pattern-context arg eval, producing XDSAR for `*name`) but `E_FNC` fell through to `default → interp_eval` (value context), turning `E_DEFER(E_VAR)` into a frozen DT_E. `pat_arbno(DT_E)` → `spat_of` returns NULL → ARBNO with NULL child → fails to advance cursor. Fix: `+31/-0` in `src/driver/interp.c::interp_eval_pat` adding a `case E_FNC` that for ARBNO and FENCE evaluates the child via `interp_eval_pat` and calls `pat_arbno`/`pat_fence_p` directly. Other pattern builtins (POS/RPOS/SPAN/BREAK/LEN/ANY/NOTANY/TAB/RTAB/ARB/REM/BAL/SUCCEED/FAIL/ABORT) take non-pattern args and keep value-context default. Session-#73 8-case bisection: 8/8 PASS in all three modes (was 6/8). Three baseline gates green (PASS=5, PASS=42 SKIP=3, PASS=49). Crosscheck snobol4: PASS=6; crosscheck snocone: PASS=8; broad corpus: PASS=222 FAIL=52 (identical to baseline, no regression). **Side-effect closures:** SB-5d.1 LANDED (`treebank-list.sc` byte-identical to SPITBOL oracle in all three modes, 24 lines, md5 `7096beb49889b0d2c5db66b4a45ae444` matches .ref); SB-5c.5 LANDED (`treebank-list.sno` and `treebank-array.sno` byte-identical to SPITBOL in all three modes — same root cause via SNOBOL4 frontend's E_ARBNO path); SB-5c.3 CLEARED (`claws5.sno` no longer hangs, produces same `Pattern match failed` as SPITBOL). Beauty.sc end-to-end: `echo START | ./scrip --ir-run $LIBS beauty.sc` no longer hangs (emits "Parse"); on `beauty.sno` input now flows through 7-line comment header AND 17 `-INCLUDE` lines (was hanging on first non-comment statement). Real grammar work in beauty.sc remains for SB-5/SB-6. Active rung now SB-5c.4 — faithful re-port of `claws5.sc::pp_mem` 1-for-1 against `claws5.sno::pp_mem`, zero gotos. SB-5c.2 (claws5 input alignment), SB-5d.2 (treebank-array.sc blocked on LS-0), SB-5d.4 (zero-goto invariant) also still open. Files touched: `src/driver/interp.c` only (+31/-0).) |
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
| NET Beauty Self-Host | `GOAL-NET-BEAUTY-SELF.md` | snobol4dotnet | S-2-bridge-event-bombs-coverage / S-2-bridge-7-A1 (session #69, 2026-04-30 — full session detail in GOAL-NET-BEAUTY-SELF.md session-#69 narrative. Path A chosen: fix the spl bridge gap rather than work around it. With unfiltered harness — no `MONITOR_SKIP_EXTRA_KEYWORD_VALUES`, no `MONITOR_NAME_WILDCARD` — first DIVERGE is at controller step #933 on `&FULLSCAN = 1` itself: dot emits `@653 VALUE &fullscan = INT=1`, spl emits `LABEL stno=INT=654` (skipped the VALUE — spl's bridge has no fire-point on keyword stores in `sbl.min asign asg14/asg15/asg26`). With diagnostic TraceEnabled instrumentation added in `ThreadedExecuteLoop.cs` and `OperatorsBinary/AssignReplace (=).cs` (reverted before commit per RULES.md), captured 10-event trace between dot wire #931 and #934 confirming dot runs the keyword path correctly: `[TEL CallMsil] -> [ASN ENTER] -> [ASN KEYWORD-PATH] -> [ASN HANDLER-FOUND] -> [ASN HANDLER-RETURNED] -> EmitValue` — bug is exclusively spl's missing `jsr sysmv` on its keyword-commit branches. Lon caught session-start error: scanner-only TraceEnabled produced empty trace, was wrongly read as "nothing happened" — actually "wrong layer instrumented". S-2-bridge-event-bombs-coverage rung opened to require TraceEnabled coverage on every C# code path between adjacent emits. snobol4dotnet HEAD unchanged at `c578fb5` — diagnostic patches reverted, baseline preserved at 28 stderr lines. Next session: implement S-2-bridge-event-bombs-coverage (durable instrumentation) then S-2-bridge-7-A1 (`zysmk` syscall + `jsr sysmk` in `sbl.min asign` keyword exits) on x64 repo.) |
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
