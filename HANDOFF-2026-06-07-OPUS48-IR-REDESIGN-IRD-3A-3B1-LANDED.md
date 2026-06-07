# HANDOFF 2026-06-07 OPUS48 — IR-REDESIGN: IRD-3a SNO + IRD-3b-1 ICON CLUSTER LANDED

## Commits (SCRIP origin/main)

- `e070535` IRD-3a SNO sweep (cherry-picked over parallel FIXUP `0a57954`)
- `4699ab8` IRD-3b-1 ICON access/assign cluster

Both re-gated on the merged tree after the parallel FIXUP session
advanced origin under this session (twice).

## Lon ruling recorded (in-session, do not relitigate)

idx/own STAY on IR_t — the sidecar key survives; IR_t = 7 members
(5 ratified + idx/own); IRD-5 fence updated to 7. Interpretation
note flagged to Lon at the time: ruling read as BOTH idx and own
(the macros need own to resolve idx); if Lon meant idx-only with
graph-passed macros, say so next session.

## What moved

IRD-3a (sno, 5 kinds): PAT_ASSIGN_COND/IMM inner entry α→operands[0];
IR_SCAN subj/repl GRAPHS aux→operands (IR_graph_t* cast as IR_t*
PRESERVED — move-not-fix); REF_INVARIANT sealed PAT_LIT +
PAT_MATCH element aux→operands[0], incl. the emit-time
flat_drive_scan_native PAT_MATCH producer inside emit_bb.c.
Consumers: interp arms; flat_drive_capture/scan_stmt/ref_invariant/
match; bb_print SCAN recursion.

IRD-3b-1 (icon, 5 kinds): IDX_SET base/key/rhs and SECTION
base/i1/i2 → operands[0..2] with the β→γ third-operand parking
stitch DROPPED; FIELD_SET obj/rhs → operands[0..1]; FIELD_GET obj
→ operands[0]; SWAP lv/rv → operands[0..1]. Consumers: 5 interp
arms; flat_drive_swap/field_get/field_set/idx_set;
flat_drive_every deep-reads of FIELD_SET/IDX_SET children.

## Safety findings (verified, reusable)

1. walk_bb_flat is a SINGLE-NODE label-driven dispatcher: passed
   labels override stored γ/ω; multi-node composition is recursive
   by kind. Stored γ on operand entries is inert in flat emission —
   that's what made dropping the β→γ stitch safe.
2. descr_chain_operand_refs is a kind-blind α/β WRITER on the descr
   chain, gated by descr_chain_arity; arity −1 (default) for all 10
   swept kinds, so it never rewires them. CHECK THIS TABLE before
   sweeping any further kind.
3. IR_SCAN's operands hold IR_graph_t* cast as IR_t*. Any generic
   walker over operands[] MUST explicit-case IR_SCAN (done in
   ir_is_single_shot). Repeat the guard in every future walker.
4. Dual-mode arms (SECTION/IDX_SET): the AG-ring flat mode gate
   `!α && !β` becomes `n_operands == 0`. Same pattern will recur.
5. dump-bb and prove_lower print α/β port columns → they DRIFT BY
   DESIGN when children move. Gate on program output + prove_lower
   PASS count (68), never on their byte identity. prove_lower also
   has pre-existing ASLR ival-pointer noise (GCONJ et al.).

## Gate procedure (scripts/bake_ird3_baseline.sh, NEW at e070535)

Bakes: 4 smoke logs + prove_lower log + per-file --interp md5
sweeps (sno 153 / icn 9 / pl 8 / pas 5). Gate = sweeps
byte-identical; smoke PASS/FAIL rows identical; prove_lower PASS
count stable. Both commits ALSO carry live-kind proof so the gate
isn't vacuous: sno m4 smoke 7/7 HARD GATE + pat_rung 18/0;
rung13_tables 5/5 (IDX_SET), rung24 records 3/3 m2 (FIELD_GET/SET),
SECTION/SWAP dialect probes.

## Environment (fresh container)

- apt-get install -y libgc-dev before make.
- `make libscrip_rt` is MANDATORY for any m4 work: without
  out/libscrip_rt.so every m4 gcc link fails and all m4 suites
  vacuous-fail (this poisoned the first baseline of this session).
  With it: sno m4 7/7, icon m4 10/12, prolog m4 5/5, pat_rung 18/0.
- Probe programs must match the live Icon dialect: no multi-name
  `local a, b` lines (parse error); copy dialect from
  corpus/programs/icon/rung* fixtures.

## Law-5 flags (pre-existing, A/B-stash-proven, NOT chased)

- RAKU (owner RAKU-BB): `scrip x.raku` aborts "main BB graph not
  found" ALL modes at HEAD and at pre-IRD c792829 (mode-2 driver
  looks up proc "main"); smoke 0/17, full suite m2 17/47. The
  IRD-1/2 handoff's "raku 25/25" does not reproduce.
- rung36_jcon_lists / rung36_jcon_string1 m2 FAIL (icon sections).
- pat_rung 053_pat_alt_commit m4 SKIP (compile/link).

## NEXT — IRD-3b-2 (remaining icon, line refs at 4699ab8)

lower_icon.c: ASSIGN 137, RANDOM 170, INITIAL 202, LIMIT 217/221,
CASE 236/279/286 (chain-shaped arms via β/γ stitches).
⚠ ASSIGN FIRST NEEDS A PRODUCER CENSUS: lower_icon sets only
α=rhs, yet gen_resume_target recurses ->β and flat_drive_every
reads gen_assign->β — somebody else writes ASSIGN->β (suspects:
every-gen wiring, descr_chain_operand_refs arity-1 path which
WRITES n->α for ASSIGN kinds on the descr chain). Map all writers
before moving the field, or the sweep will silently orphan a
consumer. After icon: prolog, raku, pascal, program (shared lower.c
operand_aux at 103/231/267/495 = apply/binop/bounds/ce — identify
kinds during that sweep), then the bulk consumer-internal α/β
classification in IR_interp.c (~300) and emit_bb.c (~190).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
