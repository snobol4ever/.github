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

**DAI-8 C18 AUDIT COMPLETE — no safe deletions.** All remaining GC-dead symbols are anchored live:
- `static_get`/`static_set` in `icn_runtime.c`: called from `sm_call_proc` (live via `icn_runtime.h`). Method 7 chain — internal callers are live.
- `rt_set_last_ok` in `rt.c`: called from `rt_match_blob` (PLT-live in emit_sm.c). Method 7 chain — anchored.
- `emit_core.c` 98 symbols: all have real call sites in `emit_bb.c`/`emit_sm.c`. GC-sections false positive caused by `emit_bb.c` compile failure in the audit build.

**DAI-8 sweep is complete.** All auditable dead code removed in C1–C17. Remaining dead-looking symbols are live.

**EC-BB-UNIFY-2 partial ✅ (compile-time path, one4all `50217d15`, 2026-05-19, Opus 4.7):** emit_walk_phase2 rewritten to build IR_t* directly into a caller-supplied IR_block_t arena (no more compile-time pat_* PATND_t constructors). `emit_flat_eligible`/`emit_flat_invariant` converted to `(const IR_t *)`. `pattern_window_t` holds `IR_t *root + IR_block_t *cfg`. `emit_pattern_blobs` passes IR_t* through directly — fixes the type-punned UB introduced by 1fc21e2d (PATND_t* cast through DESCR_t.p into an IR_t*-shaped reader). Obsolete tests sm_phase2_sim_test.c and bb_flat_text_test.c retired (XKIND_t-based assertions invalid post-conversion); Makefile targets removed. Mode-4 (`--compile`) pattern emission now produces correct `pat_N_α/β/γ/ω` blobs with the right BOX banner and literal references. Net −140 LOC. Gates green at floor: GATE-1 5/0, GATE-2 23/26, GATE-3 194/36/35.

**EC-3-prep ✅ (one4all `d9295c19`, 2026-05-19, Opus 4.7):** Installs `emit_mode_set(EMIT_JVM/JS/NET, out)` at the top of `emit_jvm_program` / `emit_js_program` / `emit_net_program`, with save/restore around each. Pure infrastructure — silos hardcode per-target output and don't currently read `bb_emit_mode`, so the change is byte-identical (verified via md5sum across .j and .js output). Unblocks future EC-3 sub-commits that will move SM instruction families into `SM_templates/` files with internal `IS_JVM/IS_JS/IS_NET` dispatch. Gates floor across all 12 measured paths. +26 LOC.

**EC-3a ✅ (one4all `519ed55f` → rebased `774c1e0e`, 2026-05-19, Sonnet 4.6):** Create `SM_templates/` + `sm_template_common.h`. Promote `jvm_push_int2` + `jvm_emit_ldc_string` from static→`emit_core.c`. `sm_push_pop_lits.c`: 7 unified functions (`sm_push_lit_i/s/f`, `sm_push_null`, `sm_void_pop`, `sm_push_var`, `sm_store_var`) with `IS_JVM/IS_JS/IS_NET` dispatch. Replace 3×7=21 parallel case arms with one-line calls. +166/−159 LOC.

**EC-3b ✅ (one4all `774c1e0e`, 2026-05-19, Sonnet 4.6):** `sm_arith.c`: 9 unified arithmetic functions (`sm_concat`, `sm_neg`, `sm_coerce_num`, `sm_exp`, `sm_add/sub/mul/div/mod`) with `IS_JVM/IS_JS/IS_NET` dispatch. Replace 3×9=27 parallel case arms. +65 LOC. Gates held: GATE-1 5/0, GATE-2 23/26, GATE-3 194/36.

**EC-3c ✅ (one4all `53f2ef4f`, 2026-05-19, Sonnet 4.6):** `sm_compare.c`: 3 unified functions (`sm_stno`, `sm_acomp`, `sm_lcomp`). 9 silo arms → one-liners. +37/−24 LOC. Gates: 5/0·23/26·194/36.

