# GOAL-IR-EMITTER-PREREQ.md — IR_t Emitter Foundation (prerequisite for JVM + JS)

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║  A C Byrd box (C BB) is ANY C function with signature: DESCR_t foo(void *zeta, int entry)      ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                             ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

⛔ **Read before any source file:** ARCH-IR.md then ARCH-SCRIP.md then ARCH-EMITTER.md then GOAL-LOWER-REDESIGN.md.

**Repo:** one4all + .github
**Prereq for:** GOAL-SN4-JVM-EMIT.md and GOAL-SN4-JS-EMIT.md
**Done when:** a new emitter entry point accepts an IR_t* (the DCG) and produces correct SM opcodes + BB code for a SNOBOL4 smoke program, without reading SM_Program as input.

---

## Architecture: the correct pipeline

The stages pass exactly ONE structure between them:

```
source
  → parser
  → tree_t          (AST — one named structure out)

tree_t
  → lower           (lower_sno.c / lower_icn.c / lower_pat_dcg.c / IR_lower_wire)
  → IR_t            (DCG — one named structure out; the ONLY output of lower)

IR_t
  → emitter         (emit_x86.c / emit_jvm.c / emit_js.c)
  → SM opcodes      (for scalar expressions, control flow, function calls)
  + BB code         (for pattern/generator nodes — emitted inline alongside SM)
```

**Lower produces IR_t only. Emitters consume IR_t only.**

Today's state is transitional: `lower.c` writes directly to `SM_Program` AND calls `IR_lower_pat()` to produce `IR_block_t` as a side attachment on `SM_EXEC_STMT`. This is the pre-redesign state being eliminated by GOAL-LOWER-REDESIGN. **This GOAL builds the emitter side of that elimination:** the infrastructure for emitters to read `IR_t` and produce everything themselves.

The x86 emitter currently reads `SM_Program` (it is the reference emitter for the old path). JVM and JS emitters must NOT follow that model. They read `IR_t`.

---

## What "reading IR_t" means for an emitter

An IR_t node has four ports: `port_start`, `port_resume`, `port_succ`, `port_fail`. The emitter walks the DCG by following these pointers and emits target code for each node kind:

- **Scalar IR_t nodes** (IR_LIT_I, IR_LIT_S, IR_VAR, IR_BINOP, IR_CALL, IR_ASSIGN, IR_RETURN, IR_SEQ) → emit SM-opcode-equivalent code (push, store, call, jump, return). These are the SM template functions.
- **Generator IR_t nodes** (IR_PAT_LIT, IR_PAT_SPAN, IR_PAT_ARB, IR_PAT_CAT, IR_PAT_ALT, IR_PAT_ARBNO, IR_PAT_ASSIGN_IMM, IR_PAT_ASSIGN_COND, IR_PAT_ANY, IR_PAT_NOTANY, IR_PAT_LEN, IR_PAT_POS, IR_PAT_TAB, IR_PAT_REM, IR_PAT_FENCE, IR_PAT_ABORT, IR_ALTERNATE, IR_TO_BY, IR_EVERY, IR_WHILE, IR_LIMIT, IR_SCAN, etc.) → emit BB-equivalent code (classes/factories with alpha/beta methods). These are the BB template functions.

The emitter does NOT receive SM_Program. It receives IR_t and emits both the SM and BB parts itself.

---

## Prior art: every BB is already implemented

All SNOBOL4 BB implementations exist in two target languages already, written during the pre-SM era. They are the complete, tested reference for every BB template the emitter must generate:

**JVM — `src/runtime/jvm/bb_boxes.j`** (2309 lines)
Each class in this file is a one-to-one match with one IR_t generator node kind. The alpha() and beta() method bodies are exactly the code the JVM emitter must generate for that node kind. The emitter's job is: write a C function `emit_jvm_pat_lit(IR_t *nd, FILE *out)` that generates the equivalent of the `bb/bb_lit` class body. Do this for every IR_PAT_* kind.

