# ⛔⭐⭐⭐ ARCH — THE COLLECTOR GUESSES NOTHING: COMPILE-TIME FRAME MAPS AND SAFE POINTS (Lon 2026-09-17, in-chat to ceo; CEO-812)

**Lon's word, verbatim, the morning of 2026-09-17 (landed 09:4x CDT by the ceo's clock), after the ceo confirmed that `gc_heap.c` scans stack words Boehm-style and rewrites the ones that fall inside a heap block:** *"Nope. Can not do that. You must find another way. We must know what each memory structure you are looking at. I thought they were all DESCR. But if they are varying types, then the compiler should be making maps. What do you think? Can you do it?"* — then: *"Can you do it with a compile time map versus a runtime map. If so, do so."* — then: *"If you are choosing safe points, then you can not just say at MATCH_BEGIN and MATCH_END for instance. How will you choose the safe points?"*

This page is the design. It supersedes the conservative arm of `ARCH-GC-PINNED-ALLOCATOR-LIFETIME-CLASSES.md` and the per-cycle no-move alternative the ceo put to Lon in CEO-809, which is REFUSED: no pinning in any form, per allocation or per cycle.

## 1. What is on the stack today, and why guessing became corruption

Three kinds of memory, measured at SCRIP `db4a6b1fc`:

1. **Zeta slots in emitted frames** — ζ-ACTIVATION-FRAME on RBP, ζ-SPINE on RSP. The compiler lays every slot out in `src/ir/frame_layout.c` and records its kind in `zls_field_t.kind`: `ZK_DESCR` (a 16-byte descriptor), `ZK_PTR_GC` (a raw 8-byte pointer into the collected heap: bucket vectors, field arrays, array data), `ZK_RAW` (counters, cursors, watermarks, saved rsp — never a pointer). 64 registrations today. The compiler knows every slot's kind and never tells the collector.
2. **The runtime's own C frames** — locals of `rt_*` functions holding a raw heap pointer across a call that can collect. The 24-site register-spill class (CEO-803) and hq_prolog's twelve stress SIGSEGVs are this kind.
3. **Registered slots** — coexpressions (`rt_coexpr.c`), the Prolog trail (`rt_pl_trail.c`), `rtcc_init.c`: precise, registered through `rt_gc_slot_reg`/`rt_gc_root_range_add`. This path is correct and is the model.

`gc_zeta_frame` (gc_heap.c:557–563) walks every registered range word by word: 16 bytes that parse as a valid descriptor are visited precisely; otherwise each 8-byte word is handed to `gc_blk_of`, and any word inside a heap block is MARKED and its slot REGISTERED FOR REWRITE when the block slides. That is the Boehm guess, and worse than Boehm: Boehm never moves, so a wrong guess leaks; here a wrong guess moves the block and overwrites a word that was an integer or the length-and-tag half of a descriptor. Under the pinned class the guessed blocks did not move, so the guess cost nothing; deleting pinning (CEO-803, `3b79683b5`) turned the leak into gc2. hq_icon measured it: 100–270 guessed words rewritten per collection on gc2; under `setarch -R env -i` with equal-length knobs the verdict is a function of the stack offset alone (BAD over a band of 32 of 64 offsets; a mark-only arm halves the band to 34..49 and cannot close it, because mark-only stops relocating genuine roots too). The poison detector does not reach this defect (0 of 36): a block that slid DOWN leaves its old bytes inside live data.

## 2. The design: compile-time maps, and the allocator never collects

**Rule 1 — the map is compile-time data.** For every safe point (§ 3) the emitter writes a static table entry beside the code, in BOTH media (in the sealed mode-3 slab; in `.rodata` under a label in mode 4): `{ return-PC, spine depth at that PC, [ (offset, kind) for every live slot of the RBP frame and the RSP spine at that PC ], [ callee-saved registers that hold a ZK_DESCR/ZK_PTR_GC at that PC ] }`, generated from `zls_field_t` and the emitter's own knowledge of which registers it assigned. Nothing is built at run time; there is no registration call per activation. Keyed by return PC, the collector finds each frame by walking the RBP chain (the runtime is `-fno-omit-frame-pointer`; emitted activation frames are RBP frames by the BB FRAME-PLACEMENT CRITERION) and binary-searches the table.

