# ARCH-RUNTIME-GLOBALS-INVENTORY — every global the runtime holds, asked the one question: can it live on one of the three zetas?

**Lon 2026-10-08 15:4x–16:0x CDT, in-chat to the ceo, verbatim:** *"Take an inventory of all global variables use at runtime. Ask the question, can that global live on one of the 3 ZETAS? If so make a task to move it and remove the global variable."* · *"Regarding the global variable census, do not consider the parser code, nor the lower nor the emitter for now. Just the runtime."* · *"Do all the global variables start with prefix "g_", if not, make it so."* · *"One idea is to collect all the globals into a structure, just for housekeeping. You could put all the parser globals, lower globals, emitter driver globals, template globals (g_emit), in SEPERATE global structs. g_parser, g_lower, g_emitter, g_template."* Ruled CEO-1561. The instrument is `SCRIP/scripts/audit_runtime_globals_census.py` (nm -l over `out/libscrip_rt.so`; `--list`, `--file F`, `--all --max N`, `--gone NAME...`, `--prefix`, `--tree runtime|compiler`); every number below is its reading at SCRIP `cfb6fde7e` (2026-10-08 16:0x CDT) and is re-measured, never quoted.

## 1. The population

659 writable data symbols defined under `src/runtime/`: 478 file-scope globals and 181 function-scope statics (a `name.NN` symbol), in 25 translation units; 4.06 MB, of which `g_zsm` (runtime_init.c, 3 MB) and its six 16 KB `g_zsm_tr_*` tables are a diagnostic shadow, `rk_case` (114 KB) a case-folding table, and two `acc_types`/`acc_names` function-scope buffers 65 KB and 49 KB. 111 of the 478 file-scope globals do not start with `g_`.

| file | symbols | file-scope | what they are |
|---|---|---|---|
| rt/gc_heap.c | 183 | 141 | the collector's registers: the arena, window, cap and line (`g_hp_*`), the mark worklist, segments, maps, site tables, chain statistics and reports (`g_gc_*`), the GW diagnostics (`g_gw*`) |
| core/core.c | 110 | 90 | the monitor session (`monitor_*`, `g_trace_*`, `g_comm_dbg`), the SNOBOL4 keywords (`kw_*`), the DATA registry (`_data_types`, `_ctor_fns`, `_facc_*`), the variable table and NV memo, the error voice and errjmp chain, I/O channels, the DUMP walk, the Icon `&error` trio |
| by_name_dispatch.c | 89 | 44 | the Pascal heap (`g_pas_*`), TAP state, Prolog flags, Raku inline caches (`g_ctor_ic`, `g_field_ic`), the dispatch tables (`g_dtax*`, `g_bn_direct`, `g_bidprof*`), main args, two chain heads (`g_redisp_cur`, `g_rk_cbh_cur`), the `tr` map cache `g_rm` |
| keywords.c | 41 | 29 | the SNOBOL4 keyword cells (`g_error g_trace g_dump g_random g_anchor g_maxlngth g_stno g_stcount g_line g_file …`), the keyword cset registry, `g_kwb` |
| rt/rt.c | 40 | 24 | the call protocol (`g_call_args`, `rt_g_ret_by_name`, `rt_g_want_name`, `rt_k_level`), the procedure registry and its caches (`g_cell_cache`, `g_proc_idx_*`, `g_proc_hsl`), the generator chain head `g_genp_head`, `g_gva_mapped` |
| pattern_match.c | 36 | 21 | the match's own state: the deferred cells `g_sno_defer_cells` (32 KB), the rsp deltas `g_rspd_*`, the capture name cells `g_dcap_nv_*`, `g_cap_gen`, the CAS base `g_dcap_base` |
| runtime_init.c | 29 | 24 | the ZSM diagnostic shadow (`g_zsm`, `g_zsm_tr_*`, the violation counters) and the ZDP anchors |
| rt/prolog_atom.c | 26 | 23 | the atom and functor tables and their hashes (`atom_names ht functors fht opcols …`), the five `ATOM_*` ids |
| runtime_eval.c | 16 | 11 | the EVAL cache, the label table, the eval call-frame chain head `g_eval_cfr`, `g_eval_ret_v` |
| rt/bbprof.c | 16 | 15 | the profiler: `g_pcs` 32 KB, `g_altstack` 64 KB, the sample tables |
| snobol4_system_fns.h, builtin_ids.h, rk_case_table.h | 19 | 19 | tables defined in HEADERS, so each including TU carries its own copy (`g_sn4_system_fns` ×4, `g_sn4_leaf_fns` ×4, `g_bid_tab` ×3, `rk_case`) |
| builtins/gen_runtime.c | 12 | 12 | the Icon scan state (`scan_subj`, `scan_pos`, `scan_depth`, `g_scan_subj_*`, `g_scan_needle_*`), the generator drive (`drive_node`, `drive_val`), `bb_rnd_seed`, `g_root` |
| rt/rt_coexpr.c | 10 | 9 | the current co-expression `scrip_co_current`, the chain head `g_co_gc_head`, the main thread and root context |
| portcount.c, aggregates.c, core/stmt_exec.c, rt_runtime.c, rt/rt_slab.c, rtx/rtcc_init.c, unification.c, icn_extfn.c, string_ops.c | 28 | 24 | port counters, aggregate serials, the statement's subject/delta/omega (`Σ Δ Ω Σlen g_scan_pre_delta`), the current call (`g_ir_return_val g_cur_func g_current_cfg`), the slab allocator, the rtx callback block |

