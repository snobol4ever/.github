# FINDING 2026-09-23 (cto, MODE DECTET) — THE FRAME MAP WAS ANCHORED AT THE POLL'S FLOOR, NOT THE FRAME'S BASE, SO EVERY CELL IN THE FRAME READ EIGHT BYTES OUT OF PHASE WHENEVER THE SPINE WAS SHALLOWER THAN THE MAP'S DECLARED EXTENT

Rows: gc-a-site-that-refuses-every-poll-form-names-an-unrooted-holder-starting-with-the-concat-slot-capture (row 867, the ceo's kill-map lead, CEO-1181/1183), gc-chunk-d-the-ceo-remainder-32-sites-in-seventeen-files-the-cure-form-follows-the-box (the lock the bus served), hq_icon's two mode-4 witnesses (icon-mindfa-recursive-marklists-frame-map-agree-zero-..., icon-ilib-arizona-m4-segv-...). Landed in SCRIP 7b74d4022; the measured claims are folded into the row 867 ledger, the chunk D ledger and GOAL-CTO.md CTO-145 in the same landing (CEO-859).

## THE ONE GDB READ THE CEO ASKED FOR, AND WHAT IT KILLED

The ceo's lead (row 867 ledger, 02:42 CDT): concat results 3 onward live in a second rw mapping outside [g_hp_arena, g_hp_top), gc_blk_of answers NULL there, the cell is never visited. Measured in the scratch worktree at 90392846a with the bare poll restored after the ZRES stores at bb_binop_concat_slot.cpp:69, witness scripts/gc_witnesses/hb_concat_slot_capture_across_a_collection.sc, SCRIP_HEAP_KB=128, stress 1, gdb breaking at gc_collect_ex and logging every concat result's address against the arena bounds:

    arena=0x7fff6ca00000 top=0x7fff6ca0a8xx end=0x7fff6ca20000 cap_end=0x7fff6ce00000
    every result 0x7fff6ca0a850..0x7fff6ca0a8f0 -- INSIDE the arena, just below the live top

The "second mapping" was the arena's own live window: the quarantine trap PROT_NONEs vacated ground above the top, which splits the arena's VMA at the page boundary above it, and /proc/maps shows the live part as its own rw line. The "2 GB reserve" strings at 0x7fffece1xxxx are the mode-3 slab's literal pool (the `'ARB-1 cap='` literals), not heap results. The index is not the defect. One read, as promised.

## THE HOLDER, AND THE WALK THAT MISSED IT

Reading the poll's floor cells at every collection (the slow path passes floor = the address of its own return-address slot): the ZRES cell {DT_S slen, s} sits at floor+8, holding the fresh concat result, at every polled collection. Re-reading each block's header after its collection: collections 4..12 keep or move the block and update the cell; collections 13, 14, 16, 18, 19, 21..25 leave the cell untouched and the block's ground reads 0xDB. The three wrong output lines are exactly collections 13, 14 and 16.

Breaking on gc_walk_interior and printing its anchor against the floor:

    #12  anchor=0x7fffffbf93a0  lo=0x7fffffbf9398  floor-anchor=-8   -> cell visited, block moved and the cell updated
    #13  anchor=0x7fffffbf93e8  lo=0x7fffffbf93e8  floor-anchor=0    -> cell never visited, block reclaimed
    #14..#25 the same: anchor == floor

The frame's map cell (DT_MAP, graph=main, frame_bytes=6560, map_off=6544) is at a fixed address, so the true base cell - map_off is fixed too. gc_walk_range computed it, then CLAMPED it up to the floor whenever the floor sat above it (`if (base < p) base = p;`) and handed the clamped value to gc_walk_interior as the ANCHOR. Every layout offset in the frame was then applied from the return-address slot: the first entry (off 0, DESCR, 160 bytes) read the poll site's return address as a tag, and the collector said so in its own words --

    [GC-WALK-BADTAG] pop=cstack graph=main off=0 v=0xd0 slen=30136 p=0x900000002

v=0xd0 is the low byte of the poll site 0x7fff6ce0b3d0; p=0x900000002 is the ZRES TAG word (slen 9, DT_S) read in the pointer position. Eight bytes out of phase, for the whole frame, at every poll whose floor lay above the declared base -- which is every poll taken while the spine is shallower than the map's declared extent. That is why the site "refused every poll form" (four forms, four DIFFs, CEO-1131): no poll form can root a cell the walk reads at the wrong address.

## THE CURE (src/runtime/rt/gc_heap.c, gc_walk_range and gc_walk_interior)

1. The anchor stays the true base. Only the SPINE word walk (gc_walk_words, cls 0) starts at max(base, floor).
2. A layout entry clipped at the floor is clipped on its own 16-byte cell grid (`w += ((lo - w) + 15) & ~15`), never to the floor itself: the floor is a return-address slot and always sits one word below the first live cell, so clipping to it would put the DESCR walk out of phase by construction.
3. The walk report carries `i_phase`: a bad-tag cell whose pointer word is itself a known tag -- the signature of a cell read out of phase. Zero on the cured tree at every collection of the witness at stress 1 and 5; 21 of 21 and 6 of 6 on 90392846a.

Gate: scripts/test_gate_gc_the_frame_map_anchor_is_the_frame_base_even_when_the_poll_floor_is_above_it.sh (wired in `make test` after the concat gate, recorded in gate_wiring.tsv). Arms: the concat witness matches its ref at stress 1 and 5 with i_phase=0 on every cstack walk line and at least one collection with its floor at or above the base (s_words=0 -- the shape the gate grades); Arizona mindfa (scripts/gc_witnesses/hb_frame_map_anchor_recursive_marklists_mode4.icn, ref = the Icon distribution's .std) compiles, links and matches in mode 4 at 128 KB with collections>0. On 90392846a: red on all three arms, mindfa rc=139.

## WHAT ELSE THE SAME DEFECT WAS

hq_icon's two telegrams of this morning: Arizona mindfa (also jcon mindfa and IcnM procedure_record_every_replace_3 -- one bug, three suite entries) with "agree=0 for pop=cstack at every collection, frames=5", and Arizona ilib (SIGSEGV in rt_list_view under a subscript through a chain the unwinder could not read). Both at SCRIP_HEAP_KB=128, mode 4: control 90392846a rc=139 and rc=139 with 319 lines differing; the cured tree rc=0, byte-identical to mindfa.std (21 collections) and ilib.std (616 collections). Mode 3 passes on both trees for both, because the mode-3 spine at those polls happened to sit at the declared base.

## THE POLL AT bb_binop_concat_slot.cpp:69 STAYS OUT, AND THE NEXT HOLDER IS NAMED

With the walker cured and the :69 poll restored, the concat gate is GREEN at stress 0, 1, 3 and 5 (25, 9 and 6 collections) -- the cfo's gate can carry the poll now. But the SNOBOL4 population arm reads ONE cure-only red with that poll in: user_function_opsyn_8 (`DEFINE('cat(a,b)') ... cat = a b :(RETURN); OPSYN('foo','cat',0); OUTPUT = foo('abc','def')`) prints an empty line instead of abcdef at stress 0 in both modes, one collection, re-drawn three times on the cure tree, three times on a poll-only tree (same DIFF), three times on the control (same as the ref); with or without forced relocation. The collector names the holder in its own report at that collection:

    [GC-WALK-SPINE] pop=cstack graph=main off=-1424 word=0x72c51f807270 blk=... type=205 text=cat.....   (HB_WSC, the function-name string; three raw copies at off -1424, -1384, -872)
    [GC-WALK-SPINE] pop=cstack graph=main off=-1328 word=0x72c51f80b1e0 blk=... type=215                (HB_WSB, the call's workspace block; two raw copies at off -1328, -728)
    [GC-WALK] pop=cstack ... s_raw_heap=5 a_heap=1 divergence=6

Five raw, untagged spine words in the SNOBOL4 user-function call path hold heap blocks across the body's execution and are not visited; the collection the :69 poll takes inside the body moves them; the RETURN path reads the stale copies. That is the bb_call_proc_staged family -- chunk B's rt_proc_call_open* sites, unpolled for exactly this reason -- and a cure that trades one program for another never lands (CEO-589), so the poll waits for chunk B's holder. The reach witness for that row is this program; the count stays 195 of 231.

## THE EVIDENCE MACHINE (CEO-1165/1172)

Control worktree at origin 90392846a, clean, built. Population by name from ALL.csv extracted standalone with refs and stdin: SNOBOL4 440 (320 by goto_fail/goto_success/CODE/EVAL/DEFINE/capture_plus_defer/deferred_eval/APPLY + 120 sampled), Icon 320 (procedure/every/suspend/scan/create/element_gen), Snocone all 337; m3 and m4; stress 0 and 1; SCRIP_HEAP_KB=128, SCRIP_GC_RELOC=1, 30 s ceiling. The name sets are in the ledger line of the landing commit. Witness sweep GREEN 100/100 pairs. Census 195 + 0 + 36 == 231, identity held, no poll touched, baseline unchanged. Tiny-arena pass (make test-arena) and preflight receipts in the same ledger line.
