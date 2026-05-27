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
| **ICON-BB** | `GOAL-ICON-BB.md` | LFJ-0..LFJ-1a-iii ✅. **LFJ-1a-iv** ✅ (`320f1eea`: binop/logical cases extracted — TT_ADD..TT_NE+TT_CAT (13 labels shared), TT_LCONCAT, TT_LLT..TT_LNE (6 labels shared), TT_NOT, TT_ALTERNATE, TT_AUGOP → 6 lower_icn_legacy_<KIND>* static fns; ZERO logic change). Next: **LFJ-1a-v** — extract TT_GLOBAL/LOCAL/STATIC_DECL, TT_INITIAL, TT_RETURN, TT_SUSPEND, TT_IDENTICAL, TT_NONNULL, TT_NULL, TT_RANDOM, TT_MATCH_UNARY, TT_MNS, TT_PLS, TT_CSET_*. Gates: smoke 5/5, broker 24, rungs 198, smoke_prolog 5/5. |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | CAT-A-2 ✅ (Opus 4.7, one4all `471ab202`, `flat_drive_pl_seq` resumability-aware ω-wiring mirrors `lower_pl.c:191-197`). Gate-safe; GATE-2 unchanged at 36/96. NEXT: CAT-A-3 — BB_PL_CALL + BB_CHOICE β-resume (both stubs `β: jmp ω` at `bb_pl_call.cpp:97` and `bb_pl_choice.cpp:58`). Needs Lon directive on design (inline-on-demand vs resumable-call protocol). |
| **Raku BB** | `GOAL-RAKU-BB.md` | RK-BB-1 ✅. RK-BB-2 ✅ (`d08237e0`: rk_gather PASSES mode-4 — 9/30). Three-edit unblock in lower.c: (a) lower_hoist_gather_in_expr v.sval→v.ival=0 fix (Open Q5 union-clobber); (b) lower_stmt suppress body emission for __gather_*; (c) lower_expr_inner same defensive skip. lower_icn_proc_body now builds the BB graph; SM_BB_SWITCH(RK_GEN) routes through bb_seq + bb_suspend; native x86 emits 10\\n20\\n30\\ndone\\n byte-exact. NEXT: **RK-BB-3** lazy map/grep as Seq CONSUMERS (BB_ITERATE consumer + γ-predicate). |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | SBL-DCG-DEFER ✅ (`2b68dc44`): TT_VAR/TT_DEFER → BB_PAT_DEFER; mode-2 *PAT working, rung M2=15. Next: SBL-DCG-DEFER-M4 — root cause refined (cont 7, no commit): bug is in `case BB_PAT_DEFER`'s recursive `exec_stmt` call hitting `bb_build_brokered((PATND_t*)pat.p)` cast bug — affects BOTH m2 and m4. Designed fix: add `patnd_to_bb_graph()` translator in lower_pat_dcg.c (PATND→BB_graph_t, mapping table in goal-file); use it in `case BB_PAT_DEFER` DT_P branch + `exec_stmt` DT_P branch before falling back. ~100 LOC. Expected uplift ~15 broad-corpus + rung 056. |
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
