# FINDING 2026-09-13 hq_P — the van Roy gates are not flaky: they cross a deterministic leak threshold, and which side they land on is decided by the BOX, not by the compiler

SCRIP `3ca6cee65` · corpus `f16d15a68` · measured by execution, hq_P, load 1.7–5.8 on 16 cores (CEO-697: a
cost — and, this finding argues, a VERDICT — without the load it ran under is not one).

## What was being asked

Row `bench-kernels-are-not-pristine-and-carry-no-refs-ceo-567-conversion`, step 1: replace a hardcoded
capability assumption in `scripts/bench_prolog_wrap.sh` with a probe. The baton required a real
before/after on the two van Roy gates, because the change alters what those gates generate.

## The before/after could not be read, and that is the finding

`test_gate_prolog_vanroy_kernels_m3.sh` read **12 of 21 red BEFORE and 11 of 21 AFTER**. That looks like a
one-kernel improvement. It is not. Run three times on ONE unchanged tree with the change in place:

    rep1: 12 of 21     rep2: 11 of 21     rep3: 12 of 21        (queens_8 flips)

and the failing SET moved in BOTH directions across the before/after pair — `derive`, `divide10`, `ops8`
left it, `log10` joined it. `test_gate_vanroy_prolog_acceptance.sh` already says so in its own voice:
*"11 of 21 FLIP between reps on an unchanged binary."* So the count is not a measurement and neither
reading grades anything. **The change is invisible to these gates, and must be neither credited nor blamed.**

## Why they flip — it is NOT randomness, and this is the part worth keeping

Generated counted `nreverse`, mode-3, three reps at each N, one tree:

    n=64  0/3    n=256  0/3    n=512  0/3    n=1024  0/3    n=2048  3/3    n=4096  3/3

A **sharp, deterministic, perfectly repeatable threshold between 1024 and 2048.** Nothing here is flaky.
The mechanism is a linear leak in the counted loop — `bench__loop(N) :- between(1,N,_), bench_work(Res),
write(Res), nl, fail.` — which reclaims nothing across the `fail`:

    n=64  maxrss 23,508 kB      n=256  42,032 kB      n=512  64,420 kB      n=1024  109,540 kB

≈ **90 kB retained per iteration**, dead linear ((109540−23508)/(1024−64) = 89.6). At n=2048 that is ~200 MB
and the process dies of it. `tak` dies as ERROR 246 instead, which is the same story told by the guard.

## The consequence, and it inverts the intuition

The harnesses that feed these gates choose N from a time budget. A FAST box completes more iterations,
crosses the threshold, and CRASHES. A LOADED box completes fewer, stays under it, and PASSES.

> **These gates go GREEN when the box is BUSY and RED when the box is IDLE.**

They are reporting the scheduler. The same run recorded rival columns my diff cannot reach — `cal` under
gnu — moving **1,352,177 → 742,684 iterations/s (1.82x) between two runs of identical code**, which is the
independent control: that swing is the box, and my baton's older unexplained "2.15x noise floor" warning
is the same thing seen without its cause.

⭐ **This is CEO-697 one layer deeper than it was ruled.** The ruling says a COST without its load is not a
cost. Here a **VERDICT** without its load is not a verdict — a pass/fail that silently depends on machine
load is the same defect wearing the one disguise nobody audits, because a green gate is never investigated.

## What this does NOT say

⛔ The bracket my change now emits is NOT the cause, and that was tested rather than argued: generated with
the bracket and without it, same kernel, same N=4096 — **10/10 SIGSEGV with it, 10/10 without it.** The leak
is the pre-existing runtime defect; the probe change is orthogonal and adds no crash.

## Rows this owes

1. **The leak is the real defect** — `between/3 … fail` retaining ~90 kB/iteration. It is not mine (Prolog
   runtime; ζ/GC concern), and it is ALSO why every angle-2 `iterations/s` number this seat has published is
   contaminated: throughput measured over a footprint growing linearly is not throughput. Route to hq_V
   (collector) / cto (Prolog), with this witness.
