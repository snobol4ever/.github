# FINDING — seat1, spine-carve-coalescing: the carve is free in the shape that actually occurs, and the census no longer reproduces

**Date:** 2026-08-21 · **Seat:** seat1 (`/home/claude1`, Claude Opus 5) · **Topic:** `spine-carve-coalescing` · **Status:** ⛔ STOPPED AT THE FIRST STEP AND ASKED, exactly as the row instructs. **No emitter code written.**

The row's first step was: reproduce the price and the census before writing code, and *"if either number differs materially, STOP and ask; the tree has moved."* **Both differ.** Probe checked in at `corpus/probe/carve/`.

## 1. The price — the carve is free behind two stores, and two is the real shape

`rdtscp` counts **TSC ticks, not core cycles**; calibrated on this box at **3.294 GHz** (the row assumed ~4.9 GHz, which is a second reason its ns figures do not map here). Best-of-9, 20M iterations:

| A/B shape | per-carve price |
|---|---|
| 8× `sub rsp,16` vs 1× `sub rsp,128`, **no stores** | 0.662 tsc = **0.201 ns** |
| same, **+1 store** per carve | 0.368 tsc = **0.112 ns** |
| same, **+2 stores** per carve — *the row's own specified shape* | **0.0019 / 0.0006 / −0.0082 tsc — indistinguishable from ZERO** |

The row predicted **0.24–0.35 ns/iter for 7 removed carves**, i.e. 0.79–1.15 tsc/iter at this box's TSC. Measured: **0.013 / 0.004 / −0.058 tsc/iter** across three independent runs. That is a 60–100× shortfall straddling zero, not a noisy agreement.

**Why, and it is not a mystery.** The two-store loop runs at **8.06 tsc/iter for 16 stores** — exactly 2 stores/cycle, the store-port throughput limit. The loop is store-bound, so the `sub rsp` retires in the shadow of the stores and costs nothing. `sub rsp,16` is a stack-engine operation with no dependent consumer; it only becomes visible when nothing else saturates a port.

⭐ **Reconciled against s249, and the divergence is the MACHINE, not the shape.** s249 §7C.1 specifies its microbench as *"8 chained `sub rsp,16`+2-store groups vs one `sub rsp,128` and the same 8 store pairs at re-based offsets — identical stores, identical final RSP, only the carve count differs."* That is byte-for-byte what `carve_pair.c` runs. So this is not a disagreement about method: the same experiment gives 0.24–0.35 ns/iter on HQ's box (Lon's Linux, ~4.9 GHz) and ~0 on this seat's (TSC 3.294 GHz), where the store ports saturate first. **The s249 price list's 0.17 cyc/carve is therefore a per-machine constant, not a portable one** — which matters for every future row that ranks an idea against that list before building it.

⛔ **This is decisive for the rung, because a SCRIP box writes a 16-byte DESCR result — literally two 8-byte stores per carve.** That is the measured-free column. `n1_lit_integer_α` is the canonical case: `sub rsp,16`, `mov [rsp+0]`, `mov [rsp+8]`. The row's own price list ("a carve is 8× an ordinary instruction") holds only for a carve that is *not* behind the DESCR write, and in the hot loop they all are.

## 2. The census — the hot-loop carve count reproduces exactly; the stretch decomposition does not

Criterion as stated: consecutive α-boxes each carving 16, no other rsp movement, γ jumping to the next box's α label.

| | row says | measured |
|---|---|---|
| hot loop carves | 12 | **12 ✅ exact** |
| hot loop removable | 10 | **8** |
| hot loop stretches / mean len | 2 / 6.0 | **3 / 3.67** |
| whole file carves | 82 | 83 |
| whole file removable | 52 (63%) | **42 (51%)** |
| whole file mean stretch | 2.73 | 3.00 |

