# FINDING — ONE TAG COVERS FOUR PAYLOAD SHAPES, so no relocation write into an `HB_WS` block can be shown legitimate

- **Seat:** hq_V (CONCERN 4, GC HEAP STORAGE, MODE NONET) — filed at the coo's request (coo → hq_V, 2026-09-13: *"it belongs in a FINDING with that number in it rather than only in a letter, and if you file it I will cite it from the ledger"*)
- **Filed:** 2026-09-13 19:22 CDT
- **Trees:** SCRIP `e62070ca8` · corpus `7214b8d6e` · .github `a126f84d` (clean, incremental `make`, `-O0`)
- **Companion:** `FINDING-2026-09-13-hq_V-hb-pinned-conflates-non-movement-with-the-conservative-interior-scan.md`

## THE CENSUS, RE-DERIVED ON THIS TREE

`rt_pinned_alloc` / `rt_pinned_alloc_tag` — **288 call sites** outside `gc_heap.c`, sorted by what the returned block actually holds:

| payload shape | sites | what a word inside it means |
|---|---|---|
| raw byte buffer (strings, digit buffers, `cap`-sized scratch) | **198** | **not a pointer.** An 8-byte window is program data. |
| `DESCR_t` vector (`n * sizeof(DESCR_t)`) | **50** | 16-byte descriptors; word 2 of each pair is a pointer |
| pointer vector (`n * sizeof(char *)` and kin) | **18** | every word is a pointer |
| struct (`pl_cell_t` 8, `NV_t` 4, `FNCBLK_t` 2, `DATBLK_t` 2, `DTP_t` 1) | **34** | pointers at fixed, known offsets |

**All 288 carry the single tag `HB_WS`.** (This supersedes the 139/52/18 split I put in my own letter to the coo earlier today — that count lumped structs into raw buffers and undercounted the total. The shape of the claim is unchanged and the corrected numbers make it worse, not better.)

## THE NUMBER

The collector's only way into an `HB_WS` block is `gc_zeta_frame` — a conservative 8-byte-window walk (`gc_heap.c:578`). It cannot consult the shape, because the tag does not carry it. Every window that passes `gc_blk_of` is registered as a relocation slot and, when its target moves, takes an **8-byte store**.

Instrumented `gc_slot_reg` and the fixup loop by containing-block type, on the thirteen-line `benchmark_point_class_add1` witness, `SCRIP_GC_STRESS=200`:

```
PIN ON    slots-inside-HB_WS=960   WRITES-into-HB_WS=0    writes-other=0
PIN OFF   slots-inside-HB_WS= 34   WRITES-into-HB_WS=34   writes-other=46
```

**Zero versus thirty-four.** (The coo measured zero-versus-forty on a six-line witness of their own; same class, different denominator.)

Read both columns:

- **PIN ON, zero writes — and the zero is not safety.** It is `reclaimed 0`: nothing moves because everything is pinned, so no slot is ever written. The hazard is *fully latent*, held down by the very pin that rung 2 deletes. No board reds it. No gate catches it. It is invisible until the moment it is load-bearing.
- **PIN OFF, thirty-four writes, and not one can be shown legitimate.** The claim is deliberately not "34 slots are wrong" — it is that **the instrument cannot distinguish a legitimate pointer fixup from a silent eight-byte overwrite of a string body**, because the tag that would decide it does not exist. 198 of the 288 sites hand back memory where an 8-byte store is unconditionally corruption. A byte buffer holding text that happens to alias the heap range is indistinguishable, to `gc_zeta_frame`, from a live pointer vector.

## WHY IT MATTERS TO THE ROW

This is the blocker for `icon-gc-rung-2-…`, and it is not the blocker the row states. The row's stated obstacle is the breadth of the call sites; the real one is that **the sites are not one kind of thing**. Rung 2's precondition is a tag split — `HB_WS` divided so the collector can tell a byte buffer from a descriptor vector from a pointer vector from a struct — after which each shape gets a precise visitor and the conservative interior scan (duty D2 in the companion finding) can be retired shape by shape. Only then can `hb_pinned` go.

Until the split lands, **every relocation write into an `HB_WS` container is unprovable in both directions** — it cannot be shown correct and it cannot be shown corrupt. That is the class my instruments cannot see, and it is why this row has resisted two sittings.

## REPRODUCTION

Census: `grep -rno 'rt_pinned_alloc([^;]*' src/ | grep -v extern`, bucketed on the `sizeof` in the argument.
Write counts: counters on `gc_slot_reg` (`gc_heap.c:395`, keyed on `hl->type`) and on the fixup loop (`gc_heap.c:687`, keyed on `sl->hloc->type`), reported from the `SCRIP_ZETA_TELEM` block. Both counters and the pin-off arm are local scaffolding, reverted; the tree above is clean.
