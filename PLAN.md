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
| Icon Frontend Ladder | `GOAL-LANG-ICON.md` | one4all | IC-9 (session #23, 2026-05-01, one4all HEAD `1233e800`: **+11 PASS** rung01-36 (188 → 199), **+3 PASS** rung36 (6 → 9), gates clean smoke 5/0, broker 49/0, crosscheck 4/0, smoke_snobol4 7/0. Eight fixes: (1) `icn_bb_cat_gen` re-pumps leaf gen on per-tick failure (don't exhaust box) — unblocks `s[N to M]` shape across many tests; (2) E_SECTION_PLUS / E_SECTION_MINUS read handlers (these IR kinds existed only in lvalue context since #21); (3) E_CAT in Icon mode forces real DT_S empty result instead of DT_SNUL passthrough — `image("" || "")` → `""` not `&null`; (4) E_POW Icon mode always returns real (gated SPITBOL int-fast-path on `g_lang != 1`) — closes 5 pow tests rung19/26; (5) left/right/center rewritten — default n=1, `&null`/elided arg, correct pad-cycling rules (left-pads use `fill[i % fl]`, right-pads end at `fill[fl-1]` via `fill[((k + fl - padlen) % fl + fl) % fl]`), center srcoff rounds UP `(sl - n + 1) / 2` — closes 3 tests; (6) `integer()`/`numeric()` parse `BASErDIGITS` radix prefix (base 2..36, case-insensitive `r/R`, digits 0-9 + a-z); (7) new `list(n, x)` constructor builtin (was missing entirely); (8) `static` decls persist across calls via per-(proc EXPR_t*, var-name) `icn_static_tab[256]` with `icn_static_get/set` helpers; parser tags `E_GLOBAL.ival=1` for `static` vs `local`; entry-restore + exit-snapshot bracket the body loop in `icn_call_proc` — closes `statics`. Files touched: `src/driver/interp.c` (~280 lines), `src/runtime/interp/icn_runtime.c` (~80 lines static infra + ~30 entry/exit hooks), `src/frontend/icon/icon_parse.c` (3-line `local` vs `static` distinction). No header struct changes, no clean rebuild needed. **Next pivot:** records-as-iterables — `!record` field iteration and `every !r := V` field assignment closes `rung36_jcon_record` and contributes to 3+ other tests. Same shape as table-lvalue work in #21; extend `E_ITERATE` and `E_ASSIGN` lvalue handlers with a DT_DATA/record branch that walks `data->fields`.) |
| Prolog Frontend Ladder | `GOAL-LANG-PROLOG.md` | one4all | PL-12 (session 2026-05-01 #1: 5 commits landed bisectable+gate-neutral. corpus `dfc26da` Step A plunit stdlib enrichment (~25 stubs), `80ce2f2` Step A-patch numbervars/4 direction fix. one4all `1de19342` Step B.1 copy_term_rec slot fix (1<<20 + nmap so bind() trails fresh vars), `018bfdef` Step B.2 findall snapshots use pl_copy_term (preserves var sharing), `3bc1573d` Step C arith INT_MIN/-1 SIGFPE guard. B.3 bridge held back as `docs/PL-12-session-2026-05-01-bridge.diff`. **Session 2026-05-01 #2: Step D decided — KEEP block-level scoring** (per-test scoring would inflate without improving correctness; the block metric is honest about whether SCRIP genuinely runs Prolog). **+1 corpus commit `ada87b6` Step D fix — plunit suite-skip support:** `begin_tests(Suite,Opts)` previously discarded Opts, so `bigint`'s `condition(bounded=false)` was ignored — bridge-on `bigint` ran instead of skipping and segfaulted partway through, killing 14 test_arith blocks. Fix: `pj_suite/2` stores Opts; new `pj_run_suite` clause short-circuits skip; `pj_skip_cond` rewritten to use clause-head pattern matching (`pj_cond_fails/1`) sidestepping the same E_VAR Var-bound-goal bug the bridge fixes for `catch/3`. Bridge-neutral baseline: 43/57 preserved. With bridge: 14/57 → 15/57 (+1, bigint now skips cleanly). **Other findings (not actioned):** (a) `:- if/:- endif` are runtime no-ops in `pl_runtime.c:586` and the parser passes through bodies unconditionally — bigint-needing tests gated by `:- if(\+current_prolog_flag(bounded,true)).` load anyway and contribute to segfault path; (b) `minint_promotion` segfaults on `+`/`-`/`*` overflow at INT_MIN boundary (not covered by Step C's IDIV guard); (c) test_call has 127 parse errors — likely a single grammar gap unlocking 9 blocks. **REVISED next-session steps:** E.1 `:- if/:- endif` parser-level conditional compilation, E.2 arith overflow guards beyond IDIV, then E (land bridge once segfault-prone paths are gated). Findings doc `one4all/docs/PL-12-session-2026-05-01-2-findings.md`. Smoke 5/5, broker 49/49, SWI 43/57 unchanged at session-end.) |
| Raku Frontend Ladder | `GOAL-LANG-RAKU.md` | one4all | RK-34 |
| Snocone Frontend Ladder | `GOAL-LANG-SNOCONE.md` | one4all+corpus | D-1 |
| Rebus Frontend Ladder | `GOAL-LANG-REBUS.md` | one4all | RB-2 |
| Snocone claws5.sc | `GOAL-SNOCONE-CLAWS5.md` | one4all+corpus | CL-2 |
| Snocone treebank-list.sc | `GOAL-SNOCONE-TREEBANK-LIST.md` | one4all+corpus | TB-1 |
| Snocone Beauty         | `GOAL-SNOCONE-BEAUTY.md`       | corpus+one4all | SB-6.D (session #81, 2026-04-30: SB-5d.2 LANDED — `treebank-array.sc` byte-identical to .ref in all 3 modes (md5 `7096beb...`); rewrote two bare-juxtaposition concat sites in `node_repr`/`pp_node` as canonical Snocone integer-loop form mirroring `treebank-array.sno::nr_lp` and `pp_wch/pp_wlast/pp_wdone` exactly; added `GT(n,0)` guard in pp_node fixing latent zero-children bug. Lon's session-#80 minor edits to `claws5.sc`, `treebank-list.sc`, `treebank-array.sc` verified — treebank-list.sc preserved at PASS in all 3 modes; claws5.sc remains byte-identical to claws5.sno SPITBOL on both inputs (SB-5c.2 corpus-curation issue unchanged). Three baseline gates green PASS=5/PASS=42 SKIP=3/PASS=49; crosscheck snobol4=6, snocone=8 unchanged. SB-6.D investigation snapshot: `EVAL(EXPRESSION)` is no-op at beauty.sc's Reduce call site (1st EVAL returns same EXPRESSION descriptor; 2nd EVAL produces correct STRING `''` failure). Standalone `/tmp/repro2.sc` (omega-string-EVAL pattern matching semantic.sc::reduce shape) does NOT reproduce — first EVAL works correctly there. Bug requires the wrapped context (`nPush() && X4 && reduce(...) && nPop()` like Expr4 line 69 of beauty.sc); EXPRESSION descriptor at Reduce call site appears double-wrapped. **Session #82 next steps:** (1) run `/tmp/repro3.sc` to confirm wrapper exposes double-wrap; (2) SPITBOL cross-check on SNOBOL4-equivalent reproducer; (3) if confirmed, fix in `src/runtime/x86/snobol4_invoke.c` or EVAL/EXPRESSION descriptor packing path. corpus dirty (3 .sc); .github dirty (this update + goal file s#81 narrative); one4all/csnobol4/x64 clean.) |
| **Snocone Language: Space-Concat** | `GOAL-SNOCONE-LANG-SPACE.md` | one4all+corpus | LS-5 done, LS-4.l beauty pending (session 2026-05-01 #2: LS-5.a/b/c LANDED — one4all `5bcc7412` ships ~700-line `util_migrate_snocone_to_lang_space.py` (24/24 unit tests, idempotent, two-stage paren-aware tokenizer; whole-source `||` rewrite then per-span `&&`/`go to` sweep). corpus `a4aaf83` migrates 69 files (68 auto + 1 hand-fix `hello_literals.sc` for SNOBOL4-surface conventions: `#`→`//` and added `;`). Beauty advances **6/36/3 → 30/12/3** — 24 tests recovered. Smoke 5/5 ✅, broker 49/0 ✅. Remaining 12 FAILs (`fence`/`match`/`semantic`/`trace` × 3 modes) are pre-existing parser/runtime issues unrelated to migration — diffs show no `&&`/`||` involvement; surfaced now that the language-migration breakage cleared. Corpus-data drift noted at `sc8_strings.sc` (`.ref` expects concat output but `\|\|` was alt-eval — pre-existing, not migration-caused). LS-4.l acceptance 42/0/3 pending those four investigations. Next: investigate fence/match/semantic/trace.) |
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
| NET Beauty Self-Host | `GOAL-NET-BEAUTY-SELF.md` | snobol4dotnet | S-2-bridge-7-byrd-pattern (session #75, 2026-05-01 — partial. New step opened above S-2-bridge-coverage-pattern-traversal: Byrd-box (CALL/EXIT/REDO/FAIL) per-AST-node wire events. Four wire kinds added: `MWK_PM_CALL=7`, `MWK_PM_EXIT=8`, `MWK_PM_REDO=9`, `MWK_PM_FAIL=10` in `monitor_wire.h`. dot-side emit + controller recognition LANDED. Gated `MONITOR_PM_TRACE=1` (default off — baseline self-host byte-identical at 47 stderr lines, beauty 17/17 PASS). Files: `MonitorIpc.cs` adds `EmitPmCall/Exit/Redo/Fail` going through full IPC ack handshake; `Scanner.Match()` emits the four ports; `UnevaluatedPattern.MethodName` derives `*snoString` etc. from delegate Method.Name; `Scanner.NodeTag` returns `'literal'` for LiteralPattern, type-name otherwise; controller `monitor_sync_bin.py` formats PM events as first-class comparison-eligible kinds. **IPC validated:** dotA + dotB both with PM_TRACE=1 sync-stepped 17 events through `monitor_sync_bin.py`, `all reached END` clean — PM events traverse IPC ack one-at-a-time. dotA-on vs dotB-off correctly diverged at first PM_CALL row. **Beauty self-host PM trace (dot solo, 18.7M wire events):** at line 48 snoDQ parse, dot fires `PM_CALL PosPattern c=0 → PM_EXIT c=0 → PM_CALL AnyPattern c=0 → PM_FAIL c=0`, then cursor-retries `PosPattern` from c=1, 2, … instead of falling through to next snoExpr17 arm. The Alternate link out of the snoFunction/snoId-head arm is mis-wired — likely bug in `AbstractSyntaxTree.ComputeAlternate`. **Session #76 next steps:** (1) spl fire-points in `x64/osint/monitor_ipc_runtime.c` + `sbl.min` mtchcd/bktrk/snofal/snosuc, regenerate `bootstrap/sbl.asm`, gate `SPL_PM_TRACE=1`; (2) wire `MONITOR_PM=1` through `test_monitor_3way_sync_step_auto.sh`; (3) two-way harness on line-48 minimal repro — clean DIVERGE row inside first ~50 PM events; (4) fix Alternate link bug. Baseline: 17/17 beauty drivers, self-host 47 stderr lines, build clean. snobol4dotnet + one4all + .github committed at session end.) |
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
