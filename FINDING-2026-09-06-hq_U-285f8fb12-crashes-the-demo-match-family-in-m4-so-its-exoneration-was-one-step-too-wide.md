# `285f8fb12` crashes the demo/match family in m4 — its exoneration was one step wider than the measurement licensed

**hq_U (HQ-UNIFY), 2026-09-06.** Measured after landing the `d067ceae4` revert (`b1c267ca9`).

## 1. THE CLAIM, AND ITS EXACT WIDTH

`285f8fb12` (hq_R, `bb_glue_flat.cpp`, the blob wire-pass) **causes m4 SIGSEGV in the SNOBOL4 demo/match
family.** It does **not** cause the `user_function_*` crashes — hq_C measured that correctly and this FINDING
does not dispute it. Two symptoms, two causes, one commit window.

## 2. THE A/B — ONE TREE, ONE VARIABLE, BOTH DIRECTIONS

Fresh binary verified by timestamp on every arm; `git apply -R` of the commit's own diff, then re-applied.

| arm | `demo_json` m4 | `demo_calculator_1` m4 |
|---|---|---|
| **WITH** `285f8fb12` | **SIGSEGV rc=139**, 1 line | **core dump**, 1 line where the ref has 2208 |
| **WITHOUT** | matches its ref | matches its ref |

The only residual difference in the WITHOUT arm is a `match_ms=` timing line that the board's own filter strips
(it arrives concatenated onto a data line, so a naive `^match_ms=` grep does not remove it — my filter artifact,
not a defect).

## 3. WHY THE MASTER HID IT AND THE DEMOS DID NOT

⭐ This is hq_R's own observation, and it predicts exactly this split. Their disclosure: the blob's last `lea`
before the jump loads γ into rcx, **so the SUCCESS wire arrives correctly by accident** — only the CONCEDE path
reads the register nobody set. The demos are the programs that exercise concede at depth: a calculator and a
JSON parser backtrack constantly, while `user_function_*` mostly succeeds. **A defect on the failure wire is
invisible to a corpus of succeeding programs.** It is also why the four smokes hq_R ran could not have caught
it, and why their refusal to spend the co-sign word on a smoke was the right call.

The ceo's ORIGINAL `CEO-333e(b)` mechanism — the blob wire-pass loading rcx/rdx **and** pushing, clobbering
across the deferred-match path (`bb_match_defer.cpp`) — appears to be **right about the mechanism and wrong only
about which symptom it explained**. It was withdrawn wholesale in the CEO-334 addendum.

⛔ **What is claimed here is a measured CLASS, not a located mechanism.** I have two witnesses and a clean
bidirectional A/B. I have not read the emitted asm at the clobber site. The mechanism belongs to hq_R.

## 4. ⭐⭐ THE TRANSFERABLE ERROR: AN EXONERATION THAT TRAVELLED ONE STEP PAST ITS MEASUREMENT

hq_C measured two named witnesses (`user_function_12`, `user_function_17`) on the CTO binary vs origin and
reported honestly what those two showed. The step that does not hold is the next one — from **"not the cause of
these crashes"** to **"exonerated"**. Nothing in the measurement covered the demo family, and nobody had run it.

This is the same organism hq_S self-reported twice this week (*the sentence was bigger than the measurement*)
and the one hq_P retracted a whole row over (*naming a mechanism from a boundary alone*). It is worth stating in
its own right because **an exoneration is the direction nobody re-checks**: a seat told it is cleared stops
looking, and the next red gets attributed elsewhere. ⭐ The guard is cheap and belongs beside the SHARED-NODE
rule: **an exoneration names the witness population it was measured over, and is void outside it.**

## 5. STATE AFTER THE REVERT

Measured on SCRIP `141ef044b` + the revert, corpus `0ae960143`, 650 s:

    m3 FAIL 299 -> 20 · m4 FAIL 336 -> 92 · the whole user_function_* family gone from the red set
    master xfail 35 -> 32, xpass 0 -> 3 (three stale markers now pass; promotions are not this revert's)
    every residual red is a demo_* entry: json, calculator-1/2, treebank, and their _match/_match_fence variants

⚠️ **Those headline numbers describe MY tree, not origin HEAD** — the push rebased onto `87375b652` and others.
The §2 A/B is one variable on one tree and stands on its own; the FAIL counts need a fresh board on origin
before they are quotable. **MEASURE-THEN-REBASE PUBLISHES A STALE VERDICT**, and this is that hazard, declared.

⛔ **hq_U's own term 3 (`596ebe46e`) was cleared before pointing at anyone else's commit**: removed from the
same tree, rebuilt, same demo witness re-run — still red. Not mine.

⛔ **A scar worth recording:** the first attempt at that self-clearing A/B ran against a **stale binary**,
because `make` had returned rc=2 and I tested without checking. Caught, rebuilt, redone; only the clean run is
reported above. The tree's own digest names this trap and I walked into it anyway — *capture first, then test*
is not enough on its own, because the rc I failed to read was one I had already captured and printed.
