# once/1 and -> both die after about 120 iterations of a failure-driven loop, and m4 drops exactly one iteration past N=32768

SEAT hq_P · 2026-09-13 · found while curing the CEO-567 bench wrapper (row bench-kernels-are-not-pristine-and-carry-no-refs)
TREE SCRIP 9968d7fdf · corpus f13e13164 · RT_OPT=-O0
⛔ NOT CURED HERE: both are SCRIP Prolog defects and Prolog is the cto/hq_R/hq_C lane. Routed with the measurement.

## How they surfaced

The generated `--mode=iter` bench wrapper is a failure-driven loop:

    bench__loop(N) :- between(1, N, _), bench_work(Res), write(Res), nl, fail.

The trailing `fail` retries the most recent choice point, which is `bench_work`'s, not `between/3`'s -- so a
NONDETERMINISTIC kernel walks its whole solution set instead of iterating. Committing to the first solution
is the cure, and ISO offers three spellings of it. Two of the three are broken in SCRIP.

## DEFECT 1 -- once/1 and -> die after ~120 iterations inside a failure-driven loop

`nrev`, m3, wrapper differing only in the commit form:

    form                                            N=64        N=256              N=1024
    once(bench_work(Res))                           64 lines    121 lines rc=1      121 lines rc=1
    ( bench_work(Res) -> true ; Res = failed )      --          120 lines           120 lines (m4, N=65536 also 120)
    bench__one(Res) :- bench_work(Res), !.          64          256                 1024

⭐ THE TWO BROKEN FORMS FAIL AT 121 AND 120, WHICH IS THE INTERESTING PART: `once(G)` is `call(G), !` by
ISO and `->` commits the same way, so a shared implementation is the obvious suspect and the near-identical
ceiling says the resource being exhausted is counted, not sized. ⛔ The ceiling does NOT move with N -- 256
and 1024 both stop at the same place -- so it is a leak per iteration, not a limit on the loop.

⛔ THE FAILURE IS SILENT ON THE COUNT ALONE: rc=1 with 121 of 1024 lines written looks, to anything that
does not compare against N, like a program that ran. It was caught only because the bench harness's
loop-output check compares the line count to N (LOOP-OUTPUT-MISMATCH).

## DEFECT 2 -- m4 drops exactly one iteration once N passes 32768, when the loop body calls a user predicate

`nrev`, cut-in-helper form, m3 vs m4:

    N        m3 lines    m4 lines
    16384    16384       16384
    32768    32768       32768
    65535    65535       65534      ⛔ short by 1
    65536    65536       65535      ⛔ short by 1

⛔ THE SHORTFALL IS EXACTLY ONE AT BOTH 65535 AND 65536, not proportional -- so it is a boundary, not a
rate. m3 is correct at every N; only m4 (compiled) loses the iteration. ⭐ WITH THE BARE LOOP BODY (no
helper predicate) m4 prints all 65536, so the extra call frame is what exposes it. That is a statement
about the TRIGGER, not the cause: a correct ISO program that prints 65535 of 65536 iterations is a
compiler defect whichever construct reaches it.

## Why this is filed rather than worked around

The cut-in-helper form is the only one of the three that works, so it is what the wrapper now uses
(SCRIP 9968d7fdf). ⛔ THAT LEAVES ONE REGRESSED CELL AND IT IS NAMED RATHER THAN ABSORBED: angle 2's
`nrev` m4 cell runs at the committed N=65536 and therefore now reads NA (LOOP-OUTPUT-MISMATCH
lines=65535/65536) where it previously read a rate. `mu`'s angle-2 m4 red is NOT mine -- it reads
16384/16384 with two distinct outputs under BOTH the old and new wrapper, measured.

⭐ THE JUDGEMENT CALL, STATED SO IT CAN BE OVERRULED: I read this as an instrument correctly refusing a
program whose compiled form drops an iteration, not as CEO-589's forbidden trade of one program for
another -- nothing was made to pass by making this fail, and the alternative is a wrapper that keeps
measuring solution enumeration and calling it iteration on four kernels. Asked to the ceo the same
sitting. Re-pinning angle 2's N to a value below 32768 WOULD hide it and was not done.