**Rule 2 — the collector walks maps, not words.** `gc_collect_ex` visits exactly the slots the map names: `ZK_DESCR` through `rt_gc_visit_descr`, `ZK_PTR_GC` through `rt_gc_visit_raw`, `ZK_RAW` never. The word scan, the 16-byte descriptor sniff, `cons_stack` and the `rt_cas_live_span` byte scan are DELETED, not gated. Coexpression stacks are chains of mapped frames walked from the coexpression's saved RBP. Registered slots (kind 3 above) stay precise roots.

**Rule 3 — the allocator never collects.** Today `rt_gcheap_alloc` (gc_heap.c:206–207) calls `rt_gc_collect` from inside the runtime, with every runtime C frame live and unmapped — which is the only reason kind 2 was ever scanned. Under this design the allocator sets `g_gc_pending` (it already exists and is already set by the stress and budget pacers) and, when the line is crossed, GROWS the arena window rather than collecting; the collection runs at the next safe point, where the only live C frame is the poll's own call into the collector. Therefore no runtime C frame is ever scanned, and the 24-site spill class and the twelve SIGSEGVs are cured by construction rather than site by site. The arena must be growable to the next safe point; the bound is one runtime call's own allocation (a `DUPL` of a gigabyte grows the window by a gigabyte and the next safe point compacts).

**Rule 4 — the one residual, enumerable.** A runtime C frame that CALLS BACK into emitted code (`by_name_dispatch.c`, `gen_runtime.c`: APPLY, EVAL, by-name calls, sort comparators, generator resumption) has a safe point BELOW it on the stack. Such a frame may not hold a raw heap pointer across the callback: it registers the slot precisely (the coexpression way) or re-reads through a handle after the callback returns. These sites are found by grep of the callback entry points, not by scanning; a gate censuses them.

## 3. Lon's question: how are the safe points chosen?

Not by box. `MATCH_BEGIN`, `MATCH_END` and every other box kind are irrelevant to the choice. **A safe point is exactly the return point of an emitted call into a runtime entry that can allocate, placed AFTER the call's result has been stored to its mapped slot** — and nowhere else. The reasons:

- **It is where collection is needed.** Memory is consumed only inside allocating runtime calls; a box that never allocates never needs a safe point; a program that allocates nothing never collects. Loop back-edges need no poll because a loop that allocates passes a safe point every iteration by construction.
- **It is where the map is knowable.** At a call's return PC the spine depth is a compile-time constant (RESULT/LOCALS live on the RSP spine only where every consumer reaches them at a fixed compile-time offset — the FRAME-PLACEMENT CRITERION already guarantees it), the RBP frame's layout is `zls_field_t`, caller-saved registers are dead across the call, and the callee-saved registers the emitter assigned are known. Storing the result before the poll means the fresh pointer is in a mapped slot, never only in `rax`.
- **It is cheap.** The poll is `cmp dword [rip+g_gc_pending], 0 ; jne slow` — the shape `bb_call_proc_staged.cpp` already emits at the staged call boundary — beside a call that just allocated. The slow path spills the callee-saved registers to a known frame and calls the collector with the map key.
- **It is complete.** Because Rule 3 removes every other collection site, the set of safe points IS the set of allocating call returns; a runtime entry that allocates and has no poll at its return is the gate's red (a census over the runtime's allocating entry points against the emitter's poll sites), and the residual of Rule 4 is the only other place a collection can begin.

The compiler already annotates one field *"dead at safe points"* (frame_layout.c:107): the notion exists; this design makes it the whole root policy.

## 4. Proof and gates

