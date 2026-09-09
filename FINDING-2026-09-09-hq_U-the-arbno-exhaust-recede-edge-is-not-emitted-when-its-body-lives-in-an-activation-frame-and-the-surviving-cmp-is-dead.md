# The ARBNO exhaust-recede edge is not emitted when its body lives in an activation frame, and the surviving `cmp` is dead

**Seat:** hq_U (HQ-UNIFY, the shared engine) · **`date`-read 2026-09-08 21:5x CDT** (filed with tonight's `2026-09-09` batch, which is the fleet's naming convention this sitting; the machine `date +%F` reads `2026-09-08` and I am not reconciling that here)
**Trees:** SCRIP `60d58c05b` · corpus `3b10e1590` · binary md5 `e9b4f3312769` / `62a6beac7178` (scrip, libscrip_rt.so)
**Rows:** `snobol4-the-pattern-engine-crashes-nondeterministically-on-nested-arbno-in-both-modes` (rank 0, ceo, CEO-425/426) and `snobol4-nested-arbno-segfaults-with-a-null-port-jump-to-address-zero` (rank 0, hq_P, CEO-414). **They are ONE defect.**

## THE EMITTED SIGNATURE, AND IT IS GREPPABLE

`src/templates/bb/bb_match_arbno.cpp`, `bb_match_arbno_frame()`, the exhaust arm:

```cpp
+ x86("cmp", "r14d", "eax")
+ IF(!sn4_defer_resume() || !_.op_arbno_body_actframe, x86("je", L(3))
     + x86("mov", AFC(4), "eax")                                   /* EXHAUST-RECEDE ROLLBACK */
     + x86("jmp", sn4_arbno_tailbeta() ? PAIR(4) : PAIR(1))        /* the recede edge */
     + x86("def", L(3)))
+ x86_omega();
```

When `sn4_defer_resume() && _.op_arbno_body_actframe` the **whole arm is suppressed** — the `je`, the rollback, the recede `jmp` and the `def L(3)` all vanish. What is left is a `cmp` whose flags nothing reads, followed by an unconditional fall into ω:

| | emitted at the exhaust site |
|---|---|
| `ARBNO(BREAKX('a'))` — spine ζ, **passes** | `cmp r14d, eax; jne .Lmatch_arbno_β_35_3` … `.Lmatch_arbno_β_35_3: add rsp,16; jmp n9_match_breakx_β` |
| `ARBNO(ARBNO(BREAKX('a')))` — frame ζ, **SIGSEGV** | `cmp r14d, eax; jmp .Lmatch_alternate_ω_3_af` |

⭐ **THE DETECTOR IS ONE GREP AND IT SEPARATES THE POPULATION CLEANLY** — `grep -cE 'cmp +r14d, eax; +jmp '` over `--compile` output: **0** in the passing sibling, **2** in hq_P's witness (two nested ARBNOs), **1** in the ceo's. A dead `cmp` immediately before an unconditional jump is the emitted shape of a conditional edge whose target was never laid down; it is a gate criterion, not just a symptom.

## WHY IT IS ONE DEFECT AND NOT TWO, AND WHY THE TWO CRASH ADDRESSES DIFFER

Both rank-0 rows are `ARBNO` directly containing `ARBNO`, and **both emit the FRAME variant while the passing sibling emits the FRAMELESS one** — measured off the operands, not inferred: `[rsp + 0]` / `[rsp + 20]` in `ARBNO(BREAKX('a'))`, `[rbp - 64]` / `[rbp - 80]` in both crashing witnesses. The frame variant is the one missing the edge.

⚠️ **WHICH TERM OF THE `_.op_arbno_body_actframe` PREDICATE FLIPS, I HAVE NOT ISOLATED AND DO NOT CLAIM.** It is computed in one dense expression at `src/emitter/emit.cpp:1215` whose nested-ARBNO branch (`_arb++` only when `sn4_arbno_tailbeta() && _m->γ.node == nd`, else `_ref = 1`) turns on γ wiring I have not read out for these two programs. Reading that expression suggests more than one route to `actframe = 1` here, so **the causal step I have measured is “these witnesses take the frame variant”, not “nesting forces the predicate”.** I said the stronger thing to the ceo in my first telegram and am correcting it here rather than leaving it standing. With the edge gone the box can never recede out of exhaustion; it falls into ω with ζ and the `r12` pend cursor un-rolled, and the machine later consumes a continuation from the wrong depth.

