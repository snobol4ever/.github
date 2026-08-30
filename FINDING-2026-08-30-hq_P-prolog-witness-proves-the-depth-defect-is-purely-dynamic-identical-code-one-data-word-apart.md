# FINDING — the depth defect is PROVABLY not statically detectable. ceo's Prolog witness gives a control pair
# whose emitted machine code is BYTE-IDENTICAL except for ONE DATA CONSTANT (`.quad 8` vs `.quad 10`) — and one
# crashes while the other passes. No predicate over emitted code can separate them, which retroactively and
# completely explains why all three static discriminators I tested failed. The dynamic lead is now proven
# necessary, not merely preferred.

**hq_P · 2026-08-30 · row `calling-convention-depth-tracked`**, on ceo's routing of a **Lon-direct escalation**
(*"Get the remaining Prolog benchmarks working"*): all 12 crashing van Roy kernels diagnosed by ceo as this
row's defect, witness `corpus/benchmarks/prolog/bench/witness_depth_nrev8.pl` (`28d444441`).
Diagnosis only — nothing committed to SCRIP for this.

## 1. The lottery reproduces, independently, and it is non-monotonic

Eight-line naive reverse; only the list length changes. SCRIP `b54c1c95`, m3, `setarch -R`:

| N | 3 | 5 | **8** | 10 | **15** | **20** | **30** |
|---|---|---|---|---|---|---|---|
| result | ok | ok | **SIGSEGV** | ok | **SIGABRT** | **SIGSEGV** | **SIGABRT** |

⭐ **N=8 CRASHES WHILE N=10 PASSES.** Not a depth threshold — a layout lottery, the identical shape as the
`volatile char[N]` pad sweep on the FENCE witness (8/32/40 clean, 16/24/48/56/64+ crash). ⚠️ Two distinct
signals, worth noting rather than smoothing over: N=8/20 abort with SIGSEGV, N=15/30 with SIGABRT.

## 2. ⭐⭐ THE DECISIVE MEASUREMENT — THE TWO PROGRAMS ARE THE SAME MACHINE CODE

`--compile` both arms and diff the emitted assembly:
```
4541c4541
< .Llit_integer_α_279_0:  .quad            8
---
> .Llit_integer_α_279_0:  .quad            10
```
**Two lines. One data word.** Every instruction, every label, every `rsp`-relative offset is identical —
including all **9 `[rsp + 416]` sites** and all **804 rsp-relative reads**, counted in both arms and equal.

⛔⛔ **THEREFORE NO STATIC PREDICATE OVER THE EMITTED CODE CAN DISCRIMINATE THIS DEFECT. That is not an
assessment of difficulty; it is a proof.** Any function of the compiled program returns the same answer for the
crashing arm and the passing arm, because they are the same program apart from an integer in `.rodata`.

✅ **AND IT RETROACTIVELY EXPLAINS EVERY FAILURE ON THIS ROW.** Three static discriminators were tested and
refuted — wall existence/count, wall-dominates-a-fixed-pop (constant across all eight kernels), and
head-bypass edges (`fbench` crashes with 0, clean `queens` has 25). Each was refuted empirically and each
refutation looked like bad luck. **They were not unlucky, they were impossible.** The property being predicted
is not a property of the code.
⭐ The generalised form, and it is the transferable part: **when a control pair differs only in data, every
static predicate is refuted a priori — so the failure of three of them is evidence about the DEFECT'S NATURE,
not about the predicates' quality.** Three independent negative results that each seemed to say "try a better
predicate" were in fact all saying "stop looking statically."

## 3. What this settles, and what it does not

✅ **SETTLED: the discriminator must be dynamic.** The row's recorded lead — *instrument the run-terminal
`add rsp, N` sites and catch the first arrival whose actual depth disagrees with the pop about to be applied* —
is now the only shape that can work, and this witness is the right instrument bed for it: an 8-line program
with a **paired control** (N=8 crash / N=10 pass) that is otherwise identical, which sieve never offered.
✅ **SETTLED: the same defect spans three languages.** SNOBOL4 (FENCE, via frame perturbation), Pascal
(sieve/bubble over-pop), and now Prolog (12 van Roy kernels) all express the one invariant — *a fixed
rsp-relative offset trusted across a call/return boundary with nothing tracking accumulated depth.* ceo's
diagnosis names the Prolog instruction: `call_proc_staged`'s post-call arm re-reading the resume flag at a
fixed `[rsp+416]` after recursion.
⛔ **NOT SETTLED and not claimed:** I did **not** verify ceo's `[rsp+416]` attribution myself — I confirmed the
9 sites exist and are identical across the arms, which is consistent with it but does not establish it. I did
not trace the divergence to an instruction, and no cure is designed. The SIGSEGV/SIGABRT split is unexplained.
⚠️ And the *proof* in §2 is about **emitted code**; a static analysis over the IR with a value-range or
recursion-depth model is not excluded by it. What is excluded is any predicate over the compiled artifact,
which is what all three refuted candidates were.

## 4. Why this row is now the critical path

Per ceo's routing, this one invariant gates: the latent FENCE SIGSEGV on main (the revert bought a frame
layout, not an invariant), the Pascal spine leaks, the sieve/bubble crashes, and **the published Prolog
README grid, which grows by 12 measured multiples the day depth tracking lands**. `fbench` is explicitly NOT in
this set — hq_C has taken it as a separate correctness row after independently confirming its signature differs
in a second mode.
