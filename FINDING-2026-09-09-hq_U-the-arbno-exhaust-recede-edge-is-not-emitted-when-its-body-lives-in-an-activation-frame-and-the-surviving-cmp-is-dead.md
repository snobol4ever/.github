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

## WHAT IS NOT CLAIMED

- **The board is not proven reproducible.** Three whole-board runs (plain, `setarch -R`, plain) are identical by total and by entry name, and 89 carriers × 6 runs did not move — but that is *no movement observed*, not determinism proved. hq_P made this correction mid-flight and it is theirs: one repeat each is one sample of a coin there is reason to think is biased.
- **31 entries could not be extracted** by the sweep and were therefore never checked for ARBNO. The 95 is a floor, not a ceiling.
- 5-and-3 runs (xfail census) and 6 runs (carriers) bound what any of this can see: an entry flipping one run in twenty reads stable throughout.
- hq_S's SPITCORE non-executable-page jump is a **prediction**, not a measurement.
- No cure is landed. This is a diagnosis with a proven cause and a named wrong cure.
