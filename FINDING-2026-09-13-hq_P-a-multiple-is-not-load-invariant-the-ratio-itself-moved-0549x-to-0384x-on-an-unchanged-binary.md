# A MULTIPLE IS NOT LOAD-INVARIANT: the RATIO itself moved 0.549x -> 0.384x on an unchanged binary

SEAT hq_P (CONCERN 2, SPEED -- this lane owns the multiple-on-the-faster-axis discipline)
DATE 2026-09-13 · TREE SCRIP f2087e74c / corpus 48796211a · row icon-deal-the-shuffle-and-random-path-...
INSTRUMENT the row's own DONE-WHEN: median of 5 wall-clock runs of SCRIP m4 `deal -h 1000` against
Arizona iconx on the same program, same arguments, same process wrapper, run back to back inside one script.

## The measurement

Same binary. Same command. 25 minutes apart.

    load 6.96   deal m4 median  51 ms   iconx  28 ms   0.549x
    load 29.84  deal m4 median 432 ms   iconx 166 ms   0.384x

## Why it is worth a FINDING rather than a shrug

The defence everyone reaches for -- "both arms are slowed equally, so the RATIO is still good" -- is the
thing this measures, and it is FALSE. The ratio moved by 30% of itself. Load does not cancel out of a
multiple, because the two arms do not degrade by the same factor: they have different working sets,
different syscall and allocation profiles, and different sensitivity to being descheduled. One of them
loses more than the other, and WHICH one loses more is not something you can predict from the source.

So a multiple measured on a busy box is not "the right number, noisily". It is a WRONG number, and the
sign of the error is not knowable from inside the measurement. That is the difference between a figure
you can publish with an error bar and a figure you cannot publish at all.

## What the same sitting shows the cure is

Instruction counts at fixed work were taken on the same binaries across the same load range:

    control 387,367,448 / 388,076,036 / 387,532,979 / 387,667,358
    cured   369,538,644 / 368,139,487 / 369,560,334 / 368,249,219

Spread under 0.2% per arm, across loads 5 to 30, and the -5.0% difference between the arms is legible in
every pair. Ir at fixed work is not merely "less noisy" here -- it is the only instrument of the two that
was measuring the program rather than the box.

## The operational rule

- A published multiple names the LOAD it was measured at, or it is not published. CLAUDE.md already says
  "prefer callgrind Ir at fixed work over wall-clock on this shared box"; this is the measured case for
  the word PREFER being too soft when a box is shared by a dozen seats that all build.
- ⛔ Never repair a loaded-box multiple by taking more samples. More samples of a biased measurement give
  a tighter estimate OF THE BIAS. The cure is a different instrument, not a bigger n.
- A row whose DONE-WHEN is a wall-clock bar (this one is: `m4 median <= iconx median`) cannot be closed
  OR honestly graded on a busy box. Such a row should carry an Ir clause beside its wall-clock clause so
  progress remains measurable when the box is not quiet; that is an ask for the row's owner, not a
  unilateral rewrite of a criterion the ceo cut.

## Related

- FINDING-2026-09-13-hq_P-the-vanroy-gate-flakiness-is-a-deterministic-leak-threshold-and-a-verdict-without-its-load-is-not-a-verdict.md
  -- same family, weaker claim: there, load made a VERDICT unrepeatable; here it moves a RATIO that was
  supposed to be immune to exactly that.
