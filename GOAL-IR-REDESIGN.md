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
  STATUS: sno/icon/raku/pascal/program lowering files carry ZERO
  child α/β writes; prolog pair-cluster, IF/WHILE cond, SNO-ISO and
  the chain-writer flip are LANDED (history + encoding specs in
  commits e070535, 4699ab8, fbfd71c, c6b09f5, 2f17bf4, 5a40338,
  d20c45e). REMAINING:
  (a) lower_prolog.c 7 writes (LIVE-GREPPED at c03d46b; ITE
  312/333/354 DONE → operands[0]): STRUCT 228/253 + g_builtin 271
  γ-CHAINED ARG LISTS
  (the IRD-4 "arg lists via ->γ" prereq); pair-shape BUILTIN
  178/193 + IS 208 — ⚠ BUILTIN is DUAL-ENCODED by builtin NAME
  (pair α/β vs γ-chain-from-α); its sweep must be name-aware
  across interp/emit/driver consumers; PAIR-NAME SET BANKED
  (routing lower_prolog.c ~495-511): g_compare < > =< >= =:= =\=
  · g_is is · g_term_compare == \== @< @> @=< @>= succ; ALL else
  γ-chains via g_builtin. Pair needs NEW ir_pair_arg(nd,j)
  (operands-first else j?β:α) — ir_call_arg fallback WRONG for
  pair arg1 (lα->γ wires into arith-subgraph internals); γ-chain
  reuses ir_call_arg as-is. Driver ~517 guard (ival==2 && α && β)
  shape-sniffs by β-presence — name set (is_cmp) must gate
  post-conversion; return-0 semantics proven equal both regimes.
  kind at 380 (α=cα,
  ival=subgraph; interp 4763 bb->α + driver 1242 zc->catcher
  sidecar). NOTE 427/428 zc->args[]=aaα are local-α captures
  into the zc args array, NOT IR_t child-field writes.
  (b) lower.c (shared) 4 single-child writes, ALL icon-scope (zero
  SNO hits, census-proven): ITERATE-bang 181, EVERY 346, UNTIL
  423, REPEAT 436 — consumers incl. v_every / interp EVERY
  bb->α/bb->β, flat_drive_every (its ival==2 ASSIGN-gen branch
  ~1892 is DEAD — guard requires never-written ASSIGN->β); UNTIL
  rides the while_cond_emittable bb_child0 fallback until its
  sweep. PLUS IR_PROC_GEN self-loop lower_program.c 139/140
  (icon, GeneratorState sentinel).
  (c) BULK remaining: icn_ring_to_tree (driver/scrip.c) BINOP/
  UNOP/EVERY arms still write α/β — its CALL arm CONVERTED to
  operands[0] at CHAIN-2 — plus the interp tree reads those ring
  shapes serve (BINOP ~2598 / UNOP ~2712 / SEQ ~2508 — icon/raku
  scope); SCAN subject α (gvar writer ONLY — SCAN operands hold
  IRD-3a type-punned subj/repl GRAPHS so the slot map is a
  pattern-BB joint ruling; op_a, bb_walk_rec and both chain
  writers carry the SCAN exemption);
  gz-synth (driver pl_gz_* writes α/β on synthesized CELL_UNIFY/
  DET_IS/DET_CMP/DET_WRITE/ARITH-copy nodes — emit marshal arms
  already dual-read); operand_aux callers
  fold in; operand_aux DELETED at sweep end. RETURN chain:
  descr_chain_arity RETURN STAYS 1 — the slot-priming consumer is
  emit_core.c:440 dual-read (arity→0 empirically broke proc m3 at
  fbfd71c).
  LAWS: census every kind in driver/ too — classifiers ARE
  consumers; never truncate the consumer grep (fbfd71c). Generic
  WALKERS and the generic op_a_* template feed are consumers
  (d20c45e RED cycle: bb_walk_rec missed operand-held literals →
  empty .rodata strings; op_a_* was the hidden SCAN-α reader —
  same-line greps lie for switch-case consumers). Any walker over
  operands[] MUST exempt IR_SCAN (operands hold IRD-3a subj/repl
  GRAPHS cast as IR_t*). bb_child0/bb_child1 (emit_bb.c) = the
  dual-read accessors.
  RESIDUE FLAGS (bulk scope): interp IF/WHILE ->β then/body reads
  have ZERO writers in src (write census 2026-06-07-D) —
  verify-then-delete candidates, NOT chain-fed.
  GATE per cluster: build = apt-get install -y libgc-dev; make;
  make libscrip_rt (MANDATORY for m4). Bake
  scripts/bake_ird3_baseline.sh BEFORE touching code (script now
  includes sco sweep 191 + rebus smoke; rebus PASS=0 FAIL=4
  pre-existing); post-bake and diff: all sweeps byte-identical;
  smoke rows identical; prove_lower PASS count (68); live-kind
  probes per kind; A/B git-stash for any anomaly.

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

