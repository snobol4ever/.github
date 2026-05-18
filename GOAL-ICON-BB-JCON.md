# GOAL-ICON-BB-JCON.md — Icon: BB emitters + lower_icn DCG

**Repo:** one4all + corpus + .github
**Prereq:** GOAL-ICON-BB-NATIVE ✅ `7efdf09a`

## Invariants

1. **No AST walking in modes 2/3/4.** If gate fails with `[NO-AST] FOO`, write fresh SM/BB lowering — do not restore AST-walking call.
2. **Zero C Byrd-box functions.** `DESCR_t foo(void *zeta, int entry)` — NONE. Only permitted: `icn_bb_dcg` (infrastructure DCG driver).
3. **Cross-language:** SM↔SM via `g_user_call_hook`; BB↔BB via universal α/β/γ/ω contract. Never invoke language-A SM-bridge handler with language-B BB object.
4. **Four ports hard-wired.** `IR_node_alloc` bakes α=nd, β=nd, γ=NULL, ω=NULL. Zero call sites depend on NULL α/β as sentinel.
5. **Three orthogonal constructs per session max**, separate commits, single gate run at end.

## Session Setup

```
cd /home/claude/one4all && bash scripts/build_scrip.sh
```

## Architecture

```
AST --(lower)--> SM_Program [SM_BB_XXX bridge opcodes]
                 IR_block_t* [pre-built per bridge op]
```

Mode 2 (`--interp`) is the reference path for Icon at 194/265. Target: one `IR_block_t*` per proc in `proc_table[i].ir_body`, driven by `icn_bb_dcg`. Mode 4 (`--compile`) emits wired x86 asm — no `bb_broker`.

## Gates

```
GATE-1  bash scripts/test_smoke_icon.sh                        # PASS=5
GATE-2  bash scripts/test_smoke_unified_broker.sh              # PASS >= 23
GATE-3  bash scripts/test_icon_all_rungs.sh --interp           # PASS=194
```

## Open step

- [x] **DAI-8 C8 — `icn_runtime.c` (interp) dead-fn sweep.** 17 fns deleted, −185 LOC. `881d1a60` 2026-05-18.
- [x] **DAI-8 C10 — `emit_wasm.c` dead-fn sweep.** 22 fns deleted, −175 LOC. `533c17c3` 2026-05-18.
- [ ] **DAI-8 C11+ — Continue dead-code sweep.** Remaining:
  - `snobol4.c` ~25 — excluded from Method 1 (self-referencing runtime); needs Method 7 sub-graph analysis
  - `rt.c` — `chunk_reg_lookup`/`call_native_chunk`/`rt_in_native_chunk` deferred (Method 7 sub-graph)
  - Run `make scrip GC=1 | grep removing` — done when zero output; all gates hold floor.

  **Process per cluster:** Method 1 nominates → Method 6 confirms zero callers + zero address-of → delete → gate. See DAI-8 methodology note below.

  **Done when:** `make scrip GC=1 | grep removing` returns 0; all gates hold floor.

## DAI-8 methodology note

Method 1: compile with `-ffunction-sections -fdata-sections`, link with `--gc-sections --print-gc-sections`, grep `.text.<name>` discards. **Two mandatory filters:**
1. Exclude generated files (`*.lex.c`, `*.tab.c`, `snobol4.c`).
2. **@PLT rescue:** any symbol appearing as `"name@PLT"` in `src/emitter/*.c` is live (called from emitted asm text). Filter regex must be `"NAME(@PLT)?"`.

Method 6: `grep -rn "\bNAME\b" src/ --include="*.c" --include="*.h"` excluding the symbol's own file. Zero hits + zero `&NAME` address-of = safe to delete.

Method 7 (internal-caller chain): if linker-GC-dead public fn F only calls other GC-dead fns, the whole sub-graph is deletable together.

## DAI-8 deletions ledger

| Cluster | Deleted | Commit | Gate delta |
|---------|---------|--------|------------|
| **C1** `emit_bb.c` | 75 fns + 22 dead decls | `a4fe1c21` | mode-2 floor held; mode-3/4 retroactively validated in C2 |
| **C2** `emit_core.c` + `emit_sm.c` byte-emit family | ~198 fns, −877 LOC | `895ab323` | all gates floor; broker 22→23 |
| **C3a** `emit_form.h` + `emit_core.c::ef_greek_port` | 14 fns, −23 LOC | `c3af9e23` | floor held |
| **C3b** `rt.c` 7 dead public fns + 7 rt.h decls | −43 LOC | `a7259b9b` | floor held |
| **C4** `stmt_exec.c` 10 fns + 1 typedef; C-BB violation removed | −248 LOC | `de6e7b77` | floor held |
| **C5** `snobol4_pattern.c` 16 fns + 1 typedef + 9 decls | −197 LOC | `af744aaa` | floor held |
| **C6** `prolog_builtin.c` 15 fns + 14 decls | −75 LOC | `607b6aac` | floor held |
| **C7** `icon_runtime.c` (frontend) 12 fns + 2 globals | −118 LOC | `2b7081c5` | floor held |

| **C8** `icn_runtime.c` (interp) 17 fns + state structs | −185 LOC | `881d1a60` | floor held |
| **C9** `rt.c` `rt_pop_int` | −12 LOC | `ff9ee063` | floor held |
| **C10** `emit_wasm.c` 22 fns (20 bb_* + generator + scalar) | −175 LOC | `533c17c3` | floor held |

## Watermark

```
one4all: 533c17c3     (DAI-8 C10: emit_wasm.c 22 fns −175 LOC)
corpus:  92e103f      (unchanged)
.github: (this commit)
--interp:    194/265  (held)
smoke ×6:    5/0 5/0 5/0 4/0 5/0 7/0  (held)
broker:      23/26    (held)
crosscheck_prolog: 128/0/4SKIP/11ORACLE_MISS  (held)
hello-world: 6/6 PASS-wired  (held)
scrip_all_modes: 2/0
DAI-BOMB fires: 0
```

## Completed steps (summary)

All IJ-* and DAI-1 through DAI-7 steps ✅. IJ-HELLO-1 through IJ-HELLO-5 ✅ (6/6 wired hello-world matrix closed 2026-05-18). DAI-8 clusters C1–C7 ✅. Full step histories available in git log.

**Key architectural facts established:**
- Icon `--interp` (mode 2) = `--ast-run` (mode 1) at 194/265 — parity confirmed, mode-1 flag deleted.
- Icon AST walker (`bb_eval_value`/`bb_exec_stmt`/`icn_bb_build`) fully amputated (DAI-1 through DAI-7).
- Hello-world matrix 6/6 wired: SNOBOL4/Snocone/Rebus always passing; Icon via `SM_BB_PUMP_PROC → call .L<entry_pc>`; Prolog via `rt_pl_once` (no broker); Raku via `SUB_TAG_ID` lower_stmt fix.
- `rt_bb_once_proc` deleted; `rt_bb_pump_proc` never existed. Only `rt_pl_once` + `icn_bb_dcg` remain as bridge shims.