The hot loop is the `ZBL` back-edge, `arith_loop.s` lines 358–559 (`n36_statement_begin_α`), 18 α-boxes of which 12 carve. It does **not** decompose into 2 stretches of 6: `n39_binop_α` and `n50_binop_α` each contain an `add rsp`, which disqualifies them as non-final members and splits the run into 3 + 5 + 3. The most likely cause is s249's own arith_loop work (**+41.9% throughput, 165 → 120 instructions/iteration**), which changed this file's box structure after the census was taken.

## 3. The β side — s249's claim CONFIRMED by tracing a whole chain, and a correction to my own first pass

s249 §7C states *"a `_β` label inside the stretch does NOT break it"*, and the row asks that this be verified on one concrete β before it is trusted generally. I traced the **entire** β chain of the longest stretch (`n43→n44→n45→n46→n47`, L=5, total carve 80):

```
n47_cmp_test_β:        add rsp,16  -> n46_coerce_numeric_β
n46_coerce_numeric_β:  add rsp,16  -> n45_coerce_numeric_β
n45_coerce_numeric_β:  add rsp,16  -> n44_var_β
n44_var_β:             add rsp,16
                       add rsp,16  -> n42_statement_begin_β      (16+16+16+32 = 80 ✅)
```

The total unwind is exactly the stretch's total carve, and — the load-bearing detail — **not one of these β boxes dereferences an `[rsp+K]` slot.** They only unwind and jump. So the *intermediate* rsp values, which the transform does change (at `n45_β` the original is 32-low where the transform is 64-low), are never observed. s249 is right, and the property that makes it right is "the β boxes are pure unwind-and-jump", which is worth stating explicitly because it is what a future stretch could violate. **A β box that reads a spine slot would break this transform silently**; the census should test for it rather than assume it.

⛔ **Correction to my own first pass.** I initially scored a stricter "single-exit" criterion requiring exactly one `jmp` per non-final member, and reported 6 removable. **That was over-conservative and the 6 is withdrawn.** `n45_coerce_numeric_α` and `n46_coerce_numeric_α` each contain two `jmp`s, but *both arms target the next box's α* — they are the converging arms of an internal branch, not a second exit. The correct hot-loop figure under a criterion that is both safe and accurate is **8 removable**, matching the row's own criterion; the row's 10 is still not reproducible, for the `n39`/`n50` `add rsp` reason in §2.

The α-side constraint I described does stand: a non-final member must not itself move rsp, because its own exit unwinds the `16*i` it was emitted for and would under-unwind by `16*(L−i)`. That is what disqualifies `n39_binop_α` and `n50_binop_α`, and it is the same rule as Lon's, reached from the offset arithmetic.

*(The offset-neutrality invariant checks out on the case the row named: `n2` reads `n1`'s slots at `[rsp+16]/[rsp+24]`, unchanged when `n1` pre-carves 32.)*

## 4. Projected payoff, three ways — all at or under the row's own abort floor

The row says: *"if it comes in under 2% say so and stop rather than pressing on."* Hot loop is 28.4 cyc/iteration.

| assumption | removable | gain |
|---|---|---|
| row's price (0.17 cyc), row's count (10) | 10 | ~6% — *the row's projection* |
| row's price (0.17 cyc), reproduced count (8) | 8 | ~4.8% |
| **measured** price (~0 behind 2 stores), count (8) | 8 | **~0%** |

The third row is the one built on measurement rather than assumption.

## 5. Recommendation

**Do not implement as specified.** The transform is correct and offset-neutral, but it removes an instruction that this box already executes for free in the only shape the hot loop contains. The honest expected gain is ~0%, below the row's own 2% floor.

If the idea is still wanted, the measurement points somewhere specific: carves *do* cost ~0.2 ns when the box is **not** store-bound. A census keyed on "carving boxes that write fewer than two stores before their γ" would find the cases where coalescing actually pays — but that is a different row with a different census, and I have not run it.

## 6. What was not done

No emitter change, no `.s` regeneration, no A/B benchmark run. `SCRIP` working tree clean. Checked in: `corpus/probe/carve/` (two microbenches, the census script, README) so the next session reproduces this in three commands instead of rebuilding the reasoning.
