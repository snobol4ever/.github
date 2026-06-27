# ICON-BB THREE PILES — the complete remaining-work catalog (2026-06-27, Claude)

Baseline: SCRIP `a2d0385b`, m3==m4 **PASS=212 FAIL=41**. This document replaces "fill the
bomb arms" with the truth found by reading every Icon-reachable bomb: **the boxes are written.**
Almost every bomb is a GUARD that fires when an *upstream* slot was not promoted, not a missing
template arm. The remaining work is three piles, in priority order. Fix 1, then 2, then 3, done.

Method note (per RULES.md): each fix is verified with the 2-way monitor before commit. `.s`
artifacts regen after any emitter/lowerer change. No commit without the goal gate green.

---

## PILE 1 — SLOT-PROMOTION GUARDS  (box already written; fix is ONE upstream problem)

**Symptom.** A template bombs with `op_a_slot==-1 (… slot not promoted)`, `op_off<0`,
`needs … slot`, or `needs descr flat-chain`. **Proof the box is complete:** `bb_gvar_assign`
emits real x86 for ten RHS shapes (LIT_S/I/F, VAR, BINOP×3, UNOP, VAR_FRAME, VAR_FRAME_REF,
CALL, IDX); its bombs fire ONLY on `_.op_a_slot < 0`. You cannot fill this in-box — the slot is
−1, there is nothing to read. **Root cause is upstream:** the lowerer / `emit_bb.c`
chain-walker does not promote the operand's result slot for these RHS/operand shapes, so
`op_a_slot` (and friends) arrive unset.

**This is ONE bug wearing many hats.** The same `op_a_slot==-1` appears across `bb_gvar_assign`,
`bb_assign_frame`, `bb_assign_frame_ref` for the BINOP/CALL/IDX/UNOP/FRAME-VAR RHS shapes —
identical cause: when the RHS is itself a value-producing box, its result slot must be allocated
and recorded as the consumer's `op_a_slot`; the promotion pass skips these shapes.

### Pile-1 inventory (box · guard · what slot is missing)

| box | guard | missing slot(s) |
|-----|-------|-----------------|
| `bb_gvar_assign` ×5 | `op_a_slot==-1` for BINOP/UNOP/FRAME-VAR/CALL/IDX RHS | RHS producer result slot |
| `bb_assign_frame` ×2 | `op_a_slot==-1` int-binop / call-result | RHS producer result slot |
| `bb_assign_frame_ref` ×2 | `op_a_slot==-1` int-binop / call-result | RHS producer result slot |
| `bb_gvar_assign_descr` | `needs rhs slot + own slot` | `op_sa`, `op_off` |
| `bb_rasgn` ×2 | `arr[i]<-v` / `x<-v` slots | base/key/value/save/own |
| `bb_idx_get` ×2 | base name + result/scratch; key kind | `op_off`, scratch, key |
| `bb_idx_set` | base/key/value operand slots | `op_sa/op_sb/op_sc` |
| `bb_gen_scan` ×2 | leave-glue out-area `op_off<0` | `op_off` |
| `bb_case_arm` ×2 | value/case slot; selector/key slot | `op_sa/op_sb/op_off` |
| `bb_to` | static operands, nonzero by, flat-chain | operand slots |
| `bb_limit` | flat-chain, static slots, literal count, gen-β | operand slots + gen β |
| `bb_suspend` | flat-chain, expr-value slot, do-body resume | `op_off` + resume label |
| `bb_keyword` | `no slot` (`op_off<0`) | `op_off` |
| `bb_unop` | `op_sa<0` (LIT_F/NUL or non-slot producer) | `op_sa` |
| `bb_var` / `_frame` / `_frame_ref` / `_global` | flat-chain + own slot | `op_off` |
| `bb_swap` | both var slots + own slot | `op_sa/op_sb/op_off` |
| `bb_return` | descr flat-chain | flat-chain mode |
| `bb_key_gen` / `bb_iterate` | operand/idx/out slot | `op_sa/op_sb/op_off` |
| `bb_repalt` | sub-expr value slot | `op_sa` |
| `bb_scan_*` (any/many/upto/tab/move/match/find/bal/pos) | literal arg + flat-chain slot | `op_off` (+ literal-arg admit) |
| `bb_unop_gvar_slot` / `bb_binop_gvar_relop` | shape/predicate mismatch | dispatch chose arm, predicate failed → slot |

### Pile-1 fix — PINNED TO THE EXACT SITE (diagnosis complete 2026-06-27)

**Mechanism (verified):** `bb_slot_get(nd)` returns the node's frame-slot from the slotmap, or
−1 if the node was never slot-allocated. The template bombs read `_.op_a_slot`; the value comes
from the consumer's flat-drive setting `g_emit.op_a_slot = bb_slot_get(rhs_producer)`. The
guards fire because **the consumer's driver does not propagate the producer's slot into
`op_a_slot`.** Two drivers, `emit_bb.c`:

- **`flat_drive_gvar_assign` (line ~2213)** — reached (dispatch ~3217) for RHS = `IR_CALL` /
  `IR_IDX` / `IR_VAR_FRAME` / `IR_VAR_FRAME_REF`. It sets `op_parts` for the SEQ/LIT_S concat
  case **but never sets `g_emit.op_a_slot` (nor confirms `op_a_node_kind`) for the
  producer-RHS shapes.** The producer is already walked into the flat chain by
  `codegen_flat_chain_body` (so it HAS a slot); the driver simply fails to forward it. **Fix:**
  for producer-RHS (`c0->op` in CALL/IDX/FRAME-VAR), set
  `g_emit.op_a_slot = (c0->op==IR_VAR* ? bb_varslot_peek(name) : bb_slot_get(c0))` and ensure
  `op_a_node_kind` reaches the template (confirm whether `EMIT_PAIR_FILL` derives it from
  `bb_child0` or the driver must set it — READ the macro first).
- **`flat_drive_gvar_assign_binop` (line ~2259)** — handles BINOP/UNOP RHS; already
  `walk_bb_flat(c0,…)` then emits. Confirm it sets `op_a_slot = bb_slot_get(c0)` AFTER the walk
  (the POW/UNOP const-fold special cases are fine; the general case at ~2295 is the one to check).

Then the IDENTICAL propagation is needed in the `bb_assign_frame` / `bb_assign_frame_ref`
drivers (same `op_a_slot==-1` guard, same cause). **One propagation pattern, applied at these 2–3
driver sites, un-bombs the ~9 assign-family guards; the remaining Pile-1 guards (`bb_idx_*`,
`bb_swap`, `bb_keyword`, `bb_scan_*`, `bb_to/limit/suspend`) are the SAME "driver doesn't forward
the producer slot" shape and fix the same way** — this is why Pile 1 is one bug, not 35.

**SAFETY of the edit:** adding `op_a_slot = bb_slot_get(c0)` is monotone — if the producer has a
slot it fixes the case; if not, `bb_slot_get` returns −1 and the guard still fires (no
regression). Compiles trivially. Behavioral correctness verified next session via the 2-way
monitor on `rung24_records_*` / global-assign rungs.

---

## PILE 2 — GENUINELY MISSING TEMPLATE ARMS  (real codegen; small)

Real absent arms — the only true "write the box" work, and it is short.

| construct | box | canonical spec | shape |
|-----------|-----|----------------|-------|
| `s[i+:n]` / `s[i-:n]` | `bb_section` (`op_ival != 0`) | `oref.r` §sect | extended-section: base + i + signed-n length |
| non-literal scan pattern (mode-4) | `bb_scan_stmt` | — (likely SNOBOL, verify scope) | PB-RB native graph for computed subject/pattern/replacement |
| computed-cset scan | `bb_scan_*` runtime variant | `fscan.r` (`any/upto/many`) | cset arg from a slot, not a `[rip]` literal — runtime-driven cset compare |

`bb_section` plain `s[i:j]` already works; only the `+:`/`-:` forms (`op_ival != 0`) are absent.

---

## PILE 3 — CALL-ROUTER BUILTINS  (fail at the router, NOT a template; several need NEW runtime)

These fail at the `emit_bb.c` call router (`unsupported call shape fn=<X>`), before any template.
Each needs a router arm; the I/O and coexpr ones ALSO need a runtime subsystem that does not yet
exist. **This pile contains the genuine feature work — it is the honest reason Icon is not
"done," and it does not collapse into a quick fix.**

| builtin | canonical | router arm | new runtime needed? |
|---------|-----------|-----------|---------------------|
| `tab(gen)` / `move(gen)` | `fscan.r` | yes | no — scan-producer slot wiring (overlaps Pile 1) |
| `open` / `read` / `reads` / `write`(file) / `close` | `fsys.r`, `fmisc.r` | yes | **YES — file I/O subsystem** (FILE* descriptor type, `rt_open/read/close`) |
| `display` | `fmisc.r` | yes | partial — needs symbol-table walk |
| `remove` / `delete`(file) | `fsys.r` | yes | YES — fs helpers |
| `@e` (activate), `create e` | `invoke.r`, `oref.r` | yes | **YES — coexpression facility** (coroutine stack; `ir_Create`/`ir_ResumeValue`/`ir_CoRet`). Largest single item. |
| `o` (operator-string invocation) | `invoke.r` | yes | indirect-operator dispatch table |
| `p` (indirect proc by string) | `invoke.r` | yes | by-name proc lookup at runtime |
| `?` (computed callee) | `invoke.r` | yes | computed-invocation dispatch |
| `goal` / `goal-directed` builtins | `invoke.r` | yes | dispatch |

### Pile-3 sizing (honest)
- **Cheap (router arm only):** `tab`/`move` (overlaps Pile 1), `display`.
- **Medium (router + small runtime):** `o`/`p`/`?` indirect/computed invocation (one dispatch helper + table).
- **Large (router + whole subsystem):** file I/O (`open`/`read`/`close`/`remove`) and
  **coexpressions** (`@`/`create`). These are real Icon facilities. Coexpr needs a coroutine
  stack and the three IR forms `ir_Create`/`ir_ResumeValue`/`ir_CoRet` (absent everywhere). No
  shortcut exists; this is the long tail.

---

## ORDER OF EXECUTION
1. **Pile 1** — one slot-promotion fix in `emit_bb.c`; un-bombs ~35 guards. Highest yield, lowest surface.
2. **Pile 2** — `bb_section` `+:`/`-:`, computed-cset scan, (scan-stmt if in Icon scope). Short, real arms.
3. **Pile 3** — router arms for the cheap/medium builtins; then the two subsystems (file I/O, coexpr) as their own goals. This pile is where remaining time genuinely goes.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
