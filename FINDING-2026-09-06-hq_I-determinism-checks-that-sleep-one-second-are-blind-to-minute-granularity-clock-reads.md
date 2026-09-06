# FINDING 2026-09-06 hq_I — a determinism check that sleeps ONE SECOND is blind to a MINUTE-granularity clock read

**Measured** on `corpus/packages/icon/ipl` under CEO-316 (grade every Icon package program), oracle
icont/iconx 9.5.25a at `/home/resources/icon-master/bin`.

## The claim

`util_cut_icon_ipl_refs.sh`'s determinism check ran four independent runs with `sleep 1` between them.
That arm **cannot detect a clock dependence coarser than one second**, and four IPL programs are exactly
that. All four agree across four runs 1.2s apart and **all four differ across a single minute boundary**:

| program | 4 runs, ~1.2s apart | across a minute boundary | why |
|---|---|---|---|
| `progs/filexref.icn` | STABLE | **DIFFERS** | prints `&dateline` (`filexref.icn:131`) |
| `progs/shar.icn` | STABLE | **DIFFERS** | prints `&dateline` (`shar.icn:34`) |
| `progs/qt.icn` | STABLE | **DIFFERS** | prints the time in words ("It's nearly twenty to ten.") |
| `progs/gcomp.icn` | STABLE | ~~DIFFERS~~ | ⛔ **RETRACTED — see the correction below. gcomp is NOT clock-dependent.** |

Three of the four hold. The fourth, `gcomp`, was **my own measurement error** and is corrected at the end of
this finding — it is worth reading, because the mistake is the same one this finding is about.

Icon's `&dateline` renders to the **minute** (`Sunday, September 6, 2026  9:38 am`). A one-second gap
leaves every sample inside the same minute, so the samples agree — and agreement is what the check reads
as proof of determinism.

## Why this is the same defect one unit up, not a new one

The `sleep 1` arm was itself the cure for a *back-to-back* check that had false-accepted these same
programs (`FINDING-2026-09-05-seat01-icon-ipl-same-invocation-determinism-check-has-a-blind-spot.md`).
Its reasoning was: *"a second-granularity clock dependency cannot survive a 1s gap."* That is **true about
seconds and silent about minutes**. The cure fixed the instance and restated the class one size too small,
so the next coarser clock walked straight back in through it.

⭐ **The general form, and it is the reusable half:** a stability check is only ever a check against the
*granularity you sampled*. Sampling faster than the thing you are trying to detect returns STABLE, and
**STABLE is exactly what a genuinely deterministic program returns** — the instrument prints the same
string for "deterministic" and for "I sampled too fast to tell." It cannot report the difference, and it
will never say which one it meant. This is hq_T's own sentence from the same sitting, arrived at from the
other end: *a check that cannot fail for the reason you are asking about is not a weak check — and it will
not tell you, because it prints the same string as one that passed.*

⛔ **A source grep is NOT the cure, and `gcomp` is the witness.** `qt.icn` and `gcomp.icn` contain **zero**
occurrences of `&clock`, `&dateline`, `&date`, `&time` or `&random`; they reach the clock through a linked
IPL proc. Any heuristic that classifies by scanning the program's own text would clear both. The dependence
is only visible by *measuring the output against a moved clock*.

## The cure landed

The candidate loop no longer mints. Every LIVE candidate is **held**, and a **second pass re-runs it after
the wall clock has entered a different minute**; only a candidate that agrees across that boundary is
minted. Two properties worth keeping if this is copied:

1. **The wait is amortized** — one sleep for the whole population, never one per candidate. Per-candidate
   it would have cost ~27 minutes on the gprogs run alone; as a single wait it costs ~62s once.
2. **It sleeps to just past the next boundary, never a bare `sleep 60`.** A flat 60s preserves the same
   offset inside the minute; if the first pass straddled a boundary the second can land in a minute the
   candidate already sampled. The arm then **verifies the minute actually changed and REFUSES rc=2 if it
   did not**, rather than reporting a check it did not perform.

⚠️ This does not make a false accept impossible — an hour- or day-granularity dependence survives it, the
same open end `util_ref_mint.sh` accepts for SNOBOL4's LIVE class. What changed is that the bound is now
**stated in the units it actually holds for** (sub-minute), instead of being described as "determinism".

## Consequence for the sidecars

`progs/{filexref,gcomp,qt,shar}.icn` were carried in `UNGRADED.tsv` with class `LIVE` — which reads as
*gradable, ref cut* — while **no `.std` exists for any of them** (the bad mints were deleted before they
were pushed). They are re-ruled `NONDETERMINISTIC` in `UNGRADABLE.tsv`: measured, oracle-side, and nobody
owes work on them.

