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
  (a) lower_prolog.c 11 writes: DISJ 117 first-arm; ITE cond
  312/333/354; STRUCT 228/253 + g_builtin 271 γ-CHAINED ARG LISTS
  (the IRD-4 "arg lists via ->γ" prereq); pair-shape BUILTIN
  178/193/208 — ⚠ BUILTIN is DUAL-ENCODED by builtin NAME (pair
  α/β vs γ-chain-from-α); its sweep must be name-aware across
  interp/emit/driver consumers; kind at ~380 (α=cα, ival=subgraph).
  (b) lower.c (shared) 7 single-child writes: DISJ 105, ITERATE
  182, CONJ 292, EVERY 347, WHILE 403, UNTIL 424, REPEAT 437 —
  consumers incl. v_every/interp EVERY bb->α/bb->β,
  while_cond_emittable(nd->α), flat_drive_every (its ival==2
  ASSIGN-gen branch at ~1892 is DEAD CODE — guard requires
  never-written ASSIGN->β).
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
  fallback). NEW RESIDUE FLAGS (bulk scope): IF/WHILE ->β reads are
  chain-shape then/body; while_cond_emittable INTERNAL cond->α/β
  reads are BINOP-child residue on a swept kind (pre-existing m3
  behavior preserved — do not "fix" inside a sweep). IRD-3e-2
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

**OPEN — SNO-ISO + IRD-3e-1 LANDED (2026-06-07-C, Opus 4.8, Lon
attending; prioritization directive: complete+isolated SNOBOL4
lower first).**
This session: 2f17bf4 (SNO-ISO-1 — lower_sno.c complete+isolated,
lower_value_shared SEVERED from the SNO route, full kind census
recorded in step text) + 5a40338 (IRD-3e-1 — IF/WHILE cond →
operands[0], consumers dual-read, three encoding regimes
lowered/chain/ring proven identical). GATE both: sno 153 / icn 9 /
pl 8 / pas 5 / sco 191 sweeps + rebus smoke + 4 smoke logs ALL
byte-identical vs pre-session baseline; prove_lower PASS rows
md5-identical (68; raw byte-diff is ASLR pointer noise in dump
rows — compare PASS/FAIL rows). sco sweep (191 .sc, test/snocone +
corpus/crosscheck/snocone) + rebus smoke ADDED to the gate set
alongside bake_ird3_baseline.sh.
Plus IRD-3e-2 RESOLVED-DEAD: DISJ->α zero readers, both writes
DELETED, gate identical — no DISJ cluster remains (aux fold =
bulk stage).
NEXT: IRD-3d prolog
remaining (ITE 313/334/355; γ-chained STRUCT 229/254 + g_builtin
272 arg lists; name-aware BUILTIN pair 179/194/209; kind ~381) →
IRD-3e-rest icon-scope shared sites (ITERATE-bang 182, EVERY 347,
UNTIL 424, REPEAT 437 — zero SNO hits) → bulk stage (c) → IRD-4 →
IRD-5. See
HANDOFF-2026-06-07-OPUS48-IR-REDESIGN-SNO-ISO-IRD-3E1.md.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