**EC-3d ✅ (one4all `f478df98`, 2026-05-19, Sonnet 4.6):** `sm_ctx.h` + `sm_control.c`: 4 fns (sm_jump/s/f, sm_halt) via sm_ctx_t; 12 silo arms → one-liners. +125/-89 LOC.

**EC-3e ✅ (one4all `87c1be66`, 2026-05-19, Sonnet 4.6):** sm_return/freturn/nreturn (9 variants → 3 fns). Extend sm_ctx_t with pc_to_fn[]/fn_names[]/fn_count. 27 silo arms → 3 grouped one-liners. +123/-161 LOC.

**EC-3f ✅ (one4all `5cb3b909`, 2026-05-19, Sonnet 4.6):** sm_pat.c: 30 unified fns — full SM_PAT_* + SM_EXEC_STMT. 58 silo arms → one-liners. +260/-232 LOC. NET PAT is stub (no-op for IS_NET).

**EC-4 ✅ COMPLETE 2026-05-19 (Sonnet 4.6, one4all `8890d685`).** emit_prologue/emit_epilogue unified in emit_core.c; IS_JVM/IS_JS/IS_NET dispatch; emit_ir_block calls unified fns. Static silo fns retained for EC-5 vtable. +71/-13 LOC.

**EC-5 ✅ COMPLETE 2026-05-19 (Sonnet 4.6, one4all `e1c8a4ac`).** emit_jvm.c/emit_js.c/emit_net.c/emit_ir.c/emit_ir_targets.c/emit_ir.h(shim) deleted. IR walk (ir_node_id/ir_is_generator/ir_walk) + three SM-walk loops (emit_jvm_from_sm/emit_js_from_sm/emit_net_from_sm) + helpers (jvm_sanitize_name/net_parse_define_proto) moved to emit_core.c. Unified emit_program(ast_prog,out,mode) replaces 3 per-target entry points. IR_emit_vtable_t deleted. src/include/emit_ir.h stripped. Net −2077 LOC. Gates floor: 5/0·23/26·194/36.

**NEXT: EC-UNI-2** — Add `IS_X86_TEXT` arms to `sm_arith.c` (9 fns), `sm_compare.c` (3 fns), `sm_control.c` (4 fns), `sm_pat.c` (30 fns), and the sm_return family. Same pattern as EC-UNI-1 — un-static the x86 dispatcher in `emit_sm.c`, declare in `emit_sm.h`, call from `IS_X86_TEXT` arm.

**Recent progress:**
- EC-UNI-0 (this session, one4all `f29c95e9`): scaffold (emit_sm_dispatch returning −1; enum stubs; macros)
- EC-UNI-1 (this session, one4all `e2491770`): `sm_push_pop_lits.c` 7 fns now carry `IS_X86_TEXT` arms


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
| **C17** `snobol4_stmt_rt.c` 43 dead fns (entire file) | −447 LOC | `d48681fb` | floor held |

## Watermark

