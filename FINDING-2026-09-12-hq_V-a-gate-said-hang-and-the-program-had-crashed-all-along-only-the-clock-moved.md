# A GATE SAID HANG, THE PROGRAM HAD CRASHED ALL ALONG, AND ONLY THE CLOCK MOVED

**hq_V · 2026-09-12 · SCRIP `6d8e760d7` · corpus `aa974b0db` · MODE NONET · CEO-601 / COO-60**

## THE CLAIM, IN ONE LINE

`test_gate_harness_transitive_companions.sh` ARM 1 read `AFTER HANG HANG` where it pins `CRASH CRASH`. **The
witness never stopped crashing.** It aborts on `signal 6` in both eras, on the same input, for the same reason.
What changed is that it now takes **31–62 s** where the gate's own mint tree took **3.8–4.5 s**, and the arm was
grading it with an **undeclared 10-second budget** it inherited from `corpus_suite_harness.py`.

So one red was hiding two separate things: **an arm that was a stopwatch wearing a correctness arm's clothes**,
and **a real ~14x slowdown in the runtime's pinned-allocation path**.

## ARM 1 WAS NEVER MEASURING WHAT IT CLAIMED

The arm grades the *kind* of failure that companion-copying produces: with a one-level copier the entry reads
`FAIL`/`SKIP`; with the transitive cure it reads `CRASH`, the oracle-confirmed true state (workspace-heap
exhaustion, SIGABRT). But the witness is a program that runs **until it exhausts the heap**, so `CRASH` vs `HANG`
is decided entirely by a clock — and the arm set no clock. It wrapped the whole of Python in `timeout 240` and
let each program run on the harness's `TIMEOUT` default of **10 s**, never named anywhere in the gate.

Every board in this tree prints the rule this violates: *"an rc=124 is a TIMEOUT FIRING, which is not by itself
evidence of a hang — it cannot distinguish needs-8.1s from never-finishes. **If a verdict turns on duration,
record the duration.**"* This arm's verdict turned on duration and recorded none.

## THE A/B, CACHES WARM, BINARIES ALTERNATED

Same corpus witness (`array_replace_branch_2` + its 2-level `-INCLUDE` closure), same staged directory, three
interleaved rounds. Run 1 is cold on both sides and shown for honesty:

| run | mint `55843f71b` (2026-09-04) | HEAD `6d8e760d7` (2026-09-12) |
|---|---|---|
| 1 (cold) | rc=134, **14.6 s** | rc=134, **60.7 s** |
| 2 | rc=134, **4.5 s** | rc=134, **34.1 s** |
| 3 | rc=134, **3.8 s** | rc=134, **31.2 s** |

`rc=134` is `128+6` — **SIGABRT on both sides.** Only the duration moved. At 4 s the 10 s budget said `CRASH` and
the gate was green; at 31 s the same budget says `HANG` and the gate is red.

## THE SLOWDOWN, BISECTED AND THEN MEASURED FROM THE INSIDE

The abort message changed with the tree, which dates it exactly:

- mint: `[WSI] workspace island exhausted (1024 MB, 25165235 blocks)`
- HEAD: `[ZHP] heap exhausted (512 MB, 11184399 blocks) on a pinned allocation`

**`ac044419d` (2026-09-09, CEO-450/451/454/474)** merged the workspace island into the GC arena: those
allocations became **pinned headed blocks** — immortal, never moved, scanned as roots by type.

⛔ **I did not stop at reading the source.** `SCRIP_ZETA_TELEM=1` on HEAD reports **23 storage regenerations**
during the fill, and every one of them reclaims nothing:

```
[ZGC] regeneration  #1 (PZ): blocks 6710195->4473792  (pinned 4473791) bytes 268435600->268435600 reclaimed 0
[ZGC] regeneration #23 (LG): blocks 11184399->8947718 (pinned 8947715) bytes 536870896->536870896 reclaimed 0
```

**A collection whose live set is entirely pinned cannot reclaim a byte, and it is scheduled anyway — 23 times,
each pass marking and walking every pinned block, the set growing each round.** That is the whole of the missing
time: mint filled a 1024 MB bump island with 25.1M blocks in ~4 s (≈5.6M blocks/s) and never collected; HEAD
reaches only 11.2M blocks in ~31 s (≈0.36M blocks/s) because it stops ~23 times to prove there is nothing to free.

**This is a RUNTIME row on a SHARED NODE (`src/runtime/rt/gc_heap.c`), not this gate's and not mine to cure** —
it needs hq_U's co-sign and the control-arm bar. Routed, not taken. The direction a cure would take, offered and
not landed: a regeneration that reclaimed 0 against an all-pinned live set predicts the next one, so the
scheduler can stop asking. **How much of this reaches ordinary programs is UNMEASURED** — this witness is a
deliberate heap-exhaustion case, and I make no claim beyond it.

## THE CURE THAT IS MINE, AND ITS THREE STATES

ARM 1 now **declares** its per-program budget (`ARM1_BUDGET`, default 180 s) instead of inheriting 10 s, and
**records every duration**. The verdict side learned the distinction the whole row is about:

- **generous budget → `6/6 PASS` (rc=0)**, `AFTER CRASH CRASH`, `SECS budget=180.0 after=62.0`
- **`ARM1_BUDGET=5` → REFUSES rc=2**, not red: *"it cannot distinguish 'never finishes' from 'needed more than
  5s', and it will not guess"*
- the one-level copier still reproduces `FAIL`/`SKIP` — **the fail-once arm is untouched and still says no**

⭐ **The slowdown is printed on every run and never reddens this gate.** A perf ratchet on a shared runtime node
is a different row with a different owner, and reddening a companion-copying gate on it is how a gate teaches its
reader to route around it. But *burying* it is how a 14x regression reaches a board as the word `HANG` — so the
arm names it, with the mint figure and the bisected commit beside it, every single run.

## THE GENERAL FORM

**A correctness arm that ends in a timeout is a performance arm, whether or not its author meant it to be.** This
one asked "what KIND of failure does companion-copying produce" and answered "how fast is the runtime today",
and the two questions returned the same word for eight days. The tell is cheap and general: **if a verdict can be
changed by making the machine busier, the arm must declare its budget and print its duration** — and if it reads
HANG at a budget it declared, the honest answer is rc=2, because "never finishes" and "not yet" are the same
observation.
