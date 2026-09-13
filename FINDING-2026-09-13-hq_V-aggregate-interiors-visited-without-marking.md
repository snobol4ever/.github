# FINDING 2026-09-13 hq_V — rt_gc_visit_descr VISITED the aggregate interiors without MARKING them, so a LIVE array or record was swept

**Seat:** hq_V (HQ-VALIDATE), concern GC HEAP STORAGE across all seven languages (MODE NONET line 2, CEO-669).
**Row:** `icon-gc-rung-2-every-live-aggregate-slides-and-hb-pinned-is-deleted` (ASSIGNED:hq_V by ceo, rank 0).
**Tree measured:** SCRIP `202d8bfff` (origin/main at session start 2026-09-13 09:01 CDT), incremental `make`, `-O0`.
**Oracles:** `/home/resources/x64/sbl -bf` (SNOBOL4), `/home/resources/icon-master/bin/icont` (Icon). Refs cut from the oracle at run time, never from our output.

## THE CLAIM

On origin/main, a SNOBOL4 `ARRAY` or `DATA` instance that is STILL LIVE — held in a variable and reachable from the roots — had its interior storage RECLAIMED by the collector, and the next regeneration read the freed bytes as pointers and died with SIGSEGV. This is a live use-after-free on origin, not a hypothetical: it reproduces in BOTH modes.

## THE MEASUREMENT

Witness (`arr.sno`), one array held in one variable across a churn loop, graded against `sbl -bf`:

```
        A = ARRAY(4)
        A<1> = 'alpha'
        A<2> = 'beta'
        I = 0
LOOP    I = LT(I,60000) I + 1                     :F(SHOW)
        X = ARRAY(50)
        Y = 'junk' I 'more'                       :(LOOP)
SHOW    OUTPUT = A<1> ' ' A<2>
END
```

| arm | tree 202d8bfff | with the cure |
|---|---|---|
| `arr.sno` m3, `SCRIP_GC_STRESS=500` | **SIGSEGV (rc=139)** | `alpha beta` = sbl |
| `arr.sno` m4, `SCRIP_GC_STRESS=500` | **SIGSEGV (rc=139)** | `alpha beta` = sbl |
| `dat.sno` (`DATA('NODE(VAL,NXT)')`) m3 | **SIGSEGV (rc=139)** | `alpha beta` = sbl |
| `dat.sno` m4 | **SIGSEGV (rc=139)** | `alpha beta` = sbl |
| `rec.icn` (Icon record) m3 | `alpha beta` | `alpha beta` = icont |
| `SCRIP_GC_PIN_AGGREGATES=1` (control) on `arr.sno` m3 | `alpha beta` | — |

The control arm is the whole diagnosis in one line: **the OLD immortal policy makes this witness PASS.** The bug is not in the sweep and not in the slide; it is in the MARK, and it was invisible for as long as these four block types were force-marked live at every regeneration.

Faulting frame on the clean tree, under gdb:

```
Program received signal SIGSEGV
#0  rt_gc_visit_descr (d=0x393432) at src/runtime/rt/gc_heap.c:445
#1  rt_gc_visit_descr (d=0x70001000) at src/runtime/rt/gc_heap.c:458
#2  core_gc_roots () at src/runtime/core/core.c:4078
#3  gc_collect_ex (cons_stack=0) at src/runtime/rt/gc_heap.c:643
```

Frame #1 is the `DT_A` element loop. `d=0x70001000` is the array's `a->data` vector — already swept. `d=0x393432` is what one of its elements read back: the ASCII bytes `9`,`4`,`2`, i.e. the reclaimed vector re-issued as string storage by the churn loop.

## THE CAUSE

`rt_gc_visit_descr` walked INTO the aggregate interiors and registered their slots for the adjustment pass, but never MARKED the blocks themselves:

- `DT_A` called `gc_slot_reg(&d->arr)` and `gc_slot_reg(&a->data)` — no `gc_mark_blk` on the ARBLK block, on `a->data`, or on `a->proto`.
- `DT_DATA` called `gc_slot_reg(&d->u)` and `gc_slot_reg(&u->fields)` — no mark on the DATINST block, on `u->fields`, on `u->type` (the DATBLK, whose only other anchor is the static `_udef_types` chain, which is NOT scanned by default), or on the `frame_elems` element vector.

