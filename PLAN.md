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
| **ICON-BB** | `GOAL-ICON-BB.md` | LFJ-0..LFJ-14 ✅. **LFJ-15 ✅ (partial — three of four items)** (`cde72b79`, Opus 4.7, 2026-05-27): delete legacy `lower_icn.c` ✅ (1616 lines: 49 `legacy_<KIND>` fns, `lower_kind_table[]` + init, table-lookup dispatcher); delete `lower_kind_table` indirection ✅ — `lower_icn_expr_node` now a plain `switch (e->t)` calling `new_<KIND>` directly; rename `lower_icn_new.{c,h}` → `lower_icn.{c,h}` ✅. Helpers + threading machinery moved into consolidated file (`icn_binop_apply`, `icn_fold_signed_lit`, `lower_icn_upto`, `lower_icn_proc_gen`, `lower_icn_proc_body`, `lower_icn_expr_top`, `lower_icn_expr_threaded`/`_b`, `icn_leaf`, `icn_tree_is_leaf`, `icn_kind_is_resumable`, `icn_kind_owns_omega_operand`). Dead `lower_icn_new_NoOp` removed. Makefile updated. Net **-1107 lines** (2858 → 1767, single file). **DEFERRED**: "Delete all `_threaded_b` AG-PURE intercept branches" — Families 3/5/6/7/8.1/8.2 still reshape new functions' legacy-shape output into AG-pure chain-walker shape (scrubbed α/β, chained operands via γ, sval `"ag"`/`"ai"`/`"ar"`, ival=1 markers). Folding those INTO the new functions is **LFJ-15b** (new staircase row). Gates: 5/5 · 198 · 5/5 · 30/52, FACT RULE 0. **14 of 15 LFJ rungs complete** (93%). Next: **LFJ-15b** — AG-pure consolidation per-family with γ_in/ω_in threaded into new functions, retire intercept blocks from `_threaded_b`. |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | CAT-D-1..9b ✅, CAT-D-6 ✅, CAT-D-10 ✅, CAT-D-12-S1 ✅, CAT-D-12-S2 ✅. **CAT-B ✅** (Opus 4.7, 2026-05-27): compound-term unify closed. Single de-staticization of `emit_build_compound_term` in bb_builtin.cpp + `bb_unify.cpp` routes BB_PL_STRUCT operands through it (new `build_operand_term` dispatcher) + push/pop swapped to 16-aligned scratch frame so the walker's internal recursive `rt_pl_compound_build_n` calls satisfy SysV alignment. Zero new RT helpers, zero new linkage symbols, zero LOC delta in rt.c / bb_exec.c — pure refactor of existing infrastructure (walker reused from CAT-D-9b, alignment frame pattern reused from CAT-D-12 functor_term/arg_term/univ_term). `f(X,a)=f(b,Y)` binds X=b, Y=a correctly. Also unblocks CAT-D-12-S2's scalar functor/arg/=.. paths automatically (`T = foo(...)` now genuinely binds T to the compound). Gates: GATE-1 5/5, GATE-2 132/132, GATE-3 mode-2/mode-3 89/107 ea., GATE-4 4/4, **full mode-4 corpus 22/107 → 23/107 (+1: rung03_unify_unify)**. FACT RULE clean. Sibling smokes hold: icon 5/5, raku 5/5, snobol4 13/13, snocone 5/5, rebus 4/4, prolog 5/5. NEXT: **CAT-A-3** (BB_PL_CALL + BB_CHOICE β-resume — needs Lon directive on design; largest single-step unlock, est. +15-25 PASS by unblocking rung02/05/06/08 multi-clause retry). Then **CAT-C** (cons-list `member/2` segfault — compound root shared with CAT-B is now sound, remaining work is in bb_pl_call.cpp arg-passing for compound args with unbound tail variables; needs gdb on child binary). Then **CAT-D-11** (sort/2 + msort/2). |
| **Raku BB** | `GOAL-RAKU-BB.md` | RK-BB-1 ✅. RK-BB-2 ✅ (`d08237e0`). RK-BB-3.0+3d ✅ (`fcac4ab3`). RK-BB-3.0a ✅ (`ba481112`). RK-BB-3.0b ✅ (`7a60d30e`). RK-BB-3a CLOSED ✅ (`cc6c1a06`). RK-BB-3b/c scaffold ✅ (`42d2a367`). RK-BB-3b/c-binding-fix ✅ (`af0df613`). **RK-BB-4 substrate audit** (`4ee45eb7`, Opus 4.7, 2026-05-27): probe-based audit; goal text "REUSE bb_gen_alt.cpp/bb_alt.cpp" understated by ~7 substrate gaps. Verified: (1) raku.l has no KW_ANY/ALL/ONE/NONE tokens, no single-char `\|`/`&` infix; (2) TT_ALT is overloaded — Raku `\|\|` reuses SNOBOL4 pattern-alt path (works by coincidence); (3) bb_exec.c:1618-1620 BB_ALTERNATE mode-2 is a no-op stub; (4) bb_alternate.cpp mode-4 template does NOT EXIST; (5) bb_alt.cpp is a 37-line stub (α→γ, β→ω passthrough only); (6) bb_gen_alt.cpp is an 11-line empty-string stub; (7) Icon's TT_ALTERNATE lowers to BB_ALT not BB_ALTERNATE — BB_ALTERNATE is orphan. **REUSABLE substrate = BB_ALT, not BB_ALTERNATE** (but even BB_ALT mode-4 is a stub). Added `test/raku/rk_junctions.{raku,expected}` as target probe; fails today at lex with `unexpected char '\|'`. Gates HOLD: 14/14/15 of 33. Four Q's tabled for Lon (Q9 disentangle Raku `\|\|`/`&&` from SNOBOL4 pattern path; Q10 BB_ALT vs BB_ALTERNATE; Q11 substrate-first vs frontend-first; Q12 junction value rep). ZERO code changes. Recommended path: **path b (frontend-first eager)** — mirror RK-BB-3.0+3d's by-name dispatcher pattern; substrate becomes its own later rung that benefits Icon too. FACT RULE 0. NEXT: **RK-BB-4-frontend** pending Lon directive on Q9–Q12. |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | SBL-MODE3-REACTIVATE ✅. SBL-MODE-PURITY-1..5 ✅ (`e7e7bd63`). **SBL-ANY-2-CORRECTNESS ✅** (Opus 4.7, 2026-05-27, one4all `3eb09ba0`): traced actual dispatch path (SM_EXEC_STMT → bb_exec_pat → bb_exec_once → BB_PAT_DEFER → bb_exec_once → BB_PAT_ANY in C oracle; `bb_pat_any.cpp` template NOT exercised under --interp). Fixed two bugs in BB_PAT_DEFER recursive sub-pattern dispatch: (1) DESCR_t union clobber `sub_d.i = 0` after `sub_d.s = sub` nulled the string pointer because .s/.i share a union (bb_exec.c:2378 + rt.c:560); (2) architectural double-scan — inner pattern called bb_exec_pat which has its own kw_anchor scan loop, replaced with bb_exec_once. Gates: GATE-1 13/13, GATE-2 28, GATE-3 mode-4 175, **GATE-4 mode-2 238 (+20 from 218)**, rungs **M2=19 (+1: rung 053)**, M4=15. ANY/NOTANY/SPAN/BREAK via var-deref now byte-identical to SPITBOL across all three modes. NEXT: SBL-ANY-2 BINARY arm (scope narrowed — mode-3/mode-4 only since --interp now green via C oracle); investigate path that makes 042-048 mode-4 rungs pass despite stub BINARY arms (prereq for confident BINARY-arm fills). |
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
