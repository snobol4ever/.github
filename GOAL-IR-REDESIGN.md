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

**OPEN — IRD-3 ICON COMPLETE + PROLOG PAIR CLUSTER LANDED
(2026-06-07-B, Opus 4.8, Lon attending).**
This session: fbfd71c (IRD-3b-2 icon control cluster —
ASSIGN/RETURN/INITIAL/LIMIT/CASE producer+consumer; CASE arm chain
flattened to operand wrappers; RETURN kind-complete across
icon+pascal+sno producers) + c6b09f5 (IRD-3c prolog pair cluster —
UNIFY/ARITH kind-complete incl. the full gz driver classifier set).
Both gated on the merged tree over the parallel FIXUP lap
(…28b0c52): 4 m2 per-file sweeps byte-identical ×175, prove_lower
68 PASS, all 4 smoke row-sets identical; live-kind probes per kind.
CENSUS RESULTS RECORDED IN STEP TEXT (do not re-derive): ASSIGN->β
zero writers / every-1892 dead; RETURN chain arity stays 1; three
RPN writers; gz-synth subsystem; BUILTIN dual-encoding; driver
classifiers are consumers; bb_child0 dual-read pattern.
ENV (fresh container): apt-get install -y libgc-dev; make;
make libscrip_rt MANDATORY before any m4 (else vacuous link fails).
LAW-5 PRE-EXISTING (A/B git-stash-proven this session, NOT chased):
icon LIMIT m2 over-generates (every write(1 to 9 \\ 3) prints 1..9
×3 — interp transcription diverges from JCON ir_a_Limitation
counter); icon LIMIT m3 FATAL-aborts on LIT-headed generator entry
(flat_drive_limit kind gate); prolog 2-arg rule-call probe (add7)
not gz-admitted m3 (PBB FATAL fence) — all byte-identical at
pre-change HEAD. CARRIED from prior session: RAKU "main BB graph
not found" all modes (owner RAKU-BB); rung36_jcon_lists/string1 m2
FAIL; pat_rung 053 m4 SKIP; icon proc_zeroarg/proc_recursion m3/m4
smoke FAIL; icon CASE m3 segfault (flat_drive_case walks a γ-list
shape icn_case never built — desynced pre-IRD, rung33 m3 rc=139).
NEXT: IRD-3d prolog remaining (DISJ/ITE first; then the γ-chained
STRUCT/g_builtin arg lists; then name-aware BUILTIN pair sites;
site ~380) → IRD-3e shared lower.c 7 sites → bulk stage (c) →
IRD-4. See
HANDOFF-2026-06-07-OPUS48-IR-REDESIGN-IRD-3B2-3C-LANDED.md.**

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
