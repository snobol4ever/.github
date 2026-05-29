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
| **ICON-BB** | `GOAL-ICON-BB.md` | **GEN-BUILTIN ✅** (Opus 4.7, 2026-05-28, one4all `8cc487e9`): Icon `find()`/`key()` were lowered via flat `SM_CALL_FN`, so they returned only first value when used as generators. Routed shape-2 TT_FNC dispatch through `lower_icn_expr_top` for fn∈{find,key} → SM_BB_INVOKE. Recovered `rung08_strbuiltins_find_gen`. `key(t)` standalone generates 3 keys; `rung23_table_table_key` still FAILs because `t[key(t)]` triggers a separate stack-underflow (generator-in-subscript family). **Earlier this session: BANG-EXPR** (`381df169`) — `lower_iterate` for LANG_ICN was the same anti-pattern: build bbg, BB_free, lower_unhandled. Recovered 10 rungs (rung22 bang_list/put_bang, rung31 sort/sortf, rung11/13/15 each one). **LIMIT-EXPR** (`471ac1c9`) — `lower_limit` was lower_unhandled stub; mirrored `lower_to`. Recovered all 5 rung14 + rung30_misc_seq. Also added rung37 to runner glob (was silently skipped, 14 tests). **PARAM-SHADOW** (`4d5fe69e`) — applied last session's diagnosis: `emit_var_load` was checking LANG_ICN proc-as-value before `scope_get`, so parameters didn't shadow proc names. Reordered (matches `emit_var_store`). Recovered rung32_basic_strret. **rung36 split** (corpus `e89681b` + one4all `64c7530c`): 75-test JCON pool split into 8 intent categories via runner-side sidecar. No file renames. Per-category subtotals emitted by `test_icon_all_rungs.sh`. Gates: smoke_icon 5/5 · smoke_prolog 5/5 · broker 36 (+1) · rungs 170 → **194** / FAIL 53 / XFAIL 36 / TOTAL 269 → **283** (+14 from rung37 glob) · FACT 0. **rung36 by category snapshot:** control 0/4/9, gens 0/6/6, io 0/3/3, numbers 0/3/5, reflection 1/4/4, scan 0/6/3 (best signal/noise), strings 5/4/2 (moving), structures 0/3/4. **NEXT options:** rung36_scan cluster · every-augop-gen stack underflow · generator-in-subscript stack underflow · block-body BREAK/NEXT on new BANG path · rung37 newly-visible tactical fails (8). |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **SWI-2-fold + SWI-2b ✅** (Opus 4.7, 2026-05-28, one4all `43933846` · corpus `c4e0229`): GATE-SWI **0/57 → 53/57 (92%)** mode-2 and mode-3. Frontend fold in `prolog_lower.c` rewrites callable directives with args (`begin_tests`/`end_tests`/`dynamic`/`use_module`/`module`/`nb_setval` etc.) into anonymous helper predicate `pj_dir_N/0` + `:- initialization(pj_dir_N).` — args flow through normal BB_PL_CALL which materializes them correctly, instead of through SM_BB_PL_INVOKE which dropped them. Paired plunit.pl rewrite: suite registry uses `nb_setval(pj_suites, [Suite-Opts|Old])` instead of runtime `assertz(pj_suite/2)` (PL-RT-ASSERTZ is a separate open task). `scripts/test_prolog_swi_suite.sh` WRAP gets explicit `:- initialization(main).` (plunit.pl's own `pj_suites_init` initialization sets `g_pl_initialization_seen=1`, suppressing PJ-AGW-MAIN0 auto-main). Other gates byte-identical: G1=5/5, G2=132/0, G3 m2/m3=104/107, FACT=0. **NEXT options:** (a) chase remaining 4/57 SWI failures; (b) PL-RT-ASSERTZ; (c) WAM-CP-13 (longjmp-free catch + mode-4 emit); (d) WAM-CP-6 LCO. [Prior: **SWI-2-pre ✅** (`cda40a70`) findall determinism guard; **SWI-1a ✅** (`86abe166`) directive whitelist; **WAM-CP-1/2/3/4/5 ✅. WAM-CP-9/10 partial 🟡** (`5427e12e`).] |
| **Raku BB** | `GOAL-RAKU-BB.md` | **RK-CLASS partial 🟡** (Claude Sonnet 4.6, 2026-05-28, one4all `77e84268`): `lower_field` fix: Raku `$p.x` → `TT_FIELD` has name in `t->v.sval` not `c[1]`; `ICN_FIELD_NAME` returned NULL → empty string. Fixed fallback. 3 blockers remain for full CLASS pass: (1) method `TT_SUB_DECL`s inside `TT_CLASS_DECL` not registered in `proc_table` → bodies emitted inline in main → SIGSEGV; (2) `raku_new`/`raku_mcall` missing from `raku_builtins_byname.c`; (3) mode-4 method dispatch needs static resolution in `TT_METHCALL` lowering via `g_raku_meth_table` or Lon directive. See `HANDOFF-2026-05-28-SONNET-RAKU-BB-CLASS.md`. GATE-RK4 25/33 HOLD. 8 FAILs: REGEX/NFA (6, deferred), JUNCTIONS (1, blocked Q9-Q12), CLASS (1). |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | **SBL-EP-BINARY restore ✅** (Opus 4.7, 2026-05-28, one4all `df8e6126`): five combinator templates (`bb_pat_alt`, `bb_pat_cat`, `bb_pl_seq`, `bb_pl_ite`, `bb_succeed`) restored to FACT-correct inline EP-walk shape after `88bacd2a` stripped them. `_str(BB_t*, bb_bin_t&)` signature back; loop walks `g_emit.xa_bb_emit_pair_*[]` emitting bytes AND populating `bin.sites/labels/is_def` inline (duplication is the point per FACT RULE). `audit_m3_native_binary_arms.sh` **GATE FAIL → GATE OK**. All gates byte-identical: G1=13/13 default+native, G2=37, G3=175/280, G4=237/280, native=165/280, rungs M2=19 M4=15, sister smokes prolog/raku/icon 5/5 + rebus 4/4, FACT=0. **NEXT:** XNME/XFNME varname fix (latent bug discovered this session — `NAME_fn` always returns NAMEPTR because `NV_PTR_fn` always creates the cell; legacy `build_patnd` reads `var.s` which for NAMEPTR is the cell pointer reinterpreted, → garbage → `bb->sval=""` → bb_capture honest-skip → `lbl_β` never defined → abort. Fix: populate `p->STRVAL_fn` in `pat_assign_imm/cond` from NAMEVAL `.s` OR via new `NV_NAME_fn(cell)` reverse-lookup. Full sketch in HANDOFF-2026-05-28-OPUS-SBL-EP-BINARY-RESTORE.md). Then `patnd_to_bb_tree` + extend `patnd_needs_xlate` to combinator roots; validate 050/055 native. Beyond combinator flat-wire: SPAN/ARBNO/BREAKX/FENCE/POS/RPOS/TAB/RTAB cluster knockdown. |
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