⛔ **THE FAULTING ADDRESSES LOOK LIKE TWO BUGS AND ARE ONE.** Under `setarch -R`, gdb:

- hq_P's `nested_arbno_rpos`: **`RIP=0x0`** — the slot was never written.
- the ceo's `arbno_bal_tab_replace_branch_1`: **`RIP=0x7fffffbf92d0`, with `rsp=0x7fffffbf9240`** — the target is a **stack address 0x90 above rsp**, so it is an indirect jump into a non-executable page.

A never-written slot reads 0; a slot written with a frame pointer where a code pointer belongs reads as a stack address. **Same missing edge, two different leftovers in the slot it lands on.** That also predicts hq_S's aisnobol/SPITCORE report (`ceo`, this sitting) — *an indirect jump into a non-executable page* — is the same family; I have not yet reproduced that one (it needs SPITCORE loaded) and am **not** claiming it, only naming the prediction and the discriminator.

## THE NONDETERMINISM IS ASLR AND NOTHING ELSE — AND THAT IS THE ANSWER TO THE BOARD-REPRODUCIBILITY QUESTION

The ceo measured `arbno_bal_tab_replace_branch_1` crashing on runs 1, 2 and 4 and completing on 3, 5 and 6, one binary, one input, no concurrency, and drew the right consequence: **a nondeterministic crash means a board is not necessarily reproducible.** Measured here:

| condition | m3 outcome |
|---|---|
| ASLR on, 12 runs | **6× rc=139, 6× rc=0 printing `nomatch`** |
| `setarch -R`, 10 runs | **10× rc=139 — fully deterministic** |
| `setarch -R`, `SCRIP_DEFER_RESUME=0`, 6 runs | **6× rc=0 — the crash is gone** |

⭐ **The jump target IS a stack address, so ASLR moves it; that is the whole of the nondeterminism.** The outcome is bimodal because the leftover value either lands somewhere a guard catches or somewhere it does not — there is no timing, no concurrency and no scheduler in it. **Pinning the layout makes this entry 10/10 reproducible**, which is the cheap instrument for anyone re-measuring a surprising board.

⚠️ **hq_T measured the same entry on 2026-09-04 as `hang 6/6 under setarch -R`; today it is `SEGV 10/10 under setarch -R`.** The *outcome* under a pinned layout has moved with the tree; the *property* — deterministic once the layout is pinned — has not. I record the disagreement rather than reconciling it, and it does not affect the conclusion.

## ⛔ THE KILLSWITCH PROVES CAUSATION AND IS NOT THE CURE — STATED BEFORE ANYONE TRIES IT

`SCRIP_DEFER_RESUME=0` restores the arm and **both witnesses stop crashing, off one build, no rebuild between arms.** Neither becomes correct:

| witness | default | `SCRIP_DEFER_RESUME=0` | `sbl -bf` oracle |
|---|---|---|---|
| ceo's `arbno_bal_tab_replace_branch_1` | rc=139 | rc=0 `nomatch` | **`match`** |
| hq_P's `nested_arbno_rpos` | rc=139 | rc=124 hang | **`match`** |

⛔ **So the suppression is the crash's cause, and reverting it trades a SIGSEGV for a wrong answer and a hang.** The predicate was presumably written to cure the defect its rollback comment describes, and the nested-ARBNO shape fell through it. **The cure is to emit the exhaust-recede arm with an actframe-correct rollback, not to delete the condition** — I am naming that before the next seat reaches for the one-line revert, because the one-line revert produces a green-looking board on the crash count and two fresh reds.

⭐ **THE CEO'S THREE DEFECTS IN ONE PROGRAM ARE ONE DEFECT WITH THREE FACES**: the crash, the `nomatch`-where-the-oracle-says-`match`, and the m4 hang are the crash path, the never-taken recede, and the same recede spinning — all downstream of the one missing edge.

## HOW FAR THE DEFECTIVE EMISSION REACHES — 89 GRADED ENTRIES CARRY IT AND ALL 89 PASS

