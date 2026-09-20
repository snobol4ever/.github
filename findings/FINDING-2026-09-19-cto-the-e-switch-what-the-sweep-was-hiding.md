# FINDING 2026-09-19 (cto, CTO-90): THE E SWITCH -- what the conservative sweep was hiding, measured holder by holder

Row: gc-the-collector-walks-the-rbp-chain-keyed-by-return-pc-visits-only-mapped-slots-and-coexpression-stacks-are-mapped-frames.
Branch: cto/e-switch-2026-09-19 (SCRIP 2337cd14a on origin/main 2be0f91a2). Every claim below is folded into the row's LEDGER and
the GOAL-CTO.md LIVE CURSOR in the same landing, because Lon deletes FINDINGs periodically (CEO-859).

## The instrument

Under E the collector has no raw arm: a spine word is visited only as a DESCR cell read by its tag byte with a per-kind
block check, or as an interior slot the graph's sealed kind table names DESCR or PTR_GC. So every holder the sweep found
BY VALUE reads as a crash or a wrong answer at SCRIP_HEAP_MB=1 SCRIP_GC_STRESS=1,3,5 -- the battery of 26 GC witnesses in
both media is the instrument, and each red was taken to its holder with gdb (a hardware watchpoint on the block's first
word names the poll that freed it) and the walker's own site lines (SCRIP_GC_MAPS=1..3).

## The holders, each measured red then green on one tree

1. The Prolog standing cells at [r14 - 24 - 8k] sat ABOVE the ROOT map cell, in the header the walker reports and never
   visits; k >= 2 overwrote the cell itself. Cure: FLAT_FRAME_ALLOWANCE_ROOT (80) -- the ROOT graph's cell moves into the
   Prolog quad's spare pair [kt-80, kt-64) and emit_gc_map_data seals the cells (and the alignment pad, RAW) as one
   PTR_GC entry [region, map_off). hb_pl_findall kt 272 -> 256, cell +176, entry off=160 PTR_GC 16.
2. rt_pl_dop_findall_new returned the accumulator (an HB_DVEC) as INTVAL(pointer): a DT_I the typed visitor reads as an
   integer. gdb: rt_pl_findall_collect read n=18446744072496854966 from poison. Cure: the DT_DATA/DATA_ELEMS_SLEN carrier
   (pl_fa_handle/pl_fa_of), and the carrier arm in gc_cell_visit gated on gc_block_exact(HB_DVEC). The census of
   INTVAL-wrapped pointers in the runtime found exactly this site.
3. C-built descriptors set only the tag BYTE (DESCR_t.v); emitted stores write 32 bits. The DT_P cell holding the ARBNO
   pattern block read 0x0000000055556408 in its first word -- tag 0x08 with stack garbage above it -- and gc_cell_visit
   refused any tag word with nonzero upper bytes. Watchpoint: dtp_new allocates, the very next return poll frees. Cure:
   the padding gate is deleted; the per-kind block checks were always the discriminator. Cleared hb_dvec_sort_match,
   hb_datblk, hb_eval_names, hb_dvec_data_convert together.
4. rk_write/rk_writes built their argument array with rt_ws_alloc_descr and handed it to rt_call_arr("write"): the
   by-name entry poll shields the descriptors INSIDE the array, never the block, so `say "hello"` printed an empty line
   at stress 1. Cure: stack VLAs there and in the two multi-method roads of the same shape.
5. g_redisp[].self and .args[] were unrooted across the method's execution: bnd_gc_roots().
6. gc_visit_one's DT_N arms dereferenced unchecked targets ({DT_N, 1, ptr=1} in a DESCR-kinded interior slot crashed the
   walker on hb_bignum_length): both arms now verify the target as the deleted sniff did.
7. A co-expression thread carries the creator's frame image TWICE, both with main's ROOT flag; the copied spine between
   them held live tagged cells and was classified above-root. Cure: a ROOT cell ends a segment only when no frame follows
   it ([GC-WALK-CELL] under SCRIP_GC_MAPS=2 is the print that showed it).

## What is not E's, measured on a clean worktree of origin/main 2be0f91a2

- The cfo's c2e82f161 (the five defer polls) keeps rax and rdx as raw words BELOW the floor its record hands the poll; at
  the open/land return rax is the DTP when rdx==4. hb_dvec_sort_match rc=139 at 1 MB stress 1 ON MAIN WITH THE SWEEP, and
  the cfo's user_function_eval_arbno_replace_branch_2 prints 1 of its 10 ref lines there. Cure shape telegrammed (the
  protocol-decided tag in the shield array).
- hb_pl_root_cells reads 3-1-1-1-1 on main at stress 0 with the overlap cured: a dynamic predicate's first enumeration under
  a findall that follows another dynamic predicate's findall yields one solution (eight-program bisection in the row's QA).
  The Prolog road, telegrammed to the ceo.
- gc2 prints &collections: 0 of 3 byte-identical at 1 MB on main and on E alike, 3 of 3 at 512 MB -- the gate pins its arena.
