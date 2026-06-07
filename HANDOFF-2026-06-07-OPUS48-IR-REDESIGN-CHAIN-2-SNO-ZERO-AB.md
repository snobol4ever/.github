# HANDOFF 2026-06-07-E OPUS48 — IR-REDESIGN: IRD-3-CHAIN-2 LANDED — SNOBOL4 AT ZERO α/β USAGE

## Commit (SCRIP origin/main)

- `fec38d4` IRD-3-CHAIN-2 — CALL arg-list sub-cluster → operands[]
  (rebased over BB-FIXUP `451bfd0` bb_scan_upto at push; merged tree
  re-gated green: SNO m4 7/7, icon 12/10/10 at floors).

## Lon directives this session

1. Put the final finish on SNOBOL4 lower — isolated, complete, only
   proper IR_t fields. 2. Continue. 3. Perform hand off.

## What landed

**ir_call_arg(nd, j)** — NEW dual-read accessor in contracts/IR.h:
operands-bounded when n_operands>0, else the EXACT legacy α+γ-hop
walk (identical node sequences in both regimes; fallback termination
identical to the old unbounded loops).

**Writers.** descr_chain_operand_refs + gvar_stmt_operand_refs: CALL
ar∈{1,2} now push operands[0..ar-1]; CALL α/β writes DELETED. The
CALL β write was a pure zero-reader vestige — every arg walk reads α
then hops the γ statement-flow wires; β was never consulted.
icn_ring_to_tree (the third RPN writer, driver/scrip.c): CALL ar==1
pushes operands[0] lockstep, α write deleted; its BINOP/UNOP/EVERY
arms still write α/β — bulk scope, together with the interp tree
reads they serve (BINOP ~2598 / UNOP ~2712 / SEQ ~2508).

**Consumers → ir_call_arg.** emit_bb.c: flat_drive_call_intexpr
(guard + walk), flat_drive_call_userproc, flat_drive_call_builtin,
call_args_single_shot, dispatch-arm a0. IR_interp.c:
ir_is_single_shot BOTH unbounded CALL walks (per-index form) +
CALL-arm has_gen_arg probe, argv build, both arg pull loops (NULL
handling verbatim). Templates: bb_call.cpp a0 +
bb_call_write_slot.cpp slot-fetch + write_binop a0 — 3 one-line
dual-reads (BB-FIXUP owns BB_templates; their cursor was past these
files this lap; coordinated via small-commit-fast-push).

**Out-of-cluster confirmed (census, recorded).** interp 352 =
IR_STRUCT γ-chain and bb_atom_string.cpp pBB->α sites = prolog
IR_BUILTIN γ-chain — both IRD-3d scope. interp 2508 = IR_SEQ
raku/ring. emit_core.c 386 generic op_a priming was ALREADY
operands-first, so CALL gaining operands[0] feeds the same node.

**SCAN decision (recorded, deferred).** SCAN subject α KEPT in the
gvar writer pending the pattern-BB joint ruling / IRD-4. Pinned map:
SCAN operands hold the IRD-3a TYPE-PUNNED subj/repl GRAPHS — count
1-2 varies with replacement — pattern graph in EXEC.counter, subject
NAME in LIT.sval. Appending the subject NODE to the punned array
forces SCAN-aware positional walkers (slot-map redesign the
pattern-BB session co-owns). op_a, bb_walk_rec and both chain
writers carry the SCAN exemption.

## SNO verdict — prime time

lower_sno.c: complete explicit dispatch, isolated (SNO-ISO), zero
α/β, speaks {op, γ, ω, operands} + lit/exec sidecars only, AG
discipline end-to-end ⇒ ZERO touches needed at IRD-4. Full SNO route
(lowering + chain writers + CALL ecosystem) at zero α/β usage; sole
α residue = SCAN subject in the EMIT-TIME gvar writer, not in
lower_sno.c. Census caveat: PROGRAM/IDX/stray-pattern-kinds-in-
value-role still → lower_unhandled (pre-existing semantic gaps,
owner SNOBOL4-BB).

## Gate

bake_ird3_baseline.sh /tmp/base_pre at session HEAD vs /tmp/base_post:
sno 153 / icn 9 / pl 8 / pas 5 / sco 191 sweeps + 5 smokes
byte-identical; prove_lower 68 PASS rows md5-identical (`; PASS`
grep — `^PASS` does NOT match this log format); SNO m4 7/7 HARD
GATE; A/B asm diff EMPTY at git-stash pre-HEAD on CALL-hot probes
(icon userproc+builtin+intexpr+size, sno DEFINE+gvar).

## Law-5 flag (A/B-stash-proven pre-existing, NOT chased)

- `test/snobol4/keywords/100_roman_numeral.sno` m2 runs 7.8–8.5s at
  pre-change HEAD too — borderline 8s-fence flake; one bake row
  flipped rc 0→124 under load, full resweep byte-identical. Expect
  occasional fence noise on this row in future bakes.

## Environment (fresh container)

apt-get install -y libgc-dev; make; `make libscrip_rt` MANDATORY
before any m4 work. Authenticate origin remotes with Lon's token
(git remote set-url origin), git identity
LCherryholmes/lcherryh@yahoo.com per repo. ALWAYS git pull --rebase
both repos before working — BB-FIXUP pushed twice DURING this
session (391068f, 451bfd0).

## NEXT (order per Lon 2026-06-07-C; line numbers live-grepped at fec38d4)

1. **IRD-3d prolog** — ITE 312/333/354; γ-chained STRUCT 228/253 +
   g_builtin 271 arg lists (IRD-4 prereq; consumers incl. interp
   resolve 352 STRUCT walk + bb_atom_string.cpp BUILTIN sites,
   name-aware); name-aware BUILTIN pair 178/193/208; kind ~380.
2. **IRD-3e-rest icon** — ITERATE-bang 181, EVERY 346, UNTIL 423,
   REPEAT 436 (lower.c) + IR_PROC_GEN self-loop lower_program.c
   139/140.
3. **Bulk (c)** — ring BINOP/UNOP arms + interp tree reads, gz-synth,
   SCAN subject ruling, RETURN chain residue, operand_aux DELETED.
4. **IRD-4** → 5. **IRD-5**.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
