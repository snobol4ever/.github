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
**Done when:** `IR_t` is the single explicit handoff structure between lower and emitter; the existing x86 emitter receives `IR_t` (walks it to produce SM opcodes + BB code); the entry point `emit_ir_block` is live and dispatches correctly; JVM and JS emitters can plug into the same handoff point without further rewiring.

---

## What this GOAL does — and does NOT do

**Does:** Rewire the existing pipeline so `IR_t` is the named structure that crosses the lower→emitter stage boundary. The x86 emitter (which already exists and works) is the first consumer of this rewired path. GOAL-SN4-JVM-EMIT and GOAL-SN4-JS-EMIT then plug their own emitters into the same `emit_ir_block` dispatch point.

**Does NOT:** Implement JVM or JS emitters. That is GOAL-SN4-JVM-EMIT and GOAL-SN4-JS-EMIT respectively. Those goals add `emit_ir_block_jvm` and `emit_ir_block_js` implementations that walk `IR_t` and emit Jasmin / JS code equivalent to `bb_boxes.j` / `bb_boxes.js`.

---

## Architecture: the correct pipeline

The stages pass exactly ONE structure between them:

```
source
  → parser
  → tree_t          (AST — one named structure out)

tree_t
  → lower           (lower_sno.c / lower_icn.c / lower_pat_dcg.c)
  → IR_t            (DCG — one named structure out; the ONLY output of lower)

IR_t
  → emitter         (emit_ir_block dispatch → x86 now; jvm/js later)
  → SM opcodes      (for scalar expressions, control flow, function calls)
  + BB code         (for pattern/generator nodes)
```

**Lower produces IR_t. Emitters consume IR_t. SM_Program is an internal detail of the x86 emitter, not a stage boundary.**

Today's state: `lower.c` writes directly to `SM_Program` and attaches `IR_block_t` as a side channel on `SM_EXEC_STMT`. The emitter reads `SM_Program`. This GOAL makes `IR_t` the explicit single handoff — the x86 emitter still produces the same SM opcodes and BB code internally, but it now receives `IR_t` as input and produces that output itself by walking the DCG.

---

## IR_t node traversal

An `IR_t` node has four ports: `α` (start/alpha), `β` (resume/beta), `γ` (succ/gamma), `ω` (fail/omega). The emitter walks the DCG by following these pointers. Two node classes:

- **Scalar nodes** (IR_LIT_I, IR_LIT_S, IR_LIT_F, IR_LIT_NUL, IR_VAR, IR_ASSIGN, IR_BINOP, IR_CALL, IR_RETURN, IR_SEQ, IR_GOTO, IR_FAIL, IR_SUCCEED, IR_PROC) → emit SM opcode sequences.
- **Generator nodes** (all IR_PAT_*, IR_SCAN, IR_ALTERNATE, IR_TO_BY, IR_EVERY, IR_WHILE, IR_LIMIT, IR_SUSPEND, IR_ICN_*, IR_PL_*) → emit BB box code.

---

## Steps

### IEP-1 — Define the emitter entry point signature

- [x] **IEP-1** — `emit_ir_block(IR_block_t *cfg, FILE *out, const char *target)` in `src/emitter/emit_ir.h` / `emit_ir.c`. Dispatch table: calls `emit_ir_block_jvm` / `emit_ir_block_js` / `emit_ir_block_x86` etc. by target string. `ir_node_id(IR_t *nd)` — pointer-based stable ID. All per-target functions are stubs. Makefile wired. ✅ one4all `b7f54805`

### IEP-2 — IR_t traversal infrastructure: visitor

- [x] **IEP-2** — Implement `ir_walk(IR_block_t *cfg, void (*visit)(IR_t *nd, void *ctx), void *ctx)` in `src/emitter/emit_ir.c`. Walks all reachable IR_t nodes from `cfg->entry` following all four ports (α β γ ω), calling `visit` exactly once per node. Visited set keyed on `ir_node_id`. Handles cycles correctly. Also implement `ir_is_generator(IR_e kind)` — returns 1 for all IR_PAT_*, IR_SCAN, IR_ALTERNATE, IR_TO_BY, IR_EVERY, IR_WHILE, IR_LIMIT, IR_SUSPEND, IR_ICN_*, IR_PL_*; 0 for scalar kinds. ✅ one4all `e942e468`

  **Gate:** `ir_walk` on a hand-built DCG (IR_PAT_CAT of two IR_PAT_LIT nodes) visits exactly 3 nodes.

### IEP-3 — Wire scrip.c to pass IR_t to emitter

- [x] **IEP-3** — In `src/driver/scrip.c`, add `--target=jvm` and `--target=js` flag parsing (alongside existing `--jit-emit --x64`). For all `--jit-emit` targets: instead of calling `sm_codegen_text(sm, ...)` directly, obtain the `IR_block_t*` from lower and call `emit_ir_block(ir_cfg, stdout, target)`. The x86 target (`--target=x64`) keeps its current behaviour — `emit_ir_block_x86` calls through to `sm_codegen_text` internally. For jvm/js targets the stub prints its comment line. ✅ one4all `35142ba5`

  **Gate:** `scrip --target=jvm simple.sno` → prints `; JVM stub`, exits 0. ✅  `scrip --jit-emit --x64 simple.sno` → correct x86 asm. ✅

---

## State

```
watermark: IEP-COMPLETE
head: 1e7a7f5e
session: 2026-05-15 (Claude Sonnet 4.6)
```

---

## Key invariants

- **IR_t is the stage boundary.** Lower produces IR_t. Emitters receive IR_t. SM_Program is internal to the x86 emitter, not a pipeline stage.
- **x86 emitter output unchanged.** The existing `--jit-emit --x64` path produces identical output before and after this GOAL. Only the internal wiring changes — it now enters via `emit_ir_block_x86(IR_block_t*)` instead of directly via `sm_codegen_text(SM_Program*)`.
- **JVM and JS are stubs here.** The real JVM and JS emitter implementations (walking IR_t nodes, emitting Jasmin / JS code equivalent to bb_boxes.j / bb_boxes.js) are written in GOAL-SN4-JVM-EMIT and GOAL-SN4-JS-EMIT. Those goals plug into the `emit_ir_block_jvm` / `emit_ir_block_js` symbols defined here as stubs.
- **No C Byrd box functions.** Zero `DESCR_t foo(void *zeta, int entry)` functions.
