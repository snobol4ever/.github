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
5. **If the goal is `MODE3-EMIT` or `MODE4-EMIT` (or any rung in `GOAL-MODE3-EMIT.md` / `GOAL-MODE4-EMIT.md`) — read `ARCH-x86.md` AND `ARCH-SCRIP.md` first, in full, before opening the Goal file.**  These define what mode-3 and mode-4 ARE; the Goal files assume you know.  Past Claude has repeatedly inferred mode-3/mode-4 semantics from `sm_codegen.c` source instead of the architecture docs and arrived at the wrong picture every time.  Read the docs.
6. Open the Goal file. It names the repo. Open that repo's REPO file.
7. Run the Goal file's `## Session Setup` scripts (fallback: `REPO-one4all.md`).
8. Find the first incomplete Step (`- [ ]`). Do it.

---

## Active Goals

Current-step detail lives in each Goal file. This table is navigation + current step only.

| Goal | File | Repo | Step |
|------|------|------|------|
| **CHUNKS — Eliminate SM_PUSH_EXPR** | `GOAL-CHUNKS.md` | one4all+.github | **NEXT ACTIVE: CH-17g-irrun-execution** — the architectural unblock for the whole Icon/Prolog mode-2/3/4 isolation ladder.  Routes `--ir-run` non-SNO through `sm_preamble` + `sm_run_with_recovery` (same path as `--sm-run`), so modes 2 and 3 share the SM dispatch runtime.  Spec at GOAL-CHUNKS-STEP17.md §CH-17g-irrun-execution — 6 steps, file-disjoint from per-kind work, byte-identity gate against pre-rung `--ir-run` baseline.  After it lands the per-kind sequenced rungs (CH-17i-bang-concat 2/3/4, CH-17i-section, CH-17i-limit-random, CH-17i-prolog-initialization) gain real anchors.  **Sess 2026-05-10 probe-and-revert (no code landed): Step 2 alone produces 76-program Icon regression (177→105) bucketed cleanly onto un-landed CH-17i sub-rungs + new gaps (table mutators, list mutators, records, table indexing opcode) — root cause is `SM_CALL_FN` from lowered Icon proc bodies routes through `_usercall_hook` which does not reach `icn_call_builtin`'s chain.  Targeted `_usercall_hook` patch tried this session: clean on baseline, only +1 PASS under Step 2, introduced flake — reverted.  Recommendation: file CH-17g-irrun-prep (`_usercall_hook` Icon-builtin dispatch, lands on its own merits) + CH-17i-table-mutators + CH-17i-icn-list-mutators ahead of Step 2 retry.  Diagnosis written into GOAL-CHUNKS-STEP17.md §CH-17g-irrun-execution.**  Recently closed: CH-17i-bang-concat Phase 1 ✅ 2026-05-10 (one4all `a8a064a0`); Phases 2/3/4 ✅ SEQUENCED 2026-05-10 behind CH-17g-irrun-execution (706-program audit, doc `CHUNKS-step17i-bang-concat-phase234-audit.md`, one4all `f78d366c`).  Sequence to Mode 4 Icon/Prolog: CH-17g-irrun-prep → per-kind migrations → CH-17g-irrun-execution → CH-17i-mode3-completeness → CH-17g-final → CH-17i-mode4-icon-prolog → CH-17i-final-isolation. |
| **CHUNKS Step 17** | `GOAL-CHUNKS-STEP17.md` | one4all+.github | **NEXT ACTIVE: CH-17g-irrun-execution** (sess 2026-05-10 probe-and-revert: see GOAL-CHUNKS row) |
| **⚡ PREMIER: Mode-3 x86 Emitter** | `GOAL-MODE3-EMIT.md` | one4all+corpus+.github | **NEXT ACTIVE: ME-1 — pat-stack unification.**  Carved sess 2026-05-10 (Claude latest) as premier-goal: most other work pauses until this Goal closes.  Mode 3 today is not what `ARCH-x86.md` says it is — it is a per-opcode tail-call thunk + C dispatch loop in `sm_jit_run`, not a per-instruction native emitter.  This Goal fixes that.  Architecture locked: one value stack (pat-stack collapses in ME-1), `r12 = SM_State*`, `r10` = per-glob data region (matches existing `bb_flat.c` convention), `rbp` = chunk frame for DEFINE'd chunks.  Variant patterns stay dynamic in `bb_pool`; no static dump.  Deferred-eval consumer (ME-8 — `SM_CALL_CHUNK` / `SM_PUSH_CHUNK`) lands after GOAL-CHUNKS-STEP17 closes.  Byrd-box ABI from `bb_boxes.s` preserved verbatim.  14 rungs in 6 phases.  When ME-14 closes, GOAL-MODE4-EMIT's `EM-MODE4-IS-MODE3-DUMP` reopens.  Sibling Goal that stays active: `GOAL-ICON-BB-COMPLETE`.  Baseline gates at carve: smoke 7/7, unified_broker 49/49, em_beauty_subsystems_mode4 PASS=4 FAIL=13 (frozen tripwire — mode 4 untouched).  ⛔ **Session-start protocol REQUIRES reading `ARCH-x86.md` AND `ARCH-SCRIP.md` before opening this Goal file.** |
| **Mode-4 x86 Emitter** | `GOAL-MODE4-EMIT.md` | one4all+corpus+.github | **PAUSED on premier-goal `GOAL-MODE3-EMIT`** (carved sess 2026-05-10).  `EM-MODE4-IS-MODE3-DUMP` reopens when GOAL-MODE3-EMIT ME-14 closes.  Until then, mode 4 stays frozen at the baseline `test_gate_em_beauty_subsystems_mode4.sh` PASS=4 FAIL=13 as a tripwire — any change there during mode-3 work signals an unintended side-effect.  Original architectural rung text below preserved for reference: **EM-MODE4-IS-MODE3-DUMP — pivot sess 2026-05-10 (Claude later) per ARCH-x86.md + ARCH-SCRIP.md.**  Mode-4 is no longer authored as a text emitter that walks SM_Program in parallel to mode-3.  Instead: **mode-4 IS mode-3 plus a SEG_CODE serializer.**  Mode-3 (`--sm-native` / `--jit-run`) is the one and only SM-x86 emitter; it produces native bytes in `SEG_CODE`.  Mode-4 (`--sm-emit --target=x64` / `--jit-emit --x64`) runs mode-3 to populate SEG_CODE, then dumps the bytes as `.s` (via `objdump -d`-equivalent disassembly) plus the auxiliary sections (.rodata strtab, .data registry, .bss/.data libscrip_rt-imports) the linker needs.  Two consequences: (1) mode-4 byte-identity to mode-3 is by construction, not a gate to maintain; (2) the alignment/prologue/chunk-frame question collapses — whatever mode-3 does is what mode-4 emits.  This also implies mode-3 must actually be a JIT (today it's a per-opcode tail-call thunk + C dispatch loop in `sm_jit_run`); fixing mode-3 to per-instruction native blobs is sub-rung -a of the new rung.  EM-7d-beauty-subsystems explicitly BLOCKED on EM-MODE4-IS-MODE3-DUMP.  Baseline mode-4 parity gate PASS=4 FAIL=13 frozen.  ⛔ **Session-start protocol REQUIRES reading `ARCH-x86.md` AND `ARCH-SCRIP.md` before opening this Goal file** — past Claude inferred mode definitions from `sm_codegen.c` source repeatedly and got it wrong every time. |
| **AST Rename** | `GOAL-AST-RENAME.md` | one4all+corpus+.github | AR-3 — prose "IR"→"AST" pass (AR-1+AR-2 ✅ 2026-05-09) |
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
