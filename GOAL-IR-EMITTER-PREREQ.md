# GOAL-IR-EMITTER-PREREQ.md — IR_t Emitter Foundation (prerequisite for JVM + JS)

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ NO AST WALKING IN MODES 2/3/4 — see RULES.md § "NO AST WALKING IN MODES 2, 3, OR 4"         ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║  Sess 2026-05-15g removed all tree_t* dereferences from sm_interp.c (mode 2) and                ║
║  sm_jit_interp.c (mode 3). Stubs print [NO-AST] <opcode> on stderr.                              ║
║                                                                                                  ║
║  If a gate breaks with [NO-AST] FOO — write fresh SM/BB lowering for FOO.                       ║
║  Do NOT restore the AST-walking call.  Do NOT route through proc_table_call or any              ║
║  other back-door that hands a tree_t* to mode-2/3/4 code.                                       ║
║                                                                                                  ║
║  Mode 1 (`--interp` standalone AST interp) is unchanged and remains the reference path.        ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝


╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║  A C Byrd box (C BB) is ANY C function with signature: DESCR_t foo(void *zeta, int entry)      ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                             ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

⛔ **Read before any source file:** ARCH-IR.md then ARCH-SCRIP.md then ARCH-EMITTER.md.

**Repo:** SCRIP + .github
**Prereq for:** GOAL-SN4-JVM-EMIT.md and GOAL-SN4-JS-EMIT.md

---

## Goal statement

Three hard rules — no exceptions:

1. **After parser exits: tree_t is deleted.** Lower may not reference tree_t at all after lower() returns. Enforced by freeing tree_t immediately after lower() completes. Any dangling reference crashes.

2. **After lower exits: IR_block_t is deleted from lower's local scope.** The emitter receives the dcg_table (owned by SM_Program) — not a live IR pointer from lower's heap. Enforced by calling IR_free on lower's locally-produced IR_block_t after registering it in dcg_table. Any dangling reference crashes.

3. **SM opcodes contain no pointers to prior phases.** SM_Instr fields are integers, strings (interned), and floats only. No void*, tree_t*, or IR_block_t* in any SM_Instr operand used as a cross-phase carrier.

**Shared tables (label_table, proc_table, g_pl_pred_table) are built from tree_t before lower runs and are legitimate shared state — they are not references into the tree structure itself.**

**Done when:** tree_t freed after lower(); IR_block_t freed after dcg_table registration; SM_Instr has no cross-phase pointer fields; all three modes (--interp, --run, --compile) pass on beauty.sno.

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
- [x] **IEP-3** — scrip.c wired: --target=jvm/js → emit_ir_block; --target=x86 unchanged. ✅ `35142ba5`
- [x] **IEP-VTABLE** — IR_emit_vtable_t dispatch inside single walk; emit_ir_targets.c. ✅ `92f628b0`
- [x] **IEP-INCLUDE** — src/include/ with 6 stage-boundary headers; forward shims. ✅ `b77d3729`
- [x] **IEP-RENAME** — scrip_ir.h → src/include/IR.h; mass-replace. ✅ `1e7a7f5e`
- [x] **IEP-4** — SM_EXEC_STMT and SM_EXEC_BB: IR_block_t* → dcg_table integer index. ✅ `d9dff43a`
- [x] **IEP-PKG** — ParserOutput struct + parser_output_build(): single place that names the parser→lower contract. ✅ `b4859b69`. Design B (named contract; globals stay in place). Three call sites (sm_preamble, --dump-sm, sync_monitor_run) updated. Groundwork for Design A (move label_table / proc_table / g_pl_pred_table into the struct as fields — ~121 read sites — once IR-CD-5 lands) and for IEP-7 (cannot delete tree_t* after lower returns without first reifying the boundary).

---

## Remaining steps

### IEP-5 — DEFERRED: owned by GOAL-CHUNKS (every_table / SM_PUSH_EXPR)

- [ ] **IEP-5** — ⛔ **Do not implement here. Owned by GOAL-CHUNKS.**

  `SM_BB_EVAL`, `SM_BB_PUMP_EVERY`, and `every_table[]` are active intentional infrastructure introduced by CHUNKS STEP17 (CH-17f). `every_table` holds `tree_t*` — a Rule 3 violation — but CHUNKS owns the migration. Touching it here conflicts with active CHUNKS work.

  `SM_PUSH_EXPR` elimination is the stated goal of `GOAL-CHUNKS.md` ("Done when: SM_PUSH_EXPR opcode is deleted"). CHUNKS migrates it via `SM_PUSH_CHUNK` / `SM_BB_PUMP_AST`.

  This step completes when GOAL-CHUNKS closes. At that point: `every_table` gone, `SM_PUSH_EXPR` gone, Rule 3 satisfied by construction.

