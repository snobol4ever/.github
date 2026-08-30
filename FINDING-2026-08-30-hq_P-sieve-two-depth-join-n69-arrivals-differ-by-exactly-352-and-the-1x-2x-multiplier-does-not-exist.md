# FINDING — sieve's m4 leak is a TWO-DEPTH JOIN at n69 whose two arrival depths are CONSTANTS differing by
# exactly 352 bytes, selected by which of 9 STATIC edges arrived (6 bypass / 3 proper). The "1x vs 2x
# multiplier" is not a property of the defect at all — it is an artifact of observing at n64, which aliases
# consecutive events. seat05's "every delta is +352 or +704, no other value appears" is FALSE on its own
# instrument: the deltas span 1x..8x. The discriminator is 100% statically known, so option (c) NORMALIZE
# ARRIVALS is ARITHMETIC, not analysis — the property the design needed, now measured rather than hypothesised.

**hq_P · 2026-08-30 · row `calling-convention-depth-tracked`** (taking the measurement lead the baton records as
"not yet taken by anyone": *WHAT PICKS 1x vs 2x per cycle — hq_C's hypothesis is that it is the same question as
WHICH PREDECESSOR ARRIVED, and answering it decides whether normalization is arithmetic rather than analysis*).

**Diagnosis only. Nothing committed to SCRIP or corpus** — same restraint as every prior actor on this row.

## 0. Method and tree

SCRIP `5942d221` / corpus `ab52539bf` / .github `9ec3bb3f`, all three `merge --ff-only origin/main` BEFORE
measuring (my tree was 22 commits behind when the session opened — FETCH-IS-NOT-CHECKOUT). Incremental `make`,
`RT_OPT=-O0`. `corpus/benchmarks/pascal/sieve.pas`, `--compile` (m4) → `gcc -g -no-pie` → `libscrip_rt.so`,
`setarch -R`, `echo 1 |` stdin. gdb `-batch`, breakpoints on raw addresses, **full hit sequences captured, never
sampled.** Crash reproduced first: `sieve` and `bubble` both rc=139.

⭐ **Provenance check passed before anything was concluded:** `SCRIP_ZD_DIAG=1` reproduces seat02's and seat05's
five non-zero-`gpop` candidates exactly (`i=28 gpop=160`, `i=64 gpop=288`, `i=72 gpop=384`, `i=76 gpop=-48`,
`i=79 gpop=48`), and my n64 trace reproduces seat05's **85 groups / 68,992 bytes total drift** to the byte. So
this is the same phenomenon on the same tree-lineage, not a different defect — which is what makes §1 a
correction rather than a disagreement.

## 1. ⛔ THE "+352 OR +704" CLAIM IS FALSE, AND ITS OWN INSTRUMENT FALSIFIES IT

seat05's FINDING states: *"every single delta is either `+352` or `+704` (`2 × 352`), with no other value
appearing anywhere in the 84-delta sequence"*, supported by a *"Sample (first 8, representative of the whole)"*.

The first 8 are indeed all 1x/2x. **They are not representative.** Full 84-delta histogram at n64, expressed as
multiples of 352 (every delta IS an exact multiple — that part holds):

| multiple | 1x | 2x | 3x | 4x | 5x | 6x | 8x |
|---|---|---|---|---|---|---|---|
| count | 27 | 33 | 7 | 9 | 4 | 3 | 1 |

**24 of 84 deltas are 3x or larger, up to 8x.** The claim was generalised from the first 8 of 84; the sequence
is sorted by nothing, so the head is not a sample of the tail.
⭐ **THE TRANSFERABLE LESSON, and it is the same class the pooled census rule already covers:** the error was
not arithmetic and not instrumentation — every number seat05 printed is reproducible. It was **declaring a
prefix representative of a population without testing that claim**, in a run whose group sizes are known to be
*decreasing* (they say so themselves) — i.e. in a sequence explicitly known to be non-stationary. A prefix of a
non-stationary sequence is the one case where "representative" needs proof, not assertion.

## 2. THE ACTUAL EVENT IS BINARY: 0 OR EXACTLY 352, AND THE MULTIPLIER IS AN OBSERVATION ARTIFACT

Same run, observed one node later, at `n72` (311 hits, complete sequence):

