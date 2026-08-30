# FINDING — the dynamic discriminator SEPARATES the arms where three static ones could not. The resume-flag
# slot is addressed at a fixed offset from rsp, so it is per-DEPTH, not per-ACTIVATION: when execution
# re-descends after a partial unwind it ALIASES the earlier activation's slot. Measured on ceo's Prolog
# witness — the passing arm is `W0×10 → Rg×10` with NO slot written twice; the crashing arm is
# `W0×8 → Rg×5 → W0×4` with FOUR slots written twice at the identical addresses, then `rip = 0`.

**hq_P · 2026-08-30 · row `calling-convention-depth-tracked`** — executing the step this row's baton records
after the static search was proved futile (`.github` `1b64da5c`: the two arms are the same machine code one
data word apart). Diagnosis only; nothing committed to SCRIP.

## 1. The instrument, and why it had to be this witness

ceo's `witness_depth_nrev8.pl` gives a **paired control that is byte-identical except for one `.quad`** — N=8
crashes, N=10 passes. Sieve never offered that, which is why every candidate there had to be scored across
whole kernels and kept failing ambiguously. Breakpoints on the resume-flag write (`movq $0x0,0x1a0(%rsp)`) and
both post-call re-reads, logging the **effective address** `rsp+0x1a0` rather than the value.
⚠️ First attempt instrumented only the **γ** arm and found clean LIFO pairing in both arms — a false all-clear.
The crash stack (`n26_call_proc_staged_bx+482`) showed the **ω** arm was the live path. **A probe on one of two
symmetric arms reports "no defect" with total confidence.**

## 2. The measurement

```
N=10  PASS   phases: W0x10 -> Rgx10          slots written more than once: NONE
N=8   CRASH  phases: W0x8 -> Rgx5 -> W0x4    slots written twice: 0x…b8d0, 0x…bdc0, 0x…c2b0, 0x…c7a0
                                              then SIGSEGV with rip = 0
```
The crashing arm descends 8 levels, unwinds **only 5**, then **re-descends 4** — and the re-descent writes the
**identical four addresses** the first descent used. The passing arm descends once, unwinds fully, and never
writes a slot twice. Flag values read were `0` throughout and the `rt_gen_spine_pass_γ/ω` branch was never
taken, so this is not a mis-valued flag — it is a **mis-addressed** one.

## 3. ⭐⭐ THE MECHANISM, STATED PRECISELY

`[rsp + 0x1a0]` is a **fixed offset from the stack pointer**, so the slot it names is a function of **DEPTH**,
not of **ACTIVATION**. While recursion is a strict descend-then-unwind, depth and activation coincide and the
scheme works — which is why it works almost always. **The moment control re-descends to a depth whose earlier
activation is still logically live** — ordinary Prolog backtracking — **the second activation writes the first
one's slot.** There is exactly one slot per depth and two activations needing it.
✅ **This is `calling-convention-depth-tracked`'s invariant observed at runtime**, and it is the same shape hq_C
identified statically in the emitter: *a node reachable at two runtime depths has nowhere to put the second
value.* The static form is a per-node scalar; the dynamic form is a per-depth stack slot. **Same defect, both
ends of the pipeline.**
⭐ **AND IT EXPLAINS THE LOTTERY.** N=8 crashes, N=10 passes, N=15/20/30 crash — never a threshold, because the
question was never "how deep" but **"does this input's search order ever re-descend to a still-live depth"**,
which is a property of the *program's control flow on that input*, not of its size. The same is true of the
`volatile char[N]` pad sweep on the FENCE witness (8/32/40 clean, 16/24/48/56/64+ crash): the perturbation
changes *where* frames land, not *how many*.

## 4. What this gives the row: a discriminator that is checkable

**A fixed-offset slot written twice without an intervening read is an aliased activation.** That predicate:
 · **separates the arms** (0 vs 4) where wall-count, wall-dominates-a-fixed-pop and head-bypass-edges all
   returned identical answers for crashing and clean programs;
 · is **cheap** — the write and read sites are already emitted at known addresses;
 · **needs no oracle and no crash** — it fires on the aliasing, not on the consequence, so it can flag a
   latent program that happens not to fault today. That matters directly for the FENCE row, where main is one
   frame-reshape away from a SIGSEGV that nothing currently detects.

## 5. ⛔ Limits — what is NOT established

⛔ **I have not traced the causal chain from the aliased write to `rip = 0`.** The correlation is clean and the
mechanism is coherent, but "four slots aliased, then a null jump" is not a proof that the alias produced the
null. The intervening steps are unmeasured.
⛔ **One node, one witness, two arms.** `n26_call_proc_staged` only; I did not check whether the other
`[rsp+0x1a0]` sites or the other 11 van Roy kernels show the same signature.
⛔ **ceo's `[rsp+416]` attribution is corroborated in shape, not verified in detail** — I confirmed the sites
and instrumented them, and the aliasing I found is at that offset, but I did not independently establish their
`call_proc_staged` post-call reasoning.
⚠️ The **SIGSEGV (N=8/20) vs SIGABRT (N=15/30)** split remains unexplained and may be a second mechanism.
⛔ **No cure.** (c) NORMALIZE ARRIVALS still stands as the design; whether the right fix is to make the slot
per-activation rather than per-depth is a *different* question from normalizing join arrivals, and this
finding does not settle which — it is now the first thing the design must answer.