These classes were originally in individual files under `src/runtime/boxes/` (one per box: `bb_lit.j`, `bb_span.j`, `bb_arb.j`, etc.), consolidated at git commit `660339cd`. To read a single box in isolation use: `git show 660339cd:src/runtime/boxes/NAME/bb_NAME.j`. The mapping is:
- IR_PAT_LIT → bb_lit.j
- IR_PAT_SPAN → bb_span.j
- IR_PAT_BREAK → bb_brk.j
- IR_PAT_ANY → bb_any.j
- IR_PAT_NOTANY → bb_notany.j
- IR_PAT_LEN → bb_len.j
- IR_PAT_POS → bb_pos.j (rpos variant: nd->n==1)
- IR_PAT_TAB → bb_tab.j (rtab variant: nd->n==1)
- IR_PAT_REM → bb_rem.j
- IR_PAT_ARB → bb_arb.j
- IR_PAT_ARBNO → bb_arbno.j
- IR_PAT_ALT → bb_alt.j
- IR_PAT_CAT → bb_seq.j
- IR_PAT_ASSIGN_IMM → bb_capture.j (immediate=true)
- IR_PAT_ASSIGN_COND → bb_capture.j (immediate=false)
- IR_PAT_FENCE → bb_fence.j
- IR_PAT_ABORT → bb_abort.j

**JS — `src/runtime/js/bb_boxes.js`** (605 lines)
Each factory function in this file is a one-to-one match with one IR_t generator node kind. The same mapping applies. To read a single box: `git show 660339cd:src/runtime/boxes/NAME/bb_NAME.js`.

**The emitter's task for each BB:** write a C function in `emit_jvm.c` / `emit_js.c` that traverses one IR_t node and emits the Jasmin / JS code that is equivalent to the corresponding entry in `bb_boxes.j` / `bb_boxes.js`. The reference implementation is already done — translate it into emitter template form.

---

## IR_t node traversal algorithm

The DCG is cyclic. Traversal must:
1. Assign a unique integer ID to each IR_t node (by `nd->id` if set, else by pointer address).
2. Use a visited bitset or hash to avoid re-processing nodes.
3. Walk in DFS pre-order from `cfg->entry` (= `IR_t->entry`), following `port_start`, `port_succ`, `port_fail`, `port_resume` edges.
4. Emit a function/class declaration for each unvisited node.
5. After all declarations, emit a wiring phase that sets successor references (connecting the emitted objects into the same graph shape as the IR_t DCG).

For cyclic nodes (IR_PAT_ARB, IR_PAT_SPAN, IR_PAT_ARBNO — where `port_resume` points back to self or an ancestor), emit a forward-reference placeholder during the declaration phase and fill it in during the wiring phase.

---

## Steps

### IEP-1 — Define the emitter entry point signature

- [ ] **IEP-1** — Define `emit_ir_block(IR_t *cfg, FILE *out, const char *target)` in a new file `src/emitter/emit_ir.h`. This is the single entry point all target emitters will implement. `target` is one of `"x86"`, `"jvm"`, `"js"`, `"wasm"`, `"net"`, `"c"`. Add a dispatch table: `emit_ir_block` calls `emit_ir_block_jvm` / `emit_ir_block_js` etc. based on target. No implementation yet — stubs only (return 0, emit a comment).

  Also define `ir_node_id(IR_t *nd)` — returns `nd->id` if nonzero, else `(int)(uintptr_t)nd % 100000` as a stable surrogate. Emitters use this for all label/name generation.

  **Gate:** `emit_ir.h` compiles cleanly as included by a stub `emit_ir.c`.

### IEP-2 — IR_t traversal infrastructure: visitor

- [ ] **IEP-2** — Implement `ir_walk(IR_t *cfg, void (*visit)(IR_t *nd, void *ctx), void *ctx)` in `src/emitter/emit_ir.c`. Walks all reachable IR_t nodes from `cfg->entry` following all four ports, calling `visit` exactly once per node (visited bitset keyed on `ir_node_id`). Handles cycles (back-edges) correctly by checking visited before recursing. Exposes `ir_is_generator(IR_e kind)` — returns 1 for all IR_PAT_* and Icon/Prolog generator kinds, 0 for scalar kinds.

  **Gate:** `ir_walk` on a hand-built IR_t DCG (IR_PAT_CAT of two IR_PAT_LIT nodes) visits exactly 3 nodes.

