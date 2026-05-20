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

### ✅ EC-UNI-9 axis-correction COMPLETE (2026-05-19, Opus 4.7)

Rung closed in 4 commits — one4all `63708215`, `7d792c59`, `073f3711`, `8308a457`.

- **9a `63708215`** — collapsed `IS_<BE>_TEXT`/`IS_<BE>_BIN` arms to `IS_<BE>` in 26 template files (10 SM + 16 BB). 349 BIN arms deleted, 349 TEXT→BE rewrites, net -349 LOC. Script `scripts/ec_uni_9a_collapse.py` is idempotent and committed.
- **9b `7d792c59`** — deleted `EMIT_BIN_{JVM,NET,WASM}` enum values + 12 dead macros from `emit_core.h`. `IS_X86` redefined as the union of all five x86 sub-modes (`EMIT_TEXT`, `EMIT_TEXT_INLINE`, `EMIT_MACRO_DEF`, `EMIT_BINARY_WIRED`, `EMIT_BINARY_BROKERED`).
- **9c `073f3711`** — rewrote matrix gate for 5-column form. `scripts/test_gate_em_template_matrix.{py,sh}` now enforces 365 cells (57 SM × 5 + 16 BB × 4) instead of the false-axis 730. Pass: 0/365.
- **9d `8308a457`** — renamed `dispatch_one_x86_text` → `dispatch_one_x86`; expanded the `IS_X86` comment in `emit_core.h` to enumerate all five x86 sub-modes explicitly so the next reader sees the architectural point.
- **9e** — HQ doc updates (this block + AXIS CORRECTION block + watermark + Invariant rewrite landed in `.github` before code work).

Gates floor flag-off AND flag-on across all rungs:
- GATE-1 (smoke icon): 5/0
- GATE-2 (broker): 23/26
- GATE-3 (icon all-rungs `--interp`): 194/36/35
- matrix gate: 0/365 PASS

**NEXT: EC-UNI-3-beauty** (unblocked, partially investigated). Probe ran end of session — the HQ doc's prediction that flag-off vs flag-on diff would be "GAS-comments only" turned out to be **wrong**.  Real divergences found:

| Macro emitted | Flag OFF | Flag ON | Why |
|---|---|---|---|
| `SM_NRETURN[_S/_F]` | `NRETURN_VAR fname_lbl, cond, pc` | `RETURN_VARIANT 2, cond, 0` | `emit_sm_return_template` passes `prog=NULL` and `pc=0` to `emit_sm_return_variant_dispatch`; the `kind==2 && prog` branch (lines 2109–2122 of `emit_sm.c`) never fires → falls through to the generic `emit_sm_ret_var`. **Different GAS macro.** |
| `SM_FRETURN[_S/_F]`, `SM_RETURN_[S/F]` | `RETURN_VARIANT k, c, pc` | `RETURN_VARIANT k, c, 0` | Same shim → same `pc=0`. Macro is the same but third operand differs. **Real divergence — pc is not annotational, it's a macro arg used at GAS-assembly time.** |
| `SM_STNO` annotation | `# stmt N (line M): SOURCE_TEXT` | `# stmt N (line M)` | `emit_sm_stno_template` passes `SrcLines=NULL`. Comment drift only — as predicted. |

**Root cause:** two shims (`emit_sm_return_template` in `emit_sm.c:2132`, `emit_sm_stno_template` in `emit_sm.c:2027`) pass NULL for the private state (`SM_Program *`, `SrcLines *`) and `0` for `pc`. The clean fix is approach #2 from earlier: **promote `prog` + `srclines` into `sm_ctx_t`** (extension to the existing struct in `SM_templates/sm_ctx.h`) and have `dispatch_one_x86` populate them. Then the shims forward `ctx->i`, `ctx->prog`, `ctx->srclines`. WIP was laid in but reverted at handoff for cleanliness.

