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

Three hard rules — no exceptions:

1. **IR_t makes no reference, direct or indirect, to tree_t.** The IR graph is self-contained. Lower fully consumes tree_t and produces IR_block_t. No tree_t* anywhere in IR_t nodes, IR_block_t, or any struct reachable from them.

2. **SM opcodes make no reference, direct or indirect, to IR_block_t or IR_t.** SM_Program is a flat serializable instruction array. No IR_block_t* or IR_t* in any SM_Instr field. References to DCGs are integer indices into SM_Program.dcg_table — an owned roster whose entries are serialized inline by the emitter.

3. **SM opcodes make no reference, direct or indirect, to tree_t.** No tree_t* in any SM_Instr field. All AST data is fully lowered to IR before lower exits.

**Done when:** All three rules hold. Mode 4 (emit→asm→link→exec) is correct: no live-process pointer from any prior phase survives into emitted output.

---

## Architecture: the correct pipeline

```
source → parser → tree_t
                    ↓ lower CONSUMES tree_t completely
                  IR_block_t   ← self-contained; no tree_t* anywhere inside
                    ↓ emitter walks IR_block_t
                  bytes / asm  ← no pointers to prior phases
```

SM_Program is an internal carrier for the x86 path. After this GOAL:
- SM_Program.dcg_table[] owns all IR_block_t entries (integer-indexed from SM opcodes)
- SM_Instr has no void*/tree_t*/IR_block_t* cross-phase fields
- every_table is eliminated (it held tree_t* keyed by SM opcode operand)
- SM_PUSH_EXPR is eliminated (it carried a tree_t* clone)

---

## Audit of violations (as of IEP-4)

### Rule 1: IR_t → tree_t (CLEAN)
IR_t.opaque holds runtime structs (icn_alt_dcg_t, GeneratorState etc) — all created by lower, not references into tree_t. ✅ No violation.

### Rule 2: SM opcodes → IR_block_t / IR_t (IEP-4 partially fixed)
| Site | Status |
|------|--------|
| SM_EXEC_STMT a[2] was IR_block_t* | ✅ Fixed IEP-4 — now dcg_table index |
| SM_EXEC_BB a[0] was IR_block_t* | ✅ Fixed IEP-4 — now dcg_table index |
| SM_BB_EVAL a[0].i = every_table index → every_table[i] = tree_t* | ⏳ IEP-5 |

### Rule 3: SM opcodes → tree_t (OPEN)
| Site | Status |
|------|--------|
| SM_PUSH_EXPR a[0].ptr = tree_t* (ast_gc_clone) | ⏳ IEP-6 |
| DESCR_t.ptr cast to tree_t* in sm_interp (SM_PUSH_EXPR consumer) | ⏳ IEP-6 (eliminated with opcode) |
| DESCR_t.ptr cast to tree_t* for Prolog goal (sm_interp) | ⏳ IEP-6 |

### Note: runtime mutable state in SM_Instr (separate concern)
icn_to_state_t* / icn_to_by_state_t* in SM_Instr.a[2].ptr are allocated by the interpreter at runtime (not by lower) and mutated per-execution. These are not cross-phase leaks from lower — they are mutable execution state embedded in the instruction. Mode-4 fix for these is a separate GOAL (they need to become per-call stack allocations, not instruction-embedded pointers). NOT in scope here.

---

## Completed steps

- [x] **IEP-1** — emit_ir_block entry point + ir_node_id stubs. ✅ `b7f54805`
- [x] **IEP-2** — ir_walk DFS visitor + ir_is_generator. ✅ `e942e468`
- [x] **IEP-3** — scrip.c wired: --target=jvm/js → emit_ir_block; --x64 unchanged. ✅ `35142ba5`
- [x] **IEP-VTABLE** — IR_emit_vtable_t dispatch inside single walk; emit_ir_targets.c with 6 stub vtables. ✅ `92f628b0`
- [x] **IEP-INCLUDE** — src/include/ with 6 stage-boundary headers; forward shims; -I$(SRC)/include. ✅ `b77d3729`
- [x] **IEP-RENAME** — scrip_ir.h → src/include/IR.h; mass-replace. ✅ `1e7a7f5e`
- [x] **IEP-4** — SM_EXEC_STMT and SM_EXEC_BB: IR_block_t* → dcg_table integer index. sm_prog_dcg_add + sm_emit_sii added. Both interpreters updated. ✅ `d9dff43a`

---

## Remaining steps

### IEP-5 — Eliminate every_table (tree_t* keyed by SM_BB_EVAL index)

