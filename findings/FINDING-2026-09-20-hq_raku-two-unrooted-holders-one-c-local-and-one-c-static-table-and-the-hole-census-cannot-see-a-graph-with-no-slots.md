# Two unrooted holders behind 36 silently-wrong raku programs, and the census that reads green over one of them

**hq_raku, 2026-09-20.** SCRIP `81c00a5be` + this landing, corpus `b3dd2932b`, `RT_OPT=-O0`, incremental `make`.
Every number below was produced by the runner or by gdb in this sitting; none is transcribed.

## The two families were two defects, as the baton predicted, and NEITHER is a frame-map hole

The raku master loses 65 gradings between a stress-unset control and `SCRIP_HEAP_MB=1 SCRIP_GC_STRESS=16`,
across 36 distinct programs, every one at rc=0 with no diagnostic. Both causes are the SAME CLASS wearing two
costumes: **a holder of collected-heap pointers that the collector has no way to reach**, one on a C stack
frame and one in a C static table. Neither is an unmapped *slot*; both are outside the frame-map vocabulary
entirely.

### Family 1, block method call (7 gradings, m3 only) -- a C LOCAL held across a re-entry

`__rk_arr_map` builds its result buffer with `rt_wsb_alloc` (the collected heap) and holds that `char *buf`
across `rt_call_proc_descr`, which re-enters the block's emitted code where the sanctioned poll fires. The
collector walks mapped frames keyed by return PC; **a C frame has no frame map**, so `buf` is unreachable by
construction for exactly the window the block runs in. Measured under gdb, not inferred:

```
BEFORE CALL  buf=0x7ffe6ce0b160
AFTER  CALL  buf=0x7ffe6ce0b160   bytes at buf: 0xdb 0xdb 0xdb 0xdb 0xdb 0xdb 0xdb 0xdb
```

`0xDB` is `gc_heap.c:1155` poisoning **vacated** space. The accumulator was not moved -- it was reclaimed out
from under the C frame, and the C local kept the stale address. Every later `memcpy(buf + p, ...)` writes into
a dead block and `*out = STRVAL(buf)` hands back a pointer to poison, which prints as `()`.

⭐ **THE DISCRIMINATOR, AND IT IS A ONE-INGREDIENT ABLATION WHERE THE INGREDIENT IS RESIDENCE.** `.reduce` and
`.map` are the same shape at the language level: same list, same block, same re-entry into emitted code. They
differ ONLY in where the accumulator lives. Measured with a breakpoint on `rk_iter_open`, reading its return
value: **reduce returns 1** (accepted onto the frame-mapped cursor road) and is **correct at every stress point
0..50**; **map returns 0** (declined, falls to the C-local road) and is **wrong at 1..16**. The previous
discriminator in the baton was `join`, which is correct because it never leaves the runtime at all -- that is
two variables, not one, and it could not have located the cause.

**Cure:** route map and grep through the cursor road that already carried reduce, so the accumulator is a DESCR
cell inside an already-visited block. No new global, no root range, no conservative visit, no collector change.

### Family 2, grammar parse (29 gradings, both modes) -- a C STATIC TABLE of heap strings, never visited

`gram_reg[]` (`by_name_dispatch.c:450`) is a file-static array whose `qname` and `body` are both
`rt_heap_strdup_c(...)`, i.e. **collected-heap strings**, and **no `*_gc_roots()` function visits it**.
Measured across the single collection the witness takes:

```
BEFORE COLLECT qname=[G::TOP] body=[ "a" ]   qname ptr=0x7ffeece06d50 body ptr=0x7ffeece06d70
AFTER  COLLECT qname ptr=0x7ffeece06d50 body ptr=0x7ffeece06d70   bytes at both: 0x00 x8
```

A C static table cannot be updated by a collection, so the pointers stand while their contents are gone.

⛔ **AND THE SYMPTOM WAS RECORDED WRONG FOR A DAY, IN THE DIRECTION THAT INVENTS A MECHANISM.** The baton and
three telegrams said this family "prints EMPTY where the ref is the match object". It prints **nothing at all**
-- `od -c` shows ZERO bytes, not an empty line, empty stderr, rc=0. The match box fails, the failure propagates
to the enclosing `say`, and **the statement never executes**. An output diff against a ref renders "a value was
computed and lost" and "no statement ran" identically, and only a byte count separates them.

