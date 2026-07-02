# ARCH-SCRIP.md — SCRIP Frontend + Execution Modes

(Pruned 2026-07-01 per Lon: the former 3-mode `sm_lower`→`sm_interp_run`/`sm_jit_run` body, its strikethrough corrections, and the dead-symbol inventory are deleted — recover from git. What follows is the verified current reality; for build/registers/corpus see GOAL-IR-IMMUTABLE-EMIT.md's ORIENTATION SYNOPSIS.)

## Frontend
SCRIP. Produces the shared AST (tree_t/STMT_t). See ARCH-IR.md.

## Execution modes — EXACTLY TWO (modes 1 and 2 DELETED; see GOAL-MODE34-IDENTICAL.md)
| Flag | Mode | Pipeline |
|------|------|----------|
| `--run` | 3 — native x86 BINARY in-process | IR → `src/emitter/emit.cpp` (`emit_drive` + dispatch) → BINARY → jump in |
| `--compile` | 4 — standalone binary via toolchain | IR → `emit.cpp` → x86 TEXT `.s` → `gcc -no-pie` + `libscrip_rt.so` → exec |
An OPTIMIZER stage (`src/optimizer/`, `SCRIP_OPT` env-gated, OFF by default) sits between LOWER and the emitter since 2026-07-01.

## Isolation invariant (current statement)
Neither mode walks the AST or IR at runtime. `emit.cpp` walks the IR graph exactly once, at EMIT TIME, then the IR is never referenced again — the running program is pure emitted x86: zero per-opcode C dispatch, zero `BB_t`-graph traversal. Runtime stubs print `[NO-SM-BB] <opcode>` and set `last_ok=0`. (Check GOAL-PROLOG-BB.md directly for any Prolog-side temporary exception.)

## Shared substrate — symbols verified live (2026-06-30)
`INVOKE_fn`/`APPLY_fn` (builtin dispatch — re-grep location) · `NV_GET_fn`/`NV_SET_fn` (name-value table) · `exec_stmt`/`bb_build` (`src/runtime/core/stmt_exec.c`) · `eval_node` (`src/runtime/runtime_eval.c`) · `coerce.c` (`src/runtime/core/`) · `sm_lower` (vestigial failure-message reference in `src/driver/scrip_sm.c` only). Dead, do not cite: `bb_broker`, `bb_boxes`, `sm_interp_run`, `sm_jit_run`, `SM_sequence_t`, `bb_exec_*`, `g_jit_prog`.

## SNOBOL4 native pattern matching (modes 3 & 4)
The 5-phase `SUBJ ? PAT [= REPL]` model is specified in ARCH-SNOBOL4.md §"Native pattern architecture — modes 3 & 4"; ladder in GOAL-SNOBOL4-BB.md (SBL-PAT-BB). Read before mode-3/4 SNOBOL4 pattern work.
