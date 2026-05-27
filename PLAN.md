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
| **ICON-BB** | `GOAL-ICON-BB.md` | LFJ-0..LFJ-1a-v ✅. **LFJ-1a-vi** ✅ (`0ed7ace3`: TT_SIZE, TT_IDX, TT_SECTION/SECTION_PLUS/SECTION_MINUS (3-label shared), TT_CASE, TT_FIELD, TT_RECORD, TT_MAKELIST, TT_ITERATE → 8 lower_icn_legacy_<KIND>* static fns; ZERO logic change. **Mega-switch is now a pure dispatcher** — every arm is a one-line `return lower_icn_legacy_<KIND>(cfg, e);`). Next: **LFJ-1b** — introduce `lower_kind_table[TT_MAX]` of `BB_t* (*)(BB_graph_t*, tree_t*)`. `lower_kind_table_init()` populates every slot with the matching `lower_icn_legacy_<KIND>`. Dispatcher reads the table instead of switching directly. Gates: smoke 5/5, broker 24, rungs 198, smoke_prolog 5/5. |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | CAT-D-1 ✅ (Opus 4.7, one4all `95f73bad`, atom_length/upcase_atom/downcase_atom in `bb_builtin.cpp` + 3 rt helpers). GATE-2 36/96 → 38/94 (+2). NEXT: CAT-A-3 — BB_PL_CALL + BB_CHOICE β-resume (both stubs `β: jmp ω`); needs Lon directive on design. Or continue CAT-D (string_length/2, succ/2, type tests). |
| **Raku BB** | `GOAL-RAKU-BB.md` | RK-BB-1 ✅. RK-BB-2 ✅ (`d08237e0`: rk_gather PASSES mode-4 — 9/30). RK-BB-3 substrate audit done (2026-05-27, Opus 4.7, one4all `d4cbefaf`) — 6 gaps verified, scope decomposed into 3a/3b/3c/3d; gating on Lon Q6/Q7/Q8 (polymorphic BB_ITERATE, FIELD_GET_fn in template, eager vs lazy `my @x = map`). New probe test/raku/rk_for_array_simple.raku added (mode-4 9/31, mode-2 8/31). |
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
