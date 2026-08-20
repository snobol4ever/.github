# FINDING — s173 (seat `/home/claude5`, Claude Opus 5, queue row `gc-w2`) — GC-W2 WALK-FLOOR DIET: THE FLOOR IS **91% OF THE COLLECT**, THE FOLD **HALVES** IT, AND THE REMAINING TWO PASSES ARE A **STRUCTURAL FLOOR THAT CANNOT FUSE**

**Watermark:** SCRIP **`e1e7be15`** (rebased onto seats M1-R4b `aaf9d96b` and PT-3 `982f7b46`) · corpus untouched · `.github` this commit. **Rung:** D-22 GC-W2 (`GOAL-SNOBOL4-100.md`). **Killswitch:** `SCRIP_GC_WALKFOLD` (unset/non-`0` ⇒ FOLD, the new arm; `=0` ⇒ LEGACY, the five separate passes verbatim). **Touched:** `src/runtime/rt/gc_heap.c` ONLY — 33 insertions / 11 deletions, runtime `.so` only, **zero** emitter/template/lowerer files ⇒ `.s` blast is structurally zero. **RT_OPT `-O0`** (FACT RULE O0-DEV). **Net new globals: 0** — every census counter is a `gc_collect_ex` local, and the killswitch reader carries no cached static (deliberately: the file's neighbouring readers `legacy_env`/`blanket`/`cov` do cache, but GC-W1 landed at net −1 global and a per-collect `getenv` is free at collect granularity).

## 1. The instrument came first, and it re-priced the rung before a line of the diet was written

New per-collect census, `[ZGC-WALK]`, printed under `SCRIP_ZETA_TELEM` — every unconditional pass counted in titles AND timed in µs, so the floor is no longer inferred from source reading (which is all s167 had):

```
[ZGC-WALK] arm=… nblk=… | count=…/…us index=…/…us pmap-gran=… fwd=…/…us live=…/…us
           | mark=…us fixup=…+…/…us slide=…/…us moved=…B verify=…/…us
           | walk-floor=… titles …us of …us total
```

**One `array_sum` collect, LEGACY arm (= the shipping collector before this rung):**

| pass | titles | time | share |
|---|---|---|---|
| count walk | 5,592,406 | 51.5 ms | 18% |
| index + flag-clear + pmap | 5,592,406 | 72.7 ms | 26% |
| **mark (GC-W1 worklist)** | — | **24.7 ms** | **9%** |
| forwarding | 5,592,406 | 90.6 ms | 32% |
| live-array | 5,592,406 | 42.8 ms | 15% |
| slide (1 block, 0 B moved) | 1 | 0.001 ms | ~0% |
| verify | 2 | 0.003 ms | ~0% |
| **WALK FLOOR** | **22,369,626** | **257.7 ms** | **91%** |
| **TOTAL COLLECT** | | **282.4 ms** | 100% |

⭐ **This is the number D-22 was missing.** GC-W1 took mark from a whole-arena fixpoint to a worklist and the wall-clock gain was 0–10% — s169 correctly read that as *"the fixpoint was never the mass"* but could not say where the mass **was**. It is here: **mark is 9% of the collect and the unconditional walk floor is 91%.** GC-W2 was promoted on that inference; the census confirms it as measurement.

## 2. s167's census of the floor was short by one pass

s167 named five passes (count · flag-clear+index+pmap · forwarding · live-array, plus the fixpoint's rounds). **`rt_gcheap_verify()` at the tail of `gc_collect_ex` is a sixth unconditional full title walk** and was never in the ladder's cost model. It is *harmless on this witness* — it walks the **post**-collect heap (2 titles, 3 µs, because the collapse leaves almost nothing) — but it is O(surviving blocks) on every collect and would be visible on any workload that actually retains. Recorded here so the ladder's floor accounting is complete; **not** dieted in this rung (nothing to win on the measured witnesses).

## 3. What the fold does — and what it provably cannot do

**FOLD-A "index once."** The count walk existed only to size `g_gc_idxbuf` before the index walk filled it. It is deleted: the index walk grows the buffer by amortized doubling and publishes `g_gc_nblk` at its end. One full O(nblk) title chase gone.

**FOLD-B "forwarding + live-array fused."** The live-array pass re-read the `fwd` word the forwarding pass had just written, over the same `g_gc_idx[]`. The append moves into the forwarding pass itself (`gc_live_grow` on demand). One more full O(nblk) walk gone. Safe by inspection: the only code between the two passes is the cell/raw fixup, which reads `h->fwd` and writes `d->s`/`*loc` — it never mutates `fwd`, so the fused array is bit-for-bit the array the separate pass built.

⛔ **THE REMAINING TWO PASSES ARE A STRUCTURAL FLOOR, NOT REMAINING DEBT.** The index walk must complete **before** mark (it clears `HBF_MARK`/`HBF_PIN`, zeroes `fwd`, and builds the index mark itself navigates by). The forwarding walk must run **after** mark (it reads the marks). They are separated by the phase they exist to bracket and **cannot** be fused by any restructuring that keeps mark in the middle. **GC-W2 is therefore complete at its ceiling: 4 unconditional O(nblk) walks → 2, which is the minimum this collector shape admits.** Any future gain on the floor requires changing what a collect *is* (GC-P's territory), not how many times it walks.

## 4. D-22's third prescription — "pmap incremental" — is priced and DECLINED

Measured directly (throwaway build, fill skipped, probe hoisted out of the block loop after a first attempt put a `getenv` inside it and inflated **both** arms ~9×): index walk **76.4 ms with the pmap fill, 69.5 ms without** ⇒ the 1,048,576-entry rebuild costs **~6.8 ms, 3.3% of the collect**. And it is not free to remove: the pmap is the accelerator that keeps `gc_blk_of` O(1), and every conservative-scan word falls back to an O(log 5.6M) binary search without it. **Not worth a rung. D-22's GC-W2 line should be amended to "index once + forwarding/live fused"; "pmap incremental" is dispositioned here.**

## 5. Receipts

**A/B is one binary, two arms** (`SCRIP_GC_WALKFOLD=0` vs default) — no build pairing, so the HQ-21 stale-driver/`.so` class cannot apply. Independently confirmed: `nm ./scrip | grep -c gc_collect_ex` = **0** and `nm -D out/libscrip_rt.so | grep -c rt_gc_collect` = **1** — the driver carries no copy of the collector, both modes execute the fresh `.so`.

**THE DETERMINISTIC RESULT (exact, every run):** walk-floor titles **22,369,626 → 11,184,814** on one `array_sum` collect. Exactly half, because exactly two of the four unconditional O(nblk) walks are gone.

⛔ **THE PER-COLLECT µs FIGURE IS NOISE-DOMINATED AND MUST NOT BE QUOTED AS THE RESULT — I nearly did.** A first A/B read LEGACY 257.7 ms → FOLD 163.3 ms (−37%) and I drafted it as the headline. Re-measured on the same binary, the LEGACY arm alone swung **258 / 271 / 467 ms** across three consecutive runs — ~80% spread, wider than the effect being claimed. **A single collect's wall time on this box cannot resolve a 30% change.** This is the GC-W1 lesson in its second costume: there, a 28,315× count collapse bought 0–10% of wall; here, a genuine 2× count collapse was nearly published with a wall number the noise never supported.

**THE WALL GAIN, MEASURED THE WAY IT SURVIVES THE NOISE** — interleaved A/B/A/B pairs (never arm-blocked, so machine drift cancels within a pair), scoring the benchmark's own time-boxed throughput (`iters` in a fixed ~520 ms box), quantized to 512:

| witness | pairs won by FOLD | median LEGACY → FOLD | best-of-N |
|---|---|---|---|
| `array_sum` (6 cold + 6 warm pairs) | **12 / 12** | 6,144 → **9,216 (+50%)** | 7,168 → 9,216 (+29%) |
| `table_access` (4 warm pairs) | **4 / 4** | 3,328 → **3,840 (+15%)** | 3,328 → 4,096 (+23%) |

The first six `array_sum` pairs were taken on a cold box and drift upward in **both** arms (LEGACY 4,096→7,168 across them) — which is exactly why only the paired comparison and the warm block are quoted. **FOLD is ahead in 16 of 16 interleaved pairs across both witnesses; the direction is unanimous, the magnitude is 15–50%.**

**The intra-run decomposition in §1 is unaffected by any of this** — every pass there is timed inside one collect under one set of machine conditions, and the ratio reproduces: mark is **9%** of the collect in the LEGACY run and **13%** in the FOLD run; the floor is **91%** and **87%**. The floor's dominance is not a cross-run comparison and does not inherit the cross-run variance.

Semantics identical across arms: `blocks 5592406->1 (pinned 1, fill 1) … reclaimed 0 win=536870752` byte-for-byte, and `check: 250500` matches `array_sum.ref` in **both** arms.

⛔ **AND THE HONEST READ, IN GC-W1'S OWN IDIOM:** the collect got materially cheaper and `reclaimed` is **still 0**. `blocks 5592406->1 (pinned 1)` — one survivor, pinned, `g_hp_top` unmoved. GC-W2 makes a collect cheaper; it does not make a collect *productive*. **Divergence #3 (every survivor pinned) is now, on measurement, the largest thing left on the D-22 ladder — GC-P0/GC-P1, not another walk rung.**

## 6. Gates

- `test_gc_stress_suite.sh` — **ALL GREEN**, 8 rungs × 15 tests (`plain`/`STRESS=25`/`STRESS=7`/`STRESS=1` × m3/m4), incl. collect-every-alloc. RC=0.
- `test_corpus_snobol4.sh` — **m3 PASS=326 FAIL=11 · m4 PASS=323 FAIL=13 SKIP=1**, from a **pristine** build re-proven after the rebase onto seat M1-R4b `aaf9d96b`. Run in **both arms**: totals identical and the red set **identical program-for-program (13/13, both operands verified non-empty)**, so every red is pre-existing and arm-independent.
  - ⚠ **The m4 watermark MOVED and it is not mine:** s172 recorded 322/13/SKIP=2; this tree reads 323/13/SKIP=1, and the SKIP row changed from `omega_driver` to `132_pat_fence_eps_recur_shallow`. It reads **identically in both my arms**, so it is `aaf9d96b`'s effect (the M1-R4b shim-face dedup), not GC-W2's. Pre-rebase, on `1ac779ad`, my rung measured **322/13/SKIP=2 in both arms** — the s172 watermark exactly. **Routed to the M1-R4b seat to confirm and record; I am not claiming their +1.**
- `.s` blast — **0**, structurally: no emitter, template, `x86_asm.h`, or lowerer file is in the diff.
