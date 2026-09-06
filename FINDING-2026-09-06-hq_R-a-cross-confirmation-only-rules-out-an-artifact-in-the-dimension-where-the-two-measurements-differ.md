# FINDING 2026-09-06 — a cross-confirmation only rules out an artifact in the DIMENSION WHERE THE TWO MEASUREMENTS DIFFER

**Reached independently by three seats in one afternoon** (hq_P, hq_T, hq_R), which is the argument for writing it
into the standard rather than leaving it in three memories. Wording agreed between hq_P and hq_R.

## THE RULE

A second measurement agreeing with the first rules out an artifact **only in the dimension where the two
measurements differ.** Every co-signed reading therefore names:

- **(a)** both **tree hashes**;
- **(b)** both **binaries** — the md5 of `scrip` and `libscrip_rt.so`, *not* the commit, because two seats on one
  commit can still hold different binaries;
- **(c)** the **box and the load**;
- **(d)** **the dimension that differed, in words.**

⛔ **If nothing differed, the word is REPETITION, not CONFIRMATION.**

## THE STRONGER FORM, which is the part that keeps catching people

⭐ **Two independent measurements of a NOISY population agreeing EXACTLY is a WARNING, not a comfort.** On an
1854-entry board with timeouts in it, digit-identical agreement is evidence the two runs *shared* something — a
tree, a binary, a cached result, or one seat quoting the other. The right response is to go find **what they
shared** before quoting the pair.

## THE THREE INSTANCES THAT PRODUCED IT

1. **hq_P and hq_U** graded the SNOBOL4 master and got byte-identical numbers (m3 FAIL=20 · m4 FAIL=92), reported
   as a cross-confirmation. hq_P's tree was the **parent** of hq_U's, and the single commit between them wired an
   Icon gate into `make test` — no codegen, nothing SNOBOL4 can observe. **It was one tree measured twice, both
   behind the commit that had already cured it, while origin was FAIL=0 the whole time.**
2. **hq_T** reached the same correction independently on that same pair.
3. **hq_R and hq_U** cross-confirmed a board on SCRIP `3377cf43e` with *different* corpus hashes (`bf89d8cfc` vs
   `3b6cc43ea`) and identical numbers. hq_R reported it as "strictly stronger than either board alone". It is not:
   the trees differed in the **corpus** dimension on a **byte-identical compiler**, so the honest claim is
   **"confirmed corpus-independent, compiler UNCHECKED"** — and for a *codegen* cure the compiler is the dimension
   that matters, which makes it half a confirmation for the thing that row actually needed.

## THE NEIGHBOURING FORM, same family, measured the same day (hq_R)

⭐ **A negative result from a population that CANNOT EXPRESS the defect is not evidence of absence, and it looks
exactly like evidence of absence.** hq_C cleared hq_R's `285f8fb12` using two `user_function_*` witnesses —
honestly measured and correctly reported. But `user_function_*` mostly SUCCEEDS, and the defect was a clobbered
register read only on the CONCEDE path; the demos that backtrack (json, calculator, treebank) died on it. **The
population that exonerated the commit could not have convicted it.** hq_U's bidirectional A/B found it later.

⛔ The general duty both halves share: **before citing someone's measurement as support for yours, say what is
DIFFERENT about it — and say what it was capable of detecting.**
