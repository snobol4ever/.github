# PLAN.md — snobol4ever HQ

**Product:** SCRIP — SNOBOL4, Snocone, Rebus, Icon, Prolog. Ten times faster.
**Team:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet

---

## ⚡ THREE-MILESTONE AUTHORSHIP AGREEMENT

**Claude Sonnet is the third developer of snobol4ever — co-author of one4all / SCRIP.**

### Milestone 1 ✅ Session #57, 2026-04-28
beauty.sno byte-identical to SPITBOL oracle (md5 `abfd19a7a834484a96e824851caee159`).

### Milestone 2 ⏳
`scrip_stage2` compiled by `scrip_stage1` produces output identical to `scrip_stage1` compiling itself.

### Milestone 3 ⏳
All languages × all backends green.

---

## ⛔ SESSION START — every session, no exceptions

Lon names a goal. You:
1. Clone `.github`: `git clone https://TOKEN@github.com/snobol4ever/.github.git /home/claude/.github`
2. Read `PLAN.md`. Find goal in table below.
3. Read `RULES.md` in full.
4. **If PARSER-* or Snocone — read `SNOBOL4-SNOCONE-PRIMER.md` first.**
5. **If touches language corpus — read `CORPUS-LOCATIONS.md`.**
6. **If MODE3-EMIT or MODE4-EMIT — read `ARCH-x86.md` AND `ARCH-SCRIP.md` first.**
7. Open Goal file. Open that repo's REPO file.
8. Run Goal file's `## Session Setup` scripts.
9. Find first incomplete Step (`- [ ]`). Do it.

### Clone SPITBOL oracle
```bash
git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64
/home/claude/x64/bin/sbl -b file.sno
```

---

## Active Goals

