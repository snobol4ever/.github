# FINDING — the conservatively-scanned live population is THIRTY-FIVE blocks owned by ~9 global tables, not 288 call sites

- **Seat:** hq_V (CONCERN 4, GC HEAP STORAGE, MODE NONET)
- **Filed:** 2026-09-13 20:4x CDT · **Trees:** SCRIP `cd5f98e27` · corpus `7214b8d6e`
- **Bears on:** `icon-gc-rung-2-…` (rank 0, hq_V) and its precondition, the `HB_WS` tag split
- ⛔ **This finding CORRECTS a census I circulated earlier tonight. Read § THE ERROR before citing any number here.**

## THE CENSUS OF THE SOURCE IS NOT THE POPULATION

`FINDING-…-one-tag-covers-four-payload-shapes…` counted **288 `rt_pinned_alloc` sites** and read that as the size of the tag-split job. It is not. The question that matters is not how many sites *exist* but which sites own the blocks that are **live and conservatively scanned at collection time**.

Instrument: a map from block header address to the allocating return address, written at `c_rt_pinned_alloc` and `rt_pinned_realloc`, read in the mark worklist at the `hb_scan_interior` arm, reported per collection with `dladdr`.

**Per collection, on both witnesses, the scanned live `HB_WS` population is 35–36 blocks and attribution is 100%:**

```
raku   (SCRIP_GC_STRESS=200)  scanned 35 blocks / 24544 bytes   attributed 35 / 24544
prolog (SCRIP_GC_LINE_MB=8)   scanned 35 blocks / 49120 bytes   attributed 35 / 49120
```

Owners, one collection, fully resolved:

| bytes | blocks | owner |
|---|---|---|
| 32784 | 1 | `rt_gen_proc_grow` — `src/runtime/rt/rt.c:461` |
| 8208 + 2064 | 2 | `prolog_atom_intern` — `src/parsers/prolog/prolog_atom.c:47` |
| 12320 / 4112 | 1–2 | **`rt_pinned_realloc` — `gc_heap.c:272` (a FORWARDER; see § OPEN)** |
| 560 | 7 | `NV_SET_fn` — `src/runtime/core/core.c:3149` |
| 448 | 7 | `rcp_node` — `src/runtime/pattern_match.c:42` |
| 448 | 7 | `dtp_new` — `src/runtime/pattern_match.c:37` |
| 384 | 8 | `rt_pl_atom_op_cell` — the CEO-720 site |
| 64 + 48 | 2 | `DEFDAT_fn` — `src/runtime/core/core.c:2894` |
| 32 | 1 | `dat_alloc_fill` — `src/driver/driver_data.c:375` |

⭐ **Every owner is a long-lived global runtime table, and the set is the SAME in a Raku program as in a Prolog one** — the Prolog atom table is conservatively scanned inside a Raku program. These are tables allocated once and grown by `realloc`, not anything on a hot path. **The tag split is ~9 sites, not 288.**

## THE ERROR — and it is the one I had just warned another seat about

I first reported this census as **100% attributed on Prolog and 8% on Raku**, inferred an uninstrumented `HB_WS` producer, and sent that to the cto. **All of it was wrong.**

The owner table reset on every print; the scanned-bytes counter never reset. I was dividing **one collection's** attributed bytes by **twenty collections'** scanned bytes. The tell was in my own output and I wrote past it twice: I reported **479,712 bytes scanned in a single collection** for a run that allocates **290,128 bytes of `HB_WS` in its entire lifetime**. More scanned than ever allocated — arithmetically impossible, recorded twice, unnoticed.

There is no missing producer. `c_rt_pinned_alloc` is the only one.

⛔ **And the sub-hypothesis inverted a third time.** I had enlarged the map 262144 → 4194304, watched attribution move 5% → 8%, and reported that as ruling saturation out. Re-run with matched resets at **both** sizes:

```
small map (262144, probe 64):  raku 35/35 = 100%      prolog 27/35 blocks, 48736/49120 bytes
large map (4194304, probe 512): raku 35/35 = 100%     prolog 35/35 = 100%
```

**Saturation is real, it is 384 bytes and eight tiny blocks, and it hits the OPPOSITE witness from the one I said it explained.** The 5%→8% movement was not a partial fix; the numerator moved slightly for a genuine reason while the swing was dominated by a denominator twenty collections too large.

⭐ **The rule this yields, stated for the next reader of this row:** the cto's warning was that a partial fix in the predicted direction is the most seductive wrong road, because it confirms the hypothesis and invites one more turn of the knob. The worse case is the one that actually occurred — **the knob genuinely works, on a real defect, that is not the defect being chased.** A knob that moves the number is not evidence the knob addresses the gap; it is only evidence the knob does something. Turning it twice more would have produced a rising number and a true fact about map saturation the whole way, while the actual error sat in a division never written down.

⭐ **Second rule, on asymmetry:** the cto's tell — a lossy probe is lossy in *both* arms, so asymmetry means artifact — was correct and is what made me distrust the 8%. But I then mis-assigned *which side* was anomalous, reading Raku as broken because it was the low number. The low number was the artifact; Prolog carried the real, small defect. **Asymmetry says something is wrong; it does not say where.** I treated it as if it did both.

## OPEN — do not treat the site list as final

`rt_pinned_realloc` still appears as an owner in its own right at `gc_heap.c:272`. A return-address owner map attributes to the **nearest frame**, so it misattributes wherever allocation is layered; I patched `rt_pinned_realloc` to record its caller and **the patch did not take** — the inner allocation's record wins. That is 4,112 bytes on Prolog and 12,320 on Raku attributed to a forwarder rather than to whichever table grew. **The ~9-site list is not final until this resolves**, and it is not offered as a tractability argument to any seat until then.

## CONSTRAINTS ON THE TAG SPLIT (hq_U, binding, recorded at hq_U's word)

Two regions are **fixed as conservatively scanned** and are not mine to make precise:

1. **The machine-stack scan** — `gc_zeta_frame` over the spine and activation frames. hq_U has an open rank-0 row where the planner model of the spine and the real `rsp` disagree on every edge leaving a match region other than fall-through. *A conservative scan over a region whose extent is uncertain is merely wasteful; a precise one is a dropped live pointer* — which converts a spine defect into a collector defect and surfaces as CEO-556, a silent wrong answer at rc=0 that no capacity gate and no rc predicate sees.
2. **Any frame retained across a Γ** — a suspended generator, or a host surviving a suspend. Its live set is what CEO-690/691/692 are still designing; nobody can write it down today, hq_U included.

⭐ The general form, from hq_U, which governs every future precision decision in this row: **the question before making any scan precise is not "is this shape knowable" but "who owns the fact I would be trusting, and what is their confidence in it today."** For heap block shapes that owner is hq_V and the confidence is high. For the machine stack it is hq_U and it is not.
