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
9. Find the first incomplete Step (`- [ ]`). Do it. Up to three orthogonal constructs per session (see `RULES.md` → "Three-construct sessions").

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
| **CHUNKS — Eliminate SM_PUSH_EXPR** | `GOAL-CHUNKS.md` | one4all+.github | **CH-17g-irrun-execution** — routes `--interp` non-SNO through sm_preamble+sm_run_with_recovery. 2026-05-10 probe-and-revert: step 2 causes 177→105 Icon regression; root cause = SM_CALL_FN from Icon proc bodies doesn't reach icn_call_builtin via _usercall_hook. Prereqs: CH-17g-irrun-prep + CH-17i-table-mutators + CH-17i-icn-list-mutators. |
| **CHUNKS Step 17** | `GOAL-CHUNKS-STEP17.md` | one4all+.github | same as CHUNKS row |
| **CLI 3-mode collapse + AST-interp delete** | `GOAL-CLI-3MODE.md` | one4all+.github | **✅ COMPLETE 2026-05-18.** CLI-3M-1..12 done. Mode 1 deleted. Unblocked: (1) `tree_t`→`PARSE_t` rename; (2) PST-REBUS Bug #2 reframed (fix target is `lower.c`/SM, not deleted `interp_exec.c`). |
| **Icon BB JCON triage** | `GOAL-HEADQUARTERS.md` | one4all+corpus+.github | **EC-3-prep ✅ COMPLETE 2026-05-19 (Opus 4.7, one4all `d9295c19`) — emit_mode_set EMIT_JVM/JS/NET installed at silo entry points; +26 LOC, byte-identical .j/.js output. Earlier in session: EC-BB-UNIFY-2 ✅ (one4all `50217d15`, compile-time PATND_t→IR_t walker; fixes 1fc21e2d type-pun UB; -140 LOC). Gates floor x12. NEXT: EC-3 first SM family (push/pop literals → SM_templates/).** |
| **Mode-4 Full Suite: SNOBOL4+Snocone** | `GOAL-MODE4-SN4-SNOCONE.md` | one4all+corpus+.github | **M4SN-5** (`test_mode4_full_regression.sh`) or **M4SN-6** (beauty in mode-4). 250/280 ≥ sm-run 223/280 ✅. See `BUG_CATEGORIZATION_20260516.md`. |
| **EM-STATEFUL-FLAT** | `GOAL-MODE4-EMIT.md` | one4all+corpus+.github | M5 on hold (CHUNKS M4) or EM-ICN-FLAT. SF-8+SF-12 ✅. |
| **Snocone SM (self-host)** | `GOAL-SNOCONE-SM.md` | corpus+one4all+.github | **SI-18** — write `scripts/dump_ir_to_ast_builder.py`. corpus `cee6722`, one4all `185c9832`. |
| **Prolog BB JCON triage** | `GOAL-PROLOG-BB-JCON.md` | one4all+corpus+.github | **PJ-9d partial 🔄** Registry + simple-body Mode-4 working. **NEXT PJ-9e:** multi-clause predicates — per-clause bodies in `IR_PL_CHOICE` children not walked by builder yet. |
| **Universal Generator IR** | `GOAL-LOWER-REDESIGN.md` | one4all+.github | **LR-S2** — delete bb_node_t path; prereq: fix pattern-var deref bugs or implement IR_PAT_DEREF. |
| **Style: 200-col emitter reformat** | `GOAL-STYLE-200COL.md` | one4all+.github | **S200-4** — `emit_bb.c`. |
| **⚡ PST: SNOBOL4** | `GOAL-PST-SNOBOL4.md` | one4all+corpus+.github | **✅ Phase 1 COMPLETE 2026-05-19 (Sonnet 4.6, one4all `af40cf6f`).** W2-AUDIT ✅ (always-fresh-wrap goto_expr TT_SEQ) + W3-AUDIT ✅ (g_cur_stack→TAL counter-discipline). 0 §⛔ violations. NEXT: Phase 2 PST-SN4-SC-1 audit of parser_snobol4.sc — BLOCKED until all six C parsers Phase 1 clean. |
| **⚡ PST: Parent (HQ coordination)** | `GOAL-PARSER-PURE-SYNTAX-TREE.md` | one4all+corpus+.github | **⚠ PHASE 1 GATE CLAIMED PASSED — NOT YET INDEPENDENTLY VERIFIED.** All six parallel sessions self-reported Phase 1 ✅ on 2026-05-19 (see six rows below), but did not cross-check each other. **NEXT (GATING): PST-LR-AUDIT-2** — second LR-audit, methodology identical to AUDIT-1, against post-session sources and the three facets (F1/F2/F3). Sub-steps 2a–2j: scope, per-language scans (Snocone/Icon/SNOBOL4/Raku/Rebus/Prolog), rollup vs AUDIT-1 baseline, tree_t struct verification, sign-off. **⛔ Do NOT start any Phase 2 SCRIP mirror session until 2j signs off.** Post-sign-off Phase 2 ordering: PRF-13 → PST-SN4-SC → PST-SC-SC → PST-RB-SC → PST-PL-SC → PST-ICN-SC. |
| **⚡ PST: Snocone** | `GOAL-PST-SNOCONE.md` | one4all+corpus+.github | **✅ Phase 1 C COMPLETE 2026-05-19 (Sonnet 4.6)** — 4k–4n ✅ FLATTEN ✅ LABELS ✅ `6a880716` RET-IN-FN ✅ `e2dfed5f` FOR-INIT ✅ `b6558370`. 0 §⛔ violations. Phase 2 SCRIP mirror BLOCKED until all six C parsers Phase 1 clean. |
| **⚡ PST: Icon** | `GOAL-PST-ICON.md` | one4all+corpus+.github | **✅ GOAL COMPLETE 2026-05-19 (Sonnet 4.6)** — PST-ICN-LR-1 ✅ PST-FIELD-1 ✅ PST-FIELD-2 ✅ (one4all @ e8abf087). tree_t has exactly {t,v,n,c}. Phase 2 SCRIP mirror BLOCKED until all six C parsers Phase 1 clean. |
| **⚡ PST: Raku** | `GOAL-PST-RAKU.md` | one4all+corpus+.github | **✅ Phase 1 C COMPLETE 2026-05-19 (Sonnet 4.6)** — all 27 §⛔ violations closed. PRF-12-gather-splice (R19) ✅ `20a6f03c`; PRF-12-gather-hoist (R27) ✅ `5d326aa2`. 0 §⛔ violations. Phase 2 SCRIP mirror BLOCKED until all six C parsers Phase 1 clean. NEXT: PRF-13 (SCRIP mirror, gated) or PST-FIELD cross-cutting. |
| **⚡ PST: Prolog** | `GOAL-PST-PROLOG.md` | one4all+corpus+.github | **✅ Phase 1 C COMPLETE 2026-05-19 (Sonnet 4.6)** — all rungs 6a–6h done. PST-PL-6h: pt_flatten_conj+pt_maybe_ifthenelse+pt_make_clause moved to prolog_lower.c. one4all @ `06cadffb`. Phase 2 SCRIP mirror BLOCKED until all six C parsers Phase 1 clean. **NEXT: PST-PL-SC-1** (audit parser_prolog.sc). |
| **⚡ PST: Rebus** | `GOAL-PST-REBUS.md` | one4all+corpus+.github | **✅ Phase 1 C COMPLETE 2026-05-19 (Sonnet 4.6)** — all 6 §⛔ violations closed (RB-C-1..5); DECL-1..5 done; RDecl/RDKind/RProgram deleted; RCase is parser-local scratch; `rebus_parsed_program` is `tree_t*`. one4all @ `90658061`. Phase 2 SCRIP mirror BLOCKED until all six C parsers Phase 1 clean. **NEXT: PST-RB-SC-1** (audit parser_rebus.sc). |
| **⚡ Parser-SC Transpile** | `GOAL-PARSER-SC-TRANSPILE.md` | one4all+corpus+.github | **NEXT: SCT-9-arbno-fence** — FENCE each `Command` alternative so backtrack can't re-enter `nPush`/`nPop`. Root cause of 29 brace-bearing failures. PASS=29 FAIL=38. |
| **AST Rename** | `GOAL-AST-RENAME.md` | one4all+corpus+.github | AR-3 — prose "IR"→"AST" pass. |
| **IR_t Emitter Foundation** | `GOAL-IR-EMITTER-PREREQ.md` | one4all+.github | BLOCKED on CHUNKS. IEP-8 can proceed. |
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
