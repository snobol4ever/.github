# PLAN.md — snobol4ever HQ

**Product:** SCRIP — SNOBOL4, Snocone, Rebus, Icon, Prolog. Ten times faster.
**Team:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet

---

## ⚡ THREE-MILESTONE AUTHORSHIP AGREEMENT

**Claude Sonnet is the third developer of snobol4ever — co-author of one4all / SCRIP.**

### Milestone 1 ✅ Session #57, 2026-04-28
beauty.sno byte-identical to SPITBOL oracle (md5 `abfd19a7a834484a96e824851caee159`). one4all `c801421a`, `.github` `94e86ca`.

### Milestone 2 ⏳
`scrip_stage2` compiled by `scrip_stage1` produces output identical to `scrip_stage1` compiling itself. Empty diff.

### Milestone 3 ⏳

|             | C/x86-64 | JVM | .NET | WASM | JS |
|-------------|:--------:|:---:|:----:|:----:|:--:|
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
Prebuilt binary ships in repo — clone IS install. See RULES.md → "Oracles".

---

## Active Goals

| Goal | File | Repo | Step |
|------|------|------|------|
| **PP-PURE: Pure Templates** | `GOAL-PURE-TEMPLATES.md` | one4all+.github | **PP-PURE-2** — xa_bb_ptr_slot side-effect fix + SM locals. Then PP-PURE-3..7 BB templates. |
| **CHUNKS — Eliminate SM_PUSH_EXPR** | `GOAL-CHUNKS.md` | one4all+.github | **CH-17g-irrun-execution** — routes `--interp` non-SNO through sm_preamble+sm_run_with_recovery. Icon regression: SM_CALL_FN from Icon proc bodies misses `_usercall_hook`. Prereqs: CH-17g-irrun-prep + CH-17i-table/list-mutators. |
| **CHUNKS Step 17** | `GOAL-CHUNKS-STEP17.md` | one4all+.github | same as CHUNKS row |
| **CLI 3-mode collapse** | `GOAL-CLI-3MODE.md` | one4all+.github | ✅ COMPLETE 2026-05-18. |
| **TEXTF: literal emit_textf templates** | `GOAL-TEXTF-TEMPLATES.md` | one4all+.github | G1-G9 ✅. NEXT: G11 emit_flat_ir rewire — path-a/b decision from Lon. Beauty gate SUSPENDED. |
| **SCRIP Head Quarters** | `GOAL-HEADQUARTERS.md` | one4all+corpus+(.github) | CAPS-CONCAT CC-1..4 ✅ (`a3d4fbe1`). GATE-PK 504/0/625. SM_BB_EVAL/PUMP_EVERY/PUMP/ONCE/EXEC_BB DELETED. SM_BB_SWITCH new opcode. BB_t.ival→ival1 rename PENDING. Beauty gate SUSPENDED. |
| **SNOBOL4 Pattern BB** | `GOAL-SNOBOL4-BB.md` | one4all+corpus+.github | SBL-G-1 ✅ + SBL-ANY-1 ✅ (`308e0378`). Fixed flat-driver α-label (box entry skipped `lea r10` cursor setup → all subject-deref boxes broke incl. "filled" LIT) + GAS macro-annotation bug. Broad corpus 121→137. **NEXT: SBL-CAP** (capture forces non-invariant → blocks inline; recovered `bb_capture.s` at `660339cd~1`). Then NOTANY/SPAN/BREAK TEXT (transcribe recovered .s), BINARY arms, ARBNO, BREAKX flag, ATP kind. NOT pushed yet. |
| **Mode-4 Full Suite: SNOBOL4+Snocone** | `GOAL-MODE4-SN4-SNOCONE.md` | one4all+corpus+.github | **M4SN-5** (`test_mode4_full_regression.sh`) or **M4SN-6** (beauty in mode-4). 250/280 ≥ --interp 223/280 ✅. |
| **EM-STATEFUL-FLAT** | `GOAL-MODE4-EMIT.md` | one4all+corpus+.github | M5 on hold (CHUNKS M4) or EM-ICN-FLAT. SF-8+SF-12 ✅. |
| **Snocone SM (self-host)** | `GOAL-SNOCONE-SM.md` | corpus+one4all+.github | **SI-18** — write `scripts/dump_ir_to_ast_builder.py`. corpus `cee6722`, one4all `185c9832`. |
| **BB Template Ladder — Icon + Prolog** | `GOAL-ICON-BB.md` | one4all+.github | ⛔ **NEXT: RUNG ICN-Z-2b — leaf + BB_SEQ/COMPOUND true-port slice** (see "START HERE" block at top of goal file; fully specified entry point, gate after each step). The one safely-sliceable piece of the ICN-Z port rewire. PRIOR: ICN-XA-1 ✅ + ICN-M4 binop-gen ✅ (`809fc870`/`7ff8fce8`) mode4_rung PASS=2→5. Gates: smoke_icon 5/5, broker 23, rungs 198, smoke_prolog 5/5, FACT 0. After Z-2b: full atomic ICN-Z pass (68 lower_icn.c sites + bb_exec.c port-follower — line map in goal file). |
| **Prolog BB / SB-LINEAR** | `GOAL-PROLOG-BB.md` | one4all+corpus+.github | ⛔ **TOP: Prolog RUNG LADDER + mode-4.** GATE-3 **88/107**, **GATE-4 2/4** (m4-seq + m4-call green; `449f4ca3` 2026-05-27 Opus). V-1+V-2+AGW-9B-call ✅; write(atom) mode-4 ✅. NEXT: V-3 remainder — `bb_pl_choice.cpp` then `bb_pl_alt.cpp` (greens m4-choice/alt); each needs a `walk_bb_flat` case + inline trail_mark/unwind. Then V-4 (delete rt_pl_b_* runtime rebuild). Also pending: rung18 plus/3, rung25 term_to_atom ops, rung28 catch/throw, AGW-5 stateful ITE, runtime assertz-in-body. See HANDOFF-2026-05-27-OPUS-PROLOG-BB-AGW9B-CALL.md. |
| **Raku BB** | `GOAL-RAKU-BB.md` | one4all+corpus+.github | **RK-BB-1 ✅** (`13cef01a`, 2026-05-27 Opus) — lazy range→shared `BB_TO_BY` via `lower_raku_range`(reuses `lower_icn_expr_top`)+`SM_BBSW_RK_GEN`; mode-2 8/30, mode-4 GATE-RK4 8/30 (incl rk_range_for). `bb_to_by.cpp` reused unchanged. Shared `rt_nv_set` peek-fix (mode-2/4 STORE_VAR parity). GATE-PK 455/64 HELD pre-6deb9f71 (that upstream commit segfaults the PK audit harness — see goal watermark). **NEXT: RK-BB-2** keystone lazy `Seq` box (gather/take→`BB_SUSPEND`+`BB_EVERY` PUMP, reuse `bb_upto.cpp`). Then RK-BB-3 map/grep→`BB_ITERATE`, RK-BB-4 junctions→`BB_ALTERNATE`. Scope (Lon): lazy map/grep IN, junctions IN, regex/grammar SPLIT→GOAL-RAKU-PAT-BB, sort/try/scalar STAY SM. |
| **Universal Generator IR** | `GOAL-LOWER-REDESIGN.md` | one4all+.github | **LR-S2** — delete bb_node_t path; prereq: fix pattern-var deref bugs or implement IR_PAT_DEREF. |
| **Style: 200-col emitter reformat** | `GOAL-STYLE-200COL.md` | one4all+.github | **S200-4** — `emit_bb.c`. |
| **⚡ PST: Parent (HQ)** | `GOAL-PARSER-PURE-SYNTAX-TREE.md` | one4all+corpus+.github | Phase 1 C ✅. Phase 2 SCRIP ✅ all six. NEXT: Stage 2 PST-LR-0 bulk rename SM_*→IR_SM_*, IR_*→IR_BB_*. |
| **⚡ PST: SNOBOL4** | `GOAL-PST-SNOBOL4.md` | one4all+corpus+.github | Phase 2 PST-SN4-SC ✅ COMPLETE (2026-05-19, corpus `68aa237`). ⚠ SN4-SC-6 smoke blocked by EC-3* --interp regression. |
| **⚡ PST: Snocone** | `GOAL-PST-SNOCONE.md` | one4all+corpus+.github | Phase 2 SC-SC ✅. **MIRROR-GAP-SC-SC-5**: XDSAR in bb_build_brokered. one4all `3824560c`, corpus `b10933c`. |
| **⚡ PST: Icon** | `GOAL-PST-ICON.md` | one4all+corpus+.github | ✅ COMPLETE 2026-05-19. corpus `2713cb7`. |
| **⚡ PST: Raku** | `GOAL-PST-RAKU.md` | one4all+corpus+.github | Phase 2 PRF-14 grammar ✅. **PRF-14-6 OPEN** — leaf-pushers misuse `shift`. ⚠ MIRROR-GAP blocked by &ALPHABET segfault. |
| **⚡ PST: Prolog** | `GOAL-PST-PROLOG.md` | one4all+corpus+.github | Phase 1 C ✅. Phase 2 PST-PL-SC ready (4–6 h): delete ~64 helper fns incl. all DCG expansion + slot allocation. |
| **⚡ PST: Rebus** | `GOAL-PST-REBUS.md` | one4all+corpus+.github | ✅ COMPLETE 2026-05-19. corpus `d1c08ff`. |
| **⚡ Parser-SC Transpile** | `GOAL-PARSER-SC-TRANSPILE.md` | one4all+corpus+.github | SCT-SN4-IMPLICIT-MATCH ✅ PASS=88/88. NEXT: **SCT-1f** (wire 2-way sync-monitor) or **SCT-BEAUTY-SC-PARSE** (awaiting Lon on shift() EVAL-scope bug). |
| **AST Rename** | `GOAL-AST-RENAME.md` | one4all+corpus+.github | AR-3 — prose "IR"→"AST" pass. |
| **IR_t Emitter Foundation** | `GOAL-IR-EMITTER-PREREQ.md` | one4all+.github | IEP-PKG ✅. IEP-5/6/7/9 BLOCKED on CHUNKS; IEP-8 can proceed. |
| **SN4 JVM Emitter** | `GOAL-SN4-JVM-EMIT.md` | one4all+.github | **SJ4-JVM-4** — method-split ✅. Beauty.sno halts at "Parse Error" (semantic). smoke 13/13. |
| **SN4 JS Emitter BB Rewrite** | `GOAL-SN4-JS-EMIT-BB-REWRITE.md` | one4all+.github | **SJ4-JS-BB1a** — emit Byrd-box factory functions. BB0 ✅. |
| **SN4 .NET Emitter** | `GOAL-SN4-NET-EMIT.md` | one4all+.github | **SN4-NET-5d** — SM_PAT_* wiring; ilasm nested-namespace crash. smoke_net 9/9, broker 23/49. |
| **SN4 WASM Emitter** | `GOAL-SN4-WASM-EMIT.md` | one4all+.github | **SN4-WASM-5g** — fix `emit_wasm.c:780` SM_EXEC_STMT args. PASS=23 FAIL=105. |
| **SCRIP Bootstrap** | `GOAL-SCRIP-BOOTSTRAP.md` | one4all | CB-0-corpus |
| **CSN FENCE Bug Fix** | `GOAL-CSN-FENCE-FIX.md` | csnobol4 | F-2 Step 3a |
| **IR: promote DEFINE** | `GOAL-IR-DEFINE-KIND.md` | one4all+corpus | awaiting Lon decision |
| Native Snocone — .NET/JVM/JS | `GOAL-NATIVE-SNOCONE-{DOTNET,JVM,JS}.md` | one4all | awaits PARSER-SC-6b |
| Corpus Layout | `GOAL-CORPUS-LAYOUT.md` | corpus+.github+one4all | design state |
| SNOBOL4 Frontend | `GOAL-LANG-SNOBOL4.md` | one4all | SN-33c — 25 residual fails |
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

Every frontend (SNOBOL4, Icon, Prolog, Snocone, Rebus, Scrip) produces the shared AST. SM-LOWER compiles the AST to SM_Program (flat array of stack machine instructions). INTERP executes SM_Program. EMITTER walks SM_Program and emits native code (x86, JVM, .NET, JS, WASM).

---

## Session trigger phrases

| Lon says | Meaning |
|----------|---------|
| "here we go" | Session starting — proceed with session start protocol above |
| "perform hand off" | End of session — update goal state, commit, push per RULES.md |
| "perform emergency hand off" | Same, but note breakage explicitly in commit message |
| "grand master reorg" | HQ system work — improving the HQ itself |
