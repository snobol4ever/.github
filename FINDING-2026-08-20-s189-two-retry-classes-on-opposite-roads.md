# FINDING s189 (HQ) — TWO RETRY CLASSES, ON **OPPOSITE ROADS**: `FAIL` DOES NOT RE-DRIVE A GENERATOR INLINE, AND A FENCE-PREFIXED ARBNO BODY NEVER MATCHES WHEN STORED

**Date:** 2026-08-20 · **SCRIP:** `28e2122a` (`make pristine`, RT_OPT `-O0`, includes seat7's alt-seam-tier landing) · **corpus:** `+probe/retry/` · oracle live `sbl`.
**Provenance:** the last two unrouted m3 reds on the broad corpus board, taken through the finder and then ablated. Both reduce to three-line witnesses with green one-token twins. **Ten witnesses checked in at `corpus/probe/retry/` (4 red, 6 green controls), every `.ref` from the live oracle.**

## 1 · THE TWO CLASSES, AND WHY THE PAIRING IS THE FINDING

| witness | road | oracle | SCRIP | |
|---|---|---|---|---|
| `rty_fail_bal_inline` (`'ABC' ? POS(0) BAL $ OUTPUT FAIL`) | **inline** | `A AB ABC` | `A` | ⛔ RED |
| `rty_fail_bal_stored_ctl` (same pattern, `p = BAL $ OUTPUT FAIL`) | **stored** | `A AB ABC` | `A AB ABC` | GREEN |
| `rty_fence_arbno_stored` (`expr = LEN(1) ARBNO(FENCE('+') LEN(1))`) | **stored** | `match` | `nomatch` | ⛔ RED |
| `rty_fence_arbno_inline_ctl` (identical text, inline) | **inline** | `match` | `match` | GREEN |

**The two roads each break where the other works.** That is the useful part: for each defect there is a working reference implementation *in the same tree* — the cure is not invention, it is making one road do what the other already does.

## 2 · CLASS A — `FAIL` DOES NOT RE-DRIVE AN EXTENDING GENERATOR (inline road)

`BAL`/`ARB` are extending generators; the manual's own enumeration idiom is `P $ OUTPUT FAIL`, where `FAIL` forces the scanner to re-drive the generator to exhaustion. SCRIP fires the generator **once**.

Controls that make it exact:
- `rty_fail_arb_inline` — same defect one generator over (`ARB`) ⇒ **one class, two members**; an op-conditioned cure would violate NO-PER-OP-FILTER.
- ⭐ **`rty_deadlit_arb_ctl` is the sharpest control: the driver is the literal `'Z'`, which can never match** — it fails exactly as `FAIL` does, and the generator **extends correctly**. So the defect is **not** "an always-failing right element". It is the **`FAIL` node itself**.
- `rty_fail_span_ctl` — `SPAN` is not an extending generator, so firing once is correct; this guards the cure against over-firing.
- Also green (already measured): `ARB $ OUTPUT RPOS(0)`, `ARB $ OUTPUT 'C'` — real drivers re-drive fine.

**Reading:** on the inline statement-graph road, `IR_MATCH_FAIL`'s failure exits as a **wholesale concede** instead of a **retreat (β) into the left element**. The stored/blob road wires the same retreat correctly — `rty_fail_bal_stored_ctl` enumerates all three. **Diff how each road wires FAIL's ports; the blob road is the specification.**

## 3 · CLASS B — A STORED PATTERN WHOSE ARBNO BODY *BEGINS* WITH `FENCE(x)` NEVER MATCHES

Reduced from `crosscheck/patterns/145_pat_left_assoc_via_arbno_fence` (oracle `first=1 last=5`, SCRIP `fail`). Ablated to `expr = LEN(1) ARBNO(FENCE('+') LEN(1))`, subject `'1+2+3'`.

Ingredients ruled OUT by green controls: the conditional captures (`. FIRST` / `. LAST`), `SPAN`, the `*expr` defer form (`rty_fence_arbno_defer` is red the same way — so it is the stored pattern's own resume surface, not the defer road), and **iteration count** (`rty_fence_arbno_stored_1iter`, one iteration, equally red). Ingredients ruled IN: **stored** (inline is green at counts 1–7) and **FENCE as a body prefix** (`rty_nofence_stored_ctl` green; and fencing the *whole* body, `ARBNO(FENCE('+' LEN(1)))`, is green).

**Reading, and a specific hypothesis the seat can test in one command:** this is the s183 mechanism one shape over — the blob publishes the wrong node as its resume carrier. When the ARBNO body's first node is a `FENCE`, the published body root is a node that `resume_carrier_ok` refuses (the untiered/refused-shape family of s180/s182/s188), so β dies at the fence and the ARBNO can never take its next iteration. **`SCRIP_RESUME_WHY=1` on `rty_fence_arbno_stored` names the published root and tier directly** — that instrument was built for exactly this question at s183 and answers for both roads.

## 4 · ⛔ TWO HQ CORRECTIONS, BOTH CAUGHT BY DISBELIEF RATHER THAN BY PROCESS

1. **A false "iteration parity" result was nearly published.** Varying the iteration count appeared to show 0,1,3+ green and 2 red. Implausible ⇒ retested ⇒ **the rewrite had silently moved the witness from the stored road to the inline road**. The count was never an ingredient. **An ablation must change exactly one thing, and *the road* is a thing** — rewriting a stored pattern inline to vary something else changes two.
2. **The first pass called Class A "BAL-specific" and then "FAIL-driven retreat".** Both were narrowed by the controls above: it is neither BAL nor "a failing right element", it is the `FAIL` node on the inline road only.

## 5 · WHAT THIS RETIRES ON THE BOARD

Both classes are m3 corpus reds with no owner: `175_pat_bal_generator_retry` (Class A) and `145_pat_left_assoc_via_arbno_fence` (Class B). ⭐ **145 survived seat7's alt-seam-tier landing at `28e2122a`** (fail-set re-measured pristine: m3 332/5 unchanged), which is the evidence that row's DONE-WHEN asked for — **145 is NOT the alt-seam-tier class**, and is now named as its own. Queue rows minted: `rty-fail-inline-retry`, `rty-fence-arbno-stored`.
