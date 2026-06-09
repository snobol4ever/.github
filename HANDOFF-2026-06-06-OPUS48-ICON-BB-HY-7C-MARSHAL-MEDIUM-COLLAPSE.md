# HANDOFF 2026-06-06 — Opus 4.8 — ICON-BB ICN-HY-7c: marshal_call_arg medium collapse + PREREQ verdict

## The PREREQ verdict (the rung's first finding)

**The "lowerer PREREQ" blocking the HY-7 marshal de-fuse is STALE.** Diagnosed 2026-06-01 ("the lowerer
does not yet chain literal operands as producer boxes"), it was satisfied by DRIVER machinery that landed
with the scan ladder: `descr_chain_operand_refs(entry)` + `flat_emit_arg_subchain(entry, succ, fail)` +
`bb_slot_get(terminal)` — live at emit_bb.c ~1260/2027 (SCAN-7 `tab(upto(c))`) and ~1296
(`flat_drive_userproc`, per-arg subchains). The full DUP-FORM-3 de-fuse (delete the operand-kind reads,
drive every marshal site from pre-emitted arg-subchain slots) is therefore UNBLOCKED — it needs the
g_emit slot carrier extended to N args plus per-shape driver adoption, its own rung(s).

## What landed (one gated rung — bb_call.cpp only, 77 lines → 29+48)

**ICN-HY-7c** — `marshal_call_arg`'s lit/var tail was the same marshal algorithm written TWICE
(`if (MEDIUM_TEXT) {…} else if (MEDIUM_BINARY) {…}`, DUP FORM 1 in statement form). Collapsed to ONE
medium-invisible body: LIT_I/LIT_F via `x86("mov",FRQ,tag)` + `x86_movabs_r64` + `x86_frame_store64`;
LIT_NUL two FRQ stores; LIT_S tag + `x86_ro_load_q` + jump-over in-band `x86_ro_seal_str` (ids
`idx*2`/`idx*2+1`; the call family used ZERO internal ids — verified — so the namespace is free); var
arm = pure `x86_frame_load64/store64` slot copy. The gvar/arith heads and `marshal_single_call`
dispatch are untouched (the gvar call pair is the sanctioned per-medium call encoding).

**RO FACT-rule fix riding it:** the old BINARY LIT_S arm baked the ABSOLUTE in-process `sval` pointer
(`x86_load_ro(… (uintptr_t)sval)`) — a direct violation of ICON READ-ONLY LOCALS ARE IP-RELATIVE
("never an absolute movabs immediate"). Now both media seal the string in-band and load rip-relative.

**Gate-intel:** `test_gate_template_medium_invisible.sh` greps the `IF(MEDIUM_BINARY,…)` MACRO form
only; this site used the `if (MEDIUM_BINARY)` STATEMENT form and was never counted (total stays 347).
The grep has a blind spot for statement-form medium branches — a future gate-hardening candidate.

## Build-staleness lesson (do not skip)

The first incremental build after the edit produced a binary whose multi-arg probe behaved
inconsistently (apparent abort) while every suite ran green; a stash/rebuild cycle and a second full
rebuild of the SAME source EXCISED the probe cleanly rc=0, identical to baseline. All gates were then
RE-RUN on the verified-clean build. Treat any post-template-edit anomaly as stale objects FIRST:
clean-rebuild before diagnosing (the g_emit STRUCT-LAYOUT lesson, generalized).

## Gates (all green, on the clean build)

Probes write {42, "hello", var, 2+3, "a"||"b"} m2==m3==m4; multi-arg `write("v=",x)` EXCISES loud
rc=0 in m3/m4 (= baseline). Smoke Icon 12/12 · 10/12 · 10/12 · Prolog 5/5. Full suite **m2 143 HARD ·
m3 30 · m4 40** byte-identical, zero flips. VAR fence PASS (19/19, bucket 62/12/22, m3/m4 FAIL=0) ·
SCAN fence PASS (28/28, bucket 11/11) · no_bb_bin_t 0 · handencoded --strict 0 · icn_no_stack 0 ·
one-reg-frame 0 · prove_lower2 PASS · medium-invisible 347 (the macro-grep blind spot above).

## Next

HY-7 remainder, now UNBLOCKED: extend the slot carrier to N call args; per marshal call-site shape,
driver-emit arg subchains (`flat_emit_arg_subchain` pattern) and deposit slots; DELETE the lit
operand-kind arms in `marshal_call_arg` + the `->t/->sval` reads in `marshal_varparam_addr`; then
ICN-HY-FENCE (extend `test_gate_bb_one_box.sh` to Icon files only after).
