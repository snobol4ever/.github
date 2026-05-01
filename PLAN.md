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
| **CSN FENCE Bug Fix** | `GOAL-CSN-FENCE-FIX.md` | csnobol4 | F-2 Step 3a (session #54: implemented session #53's "targeted slot-zeroing" proposal at L_STARP2/L_DSARP2 — walk PDL from saved-pre-SCIN snapshot to current PDLPTR, zero slot[1] of non-FNC traps. **fence_suite 27/3/2 → 29 OK / 3 FAIL / 0 CRASH** (best ever; tests 119, 129 = canonical beauty-class CRASHes FIXED). fence_function 10/10 preserved. **BUT regresses inner-pattern alternation backtrack** — new 5-line regression guard repro `cmd=(LEN(1)\|LEN(2)); outer=(*cmd 'X'); s='ABX'` should match (SPITBOL ✓, csnobol4+s52 ✓) but FAILS under zeroing. Beauty regresses ~32 → ~10 lines. **NOT committed** per RULES.md regression-in-error-class. Saved as `csnobol4/docs/F-2-Step3a-session54-zeroing-attempt.diff`. **Genuine new contribution:** demonstrated via instrumented SALT2/SCIN1/L_UNSC/L_DSAR trace that leaked inner-PATBCL traps ARE legitimately consulted via outer's "redo *cmd" trap → DSAR → L_UNSC → PATBCL=cmd restored → walker dispatches inner alts correctly. Targeted zeroing destroys live state. Test 119 crashes because leaked inner trap is reached AFTER all DSAR-redo entries consumed — no remaining mechanism to re-route through L_UNSC. **Architectural fix shape: SPITBOL `=ndexc` sentinel analog (call it STREXCCL)** mirroring `p_nth` at sbl.min:12213. On STARP6/DSARP success when inner pushed entries, install sentinel trap whose handler restores PATBCL=inner before walker walks the leaked region. Session #55: implement STREXCCL — define constant, add PATBRA case, define L_STREXC handler, modify STARP6/DSARP to push sentinel conditionally on `PDLPTR > saved_snapshot`. Apply s52 patch first. Test gates: fence_function 10/10, fence_suite 30+/32, 5-line repro must produce `inner backtrack worked`, beauty ≥ 500 lines. Findings in `csnobol4/docs/F-2-Step3a-session54-findings.md`. corpus @ 6955503, csnobol4 working tree CLEAN at HEAD `447b411`. **Session #55**: did NOT implement STREXCCL. Added 16 depth-recursion stress tests (Tier F, IDs 132–147) to fence_suite/. Result: **all 16 PASS on csnobol4 baseline** — empirically confirms 119/129/130 bug class is narrow (requires `*var` + outer ARBNO + tail-anchor failure conjunction; NOT generic depth recursion, NOT generic FENCE-under-recursion, NOT double-fn dispatch, NOT mutual recursion). New baseline: fence_suite **40/2/6 of 48** (csnobol4) / 47/1 of 48 (SPITBOL). Tier F + 5-line guard5 = regression-prevention floor for session #56. corpus has 32 new untracked files (132–147 .sno/.ref); csnobol4 has Makefile/README.md/findings.md changes. NO runtime source touched. Findings in `csnobol4/docs/F-2-Step3a-session55-tier-f-findings.md`. Session #56 should implement STREXCCL with the 48-test gate.) **Session #56**: implemented STREXCCL in `isnobol4.c` (5 edits, ~50 lines): static descriptors + dispatch case 41 + L_STREXC handler + STARP6/DSARP2 PUSH(PDLPTR,YPTR) + STARP2 conditional install. **All floors preserved** (fence_function 10/10, Tier F 16/16, guard5 ✓) but **fence_suite did NOT improve**: same 43/3/2 as s52 alone. Trace evidence on test 114 (`STREXC_TRACE=1`) shows STREXCCL **does fire** but **PATBCL is already = inner-PATBCL** when walker reaches sentinel — refutes session #54's "leaked traps dispatched under wrong PATBCL" hypothesis. Some upstream handler sets PATBCL=inner during outer's failure walk before sentinel is reached. Saved as `csnobol4/docs/F-2-Step3a-session56-strexccl-attempt.diff` (combined with s52, 90 lines self-contained against HEAD `1b2e28a`, verified to reproduce gates). **Session #57** should apply session #56 patch and add a PATBCL-write logger at every `D(PATBCL) = ...` site to find which write sets PATBCL=inner during outer walk — that's the upstream bug. Then either fix that write or augment STREXCCL with a paired BOTTOM-of-region sentinel. Findings in `csnobol4/docs/F-2-Step3a-session56-findings.md`. csnobol4 working tree CLEAN at HEAD `1b2e28a`.) **Session #57**: applied s56 patch + instrumented all PATBCL touchpoints (3 D(PATBCL)= sites, 7 POP(PATBCL) sites, every SALT2 entry). Trace on test 119 **refutes both** session #54 (wrong-PATBCL-on-leaks) and session #56 (upstream-write-sets-PATBCL=inner). Decisive evidence: every PATBCL change in the run is accounted for; bug is **multi-iteration ARBNO leak class** — STREXCCL only protects most recent iteration; earlier ARBNO `*cmd` iterations left inner-pattern leaks below STREXCCL's reach. After STARP5 final POP restores PATBCL=outer, walker descends into iter#2's unprotected leaks at PDLPTR=0x...ae0 reading `{a=0x200, f=0, v=96}` under outer PATBCL → SCIN3 fallthrough → `D(outer + 0x200)` = garbage → ZCL=NULL → SEGV at isnobol4.c:11521. Three fix candidates documented: **(c)** persistent STREXCCL across iterations; **(b refined)** paired BOTTOM-sentinel; **(d)** PDL truncate + deferred-alt array. Diagnostic patch saved as `csnobol4/docs/F-2-Step3a-session57-diagnostic.diff` (145 lines, env-gated `PATBCL_LOG=1`, reusable). Findings in `csnobol4/docs/F-2-Step3a-session57-findings.md`. Working tree CLEAN at HEAD `273f5f3`. **Session #58** should read SPITBOL p_str/=ndexc/flpop carefully then implement (b/c/d).) **Session #58**: read SPITBOL p_exa/p_nth/p_exb/p_exc + p_aba/p_abb/p_abc/p_abd. Implemented paired top + bottom STREXCCL sentinels (s58 patch). **All 6 fence_suite CRASHes ELIMINATED** (44/4/0). fence_function 10/10 + Tier F 16/16 + guard5 preserved. Beauty 35→42 lines (first non-zero gain since session #45). Tests 119/129 went CRASH→FAIL (wrong-answer not crash). NOT committed (RULES.md). Saved as `csnobol4/docs/F-2-Step3a-session58-paired-strexc-attempt.diff`. csnobol4 advanced to `68075bb` (docs only). **Session #59**: continued from s58; added SALT2-entry trace; test 119 produced only 7 events before "unexpected match". **Architectural diagnosis: CSNOBOL4 uses PATBCL+offset addressing while SPITBOL uses direct memory pointers — leaked inner SCIN3 entries become semantically wrong (not crashing) when read under outer PATBCL.** Two STREXBCL variants tested: FAIL-on-fire regressed 44/4/0→43/5/0; PATBCL=outer+continue identical to s58. **Two structural fix candidates: (a) PDLHED-bound SALT2 walker — mirror SPITBOL pmhbs; reuse existing PDLHED machinery; precedent at v311.sil:3975 (BAL walker); RECOMMENDED. (b) truncate-on-success with deferred-alts array — heavier.** Session #60 should implement (a). Findings in `csnobol4/docs/F-2-Step3a-session59-findings.md`. csnobol4 advanced to `1b59147`. **Session #64**: per s63 plan, instrumented every `S_L(TXSP) = ...` write site in `isnobol4.c`; pinpointed the corruption to `isnobol4.c:11498` `S_L(TXSP) = D_A(YCL)` in L_SALT2 — fires for ALL non-zero PATICL entries, including FNC traps (STREXCCL, FNCDCL, etc.) where slot[2] is handler-specific data (a heap PATBCL pointer for STREXCCL), NOT a cursor offset. **Fix landed**: gate the assignment + goto-SCIN3 inside `if (!(D_F(PATICL) & FNC))` block. Eliminates the latent corruption mode session #63 traced. Gate-neutral: fence_function 10/10, fence_suite 44/4/0, guard5 OK, beauty 42 lines (all unchanged from s58 baseline). Also attempted FNCDCL-at-P2 placement (move FENCE seal from clean PDL base P1 to top-of-leaks P2 so walker hits seal before any leaked alts) — **refuted by trace evidence**: FNCDCL is correctly placed at P2 but never fires. **Architectural mechanism named**: after FNCA's success, control returns up to enclosing `*outer`'s STARP2, which `POP(PDLPTR)` restores PDLPTR to its `*outer`-entry value (far below FNCDCL@P2) — **abandoning FENCE's seal**. STARP2 then installs its own STREXCCL pair routing the walker through the abandoned region under inner PATBCL=cmd. Walker dispatches the still-physically-present leaked FENCE alt-conts as if they were legitimate `*outer` redo conts. Refines session #57's framing: not just "leaks unprotected" but "STARP2 abandons seal AND re-routes walker through abandoned leaks". **Session #65 fix recommendation**: implement session #57 (d) — zero leaked alt-conts at FNCA-success time (NOT at STARP2 like session #54 tried). Walk PDL from P1+3*DESCR to P2 at FNCA-success; zero slot[1] of any non-FNC trap. Should preserve guard5 (no FENCE involved → FNCA never runs → zeroing never fires) and fix tests 119/124/127/129 (FENCE involved → leaks zeroed before STARP2 can route through them). Findings in `csnobol4/docs/F-2-Step3a-session64-findings.md`. csnobol4 working tree clean after commit. |
| Icon Frontend Ladder | `GOAL-LANG-ICON.md` | one4all | IC-9 (session #24, 2026-05-01: records-as-iterables landed. PASS counts unchanged at rung01-36 PASS=199/FAIL=34/XFAIL=30 and rung_36 PASS=11/FAIL=34/XFAIL=30 — `rung36_jcon_record` is .xfail-listed and still 4 lines short of PASS — but went from 10+ lines of garbled raw-bytes output to 4 clean missing lines, with five distinct record-shape root causes fixed. Session #23 (HEAD `1233e800`) closed +11 PASS rung01-36 (188→199) and +3 PASS rung_36 (6→9) via 8 fixes — icn_bb_cat_gen re-pump, E_SECTION+/- read, E_CAT/E_POW Icon-mode, left/right/center spec, integer/numeric radix, list(n,x), static persistence. Session #24 fixes (5): (1) icn_bb_record_iterate Byrd box for `!record` generator; (2) interp_eval E_ITERATE returns `inst.u->fields[0]` for record scalar; (3) E_ASSIGN icon-frame E_ITERATE LHS gets DT_DATA-record arm walking all fields; (4) E_AUGOP E_ITERATE LHS same arm via AUGOP_CELL; (5) E_RANDOM record arm + new E_RANDOM-LHS branch for `?b := V` random-field write. Files: src/driver/interp.c, src/runtime/interp/icn_runtime.c, src/frontend/icon/icon_gen.c, src/frontend/icon/icon_gen.h. No header struct changes. Gates clean: smoke 5/0, broker 49/0, crosscheck 4/0/0. **Next pivot:** record subscript by integer (`b[N]` Nth field) and string (`b["fN"]` named field) under every — single subscript_get arm before icnlist arm. Closes remaining 4 lines of rung36_jcon_record.) |
| Prolog Frontend Ladder | `GOAL-LANG-PROLOG.md` | one4all+corpus | PL-12 (session 2026-05-01 #4: 2 commits landed gate-neutral and bisectable. one4all `86aee891` Step F.1.b — module-qualified `:` operator parsing: single-line `{ ":", 200, ASSOC_RIGHT }` added to BIN_OPS in prolog_parse.c. Lexer already produced TK_OP `:` via the graphic-char set; `:-` lexes greedily so neck syntax is unaffected. test_call.pl bridge-off parse errors 111→47 (lines 103-110 region clean — `call8:does_not_exist/8`, `_:does_not_exist/8`, `Goal = call(call8:does_not_exist, ...)` all parse correctly building `:(Module,Goal)` compounds; remaining lines 186+ errors are the `@` call-at-context operator — separate gap, F.4 next session). corpus `92f3179` Step F.3 — split_string/4 + string_bytes/3 stubs in plunit.pl (+48): split_string is a code-list splitter on separator-char set with pad-char strip left+right per part, verified against four test_string.pl shapes; string_bytes is encoding-aware byte list, utf8 = atom_codes / utf16be = interleave 0-bytes-before / utf16le = interleave 0-bytes-after (ASCII-only sufficient — non-ASCII tests already commented out via prior session UTF-8 lex patch), bidirectional verified for six ASCII-mode tests. **Bridge-on probes**: bridge + E.1 + E.2 + F.1.b + F.3 = **17/57** (+1 from F.3 unblocking test_string string_bytes); F.1.b was bridge-on-net-zero on suite-line metric (foundational — prevents parse-error cascades the bridge would surface). Smoke 5/5, broker 49/49, SWI bridge-neutral 43/57 unchanged at session-end. **NEXT SESSION:** F.2 — investigate the 17→43 bridge-on gap. Likely culprits: (a) `\+/1`, `once/1`, `not/1` still dispatch through pre-bridge default-arm (bridge currently only wires into catch/3 per v3 diff); (b) call/N's `=..` rebuild + tail-call may mis-handle Term-not-Expr inner goals; (c) setof/3 / setup_call_cleanup/3 stub bodies use catch that only works bridge-correctly from non-bridged contexts. Trace one MISS suite at a time bridge-on, isolate first failing sub-test, fix dispatcher gap, iterate. F.4 — `@` operator (yfx 200) one-line BIN_OPS addition for test_call lines 186-200. Then E (re-attempt land bridge once bridge-on >= 43/57). Then G (numbervars/3 negative start, =@=, compound/1 edge cases).) |
| Raku Frontend Ladder | `GOAL-LANG-RAKU.md` | one4all | RK-34 |
| Snocone Frontend Ladder | `GOAL-LANG-SNOCONE.md` | one4all+corpus | D-1 |
| Rebus Frontend Ladder | `GOAL-LANG-REBUS.md` | one4all | RB-2 |
| Snocone claws5.sc | `GOAL-SNOCONE-CLAWS5.md` | one4all+corpus | CL-2 |
| Snocone treebank-list.sc | `GOAL-SNOCONE-TREEBANK-LIST.md` | one4all+corpus | TB-1 |
| Snocone Beauty         | `GOAL-SNOCONE-BEAUTY.md`       | corpus+one4all | SB-6.D (session #81, 2026-04-30: SB-5d.2 LANDED — `treebank-array.sc` byte-identical to .ref in all 3 modes (md5 `7096beb...`); rewrote two bare-juxtaposition concat sites in `node_repr`/`pp_node` as canonical Snocone integer-loop form mirroring `treebank-array.sno::nr_lp` and `pp_wch/pp_wlast/pp_wdone` exactly; added `GT(n,0)` guard in pp_node fixing latent zero-children bug. Lon's session-#80 minor edits to `claws5.sc`, `treebank-list.sc`, `treebank-array.sc` verified — treebank-list.sc preserved at PASS in all 3 modes; claws5.sc remains byte-identical to claws5.sno SPITBOL on both inputs (SB-5c.2 corpus-curation issue unchanged). Three baseline gates green PASS=5/PASS=42 SKIP=3/PASS=49; crosscheck snobol4=6, snocone=8 unchanged. SB-6.D investigation snapshot: `EVAL(EXPRESSION)` is no-op at beauty.sc's Reduce call site (1st EVAL returns same EXPRESSION descriptor; 2nd EVAL produces correct STRING `''` failure). Standalone `/tmp/repro2.sc` (omega-string-EVAL pattern matching semantic.sc::reduce shape) does NOT reproduce — first EVAL works correctly there. Bug requires the wrapped context (`nPush() && X4 && reduce(...) && nPop()` like Expr4 line 69 of beauty.sc); EXPRESSION descriptor at Reduce call site appears double-wrapped. **Session #82 next steps:** (1) run `/tmp/repro3.sc` to confirm wrapper exposes double-wrap; (2) SPITBOL cross-check on SNOBOL4-equivalent reproducer; (3) if confirmed, fix in `src/runtime/x86/snobol4_invoke.c` or EVAL/EXPRESSION descriptor packing path. corpus dirty (3 .sc); .github dirty (this update + goal file s#81 narrative); one4all/csnobol4/x64 clean.) |
| **Snocone Language: Space-Concat** | `GOAL-SNOCONE-LANG-SPACE.md` | one4all+corpus | LS-6.c (session 2026-05-01 #7: LS-6.a + LS-6.b CLOSED, **LS-7 documentation pass LANDED** — all four sub-rungs done. LS-7.a: new `## Snocone language facts` section in `RULES.md`. LS-7.b: rewrote `GOAL-SNOCONE-BEAUTY.md` "Snocone language facts" section for post-LS-4 reality (operator table, `function` rename, added constructs, SPITBOL-superset invariant). LS-7.c: new `## Snocone front-end` section in `REPO-one4all.md` (status, source paths, lexer/grammar shape, build path, gates). LS-7.d: new `corpus/programs/snocone/LANGUAGE.md` (short tour for the next reader). All four gates re-verified green: smoke snocone 5/0, beauty 42/0/3, broker 49/0, smoke snobol4 7/0 (no-regression bonus). LS-6.c REMAINS OPEN, GATED on GOAL-SNOCONE-BEAUTY SB-6.D `EVAL(EXPRESSION)` double-wrap fix at beauty.sc Reduce call site — `beauty.ref` cannot exist until SB-6.D lands. After LS-6.c lands, GOAL closes and `GOAL-LANG-SNOCONE` advances D-1 → D-2.) |
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
| NET Beauty Self-Host | `GOAL-NET-BEAUTY-SELF.md` | snobol4dotnet | S-2-bridge-7-byrd-pattern (session #76, 2026-05-01 — diagnostic only, no commit. spl-side PM fire-points still not wired. C# function trace (DOT_TRACE_ALT=1) between last-agreed and first-diverged IPC sync-step positions revealed: `*snoString` is NEVER saved as an alternate in the entire beauty self-host run. `PosPattern` fails with ALT_STACK_EMPTY inside grafted sub-patterns. `AbstractSyntaxTree.ValidateAlternates()` diagnostic found **27,763 RIGHT-ALT anomalies in Graft sub-ASTs** — terminals that are RIGHT children of AlternatePattern nodes but have non-(-1) Alternate values. These come from `ConditionalVariableAssociationBackup` nodes inside the `.` operator's internal AlternatePattern structure. The `ComputeAlternate` logic appears correct for the simple FENCE-alternation cases tested in isolation; the bug only manifests in the full beauty self-host context (state-dependent, confirmed since session #62). `AbstractSyntaxTree.Graft` remap `newAlt = n.Alternate >= 0 ? n.Alternate + offset : -1` may not account for cases where `ConditionalVariableAssociationBackup`'s Alternate (computed in the sub-AST) incorrectly points to something. All diagnostic patches reverted; baseline preserved at 47 stderr lines. **Session #77 next steps:** (1) Wire spl-side PM fire-points (`x64/osint/monitor_ipc_runtime.c`, `sbl.min`, regenerate `bootstrap/sbl.asm`, gate `SPL_PM_TRACE=1`) — this is the critical missing piece for two-way comparison; (2) Write targeted unit test for `FENCE(*fnA | *fnB)` where fnA evaluates to a pattern containing `.` (ConditionalVariableAssociation) capture, verify Alternate chain is correct; (3) Trace `ComputeAlternate` in Graft sub-AST for `ConditionalVariableAssociationBackup` to see why it gets non-(-1) when it's RIGHT child of AlternatePattern; (4) Fix. Baseline: beauty 17/17 PASS, self-host 47 stderr lines, build clean.) |
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
