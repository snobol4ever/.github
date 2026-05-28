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
| **Prolog BB** | `GOAL-PROLOG-BB.md` | CAT-D-1..9b ✅, CAT-D-6 ✅, CAT-D-10 ✅, CAT-D-12-S1 ✅, CAT-D-12-S2 ✅, CAT-B ✅, CAT-C ✅, CAT-D-11 ✅. **CAT-RUNG07-1 ✅** (Opus 4.7, 2026-05-27): emit-time `bb_emit_byte: non-BINARY-mode reach (mode=0, b=0xe9)` abort on rung07_cut_cut fixed by adding `case BB_CUT: FILL(nd, lbl_γ, lbl_ω, lbl_β); break;` to `walk_bb_flat` in `emit_bb.c`. The cut was falling through `default:` which calls `emit_jmp_label`/`bb_emit_byte` (BINARY-mode helpers) during text-mode `--target=x86` emit. `bb_pl_cut.cpp` template already existed (AGW-9B-1 era) and `emit_core.c:542` already routed BB_CUT → `bb_pl_cut` via `codegen_bb_dispatch`; only the byte-free recursion driver's switch needed the case. One-line substantive change + 7-line block comment (+8 / 0). gdb backtrace nailed the chain: pl_emit_callee_block_body → flat_drive_pl_choice → flat_drive_pl_seq → walk_bb_flat default → emit_jmp_label → ef_b1 → bb_emit_byte (mode=0). **`bb_emit_byte` aborts in full mode-4 corpus 1 → 0.** Mode-4 corpus 28/107 → 28/107 (PASS set IDENTICAL — rung07 still FAILs with wrong output `yes\\nyes` instead of `yes\\nno`, which is **PJ-AGW-5-CUT-BARRIER** ledger item — full cut ω-rewiring for non-deterministic conditions). FACT-RULE-adjacent fix: the driver should never emit bytes; the template owns them. Gates: GATE-1 5/5, GATE-2 132/0, GATE-3 mode-2/3 89/107 ea., GATE-4 4/4, FACT RULE 0, sibling smokes hold. NEXT: **CAT-A-3** (BB_PL_CALL + BB_CHOICE β-resume — Lon directive needed; est. +15-25 PASS); **PJ-AGW-5** (cut-barrier semantic — rung07 `yes\\nyes` → `yes\\nno`). |
| **Raku BB** | `GOAL-RAKU-BB.md` | RK-BB-1 ✅. RK-BB-2 ✅ (`d08237e0`). RK-BB-3.0+3d ✅ (`fcac4ab3`). RK-BB-3.0a ✅ (`ba481112`). RK-BB-3.0b ✅ (`7a60d30e`). RK-BB-3a CLOSED ✅ (`cc6c1a06`). RK-BB-3b/c scaffold ✅ (`42d2a367`). RK-BB-3b/c-binding-fix ✅ (`af0df613`). RK-BB-4 substrate audit ✅ (`4ee45eb7`). **RK-BB-SEGFAULT-CLUSTER bug 1 ✅** (`0f3561c0`, Opus 4.7, 2026-05-27): three tests (rk_subs, rk_interp, rk_try_catch25) no longer SIGSEGV. Root cause: `polyglot_init` L123 `proc->v.sval && *proc->v.sval` is UNSAFE for TT_SUB_DECL because raku.y:340 sets v.sval via leaf_sval then CLOBBERS via v.ival=np (union write). When np > 0, the union slot reads as a small non-NULL pointer (0x1, 0x2, …) that PASSES the NULL check and segfaults at `*v.sval`. Tests with `sub main()` (np=0) lucked out. Fix: for TT_SUB_DECL, never trust v.sval — always use c[0]->v.sval (TT_VAR child where parser puts surviving name). One file +20/-3. Bugs 2+3 documented for next session: (2) **double body emission** — `lower_stmt` (L1987) emits Raku sub bodies inline at top level while `lower_proc_skeletons` (L2328) emits empty named skeletons (bnd-extraction only handles TT_PROC_DECL); for multi-sub programs every sub's body runs at startup, first `return` halts. (3) **no param→scope binding** for TT_SUB_DECL — `build_proc_scope` (L2287) only handles TT_PROC_DECL's `c[1]` TT_VLIST shape; Raku params live as flat TT_VAR children at `c[1..nparams]`, so scope is empty and body's $name reads from global. Two-edit patch each documented in watermark. Gates HOLD: 14/14/15 of 33; smokes 5/5/5/13; broker 198; FACT RULE 0. Memory-safety improvement, PASS counts unchanged. NEXT: **RK-BB-SEGFAULT-CLUSTER bug 2+3** — reapply experimental edits from this session + extend build_proc_scope, expected +3 each gate. |
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
