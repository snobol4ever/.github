# FINDING 2026-09-01 seat03 — co-expression thread stacks are GC-heap blocks, and the s262 PIN removal lets the compactor relocate them under a running thread

Row: `icon-n2-recursive-generator-per-activation-storage`. Measured on a `make pristine` build at SCRIP
`bcb0ec1e`, corpus `90582d05`, `RT_OPT=-O0`, after `git pull --rebase` on all three repos.

## THE HEADLINE, AND IT ANSWERS A QUESTION LON ASKED ON PURPOSE

`gc_heap.c:697` carries the note: *"TYPE-BASED PIN REMOVED (Lon s262: 'Completely remove the PIN path.
Let's see what breaks.')"*. **This is what breaks.** Co-expression thread stacks are allocated FROM THE GC
HEAP as `HB_ZBLK` blocks (`rt_coexpr.c:63`, `rt_gcheap_alloc((uint16_t)HB_ZBLK, total)`), so with the pin
gone the compactor slides a live thread's stack out from under it.

MEASURED AT THE CRASHING FRAME, not inferred — `print *h` inside `gc_collect_ex`'s move branch:

    $3 = {fwd = 140735519146192, size = 8400912, type = 204, flags = 3}     /* 204 == HB_ZBLK */
    #1 gc_collect_ex (cons_stack=1) at gc_heap.c:715
       else { memmove((void *)livef[i], (void *)h, (size_t)sz); ... }

An 8,400,912-byte (~8MB) co-expression thread stack, `memmove`d while a thread runs on it. That is the
whole mechanism. `HB_ZBLK` appears in `gc_heap.c` exactly once outside this path — `:640`, `nforeign++`,
which only forces `cons_stack=1`; nothing pins it any more.

## WHY THIS ROW KEPT MISSING IT

Four passes (seat08 ×2, seat14, seat07) chased the call-site region-LEA/push arithmetic. That thread was
real but is now closed, and the fix for it LANDED at SCRIP `d81d0444` (missing 5th stack word +
label-address depth seed). **The baton's `## NEXT` predates that landing and its NEXT ACTOR items 1-2 are
already done** — its ledger has no entry for `d81d0444`. The residue was never in the call-site arithmetic
at all; `geddump.icn`'s `gedsub` is apply-style self-recursion (`suspend gedsub ! push(f, x)`, geddump.icn:232),
which routes to a CO-EXPRESSION per activation:

    rt_call_apply_gen_h -> rt_call_value_gen_h -> rt_proc_call_gen_h(name="gedsub") ->
    scrip_coexpr_activate -> scrip_coswitch -> pthread_create        (one OS thread PER ACTIVATION)

so a self-recursive apply-generator spawns a thread per depth, and the first compacting collection with
enough of them live relocates one of their stacks.

## THE WITNESS IS NOW DURABLE (seat07 asked for this)

`corpus/tests/icon/coexpr_gc_stack_witness.icn` + `.ref` — 33 lines, no data file, oracle-graded
(`found=40`, byte-exact vs `/home/resources/icon-master/bin/icont`). Replaces a 250-line program plus a
24,431-line `.dat`. ⛔ **It crashes in the DEFAULT build — rc=139, no opt-in flag** — so this is a live
correctness defect, not an armed-path-only one. It is a loose pair in `tests/icon/` per the documented
`repro`/`probe_witness` precedent (`ALL.excluded.txt`: "left in place for inspection, NOT re-absorbed");
the only runner globbing that directory is the PARSER suite, which it passes.

Threshold measured by bisection: 15 outer iterations pass, 16 crash (~32 live coexpr threads, and the
crash is always on "Thread 33").

## THE CAUSE BEARS WEIGHT — TESTED IN BOTH DIRECTIONS, THEN REVERTED

Per RULES.md's TWO-PART PROOF, the repair the mechanism implies was derived and run (experiment only,
reverted, `git status` clean; patch preserved below):

    /* gc_heap.c:700, in the forwarding-address loop */
    if (h->flags & HBF_MARK) { if (h->type == HB_ZBLK && (char *)h >= dest) { h->fwd = (uint64_t)h; dest = (char *)h + h->size; nlive++; } else { h->fwd = (uint64_t)dest; dest += h->size; nlive++; } }

- CAN SAY YES: witness `rc=0`, `found=40`, byte-exact vs oracle.
- CAN SAY NO: unpatched, same build, `rc=139`.
- `geddump.icn` advanced from **0 bytes of output** to REAL GEDCOM output ("b. 21 Jan 1884 Tippah Co., MS")
  before failing later — the DONE-WHEN is measurably closer, still unmet.

## SECOND, INDEPENDENT DEFECT, EXPOSED UNDERNEATH (not a consequence of the patch)

With the stack no longer moving, both the witness and `geddump` hit the SAME next wall:

    #0 __pthread_getattr_np (thread_id=0, ...)
    #1 scrip_co_stack_of (ctx=...) at rt_coexpr.c:228

`scrip_co_stack_of` guards `ctx->stk_win` and `!ctx->alive`, but never that a thread was actually created,
so the GC's root walk calls `pthread_getattr_np(0)`. `scrip_coswitch`'s `first != 0` arm creates no thread
and sets no `stk_win`. A `ctx->thread != 0` guard is the obvious repair; NOT landed here, because it is
only reachable once the first defect is cured and an unverifiable patch is what this row has repeatedly
paid for.

## ⛔ WHY NOTHING WAS LANDED — THIS NEEDS LON, NOT A SEAT

The primary repair means RESTORING A PATH LON DELETED ON PURPOSE. Re-adding it silently would both override
his call and destroy the information value of the experiment he ran. His s262 question was "let's see what
breaks"; this document is the answer, routed to him rather than papered over.

⭐ AND THERE MAY BE A BETTER CURE THAN THE PIN, which is exactly why the ruling is his: RULES.md's storage
doctrine says activation frames live on the machine stack and only GENUINE ESCAPERS go to the heap, and the
s272 "workspace island" mmap store was DELETED with "NO mmap frame store may replace it". A co-expression
thread stack sitting in the GC heap as a relocatable block sits athwart that doctrine. Whether the answer is
(a) restore the type-based pin for `HB_ZBLK`, (b) move coexpr stacks out of the collected heap, or (c)
something else, is a design ruling, not a seat's patch. Both (a) and (b) are named here WITHOUT a
recommendation, per the meta-rule that a ruling names a destination and a seat greps that it exists.

## STATE OF THE ROW

- NEXT ACTOR items 1-2 of the current baton: **DONE at `d81d0444`**, before this pass.
- The named blocker `icon-apply-to-generator-segv-bb-call-value-has-no-n2-awareness` is **DONE**, and its
  simple witness (`gen ! [10]`) passes — but the SELF-RECURSIVE apply case it did not cover is still live.
- Minimal apply witnesses that DO pass, added context for the next actor: simple apply, self-recursive
  apply (depth 3), and a record-tree direct-recursive `suspend r | walk(!r.sub)` — all oracle-exact,
  including under `SCRIP_GC_STRESS=1`. The headline N-2 mechanism is sound; the residue is the GC/coexpr
  interaction above.
- DONE-WHEN re-verified fresh this pass (universal rule on this row): **rc=139**, and the signature has
  MOVED from the `rc=1 / Error 3` every prior pass recorded — evidence of `d81d0444`, not a regression.
