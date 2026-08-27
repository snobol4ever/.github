# FINDING 2026-08-27 hq_P — THE FIVE DEMO PROGRAMS, THREE-ANGLE: **0.250x–0.772x vs SPITBOL** AS WHOLE-PROGRAM TOTALS — AND THE INSTRUMENT LIED TWICE BEFORE IT TOLD THE TRUTH

**hq_P (Claude Opus 5), 2026-08-27, on Lon's in-chat PIVOT** — verbatim in substance: *"Get numbers for 3-angle performance numbers on all the demo programs. claws5, treebank, json, calculator, beauty. And keep the numbers for the README.md."*
Trees: SCRIP `f928c8ca`, corpus `96283343f`, `.github` `30ddc795`. `RT_OPT=-O0` (the only arm that exists — NO `-O2` BUILDS, Lon s262). Instrument: `tools/bench_rusage` **external** cpu(user+sys), never engine self-timing. Oracle: `/home/resources/spitbol-bench-oracle/sbl -bf` + per-row size flags. Law: `ARCH-BENCH-CAMPAIGN-README-TABLES.md § THREE-ANGLE TRIANGULATION`.

## ⛔⭐ THE BASIS, AND IT IS NOT THE KERNELS' BASIS — READ THIS BEFORE COPYING ANY NUMBER

A `benchmarks/snobol4` kernel exposes a `*BENCH kernel=NAME` entry point, so the harness loops it and its rate is a **SLOPE** with startup divided away. **A demo has no such entry point and no internal loop.** It reads stdin, does its job once, and exits. So here one "iteration" is **ONE WHOLE PROGRAM RUN**, and every number below is a **TOTAL carrying process startup AND the compile**.
⛔ **FACT RULE CONSEQUENCE: these totals may never share a column, grid, or sentence with a kernel slope.** Different instrument, different basis. The harness prints its basis in its own header so a pasted table cannot lose it.
⭐ Measured justification that the scaling exists at all: at x1 a demo run is **startup-dominated** — claws5 at **62x more input data** moved sbl only **2.0 ms → 2.4 ms**. Inputs are replicated to a per-demo scale so execution dominates.

## ⭐ THE NUMBERS — the README table (axis named once: × vs SPITBOL, faster axis, ≥1.00x ahead)

```diff
  demo         scale   m3       m4      angle1↔angle2   answer
- claws5        x16    0.761x   0.772x  AGREE           identical across all 3 engines
- treebank      x1024  0.285x   0.346x  AGREE           identical across all 3 engines
- json          x1     0.250x   0.406x  AGREE           identical across all 3 engines
- calculator    x4     0.349x   0.477x  AGREE           identical across all 3 engines
! beauty        x1     —        —       (see below)     ⛔ NO ORACLE — no multiple exists
```

Raw per-engine rates, both angles, are in `profile/demo-triangulation-2026-08-27-hq_P.tsv` (the never-redo record). Every measured row **AGREE**s: angle 1 (fixed 3 s budget, runs counted) and angle 2 (fixed 5 runs, cpu measured) land within 1.01–1.09 of each other, well inside the 15% floor. Angle 3 telemetry: `inblock=0` throughout; `oublock=8` on the three demos that write bulk stdout — reported, not folded into the verdict.

**m4 beats m3 on every demo that has an oracle** (0.772 vs 0.761, 0.346 vs 0.285, 0.406 vs 0.250, 0.477 vs 0.349) — consistent with m3 paying its compile inside the timed region while m4's compile+link sits outside it, per the kernel harness's own established protocol.

## ⛔⭐ BEAUTY HAS NO ORACLE COLUMN, AND THE FIRST TWO READINGS OF *WHY* WERE BOTH WRONG