**OPEN — IRD-3d-ITE LANDED (2026-06-07-F, Opus 4.8, Lon
attending): prolog ITE cond-entry α → operands[0]; merged tree
re-gated green over Lon's DUMP-V2 d3907e8.**
This session: SCRIP c03d46b — writers g_ite/g_neg_goal/g_not_unify
(lower_prolog.c 312/333/354) ite->α=cα DELETED → ir_operand_push;
sole runtime reader interp case IR_ITE → ir_call_arg(bb,0)
dual-read (resume path reads zi->then_/else_ sidecar, untouched).
Census-proven invariant: emit flat_drive_ite + ALL driver gz/flat
ITE classifiers read the zi SIDECAR — zero α; op_a priming already
operands-first (same node); ir_is_single_shot walks α AND β AND
operands; bb_ite.cpp port-free; zero IR_ITE in m4 marshal outside
emit_bb/emit_core.
GATE: sno 153/icn 9/pl 8/pas 5/sco 191 sweeps + 5 smokes + rebus
BYTE-IDENTICAL pre/post AND re-baked green on the merged tree
post-rebase; prove_lower PASS=68, git-stash A/B dump diff EXACTLY
the ITE α column (8→-1, 7→-1; ITE rows' node-count FAILs
pre-existing, identical both sides); live-kind probe
(scratch-instrumented) [ITE-LIVE ops=1]×2 m2 with correct lt/ge;
m4 asm probe ITE arms live via sidecar; m3 ->-probe rejection
(pl_gz_admit no-blob FATAL) A/B-PROVEN PRE-EXISTING at c9e018e
(LAW-5, not chased).
LAWS RECORDED: (1) prove_lower ival column prints sidecar
POINTERS — ASLR noise, md5 INVALID for prolog rows, STRUCTURAL
diff is the comparator. (2) prove_lower.sh RECOMPILES lower*.c
from source — a post-edit bake contaminates its prove_lower log
even with a stale binary; git-stash A/B for the true pre dump.
(3) Background jobs are REAPED between tool calls — run
bake_ird3_baseline.sh FOREGROUND (~2-3 min).
DUMP-V2 COORDINATION (Lon d3907e8, mid-session): print_port
DELETED, --dump-bb one-line revamp, α/β dump columns dropped
(dying fields), PORT-LAW idx+entry-letter until IRD-4
IR_ref_t.sz; lower_sno verified 0 α/β. Anticipates IRD-4.
NEXT (Lon 2026-06-07-C order; ITE done):
1. IRD-3d remainder — γ-chained STRUCT 228/253 + g_builtin 271
arg lists (IRD-4 prereq; consumers: interp resolve 352 STRUCT
walk + case IR_STRUCT 4725, ~40 builtin a0/a1/a2 γ-hop sites
interp 4836-5500 incl. a1->α at 5055 = nested-STRUCT arg0,
bb_atom_string.cpp BUILTIN sites, driver classifiers ~293-335 /
505-523 + gz-synth LOWERED-node reads 617-700 — name-aware per
banked census in IRD-3(a)); then pair-shape 178/193/208 (NEW
ir_pair_arg, see IRD-3(a)); then kind 380 g_catch.
2. IRD-3e-rest icon-scope — ITERATE-bang 181, EVERY 346, UNTIL
423, REPEAT 436 (lower.c) + IR_PROC_GEN self-loop
lower_program.c 139/140.
3. Bulk stage (c) — ring BINOP/UNOP arms + interp tree reads,
gz-synth SYNTHESIZED-node writes, SCAN subject ruling, RETURN
chain residue, operand_aux DELETED.
4. IRD-4 → 5. IRD-5.
HANDOFF 2026-06-07-F CLOSED (Opus 4.8): SCRIP origin = c03d46b,
.github origin = this commit; both trees CLEAN, all pushed. See
HANDOFF-2026-06-07-OPUS48-IR-REDESIGN-IRD-3D-ITE.md. Next
session: clone/pull BOTH repos (authenticate origin with Lon's
token: git remote set-url origin
https://TOKEN@github.com/snobol4ever/<repo>), git identity
LCherryholmes/lcherryh@yahoo.com per repo, apt-get install -y
libgc-dev; make; make libscrip_rt (MANDATORY for m4), bake
scripts/bake_ird3_baseline.sh /tmp/base_pre FOREGROUND BEFORE
touching code, then IRD-3d remainder per NEXT. Concurrent
sessions: BB-FIXUP (owns BB_templates, rebase before touching
bb_*.cpp) and pattern-BB design (joint owner of the SCAN-subject
ruling). ALWAYS git pull --rebase both repos before working.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
