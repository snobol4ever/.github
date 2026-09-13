# FINDING 2026-09-12 (coo) — the collector slides, but since ac044419d four block types are immortal and never moved; Lon's design has no pinning

**Lon, 2026-09-12 ~19:2x CDT, in-chat to the coo, verbatim:** *"I'm confused about this pinned allocation heap. We do not have that. We do not allow pinning in our heap since we slide. So explain."*

## What the code does (SCRIP origin 88dfe7505, src/runtime/rt/gc_heap.c)
- The collector compacts: live blocks are forwarded and moved with `memmove` (gc_heap.c:690, inside `gc_collect_ex`).
- Four block types are exempt: `hb_pinned(t)` at gc_heap.c:12 names `HB_WS`, `HB_WSS`, `HB_DINST`, `HB_ARR` (workspace, workspace strings, SNOBOL4 DATA instances, arrays). At every collection they are marked live unconditionally and threaded on the mark list (gc_heap.c:641); `gc_pinned_exact` (:566, used at :581-582) recognises them by exact address; they are never moved and never reclaimed.
- `rt_pinned_alloc` / `rt_pinned_alloc_tag` / `rt_pinned_strdup` (gc_heap.c:237-275) mint them; a failed carve prints "heap exhausted ... on a pinned allocation".
- Landed in SCRIP `ac044419d` (2026-09-09) — its own message: *"the workspace island dies -- its blocks are PINNED headed blocks in the GC arena (immortal, never moved, scanned as roots by type: HB_WS, HB_WSS, HB_DINST, HB_ARR)"*. The ledgers naming that landing are GOAL-CTO.md and GOAL-CFO.md (the SNOBOL4 runtime lane), not a Pascal landing.

## What it means for Pascal
- `new(p)` allocates the record cell through `rt_pinned_alloc` (by_name_dispatch.c, `__pas_alloc_rec`), and `p` is an integer handle into a Pascal-own heap table (`pas_heap_cell`), never a raw address. `dispose` is a no-op (`__pas_dispose` returns null).
- So Pascal pointer stability today is a side effect of the exemption, not a Pascal design. If the exemption is removed to restore the pure sliding design, Pascal needs nothing more than that its heap table be a root the collector updates when it moves a block — the handle indirection is already there.
- P4 uses `new` + `mark`/`release` (bulk free), P5 uses `new` + `dispose`; neither collects. Both will run on either heap design; today neither frees anything.

## Asked
The runtime is the ceo's; this finding asks for the ruling: keep the exemption (and say so in ARCH-ENGINE.md), or retire it and make the Pascal heap table a movable-root, in which case the coo takes the Pascal half.
