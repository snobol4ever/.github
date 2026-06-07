# GOAL-IR-REDESIGN.md — IR_t = pure BB wiring: {op, γ, ω, operands}

**Owner repo:** SCRIP + this file. **Scope: ALL LANGUAGES** — IR_t is shared.

## TARGET SHAPE (Lon ratified 2026-06-07)

```c
typedef struct {
    IR_t  * node;
    char    sz[4];      /* literal "α" or "β" — the target block name */
} IR_ref_t;

struct IR_t {
    IR_e       op;          /* the operator — selects α and β templates */
    IR_ref_t   γ;           /* success wire → some box's α or β          */
    IR_ref_t   ω;           /* failure wire → some box's α or β          */
    IR_t    ** operands;    /* realloc array: boxes whose RESULT feeds this op */
    int        n_operands;
    int        idx;         /* sidecar key — lit[]/exec[] parallel arrays (Lon ruling 2026-06-07) */
    IR_graph_t * own;       /* owning graph — resolves idx for IR_LIT/IR_EXEC (Lon ruling 2026-06-07) */
};
```

Box = operator + two outbound port wires + operand list. NOTHING else.
A box's α/β are not fields — they are this node at "α"/"β" in someone's
IR_ref_t. Result value: NOT in IR_t (multi-instance; interp/emitted code
memory-manage it). Literal payload (sval/ival/dval): SIDECAR. Runtime
state (value/counter/state): SIDECAR or per-activation. Use literal "α"
"β" strings in code, never named constants (IDE color).

## RATIONALE RECORD