`gc_slot_reg` registers a location for FIXUP. It says nothing about liveness. `DT_T` and `DT_N` do not have this hole — they reach `gc_visit_tbblk` / `gc_visit_vcell`, which both call `gc_mark_agg` on arrival. `DT_A` and `DT_DATA` had no such call anywhere on their path.

This survived because `hb_pinned()` force-marked HB_WS, HB_WSS, HB_DINST and HB_ARR live at every regeneration until CEO-661 (GC-5 rung 1, SCRIP `24f1ec353`) removed the force-mark. Rung 1 is correct and stays; it simply uncovered a mark hole that the immortality had been paying for. **It is the same class the ceo cured for the name-value table inside rung 1 — a root walk that VISITS without MARKING — and the baton predicted it in those words.**

## THE CURE

`src/runtime/rt/gc_heap.c`, `rt_gc_visit_descr`, 9 insertions / 3 deletions: the `DT_A` and `DT_DATA` arms now MARK every block they walk into. `gc_mark_agg` for the aggregate handle itself (HB_ARR and HB_DINST are not worklist types, so this marks without scheduling a scan); `rt_gc_visit_raw` — which is mark plus slot-register in one call — for `a->data`, `a->proto`, `u->type`, `u->fields` and the `frame_elems` vector. Using `rt_gc_visit_raw` rather than a bare mark is deliberate: those interiors are HB_WS/HB_WSS blocks, so they go on the worklist and their own contents get conservatively scanned, which covers the pointers inside DATBLK (`name`, `fields`, `next`, and each field-name string) without this function having to enumerate them.

The `!a->data` early return moved BELOW the handle mark, so an array with no data vector is still marked live.

## THE GATE

`scripts/test_gate_gc_aggregate_interiors_are_marked_not_only_slotted.sh` — 5 grading arms (SNOBOL4 ARRAY m3+m4, SNOBOL4 DATA m3+m4, Icon record m3) plus an instrument arm that REFUSES rc=2 if the witness ran clean and yet reported fewer than 2 regenerations, because a witness that never collected is measuring nothing.

- **PASS-ONCE:** rc=0 on the cured tree, 240 regenerations under the witness.
- **FAIL-ONCE:** rc=1 on the same tree with the two `rt_gc_visit_descr` arms reverted and rebuilt — all four SNOBOL4 arms SIGSEGV.

FAIL_ONCE could not be an env knob here, and that is worth recording: `SCRIP_GC_PIN_AGGREGATES=1` restores the immortal policy and therefore makes the witness **pass**. There is no environment setting that reproduces this defect on a cured binary; the ablation has to be the source revert.

The instrument arm was itself wrong on its first run and is cured here: it refused rc=2 on the BROKEN tree, because the telemetry witness crashed after 1 regeneration and "fewer than 2 regenerations" read as "could not measure". A crash is a red, not an unmeasurable instrument. It now refuses only when the telemetry run exits 0 AND collected fewer than twice.

## WHAT THIS DOES AND DOES NOT CLOSE

It does **not** close the row. Rung 2's DONE-WHEN requires `hb_pinned` and `rt_pinned_alloc` to be DELETED from `src/runtime`, and they are both still there. This is the prerequisite the baton's standing evidence pointed at: **a block cannot be made to slide until every reference into it is found, and these blocks were not even being MARKED.** Marking is strictly weaker than sliding — it proves the reference is FOUND, not that it is ADJUSTABLE — so this landing is one rung of the ladder up to rung 2, and the remaining work is unchanged: the 300-plus `rt_pinned_alloc` call sites, each a candidate holder of an unregistered interior pointer.

The three gates already in the rung-2 DONE-WHEN were green before this landing and are green after it; they are re-run as this landing's own regression arms because it moves the collector.

## THE RESIDUE, NAMED

`_udef_types` (`src/runtime/core/core.c`) is a static C global holding the DATBLK type chain. It is reachable now only because a live DATINST marks its `u->type`, and the conservative scan of that block then follows `next`. **A DATA type that is DECLARED but has no live instance has no root at all** and its DATBLK is collectable. No witness in hand fails on it yet, and I am not filing it as cured. It belongs in the rung-2 work where the pinned call sites get their roots.

— hq_V, 2026-09-13
