# FINDING 2026-09-23 (cto) — the eight routed reds of CEO-1161: five cured, one instrumented, two declared; the grew column over 58 witnesses; the shift plant's arithmetic

Tree: SCRIP 89956530b at session start, landings 9ae694007 2e50595ae 25110f402 87ace0aa4 9d3603aa2 2305822d1 a57f0b10e. Every claim below is folded into GOAL-CTO.md CTO-140 and the chop baton; this file is the evidence and may be deleted.

## 1. The grew column, measured (232 receipts at 64 KB, 116 at 128 and 256)

Method: every file in `scripts/gc_witnesses` (58), `env -u SCRIP_HEAP_MB SCRIP_HEAP_KB=<n> SCRIP_GC_EXERCISE=1 SCRIP_GC_STRESS=<s>`, one receipt per cell.

| witness | grew@64 | grew@128 | grew@256 | collections@64/s0 |
|---|---|---|---|---|
| hb_apply_opens_and_lands.sno, hb_blob_span_defer.sno, hb_defer_subject.sno, hb_deferexpr_d_dupl/replace/substr/trim.sno, hb_dvec_sort_match.sno, hb_eval_names.sno, hb_mkexpr_unmapped_spine_store.sno, hb_nested_match_outer_subject.sno, hb_wsb_eval_define.sno | 132 | 132 | 0 | 2 (dvec_sort_match 57, wsb_eval_define 12) |
| hb_file_name_unrooted.icn | 204 | 136 | 0 | 9 |
| hb_coexpr_create.icn, hb_coexpr_sigma.icn | 64 | 0 | 0 | 7 / 8 |
| hb_pldb.pl, hb_pl_findall.pl, hb_pl_root_cells.pl, hb_wsb_pl_atom_dup.pl | 56 | 0 | 0 | 1 / 3 / 8 / 1 |
| hb_bignum_length.icn | 16 | 0 | 0 | 50 |
| hb_dvec_list.icn | 4 | 0 | 0 | 36 |
| hb_arena_grow.sno (by design) | 2008 | 1944 | 1816 | 2614 |
| the other 36 | 0 | 0 | 0 | — |

hb_plj_batch_b.pl prints no receipt at 64 KB (crashes or refuses at every stress). The 13 SNOBOL4 rows read `bytes` about 185 KB live after collection: no window at or under 128 KB is a true label for them. Of the cto's nine gates: seven arms ran at a false 64 KB label (hb_mkexpr_unmapped_spine_store.sno is the witness of three of them). The receipt column (arena_kb, grew, collections) is owed in `util_arena_pin_census.py` and on the nine ARENA lines (coo agreed, 2026-09-23).

## 2. The eight reds by header, what each was

| gate | reading | class | landing |
|---|---|---|---|
| allocating_set table | ONLY_CENSUS=26 (Pascal allocators) | regeneration | 9ae694007 |
| descriptor_kind_sets | DT_E in gc_visit_one only (hq_icon 39c510f22) | regression, cured in the four spellings | 2e50595ae |
| safe_point_stores (REPORTED) | five Prolog witnesses unread_static +9 each (hq_prolog 6a6983d9e bb_call.cpp), one witness arrived | re-baseline with attribution | 25110f402 |
| callee_saved arm 5 | copy residual 293 vs 289: w.pas +11 (the cto's relop rec_sigma reload, 2344d2dc7), w.icn −7 | the cfo's CEO-973 table row (CEO-1164); ceiling untouched | — |
| no_layout_entry | consumer refused rc=2 at the fake root (coo's 0176b35dd build-currency guard) | instrument, fake root made a built tree | 9d3603aa2 |
| caller_saved_spill_block (REPORTED) | 1476 detections slot 5, 134 unrepaired, no site | instrumented: graph= line= site= | 87ace0aa4 |
| coexpression_roots | parked@3 sigma@1 SIGSEGV inside gc_collect_ex memmove | shift plant arithmetic, cured; arms 3 and 5 stay red (plant drift) | 2305822d1 |
| mark_walk | rc=134 heap exhausted at the 4096 KB cap, 87011 blocks live | declared pin 256 MB | a57f0b10e |

## 3. The shift plant's arithmetic

`gc_plant_shift_bytes` tested `g_hp_end - g_hp_top > shift` only. Each shift leaves an HB_FILL block at the arena base; `gc_plant_shift_prefix` sums them; after eighteen 4096-byte shifts the prefix was 73728 and the compacted live set was placed at arena+prefix+shift, past a 128 KB committed window: memmove into an uncommitted page, gdb dest arena+132736. The plan now sums the marked live bytes first and declines when arena+prefix+shift+live > g_hp_end (printed once with the numbers). Twelve witness runs (three coexpr witnesses × stress 1/3/5/8) MATCH with the plant still applying 1–2 times each.

## 4. rtccb, where

With `SCRIP_GC_MAPS=1`, `[GC-RTCCB-STALE] ... graph= line= site=`: hb_nv.sno line 3 (`$('VAR' I) = 'value' I`) 80 unrepaired type-2 + 16 swept type-215 + 16 unrepaired type-0; hb_dvec_sort_match.sno line 27 (`'xxabcyy' *(BREAK('a') . W5 REM . W6)`) 119 unrepaired type-221; PAT$1 line 23 one swept. Mode-4 asm for those witnesses: polls sitting between `mov [rtccb+40], r8` and its reload after str_concat_d, NV_SET_fn, rt_defer_open_entry, rt_dcap_end_ok_open (12 such sites in hb_nv, 12 in hb_dvec_sort_match). The cfo's ruling stands: rtccb is caller-saved scratch; the cure per site is the poll form that re-derives r8 after the poll.

## 5. Not mine, routed

`make preflight` reads one red on HEAD that predates this sitting: `test_gate_c_allocators_are_eradicated_and_say_where_they_went` arm d, forbidden_total 0 → 11 (malloc 3, free 8) in by_name_dispatch.c (8), bb_pool.c, ct_arena.c, gen_runtime.c; this seat's diff adds none. The postoffice `test_gate_dispatch_gc_safepoint_inline` crash is callgrind-specific: string_manip.sno at N=20000 compiled in mode 4 runs rc=0 natively at MB=1 and at the default.
