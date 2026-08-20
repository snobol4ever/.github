# FINDING s169 — GC-R: THE BUDGET KNOB CANNOT PRICE THE CADENCE HYPOTHESIS. IT IS CONFOUNDED, STRUCTURALLY GATED, AND THE HYPOTHESIS CANNOT PAY OFF UNTIL THE PINS GO

**Seat:** local `/home/claude1` (seat1), Claude Opus 5. **Picked up:** postoffice QUEUE.tsv row 5 `gc-r-ab`
— *"GOAL-SNOBOL4-100.md s167 D-22, rung GC-R ONLY (measurement, no code)."*
**SCRIP** `a78b39fb` · **corpus** `a3604cc9` · **.github** this commit.
**Measurement condition:** `make pristine` at `a78b39fb`, **RT_OPT = `-O0`** (FACT RULE O0-DEV; every number
below is an `-O0` number), `SCRIP_NOHUGE=1`, m3, harness `ZBUD=500` ms, **median of 5** unless stated.
**No code changed. Measurement only, as the rung specifies.**

## VERDICT (the rung asks for one, stated first)

**GC-R is a NO. Do not ship `SCRIP_GC_BUDGET_MB` as a cadence knob, and do not read the s167
small-region-often hypothesis as priced by it.** The knob cannot answer the question it was nominated to
answer, for three independently measured reasons — and the third is the one that matters strategically:
**a cadence change cannot pay off on a collector whose collections reclaim nothing.** The road is blocked
behind **GC-W1** (make a collection O(live)) and **GC-P1** (make it actually reclaim). Re-run GC-R after
those land; before them the hypothesis is not merely unproven, it is **untestable**.

## 1. THE KNOB IS CONFOUNDED BY CONSTRUCTION — IT COSTS 10–14% BEFORE IT COLLECTS ANYTHING

`gc_heap.c:218–222`, reading the code before running it:

```c
if (budget < 0) { const char *e = getenv("SCRIP_GC_BUDGET_MB"); long mb = e ? atol(e) : 0; budget = mb > 0 ? (mb << 20) : 0; }
if (!g_alloc_detax) g_alloc_detax = (stress_n == 0 && budget == 0 && g_ah_on <= 0 && …) ? 1 : -1;
g_hp_fr.armed = (g_alloc_detax == 1 && g_ah_on <= 0) ? 1 : 0;
```

**Setting the budget sets `budget != 0`, which forces `g_alloc_detax = -1`, which disarms
`g_hp_fr.armed` — the inline allocation fast path** (the `armed` byte the template bakes, contract §6).
So "budget on" is never one change; it is *cadence* **and** *every allocation rerouted through the slow C
path*. A naive A/B would bill that to cadence.

**Priced it.** `SCRIP_GC_STRESS=999999999999` disarms the detax by the same predicate while **never
triggering a collection** (`++stress_c >= stress_n` is unreachable) — a control that moves the confound
alone. Rows below were chosen because **gc = 0 in every arm**, so no collection-count difference exists to
explain any delta:

| row (m3, HEAP=512, gc=0 in all arms) | BASE | STRESS-huge (detax off only) | BUDGET4 |
|---|---|---|---|
| `eval_fixed` | 1,769,472 | 1,572,864 (**−11.1%**) | 1,703,936 (−3.7%) |
| `string_pattern` | 2,752,512 | 2,359,296 (**−14.3%**) | 2,359,296 (**−14.3%**) |
| `string_manip` | 1,310,720 | 1,179,648 (**−10.0%**) | 1,179,648 (**−10.0%**) |

**`STRESS-huge` and `BUDGET4` land on byte-identical medians for `string_pattern` and `string_manip`** —
exactly the prediction, since at HEAP=512 the budget never fires (§2) and both arms are therefore doing
nothing but disarming the inline allocator. **The detax disarm alone costs 10–14% throughput.** Any GC-R
table that omits this control reports a cadence result that is mostly an allocator result.

