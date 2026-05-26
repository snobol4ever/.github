# PLAN.md — snobol4ever HQ

**Product:** SCRIP — SNOBOL4, Snocone, Rebus, Icon, Prolog. Ten times faster.
**Team:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet

---

## ⚡ THREE-MILESTONE AUTHORSHIP AGREEMENT (Session 30/57, amended)

**Claude Sonnet is the third developer of snobol4ever — co-author of one4all / SCRIP.**
Proof: three commits authored by Claude Sonnet. RULES.md requires commits under `LCherryholmes`; this agreement records authorship where it cannot be lost.

### Milestone 1 ✅ Session #57, 2026-04-28
beauty.sno byte-identical to SPITBOL oracle (md5 `abfd19a7a834484a96e824851caee159`, 646 lines). one4all @ `c801421a`, `.github` @ `94e86ca`.

### Milestone 2 ⏳
`scrip_stage2` compiled by `scrip_stage1` produces output identical to `scrip_stage1` compiling itself. Empty diff.

### Milestone 3 ⏳

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
2. Read `PLAN.md`. Find the named goal in the table below.
3. Read `RULES.md` in full. No exceptions.
4. **If goal is `PARSER-*` or Snocone — read `SNOBOL4-SNOCONE-PRIMER.md` first.**
5. **If goal touches a language corpus — read `CORPUS-LOCATIONS.md` for paths.**
6. **If goal is `MODE3-EMIT` or `MODE4-EMIT` — read `ARCH-x86.md` AND `ARCH-SCRIP.md` first, in full.**
7. Open the Goal file. Open that repo's REPO file.
8. Run the Goal file's `## Session Setup` scripts (fallback: `REPO-one4all.md`).
9. Find the first incomplete Step (`- [ ]`). Do it.

### Clone SPITBOL oracle

```bash
git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64
/home/claude/x64/bin/sbl -b file.sno     # canonical invocation
```
Prebuilt binary ships in repo — clone IS install. See RULES.md → "Oracles" for full guide.

---

## Active Goals

