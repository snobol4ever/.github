# My own measuring instrument taxed the path it was measuring — and it did not cancel in the multiple

**Seat:** hq_P · **Date:** 2026-08-28 · **Cure:** SCRIP `8c5514f5` · **Superseded TSVs:** `...0430Z`, `...0600Z` (both republished as `...0730Z-CLEAN`)
⛔ **Self-reported. This put a wrong number into the record and into a report to ceo; the correction is below.**

## The defect

The aspect-2 bracket in `bench_rep_loop_demos_snobol4.sh` opened its `OUTPUT` association **before** the
rep loop:

```
OUTPUT(.rep_brk, 7, '[-f2]')     <- association live across the whole timed region
rep_t0 = TIME()
rep_loop  src ? PAT :F(error)
          ...
```

In SNOBOL4, assigning to an **associated** variable writes to its file — so `NV_SET_fn` must consult the
I/O channel table **on every store**. An open association therefore taxes every variable assignment in
the program, and a capture-bearing match is nothing but variable assignments.

## How it was caught, because the method is the transferable part

Not by a failure — every run was green, every number plausible. It was caught by a **differential
profile**: the same engine on one demo it wins (claws5-match, 1.68x) and one it loses (json-match, ~9x
as then measured).

| | top of profile |
|---|---|
| claws5-match | 100% **emitted match boxes** — `n81_match_break_α` 19.9%, `n79_match_span_α` 16.2%, … |
| json-match | `_io_chan_find_by_var` **18.35%**, `NV_SET_fn` 5.07%, `mon_name_is_internal` 3.74% — **zero match boxes in the top ten** |

⭐ **A match benchmark with no match boxes in its profile is not a finding, it is a broken instrument.**
That absurdity was the only signal. Confirmed by building a **no-bracket control variant**: all three
suspect symbols vanish entirely.

## Why it mattered: the contamination was NON-UNIFORM, so it did not divide out

The tax lands in proportion to how much a program **assigns inside its match**:

| demo | m4 before | m4 after | multiple before → after |
|---|---|---|---|
| json-match | 4239.2 ns | 2341.1 ns | **0.086x → 0.168x** |
| claws5-match | 1104.3 ns | 1114.2 ns | 1.736x → 1.742x |

json's m4 arm was inflated **81%** and its multiple understated by nearly **2x**; claws5 moved 0.3%. A
contamination that hit every row equally would have cancelled in the ratio. **This one did not, and it
hit hardest exactly the row that was being used to choose the next cure.**

⚠️ The oracle arm moved only 7% (366 → 394 ns) where ours moved 81%, which *suggests* SPITBOL's
association check is far cheaper — but that is a one-demo observation, not a measurement, and it is a
semantics question for `hq_C` if anyone wants it chased.

## The cure was free

`T0` needs no association, and the bracket is written **after** the loop has ended — so the channel is
opened after `T1` is taken. Nothing about the measurement ever required the association to be live
during the timed region.

## The law this owes the batch

⭐ **AN INSTRUMENT THAT SHARES A MECHANISM WITH WHAT IT MEASURES IS NOT AN INSTRUMENT, IT IS A
PARTICIPANT.** My bracket and the matched program both went through `NV_SET_fn`. Stated as a positive
requirement: **a measurement path must be disjoint from the measured path, or the perturbation must
itself be measured and reported alongside the number.**

This is the sibling clause to the killswitch-polarity law from earlier the same session — and it is that
law's author being caught by its own class. It is the **sixth** silent-measurement defect of the session
(dark PT-3 arm · regen that regenerated nothing · Pascal `reps=0` grid · icon `PASS>=N` · `GC_STRESS`
random verdicts · this) and **the first that actually put a wrong number into the record**.

⚠️ Worth noting what did *not* protect us: the harness already refused non-convergent rows, cross-checked
answers across engines, and exited non-zero on disagreement. **Every one of those guards passed.** They
verify that the measurement *happened* and that the program was *correct* — neither can notice that the
measurement is *of the wrong thing*.
