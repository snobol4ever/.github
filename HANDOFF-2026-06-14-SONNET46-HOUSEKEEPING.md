# HANDOFF — Sonnet 4.6 housekeeping session, 2026-06-14

## Repo state
- Branch: `main`
- HEAD SCRIP: `8e82507` (dead-code sweep pass 1)
- HEAD .github: `3bb377c0` (GOAL-DEAD-CODE-SWEEP.md added)
- Build: CLEAN
- Gates: smoke M3 7/7 · M4 7/7 HARD · pat-rung M4 19/19 HARD · fence TIER1=0 TIER2=0 HARD

## What landed this session

### 1. CLI trimmed to 7 switches (94c94f4, 6de515a)
Kept: `--run` `--compile` `--target=` `--dump-ast` `--dump-ir` (was `--dump-bb*`) `--transpile` (was `--dump-sno`) `--bench`.
Removed and dead-code swept simultaneously: `--monitor` `--trace` `--dump-bb` `--dump-bb2` `--dump-sno` `--dump-sm` `--dump-ast-bison` `--dump-width` `--case-sensitive` `--fold-case`, plus `sync_monitor.h` include, `CODE_t *sub`, `extern ir_set_print_width`, `g_opt_trace` global and its declaration, `sync_monitor.c` from main Makefile build.

### 2. Dead-code sweep pass 1 (8e82507)
GC oracle (`--gc-sections`, 841 corpus programs across 6 languages, combined 2208 roots) identified **601 dead functions**.
Pass 1 excised:
- `smx_dead_stubs.c` dropped from Makefile (already in attic)
- `execute_program_steps` stub from `interp_ast_stubs.c`
- `g_ir_step_limit/done/jmp` + `rs24_diag_*` + `rs24_diag_hits_ptr` from `interp_globals.c`
- `execute_program_steps` / `g_ir_step_*` declarations from `interp.h`
- `sm_yield_to_caller` stub from `gen_runtime.c`
- Weak stubs `sm_opcode_name` + `_is_pat_fnc_name` + `_expr_is_pat` from `rt.c`
- `sm_opcode_name` declaration from `SM.h`
All excised code mirrored to `src/attic/<mirror-path>/file.c` with provenance headers.
Policy: JVM/NET/JS/WASM backend helpers **KEPT** (all 5 platforms supported).

### 3. GOAL files updated (3bb377c0)
- `.github/GOAL-DEAD-CODE-SWEEP.md` — new file; full 601-item dead list; attic convention
- `.github/GOAL-SNOBOL4-BB.md` — session watermark prepended
- `.github/PLAN.md` — DEAD-CODE-SWEEP added to Active Goals table

## Next session setup
```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && bash scripts/build_scrip.sh
make libscrip_rt
```

## Next dead-code sweep targets (see GOAL-DEAD-CODE-SWEEP.md)
Largest clusters not yet tackled:
1. **emit_io.c** — `emit_textf` `emit_1asm` `emit_2asm` `emit_directive` `emit_comment` `emit_io_flush` `emit_io_reset` `emit_io_get_sink` — need coordinated removal from `emit_io.h`, `emit.h`, and the 3 call sites in `emit_bb.c` (dead paths)
2. **rt_push_*/rt_pop_*** — value-stack residue (ICON STACKLESS rule); scattered across `rt.c` and runtime
3. **Prolog resolve_* tree** — ~30 functions; needs audit of which are live from Prolog BB templates
4. **Old meta-interp cluster** — `meta_arith` `meta_builtin_solve` `meta_conj_drive` etc.
5. **Lex utility stubs** — `yy_init_globals` `yy_pop_state` `yyget_*` `yyset_*` per-parser copies