- [ ] **IEP-5** — every_table[] in sm_interp holds tree_t* entries, indexed by SM_BB_EVAL's integer operand. This is an indirect tree_t reference from SM opcodes (Rule 3 violation). Replace:
  1. In lower.c, wherever `every_table_register(tree_t* t)` is called: instead call `IR_lower_icn_gen(t)` to produce `IR_block_t*`, register via `sm_prog_dcg_add`, emit the dcg index as the SM_BB_EVAL operand.
  2. In sm_interp and sm_jit_interp: SM_BB_EVAL resolves `sm->dcg_table[idx]` instead of `every_table_lookup(id)`.
  3. Delete `every_table_register`, `every_table_lookup`, `every_table_reset`, the `every_table[]` array, and `SM_BB_PUMP_EVERY` if it also uses every_table.
  4. IR_lower_icn_gen must produce a fully self-contained IR_block_t — no tree_t* inside.

  **Gate:** Symbol `every_table` absent from codebase. SM_BB_EVAL operand is a dcg_table index. scrip --sm-run Icon corpus gate unchanged.

### IEP-6 — Eliminate SM_PUSH_EXPR (tree_t* in SM_Instr)

- [ ] **IEP-6** — SM_PUSH_EXPR carries `a[0].ptr = tree_t*` (a GC-cloned AST subtree for deferred eval). This is a direct tree_t reference from SM opcodes (Rule 3 violation). Replace:
  1. In lower.c, `emit_push_expr(tree_t* t)`: call `IR_lower_expr(t)` to produce a scalar IR_t subtree, wrap in IR_block_t, register via `sm_prog_dcg_add`, emit `SM_PUSH_IR_EXPR` with the dcg index.
  2. In sm_interp and sm_jit_interp: SM_PUSH_IR_EXPR resolves `sm->dcg_table[idx]`, evaluates via `IR_exec_once`, pushes result.
  3. All DESCR_t.ptr casts to tree_t* that come from SM_PUSH_EXPR consumers are eliminated with the opcode.
  4. Remove SM_PUSH_EXPR from sm_prog.h. Remove ast_gc_clone dependency from lower.c.
  5. IR_lower_expr must produce a fully self-contained IR_block_t — no tree_t* inside.

  **Gate:** SM_PUSH_EXPR absent from sm_prog.h. ast_gc_clone not called from lower.c. All (tree_t*)expr_d.ptr casts gone from interpreters. scrip --sm-run on full SNOBOL4 corpus unchanged.

### IEP-7 — Audit and verify all three rules hold

- [ ] **IEP-7** — Confirm all three rules:
  1. `grep -rn "tree_t" src/include/IR.h src/lower/ir_exec.c src/lower/lower_icn.c` — zero tree_t references in IR subsystem files.
  2. `grep -n "void \*ptr\|tree_t \*\|IR_block_t \*" src/include/sm_prog.h` — zero cross-phase pointer fields in SM_Instr (dcg_table itself is allowed — it is the owned roster).
  3. `grep "sm_emit_ptr\|\.ptr\s*=" src/lower/lower.c` — zero pointer-embedding calls in lower (only integer/string/float operands emitted).
  4. Run scrip --jit-emit --x64 on beauty.sno — output byte-identical to pre-IEP-4 baseline.

  Note: icn_to_state_t* / icn_to_by_state_t* in SM_Instr.a[2].ptr are runtime-mutable execution state (not lower sidecars) — flagged for a separate GOAL, not blocking here.

---

## What next GOALs plug in here

**GOAL-SN4-JVM-EMIT:** fill g_emit_vtable_jvm.emit_scalar and .emit_generator in src/emitter/emit_jvm.c.
**GOAL-SN4-JS-EMIT:** same for g_emit_vtable_js in src/emitter/emit_js.c.
**Mode-4 runtime state:** icn_to_state_t* embedded in SM_Instr needs its own GOAL — per-call stack allocation replacing instruction-embedded mutable pointer.

---

## State

```
watermark: IEP-4 (IEP-5/6/7 open)
head: d9dff43a
session: 2026-05-15 (Claude Sonnet 4.6)
```

---

## Key invariants

- **One entry point.** emit_ir_block is the sole emitter entry for all 6 backends × all 6 frontends.
- **One walk.** ir_walk traverses the DCG once; the vtable selects per-node template functions.
- **IR_block_t is the stage boundary.** Lower produces it. Emitters receive it. SM_Program is pointer-free after IEP-5/6.
- **src/include/ is the canonical header location.**
- **No C Byrd box functions.**