## 2. THE TRIGGER IS STRUCTURALLY GATED — IT CANNOT FIRE AT THE SHIPPING HEAP UNTIL 256 MB IS GONE

```c
if (budget) { since += total; if (since >= budget && (g_hp_top - g_hp_arena) * 2 >= (g_hp_end - g_hp_arena)) { … g_gc_pending = 2; } }
```

The budget is **AND-ed with "the arena is at least half full."** At the shipping `SCRIP_HEAP_MB` default of
512 that is **256 MB allocated before the first budget-triggered collect is even eligible**, and at the
timed runner's own default of 1024 it is 512 MB. **"Small region, often" is unreachable through this knob
without also shrinking the heap** — the knob does not control cadence, it controls cadence *within the
second half of an arena you sized elsewhere*. That is why the three rows in §1 show `gc=0` in the budget
arms: not because the budget was large, but because the precondition was never met.

## 3. WHERE THE KNOB *DOES* CHANGE CADENCE, THE MECHANISM IS REAL — AND IT STILL LOSES

Two measurements, and they point opposite ways until you put them together.

**(a) The mechanism is confirmed.** Heap sweep, `table_access`, BASE arm, one run each — as the arena
shrinks, collections multiply *and throughput improves*:

| `SCRIP_HEAP_MB` | 1024 | 256 | 128 | 64 | 32 | 16 |
|---|---|---|---|---|---|---|
| iters | 4352 | 1536 | 1536 | 1792 | 1664 | **2304** |
| collections in window | 0 | 1 | 2 | 5 | 8 | **24** |

