# GOAL-HEADQUARTERS.md — one4all Maintenance HQ

**Formerly:** GOAL-HEADQUARTERS.md

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
| **C11** `lower_icn.c` 9 fns (7 IR constructors + expr_top + fail_box) | −136 LOC | `04679f20` | floor held |
| **C12** `bb_boxes.c`+`emit_sm.c`+`scan_builtins.c` 20 fns | −157 LOC | `5e854341` | floor held |
| **C13** `prolog_*`+`raku_re.c` 18 fns | −234 LOC | `947ecd7a` | floor held |
| **C14** `icon_runtime`+`sm_interp`+`sm_jit_interp`+`stmt_exec` 20 fns | −168 LOC | `50e025f6` | floor held |
| **C15** `bb_pool`+`lower`+`polyglot`+`snocone_lex` 10 fns | −75 LOC | `06ea32b0` | floor held |
| **C16** `sm_interp.c` `every_table_lookup` (binary-safe) | −324 bytes | `f82a34c9` | floor held |

## Watermark

```
one4all: f82a34c9     (DAI-8 C16: sm_interp every_table_lookup binary-safe −324 bytes)
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

---

## IR Rename (moved from GOAL-PARSER-PURE-SYNTAX-TREE Stage 2, 2026-05-18)

### Why

Two confusingly-named prefixes exist today. `IR_t` and `IR_block_t` are the Byrd-box DCG nodes; `SM_Instr` and `SM_Program` are the stack-machine instruction stream. Both are IR. Neither name says what it is. The rename makes them symmetric and self-describing.

### Legacy → renamed map

| Today | After rename |
|-------|--------------|
| `SM_*` opcode names (`SM_HALT`, `SM_JUMP`, `SM_PUSH_LIT_S`, …) | **`IR_SM_*`** |
| `sm_opcode_t` | `IR_sm_op_t` |
| `sm_operand_t` | `IR_sm_arg_t` |
| `SM_Instr` | `IR_sm_t` |
| `SM_Program` | `IR_sm_program_t` |
| `SmExpression_t` | `IR_sm_expr_t` |
| `sm_*` API (`sm_emit*`, `sm_label*`, `sm_patch_jump`, `sm_prog_new`, …) | `ir_sm_*` |
| `g_current_sm_prog` | `g_current_ir_sm_prog` |
| `IR_*` enum (`IR_LIT_I`, `IR_PAT_*`, `IR_PL_*`, `IR_ICN_*`, …) | **`IR_BB_*`** |
| `IR_e` | `IR_bb_op_t` |
| `IR_t` | `IR_bb_t` |
| `IR_block_t` | `IR_bb_block_t` |
| `IR_alloc / IR_node_alloc / IR_reset / IR_free` | `IR_bb_alloc / IR_bb_node_alloc / IR_bb_reset / IR_bb_free` |
| `IR_LANG_*` constants | stay as-is |

### Must NOT rename

- `BB_*` in `bb_box.h`, `bb_broker.h`, `bb_pool.h` — runtime Byrd-box engine
- `SM_INTERP_*`, `SM_CALL_STACK_MAX`, `SM_GEN_LOCAL_MAX`, `SM_MAX_OPERANDS`, `SM_INTERP_SUSPENDED` — runtime/interpreter constants (exception: `SM_MAX_OPERANDS` → `IR_SM_MAX_OPERANDS`)
- Header guards (`SM_INTERP_H`, `BB_BOX_H`, etc.)
- Emitter-internal helper names (references to IR opcodes rename automatically via sed)

### Rename step ladder

- [ ] **IR-RN-0** — **Bulk rename** (single rung). Mechanical sed. No structural change. Gates must pass before commit.
    - 0.1 — `scripts/audit_ir_names.sh`: print every renamed identifier, every preserved name, every ambiguous name needing manual review.
    - 0.2 — `scripts/rename_ir_to_ir_bb.sh` and `scripts/rename_sm_to_ir_sm.sh`: explicit per-pattern sed rules, never blind global replace.
    - 0.3 — Apply in two ordered passes: `IR_*`→`IR_BB_*` first, then `SM_*`→`IR_SM_*` (avoids collision).
    - 0.4 — Split `sm_prog.h` and `IR.h` into `IR_sm.h` / `IR_bb.h`; old headers become one-line `#include` shims, deleted at end of rung.
    - 0.5 — Gates green: build, all smoke tests, beauty self-host byte-identical.
