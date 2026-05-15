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

1. **After parser exits: tree_t is deleted.** Lower may not reference tree_t at all after lower() returns. Enforced by freeing tree_t immediately after lower() completes. Any dangling reference crashes.

2. **After lower exits: IR_block_t is deleted from lower's local scope.** The emitter receives the dcg_table (owned by SM_Program) — not a live IR pointer from lower's heap. Enforced by calling IR_free on lower's locally-produced IR_block_t after registering it in dcg_table. Any dangling reference crashes.

3. **SM opcodes contain no pointers to prior phases.** SM_Instr fields are integers, strings (interned), and floats only. No void*, tree_t*, or IR_block_t* in any SM_Instr operand used as a cross-phase carrier.

**Shared tables (label_table, proc_table, g_pl_pred_table) are built from tree_t before lower runs and are legitimate shared state — they are not references into the tree structure itself.**

**Done when:** tree_t freed after lower(); IR_block_t freed after dcg_table registration; SM_Instr has no cross-phase pointer fields; all three modes (--sm-run, --jit-run, --jit-emit) pass on beauty.sno.

---

## Architecture: the correct pipeline

```
source → parser → tree_t + shared tables (label_table, proc_table, g_pl_pred_table)
                    ↓ lower() consumes tree_t
                    ↓ lower() registers IR_block_t entries into SM_Program.dcg_table
                    ↓ tree_t DELETED immediately after lower() returns
                  SM_Program (dcg_table[] owns IR_block_t entries by index)
                    ↓ emitter walks dcg_table entries
                    ↓ IR_block_t entries DELETED after emitter finishes each one
                  bytes / asm — no pointers to any prior phase
```

---

## Completed steps

- [x] **IEP-1** — emit_ir_block entry point + ir_node_id stubs. ✅ `b7f54805`
- [x] **IEP-2** — ir_walk DFS visitor + ir_is_generator. ✅ `e942e468`
- [x] **IEP-3** — scrip.c wired: --target=jvm/js → emit_ir_block; --x64 unchanged. ✅ `35142ba5`
- [x] **IEP-VTABLE** — IR_emit_vtable_t dispatch inside single walk; emit_ir_targets.c. ✅ `92f628b0`
- [x] **IEP-INCLUDE** — src/include/ with 6 stage-boundary headers; forward shims. ✅ `b77d3729`
- [x] **IEP-RENAME** — scrip_ir.h → src/include/IR.h; mass-replace. ✅ `1e7a7f5e`
- [x] **IEP-4** — SM_EXEC_STMT and SM_EXEC_BB: IR_block_t* → dcg_table integer index. ✅ `d9dff43a`

---

## Remaining steps

### IEP-5 — Eliminate every_table (indirect tree_t* reference from SM_BB_EVAL)

- [ ] **IEP-5** — `every_table[]` holds `tree_t*` entries indexed by `SM_BB_EVAL`'s integer operand. This is an indirect tree_t reference from SM opcodes — violates Rule 3. Replace:
  1. In lower.c, replace every `every_table_register(tree_t* t)` call: call `IR_lower_icn_gen(t)` to produce `IR_block_t*`, register via `sm_prog_dcg_add`, emit the dcg index as the `SM_BB_EVAL` operand. `IR_lower_icn_gen` must produce a fully self-contained `IR_block_t` — no `tree_t*` inside.
  2. In sm_interp and sm_jit_interp: `SM_BB_EVAL` resolves `sm->dcg_table[idx]` instead of `every_table_lookup(id)`.
  3. Delete `every_table_register`, `every_table_lookup`, `every_table_reset`, `every_table[]`. Delete `SM_BB_PUMP_EVERY` if it also uses every_table.

  **Gate:** Symbol `every_table` absent from codebase. `scrip --sm-run` Icon corpus gate unchanged.

### IEP-6 — Eliminate SM_PUSH_EXPR (direct tree_t* in SM_Instr)

- [ ] **IEP-6** — `SM_PUSH_EXPR` carries `a[0].ptr = tree_t*` (a GC-cloned AST subtree). Direct tree_t reference from SM opcodes — violates Rule 3. Replace:
  1. In lower.c, `emit_push_expr(tree_t* t)`: call `IR_lower_expr(t)` to produce a scalar `IR_t` subtree, wrap in `IR_block_t`, register via `sm_prog_dcg_add`, emit `SM_PUSH_IR_EXPR` with the dcg index. `IR_lower_expr` must produce a fully self-contained `IR_block_t` — no `tree_t*` inside.
  2. In sm_interp and sm_jit_interp: `SM_PUSH_IR_EXPR` resolves `sm->dcg_table[idx]`, evaluates via `IR_exec_once`, pushes result. All `(tree_t*)expr_d.ptr` casts eliminated.
  3. Remove `SM_PUSH_EXPR` from sm_prog.h. Remove `ast_gc_clone` from lower.c.

  **Gate:** `SM_PUSH_EXPR` absent from sm_prog.h. `ast_gc_clone` not called from lower.c. `scrip --sm-run` on full SNOBOL4 corpus unchanged.

