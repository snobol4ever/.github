# FINDING 2026-09-12 15:21 CDT (ceo) — an alternation beyond 32 arms delivered the 32nd arm's value in both modes

**Tree:** measured on SCRIP `26bbc4c6f`, cured `4faf4ed6b` · corpus `cb0301bb6` (fileprnt, the IPL program that exposed it) · seat ceo (lane ICON TO 100%) · cursor CEO-632.

## Measurement

`fileprnt` read `error 103: string expected … &null || "|"` at line 72. Ablation (fourteen witnesses): the exhausted-co-expression shapes all
pass; the trigger is the WIDTH of the alternation. Sweep: 2, 3, 4, 8, 17, 24, 31, 32 arms pass; 33 and 34 fail. Plain
`every write("s1" | … | "s34")` prints `s32 s32 s32` for its last three lines in BOTH modes — a silently wrong value, no error — and
through a co-expression the 33rd result is `&null`. icont has no such limit.

## Cause

`src/emitter/emit.h` carried `int64_t op_parts_ival[32]` in the template context; the DISJUNCTION and SCAN_SEQUENCE writers in
`emit.cpp` filled it with `for (j < N && j < 32)` while setting `op_parts_n = N`, so `bb_disjunction.cpp`'s σ-copy loop indexed
arms 33+ past the array (into the neighbouring fields). `lower_alt_impl` had its own silent cap: `resv[64]`, `j < 64`, and
`ival = min(n, 64)` — arms 65+ dropped at lowering.

## Cure (SCRIP `4faf4ed6b`)

`op_parts_ival` is a growable table (`emit_parts_reserve`, doubling from 32; both writers reserve N first); `bb_define.cpp`'s two
by-value save/restore sites of `g_emit` keep the live pointer and capacity across the restore; the lowerer sizes its arm list by n.
The three sibling arrays `op_parts_tag/str/lbl` have no writer anywhere in the tree and are left as they are.

## Proof

`test_gate_icn_alternation_beyond_32_arms.sh`: a 40-way alternation plain and through a co-expression, 82 lines byte-identical to
icont in m3 and m4; `FAIL_ONCE=1` trips the diff arm. Wired into `make test`. Control arms on the shared box: smokes icon 15/15,
snobol4 7/7, prolog 5/5, snocone 5/5 (both modes); emit_no_lang, template_medium_invisible, define_alternate_entry and the seq
gate green; preflight 33/0; fileprnt PASS/PASS in the IPL runner's isolation. `test_gate_sno_define_prototype_follows_the_executed_define.sh`
reads red before and after — the cfo's standing row under CEO-630, not this change.
