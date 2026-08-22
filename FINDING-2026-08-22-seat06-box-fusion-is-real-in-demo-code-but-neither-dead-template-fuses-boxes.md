# FINDING seat06 — BOX-FUSION'S TARGET SHAPE IS REAL IN DEMO CODE (40 SITES / 8 OF 24 FILES), BUT NEITHER DEAD TEMPLATE ACTUALLY FUSES BOXES — IT NEEDS A NEW ELISION MECHANISM

**Session:** seat06 (`/home/claude06`, Claude Sonnet 5) · **Date:** 2026-08-22 · **Queue row:** `box-fusion` (rank 6, demoted from `chain-slot-coalescing` rank 1)
**Tree:** SCRIP `568bf098` clean · corpus `568bf098`(n/a, untouched) · .github `950778f1` clean · **no code changed this session — confirm + design only, per CHAT-ESCALATION below**

⛔ **NOTHING LANDED. CHAT-ESCALATION invoked** (this goal file's own § LAWS THAT BIND EVERY RUNG: *"any blocker only Lon can clear goes into chat as one question at the TOP of the reply; ≥2 zero-rung sessions ⇒ ask before code"*). Count: (1) s250 zero-runged this exact lever and filed an ask rather than freelancing past a "needs a new IR node" gap; (2) this row's own brief records that Lon separately aborted a fusion *build* in-chat. That is two. Asked in-chat this session; not attempting a third zero-rung pass blind.

---

## 1. FIRST STEP — s250's dead-code claims hold exactly, unchanged, on the live tree

- `bb_binop_gvar_arith()` / `bb_binop_gvar_arith_slot()` (`src/templates/bb_binop_gvar_arith{,_slot}.cpp`): declared `bb_templates.h:81-82`, defined, **zero call sites** anywhere outside their own file (`grep -rn bb_binop_gvar_arith src/` returns only the two definitions and each function's own shape-mismatch `x86_bomb`).
- `IR_BINOP_GVAR_ARITH` is not an IR opcode — no such member in `src/contracts/IR.h`.
- `ir_node_may_write_globals` (s250 §4.1's proposed safety predicate) does not exist anywhere in `src/`.
- `emit.cpp`'s `IR_BINOP` dispatch (~line 1088) is a 4-way switch on `op_binop_kind` (RELOP / CONCAT / XREP / ARITH-default) that unconditionally calls `bb_binop_arith()` for the arith category. No arm anywhere reaches either dead template.

## 2. NEW THIS SESSION — NEITHER DEAD TEMPLATE ACTUALLY COLLAPSES 3 BOXES INTO 1

The brief's "wire a dead template" undersells the gap. Byrd boxes are independently-dispatched: `--dump-bb` on `corpus/programs/snobol4/demo/counter.sno` shows `VAR "I"`, `BINOP op0`, `ASSIGN "I"` as three distinct box ids with their own α/γ/ω edges, each walked separately by `walk_bb_node_inner` (`emit.cpp`, ~2900 dense lines). Both dead templates only replace the **BINOP box's own arithmetic body** — both still write their result to a spine slot (`FRQ(_.op_off)`), not the direct register-resident read-modify-write s250's arm-C prototype measured. Wiring either into the `IR_BINOP` switch would leave the VAR box's *and* the ASSIGN box's own port overhead in place — it reproduces a slice of arm C's −19 instr/−7 stores, not the whole thing.

## 3. THE PRECEDENT MECHANISM THIS CODEBASE ALREADY HAS FOR "DELETE A BOX" — AND WHY IT DOESN'T REACH HERE UNCHANGED

`src/optimizer/copy_prop.c` (`cp_source`/`cp_run`) is the *only* existing precedent for retiring a box from the live emit spine: `cp_source` names a node whose value is a pure identity of one operand (today: `COERCE_STRING` of a `LIT_STRING`, `COERCE_INTEGER` of a non-negative `LIT_INTEGER`, null-string `CONCAT`); `cp_run` redirects every consumer's operand edge past it, then any such node with zero remaining references gets `op` set to `IR_SUCCEED` / `n_operands=0` — inert, and `branch_chain.c`'s `bc_run` (same optimizer round) folds it out of the control-flow chain. Its own doc comment is explicit: *"ONLY pure value-identities belong here."*

Box fusion is a stronger claim than value-identity: "this box's value *and* side effect can be folded into a neighbor's computation," not "this box's value already equals an operand's." No existing pass does that. Building it means:
1. A new predicate implementing s250 §4.1's full 4-condition check (op ∈ {ADD,SUB,MUL,DIV,MOD}; same-name GVA-resident var both sides; BINOP is the ASSIGN's sole consumer *and* VAR is the BINOP's sole consumer; nothing between read and write can write V) — the sole-consumer half needs `cp_run`'s own ref-after-rewrite technique.
2. Encoding the fused op + literal on the surviving node. `IR_t` already carries both a string payload (`var="X"`) and an operand list; PEERS RULE forbids new struct fields — so the clean move is **one new IR opcode** (e.g. on `IR_ASSIGN`), not a new field. Zero new global state either way.
3. Neutering the VAR (and the BINOP, if `ASSIGN` is kept as the fusion anchor) to `IR_SUCCEED`/`n_operands=0` exactly like `cp_run`, leaning on `bc_run` (already runs every optimizer round) to fold them out of the control-flow chain.

This is workable and nothing above is unsafe *to build* — but it is a fourth kind of optimizer elision (beside fold / copy-prop / pat-fold / dead-pure), not a rewiring of dead code, and it is exactly the shape of gap s250 hit and refused to freelance past.

## 4. REAL-DEMO CENSUS (not synthetic) — the shape is real, not an artifact of the `arith_loop` microbenchmark

All 24 programs in `corpus/programs/snobol4/demo/*.sno`, via `--dump-ir`, parsed programmatically (script + per-file dumps not committed — reproducible in ~10s, see command below):

| metric | count |
|---|---|
| total `ASSIGN` nodes (24 files) | 727 |
| `ASSIGN`'s direct RHS is `VAR` / `CALL` / `BINOP` / `LIT_STRING` / `LIT_INTEGER` / other | 254 / 230 / 128 / 68 / 29 / 18 |
| arithmetic `BINOP` nodes (op ∈ ADD/SUB/MUL/DIV/MOD) | 126 |
| **EXACT s250 §4.1 shape** — `ASSIGN(V) ← BINOP_arith(VAR(V), LIT_INTEGER)` directly | **40, in 8 of 24 files** |
| near-miss — `ASSIGN(V) ← BINOP_CONCAT(X, BINOP_arith(VAR(V), LIT_INTEGER))` (loop-counter idiom, see below) | 8, in 3 of 24 files |
| single most common arith-`BINOP` operand-kind pair, any context | `(LIT_INTEGER, VAR)`: 68 / 126 = 54% |

Reproduce: `for f in corpus/programs/snobol4/demo/*.sno; do LD_LIBRARY_PATH=out ./scrip --dump-ir "$f" </dev/null; done` then match `ASSIGN [x] var="V"` → `x: BINOP [a,b] binop∈{0..4}` → `{a,b}` = one `VAR var="V"` + one `LIT_INTEGER`.

Most of the 40 are a stack-pointer increment/decrement idiom in `calculator-1.sno` (`sp = sp + 1` / `sp = sp - 1` shaped). The near-miss class is the `V = LT(V,N) V + 1 :S(LABEL)` loop-counter idiom (present verbatim in `corpus/programs/snobol4/demo/counter.sno`, statement 3) — real, but the `ASSIGN`'s sole operand there is the `CONCAT`, not the arith `BINOP`, directly. It is a legitimate but *different and harder* fusion (three levels, not two) — out of scope for rung 1, noted for whoever takes it next.

## 5. RECOMMENDATION

Rung 1's target is **confirmed as the right one to keep pursuing**: real (40 sites / 8 files, not a synthetic artifact), and unlike the copy-assign case s250 separately ruled out (§3.2 — `IR_VAR` has no operands, so plain copy-propagation can never reach it), this shape *deletes* the VAR box rather than redirecting a read, so it doesn't hit that same wall. What's left is genuinely new machinery (§3 above), not a wiring job — asking rather than building it blind a third time.

**Question for Lon, asked in-chat this session:** proceed with (a) a new `box_fusion.c` optimizer pass built on the `cp_run` pattern generalized to computed values, plus (b) one new IR opcode to carry the fused op+literal on `IR_ASSIGN`, scoped exactly to the §4.1 safety condition and gated on the row's full DONE-WHEN (m3≡m4, beauty fixed point both modes, corpus at standing reds, instruction count measured) — or is there something from the aborted build attempt this should avoid repeating?
