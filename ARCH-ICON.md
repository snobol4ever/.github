# ARCH-ICON.md — Icon Frontend and BB Execution

Frontend: Icon. Produces shared IR (tree_t* via icon_parse). See ARCH-IR.md.

---

## Execution model

Icon is a goal-directed language. Every expression either:
- **Succeeds** (gamma port) — produces a value, may produce more on resume
- **Fails** (omega port) — produces no value, terminates generator

This is exactly the Byrd Box four-port model: alpha (start), beta (resume),
gamma (succeed), omega (fail). Icon IS a Byrd Box graph. Every construct is
a box. The broker pumps it (BB_PUMP mode).

**Key distinction from SNOBOL4:** SNOBOL4 uses BB_SCAN (try each cursor
position). Icon uses BB_PUMP (generate all values until omega).

---

## Statement-level dispatch (SM layer — already correct)

  lower.c emits:   SM_PUSH_EXPR <tree_t*>  +  SM_BB_PUMP
  sm_interp.c:     pops tree_t*, calls coro_eval() -> bb_node_t,
                   then bb_broker(node, BB_PUMP, pump_print, NULL)
  sm_codegen.c:    h_bb_pump mirrors sm_interp exactly

This is CORRECT and COMPLETE. The SM layer is thin — one SM_BB_PUMP per
Icon statement. BB does all the work. Do not change this.

---

## Sub-expression level dispatch (BB templates — the work to do)

Generator sub-expressions (1 to N, !E, A|B, every, E\N, E1!E2, |||) are
currently implemented as:
  (a) SM coroutine bytecode (SM_RESUME/SM_STORE_GLOCAL/SM_SUSPEND/SM_RETURN)
      — this is WRONG. See GOAL-ICON-BB-COMPLETE (superseded).
  (b) SM_BB_PUMP_AST fallthrough to coro_eval — works but dishonest.

The correct implementation is a flat BB template function per construct:
  emit_bb_icn_to, emit_bb_icn_iterate, emit_bb_icn_alt, emit_bb_icn_every,
  emit_bb_icn_limit, emit_bb_icn_bang, emit_bb_icn_lconcat, emit_bb_icn_seq
See GOAL-ICON-BB-NATIVE.md for the full plan and rungs.

---

## Box structure for Icon constructs (from .github/test_icon.c)

  construct_alpha:  initialize state; compute first value; goto gamma or omega
  construct_beta:   advance state; compute next value; goto gamma or omega
  construct_gamma:  value ready — wire to caller's success label
  construct_omega:  exhausted — wire to caller's fail label

Three-column form: LABEL / ACTION / GOTO. Exactly as in test_icon.c.
State (cur, lo, hi, index, etc.) lives in the DATA block (zeta struct),
allocated fresh per alpha-entry. CODE is shared.

---

## Existing semantic reference (BROKERED / legacy form)

coro_runtime.c contains C-function boxes for all Icon constructs:
  coro_bb_to_by, coro_bb_every, coro_bb_limit, coro_bb_bang_binary,
  coro_bb_seq_expr, icn_bb_assign_gen, icn_bb_identical_gen, etc.

These are EMIT_BINARY_BROKERED form — fn(zeta, port) called by broker.
They work correctly and are the SEMANTIC REFERENCE for each construct.
They are NOT the architectural target (EMIT_BINARY_WIRED flat templates).
Read them to understand semantics. Do not copy them as implementation.

---

## JCON reference

jcon-master/tran/irgen.icn — 43 ir_a_* procedures, one per AST construct.
ir_info(start, resume, failure, success) — the four-port record on every node.
ir_a_ToBy, ir_a_Unop (closure=!E), ir_a_Alt, ir_a_Every, ir_a_Limitation,
ir_a_Binop (closure=bang), ir_a_Mutual (seq), ir_a_Scan, ir_a_Not, etc.

Each procedure emits ir_chunk records wiring start/resume/failure/success.
This is the ground truth for what each Icon construct does.

---

## Active goal

GOAL-ICON-BB-NATIVE.md — implement Icon generator constructs as flat BB
template functions. 9 rungs (IB-0 through IB-9). Current: IB-0.
