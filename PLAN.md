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
| **Prolog BB** | `GOAL-PROLOG-BB.md` | …rung25-TERM-STRING ✅. **CAT-A-3 Step A ✅** (Opus 4.7, 2026-05-27, one4all `58142007`): Lon chose **option (b) resumable-call protocol** (not (a) inline-on-demand) — preserves single-emit. Step A is the runtime substrate, behavior-neutral: reused existing `rt_pl_trail_mark`/`rt_pl_trail_unwind(int)` (mark-by-value, per-call-site, no LIFO aliasing) + added `pl_bb_env_install(Term**)` (non-freeing env install; resumable path keeps callee env alive across redo). Not yet called by any template → all gates hold at watermark (5/5, 132/0, 91/107, 4/4, 28/107 mode-4, FACT RULE 0). Full Steps B–D design in HANDOFF-2026-05-27-OPUS-PROLOG-BB-CAT-A3-STEPA.md: B = `bb_pl_choice.cpp` cursor-driven dispatcher; C = `bb_pl_call.cpp` + PL_ENTRY arm r12 resume-buffer ABI + `.Lplpred_<name>_<arity>_redo` entry; D = verify rung02/05/06 + corpus (est. +15–25). First-cut scope: single rightmost BB_CHOICE per callee (nested = follow-up); recommend always-r12. NEXT: **CAT-A-3 Steps B–D** (fresh context); PJ-AGW-5; rung18 plus/3; term_to_atom+term_string mode-4 emit. |
| **Raku BB** | `GOAL-RAKU-BB.md` | RK-BB-1 ✅. RK-BB-2 ✅. RK-BB-3 ✅ (3.0/3d/3.0a/3.0b/3a/3b/c). RK-BB-4 substrate audit done (pending Lon Q9–Q12). **RK-BB-SEGFAULT-CLUSTER ALL 4 BUGS ✅** (Opus 4.7, 2026-05-27): bug 4 closed in `ecd561b1` — one4all `src/lower/lower.c` `lower_return` (+2 -0): added LANG_RAKU branch that emits `lower_expr` then `SM_RETURN` with NO VOID_POP. Gates: GATE-RK mode-2 **16→18** (+rk_subs, +rk_combinator), GATE-RK4 15 HOLD, smokes 5/5/5/13 HOLD, broker Icon 198 HOLD, FACT RULE 0. NEXT: **RK-BB-SM-FRAME-MODE4** — mode-4 SM_LOAD_FRAME / SM_STORE_FRAME templates + libscrip_rt frame stack + user-sub direct `call .L<pc>` dispatch in sm_calls.cpp X86 arm. Architecture analyzed and documented in goal file (4-piece design: callsite dispatch, frame enter, frame leave, slot load/store templates + new rt_frame.c). Estimated 6-10hr; defer to next session. rk_try_catch25 also still open (separate try/CATCH issue). |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | SBL-ANY-2 ✅. **SBL-NOTANY-2 ✅** (Opus 4.7, 2026-05-28): `bb_pat_notany.cpp` BINARY arm filled (was 2-jump stub) — byte-identical to ANY BINARY except offset 70 `jne ω` vs `je ω`. Mode-4 compiled binary validated via brokered path. Gates: 13/13, 30, 175/280, 238/280, M2=19 M4=15, FACT RULE 0. NEXT: **SBL-SPAN-2 / SBL-BREAK-2 / SBL-ARBNO-3** (SPAN/ARBNO use `nd->counter` β-state — not pure ANY copy); then **SBL-CAP-2** (BINARY arm fill — design described in GOAL, needs `bb_child_fn` + per-node saved_Δ). |
| **PP-PURE** | `GOAL-PURE-TEMPLATES.md` | PP-PURE-2 — xa_bb_ptr_slot side-effect fix + SM locals. |
| **CHUNKS** | `GOAL-CHUNKS.md` | CH-17g-irrun-execution. |
| **Prolog LOWER revamp** | `GOAL-PROLOG-LOWER-REVAMP.md` | **Investigation ✅** (Opus 4.7, 2026-05-28): compared `lower_pl.c` against the canonical four-port reference `tran/irgen.icn` (Jcon, uploaded jcon-master) and against `lower_icn.c` (which faithfully mirrors irgen: 9 `_ag` threaded fns + 104 per-construct `_new_` dispatchers, 343 α/β/γ/ω refs). Found 3 structural gaps in Prolog LOWER: (1) monolithic dispatch — all goal lowering in 2 mega-functions (`lower_pl_goal` ~340 lines) vs irgen's 43 `ir_a_*` / one-per-node; (2) **β by heuristic** — conjunction computes resume as "nearest resumable predecessor" over a hardcoded {CALL,CHOICE,ALT} set (lines 196–206) instead of irgen's explicit per-node `resume` port; likely root structural cause of CAT-A-3 backtracking failures; (3) no `bounded`/determinacy flag (irgen threads one; we don't). Revamp staged 0–4: bounded-plumb → split monolith → explicit resume ports → BB_CHOICE = transliteration of `ir_a_Alt` MoveLabel/IndirectGoto (unifies with CAT-A-3 Step C resume-buffer). NEXT: Lon to confirm sequencing vs CAT-A-3 B–D; Stage 0 (bounded plumb, zero-behavior-change) is the safe first commit. |
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
