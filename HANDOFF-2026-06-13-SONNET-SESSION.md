# HANDOFF — Sonnet session 2026-06-13 (Icon m3/m4)

## Verified state at handoff
- **SCRIP HEAD = `8b9a58e`**, **.github HEAD = `5b6b495a`** — both clean & pushed.
- m2 interp HARD gate **PASS=202** / 283 (XFAIL 36). Icon rung tally **m2 202 · m3 76 · m4 82**.
- icon smoke 12/12 ALL three modes; prolog smoke 5/5 all modes; `test_gate_icn_no_stack`=0;
  `test_gate_icn_one_reg_frame`=0. (The 45 `test_gate_bb_one_box` FAILs are PRE-EXISTING — emitter
  entry-count gate, untouched.)

## What landed this session
1. **Icon pow `^` constant-fold** (SCRIP `2831781`, lowering only — `src/lower/lower_icon.c`, +9 lines).
   Icon `^` always yields a real (`.expected`: `2^10`→`1024.0`). The interp dispatched int^int through the
   `**` path (int result) so the pow rungs FAILed in all three modes. Fold a fully-constant pow to
   `IR_LIT_F` at the lowering binop site, reusing the existing real-literal path on both m2 (interp prints
   LIT_F = computed real) and native (`bb_lit_scalar` IR_LIT_F arm). `icn_const_step` extended with a
   recursive `TT_POW` case so `2^2^3` folds whole. Result: **m2 197→202, m3 70→76, m4 76→82**, no
   regression. (rung26_pow_pow_expr `2^3+1` → `LIT_F(8.0)+LIT_I(1)` still declines native — the real-arith
   gap, see below.)
2. **IR-IMMUTABLE rule — misread, then corrected.** Briefly bombed the mode-3/4 emitter entry (`e50b089`)
   on the wrong reading that the emitter must not read the IR at all; **reverted in `8b9a58e`**. CORRECT
   model: mode 3/4 require ONE full read of the IR at EMISSION time (mode 3 → in-process image; mode 4 →
   `.s` source) — that read is required and correct. The IR must only be untouched DURING EXECUTION of the
   emitted artifact (no runtime `IR_t *` deref reachable from the running program; no IR pointer chased by
   generated code). Full corrected plan + the real audit task: **HANDOFF-2026-06-13-IR-IMMUTABLE-MODE34.md**.
   Do NOT purge `emit_bb.c` — its read IS the sanctioned emission read.

## Next steps, prioritized (m2 frozen as HARD gate; m3/m4 are the work)
1. **REAL ARITHMETIC native path** — highest-leverage rc=134 unblock. `write(2.0*3.5)` (rung17), real
   relops (rung18), and `2^3+1` (rung26_pow_pow_expr, now `LIT_F+LIT_I`) all bomb/decline: in `emit_bb.c`
   `descr_binop_opnd_slot` (~line 1420) returns -1 for `IR_LIT_F`, so real/mixed operands never get a slot,
   and the arith template only does integer `add/sub/imul/idiv`. Fix: slot LIT_F operands + a real-arith
   template arm (SSE `addsd/mulsd/divsd` on the boxed doubles, or a DESCR-in/out `rt_*` arith helper —
   match the m2 interp's REAL coercion semantics, not `POWER_fn`).
2. **Native builtin call wiring** — `[IBB] bb_call: unsupported call shape fn='push'/'read'/'iand'` (lists
   rung22, read rung27, math rung37). Wire these into the native call path.
3. **`bb_every` four-port box** (architectural) — the rc=124 generator-resume timeout cluster (rung01 paper,
   rung02 arith-gen, rung03 suspend, rung14 limit, rung19 real_toby). `bb_every.cpp` is a hollow stub; the
   real EVERY drive/resume/exhaust lives in `flat_drive_every` (DRIVER, violates TEMPLATE-ONLY). Build a
   real box mirroring canonical `ir_a_Every` (irgen.icn:309). See HANDOFF-…-EVERY-BOX-MISSING.md.
4. **Global var native reads** (`bb_var` arm; rung21/25) — riskier, touches the OLD/NEW var-model switch
   (`g_icn_globals_nv`); consult GOAL-ICN-GLOBAL-NV.
5. The **execution-time IR-access audit** (rule enforcement) — orthogonal to scoring; see the dedicated
   IR-IMMUTABLE handoff.

## Discipline (binding)
m2 (`--run`) is the HARD oracle — never let `--mode interp` PASS drop below 202; verify with an explicit
before/after `bash scripts/test_icon_rung_suite.sh --mode interp` diff. ALWAYS gate all three modes; a
native shape with no template should LOUDLY `[SMX]` decline (→ EXCISED, sanctioned) — NOT abort. Filter
triage output (rung37 has an infinite-loop case that floods stdout). Build: `bash scripts/build_scrip.sh &&
make libscrip_rt`. Commit per repo, push code repos first then .github last; `.github` remote needs the
token copied from SCRIP's remote to push. No broken commits.