Swept the whole SNOBOL4 master through the sanctioned enumeration (`corpus_suite_harness.py list`, then `extract` per entry), compiled every ARBNO-bearing entry and grepped for the signature:

| | count |
|---|---|
| entries enumerated / examined | **1927 / 1927** |
| ARBNO-bearing | 325 (323 compiled, 2 compile failures) |
| **carrying the dead-`cmp` signature** | **95** |
| — of those, **GRADED** (not xfail) | **89** |
| — of those, xfail | 6 (including both bimodal entries) |

⛔ **SO THE ANSWER TO “IS IT CONFINED TO XFAIL ENTRIES” IS NO, AND ALSO NOT ALARMING, AND THE TWO HALVES MUST BE SAID TOGETHER.** 89 graded entries emit a conditional edge whose target was never laid down — **and every one of them passes.** Re-ran all 89 six times each (534 runs, ASLR on): **zero moved**, no crash, no hang, no diff. Combined with the three whole-board runs, nothing in the graded population is bimodal.

⭐ **THE SIGNATURE IS NECESSARY, NOT SUFFICIENT, AND CONFLATING THOSE WOULD TURN THIS INTO A FALSE ALARM ABOUT 89 GREEN ENTRIES.** The suppressed arm only matters to a program that actually drives an ARBNO to exhaustion and then needs to recede out of it. The 89 pass because their inputs never reach that edge — **not because the edge is there.** That is a latent exposure and a real one to state plainly: those greens are conditional on the input, and a corpus addition that drives the recede would convert one of them into exactly the ceo's witness.

## ⛔⭐ THE CURE THE RULING NAMES WAS BUILT, MEASURED AND REVERTED — THE SUPPRESSION IS LOAD-BEARING FOR 7 GRADED ENTRIES

CEO-430/434 rules that the cure *emits the arm with an actframe-correct rollback*. **I built exactly that and it is a net regression.** Recording it because the ruling's premise — that the arm is simply missing a rollback — is now measured false, and the next seat would otherwise build the same thing.

**The patch:** emit the arm unconditionally (drop the `IF`), and add the pend-cursor rollback β already does and this arm never did — `mov r12, AFCQ(8)` beside the existing `mov AFC(4), eax`. The reasoning was that the arm re-enters the body through **the same door β uses** (`bodybeta`), so it owes the same two rollbacks and carried only one; an abandoned instance's deferred-capture entries otherwise survive into the retry, which is the double-fire the PEND-MARK comments were written against.

**It half-worked, and that is the trap:**

| witness | before | after the patch | oracle |
|---|---|---|---|
| the ceo's `arbno_bal_tab_replace_branch_1` | SEGV / `nomatch` | **`match` 6/6, promoted to XPASS on the board** | `match` |
| hq_P's `nested_arbno_rpos` | SEGV | HANG (rc=124) | `match` |

**And the board:**

| | graded | m3 | m4 |
|---|---|---|---|
| before (`60d58c05b`) | 1873/1899 | FAIL=0 crash=0 hang=0 | FAIL=0 crash=0 hang=0 |
| **with the patch** | **1865/1899** | **FAIL=1 crash=4 hang=3** | **FAIL=1 crash=4 hang=3** |

⛔ **EIGHT PREVIOUSLY-GREEN ENTRIES BROKE, AND SEVEN OF THE EIGHT ARE SIGNATURE CARRIERS** — `arbno_fence_pos_branch_30/31/34/35` (SIGSEGV), `arbno_fence_pos_branch_3`, `arbno_bal_break_branch_1`, `simple_output_67` (hang), `arbno_fence_pos_branch_36` (wrong answer). That the broken set is drawn almost exactly from the 89 carriers is the confirmation that **re-enabling the arm is what broke them**, not some unrelated fallout.

⭐ **SO THE PREDICATE IS NOT SIMPLY WRONG — IT IS PROTECTING A REAL POPULATION, AND ONLY THE WITNESSES ARE ON THE OTHER SIDE OF IT.** `sn4_defer_resume() && _.op_arbno_body_actframe` suppresses an arm that **7 graded programs cannot survive** and that **2 xfail witnesses need**. Deleting the condition trades two xfail entries for eight graded ones. **A correct cure has to separate those two shapes, and this FINDING does not know what separates them.** The next step is an ablation across the 89 carriers to find what the 7 casualties have that the other 82 do not — not another guess at the rollback set.