### IEP-7 — Delete tree_t immediately after lower() returns (Rule 1 enforcement)

- [ ] **IEP-7** — In scrip.c and scrip_sm.c, immediately after `lower(ast_prog)` / `sm_preamble(ast_prog)` returns successfully, call `code_free(code)` and null out `ast_prog`. This frees the entire parser-phase tree. Any code that retained a pointer into tree_t will crash immediately — making silent violations impossible.

  `code_free` exists in `ast_clone.c` but is never called. Wire it:
  - In `sm_preamble()` in `scrip_sm.c`: after `SM_Program *sm = lower(ast_prog)`, call `code_free` and set `ast_prog = NULL`.
  - In the `--dump-sm` path in scrip.c (which calls `lower()` directly): same treatment.
  - In `execute_program` (mode 1 / --ast-run): tree_t IS the program — do NOT free here. Mode 1 is exempt because it walks the tree directly; it has no lower phase. Document this exemption explicitly.

  **Gate:** `scrip --sm-run beauty.sno` and `scrip --jit-run beauty.sno` pass. Any surviving dangling pointer crashes immediately on the first run after this step, exposing any IEP-5/6 violations not yet fixed.

  ⛔ **IEP-7 must run AFTER IEP-5 and IEP-6 are complete.** Freeing tree_t before eliminating every_table and SM_PUSH_EXPR will crash because they still hold tree_t pointers. IEP-5 and IEP-6 first, then IEP-7.

### IEP-8 — Delete IR_block_t after dcg_table registration (Rule 2 enforcement)

- [ ] **IEP-8** — After lower registers each `IR_block_t*` into `dcg_table` via `sm_prog_dcg_add`, the local `IR_block_t*` in lower must be freed — lower no longer owns it; `SM_Program.dcg_table` owns it. After the emitter processes each dcg_table entry in `emit_ir_block`, free that entry via `IR_free`. This enforces that no code retains a live IR pointer beyond its phase.

  Concretely:
  - In lower.c: after each `sm_prog_dcg_add(g_p, pat_dcg)` call, do NOT free pat_dcg (dcg_table now owns it). Document ownership transfer clearly.
  - In `sm_prog_free()`: call `IR_free(dcg_table[i])` for each entry before freeing `dcg_table` itself.
  - In `emit_ir_block`: after calling `ir_walk` on `cfg`, call `IR_free(cfg)` only if the emitter is the terminal consumer (i.e. mode 4). In modes 2/3, dcg_table entries must survive for the interpreter. Add an `IR_emit_vtable_t.owns_dcg` flag — mode-4 emitters set it to 1.

  **Gate:** valgrind on `scrip --jit-emit --x64 beauty.sno` shows zero IR_block_t leaks.

### IEP-9 — Final audit: all three rules verified by construction

- [ ] **IEP-9** — Confirm by construction:
  1. `grep -rn "ast_prog\|tree_t\b" src/lower/lower.c` after IEP-7 — no live ast_prog reference after `lower()` returns.
  2. `grep -n "void \*ptr" src/include/sm_prog.h` — `sm_operand_t.ptr` field removed or commented "runtime state only — no cross-phase use".
  3. `grep "sm_emit_ptr\|\.ptr\s*=" src/lower/lower.c` — zero hits.
  4. `scrip --sm-run beauty.sno` and `scrip --jit-run beauty.sno` — pass.
  5. `scrip --jit-emit --x64 beauty.sno` — byte-identical to pre-IEP-4 baseline.

  Note: `icn_to_state_t*` / `icn_to_by_state_t*` in `SM_Instr.a[2].ptr` are runtime-mutable execution state written by the interpreter itself — not lower sidecars. They are a separate mode-4 concern (need per-call stack allocation) tracked in a future GOAL.

---

## What next GOALs plug in here

**GOAL-SN4-JVM-EMIT:** fill `g_emit_vtable_jvm` in `src/emitter/emit_jvm.c`.
**GOAL-SN4-JS-EMIT:** fill `g_emit_vtable_js` in `src/emitter/emit_js.c`.
**Runtime state in SM_Instr:** `icn_to_state_t*` per-call allocation — separate GOAL.

---

## State

```
watermark: IEP-4 (IEP-5/6/7/8/9 open)
head: d9dff43a
session: 2026-05-15 (Claude Sonnet 4.6)
```

---

## Key invariants

- **One entry point.** `emit_ir_block` is the sole emitter entry for all 6 backends × all 6 frontends.
- **One walk.** `ir_walk` traverses the DCG once; the vtable selects per-node template functions.
- **Phases are isolated by deletion.** tree_t deleted after lower(). IR_block_t owned by dcg_table, freed by sm_prog_free(). No silent dangling references.
- **src/include/ is the canonical header location.**
- **No C Byrd box functions.**
