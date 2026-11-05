# The collector: the reference

Verified 2026-11-01 against SCRIP 9cb24d2ca. Consolidated from ARCH-GC-COMPILE-TIME-FRAME-MAPS (sections 0-18) and ARCH-GC-PINNED-ALLOCATOR-LIFETIME-CLASSES, both retired; `.github/RETIRED-ARCH-PAGES.tsv` reads either at its last commit.

## 1. The source map

- `src/runtime/rt/gc_heap.c` and `gc_heap.h`: the heap, the allocator's C side (`c_rt_gcheap_alloc`, `rt_heap_out_of_memory` for error 204, 306 or 307), the chain walk in C (`gc_visit_segment`, `gc_sw_run`, `gc_sw_chain_frame`, `gc_sw_frame`, `gc_chain_find`, `gc_walk_words`, `gc_cell_visit`), `rt_gc_frame_maps_add`, `rt_gc_root_range_add`, `rt_gc_visit_descr`.
- `src/runtime/rtx/rtx_alloc.s`: the allocator fast paths (`rt_gcheap_alloc`, `rt_str_alloc`, `rt_agg_alloc`) and the mark run (`rt_gc_mark_run`, `gc_wl_drain`). `src/runtime/rtx/rtx_gc.s`: `gc_collect_ex` and the runs (`rt_gc_first_dead_run`, `rt_gc_prefix_run`, `rt_gc_fix_run`, `rt_gc_slide_run`, `rt_gc_start_compact_run`, `rt_gc_ssum_run`, `rt_gc_trail_run`, `rt_gc_clear_run`, the root runs `rt_gc_core_roots_run`, `rt_gc_trail_roots_run`, `rt_gc_proc_roots_run`, `rt_gc_flags_roots_run`, `rt_gc_ptr_fields_run`, `rt_gc_loc_list_run`, the chain steps `rt_gc_site_find_a`, `rt_gc_sw_links_a`, `rt_gc_sw_step_a`, the spine reader with its `.Lsw_reject` loop).
- `src/runtime/rt/gc_slot_table.c` and `.h` (`gc_slot_row_t`, `gc_run_t`, `gc_sfield_t`): the heap validator's per-type slot table, cut from the struct declarations by field name; `gc_audit_b.c`.
- `src/ir/gc_frame_map.h` (the map format), `src/planner/frame_layout.c` (the layout quads), `src/emitter/emit.cpp` (`gc_site_rule_pick`, `emit_gc_site_new`, `emit_gc_site_play`), `src/templates/x86/x86_gc.cpp`, the generated `gc_allocating_table.inc`.
- Co-expressions: `src/runtime/rt/rt_coexpr.c` (`scrip_coctx_t`, `park_rbp`). The Prolog trail: `rt_pl_trail.c`.

## 2. The site rules (a site entry is `{pc, w = kind | rule << 16 | depth << 32, third, anchor}`, 32 bytes, CTO-509)

