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
| **ICON-BB** | `GOAL-ICON-BB.md` | LFJ-0..LFJ-15b ✅ COMPLETE. Step 9 ✅ `1dfe9631` (AG-pure BB_LCONCAT/SECTION/IDX/IDX_SET). Gates: 5/5 · 198 · 5/5 · 30/52, FACT RULE 0. Next: **Step 10** — sidecar cleanup (bb_operand_aux_set/get from Icon Fam-1/2). |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | CAT-D-1..9b ✅, CAT-D-6 ✅, CAT-D-10 ✅, CAT-D-12-S1 ✅, CAT-D-12-S2 ✅, CAT-B ✅, CAT-C ✅, CAT-D-11 ✅, CAT-RUNG07-1 ✅. **rung25-TERM2ATOM-OPS ✅** (Opus 4.7, 2026-05-27, `b0093cd1`): operator-notation writer for `term_to_atom/2`. Ported the op-prec block from `pl_writeq_term` (lines 241-279) into `pl_write_to_file` — same logic but writes to FILE* and doesn't apply atom-quoting (write family, not writeq). Was `+(1,2)`, now `1+2`. GATE-3 mode-2 89/107 → **90/107** (+1: rung25_term_string_term_to_atom_arith). Mode-4 corpus 28/107 unchanged (term_to_atom mode-4 emit still TODO — falls through to `_` output; CAT-D-* candidate). Goal file pruned 1225 → 397 lines (`170b7ce2`). Gates: GATE-1 5/5, GATE-2 132/0, GATE-4 4/4, FACT RULE 0, all sibling smokes hold. NEXT: **CAT-A-3** (still Lon-directive blocked); **PJ-AGW-5** (rung07 cut-barrier semantic); **term_string/2** (rung25 still 1 open — not registered as builtin; needs lower_pl recognizer); **rung18 plus/3** (bidirectional arith). |
| **Raku BB** | `GOAL-RAKU-BB.md` | RK-BB-1 ✅. RK-BB-2 ✅. RK-BB-3 ✅ (3.0/3d/3.0a/3.0b/3a/3b/c). RK-BB-4 substrate audit done (pending Lon Q9–Q12). **RK-BB-SEGFAULT-CLUSTER bugs 2+3 ✅** (Opus 4.7, one4all `2a70abed`, 2026-05-27): TT_SUB_DECL structural fix in `src/lower/lower.c` (+56/-8). (a) `lower_stmt` inline emission gated on `_is_main`. (b) `lower_proc_skeletons` body extraction from `c[nparams+1..]` + `g_lang=LANG_RAKU` + skip main/__gather_. (c) `build_proc_scope` walks `c[1..v.ival]` as flat TT_VAR params. Gates: GATE-RK mode-2 **14→16** (+rk_interp, +rk_map_grep_sort24), GATE-RK4 15 HOLD, smokes 5/5/5/13 HOLD, broker Icon 198 HOLD, FACT RULE 0. NEXT: **bug 4 (lower_return)** — `lower_return` VOID_POPs Raku return value before SM_RETURN; one-line Raku branch needed (no VOID_POP). Then mode-4 SM_LOAD_FRAME template (currently emits `unhandled SM_LOAD_FRAME` directive — assembler error). |
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
