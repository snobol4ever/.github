# FINDING — RUNG C-0: cured at `-O0`, ⛔ **STILL BROKEN AT `-O2`** — and the instrument that was about to prove otherwise was blind

> ⛔ **TITLE RETRACTED IN PART.** This finding first read "Milestone 1 is not regressed at HEAD". That is true **only at `-O0`**. At `-O2` beauty self-host emits 278 bytes in both media. See "THE `-O2` RESULT LANDED" below. Lon called this from memory before it was measured.

**Seat:** `hq_C` (HQ-CORRECTNESS) · **Date:** 2026-08-22 · **SCRIP HEAD measured:** `457dc5d9` · **⛔ RT_OPT: `-O0` (see the RT_OPT CAVEAT below — the `-O2` arm is unmeasured and Lon remembers it broken)** · **Class:** MEASURED (every number below carries the command that produced it)

## THE HEADLINE

**RUNG C-0 — the #1 rung, "nothing outranks it" — does not reproduce at HEAD.** Beauty self-hosts to its exact fixed point in **both** media. The 278-byte "Parse Error on START" stub is real, reproducible, and **already cured**; the board simply never caught up.

| tree | arm | bytes | md5 | verdict |
|---|---|---|---|---|
| `cd13321e` and its parent | m3 | **278** | `1c75f97d1907f92f4c0a8a3ef49eb9ee` | ⛔ Parse Error on START |
| `457dc5d9` (HEAD) | m3 | **40,971** | `6f1671c0757729992ae01a6bdf16f081` | ✅ FIXED POINT |
| `457dc5d9` (HEAD) | m4 | **40,971** | `6f1671c0757729992ae01a6bdf16f081` | ✅ FIXED POINT |
| the source (= the oracle, Lon s117) | — | 40,971 | `6f1671c0757729992ae01a6bdf16f081` | — |

278 bytes is the sovereign file's documented C-0 signature **to the byte**, so the harness demonstrably reproduces the defect (twice, at two different commits); it reports the fixed point at HEAD from the same harness, same pinned source, same working directory. **m3 ≡ m4 holds. The DESIGN-INVARIANT violation is closed.**

The live *converted* beauty (`corpus .../beauty.sno`, 41,492 B) also self-hosts to **its** own fixed point at HEAD (`006850eb4e1ff2d0f7afc1aac2671b65`), so both grammars are healthy.

```bash
bash .github/probes/m1-bisect/check_m1_fixedpoint.sh both      # exit 0 at HEAD — this is the M1 DONE-WHEN
```

## THE CURE IS IN `cd13321e..457dc5d9` — AND HQ'S OWN PRIME SUSPECT WAS **DISPROVEN**

`GOAL-HQ-COMPLETE.md` carried an explicitly-unmeasured hypothesis: `62017f8a` split `DTYPE_t v` so bits 8–31 stopped belonging to `v`, while the tree still DWORD-tested that word against `DT_NOTSTR_MASK` — making **a string test read as not-a-string**, which would break beauty "first and loudest" because beauty is pure string work.

