# HANDOFF — 2026-05-26 — Opus — SB-LINEAR Mode 3 (`--run`) SNOBOL4

**Goal:** GOAL-PROLOG-BB.md → NEW TOP-PRIORITY block "SB-LINEAR Mode 3 SNOBOL4 FIRST".
**Build:** ✅ GREEN (requires `apt-get install libgc-dev` in a fresh container).
**Mode 3 (`--run`) SNOBOL4 smoke: PASS=5 FAIL=1** (only `pattern`).
**Mode 2 (`--interp`) smoke: 7/7 — UNREGRESSED.** All edits isolated to the linear `--run` path.

⚠ **UNCOMMITTED.** One file changed: `src/processor/sm_jit_interp.c`. Gate not 6/6, so not committed.

## Honesty correction
Prior PLAN/HANDOFF notes asserted Mode 3 was "complete"/"wired". It was NOT: `--run`
crashed `define` with a stack-underflow abort and mis-ran `pattern`. Mode 3 is now tracked
ONLY by the reproducible 6-case `--run` smoke (see GOAL top block). No "done" without numbers.

## What was actually broken and what I fixed (all in sm_jit_interp.c)

The `--run` path = SB-LINEAR: `sm_emit_linear` lays the whole SM stream out as linear x86 in
SEG_CODE (each instr falls through; only JUMP*/RETURN*/HALT emit jmp/ret), then `sm_run_linear`
jumps to `sl_instr_addr[0]`. Function bodies are entered by `rt_call_fn` via a native C call
`((blob_fn_t)blob)()` into the body's label address.

1. **SBL-FN-RET (define abort → PASS).** `SM_RETURN` ran `h_return_impl`, which only did
   trampoline-era `STATE->pc = ret_pc` bookkeeping — NO native `ret`. So after RETURN the body
   fell through into whatever code physically followed it → stack underflow → abort.
   - `h_return_impl` now returns `int` (1 = a return fired).
   - `rt_return*` wrappers return that int (conditional :S/:F return 0 when guard not met).
   - New `sl_ret_if_eax()` emits `test al,al ; jz +1 ; ret` (5 bytes) after EVERY RETURN-family
     `sl_call` so a fired return unwinds natively to rt_call_fn's call site; a non-fired
     conditional return falls through to the next linear instruction.

2. **SBL-FN-ARGS (part of define PASS).** `rt_call_fn` bound every parameter to `NULVCL` and
   NEVER bound the actual arguments (so `DOUBLE(21)` saw `X` = null → printed 0). Now pops the
   args into `call_args[]` BEFORE `sp=0`, then `NV_SET_fn(pname, k<na ? call_args[k] : NULVCL)`
   — mirrors the trampoline `h_call` at sm_jit_interp.c:1079.

3. **SBL-EXEC-PATD.** `rt_exec_stmt` no-blob branch passed `NULVCL` instead of the popped
   pattern descriptor `pat_d`. Now passes `pat_d` to `exec_stmt`. (Correct, but does NOT fix
   `pattern` — see below.)

## The remaining failure — SBL-PAT-BLOB (OPEN, needs emit_bb.c work)

`S 'b' = 'X'` should give `aXc`; Mode 3 gives `Xabc` (replacement placed at pos 0, len 0).

**VERIFIED it is NOT a dispatch / blob-vs-pat_d choice.** I tested routing the runtime `pat_d`
(DT_P, the real PATND_t built by SM_PAT_LIT) straight into `exec_stmt` — STILL `Xabc`. Reason:
`exec_stmt`'s DT_P branch (stmt_exec.c:273) compiles the PATND_t via `bb_build_flat` /
`bb_build_brokered` and runs the SAME compiled blob. That compiled blob mis-anchors a simple
literal (matches empty at position 0 instead of scanning forward to `b` at position 1).

Mode 2 is correct ONLY because `case SM_EXEC_STMT` (sm_interp.c:585) takes the
`bb_exec_pat(pat_bb,...)` BB-graph **interpreter** branch, which never compiles.

**Fix location:** `bb_build_brokered` / `bb_build_flat` in `src/emitter/emit_bb.c:611` — the
compiled simple-literal (unanchored) pattern must scan forward like `bb_exec_pat` does in
`src/lower/bb_exec.c:2069`. Compare the two executors on the SM_PAT_LIT graph for `'b'`.

## Verify-my-work checklist for next session
- [ ] `apt-get install libgc-dev` then `bash scripts/build_scrip.sh` → "OK scrip built".
- [ ] Reproduce the 6-case `--run` smoke (bodies are in scripts/test_smoke_snobol4.sh, run each
      with `./scrip --run FILE`): expect 5/6, only `pattern` failing with `Xabc`.
- [ ] `bash scripts/test_smoke_snobol4.sh` (mode2) → 7/7, confirming no regression.
- [ ] Fix emit_bb.c pattern anchoring → 6/6 → THEN add `--run` variants to
      test_smoke_snobol4.sh as a permanent gate (SBL-GATE) → THEN commit.
- [ ] Only after SNOBOL4 6/6: return to Prolog Mode 3 — `SM_BB_ONCE_PROC` lookup misses
      (`pl_bb_once_proc_by_name` returns NULL graph for `main/0`), so `--run` and even `--interp`
      of `:- initialization(main)` print nothing. Was mid-investigation; the dcg_table /
      g_stage2.sm.bb_count linkage is the suspect (pl_runtime.c:79, bb_graph_of_pred).

## Watermark
```
one4all: 1c4e37c7 + uncommitted (sm_jit_interp.c only) — BUILD GREEN
.github: GOAL-PROLOG-BB.md top block added (SB-LINEAR FIRST) + this file
Mode 3 --run SNOBOL4 smoke: 5/6 (pattern fails: Xabc, want aXc)
Mode 2 --interp SNOBOL4 smoke: 7/7 (unregressed)
NEXT: emit_bb.c bb_build_brokered/flat simple-literal anchor fix → 6/6 → SBL-GATE → commit → Prolog
```
