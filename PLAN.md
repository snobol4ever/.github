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
| **Icon BB Complete (honest mode 3)** | `GOAL-ICON-BB-COMPLETE.md` | one4all+.github | ⛔ SUPERSEDED by GOAL-ICON-BB-NATIVE. SM-coroutine approach was wrong. |
| **⚡ Icon BB Native (flat BB templates)** | `GOAL-ICON-BB-NATIVE.md` | one4all+.github | **✅ GOAL DONE + post-IB-10 coro stack overflow fixed sess 2026-05-12 (Claude Sonnet 4.6, one4all `fa958d82`). Root: icon_gen.c makecontext hardcoded ss_size=256KB; _usercall_hook ~400KB frame overflowed into bb_pool/GC pages. Fix: CORO_STACK_SZ→header, 256KB→1MB, guard page on coro stacks. Gates: smoke_icon 5/5, broker 22/49, ir_all 180, honest 215/0 PASS/FAIL x5 stable runs. NEXT: new IB ladder for next BB cluster (35 of 43 JCON templates remain on SM_BB_PUMP_AST).** |
| **Prolog BB Complete (honest mode 3)** | `GOAL-PROLOG-BB-COMPLETE.md` | one4all+.github | **✅ EFFECTIVELY COMPLETE.** PB-8 ✅ sess 2026-05-12c: --ir-run non-SNO routed through sm_preamble. Honest 111/294 FAIL=0 ABORT=0. Broker 13→22. Cleanup ✅ sess 2026-05-12d: lower_prolog_child tombstone deleted. one4all `c9b7428d`. |
| **Mode-4 x86 Emitter** | `GOAL-MODE4-EMIT.md` | one4all+corpus+.github | **NEXT: EM-DOPPELGANGER-PURGE EDP-2 — sm_emit_template.c legacy table purge.** ⛔ Lon directive sess 2026-05-12h: with sm_templates.c + bb_templates.c established as single source of truth (91 SM + 35 BB emitters covering all SM_t and XKIND_t entries), eradicate every parallel SM/BB emission path. New EM-DOPPELGANGER-PURGE rung with 12 sub-rungs (EDP-1..EDP-12) added to goal file. Beauty-suite / beauty self-host work BLOCKED until this rung closes. Sess 2026-05-12h (one4all `baa29424`): (1) BB-blob R10 corruption FIXED — push/pop r10 around runtime calls; new BB_INSN_PUSH_R10/POP_R10. case_driver passes mode-4. PASS 6→7. (2) lower.c DEFINE_ENTRY labtab fix re-applied. (3) Template consolidation: 78 per-opcode files → 2 files (sm_templates.c, bb_templates.c). Gates: smoke 7/7, template-byte-id 4/4, snocone 5/5, beauty-subsystems mode4 PASS=7 FAIL=10.** |
| **Snocone sm_lower (M2 path)** | `GOAL-SNOCONE-SM-LOWER.md` | corpus+one4all+.github | **NEXT: SL-13d — parser_snobol4.sc driver populating Lower with full parse tree.** **SL-13c-tilde-fix ✅ sess 2026-05-12c (Claude Opus 4.7):** forward-reference jump patching in `lower.sc` was broken because `~LT(res, 0)` and `~IDENT(...)` build PATTERN values in Snocone (always truthy in `if`), not boolean negations. Two sites in `emit_goto`/`labtab_resolve` fixed to `GE(...)`; benign third site (line 1054, redundant trailing SM_HALT) left as-is. Bug surfaced via SI-11 (first .sc-side hand-built AST test using `SL_GOS`). Gates: full smoke matrix clean, broker 22/49 identical pre/post-fix. `bash run_scrip_parser.sh snobol4 trivial.sno` now runs end-to-end without hang/Error/silent-drop after SL-13c closure, but emits `SM_Program count=1 / SM_HALT` for `X='hello'
END` where C `--sm-run --dump-sm` emits 6 instructions (SM_STNO/PUSH_LIT_S/STORE_VAR/LABEL/STNO/HALT). Compiland matches but the tree handed to `Lower_collect` is empty/near-empty — parser-driver work, no longer a capture-bug blocker. SL-13c ✅ sess 2026-05-12 (Claude Opus 4.7, one4all `24133d4f`): two distinct fixes for `pat . *Fn()` deferred-call captures silently dropped under both `--ir-run` and `--sm-run`. (1) `eval_code.c` `TT_CAPT_COND_ASGN`/`TT_CAPT_IMMED_ASGN` now unwrap `TT_DEFER(TT_FNC)` → `pat_assign_callcap` (cond) / `pat_assign_callcap_named_imm` (imm), mirroring SM-path `SM_PAT_CAPTURE_FN_ARGS`. (2) `bb_flat.c` `flat_is_eligible` now excludes `XCALLCAP` — `flat_emit_node` had no case for it and was emitting β→fail stubs. Routes through `bb_build_binary`'s correct `bb_callcap_emit_binary` handler. Reproducer fires `Foo(hello) called` on both modes; bug also affected direct (non-EVAL) `pat . *Fn(args)`, not EVAL-only as previously hypothesized. Gates: smoke_lower 6/6, sm_lower_test 11/11, smoke_snobol4 7/7, smoke_snocone 5/5, smoke_icon 5/5, smoke_rebus 4/4, smoke_prolog 5/5, scrip_all_modes 2/2; unified broker 13/49 (+3 vs pre-fix 10/49); broad corpus 205/280 (+1 vs HEAD 204/280); pre-existing raku 0/5 unchanged. SL-13b ✅ sess 2026-05-12 (Claude Opus 4.7, one4all `fff3a307`). SL-13a ✅ sess 2026-05-12 (Claude Sonnet 4.6). |
| **Snocone sm_interp (M2 path, self-host)** | `GOAL-SNOCONE-SM-INTERP.md` | corpus+one4all+.github | **🎉 PHASE 2 ✅; PHASE 3 OPENED + 2 RUNGS IN ✅ sess 2026-05-12 (Claude Sonnet 4.6, handoff #2). Phase 3 Test Suite Coverage opened with SI-17..SI-21 ladder (3 tracks: corpus mirrors, dump-ir converter, full self-host via SL-13d). SI-17a (sc2_assign mirror) and SI-17b (sc4_control mirror with if/else GT/LT/EQ) landed. **Bug found and fixed via SI-17b: SM_CALL_FN always set last_ok=1 regardless of host APPLY() failure; comparisons that fail via Snocone backtracking (LT/GT/EQ returning fail) need to set last_ok=0 so :F(label) fires. Fixed by wrapping APPLY in `if (a = APPLY(...))`. This was the kind of latent bug broader test coverage was meant to surface.** Also stripped all /* */ comments from sm_interp.sc (347→305 lines) and normalized all si_*/smoke/sm_interp tests from TT_STMT → STMT to match canonical parser_*.sc wire-shape (Lower_stmt slot lookups are tag-agnostic so it worked either way, but STMT is the form a real parser emits). Earlier this session: All 87 SM_* opcodes from `sm_prog.h` now have handlers in `sm_interp.sc`: ~65 real implementations, ~22 silent stubs for Icon/Prolog complexity (BB_*, generators, frame slots). Per Lon directive, Icon/Prolog stubs are **silent no-ops** — pop expected args, push placeholders, no TERMINAL spam. TERMINAL warnings retained only for scrip-emittable paths where silent failure would hide bugs: pattern callbacks (`PAT_CAPTURE_FN`/`_ARGS`, `PAT_USERCALL`/`_ARGS`), `SM_CALL_FN` pseudo-calls (`INDIR_GET`/`ASGN`/etc.), `SM_CALL_FN` nargs>5, unknown opcode. Session work: SI-12 (`SM_CALL_FN` via APPLY), SI-13 (frame stack + `SM_CALL_EXPRESSION` + `SM_RETURN` family), SI-14 (`SM_JUMP_INDIR`), SI-15 (real-program cross-checks; closed Phase 2), SI-16 (one-shot Phase 3 stubs). Also fixed long-standing si_07_pat_lit FAIL via `SM_EXEC_STMT` named-subject local-copy + write-back. Reformat to 120-char lines + `switch(opc)` dispatch + `+X` unary coercion. **Gates this session: self_host 6/7→14/14 PASS clean; smoke matrix (snobol4/snocone/icon/prolog/rebus/raku/scrip_all_modes) 33/33 PASS clean; crosscheck snobol4 4/2 + snocone 7/1 + lower_byte_id 27/3 — all FAILs pre-existing, zero regressions.** Gates: 6/7 (start) → 16/16 (end) clean; smoke matrix 33/33 clean; zero regressions on cross-checks. **NEXT: SI-17c (sc5_while mirror), SI-17d (sc6_for, probe TT_FOR), SI-17f (sc8_strings), SI-17h (sc10_wordcount); SI-17e/g blocked on lower_proc_skeletons stub. Then SI-18 (dump_ir_to_ast_builder.py converter), SI-19 (bulk-run via test_self_host_corpus.sh), SI-20 (bug triage), SI-21 (closing gate ≥30 tests). Phase 4 deferred for real BB scheduler / SUSPEND/RESUME / pattern-engine hooks.** |
| **AST Rename** | `GOAL-AST-RENAME.md` | one4all+corpus+.github | AR-3 — prose "IR"→"AST" pass (AR-1+AR-2 ✅ 2026-05-09) |
| **✅ sm_lower.c refactor (prereq for SL)** | `GOAL-SM-LOWER-REFACTOR.md` | one4all+.github | **COMPLETE** — SI-1..SI-12 all closed. one4all `15cfaa2d`. Unlocks GOAL-SNOCONE-SM-LOWER (SL-1). |
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
