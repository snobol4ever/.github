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

- [ ] **IRD-3 — OPERANDS: α/β children → operands[]/n_operands.**
  Scaffold LANDED (operands/n_operands on IR_t, calloc-zeroed;
  ir_operand_push() in scrip_ir.c). REMAINING: per-language sweep
  (one commit each: sno, icon, prolog, raku, pascal, program): every
  nd->α/nd->β CHILD-OPERAND use → operands[0]/[1]; 3+-ary and
  γ-chained arg lists → operands[2..n]. operand_aux callers fold in;
  operand_aux DELETED at sweep end. α/β fields still exist, now only
  as port-wire residue. SIZING (audited 2026-06-07): consumers carry
  the bulk — IR_interp.c 387 + emit_bb.c 320 ->α/->β touches,
  lower_icon.c 23, lower_prolog.c 20, lower.c 7, lower_program.c 5,
  lower_sno.c 2; 34 operand_aux call sites. Each touch needs
  classifying child-operand vs port-wire-residue per op kind.
  GATE per language: baselines identical.

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

**OPEN — IRD-1 LANDED, IRD-2 VERIFIED COMPLETE, IRD-3 SCAFFOLDED
(2026-06-07, Opus 4.8, Lon attending).**
IRD-1: 6961de3 (split) + 92422d9 (drain) this session, merged over
parallel closeout 293b1d0 (prove_lower.sh repair + bb_label registry
to spine); merged HEAD 9fc612a re-verified green (build, icon 12/12,
prolog 5/5, raku 25/25, prove_lower 68 PASS, baselines identical).
NAMING CONTRACT (Lon 2026-06-07): AG signature is
`f(lcx_t cx, const tree_t * e, IR_t * γ, IR_t * ω, IR_ref_t * α,
IR_ref_t * β)` — no _in/_out suffixes. `lower` = canonical
new-signature dispatcher (ICN→lower_icn, SNO/SCO/REB→lower_sno,
RKU→lower_rku, PAS→lower_pas, PL+default→role switch via iref()).
`lower_program` = old-signature (IR_t** α/β) thin unwrap wrapper over
lower; all legacy call sites renamed. stage2_t* lower_program →
lower_stage2 (name freed; 1 caller scrip_sm.c; Lon may rename).
lower.c = pure spine: cx.lang only in dispatch + IR_alloc tag;
wire_if(else_succeeds) exported (RKU/PAS pass 1 = else→γ);
PAS bool-diamond moved whole into lower_pascal.c (b1/b2 checked
BEFORE node alloc — preserves node order).
IRD-2: sidecars/idx/IR_LIT/IR_EXEC pre-existed at HEAD (prior
session); audit 9fc612a confirms zero stragglers (all ->ival hits are
prolog Term*). KNOWN: dump-bb prints GCONJ ival heap ptr → prolog
baselines need ival-ptr masking; test_lower_byte_identical.sh uses
removed --dump-sm (vacuous baseline) — rewrite to --dump-bb.
RULING NEEDED (Lon): ratified 5-member IR_t has no idx/own, but
sidecars key on idx and macros walk own — IRD-5 fence vs sidecar
mechanism in tension. NEXT: IRD-3 sweep, sno first. Per-language
helpers (sno_conj, v_raku_*, pas_*) migrate to the 5-param signature
during their language's sweep. See
HANDOFF-2026-06-07-OPUS48-IR-REDESIGN-IRD-1-2-LANDED.md.**

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