1. Bare `-bf`: SPITBOL exits 1 with empty output. (What the s264 board recorded as `ORACLE_FAIL sbl rc=139`.)
2. With size flags it does **not** fail silently — it prints its **version banner** (`macro spitbol version 4.0f` / `x86-64 <date>`) in ~4.5 ms and stops, **never beautifying anything**.
⭐ So sbl's headline `210 runs/s` is *the speed of printing a banner*, and its answer digest is **not even stable run to run, because the banner carries a timestamp**. The board's `VOID-ANSWER` is correct and the row publishes no multiple. m3 and m4 both produce the real beautified output and agree with each other (digest `d193b7a64d00`); m4 is ~7x m3 here, but with nothing to compare against, **that is a note, not a result**.

## ⛔⛔⭐ THE PART WORTH KEEPING: MY OWN INSTRUMENT PRINTED TWO CONFIDENT, FALSE NUMBERS FIRST

**(1) A multiple was printed beside its own VOID verdict.** The first cut gated the multiple on *"did sbl produce something"*. It duly printed **`calculator m3 vs SPITBOL 14.673x`** and **`beauty m3 vs SPITBOL 0.001x`**. Both fiction: SCRIP had emitted **nothing** (ERROR 246) and was therefore very fast at it. ⭐ **The row said `VOID-EMPTY` two columns to the left and that did not stop the number appearing on the very next line** — so the suppression has to live where the number is **FORMATTED**, not where it is judged. A verdict a reader can skip past is not a guard. Cured: a multiple now requires both sides to have answered *and* to have answered **identically**; otherwise the line says so and prints no number.

**(2) I calibrated a scale on ONE engine.** calculator's x64 was chosen because *sbl* handled it (141,312 lines, 1.26 s). I never ran m3 there. That single omission is what manufactured the fake 14.673x. ⭐ **A scale is a property of the SLOWEST/WEAKEST engine in the row, never of the oracle.** Cured: `DEMO-SCALE.tsv` records the measured ceiling *and* which engine set it.

**(3) Exit status is not a correctness signal here — measured.** The clean oracle prints `ERROR 246 -- stack overflow`, emits an **empty** answer, and **still exits 0**. Any harness trusting `rc` would have published a fast, confident, wrong row. The gate is cross-engine **output agreement**; `EMPTY` is never a pass.

## ⛔ A REAL COMPILER DEFECT FELL OUT OF THE CALIBRATION — SCRIP'S STACK CEILING, AND AN INERT FLAG

On `calculator-1.sno`, **SCRIP answers at x4 and emits nothing (ERROR 246) from x8 up, while SPITBOL answers correctly to x64** — an **~8x lower capacity** on the same program and input.
⛔ **And SCRIP's own SPITBOL-compatible stack flag does not raise it:** `scrip --run -s256m -m8m …` and `-s512m` both still die with ERROR 246 (`-s` is *accepted*, so it fails silently as a no-op). Flag-order note recorded while testing: `scrip -s256m -m8m --run prog.sno` fails with `scrip: cannot open '--run'`.
⭐ This is why calculator publishes at x4 and not at SPITBOL's ceiling — the row is honest rather than flattering, and the gap is **named here instead of buried in a benchmark note**. Row-worthy on its own: a capacity limit with an inert control beside it is two defects, not one.

## DURABLE TOOLING (Lon's standing "never redo this from scratch" clause)

- `SCRIP/scripts/bench_triangulate_demos_snobol4.sh` — the demo harness. Refuses `rc=2` (never a plausible empty table) on unbuilt scrip, missing/non-`-bf` oracle, stale `bench_rusage` lacking inblock/oublock, or missing scale file. `--check-shape` proves the mechanism on one demo without touching committed data.
- `corpus/demo/snobol4/DEMO-SCALE.tsv` — per-demo scale, each with its **measured** ceiling and the reason, never a round number.
- `.github/profile/demo-triangulation-2026-08-27-hq_P.tsv` — the raw readings.

## WHAT THIS DOES NOT SAY

⛔ It does not reconcile with `FINDING-2026-08-21-s199` (claws5 pattern match at 1.35x) or with the 2026-08-27 rivals grid (`patmatch 0.55x`). Those are **slopes on different instruments**; these are totals. Three numbers about "claws5" that do not share a basis are not in conflict — they are not comparable, and forcing them into one column is the error this FINDING's header exists to prevent.
