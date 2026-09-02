# FINDING 2026-09-02 (ceo) — Prolog-only globals: 56 live (41 runtime, 15 compile-time), 9 dead, and what the last five days deleted

**Tree:** SCRIP `46db4457` · corpus `b5a3e4926` · .github `cd63c76c` · `RT_OPT=-O0` · MODE `CEO` (file read 2026-09-02).
**Asked by Lon in-chat to ceo 2026-09-02:** *"List all the global variables which Prolog uses that the other languages do not use. List the ones recently deleted."*
**Instrument (re-run it, never quote from memory):**
```bash
cd SCRIP && make -s && for o in out/rt_pic-*/*.o; do nm -S $o | awk '$3 ~ /^[BbDdC]$/'; done   # every writable data/bss symbol, defining TU
# classification: a symbol is PROLOG-ONLY when every non-extern reference in src/ sits in a Prolog-owned file (src/parsers/prolog/, lower_prolog.c, unification.c, resolution.c, rt_arena.c, rtx_plunify.s)
# or in a function named rt_pl_/plw_/plc_/dop_/pl_/resolve_/prolog_.  Emitted-code reach: grep -l '<sym>' corpus/benchmarks/*/*.s corpus/demos/*/*.s
```
Line numbers below are at SCRIP `46db4457`; they will drift, the names will not.

## A. Prolog-only globals that exist today — RUNTIME (live in `libscrip_rt.so`, touched while a program runs)