The third quad is the mask: rule 0 and 4 inline to 512 bytes of depth, else a byte offset into the pool after the entries; rule 1 and 2 pool offset | NW << 32. Bit w names the word at R + 8A - 8(w + 1), A the fourth quad (the run base's distance from R in words: depth / 8 at rule 0 and 4, dk / 8 at rule 1 and 2, 0 where the site declares no cell), w = 0 the oldest word of the run. `gc_site_ent_t` (gc_heap.c) and `rt_gc_site_find_a` (rtx_gc.s, shl 5) read the 32-byte stride; the table is `quads = 4 + 4n + pool`.

Kinds: 1 CALL, 2 LANDING, 3 RES, 4 MATCH_ENTER, 5 MATCH_LEAVE, 6 FN_EXIT, 7 RET_ROAD. R is the address just above the return slot the call pushed.
- **0** the rsp regime: base = R + depth, depth = E + K (the plan's entry depth and the encoder's tracked distance); carries the mask.
- **1** the rbp regime: base = rbp, depth 0.
- **2** a flat generator frame addressed down from rbp: base = rbp - depth.
- **3** a pattern blob frame: base = rbp, depth 0; kept apart so the match's inner sites read it.
- **4** the rsp regime inside a realigned region (`and rsp, -16` with the old rsp saved at `[rsp]`): base = the word at R + depth.
- **5** UNKNOWN depth (the encoder lost the distance): the chain stops and the stop is refused by name. A rule 5 site in a graded witness is the finding; zeta-layout step 3 makes rule 5 cease.
- **6** a site inside a pattern match: kind bits carry the nesting level and the owning enter's kind; depth is the enter's recorded depth.
- **7** hop only: a RET_ROAD (`add rsp, n; ret`) or the default FN_EXIT; **8** FN_EXIT whose link record is the caller's return slot; **9** SHIM-SELF, a site inside a shim frame named by its distance from R.

## 3. The heap and the compactor

- Every block is a 16-byte header plus a payload rounded to 16. Heap interiors are typed visitors by block type (descriptors, arrays, data instances, Prolog database and trie blocks); `gc_slot_table.c` is the validator's independent reading of the same layouts.
- The arena is a contiguous reservation (`mmap PROT_NONE`) up to the declared cap: the heap does not extend past it (Lon 2026-09-21: "Place a hard cap on the GC HEAP. Do not extend it." CEO-1101); memory inside the cap is committed lazily.
- The compactor (Lon to hq_runtime 2026-10-15: "We want to ensure a GC algorithm that is exact with no guessing."): LIVE and START bitmaps, one bit per granule (START set by the allocator beside the header store); MARK finds a pointer's header as the highest START bit at or below it; PREFIX gives each block's destination as the live bytes below it; FIX rewrites each recorded slot from PREFIX and a popcount; SLIDE moves each maximal live run with one `rep movsq`; RESET clears LIVE. No header is written for forwarding; no FILL gap is left on the plain road. The plants (shift, flip, forced relocation) stay on their C road behind their knobs.

## 4. The proof of a collector landing

The row's DONE-WHEN plus: the gc witnesses the change can reach in both modes, plain and under `SCRIP_GC_STRESS=1` and `3` and `SCRIP_GC_CHAIN_CHECK=1`, outputs byte-identical to their refs; the collection-identity proof, `SCRIP_ZETA_TELEM=1`'s per-collection regeneration lines (blocks, bytes, reclaimed, slots, marked, forwarded) identical between a control worktree at the parent and the landing; the instruction count of one witness before and after (`util_instr_count.sh`); the eight smokes. The heavy gc passes (`make test-arena`, `util_gc_acceptance.py`) are the coo's.

## 5. Debugging a collector red

1. Confirm it is the collector: the program is green plain and red under `SCRIP_GC_STRESS=1`; then `SCRIP_GC_PLANT_FLIP=1` turns a stale pointer into a located fault (filter `[GC-` lines before diffing).
2. `SCRIP_GC_CHAIN_CHECK=2` names a chain that stops short; dump the live stack's site pcs to locate a frameless stop.
3. A poll that DIFFs in every configuration names a reclaimed root, not a moved one; `ZGC-STALE` in an asm leaf after a C call is a clobbered register.
4. Trace a slab chain with a gdb Python stepper, then put a watchpoint on the corrupted word. Bound memory with a cgroup.

## 6. Retired designs a reader of old receipts meets

The marker cell (`DT_MAP`, `emit_gc_map_cell`, `gc_walk_cell`), the stack ceiling machinery (`rt_gc_emit_ceiling_adopt`), the stale-frame plant and the conservative word scan (`gc_zeta_frame`) are deleted (§ 13.2 of the old page). "Maps found by the frame's cell, never by a return-pc table" (the 09-18 freeze) was superseded by the chain keyed by return pc (CEO-1492). The retry at the site (`DT_RETRY`, a re-issuable builtin re-called after a collection at the cap) was designed on 2026-10-14 and its row retired as cannot-measure; nothing of it is built.