**Concrete EC-UNI-3-beauty plan for next session:**
1. Extend `sm_ctx_t` (in `src/emitter/SM_templates/sm_ctx.h`) with `const struct SM_Program * prog;` and `const void * srclines;` (opaque — `SrcLines` is private to `emit_sm.c`).
2. Add `#include "SM_templates/sm_ctx.h"` to `emit_sm.h` (currently only `sm_template_common.h` pulls it in).
3. Change signatures: `emit_sm_return_template(out, ins, ctx)`, `emit_sm_stno_template(out, ins, ctx)`. Pass `ctx->i` as pc, `(SM_Program*)ctx->prog`, `(SrcLines*)ctx->srclines`.
4. Promote `sm_stno` template to take `const sm_ctx_t *ctx` (mirrors `sm_jump`/`sm_halt`/`sm_return`).
5. Update `dispatch_one_x86` signature to receive `prog` and `sl` from `emit_walk_codegen` (currently file-scope locals at `emit_sm.c:3032–3033`). Fill `ctx.prog = prog; ctx.srclines = sl_loaded ? &sl : NULL;`.
6. Build, gate, write `scripts/test_gate_em_ec_uni_3_beauty.sh`: compile `corpus/programs/snobol4/demo/beauty/beauty.sno --compile` flag-off and flag-on, `diff -q` should report identical. SPITBOL oracle (`/home/claude/x64`) only needed if we want to also verify against Milestone 1's byte-identity — `EC-UNI-3-beauty` itself just needs self-identity.
7. After 3-beauty closes, **EC-UNI-4** deletes `emit_walk_codegen`.

The 5 affected files (uncommitted WIP, reverted at handoff): `src/emitter/SM_templates/sm_ctx.h`, `src/emitter/SM_templates/sm_returns.c`, `src/emitter/SM_templates/sm_templates.h`, `src/emitter/emit_sm.c`, `src/emitter/emit_sm.h`. About 60% of the work was done before revert; reproducing should take an hour.

---

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

**EC-UNI-2d ✅ (one4all `b1711529`, 2026-05-19, Opus 4.7):** `IS_X86_TEXT` arms in `sm_pat.c` — all 31 fns carry x86 text arms (30 SM_PAT_* + SM_EXEC_STMT, with `sm_pat_any`/`sm_pat_any_i` variant pair). Un-staticed 22 uniform pat dispatchers (`emit_sm_pat_span_dispatch`..`emit_sm_pat_deref_dispatch`) so templates call them directly. Introduced 8 public shims for the non-uniform dispatchers (`emit_sm_pat_lit_template`, `_refname_template`, `_capture_template`, `_capture_fn_template`, `_capture_fn_args_template`, `_usercall_template`, `_usercall_args_template`, `emit_sm_exec_stmt_template`) that keep the private types (`sm_op_template_t`, `emit_sm_args_t`, `pat_arg_label`) inside `emit_sm.c` — same pattern as EC-UNI-2b/2c's `emit_sm_stno_template` / `emit_sm_return_template`. All 31 template arms call the dispatcher/shim directly → byte-identity by construction. `emit_sm_dispatch` still returns −1; new arms are reachable but unreached. EC-UNI-3 wires them. Gates floor: GATE-1 5/0, GATE-2 23/26, GATE-3 194/36/35; smoke prolog 5/0, raku 5/0, rebus 4/0, snobol4 7/0, snocone 2/3.

**EC-4 ✅ COMPLETE 2026-05-19 (Sonnet 4.6, one4all `8890d685`).** emit_prologue/emit_epilogue unified in emit_core.c; IS_JVM/IS_JS/IS_NET dispatch; emit_ir_block calls unified fns. Static silo fns retained for EC-5 vtable. +71/-13 LOC.

**EC-5 ✅ COMPLETE 2026-05-19 (Sonnet 4.6, one4all `e1c8a4ac`).** emit_jvm.c/emit_js.c/emit_net.c/emit_ir.c/emit_ir_targets.c/emit_ir.h(shim) deleted. IR walk (ir_node_id/ir_is_generator/ir_walk) + three SM-walk loops (emit_jvm_from_sm/emit_js_from_sm/emit_net_from_sm) + helpers (jvm_sanitize_name/net_parse_define_proto) moved to emit_core.c. Unified emit_program(ast_prog,out,mode) replaces 3 per-target entry points. IR_emit_vtable_t deleted. src/include/emit_ir.h stripped. Net −2077 LOC. Gates floor: 5/0·23/26·194/36.

