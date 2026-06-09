# HANDOFF 2026-06-06 — Opus 4.8 — ICON-BB ICN-VAR-FENCE: the var-ladder close-out gate

## What landed (one gated rung — script-only, zero source changes)

**ICN-VAR-FENCE** — `scripts/test_gate_icn_var.sh`, the ICN-SCAN-FENCE pattern (capture-then-match,
never `cmd | grep -q` under pipefail). Four sections: (a) IR_ASSIGN/IR_VAR absent from
`icn_kind_native_stub` + present in contracts; (b) 19-probe three-mode sweep covering VAR-1
(assign int/str, var-to-var, reassign), VAR-2 (var binop/relop, accumulate, while/until loops),
VAR-AUGOP (`+:=` `*:=` `-:= %:=` chains), VAR-3 (`?:=` scan, var-subject scan); (c) the corpus
IR_ASSIGN bucket — every rung*.icn whose `--dump-bb` carries IR_ASSIGN, N=104, ratchet floors
m2>=62 m3>=12 m4>=22 PLUS the HARD law m3/m4 FAIL==0 (only PASS or EXCISED — a silent native
miscompile in the var bucket fails the gate); (d) the standing structural battery (bb_bin_t,
handencoded --strict, icn_no_stack, one-reg-frame, prove_lower2 HARD; vstack informational;
medium-invisible scoped to bb_assign_local/bb_var_frame*).

## Probe-policy decisions made while landing (the four first-run failures)

1. **var2_var_while** — first draft used `writes(i)`, which routes through the abolished
   `rt_call_builtin` and aborts m3/m4 (the builtin lane, not a var defect). Probe now uses
   `write(i)` with multi-line expected; m2==m3==m4.
2. **augop_sub_mod** — my arithmetic was wrong (7-3=4, 4%2=0, not 1). Now 10-3=7, 7%4=3.
3. **augop_concat** (`s ||:= "world"`) — pinned **X34**: the desugar produces a concat BINOP,
   which is outside the VAR-2 numrel+arith lens; m2-correct + clean native EXCISE, exactly as
   the AUGOP handoff documented ("`||:=` m2-correct + clean native EXCISE (concat lens)").
   Lighting it natively = extending the BINOP lens + bb_binop_concat_slot admission, a future tier.
4. **static_single_call** — the draft expected static to EXCISE; FALSE. TT_STATIC_DECL lowers
   as a no-op IR_SUCCEED (lower.c ~1108) and the var routes through the same bb_varslot path as a
   local — verified m2==m3==m4 `hello`. The probe now pins that three-mode agreement STRICT.
   Cross-call static persistence is not exercised anywhere in the native lane yet; when userproc
   recursion lands (standing flag 4), static needs its own tier (a global slot, not a frame slot).

## Gates (all green)

Fence **GATE: PASS** — probes 19/19; bucket N=104 m2 62 / m3 12+0F+92E / m4 22+0F+82E at the
floors. Full three-mode corpus suite confirms the watermark columns unchanged: **m2 143 HARD ·
m3 30 · m4 40** (diff is additive script-only). Smoke Icon 12/12 · 10/12 · 10/12 (userproc lane,
standing flag) · no_bb_bin_t 0 · handencoded --strict 0 · icn_no_stack 0 · one-reg-frame 0 ·
g_vstack 3 (pre-existing rt.c/rt.h) · prove_lower2 PASS.

## Next

The ICN-VAR LADDER is **CLOSED**. Per the goal priority line: **BB-HYGIENE remainder** — ICN-HY-7
marshal fusion (`marshal_call_arg`/`marshal_varparam_addr` operand-subgraph reads), BLOCKED on the
standing lowerer PREREQ (chain literal operands as producer boxes, the GZ-3/GZ-4 class): lowerer
rung first, then delete the operand-kind arms, then ICN-HY-FENCE (extend
`test_gate_bb_one_box.sh`'s file set to Icon AFTER the fusion fix or it arrives RED). Open tiers
behind it: GZ-DEFER, `bb_binop_gen` Fig-1 cross-product, native `!x`, concat-BINOP lens, statics.
