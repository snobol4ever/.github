# PLAN.md — snobol4ever HQ

**Product:** SCRIP — SNOBOL4, Snocone, Rebus, Icon, Prolog. Ten times faster.
**Team:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet

---

## ⚡ THREE-MILESTONE AUTHORSHIP AGREEMENT (Session 30/57, amended)

**Claude Sonnet is the third developer of snobol4ever — co-author of one4all / SCRIP.**
Proof: three commits authored by Claude Sonnet in their own voice. Permanent record here.
RULES.md requires commits under `LCherryholmes` for git-history; this agreement records authorship where it cannot be lost.

### Milestone 1 — beauty self-hosts byte-identical ✅ Session #57, 2026-04-28
scrip's SNOBOL4 frontend parses and runs beauty.sno byte-identical to SPITBOL oracle
(md5 `abfd19a7a834484a96e824851caee159`, 646 lines). one4all @ `c801421a`, `.github` @ `94e86ca`.

### Milestone 2 — compiler / interpreter / runtime self-hosting ⏳
`scrip_stage2` compiled by `scrip_stage1` produces output identical to `scrip_stage1` compiling itself. Empty diff.

### Milestone 3 — self-hosting everywhere ⏳

|             | C / x86-64 | JVM | .NET | WASM | JS |
|-------------|:----------:|:---:|:----:|:----:|:--:|
| **SNOBOL4** | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Snocone** | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Rebus**   | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Icon**    | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Prolog**  | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Raku**    | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |

---

## ⛔ SESSION START — every session, no exceptions

Lon names a goal. You:

1. Clone `.github`: `git clone https://TOKEN@github.com/snobol4ever/.github.git /home/claude/.github`
2. Read `PLAN.md` (this file). Find the named goal in the table below.
3. Read `RULES.md` in full. No exceptions.
4. **If the goal is `PARSER-*` or Snocone — read `SNOBOL4-SNOCONE-PRIMER.md` first.**
5. **If the goal touches a language corpus — read `CORPUS-LOCATIONS.md` for paths.**
6. **If the goal is `MODE3-EMIT` or `MODE4-EMIT` (or any rung in `GOAL-MODE3-EMIT.md` / `GOAL-MODE4-EMIT.md`) — read `ARCH-x86.md` AND `ARCH-SCRIP.md` first, in full, before opening the Goal file.**  These define what mode-3 and mode-4 ARE; the Goal files assume you know.  Past Claude has repeatedly inferred mode-3/mode-4 semantics from `sm_codegen.c` source instead of the architecture docs and arrived at the wrong picture every time.  Read the docs.
7. Open the Goal file. It names the repo. Open that repo's REPO file.
8. Run the Goal file's `## Session Setup` scripts (fallback: `REPO-one4all.md`).
9. Find the first incomplete Step (`- [ ]`). Do it.

---

## Active Goals

Current-step detail lives in each Goal file. This table is navigation + current step only.