**EC-UNI-3 partial 🔄 (one4all `42908963`, 2026-05-19, Opus 4.7):** wired feature-flag-gated unified dispatch into `emit_walk_codegen`. Added `g_emit_use_unified_dispatch` (env var `SCRIP_UNIFIED_DISPATCH`) and `dispatch_one_x86_text(out, ins, pc)` covering all 52 templated opcodes. Hook runs after pattern-window check, before the legacy switch; falls through to legacy on -1.

  **Mode-set invariant surfaced during validation (binding on EC-UNI-4):** `bb_emit_mode` defaults to `EMIT_BINARY_WIRED` at process start. Legacy `emit_walk_codegen` relies on individual dispatchers calling `emitter_init_text` to flip into `EMIT_TEXT`. The unified hook runs BEFORE those dispatchers, so without an explicit mode set, `IS_X86_TEXT` is false on the first iteration and templates fall through all backend arms producing no output. Fix landed in same commit: `dispatch_one_x86_text` calls `emit_mode_set(TEXT_MODE(), out)` at entry. **EC-UNI-4 invariant: the unified dispatch entry point owns mode-setting; individual dispatchers can remain idempotent.**

  Validation:
   - Flag OFF (default): all gates floor, no regression — hot path costs one predictable-not-taken compare per iteration.
   - Flag ON: all smoke + broker + icon rungs floor. `hello.sno --compile` byte diff vs flag-off is GAS-comments only (EC-UNI-2b SrcLines degradation in SM_STNO banner — machine code byte-identical).

  **NEXT: EC-UNI-3-beauty** — close the rung by running the byte-identity gate on beauty.sno. SPITBOL x64 cloned to `/home/claude/x64`. Two paths:
  1. Write `scripts/test_gate_em_ec_uni_3_beauty.sh` that compiles beauty.sno both ways and md5-compares modulo SrcLines drift (filter `# stmt` comment lines).
  2. Promote SrcLines into `sm_ctx_t` so the unified path carries source lines through — md5 matches exactly without filtering.
  Approach #2 is cleaner; #1 unblocks EC-UNI-4 faster.

**Recent progress this session (Opus 4.7, 2026-05-19):**
- EC-UNI-0  (one4all `f29c95e9`): scaffold + macros + enum stubs
- EC-UNI-1  (one4all `e2491770`): `sm_push_pop_lits.c` 7 fns
- EC-UNI-2a (one4all `fc9d0122`): `sm_arith.c` 9 fns
- EC-UNI-2b (one4all `609dac51`): `sm_compare.c` 3 fns + `emit_sm_stno_template` shim
- EC-UNI-2c (one4all `bfa65968`): `sm_control.c` 7 fns + `emit_sm_return_template` shim
- EC-UNI-2d (one4all `b1711529`): `sm_pat.c` 31 fns + 8 non-uniform pat shims
- EC-UNI-3  (one4all `42908963`) partial: `dispatch_one_x86_text` + feature flag; mode-set invariant surfaced and fixed; beauty.sno gate still owed.

All 52 SM_template fns across 5 files carry `IS_X86_TEXT` arms and are reachable via `SCRIP_UNIFIED_DISPATCH=1`. EC-UNI-3-beauty (the byte-identity gate on beauty.sno) closes the rung.

**Architectural decisions established this session:**
1. **Byte-identity by construction** — template `IS_X86_TEXT` arms call exactly the dispatcher fns the existing `emit_walk_codegen` switch calls. Not parallel reimplementations.
2. **Private types stay private** — when a dispatcher takes private state (`SrcLines`, `SM_Program *prog`), expose a thin shim that passes NULL. The minor degradation (comment annotations only) is GAS-comment-only — machine code unaffected. EC-UNI-3 can promote these into `sm_ctx_t`.
3. **`emit_sm_dispatch` returns −1** until EC-UNI-3. New arms are reachable but unreached today; bisectable by construction.
4. **Unified dispatch owns mode-setting** (EC-UNI-3, 2026-05-19) — `bb_emit_mode` defaults to `EMIT_BINARY_WIRED`; legacy dispatchers each set `EMIT_TEXT` themselves via `emitter_init_text` (or rely on a prior dispatcher having done so). The unified-dispatch entry point must call `emit_mode_set(TEXT_MODE(), out)` at the top of every per-opcode iteration. Individual dispatchers remain idempotent — they can still call `emit_mode_set` themselves with no harm. **Binding on EC-UNI-4** when `emit_walk_codegen` is deleted and the unified dispatch becomes the sole entry.


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
one4all: 8308a457     (EC-UNI-9 axis-correction COMPLETE.  9a: 26 template files
                       collapsed to 5-arm form (-349 BIN arms).  9b: EMIT_BIN_*
                       enum + 12 dead macros deleted; IS_X86 covers all 5 x86
                       sub-modes (TEXT/TEXT_INLINE/MACRO_DEF/BIN_WIRED/BIN_BROK).
                       9c: matrix gate rewritten for 5-column form (365 cells,
                       was 730).  9d: dispatch_one_x86_text -> dispatch_one_x86.
                       Net -376 LOC.  EC-UNI-3-beauty unblocked.)