| Goal | File | Step |
|------|------|------|
| **ICON-BB** | `GOAL-ICON-BB.md` | LFJ-0..LFJ-1b ✅. LFJ-1c ✅ (`5cd9003d`). **LFJ-2..LFJ-7 ✅** (`0b3b331d`, Opus 4.7, 2026-05-27). **LFJ-8 ✅** (`3d8aae8c`). **LFJ-9 ✅** (`80b9130e`): `ir_a_Compound`/`ir_a_ProcBody` documented non-emission. **LFJ-10 ✅** (`5c5bc669`): TT_FNC→Call, TT_FIELD→Field, TT_SECTION/PLUS/MINUS→Sectionop. **LFJ-11 ✅** (`8b6e513b`, Opus 4.7, 2026-05-27): TT_ALTERNATE→Alt, TT_SEQ→Conjunction, TT_NOT→Not. **LFJ-12 ✅** (`9b8fec0c`, Opus 4.7, 2026-05-27): TT_WHILE→While, TT_UNTIL→Until, TT_REPEAT→Repeat, TT_LIMIT→Limitation. **LFJ-13 ✅** (`c08187de`, Opus 4.7, 2026-05-27): TT_SCAN→Scan, TT_CASE→Case, TT_RETURN→Return, TT_SUSPEND→Suspend (Icon lang gate preserved), TT_LOOP_BREAK→Break, TT_LOOP_NEXT→Next. **LFJ-14 ✅** (`0540aace`, Opus 4.7, 2026-05-27): final transcription rung. lower_kind_table now contains ZERO references to lower_icn_legacy_* — every entry points into lower_icn_new.c. Named JCON procs: `ir_a_Initial`→TT_INITIAL, `ir_a_Unop`→{TT_MNS, TT_PLS, TT_SIZE, TT_NULL, TT_NONNULL, TT_RANDOM, TT_CSET_COMPL, TT_ITERATE, TT_MATCH_UNARY}, `ir_augmented_assignment`→TT_AUGOP. Non-emission stubs (no SCRIP TT_*, LFJ-9 pattern): `ir_a_Create`, `ir_a_Mutual`, `ir_a_Key`, `ir_a_Invocable`, `ir_a_Link`, `ir_a_RepAlt`, `ir_a_CoexpList`. Plus 12 auxiliary new functions for SCRIP-only AST kinds folded into other JCON procs (ir_a_Binop/Ident/Compound/Record/ListConstructor/Fail): new_Var, new_Keyword, new_Assign, new_Swap, new_SeqExpr, new_Decl, new_Idx, new_Identical, new_ProcFail, new_CsetBinop, new_Record, new_Makelist — each 1:1 with its lower_icn_legacy_* counterpart per LFJ-1a extraction encoding. Gates: 5/5 · 198 · 5/5 · 28/51. FACT RULE clean. **13 of 15 LFJ rungs complete** (87%). Next: **LFJ-15** — delete lower_icn.c, delete _threaded_b AG-PURE intercept branches, delete lower_kind_table indirection, rename lower_icn_new.c → lower_icn.c. One file, one traversal. |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | CAT-D-1..9b ✅, CAT-D-6 ✅, CAT-D-10 ✅, CAT-D-12-S1 ✅. **CAT-D-12-S2 ✅** (`62e45b49`, Opus 4.7, 2026-05-27): mode-4 templates for functor/3 + arg/3 + =../2 in bb_builtin.cpp (+197 lines) + 8 effect helpers in bb_exec.c (+144 lines: functor_common/arg_common/univ_common statics + rt_pl_functor/_term, rt_pl_arg/_term, rt_pl_univ/_term/_term_list/_term_term). Pattern mirrors CAT-D-6 + CAT-D-10 two-path (scalar 9-arg via flat (k,i,s) triples; compound literal via emit_build_compound_term post-order walker → _term variants). Trail-marked, deterministic, return 1=γ/0=ω; template owns only test/je/jmp triplet. **rung09_builtins_builtins mode-4 byte-exact match to oracle**: `foo 2\nb\n[foo,a,b]\nyes\nyes\nno\nno`. PL_BUILTIN unknown-stubs in r09 emit: 3→0. FACT RULE clean. Gates: GATE-1 5/5, GATE-2 132/132, GATE-3 mode-2/mode-3 89/107 ea., GATE-4 4/4, **full mode-4 corpus 21/89 → 22/89 (+1)**. Other lang smokes hold (icon/raku/snocone/rebus/snobol4 all unchanged). Investigated and documented: scalar paths of new helpers dead-code in current corpus because pre-existing **CAT-B** bug (rt_pl_node_to_term has no BB_PL_STRUCT case in src/runtime/rt/rt.c:965-980; falls through `default: term_new_int(ival)`) breaks compound-via-var binding upstream at `T = foo(...)` unify; once CAT-B lands, scalar helpers light up free. NEXT: **CAT-B** (compound-term unify — small bb_unify.cpp surface, est. +10-20 mode-4 PASS via rung02/03/05/06 cascade). Then CAT-A-3 (BB_PL_CALL + BB_CHOICE β-resume — needs Lon directive on design), CAT-D-11 (sort/2 + msort/2). |
| **Raku BB** | `GOAL-RAKU-BB.md` | RK-BB-1 ✅. RK-BB-2 ✅ (`d08237e0`). RK-BB-3.0+3d ✅ (`fcac4ab3`). RK-BB-3.0a ✅ (`ba481112`). RK-BB-3.0b ✅ (`7a60d30e`). RK-BB-3a CLOSED ✅ (`cc6c1a06`). **RK-BB-3b/c WIP** (`42d2a367`, 2026-05-27, Opus 4.7) — map/grep eager-drain lowering scaffold authored in `lower.c` (+117). New helper `lower_raku_map_or_grep(t, is_grep)` desugars `map { body } @src` / `grep { pred } @src` onto RK-BB-3a's BB_ITERATE + RK-BB-3.0b's push by-name dispatch. Pure lowering transform; ZERO new BB kinds, ZERO new runtime helpers. Scaffold structurally works (BB_ITERATE fires, push accumulates, sort segments green) but `$_` reads as 0 in body/predicate — reproduces in mode-2 --interp, so bug is in SM emission, NOT mode-4-specific codegen. All gates HOLD (12/12/13, smokes, broker 198, FACT RULE 0). NEXT: **RK-BB-3b/c-binding-fix** — three hypotheses listed in handoff (implicit `$_` scope registration; stack-order interaction; closure tree aliasing). Recommended diagnostic: hand-desugar probe + `--sm-dump` diff against the BB-generated stream + slot-printf in emit_var_store/load. |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | SBL-MODE3-REACTIVATE ✅. **SBL-MODE-PURITY-1..5 ✅** (Opus 4.7, continued 13B, one4all `e7e7bd63`): eliminated all silent fallbacks in SNOBOL4 pattern dispatch. New helper `bb_build_pure_mode(BB_t *nd)` dispatches on g_bb_mode (LIVE→flat, BROKERED→brokered) with NO inter-mode fallback. All 7 eps-rescue sites removed; on NULL build, root.fn=NULL → bb_broker returns 0 → exec_stmt honest fail. Gates hold at watermark: GATE-1 13/13, GATE-2 28, GATE-3 175/280, GATE-4 218/280, M2=18 M4=15. **SBL-ANY-2 attempted, NOT COMMITTED** (continued 13C): wrote 104-byte BINARY arm GAS-verified, but probes proved `bb_pat_any` and `exec_stmt` are NEVER called for `S PAT . M` under `--interp`. Pre-existing mode-independent bug: `match=x` instead of oracle `match=a` for `ANY('cab')` over `'xyzabcdef'`. Reverted to clean watermark. NEXT: **SBL-ANY-2-DISPATCH-TRACE** — instrument `sm_interp.c:582 case SM_EXEC_STMT` to map the actual dispatch path; only after that is safe to fill BINARY arms (do not commit code we cannot prove ran). |
| **PP-PURE** | `GOAL-PURE-TEMPLATES.md` | PP-PURE-2 — xa_bb_ptr_slot side-effect fix + SM locals. |
| **CHUNKS** | `GOAL-CHUNKS.md` | CH-17g-irrun-execution. |
| **Mode-4 SN4+Snocone** | `GOAL-MODE4-SN4-SNOCONE.md` | M4SN-5 or M4SN-6. 250/280 ✅. |
| **PST Parent** | `GOAL-PARSER-PURE-SYNTAX-TREE.md` | Stage 2 PST-LR-0 bulk rename. |
| **PST SNOBOL4** | `GOAL-PST-SNOBOL4.md` | SN4-SC-6 smoke blocked by EC-3* regression. |
| **PST Snocone** | `GOAL-PST-SNOCONE.md` | MIRROR-GAP-SC-SC-5: XDSAR in bb_build_brokered. |
| **PST Raku** | `GOAL-PST-RAKU.md` | PRF-14-6 OPEN — leaf-pushers misuse shift. |
| **SN4 JVM** | `GOAL-SN4-JVM-EMIT.md` | SJ4-JVM-4 done. Beauty.sno halts at Parse Error. smoke 13/13. |
| **SN4 .NET** | `GOAL-SN4-NET-EMIT.md` | SN4-NET-5d — SM_PAT_* wiring. smoke_net 9/9, broker 23/49. |
| **IR Emitter** | `GOAL-IR-EMITTER-PREREQ.md` | IEP-8 can proceed; IEP-5/6/7/9 blocked on CHUNKS. |
| **Universal Gen IR** | `GOAL-LOWER-REDESIGN.md` | LR-S2 — delete bb_node_t path. |
| **Parser-SC Transpile** | `GOAL-PARSER-SC-TRANSPILE.md` | SCT-1f or SCT-BEAUTY-SC-PARSE. |

---

## Repos

| Repo | File |
|------|------|
| one4all | `REPO-one4all.md` |
| corpus | `REPO-corpus.md` |
| snobol4dotnet | `REPO-snobol4dotnet.md` |
| snobol4jvm | `REPO-snobol4jvm.md` |

---

## Architecture

Every frontend (SNOBOL4, Icon, Prolog, Snocone, Rebus, Scrip) produces the shared AST. SM-LOWER compiles AST to SM_Program. INTERP executes SM_Program. EMITTER walks SM_Program and emits native code (x86, JVM, .NET, JS, WASM).

---

## Session trigger phrases

| Lon says | Meaning |
|----------|---------| 
| "here we go" | Session starting |
| "perform hand off" | End of session — update goal state, commit, push per RULES.md |
| "perform emergency hand off" | Same, note breakage |
| "grand master reorg" | HQ system work |
