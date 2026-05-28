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
| **ICON-BB** | `GOAL-ICON-BB.md` | LFJ ✅. Step 9 ✅. 10a-1/2/3 ✅. **10a-5/6/7/8 ✅** (Binop/Lconcat/Section/Idx via threaded_b) + **10a-10 ✅** (ToBy verify) (Opus 4.7, 2026-05-28, `6f41527f`). Gates: 5/5 · 198 · 34 · 5/5, FACT RULE 0. ⚠️ **10a-4 (Every_ag) BLOCKED** (cyclic flat-wire); **10a-9 (Idx_set_ag) needs new `_ag` variant**. Next: **10a-9** then **10b** (sidecar deletion + ring-peek). |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **LOWER-PIVOT** ⏳ CURRENT (Opus 4.7, 2026-05-28): `lower_pl.c` → one-function-per-node Icon style. Done `7119e41d` (Alt/Ite/Unify/Compare) + `4e555954` (Conj/Call) — behavior-neutral, gates at watermark (5/5, 132/0, 91/107, 4/4, 28/107 mode-4, FACT RULE 0). `lower_pl_new_Call` now the home for CAT-A-3 β-resume. NEXT: `lower_pl_new_Builtin` (table-driven builtin collapse, keep phrase/findall separate; detail-sensitive — diff per-family outputs, fresh context). Then CAT-A-3 Steps B–D. CAT-A-3 Step A substrate already in `58142007`. |
| **Raku BB** | `GOAL-RAKU-BB.md` | RK-BB-1 ✅. RK-BB-2 ✅. RK-BB-3 ✅ (3.0/3d/3.0a/3.0b/3a/3b/c). RK-BB-4 substrate audit done (pending Lon Q9–Q12). **RK-BB-SEGFAULT-CLUSTER ALL 4 BUGS ✅** (Opus 4.7, 2026-05-27): bug 4 closed in `ecd561b1` — one4all `src/lower/lower.c` `lower_return` (+2 -0): added LANG_RAKU branch that emits `lower_expr` then `SM_RETURN` with NO VOID_POP. Gates: GATE-RK mode-2 **16→18** (+rk_subs, +rk_combinator), GATE-RK4 15 HOLD, smokes 5/5/5/13 HOLD, broker Icon 198 HOLD, FACT RULE 0. NEXT: **RK-BB-SM-FRAME-MODE4** — mode-4 SM_LOAD_FRAME / SM_STORE_FRAME templates + libscrip_rt frame stack + user-sub direct `call .L<pc>` dispatch in sm_calls.cpp X86 arm. Architecture analyzed and documented in goal file (4-piece design: callsite dispatch, frame enter, frame leave, slot load/store templates + new rt_frame.c). Estimated 6-10hr; defer to next session. rk_try_catch25 also still open (separate try/CATCH issue). |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | SBL-ANY-2 ✅, SBL-NOTANY-2 ✅. **SBL-BREAK-2 ✅** (Opus 4.7, 2026-05-28): plain-BREAK BINARY arm filled (178 bytes; was 2-jump stub aborting mode-4). Per-node loop count via `bb_cs_zeta` rt_cs_t.delta @off 8 — established shared persistent-storage pattern for SPAN/ARBNO/CAP-2. Validated BREAK('c')/'abXcde'→'abX'. Gates: 13/13, 30, 175/280, 238/280, M2=19 M4=15, FACT RULE 0. NEXT: **SBL-SPAN-2** (near-identical to BREAK, invert strchr test `jz done`); then **SBL-ARBNO-3** (generator, study TEXT β); then **SBL-CAP-2** (uses same zeta-slot for saved_Δ + needs bb_child_fn). |
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