- [ ] **IR-RN-1** — Audit `lower.c` post-rename; confirm all lowering call sites use new names correctly.
- [ ] **IR-RN-2** — Audit emitters (`emit_bb.c`, `emit_sm.c`, `emit_core.c`, `emit_wasm.c`, `emit_net.c`) — all IR opcode references renamed; no old-name leakage.
- [ ] **IR-RN-3** — Audit runtime (`sm_interp.c`, `sm_jit_interp.c`, `ir_exec.c`) — new names throughout.
- [ ] **IR-RN-4** — Update all arch docs (`ARCH-IR.md`, `ARCH-ICON.md`, `ARCH-SCRIP.md`, `GOAL-HEADQUARTERS.md`) to use new names.
- [ ] **IR-RN-5** — Cross-language gate run: all six frontends + broker + smoke + beauty. Close rung.

---

## Emitter Consolidation (EC) — move JVM/JS/.NET into per-instruction template functions

### Problem

`emit_jvm.c`, `emit_js.c`, `emit_net.c` are parallel silos. Each reimplements its own
scalar/generator dispatch loop and its own per-node functions. The SM instruction and BB box
logic for each target is invisible to the others. Adding a new SM opcode or BB box kind
requires touching N files.

### Target architecture

One function per SM instruction and one function per BB box kind, in `emit_templates.h` /
`emit_core.c`. Each function dispatches on `bb_emit_mode` internally:

```c
void emit_sm_halt(void) {
    switch (bb_emit_mode) {
        case EMIT_TEXT:          /* x86 GAS text — existing */
        case EMIT_BINARY_WIRED:  /* x86 binary — existing */
        case EMIT_JVM:           /* JVM Jasmin — moved from emit_jvm.c */
        case EMIT_JS:            /* JavaScript — moved from emit_js.c */
        case EMIT_NET:           /* MSIL .NET — moved from emit_net.c */
        case EMIT_WASM:          /* WASM — moved from emit_wasm.c */
    }
}
```

The vtable (`IR_emit_vtable_t` / `emit_ir_block`) and the three silo files are deleted.
`emit_ir.c` / `emit_ir.h` collapse — the walk infrastructure moves into `emit_core.c` and
is invoked with the mode already set via `emit_mode_set()`.

### Step ladder

- [ ] **EC-0** — Add `EMIT_JVM`, `EMIT_JS`, `EMIT_NET` to `bb_emit_mode_t` in `emit_core.h`. Add `IS_JVM` / `IS_JS` / `IS_NET` macros. No functional change. Gates green.
- [ ] **EC-1** — Inventory pass. For every `emit_jvm_bb_*` / `emit_js_bb_*` / `emit_net_bb_*` function, identify the corresponding template function in `emit_templates.h`. Produce mapping table (jvm/js/net function → template function). Document any BB kinds present in silos but absent from templates (gap list).
- [ ] **EC-2** — For each BB box kind, add the JVM / JS / .NET arms to the corresponding template function in `emit_core.c`. One BB kind per sub-commit. Order: `IR_PAT_LIT` first (simplest), then remaining SNOBOL4 pattern leaves, then composers, then Icon, then Prolog.
- [ ] **EC-3** — For each SM instruction kind, add the JVM / JS / .NET arms to the corresponding template function in `emit_core.c`. One SM family per sub-commit. Order: push/pop literals → variables → arithmetic → control flow → calls → pattern bridge → return family.
- [ ] **EC-4** — Move `emit_jvm_prologue` / `emit_jvm_epilogue` (and JS/.NET equivalents) into `emit_core.c` as mode arms of `emit_prologue()` / `emit_epilogue()`. Delete the vtable struct and `emit_ir_block()` dispatch.
- [ ] **EC-5** — Delete `emit_jvm.c`, `emit_js.c`, `emit_net.c`. Move IR walk infrastructure from `emit_ir.c` into `emit_core.c`. Delete `emit_ir.c` / `emit_ir.h`. Delete `IR_emit_vtable_t`. Gates green.
- [ ] **EC-6** — Audit `emit_wasm.c`: same pattern — move its per-node functions into template arms. Delete `emit_wasm.c` after move. (WASM already partially cleaned by DAI-8 C10.)
- [ ] **EC-7** — Gate run: all six frontends, broker, smoke, beauty. Confirm no regression. Update `ARCH-IR.md` to document the unified template model. Close EC rung.

### Invariant

After EC-5: every SM instruction and every BB box kind has exactly one function in
`emit_core.c`. Adding a new backend = adding one `case EMIT_NEW_TARGET:` arm per
function. Adding a new SM opcode = adding one function with arms for all backends.
No per-target silo files. No vtable dispatch.
