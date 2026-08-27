# FINDING: Pascal m4 has a genuinely non-deterministic SIGSEGV, distinct from the known arrparam bug

**UPDATE, same session, post-conversion:** a THIRD, independent witness confirmed — `rec2` (one
of the three entries in the newly-converted `tests/pascal/crosscheck/rec.pas` suite) shows the
identical pattern under repeated `corpus_suite_harness.py run --modes m4`: PASS, CRASH, CRASH,
PASS, CRASH across 5 runs of the byte-identical extracted entry. This is not confined to
`pb30`/`sieve` — it is a broader class affecting an unknown fraction of Pascal m4 programs.
Anyone reading a Pascal m4 board (loose-file gate or suite) after this finding should expect
small (likely low-single-digit) PASS/FAIL count wobble between runs that is NOT a regression —
it's this pre-existing bug being sampled differently each run. Do not chase a perfectly stable
board number without accounting for this; a real regression needs a bigger, reproducible swing
or a new (not already-flaky) witness to be credible.

**Who/when:** seat02, 2026-08-27, discovered mid-`tests-consolidate-pascal` while converting the
`pb` and `misc` families through `corpus_suite_harness.py convert-blocks`.

## What happened

`corpus_suite_harness.py`'s own byte-equal-or-no-delete revalidation (which runs each entry's
original file fresh, twice, plus the suite-extracted copy once) caught two files reporting
green on their first check and then CRASH (signal 11) on a later fresh run of the *identical*
unmodified original file:

- `pb30.pas`: `orig={m3:PASS,m4:CRASH rc=-11}` on the gating check that excluded it from `pb`.
- `sieve.pas`: `orig={m3:PASS,m4:PASS} suite={m3:PASS,m4:CRASH rc=-11}` on `misc`'s revalidation
  pass (the ORIGINAL was clean on both checks; the SUITE-EXTRACTED byte-identical copy crashed).

**Independently confirmed outside the harness**, same built `./scrip`, same compiled binary,
5 repeat runs each, no rebuild in between:
- `pb30`: PASS, PASS, PASS, SIGSEGV, SIGSEGV
- `sieve`: PASS, SIGSEGV, SIGSEGV, PASS, PASS

No pattern by run order, no code change between runs — this is genuine non-determinism (memory
layout / ASLR / adjacent-heap-state sensitive, most likely), not a flaky test harness artifact.

## Why this isn't `pascal-m4-registered-dispatch-segv`

That row's witness (`arrparam.pas`) crashes **deterministically on the first call**, root-caused
to `rt_proc_call_prologue_lex` via a by-value-array parameter copy overrunning the callee frame
and trashing `environ`. `pb30`/`sieve` crash **intermittently**, and `sieve` (Sieve of
Eratosthenes — no records, no by-value array params, no nested procedures) doesn't share that
row's implicated ingredient at all. Could be the same underlying corruption class manifesting
more subtly (a partial/adjacent overwrite that doesn't always land on live data) or a different
defect entirely — not established which, deliberately not guessed further here.

## What was NOT done

Not bisected, not gdb'd, not rowed with a claimed owner. `tests-consolidate-pascal` is a
consolidation row, not a codegen-debugging row (row-factory discipline: mint, don't cure inline).
`pb30.pas` and `sieve.pas` were left as loose files in `corpus/tests/pascal/` (documented in that
directory's `KEEP.md`) rather than forcing a lucky green moment into the suite, which would only
have hidden the flakiness inside a regression-guard file instead of surfacing it.

## Suggested next step for whoever picks this up

Both witnesses are small (`sieve.pas` is the classic ~28-line Sieve of Eratosthenes with no
records/pointers/nested procs — about as minimal an m4 witness as Pascal has). ASM-DIFF-FIRST:
diff the `.s` between a run and a re-run isn't applicable (codegen is deterministic per-source;
the crash is a *runtime* data-dependent one) — likely needs `ulimit -c unlimited` + repeat-until-
crash + core dump inspection, or ASLR-disabled repeat runs (`setarch -R`) to see if disabling
ASLR makes it deterministic one way or the other, which would strongly implicate an
uninitialized-read or stack-layout-dependent overwrite over a logic bug.