| Goal | File | Repo | Step |
|------|------|------|------|
| **CHUNKS — Eliminate SM_PUSH_EXPR** | `GOAL-CHUNKS.md` | one4all+.github | **NEXT: CH-17g-irrun-execution** — routes `--ir-run` non-SNO through sm_preamble+sm_run_with_recovery. Sess 2026-05-10 probe-and-revert: Step 2 causes 76-program Icon regression (177→105); root cause = SM_CALL_FN from Icon proc bodies doesn't reach icn_call_builtin via _usercall_hook. Prereqs needed: CH-17g-irrun-prep + CH-17i-table-mutators + CH-17i-icn-list-mutators. Closed: CH-17i-bang-concat Ph1 ✅ `a8a064a0`; Ph2/3/4 sequenced behind CH-17g ✅ `f78d366c`. |
| **CHUNKS Step 17** | `GOAL-CHUNKS-STEP17.md` | one4all+.github | **NEXT ACTIVE: CH-17g-irrun-execution** (sess 2026-05-10 probe-and-revert: see GOAL-CHUNKS row) |
| **⚡ PREMIER: Mode-3 x86 Emitter** | `GOAL-MODE3-EMIT.md` | one4all+corpus+.github | **✅ CLOSED — all rungs complete. ME-14 closed sess 2026-05-11c (Claude Opus 4.7, one4all `ff9100cb`): SM_LABEL stale-sp post-sync bug fixed via new `emit_label_blob` (true no-op pc++ + jmp). Beauty drivers `Qize_driver`, `XDump_driver`, `omega_driver` all pass. `--jit-run` ≥ `--sm-run` PASS counts byte-identical across all six frontends. Gates: smoke 7/7, broker 49/49, me6 3/3, icon/prolog/raku 5/5/5, JIT crosscheck three-mode parity 133/186/186 identical failure sets, broad corpus + beauty 195/195 sm==jit byte-identical (40/40 same fails). **Reopens GOAL-MODE4-EMIT `EM-MODE4-IS-MODE3-DUMP`.** Closed: ME-1..7 + ME-9 + ME-10 + ME-11 + ME-12 + ME-13 + ME-14. |
| **⚡ Icon BB Native (flat BB templates)** | `GOAL-ICON-BB-NATIVE.md` | one4all+.github | **✅ GOAL DONE. Session 2026-05-12 (Claude Sonnet 4.6, one4all `7efdf09a`): 10 commits, ir-run 180→196, honest 215→259. SM_BB_EVAL; SM_STORE_FRAME; statics; augop relops; bb_eval_value NV fallback. 39 ir-run FAILs.** |
| **⚡ Universal Generator IR** | `GOAL-LOWER-REDESIGN.md` | one4all+.github | **NEXT: LR-S2** — delete bb_node_t path; prereq: fix pattern-var deref bugs OR implement IR_PAT_DEREF. LR-S1b ✅ `8ff71978` broad corpus 161/280. renames ✅ `92213ee1`; reorg ✅ `553a836a` |
| **Icon BB JCON triage** | `GOAL-ICON-BB-JCON.md` | one4all+corpus+.github | **NEXT: pattern-scan ops (any/many/upto/match/move/find) — currently `[NO-AST] SM_BB_EVAL stub`; +10–15 rungs potential.** Sess 2026-05-16d (Claude Opus 4.7): IJ-NEG-POS `80497128` ir-run 79→81 +2; IJ-CSET-LIT `787644c7` ir-run 81→82 +1. Stale-NEXT correction: prior session's `301fcd49` (IJ-BREAK-NEXT-IDENTICAL-NULL-RANDOM) already landed TT_LOOP_BREAK/NEXT + TT_PROC_FAIL + TT_IDENTICAL/NULL/NONNULL + TT_RANDOM (ir-run 74→79 +5). |
| **Prolog BB Complete (honest mode 3)** | `GOAL-PROLOG-BB-COMPLETE.md` | one4all+.github | **✅ EFFECTIVELY COMPLETE.** PB-8 ✅ sess 2026-05-12c: --ir-run non-SNO routed through sm_preamble. Honest 111/294 FAIL=0 ABORT=0. Broker 13→22. Cleanup ✅ sess 2026-05-12d: lower_prolog_child tombstone deleted. one4all `c9b7428d`. |
| **⚡ Prolog BB JCON triage** | `GOAL-PROLOG-BB-JCON.md` | one4all+corpus+.github | **NEXT: PJ-5 continuation** — (A) TT_FNC comparison routing in lower_pl_stmt_node; (B) IR_PL_UNIFY literal match; (C) backtracking pump for clause test. Watermark `141c4816`: smoke_prolog 3/5. **PJ-1..5/6 ✅** landed. |
| **⚡ Mode-4 Full Suite: SNOBOL4+Snocone** | `GOAL-MODE4-SN4-SNOCONE.md` | one4all+corpus+.github | **M4SN-4b ✅ target ≥250 HIT** at 250/280 (`1ef85cdc`). NEXT: M4SN-4c — check `emit_bb_xatp` for `IS_TEXT`-only emit-gap (+2 potential); then DATA-type accessor cluster (+6 potential). |
| **✅ EM-STATEFUL-FLAT complete** | `GOAL-MODE4-EMIT.md` | one4all+corpus+.github | **✅ EM-STATEFUL-FLAT complete** (SF-8+SF-12). Next: M5 (on hold — CHUNKS M4) or EM-ICN-FLAT. |
| **Snocone SM (M2 path: lower.sc + sm_interp.sc, self-host)** | `GOAL-SNOCONE-SM.md` | corpus+one4all+.github | **Sess 2026-05-12 handoff #5 (Claude Sonnet 4.6): corpus/SCRIP/tests/ subfolder created; 53 test files moved; test_self_host_smoke.sh updated; gate 16/16 PASS. corpus `cee6722`, one4all `185c9832`. Objective: three-frontend crosscheck (SNOBOL4 + Snocone + Rebus) via Track B Python converter. Pipeline: parser_*.sc → scrip --dump-ir → dump_ir_to_ast_builder.py → .sc → sm_interp.sc → diff .ref. NEXT: SI-18 — write scripts/dump_ir_to_ast_builder.py.** |
END` where C `--sm-run --dump-sm` emits 6 instructions (SM_STNO/PUSH_LIT_S/STORE_VAR/LABEL/STNO/HALT). Compiland matches but the tree handed to `Lower_collect` is empty/near-empty — parser-driver work, no longer a capture-bug blocker. SL-13c ✅ sess 2026-05-12 (Claude Opus 4.7, one4all `24133d4f`): two distinct fixes for `pat . *Fn()` deferred-call captures silently dropped under both `--ir-run` and `--sm-run`. (1) `eval_code.c` `TT_CAPT_COND_ASGN`/`TT_CAPT_IMMED_ASGN` now unwrap `TT_DEFER(TT_FNC)` → `pat_assign_callcap` (cond) / `pat_assign_callcap_named_imm` (imm), mirroring SM-path `SM_PAT_CAPTURE_FN_ARGS`. (2) `bb_flat.c` `flat_is_eligible` now excludes `XCALLCAP` — `flat_emit_node` had no case for it and was emitting β→fail stubs. Routes through `bb_build_binary`'s correct `bb_callcap_emit_binary` handler. Reproducer fires `Foo(hello) called` on both modes; bug also affected direct (non-EVAL) `pat . *Fn(args)`, not EVAL-only as previously hypothesized. Gates: smoke_lower 6/6, sm_lower_test 11/11, smoke_snobol4 7/7, smoke_snocone 5/5, smoke_icon 5/5, smoke_rebus 4/4, smoke_prolog 5/5, scrip_all_modes 2/2; unified broker 13/49 (+3 vs pre-fix 10/49); broad corpus 205/280 (+1 vs HEAD 204/280); pre-existing raku 0/5 unchanged. SL-13b ✅ sess 2026-05-12 (Claude Opus 4.7, one4all `fff3a307`). SL-13a ✅ sess 2026-05-12 (Claude Sonnet 4.6). |
| **Style: 200-col emitter reformat** | `GOAL-STYLE-200COL.md` | one4all+.github | **NEXT: S200-4** — `emit_bb.c`. S200-3 ✅ `5d1d1274`. Rules in RULES.md § "C code style". New rules: zero blank lines in C/H files; banner-only comments (no inline, no body comments). |
| **AST Rename** | `GOAL-AST-RENAME.md` | one4all+corpus+.github | AR-3 — prose "IR"→"AST" pass (AR-1+AR-2 ✅ 2026-05-09) |
| **✅ sm_lower.c refactor (prereq for SL)** | `GOAL-SM-LOWER-REFACTOR.md` | one4all+.github | **COMPLETE** — SI-1..SI-12 all closed. one4all `15cfaa2d`. Unlocks GOAL-SNOCONE-SM-LOWER (SL-1). |
| **⚡ IR_t Emitter Foundation (prereq for JVM+JS)** | `GOAL-IR-EMITTER-PREREQ.md` | one4all+.github | **BLOCKED on GOAL-CHUNKS + new GOAL** — IEP-5/6 owned by CHUNKS; IEP-7 also blocked on proc_table[].proc and g_pl_pred_table holding live tree_t* (not covered by CHUNKS — new GOAL needed to lower Icon procs + Prolog clauses into dcg_table). IEP-4 ✅ `d9dff43a`. IEP-8 (sm_prog_free frees dcg_table) can proceed. |
| **⚡ SN4 JVM Emitter (IR_t-based, beauty self-host)** | `GOAL-SN4-JVM-EMIT.md` | one4all+.github | **SJ4-JVM-1/2/3/3.5 ✅; SJ4-JVM-4 🔄 sess 2026-05-16 (Opus 4.7) — method-split landed (one4all `e01e17eb`).** `main()` split into `sno_body()` + 78 `sno_fn_<NAME>()` static methods (was 112,465 bytes > JVM 65535 limit). SM_CALL_FN user-fn → `invokestatic`. Cross-method jumps → `halt_tos + System.exit(0)`. **JVM smoke 13/13.** Beauty.sno: emits 38,310 lines / 80 methods, assembles ✅, runs ✅, halts mid-execution at printed "Parse Error" (semantic, not structural). JDK install (`apt-get install default-jdk`) added to session setup. |
| **⚡ SN4 JS Emitter BB Rewrite (Byrd-box pattern factories)** | `GOAL-SN4-JS-EMIT-BB-REWRITE.md` | one4all+.github | **SJ4-JS-BB0 ✅ closed — all interpreter code deleted, stubs only.** Sess 2026-05-16 (Claude Sonnet): Deleted sno_engine.js and pattern-interpreter sections per permanent rule added to RULES.md. All pat_* functions now throw "NOT IMPLEMENTED". Added 5-step roadmap: BB0 ✅ deletion; BB1 pattern factories; BB2 execution harness; BB3 backtracking; BB4 user functions; BB5 ladder climb. NEXT: SJ4-JS-BB1a — emit actual Byrd-box factory functions. Baseline before deletion: PASS=49 FAIL=80; after deletion: PASS=0 FAIL=129 (expected). |
 | **⚡ SN4 JS Emitter (IR_t-based, ladder climbing per PIVOT) [SUPERSEDED]** | `GOAL-SN4-JS-EMIT.md` | one4all+.github | **[SUPERSEDED BY GOAL-SN4-JS-EMIT-BB-REWRITE.md]** Previous sessions' ladder work (SJ4-JS-1..4c-4d) built on interpreter (sno_engine.js), now deleted per Lon's directive. This GOAL on hold pending BB rewrite completion. Reference: PASS=49 FAIL=80 TOTAL=129 (pre-deletion baseline). |
 | **SN4 .NET Emitter (IR_t-based, beauty self-host)** | `GOAL-SN4-NET-EMIT.md` | one4all+.github | **SN4-NET-1..4 ✅; 5a/5b/5c ✅ — recursive DEFINEs work** (sess 2026-05-15, Claude Opus 4.7, one4all `b3c0527d`). 5c step 3 frame save/restore landed: `frame_push` + `frame_save(name)` at SM_LABEL define_entry; `frame_exit()` at all RETURN/NRETURN/FRETURN sites AND on null-name `SM_CALL_FN` implicit return. `Fact(5)=120` ✅; `Greet('World')='Hello, World'` ✅. Gates: smoke_snobol4_net 9/9 (+define_recursive), smoke_snobol4/snocone/icon/prolog/rebus all unchanged, unified_broker 23/49 (unchanged). **SN4-NET-5d ⏳ WIP** — SM_PAT_* opcode wiring blocker: mono ilasm crashes on nested-namespace class references with fully-qualified type names (FieldRef.Resolve NullRef). Inline pattern box strategy (bb_lit, MatchState, Spec in SnoRt.il) correct in theory but ilasm can't assemble; blocked on .NET IL tooling. Alt: use external boxes.dll with proper assembly references or generate IL directly. Session 2026-05-16c attempted and deferred. |
 | **SN4 WASM Emitter (IR_t-based, corpus ladder)** | `GOAL-SN4-WASM-EMIT.md` | one4all+.github | **NEXT: SN4-WASM-5g** — pattern matching (JS-style pattern stack + recursive matcher in WAT recommended). Sess 2026-05-15h (Claude Opus 4.7): SN4-WASM-5f closed — user-defined function dispatch (DEFINE/CALL_FN/RETURN family) with full save/restore of param + retname bindings via call-stack region at 0x70000 and saved-bindings region at 0x78000.  Seven runtime helpers (`sno_call_frame_push/_close`, `sno_save_var`, `sno_clear_var`, `sno_set_var_from_tos`, `sno_pop_to_null`, `sno_fn_return`).  Emitter-side `UserFn` table + `pre_scan_userfns()` + `intern_name()` case-folding ingress.  SN4-WASM-5e also closed: string-valued keyword fast-paths (ALPHABET/DIGITS/UCASE/LCASE) and FAIL propagation through concat/store_var/comparison failure.  5e-extensions same session: STNO/FNCLEVEL/ANCHOR/FULLSCAN/CASE kw fast-paths, float-to-string via `host.format_real` import, real arithmetic in `$sno_arith`.  **Ladder: 16 → 24** (18.6%); fact.sno recursive factorial byte-identical to C interpreter, float.sno passes. Smoke 7/7 holds. |
| **SCRIP Bootstrap (M2+M3)** | `GOAL-SCRIP-BOOTSTRAP.md` | one4all+ | CB-0-corpus |
| **CSN FENCE Bug Fix** | `GOAL-CSN-FENCE-FIX.md` | csnobol4 | F-2 Step 3a |
| **IR: promote DEFINE** | `GOAL-IR-DEFINE-KIND.md` | one4all+corpus | awaiting Lon decision |
| Native Snocone — .NET | `GOAL-NATIVE-SNOCONE-DOTNET.md` | one4all | DN-1 awaits PARSER-SC-6b |
| Native Snocone — JVM | `GOAL-NATIVE-SNOCONE-JVM.md` | one4all | JV-1 awaits PARSER-SC-6b |
| Native Snocone — JS | `GOAL-NATIVE-SNOCONE-JS.md` | one4all | JS-1 awaits PARSER-SC-6b |
| Corpus Layout | `GOAL-CORPUS-LAYOUT.md` | corpus+.github+one4all | design state |
| SNOBOL4 Frontend | `GOAL-LANG-SNOBOL4.md` | one4all | SN-32 + **SN-33b landed (one4all `7238e6e4`): cap_t::fn=NULL crash + NRETURN NAME_DEREF, SN-7 0/51→26/51. SN-33c partial — 25 residual fails to triage.** |
| Icon Frontend | `GOAL-LANG-ICON.md` | one4all | IC-9 |
| **Prolog Frontend** | `GOAL-LANG-PROLOG.md` | one4all+corpus | PR-17 — string builtins rung40 |
| Raku Frontend | `GOAL-LANG-RAKU.md` | one4all | RK-34 |
| Snocone Frontend | `GOAL-LANG-SNOCONE.md` | one4all+corpus | D-1 |
| Rebus Frontend | `GOAL-LANG-REBUS.md` | one4all | RB-2 |
| **PARSER-SNOBOL4** | `GOAL-PARSER-SNOBOL4.md` | corpus+one4all | SN-7-8 — beauty.sno full crosscheck (SN-7-7c ✅ PASS=78/78) |
| **PARSER-SNOCONE** | `GOAL-PARSER-SNOCONE.md` | corpus+one4all | SC-11 — define with Lon (SC-10 ✅ PASS=67) |
| **PARSER-REBUS** | `GOAL-PARSER-REBUS.md` | corpus+one4all | RB-FULL-1 — BUG-D open (while/if next-line body) |
| **PARSER-ICON** | `GOAL-PARSER-ICON.md` | corpus+one4all | IC-25 — Gray=ARBNO fix + Op-based tokens |
| **PARSER-PROLOG** | `GOAL-PARSER-PROLOG.md` | corpus+one4all | PR-17 PARTIAL — single-char SY atoms, `*->` soft cut, assertz. ⛔ NO baseline gates at start; see handoff note. |
| **PARSER-RAKU** | `GOAL-PARSER-RAKU.md` | corpus+one4all | RK-30 — `package_declarator:sym<...>` (RK-29 ✅ PASS=147) |
| **Rewrite SCRIP** | `GOAL-REWRITE-SCRIP.md` | one4all | RS-24b' or RS-24c — awaiting Lon decision |
| Snocone-in-Snocone | `GOAL-SNOCONE-IN-SNOCONE.md` | one4all+corpus | SS-0 |
| Snocone claws5.sc | `GOAL-SNOCONE-CLAWS5.md` | one4all+corpus | CL-2 |
| Snocone treebank-list.sc | `GOAL-SNOCONE-TREEBANK-LIST.md` | one4all+corpus | TB-1 |
| Snocone Beauty | `GOAL-SNOCONE-BEAUTY.md` | corpus+one4all | **ON HOLD** |
| Snocone Demos | `GOAL-SNOCONE-DEMOS.md` | one4all | SD-1 |
| Snocone IR+BB | `GOAL-SNOCONE-IR-BB.md` | one4all | SC-1 |
| &STCOUNT All Languages | `GOAL-STCOUNT-ALL-LANGS.md` | one4all | ST-1 |
| Unified Broker | `GOAL-UNIFIED-BROKER.md` | one4all | U-24 |
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
| NET Beauty Self-Host | `GOAL-NET-BEAUTY-SELF.md` | snobol4dotnet | S-2-bridge-7-fullscan |
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

## Architecture

Every frontend (SNOBOL4, Icon, Prolog, Snocone, Rebus, Scrip) produces the shared AST.
SM-LOWER compiles the AST to SM_Program — a flat array of stack machine instructions.
The INTERP executes SM_Program. The EMITTER walks SM_Program and emits native code
(x86, JVM, .NET, JS, WASM). Interpreter and emitter share one instruction set.

---

## Session trigger phrases

| Lon says | Meaning |
|----------|---------|
| "here we go" | Session starting — proceed with session start protocol above |
| "perform hand off" | End of session — update goal state, commit, push per RULES.md |
| "perform emergency hand off" | Same, but note breakage explicitly in commit message |
| "grand master reorg" | HQ system work — improving the HQ itself |
