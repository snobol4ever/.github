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

- [ ] **IRD-1 — BREAKOUT: finish per-language lower split.**
  lower.c (1393 ln) still serves SNO/SCO/REB/RKU/PAS via cx.lang branches.
  Split: lower_sno absorbs SNO+SCO arms, new lower_raku.c, new
  lower_pascal.c; lower.c keeps ONLY the shared spine (dispatch, wire
  helpers, tmp alloc). Icon+Prolog already out. NO semantic change.
  GATE: build green; smokes icon 12/12 prolog 5/5 broker >=25; corpus
  baselines byte-identical per language.

- [ ] **IRD-2 — SIDECAR: payload + runtime state out of IR_t.**
  Add to IR_graph_t parallel arrays keyed by node idx:
  `IR_lit_t *lit` {sval,ival,dval} · `IR_exec_t *exec` {value,counter,state}.
  Add `int idx` to IR_t (set at IR_node_alloc). Mechanical rewrite:
  nd->sval → LIT(g,nd).sval etc., nd->value → EXEC(g,nd).value etc.
  (accessor macros). ival-as-state-pointer and dval-as-mode-flag sites
  KEEP WORKING (they move with their field); flagged for later cleanup,
  not fixed here. GATE: build green; all smokes; baselines identical.

- [ ] **IRD-3 — OPERANDS: α/β children → operands[]/n_operands.**
  Add operands/n_operands to IR_t (realloc array; ir_operand_push()).
  Per-language sweep (one commit each: sno, icon, prolog, raku, pascal,
  program): every nd->α/nd->β CHILD-OPERAND use → operands[0]/[1];
  3+-ary and γ-chained arg lists → operands[2..n]. operand_aux callers
  fold in; operand_aux DELETED at sweep end. α/β fields still exist,
  now only as port-wire residue. GATE per language: baselines identical.

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
  sidecar; IR_t struct has exactly 5 members. Update ARCH-IR.md.

## DO NOT

- Touch chunk.h/.c or the JCON chunk-IR path (GOAL-ICON-IRGEN owns it).
- Fix ival-pointer / dval-flag abuses inside IRD-2 (move, don't fix).
- Reorder ladder: BREAKOUT FIRST (Lon 2026-06-07) — per-language sweeps
  in IRD-3/4 need the per-language files to exist.
- Change γ/ω SEMANTICS — only their carrier type.

## Watermark

**OPEN — design ratified + ladder written 2026-06-07 (Opus 4.8, Lon
attending). Design Q&A: result field REJECTED (multi-instance), lhs
recognized as JCON's explicit result slot → implicit via identity,
operands arity 0..N proven from irgen.icn (sectionop=3, call=N).
No steps landed. NEXT: IRD-1.**

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
