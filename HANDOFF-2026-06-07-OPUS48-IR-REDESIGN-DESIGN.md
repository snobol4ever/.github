# HANDOFF 2026-06-07 OPUS48 — IR-REDESIGN design session (Lon attending)

## What this session was

Design-only. NO SCRIP code changed (SCRIP working tree clean, no commit).
Produced GOAL-IR-REDESIGN.md (ratified design + IRD-1..5 ladder), committed
to .github at 7cb2a19e. PLAN.md goals table carries the IR REDESIGN row
(added 3c124a91).

## The ratified IR_t (Lon 2026-06-07)

```c
typedef struct { IR_t * node; char sz[4]; } IR_ref_t;   /* sz = literal "α"/"β" */
struct IR_t {
    IR_e       op;          /* operator — selects α/β templates */
    IR_ref_t   γ;           /* success wire */
    IR_ref_t   ω;           /* failure wire */
    IR_t    ** operands;    /* realloc array — boxes whose RESULT feeds this op */
    int        n_operands;
};
```

Five members, nothing else. This is the BB white-paper box physically:
operator + two outbound port wires + operand list.

## Decisions reached (the Q&A path — don't relitigate)

1. **t → op** (rename; tree_t already owns `t`).
2. **α/β are NOT fields.** A box's α and β are this node referenced at
   port "α"/"β" in someone else's IR_ref_t. The node IS its own α/β.
3. **γ/ω are INHERITED** (parent passes down); **α/β SYNTHESIZED** (the
   node's own blocks, materialized later by templates keyed on `op`).
   Code blocks live in TEMPLATES, not the IR — `op` encodes which.
4. **IR_ref_t carries the port name as a 4-byte UTF-8 string** (`sz[4]`),
   holding literal "α" or "β", NOT an int. Greek letter = 2 UTF-8 bytes
   (α=ce b1, β=ce b2, γ=ce b3, ω=cf 89), fits sz[4] with NUL. Compare via
   sz[1] (0xB1=α/0xB2=β) or strcmp. Use literal strings in code (IDE color);
   globals idea was raised then DROPPED by Lon.
5. **operands/n_operands, realloc array** (Lon-named). Each entry points to
   a child BB; the value read is that child's single RESULT. Arity 0..N is
   STRUCTURALLY required, proven from irgen.icn: 0=literals/Fail/Goto,
   1=unop, 2=binop, 3=sectionop x[i:j] (ir_a_Sectionop:353), N=Call argList
   / MakeList valueList. The old 4-pointer design capped operands at 2 and
   already needed operand_aux + γ-chained arg lists as workarounds.
6. **NO result field in IR_t.** Considered (DESCR_t, interp-only) then
   REJECTED by Lon: a graph carrying its own result is single-instance and
   breaks on recursion/re-entry. Interp and emitted code memory-manage the
   result themselves (frame slots / per-activation).
7. **lhs (JCON's explicit result slot in ir_OpFunction/ir_IntLit/ir_Var)
   becomes IMPLICIT** — a box's result slot is identified by the box's own
   identity; the parent's operands[] pointer to the child is the read side.
   JCON's slot economy (one tmp written by child, read by parent) collapses
   to identity in our model.

## Sidecar plan (where the deleted fields go)

- sval/ival/dval → IR_graph_t.lit[] (parallel, by idx). Literal payload.
- value/counter/state → IR_graph_t.exec[] (parallel, by idx). Runtime state
  (876 hits in IR_interp.c, 0 in emit_bb.c — proves it's interp-only).
- New `int idx` on IR_t, set at IR_node_alloc, keys both sidecars.
- KNOWN DEBT, do NOT fix mid-move: ival holds disguised heap pointers
  ((bb_choice_state_t*)(intptr_t)nd->ival etc.); dval holds mode flags
  (dval==1.0/2.0/3.0/5.0) AND to..by iterator state AND Pascal static-link
  depth AND the float literal. These MOVE with their field in IRD-2;
  cleanup is post-ladder.

## Ladder state (all OPEN — nothing landed)

- IRD-1 BREAKOUT — finish lower.c per-language split (SNO/SCO/REB/RKU/PAS
  still branch on cx.lang in lower.c, 1393 ln; icon+prolog already out).
  MUST be first: IRD-3/4 are per-language sweeps needing the files.
  IRD-1 and IRD-2 are mutually independent; only IRD-1→IRD-3 is hard-ordered.
- IRD-2 SIDECAR — payload + runtime state out.
- IRD-3 OPERANDS — α/β child-operands → operands[]; operand_aux folded+deleted.
- IRD-4 WIRES — γ/ω → IR_ref_t; α/β fields deleted; t→op.
- IRD-5 FENCE — grep gates, sizeof record, ARCH-IR.md.

Gate every rung on BYTE-IDENTICAL corpus baselines per language.

## Standing state certified (inherited HEAD, unchanged this session)

SCRIP HEAD a2aa3b5 (untouched). Per GOAL-ICON-BB watermark f86427a lineage:
m2 181 · m3 31 · m4 34. No build run this session (design-only).

## NEXT

IRD-1 (breakout). Build + smokes + per-language corpus baseline capture
BEFORE touching lower.c, so IRD-1's "byte-identical" gate has a reference.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
