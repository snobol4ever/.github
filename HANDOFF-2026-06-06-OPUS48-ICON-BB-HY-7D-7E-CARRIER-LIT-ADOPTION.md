# HANDOFF 2026-06-06 — Opus 4.8 — ICON-BB HY-7d+7e: N-arg slot carrier + LIT_I/LIT_S producer-box adoption

## What landed (two gated rungs — the first DUP-FORM-3 de-fuse slices, riding the HY-7c UNBLOCKED verdict)

**HY-7d (`1ec4252`)** — the N-arg call-arg slot carrier: `g_emit.op_arg_slot[16]` + `op_arg_slot_n`
(emit_globals.h, struct-END append so no existing offsets shift) + `gvar_drive_call_arg_slots` (emit_bb.c):
pre-scans the call's arg subgraphs (leading SUCCEED/FAIL resolved), admits terminal `IR_LIT_I`, emits each
admitted arg as a `bb_lit_scalar` producer box inside a `g_gvar_callarg_live` window (widens the IR_LIT_I
walk-case slot-alloc + the template arm), deposits terminal slots into the carrier. `marshal_call_arg` gained
a slot-first arm: owner-guarded (`owner == _.node`) pure 16B `[r12+ps]→[r12+aoff]` copy — medium-invisible,
ZERO `lf->t` reads. Wired BOTH gvar call branches: dval==3.0 (Pascal v_det_call) AND dval==2.0 (SNOBOL TT_FNC;
DEFINE 5.0 excluded). Carrier reset at `case IR_CALL` top kills cross-call staleness; nested
`marshal_single_call` args fall through by the owner guard (their adoption = a later slice).

**HY-7e (`447edd9`)** — LIT_S adoption, a 3-line gate-widen: admit terminal `IR_LIT_S`; the `IR_LIT_S`
walk case + the `bb_lit_scalar` LIT_S arm join the `g_gvar_callarg_live` window. Strings seal RO
`[rip+disp]` per the READ-ONLY FACT rule.

## THE FINDING (latent hazard, found + fixed in-rung)

The gvar flat-chain builds do NOT reserve frame[0..15] — the gvar proc-RESULT slot that the ω FAILDESCR
epilogue writes and `rt_call_proc_descr` reads (`descr_flat_chain_build_proc` reserves it; the gvar builds
start at 0/nslots). The first arg pre-alloc stole offset 0 — harmless for procedures, RESULT-CORRUPTING for
functions. Fix: pre-scan admits, then `bb_slot_claim(16 - g_flat_slot_count)` ONLY when adopting — zero
byte-churn for every non-adopted program. Proven by the nested stress `F = G(10) + X; OUTPUT = F(1)` → 21
in m2==m3==m4 including the gcc-linked m4 binary.

## Gates (all green, both rungs)

Probes SNO `F(41)`→42 / nested →21 / `F('AB')`→ABAB / PAS `q(42)`→42 / `writeln('hello')` — all three modes
incl. linked m4. Icon suite **m2 143 HARD · m3 30 · m4 40** byte-identical, zero flips. Smokes: icon 12/10/10
· sno 7/6/6 · prolog 5/4+1E/5. Blast radius proven pre-existing via stash-baseline re-runs: raku 1/1/23 ·
snocone 2/3 · rebus 0/4 · crosscheck FAIL=1 · broker 32/35. FACT 0 · bb_bin_t 0 · handencoded --strict 0 ·
medium-invisible 347 (new arm is pure x86()) · icn_no_stack 0 · one-reg-frame 0 · VAR fence PASS · SCAN
fence PASS · prove_lower2 PASS. CONCURRENCY: rebased over SNO-HY-2a (`178b6e8`) + a BB-FIXUP; re-verified
green at merged HEAD.

## Next

HY-7f: LIT_F/NUL producer arms — `bb_lit_scalar` has ONLY the pass-through for these kinds, so this slice
writes NEW template bytes (LIT_F: tag-7 + RO-sealed IEEE bits; LIT_NUL: two zero stores), byte-verified vs
`as`. Then gvar/frame-var reads as producer boxes; then nested `marshal_single_call` args; THEN delete the
operand-kind arms in `marshal_call_arg` + the `->t/->sval` reads in `marshal_varparam_addr`; then
ICN-HY-FENCE (extend `test_gate_bb_one_box.sh` to Icon files only after).
