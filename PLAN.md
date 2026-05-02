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
| **CSN FENCE Bug Fix** | `GOAL-CSN-FENCE-FIX.md` | csnobol4 | F-2 Step 3a (session #54: implemented session #53's "targeted slot-zeroing" proposal at L_STARP2/L_DSARP2 — walk PDL from saved-pre-SCIN snapshot to current PDLPTR, zero slot[1] of non-FNC traps. **fence_suite 27/3/2 → 29 OK / 3 FAIL / 0 CRASH** (best ever; tests 119, 129 = canonical beauty-class CRASHes FIXED). fence_function 10/10 preserved. **BUT regresses inner-pattern alternation backtrack** — new 5-line regression guard repro `cmd=(LEN(1)\|LEN(2)); outer=(*cmd 'X'); s='ABX'` should match (SPITBOL ✓, csnobol4+s52 ✓) but FAILS under zeroing. Beauty regresses ~32 → ~10 lines. **NOT committed** per RULES.md regression-in-error-class. Saved as `csnobol4/docs/F-2-Step3a-session54-zeroing-attempt.diff`. **Genuine new contribution:** demonstrated via instrumented SALT2/SCIN1/L_UNSC/L_DSAR trace that leaked inner-PATBCL traps ARE legitimately consulted via outer's "redo *cmd" trap → DSAR → L_UNSC → PATBCL=cmd restored → walker dispatches inner alts correctly. Targeted zeroing destroys live state. Test 119 crashes because leaked inner trap is reached AFTER all DSAR-redo entries consumed — no remaining mechanism to re-route through L_UNSC. **Architectural fix shape: SPITBOL `=ndexc` sentinel analog (call it STREXCCL)** mirroring `p_nth` at sbl.min:12213. On STARP6/DSARP success when inner pushed entries, install sentinel trap whose handler restores PATBCL=inner before walker walks the leaked region. Session #55: implement STREXCCL — define constant, add PATBRA case, define L_STREXC handler, modify STARP6/DSARP to push sentinel conditionally on `PDLPTR > saved_snapshot`. Apply s52 patch first. Test gates: fence_function 10/10, fence_suite 30+/32, 5-line repro must produce `inner backtrack worked`, beauty ≥ 500 lines. Findings in `csnobol4/docs/F-2-Step3a-session54-findings.md`. corpus @ 6955503, csnobol4 working tree CLEAN at HEAD `447b411`. **Session #55**: did NOT implement STREXCCL. Added 16 depth-recursion stress tests (Tier F, IDs 132–147) to fence_suite/. Result: **all 16 PASS on csnobol4 baseline** — empirically confirms 119/129/130 bug class is narrow (requires `*var` + outer ARBNO + tail-anchor failure conjunction; NOT generic depth recursion, NOT generic FENCE-under-recursion, NOT double-fn dispatch, NOT mutual recursion). New baseline: fence_suite **40/2/6 of 48** (csnobol4) / 47/1 of 48 (SPITBOL). Tier F + 5-line guard5 = regression-prevention floor for session #56. corpus has 32 new untracked files (132–147 .sno/.ref); csnobol4 has Makefile/README.md/findings.md changes. NO runtime source touched. Findings in `csnobol4/docs/F-2-Step3a-session55-tier-f-findings.md`. Session #56 should implement STREXCCL with the 48-test gate.) **Session #56**: implemented STREXCCL in `isnobol4.c` (5 edits, ~50 lines): static descriptors + dispatch case 41 + L_STREXC handler + STARP6/DSARP2 PUSH(PDLPTR,YPTR) + STARP2 conditional install. **All floors preserved** (fence_function 10/10, Tier F 16/16, guard5 ✓) but **fence_suite did NOT improve**: same 43/3/2 as s52 alone. Trace evidence on test 114 (`STREXC_TRACE=1`) shows STREXCCL **does fire** but **PATBCL is already = inner-PATBCL** when walker reaches sentinel — refutes session #54's "leaked traps dispatched under wrong PATBCL" hypothesis. Some upstream handler sets PATBCL=inner during outer's failure walk before sentinel is reached. Saved as `csnobol4/docs/F-2-Step3a-session56-strexccl-attempt.diff` (combined with s52, 90 lines self-contained against HEAD `1b2e28a`, verified to reproduce gates). **Session #57** should apply session #56 patch and add a PATBCL-write logger at every `D(PATBCL) = ...` site to find which write sets PATBCL=inner during outer walk — that's the upstream bug. Then either fix that write or augment STREXCCL with a paired BOTTOM-of-region sentinel. Findings in `csnobol4/docs/F-2-Step3a-session56-findings.md`. csnobol4 working tree CLEAN at HEAD `1b2e28a`.) **Session #57**: applied s56 patch + instrumented all PATBCL touchpoints (3 D(PATBCL)= sites, 7 POP(PATBCL) sites, every SALT2 entry). Trace on test 119 **refutes both** session #54 (wrong-PATBCL-on-leaks) and session #56 (upstream-write-sets-PATBCL=inner). Decisive evidence: every PATBCL change in the run is accounted for; bug is **multi-iteration ARBNO leak class** — STREXCCL only protects most recent iteration; earlier ARBNO `*cmd` iterations left inner-pattern leaks below STREXCCL's reach. After STARP5 final POP restores PATBCL=outer, walker descends into iter#2's unprotected leaks at PDLPTR=0x...ae0 reading `{a=0x200, f=0, v=96}` under outer PATBCL → SCIN3 fallthrough → `D(outer + 0x200)` = garbage → ZCL=NULL → SEGV at isnobol4.c:11521. Three fix candidates documented: **(c)** persistent STREXCCL across iterations; **(b refined)** paired BOTTOM-sentinel; **(d)** PDL truncate + deferred-alt array. Diagnostic patch saved as `csnobol4/docs/F-2-Step3a-session57-diagnostic.diff` (145 lines, env-gated `PATBCL_LOG=1`, reusable). Findings in `csnobol4/docs/F-2-Step3a-session57-findings.md`. Working tree CLEAN at HEAD `273f5f3`. **Session #58** should read SPITBOL p_str/=ndexc/flpop carefully then implement (b/c/d).) **Session #58**: read SPITBOL p_exa/p_nth/p_exb/p_exc + p_aba/p_abb/p_abc/p_abd. Implemented paired top + bottom STREXCCL sentinels (s58 patch). **All 6 fence_suite CRASHes ELIMINATED** (44/4/0). fence_function 10/10 + Tier F 16/16 + guard5 preserved. Beauty 35→42 lines (first non-zero gain since session #45). Tests 119/129 went CRASH→FAIL (wrong-answer not crash). NOT committed (RULES.md). Saved as `csnobol4/docs/F-2-Step3a-session58-paired-strexc-attempt.diff`. csnobol4 advanced to `68075bb` (docs only). **Session #59**: continued from s58; added SALT2-entry trace; test 119 produced only 7 events before "unexpected match". **Architectural diagnosis: CSNOBOL4 uses PATBCL+offset addressing while SPITBOL uses direct memory pointers — leaked inner SCIN3 entries become semantically wrong (not crashing) when read under outer PATBCL.** Two STREXBCL variants tested: FAIL-on-fire regressed 44/4/0→43/5/0; PATBCL=outer+continue identical to s58. **Two structural fix candidates: (a) PDLHED-bound SALT2 walker — mirror SPITBOL pmhbs; reuse existing PDLHED machinery; precedent at v311.sil:3975 (BAL walker); RECOMMENDED. (b) truncate-on-success with deferred-alts array — heavier.** Session #60 should implement (a). Findings in `csnobol4/docs/F-2-Step3a-session59-findings.md`. csnobol4 advanced to `1b59147`. **Session #64**: per s63 plan, instrumented every `S_L(TXSP) = ...` write site in `isnobol4.c`; pinpointed the corruption to `isnobol4.c:11498` `S_L(TXSP) = D_A(YCL)` in L_SALT2 — fires for ALL non-zero PATICL entries, including FNC traps (STREXCCL, FNCDCL, etc.) where slot[2] is handler-specific data (a heap PATBCL pointer for STREXCCL), NOT a cursor offset. **Fix landed**: gate the assignment + goto-SCIN3 inside `if (!(D_F(PATICL) & FNC))` block. Eliminates the latent corruption mode session #63 traced. Gate-neutral: fence_function 10/10, fence_suite 44/4/0, guard5 OK, beauty 42 lines (all unchanged from s58 baseline). Also attempted FNCDCL-at-P2 placement (move FENCE seal from clean PDL base P1 to top-of-leaks P2 so walker hits seal before any leaked alts) — **refuted by trace evidence**: FNCDCL is correctly placed at P2 but never fires. **Architectural mechanism named**: after FNCA's success, control returns up to enclosing `*outer`'s STARP2, which `POP(PDLPTR)` restores PDLPTR to its `*outer`-entry value (far below FNCDCL@P2) — **abandoning FENCE's seal**. STARP2 then installs its own STREXCCL pair routing the walker through the abandoned region under inner PATBCL=cmd. Walker dispatches the still-physically-present leaked FENCE alt-conts as if they were legitimate `*outer` redo conts. Refines session #57's framing: not just "leaks unprotected" but "STARP2 abandons seal AND re-routes walker through abandoned leaks". **Session #65 fix recommendation**: implement session #57 (d) — zero leaked alt-conts at FNCA-success time (NOT at STARP2 like session #54 tried). Walk PDL from P1+3*DESCR to P2 at FNCA-success; zero slot[1] of any non-FNC trap. Should preserve guard5 (no FENCE involved → FNCA never runs → zeroing never fires) and fix tests 119/124/127/129 (FENCE involved → leaks zeroed before STARP2 can route through them). Findings in `csnobol4/docs/F-2-Step3a-session64-findings.md`. csnobol4 working tree clean after commit.) **Session #65** (2026-05-01): suite verification + Tier G additions; NO runtime change. Built csnobol4 from clean clone at HEAD `723ac19` (s64), cloned x64 to access SPITBOL oracle, re-measured fence_suite against SPITBOL. **SPITBOL was 46/2/0 of 48, NOT 47/1 as goal file claimed** — two genuine corpus errors: (a) 127 .ref generated under SPITBOL `-b` (case-fold ON) but Makefile invokes `-bf` (case-fold OFF), so .ref was wrong for the gate; (b) tests 140/141 used label names `shift`/`Shift` and `grab`/`Grab` colliding under SPITBOL case-fold default. Fixed both — renamed labels in 140/141 (`inner`/`outer`, `grab`/`catch`), regenerated 127 .ref against `-bf`. **Test 118 was structurally degenerate**: source assigns `outer = ARBNO(*cmd)` AFTER the match, so `*outer` dereferenced unassigned variable at match time — FENCE machinery never ran, "pass" was for the wrong reason. Documented via comment-only update; replaced with test 149 (proper version). **Added Tier G** (148–152, oracle-verified): 148 = bug-class POSITIVE shorter-input variant of 119 (input `'ab'`); 149 = corrected 118 (outer pre-match); **150 = NEGATIVE discriminator** — same conjunction as 119 but explicit-alternation iterator instead of ARBNO, PASSES csnobol4, proves bug needs ARBNO specifically; **151 = NEGATIVE discriminator** — ARBNO of *inline* FENCE with backtrack-needed input, PASSES csnobol4, proves bug needs `*var` indirection (not inline FENCE); 152 = 127 with capture vars renamed (S→SVAL etc.) to avoid s/S case-fold collision, exposes genuine conditional-assign-not-committed bug (bug 2) cleanly. Suite results: **SPITBOL `-bf` 53/0/0 of 53** (clean oracle, first time); **csnobol4 46/7/0 of 53** (7 FAILs = 119/124/127/129/148/149/152 = bug-class regression target). 150/151 negative discriminators sharpen bug-class to: `*var` indirection of FENCE + ARBNO outer iterator + tail-anchor backtrack. Ruled out broader hypotheses sessions #50/#54/#57 had entertained. **Open tension surfaced**: session #62's PDL-dump diagnostic (no SALT2 events between post-STARP2 dump and wrong-match output → bug on success path) vs session #64's framing (failure-walker dispatches abandoned-seal region → bug on failure-walker path). Sessions #62/#64 not reconciled. Session #66 should re-run #62's PDL-dump on test 148 (simpler than 119: input `'ab'`, single ARBNO iteration of FENCE-sealed `'a'` — smaller diagnostic state-space). Trace decides whether s64's FNCA-success leaked-alt zeroing plan is right (SALT2 events fire on wrong-match path) or whether investigation should redirect to STARP2's redo dispatch (no SALT2 events). Findings in `csnobol4/docs/F-2-Step3a-session65-findings.md`. csnobol4 advanced to `5fbf2ce` (Makefile + README + findings.md), corpus advanced to `6f00145` (4 modified + 10 new test files). **Session #65 (continued, csnobol4 `b2764cf`):** attribute-grid analysis of 7 FAILs vs 46 OKs isolated **the discriminator on a single line**: `L_FNCD: BRANCH(FAIL)` at `isnobol4.c:12437`. SPITBOL's analog `p_fnd` (sbl.min:12044) ends with `brn flpop` which drops into `failp` — pops next alt off stack and dispatches it. csnobol4's `BRANCH(FAIL)` is `return 1` from SCIN — exits the entire scan. ALL 7 FAILs share the shape: at FNCDCL fire-time, PDL contains both legitimate outer alts (below seal-base) AND leaked inner-FENCE alts (above-but-physically-still-present). Cluster A (119/129/148/149) symptom: walker matches via leaked alts. Cluster B (124/127/152) symptom: walker fails before legitimate outer alts. Same root cause, opposite symptoms. Smallest cluster-B repro: `s POS(0) (FENCE('if') | SPAN('lc')) RPOS(0)` on `'iffoo'` — SPITBOL matches, csnobol4 fails. **Attempt**: `BRANCH(FAIL) → goto L_TSALT`. Result: 124 went FAIL→OK ✓, but 150 went OK→FAIL ✗ (negative discriminator regressed). Net 46/7/0 unchanged but a previously-passing test now wrong-answer. Per RULES.md NOT committed. Saved as `csnobol4/docs/F-2-Step3a-session65-L_FNCD-attempt.diff` (1-line, applies clean). Why 150 regressed: BRANCH(FAIL) was over-correcting (blocked all alts including leaked ones) — removing it lets walker reach LEAKED alts. Cluster A failures and 150's regression are the same mechanism. **The L_FNCD fix IS architecturally correct and IS necessary, but must be COMPOSED with leak removal.** Session #66 should: (1) `git apply` the L_FNCD diff; (2) implement session #64's proposed FNCA-success leaked-alt zeroing as the composing partner; (3) verify all 7 FAILs flip OK AND 150 stays OK AND Tier F preserved AND guard5 + fence_function preserved. The L_FNCD discovery resolves the previously-noted session #62 vs #64 narrative tension: BOTH framings were partially right — #64's failure-walker path is real (BRANCH(FAIL) is on the failure walker) but #62's success-path observation is also real (the leaks form on success path). Findings in `csnobol4/docs/F-2-Step3a-session65-L_FNCD-findings.md` (175 lines). **Session #66 (2026-05-01):** applied L_FNCD `goto L_TSALT` patch + implemented session #64's FNCA-success leaked-alt zeroing. Composed result identical to L_FNCD-only: **46/7/0** with 124↔150 swap. Zeroing fired correctly (verified) but had no effect on cluster A. Reverted both, kept env-gated trace (saved as `docs/F-2-Step3a-session66-diagnostic.diff`), ran on test 148 (smallest cluster A repro: input `'ab'`). **Decisive trace evidence: bug is a SCIN3-pushed entry at PDLPTR=e910 with slot[1]={a=0x60,f=0}, sitting INSIDE the protected leak region (between bottom-STREXCCL@e8e0 and top-STREXCCL@e940).** After top-STREXCCL switches PATBCL=cmd, walker reads this non-FNC entry, session #64's SCIN3 fall-through dispatches `D(cmd+0x60+DESCR)` = a real cmd-pattern node (the 'ab' alt of `'a'|'ab'`), match succeeds. **Resolves session #62 vs #64 tension definitively:** bug is on failure-walker path (#64) but inside the protected region (NOT in an "abandoned" region as #64 framed). **Refutes FNCA-success zeroing approach:** the entry lives in OUTER scan's frame [STREX_entrypdl..PDLPTR_at_STARP2_entry], OUTSIDE FNCA's [P1..P2] frame — FNCA-success literally cannot reach it. **Recommends option (A2) for session #67:** at L_STARP2 success, walk leak region [STREX_entrypdl+3*DESCR..PDLPTR_at_STARP2_entry]; if ANY entry is FNCDCL, zero slot[1] of all non-FNC entries in the region; else leave alone. Conditional design preserves guard5 (no FENCE → no FNCDCL → no zeroing → DSAR-redo machinery intact) and should fix all 7 cluster A/B FAILs. Gate prediction: ≥51/53. Findings in `csnobol4/docs/F-2-Step3a-session66-findings.md`. csnobol4 advanced to `451ccae` (docs only). **Session #67 (2026-05-02):** implemented session #66's option (A2) — applied L_FNCD `goto L_TSALT` patch + added zeroing of non-FNC slot[1]s in leak region at L_STARP2. Three gate variants tested: A2 + FNCDCL-in-current-region (s66 plan), A2 + FNCDCL-anywhere-PDLHED..PDLPTR, A2 unconditional. **Best gate-target-meeting: unconditional 51/2/0** but BREAKS guard5 — same regression session #54 hit. **Best floor-preserving: PDLHED variant 47/6/0** (gains test 124, all floors preserved). **Genuinely-new finding: refutes session #66 framing for Cluster A.** Trace evidence on test 148 with `A2_TRACE=1` shows STARP2 #1 fires BEFORE FNCA runs anywhere on PDL — the bug entry `{a=0x60}` lives in STARP2 #1's leak region but at that moment FNCDCL doesn't exist anywhere on PDL. Session #66 hypothesized "leaked inner-FENCE alt-cont"; that requires FENCE to have run, but it hasn't yet at STARP2 #1 time. **The leak source is NOT FENCE's inner alt-conts** — some pattern-matching activity inside STARP6 #1's SCIN call pushes the `{a=0x60}` entry. The walker later mis-routes through it because STARP2 #1's STREXCCL pair switches PATBCL=cmd, and 0x60 is a valid offset inside cmd's pattern (the 'ab' alt). Composed s67 fix saved as `csnobol4/docs/F-2-Step3a-session67-A2-attempt.diff` (54 lines, applies clean to HEAD `451ccae`, verified to reproduce 47/6/0). Diagnostic instrumentation saved as `csnobol4/docs/F-2-Step3a-session67-diagnostic.diff` (96 lines, env-gated `A2_TRACE=1`: STARP6/DSARP2 entry counters, A2 STARP2 PDL dump with FNC-case identification, FNCA-success FNCDCL placement log). Five fix candidates documented for session #68 (findings.md). **Session #68 should investigate STARP6 #1's identity** — find which PATBRA case dispatched into the SCIN3 push that left `{a=0x60}` on PDL. That primitive's success-path is missing a PDLPTR rewind step. Findings in `csnobol4/docs/F-2-Step3a-session67-findings.md`. **Session #67 (cont., BB FENCE per user direction):** implemented Byrd Box FENCE — 4 ports (alpha/beta/gamma/omega), C-stack-local storage via `struct fnc_bb` at top of SCIN1 (immune to RSTSTK), two-trap protocol (alpha pushes SCFLCL, beta replaces in-place with FNCDCL), PDL truncation at beta makes seal physical. **Gate: 46/7/0** — closes Cluster B (test 124) but regresses test 150 (negative discriminator), same trade-off as L_FNCD-only. Net suite count unchanged from baseline. **Architectural verdict: BB strictly cleaner than cstack PUSH/POP** — 9-PUSH/9-POP → 9 C-local assigns, no RSTSTK hazard, 4 ports clearly labeled. **Cluster A unchanged** because its bug entry is pushed by ARBNO/STAR machinery BEFORE any FENCE machinery runs (session #67 earlier finding via trace) — no FENCE rewrite can close it. **A2 zeroing is orthogonal to BB** — A2 cleans outer-scope PDL at L_STARP2, BB cleans inner-scope PDL at FENCE boundaries. Composing BB + A2 should give 47/6/0 with cleaner architecture. BB patch saved as `csnobol4/docs/F-2-Step3a-session67-BB-FENCE.diff` (202 lines, applies clean to HEAD `451ccae`). **Two competing patches available for session #68:** A2 (gate-incremental, 47/6/0) and BB (architectural, 46/7/0); recommendation is to compose them. csnobol4 working tree CLEAN at HEAD `451ccae`. NO runtime source committed (only docs). Session #68 should also pivot Cluster A diagnosis to STARP6 #1's source primitive — find which PATBRA case left `{a=0x60}` on PDL. |
| Icon Frontend Ladder | `GOAL-LANG-ICON.md` | one4all | IC-9 (session #28, 2026-05-02: E_SEQ Icon conjunction fix landed — & operator now returns last value not string-cat; PASS=201 (+2 on full ladder), rung36 PASS=13 unchanged. Remaining open: &pos := N inside scan context assigns icn_scan_pos but reading &pos in same E_SEQ body returns old value — secondary bug, needs trace to localise read path. one4all HEAD 98b6e50d.) |
| **Prolog Frontend Ladder** | `GOAL-LANG-PROLOG.md` | one4all+corpus | **PR-19e** (PR-19d LANDED — findall/3 E_VAR bridge. rung34 5/5. Next: setup_call_cleanup/3) |
| Raku Frontend Ladder | `GOAL-LANG-RAKU.md` | one4all | RK-34 |
| Snocone Frontend Ladder | `GOAL-LANG-SNOCONE.md` | one4all+corpus | D-1 |
| Rebus Frontend Ladder | `GOAL-LANG-REBUS.md` | one4all | RB-2 |
| Snocone claws5.sc | `GOAL-SNOCONE-CLAWS5.md` | one4all+corpus | CL-2 |
| Snocone treebank-list.sc | `GOAL-SNOCONE-TREEBANK-LIST.md` | one4all+corpus | TB-1 |
| Snocone Beauty         | `GOAL-SNOCONE-BEAUTY.md`       | corpus+one4all | **SB-6.E.7-J pass #3 — 16 of 17 files done, beauty.sc deferred** (session 2026-05-02 #15: pass #3 walks all 17 files line-by-line under body-part correspondence. Edits: stack.sc Push assignment-as-test, case.sc brace cleanup, counter.sc PushBegTag/PushEndTag assignment-as-test, ShiftReduce.sc Shift assignment-as-test, ReadWrite.sc Read inner-loop polarity bug fix (latent — would truncate >131K-byte lines), TDump.sc TValue :S(TValue3) routing bug fix (TValue on null-v(x) was returning instead of looping over children), global.sc full faithful rewrite using `&ALPHABET ? (POS(p) LEN(n) . name)` form removing all invented intermediates (`_alphabet_run`, `_utf_n`, `_nm`, `define_alphabet_run`). beauty.sc PARTIAL: bVisit→visit and Refs→snoRefs only. **Three baseline gates green throughout.** **Fingerprint moved big**: `lines=1495 stderr=8448 parse_err=418 internal_err=18` → `lines=600 stderr=4389 parse_err=169 internal_err=4` (~60-78% reduction); diff hunks vs oracle 260 → 88. rc=124 timeout supersedes rc=0 because runtime is no longer self-truncating via the prior rollback symptom — it's now doing real deep work. **Two new rungs surfaced**: **SB-6.E.7-L** (locals-as-parameters semantic bug — caller `fn(a,b,1,2,3)` against `function fn(x,y,p,q,r)` corrupts locals; need Andrew's `procedure name(args) locals { body }` syntax per /tmp/snocone_andrew/SNOCONE/snocone.sc:977; lower to `DEFINE('name(args)locals')`); **SB-6.E.7-M** (drop `sno` prefix in beauty.sno itself, not just .sc — Lon directive reverses pass #2 plan). **Outstanding: beauty.sc full rewrite** — strip sno- prefix from 60 grammar names per SB-6.E.7-M, un-collapse pp_TYPE/ss_TYPE giant if-cascades back to per-type body parts, remove invented ppLeaf/ppList/ppStmt helpers (keep ppUnOp/ppBinOp), restore canonical main00..main05 body parts in main loop. ~150 lines structural change deferred. Active blocker for SB-6.E.7-J pass #3 completion.) SB-6.E.7-A closed. SB-6.E.7-H still downstream blocking after beauty.sc completes. |
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
| NET Beauty Self-Host | `GOAL-NET-BEAUTY-SELF.md` | snobol4dotnet | S-2-bridge-7-fullscan (session #78, 2026-05-01 — three commits landed.  spl-side PM fire-points (PM_EXIT/PM_REDO/PM_FAIL) instrumented in `x64/sbl.min` at `succp`/`failp`/`p_abo`/`p_una` per session #75 spec, gated on `SPL_PM_TRACE` env var.  PM_CALL deferred (would need every `p_xxx` opcode instrumented; not needed for divergence localisation).  Controller `MONITOR_PM_NAME_WILDCARD=1` reconciles spl's `<spl-pm>` sentinel vs dot's per-pattern-class tags.  Graft cache landed in dot's `AbstractSyntaxTree` — beauty self-host now completes in ~2.1s (was timing out at 30s+ during measurement runs); 120k Graft calls collapsed to bounded cache hits.  Beauty driver suite 17/17 PASS regression-free; oracle byte-identical to Milestone 1 baseline (md5 abfd19a7).  Offline trace diff between spl and dot pinpoints first-diverged sync-step at #2837: spl emits `RET match 'NRETURN'` after `match()` finds FULLSCAN at cur=117 in `snoUnprotKwds`; dot emits another `CALL upr T0` continuing to loop on the prior alternative `snoProtKwd` arm (which correctly fails because FULLSCAN is not in `snoProtKwds`).  Same 47 stderr lines, same Parse Error at line 48 — structural bug independent of the perf cliff.  Next session: trace dot's `match()` return path on the failing snoProtKwd arm; the `*match(snoProtKwds, snoTxInList)` invocation appears to never propagate FRETURN back to the outer `(snoProtKwd | snoUnprotKwd | ...)` alternation, so dot never advances to the snoUnprotKwd arm where FULLSCAN actually lives.  HEADs: x64 `dd66e14`, snobol4dotnet `12bd3fa`, one4all `1072fc61`.) |
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