JCON ir_OpFunction(coord, lhs, fn, argList, failLabel) maps: fn→op,
failLabel→ω, success→γ, lhs→IMPLICIT (box's own result; identity names
the slot), argList→operands. Arity 0..N proven required: 0=literals,
1=unop, 2=binop, 3=sectionop x[i:j], N=call args/MakeList. γ/ω are
INHERITED attributes (passed down by parent); α/β are SYNTHESIZED (the
node's own blocks, selected by op). The 4-pointer α/β/γ/ω IR_t conflated
operand links, chain edges, port wires, and runtime state — 876
value/counter/state hits in IR_interp.c, 0 in emit_bb.c.

## LADDER — strict order, gate after each

- [ ] **IRD-3 — OPERANDS: α/β children → operands[]/n_operands.**
  SNO SWEPT (e070535). ICON SWEPT COMPLETE (4699ab8 cluster 1 +
  fbfd71c cluster 2 — lower_icon.c carries ZERO child α/β writes;
  CASE arm encoding NEW: cas->operands[0]=selector,
  operands[1..]=LIT_NUL wrappers each holding key/val in OWN
  operands, default wrapper = 1 operand — the IRD-4 "arm lists via
  ->ω" prereq is DONE for icon). PROLOG PAIR CLUSTER SWEPT
  (c6b09f5): UNIFY + ARITH kind-complete; emit ARITH/UNIFY marshal
  arms DUAL-READ (operands-first, α/β fallback) because the GZ
  SYNTHESIZER (driver/scrip.c pl_gz_*) writes α/β on synthesized
  CELL_UNIFY/DET_IS/DET_CMP/DET_WRITE/ARITH-copy nodes — gz-synth
  subsystem needs its own sweep entry in the bulk stage.
  SURVEY (2026-06-07-B): raku/pascal/sno/program lowering files
  carry ZERO child α/β writes — the per-language ladder collapses
  to lower_prolog.c + shared lower.c + the bulk stage. REMAINING:
  (a) lower_prolog.c 10 writes (LIVE-GREPPED at b2cfd08; DISJ 117
  DELETED-DEAD): ITE cond 312/333/354; STRUCT 228/253 + g_builtin
  271 γ-CHAINED ARG LISTS (the IRD-4 "arg lists via ->γ" prereq);
  pair-shape BUILTIN 178/193 + IS 208 — ⚠ BUILTIN is DUAL-ENCODED
  by builtin NAME (pair α/β vs γ-chain-from-α); its sweep must be
  name-aware across interp/emit/driver consumers; kind at 380
  (α=cα, ival=subgraph). NOTE 427/428 zc->args[]=aaα are local-α
  captures into the zc args array, NOT IR_t child-field writes.
  (b) lower.c (shared) 4 single-child writes remain, ALL
  icon-scope (zero SNO hits, census-proven): ITERATE-bang 181,
  EVERY 346, UNTIL 423, REPEAT 436 — consumers incl. v_every/
  interp EVERY bb->α/bb->β, flat_drive_every (its ival==2
  ASSIGN-gen branch at ~1892 is DEAD CODE — guard requires
  never-written ASSIGN->β). DONE: DISJ 105 deleted-dead; WHILE +
  IF swept 5a40338 (the old "CONJ 292" entry was MISLABELED — it
  was the wire_if site; no CONJ child write ever existed; UNTIL
  rides the while_cond_emittable α fallback until its sweep).
  (c) BULK consumer-internal α/β classification: IR_interp.c +
  emit_bb.c residue; the THREE emit-time RPN α/β writers
  (descr_chain_operand_refs, gvar_stmt_operand_refs emit_bb.c;
  icn_ring_to_tree driver/scrip.c) + their chain consumers;
  gz-synth nodes; RETURN chain residue (descr_chain_arity RETURN
  STAYS 1 — chain codegen slot-priming consumes the RPN α,
  empirically proven at fbfd71c: arity→0 broke proc m3 rows).
  CENSUS LAW (fbfd71c lesson): driver/scrip.c classifiers
  (icn_local_assign_rhs_ok, icn_graph_native_emittable_mode,
  pl_flat_goal_is_simple, pl_gz_*) ARE consumers — census every
  kind in driver/ too, and never truncate the consumer grep.
  bb_child0 (emit_bb.c) = the dual-read accessor for kinds where
  chain-RPN α coexists with lowering operands.
  SNO-ISO LANDED (2f17bf4, Lon directive 2026-06-07-C): lower_sno.c
  is COMPLETE+ISOLATED — own sno_value_shared dispatch, default →
  lower_unhandled, ZERO lower_value_shared reachability from the
  SNO route; 15 shared v_* helpers exported in lower_internal.h as
  infrastructure. CENSUS (sno 153 + sco 191 + rebus): only lang=1
  fires (sco/rebus transpile through SNO); SNO-live α-writers were
  IF/WHILE/ALT-DISJ only; UNTIL/REPEAT/EVERY/ITERATE-bang have
  ZERO SNO hits (icon-scope). IRD-3e-1 LANDED (5a40338): IF + WHILE
  cond → operands[0]; consumers dual-read (interp IF/WHILE arms via
  cnd accessor + ring-guard extension; emit while_cond_emittable
  CALLSITE + flat_drive_while via bb_child0 — UNTIL rides the α
  fallback). RESIDUE FLAGS (bulk scope): interp IF/WHILE ->β then/body
  reads have ZERO writers in src (write census 2026-06-07-D) —
  verify-then-delete candidates, NOT chain-fed; while_cond_emittable
  internals CONVERTED in IRD-3-CHAIN-1 (d20c45e, jointly with the
  writer flip). IRD-3e-2
  RESOLVED-DEAD: DISJ->α had ZERO readers (census + behavioral
  proof, both producer writes DELETED — wire_alt + pl_wire_alt);
  arms flow via operand_aux only, folds to operands[] at the bulk
  stage with the operand_aux deletion. No DISJ cluster remains.
  operand_aux callers fold in; operand_aux DELETED at sweep end.
  GATE per cluster: scripts/bake_ird3_baseline.sh sweeps
  byte-identical; smoke rows identical; prove_lower PASS count
  (68); live-kind probes per kind; A/B git-stash for any anomaly.

- [ ] **IRD-4 — WIRES: γ/ω become IR_ref_t; α/β fields DELETED.**
  Change IR_t.γ/ω from IR_t* to IR_ref_t{node, sz}. Every wire write
  states its target block: strcpy(r.sz,"α") fresh-entry, "β" resume
  (conjunction right-ω→left-β, every body→expr-β, etc. per irgen.icn).
  Interp/emitter follow ref.node + dispatch on ref.sz[1] (0xB1/0xB2).
  Chain-edge abuses of γ/ω (arm lists via ->ω, arg lists via ->γ)
  already migrated in IRD-3. DELETE α/β fields; rename t→op.
  GATE: build green; full suites; grep '->t\b' == 0 in IR consumers;
  baselines identical.

- [ ] **IRD-5 — FENCE: audit + doc.**
  sizeof(IR_t) recorded before/after. Grep gates: no ->value/->counter/
  ->state outside exec sidecar; no ->sval/->ival/->dval outside lit
  sidecar; IR_t struct has exactly 7 members (5 ratified + idx/own
  sidecar key, Lon ruling 2026-06-07). Update ARCH-IR.md.

## DO NOT

- Touch chunk.h/.c or the JCON chunk-IR path (GOAL-ICON-IRGEN owns it).
- Fix ival-pointer / dval-flag abuses inside IRD-2 (move, don't fix).
- Reorder ladder: BREAKOUT FIRST (Lon 2026-06-07) — per-language sweeps
  in IRD-3/4 need the per-language files to exist.
- Change γ/ω SEMANTICS — only their carrier type.

## Watermark

**OPEN — IRD-3-CHAIN-1 LANDED (2026-06-07-D, Opus 4.8, Lon
attending; directive: SNOBOL4 COMPLETELY CONVERTED FIRST —
operands[]/n_operands used everywhere on the SNO route, α/β
child-stuffing eliminated; a concurrent session is designing
pattern-build BBs — keep commits small and pushed for cheap
rebases).**
Prior (2026-06-07-C): 2f17bf4 SNO-ISO (lower_sno.c isolated, zero
α/β writes) + 5a40338 IF/WHILE cond → operands[0]; DISJ->α
resolved-dead.
This session: d20c45e IRD-3-CHAIN-1 — both emit-time RPN chain
writers (descr_chain_operand_refs, gvar_stmt_operand_refs) now
fill operands[0..1] (reset+push, idempotent); α/β chain writes
DELETED except two flagged residues: IR_CALL (α+γ-chained arg
lists) and IR_SCAN (gvar subject α — operands hold IRD-3a
subj/repl GRAPHS, so generic operand-first EXEMPTS SCAN).
Consumers operand-first/dual-read: bb_child1 added beside
bb_child0; flat_drive_binop_tree/binop_gen_tree/unop/to; gvar
IR_BINOP case block; binop_operand_streams + gen_bb_is_gen_arg +
ASSIGN β-walks; while_operand_simple + while_cond_emittable
internals; emit_core.c op_a_* generic priming block (THE central
template operand feed — the hidden SCAN-α consumer, falsifying
the earlier no-reader read) + bb_walk_rec now walks operands[]
SCAN-guarded (its α/β-only walk was the live break: operand-held
literals never interned → empty .rodata strings; smoke-RED,
pinned by A/B asm diff, fixed). interp UNTOUCHED — writer output
is emit-only; interp α/β tree reads serve icn_ring_to_tree (icon
scope). GATE: sno 153 / icn 9 / pl 8 / pas 5 / sco 191 sweeps +
5 smokes (rebus incl.) byte-identical; prove_lower 68. sco sweep
+ rebus smoke folded INTO scripts/bake_ird3_baseline.sh.
SNO STATUS: lowering carries ZERO α/β stuffing (SNO-ISO) and the
chain ecosystem is operands-first ⇒ SNOBOL4 is fully converted
in usage EXCEPT the arg-list sub-cluster: IR_CALL args (writer
α/β for 1-2-arg + α-headed γ-chain walks in
flat_drive_call_userproc/call_builtin/call_args_single_shot,
gvar_drive_call_arg_slots, interp CALL arms ~2400-2454 +
ir_is_single_shot ~287-299, templates bb_call.cpp:487 +
bb_call_write_slot.cpp:35/67) and IR_SCAN subject α (gvar writer
+ op_a/bb_walk_rec exemptions). CAUTION: icn_ring_to_tree
(driver/scrip.c 85-92) builds the SAME CALL/arg shapes for icon
ring trees — CHAIN-2 must convert it in lockstep or keep
dual-read walkers. α/β FIELD DELETION stays global at IRD-4
(IR_t shared) — SNO reaches zero-USAGE first, struct change
lands once icon/prolog catch up.
NEXT: IRD-3-CHAIN-2 arg-list sub-cluster = SNO 100%. CENSUS
PINNED (2026-06-07-D): NO multi-arg arg-chain builder exists —
the γ hops in CALL arg walks are pre-existing statement-flow
wires; CALL->α is only a first-arg marker written by the 3 RPN
writers (descr/gvar: ar 1-2 only, ar>=3 resets sp and wires
NOTHING; icn_ring_to_tree driver/scrip.c:83 hard-rejects ar!=1).
lower.c γ writes are all control wires; lower_sno.c has zero.
gvar dval 2/3/5 CALL shapes carry args as counter-held csubs
subgraphs (arity 0, untouched). PLAN: writers push ar∈{1,2} args
as operands[0..ar-1] (stack already holds them, order
stk[sp-2],stk[sp-1]); ring_to_tree pushes operands[0] lockstep;
walkers (flat_drive_call_userproc/call_builtin/
call_args_single_shot/call_intexpr, gvar_drive_call_arg_slots,
interp CALL arms ~2400-2454, ir_is_single_shot ~287-299) get an
ir_call_arg(bb,j) dual-read (operands[j] else α/γ-hop);
templates bb_call.cpp:487 + bb_call_write_slot.cpp:35/67 read
operands[0]-else-α — COORDINATE: BB-FIXUP session owns
BB_templates (cursor bb_scan_many.cpp per its 15th-run handoff).
SCAN subject channel: decide layout against IRD-3a graph slots
(transcript 2026-06-07 has exact SCAN operand map) — candidate:
keep SCAN-α as port-style wire until IRD-4, since op_a +
bb_walk_rec already carry the SCAN exemption. → IRD-3d prolog
remaining (ITE 313/334/355; γ-chained STRUCT 229/254 + g_builtin
272 arg lists; name-aware BUILTIN pair 179/194/209; kind ~381) →
IRD-3e-rest icon-scope shared sites (ITERATE-bang 182, EVERY 347,
UNTIL 424, REPEAT 437 — zero SNO hits; + IR_PROC_GEN self-loop
lower_program.c 139/140; + icn_ring_to_tree if not folded into
CHAIN-2) → bulk stage (c) (gz-synth, operand_aux deletion) →
IRD-4 → IRD-5. Detail in commit d20c45e message.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
