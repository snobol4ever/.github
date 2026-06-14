# HANDOFF — Sonnet 4.6 dead-code sweep pass 2, 2026-06-14

## Repo state
- Branch: `main`
- HEAD SCRIP: `3f3786d` (dead-code sweep pass 2)
- HEAD .github: `5b9f582c` (from prior session)
- Build: CLEAN
- Gates: smoke M3 7/7 · M4 7/7 HARD · pat-rung M4 19/19 HARD · fence TIER1=0 TIER2=0 HARD

## What landed this session

### Dead-code sweep pass 2 (3f3786d)
Continuing from GOAL-DEAD-CODE-SWEEP.md. All removals confirmed by `--gc-sections` oracle (601-function dead list, generated 2026-06-14). Each excised snippet mirrored to `src/attic/<mirror-path>/` with provenance header.

**ast_clone.c — whole-file dead → `git mv` to attic:**
`ast_gc_clone`, `code_free`, `expr_free` (static), `stmt_free` (static). The only apparent "caller" of `code_free` was a comment in `snobol4.tab.c`. Removed from Makefile SRCS and explicit compile rule. Removed `#include "ast_clone.h"` from `lower.h`.

**emit_core.c — 11 functions excised → `src/attic/emitter/emit_core.c`:**
- `emit_mode_set` — mode selector; superseded by `emitter_init_text/binary`; only callers in `tools/emit_per_kind_audit.c` (not in main Makefile build)
- `emitter_init_macro_def` — macro-def init alias; only caller in `tools/demo_template_productions.c`
- `ef_u32`, `ef_u64` — u32/u64 emit wrappers whose only callers were `ef_t3c` (itself dead)
- `ef_t3c` — old 3-column text asm formatter; superseded by `x86()` template dispatch
- `emit_call_label` — PLT-relative call emitter; all callers dead; `x86("call",...)` handles live paths
- `emit_text_stno_banner` — statement-number comment banner; no live callers
- `emit_text_rawf` — raw fprintf to sink; no live callers
- `bb_is_generator` — IR-kind classifier for the walk; NO AST/IR WALKING rule makes it dead
- `bb_walk`, `bb_walk_rec` (static) — IR-graph BFS walkers; same rule; also `g_visited[]`/`g_vcount`/`IR_WALK_MAX` data removed

**Header cleanup (declarations removed):**
- `emit_ir.h`: `bb_is_generator`, `bb_walk`
- `emit_core.h`: `emit_mode_set`, `emit_text_rawf`, `emit_text_stno_banner`, `emit_call_label`
- `emit_form.h`: `emitter_init_macro_def`
- `emit.h`: `emitter_init_macro_def`

**Note on ef_b2/ef_b3/ef_b4:** These were accidentally included in the removal but are LIVE (used by `emit_jmp_label` and `emit_aligned_call_rt`). They were restored immediately — confirmed present and working in the final build.

## Next session setup
```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && bash scripts/build_scrip.sh && make libscrip_rt
```

## Next dead-code sweep targets (see GOAL-DEAD-CODE-SWEEP.md)
The 601-item list is still authoritative. Highest-yield remaining clusters:

**1. rt_runtime.c — ~70 dead static functions**
The biggest single-file cluster. All are statics from the old interpreter residue: `seq_cache_*`, `susp_gen_cache_get`, `suspend_buf_push`, `gen_resume_target`, `ir_is_single_shot`, `bb_is_gen_*`, `bb_dcap_*`, `pas_*` interpreter helpers, Prolog `resolve_*` statics, `rt_arith_cmp_extract`, `rt_format_walk`/`_resolve`, `sort_msort_common`, `atom_chars_codes_common`, `functor_common`, `arg_common`, `descr_is_truthy`, `size_value`, `gz_eval_cell`, plus many `rt_*` exported symbols. Approach: use `--gc-sections` to re-verify the current dead list then batch-excise by cluster.

**2. emit_io.c — 8 dead functions need coordinated surgery**
`emit_textf`, `emit_1asm`, `emit_2asm`, `emit_directive`, `emit_comment`, `emit_io_flush`, `emit_io_reset`, `emit_io_get_sink` — their definitions can be removed from `emit_io.c` and `emit_io.h`, but their call sites in `emit_bb.c` (inside dead enclosing functions `bb_prepare_capture_arbno`, `resolve_emit_callee_block_body`, `sub_label`) must be excised simultaneously. Those three enclosing functions need to be found and removed from `emit_bb.c` (3906 lines) first.

**3. name_save.c — partial (2 of 10 symbols dead)**
`NAME_commit` and `NAME_pop` are dead; `NAME_ctx_enter`/`NAME_ctx_leave` are live. Surgical excision of 2 functions.

**4. scrip_ir.c — 2 dead symbols (`IR_sidecar_own` + one other)**
Small, low-risk.

**5. rt.c — `rt_cs_new` and other dead exported functions**
Several `rt_*` exported functions in rt.c itself (not just stubs) are dead per the oracle. Careful per-function excision needed.

## Landmines for next session
- `ef_b1`, `ef_b2`, `ef_b3`, `ef_b4` in `emit_core.c` are LIVE — do NOT remove them
- JVM/NET/JS/WASM backend helpers in `emit_core.c` are KEPT per policy (all 5 platforms supported)
- `emit_comment` and `emit_directive` in `emit.h`/`emit_bb.c` still have stale references — do NOT remove their definitions from `emit_io.c` until the enclosing dead functions in `emit_bb.c` are excised first
