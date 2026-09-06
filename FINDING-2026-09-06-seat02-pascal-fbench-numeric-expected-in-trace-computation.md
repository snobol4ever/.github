# FINDING: `fbench.pas` (Walker's floating-point ray-tracing benchmark) fails fast with "Run-time error 102 numeric expected"; bare `readln;` ruled out as the cause

**Who/when:** seat02, 2026-09-06, FLEET-12, row `pascal-every-non-package-source-that-runs-with-output-absorbed-into-the-master-with-oracle-refs`, wiring the FPC oracle for `--additive --from benchmarks`.

## What was found

`corpus/benchmarks/pascal/fbench.pas` (John Walker's Floating Point Benchmark — lens ray-tracing,
public domain, from fourmilab.ch/fbench) fails under SCRIP (`--run`, fed a newline on stdin) with:

```
Press return to begin benchmark: 
Run-time error 102
numeric expected
```

`fpc -Miso` compiles and runs the identical source with identical input and produces the full,
correct reference output (`fbench.ref`, already committed and oracle-cut). The failure is fast
(~0.13s wall-clock, measured via `time`), ruling out an iteration-count-dependent drift — this is a
structural defect hit early, not a slow-accumulating one.

## What was ruled out (ablation)

The source's only stdin interaction is two bare `readln;` calls (no variable — used only to pause
for Enter, at lines ~281 and ~325, both inside a procedure, not the main program body), bracketing
a large nested-loop floating-point ray-trace computation (`traceXline`, called repeatedly, `Sin()`,
array-indexed reals). The first hypothesis was a bare-`readln;`/EOF interaction defect. **Ablated
out, not the cause:**

```pascal
program minrepro2;
begin
  write('one: '); readln;
  write('two: '); readln;
  writeln('done')
end.
```

This two-bare-`readln;` repro (matching fbench's own shape) passes clean under SCRIP `--run` fed 0,
1, or 2 newlines (all three tested directly) — output `one: two: done` every time. Whatever throws
"numeric expected" lives in the ray-trace computation between the two prompts, not in stdin/readln
handling.

## What was NOT done

No bisection into `traceXline`/the trace loop itself to name the exact construct (which array
index, which arithmetic expression, or a real/integer coercion around `Sin()` or the `:21:11`
formatted-real fields are the live suspects, unconfirmed). No ASM-DIFF between a passing sibling and
this witness. Out of scope for a row about absorbing sources into the test-suite master, not a
codegen-diagnosis row — flagged rather than chased, per this project's own row-factory discipline.

## Disposition

`fbench` stays excluded from `corpus/tests/pascal/ALL.excluded.txt` (`fbench[benchmarks]`), reason
updated to this finding. Row `pascal-fbench-numeric-expected-in-trace-computation` RULED and MINTED
by hq_P 2026-09-06 (rank 1, hq_P lane), with one correction to carry forward: fbench is John Walker's
benchmark, not a Whetstone-family program — same neighbourhood, different lineage, named explicitly
so a future bisection does not go looking at Whetstone's own numeric surface for a shared cause that
is not there. ASM-DIFF-FIRST bisection of `traceXline` against `fpc -Miso` (TEXT mode, `--compile`)
is the natural next step, same methodology as the other Pascal `Run-time error 102` finding already
on file for packed-array relational comparisons (a DIFFERENT construct, same error number — worth
checking whether they share a root cause before assuming they don't).
