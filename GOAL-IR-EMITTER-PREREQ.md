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

---

## Goal statement

Lower must consume `tree_t` completely and produce one self-contained `IR_block_t` — the DCG — that encodes the entire program: scalar expressions, pattern structure, control flow, procedure definitions, deferred evaluations, generator expressions. Nothing left dangling as a `tree_t*` or raw pointer in `SM_Program`. The emitter walks the DCG and emits bytes. It never looks back at `tree_t`. It never follows a pointer to something outside the graph.

**Done when:** `SM_Program` contains zero `tree_t*` and zero `IR_block_t*` pointer fields. Every reference to prior-phase data is an integer index into a DCG roster (`dcg_table`) owned by `SM_Program`. The emitter serializes the DCG roster inline — no live-process pointer survives into emitted output. Mode 4 (emit→asm→link→exec) is possible.

---

## Architecture: the correct pipeline

```
source
  → parser
  → tree_t + CODE_t        (label_table / proc_table / g_pl_pred_table built here — legitimate pre-lower state)

tree_t
  → lower                  (consumes tree_t COMPLETELY)
  → IR_block_t             (DCG — self-contained; no tree_t* inside; no pointers to other phases)
      scalar exprs         → IR_LIT_*, IR_VAR, IR_BINOP, IR_CALL, IR_ASSIGN, IR_RETURN ...
      pattern structure    → IR_PAT_LIT, IR_PAT_SPAN, IR_PAT_CAT, IR_PAT_ALT ...
      deferred exprs       → IR_t subtrees (not tree_t* clones)
      generator exprs      → IR_t subtrees (not every_table tree_t* entries)
      control flow         → IR_GOTO, IR_LABEL, IR_PROC ...
      proc bodies          → IR_PROC subtrees

IR_block_t
  → emitter                (walks DCG, calls vtable, emits bytes)
  → no tree_t* anywhere
  → no IR_block_t* hanging off SM opcodes
  → no live pointers of any kind in output
```

---

## Three pointer sidecars to eliminate

Today lower embeds raw pointers from prior phases into `SM_Program`. All three must become DCG-resident `IR_t` nodes:

| Opcode | Embedded pointer | Mechanism | Problem |
|--------|-----------------|-----------|---------|
| `SM_EXEC_STMT` | `void* = IR_block_t*` | `sm_emit_sip(…, pat_dcg)` | Pattern DCG pointer — dies in mode 4 |
| `SM_PUSH_EXPR` | `void* = tree_t*` | `sm_emit_ptr(SM_PUSH_EXPR, ast_gc_clone(t))` | Deferred AST pointer — dies in mode 4 |
| `SM_BB_EVAL` / `SM_BB_PUMP_EVERY` | `int64_t = every_table index` | `every_table_register(tree_t*)` | `every_table[]` holds `tree_t*` — index is safe but the table it points into holds live AST pointers; must migrate to DCG roster |

---

## Completed steps

- [x] **IEP-1** — `emit_ir_block` entry point + `ir_node_id` stubs. ✅ `b7f54805`
- [x] **IEP-2** — `ir_walk` DFS visitor + `ir_is_generator`. ✅ `e942e468`
- [x] **IEP-3** — `scrip.c` wired: `--target=jvm/js` → `emit_ir_block`; `--x64` unchanged. ✅ `35142ba5`
- [x] **IEP-VTABLE** — `IR_emit_vtable_t` dispatch inside single walk; `emit_ir_targets.c` with 6 stub vtables. ✅ `92f628b0`
- [x] **IEP-INCLUDE** — `src/include/` with 6 stage-boundary headers; forward shims; `-I$(SRC)/include`. ✅ `b77d3729`
- [x] **IEP-RENAME** — `scrip_ir.h` → `src/include/IR.h`; mass-replace. ✅ `1e7a7f5e`

---

## Remaining steps

### IEP-4 — Add DCG roster to SM_Program; replace SM_EXEC_STMT IR_block_t* with index

- [x] **IEP-4** — Add `IR_block_t **dcg_table; int dcg_count; int dcg_cap;` to `SM_Program` in `src/include/sm_prog.h`. Add `sm_prog_dcg_add(SM_Program*, IR_block_t*) -> int` in `sm_prog.c` — appends to roster, returns integer index. In `lower.c`, replace:
  ```c
  sm_emit_sip(g_p, SM_EXEC_STMT, sname, (int64_t)has_eq, (void *)pat_dcg);
  ```
  with:
  ```c
  sm_emit_sii(g_p, SM_EXEC_STMT, sname, (int64_t)has_eq, (int64_t)sm_prog_dcg_add(g_p, pat_dcg));
  ```
  Update runtime (`sm_interp.c`, `sm_jit_interp.c`) to resolve the index: `sm->dcg_table[idx]` replaces the old `(IR_block_t*)a[2].ptr`. Add `sm_prog_free` to free `dcg_table` entries. `SM_EXEC_STMT`'s third operand is now always an integer — no pointer in `SM_Instr`.

  **Gate:** `scrip --sm-run` and `scrip --jit-run` on beauty.sno produce identical output before and after. `grep "void \*ptr" src/include/sm_prog.h` — pointer field only on `SM_PUSH_EXPR` (not yet removed).

