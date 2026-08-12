# FINDING 2026-08-12 (s33, Opus 5) — THE CAPTURE-δ0 BLAST RADIUS IS TWO TEMPLATES OF NINE, THE FORMULA PREDICTS ON FRESH NUMBERS, AND MY OWN ROOT-CAUSE WAS FALSE

**Fingerprint:** SCRIP `52545cbf` + `900060c7` (board runner; **ZERO compiler bytes**) · corpus `c91d1adf` UNTOUCHED · `.github` this commit. **Measurement only.**
**Rung:** GOAL-SN4-HOME-LOWER L-0 (landed) → L-3 (opened, NOT closed). **Instrument:** `scripts/board_earn0_set.sh` + SPITBOL oracle `x64/bin/sbl -b` vs `scrip --run`.
**Seat opened without BOARD's P0 floors** — BOARD is UNOPENED and RULES 2026-08-10 forbids parking. L-0 is this seat's own open-state at its own HEAD, which is what a per-rung control must be regardless.

---

## 0. THE ONE-LINE RESULT

s27 named **nine** templates as the capture-δ0 blast radius, by grepping for `FR(x86_scratch_off)`. **Executed, it is two: ARB and BAL.** BREAK, BREAKX, REM, RTAB, TAB and SPAN are CLEAN under a prediction test that would have caught them. A grep produces candidates; only execution produces a defect set.

## 1. THE FORMULA PREDICTS ON NUMBERS NOBODY HAD USED

s27 convicted `[n, p+n)` (bound substring starts at the CONSUMED COUNT `n`, not the MATCH START `p`) by arithmetic on two witnesses. I stated predictions **before** measuring on fresh subjects:

| probe | p | n | oracle | predicted if defective | measured | verdict |
|---|---|---|---|---|---|---|
| `ARB`, `S='xy+abcdefg'` | 3 | 5 | `[abcde]` | `[cde]` | `[cde]` | **formula CONFIRMED** |
| `SPAN`, `S='q+aabbz'` | 2 | 4 | `[aabb]` | `[bb]` | `[aabb]` | **formula FALSIFIED here — SPAN clean** |

The SPAN row is the load-bearing one: the same formula that predicts ARB to the character predicts SPAN wrongly, so the defect is **not** "captures after variable-length primitives" as a class. It is per-template.

## 2. THE MEASURED BLAST RADIUS (all nine of s27's candidates, one witness each, prediction stated first)

| template | verdict |
|---|---|
| ARB · BAL | **DEFECT** — `[n, p+n)`, both signs reproduced (`cap_after_bal` 1 too far RIGHT, `cap_after_varlen` 3 too far LEFT) |
| BREAK · BREAKX · REM · RTAB · TAB · SPAN | **CLEAN** — oracle-identical; the defect-predicted string did not appear |
| SPAN with a VARIABLE arg | **DIFFERENT CLASS** — rc=124 hang, no output; see §4 |

⭐ **The two defective members are exactly the two primitives the manual gives IMPLICIT ALTERNATIVES** (Ch.18 p.207–8: *"patterns such as ARB and BAL have implicit alternatives which are tried before your explicit ones; ARB behaves as if it were `(LEN(0)|LEN(1)|LEN(2)|…)`"*). Those are the primitives that must carry state **across the γ yield** because they are re-entered on retry. BREAKX also extends on rematch and is CLEAN — consistent with the manual's description that it extends by *skipping to the next character in its argument string* (recomputed from the cursor) rather than by persisting a counter. **This is a semantic characterisation, and it is a better predictor of the defect set than "writes `FR(x86_scratch_off)`", which all nine do.**

## 3. ⛔⭐ CORRECTION ON MYSELF — I RAISED A ROOT CAUSE AND THE EVIDENCE KILLED IT

Reading `bb_match_capture.cpp` (SAVE stores `r14d` to a slot at α; COND reads that slot as the start and computes `edx = r14d - eax` as the length) against `bb_match_arb.cpp` (count at `FR(scratch)`, start at `FR(scratch+4)`, both live across γ), I hypothesised **slot aliasing**: ARB's counter overwriting the capture's saved delta. It has the merit of predicting the observed arithmetic exactly — COND would read `n`, length `= (p+n) - n = p`, bound `= [n, p+n)`.

I then found `mov dword ptr [rsp + 0], 0  # start_δ` in the emitted asm and nearly wrote it up as confirmation, because the emitter's own annotation carries the capture's word for that slot.

**It is not the capture's slot.** Pulling the raw block instead of the grep-filtered one shows it is **MATCH_BEGIN's unanchored scan anchor**, and the surrounding code is the manual's Ch.18 step 6 verbatim: set start; run pattern; on failure `add start,1`; `cmp` against subject end; consult `rt_anchor_g` (`&ANCHOR`); retry. `start_δ` there means *starting cursor position of the scan*, not *capture delta zero*.

⇒ **The aliasing hypothesis is UNCONFIRMED and is not to be inherited as fact.** What killed it was reading the raw instruction block rather than a filtered view of it. ⛔ Note the shape: an annotation string is not an instrument, and a comment that agrees with your hypothesis is the least trustworthy evidence in the file. RULES §2's *"never guess an offset — instrument"* covers guessing it from a **name**, not only from arithmetic.

## 4. A SIMPLER 061 WITNESS FELL OUT, AND IT IS NOT THIS SEAT'S

`SPAN(V)` and `SPAN(*V)` both **hang, rc=124** — 4 lines, a literal-valued variable, no stored pattern, no defer. The star is **not** the discriminator; a variable argument is. That is L-4's 061 class (*"the dynamic arm reads a cell the arg never landed in — whole class, not POS-specific"*), and `cap_after_varlen`'s own header calls the two adjacent-but-distinct. **It is a materially smaller reproducer than 061 itself**, and it says the class reaches plain variables, not just deferred ones.

## 5. BOARD AT HEAD (m3, `REPEAT=3`; the L-0 floor)

12 PASS (**all four controls green**) · 5 FAIL-silent · 2 FAIL-hang · 1 FLAKY. FINDING-2026-08-12 §7 **reproduces row-for-row** four commits past its own HEAD. `earn0_stored_capture` is three-armed at this HEAD (measured 8×: 3× rc=0 wrong-bind `V=[]`, 5× rc=134; a later run opened rc=139) — **a single-shot board reports it as a coin flip**, which is why the runner now reports FLAKY rather than a verdict.

## 6. NEXT SEAT, IN ORDER

1. **MONITOR-FIRST on `earn0_cap_after_bal`** (RULES §1) — still unrun; §3 is why reading code first was the wrong order and I should have said so before doing it.
2. **Find where the capture's saved delta actually lives for the ARB/BAL graphs**, by instrument, not by slot name. The COND read and the SAVE store must be shown to be the same address or not.
3. **Sign-check any fix against BOTH `cap_after_bal` and `cap_after_varlen`** — they displace in opposite directions, so a fix that shifts a constant must break one.
4. The six CLEAN templates are now **controls**: a fix that moves any of them off oracle is over-broad, and that is detectable in one run.

**DEBTS:** the 8 probe programs of §1–§2 live in `/tmp/l3/` and are **NOT minted into corpus** — they are the evidence for every number above, and un-minted they are lore. Minting them (with the predictions in their headers, s27's style) is the first cheap act of the next seat. · m4 arm of the board **UNMEASURED, not green** (BOARD B-0). · Root cause of L-3 **OPEN**.
