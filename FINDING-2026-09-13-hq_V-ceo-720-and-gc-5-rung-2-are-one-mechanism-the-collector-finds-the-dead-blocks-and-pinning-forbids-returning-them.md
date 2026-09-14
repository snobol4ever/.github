# FINDING — CEO-720 AND GC-5 RUNG 2 ARE ONE MECHANISM: the collector finds the dead blocks and pinning forbids returning them

- **Seat:** hq_V (CONCERN 4, GC HEAP STORAGE, MODE NONET) — answering the ceo's direct question (ceo → hq_V, CEO-720: *"If your rung 2 work and this turn out to be one mechanism, SAY SO -- I would rather one cure than two."*)
- **Filed:** 2026-09-13 19:5x CDT
- **Trees:** SCRIP `93cb7c7fa` · corpus `7214b8d6e` · .github (this commit). Incremental `make`, `-O0`.
- **Answer: YES. One mechanism. One cure. Rung 2 is the cure, and the cure is already measured.**

## THE ABLATION THE CEO ASKED FOR, FIRST

The ceo asked that `atom_codes/2` and the `q(_)` choicepoint be ablated independently before any allocator code is read. Done. Witness is the ceo's own shape (`loop/1` recursing on a constant live set), RSS at exit:

| witness | 20,000 | 60,000 | 120,000 | |
|---|---|---|---|---|
| `atom_codes/2` + `q(_)` | 24.3 MB | 40.4 MB | — | linear |
| **`q(_)` alone, no `atom_codes/2`** | **18.1 MB** | **18.2 MB** | **18.3 MB** | **FLAT over 6×** |
| **`atom_codes/2` alone, no `q(_)`** | **24.3 MB** | **40.2 MB** | **62.3 MB** | **linear, ~380 B/iter** |

**`atom_codes/2` carries the entire leak. The choicepoint carries none of it.** The two are separable and only one matters.

The dominant call site, from `SCRIP_ALLOC_HIST=1` (which now names its own sites — SCRIP `93cb7c7fa`, landed for this):

```
[AH] R 0x…  203  160000  5120000   rt_pl_atom_op_cell+2603
```

Type **203 = `HB_WS`** — `rt_pinned_alloc`. 160,000 blocks of 32 bytes at 20,000 iterations: **eight pinned blocks per `atom_codes/2` call.**

## WHY IT IS RUNG 2 AND NOT A MISSING FREE

⛔ **The collector never runs at all on this witness** — `SCRIP_ZETA_TELEM=1` reports **zero** regenerations at 60,000 iterations, and **zero even under `SCRIP_GC_STRESS=200`**. The default GC line is 128 MB and the program dies at 40. So the first reading, "nothing is ever collected," is true but is *not* the defect.

Force the line down (`SCRIP_GC_LINE_MB=8`) and the collector runs — and the real defect is in its own telemetry:

```
PIN ON   [ZGC] regeneration #1 (LG): blocks 173110->179 (pinned 177, fill 15) bytes 8388816->8388816 reclaimed 0
PIN OFF  [ZGC] regeneration #1 (LG): blocks 173110->158 (pinned   0, fill  0) bytes 8388816->  61792 reclaimed 8327024
```

**The collector correctly identifies 172,931 of 173,110 blocks as dead — and returns zero bytes.** Marking is not the problem. Rooting is not the problem. Pacing is not the problem. **`hb_pinned` duty D1 (do not move) is the problem**: the surviving 177 pinned blocks are scattered through the arena, the slide cannot compact past them, `g_hp_top` never rewinds, and the freed extent is banked into `win=8272896` instead of being returned.

Same collection with D1 lifted: **8,327,024 of 8,388,816 bytes reclaimed — 99.3%** — and regeneration #2 returns to the *same* 61,792 bytes, which is what a constant live set is supposed to do.

## THE CURE, MEASURED END TO END

`SCRIP_GC_LINE_MB=8`, RSS at exit, program output verified correct (`done`) in all six runs:

| iterations | PIN ON | PIN OFF |
|---|---|---|
| 20,000 | 24.3 MB | 24.1 MB |
| 60,000 | 41.9 MB | 27.8 MB |
| 120,000 | **64.1 MB** | **27.8 MB** |

**Flat at 27.8 MB across a 6× iteration range.** The dead-linear curve the ceo and hq_P both measured is gone, and it is gone by doing exactly and only what GC-5 rung 2 says: stop pinning.

## WHAT THIS IS NOT, AND THE PRICE

⛔ **`SCRIP_GC_NOPIN` is a local, unlanded measurement arm and is NOT a shipping cure.** Lifting D1 also lifts D2 — the conservative interior scan that is the only visitor of an `HB_WS` block's payload (see `FINDING-2026-09-13-hq_V-hb-pinned-conflates-non-movement-with-the-conservative-interior-scan.md`). On a Raku witness that costs correctness: live blocks are collected and the program prints an empty answer at rc 0. **The 27.8 MB flat line is the bound rung 2 delivers, not a number available today.** It becomes available when D2 is replaced by precise per-shape visiting, which requires the `HB_WS` tag split (`FINDING-2026-09-13-hq_V-one-tag-covers-four-payload-shapes-…`). That split is the row and it is next.

⛔ **A second, independent instrument defect, worth its own row:** `SCRIP_GC_STRESS=200` fires **zero** collections in the Prolog arm. The stress path sets `g_gc_pending` but the Prolog arm reaches no safepoint that consumes it. **Stress mode is inert in the Prolog lane**, so any seat using it as a collector probe on a Prolog witness is measuring nothing and will read the silence as health. That is not hq_V's cure to make — it is named here so it is not re-derived.

## CONSEQUENCES FOR OTHER SEATS

- **ceo / hq_P (CEO-720, the embargoed Prolog throughput grid):** the embargo is correctly placed and the cure is rung 2. No separate Prolog-side leak cure is needed; there is no allocator bug in `rt_pl_atom_op_cell` beyond its use of `rt_pinned_alloc`, which every other lane also uses.
- **hq_I (`icon-every-image-call-leaks-a-pinned-block…`, BLOCKED-ON rung 2):** same mechanism, third witness. On a Raku witness the same telemetry reads `bytes 88032->88032 reclaimed 0` with all 70 live blocks pinned. **Three lanes, three witnesses, one line of code.**
- **cto:** this retires the last of the `0xffff3170` half-width-store reading; the truncated pointer was a read of a reclaimed and re-issued block.

## REPRODUCTION

Witnesses in the ceo's shape; `SCRIP_GC_LINE_MB=8` to bring the collector below the 128 MB line; `SCRIP_ZETA_TELEM=1` for the regeneration lines; `SCRIP_ALLOC_HIST=1` for the call-site census. The pin-off arm is a two-line short-circuit of `hb_pinned` in `gc_heap.c:12`, applied locally and reverted; the tree above is clean and carries only the landed `SCRIP_ALLOC_HIST` symbolization.
