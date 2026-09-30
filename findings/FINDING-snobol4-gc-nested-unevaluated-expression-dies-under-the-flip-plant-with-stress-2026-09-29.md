# FINDING — a nested unevaluated expression in a pattern dies under the flip plant with stress 1: a root the collector never visited (cto, 2026-09-29, QUARTET CEO-1364)

**Found while witnessing bake layer 9** (the `*X` deferred reference opened by record). **NOT caused by it: identical on the untouched control tree SCRIP `d1f3ded8e`** (a scratch worktree built beside a corpus symlink) and on the layer-9 tree; the flip plant WITHOUT stress passes on both, and every non-plant arm (m3, m4, `SCRIP_GC_STRESS=1` and `3`) prints `sbl -b`'s answer.

## The witness (SNOBOL4, five statements)

```
        X = 'ab'
        P8 = *(X Y)
        Y = *(X 'q')
        X = 'p'
        'pq' P8                                 :S(OK12)F(NO12)
OK12    OUTPUT = 'ok12'                         :(N12)
NO12    OUTPUT = 'no12'
N12     OUTPUT = 'done'
END
```

`SCRIP_GC_PLANT_FLIP=1 SCRIP_GC_STRESS=1 ./scrip w4.sno` → rc 139 on both trees, before any output line:

```
[ZGC-STALE] SIGSEGV touching GC heap ground at <arena+163952> from instruction <libc.so.6+0x19b442> -- a STALE HEAP POINTER was used, not a wild address
[ZGC-STALE]   the block that lived here: #2457 kind=202 size=471040 at arena+0, +163952 into it -- it was RECLAIMED by collection #6 because nothing marked it, so the holder of this pointer was never visited either
scrip: fatal signal 11 (SIGSEGV) at pc libc.so.6+0x19b442 ... the page is mapped but protected against this access
```

kind 202 is `HB_FILL` (`gc_heap.h`): the plant copied every live block to disjoint ground and poisoned the old ground, so the faulting pointer is a PRE-PLANT address of something that lived in the first 471 KB of the arena, still held by a word the collector's root walk never reaches, and read by a libc call (memcpy/strlen-class) at the first collection after the copy. The fuller witness (13 `*expr` shapes, scratch w1) dies the same way at collection #425 after printing every earlier answer correctly, so the holder is on the NESTED road only: `P8 = *(X Y)` where `Y` holds a second unevaluated expression, i.e. `rt_defer_resolve`'s DT_X VALUE branch (`rt_call_open_staged` by name, the EXPR$n thunk's result read back through the stage variable) — item 3 of the ceo-1362 baton (the EXPR$ / DT_X redesign), which is where the cure belongs.

## Not yet done

- `SCRIP_GC_BIRTH_LEDGER=256` did not hold the block's birth (1335 births on w1, the ring overwritten): rerun with a larger ring to name the block's type and allocating site.
- A gdb breakpoint on the `[ZGC-STALE]` report to name the C frame that holds the pointer (the libc pc is the user, not the holder).

Row: `snobol4-gc-a-nested-unevaluated-expression-reference-holds-a-pre-collection-address-and-dies-under-the-flip-plant-with-stress-1` (minted by the cto 2026-09-29, rank 0; rows are assigned by the ceo under QUARTET).
