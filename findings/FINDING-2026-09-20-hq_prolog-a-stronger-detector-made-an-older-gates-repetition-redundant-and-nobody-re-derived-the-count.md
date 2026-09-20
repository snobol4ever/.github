# FINDING 2026-09-20 hq_prolog — LANDING A STRONGER DETECTOR MADE AN OLDER GATE'S REPETITION REDUNDANT, AND THE ITERATION COUNT WAS NEVER RE-DERIVED

**Measured** on SCRIP `ac1970678`, this root, 2026-09-20 by hq_prolog, while deciding where to wire
`test_gate_pl_atom_name_survives_a_collect_mid_operation.sh`.

## THE MEASUREMENT

On a build with this row's cure **reverted** (`prolog_atom.c` taking atom-name storage back onto the collected
heap via `rt_heap_strdup_c`), the gate goes **RED at ITERS=1 — 1 of 1 runs diverged, in BOTH modes.** Same at
ITERS=2 and ITERS=4. Detection is **deterministic**, not probabilistic.

| ITERS | mutated build | wall |
|---|---|---|
| 1 | GATE FAIL, m3 1/1 diverged, m4 1/1 diverged | 2s |
| 2 | GATE FAIL, m3 2/2, m4 2/2 | 1s |
| 4 | GATE FAIL, m3 4/4, m4 4/4 | 2s |

Against the healthy tree the same gate costs **778s at ITERS=20** (shipped arena) and **843s** under the tiny
arena, both green, 4 of 4 checks.

## WHY THE COUNT WAS 20, AND WHY THAT STOPPED BEING TRUE

The 20-run design is correct **for the world it was written in**. Before `SCRIP_GC_POISON` existed, the
collector was a sliding compactor that never overwrote what it vacated, so a dangling atom-name read returned
**the old bytes — still the correct string** until something allocated over them. An output comparison could
not tell that class from a correct one, and only repetition plus luck could catch it. The gate's own header
says exactly this, and it is still right about the mechanism.

`SCRIP_GC_POISON=1` fills the vacated tail with `0xDB`. A stale read is now **garbage on the first run**.

**The poison knob did not make the gate faster. It made the gate's REPETITION REDUNDANT** — and the iteration
count, which existed only to compensate for poison's absence, was never re-derived. It was landed in the same
sitting as the poison knob, by the same seat, and the connection was not made.

## THE CLASS

**When you land a stronger instrument, every older instrument's parameters that existed to compensate for its
absence become stale — and they stay stale because they still work.** A redundant parameter never fails, never
reds, and never announces itself; it only costs. This one cost **778 seconds per run** and was the sole reason
a green, high-value collector gate could not be wired into a blocking set whose most expensive arm is **90s**.

It is the sitting's fourth instrument reporting something true-when-written and false-now, and the first where
the staleness was introduced *by an improvement*:

1. clause 1's allocator **denylist** — read CLEAN after storage moved allocator names;
2. the cto's slot-kind census — **printed the count, swallowed the names**, two months;
3. `test-arena`'s `test_gate_gc_*` **name glob** — 8 collector gates invisible to the mandatory collector pass;
4. **this** — an iteration count made redundant by a better detector landed beside it.

## WHAT I DID WITH IT

The gate gains an explicit `--quick` form at **ITERS=2**, measured rather than chosen: 2 and not 1 because one
run has no margin, and this row's own history includes a witness that ran green in every configuration because
its switch was dead. The **full 20-iteration form remains the default** for a hand run and for a collector
landing; `--quick` is what the blocking set runs.

⛔ **NOT CLAIMED:** that ITERS=2 is sufficient for *every* defect this gate might ever catch. It is proven
sufficient for **the defect the gate was written against**, which is the only fail-once evidence anyone has for
any iteration count here — including for 20, which never had any.

**Folded into:** `GOAL-PROLOG-100.md` LIVE CURSOR 2026-09-20 and the baton for
`prolog-atom-names-live-in-71-c-locals-...`, same landing, because findings are deleted periodically.