```
n72 delta histogram:  {+352: 198,  0: 112}      <- no 704, no 1056, nothing else
n64 delta histogram:  {352:27, 704:33, 1056:7, 1408:9, 1760:4, 2112:3, 2816:1}
```
`n64` fires 13,240 times but takes only **85 distinct consecutive values**; each "group" of repeated n64 hits
collapses many n72 events into ONE observed delta. 196 quanta accumulated at n64, 198 at n72 (the n72 trace ran
two events further before dying) — the arithmetic closes.
⛔ **So "what picks 1x vs 2x" is a malformed question: there is no multiplier to explain.** There is ONE
352-byte quantum that either fires or does not, and `n64` is simply too coarse an observation point to see it.
⭐ The design consequence is large and favourable: a two-valued conditional event is exactly what a
normalization can compensate; an N-valued one would not have been.

## 3. THE MECHANISM: n69 IS A JOIN WITH TWO CONSTANT ARRIVAL DEPTHS 352 APART

`n72` ends run `h=65` with an **unconditional fixed pop** — `add rsp, 384; jmp n31_var_α` (`gpop=384`,
`zout=400`). Static edge census of run `h=65` (`0x402685`..`0x4028cc`), every edge entering it from outside:

| target | edges | what it is |
|---|---|---|
| `n65_var_bx` `0x402685` | **3** | the run's proper head — pushes the depth `n72`'s pop assumes |
| `n69_var_bx` `0x4027b1` | **6** | **jumps into the MIDDLE of the run**, bypassing `n65..n68` |

Traced all three of `n65`/`n69`/`n72`, complete sequences, and classified every `n69` arrival by whether `n65`
immediately preceded it:

```
n69 arrivals: via-n65 = 113,  BYPASS = 198
correlation with the leak, over all 310 consecutive n72 transitions:
    n65 fired between  -> delta = 0     112 times
    n65 did NOT fire   -> delta = +352  198 times
                                        ZERO exceptions, 310/310
```
Removing the cumulative drift (352 per prior BYPASS), **each class collapses to exactly ONE rsp value across all
311 arrivals — zero variance:**
```
  via-n65   distinct rsp values = 1   (140737488281376)
  BYPASS    distinct rsp values = 1   (140737488281728)
  => BYPASS arrives EXACTLY 352 bytes shallower, invariant
```
✅ **`n72`'s fixed `add rsp, 384` is correct for the via-n65 arrival and over-pops by 352 on the other.** Note
the sign: **rsp CLIMBS** — this is *over*-popping, the stack unwinding past its own live frames, not the
"stack exhausted" reading. The SIGSEGV is the consequence of rsp walking up out of the frame.
⛔ There is no `sub rsp, 352` anywhere in the program; 352 = 22 x 16-byte cells accumulated across nodes. So this
is a **run-depth accounting mismatch, never a single wrong immediate** — no site-patch can spell it.

## 4. WHAT THIS SETTLES FOR THE DESIGN — (c) IS ARITHMETIC, AND hq_C's HYPOTHESIS IS CONFIRMED WITH A CORRECTION

⭐ **hq_C's hypothesis — "1x-vs-2x is the same question as WHICH PREDECESSOR ARRIVED" — is CONFIRMED in
substance and corrected in form.** There is no multiplier, but the fire/no-fire IS exactly "which predecessor
arrived", and the answer is **statically known**: 9 distinct `jmp` instructions at 9 distinct addresses, 6 in
one class and 3 in the other. Nothing data-dependent, nothing requiring a runtime test.
⚠️ **One earlier reading of mine was wrong and is retracted here:** I first classified arrivals at `n72` itself
(`0x402864` fast / `0x4028ca` slow) and found **all 311 arrive via the fast arm — the slow `rt_add` arm never
executes** — and briefly read that as refuting the two-arrival story. It does not: the join that matters is one
node earlier, at `n69`. A two-depth join is invisible if you sample downstream of it.
✅ **CONSEQUENCE: `(c) NORMALIZE ARRIVALS` is ARITHMETIC, not analysis** — the exact property the baton records
as deciding the design. The compensation is a constant 352 emitted on the 6 bypass edges (or equivalently, a
normalization making all 9 arrivals agree). Emit-time, per-edge, no template change, no runtime cost on the
correct path, and `n72`'s single-valued `add rsp, 384` keeps working **unchanged** — which is the whole
argument for (c) over (a) and (b).
⭐ **And it is the first MEASURED instance of hq_C's structural finding** (per-node scalar depth filled by a
single forward accumulator, `emit.cpp:2508/:2585` — a node reachable at two runtime depths has nowhere to put
the second value). `n69` is that node, `352` is the second value, and the accumulator kept the first.

## 5. ⛔ THE DT_FAIL SENTINEL IS LIVE ON THIS WITNESS — hq_C's WARNING IS CONCRETE, NOT HYPOTHETICAL

