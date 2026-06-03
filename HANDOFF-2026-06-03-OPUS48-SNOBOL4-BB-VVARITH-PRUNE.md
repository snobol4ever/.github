# HANDOFF 2026-06-03 (Opus 4.8) — SNOBOL4-BB: VAR+VAR param-arith + GOAL prune

## TL;DR
- Landed the gvar **VAR+VAR arithmetic** path → the `X+X` (param + param) `bb_binop_arith: shape mismatch`
  BOMB is gone. SCRIP tip `f7a2ddc`.
- **Major-pruned** `GOAL-SNOBOL4-BB.md` 2922 → 1225 lines (two passes), FACT RULES byte-identical (concurrency
  gate green throughout). .github tip = this handoff commit.
- **Corrected the prior handoff's `define` diagnosis** (see "REAL BLOCKER" below) — this is the most important
  carry-forward.
- All gates GREEN, no regression. Both repos pushed to `origin/main`.

## COMMITS
- SCRIP `f7a2ddc` — VAR+VAR gvar-arith path.
- .github `1dbb8d75` — GOAL prune pass 1 (2922→1262).
- .github `37ab38c9` — GOAL frontier: corrected define diagnosis.
- .github `29638156` — GOAL prune pass 2 (1271→1226; collapsed ORACLE-PARITY log + OLD PB-0..PB-OPT rungs).
- .github (this commit) — watermark bump + this handoff file.

## WHAT LANDED — VAR+VAR param-arith (SCRIP `f7a2ddc`, 4 files, +34 lines)
`DOUBLE = X + X` (two IR_VAR params in the gvar flat chain) previously fell to `flat_drive_binop_tree` →
`IR_BINOP_ARITH` → `bb_binop_arith`, whose predicate needs `g_descr_flat_chain` (Icon) → BOMB. Fix, lowest-touch
(NO new IR kind, NO emit_core/Makefile change):
- `src/runtime/rt/rt.c` + `rt.h`: new `int64_t rt_gvar_arith(const char*a,const char*b,int op)` — reads both
  vars via `NV_GET_fn`, computes via `binop_apply` (the SAME kernel the mode-2 oracle uses → byte-identity),
  returns int64. (`binop_apply` declared with `int op`; ABI-identical to the `BinopKind` enum, no competing
  decl in that TU. `binop_apply`/`NV_GET_fn` are exported from libscrip_rt — verified.)
- `src/emitter/BB_templates/bb_binop_gvar_arith.cpp`: branch on VAR-mode (`op_name1 && op_name2`) →
  `x86_load_ro` both var-name ptrs into rdi/rsi, op in rdx, `call rt_gvar_arith`, raw int64 → `[r12+op_off]`.
  **BINARY-only**; TEXT(mode-4) bombs (needs RO-interned var-name ptrs — same posture as the concat path).
- `src/emitter/emit_bb.c` IR_BINOP dispatch: added a VAR+VAR arm that sets `op_name1/op_name2/op_off` and
  routes to the EXISTING `IR_BINOP_GVAR_ARITH` kind; and **clears `op_name1/op_name2` in the LIT+LIT arm** so
  the box's VAR-mode discriminator is unambiguous (g_emit is a reused global; `walk_bb_node` does NOT touch
  op_name1/2/op_off, so they persist across nodes — clearing in the LIT+LIT arm is required).
- Result slot contract (verified): `bb_slot_alloc(binop)` registers the offset; `emit_core.c:389` sets the
  consuming IR_ASSIGN's `op_a_slot = bb_slot_get(nd->α)`; the binop is emitted before the assign
  (`flat_drive_gvar_assign_binop`), so the slot resolves. `bb_gvar_assign` IR_BINOP arm reads it via
  `rt_gvar_assign_int` (raw int64). (Mixed `X+1` / `1+X` still fall through to `flat_drive_binop_tree` — not
  in the smoke; add VAR/LIT_I marshalling later if needed.)

## 🔴 REAL BLOCKER (define m3 5/6 → 6/6) — CORRECTS THE PRIOR HANDOFF
The smoke `DEFINE('DOUBLE(X)') ; OUTPUT = DOUBLE(21)` still FAILs (m3), but NOT for the reason previously
documented. Evidence gathered this session:
- `F()` (no-arg) `{F = 21 + 21}` → **42** (proc frame + LIT+LIT arith + RETURN all work).
- `G(X)` `{G = X}` called `G(21)` → **BLANK**; `DOUBLE(X)` `{DOUBLE = X+X}` called `DOUBLE(21)` → **0**.
  ⇒ the actual argument value never reaches the parameter X (X reads null inside the proc body).
