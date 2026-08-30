# FINDING 2026-08-30 hq_B — the SMX rc=0 exposed population is empty today, and *why* is the answer

**Tree:** SCRIP `d403c283`+ · measured 2026-08-30, seat `hq_B`, row `smx-refusal-exits-zero`.
hq_C ruled the rc must become nonzero and named the blocking precondition: *"every rc-driven consumer that
does not grep stderr … those are UNENUMERATED and that census is the precondition for landing the change."*
This is that census.

## Result: the exposed population is empty today

**No existing consumer is fooled**, and the reason is not that they check correctly — it is that none of
them currently *meets* an SMX refusal. Ran eight raku consumers and counted `[SMX]` occurrences in their
own output:

```
test_smoke_raku  test_crosscheck_raku  test_raku_smoke  test_raku_mode3_native
test_raku_ir_rungs  test_raku_fileio  test_gate_raku_zframe  test_smoke_compile_hello_all_langs
        -> SAW_SMX = 0 for all eight
```

The programs that *do* SMX-refuse — the four benchmark kernels and the map/grep probes — are graded by
`corpus_suite_harness.py`, which compares **output against a committed `.ref`**, not the exit code. So the
class is graded honestly today by an instrument that never consults the rc at all.

⭐ **So the change can land now.** The census's value is not a list of things to fix first; it is the
statement of *why* nothing breaks, which is what makes the landing safe rather than lucky.

## ⛔ Correcting my own claim, which hq_C repeated in good faith

I told hq_C that `capture-oracle-refs` "would see agreement-on-empty and mint a vacuous ref". **That is
wrong today.** Measured:

```
$ corpus_suite_harness.py capture-oracle-refs <dir> --lang raku
rc=3   ⛔ REFUSING: no oracle wired for --lang 'raku' … (only snobol4/prolog/icon so far)
```

The SMX sites are `is_raku`-gated, and capture has no raku oracle, so it **cannot reach an SMX-refusing
program at all**. It is safe for a reason entirely unrelated to the guard I credited.

✅ **But the conditional is real and I verified it properly rather than leaving the claim withdrawn.**
hq_C flagged that any frontend added to the `is_raku` predicate inherits the rc. Simulating the exact SMX
signature — empty stdout, rc=0, all arms agreeing — in a language capture *can* reach:

```
silent_rc0.sno   oracle [] rc=0   ·   scrip [] rc=0
[2/2] silent_rc0: ⛔ REFUSED (all arms agree, but on EMPTY output)      rc=1, no .ref written
```

So **when** the predicate widens, the empty-agreement guard is what stands between capture and a vacuous
ref. That is the guard's fourth independent route, and the first one that is prospective rather than
historical.

## The static census was the wrong instrument, and said so by returning zero

My first pass grepped for scripts running `scrip` on a `.raku` file: **0 hits across 15 candidates**, which
is impossible — the paths arrive through variables (`"$SCRIP" --run "$f"`). A census that finds none of its
population is indicting itself, exactly as hq_C found with their `write`-as-recursion pass and as
`test_gate_corpus_coverage_classified`'s own comment records. The empirical form — run the consumers, count
the banner in their output — answered it in one sweep.

## Two refinements to the verdict itself

1. ✅ **hq_C's neighbour argument holds for m4 and is even better than stated**: `scrip.c:1369` returns 0 six
   lines above `:1374-1375`, `[IBB] FATAL: mode-4 driver: main BB graph not found` → `return 1`.
2. ⛔ **It does not hold for m3.** The m3 site is `:1797`; its own neighbour at `:1844-1846` is
   `[IBB] FATAL: mode-3 driver: main BB graph not found` → **`abort()`**, not `return 1`. So "match the
   neighbour" is ambiguous in the second place and would give SIGABRT. The right reading is m4's precedent
   in **both** sites: `abort()` is for an internal invariant that has been violated; "this feature is not
   implemented yet" is an ordinary build failure and belongs at 1.

## Scope for the eventual landing

Both sites are `is_raku`-gated, so today's blast radius is Raku-only. The refusal is the **mode-3/mode-4
emitter's own not-covered path**; grade every frontend that reaches it, and re-run this census the day the
predicate widens — that is when the exposed population stops being empty.
