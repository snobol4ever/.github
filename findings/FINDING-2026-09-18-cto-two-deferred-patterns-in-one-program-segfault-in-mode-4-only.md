# FINDING — TWO DEFERRED PATTERNS IN ONE PROGRAM SIGSEGV IN MODE 4 AND ANSWER CORRECTLY IN MODE 3 (cto, 2026-09-18)

**PRE-EXISTING AND NOT THIS ROW'S.** Found while building the § 6.5 spill record's witness. It reproduces on the
ORIGIN tree with the spill-record templates reverted, so the polls did not cause it; it is recorded here because
the witness that found it is cheap and the class is a WRONG-MEDIUM crash, which is the shape modes are supposed
to be graded against independently.

## The witness (SNOBOL4), verbatim

```
        S = 'AAAAABBBBBCCCCC'
        N = 3
        C = 'AB'
        S LEN(*N) . X1 REM . Y1                               :F(E1)
E1      S ANY(*C) . X2                                        :F(E2)
E2
END
```

## Measured, SCRIP `d83a55c55` with `src/templates/bb/bb_match_*.cpp` at origin

| medium | result |
|---|---|
| mode 3 (`./scrip w.sno`) | rc=0, correct |
| mode 4 (`--compile`, `gcc`, run) | **SIGSEGV, rc=139**, no `SCRIP_GC_STRESS` needed |

## What narrows it and what does not

- **Each construct ALONE is clean in both media** — `ANY(*C)`, `NOTANY(*D)`, `SPAN(*C)`, `BREAK(*D)`, `BREAKX(*D)`,
  `POS(*N) LEN(2)`, `RPOS(*N) REM`, `TAB(*N)`, `RTAB(*N)`, `LEN(*N)`: nine one-pattern programs, m3 and m4 both rc=0.
- **`LEN(*N) . X1` followed by `ANY(*C) . X2` is clean in both media.** Adding `REM . Y1` to the FIRST pattern is
  what turns m4 into a SIGSEGV — that one token is the whole difference between the clean pair and the crash.
- A second, independent shape of the same crash: the same two patterns with `OUTPUT` between them and the subject
  built by `DUPL` instead of a literal (`w4.sno` in the sitting's scratch) crashes identically.
- Not GC: no stress knob is involved and the program allocates nothing beyond its own strings.

## Why it matters and who it is for

Mode 3 and mode 4 MAY diverge as an optimization choice and never as a semantic one. A correct answer in one
medium and a SIGSEGV in the other, on two deferred patterns in one program, is a semantic divergence. The SNOBOL4
master runs m4 on this class, so it is plausibly behind a standing m4-only red there.

⛔ **NOT CURED IN THIS SITTING.** It is outside the spill-record row and curing it inside that row would have
traded one measurement for two. It is written down with its minimal witness so the next seat starts from a
one-file repro rather than from a suite entry.