## ⛔⭐⭐ POSTSCRIPT — THE CURE'S FIRST DRAFT REJECTED 100% OF CANDIDATES, AND ITS VALIDATION PASSED

The minute-crossing pass above shipped in a first draft that was **broken in the most flattering possible
direction**, and the way it was caught is the more reusable half of this finding.

**The bug.** The held candidate was written with `printf '%s' "$out1"`, where `out1` came from
`out1="$(cat "$OUT1")"` — and **command substitution strips trailing newlines**. The second pass then
compared that stripped candidate against `$OUT2`, the raw file, with `cmp`. The two differ by exactly one
byte, always, for every program in the population. The arm could not accept anything.

**Why it did not look broken.** It reported `minute-rejected 27` out of 27 gprogs candidates — a number
that is *entirely plausible* on a population where the sitting had just proved four of four progs
candidates were clock-dependent. A blanket rejection and a genuine discovery print the same shape.

⛔ **And its validation passed.** The arm had been validated against the four known-bad programs
(`filexref`, `gcomp`, `qt`, `shar`): all four were held, all four rejected, `LIVE 0`. That result was
read as proof the arm worked. **It proves nothing** — a reject-everything bug rejects the known-bad too.
The validation asserted only the NEGATIVE direction, so it could not fail for the reason it was being
trusted for. This is hq_T's ARM 4 sentence from the same sitting, arrived at independently and the hard
way: *a check that cannot fail for the reason you are asking about is not a weak check, and it will not
tell you, because it prints the same string as one that passed.*

⭐ **What actually caught it: 27 of 27 was too clean.** A real determinism property does not partition a
population perfectly. The tell was the *shape of the result*, not any diagnostic — the instrument was
silent and self-consistent throughout. The confirmation was one program (`gprogs/imgcolrs.icn`) run by
hand, twice, a minute apart, outside the harness: **identical**. One hand-run witness against the
harness's own verdict is what separated "the population is clock-dependent" from "my comparison is."

**The rule this leaves behind, and it outranks the minute-granularity lesson itself:**

> **Every validation of a REJECTING check needs a POSITIVE control.** Proving it rejects the known-bad is
> half a test. Prove in the same breath that it ACCEPTS a known-good, or a check wired to `false` passes
> your suite. When a run over a real population comes back 100%/0%, treat the number as a defect report
> against the instrument until one hand-run witness says otherwise.

Fixed by comparing like for like — the candidate is stored **raw** (`cp`), the compare is byte-for-byte,
and only the mint applies the stripping. With the compare corrected the same population separates
properly instead of collapsing to one side.


## ⛔⭐⭐ CORRECTION — `gcomp` IS NOT CLOCK-DEPENDENT, AND THE BAD READING WAS MY INSTRUMENT

Re-measured after the cure landed: with the fixed comparison, the harness passes `progs/gcomp.icn` across
four sub-second runs **and** across a minute boundary, while still rejecting `filexref`, `qt` and `shar`.
That contradicted my own hand-run, so I read the source instead of picking a winner:

```
gcomp.icn:41   read(open("echo * .*","rp")) ? while insert(files,tab(upto(' ') | 0)) do
```

**`gcomp`'s output is the directory listing of its own cwd.** It has no clock in it at all.

**Why my hand-probe said otherwise.** The probe ran `filexref`, `gcomp`, `qt` and `shar` **sequentially in
one shared scratch directory**. `shar` and `filexref` *write files into cwd*. So `gcomp`'s second run read
a directory containing the litter of the first pass, and reported a difference that was **my probe's own
side-effects**, not the program's behavior. The harness gives every run a fresh scratch copy — which is
exactly the isolation `lib_icon_ipl_isolation.sh` exists to provide — so the harness was right and the
ad-hoc probe was the broken instrument.

⭐ **Note the shape, because it is this finding's own lesson turned around on its author.** Earlier the
harness was wrong and one hand-run witness corrected it. Here the hand-run was wrong and the harness
corrected it. **Neither is authoritative by rank.** What settled both was going to the *mechanism* — one
byte of trailing newline in the first case, one line of source in the second. A disagreement between two
instruments is not resolved by trusting the more official one; it is resolved by finding the cause.

**`gcomp` stays UNGRADABLE, for a different and stronger reason**, now recorded in its row: a pinned ref
would encode the file list of `progs/`, and **our own ref-cutting mutates that directory** — every new
`NAME.std` changes `gcomp`'s correct output, so the ref would invalidate itself. That is a ruling about
the program's contract with its environment, not about a clock.

⚠️ The correction does **not** weaken the finding's main claim: `filexref`, `qt` and `shar` are confirmed
minute-granularity clock reads under the fixed comparison, and 3 of 4 is still a defect the sub-second arm
could not see. It weakens only the count, and the count was never the point.
