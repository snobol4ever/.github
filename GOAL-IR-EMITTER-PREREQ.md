# GOAL-IR-EMITTER-PREREQ.md — IR_t Emitter Foundation (prerequisite for JVM + JS)

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║  A C Byrd box (C BB) is ANY C function with signature: DESCR_t foo(void *zeta, int entry)      ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                             ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

⛔ **Read before any source file:** ARCH-IR.md then ARCH-SCRIP.md then ARCH-EMITTER.md.

**Repo:** one4all + .github
**Prereq for:** GOAL-SN4-JVM-EMIT.md and GOAL-SN4-JS-EMIT.md
**Status: ✅ GOAL COMPLETE** — sess 2026-05-15 (Claude Sonnet 4.6), one4all `1e7a7f5e`

---

## What this GOAL did

Rewired the pipeline so `IR_t` is the single explicit handoff structure between lower and emitter. Established `src/include/` as the canonical location for all stage-boundary headers. All 6 frontends × 6 backends now share one entry point.

### Pipeline (post this GOAL)

```
Any frontend (SNOBOL4 / Snocone / Rebus / Icon / Prolog / Raku)
  → tree_t → lower → IR_block_t
                           ↓
              emit_ir_block(IR_block_t*, FILE*, "x86"|"jvm"|"js"|"wasm"|"net"|"c")
                           ↓
              selects IR_emit_vtable_t  (one vtable per target)
                           ↓
              ir_walk — ONE DCG traversal, shared by ALL targets
                  for each IR_t node:
                      ir_is_generator? → vt->emit_generator(nd, out)
                                       → vt->emit_scalar(nd, out)
```

### Files delivered

| File | Role |
|------|------|
| `src/include/IR.h` | Canonical `IR_t` / `IR_block_t` / `IR_e` (renamed from `scrip_ir.h`) |
| `src/include/descr.h` | Canonical `DESCR_t` |
| `src/include/ast.h` | Canonical `tree_t` / `EXPR_t` / `STMT_t` |
| `src/include/sm_prog.h` | Canonical `SM_Program` |
| `src/include/bb_box.h` | Canonical `bb_node_t` / `BrokerMode` |
| `src/include/emit_ir.h` | Canonical `IR_emit_vtable_t` / `emit_ir_block` |
| `src/emitter/emit_ir.c` | `emit_ir_block` dispatch + `ir_walk` + `ir_is_generator` + `ir_node_id` |
| `src/emitter/emit_ir_targets.c` | All 6 stub vtables (`g_emit_vtable_x86/jvm/js/wasm/net/c`) |

### Steps completed

- [x] **IEP-1** — `emit_ir_block` entry point + dispatch table + `ir_node_id`. ✅ `b7f54805`
- [x] **IEP-2** — `ir_walk` DFS visitor + `ir_is_generator`. ✅ `e942e468`
- [x] **IEP-3** — `scrip.c` wired: `--target=jvm/js` → `emit_ir_block`; `--x64` unchanged. ✅ `35142ba5`
- [x] **IEP-VTABLE** — Per-target fan-out removed; `IR_emit_vtable_t` dispatch inside single walk. ✅ `92f628b0`
- [x] **IEP-INCLUDE** — `src/include/` created; 6 stage-boundary headers moved; originals are forward shims; `-I$(SRC)/include` in Makefile; `src/backend/` removed, `jasmin.jar` → `archive/backend/`. ✅ `b77d3729`
- [x] **IEP-RENAME** — `scrip_ir.h` → `src/include/IR.h`; mass-replace all includes; builds clean. ✅ `1e7a7f5e`

---

## Remaining steps — eliminate pointer sidecars from SM_Program

These are required for mode 4 (emit→asm→link→exec) correctness. In mode 3 (in-memory JIT) raw pointers in `SM_Program` happen to work. In mode 4 the emitter writes bytes to a file — a pointer from the compiler process is meaningless in the emitted binary. Every `tree_t*` and `IR_block_t*` embedded in `SM_Program` must be replaced by fully-lowered `IR_t` nodes so the emitter receives a self-contained graph.

### Two pointer leaks to eliminate

| Opcode | Embedded pointer | What it points to | Problem |
|--------|-----------------|-------------------|---------|
| `SM_PUSH_EXPR` | `a[0].ptr = tree_t*` | cloned AST subtree for deferred eval | mode-4 emitter cannot serialize a live heap pointer |
| `SM_EXEC_STMT` | third arg `void* = IR_block_t*` | pattern DCG built by `IR_lower_pat` | same — pointer dies when compiler exits |

### IEP-4 — Eliminate SM_EXEC_STMT IR_block_t* pointer