corpus:  92e103f      (unchanged)
.github: (this commit — EC-UNI-9 marked complete; AXIS CORRECTION block enumerates 5 x86 modes; Invariant blocks already 5-column)
--interp:    194/265  (held — 194/36/35 flag-off AND flag-on, verified)
smoke ×6:    5/0 5/0 5/0 4/0 5/0 7/0  (held, flag off AND flag on)
broker:      23/26    (held, flag off AND flag on)
matrix gate: 0/365 PASS  (rewritten from 0/730)
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

### ⚠ AXIS CORRECTION (2026-05-19, Opus 4.7, ratified by Lon)

EC-UNI-0..8.3 introduced a **false text-vs-binary axis** in the template matrix. The split was wrong:

- `IS_X86_TEXT` / `IS_X86_BIN` are not two backends. They are **two output formats of one backend (x86)**. In fact x86 has FIVE output sub-modes — all flow through the single `IS_X86` arm:
  - `EMIT_TEXT` — GAS text (normal invocation)
  - `EMIT_TEXT_INLINE` — GAS text (inline form for hot paths)
  - `EMIT_MACRO_DEF` — GAS macro-definition pass
  - `EMIT_BINARY_WIRED` — binary machine code, wired BBs
  - `EMIT_BINARY_BROKERED` — binary machine code, brokered BBs
- The template function emits a *logical* instruction. The decision "write `movq $0x1, %rax` (GAS text)" vs "write `\x48\xc7\xc0\x01\x00\x00\x00` (binary machine code)" — and the choice between regular GAS, inline GAS, or macro-definition emission — is made **below** the template, in the encoder/serializer/dispatcher layer (consulting `bb_emit_mode` and `TEXT_MODE()`). The template doesn't know or care.
- The same correction applies to JVM (Jasmin text vs `.class` bytes), .NET (ilasm text vs IL bytes), and WASM (WAT text vs binary bytes). JS has no binary form.

**Correct matrix is 5 columns, not 10.**

```
                | X86 | JVM | JS  | NET | WASM |
----------------+-----+-----+-----+-----+------+
SM_PUSH_LIT_I   |  1  |  1  |  1  |  1  |  1   |   ← 5 arms per template fn
...             | ... | ... | ... | ... | ...  |
```

Text-vs-binary is **hidden inside each backend's output layer**, not exposed as a matrix dimension.

### Corrected template shape

```c
void sm_halt(SM_Instr *ins, FILE *out) {
    if (IS_X86)  { emit_sm_halt_dispatch(ins, out); return; }   // text OR binary, same call
    if (IS_JVM)  { ... }
    if (IS_JS)   { ... }
    if (IS_NET)  { ... }
    if (IS_WASM) { ... }
}
```

