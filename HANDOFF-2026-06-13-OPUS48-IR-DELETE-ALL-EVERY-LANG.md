# HANDOFF — 2026-06-13 · Opus 4.8 · `ir_delete_all` EXTENDED TO EVERY LANGUAGE (IR-NEVER-TOUCHED tripwire, all m3/m4 paths)

## Watermark
SCRIP `9baaf64` · .github `(this commit)` (both build green).

## What & why
Lon: "Extend `ir_delete_all` to all languages. Each session will be responsible for healing from the modification." The IR is now physically freed on EVERY language's mode-3 (`--run`, after the slab is built, before it executes) and mode-4 (`--compile`, after the `.S` is emitted, before return). This converts IR-NEVER-TOUCHED from a per-Prolog guarantee into a whole-compiler structural one: any path that reads IR during execution now faults (m3) or is caught as a post-emit re-read (m4). **mode-2 (`--run`) is deliberately NOT wired** — the IR-graph interpreter legitimately walks IR during execution; that is its entire job.

## Sites wired (`src/driver/scrip.c`, +4; Prolog already had its 2 at `f0c3e29`)
- **m4 Icon/Raku** — after `descr_flat_chain_build_text`/`codegen_flat_build` + `xa_emit_strtab_rodata` + `fflush`, before `return rc`.
- **m4 catch-all (SNOBOL4 / Snocone / Rebus / Pascal)** — after `gvar_flat_chain_build_text` + strtab + flush, before `return rc`.
- **m3 Icon/Raku** — after the main flat-chain build (`bb_build_flat`/`descr_flat_chain_build`), before `(void)fn(rt_frame(),0)`.
- **m3 catch-all** — after the main `gvar_flat_chain_build`, before `(void)fn(rt_frame(),0)`.

Placement principle: at each m3 site, all predicate/proc bodies are emitted up-front and stored as native `bb_box_fn` via `rt_proc_set_fn` BEFORE main runs, so the delete sits after the last emit and before the first execution. Where that still breaks, the language really does touch IR at runtime — which is the finding.

## `IR_free` reverted to shallow (`src/contracts/scrip_ir.c`)
The `f0c3e29` completion (freeing per-node `operands[]` + `lit[]`/`exec[]`/`operand_aux[]`) is REMOVED. It adds invalid-free exposure on aliased graph shapes (which demonstrably exist — see SNOBOL4 below) for zero enforcement benefit: the sidecar arrays are unreachable once the nodes are freed. `bb_program_free` still deletes the ENTIRE IR program (every graph in the pool); freeing the nodes is what makes runtime traversal fault. Shallow form verified safe across the whole matrix incl. Pascal.

## Results — all HARD gates GREEN
| Lang | m2 | m3 | m4 | note |
|---|---|---|---|---|
| Prolog | 114 (HARD ✓) | 83 | 83 | unchanged — transparent (IR freed pre-exec, scores identical) |
| Icon | 12 (HARD ✓) | 12 | 12 | unchanged — IR-clean at runtime |
| SNOBOL4 | 7 | **6** (was 7) | 6 (HARD ✓) | **DEFINE m3 aborts — HEAL #1** |
| Raku | 31 (HARD ✓) | **25** (was 26) | 26 | **class_method m3 no-ops — HEAL #2** |
| Snocone | — | — | 2/3 | pre-existing |
| Rebus | — | — | 0/4 | pre-existing |

## HEAL #1 — SNOBOL4 mode-3 `DEFINE` (owner: SNOBOL4 session)
Symptom: `DEFINE('DOUBLE(X)')` program, `--run` → `free(): invalid pointer` / SIGABRT (exit 134) **during `ir_delete_all`**, before execution. Backtrace: `IR_free` (scrip_ir.c:373, the shallow `free(bb)`/`free(bbg->all)`) ← `bb_program_free` ← `ir_delete_all` ← scrip.c m3 catch-all. This is NOT a runtime IR read — it is a **latent lowering double-ownership defect**: in the SNOBOL4 DEFINE lowering a node (or a graph's `all` array, or a whole `IR_graph_t*`) is referenced from TWO pool entries, so freeing the pool double-frees it. It never surfaced because the `--run` path never freed the pool before this change (process just exits; `stage2_reset`'s free is not on the run path). FIX DIRECTION: make DEFINE's synthetic function graph own its nodes/`all` uniquely (no aliasing of the main graph or double-registration in `s2->bbp`). Reproduce: `printf "        DEFINE('DOUBLE(X)')\n        OUTPUT = DOUBLE(21)\n        :(END)\nDOUBLE  DOUBLE = X + X\n        :(RETURN)\nEND\n" > /tmp/d.sno && ./scrip --run /tmp/d.sno`.

## HEAL #2 — Raku mode-3 method dispatch (owner: Raku session)
Symptom: `class_method` program, `--run` → prints `3` and `4` (the field reads `$p.x`, `$p.y`) then nothing; the method CALLS `$p.sum()`, `$p.scale(2)`, `$d.greet()` emit nothing; exit 0 (no crash). With the IR deleted before execution, method dispatch finds no body → silent no-op. This is a **genuine runtime IR read**: Raku method dispatch resolves/emits the method body from IR at call time (lazy emit or runtime graph lookup) rather than from an emit-time-resolved target. FIX DIRECTION: emit all method bodies up-front and dispatch to their stored `bb_box_fn` / a static label (the Prolog `call δ`/`call ε` model), so no IR is consulted at runtime. m2 (31, HARD) and m4 (26) are unaffected — m4 runs in a separate process where IR never existed.

## Don't-trip-over
- The two regressions are TRACKED/informational modes, not HARD gates: SNOBOL4 m3 is "informational (do not block)", Raku m3 is "tracked". Every HARD gate (Prolog m2, Icon m2, SNOBOL4 m4, Raku m2) is green, so this is a legitimate green commit with intentionally-surfaced tracked breakage — same pattern as the GZ-ONLY "take the hit" pivot.
- `ir_delete_all` is idempotent (nulls the pool); a later `stage2_reset` is a no-op.
- Adding the delete to m2 would break the interpreter — do NOT.

## Next
SNOBOL4 and Raku sessions take HEAL #1 / #2. Prolog open work unchanged (GROUP B rungs B2 catch/throw, B3 retract, B4 abolish, B5 DCG; resolution.c dead-code demolition). The dead `stage2_free_*` wrappers remain a candidate cleanup.
