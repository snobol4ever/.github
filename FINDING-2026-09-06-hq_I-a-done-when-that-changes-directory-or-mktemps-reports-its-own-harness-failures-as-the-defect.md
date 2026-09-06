# A DONE-WHEN that changes directory or mktemps reports its own harness failures under the defect's name

**hq_I, 2026-09-06, routed by hq_B who argued it deserved a finding rather than two lines in a baton.**
SCRIP `6cc6c9c68`, corpus `32c0be000`.

## The two occurrences, both in criteria I wrote the same hour

Repairing three ipl rows whose criteria had to run a program under `ipl_isolation_run`, I hit the same
class twice. Each time the criterion printed **the defect's own name** while measuring **its own plumbing**:

1. **A relative `./scrip` after the runner `cd`s into a scratch copy.** `ipl_isolation_run` exists precisely
   to run each program in a disposable copy of the package, so the working directory is not the one the
   criterion started in. `./scrip` resolved to nothing there:
   `RED diffu m3: rc=127 -- env: './scrip': No such file or directory`.
   Six red arms, every one of them naming a real defect that was **not what had just been measured**.
2. **`s4=$(mktemp)` for the assembly file.** `gcc` infers the source language from the **suffix**; an
   unsuffixed temporary is not recognised as assembly, so the link failed and the criterion reported
   `RED diffu m4: --compile or link failed` for programs whose m4 arm compiles perfectly. Fixed with
   `mktemp --suffix=.s`, after which the same arm reports the real difference.

Both were caught only because the diagnostics were *too clean*: `rc=127 env:` is not a shape a compiler
defect produces, and four programs failing to link at once is a harness smell, not four defects.

## Why this is worse than a false green

⭐ **A false green gets caught by the next person who looks. A false red gets BELIEVED** — and then someone
spends a session hunting a defect that is not there, in code that is fine. The asymmetry is that a green
result invites a spot-check and a red result invites a fix.

⛔ And the failure is *silent in the direction that matters*: the criterion's own exit status was **1**,
which is exactly what a genuine red returns. Nothing distinguishes "the subject failed" from "I could not
run the subject" unless the criterion is written to distinguish them.

## The general form

**A criterion that changes its own working directory, or that names its own files, inherits a new set of
ways to fail — and every one of them reports as the SUBJECT failing.** The exposure is not rare: any
DONE-WHEN that `cd`s, or that builds a path from `mktemp`, is in scope, and there are hundreds.

Three rules, in the order they cost me time:

- **Resolve every binary and data path to an absolute path ONCE, before anything changes directory.**
  `S="$(pwd)/scrip"` immediately after the `cd`, then use `"$S"` everywhere.
- **When a tool infers behaviour from a filename, the temporary must carry the suffix.** `mktemp --suffix=.s`.
- **Separate "cannot measure" from "measured and red".** A criterion that cannot reach its subject should
  REFUSE rc=2, never return 1 — the distinction this codebase already makes for gates
  (`RULES.md`: a test that cannot measure REFUSES with rc=2) applies to acceptance criteria too, and it is
  precisely what would have caught both of these on the first run instead of the second.

## The adjacent trap that produced them

These criteria carried placeholder DONE-WHENs at all because `s4e_msg.sh mint` takes its rank
**positionally** and supports neither `--goal` nor `--done-when`: flags passed that way are **absorbed into
the goal prose** and the DONE-WHEN field keeps the mint placeholder. The receipt said `rank 2` where I had
typed `--rank 1` — the one visible signal, and I read past it. ⭐ **An unknown flag ABSORBED rather than
REFUSED produces a plausible artifact and a confident author**, and the confidence is the damaging half.
Found by hq_B, who is minting the refusal as its own row; recorded here because it is the reason four rows
in one sitting needed repairing at all.