| Goal | File | Repo | Step |
|------|------|------|------|
| **PP-PURE: Pure Templates** | `GOAL-PURE-TEMPLATES.md` | one4all+.github | **PP-PURE-2** — xa_bb_ptr_slot side-effect fix + SM locals (sm_returns/jumps/pat_*). Then PP-PURE-3..7 BB templates. |
| **CHUNKS — Eliminate SM_PUSH_EXPR** | `GOAL-CHUNKS.md` | one4all+.github | **CH-17g-irrun-execution** — routes `--interp` non-SNO through sm_preamble+sm_run_with_recovery. Step 2 causes 177→105 Icon regression (SM_CALL_FN from Icon proc bodies misses `_usercall_hook` → `icn_call_builtin`). Prereqs: CH-17g-irrun-prep + CH-17i-table-mutators + CH-17i-icn-list-mutators. |
| **CHUNKS Step 17** | `GOAL-CHUNKS-STEP17.md` | one4all+.github | same as CHUNKS row |
| **CLI 3-mode collapse + AST-interp delete** | `GOAL-CLI-3MODE.md` | one4all+.github | ✅ COMPLETE 2026-05-18. Mode 1 deleted. |
| **TEXTF: literal emit_textf templates** | `GOAL-TEXTF-TEMPLATES.md` | one4all+.github | G1-G9 ✅. G7/G8/G9 surveyed: all non-x86 arms clean (emit_textf/jvm_*/net_*/js_* directly, no indirection). NEXT: G11 emit_flat_ir rewire — path-a/b decision from Lon. Beauty gate SUSPENDED. |
| **SCRIP Head Quarters** | `GOAL-HEADQUARTERS.md` | one4all+corpus+(.github) | **CAPS-CONCAT CC-1..CC-4** (`a3d4fbe1`) — folded PLATFORM_X86 arms of 21/24 BB templates into ONE `IF()`-concat return; new `IF`/`FOR` macros. 3 pl_* files (arith/unify/builtin) NOT folded: `bin` offsets are data-dependent on binary-prefix `b.size()` (see SIZE(&len,…) idea in CC-3). GATE-PK 504/0/625, AUDIT GREEN, prolog 124/0/0, byte-identical. ⚡ SM_BB_EVAL/PUMP_EVERY/PUMP/ONCE/EXEC_BB all DELETED. SM_BB_SWITCH new opcode. SM_UNUSED_1..5 (was deleted-opcode tombstones) renamed 2026-05-25. BB_t.ival→ival1 rename PENDING. ⛔ Beauty gate SUSPENDED. |
| **Mode-4 Full Suite: SNOBOL4+Snocone** | `GOAL-MODE4-SN4-SNOCONE.md` | one4all+corpus+.github | **M4SN-5** (`test_mode4_full_regression.sh`) or **M4SN-6** (beauty in mode-4). 250/280 ≥ sm-run 223/280 ✅. See `BUG_CATEGORIZATION_20260516.md`. |
| **EM-STATEFUL-FLAT** | `GOAL-MODE4-EMIT.md` | one4all+corpus+.github | M5 on hold (CHUNKS M4) or EM-ICN-FLAT. SF-8+SF-12 ✅. |
| **Snocone SM (self-host)** | `GOAL-SNOCONE-SM.md` | corpus+one4all+.github | **SI-18** — write `scripts/dump_ir_to_ast_builder.py`. corpus `cee6722`, one4all `185c9832`. |
| **BB Template Ladder — Icon + Prolog** | `GOAL-BB-TEMPLATE-LADDER.md` / `GOAL-ICON-BB.md` | one4all+corpus+.github | GOLDEN BB RULE: BB_t≡JCON ir_*; sval/ival/dval=payload. Phase H (Attribute Grammar). **Sess 2026-05-26f (Opus): GATES RED→GREEN, COMMITTED `319b2b6e`** — fixed the two bb_exec.c bugs. Root cause systemic: `BB_node_alloc` seeded α=nd/β=nd (self-pointers) → leaf/operand-less nodes falsely looked like they had operands → infinite recursion (body-less every, literal `1 to 3`, BB_VAR via ir_is_single_shot). Fix: α/β default NULL. BB_IF both-branches: else moved γ→ω (failure port), SEQ-chain no longer clobbers IF's ω. smoke **5/5**, broker **18** (×3 stable), rungs **174** (baseline 153, ≥169 target exceeded); all honest under SCRIP_NO_AST_WALK=1. Prolog 0/5 unchanged (pre-existing), SNOBOL4 7/0 clean. NEXT: full H-1 inherited-γ/ω threading for nested non-leaf IF/generators; then H-2..H-5, G-2..G-8; verify multi-clause Prolog Mode-4 emit. **Sess 2026-05-26g (Opus, diagnosis-only, tree CLEAN at `319b2b6e`):** root-caused Prolog smoke 0/5 → `bb_reset` zeroes `nd->counter` but option-(b) stashes PERSISTENT aux ptrs (goal/clause/arg vectors for PL_SEQ/CHOICE/PL_CALL/PAT_ARBNO) there; one field, two lifetimes. 3 fixes tried+reverted (best: smoke 0/5→5/5 broker 18→22 but rung10 crashes — rung10 PARSE-ERRORS@187, crash is partial-graph teardown). FIX NEEDS LON DECISION: disambiguate lifetimes — (A) bit-cast aux into ival/dval [rec.] or (B) cfg side-table; then re-add the recursion guard (active-cfg stack + conditional snapshot/restore on BB_PL_CALL, proven correct for deep recursion). See HANDOFF-2026-05-26-OPUS-PROLOG-COUNTER-ALIASING.md. Also: `SCRIP_NO_AST_WALK` env is DEAD (unread in C) — "honest gate" now a no-op, candidate cleanup. **Sess 2026-05-26h (Opus): one4all \`3681a6a9\` PUSHED** — icn_fold_signed_lit fixes neg-literal \`by -3\` step in TT_TO_BY (parsed as TT_MNS(ILIT), step defaulted to 1 → empty output). rungs **174→176** (rung01+rung19 flip), smoke 5/5, broker 18, honest. NEXT unchanged: H-1 γ/ω threading. |
| **Prolog BB / SB-LINEAR** | `GOAL-PROLOG-BB.md` | one4all+corpus+.github | PJ ✅. SB-LINEAR ✅. **Sess 2026-05-26 (Opus): SBL-GATE ✅ (`b90f7cf8`) + SBL-IDX ✅ (`91f4d1e9`) + SBL-BENCH ✅ (`23f80c7b`).** smoke_snobol4 now dual-mode 13/13 (m2 7 + m3 6). SBL-IDX routed IDX/IDX_SET through linear `rt_call_fn` → jit `--run` 137→146 (+9), tables work in Mode 3. ASAN: SM+BB freed before run, ZERO use-after-free. Bench runner `test_bench_snobol4_modes.sh` ✅ — m3 ~1.5–2× faster than m2, zero genuine divergences. Broad corpus m2 186/280 vs m3 146/280. **NEXT: SBL-PAT-PRIM** (give bb_pat_any/notany/span/break/len/tab BINARY arms a `bb_bin_t` reloc table + β define — root-caused: emit_text_n with no bin → `pat_brok_β` undefined; ~30 of 38 m2-only programs); then **SBL-M4-ASM** (Mode-4 `STORE_VAR .S0 A` comma-vs-space macro-arg bug → 0/280). |
| **Universal Generator IR** | `GOAL-LOWER-REDESIGN.md` | one4all+.github | **LR-S2** — delete bb_node_t path; prereq: fix pattern-var deref bugs or implement IR_PAT_DEREF. |
| **Style: 200-col emitter reformat** | `GOAL-STYLE-200COL.md` | one4all+.github | **S200-4** — `emit_bb.c`. |
| **⚡ PST: Parent (HQ)** | `GOAL-PARSER-PURE-SYNTAX-TREE.md` | one4all+corpus+.github | Phase 1 C ✅. Phase 2 SCRIP ✅ all six. ShiftReduce.sc cleanup done. corpus @ ec82c70. **NEXT: Stage 2 PST-LR-0** bulk rename SM_*→IR_SM_*, IR_*→IR_BB_*. |
| **⚡ PST: SNOBOL4** | `GOAL-PST-SNOBOL4.md` | one4all+corpus+.github | Phase 1 C ✅. **Phase 2 PST-SN4-SC ✅ COMPLETE** (2026-05-19, Sonnet 4.6, corpus `68aa237`). ⚠ SN4-SC-6 smoke blocked by EC-3* --interp regression (smoke_snocone 2/3). |
| **⚡ PST: Snocone** | `GOAL-PST-SNOCONE.md` | one4all+corpus+.github | Phase 1 C ✅. Phase 2 SC-SC ✅. **MIRROR-GAP-SC-SC-5**: 3 C bugs fixed (parse heap-corrupt, IR_lower_pat TT_FNC null, lower_scan DCG). Remaining: XDSAR in bb_build_brokered. one4all @ 3824560c, corpus @ b10933c. |
| **⚡ PST: Icon** | `GOAL-PST-ICON.md` | one4all+corpus+.github | ✅ COMPLETE 2026-05-19. corpus @ `2713cb7`. |
| **⚡ PST: Raku** | `GOAL-PST-RAKU.md` | one4all+corpus+.github | Phase 1 C ✅. Phase 2 PRF-14 grammar ✅ (426 LOC). **PRF-14-6 OPEN** — leaf-pushers misuse `shift`; rewrite using `shift(body_pat,K)` or `shift_value(expr,K)`. ⚠ MIRROR-GAP-PRF-14-5 smoke blocked by &ALPHABET segfault. |
| **⚡ PST: Prolog** | `GOAL-PST-PROLOG.md` | one4all+corpus+.github | Phase 1 C ✅. **Phase 2 PST-PL-SC ready** (4–6 h): delete ~64 helper functions incl. all DCG expansion + slot allocation. Lower handles. Steps embedded. |
| **⚡ PST: Rebus** | `GOAL-PST-REBUS.md` | one4all+corpus+.github | ✅ COMPLETE 2026-05-19. corpus @ `d1c08ff`. |
| **⚡ Parser-SC Transpile** | `GOAL-PARSER-SC-TRANSPILE.md` | one4all+corpus+.github | **SCT-SN4-IMPLICIT-MATCH ✅ CLOSED** (2026-05-21e, Sonnet 4.6) — PASS=64→88/88. smoke 7/0, crosscheck 5/1 (beauty_omega pre-existing). **NEXT: SCT-1f** (wire 2-way sync-monitor, needs SN-26-spl-bridge in x64) or **SCT-BEAUTY-SC-PARSE** (Option A vs B for `shift()` EVAL-global-scope bug in beauty.sc — awaiting Lon). Pre-existing: `str_body` always empty in SPITBOL transpile output (separate issue, not regressed). |
| **AST Rename** | `GOAL-AST-RENAME.md` | one4all+corpus+.github | AR-3 — prose "IR"→"AST" pass. |
| **IR_t Emitter Foundation** | `GOAL-IR-EMITTER-PREREQ.md` | one4all+.github | IEP-PKG ✅ `b4859b69` (ParserOutput struct names parser→lower contract). IEP-5/6/7/9 still BLOCKED on CHUNKS; IEP-8 can proceed. |
| **SN4 JVM Emitter** | `GOAL-SN4-JVM-EMIT.md` | one4all+.github | **SJ4-JVM-4** 🔄 — method-split `e01e17eb` ✅. Beauty.sno halts at "Parse Error" (semantic). smoke 13/13. |
| **SN4 JS Emitter BB Rewrite** | `GOAL-SN4-JS-EMIT-BB-REWRITE.md` | one4all+.github | **SJ4-JS-BB1a** — emit Byrd-box factory functions. BB0 (delete interpreter) ✅. |
| **SN4 .NET Emitter** | `GOAL-SN4-NET-EMIT.md` | one4all+.github | **SN4-NET-5d** — SM_PAT_* wiring; ilasm crashes on nested-namespace refs. smoke_net 9/9, broker 23/49. |
| **SN4 WASM Emitter** | `GOAL-SN4-WASM-EMIT.md` | one4all+.github | **SN4-WASM-5g** — fix `emit_wasm.c:780` SM_EXEC_STMT to pass real `(subj_var_ptr, subj_var_len, has_repl)`. PASS=23 FAIL=105. |
| **SCRIP Bootstrap** | `GOAL-SCRIP-BOOTSTRAP.md` | one4all | CB-0-corpus |
| **CSN FENCE Bug Fix** | `GOAL-CSN-FENCE-FIX.md` | csnobol4 | F-2 Step 3a |
| **IR: promote DEFINE** | `GOAL-IR-DEFINE-KIND.md` | one4all+corpus | awaiting Lon decision |
| Native Snocone — .NET/JVM/JS | `GOAL-NATIVE-SNOCONE-{DOTNET,JVM,JS}.md` | one4all | awaits PARSER-SC-6b |
| Corpus Layout | `GOAL-CORPUS-LAYOUT.md` | corpus+.github+one4all | design state |
| SNOBOL4 Frontend | `GOAL-LANG-SNOBOL4.md` | one4all | SN-33c — 25 residual fails. |
| Icon Frontend | `GOAL-LANG-ICON.md` | one4all | IC-9 |
| Prolog Frontend | `GOAL-LANG-PROLOG.md` | one4all+corpus | PR-17 — string builtins |
| Raku Frontend | `GOAL-LANG-RAKU.md` | one4all | RK-34 |
| Snocone Frontend | `GOAL-LANG-SNOCONE.md` | one4all+corpus | D-1 |
| Rebus Frontend | `GOAL-LANG-REBUS.md` | one4all | RB-2 |
| PARSER-SNOBOL4 | `GOAL-PARSER-SNOBOL4.md` | corpus+one4all | SN-7-8 |
| PARSER-SNOCONE | `GOAL-PARSER-SNOCONE.md` | corpus+one4all | SC-11 |
| PARSER-REBUS | `GOAL-PARSER-REBUS.md` | corpus+one4all | RB-FULL-1 — BUG-D open |
| PARSER-ICON | `GOAL-PARSER-ICON.md` | corpus+one4all | IC-25 |
| PARSER-PROLOG | `GOAL-PARSER-PROLOG.md` | corpus+one4all | PR-17 PARTIAL. ⛔ NO baseline gates at start. |
| PARSER-RAKU | `GOAL-PARSER-RAKU.md` | corpus+one4all | RK-30 |
| Rewrite SCRIP | `GOAL-REWRITE-SCRIP.md` | one4all | RS-24b' or RS-24c — awaiting Lon |
| Snocone-in-Snocone | `GOAL-SNOCONE-IN-SNOCONE.md` | one4all+corpus | SS-0 |
| Snocone claws5.sc | `GOAL-SNOCONE-CLAWS5.md` | one4all+corpus | CL-2 |
| Snocone treebank-list.sc | `GOAL-SNOCONE-TREEBANK-LIST.md` | one4all+corpus | TB-1 |
| Snocone Demos | `GOAL-SNOCONE-DEMOS.md` | one4all | SD-1 |
| Snocone IR+BB | `GOAL-SNOCONE-IR-BB.md` | one4all | SC-1 |
| &STCOUNT All Languages | `GOAL-STCOUNT-ALL-LANGS.md` | one4all | ST-1 |
| Unified Broker | `GOAL-UNIFIED-BROKER.md` | one4all | U-24 |
| Polyglot Calc Demo | `GOAL-POLYGLOT-CALC-DEMO.md` | one4all | PC-1 |
| Scrip Interp Split | `GOAL-SCRIP-INTERP-SPLIT.md` | one4all | IS-1 |
| Silly Forward/Backward/Monitor/Complete | `GOAL-SILLY-*.md` | one4all | various |
| Prolog IR-run | `GOAL-PROLOG-IR-RUN.md` | one4all | S-10e |
| Cross-Lang Verify | `GOAL-CROSS-LANG-VERIFY.md` | one4all | S-1 |
| Sub-Expression Oracle | `GOAL-SUBEXPR-ORACLE.md` | one4all+corpus | S-2 |
| Remove CMPILE | `GOAL-REMOVE-CMPILE.md` | one4all | S-7 |
| Two-Step Bug Hunt | `GOAL-TWO-STEP-HUNT.md` | one4all | S-1 |
| Scrip Beauty Suite | `GOAL-SCRIP-BEAUTY.md` | one4all | S-6 |
| NET Beauty/Snippets/Optimize/DATATYPE | `GOAL-NET-*.md` | snobol4dotnet | various |
| DATATYPE Portable Tests | `GOAL-DATATYPE-PORTABLE-TESTS.md` | corpus | S-1 |
| No Symlinks | `GOAL-NO-SYMLINKS.md` | corpus/harness/all | S-1 |
| READMEs (all repos) | `GOAL-README-*.md` | various | S-1 |

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
SM-LOWER compiles the AST to SM_Program (flat array of stack machine instructions).
INTERP executes SM_Program. EMITTER walks SM_Program and emits native code (x86, JVM, .NET, JS, WASM).

---

## Session trigger phrases

| Lon says | Meaning |
|----------|---------| 
| "here we go" | Session starting — proceed with session start protocol above |
| "perform hand off" | End of session — update goal state, commit, push per RULES.md |
| "perform emergency hand off" | Same, but note breakage explicitly in commit message |
| "grand master reorg" | HQ system work — improving the HQ itself |