- **The live mode-3 gvar proc-call does NOT route through `rt_call_named_proc` NOR `call_native_chunk`** —
  temporary `fprintf` probes inside BOTH never fired, even for the working `F()`. So the path documented in the
  earlier handoff (`marshal_call_arg` → `bb_call_gvar_userproc_str` → `rt_call_named_proc`, with args staged via
  `rt_arg_stage`/`g_call_args[]`) is NOT what executes. `rt_call_proc` is a `STACKLESS_ABORT` stub (would abort
  — it doesn't, so it's not used either).
- mode-2 (`--interp`) gives 42 (its own IR_interp path; registration semantics are fine there).

### NEXT STEP (where to start)
1. Find the ACTUAL mode-3 emit path for a registered user-proc CALL with `dval==2.0`. Trace the IR_CALL
   dispatch in `emit_bb.c` (~lines 1533-1547: `flat_drive_call_userproc` / the `g_gvar_flat_chain && dval==2.0`
   FILL branch) and confirm WHICH box actually emits for the `G`/`DOUBLE` call site (disasm the JIT, or add a
   one-line stderr in each candidate box's emit fn and see which prints). The mechanism is likely a native
   inline-jump into the proc-body label with the param bound elsewhere — NOT a C runtime call.
2. Once the real path is known: confirm where the arg DESCR is written and where the param is read, and fix the
   mismatch. The integer marshalling in `bb_call.cpp marshal_call_arg` BINARY arm (DT_I tag=6, value at aoff+8)
   looked correct in isolation, but it may not be the live path.
3. THEN the string-arg `slen` bug (does NOT block this smoke; for `G('AB')`-style): `marshal_call_arg` IR_LIT_S
   writes the DT_S tag but leaves `slen`=0 (a `DT_S` with `slen==0` is read as a VARIABLE NAME by `VARVAL_d_fn`).
   FIX both arms: pack `v | ((uint64_t)strlen(s)<<32)`.
4. When `DOUBLE(21)`→42 in m3: raise `MODE3_MIN` 5→6 in `scripts/test_smoke_snobol4.sh`.

⚠ Traps: `x86("mov",reg,uint64)` emits `movabs;call` (NOT a mov) — use `x86_load_ro`/`x86_frame_lea`;
`x86_movimm` truncates imm64→32.

## GOAL PRUNE (2922 → 1225)
Method: cursor/anchor-based scripts replacing completed/superseded/historical regions with terse stubs; FACT
RULE headers used ONLY as end-anchors so their bytes stay in the kept gaps. **Invariant honored:**
`audit_concurrency_invariants.sh` byte-checks two blocks across the 3 GOAL files — `SHARED-LOWERER ONE-FILE`
(md5 `5097ed94…`) and `ONE-DISPATCH CONCURRENCY` (md5 `307534d6…`); both verified UNCHANGED. All ten FACT RULE
blocks left byte-for-byte intact. Kept: CURRENT FRONTIER (define), all FACT RULES, the SBL-PAT-BB "Eureka"
design, the PB-RB ladder + forward `[ ]` rungs, REG/BB-HYGIENE ladders, Session Setup (gate cmds), TESTING
DIRECTIVE. Compressed: completed session narratives, the LI/de-name/REORG rungs (now split to
`GOAL-RUNTIME-RENAME.md` / `GOAL-RUNTIME-REORG.md`), GROUND-ZERO/RENAME-BB→IR done-notes, the session log, the
LOWER2 ladder, the ORACLE-PARITY achievement log, and the OLD PB-0..PB-OPT superseded rungs. Remaining length is
mostly the gated FACT RULES (~470 lines) + live forward design — not further safely prunable.

## GATES (all GREEN, no regression)
SNOBOL4 m2 **7/7 HARD** / m3 **5/6** / m4 0/6 · Icon m2 12/12 (untouched — VAR+VAR is a SNOBOL-only
`g_gvar_flat_chain` arm; Icon uses `g_descr_flat_chain`) · `prove_lower2` PASS · `no_bb_bin_t` 0 · LI-FENCE OK ·
concurrency invariants OK. ENV: `apt-get install -y libgc-dev`; rebuild BOTH `scrip` + `libscrip_rt` after any
`src/emitter/**` edit.
