# Lon's priority-1 demos were not in the demo instrument at all — and the three that mattered measured 99% pattern compilation

**Seat:** hq_P · **Date:** 2026-08-28 · **Mode:** DUO · **Cure:** corpus `6f3022f63` · **Row:** Lon demo+pattern campaign (tier 1)

## The claim

`corpus/demo/snobol4/DEMO-SCALE.tsv` is the sanctioned scale table for the three-angle demo
triangulation. It held **five rows** — `claws5`, `treebank`, `json`, `calculator`, `beauty` — and
**not one of them was a `-match` or `-match-fence` twin**. `grep -c -- "-match"` returned **0**.

Those twins are exactly what Lon named **priority 1** ("pattern matching — the `*-match` and
`*-match-fence` demos and pattern matching in general"). Every number anyone had for them was
measured **by hand, off-board** — including `ceo`'s tier-1 dig.

⚠️ **The table is mine and the omission is mine.** I minted it on 2026-08-27 against Lon's *earlier*
in-chat pivot, which named those five programs literally. That was right then. It stopped being right
the moment the twins became priority 1, and nothing in the file or the harness could notice.

## The second half, which is worse than the absence

Adding the twins is not just filling in rows, because **the scale column is load-bearing for them in a
way it was not for the base five.** Measured match-phase share of total instructions at each demo's
**committed** input (m4, `-O0`, solving `I(s) = fixed + s·marginal` from two measured points):

| twin | match share at x1 | scale needed for 80% |
|---|---|---|
| calculator-1-match | 98.7% | 1 |
| calculator-2-match | 69.8% | 2 |
| **treebank-match** | **0.7%** | 556 |
| **claws5-match** (on `claws5.input`) | **0.3%** | 1396 |
| **json-match** (on the 84-byte `json.input` stub) | **0.0%** | 41418 |

Three of the six tier-1 programs were spending **~99% of their instructions compiling patterns** and
under 1% matching. **A match-path cure measured there reads as noise no matter how large it is.**

## Proof that the instrument was the variable, not the cure

Same binary pair (`SCRIP_PATV_FAST=0` vs `1`, the s168 PT-3 collapse), same program, same day — only
the input scale differs:

| demo | at committed input | at measured scale | |
|---|---|---|---|
| treebank-match | −0.75% | **−7.75%** | noise → real |
| treebank-match-fence | −2.13% | **−15.87%** | noise → large |
| json-match | **+0.51%** | −2.64% | **wrong SIGN** → real |
| json-match-fence | **+0.23%** | −2.40% | **wrong SIGN** → real |
| claws5-match / -fence | −0.29% / −0.54% | −0.85% / 0.00% | flat → flat |

⭐ **The json rows changed SIGN.** At the committed stub the cure read as a **regression**, from a run
that was 100.0% compilation and 0.0% matching.

⛔ **Read the claws5 rows correctly: they did not change, and that is the point.** Before, "flat" was
indistinguishable from "this instrument cannot see anything here." Now it is a measured statement that
claws5's match path does not lean on the PATV deferred-group mechanism. **A true negative you can
trust is a different object from a blind spot that happens to print zero.**

## Why this is the same defect as the dark cure, one level up

The companion FINDING tonight records a proven 1.41x cure that shipped default-OFF and sat dark for
eight days. **This is why nobody caught it**: the one board that would have shown `treebank-match`
losing 1.41x did not contain `treebank-match`, and at the input it would have used, the cure was worth
0.7% of the program anyway.

⭐ **A cure and the instrument that can see it are one deliverable, not two.** Landing a match-path
optimisation while the match-path board measures compilation is how you get eight days of green.

## The rows, and how they were chosen

Ten rows added. Scales chosen for **≥80% match share**, then capped by the **4 MiB record limit** every
one of these programs declares in its own `INPUT()` call. `claws5` at x32 = 2.14 MB is **verified to
run**; x64 = 4.27 MB exceeds the cap and dies, exactly as the base `claws5` row's note already said.

⛔ **The two json twins deliberately do not replicate their input** — concatenating N JSON documents is
not a JSON document. There the **file choice is the scale axis**: `citm_catalog.json` at x1 is already
86% match-dominated, where the 84-byte stub is 0%.

⭐ **All ten verified before landing, by the harness's own correctness signal and never by exit code**
(RULES.md: `sbl` returns rc=0 while printing ERROR 246 and an empty answer): scrip m4 and the clean
oracle each produce a **non-empty** answer and the two **agree**, at the listed scale. Row shape
validated too — 15 data rows, all 6 fields, every program and input path resolves.

## Recommendation

`bench_triangulate_demos_snobol4.sh --calibrate` should **refuse a row whose match share it cannot
raise above a floor**, rather than silently measuring startup. A scale column whose value nobody can
justify from a measurement is the same class as a guard keyed on a coincidence.