```
one4all: e2491770     (EC-UNI-1: IS_X86_TEXT arms in sm_push_pop_lits.c — un-static 7 dispatchers in emit_sm.c, template arms call them directly; byte-identity by construction)
corpus:  92e103f      (unchanged)
.github: (this commit)
--interp:    194/265  (held)
smoke ×6:    5/0 5/0 5/0 4/0 5/0 7/0  (held)
broker:      23/26    (held)
snobol4_jit: 184/77 interp · 186/75 run (held = baseline)
snobol4_jvm: 7/6      (held)
snobol4_js:  4/2      (held)
snobol4_net: 0/9      (held — ilasm not installed)
snobol4_wasm: SKIP    (held — wat2wasm not installed)
snocone:     2/3      (held)
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

- [x] **EC-0** ✅ `emit_core.h`: `EMIT_JVM=5`, `EMIT_JS=6`, `EMIT_NET=7` added; `IS_JVM`/`IS_JS`/`IS_NET` macros. `6ad870bf` 2026-05-18.
- [x] **EC-1** ✅ Inventory complete. BB kinds in silos: 18 JVM, 17 JS, 18 NET. All 18 SNOBOL4 pattern kinds present in templates. GAP: `assign_imm`/`assign_cond` (JS only, BB-only path, no x86 template). Integration point: `emit_*_generator` dispatch switch in each silo → replace with unified `emit_bb_node(IR_t*, FILE*)` in `emit_core.c` with `IS_JVM`/`IS_JS`/`IS_NET` mode dispatch per `IR_PAT_*` case. `6ad870bf` 2026-05-18.
- [x] **EC-2** ✅ — All 18 BB kinds migrated to `emit_bb_node` in `emit_core.c`. Sub-commits: LIT `12e4ab86`, ANY/NOTANY/SPAN/BREAK `8b8af8cc`, ARB/ARBNO/CAT `3eaf9e9b`, ALT/LEN/POS/TAB/REM `7ebd7fa8`, FENCE/ABORT/ASSIGN_IMM/ASSIGN_COND `0e523e74`. 2026-05-19 (Sonnet 4.6).
- [x] **EC-2b** ✅ COMPLETE (commit eea3f916) — Collapse each BB kind's three per-backend helpers into one function per kind with internal mode dispatch. Today EC-2 produced `ec_bb_fence_jvm` + `ec_bb_fence_js` + `ec_bb_fence_net` (×18 kinds = 54 functions) called from `emit_bb_node`. Target: one `ec_bb_fence(IR_t*, FILE*)` per kind, dispatching on `IS_JVM`/`IS_JS`/`IS_NET` internally. `emit_bb_node` switch arms become single calls. One BB kind per sub-commit. All 18 kinds done = rung closed.
- [x] **EC-2c** ✅ COMPLETE (commit eea3f916) — Extract each bb_<kind> function into BB_templates/bb_<kind>.c (one file per box). Strip ec_ prefix from all BB and helper symbols (ec_bb_lit → bb_lit, ec_jvm_class_hdr → jvm_class_hdr, etc.). SM_templates/ directory created, empty, ready for SM opcode groups. emit_core.c: 2287 → 1360 lines. Gates: 5/0 · 23/26 · 194/36.
- [ ] **EC-3** — For each SM instruction kind, add the JVM / JS / .NET arms to the corresponding template function in `emit_core.c`. One SM family per sub-commit. Order: push/pop literals → variables → arithmetic → control flow → calls → pattern bridge → return family.
- [x] **EC-4** ✅ (one4all `8890d685`, 2026-05-19, Sonnet 4.6) — Move `emit_jvm_prologue` / `emit_jvm_epilogue` (and JS/.NET equivalents) into `emit_core.c` as mode arms of `emit_prologue()` / `emit_epilogue()`. Delete the vtable struct and `emit_ir_block()` dispatch.
- [x] **EC-5** ✅ (one4all `e1c8a4ac`, 2026-05-19, Sonnet 4.6) — Delete `emit_jvm.c`, `emit_js.c`, `emit_net.c`, `emit_ir.c`, `emit_ir_targets.c`, `emit_ir.h` shim. Move IR walk (`ir_node_id`/`ir_is_generator`/`ir_walk`) + three SM-walk loops (`emit_jvm_from_sm`, `emit_js_from_sm`, `emit_net_from_sm`) + helpers (`jvm_sanitize_name`, `net_parse_define_proto`) into `emit_core.c`. Unified `emit_program(ast_prog, out, mode)` replaces three per-target entry points. `IR_emit_vtable_t` deleted. `src/include/emit_ir.h` stripped to IR walk signatures only. `scrip.c` updated to call `emit_program(EMIT_JVM/JS/NET)`. Gates floor: GATE-1 5/0, GATE-2 23/26, GATE-3 194/36. Net −2077 LOC.
- [x] **EC-6** ✅ (one4all `7c33121c`, 2026-05-19, Sonnet 4.6) — delete `emit_wasm.c`; move WASM string table + user-fn table + `emit_wasm_from_sm` into `emit_core.c`; add `EMIT_WASM=8` + `IS_WASM` to `emit_core.h`; add WASM arms to `emit_prologue`/`emit_epilogue`/`emit_program`; `scrip.c` calls `emit_program(EMIT_WASM)`. Net −427 LOC. Gates: 5/0·23/26·194/36.
- [x] **EC-7** ✅ (2026-05-19, Sonnet 4.6) — Full gate run: all six frontends + broker + icon rung ladder all at floor. ARCH-IR.md updated with unified emitter model documentation. EC rung closed.
- [x] **EC-WASM-SM** ✅ (one4all `268619c1`, 2026-05-19, Sonnet 4.6) — IS_WASM arms added to all 5 SM_templates (push_pop_lits, arith, compare, control, pat). `sm_templates.h` created. `emit_wasm_from_sm` rewritten to call SM_template functions — one fn per opcode, all modes dispatched via IS_WASM/IS_JVM/IS_JS/IS_NET. `wasm_intern_str`/`wasm_intern_name` promoted from static. Gates: 7/0·5/0·23/26·194/36.

## Emitter Unification (EC-UNI) — x86 text/binary into SM_templates; wire all walkers through templates

### Problem

The SM_template functions (`sm_push_lit_i`, `sm_halt`, `sm_jump`, etc.) dispatch on `IS_JVM/IS_JS/IS_NET/IS_WASM` but have **no x86 arms**. The x86 text path (`EMIT_TEXT`) and x86 binary path (`EMIT_BINARY_WIRED`) go through a completely separate 3 000-line system: `emit_walk_codegen()` → `emit_sm_template()` → `sm_op_template_t` table (macro-expansion, string-table, label patching — all x86-only). The JVM/JS/NET walkers in `emit_core.c` also still carry their own inline opcode switch bodies instead of calling the template functions.

**Target:** one template function per SM opcode, one template function per BB box kind. Every backend — x86 text, x86 binary, binary-JVM, binary-.NET, JVM bytecode, JS, .NET IL, WASM — adds exactly one arm per function. Adding a new backend = add one enum value and one `IS_NEW` arm per function. Adding a new SM opcode = add one function with arms for every backend. Zero per-backend silo walkers. Zero parallel switch trees.

### Architecture after EC-UNI

```
SM_Program
    |
    v