### IEP-5 — Migrate every_table tree_t* into DCG roster; replace SM_BB_EVAL index

- [ ] **IEP-5** — `every_table[]` in `sm_interp.c` holds `tree_t*` entries indexed by `SM_BB_EVAL`'s operand. Replace: lower calls `IR_lower_icn_gen(tree_t*)` to produce an `IR_block_t*` for each Icon generator expression, registers it via `sm_prog_dcg_add`, emits the integer index. Runtime resolves `sm->dcg_table[idx]` instead of `every_table_lookup(id)`. Delete `every_table_register`, `every_table_lookup`, `every_table_reset` and the `every_table[]` array once all sites migrated. Affects `SM_BB_EVAL` and `SM_BB_PUMP_EVERY` operands throughout `lower.c`.

  **Gate:** `every_table` symbol absent from codebase. `scrip --sm-run` Icon corpus gate unchanged.

### IEP-6 — Lower deferred expressions to IR_t; eliminate SM_PUSH_EXPR

- [ ] **IEP-6** — `SM_PUSH_EXPR` carries a cloned `tree_t*` for deferred eval (pattern arguments, indirect refs, etc.). Replace `emit_push_expr(t)` in `lower.c` with `emit_push_ir_expr(t)`: call `IR_lower_expr(tree_t*) -> IR_t*` to produce a scalar `IR_t` subtree, register the containing `IR_block_t` via `sm_prog_dcg_add`, emit `SM_PUSH_IR_EXPR` with integer index. Runtime evaluates via `IR_exec_once(sm->dcg_table[idx])`. Remove `SM_PUSH_EXPR` opcode from `sm_prog.h` and `ast_clone.h` dependency from `lower.c` once all sites migrated.

  **Gate:** `SM_PUSH_EXPR` opcode absent from codebase. `ast_gc_clone` not called from `lower.c`. `scrip --sm-run` on full SNOBOL4 corpus unchanged.

### IEP-7 — Verify SM_Program is pointer-free; confirm mode 4 readiness

- [ ] **IEP-7** — Audit `SM_Instr` for any remaining `void*` or `tree_t*` or `IR_block_t*` fields used as cross-phase carriers. Run:
  ```bash
  grep -n "void \*ptr\|tree_t \*\|IR_block_t \*" src/include/sm_prog.h
  ```
  Must return zero hits outside `dcg_table` itself. The only pointer surviving in `SM_Program` is `dcg_table` — the owned roster of `IR_block_t*` entries that IS the serializable payload. String literals (`char*` in `SM_PUSH_LIT_S` etc.) are data, not phase-boundary objects.

  Run `scrip --jit-emit --x64` on beauty.sno — output byte-identical to pre-IEP-4 baseline. Mode 4 readiness confirmed.

---

## What next GOALs plug in here

**GOAL-SN4-JVM-EMIT:** fill `g_emit_vtable_jvm.emit_scalar` and `.emit_generator` in `src/emitter/emit_jvm.c`. Walk `IR_t` nodes, emit Jasmin code equivalent to `src/runtime/jvm/bb_boxes.j`.

**GOAL-SN4-JS-EMIT:** same for `g_emit_vtable_js` in `src/emitter/emit_js.c`, targeting `src/runtime/js/bb_boxes.js`.

**x86 vtable wiring:** `g_emit_vtable_x86.emit_prologue` calls `sm_codegen_text` — wired when lower produces `IR_block_t` directly (this GOAL).

---

## State

```
watermark: IEP-4 (IEP-5/6/7 open)
head: d9dff43a
session: 2026-05-15 (Claude Sonnet 4.6)
```

---

## Key invariants

- **One entry point.** `emit_ir_block` is the sole emitter entry for all 6 backends × all 6 frontends.
- **One walk.** `ir_walk` traverses the DCG once; the vtable selects per-node template functions.
- **IR_block_t is the stage boundary.** Lower produces it. Emitters receive it. `SM_Program` is an internal carrier for the x86 path only — and after IEP-4/5/6 it is pointer-free.
- **`src/include/` is the canonical header location.** Stage-boundary types live there.
- **No C Byrd box functions.** Zero `DESCR_t foo(void *zeta, int entry)` functions.