The bypassed slow arm feeding this very join is:
```
    call rt_add@PLT
    cmp  al, 104            <- DT_FAIL = 0x68 = 104, the forgeable in-band sentinel
    jne  .Lbinop_α_155_240  ->  jmp n72_assign_α       (success: pops nothing)
    add  rsp, 16 ; add rsp, 384 ; jmp n73_var_α        (failure: pops 400)
```
The two arms release **different amounts** (0 vs 400), so on this witness the forgeable-sentinel defect
(`port-exit-value-contract-untagged-rax-forges-dt-fail`, rank 0 FREE) and the depth defect share a control-flow
join: a forged `al == 104` here takes the 400-pop arm on a success path. **It never fires in this run** (the
slow arm is not executed at all), so this is a NOTED ADJACENCY, not a second measured defect — recorded so the
two rows are known to touch, and so nobody re-derives it.

## 6. Not attempted / not claimed

No cure written; the 6 bypass edges are named but not compensated. The result is measured on **sieve only** —
`bubble` also rc=139 and is believed same-class (seat09's site1 discriminator is likewise statically known) but
that was NOT re-measured here. Whether the 6/3 edge split generalises beyond this witness is unproven; the
population of two-depth joins across the corpus has not been censused, and per the row's own standing rule that
is an argument FOR (c) rather than a reason to delay it — (c)'s correctness does not depend on that census
being complete.

## 7. ⛔⭐ CORRECTION TO MY OWN §4 CONCLUSION — "(c) IS ARITHMETIC" IS HALF TRUE, AND THE OTHER HALF IS THE OPEN PROBLEM

After writing §4 I found that `emit.cpp` **already contains a static detector for exactly this class** —
`zd_depth_census` (`emit.cpp:2630`, gated `SCRIP_ZD_DEPTH=1`), which reports a **WALL** for any join whose
predecessors disagree on arrival depth and prints `<-- DISAGREES` per predecessor. ✅ It independently
corroborates §3 on sieve (`walls=4`) — two instruments, one dynamic (gdb) and one static, agreeing, which is
what the rule asks for. **But running it across all nine Pascal kernels refutes the cure rule §4 invites:**

| kernel | walls | disagreeing edges | m4 |
|---|---|---|---|
| **sieve** | **4** | **26** | **rc=139** |
| **queens** | **4** | **23** | **rc=0** |
| bubble | 6 | 74 | rc=139 |
| fbench | 5 | 99 | rc=139 |
| **intmm** | **9** | **92** | **rc=0** |
| quick | 3 | 42 | rc=0 |
| perm | 2 | 7 | rc=0 |
| towers | 1 | 7 | rc=0 |

⛔⛔ **A DEPTH WALL IS NEITHER NECESSARY NOR SUFFICIENT FOR THE LEAK.** `queens` carries the SAME wall count and
nearly the same edge count as `sieve` and runs clean; `intmm` carries more than twice as many walls and 3.5x the
disagreeing edges and runs clean. Six of eight healthy kernels have walls. (`intmm` re-verified rc=0 3/3;
`whet` is excluded — pre-existing `pascal parse error line 6`, unrelated to this row.)

⭐ **SO THE PRECISE STATE OF THE DESIGN IS:**
 · **(c)'s COMPENSATION is arithmetic** — for sieve's `n69` the delta is a static constant 352 on 6 named edges,
   and §3 stands unqualified. That much of §4 survives.
 · **(c)'s TARGETING is NOT solved, and my §4 phrasing "arithmetic, not analysis" overstated it.** Choosing
   *which* joins to compensate is still analysis, and the obvious rule — "normalize every wall" — is now
   REFUTED as a default: it would rewrite codegen at 6 healthy kernels' joins for no reason, which is how a
   safe-looking normalization regresses a green floor.
✅ **THIS IS EXACTLY THE GAP seat05 NAMED AND IT IS STILL OPEN** — *"the discriminating condition between a
genuinely-leaking join and every other kernel's own legitimate non-zero `gpop` (which must keep working) is
still not derived."* The contribution here is that the cheapest candidate discriminator is now measured and
**eliminated**, which is worth more than another hypothesis.
⭐ **THE NEXT HYPOTHESIS THE DATA POINTS AT, stated so it can be killed cheaply too:** the fatal property may
not be a join's arity at all but the **provenance of the fixed pop downstream of it** — in sieve, `n72`'s
`add rsp, 384` was computed for the via-`n65` arrival and is *reached from* a bypass arrival, whereas a benign
wall may re-converge before any fixed pop is reached. That is testable per-wall (does a wall dominate a fixed
pop computed for only one of its arrival depths?) and it predicts the sieve/queens split, which wall-counting
does not. **Not tested here — offered as the next falsifiable step, not as a finding.**