The serializer below `emit_sm_halt_dispatch` consults `bb_emit_mode` (or the `FILE *` writer's underlying sink) to choose GAS text vs binary bytes. Same for JVM/NET/WASM.

### Implications for the ladder

- `IS_X86_TEXT` / `IS_X86_BIN` / `IS_JVM_TEXT` / `IS_JVM_BIN` / `IS_NET_TEXT` / `IS_NET_BIN` / `IS_WASM_TEXT` / `IS_WASM_BIN` macros → **collapse to** `IS_X86` / `IS_JVM` / `IS_NET` / `IS_WASM`. `IS_JS` already correct.
- `EMIT_BIN_JVM = 9` / `EMIT_BIN_NET = 10` / `EMIT_BIN_WASM = 11` enum stubs → **deleted**. They were the symptom of the false axis. Binary modes for those backends, when they land, are output-format choices inside the existing `EMIT_JVM` / `EMIT_NET` / `EMIT_WASM` arms.
- `dispatch_one_x86_text` → renamed `dispatch_one_x86`. Legacy `emit_walk_codegen`'s binary path flows through the same unified dispatch as text.
- Matrix-completeness gate count: **730 cells → 365 cells** (57 SM × 5 + 16 BB × 5).
- The 213 fixups in EC-UNI-8.3-fixup (NET-PAT n/a, X86_BIN stubs, WASM n/a in BB_templates) — most were filling cells that never should have existed. Real n/a entries (NET-PAT genuinely stubbed; BB WASM never landed) survive as honest 5-column gaps.
- EC-UNI-3-beauty's byte-identity gate becomes simpler: text and binary share a function, so identity is by construction once the single `IS_X86` arm is correct.

### Remediation steps (added to ladder below as EC-UNI-9 series)

- **EC-UNI-9a** ✅ (one4all `63708215`, 2026-05-19, Opus 4.7) — Collapse `IS_<BE>_TEXT`/`IS_<BE>_BIN` to `IS_<BE>` everywhere. 26 template files (10 SM + 16 BB), 349 BIN arms deleted, 349 TEXT→BE rewrites, -349 net LOC. Mechanical via `scripts/ec_uni_9a_collapse.py` (idempotent, committed).
- **EC-UNI-9b** ✅ (one4all `7d792c59`, 2026-05-19, Opus 4.7) — Deleted `EMIT_BIN_{JVM,NET,WASM}` enum values + 12 dead macros (`IS_X86_TEXT/BIN`, `IS_BIN_{JVM,NET,WASM}`, `IS_{JVM,JS,NET,WASM}_{TEXT,BIN}`) from `emit_core.h`. `IS_X86` redefined as union of all five x86 sub-modes (`EMIT_TEXT`, `EMIT_TEXT_INLINE`, `EMIT_MACRO_DEF`, `EMIT_BINARY_WIRED`, `EMIT_BINARY_BROKERED`).
- **EC-UNI-9c** ✅ (one4all `073f3711`, 2026-05-19, Opus 4.7) — Rewrote `scripts/test_gate_em_template_matrix.{py,sh}` for 5-column matrix. Gate passes 0/365 (was 0/730). Drop `_TEXT`/`_BIN` cell parsing; BB still auto-skips X86 row.
- **EC-UNI-9d** ✅ (one4all `8308a457`, 2026-05-19, Opus 4.7) — Renamed `dispatch_one_x86_text` → `dispatch_one_x86` (3 sites in `emit_sm.c`). `IS_X86` comment in `emit_core.h` expanded to enumerate the 5 x86 sub-modes explicitly so future readers understand the architectural point: text/binary/macro-def output is chosen by the dispatcher and serializer layer below the template, not by the template itself.
- **EC-UNI-9e** ✅ (this commit) — HQ doc updates: Open-step pointer marked complete with commit ledger; Watermark refreshed; Invariant (EC-UNI-8) block already rewritten to 5-column form during AXIS CORRECTION (pre-EC-UNI-9a); AXIS CORRECTION block enumerates 5 x86 modes explicitly.

EC-UNI-9 must land **before** EC-UNI-4 (delete `emit_walk_codegen`), because EC-UNI-4 will introduce the second caller of the unified dispatch (x86 binary), and that caller must hit the same `IS_X86` arm — not a separate `IS_X86_BIN` arm.

### Historical record

Sub-steps EC-UNI-0..2d, 8.1..8.4 below were written under the 10-cell assumption. They are kept verbatim as audit trail. The work itself (un-staticing dispatchers, building template arms, wiring the feature flag) all stands — the labels just collapse from `IS_X86_TEXT` → `IS_X86` under EC-UNI-9a.

---

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
- [x] **EC-UNI-2a** ✅ (one4all `fc9d0122`, 2026-05-19, Opus 4.7) — `IS_X86_TEXT` arms in `sm_arith.c` (9 fns: concat, neg, coerce_num, exp, add/sub/mul/div/mod). Un-staticed 5 dispatchers (`edp4_sm_arith` handles 5 arith ops; 4 dedicated dispatchers for the others).
- [x] **EC-UNI-2b** ✅ (one4all `609dac51`, 2026-05-19, Opus 4.7) — `IS_X86_TEXT` arms in `sm_compare.c` (3 fns: stno, acomp, lcomp). Introduced `emit_sm_stno_template` shim (private `SrcLines` type stays inside `emit_sm.c`; shim passes NULL ⇒ no source-line comment in GAS, machine code byte-identical).
- [x] **EC-UNI-2c** ✅ (one4all `bfa65968`, 2026-05-19, Opus 4.7) — `IS_X86_TEXT` arms in `sm_control.c` (7 fns: jump/s/f, halt, return/freturn/nreturn). Un-staticed `emit_halt_line` + 3 jump dispatchers + 2 return dispatchers. Introduced `emit_sm_return_template` shim that dispatches plain SM_RETURN → `emit_sm_return_dispatch` (handles `g_in_define_body`); other 8 variants → `emit_sm_return_variant_dispatch` with `prog=NULL` (NRETURN function-name annotation degrades to generic banner; machine code byte-identical).
- [x] **EC-UNI-2d** ✅ (one4all this commit, 2026-05-19, Opus 4.7) — `IS_X86_TEXT` arms in `sm_pat.c` (31 fns: full SM_PAT_* + SM_EXEC_STMT, including `sm_pat_any`/`sm_pat_any_i` pair). Un-staticed 22 uniform pat dispatchers (`emit_sm_pat_span_dispatch`..`emit_sm_pat_deref_dispatch`) called directly from templates. Introduced 8 public shims for non-uniform dispatchers (LIT/REFNAME/CAPTURE/CAPTURE_FN/CAPTURE_FN_ARGS/USERCALL/USERCALL_ARGS/EXEC_STMT) keeping private types (`sm_op_template_t`, `emit_sm_args_t`, `pat_arg_label`) inside `emit_sm.c`. Templates call shims/dispatchers directly → byte-identity by construction. Gates floor.
- [ ] **EC-UNI-3** 🔄 partial (one4all `42908963`, 2026-05-19, Opus 4.7) — feature-flag-gated unified dispatch wired into `emit_walk_codegen`. `g_emit_use_unified_dispatch` (env `SCRIP_UNIFIED_DISPATCH`); `dispatch_one_x86_text` covers all 52 templated opcodes. Mode-set invariant fixed at hook entry. Flag-off and flag-on both pass smoke + broker + icon rungs at floor; `hello.sno --compile` diff is comment-only (EC-UNI-2b SrcLines degradation). **Rung closes when `test_gate_em_ec_uni_3_beauty.sh` md5-matches beauty.sno output flag-off vs flag-on (modulo or absent SrcLines drift).**
- [ ] **EC-UNI-4** — Delete `emit_walk_codegen` / `sm_codegen_text` / `emit_sm_template` / `sm_op_template_t` table from `emit_sm.c`. Update `scrip.c`: x86 compile path calls `emit_program(ast, out, EMIT_TEXT)` (routes through `emit_sm_dispatch`). Gate: beauty.sno still produces byte-identical output vs SPITBOL oracle. Net LOC delta estimated −1 500.
- [ ] **EC-UNI-5** — Wire JVM/JS/NET inline switch arms in `emit_core.c` (`emit_jvm_from_sm`, `emit_js_from_sm`, `emit_net_from_sm`) to call SM_template functions instead of inlining opcode logic. Confirm output byte-identical. Delete the three inline switch bodies. `emit_sm_dispatch` now handles JVM/JS/NET/WASM and x86 — single walk for all backends. Full gate run.
- [ ] **EC-UNI-6** — x86 binary arms: `IS_X86_BIN` stubs in all template functions, wired through `emit_sm_dispatch(EMIT_BINARY_WIRED)`. Byte-identity vs existing `--run` path. (Prerequisite for future binary-JVM etc.)
- [ ] **EC-UNI-7** — Audit + close: remove any remaining per-backend silo logic; verify `IS_BIN_JVM/NET/WASM` stubs are clean no-ops; full gate run across all six frontends + broker + icon rung ladder. Update ARCH-IR.md. Rung closed.
- [ ] **EC-UNI-8** — **Full unified template matrix.** Tighten EC-UNI-5/6/7 to the strictest form: exactly **one** C function per BB graph kind in `BB_templates/`, exactly **one** C function per SM opcode in `SM_templates/`, with **every backend × every mode-of-operation** handled as an arm inside the single function. No grouped-by-family multi-fn files. No silo helpers carrying backend-specific switches outside the template.
    - 8.1 ✅ **Granularity normalisation** (revised — one4all `573bc63c`, 2026-05-19, Opus 4.7). After an initial 57-file per-opcode split (ad250dce) was reviewed as too granular, regrouped into **10 themed files**: sm_push_pop_lits (7), sm_arith (9), sm_compare (3), sm_jumps (3), sm_halt (1), sm_returns (3), sm_pat_anchors (9), sm_pat_position (8), sm_pat_control (6), sm_pat_combine (8) — total 57 fns. Shared helpers (jvm_ret_guard, net_ret_guard, jvm_pat_str_push, jvm_pat_long_push, jvm_pat_noarg_push, jvm_pat_pat_push, jvm_pat_2pat_push) remain `static inline` in `sm_template_common.h`. `scripts/ec_uni_8_1_regroup.py` drives the regroup. Adding a new SM opcode = add fn to the appropriate themed file. Gates floor.
    - 8.3 ✅ **Matrix-completeness gate** (one4all `573bc63c` + `af370d45`, 2026-05-19, Opus 4.7). `scripts/test_gate_em_template_matrix.sh` + `.py` machine-check every top-level fn in `{SM,BB}_templates/` for full backend × mode matrix coverage (10 cells per fn). Initial run flagged 213 misses across 73 fns; 8.3-fixup (`af370d45`) closed all 213: 4 sm_pat_* files' one-liner fns expanded to canonical multi-line form with NET-PAT n/a sentinels, sm_halt/sm_jumps/sm_returns gained X86_BIN stubs (EC-UNI-6 owed), all 16 BB_templates gained WASM n/a sentinels (BB WASM never landed in original code). Architectural decisions ratified: NET PAT is stub (n/a everywhere in sm_pat_*), BB WASM never landed (n/a in bb_*), X86_BIN goes through legacy emit_walk_codegen today (stub), JS_BIN is global standing n/a. **Gate now passes: 0/730.**
    - 8.2 ✅ **Mode-of-operation axis explicit** (one4all `4b430ebb`/`c8b0686d`/`eca7cc34`, 2026-05-19, Opus 4.7). `IS_JVM_TEXT`/`IS_JVM_BIN`/`IS_JS_TEXT`/`IS_JS_BIN` (canonical n/a)/`IS_NET_TEXT`/`IS_NET_BIN`/`IS_WASM_TEXT`/`IS_WASM_BIN` macros landed in `emit_core.h`. All 5 SM_templates files (sm_push_pop_lits, sm_arith, sm_compare, sm_control, sm_pat — 57 fns) and all 16 BB_templates files promoted via `scripts/ec_uni_8_promote*.py`. Each fn body now carries an arm or n/a comment per cell. Byte-identity: the renamed `_TEXT` macros are equivalent to the bare `IS_*` macros (`EMIT_JVM` etc are text-mode by definition); `_BIN` arms are unreachable today (no caller sets `EMIT_BIN_*`). Gates floor flag-off AND flag-on: 5/0·23/26·194/36/35.
    - 8.3 partial 🔄 (covered by row above; landed with 8.1 regroup as one commit 573bc63c.)
    - 8.4 partial 🔄 **Silo audit** (one4all `af370d45` review, 2026-05-19, Opus 4.7). Audit ran `grep -rn "switch.*->op\|switch (instr" src/emitter/` outside `{SM,BB}_templates/`. Found 10 switches across emit_core.c + emit_sm.c, partitioned into three categories: (A) 4 silo walkers — `emit_jvm_one_instr`, `emit_js_from_sm`, `emit_net_from_sm`, `emit_wasm_from_sm` — each has its own dispatch switch but arms call `sm_*` template fns (EC-UNI-5 moved bodies into templates but left the four walker switches in parallel; EC-UNI-8.4-fix would collapse them into a single `emit_sm_dispatch`); (B) 1 legacy x86 walker `emit_walk_codegen` (EC-UNI-4 target, gated on EC-UNI-3-beauty); (C) 5 whitelisted analysis passes (`strtab_collect ×2`, `emit_flat_invariant`, `pattern_windows_collect`, `dispatch_one_x86_text` — the unified-dispatch endpoint itself). Findings logged to `EC-UNI-8.4-SILO-AUDIT.md`. **NEXT: EC-UNI-3-beauty** is the prerequisite for unwinding Category B; then EC-UNI-4 deletes 1 switch; then EC-UNI-8.4-fix collapses Category A's 4 walkers into 1.
    - 8.5 — **Add-a-backend test.** As regression scaffold, add `EMIT_NULL` = 99 to `emit_core.h` and `IS_NULL`/`IS_NULL_TEXT`/`IS_NULL_BIN` macros. Walk every template; add `if (IS_NULL_TEXT) { fputs("/*null*/", out); return; }` and `if (IS_NULL_BIN) return;` arms via mechanical patch. `emit_program(ast, out, EMIT_NULL)` produces `/*null*/` per instruction. Gate: adding the backend touched exactly N template files + 1 header — no other code. Then revert (the test proves the property, not the backend).
    - 8.6 — **Add-an-opcode test.** Same regression scaffold: add `SM_NOP` opcode and `SM_templates/sm_nop.c` with 10 arms (or n/a). Lower a synthetic AST node that emits `SM_NOP`. Confirm every backend produces correct output. Gate: adding the opcode touched exactly 1 new template file + opcode enum — no per-backend silo edits. Then revert.
    - 8.7 — **Documentation + close.** Update `ARCH-IR.md` and `ARCH-SCRIP.md` with the full matrix invariant. Update this file's "Invariant (EC-UNI)" block. Rung closed.

### Invariant (EC-UNI)

After EC-UNI-5: there is exactly one SM walk function (`emit_sm_dispatch`). Every SM opcode has exactly one template function. Every backend adds exactly one arm per function. `emit_walk_codegen`, `emit_jvm_from_sm`, `emit_js_from_sm`, `emit_net_from_sm`, `emit_wasm_from_sm` do not exist.

### Invariant (EC-UNI-8: full matrix) — REVISED 2026-05-19

After EC-UNI-8 (post EC-UNI-9 collapse) the emitter is a 2D Cartesian product with **one column per backend, not per output format**:

```
                    | X86 | JVM | JS  | NET | WASM |
--------------------+-----+-----+-----+-----+------+
SM_PUSH_LIT_I       | sm_push_lit_i.c — ONE function, 5 arms             |
SM_PUSH_LIT_S       | sm_push_lit_s.c — ONE function, 5 arms             |
...  (57 SM ops)    | ...                                                 |
--------------------+-----------------------------------------------------+
BB_LIT              | bb_lit.c — ONE function, 5 arms (WASM n/a)         |
BB_ANY              | bb_any.c — ONE function, 5 arms (WASM n/a)         |
...  (18 BB kinds)  | ...                                                 |
```

Text-vs-binary is **not** a matrix column. It is a serializer choice **inside** each `IS_X86` / `IS_JVM` / `IS_NET` / `IS_WASM` arm, made by the encoder layer below the dispatcher. JS has no binary form, so `IS_JS` is single-format by construction.

- **One file = one template fn.** No SM/BB logic outside its own file.
- **One arm per backend.** Each arm calls a dispatcher; the dispatcher emits either GAS text or binary bytes based on `bb_emit_mode` — the template does not branch on output format.
- **Adding a backend** = N template-file edits (one `IS_NEW` arm per fn) + 1 header enum + 1 macro. Zero silo files touched.
- **Adding an opcode** = 1 new template file + 1 enum value. Zero silo files touched.
- **Removing a backend** = strip its arms from every template (mechanical). Zero silo files to find.
- **Adding a new output format to an existing backend** (e.g. WASM binary alongside WAT text) = zero template-file edits. Encoder-layer change only.
- **Matrix gate** (`scripts/test_gate_em_template_matrix.sh`) machine-checks 5-cell coverage per fn: any cell missing without an `n/a` annotation fails the build. **Gate count: 365 cells** (57 SM × 5 + 16 BB × 5), down from the (incorrect) 730.

### Invariant

After EC-5: every SM instruction and every BB box kind has exactly one function in
`emit_core.c`. Adding a new backend = adding one `case EMIT_NEW_TARGET:` arm per
function. Adding a new SM opcode = adding one function with arms for all backends.
No per-target silo files. No vtable dispatch.
