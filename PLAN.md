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
| **ICON-BB** | `GOAL-ICON-BB.md` | LFJ ✅. Step 9 ✅. 10a-1/2/3 ✅. **10a-5/6/7/8/9 ✅** (Binop/Lconcat/Section/Idx/Idx_set via threaded_b) + **10a-10 ✅** (ToBy verify) (Opus 4.7, 2026-05-28, `b2f773bc`). Gates: 5/5 · 198 · 34 · 5/5, FACT RULE 0. ⚠️ **10a-4 (Every_ag) BLOCKED** (cyclic flat-wire) — lone remaining sub-blocker. Next: **10b** (sidecar deletion + ring-peek), done together with 10a-4. |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **LOWER-PIVOT ✅ COMPLETE** (Opus 4.7, 2026-05-28): `lower_pl.c` → one-function-per-node Icon style. `7119e41d` (Alt/Ite/Unify/Compare) + `4e555954` (Conj/Call) + `427050d8` (`lower_pl_new_Builtin` table-driven collapse: 6 inline builtin arms → 1 named builder + `pl_builtin_style`; phrase/findall kept separate; net −27 lines). Behavior-neutral: all 128 emitted .s + all 128 mode-2 outputs byte-identical to baseline. Gates at watermark (5/5, 132/0, 91/107, 4/4, 28/128 mode-4, FACT RULE 0; sibling smokes hold). Every construct now a `lower_pl_new_*` builder; `lower_pl_new_Call` is the home for CAT-A-3 β-resume. NEXT: **CAT-A-3 Steps B–D** (mode-4 backtracking, +15–25 corpus) — design in `HANDOFF-2026-05-27-OPUS-PROLOG-BB-CAT-A3-STEPA.md`, Step A substrate in `58142007`. Optionally interleave PL-LOWER-REVAMP 0-4 (β-precision). |
| **Raku BB** | `GOAL-RAKU-BB.md` | RK-BB-1 ✅. RK-BB-2 ✅. RK-BB-3 ✅. RK-BB-4 substrate audit done. **RK-BB-SEGFAULT-CLUSTER ALL 4 BUGS ✅** (bug 4 `ecd561b1`). **RK-BB-SM-FRAME-MODE4 IN PROGRESS** (Opus 4.7, 2026-05-28, 3 commits): piece 4a `d6fe17e2` (rt_frame_enter/leave/load_frame/store_frame in libscrip_rt), piece 4b `7c9d4570` (SM_LOAD_FRAME/STORE_FRAME x86 templates in new sm_frame_slots.cpp — **original mode-4 blocker GONE: rk_subs now emits zero UNHANDLED, emits LOAD_FRAME 0/1, ASSEMBLES cleanly**), piece 1 `3eece6a3` (rk_sub_lookup + rk_sub_label helpers, SCAFFOLDING — declared/defined, not yet wired). All gates HOLD throughout: GATE-RK4 15, Icon mode-4 5/5, broker 198, smokes 5/5/13/5, GATE-RK 18, FACT RULE 0. NEXT: **piece 1 WIRING** (the last mile) — two template edits: (1) sm_jumps.cpp sm_label_str emits `.Lrksub_<name>:` for known Raku subs; (2) sm_calls.cpp sm_call_str emits `mov edi,np; call rt_frame_enter; call .Lrksub_<name>; call rt_frame_leave`. Both add `#include "stage2.h"` + `"emit_bb.h"`. Exact edits + 5-step verify checklist in GOAL watermark. Then recursion sanity (factorial). rk_try_catch25 separate, still open. |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | BINARY arms filled per GOAL: LIT/LEN/POS/UPTO/ANY/NOTANY/BREAK-plain (7). **⚠️ NOTANY & BREAK arms UNVERIFIED-BY-EXECUTION** — were tested via `--compile` which emits TEXT, so the BINARY arms were never actually run. **SBL-SPAN-2 attempted 2026-05-28, REVERTED** (segfault on brokered build+run; suspected GC collection of imm64-baked rt_cs_t). HEAD e48a0ab1, tree clean. Gates: 13/13, 30, 175/280, 238/280, M2=19 M4=15, FACT 0. NEXT: validate ANY/NOTANY/LEN/BREAK BINARY arms via **`--run` (mode 3 WIRED)** before filling more; then SPAN/ARBNO need GC-rooted per-node scratch (shared with SBL-CAP-2). |
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