### IEP-3 — Wire --sm-emit --target= dispatch to IR_t path

- [ ] **IEP-3** — In `src/driver/scrip.c`, add `--target=jvm` and `--target=js` alongside the existing `--target=x64` (which keeps its current SM_Program path unchanged). For `--target=jvm` and `--target=js`: instead of calling `sm_codegen_text(sm, ...)`, call `emit_ir_block(ir_cfg, stdout, "jvm")` / `emit_ir_block(ir_cfg, stdout, "js")`. The `ir_cfg` comes from `sm_preamble`'s IR_t output (extend `sm_preamble` or add a parallel `ir_preamble` that produces IR_t from tree_t without lowering to SM_Program).

  Note: `sm_preamble` currently calls `sm_lower` which writes to SM_Program. For the new path, we need `ir_lower(tree_t *prog) -> IR_t*` — the function that lower.c will eventually become under GOAL-LOWER-REDESIGN. For now, use the existing `IR_lower_pat` output as a test vehicle with a single pattern-match statement.

  **Gate:** `scrip --sm-emit --target=jvm simple.sno` reaches `emit_ir_block` stub (prints "; JVM stub") without crashing.

### IEP-4 — Scalar node emission: SM-equivalent opcodes from IR_t

- [ ] **IEP-4** — For each **scalar** IR_t node kind, define what SM-equivalent code the emitter produces. These are the "SM template functions" that emit_jvm.c and emit_js.c both implement. The scalar kinds from IR_t and their SM equivalents:

  | IR_e kind | SM equivalent | JVM Jasmin | JS |
  |---|---|---|---|
  | IR_LIT_I | SM_PUSH_LIT_I | ldc2_w N; invokestatic SnoRt.push_int(J)V | rt.push_int(N); |
  | IR_LIT_S | SM_PUSH_LIT_S | ldc "s"; ldc len; invokestatic SnoRt.push_str(...)V | rt.push_str(_SN, len); |
  | IR_LIT_F | SM_PUSH_LIT_F | ldc2_w bits; invokestatic SnoRt.push_real(J)V | rt.push_real_bits(0xHEX); |
  | IR_LIT_NUL | SM_PUSH_NULL | invokestatic SnoRt.push_null()V | rt.push_null(); |
  | IR_VAR (load) | SM_PUSH_VAR | ldc "NAME"; invokestatic SnoRt.push_var(...)V | rt.push_var(_SN); |
  | IR_ASSIGN | SM_STORE_VAR | ldc "NAME"; invokestatic SnoRt.store_var(...)V | rt.store_var(_SN); |
  | IR_BINOP(ADD) | SM_ADD | ldc OP; invokestatic SnoRt.arith(I)V | rt.arith(OP); |
  | IR_CALL | SM_CALL_FN | ldc "NAME"; ldc NARGS; invokestatic SnoRt.call(...)V | rt.call(_SN, NARGS); |
  | IR_RETURN | SM_RETURN | invokestatic SnoRt.do_return(II)V; return | rt.do_return(0,0); return; |
  | IR_GOTO | SM_JUMP | goto LN | _pc=N; continue; |
  | IR_FAIL | SM_JUMP_F | (set last_ok false) | rt.set_last_ok(false); |
  | IR_SUCCEED | SM_PUSH_NULL | invokestatic SnoRt.push_null()V | rt.push_null(); |
  | IR_SEQ | (none — sequencing only) | (emit children in order) | (emit children in order) |
  | IR_PROC | SM_DEFINE_ENTRY | .method public static NAME()V | function _fn_NAME() { |

  Implement `emit_jvm_scalar(IR_t *nd, FILE *out)` and `emit_js_scalar(IR_t *nd, FILE *out)`. These handle all non-generator nodes.

  **Gate:** An IR_t graph consisting of only scalar nodes (IR_LIT_S → IR_ASSIGN("OUTPUT") → IR_CALL("HALT")) produces `OUTPUT = "hello"\n` output when emitted to JVM and run, and to JS and run.

### IEP-5 — Generator node emission: BB templates from IR_t

- [ ] **IEP-5** — For each **generator** IR_t node kind (all IR_PAT_* kinds), implement the BB template emitter. The template emitter is a C function that:
  1. Takes one IR_t node.
  2. Reads its payload (sval for LIT/SPAN/ANY/etc., ival for LEN/POS/TAB, child pointers for ARBNO/CAT/ALT/CAPTURE).
  3. Emits a Jasmin class (JVM) or JS factory function (JS) whose alpha/beta bodies implement the exact semantics of the corresponding bb_boxes.j / bb_boxes.js entry.

  **Reference for each node kind:** read the corresponding implementation from `src/runtime/jvm/bb_boxes.j` (for JVM) or `src/runtime/js/bb_boxes.js` (for JS). These are complete, tested implementations. The C emitter function generates equivalent code parameterized by the IR_t node's payload values (the literal string, the charset, the integer n, etc.).

  For each IR_PAT_* kind, implement:
  - `emit_jvm_bb_NODE(IR_t *nd, FILE *out, int stmt_id)` — emits Jasmin class `pat/PN_ID`
  - `emit_js_bb_NODE(IR_t *nd, FILE *out, int stmt_id)` — emits JS factory `make_pat_N_ID(ms)`

  Start with the simplest boxes: IR_PAT_LIT, IR_PAT_ANY, IR_PAT_LEN, IR_PAT_EPS (trivial alpha/beta), then IR_PAT_SPAN, IR_PAT_BREAK, IR_PAT_NOTANY, IR_PAT_POS, IR_PAT_TAB, IR_PAT_REM. Then the compound boxes: IR_PAT_CAT, IR_PAT_ALT, IR_PAT_ARBNO. Then capture: IR_PAT_ASSIGN_IMM, IR_PAT_ASSIGN_COND. Then degenerate: IR_PAT_ARB, IR_PAT_FENCE, IR_PAT_ABORT.

  **Gate:** `SUBJECT 'AB' = SPAN('AB') . V; OUTPUT = V` emits via --sm-emit --target=jvm and --sm-emit --target=js and produces `AB` on both.

### IEP-6 — Wiring phase: connect emitted BB objects into DCG shape

- [ ] **IEP-6** — After emitting all node classes/factories for a statement, emit a wiring function `setup_pat_N(MatchState ms)` (JVM) or `wire_pat_N(ms)` (JS) that:
  - Allocates all node objects (one per IR_t node).
  - Sets each node's successor fields (succ, fail, etc.) to point to the correct peer object, reproducing the IR_t DCG pointer structure in the emitted language.
  - Handles cycles: for back-edge targets (nodes whose ID appears as a successor before being declared), use a forward-reference slot filled after all allocations.
  - Returns the entry node object.

  Then SM_EXEC_GEN (the replacement for SM_EXEC_STMT) calls this wiring function, invokes `entry.alpha()` (JVM) or `entry.alpha()` (JS), and stores the match result.

  **Gate:** A full SNOBOL4 smoke program (hello + pattern match + goto) produces correct output on both JVM and JS targets via the IR_t emitter path.

---

## State

```
watermark: IEP-0
head: (not started)
session: (not started)
```

---

## Key invariants

- **Emitters read IR_t only.** No emitter in this GOAL reads SM_Program. SM_Program is an output of the x86 emitter path; it is not an input to JVM/JS emitters.
- **One IR_t per stage.** Lower produces exactly one IR_t. The emitter receives exactly one IR_t. No side-channels, no parallel structures.
- **BB reference implementations are in bb_boxes.j and bb_boxes.js.** Before writing any BB emitter template, read the corresponding entry in those files. They are complete and tested. The emitter generates equivalent code parameterized by IR_t node payload.
- **Individual box files accessible via git.** Original per-box files were at `src/runtime/boxes/NAME/bb_NAME.j` and `.js`, consolidated at commit `660339cd`. Use `git show 660339cd:src/runtime/boxes/lit/bb_lit.j` etc. to read a single box in isolation.
- **x86 path unchanged.** The existing `--sm-emit --target=x64` path keeps reading SM_Program. Only JVM and JS (and future targets) use the new IR_t path. The x86 path will migrate later under GOAL-LOWER-REDESIGN.
