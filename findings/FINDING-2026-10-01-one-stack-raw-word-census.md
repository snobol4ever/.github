# FINDING 2026-10-01 — the one-stack row's raw-word census: what an aligned 16-byte sweep of the emitted stack meets today

Row `gc-one-stack-all-descriptors-no-marker-no-map-no-ledger-every-raw-word-on-the-emitted-stack-becomes-a-tagged-cell-lon-2026-09-30` (cto, rank 0; ARCH-GC-COMPILE-TIME-FRAME-MAPS.md § 12). Measured by the cto on SCRIP 6b33e24d5 plus the instrument below.

## The instrument

`gc_s16_census` in `src/runtime/rt/gc_heap.c` (RT_DIAG), switched by `SCRIP_GC_SWEEP16`:

- `1` — one `[GC-S16-SUM]` line per stack segment per collection, plus one over the GVA island: `units`, `cell`, `raw`, and raw split into `code`, `stack`, `heap`, `other`.
- `2`..`8` — also one `[GC-S16]` line per raw unit for the first 8, 64, 512, … collections, naming the frame it sits in: `BLOB` (offset from the blob's rbp), `FRAME` / `ROOT` (offset from the frame base), `SPINE` (distance below the next frame's map cell), `TOP` (above the last map cell in the segment). `9` dumps every collection.

A unit is the 16 bytes at a 16-aligned address from the segment's floor. It is RAW when its first word is a heap address, a code address, a stack address, or carries no known tag (`other`). **A bare tag-known test is worthless:** every tag from `DT_P` up is a multiple of 8, so about 70% of 8-aligned stack addresses have a low byte that reads as a known tag. The classifier therefore asks what the first word *is* before it asks what its low byte *says*.

**It can say yes:** over the GVA island (an array of DESCR cells the collector already visits) it reads 0 raw units on every witness that has globals.

## Determinism

Under `env -i … setarch -R`, a run's address-valued raw count (code + stack + heap) on the main stack is exact from run to run (crypt.pl: 283,792 on every run). `other` drifts slightly — those are pads and slots nobody writes, so they hold whatever an earlier frame left there. That drift is itself the population the row must remove. The counts are observations summed over collections, so they move with any change in allocation volume. A blocking ratchet on them would go red on other seats' landings, so the gate is REPORTED and its criterion is zero.

## First readings (64 KB window, `SCRIP_GC_STRESS=1`, main stack, both modes)

| witness | m3 raw / units | m4 raw / units |
|---|---|---|
| hb_blob_span_defer.sno | 25 / 537 | 36 / 4,592 |
| hb_eval_names.sno | 649 / 2,259 | 667 / 6,302 |
| hb_sno_every_deferred_expression_shape_under_the_flip_plant.sno | 490 / 104,254 | 922 / 108,113 |
| crypt.pl | 300,228 / 2,203,438 | 300,054 / 2,206,251 |
| hb_coexpr_create.icn | 3,059 / 65,329 | 3,112 / 69,428 |
| vscroll_driver.icn | 66,469 / 3,136,257 | 66,240 / 3,140,356 |

Over the 100 programs of `scripts/gc_witnesses/` at the same arena: 12.5% of all units swept are raw. Each class:

- **Blob frames are a small share.** Only 3 witness programs had a blob frame live at a dumped collection: 31 raw units, all in the head — the caller's γ/ω pair at rbp+8, the DTP's unit at rbp−24, and the saved rbp's unit at rbp−8.
- **The root frame** carries a code word at base+0 at every collection (`main+155` in mode 4: the return into the C driver) plus a stack and a code word near base+160.
- **The spine between frames** holds box resume records. Example: IR_MATCH_DEFER's γ pushes `{pad, resume}` or `{r14, resume}` and its β is `jmp [rsp]`. These records belong to each box, in every language.
- **Prolog's code words** are return addresses left by `call` into call-entered ports. crypt.pl in mode 4 symbolizes them to `call_proc_staged` α+169/+194 and β+34. That is the PL-DC protocol, which is L2.
- **`TOP`** is mostly parked co-expression stacks above `park_sp` (C frames — § 12 (c), the C2BB rows), and Raku's main stack above its last map cell.

## What this changes in the plan

§ 12's L1 ("the blob head to cells") is the smallest class here. The bulk is per-box resume records on the spine, and Prolog's call protocol. A `{pad, resume}` record can become one `{DT_RAW, resume}` cell at the same depth — the pad becomes the tag, so `sub rsp, 8; push rax` → `push rax; push DT_RAW`, and the β becomes `jmp [rsp+8]`. The spine depth does not change, so the zd planner's depths do not move. Each box converts in its own landing while the current walker keeps working, because a `DT_RAW` cell is one the sniffing walk already skips. The census reads each conversion's effect. The walker becomes the 16-step sweep (L3) only when the gate reads zero.

## Reproduce

`bash scripts/test_gate_gc_one_stack_the_walker_sweeps_tagged_cells.sh` (~13 s), or one witness:
`env -i PATH=/usr/bin:/bin HOME=/tmp SCRIP_HEAP_KB=64 SCRIP_GC_STRESS=1 SCRIP_GC_SWEEP16=3 setarch -R ./scrip prog 2>&1 >/dev/null | grep GC-S16`.
To symbolize code words, use a mode-4 binary under `setarch -R`: subtract `0x555555554000` and look the offset up in `nm -n`.
