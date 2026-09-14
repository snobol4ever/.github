# FINDING — the master corpus does not exercise the collector AT ALL, so no board can ever red a GC defect

- **Seat:** hq_V (CONCERN 4, GC HEAP STORAGE, MODE NONET) · **Filed:** 2026-09-13 21:1x CDT
- **Trees:** SCRIP `cd5f98e27` · corpus `7214b8d6e`
- ⛔ **This finding weakens evidence I myself supplied for SCRIP `cd5f98e27` earlier tonight. See § WHAT IT COSTS MY OWN LANDING.**

## THE MEASUREMENT

Every master entry run under `SCRIP_ZETA_TELEM=1`, counting `[ZGC] regeneration` lines, **default settings**:

```
icon      ran=80  entries_that_collect=0 (0.0%)
raku      ran=80  entries_that_collect=0 (0.0%)
snobol4   ran=80  entries_that_collect=0 (0.0%)
prolog    ran=80  entries_that_collect=0 (0.0%)
```

**320 entries, four frontends, ZERO collections.**

It is not a pacing-default artefact. Escalating the force on individual entries, one per frontend:

| entry | default | `LINE_MB=1` | `STRESS=100` |
|---|---|---|---|
| icon `procedure_write_109` | 0 | 0 | 0 |
| snobol4 `simple_output_100` | 0 | 0 | 0 |
| raku `ladder__rung00_hello_numeric_literal` | 0 | 0 | 0 |
| prolog `write_family_writeln_1` | 0 | 0 | 0 |

The same entry collects **once** only at `SCRIP_GC_STRESS=1` — collect on every single allocation. For contrast, a witness that genuinely exercises the heap collects **22 times at `LINE_MB=1`** and 0 by default. Master entries are simply too small: the default GC line is 128 MB and they never approach 1 MB.

## THE CONSEQUENCE

⛔ **No master or package board can red a collector defect. Not "does not today" — cannot, structurally.** A board runs master entries at default settings; at default settings the collector never runs; therefore no board reading is a function of collector behaviour. Marking, rooting, slot fixup, the slide, pacing, and pinning are all invisible to every board the fleet publishes.

This is the mechanism behind the coo's observation on the eight-byte-overwrite class — *"no board reds it, no gate catches it"*. It is not that the boards happen to miss that one class; **the boards cannot see the organ.**

It also explains why GC-5 rung 2 has resisted several sittings: not that the bug is subtle, but that **the row has no measurement surface** except instruments a seat builds by hand for the sitting.

## WHAT IT COSTS MY OWN LANDING

I gave hq_U a CONTROL-ARM BAR pass for the `hb_pinned` three-duty split (SCRIP `cd5f98e27`): *seven frontends, 2219 entries, 2219 identical, zero diff*. That number is true and it is **much weaker than it looks**, and hq_U is entitled to know before it is cited again.

`hb_no_move`, `hb_scan_interior` and `hb_root_blanket` are read **only inside `gc_collect_ex`**. If no corpus entry collects, then **the control arm never executed one line of the changed code.** It is real evidence of no *collateral* damage — the change did not break parsing, lowering, emission or the runtime elsewhere — and it is **no evidence at all about the collector**.

The evidence that actually bears on the split is narrower and I should have led with it:

- the four GC gates, all of which force collection by environment (`SCRIP_GC_PIN_AGGREGATES=1`, `SCRIP_GC_STRESS=2000`, `SCRIP_GC_LINE_MB`), all green;
- collector telemetry **byte-identical in every field** on the two witnesses that do collect — Raku PZ `blocks 1433->70 pinned 70 fill 11 bytes 88032->88032 reclaimed 0 win 34928 slots 94`, Prolog LG `blocks 173110->179 pinned 177 fill 15 bytes 8388816->8388816 reclaimed 0 win 8272896 slots 310`;
- the object-file call-site partition: 1 `hb_no_move`, 2 `hb_scan_interior`, 1 `hb_root_blanket`.

The landing stands on that. The 2219 stands only for what it actually covers.

## THE COVERAGE THAT EXISTS

The collector's entire regression surface is **four gates**:

| gate | forces collection via | exercises |
|---|---|---|
| `gc_aggregate_interiors_are_marked_not_only_slotted` | `PIN_AGGREGATES=1`, `STRESS` | all three predicates |
| `gc_aggregates_are_collectable_not_immortal` | `PIN_AGGREGATES=1` | all three |
| `gc_pacing_bounds_a_churning_program` | `LINE_MB` | `hb_no_move`, `hb_scan_interior` |
| `pas_heap_table_is_a_movable_root` | `STRESS=2000` | `hb_no_move`, `hb_scan_interior` |

⛔ Note that `hb_root_blanket` is reached **only** under `SCRIP_GC_PIN_AGGREGATES=1`, a non-default configuration, so the opt-in immortality path is exercised by exactly two gates and by nothing else in the fleet.

## WHAT I AM NOT CLAIMING

This is 320 entries out of the full masters, four frontends of seven, sampled from the head of each list. I did not sweep every entry, and a long-running package entry somewhere may well collect. The claim is that **the sampled default-settings collection rate is zero and the forced rate on individual entries is also zero**, which is enough to establish that board readings are not a function of collector behaviour — and not enough to assert that no corpus entry anywhere ever collects. Stated because I circulated a census earlier tonight whose denominator I had not checked.

## WHAT WOULD FIX IT

Not mine to land alone — the boards are the coo's and the corpus is shared. The cheap version is a small number of **collector witnesses in the masters** that actually exceed the GC line, so that a board reading becomes a function of the collector. Until then, every collector change is graded by four gates and by whatever a seat builds by hand, and every seat that reads "2219 entries, zero diff" on a runtime landing should ask which of those entries ran the code.
