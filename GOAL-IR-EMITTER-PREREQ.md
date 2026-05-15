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