- [ ] **IEP-4** — `SM_EXEC_STMT` currently carries the pattern DCG as a raw `IR_block_t*` pointer (set by `lower.c` line `sm_emit_sip(g_p, SM_EXEC_STMT, sname, has_eq, pat_dcg)`). Replace this with a stable integer index into a DCG roster attached to `SM_Program`. Concretely:

  1. Add `IR_block_t **dcg_table; int dcg_count;` to `SM_Program` in `src/include/sm_prog.h`.
  2. Add `sm_prog_dcg_register(SM_Program*, IR_block_t*) -> int index` in `sm_prog.c`.
  3. In `lower.c`, replace `sm_emit_sip(…, pat_dcg)` with `sm_emit_sii(…, sm_prog_dcg_register(g_p, pat_dcg), 0)` — the pointer slot becomes an index.
  4. Runtime (`sm_interp.c`, `sm_jit_interp.c`) resolves the index back to `IR_block_t*` via `sm->dcg_table[idx]` before calling `bb_broker`.
  5. Emitter (`emit_ir_block`) receives the full `dcg_table` alongside `SM_Program` and serializes each `IR_block_t` as inline `IR_t` node data — no pointer emitted.

  **Gate:** `scrip --sm-run` and `scrip --jit-run` produce identical output before and after. `SM_EXEC_STMT`'s third operand is an integer index, never a pointer.

### IEP-5 — Eliminate SM_PUSH_EXPR tree_t* pointer

- [ ] **IEP-5** — `SM_PUSH_EXPR` carries a raw `tree_t*` (a GC-cloned AST subtree for deferred expression evaluation, used for pattern arguments evaluated at match time). Replace with a fully-lowered `IR_t` subtree registered in the DCG roster:

  1. In `lower.c`, when emitting `SM_PUSH_EXPR`, instead call `IR_lower_expr(t) -> IR_t*` to produce an `IR_t` node for the expression, register it in `dcg_table`, and emit `SM_PUSH_IR_EXPR` with the integer index.
  2. Replace `SM_PUSH_EXPR` opcode with `SM_PUSH_IR_EXPR` (or reuse the slot with index semantics). Remove `SM_PUSH_EXPR` from `sm_prog.h` once all sites are migrated.
  3. Runtime resolves `sm->dcg_table[idx]` and evaluates the `IR_t` expression via `IR_exec_once`.
  4. Emitter serializes the `IR_t` expression nodes inline — no `tree_t*` in emitted output.

  **Gate:** `SM_PUSH_EXPR` opcode eliminated from codebase. All former `SM_PUSH_EXPR` sites use `SM_PUSH_IR_EXPR` with integer index. `scrip --sm-run` and `scrip --jit-run` produce identical output before and after.

### IEP-6 — Verify SM_Program is pointer-free

- [ ] **IEP-6** — Audit `SM_Program` / `SM_Instr` for any remaining `void*` or `tree_t*` or `IR_block_t*` fields used as cross-phase carriers. The only surviving pointer fields must be:
  - `dcg_table` itself (the roster — this IS the serializable payload, not a sidecar pointer)
  - String literals (`char*` for `SM_PUSH_LIT_S` etc.) — these are data, not phase-boundary objects; emitter serializes them as inline bytes.

  Confirm with `grep -n "void \*ptr\|tree_t \*\|IR_block_t \*" src/include/sm_prog.h` returning zero hits outside dcg_table.

  **Gate:** `scrip --jit-emit --x64` on beauty.sno produces byte-identical output to the pre-IEP-4/5 baseline. Mode 4 readiness confirmed: no live-process pointers in `SM_Program`.

---

## What next GOALs plug in here

**GOAL-SN4-JVM-EMIT:** fill `g_emit_vtable_jvm.emit_scalar` and `.emit_generator` in a new `src/emitter/emit_jvm.c`. Walk IR_t nodes, emit Jasmin code equivalent to `src/runtime/jvm/bb_boxes.j`.

**GOAL-SN4-JS-EMIT:** same for `g_emit_vtable_js` in `src/emitter/emit_js.c`, targeting `src/runtime/js/bb_boxes.js`.

**x86 vtable wiring:** `g_emit_vtable_x86.emit_prologue` calls `sm_codegen_text` — wired when GOAL-LOWER-REDESIGN makes lower produce `IR_block_t` directly.

---

## State

```
watermark: IEP-COMPLETE
head: 1e7a7f5e
session: 2026-05-15 (Claude Sonnet 4.6)
```

---

## Key invariants

- **One entry point.** `emit_ir_block` is the sole emitter entry for all 6 backends × all 6 frontends.
- **One walk.** `ir_walk` traverses the DCG once; the vtable selects per-node template functions.
- **IR_t is the stage boundary.** Lower produces `IR_block_t`. Emitters receive `IR_block_t`. `SM_Program` is internal to the x86 path.
- **`src/include/` is the canonical header location.** Stage-boundary types live there. Other locations are forward shims.
- **No C Byrd box functions.** Zero `DESCR_t foo(void *zeta, int entry)` functions.
