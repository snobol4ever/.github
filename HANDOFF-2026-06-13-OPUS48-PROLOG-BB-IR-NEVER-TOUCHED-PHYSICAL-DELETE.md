# HANDOFF — 2026-06-13 · Opus 4.8 · Prolog BB — IR-NEVER-TOUCHED: physical deletion

## Watermark
SCRIP `0f6506b` · .github `(this commit)` (both build green).
**m2 114/115 · m3 83/115 · m4 83/115.** Ratchet floors UNCHANGED (m3 83 / m4 83). No score movement — this was a code-hygiene / rule-enforcement session, not a feature session.

## Gates
GATE-1 5/5/5 ✓ (HARD m2 gate intact). GATE-3 m2=114, m3=83, m4=83.
SNOBOL4 7/7/7 ✓ · Icon m2 12 / m3 12 / m4 12 ✓ (shared `bb_common.h` / `rt.h` / `emit_term_build.cpp` touched — verified no other-language regression).

---

## Lon's directive
"PIVOT! Ensure that the IR is NEVER TOUCHED in mode 3 or mode 4 … DELETE any code that does so and stub out the call sites with a `(*(char*)NULL)` bomb. Ensure the code is physically removed from the file." Clarified: emit *reads* IR once (to produce the m3 image / m4 `.S`), but the IR is never touched *during execution* of the m3 binary or m4 binary.

## What the prior session left (the gap this session closed)
The 2026-06-13 GZ-eradication session **bombed** the IR-walkers (turned their bodies into `*(volatile char*)0` null-derefs) but left the dead bodies and their emit-sites **physically present and compiling**. The bomb stub `rt_node_to_term_ptr` still existed, and `emit_term_from_node_bin` still baked a live `IR_t*` address as a `.quad` into the m3/m4 BINARY arms of bb_list/bb_term_inspect/bb_term_io. So the *mechanism* for an IR pointer to escape into a running binary was still in the source — it just pointed at a bomb.

## What was done this session (physical removal)
Net **−232 lines** across 7 files (`0f6506b`).

### Deleted from `src/interp/IR_interp.c`
1. **`rt_node_to_term_ptr`** — took a live `IR_t*` and (formerly) converted it to a Term at runtime. Was already a bomb stub; now gone entirely.
2. **`rt_is_eval(void *lhs_bb, void *rhs_bb)`** — cast both args to `IR_t*`, called `resolve_arith_eval(rhs)` (recursive IR-graph walker) at runtime. **Zero callers** (only an `rt.h`/`bb_common.h` decl). Deleted.
3. **`rt_throw(void *alpha_ptr)`** — cast to `IR_t*`, called `resolve_node_to_term(alpha)` on the IR node at runtime. **Zero callers**. Deleted. (KEEP: `rt_throw_term(void *ball_v)` — operates on a `Term*`, not IR; this is the real throw path.)

### Deleted from `src/emitter/emit_term_build.cpp`
4. **`emit_term_from_node_bin`** — the root emit-site. Baked `(uint64_t)(uintptr_t)nd` (a live compile-time `IR_t*`) as a `.quad` literal + a call to `rt_node_to_term_ptr`. This was the *only* mechanism by which a live IR pointer entered a running binary. Deleted.

### Declarations removed
- `bb_common.h`: `rt_is_eval`, `rt_node_to_term_ptr`, `rt_throw`, `rt_findall`, `emit_term_from_node_bin`.
- `rt/rt.h`: `rt_is_eval`, `rt_findall`, `rt_catch`, `rt_throw`.

### BINARY arms stubbed to `x86_bomb`
These template files had MEDIUM_BINARY arms that called `emit_term_from_node_bin`. Each helper deleted; the BINARY dispatch now returns a single loud `x86_bomb`:
- **`bb_term_inspect.cpp`**: deleted `bti_bin_functor`, `bti_bin_arg`, `bti_bin_univ_tt/t1/1t` + `bti_bin_ports`. BINARY → `x86_bomb`. TEXT arm untouched (uses `emit_build_compound_term`, which reads IR at EMIT time — legal).
- **`bb_term_io.cpp`**: deleted `btio_bin_numbervars`, `btio_bin_term_to_atom`, `btio_bin_format_b/a` + `btio_bin_ports`. BINARY → `x86_bomb`. TEXT arm untouched.
- **`bb_list.cpp`**: `bls_bin_alc` and `bls_bin_sort_term` bodies → `x86_bomb` (they called `emit_term_from_node_bin`). `bls_bin_sort_scalar` (no IR-ptr bake) **untouched** — still a live BINARY arm.

## Completion proof
```
grep -rn "rt_node_to_term_ptr"   src/ --include=*.{c,cpp,h}  → 0
grep -rn "rt_is_eval"            src/ --include=*.{c,cpp,h}  → 0
grep -rn "\brt_throw\b"          src/ --include=*.{c,cpp,h}  → 0
grep -rn "emit_term_from_node_bin" src/ --include=*.{c,cpp,h} → 0
```

## The standing invariant (audited green this session)
**No IR access during m3 or m4 *execution*.** The ONLY remaining IR-graph walk in the runtime library is `bb_reset` + `IR_interp_once` inside `interp_exec_builtin` (resolution.c:876–877) — and that IS the mode-2 interpreter, reachable only via `--interp`. Proven: no GZ template (`bb_cell_*`), no `emit_bb.c`, no `emit_core.c`, and no GZ-emitted m3/m4 binary calls `interp_exec_builtin` / `IR_interp_once` / `resolve_invoke_var_goal` / `resolve_arith_eval` / `resolve_node_to_term` (grep == 0). Emit reads IR once to produce the image/`.S`; the produced binary never touches IR.

## Reference: globals by phase (for next session)
**m3 RUNTIME (RX-slab execution):** `g_resolve_trail`, `g_resolve_env`, `g_resolve_bfr`, `g_resolve_cut_flag`, `g_resolve_cut_barrier`, `g_resolve_cp_stamp` (all resolution.c); `g_resolve_mark_stack`/`_top`, `g_rt_pl_nb`/`_n`, `g_meta_compat` (unification.c); `ATOM_DOT`/`NIL`/`TRUE`/`FAIL`/`CUT` (prolog_atom.c).
**m4 EMIT (`.S` generation only):** `g_emit`/`_` (emit_globals.c); `g_gz_no_struct_ptr`, `g_gz_visiting`/`_nvisiting` (scrip.c); `g_pl_catch_nodes`/`_n` (emit_bb.c); `g_flat_node_id`, slot/frame flags (emit_bb.c); `g_sm_native_unsupported`, `g_strtab_n`, `g_visited`/`_vcount` (emit_core.c); `g_resolve_bb_table`/`_count` (read by `resolve_emit_callee_block_body` to emit callee bodies); `g_stage2` (sm_prog.c). Zero overlap — m4's produced binary links its own fresh runtime-global copies in `libscrip_rt.so`.

## Next session
Open work is unchanged from the GZ-ONLY pivot handoff (GROUP B rungs B2 catch/throw, B3 retract, B4 abolish, B5 DCG; remaining dead-code demolition of `resolution.c` control engine + `resolve_bb_env_*`). This session added no new debt and removed standing IR-at-runtime debt. The bombed BINARY arms (term_inspect/term_io/list compound-term paths) are the same rungs already on the m3 "PATH BACK" list — they return when rewritten to emit term-build instructions instead of baking IR pointers.
