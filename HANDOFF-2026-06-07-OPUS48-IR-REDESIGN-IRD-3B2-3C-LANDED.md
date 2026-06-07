# HANDOFF 2026-06-07-B OPUS48 — IR-REDESIGN: IRD-3b-2 ICON CONTROL + IRD-3c PROLOG PAIR LANDED

## Commits (SCRIP origin/main)

- `fbfd71c` IRD-3b-2 icon control cluster (ASSIGN/RETURN/INITIAL/LIMIT/CASE)
- `c6b09f5` IRD-3c prolog pair cluster (UNIFY/ARITH)

Both rebased over the parallel FIXUP lap (…`28b0c52`) and re-gated
green on the merged tree before push.

## What moved

IRD-3b-2 (icon, 5 kinds — lower_icon.c now carries ZERO child α/β
writes): icn_assign rhs → operands[0]; icn_return value →
operands[0], PLUS pascal PRET→PVAR push (lower_program.c) and sno
RET/FRET dead `α=NULL` writes dropped — RETURN is kind-complete
across all three lowering producers; icn_initial body entry →
operands[0]; icn_limit body/count → operands[0..1]; icn_case
REWIRED — selector → operands[0], each arm a LIT_NUL wrapper in
operands[1..] holding key/val in its OWN operands (default wrapper
= 1 operand); the γ-key/β-val/ω-next chain abuses are DELETED
(IRD-4 "arm lists via ->ω" prereq done for icon). Consumers:
interp RETURN/INITIAL/LIMIT/CASE arms + emit
flat_drive_return/initial/limit/case operand-direct; all ASSIGN
consumers (dispatch arm, flat_drive_assign / gvar_assign /
gvar_assign_binop / icn_global_assign, binop_tree assign-peeks,
the dead every-1892 branch, driver icn_local_assign_rhs_ok) via
new `bb_child0` dual-read.

IRD-3c (prolog, 2 kinds): both UNIFY producers (g_unify,
g_head_unify) → operands[0..1]; ARITH args → in-order pushes.
Consumers: interp resolve_node_to_term / resolve_arith_eval ARITH
arms + IR_UNIFY arm operand-direct; emit ARITH and
UNIFY/CELL_UNIFY marshal arms DUAL-READ; driver gz path — every
read of LOWERED unify/arith children converted across
pl_flat_goal_is_simple, fact/rule head-unify scans,
rule_callee_body synth sources, single-goal synth sources,
pl_gz_arith_slot_map, pl_gz_arith_const, pl_gz_admit UNIFY checks,
STRUCT parent-unify scan, pl_rich_is_lint_simple,
pl_findall_term_buildable, rich UNIFY guard. BUILTIN-child α/β
reads deliberately untouched (not this cluster).

## Census results (verified, reusable — recorded in goal step too)

1. **ASSIGN->β has ZERO writers.** gen_resume_target's ASSIGN
   recursion, flat_drive_limit's ASSIGN skip-walk, and the
   flat_drive_every ival==2 branch guard all read a
   permanently-NULL field; the every-1892 branch is DEAD CODE.
2. **descr_chain_arity IR_RETURN must stay 1.** Setting it 0 broke
   proc_zeroarg/proc_recursion m3 — the descr-chain codegen's slot
   priming consumes the RPN-written α. Chain ecosystem α residue is
   bulk-stage scope (same class as ASSIGN's chain α).
3. **THREE emit-time RPN α/β writers exist**, not two:
   descr_chain_operand_refs + gvar_stmt_operand_refs (emit_bb.c)
   AND `icn_ring_to_tree` (driver/scrip.c, AG-ring trees; its arity
   table is inert for all kinds swept so far).
4. **gz synthesizer subsystem** (driver pl_gz_*): writes α/β on
   synthesized CELL_UNIFY/DET_IS/DET_CMP/DET_WRITE/ARITH-copy
   nodes feeding the shared emit marshal arms — hence those arms
   are dual-read. CELL_UNIFY has zero LOWERING producers. The
   subsystem needs its own bulk-stage sweep entry.
5. **BUILTIN is dual-encoded by builtin name**: pair shape (α/β —
   cmp/is sites lower_prolog.c 178/193/208) vs γ-chain-from-α
   (g_builtin 271). Its sweep must be name-aware in
   interp/emit/driver simultaneously.
6. **driver/scrip.c classifiers ARE consumers**
   (icn_graph_native_emittable_mode → icn_local_assign_rhs_ok was
   the live EXCISE break; pl_flat_goal_is_simple; pl_gz_*). Census
   every kind in driver/ too — and never `head`-truncate the
   consumer grep (the first prolog census missed ~10 gz sites that
   way).
7. **bb_child0** (static, emit_bb.c): `operands[0] if n_operands>0
   else α` — the dual-read accessor for kinds where chain-RPN α
   coexists with lowering operands.
8. ARITH operand encoding is positional in-order push; parser
   guarantees pairwise child presence (binary ops), unary is ar==1.

## Gate procedure

scripts/bake_ird3_baseline.sh at pre-change HEAD → edit → bake →
diff: 4 m2 per-file sweeps byte-identical (sno 153 / icn 9 / pl 8 /
pas 5), prove_lower 68 PASS, all 4 smoke row-sets identical
(`[m[234] (PASS|FAIL)]` rows). Live-kind proof per kind: rung33
case ×5 m2 (incl. no_default fail semantics), initial-twice probe,
return probe, assign via while/until m3 PASS rows, prolog
head-unify+body-unify+nested-arith probe m2 = 70. Anomalies
resolved by A/B `git stash` at pre-change HEAD before classifying.

## Environment (fresh container)

apt-get install -y libgc-dev; make; `make libscrip_rt` MANDATORY
before any m4 work. Icon probe dialect: semicolons after
statements, single-name `local`, copy from corpus rung fixtures.

## Law-5 flags (A/B-stash-proven pre-existing, NOT chased)

- icon LIMIT m2 over-generates: `every write(1 to 9 \\ 3)` prints
  1..9 ×3 — interp transcription diverges from JCON
  ir_a_Limitation counter semantics.
- icon LIMIT m3 FATAL-aborts on LIT-headed generator entry
  (flat_drive_limit generator-kind gate).
- icon CASE m3 segfault: flat_drive_case walks a γ-list shape
  icn_case never built (desynced pre-IRD; rung33 m3 rc=139).
- prolog 2-arg rule-call probe (`add7`) not gz-admitted in m3
  (PBB FATAL fence) at pre-change HEAD too.
- Carried: RAKU "main BB graph not found" all modes (owner
  RAKU-BB); rung36_jcon_lists/string1 m2 FAIL; pat_rung 053 m4
  SKIP; icon proc_zeroarg/proc_recursion m3/m4 smoke FAIL.

## NEXT — IRD-3d/3e (survey 2026-06-07-B: raku/pascal/sno/program
lowering files carry ZERO child α/β writes)

(d) lower_prolog.c 11 writes: DISJ 117; ITE 312/333/354; γ-chained
STRUCT 228/253 + g_builtin 271 arg lists (IRD-4 prereq);
name-aware BUILTIN pair sites 178/193/208; kind at ~380.
(e) shared lower.c 7 single-child writes: DISJ 105, ITERATE 182,
CONJ 292, EVERY 347, WHILE 403, UNTIL 424, REPEAT 437 — consumers
incl. v_every/interp EVERY bb->α/β, while_cond_emittable(nd->α).
Then the bulk consumer-internal classification (IR_interp.c +
emit_bb.c residue, three RPN writers + chain consumers, gz-synth,
RETURN chain residue) → IRD-4.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
