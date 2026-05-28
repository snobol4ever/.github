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
| **ICON-BB** | `GOAL-ICON-BB.md` | LFJ-0..LFJ-1b ✅. LFJ-1c ✅ (`5cd9003d`). **LFJ-2..LFJ-7 ✅** (`0b3b331d`, Opus 4.7, 2026-05-27). **LFJ-8 ✅** (`3d8aae8c`). **LFJ-9 ✅** (`80b9130e`): `ir_a_Compound`/`ir_a_ProcBody` documented non-emission. **LFJ-10 ✅** (`5c5bc669`): TT_FNC→Call, TT_FIELD→Field, TT_SECTION/PLUS/MINUS→Sectionop. **LFJ-11 ✅** (`8b6e513b`, Opus 4.7, 2026-05-27): TT_ALTERNATE→Alt, TT_SEQ→Conjunction, TT_NOT→Not. **LFJ-12 ✅** (`9b8fec0c`, Opus 4.7, 2026-05-27): TT_WHILE→While, TT_UNTIL→Until, TT_REPEAT→Repeat, TT_LIMIT→Limitation. **LFJ-13 ✅** (`c08187de`, Opus 4.7, 2026-05-27): TT_SCAN→Scan, TT_CASE→Case, TT_RETURN→Return, TT_SUSPEND→Suspend (Icon lang gate preserved), TT_LOOP_BREAK→Break, TT_LOOP_NEXT→Next. Gates: 5/5 · 198 · 5/5 · 28/51. FACT RULE clean. **12 of 15 LFJ rungs complete** (80%). Next: **LFJ-14** — transcribe `ir_a_Create`, `ir_a_Mutual`, `ir_a_Key`, `ir_a_Invocable`, `ir_a_Link`, `ir_a_Initial`, `ir_a_RepAlt`, `ir_a_CoexpList`, `ir_a_Unop`, `ir_augmented_assignment`. |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | CAT-D-1..9b ✅, CAT-D-6 ✅, CAT-D-10 ✅. **CAT-D-12-S1 ✅** (`689b693a`, Opus 4.7, 2026-05-27): Prolog mode-3 architecture restored — V-5 fake fork/exec pipeline (`scrip_run_via_x86_pipeline` + `scrip_locate_rt_lib` + `scrip_spawn_wait`) DELETED from scrip.c; Prolog `--run` now folds into the same `sm_run_with_recovery(sm, sm_interp_run)` path SNOBOL4 uses, with `bb_live=1` forced so `bb_build_flat` is the BB sink under `--run`. **GATE-2 31/132 → 132/132 PASS, 0 FAIL** (three-mode agreement is now total). GATE-1 5/5, GATE-3 mode-2 89/107, GATE-3 mode-3 89/107 (identical fail set — `comm` proves 18/18/0), GATE-4 4/4 hold. rung09 mode-3 (functor/arg/=..) turned green by byproduct — mode-2 BB_BUILTIN arms already correct, just never reached under fake pipeline. NEXT: CAT-D-12-S2 (mode-4 templates for functor/3 + arg/3 + =../2 in bb_builtin.cpp + RT helpers rt_pl_functor / rt_pl_arg / rt_pl_univ + _term variants in bb_exec.c — mirrors CAT-D-10 pattern; unblocks rung09 mode-4). Then CAT-A-3 (BB_PL_CALL + BB_CHOICE β-resume — needs Lon directive on design), CAT-D-11 (sort/2 + msort/2). |
| **Raku BB** | `GOAL-RAKU-BB.md` | RK-BB-1 ✅. RK-BB-2 ✅ (`d08237e0`). RK-BB-3.0+3d ✅ (`fcac4ab3`). RK-BB-3.0a ✅ (`ba481112`). RK-BB-3.0b ✅ (`7a60d30e`). RK-BB-3a partial ✅ (`706e2828`). **RK-BB-3a CLOSED ✅** (`cc6c1a06`, 2026-05-27, Opus 4.7) — mode-4 `for @arr -> $v` now byte-exact. Template-only fix in `bb_iterate.cpp` (+58/-4): (a) slen-fallback after NV_GET_fn — STRVAL() hard-codes .slen=0 codebase-wide, so call `strlen@PLT` inline when slen==0; (b) NUL-terminated segment copy via `GC_malloc@PLT` + inline `rep movsb` + NUL-terminate before `rt_push_str`, because downstream `fputs` is NUL-bounded and mid-string ptrs leak the array tail. 100% template emission; no new rt_* helpers. GATE-RK4 11→13 (+2: rk_for_array_simple, rk_for_array). All other gates HOLD (mode-2/-3 12/31, smokes, broker 198, FACT RULE 0). NEXT: **RK-BB-3b/c** (lazy map/grep as Seq consumers — substrate now complete; eager-drain materialization per Open Q3 recommendation). Latent: segfault cluster rk_subs/rk_interp/rk_try_catch25 (separate concern); Open Q5 union-clobber proper fix (deferred). |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | SBL-MODE3-REACTIVATE ✅. **SBL-MODE-PURITY-1..5 ✅** (Opus 4.7, continued 13B, one4all `e7e7bd63`): eliminated all silent fallbacks in SNOBOL4 pattern dispatch. New helper `bb_build_pure_mode(BB_t *nd)` in emit_bb.c — dispatches on g_bb_mode (LIVE→flat, BROKERED→brokered) with NO inter-mode fallback. All 7 eps-rescue sites in stmt_exec.c removed; on builder NULL, `root.fn=NULL` → `bb_broker` returns 0 cleanly → exec_stmt returns 0 honestly. emit_bb.c:847 unconditional brokered fallback removed (per-kind ARBNO/CALLOUT split retained — reflects child-consumer ABI, not mode dispatch). Lon's directive: "we want this change to break everything so we can see it" — breakage did NOT materialize: every formerly-protected code path was genuinely unreachable under current corpus. Dead leaks. Removing them exposes nothing new but cleans the signal: from now every passing test passes through the mode it claims. Gates all hold at watermark: GATE-1 13/13, GATE-2 28, GATE-3 175/280, GATE-4 218/280, M2=18 M4=15. Hold lifted: SBL-ANY-2 / SBL-NOTANY-2 / SBL-BREAK-2 / SBL-SPAN-2 / SBL-ARBNO-3 / SBL-CAP-2 can now proceed safely. NEXT: SBL-ANY-2 (fill bb_pat_any.cpp BINARY arm — TEXT arm is spec; reference bb_upto.cpp BINARY + bb_pat_pos.cpp/bb_pat_len.cpp rel32-fixup pattern). |
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
