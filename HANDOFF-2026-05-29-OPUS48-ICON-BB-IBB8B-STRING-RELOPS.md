# HANDOFF — ICON-BB IBB-8b — STRING RELOPS IN IF-CONDITION (partial)

**Author:** Claude Opus 4.8
**Date:** 2026-05-29
**Goal:** GOAL-ICON-BB.md, rung IBB-8 (front: relop in if-condition)
**SCRIP:** `0e926c16` (on origin/main, rebased over Prolog `baf8397d`)
**Repos touched:** SCRIP (5 files + 1 new), .github (PLAN.md, GOAL-ICON-BB.md, this doc)

---

## What landed

String relops in an Icon `if`/`while` condition now compile and run in mode-3,
byte-identical to mode-2 with zero SM opcodes.

Same-sweep mode-3 corpus (`/home/claude/corpus/programs/icon`, m2-OK filter):
**22 -> 28 PASS (+6), SEGV 0 -> 0, ABORT 141 -> 133.** Zero regressions.

Newly passing: `rung12_strrelop_size_{slt,sge,sne}`, `rung37_strrelop_hello`,
`rung07_control_seq`, and the canonical `if_expr` crosscheck.

## The IBB-8 diagnosis was partly wrong — corrected here

The prior handoff proposed a `flat_drive_if(pBB)` that walks a cond chain hung off
the BB_IF node. **That is unworkable:** BB_IF carries no pointer back to the cond
chain (the chain entry is returned to the parent as `*alpha_out` during lowering,
never stored on the node), and the PEERS RULE forbids adding a field to BB_t.

Actual topology (verified by a temporary BB-graph dump): `if (relop) then T else E`
lowers to a branching CFG flattened into the enclosing **BB_SEQ** gamma-chain:

```
cond_entry --gamma-chain--> relop(BB_BINOP, alpha=beta=NULL, state=1, gamma==omega==BB_IF)
                                                                         |
                                          BB_IF(alpha=beta=NULL): gamma=then-entry, omega=else-entry
```

- The relop's gamma AND omega both point at BB_IF (mode-2 BB_BINOP AG-pure arm returns
  gamma on success / omega on relop-false, but `lower_icn_new_If_ag` wires both to BB_IF;
  the *value* on the ring carries success, which BB_IF peeks).
- With no `else`, BB_IF.omega points at the **next statement's** cond entry — then/else
  reconverge by fall-through, there is no join node.
- Mode-2's BB_SEQ oracle is itself a per-node CFG walk: each stmt's gamma AND omega both
  advance (Icon compound semantics — success or failure both proceed).

## Implementation (3 pieces, all template-pure / FACT-clean)

1. **`bb_binop.cpp`** — added an AG-pure relop/strrel apply arm. When `pBB->ival` is a
   relop (ICN_BINOP_LT..NE) or string-relop (ICN_BINOP_SLT..SNE), emit
   `movabs rdi, tt_op ; movabs rax, &rt_acomp|&rt_lcomp ; call rax ; jmp gamma ; beta: jmp omega`
   (32 bytes, sites {23,27,28}). The jmp gamma is **unconditional** — both ports of an
   AG-pure relop reach the BB_IF router, so the single jmp lands there regardless.
   `rt_acomp`(numeric TT_*) / `rt_lcomp`(string TT_L*) pop 2, push the result, set LAST_OK.
   Arithmetic path (rt_arith) unchanged.

2. **`bb_if.cpp`** (NEW) — the BB_IF router. MEDIUM_BINARY emits:
   `rt_pop_void (discard cond value) ; rt_last_ok ; test eax,eax ; jz omega(else) ; jmp gamma(then) ; beta: jmp omega`
   (sites {28,33,37,38}, is_def {f,f,t,f}, labels {omega,gamma,beta,omega}). Registered in
   `emit_core.c` dispatch (gave BB_IF its own arm out of the bb_alt group),
   `bb_templates.h`, and the Makefile (source list + explicit compile rule).

3. **`emit_bb.c` `flat_drive_seq`** — rewritten from a gamma-only linear walker into a
   **node-keyed CFG emitter**: BFS from `pBB->alpha`, following `c->gamma` always and
   `c->omega` **only when `c->t == BB_IF`** (so operand sub-expression children are NOT
   pulled into the statement CFG — they are emitted inline by their parent's driver:
   `flat_drive_binop_tree`, `flat_drive_call_intexpr`, etc.). One stable arena label per
   node, each emitted exactly once; successors resolved through a node->label map (NULL
   successor -> outer lbl_gamma = proc fall-off). **Non-IF nodes keep the outer lbl_omega**
   (as the prior driver did) — this was essential: resolving omega generally caused a SEGV,
   because tree-shape BB_BINOP and write-intexpr drivers walk their own children inline and
   the deep-thread `dval==1.0` gate only suppresses the double-walk when omega stays the
   outer fail label. Only BB_IF resolves omega to its else-entry. AG-pure BB_BINOP
   (alpha==beta==NULL) now routes to FILL; added `case BB_IF`. BB_SEQ is Icon-exclusive
   (only `lower_icn.c` builds it; BB_PL_SEQ is separate) so there is zero cross-family risk.

## Verification

- Per-rung: rung12_strrelop_size_{slt,sge,sne}, rung37_strrelop_hello, rung07_control_seq
  byte-identical m2 vs m3; relop program `--dump-sm | grep -c '^   [0-9]'` == 0.
- `add` (write(1+2)) and multi-write straight-line confirmed non-regressed (these SEGV'd in
  an intermediate BFS-over-omega version; the BB_IF-only-omega rule fixed it).
- Same-sweep baseline vs mine (identical script, stash/pop): 22 -> 28 PASS, SEGV 0 -> 0.
- FACT gate 0; smoke icon 5/5, prolog 5/5, broker 39/14; in-repo
  `test_crosscheck_icon.sh` PASS=3 (if_expr now green; the 1 FAIL is `concat`, a
  pre-existing BB_BINOP ICN_BINOP_CONCAT gap present at baseline — out of scope).
- Rebuilt clean after rebasing over the upstream Prolog commit; smokes still 5/5.

## NEXT — IBB-8c: numeric/real relops

`rung18_real_relop_{real_gt,real_lt,real_eq,mixed_relop}` still fail (abort/SEGV). Root
cause located: **`bb_lit_scalar.cpp` has no BB_LIT_F vstack-push** — the float literal
falls into the "Other scalar literals: pass-through (10 bytes)" stub that emits only
`jmp gamma ; beta: jmp omega` and never pushes the real. So the relop pops garbage. Fix:
add a BB_LIT_F arm mirroring the BB_LIT_I arm (movabs the double bits, push a DT_R
DESCR_t via an rt push helper — check whether a real-push runtime primitive exists or add
one). Numeric int relops (`if n < m`) likely also need their int operands present on the
stack via the same chain mechanism; verify once BB_LIT_F lands.

Then: `rung35_block_body_if_{block,else_block}` — block-body `then { ... }` introduces a
nested block (BB_SEQ_EXPR or similar) the CFG emitter does not yet flatten. Then
every-E-do-body (~4), write(BB_CALL), user-proc dispatch (the large remaining cluster).

## Caveat on gate methodology

The IBB-8a row reported corpus "17 -> 32" using a different corpus path/filter than the
`/home/claude/corpus` same-sweep used here (22 -> 28). The **+6 delta is apples-to-apples**
(same script, baseline via git stash); the absolute counts are not directly comparable to
the "32". Reconcile the canonical gate corpus/filter before trusting absolute numbers in
the watermark.
