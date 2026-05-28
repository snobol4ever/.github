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
| **ICON-BB** | `GOAL-ICON-BB.md` | LFJ ✅. Steps 9, 10a-1/2/3/5/6/7/8/9/10 ✅. **Step 10b ✅ COMPLETE** (Opus 4.7, 2026-05-28): sidecar deletion + ring-peek migration. `8f887fa1` (BB_ASSIGN→ag_ring_peek, ival marker) + `359c5754` (BB_CALL deep-arg→ag_ring_peek, dval marker) + `4485d647` (icn_kind_owns_omega_operand removed). All 4 acceptance criteria met: bb_operand_aux_set==0, bb_exec_node(nd->[αβ])==0, icn_kind_owns_omega_operand==0, rungs 198. Gates: 5/5 · 198 · 34 · 5/5, FACT 0. operand_aux sidecar now has ZERO live callers (dead code; deletion deferred to HQ reorg as shared cross-lang infra). ⚠️ **10a-4 (Every_ag body-thread) still BLOCKED** but NOT a 10b criterion — purely architectural, body works via single-box path; defer. **Icon LOWER-stage AG-pure migration is functionally complete.** Next: MODE3 (--run) BB_CALL/EVERY parity, or take up another goal. |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **WAM-CP track** (Opus 4.7, 2026-05-28): GNU Prolog study DONE (`doc/GPROLOG-STUDY-2026-05-28-OPUS.md`) — confirmed CP-frame layout (gprolog reg `B`, negative-offset fields), in-place retry discipline, one-assignment cut, first-arg indexing blueprint. **WAM-CP-1 ✅ COMPLETE & gate-clean**: `pl_choice` record (+`saved_args`/`stamp` per study) + `g_pl_bfr` register + `pl_cp_push/current/pop/truncate` in `pl_runtime.c`; pure substrate, NO callers, all gates byte-identical. Gates: GATE-1 5/5, GATE-2 132/0, GATE-3 mode-2 91/107, GATE-4 4/4, full mode-4 28/128, FACT 0; siblings hold. **NEXT: WAM-CP-2** — route BB_CHOICE multi-clause through the CP stack (replace `bb_active_choice`/`nd->state` scan), mode-2 byte-identical. Then WAM-CP-3..8 (`;`, cut=truncate, mode-4 r12 promote, LCO, unify spec, indexing) + extended ladder WAM-CP-9..14 (committed-ITE/cut fix, catch/throw, deep arg-restore, determinism-elision, mode-4 parity, tagged-word bridge audit). Design principle recorded: BB graph replaces the WAM *environment* stack; CP ledger (`g_pl_bfr`) is the lean dynamic-only remainder, elided where determinism is provable. |
| **Raku BB** | `GOAL-RAKU-BB.md` | RK-BB-1/2/3 ✅. SEGFAULT-CLUSTER 4 ✅. SM-FRAME-MODE4 ✅. **RK-GIVEN-MODE4 ✅** (Opus 4.7, 2026-05-28, `5950356f`): Raku `given`/`when` rewritten from SM_PUMP_CASE+thunks (no x86 arm) to a straight if-chain over already-templated `SM_ACOMP`/`SM_LCOMP`/`JUMP_F` opcodes; per-site-unique topic temp for nesting; SM_PUMP_CASE retired (0 emit sites). rk_given == .expected. **GATE-RK4 18→19** (+rk_given). GATE-RK 18, smokes 5/5/5/13, Icon broker 198, Icon mode-4 5/5 all HOLD. FACT RULE 0. Remaining 14 FAILs triaged: regex/NFA (6, deferred to PAT-BB), hashes (2), junctions (1, blocked on Q9-Q12), I/O (2), exceptions (1), given18 (1, blocked on pre-existing for-over-pushed-array segfault). NEXT: hashes rung OR fix the array/for-loop segfault (unblocks given18 + array tests). |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | **⛔ SBL-M3-NATIVE (TOP PRIORITY, ROOT CAUSE)** — mode-3 must be PURE x86, NO interpreter, ALL languages (Lon, 2026-05-28). Traced: `scrip.c` mode_run runs the mode-2 C interpreter (`sm_interp_run` + `bb_exec_*`); native SM runner unbuilt. This is why 2 days of BINARY-arm filling was unobservable. 5-step engine build in GOAL § SBL-M3-NATIVE. Prior SBL-BREAK-VERIFY (`58c7cab9`) BREAK no-terminator fix is real + gate-clean (13/13, 34, 175/280, 238/280, M2=19 M4=15), but its "verified via --run" claim verified the C oracle, not native x86. SBL-M4-FLATWIRE separate (standalone brokers at runtime). |
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

**⛔ CROSS-CUTTING (Lon, 2026-05-28) — MODE-3 IS PURE x86, NO INTERPRETER, ALL LANGUAGES.** "SCRIP Mode 3 is NO INTERP and pure x86 asm for ALL languages" (SNOBOL4, Snocone, Rebus, Icon, Prolog, Raku). ARCH-SCRIP.md confirms: mode 3 `--run` executes native x86 only; the C walkers `sm_interp_run` + `bb_exec_*` belong to mode 2 ONLY. **VIOLATION (traced):** `scrip.c` mode_run calls `sm_run_with_recovery(sm, sm_interp_run)` — mode-3 currently runs the MODE-2 C INTERPRETER (SM via PC-dispatch loop; BB via `bb_exec_pat`/`bb_exec_once`). The named native runners (`sm_jit_run`/`sm_emit_linear`/`sm_run_linear`) DO NOT EXIST yet. The facilities do: `codegen_sm_x86` (SM x86 producer), `sm_image`+`seg_seal` (RX SM image), `bb_pool`+`bb_seal` (RX BB slab), `bb_build_flat`. This is why filling BINARY template arms changed nothing — mode-3 never emits/runs them. Full design + 5 steps in `GOAL-SNOBOL4-BB.md` § SBL-M3-NATIVE (foundational engine build, not a tweak). Mode-4 sibling: SBL-M4-FLATWIRE (standalone brokers at runtime via rt.c:335). Until M3-NATIVE lands, "verified via --run" verifies the C oracle, NOT native x86.

---

## Session trigger phrases

| Lon says | Meaning |
|----------|---------| 
| "here we go" | Session starting |
| "perform hand off" | End of session — update goal state, commit, push per RULES.md |
| "perform emergency hand off" | Same, note breakage |
| "grand master reorg" | HQ system work |