That made **`cd13321e rung-descr-stamp-notstr-mask: narrow the three DT_NOTSTR_MASK string-family tests to 8-bit`** (seat12's row) the obvious cure, and this FINDING asserted it was — until the build finished:

| tree | bytes | verdict |
|---|---|---|
| `cd13321e^` (parent) | 278 | ⛔ broken |
| **`cd13321e`** (the predicted cure) | **278** | **⛔ STILL BROKEN — byte-identical to its parent** |
| `457dc5d9` (HEAD) | 40,971 | ✅ fixed point |

⛔ **So the notstr-mask narrowing did not fix beauty.** The hypothesis was plausible, specific, mechanically argued — and wrong. It is recorded here as DISPROVEN rather than quietly dropped, because the next seat to read the sovereign file would otherwise inherit it as a lead and re-derive a dead end. (The narrowing may still be correct and necessary work; what is disproven is only that it cured C-0.)

**⭐ THE CURE IS `6ba28e5e`** — *"descr-stamp-asm-mints: census + zero-cost mod_op stamp on 29/30 sites, **two latent 32-bit-tag-compare defects found and fixed**"*. Named by `git bisect run` over the repaired inverted probe (4 probes, `cd13321e`..`457dc5d9`); in an inverted bisect git's "first bad commit" is the first commit that WORKS, i.e. the cure.

⭐ **So HQ's hypothesis was right about the MECHANISM and wrong only about the COMMIT.** The hypothesis named mixed-width reads of the `DESCR_t` tag word after `62017f8a` split it; "32-bit-tag-compare defects" is precisely that class. `cd13321e` (narrow three `DT_NOTSTR_MASK` tests to 8-bit) was **necessary but not sufficient** — beauty still emitted 278 bytes after it. `6ba28e5e` fixed two *further* latent 32-bit tag compares, and that is the commit where beauty comes back. Neither seat knew they had closed Milestone 1: `6ba28e5e`'s own message reports the two defects as incidental findings of a census.

⭐ **This is also why the bisect needed a second, inverted probe.** git's vocabulary is fixed — "good" is the OLD state, "bad" the NEW one — but here the old state is broken and the new one works. Run uninverted, git labels HEAD good and the base bad, contradicting the declared bounds, and the run is meaningless. `bisect_probe_m1_findfix.sh` inverts the exit code so git's reported "first bad commit" IS the cure.

## ⛔ THE INSTRUMENT WAS BLIND, AND ITS OWN SMOKE TEST SAID SO

This is the more transferable half, and it is LAW 0 species (3), BLIND INSTRUMENTS, on the tool built to hunt species (2).

`beauty.sno` pulls **16 `-INCLUDE` files** that resolve **relative to the working directory**. Run the pinned source from anywhere but the beauty directory and every arm emits **zero bytes** with `cannot open include 'global.inc'` — a failure with nothing to do with the code under test.

seat01 caught a *first* corruption in the HQ-spec probe (it read the live corpus `beauty.sno`, which `53dd9ac0` had converted to a grammar needing `dac65d47` — a commit postdating the entire bisect range, so every pre-`dac65d47` commit would read BAD). That catch was correct and valuable. But the corrected probe **kept the same defect through a different door**: it ran the pinned source from a directory with no `.inc` files.

**The smoke test contained the disproof and the expectation absorbed it.** seat01 recorded: *"Smoke-tested at current main HEAD (457dc5d9): reads BAD as expected (rc=1, empty output)."* The documented symptom is **278 bytes with a Parse Error** — not empty output. `0 ≠ 278`. Had `git bisect run` been launched, **every commit would have read BAD** and the bisect would have converged, fast and confidently, on the GOOD boundary — a precise, fully automated, entirely false answer, produced by a tool built specifically to avoid false answers.

⭐ **The generalisation, and the reason this is written down:** *"BAD as expected" is not a measurement — it is a prediction that happened to match a number nobody compared.* A probe must assert the **shape** of the failure it expects, not merely its polarity. `check_m1_fixedpoint.sh` now prints an explicit callout when it sees 0 bytes (include path) and when it sees 278 (the known C-0 signature), so neither can ever again be read as generic BAD.

## THE INSTRUMENTS, RESCUED AND NEGATIVE-TESTED

Both existed **only in a seat's `/tmp` scratchpad**, which dies with the session; they are now in version control at `.github/probes/m1-bisect/`, root-portable (seat01's copy hardcoded `/home/claude01` three times, so no other seat could run it).

- `beauty_classic_fixedpoint.sno` — the pinned CLASSIC source, 40,971 B, md5 `6f1671c0757729992ae01a6bdf16f081`.
- `bisect_probe_m1.sh` — for `git bisect run`; carries the full provenance of both corruptions.
- `check_m1_fixedpoint.sh` — **the M1 DONE-WHEN as one command.** `cd`s to the beauty dir itself so the include trap cannot recur.

**Negative-tested (a gate that cannot say NO is not a gate):** exit 1 on a non-fixed-point source; exit 1 with the include diagnosis on a wrong CWD; and 278 bytes at `cd13321e^` **and** `cd13321e` from the same harness that reports 40,971 at HEAD.



## ⛔⛔⛔ THE `-O2` RESULT LANDED: C-0 IS **OPEN**. LON'S MEMORY WAS CORRECT AND THIS FINDING'S TITLE IS RETRACTED

**Measured, SCRIP `3f951354`, `RT_OPT="-O2 -g -fno-strict-aliasing -fwrapv -fno-omit-frame-pointer" make pristine`, pinned classic source, run from the beauty directory:**

| arm | RT_OPT | bytes | md5 | verdict |
|---|---|---|---|---|
| m3 | `-O0` | 40,971 | `6f1671c0757729992ae01a6bdf16f081` | ✅ FIXED POINT |
| m4 | `-O0` | 40,971 | `6f1671c0757729992ae01a6bdf16f081` | ✅ FIXED POINT |
| **m3** | **`-O2`** | **278** | **`1c75f97d1907f92f4c0a8a3ef49eb9ee`** | ⛔ **Parse Error on START** |
| **m4** | **`-O2`** | **278** | **`1c75f97d1907f92f4c0a8a3ef49eb9ee`** | ⛔ **Parse Error on START** |