## 2. The answer, by class

The question is asked per global and the answer falls into five classes. **C and K can move now and each is a row; S is Lon's housekeeping struct, then the standing-block design; H and T stay by law.**

- **C — CONSTRUCT-LIFETIME: lives for one match, one call, one scan, one statement, one eval; it belongs in that construct's frame or spine cell (THE LIFETIME RULE) and the global is deleted.** The rows below name every one; the DONE-WHEN is `--gone` over the names.
  - pattern_match.c (the match frame): `g_sno_defer_cells g_sno_defer_pair_hwm g_rspd_beta g_rspd_g4 g_rspd_g5 g_rspd_g6 g_rspd_s2 g_rspd_save g_rspd_active g_dcap_nv_key g_dcap_nv_cell g_dcap_nv_seen g_cap_abort_gen g_scan_hit_start g_lf_type`, plus the dead `g_pat_main_rsp`.
  - core/stmt_exec.c and rtx (the statement/match frame): `Σ Δ Ω Σlen g_scan_pre_delta` (stored by `rtx_match.s` as dword/qword — the leaf learns a frame offset).
  - rt_runtime.c and rt.c (the call's frame): `g_ir_return_val g_cur_func g_current_cfg g_call_args rt_g_ret_by_name rt_g_want_name g_prim_val g_blob_fbv g_initial_fired`, plus the dead `g_last_ok`.
  - core/core.c (the statement or operation): `g_icn_op _x4_pending_parent_frame _command_pending_parent_frame g_dump_col g_cdobj g_dobj g_ndobj g_trace_value_last`, plus the dead `_vstop`.
  - builtins/gen_runtime.c (the IR_SCAN bank and the generator frame): `scan_subj scan_pos scan_depth g_scan_subj_len g_scan_subj_ptr g_scan_needle_len g_scan_needle_ptr drive_node drive_val`.
  - runtime_eval.c (the eval's frame): `g_eval_ret_v`.
- **K — A CONSTANT that is writable only by oversight: `const` puts it in .rodata and it is no longer a global variable at all.** `ucase lcase digits alphabet core_err_msgs` (core.c), `rk_case` (114 KB), `g_sn4_system_fns g_sn4_leaf_fns g_bid_tab` (header-defined, duplicated per TU — one `const` definition in one TU), `nulldesc` (icn_extfn.c), `pl_flags_init` (by_name_dispatch.c), the `ATOM_*`/`FUNCTOR_DOT2` ids once interning is at startup.
- **S — PROGRAM-LIFETIME STATE (the collector's registers, the keywords, the registries and caches, the monitor session, the I/O channels, the Pascal heap, the atom tables, the profiler, the diagnostics): the lifetime is the run, so by THE THREE ZETAS it is ζ-STANDING's.** Today the runtime has no base for ζ-STANDING: C code reaches each cell through its own symbol (mode 4 through the GOT), and the emitted code names the symbols. Lon's housekeeping word is the first step and a row: every S global of the runtime becomes a member of ONE struct `g_runtime` (sub-structs per subsystem: `.gc .kw .mon .io .data .proc .atoms .prof .diag`), so the runtime holds one global instead of ~330, every reader spells the member, and the symbol census reads the heads plus one. Whether `g_runtime` then lives IN ζ-STANDING (the root graph's frame, reached through a base register or one pointer; r12 is the CAS/trail island top, r13–r15 are the zetas' planes) is the follow-on design and Lon's word, not a row yet. The fixed tables inside S (`g_zsm` 3 MB, `g_zsm_tr_*` 6 × 16 KB, `g_ah_tb/tn`, `g_nv_memo_*` 3 × 16 KB, `g_cell_cache` 48 KB, `g_proc_idx_*`, `g_dcap_nv_*`, `g_ctor_ic`, `g_field_ic`, `g_dtax*`, `g_bn_direct`, `g_bidprof`, the `acc_*` buffers) are NO FIXED LIMITS debt and go through `ARCH-DYNAMIC-STORAGE.md` as they move.
- **H — A CHAIN HEAD or a single current-X cell, lawful under CEO-1542 (one cell, the nodes on the machine stack): `g_core_errjmp_stk g_core_errjmp_n g_icn_bi_top g_redisp_cur g_rk_cbh_cur g_genp_head g_eval_cfr g_co_gc_head scrip_co_current g_gc_top_graph`.** They stay, and each takes the `g_` prefix.
- **T — FUNCTION-SCOPE STATICS (181): the cached-getenv seams and once flags (`v.NN said.NN armed.N done.N tried.N diag.N live.N on.N`) are not globals by CEO-554 and stay; the BUFFERS among them (`acc_types.43` 65 KB, `acc_names.42` 49 KB, `acc_types.22`, `acc_names.18`, `map_cache.4` 6 KB, `tb.17` 4 KB, `g_rm.10` 1.5 KB, `g_tweak_none`) are S by nature and move with the struct row.**

## 3. The rows (minted 2026-10-08 16:1x CDT, CEO-1561; lanes by what each cures)

| row | lane | DONE-WHEN |
|---|---|---|
| `runtime-globals-every-file-scope-global-of-the-runtime-starts-with-g-lon-2026-10-08-ceo-1561` | hq_runtime | `--prefix` GREEN (111 red today) |
| `runtime-globals-the-matchs-own-state-leaves-pattern-match-c-and-stmt-exec-c-for-the-match-frame-ceo-1561` | hq_runtime | `--gone` over the pattern_match.c and stmt_exec.c C list |
| `runtime-globals-the-calls-own-state-leaves-rt-c-and-rt-runtime-c-for-the-call-frame-ceo-1561` | hq_runtime | `--gone` over the rt.c and rt_runtime.c C list |
| `runtime-globals-the-statements-own-state-leaves-core-c-for-the-statement-frame-ceo-1561` | hq_runtime | `--gone` over the core.c C list |
| `icon-runtime-globals-the-scan-and-generator-state-leaves-gen-runtime-c-for-the-scan-bank-and-the-generator-frame-ceo-1561` | hq_icon | `--gone` over the gen_runtime.c C list |
| `runtime-globals-the-constants-become-const-and-leave-the-data-segment-ceo-1561` | hq_runtime | `--gone` over the K list |
| `runtime-globals-the-program-lifetime-state-collects-into-one-struct-g-runtime-lons-housekeeping-ceo-1561` | hq_runtime | `--all --max 11` (the ten heads plus `g_runtime`) |
| `compiler-globals-collect-into-g-parser-g-lower-g-emitter-g-template-structs-lons-housekeeping-ceo-1561` | cfo | `--tree compiler --all --max 4` |
| `snocone-parser-stacks-the-counter-stack-pushcounter-family-becomes-a-native-stack-for-speed-two-ideas-ceo-1561` | hq_snocone | counter.sc defines no Snocone PushCounter AND `util_parser_grid.sh`'s BAR line reads every parser at C's clock and 2.00x SPITBOL |
| `snocone-parser-stacks-the-value-stack-shift-reduce-pushval-popval-becomes-a-native-stack-for-speed-two-ideas-ceo-1561` | hq_snocone | ShiftReduce.sc defines no Snocone Shift AND the same BAR |

The two parser-stack rows carry Lon's two ideas verbatim for the design: *"one to weave both stacks into a linked list style winding it way through the ZETAS, or growing lists dynamically within the ZETAS (tricky), and two consider two MMAP'd regions, one for the counter stack and one for the value stack."* The decision between them is measured on the parse clock and brought to Lon with the numbers before the massive roll-out (LARGE CHUNKS).