| group | globals | where | emitted code reaches it directly? (committed `.s` artifacts, prolog / snobol4 / icon) |
|---|---|---|---|
| **trail + env areas** | `g_pl_trail` (pl_trail_t: mmap area + `top` mark; `[g_pl_trail+32]` baked by `rtx_plcall.s` and `bb_define.cpp`), `g_pl_env_area` (pl_area_t, mmap, `pl_env_bump/mark/reset` from unification.c:568-580) | resolution.c:16, :48 | `g_pl_trail` 26/26 · 0 · 0 |
| **cut / active / marks** | `g_resolve_cut_flag` (set by `rt_cut_set`), `g_resolve_active` (polyglot_init, `_usercall_hook`), `g_resolve_mark_stack[]` + `g_resolve_mark_top` | resolution.c:14, :49; unification.c:583-584 | no |
| **exception** | `g_pl_throw_ball` (polled ball; C37 moves it into the catch box's β) | unification.c:2334 | no |
| **choice-point / retry stacks** (all `visibility("default")`) | `g_pl_retry`/`_top`/`_cap`; `g_pl_cp_stack`/`_top`/`_cap`; `g_pl_zf3_stack`/`_top`/`_cap` (3-word CP: trail-mark lo/hi + continuation, `rt_pl_cp_push3/pop3` are emitted calls) | rt.c:1722-1764 | via `rt_pl_cp_push3@PLT` / `rt_pl_cp_pop3@PLT` |
| **pending-resume cursor machine** (PZ-5 deletes) | `g_pl_zf_pending_cursor`, `g_pl_zf_pending_cursor_off`, `g_pl_zf_pending_tm_lo`, `g_pl_zf_pending_tm_hi`, `g_pl_zf_pending_tm_off`, `g_pl_zf_target_pcall_top` (consumed by `rt_jmp_frame_lexprep2`, rt.c:1698) | rt.c:1788-1793 | `g_pl_zf_pending_cursor` 23/26 · 0 · 0 (Prolog's γ polls it, `xa_flat.cpp`) |
| **arenas** | `g_pl_cterm_base/_cur/_end` (compiled-term arena), `g_pl_cellws_base/_cur/_end` (cell workspace), `g_plw_cellws_on` (env `SCRIP_PL_WS_RECLAIM`, default 0) | rt_arena.c:88-90, :131-134 | `g_plw_cellws_on` 26/26 · 0 · 0 (the `$trail_mark` sink, bb_call_fn.cpp:371) |
| **predicate tables** | `g_pl_pred_table` + `g_pl_pred_n` (static preds), `g_pl_dyn_pred_table/_n/_cap` (assert/retract), `g_plw_preds[512]` + `g_plw_pred_n` (α/β address table for call/N — ⚠ read by `icn_builtin_is_known` too, a cross-language leak), `g_plw_poison` | unification.c:601-602, :1918-1920; by_name_dispatch.c:80, :91 | no |
| **dispatch-side state** | `g_plw_dot_sl` (the `'.'` functor slot), `g_plw_cwp`/`_n`/`_cap` (cell/arena mark pairs), `pl_wot_stk[32]` + `pl_wot_sp` (with_output_to), `g_plw_unwind_floor` + `g_plw_floor_bypass` (the dead-C-stack floor, 16 sites, P7's gate names them for deletion) | by_name_dispatch.c:118, :175, :1081-1082, :1481-1482 | `g_plw_dot_sl` 11/26 · 0 · 0 (`sink_ix_g`, `sink_unify_lst`); floor via `rt_plw_floor_bypass_on@PLT` |
| **value services** | `g_pl_copy_slot_mode`, `g_pl_copy_slot_ctr`, `g_pl_functor_slot_ctr`, `g_rt_pl_nb` + `g_rt_pl_nb_n` (nb_setval store), `g_pl_flags[]` (prolog_flag table) | unification.c:1750-1751, :670, :1862-1863, :2185 | no |
| **rtx gate** | `rtx_gate_plunify` (1 byte) | rtx_plunify.s | no |

**Shared globals that only Prolog's emitted code addresses directly** (not Prolog-owned, listed because the compiled Prolog program is the only compiled program that touches them): `g_zeta_mode` (zeta_alloc.c:145, the constant `ZC_ZETA=1`; the `$trail_mark` sink compares it to 2 at run time, bb_call_fn.cpp:375 — 26/26 · 0 · 0; a mode switch surviving under ZETA HAS NO MODES), `g_hp_fr` (11/26 · 0 · 0), `g_gc_pending` and `g_call_args` (18/26 · 0 · 3/20 — Icon reaches them too, so not Prolog-only).

## B. Prolog-only globals — COMPILE-TIME (compiler state; some are parked in the runtime `.so` because the TU is linked there)

- `lower_prolog.c`: `g_pl_det_v[]` (96 KB), `g_pl_det_n`, `g_pl_det_done`, `g_pl_disj_ctr`, `pl_ll_ctr`, `g_pl_nl_arith[]`, `g_pl_nl_builtins[]`; function-scope statics at :15 (`cache[1024]`, `buf`), :21 (`buf[264]`), :717 (`cache[64]`, `buf`), :758 (`on`, env `SCRIP_PL_BOUNDED_DUMP`), :1086 (`nmbuf`), :1395-1397 (`pl_init_goals_acc[]`, `pl_init_ngoals_acc`, `pl_init_main_pi`).
- `resolution.c:50-51`: `g_resolve_bb_table[]` (**268 KB of bss in the runtime**) + `g_resolve_bb_count` — the name→bb_idx registry; written and read only by `lower_prolog.c` (compile time). Nothing reads it at run time.
- `prolog_atom.c`: `ATOM_CUT/DOT/FAIL/NIL/TRUE`, `atom_names`, `atom_len`, `atom_cap`, `ht`, `ht_size`, `ht_used`. `prolog_parse.c`: `BIN_OPS`, `g_uinfix/_n/_cap`, `dcg_var_counter` (:289), `PL_PRELUDE_SRC`, `arith`. `prolog_lower.c`: `g_pb_fresh_ctr`, `pj_dir_seq` (:526).
- `polyglot.c:17`: `g_fi8_pl_init_count` — written (`++`), never read.

## C. DEAD today (definition is the only reference in `src/`; deletable without a behaviour change)

`g_pl_yield_seq` (rt_runtime.c:246) · `g_resolve_b3_call_mark` (:55) · `g_resolve_tail_redirect_cfg` + `g_resolve_tail_redirect_entry` (:53-54) · `g_halt_rc` + `g_halt_set` (runtime_init.c:9-10) · `g_pl_catch_nodes[]` + `g_pl_catch_n` (emit.cpp:3746-3747) · `g_fi8_pl_init_count` (write-only).

## D. Recently deleted (git log since 2026-08-28, removed file-scope definitions)

| commit | date | globals removed |
|---|---|---|
| `46db4457` struct Term deleted (Lon's order) | 09-02 | the whole second CP/trail/catch machine (ARCH § 4 row T7): `g_resolve_trail` (Trail), `g_resolve_bfr`, `g_resolve_cut_barrier` (resolve_choice *), `g_resolve_cp_stamp`, `g_resolve_catch_stack[]`, `g_resolve_catch_top`, `g_resolve_exception` (Term *), `resolve_cp_stack[]`, `resolve_cp_top` (resolution.c); `g_resolve_nb[]` (rt_runtime.c); the `extern int ATOM_*` declarations of `term.h` (definitions stay in prolog_atom.c) |
| `663b47b0` P7a | 09-02 | no global deleted — `dop_call`'s `setjmp(g_core_errjmp_stk[..])` + `g_core_errjmp_n` push/pop removed; those two globals are SNOBOL4/Icon's and stay |
| `804f3d6f` T9 m5 | 09-02 | `_aid_plus/_minus/_times/_div/_mod` (prolog_builtin.c deleted with them) |
| `5b6b51de` | 09-01 | 13 `pj_*` statics in the two dead `.bak` sources (never built) |
| `df8f5473` T9 m1 | 09-01 | `fails` in the deleted orphan bridge test |
| `5c443f05` ζ phase-2 eradication | 08-29 | `zeta_heap.c` and its 18 `g_zh_*` statics (base/cur/cap/tab/free/birth/allocs/deads/slides/slid_bytes/pin_holes/telem/atexit/mu) — the s272 "workspace island" frame store, shared ζ state, not Prolog-named |

Not Prolog's, for the record: `g_exec_prog`/`static_tab`/`static_n` (72b3e4b1, AST walker), `g_core_err_stmt` (b5c64f86, core), `g_platform` (08-2x).

## What this says for the redesign (ARCH-PROLOG-THREE-ZETAS.md § 4 already names most of A as rungs; this census is the complete denominator)

Byrd boxes carry their stacks and lists INSIDE the box (Lon, ARCH § 21). Every row of A is state that a box should own in its ζ-ACTIVATION-FRAME or that should not exist: the trail and env areas (P10), the three CP/retry stacks and the pending-resume cursor (PZ-2, PZ-5), the throw ball (C37), the floor (P7), the `'.'` slot and the `g_zeta_mode` compare in `$trail_mark` (a ZETA-HAS-NO-MODES violation, one `cmp` to delete). B and C are compiler-side or dead; the 268 KB `g_resolve_bb_table` belongs to the lowerer, not the runtime image.
