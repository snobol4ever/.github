# HANDOFF — 2026-06-13 · Opus 4.8 · Prolog BB — `ir_delete_all`: physically delete the IR before m3 run / after m4 emit

## Watermark
SCRIP `f0c3e29` · .github `(this commit)` (both build green).
**m2 114/115 · m3 83/115 · m4 83/115.** Ratchet floors UNCHANGED (m3 83 / m4 83). No score movement — this is a structural-enforcement / code-hygiene session, not a feature session.

## Gates
GATE-1 5/5/5 ✓ (HARD m2 gate intact). GATE-3 m2=114, m3=83, m4=83.
Cross-language (shared `scrip_ir.c`/`stage2.h`/`sm_prog.c` touched — `IR_free` runs at teardown for every frontend): Icon m2 12 / m3 12 / m4 12 ✓ · Raku m2 31 / m3 26 / m4 26 (5 EXCISED) ✓ · SNOBOL4 m2 7 / m3 7 / m4 6 (the 1 m4 `define` fail is PRE-EXISTING — confirmed against a clean stash baseline, NOT caused by this change).

---

## Lon's directive
"Add a function which DELETES the entire IR before running in mode 3 and after emitting in mode 4."

Context: this makes the long-standing IR-NEVER-TOUCHED rule (no IR access during m3/m4 execution) **structurally enforced** rather than discipline-only. Emit reads the IR ONCE to produce the m3 image / m4 `.S`; immediately after that read the IR is physically freed, so the running program literally cannot reach it.

## What was done (SCRIP `f0c3e29`, +13 / −1 across 4 files)

### 1 · Completed `IR_free` (`src/contracts/scrip_ir.c`)
`IR_free` was leaking most of every graph — it freed each node and `bbg->all`, but NOT each node's `operands[]`, nor the parallel `lit[]`/`exec[]` sidecar arrays, nor `operand_aux[]`. "Delete the entire IR" requires deleting all of it. Now frees, per graph:
- each node's `free(bb->operands)` then `free(bb)`
- `for i in operand_aux_n: free(operand_aux[i].operands)` then `free(operand_aux)`
- `free(exec)`, `free(lit)`, `free(all)`, `free(bbg)`

This is a **pure leak-plug**: those arrays are allocated only by `IR_alloc` / `IR_node_alloc` / `ir_operand_push` / `bb_operand_aux_set` and freed NOWHERE else (the sole other free is `operand_aux[slot].operands` on realloc inside `bb_operand_aux_set`), so there is no double-free risk for any language. NOT freed (deliberately): the `lit[i].sval` strings (often interned/shared atom names — freeing risks UAF in the atom table) and the `bb_*_state_t` sidecar blobs hung off `lit[i].ival` (per-op type-dependent; they become unreachable once nodes are freed, fine for our purpose).

### 2 · New `ir_delete_all(stage2_t *s2)` (`src/machine/sm_prog.c`, decl in `src/contracts/stage2.h`)
```c
void ir_delete_all(stage2_t *s2) { if (s2) bb_program_free(&s2->bbp); }
```
Deletes the ENTIRE IR program — the whole `s2->bbp` pool (every `IR_graph_t`, not just `main`). `bb_program_free` already sweeps the pool calling the (now-complete) `IR_free`, nulls each table entry, frees the table, and zeroes count/cap. Idempotent: a second call (e.g. `stage2_reset` at teardown, since `s2 == &g_stage2`) is a harmless no-op on the nulled pool.

### 3 · Wired at BOTH Prolog dispatches (`src/driver/scrip.c`)
- **m3 `--run`** (~line 2740): `if (gzfn) { ir_delete_all(s2); (void)gzfn(rt_frame(), 0); goto run_done; }` — IR deleted AFTER `pl_gz_build` finishes emitting native code into the RX slab, BEFORE the slab executes. This is the load-bearing site: the slab runs in THIS process, so the delete is a live test that nothing the slab (or its runtime helpers) calls reaches back into IR.
- **m4 `--compile`** (~line 2433): `ir_delete_all(s2);` inserted after `pl_gz_codegen` + `xa_emit_strtab_rodata` + `fflush(stdout)`, before `return rc` — emit is provably the last reader.

## Why deleting the IR before execution is safe (and why the unchanged scores PROVE it)
`bb_cell_call` (the GZ predicate-call template) emits `call δ` / `call ε`, where δ/ε are the callee's α/β **labels**, resolved at EMIT time into static targets in the generated code. There is no runtime IR lookup anywhere on the GZ path — predicate dispatch, unify, trail, cut all run on `Term*` cells + runtime helpers. So freeing the IR cannot break a running program. The empirical proof: GATE-1 5/5/5 (incl. `recursion`, which exercises `call δ`/`call ε`) and GATE-3 m2 114 / m3 83 / m4 83 are **byte-identical to the pre-change baseline** with the IR freed before execution. If any admitted program had secretly read IR at runtime, it would now fault — none do.

## Permanent benefit
This is now a standing tripwire: should a future change reintroduce an IR-at-runtime read on the m3/m4 path, it will SEGFAULT on freed memory at the moment of access instead of silently reading a stale graph and producing subtly-wrong results. The rule enforces itself.

## Completion proof
```
make scrip + make libscrip_rt → rc=0
GATE-1 5/5/5 · GATE-3 m2 114 / m3 83 / m4 83 (== baseline, IR freed pre-exec)
Icon 12/12/12 · Raku 31/26/26 · SNOBOL4 7/7/6 (1 m4 define pre-existing)
git diff --stat: 4 files, +13 −1
```

## Next session
Open work unchanged from prior handoffs: GROUP B rungs (B2 catch/throw, B3 retract, B4 abolish, B5 DCG) and the remaining dead-code demolition of `resolution.c`'s control engine + `resolve_bb_env_*`. This session added no debt and removed standing leak debt (`IR_free` was incomplete).

Two small OPEN items for Lon's call (deferred this session, not directed):
1. **Dead wrappers.** `stage2_free_sm_bb` / `stage2_free_bb_after_emit` (declared in `scrip_sm.h`, defined in `scrip_sm.c`) are never called and are now superseded by `ir_delete_all`. Candidate for deletion in a cleanup pass (would also drop their decls).
2. **Scope of `ir_delete_all`.** Currently fired only on the Prolog m3/m4 arms (the active goal). The same structural enforcement could be extended to the SNOBOL4 / Icon / Raku / etc. m3/m4 paths — but each needs the same "is any IR read at runtime?" audit first (Icon/SNOBOL4 may still have residual IR-walkers; do not blind-wire). Left Prolog-scoped pending that audit.