24 collections beat 1. That is the s167 cost model showing through: each collect is **O(every block ever
allocated)**, so a smaller arena makes each one cheaper, and many cheap ones beat one enormous one. The
budget knob reproduces it *within* a small heap — `table_access` at HEAP=64: BASE 1792 (gc 5) →
BUDGET16 2048 (gc 28) → **BUDGET4 3584 (gc 135)**, with the budget arm also **more stable** (7-run spread
±3.6% vs BASE's ±12.5%: one big stall lands unpredictably inside a 500 ms window; 135 small ones average).

**(b) And it still loses to not collecting.** Median of 5, `table_access`:

| condition | median iters | collections |
|---|---|---|
| **HEAP=1024 BASE (GC-free)** | **3840** | **0** |
| HEAP=512 BASE (shipping default) | 3328 | 1 |
| HEAP=64 BUDGET4 (best cadence arm found) | 2944 | 115 |

**The best cadence arm does not reach the GC-free ceiling.** Every "win" in (a) is a win *relative to a
small heap*, and the small heap is itself the loss. The dominant strategy on this collector today remains
the one the timed runner already encodes: **size the arena past the window and do not collect at all.**

## 4. THE FULL MATRIX (median of 5, m3, `-O0`; `iters` = throughput, higher better)

| row | HEAP | BASE | BUDGET16 | BUDGET4 | verdict |
|---|---|---|---|---|---|
| `table_access` | 512 | **3328** (gc 1) | 1536 (gc 3) | 1664 (gc 8) | budget **halves** it |
| `table_access` | 64 | 1792 (gc 5) | 2048 (gc 28) | **3584** (gc 135) | budget **2.0×** |
| `array_sum` | 512 | **4608** (gc 1) | 2048 (gc 3) | 2560 (gc 13) | budget **−44%** |
| `array_sum` | 64 | **3584** (gc 6) | 3584 (gc 24) | 2816 (gc 69) | neutral → worse |
| `string_manip` | 512 | 1245184 (gc 0) | 1245184 | 1245184 | flat |
| `string_manip` | 64 | **1245184** (gc 1) | 1179648 (gc 4) | 1179648 (gc 12) | −5% (detax) |
| `eval_fixed` | 512 | 1769472 (gc 0) | 1835008 | 1835008 | never collects |
| `eval_fixed` | 64 | 1835008 (gc 0) | 1769472 | 1769472 | never collects |
| `string_pattern` | 512 | **2883584** (gc 0) | 2490368 | 2490368 | −14% (detax) |
| `string_pattern` | 64 | **2621440** (gc 3) | 2359296 (gc 13) | 2359296 (gc 53) | −10% |

**The knob helps in exactly ONE of ten measured cells** (`table_access` @ HEAP=64) and is neutral or
harmful in the other nine. `eval_fixed` never collects at either heap, so it prices nothing but the detax.

## 5. WHY THE HYPOTHESIS CANNOT PAY OFF YET — AND THIS IS THE STRATEGIC POINT

SPITBOL's small-region-often wins because **its regions genuinely compact**: a collection returns space, so
the next region is small and the next collection is cheap. Ours does not. s154's telemetry
(`pinned 1548` = nlive, `bytes 536870848->536870848 reclaimed 0`) is divergence 3 in the s167 ladder:
**every survivor is conservatively pinned, `fwd=self`, the slide moves nothing, `g_hp_top` never drops.**

That is the whole answer to why (3a) and (3b) disagree. Increasing cadence on a collector that reclaims
nothing buys **only** the O(heap)-per-collect saving from a smaller arena — and pays full mark + the
five-pass floor + full compaction bookkeeping each time for **zero reclaim**. The saving is real (3a) but it
is bounded by the arena you shrank, and shrinking the arena costs more than it saves (3b).

**Therefore the ordering in D-22 is not just convenient, it is load-bearing:** GC-R cannot be evaluated on
its merits until **GC-W1** makes mark O(live edges) and **GC-P1** de-foreigns the aggregates so `pz` fires
and a collection actually returns memory. `table_access` and `array_sum` — the two rows where cadence
mattered at all here — are precisely the TABLE/ARRAY programs s167 identified as **structurally locked out
of the precise mode that already exists** (`nforeign > 0` ⇒ `pz = 0` ⇒ conservative forever).

## 6. WHAT SHOULD CHANGE (no code touched this rung — these are for HQ to route)

1. **Do not expose `SCRIP_GC_BUDGET_MB` as a tuning knob.** It cannot be set without a 10–14% inline-allocator
   tax, and its trigger is gated on an arena-half-full precondition most workloads reach only near exhaustion.
2. **If the budget road is revived after GC-W1/GC-P1, decouple it from `g_alloc_detax` first** — the cadence
   trigger and the inline-alloc fast path have no reason to share a predicate. Until then no budget
   measurement is attributable.
3. **Consider the arena-half-full precondition a defect, not a policy.** A budget that means "every N MB"
   should mean that; as written it means "every N MB, but only in the top half of an arena sized elsewhere."
4. **Production guidance unchanged and now measured:** raising `SCRIP_HEAP_MB` past the working set beats
   every cadence arm tried (3840 GC-free vs 2944 best-budget on `table_access`). The timed runner's
   `HEAP=1024` default is correct and should stay.
5. **Re-run this rung after GC-W1 + GC-P1** with the detax control (`SCRIP_GC_STRESS=<huge>`) kept — it is
   the only way to read a cadence number honestly, and it costs one extra arm.

## 7. METHOD NOTE — WHY THE FIRST READING WAS WRONG

The first arm I ran said `BUDGET4` beat `BASE` by 1.75× at HEAP=64, cleanly outside a 7-run noise band
(BASE 1792–2304, BUDGET4 3456–3712, non-overlapping). That reading was **true and misleading**: it compared
two arms inside a heap size that was itself the problem, and it had no control for the detax. Adding the
GC-free ceiling row and the `gc=0` detax rows inverted the conclusion. **A non-overlapping noise band proves
a difference is real; it says nothing about what caused it or whether the baseline was worth beating.**

## 8. HANDOFF

Row 5 `gc-r-ab` DONE-WHEN met: A/B table in §4 (plus ceiling §3b and confound §1), knob verdict stated up
front. No code changed ⇒ no `.s` regen debt, no gate re-prove owed beyond the pristine build the numbers
were taken on.
