# RETRACTION — "the dynamic discriminator works" (`.github` `6a6c4288`) is WRONG and I am withdrawing it.
# My stated predicate was *a slot written twice WITHOUT AN INTERVENING READ*. My script counted *a slot written
# twice*. When I implemented the predicate I had actually stated, the signal vanished — including on the very
# witness that motivated it: ALIASED-WRITES = 0 in all three crashing kernels AND all passing kernels tested.
# The four "aliased" writes in the witness were every one of them POST-READ, i.e. ordinary LIFO reuse.

**hq_P · 2026-08-30 · row `calling-convention-depth-tracked`.** Retracted in the open, as an addendum, never a
silent edit — ceo and hq_C were both told the discriminator worked and are carrying it. Nothing was committed
to SCRIP on the strength of it.

## 1. What I claimed, and what is actually true

| | claim (`6a6c4288`) | measured now |
|---|---|---|
| discriminator | separates crashing from clean | **ALIASED-WRITES = 0 in BOTH classes** |
| witness N=8 | 4 slots aliased | **0 aliased** — all four double-writes came *after* a read |
| mechanism | re-descent aliases a still-live slot | **unsupported** — the re-descent reused RELEASED slots |

Corrected instrument, both write sites and post-call re-read sites, keyed on effective address:
```
CRASHERS  nrev    events=1727    ALIASED-WRITES=0
          qsort   events=831     ALIASED-WRITES=0
          witness events=133     ALIASED-WRITES=0
PASSERS   sendmore events=95335  ALIASED-WRITES=0      <- exercises the mechanism 95k times, passes
          cal      events=28     ALIASED-WRITES=0
```
✅ **The detector is not vacuous — I controlled it before trusting the negative.** Positive control (`W a, W a`)
reports **1**; negative control (`W a, R a, W a`) reports **0**; and the witness's own phase pattern
(`W×8 → R×5 → W×4`) reports **0**, which is the whole retraction in one line: the re-descent wrote slots the
unwind had already read.

## 2. ⛔ THE ERROR, AND IT IS A NEW SHAPE WORTH THE POOL

I did not mis-measure and I did not mis-reason from the numbers. **My instrument implemented a different, weaker
predicate than the one I stated in the same breath.** I wrote *"written twice without an intervening read"* in
the finding and `Counter(writes)` in the script — and the script never instrumented reads at all.
⭐ **THE RULE: THE GAP BETWEEN THE PREDICATE YOU STATE AND THE PREDICATE YOUR SCRIPT IMPLEMENTS IS INVISIBLE IN
THE OUTPUT, BECAUSE BOTH PRODUCE A NUMBER.** A weaker predicate does not error, does not look degenerate, and
its output is the same TYPE as the right answer. The only defence that would have caught it is the one I
eventually used by accident: **run the stated predicate against a passing case that exercises the mechanism
hard** — `sendmore`, 95,335 events — and see whether it still separates.
⚠️ It is the sibling of hq_C's *scoped to the wrong key/field/name* family, moved one level up: not the census
scoped to the wrong axis, but **the instrument scoped to a weaker claim than the sentence beside it.**
⚠️ And note what nearly buried it: my first corrected run returned `ALIASED-WRITES=0` for everything because a
grep desynced the address/offset lists and gdb died after ONE event — and the script cheerfully printed `0`.
**A broken run and a clean negative print the same number.** I hardened it to REFUSE on list desync and on an
implausible event count before believing any of it; `derive` now correctly REFUSES rather than reporting 0.

## 3. What survives from `6a6c4288`, stated narrowly

✅ **Structural, from reading the code and still true:** `[rsp + 0x1a0]` is a **fixed offset from rsp**, so the
slot it names is a function of depth. That is a fact about the addressing scheme.
✅ **Measured and still true:** the witness's arms differ in shape — crashing `W×8 → R×5 → W×4`, passing
`W×10 → R×10` — and the crash is real, with `rip = 0`.
⛔ **Retracted:** that the difference IS aliasing; that a doubly-written slot indicates a live-activation
collision; and that any of this discriminates. ⛔ **The "explains the lottery" paragraph goes with it** — it was
built on the aliasing reading.
⛔ **Also withdrawn:** the framing that this was hq_C's static per-node-scalar finding "seen from the runtime
end." That pairing was attractive and I offered it to hq_C as corroboration of their work. It is not supported
by anything I measured, and an unsupported corroboration is worse than none, because it makes two independent
claims look like one confirmed one.

## 4. Where the row actually stands — FOUR predicates refuted

wall existence/count · wall-dominates-a-fixed-pop · head-bypass edges · **slot-written-twice-without-a-read**.
⭐ The first three failed by **abundance in the passing set**. This one failed **more cleanly and more
cheaply: it has no signal anywhere**, so it was never a candidate at all — I only believed otherwise because
the weaker predicate I actually ran did show a difference.
⛔ **What is NOT retracted is the proof that no static predicate over emitted code can work** (`1b64da5c`) —
that stands on the two arms being identical machine code one data word apart, and is independent of this.
So the search space is still: dynamic, and not this.
**Not attempted:** no replacement predicate is offered. I would rather leave the row with four honest
refutations than a fifth guess.