- gc2 under `setarch -R env -i` with equal-length A/B knobs reads GOOD over the whole offset band in mode 4 (hq_icon's hardened recipe: never a single PAD number, always a band under an empty ambient environment); the gc2 gate reads 5 of 5 both modes and its Makefile arm loses its leading dash in the same landing (CEO-807's clause).
- hq_prolog's twelve master entries under `SCRIP_GC_STRESS=1` read PASS; the Prolog master under stress 1 reads FAIL=0 over its printed denominator.
- Census gates: zero conservative visits in `gc_heap.c` (no `gc_blk_of` on a stack word, no `cons_stack`); zero `rt_gc_collect` calls inside `rt_gcheap_alloc`; every allocating runtime entry has a poll at its emitted return (the safe-point census); every callback site of Rule 4 holds no raw heap pointer across the callback (the residual census). `SCRIP_GC_COVERAGE=1` reports words-scanned = 0.
- The control arm is base-vs-head on every frontend under CEO-757's batch; the seven masters and the benchmark grids read no worse.

## 5. Rows — THE EMERGENCY SPLIT (Lon 2026-09-17, verbatim: *"In general we are at a reset point an EMERGENCY fork so quit any existing work and concentrate solely on the mess you made with the GC HEAP design."*; CEO-813; MODE line 2 carries it; every seat parks everything else)

Ten seats, one row each, all rank 0, DONE-WHENs red on origin `96c80d49d`, assigned:

| seat | row (prefix) | piece | lands |
|---|---|---|---|
| cto | `gc-frame-placement-proof-...` | LOAD-BEARING: prove every spine/frame slot has a fixed compile-time offset at every allocating call return; name the callee-saved registers that can hold a DESCR/PTR_GC there (Prolog r12–r15 first); where the criterion fails the slot moves to the RBP frame | FIRST |
| hq_prolog | `gc-safe-points-the-allocator-never-collects-...` | the allocator sets `g_gc_pending` and grows the window, never collects; polls at Prolog allocating returns; `gen_runtime` callback residual | second — alone cures the C-frame class |
| hq_icon | `gc-compile-time-frame-maps-...-walks-maps-not-words` | the emitter's map table from `zls_field_t` (format fixed with the cto in § 6 today); Icon box polls; gc2 under `setarch -R env -i` over the band is the witness; the gc2 gate loses its dash | third |
| hq_snobol4 | `gc-every-snobol4-and-snocone-allocating-box-stores-its-result-then-polls-...` | SNOBOL4/Snocone box polls after the result store; `by_name_dispatch`'s 208 callback sites hold no raw heap pointer across the callback | with hq_icon |
| hq_snocone | `gc-the-compile-time-map-table-is-emitted-beside-the-code-in-both-media-...` | the map table as static data through `x86_asm.h`/xa in the sealed slab (mode 3) and labelled `.rodata` (mode 4), found through one runtime symbol | with hq_icon |
| cfo | `gc-the-collector-walks-the-rbp-chain-keyed-by-return-pc-...` | `gc_collect_ex` walks main and coexpression stacks by RBP chain keyed by return PC; visits only mapped slots; the scan, the sniff, `cons_stack`, `rt_cas_live_span` deleted; coverage words-scanned 0 | after the table exists |
| hq_pascal | `gc-every-zeta-slot-of-a-pascal-graph-registers-its-kind-...` | no Pascal frame slot without a `ZK_` kind | parallel |
| hq_raku | `gc-every-zeta-slot-of-a-raku-and-rebus-graph-registers-its-kind-...` | no Raku/Rebus frame slot without a `ZK_` kind | parallel |
| coo | `gc-instruments-the-safe-point-census-the-maps-census-and-scrip-gc-coverage-...` | the census gates, each tripping under a planted violation | parallel |
| ceo | — | the integration audit daily; the ARCH page and § 6 kept current; lifts the emergency on Lon's word | — |

## 6. The map table format (to be fixed by the cto and hq_icon today, then frozen)

To be written by the cto and hq_icon in one landing on this page before any seat codes to it: the entry struct (return PC, spine depth, slot list as (offset, kind) pairs, callee-saved register mask), its sort key, how the collector finds the table in each medium (one exported symbol), and the static-assert that pins its layout. Until this section is filled, no row but the cto's and hq_prolog's lands code.
