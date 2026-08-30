# FINDING — the two remaining candidate discriminators for the depth defect are BOTH refuted by measurement,
# and the "three crashing Pascal kernels" are NOT one defect: fbench faults on `jmp *%rcx` with a healthy rsp
# while sieve and bubble share the rsp-unwound-past-stack-top signature. Also: 100% of walls in BOTH the
# crashing and the clean kernels sit in a run with a nonzero terminal pop, and fbench crashes with ZERO
# head-bypass edges while clean queens has 25 — the most of any kernel.

**hq_P · 2026-08-30 · row `calling-convention-depth-tracked`** — taking the falsifiable next step this row's own
baton recorded (*"kill it or confirm it on queens vs sieve first — one counterexample either way settles it"*).
It is killed. Diagnosis only; the instrument change is the sole code delta.

## 0. Where this row stood

Two things were already established and are unchanged: sieve's `n69` is a two-depth join whose arrivals are
constants exactly 352 apart, selected by 6-vs-3 static edges (measured, 310/310); and **wall-counting is not
the discriminator** (sieve 4 walls crashes, queens 4 walls clean, intmm 9 walls clean). This session tested the
two candidates that survived that.

## 1. ⛔ CANDIDATE 2 — "the wall dominates a FIXED POP computed for only one arrival depth" — REFUTED, MAXIMALLY

The baton's recorded hypothesis: *the fatal property may not be a join's arity but the provenance of the fixed
pop downstream of it.* To test it I first had to make walls correlatable to runs at all — the census printed op
names only, no node index (see §4). With indices:

| prog | state | walls | walls in a run whose TERMINAL POP is nonzero |
|---|---|---|---|
| sieve | CRASH | 4 | **4 / 4** |
| bubble | CRASH | 6 | **6 / 6** |
| fbench | CRASH | 5 | **5 / 5** |
| queens | ok | 4 | **4 / 4** |
| intmm | ok | 9 | **9 / 9** |
| quick | ok | 3 | **3 / 3** |
| perm | ok | 2 | **2 / 2** |
| towers | ok | 1 | **1 / 1** |

**Every wall in every kernel qualifies, in both classes.** The predicate has no discriminating power whatsoever
— it is not weak, it is constant. Refuted.

## 2. ⛔ CANDIDATE 3 — "edges entering a run BELOW its head" — REFUTED IN BOTH DIRECTIONS

This one was the strongest candidate, because it is the mechanism I *proved* on sieve: 6 static edges jump into
run `h65` at `n69`, bypassing the head's push, so the terminal's fixed `add rsp,384` over-pops by 352. Counting
that edge class across the kernels (jumps from outside a run into a non-head member of it):

| prog | state | head-bypass edges | where |
|---|---|---|---|
| sieve | CRASH | 8 | h0@n10×1, h29@n31×1, **h65@n69×6** |
| bubble | CRASH | 10 | h0@n12×1, h0@n67×7, h71@n73×2 |
| **fbench** | **CRASH** | **0** | **(none)** |
| **queens** | **ok** | **25** | h0@n5×3, h88@n90×3, **h92@n93×19** |
| intmm | ok | 7 | seven single edges |
| quick | ok | 12 | four sites ×3 |
| perm / towers | ok | 0 / 0 | (none) |

⛔ **NOT SUFFICIENT: `queens` carries 25 head-bypass edges — more than any other kernel — and runs clean.**
⛔ **NOT NECESSARY: `fbench` crashes with ZERO.**
⭐ This does **not** retract the sieve result: that bypass *is* sieve's mechanism, proven dynamically. What it
kills is the generalisation — **a head-bypass edge is fatal in sieve and benign 25 times over in queens**, so
the edge class alone cannot be the targeting rule (c) needs.

## 3. ⭐⭐ THE STRUCTURAL CORRECTION — THE CRASHING SET IS NOT ONE DEFECT

Everyone, this baton included, has treated `{sieve, bubble, fbench}` as one class. **Their crash signatures say
otherwise** (m4, `gdb`, same tree):
```
sieve   rsp=0x7ffffffff090  n31_var_bx+19:        mov %rax,(%rsp)
bubble  rsp=0x7ffffffff050  n78_var_bx+19:        mov %rax,(%rsp)
fbench  rsp=0x7ffffffed860  transitxsurface_ω+20: jmp *%rcx
```
✅ **sieve and bubble are the same shape** — a store through an rsp that has been unwound *above* the stack top,
which is the over-popping signature the sieve trace established.
⛔ **fbench is a different fault entirely**: an indirect jump through `rcx`, at an rsp in a perfectly normal
range, and with zero head-bypass edges. **It does not belong in the depth bucket**, and its presence there is
why both discriminators above look like they fail in the "not necessary" direction — they are being asked to
predict a crash that has another cause.
⛔ **Consequence for the row: re-test any future discriminator against `{sieve, bubble}`, not against
`{sieve, bubble, fbench}`.** A rule scored against a mixed set will be rejected for the wrong reason.
⚠️ Kept honest: I have NOT diagnosed fbench. "Different signature" is evidence of a different fault, not proof;
it could still share a root that expresses differently. What is established is that it is wrong to *assume*
homogeneity, which is what was being assumed.

## 4. INSTRUMENT — the wall census could not be correlated to anything, and now can

`zd_depth_census` (`emit.cpp`, `SCRIP_ZD_DEPTH=1`) printed walls by **op name only** — no node index — so a wall
could not be tied to its run, its terminal, or the `[ZD]` diag's per-node `gpop`. Every analysis in §1 was
impossible to state before this. Added: `i=<idx>` plus the wall's own `gpop`/`zout` on the WALL line, and
`i=<idx>` plus `gpop` on each predecessor line. Diagnostic path only, `getenv`-gated, emits nothing by default.

## 5. Where the row actually stands, and what NOT to try next

Three candidate discriminators are now eliminated by measurement: **wall existence/count**, **wall-dominates-a-
fixed-pop**, and **head-bypass edges**. ⭐ That is the useful output — each was cheap to believe and none
survives contact with the clean kernels, and the pattern in all three failures is the same: *the structure the
crashing kernels exhibit is also present, often more abundantly, in kernels that work.*
⛔ **DO NOT propose a rule fitted to the four sieve data points** — I started to see a "wall is at a run head or
head−4" pattern and abandoned it deliberately: a magic constant fitted to a handful of points is the
generalised-from-a-prefix error this project has already paid for once.
⭐ The next honest step is probably **dynamic, not static**: sieve's fatality was established by *watching rsp
drift*, not by any static property, and the one thing that separated the two arrival classes there was a
runtime observation (310/310 correlation). A discriminator that no static predicate has captured across three
attempts may simply not be static.
**Not attempted:** no cure, no planner change, and `{sieve, bubble}` was not re-tested as a two-member set
against a fresh candidate — there is no fresh candidate yet.
