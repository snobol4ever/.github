# FINDING — SCRIP pattern matching is **2.17x** and **0.304x** at the same time: the s255 oracle swap moved pattern kernels by **7.1x**, not the documented 2.2–3.5x

**Seat:** `hq_P` · **Date:** 2026-08-27 s277 · **Mode:** FLEET-4
**Trigger:** Lon, in-chat, challenging a relayed 0.55x patmatch figure: *"We have already determined that SCRIP pattern
matching is 2-3x faster than SPITBOL, for sure 1.5x faster. So you make no sense and your numbers must be wrong."*
**Verdict: Lon's number is CORRECT for the oracle it was taken against. So is the new one. Nothing is wrong except the
missing label.**

## The reconciliation

Instrument: **callgrind Ir at fixed work, SLOPE basis** (two runs per engine at N=1000 and N=11000; the slope cancels
startup *and* — for `./scrip prog.sno` — the compiler, both of which are constant in N). Outputs verified
**byte-identical** across all three engines before any number was taken. `-O0`. Axis: `× vs the named oracle`.

```diff
  kernel            scrip Ir/it   clean Ir/it   x64 Ir/it   vs clean   vs x64   oracle gap
- pattern_bt               5463          1663       11861     0.304x                 7.13x
+ pattern_bt                                                             2.171x
- string_pattern           2288           733        3059     0.320x                 4.17x
+ string_pattern                                                         1.337x
```

- **`clean`** = `/home/resources/spitbol-bench-oracle/sbl` (Lon's s255 benchmark oracle, `sbl_clean_bin()`)
- **`x64`** = `/home/resources/x64/bin/sbl` (the correctness oracle, `sbl_correctness_bin()`)

⭐ **`2.171x` and `1.337x` against `x64` is Lon's remembered result, reproduced today, to the decimal — including his
own hedge ("for sure 1.5x") landing between the two kernels.** The measurement was never wrong. The **reference
changed**, by Lon's own s255 ruling, and the number moved with it.

## ⛔ The part that is genuinely new, and it is a documentation defect

CLAUDE.md and RULES.md both state the handicap as **"~2.2–3.5x Ir"**. **On pattern kernels it is 4.17x and 7.13x.**
The monitor hooks (`sysmc`/`sysml`/`sysmv`) fire per pattern operation, so pattern-heavy code pays the handicap far
harder than the arithmetic/loop kernels the 2.2–3.5x range was presumably characterized on.

⭐ **This is exactly why the disagreement was possible.** Anyone applying the documented 2.2–3.5x to convert a
remembered pre-s255 pattern number would land at `2.171 / 3.5 = 0.62x` … `2.171 / 2.2 = 0.99x` — i.e. they would
conclude the two figures *still* did not reconcile, and go looking for a broken measurement that does not exist. The
real factor is 7.13x. **The documented range is not merely imprecise for this class, it is small enough to hide the
reconciliation.**

## Consequences

1. ⛔ **No pre-s255 pattern number can be converted by the documented range.** Re-measure, never rescale — and note this
   is the FACT RULE's own "a number carried into a NEW column must be re-measured, not copied", with a worked example.
2. ⭐ **Every quoted multiple must name its oracle**, not just its RT_OPT/mode/basis. The current FACT RULE list of
   shared axes says "the oracle + flags" — this finding is the evidence for why that entry is load-bearing rather than
   pedantic, and it should be the FIRST axis stated, not the last.
3. ⛔ **The honest current figure is `0.304x` / `0.320x`** — Lon's s255 ruling makes the clean oracle the benchmark
   authority, so that is what publishes. The 2.17x is history, and citing it today without the oracle label would be
   the same defect from the other side.
4. ⚠️ **ceo's relayed `0.55x` patmatch figure is neither confirmed nor refuted here.** Different kernel (his own, not in
   `corpus/benchmarks/snobol4`), different instrument (wall-clock TOTAL, single run). It sits between my 0.30x and 1.0x
   and should be re-taken on this instrument before anyone cites it.
5. ⛔ **`bench_triangulate_snobol4.sh` REFUSES to certify `pattern_bt` on wall clock:** `sbl` DISAGREE at **1.1724x**
   between angle 1 and angle 2 (tolerance 10%), verdict *"VOID: do not publish or cite"*. The harness was right to
   refuse — and that refusal is why the Ir instrument, not the wall-clock grid, settled this.

## Method note — why SLOPE, and why it is not optional here

TOTAL basis on these kernels is dominated by constant cost and would have given `0.080x` at N=1000 and `0.235x` at
N=11000 for the same code — **a 2.9x swing from the iteration count alone.** A TOTAL-basis pattern number is therefore
almost meaningless without its N, which is precisely the "a SLOPE is not a TOTAL, they may never share a column"
clause. Reported here as slope only.

## Transferable lesson

⭐ **When a remembered number and a fresh number disagree by a large factor, the first hypothesis should be "they have
different references", not "one of them is wrong".** Both parties here were measuring correctly. What failed was that
the multiple was carried in memory and in grids **without its oracle attached**, so two true statements read as a
contradiction — and the documented conversion factor was too small to reveal it. ⛔ A multiple without its reference is
not a weakly-labelled number; it is **not a number at all**.