### IEP-6 — DEFERRED: owned by GOAL-CHUNKS

- [ ] **IEP-6** — ⛔ **Do not implement here. See IEP-5.**

### IEP-7 — Delete tree_t immediately after lower() returns (Rule 1 enforcement)

- [ ] **IEP-7** — In `scrip_sm.c`, after `SM_Program *sm = lower(ast_prog)` succeeds, call `code_free(code)` and null `ast_prog`. In the `--dump-sm` path in `scrip.c` (calls `lower()` directly): same. Mode 1 (`--interp`) is exempt — tree_t IS the program there; no lower phase runs.

  `code_free` exists in `ast_clone.c` but is currently never called. Wire it at both SM-path exit points.

  ⛔ **IEP-7 cannot run until GOAL-CHUNKS completes.** Every surviving `every_table` and `SM_PUSH_EXPR` site holds a `tree_t*` — freeing tree_t before CHUNKS finishes crashes immediately. That crash is the proof CHUNKS is done.

  **Gate:** `scrip --interp beauty.sno` and `scrip --run beauty.sno` pass with tree_t freed after lower. Any dangling reference crashes immediately.

### IEP-8 — sm_prog_free frees dcg_table entries (Rule 2 enforcement)

- [ ] **IEP-8** — In `sm_prog_free()`: call `IR_free(dcg_table[i])` for each entry before freeing `dcg_table`. Ownership: `sm_prog_dcg_add` transfers ownership to `SM_Program`; lower must not free after registration. Modes 2/3 keep dcg_table alive for the interpreter lifetime; mode 4 emitter walks dcg_table then sm_prog_free cleans up.

  **Gate:** valgrind on `scrip --interp beauty.sno` shows zero IR_block_t leaks.

### IEP-9 — Final audit: all three rules verified by construction

- [ ] **IEP-9** — After IEP-7 and IEP-8 (and GOAL-CHUNKS complete):
  1. `grep "sm_emit_ptr" src/lower/lower.c` — zero hits.
  2. `grep "every_table" src/` — zero hits (CHUNKS done).
  3. `grep "SM_PUSH_EXPR" src/include/sm_prog.h` — zero hits (CHUNKS done).
  4. `scrip --interp beauty.sno` and `scrip --run beauty.sno` pass.
  5. `scrip --compile beauty.sno` byte-identical to pre-IEP-4 baseline.

---

## Remaining tree_t* dependencies NOT covered by CHUNKS

Two live `tree_t*` references survive in shared tables after lower runs. CHUNKS does not touch these. They independently block IEP-7 (delete tree_t after lower):

| Table | Field | Set by | Used by | Problem |
|-------|-------|--------|---------|---------|
| `proc_table[i].proc` | `tree_t*` | `polyglot_init` walks AST | `icn_runtime.c` — proc body re-execution at runtime | live tree_t* past lower boundary |
| `g_pl_pred_table` entries | `tree_t*` | `polyglot_init` inserts AST subtrees | `pl_runtime.c` — Prolog clause eval at runtime | live tree_t* past lower boundary |

Fix: lower must fully lower Icon proc bodies and Prolog clause trees to `IR_block_t` entries in `dcg_table`, replacing `tree_t*` in both tables with integer indices. New GOAL needed — larger than IEP scope.

---

## What next GOALs plug in here

**GOAL-SN4-JVM-EMIT:** fill `g_emit_vtable_jvm` in `src/emitter/emit_jvm.c`.
**GOAL-SN4-JS-EMIT:** fill `g_emit_vtable_js` in `src/emitter/emit_js.c`.
**Runtime state in SM_Instr:** `icn_to_state_t*` per-call allocation — separate GOAL.
**proc_table + pl_pred_table:** new GOAL — lower Icon proc bodies and Prolog clauses fully into dcg_table; replace tree_t* in both tables with integer indices. Prerequisite for IEP-7.

---

## State

```
watermark: IEP-PKG (IEP-5/6 deferred to CHUNKS; IEP-7/8/9 blocked on CHUNKS + proc_table/pl_pred_table GOAL)
head: b4859b69
session: 2026-05-20 (Claude Opus 4.7)
```

---

## Key invariants

- **One entry point.** `emit_ir_block` is the sole emitter entry for all 6 backends × all 6 frontends.
- **One walk.** `ir_walk` traverses the DCG once; the vtable selects per-node template functions.
- **Phases are isolated by deletion.** tree_t deleted after lower(). IR_block_t owned by dcg_table, freed by sm_prog_free(). No silent dangling references.
- **src/include/ is the canonical header location.**
- **No C Byrd box functions.**