emit_sm_dispatch(sm, out, mode)          ← single walk for ALL backends
    |
    for each SM_Instr:
        sm_<opcode>(instr, out)           ← one template fn per opcode
            IS_TEXT / IS_BIN  → x86 GAS text  / binary wired
            IS_JVM            → JVM Jasmin text
            IS_JS             → JavaScript text
            IS_NET            → MSIL .NET text
            IS_WASM           → WAT text
            IS_BIN_JVM        → (future) binary JVM class bytes
            IS_BIN_NET        → (future) binary .NET IL bytes
            IS_BIN_WASM       → (future) binary WASM bytes
```

`emit_walk_codegen` (x86), `emit_jvm_from_sm`, `emit_js_from_sm`, `emit_net_from_sm`, `emit_wasm_from_sm` are all deleted. A single `emit_sm_dispatch(SM_Program *, FILE *, bb_emit_mode_t)` replaces all five.

### Enum additions required

```c
/* emit_core.h — add after EMIT_WASM = 8 */
EMIT_BIN_JVM  = 9,   /* future: binary JVM .class bytes */
EMIT_BIN_NET  = 10,  /* future: binary .NET IL bytes    */
EMIT_BIN_WASM = 11,  /* future: binary WASM bytes       */

#define IS_X86_TEXT  (bb_emit_mode == EMIT_TEXT || bb_emit_mode == EMIT_TEXT_INLINE)
#define IS_X86_BIN   (bb_emit_mode == EMIT_BINARY_WIRED || bb_emit_mode == EMIT_BINARY_BROKERED)
#define IS_X86       (IS_X86_TEXT || IS_X86_BIN)
```

### Step ladder

- [x] **EC-UNI-0** ✅ (2026-05-19, Opus 4.7) — `emit_core.h`: enum split across 12 lines with `EMIT_BIN_JVM=9 / EMIT_BIN_NET=10 / EMIT_BIN_WASM=11` stubs added; macros `IS_X86_TEXT` / `IS_X86_BIN` / `IS_X86` (refine legacy `IS_TEXT` semantic without breaking it) + `IS_BIN_JVM` / `IS_BIN_NET` / `IS_BIN_WASM`; `emit_sm_dispatch(SM_Program *, FILE *, bb_emit_mode_t)` declared. `emit_core.c`: scaffold definition returns −1 for every mode (no callers yet). Gates floor: GATE-1 5/0, GATE-2 23/26, GATE-3 194/36/35, smoke prolog/raku 5/0 each.
- [x] **EC-UNI-1** ✅ (one4all `e2491770`, 2026-05-19, Opus 4.7) — `IS_X86_TEXT` arms in all 7 fns of `sm_push_pop_lits.c`. Un-staticed 7 dispatchers in `emit_sm.c` (no body changes) and declared them in `emit_sm.h`. Template arms call dispatchers directly → byte-identity by construction. New arms unreachable today (`emit_sm_dispatch` returns −1); EC-UNI-3 wires them. Gates floor: 5/0·23/26·194/36/35; prolog/raku 5/0 each.
- [ ] **EC-UNI-2** — x86 text arms: `sm_arith.c` (9 fns), `sm_compare.c` (3 fns), `sm_control.c` (4 fns: jump/s/f, halt), `sm_pat.c` (30 fns: SM_PAT_* + SM_EXEC_STMT), `sm_return` family (9 variants). One sub-commit per file. Gates held.
- [ ] **EC-UNI-3** — Wire `emit_sm_dispatch` for x86 text: if mode is `EMIT_TEXT`/`EMIT_TEXT_INLINE`, walk SM_Program calling template functions (now x86-capable). Run byte-identity check: `sm_codegen_text` output vs `emit_sm_dispatch(EMIT_TEXT)` output must be identical (md5 match on beauty.sno). Gates held.
- [ ] **EC-UNI-4** — Delete `emit_walk_codegen` / `sm_codegen_text` / `emit_sm_template` / `sm_op_template_t` table from `emit_sm.c`. Update `scrip.c`: x86 compile path calls `emit_program(ast, out, EMIT_TEXT)` (routes through `emit_sm_dispatch`). Gate: beauty.sno still produces byte-identical output vs SPITBOL oracle. Net LOC delta estimated −1 500.
- [ ] **EC-UNI-5** — Wire JVM/JS/NET inline switch arms in `emit_core.c` (`emit_jvm_from_sm`, `emit_js_from_sm`, `emit_net_from_sm`) to call SM_template functions instead of inlining opcode logic. Confirm output byte-identical. Delete the three inline switch bodies. `emit_sm_dispatch` now handles JVM/JS/NET/WASM and x86 — single walk for all backends. Full gate run.
- [ ] **EC-UNI-6** — x86 binary arms: `IS_X86_BIN` stubs in all template functions, wired through `emit_sm_dispatch(EMIT_BINARY_WIRED)`. Byte-identity vs existing `--run` path. (Prerequisite for future binary-JVM etc.)
- [ ] **EC-UNI-7** — Audit + close: remove any remaining per-backend silo logic; verify `IS_BIN_JVM/NET/WASM` stubs are clean no-ops; full gate run across all six frontends + broker + icon rung ladder. Update ARCH-IR.md. Rung closed.

### Invariant (EC-UNI)

After EC-UNI-5: there is exactly one SM walk function (`emit_sm_dispatch`). Every SM opcode has exactly one template function. Every backend adds exactly one arm per function. `emit_walk_codegen`, `emit_jvm_from_sm`, `emit_js_from_sm`, `emit_net_from_sm`, `emit_wasm_from_sm` do not exist.

### Invariant

After EC-5: every SM instruction and every BB box kind has exactly one function in
`emit_core.c`. Adding a new backend = adding one `case EMIT_NEW_TARGET:` arm per
function. Adding a new SM opcode = adding one function with arms for all backends.
No per-target silo files. No vtable dispatch.