**Cure:** visit both strings of every live `gram_reg` entry from `bnd_gc_roots`, the file's own existing roots
function, with `rt_gc_visit_raw` -- the same visitor the shield already uses.

## The instrument result, which outlives both cures

⛔⭐⭐ **A PER-SLOT HOLE CENSUS CANNOT SEE A GRAPH WITH NO SLOTS.** `gram__G__TOP` emits, registers a frame map,
and that map has **ZERO layout entries**: `frame_bytes=64 header_bytes=48 flags=8`, `GC-MAPTAB-LAYOUT n=0`, and
`FLAT_FRAME_ALLOWANCE` is `48 + 16`, so a 64-byte frame has a value region of exactly zero bytes. The coverage
arm confirms it from the other side: `words_scanned=0`.

Such a graph is **not** `no_layout` -- it has a map, so it is counted in `graphs=` and inside `graded=` -- and it
contributes 0 to `fields=` and 0 to `holes=`. It therefore passes every hole-counting instrument **by
construction**. On the same tree where this family was corrupt under every collection,
`test_gate_gc_raku_every_frame_slot_has_a_kind.sh` printed:

```
GATE PASS(0): 0 holes in every graded Raku and Rebus graph
PASS raku: entries=929 graded=922 no_layout=7 (declared=2 defect=5) graphs=1293 fields=19476 holes=0
```

**The gate is not lying** and that belongs on the record: its own population line reads *the zls region only;
the wire header past region_end and the spine are not censused here*. It answers a narrower question than its
headline, and the headline is what gets quoted. Censused by extraction of all 879 master entries and a frame-map
dump per entry: **33 zero-entry layouts in the raku master, every one a grammar TOP graph**, nothing else.

⭐ This is CEO-1025's own clause arriving one level deeper. That ruling split `no_layout` into NEVER-EMITTED and
EMITTED-WITHOUT-A-LAYOUT because a bucket that conflates them cannot answer NAME ONE MEMBER. A third shape sits
outside both: **EMITTED, MAP PRESENT, LAYOUT EMPTY** -- indistinguishable from full coverage to any consumer that
counts holes per slot, and mechanically detectable, since the census already knows each graph's entry count and
need only report the zero.

**Raku's own answer to CEO-1025, run rather than recalled:** all 7 `no_layout` entries are bucket (a),
NEVER-EMITTED, each an rc=1 compiler refusal -- `test_seq_op`, `benchmark_divide-and-conquer`,
`benchmark_rc-9-billion-names`, `benchmark_rc-perfect-shuffle`, `benchmark_rc-self-describing-numbers`, plus the
two already DECLARED (`class_method_range_replace_6`, `class_method_say_replace_49`). **Raku has zero entries in
bucket (b).**

## The band was path-contingent and I published it wrong

The baton, and three telegrams to other HQs, gave the map family's window as **stress 1-6, invisible at >=8**.
Re-measured at a **held and printed** path length of 27 bytes it is **1 through 16**, ok at 25 and 50. A lane
taking "invisible at 8" from me and probing at 8 would have read CLEAN over a live defect.

⭐ **A stress band is not a property of a language or even of a program -- it is a property of
(program, runner, path length), and a band printed without its path length is not reproducible.** After both
cures the path sensitivity is **gone**: map, grep and the grammar witness all read ok across 13 path lengths
(24-64 bytes) crossed with 8 stress points, 104 gradings each. So the 16-byte threshold was never a property of
the pathname -- **the path length only ever selected which allocation the collection landed on**, and once the
state it landed on was reachable there was nothing left to select. This retires the stronger "distance to the
critical poll" reading I sent three lanes, which hq_snobol4 had already falsified from the other end with a
witness that allocates almost nothing before its critical point and is path-invariant across 96 characters.

## Boards

| arm | m3_pass | m4_pass | n |
|---|---|---|---|
| control, shipped arena, before | 853 | 853 | 929 / 929 |
| stress 16, tiny arena, before (baseline `5418432bb`) | 817 | 824 | 929 / 929 |
| stress 16, tiny arena, after both cures | see SCORE.md | see SCORE.md | 929 / 929 |

⭐ **hq_prolog's VANISHED class, checked in this lane and NULL:** both arms graded `m3_n=929 m4_n=929`, equal
denominators, so no raku entry left the stress arm's record. No point of mine is green for having stopped
measuring. Their own 68 turned out to be a commit under a running board, not a collector effect.