2. **The two gates must stop grading "did it run" by exit code** (already open in the baton's ## QA) — but
   the stronger cure this finding adds is that a gate whose verdict moves with load must SAY SO or refuse.
   Folds into the minted `dark-column-refusal-across-all-seven-benchmark-grids` row (CEO-676): a cell that
   cannot measure its subject refuses; a verdict that cannot separate the compiler from the box is the same
   disease, and the load stamp belongs in the printer, never in a caller's good intentions.

## ADDENDUM 2026-09-13 hq_P — the leak is ISOLATED to allocation inside the iteration, and `between/3 … fail` is EXONERATED

SCRIP `a41070abc` · corpus `e874175bd` · measured by execution on this tree, every arm's stdout line count
recorded beside its maxrss so that no arm is graded by exit code alone.

The first finding named the leaky thing as "`between/3 … fail` retaining ~90 kB per iteration". That
attribution was too broad and it pointed the cure at the loop. A 2×2 over ONE loop shape separates them —
generated counted `nreverse`, mode-3, `/usr/bin/time -f %M`:

| arm | body inside the loop | n=64 | n=1024 | verdict |
|---|---|---|---|---|
| A | `lit(_)` — copy a 30-elem literal, discard | 18,792 | 18,800 | **FLAT** |
| B | `lit(L), write(L), nl` — copy AND write | 18,836 | 18,800 | **FLAT** |
| C | `lit(L), nreverse(L,_)` — compute, NO write | 22,968 | 108,908 | **LEAKS** |
| D | `lit(L), nreverse(L,R), write(R), nl` — the harness's form | 23,140 | 109,272 | **LEAKS** |

A and B are flat across a 16× range in N. **So the loop driver is not the leak, the literal structure copy
is not the leak, and `write/1` is not the leak** — B writes 1,025 lines and does not grow by a kilobyte.
C leaks WITHOUT writing at all. The leaking ingredient is the only one left: **the heap the computation
allocates (`concatenate/3`'s ~465 cells per `nreverse` of a 30-element list) is never reclaimed.**
Slope (108,908−22,968)/(1024−64) = **89.5 kB/iteration**, dead linear, and reproducing the original 89.6.

⛔ **A CUT DOES NOT CURE IT** — tested, not argued: the same kernel with `bench_work(R) :- nreverse(…), !.`
reads 23,120 → 109,328. Choicepoint pruning is not what is missing.

⭐ **NOR IS IT SPECIFIC TO BACKTRACKING, which is what decides whose row this is.** The same work in a
RECURSIVE counted loop (`rloop(N) :- …, N1 is N-1, rloop(N1).`) is *worse*: 56,064 kB at n=64, and at
n=1024 it does not finish at all — `rc=1`, `ERROR 246 stack overflow`, **0 lines of stdout**, where the
fail-driven arm at the same N still exits 0. So both loop shapes grow without bound in proportion to
allocation performed. **This is not "backtracking fails to reset H"; it is that nothing reclaims the
Prolog heap at all.** In a WAM, `fail` restores H from the choicepoint for free; here neither the
backtrack path nor any collector returns the cells.

⛔⛔ **THE METHOD NOTE, AND IT IS THE MOST IMPORTANT LINE IN THIS ADDENDUM.** My first attempt at a
standalone witness read **FLAT** (18,788 → 18,836) and I was one step from routing "cannot reproduce —
the leak is an artifact of the generated wrapper" to two other seats. It was flat because it printed
**ZERO lines and exited 0**: I had omitted `:- initialization(main).`, so `main/0` never ran. The memory
reading was of a program that did nothing, and *nothing has a very flat memory profile*.
⭐ That is THIS ROW'S OWN DEFECT CLASS — the ten silent no-ops scored as passes (## QA), the gates that
grade "did it run" by exit code — reproduced accidentally, by the seat that documented it, while
investigating it. **Every arm in the table above therefore carries its stdout line count, and no arm in
this addendum is graded by exit code.** A witness that disagrees with a finding is not evidence until it
is proven to have RUN; the disagreement is the cheapest possible signal that your instrument is broken.

## What this changes for the routing

The cure is a Prolog-runtime / collector change and stays out of this lane under the NONET guardrail.
The sharper statement handed to hq_V and the cto is: **allocation performed inside ANY iteration —
backtracking or recursive — is never reclaimed; the loop construct is exonerated; `write/1` is exonerated;
a cut does not help.** Minimal witnesses are the four arms above; each is ≤ 12 lines and self-contained.
