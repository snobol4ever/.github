# FINDING: the beauty self-host fixed point is BROKEN — its "6x improvement" is a program that stops after 10 lines

**Seat:** hq_P (FLEET-16) · **Date:** 2026-08-30 · **Found:** while re-pinning `test_gate_instr_budget.sh`'s
watermarks, routed to me by hq_B · **Status:** ⛔ NOT cured — measured and characterised, not root-caused.

## THE NUMBER THAT LOOKED LIKE A WIN
`test_gate_instr_budget.sh` reports beauty at **Ir=299,962,038** against a pinned budget of **1,897,159,187**,
and its own NOTE line says *"improved; consider re-pinning down"*. Reported up the chain as the worst of four
stale watermarks, *"~6x under"*.

⛔ **It is not an improvement. `beauty.sno < beauty.sno` no longer reaches the Milestone-1 fixed point.**
```
$ scrip beauty.sno < beauty.sno   → rc=0, 10 lines of output (beauty.sno is 618 lines)
  line 8:  Parse Error
  then:    every -INCLUDE line missing (global.inc, case.inc, assign.inc, match.inc, counter.inc,
           stack.inc, tree.inc, ShiftReduce.inc, TDump.inc …)
```
So the Ir figure is the cost of a program that **dies at the `-INCLUDE` block after ten lines**. The gate
already knew — it prints `FAIL beauty: output is NOT the fixed point -- Ir count below is not trustworthy`
immediately above the tempting NOTE.

## ⛔ WHY THE OBVIOUS ACTION WOULD HAVE BEEN THE WRONG ONE
Re-pinning beauty to ~300M — which is exactly what "stale low, re-pin it" prescribes — would have **frozen a
broken program's cost as the target**. The eventual real fix restores ~1.9G of work, so a repaired beauty
would then read as a **~6x REGRESSION** and fail the gate. The budget is not stale; the measurement is.
⭐ **A performance number is only a performance number if the program did the work.** An Ir count over a
program that exits early is not a fast program, it is a short one — and it arrives wearing the same units as a
win. This is the perf-side twin of the vacuous-test class: not "green by construction" but **"fast by
construction"**, and it points in the direction people are hoping for, which is what makes it dangerous.

## WHAT IS AND IS NOT KNOWN
- **Known:** the fixed point fails; output is 10 lines vs 618; the divergence begins at line 8 with a
  `Parse Error` emitted by beauty itself; the `-INCLUDE` directives are absent from the output; rc=0 and
  stderr is empty, so nothing crashes and no exit code announces it.
- **NOT known:** whether the cause is a SCRIP semantic regression, a corpus change to `beauty.sno` or the
  `.inc` files, or an include-resolution/path issue following the `demo/ → demos/` re-grid. ⛔ Not investigated
  — this was found while re-pinning watermarks, and root-causing it is a different row.
- hq_B asked whether it is the same class as the snocone `beauty_arith` defect they routed to hq_C (three
  output lines dropped). Both are "beauty" corpora, so it is worth one look, but **that is a hypothesis, not a
  measurement** — the shapes differ (three dropped lines vs a parse error at line 8 and 608 missing).

## ACTIONS TAKEN
- Three sound watermarks re-pinned (`roman` 10224491→8225814, `table_access` 11879659→10249870, `array_sum`
  10912565→9287873), SCRIP `a85c7ed9`.
- **Beauty deliberately left at 1,897,159,187**, with the reasoning written at the pin site so the next person
  to read "improved; consider re-pinning down" reads why not, at the line where they would otherwise act on it.
- The gate now exits 1 on beauty's precondition failure. **That is the correct verdict and must not be
  silenced** — it is the only instrument currently reporting that Milestone-1's self-host is broken.
