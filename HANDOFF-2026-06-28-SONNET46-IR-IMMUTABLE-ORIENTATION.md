# HANDOFF 2026-06-27 — GOAL-IR-IMMUTABLE-EMIT: Orientation + Pile-1 Diagnosis

**Model:** Claude Sonnet 4.6
**SCRIP HEAD:** e2f1d61b (unchanged — no code landed this session)
**Gate at session end:** A=34 B=11 HARD=45 (unchanged, correct)
**Icon --run at session end:** PASS=213 FAIL=40 XFAIL=36 (unchanged)

---

## Session purpose

Orientation session for GOAL-IR-IMMUTABLE-EMIT (Ground Zero #5). No code landed. All findings
are intelligence for the next session. Tree is clean at e2f1d61b.

---

## Key corrections to GOAL-IR-IMMUTABLE-EMIT.md prose

### 1 — JCON-33 framing is wrong as a target for SCRIP

The goal file says "collapse toward JCON-33" and "operators unify under ir_OpFunction." JCON
merges unary and binary operators into one ir_OpFunction record because in JCON an operator IS
a Java vProc method — one dispatch path, arity resolved at runtime. SCRIP is a template system:
one BB = one instruction = one template emitting native x86 directly. bb_binop_arith reads TWO
operand slots (op_sa + op_sb); bb_unop reads ONE (op_sa). Merging them forces an arity branch
inside the template — exactly what the template model exists to avoid.

**Correction:** IR_UNOP and IR_BINOP stay distinct. The real bloat is the OPERAND-SOURCE axis
(IR_BINOP_GVAR_ARITH, _GVAR_RELOP, etc.) and the RHS-SOURCE assign variants (IR_ASSIGN_LIT_S,
_VAR, _CALL, etc.) — those encode WHERE an operand came from into the opcode, which belongs on
the producer box, not the consumer opcode. The JCON-33 reference is useful as a "no source
variants in the opcode" principle, not as a literal instruction-count target.

### 2 — operand_aux was not deleted; its storage moved

The goal file says "operand_aux deleted — node operands[] is single source of truth." Correct
on storage. But bb_operand_aux_set() still exists as an API (lower.h, scrip_ir.c) and still
writes operands[] — the bbg arg is now (void)bbg. ir_operand_push() also writes operands[].
Both are live in lower_icon.c, lower_pascal.c, lower_prolog.c, lower_snobol4.c.

### 3 — SNOBOL4 lower_expr already uses the producer-box model

The goal file says "SNOBOL4 wires binop operands as direct c[] children — which trips F1."
This is stale. lower_snobol4.c lower_expr() lines 130–135 recursively lowers each operand
into its own producer box (lr, rr) and records them via ir_operand_push — structurally
identical to the Icon model. Same for unop (lines 146–149). IRM-1 for lower_expr is DONE.

### 4 — Three-Piles "Pile 1 assign-slot" premise is stale at HEAD

The Three-Piles doc (2026-06-27) describes ~35 guards bombing on op_a_slot==-1 for the
assign family. At e2f1d61b these are resolved:
- Zero committed .s artifacts carry "slot not promoted" or "op_a_slot==-1"
- x := f() compiles 0-bombs, runs correctly
- x := a + b compiles 0-bombs, runs correctly
- a[1] := f() compiles 0-bombs, runs correctly (call result slot already promoted)

Verified by stash/rebuild/re-test cycle. Two additive slot-forwarding edits were written,
tested against the pristine tree, found behaviorally inert, and reverted. Tree is clean.

---

## ONE genuinely live bomb pinned (next session's first rung)

**Shape:** a[i] := <binop>  (list-element assignment, computed value)
**Reproduced:** `procedure main();a:=list(3);a[1]:=2+3;write(a[1]);end`
  → aborts: libscrip_rt: BOMB — bb_idx_set: needs base/key/value operand slots
**NOT affected:** a[1] := f() runs fine (call-result slot is allocated; binop result is not)

**Anatomy of the bomb (fully diagnosed):**

flat_drive_idx_set (emit_bb.c:1696) already:
- Reads all three operands from pBB->operands[0/1/2] (base, key, val)
- Walks each via walk_bb_flat when bb_slot_get < 0 (lines 1713–1715)
- Forwards all three slots to g_emit: op_a_slot=base, op_sb=key, op_sc=val (lines 1716–1718)

bb_idx_set.cpp consumer bombs (line 12–13) when ANY of op_a_slot/op_sb/op_sc is < 0.

The gap: walk_bb_flat(val_box=IR_BINOP, ...) walks the binop's subgraph but does NOT
allocate a result slot for the binop node itself. bb_slot_get(val_box) stays -1 after the
walk. So op_sc = -1 → bomb.

**The candidate fix:**
Before walk_bb_flat(val_box, ...) in flat_drive_idx_set, if val_box->op == IR_BINOP (or
IR_UNOP, or any value-producing non-literal), ensure bb_slot_alloc16(val_box) is called to
give it a result slot. Then bb_slot_get(val_box) >= 0 after the walk and op_sc is correct.

**MANDATORY VERIFICATION before landing:**
Confirm that bb_binop_arith (the binop consumer template) actually WRITES its result to the
slot allocated by bb_slot_alloc16. If it does not, the program will run with silently wrong
output instead of a loud bomb — which is worse. Check: grep op_off bb_binop_arith.cpp and
confirm the result store uses the node's own allocated slot. Then direct-run:
  a:=list(3); a[1]:=2+3; write(a[1])  →  must print 5.

---

## The _GVAR_ opcodes: F1 is still live, cause confirmed

IR_BINOP_GVAR_ARITH, _GVAR_RELOP, _GVAR_CONCAT, IR_UNOP_GVAR_SLOT are produced by NO
lowerer (grep src/lower is empty for all four). They are purely emit-time transients:
flat_drive_gvar_assign_binop (line 2288) and flat_drive_gvar_concat (line 2267) swap ->op
to the _GVAR_ variant, call EMIT_PAIR_FILL, restore. These are F1's 14 swap sites.

The IRM-3 deletion path (after IRM-1/2 universalize producer slots) is:
1. Confirm bb_binop_arith reads op_sa/op_sb (slots) not the global name inline — it does.
2. Confirm a global-variable operand's producer box writes a slot visible to the consumer.
3. Delete the _GVAR_ template files + opcodes + swap sites.
At HEAD, step 2 may already be true for arith (gvar arith runs correctly on current tree).
Verify then delete.

---

## Session ground rules confirmed (for next session)

- No monitor needed for this work (Lon directive, 2026-06-27). Direct compile/run.
- IR_UNOP and IR_BINOP stay distinct (template grain, not a collapse target).
- JCON-33 is a "no source-variants" principle, not a literal count target.
- Stash/rebuild/pristine-test before claiming a fix is live. Learned this session.

## Watermark
**Ground Zero #5 — orientation + Pile-1 re-diagnosis — 2026-06-27.**
Gate baseline: HARD=45 (34 op-writes + 11 field-writes), C=19 runtime-query refs.
Next rung: bb_idx_set val-operand slot (a[i]:=binop) — see above for full fix spec.