**Milestone 1 holds at `-O0` and is broken at `-O2`. A milestone that holds only in the development arm is not the milestone.**

⭐ **THE SHARPEST FACT IN THIS FINDING: the `-O2` output is BYTE-IDENTICAL to the pre-cure `-O0` output.** Same 278 bytes, same md5 `1c75f97d…`. Not a similar failure — **the same failure**. So `6ba28e5e`'s cure of the 32-bit-tag-compare class **holds at `-O0` and does not hold at `-O2`**, which matches the standing `161-o2-red` row's own note exactly: *"asm RT_OPT-independent; wound is runtime C under optimization."* The emitted code is not the suspect; the runtime C is either being miscompiled or is exercising UB that `-O2` is entitled to exploit. Note also that `m3 ≡ m4` still holds *within* each arm — this is not a medium split, it is an optimisation-level split.

**Confirmed twice, independently of the first measurement:** after the flag-keyed build cache landed, a clean A/B on one tree gave `-O0` → FIXED POINT, switch to `-O2` (0s) → 278 bytes, switch back to `-O0` (1s) → FIXED POINT.

## ⛔ MY ERROR, NAMED — IT IS THE CLASS LAW 0 EXISTS TO CATCH, COMMITTED BY THE SEAT ENFORCING LAW 0

I ran **one arm of a two-arm axis and reported the result without the axis.** `make pristine` defaults to `RT_OPT=-O0`; I never passed `-O2`; I dated the verdict by commit and never by RT_OPT, which `CLAUDE.md` explicitly requires. Every individual number in the original finding was true and reproducible. **The scope was missing — and a true number with a missing scope reads as a general claim.** That is LAW 0 species (2) EXPIRY, produced not by time passing but by a dimension nobody stated.

It also went unnoticed because the `-O2` arm was *expensive*: 9m30 per rebuild, thrown away on every switch. **Cost and blindness were the same defect** — nobody re-ran `-O2` because nobody could afford to. That is now fixed (`Makefile` flag-keyed cache: an `-O2` switch costs 0–1s), which is why this finding and the build finding belong to one session.

⭐ **PROPOSED LAW (one line, for CEO to land or reject):** *a correctness verdict must name every configuration axis it was taken on, and a verdict on one arm of a selectable axis is a verdict about that arm ONLY, never about the product.* We already require RT_OPT labels on **perf** numbers; this extends it to **correctness**, where it matters more — a perf number with the wrong flag is merely wrong, while a correctness verdict with the wrong flag closes a milestone that is still broken.

## WHAT REMAINS TRUE FROM THE ORIGINAL FINDING

Unchanged and still load-bearing: the descr-stamp regression is real at `-O0`, reproduces at `cd13321e^` and `cd13321e`, is cured by `6ba28e5e` **at `-O0`**, HQ's prime-suspect *commit* is disproven while its *mechanism* is confirmed, the rescued probes are correct, the `-INCLUDE`/CWD blindness was real, and the corpus baseline (m3 357/359, m4 355/359+2 SKIP, denominator 359) stands — **all of it at `-O0`.**

## THE CORPUS BASELINE, MEASURED HERE, SUPERSEDING BOTH QUOTED NUMBERS

`bash scripts/test_corpus_snobol4.sh` at `457dc5d9`:

```
mode-3 (--run):     PASS=357 FAIL=2            (359 total)
mode-4 (--compile): PASS=355 FAIL=2 SKIP=2     (359 total)
```

Reds: `160_pat_alt_inner_gen_resume` (standing front red, both modes) · `demo_treebank` (deliberate, row `vlist-expr-alternation`) · `132_pat_fence_eps_recur_shallow` (compile SKIP) · **`demo_porter` (compile SKIP — this is seat13's m4 duplicate-label defect, corpus-visible)**.

⛔ The long-quoted `339/341` is stale, and so is seat3's `320/321` — **the denominator is 359.** Cite this one, or measure your own.

## WHAT MUST HAPPEN NEXT (rows, not edits — under the s256 delegate-only rule in force at the time)

1. **`rung-m1-m3-regression` is redirected, not closed by fiat.** Its NEXT block no longer says "bisect 66 commits"; it says run the DONE-WHEN, confirm, and correct the board. A seat re-firing the old brief would have spent a full session bisecting a cured defect with a probe that reads BAD at every step.
2. **Retract owed-ruling item (v) properly.** seat07 was right that it read stale — but stale in the *opposite* direction from what anyone assumed: M1 is not broken, it is fixed.
3. **`board_beauty_m1.sh` needs re-running at HEAD.** seat07's 0/10-both-modes was measured at `3cf83181`, pre-cure. Its verdict is expired, not wrong.
