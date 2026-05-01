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
| **CSN FENCE Bug Fix** | `GOAL-CSN-FENCE-FIX.md` | csnobol4 | F-2 Step 3a (session #54: implemented session #53's "targeted slot-zeroing" proposal at L_STARP2/L_DSARP2 — walk PDL from saved-pre-SCIN snapshot to current PDLPTR, zero slot[1] of non-FNC traps. **fence_suite 27/3/2 → 29 OK / 3 FAIL / 0 CRASH** (best ever; tests 119, 129 = canonical beauty-class CRASHes FIXED). fence_function 10/10 preserved. **BUT regresses inner-pattern alternation backtrack** — new 5-line regression guard repro `cmd=(LEN(1)\|LEN(2)); outer=(*cmd 'X'); s='ABX'` should match (SPITBOL ✓, csnobol4+s52 ✓) but FAILS under zeroing. Beauty regresses ~32 → ~10 lines. **NOT committed** per RULES.md regression-in-error-class. Saved as `csnobol4/docs/F-2-Step3a-session54-zeroing-attempt.diff`. **Genuine new contribution:** demonstrated via instrumented SALT2/SCIN1/L_UNSC/L_DSAR trace that leaked inner-PATBCL traps ARE legitimately consulted via outer's "redo *cmd" trap → DSAR → L_UNSC → PATBCL=cmd restored → walker dispatches inner alts correctly. Targeted zeroing destroys live state. Test 119 crashes because leaked inner trap is reached AFTER all DSAR-redo entries consumed — no remaining mechanism to re-route through L_UNSC. **Architectural fix shape: SPITBOL `=ndexc` sentinel analog (call it STREXCCL)** mirroring `p_nth` at sbl.min:12213. On STARP6/DSARP success when inner pushed entries, install sentinel trap whose handler restores PATBCL=inner before walker walks the leaked region. Session #55: implement STREXCCL — define constant, add PATBRA case, define L_STREXC handler, modify STARP6/DSARP to push sentinel conditionally on `PDLPTR > saved_snapshot`. Apply s52 patch first. Test gates: fence_function 10/10, fence_suite 30+/32, 5-line repro must produce `inner backtrack worked`, beauty ≥ 500 lines. Findings in `csnobol4/docs/F-2-Step3a-session54-findings.md`. corpus @ 6955503, csnobol4 working tree CLEAN at HEAD `447b411`. **Session #55**: did NOT implement STREXCCL. Added 16 depth-recursion stress tests (Tier F, IDs 132–147) to fence_suite/. Result: **all 16 PASS on csnobol4 baseline** — empirically confirms 119/129/130 bug class is narrow (requires `*var` + outer ARBNO + tail-anchor failure conjunction; NOT generic depth recursion, NOT generic FENCE-under-recursion, NOT double-fn dispatch, NOT mutual recursion). New baseline: fence_suite **40/2/6 of 48** (csnobol4) / 47/1 of 48 (SPITBOL). Tier F + 5-line guard5 = regression-prevention floor for session #56. corpus has 32 new untracked files (132–147 .sno/.ref); csnobol4 has Makefile/README.md/findings.md changes. NO runtime source touched. Findings in `csnobol4/docs/F-2-Step3a-session55-tier-f-findings.md`. Session #56 should implement STREXCCL with the 48-test gate.) **Session #56**: implemented STREXCCL in `isnobol4.c` (5 edits, ~50 lines): static descriptors + dispatch case 41 + L_STREXC handler + STARP6/DSARP2 PUSH(PDLPTR,YPTR) + STARP2 conditional install. **All floors preserved** (fence_function 10/10, Tier F 16/16, guard5 ✓) but **fence_suite did NOT improve**: same 43/3/2 as s52 alone. Trace evidence on test 114 (`STREXC_TRACE=1`) shows STREXCCL **does fire** but **PATBCL is already = inner-PATBCL** when walker reaches sentinel — refutes session #54's "leaked traps dispatched under wrong PATBCL" hypothesis. Some upstream handler sets PATBCL=inner during outer's failure walk before sentinel is reached. Saved as `csnobol4/docs/F-2-Step3a-session56-strexccl-attempt.diff` (combined with s52, 90 lines self-contained against HEAD `1b2e28a`, verified to reproduce gates). **Session #57** should apply session #56 patch and add a PATBCL-write logger at every `D(PATBCL) = ...` site to find which write sets PATBCL=inner during outer walk — that's the upstream bug. Then either fix that write or augment STREXCCL with a paired BOTTOM-of-region sentinel. Findings in `csnobol4/docs/F-2-Step3a-session56-findings.md`. csnobol4 working tree CLEAN at HEAD `1b2e28a`.) **Session #57**: applied s56 patch + instrumented all PATBCL touchpoints (3 D(PATBCL)= sites, 7 POP(PATBCL) sites, every SALT2 entry). Trace on test 119 **refutes both** session #54 (wrong-PATBCL-on-leaks) and session #56 (upstream-write-sets-PATBCL=inner). Decisive evidence: every PATBCL change in the run is accounted for; bug is **multi-iteration ARBNO leak class** — STREXCCL only protects most recent iteration; earlier ARBNO `*cmd` iterations left inner-pattern leaks below STREXCCL's reach. After STARP5 final POP restores PATBCL=outer, walker descends into iter#2's unprotected leaks at PDLPTR=0x...ae0 reading `{a=0x200, f=0, v=96}` under outer PATBCL → SCIN3 fallthrough → `D(outer + 0x200)` = garbage → ZCL=NULL → SEGV at isnobol4.c:11521. Three fix candidates documented: **(c)** persistent STREXCCL across iterations; **(b refined)** paired BOTTOM-sentinel; **(d)** PDL truncate + deferred-alt array. Diagnostic patch saved as `csnobol4/docs/F-2-Step3a-session57-diagnostic.diff` (145 lines, env-gated `PATBCL_LOG=1`, reusable). Findings in `csnobol4/docs/F-2-Step3a-session57-findings.md`. Working tree CLEAN at HEAD `273f5f3`. **Session #58** should read SPITBOL p_str/=ndexc/flpop carefully then implement (b/c/d).) **Session #58**: read SPITBOL p_exa/p_nth/p_exb/p_exc + p_aba/p_abb/p_abc/p_abd. Implemented paired top + bottom STREXCCL sentinels (s58 patch). **All 6 fence_suite CRASHes ELIMINATED** (44/4/0). fence_function 10/10 + Tier F 16/16 + guard5 preserved. Beauty 35→42 lines (first non-zero gain since session #45). Tests 119/129 went CRASH→FAIL (wrong-answer not crash). NOT committed (RULES.md). Saved as `csnobol4/docs/F-2-Step3a-session58-paired-strexc-attempt.diff`. csnobol4 advanced to `68075bb` (docs only). **Session #59**: continued from s58; added SALT2-entry trace; test 119 produced only 7 events before "unexpected match". **Architectural diagnosis: CSNOBOL4 uses PATBCL+offset addressing while SPITBOL uses direct memory pointers — leaked inner SCIN3 entries become semantically wrong (not crashing) when read under outer PATBCL.** Two STREXBCL variants tested: FAIL-on-fire regressed 44/4/0→43/5/0; PATBCL=outer+continue identical to s58. **Two structural fix candidates: (a) PDLHED-bound SALT2 walker — mirror SPITBOL pmhbs; reuse existing PDLHED machinery; precedent at v311.sil:3975 (BAL walker); RECOMMENDED. (b) truncate-on-success with deferred-alts array — heavier.** Session #60 should implement (a). Findings in `csnobol4/docs/F-2-Step3a-session59-findings.md`. csnobol4 advanced to `1b59147`. |
| Icon Frontend Ladder | `GOAL-LANG-ICON.md` | one4all | IC-8 (session #18, 2026-04-30: two tactical IC-8 fixes — (a) `!N` numeric iteration: integer/real arg to `E_ITERATE` now coerces to image-string and iterates characters (`!-514`→`-`,`5`,`1`,`4`; `!12.5`→`1`,`2`,`.`,`5`); patched both icn_drive E_ITERATE handler (interp_eval-side, L191) and icn_eval_gen box-construction handler (L713) using `icn_real_str` (un-static'd from interp.c). (b) `===` (E_IDENTICAL) goal-directed evaluation: previously had NO interp_eval handler, fell through to `default → NULVCL` which is truthy, so every `if x === key(T)` succeeded spuriously — the root cause of the rung36_jcon_table NONMEMBER-leak (tdump leaked `&null:NONMEMBER` for every probed key). Fix in three sites: shared-switch `case E_IDENTICAL` in interp_eval (non-generator path), `icn_is_gen` adds E_IDENTICAL to gen-if-any-child-is list so `if x === key(T)` routes to icn_eval_gen, and new `icn_bb_identical_gen` box drives RHS as generator and tests identity each tick. New helper `icn_descr_identical` covers Icon `===` semantics: same type required (excepting DT_S/DT_SNUL null parity), strings byte-equal, ints/reals same value, tables/lists same pointer (identity not deep-equal). NONMEMBER-leak verified gone in rung36_jcon_table diff; remaining diffs are unrelated bugs (every-bang lvalue, augmented assign, image(?x) on empty table). All gates clean: smoke_icon 5/5, smoke_unified_broker 49/0, crosscheck_icon 4/0, test_icon_ir_all_rungs 188/45/30 of 263 (unchanged — affected tests stay .xfail due to other unimplemented features). Files touched: src/driver/interp.c +14/-2, src/runtime/interp/icn_runtime.c +99/-1, src/runtime/interp/icn_runtime.h +6/-0. one4all advances from 15648d3c to b6350608. Build hazard: changes to icn_runtime.h again required clean `find src -name '*.o' -delete` rebuild. **Next pivot:** rung36_jcon_table mutate-via-iterate family: `every !x := V`, `every x[key(x)] := V`, `every x[k] <- V` augmented-assign-on-match, plus `\x[k]`/`/x[k]` non-inserting null-tests. These all live at the IcnFrame/table-lvalue boundary and likely share a single fix.) |
| Prolog Frontend Ladder | `GOAL-LANG-PROLOG.md` | one4all | PL-12 (session 2026-04-30 #3, one4all `d9a9b99f`: 75% baseline preserved; **directive-binding bug fixed** — root cause was `polyglot.c::polyglot_execute` LANG_PL branch passing `env=NULL` to `interp_exec_pl_builtin`, NOT `interp.c:4445` as session #2 hypothesised. Fix `+51/-2` adds static helper `pl_directive_max_var_slot` + per-directive cenv allocation in polyglot_execute. Repro `:- assertz(test_g(hello)), test_g(G), write(G)` now prints `hello` (was `_G0`). **SWI suite unchanged at 43/57** because plunit harness asserts test goals from a directive but reads result-vars only inside clause-body `run_tests`/`pj_run_one`, which already had a proper env. Latent bug removed; foundation cleaner. **Also: session #2's Fix #3 (plunit throw-vs-succeed) plan invalidated** — empirically tested in #3 and confirmed it cannot help in isolation. The `string:number_string` "expected fail, succeeded" line is caused by `catch(Var,_,_)` returning success silently when Var holds a callable Term — same root cause as Fix #2, NOT a misclassified throw. Plunit v4 patch was applied, suite still 43/57, reverted. **Updated next-session plan: (1) Fix #2 properly via Term→EXPR bridge with var-pointer-keyed env (+3-4 suites → 46-47/57 = 81-82% ≥ 80% gate); (2) plunit v4 only AFTER Fix #2 lands; (3) other independent MISS fixes one at a time.**) |
| Raku Frontend Ladder | `GOAL-LANG-RAKU.md` | one4all | RK-34 |
| Snocone Frontend Ladder | `GOAL-LANG-SNOCONE.md` | one4all+corpus | D-1 |
| Rebus Frontend Ladder | `GOAL-LANG-REBUS.md` | one4all | RB-2 |
| Snocone claws5.sc | `GOAL-SNOCONE-CLAWS5.md` | one4all+corpus | CL-2 |
| Snocone treebank-list.sc | `GOAL-SNOCONE-TREEBANK-LIST.md` | one4all+corpus | TB-1 |
| Snocone Beauty         | `GOAL-SNOCONE-BEAUTY.md`       | corpus+one4all | SB-6.D (session #81, 2026-04-30: SB-5d.2 LANDED — `treebank-array.sc` byte-identical to .ref in all 3 modes (md5 `7096beb...`); rewrote two bare-juxtaposition concat sites in `node_repr`/`pp_node` as canonical Snocone integer-loop form mirroring `treebank-array.sno::nr_lp` and `pp_wch/pp_wlast/pp_wdone` exactly; added `GT(n,0)` guard in pp_node fixing latent zero-children bug. Lon's session-#80 minor edits to `claws5.sc`, `treebank-list.sc`, `treebank-array.sc` verified — treebank-list.sc preserved at PASS in all 3 modes; claws5.sc remains byte-identical to claws5.sno SPITBOL on both inputs (SB-5c.2 corpus-curation issue unchanged). Three baseline gates green PASS=5/PASS=42 SKIP=3/PASS=49; crosscheck snobol4=6, snocone=8 unchanged. SB-6.D investigation snapshot: `EVAL(EXPRESSION)` is no-op at beauty.sc's Reduce call site (1st EVAL returns same EXPRESSION descriptor; 2nd EVAL produces correct STRING `''` failure). Standalone `/tmp/repro2.sc` (omega-string-EVAL pattern matching semantic.sc::reduce shape) does NOT reproduce — first EVAL works correctly there. Bug requires the wrapped context (`nPush() && X4 && reduce(...) && nPop()` like Expr4 line 69 of beauty.sc); EXPRESSION descriptor at Reduce call site appears double-wrapped. **Session #82 next steps:** (1) run `/tmp/repro3.sc` to confirm wrapper exposes double-wrap; (2) SPITBOL cross-check on SNOBOL4-equivalent reproducer; (3) if confirmed, fix in `src/runtime/x86/snobol4_invoke.c` or EVAL/EXPRESSION descriptor packing path. corpus dirty (3 .sc); .github dirty (this update + goal file s#81 narrative); one4all/csnobol4/x64 clean.) |
| **Snocone Language: Space-Concat** | `GOAL-SNOCONE-LANG-SPACE.md` | one4all+corpus | LS-4.d (session 2026-04-30 #5: **LS-4.c LANDED.** Three pattern operator tiers added in `src/frontend/snocone/snocone.y` — `expr1` (match `?` → E_SCAN, right-assoc), `expr3` (alternation `|` → E_ALT n-ary fold), `expr4` (concat T_CONCAT → E_SEQ n-ary fold) — slotted between `expr0` (assignment) and `expr5` (comparison). Precedence chain now `=  <  ?  <  |  <  concat  <  ==  <  +/-  <  */  <  ^` (each binds tighter than the one to its left). `expr3`/`expr4` use snobol4.y:131,134 idiom: extend in-place when LHS is already same-kind n-ary node, else create fresh. Compound-assigns (`+=` `-=` `*=` `/=` `^=`) added to `expr0` level; each lowers to clone-LHS pattern `a += b` → `E_ASSIGN(a, E_ADD(clone(a), b))` via new `sc_clone_expr_simple` helper (shallow recursive clone — required because IR forbids node aliasing). T_CONCAT/T_MATCH/T_ALTERNATION/compound-assign tokens promoted out of catch-all into dedicated declaration blocks (cosmetic). Header comment consolidated with precedence-table summary. No bison conflicts. **Headline gate met:** parses `s = 'hello' ' world'` → `E_ASSIGN(s, E_SEQ(E_QLIT("hello"), E_QLIT(" world")))`. **Full chain demo from test:** `result = subject ? a b | c d` → `E_ASSIGN(result, E_SCAN(subject, E_ALT(E_SEQ(a,b), E_SEQ(c,d))))` — match pattern is the n-ary alt, alt children are the n-ary seqs. Lexer-behaviour note: `1+2` (no spaces) lexes as `T_INT T_UN_PLUS T_INT` per W{OP}W envelope rule — `1 + 2` required for binary T_ADDITION. SNOBOL4 surface convention preserved; documented in test. New gate `test_smoke_snocone_parse_c.sh` runs `test_snocone_parse_c.c` (14 test functions / **66/66 PASS**). Production gates remain green: smoke 5/5, beauty 42/0/3, broker 49/0; FSM lex 31/31; LS-4.a 35/35, LS-4.b 119/119. Combined LS-4.{a,b,c} = 220/220. **Archive cleanup invariant:** four active-code references to `archive/snocone_lex.*` still present (unchanged from LS-4.a); LS-4.j removes them. **Next: LS-4.d** — add subscripting `a[i,j]` → `E_IDX`. Call-form already landed in LS-4.b.) |
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
| NET Beauty Self-Host | `GOAL-NET-BEAUTY-SELF.md` | snobol4dotnet | S-2-bridge-7-fullscan (session #72, 2026-04-30 — IPC sync-step monitor confirmed divergence still at step #2839 (spl RETURN match NRETURN vs dot 19th CALL upr) on fresh session with betastack-failure-leak fix in place. C# function tracing ([QPM]/[PM]/[M] gated on MonitorIpc.TraceEnabled) added to PatternMatch/Scanner. Trace at ec=2840 showed *upr (UnevaluatedPattern node=5) being re-entered after the graft succeeds. Root cause: BetaStack is shared across PatternMatch invocations; nested PatternMatch (via $ *fn(...) immediate-assignment calling match() which runs its own ?) iterates the outer BetaStack in its commit loop, causing spurious extra function calls. Fix: save/restore BetaStack per PatternMatch invocation (fresh stack for each, restore on both success and failure paths). snobol4dotnet `a629a15`. Unit suite 2385p/0f/2s; Beauty 17/17 PASS; self-host UNCHANGED at 47 lines/Parse Error at snoDQ line 48 — step #2839 is a pre-existing bridge gap (spl doesn't emit VALUE on keyword stores), not the gating bug for line 48. Next bug: snoParse fails to parse `snoDQ = '"' BREAK('"' nl) '"'` on dot — likely FENCE/alternation in *snoSQ|*snoDQ not backtracking correctly when *snoSQ fails on the `'"'` single-quote string containing a double-quote. Diagnostic patches reverted per RULES.md.) |
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