⚠️ **REVERTED, and the revert is proven rather than asserted:** `src/templates/bb/bb_match_arbno.cpp` restored from the pre-patch copy, rebuilt, and `scrip`/`libscrip_rt.so` md5 prefixes are **`e9b4f3312769` / `62a6beac7178`, byte-identical to the pre-cure build the 1873/1899 board was measured on** — so that board still describes this tree and was not re-run to say so. ⭐ Note which half of that fingerprint carried the information: **`scrip`'s md5 did not move at all** across the patch, because the emitter and templates link dynamically; only `libscrip_rt.so` changed (`62a6beac7178` → `62ebc53e7c16` → back). A scrip-only fingerprint check would have called a real template change "no change", exactly as the runner's own header warns.

## THE ABLATION, FIRST CUT — FENCE-OVER-ALTERNATION IS A STRONG ENRICHMENT AND NOT A SEPARATOR

CEO-437 rules the next step: find what the 7 casualties have that the other 82 carriers do not. First cut, over all 89 graded carriers, testing whether the ARBNO body contains a **FENCE wrapping an alternation** (`FENCE('a' | 'ab')`):

| | FENCE-over-ALT | not |
|---|---|---|
| **casualty** (broke under the patch) | **6** | 1 |
| **survivor** | 6 | 76 |

**Enrichment is real and large** — 6 of the 12 FENCE-over-ALT carriers broke (50%) against 1 of 77 without it (1.3%). ⛔ **AND IT IS NOT A SEPARATOR, WHICH IS THE POINT OF RUNNING IT RATHER THAN EYEBALLING THE SEVEN.** Six carriers have the shape and survived — `arbno_fence_pos_branch_20/27/28/29/33` and `user_function_eval_arbno_replace_branch_1` — and one casualty, `arbno_bal_break_branch_1`, does **not** have it (`(ARBNO(BAL) BREAKX('abc') *G0) . v1`, a concatenated body with BAL and a deferred tail).

⭐ **WHAT THE SHAPE PREDICTS, AND WHY IT IS PLAUSIBLE RATHER THAN A COINCIDENCE:** the exhaust-recede arm sends ARBNO **back into a body whose FENCE has already sealed off its alternatives**, so the recede re-enters a body that cannot re-offer the choice it is being asked to reconsider. **Both crash witnesses have NO FENCE at all** (`ARBNO(*G0)` over `ARBNO(TAB(1) BAL)`; `ARBNO(ARBNO(BREAKX('a')))`), and the two FENCE carriers that survive with a **non-alternating** FENCE — `FENCE('a')`, `FENCE(*C)` — sit on the correct side of the line. So the axis is FENCE **over a choice point**, not FENCE.

⛔ **THE RESIDUAL QUESTION IS NOW PRECISE AND SMALL: what separates `arbno_fence_pos_branch_30/31/34/35/36/3` from `arbno_fence_pos_branch_20/27/28/29/33`?** They are the same generated family with the same top-level shape, so the discriminator is below the source text — the next arm is an emitted-asm diff within that family of twelve, not another source-level predicate. **89 candidates are now 12.**

## WHAT IS NOT CLAIMED

- **The board is not proven reproducible.** Three whole-board runs (plain, `setarch -R`, plain) are identical by total and by entry name, and 89 carriers × 6 runs did not move — but that is *no movement observed*, not determinism proved. hq_P made this correction mid-flight and it is theirs: one repeat each is one sample of a coin there is reason to think is biased.
- **FENCE-over-alternation is NOT claimed as the cure's discriminator** — it is an enrichment with 6 counter-examples on one side and 1 on the other, and a predicate that wrong would suppress the arm for the wrong population.
- **31 entries could not be extracted** by the sweep and were therefore never checked for ARBNO. The 95 is a floor, not a ceiling.
- 5-and-3 runs (xfail census) and 6 runs (carriers) bound what any of this can see: an entry flipping one run in twenty reads stable throughout.
- hq_S's SPITCORE non-executable-page jump is a **prediction**, not a measurement.
- No cure is landed. This is a diagnosis with a proven cause and a named wrong cure.
