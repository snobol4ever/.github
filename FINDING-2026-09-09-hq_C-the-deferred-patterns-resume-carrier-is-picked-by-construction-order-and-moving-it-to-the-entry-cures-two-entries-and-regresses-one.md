# The deferred pattern's resume carrier is picked by CONSTRUCTION order, and moving it to the graph ENTRY cures two entries and regresses a third

**Seat:** hq_C · **`date`-read 2026-09-09 09:1x CDT** · **PARKED MID-DIAGNOSIS** on Lon's 09:0x switch to Icon (CEO-445).
**Trees:** SCRIP `01eb996ca` (clean; the change below was NEVER committed) · corpus `f7c68a8c5` · `.github` `2d59f6e6` · RT_OPT=-O0 · oracle `sbl -bf` live, swap stamp 20260909T033439Z.
**Row:** `flip-snobol4-fence-right-seal-discards-left-elements-alternatives` (hq_C, CEO-441's 13 WRONG-ANSWER xfail entries).

## WHAT WAS MEASURED, AND WHAT THE MARKER GOT WRONG

Four of the master's 13 WRONG-ANSWER xfail entries print `nomatch` where the live oracle and their own `.ref` print `match`. Their `ALL.xfail` marker text files all four under one class (`passthrough-window-ptw`). **They are three different mechanisms, and the tree's own `SCRIP_RESUME_WHY` instrument separates them in one run:**

| entry | `right_sealed` | `pfenced` | carrier `rn` | published `body_root` |
|---|---|---|---|---|
| `arbno_fence_pos_replace_branch_3` | 1 | 1 | 0 | NULL |
| `arbno_fence_pos_replace_branch_4` | 0 | 1 | 0 | NULL |
| `fence_pos_rpos_replace_branch_3` (PAT$1) | 1 | 1 | 0 | NULL |
| `arbno_fence_pos_branch_22` | — | 1 | 1 | **op 60 `IR_MATCH_ARBNO` — published** |

⭐ **`arbno_fence_pos_branch_22` publishes a perfectly good carrier and still answers wrong**, so it was never a `body_root` defect at all. A marker that groups by symptom grouped it with three entries whose symptom has a different cause.

## THE THREE STACKED REFUSALS

For `P = ARBNO('a') FENCE('b' | epsilon)` the IR wiring is already CORRECT — `MATCH_FENCE1`'s ω recedes to the `MATCH_ARBNO`. The defect is entirely in whether the deferred pattern may be re-offered at all. Three independent refusals sit on the same blob, and **curing any two still leaves it red** (proven by a factorial over three env-gated arms, not by one-at-a-time removal):

1. **`sno_pat_publish_body_root` picks the carrier by CONSTRUCTION order** (`gp->all[before_pat]`), not by the graph's entry. For these patterns the first-constructed node is the `FENCE1` (tier 0), so no carrier is accepted — while `gp->entry`, assigned three lines earlier, is the `ARBNO` (tier 1).
2. **`rs` (`sno_pat_right_sealed`) nulls `body_root` even when a valid carrier was computed** — the ternary's `!rs` discards a live `rn`.
3. **The USE site seals independently:** `nd->seal = sno_defer_sealed(...)` marks the `MATCH_DEFER` for `*P` non-resumable whenever `P`'s rightmost element is a fence form.

⛔ **The seal's premise is wrong in all three places.** SPITBOL's FENCE forbids re-offering **the fence's own alternatives**; it does not make the whole pattern non-resumable when an element to the fence's LEFT still has instances to give, and reaching that element never backs up THROUGH the fence.

## THE ATTEMPT, AND THE MEASURED REASON IT IS NOT LANDABLE

Two edits (no env switches): (A) `sno_pat_right_sealed` seals a `TT_SEQ`/`TT_CAT` only if the right child is fence-sealed AND a new `sno_pat_offers_alt` says the left child offers no instances; (B) the pfenced arm takes its carrier from `gp->entry` (GOTO-chased) before falling back to the construction-order scan.

**Result, both modes:** `arbno_fence_pos_replace_branch_3` and `_4` CURED (m3 and m4 `match`) · `fence_pos_rpos_replace_branch_3` and `arbno_fence_pos_branch_22` unchanged · **and `arbno_fence_bal_replace_branch_4` REGRESSED from `match` to `nomatch`** (`P = FENCE(epsilon) ( 'a' | 'aa' )` — a fence as the LEFT element, whose live resume surface is the TRAILING alternation).

⭐ **THE ISOLATION IS THE HANDOVER FACT: edit (A) ALONE IS INERT — it cures nothing and regresses nothing. Edit (B), the carrier choice, is BOTH the cure and the regression.** Construction order and entry order each name the right carrier for one shape and the wrong one for the other: entry-first is right when the generator is LEFT of the fence, construction-first is right when it is RIGHT of it. **Neither order is the answer; the carrier has to be chosen by which node can still offer, not by position.** That is the next step, and it is why nothing was committed.

⚠️ I predicted edit (B) could not touch `arbno_fence_bal_replace_branch_4` (its right child is an alternation, not a fence, so `rs` is 0 either way) and ran the A/B anyway. **The prediction was wrong.** A revert-and-rebuild baseline on the same tree is what caught it; the reasoning would have shipped a swap — two cured, one broken, and the master's FAIL count moving by only one.

## WHAT IS NOT CLAIMED

- No cure is landed. SCRIP is clean at `01eb996ca`; the patch is preserved in the baton's ledger, not in the tree.
- `fence_pos_rpos_replace_branch_3` and `arbno_fence_pos_branch_22` have NOT been root-caused — only shown to be separate from the other two.
- `simple_output_64` reads `FAIL` (not `XFAIL`) in a `--by-modes-column` m3 run beside `arbno_fence_bal_replace_branch_4`; both are pre-existing on `01eb996ca` and neither is mine.
