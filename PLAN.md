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

### Clone the SPITBOL oracle alongside the standard repos

SPITBOL is the **primary oracle** for every SCRIP language (SNOBOL4, Snocone, Rebus, Icon, Prolog, Raku) — no day-to-day SCRIP work should be without it. Clone `snobol4ever/x64` to `/home/claude/x64` whenever you clone the standard repos. The repo **ships a prebuilt `sbl` binary at `/home/claude/x64/bin/sbl`** — cloning IS the install; no build step required for routine work. The `interp` profile in `.github/snobol4ever_clone.sh` already includes `x64`; if you're cloning by hand instead, add it:

```bash
git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64
/home/claude/x64/bin/sbl -b file.sno     # canonical invocation
```

Only rebuild SPITBOL from source (`bash one4all/scripts/build_spitbol_oracle.sh`) when patching the SPITBOL runtime itself (e.g. SN-26-spl-bridge for the IPC monitor wire). RULES.md → "Oracles" has the full SPITBOL invocation guide.

---

## Active Goals

| Goal | File | Repo | Step |
|------|------|------|------|
| **CHUNKS — Eliminate SM_PUSH_EXPR** | `GOAL-CHUNKS.md` | one4all+.github | **CH-17g-irrun-execution** — routes `--ir-run` non-SNO through sm_preamble+sm_run_with_recovery. 2026-05-10 probe-and-revert: step 2 causes 177→105 Icon regression; root cause = SM_CALL_FN from Icon proc bodies doesn't reach icn_call_builtin via _usercall_hook. Prereqs: CH-17g-irrun-prep + CH-17i-table-mutators + CH-17i-icn-list-mutators. |
| **CHUNKS Step 17** | `GOAL-CHUNKS-STEP17.md` | one4all+.github | same as CHUNKS row |
| **Icon BB JCON triage** | `GOAL-ICON-BB-JCON.md` | one4all+corpus+.github | Session 2026-05-17e (Opus 4.7): IJ-LCONCAT+IJ-FIND-GEN+IJ-SEQ-GEN landed. one4all `f81302ca`. ir-run 191→194 (+3, zero regressions). rung15 lconcat ✅, rung08 find_gen ✅, rung30 misc_seq ✅. NEXT: rung31 sort (3); rung13 alt_filter; rung06 upto; rung36 jcon survey (32 remaining). |
| **Mode-4 Full Suite: SNOBOL4+Snocone** | `GOAL-MODE4-SN4-SNOCONE.md` | one4all+corpus+.github | **M4SN-5** (`test_mode4_full_regression.sh`) or **M4SN-6** (beauty in mode-4). 250/280 ≥ sm-run 223/280 ✅. See `BUG_CATEGORIZATION_20260516.md`. |
| **EM-STATEFUL-FLAT** | `GOAL-MODE4-EMIT.md` | one4all+corpus+.github | M5 on hold (CHUNKS M4) or EM-ICN-FLAT. SF-8+SF-12 ✅. |
| **Snocone SM (self-host)** | `GOAL-SNOCONE-SM.md` | corpus+one4all+.github | **SI-18** — write `scripts/dump_ir_to_ast_builder.py`. corpus `cee6722`, one4all `185c9832`. |
| **Prolog BB JCON triage** | `GOAL-PROLOG-BB-JCON.md` | one4all+corpus+.github | **PJ-9d partial 🔄** (2026-05-16i). Registry mechanism + simple-body Mode-4 working: `rt_register_predicates_pl` + builder API in rt.c, `emit_pl_predicate_registry` in emit_sm.c, end-to-end runner script. Mode-4 prints correct output for write/arith/cross-pred-call/arg-binding tests. **Open (PJ-9e candidate):** multi-clause predicates fail — per-clause bodies live in `IR_PL_CHOICE` children's `opaque` as separate `IR_block_t*` not in parent `cfg->all[]`; builder doesn't walk them yet. Cross-language AST-walk audit completed (Lon Q): all six languages clean in Modes 2/3 across 609 gate tests, empirically. PJ-9c partial ✅ (one4all 0ffffa2e); PJ-9b ✅ (ef2f90e4); PJ-9a ✅ (fc6fa0a8). All gates hold: smoke 5/5, crosscheck 128/0, honest_prolog 124/0/0, honest_icon 277/0/0, broker 20/49. |
| **Universal Generator IR** | `GOAL-LOWER-REDESIGN.md` | one4all+.github | **LR-S2** — delete bb_node_t path; prereq: fix pattern-var deref bugs or implement IR_PAT_DEREF. |
| **Style: 200-col emitter reformat** | `GOAL-STYLE-200COL.md` | one4all+.github | **S200-4** — `emit_bb.c`. |
| **⚡ PST: SNOBOL4 + Snocone** | `GOAL-PARSER-PURE-SYNTAX-TREE.md` | one4all+corpus+.github | **PST-SC-4j fix** ⚠ BROKEN — lower_return must emit SM_RETURN directly not SM_JUMP. SN4: 1a-1d ✅ PST-SN4-2 ✅ PST-SC-4a…4i ✅ 4j grammar done but broken. |
| **⚡ PST: Icon + Raku** | `GOAL-PST-ICN-RAKU.md` | one4all+corpus+.github | **DONE (with sidecar caveat)** PST-RAKU-5c ✅ 2026-05-16. parser_raku.sc rewrite: 1788→607 lines in parser file; **11 functions relocated to `raku_helpers.sc` (231 lines)**, not eliminated. parser_icon.sc 525→381 lines; **5 functions relocated to `icon_helpers.sc`**. Helpers loaded by `run_scrip_parser.sh` alongside the parser. Cleanup pass deferred until runtime stabilises. corpus@16b799c, one4all@c52b724c. |
| **⚡ PST: Rebus** | `GOAL-PST-REBUS.md` | one4all+corpus+.github | **PST-RB-PRE-BEAUTY Bug #1 ✅** 2026-05-17 (Opus 4.7, one4all `bad0fffd`): upr(upr) shadow-param recursion fixed in interp_eval.c via is_current_frame_local() helper in interp_call.c. 30 LOC, 3 files. All gates hold floor. Beauty self-host no longer segfaults but still 0 lines (now hangs in icase due to Bug #2: mode-1 interp_exec missing SUBJ-PAT split that lower.c does for modes 2/3/4). NEXT: PST-RB-PRE-BEAUTY Bug #2 (~30 lines sketched, untested). Then 5i triage queues from emergency handoff #2 (icon hang, prolog/raku BB overflow, three segfaulters), then PST-RB-5i-PRE-CORPUS → PST-RB-NEXT-BB-CACHE → PST-RB-NEXT-LABTAB → 5i finish → 5j → 5k. |
| **⚡ PST: Prolog** | `GOAL-PST-PROLOG.md` | one4all+corpus+.github | **PST-PL-6f** — Delete Term*-returning parse paths; remove lower_term() sites replaced by 6d. PST-PL-6a-6e ✅ 2026-05-16. |
| **⚡ Parser-SC Transpile (2-way harness via Snocone→SNOBOL4)** | `GOAL-PARSER-SC-TRANSPILE.md` | one4all+corpus+.github | **SCT-9g-snocone ✅ + n-ary arith emission fix ✅** 2026-05-17 (Opus 4.7). SCT-9g re-scoped per-language (a-f + cross); snocone audit landed as `.github/PRECEDENCE-AUDIT.md`. Findings: `.sc` grammar `+ - * /` are right-recursive (wrong) per SPITBOL Manual Ch.15 LEFT-assoc; C frontend correct. Bonus: `lower_sno.c` TT_ADD/SUB/MUL/DIV cases were silently dropping n-ary children `c[2..n-1]`; now left-folded — `20-5+2`→17 via SPITBOL ✅. Snocone fixture gate 60/7/0 (no regressions). Prior SCT-9c+9d+9e+9f ✅ still stands. one4all HEAD `96d39c05`+local-WIP, corpus HEAD `1b24df4`. **NEEDS LON:** (1) spec docs for rebus/icon/raku/prolog audits; (2) decision on `.sc` arith grammar fix (rewrite Expr6..Expr11 to left-fold) or documented exception; (3) decisions on SCT-9i do-while shape. **NEXT (no decision):** SCT-9g-snobol4 (manual on disk), SCT-9h (token-slot mangling), SCT-9j (wire test_parser_sc_transpile.sh), &FULLSCAN prelude dedup (3-line followup unblocks snocone/icon SPITBOL accept-check). |
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
