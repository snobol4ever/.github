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
| **CSN FENCE Bug Fix** | `GOAL-CSN-FENCE-FIX.md` | csnobol4 | F-2 Step 3a (session #54: implemented session #53's "targeted slot-zeroing" proposal at L_STARP2/L_DSARP2 — walk PDL from saved-pre-SCIN snapshot to current PDLPTR, zero slot[1] of non-FNC traps. **fence_suite 27/3/2 → 29 OK / 3 FAIL / 0 CRASH** (best ever; tests 119, 129 = canonical beauty-class CRASHes FIXED). fence_function 10/10 preserved. **BUT regresses inner-pattern alternation backtrack** — new 5-line regression guard repro `cmd=(LEN(1)\|LEN(2)); outer=(*cmd 'X'); s='ABX'` should match (SPITBOL ✓, csnobol4+s52 ✓) but FAILS under zeroing. Beauty regresses ~32 → ~10 lines. **NOT committed** per RULES.md regression-in-error-class. Saved as `csnobol4/docs/F-2-Step3a-session54-zeroing-attempt.diff`. **Genuine new contribution:** demonstrated via instrumented SALT2/SCIN1/L_UNSC/L_DSAR trace that leaked inner-PATBCL traps ARE legitimately consulted via outer's "redo *cmd" trap → DSAR → L_UNSC → PATBCL=cmd restored → walker dispatches inner alts correctly. Targeted zeroing destroys live state. Test 119 crashes because leaked inner trap is reached AFTER all DSAR-redo entries consumed — no remaining mechanism to re-route through L_UNSC. **Architectural fix shape: SPITBOL `=ndexc` sentinel analog (call it STREXCCL)** mirroring `p_nth` at sbl.min:12213. On STARP6/DSARP success when inner pushed entries, install sentinel trap whose handler restores PATBCL=inner before walker walks the leaked region. Session #55: implement STREXCCL — define constant, add PATBRA case, define L_STREXC handler, modify STARP6/DSARP to push sentinel conditionally on `PDLPTR > saved_snapshot`. Apply s52 patch first. Test gates: fence_function 10/10, fence_suite 30+/32, 5-line repro must produce `inner backtrack worked`, beauty ≥ 500 lines. Findings in `csnobol4/docs/F-2-Step3a-session54-findings.md`. corpus @ 6955503, csnobol4 working tree CLEAN at HEAD `447b411`. **Session #55**: did NOT implement STREXCCL. Added 16 depth-recursion stress tests (Tier F, IDs 132–147) to fence_suite/. Result: **all 16 PASS on csnobol4 baseline** — empirically confirms 119/129/130 bug class is narrow (requires `*var` + outer ARBNO + tail-anchor failure conjunction; NOT generic depth recursion, NOT generic FENCE-under-recursion, NOT double-fn dispatch, NOT mutual recursion). New baseline: fence_suite **40/2/6 of 48** (csnobol4) / 47/1 of 48 (SPITBOL). Tier F + 5-line guard5 = regression-prevention floor for session #56. corpus has 32 new untracked files (132–147 .sno/.ref); csnobol4 has Makefile/README.md/findings.md changes. NO runtime source touched. Findings in `csnobol4/docs/F-2-Step3a-session55-tier-f-findings.md`. Session #56 should implement STREXCCL with the 48-test gate.) **Session #56**: implemented STREXCCL in `isnobol4.c` (5 edits, ~50 lines): static descriptors + dispatch case 41 + L_STREXC handler + STARP6/DSARP2 PUSH(PDLPTR,YPTR) + STARP2 conditional install. **All floors preserved** (fence_function 10/10, Tier F 16/16, guard5 ✓) but **fence_suite did NOT improve**: same 43/3/2 as s52 alone. Trace evidence on test 114 (`STREXC_TRACE=1`) shows STREXCCL **does fire** but **PATBCL is already = inner-PATBCL** when walker reaches sentinel — refutes session #54's "leaked traps dispatched under wrong PATBCL" hypothesis. Some upstream handler sets PATBCL=inner during outer's failure walk before sentinel is reached. Saved as `csnobol4/docs/F-2-Step3a-session56-strexccl-attempt.diff` (combined with s52, 90 lines self-contained against HEAD `1b2e28a`, verified to reproduce gates). **Session #57** should apply session #56 patch and add a PATBCL-write logger at every `D(PATBCL) = ...` site to find which write sets PATBCL=inner during outer walk — that's the upstream bug. Then either fix that write or augment STREXCCL with a paired BOTTOM-of-region sentinel. Findings in `csnobol4/docs/F-2-Step3a-session56-findings.md`. csnobol4 working tree CLEAN at HEAD `1b2e28a`.) **Session #57**: applied s56 patch + instrumented all PATBCL touchpoints (3 D(PATBCL)= sites, 7 POP(PATBCL) sites, every SALT2 entry). Trace on test 119 **refutes both** session #54 (wrong-PATBCL-on-leaks) and session #56 (upstream-write-sets-PATBCL=inner). Decisive evidence: every PATBCL change in the run is accounted for; bug is **multi-iteration ARBNO leak class** — STREXCCL only protects most recent iteration; earlier ARBNO `*cmd` iterations left inner-pattern leaks below STREXCCL's reach. After STARP5 final POP restores PATBCL=outer, walker descends into iter#2's unprotected leaks at PDLPTR=0x...ae0 reading `{a=0x200, f=0, v=96}` under outer PATBCL → SCIN3 fallthrough → `D(outer + 0x200)` = garbage → ZCL=NULL → SEGV at isnobol4.c:11521. Three fix candidates documented: **(c)** persistent STREXCCL across iterations; **(b refined)** paired BOTTOM-sentinel; **(d)** PDL truncate + deferred-alt array. Diagnostic patch saved as `csnobol4/docs/F-2-Step3a-session57-diagnostic.diff` (145 lines, env-gated `PATBCL_LOG=1`, reusable). Findings in `csnobol4/docs/F-2-Step3a-session57-findings.md`. Working tree CLEAN at HEAD `273f5f3`. **Session #58** should read SPITBOL p_str/=ndexc/flpop carefully then implement (b/c/d).) **Session #58**: read SPITBOL p_exa/p_nth/p_exb/p_exc (sbl.min:11920-12000, 12213) AND p_aba/p_abb/p_abc/p_abd (11600-11665) carefully — first session to actually do the SPITBOL reading session #57 ordered. Architectural finding: CSNOBOL4 has `PDLHED` declared (analog of SPITBOL `pmhbs`) and BAL/EXPVAL/ATP save/restore it across recursive matches, but **STAR/DSAR do NOT** and the failure walker SALT2/SALT3 has no PDLHED bound check (only BAL's walker does, v311.sil:3975). Implemented session #57 candidate (b refined) — paired top + bottom STREXCCL sentinels. 3 edits in isnobol4.c (~40 net lines on top of s52+s56, total 195 lines self-contained vs HEAD `8ebab64`): (1) L_STARP2 success rewrites the SCFLCL trap at `STREX_entrypdl + DESCR` to STREXCCL with slot[2]=OUTER PATBCL — symmetric with the top STREXCCL (slot[2]=inner); same handler `L_STREXC` fires both. (2) L_DSARP2 pushes SCFLCL frame symmetrically with STARP6 so DSARP2 success has a known target for the bottom-rewrite. (3) Top STREXCCL push from s56 preserved unchanged. SCFLCL is preserved on FAIL path (STARP5) — was already consumed during inner SCIN's fail-walk → FAIL exit. **Result: ALL 6 fence_suite CRASHes ELIMINATED.** Tests 109, 113, 130 — CRASH at baseline AND CRASH after s56 alone — now OK. fence_suite **44 OK / 4 FAIL / 0 CRASH** of 48 (was 40/2/6 baseline, 43/3/2 s56). fence_function 10/10 preserved. Tier F 16/16 preserved. guard5 preserved. Beauty self-host **35 → 42 lines** before Error 17 (controlled program error, not memory corruption) — first non-zero gain since session #45. **Bug class shifted from memory corruption to wrong-answer semantics:** tests 119/129 went CRASH → FAIL (`unexpected match` instead of `triple-indirect FENCE sealed`). Hypothesis: bottom-STREXCCL routing lets walker re-enter inner cmd region under inner PATBCL via an EARLIER iteration's top STREXCCL — re-entry finds FNCDCL but treats it as legitimate retry rather than sealed wall. Or: bottom-STREXCCL fires during legitimate inner-pattern-fail walk when it should leave walker in inner-mode all the way to SCFLCL→FAIL. **NOT committed** per RULES.md: 119/129 are wrong-answer; F-2 Step 3a `Done when` requires beauty ≥500 lines (42 << 500). Saved as `csnobol4/docs/F-2-Step3a-session58-paired-strexc-attempt.diff` (195 lines, applies clean to HEAD `8ebab64`, verified gates). Findings in `csnobol4/docs/F-2-Step3a-session58-findings.md`. Session #59 should apply s58 patch + s57 diagnostic, trace test 119 with PATBCL_LOG=1/STREXC_TRACE=1 to identify which path produces unexpected match, cross-check on test 130 (FAIL→OK in s58) for mechanism understanding, possibly refine bottom-STREXCCL with fail-mid-iteration vs. fail-after-iteration-success distinction. csnobol4 advanced to `68075bb` (docs files committed). |
| Icon Frontend Ladder | `GOAL-LANG-ICON.md` | one4all | IC-9 (session #19, 2026-04-30: `/E` and `\E` scalar evaluator semantics fix in `interp.c`. Pre-fix `case E_NULL` body was `return IS_FAIL_fn(v) ? NULVCL : FAILDESCR;` — i.e. "/E succeeds iff E *failed*", confusing "fail" with "yielded null". `/x[1]` for missing key returned NULVCL (success-with-null), handler saw `IS_FAIL_fn(NULVCL)==false` and reported FAIL — wrong. `\E` had a parallel bug: missed `DT_SNUL` entirely, so `\&null` returned `&null` (success) instead of failing; also carried a dead-code line `if (v.v==DT_I && v.i==0 && !IS_INT_fn(v))` (unsatisfiable conjunction) from an earlier confused attempt. Fix rewrites both handlers to test the value directly: /E fails on FAIL, succeeds (returns NULVCL) on DT_SNUL or DT_S empty .s, fails otherwise; \E mirrors. Verified on minimal probe: with `x:=table(); x[2]:=2`, `/x[1]→succeed, \x[1]→fail, /x[2]→fail, \x[2]→succeed` — all four directions now correct. Visible diff improvement: spurious `/1` line in `rung36_jcon_table` output is gone (the test's `/x[1]|write("/1")` now correctly suppresses the write). All gates byte-identical at PASS=5/49/4/188/5 (icon-smoke/broker/crosscheck/all-rungs/rung36) — per-test diff vs baseline empty. NOTE: PLAN.md row got reverted to session #17 between IC-8 commit (4b33106) and Snocone commits — session #18's narrative (in the GOAL file) was preserved but the table row regressed; this entry restores forward continuity at session #19. **Correction to prior session's diagnosis:** the goal-file IC-9 list item #5 ("\x[k]/x[k] for missing key currently inserts &null entries causing delete:4 instead of delete:2") was wrong about the cause. Probing missing keys does NOT insert (verified). The `delete:4` symptom is a separate `delete()` arity bug — `delete(x)` with no 2nd arg and `delete(x,3,6)` with 3 args silently fail to remove. Documented in goal-file session-#19 narrative. **Working-tree pollution cleaned**: at session start found `foo.baz`, `interp.c.fixed`, `interp.c.orig` in working tree — the .c.* pair were byte-identical and contained a drafted-but-not-committed version of this exact fix. Per RULES.md these don't ship; removed. Files: src/driver/interp.c +17/-5. No header changes. Next IC-9 candidate: `?T` random-select on empty/sparse table — the `should fail &null` line in rung36_jcon_table diff is `?T` returning NULVCL when it should fail.) |
| Prolog Frontend Ladder | `GOAL-LANG-PROLOG.md` | one4all | PL-12 (session 2026-04-30 #4, one4all `75d5775b` baseline + 2 docs commits: 75% baseline preserved; fix #2 v2 attempted, regressed 43→7, reverted, NOT committed. Three changes implemented in `pl_runtime.c` (264-line working-tree diff saved as docs): (A) NEW `pl_term_to_goal_expr` + `pl_invoke_term` 197-line Term→EXPR bridge mirroring `prolog_lower.c::lower_term` exactly (=/2→E_UNIFY, +/-/*///mod→E_ADD/SUB/MUL/DIV/MOD, atom→E_FNC nchildren=0, etc.) wired into catch/3 when goal_e->kind==E_VAR; (B) NEW E_UNIFY/E_CUT/E_NUL cases in `pl_unified_term_from_expr` — separate latent bug surfaced by A: was falling through default to atom("?"), so any directive `G = (X = 5)` silently bound G to `?` instead of `=(X,5)` compound; (C) findall snapshot `pl_unified_deep_copy` → `pl_copy_term` (working-tree carryover) so var sharing within one snapshot survives. **All 5 primary repros pass standalone** (literal catch, Var=fail, Var=(X=5), Var=(A is 3+4), post-assertz term_singletons). **But SWI 43/57 → 7/57** in plunit-harnessed tests: standalone `memberchk(f(X,a),...)` works, but after assertz round-trip caller's X is not bound by bridge dispatch (`_G1` instead of `y`). Asserted-clause cenv TT_VARs that pl_invoke_term binds are not visible to caller's source-level vars after pl_box_choice_call returns — head-unify TT_REF chain not propagating, β unwinding prematurely, or chain not built as expected. **Diagnostic insight:** Change B is independent and correct; could land standalone as pre-fix-#2 cleanup. Saved as `docs/PL-12-session-2026-04-30-4-attempt.diff` and `docs/PL-12-session-2026-04-30-4-findings.md`. **NEXT SESSION**: (1) trace the asserted-clause TT_REF chain with minimal `:- assertz(stored(=(X,hello))). main :- stored(G), catch(G,_,fail), write(X).` repro to find exactly where main's X loses connection to asserted-cenv X; (2) land Change B as standalone commit if gate stays clean; (3) land Change C if not already committed; (4) only then re-attempt fix #2 v3 with correct dispatch lifecycle. Smoke 5/5, broker 49/49, SWI 43/57=75% all green at end of session.) |
| Raku Frontend Ladder | `GOAL-LANG-RAKU.md` | one4all | RK-34 |
| Snocone Frontend Ladder | `GOAL-LANG-SNOCONE.md` | one4all+corpus | D-1 |
| Rebus Frontend Ladder | `GOAL-LANG-REBUS.md` | one4all | RB-2 |
| Snocone claws5.sc | `GOAL-SNOCONE-CLAWS5.md` | one4all+corpus | CL-2 |
| Snocone treebank-list.sc | `GOAL-SNOCONE-TREEBANK-LIST.md` | one4all+corpus | TB-1 |
| Snocone Beauty         | `GOAL-SNOCONE-BEAUTY.md`       | corpus+one4all | SB-6.D (session #79, 2026-04-30: SB-6.A/B/C all LANDED. E_VLIST IR node added (`ir.h`, `interp.c` evaluator in both value and pattern context, `sm_lower.c` lowering via existing SM_JUMP_S/SM_POP — no new SM opcode needed). SB-6.A: Snocone `\|\|` rewired to emit E_VLIST in `snocone_lower.c::SNOCONE_OR` with left-associative collapse mirroring E_ALT/E_SEQ; verified across all 3 modes on the IDENT-OR truth-table fixture (9/9 PASS). SB-6.B: SNOBOL4 paren-list rewired in `snobol4.y:195` to emit E_VLIST; parser regenerated; **byte-identical to SPITBOL oracle** on the same fixture written in SNOBOL4. SB-6.C: Snocone unary `?x` rewritten to `E_NOT(E_NOT(x))` per session #78 design — uses existing IR, zero new node; truth table verified including the `?''` regression-fix (was FAIL, now succeeds-as-null per spec). All baseline gates green: PASS=5 / PASS=42 SKIP=3 / PASS=49. Crosscheck snobol4=6, snocone=8 unchanged. Broad interp PASS=222 FAIL=52 — exact match to s#75/#77 baseline, zero regressions. **SB-6.D opens** as the remaining gate: with A/B/C landed, the session-#78 tiny fixture `printf '\\tA = 1\\n\\tOUTPUT = A\\nEND\\n' \| scrip --ir-run $LIBS beauty.sc` still emits "Parse Error" twice plus 3 stderr errors (`** Error 1 ... GE first argument is not numeric` ×2, `** Error 5 ... Undefined function or operation` ×1). Operator fixes were necessary but not sufficient. Recommended s#80 first diagnostic: check out 41c9a50a (pre-A/B/C), rebuild clean, re-run tiny fixture; if same 3 errors fire, they're pre-existing and were merely unmasked when A/B/C let beauty.sc proceed past the prior `||`/`(,)`/`?` mis-construction. The `GE first arg not numeric` pattern strongly suggests a non-numeric (PATTERN or EXPRESSION descriptor) leaking into a `GE(a,b)` call in beauty.sc's pattern-construction phase — candidates: `ppStop[]` array, `ppSmBump`/`ppLgBump` arithmetic, `Real` pattern's nested SPAN/FENCE, or a `*Pat`-deferred reference resolving to wrong type. Build hazard re-confirmed: stale `.o` files mixed with dirty working tree masqueraded as a regression on `main` until `find src -name '*.o' -delete` clean rebuild — exactly the warning IC-8 #18 commit message gave. Six files +79/-6 net: `ir.h`, `interp.c`, `sm_lower.c` (E_VLIST infrastructure, partly inherited from earlier abandoned session), `snocone_lower.c` (Bug A + Bug C), `snobol4.y` (Bug B, regenerated `snobol4.tab.c`).) |
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
| NET Beauty Self-Host | `GOAL-NET-BEAUTY-SELF.md` | snobol4dotnet | S-2-bridge-event-bombs-coverage / S-2-bridge-7-fullscan (session #70, 2026-04-30 — full detail in GOAL-NET-BEAUTY-SELF.md session-#70 narrative. C# function tracing landed standalone: `MonitorIpc.cs` patched so `_standaloneCount` ticks without a live controller, making `MONITOR_TRACE_FROM_EVENT`/`TO_EVENT` work without the harness. `Scanner.cs`/`ScannerState.cs` instrumented with TraceEnabled-gated `[ALT]`/`[PM]`/`[M]` traces. All diagnostic patches reverted before commit per RULES.md. Trace revealed: beauty self-host dot emits 2609 events, failing parse is scanner-state s80 (subject `&FULLSCAN = 1`) with 2.5M alt-stack events. Just before final SEAL on s80: stack `[94, 91, 86, -2, -2, 352, -2, -2, 594, …, 466, 56, 51, 24, 19, -3, 10, 5, -1]` — multiple prior `-2` seals interleaved with outer alts, only one `-3` mark at depth 29. Seal pops 28 entries to find the lone mark, eating outer snoExpr14/snoVar alts (19, 24, 51, 56, 466, 471, 476, 479, 352, 503, 503) where `*snoUnprotKwd` lives. One-line fix attempted (`if (top == -2) break;` in `SealAlternates`): build clean, seals correctly stopped at `-2` (final s80 seal popped 3 entries instead of 28, outer alts preserved), but **beauty self-host unchanged at 28 stderr lines / same Parse Error**. Confirms session #68's "bug is above the seal" diagnosis: high-numbered alts (588, 594, 273000-series, 280000-series) succeed at intermediate steps and commit the parse to `*snoFunction` BEFORE backtrack ever reaches the snoExpr14 alts where `*snoUnprotKwd` sits. snobol4dotnet HEAD UNCHANGED at `c578fb5`. Next session: restore diagnostic patches per session-#70 narrative; find first `[M s80] Result=SUCCESS` leading to `*snoFunction`; walk back to identify which snoExpr14 alt was supposed to fire first; bug is whatever causes that alt to be skipped — likely AST-build wiring of `*snoUnprotKwd.Alternate` or fence-between-snoExpr14-arms wiping wrong alts.) |
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
