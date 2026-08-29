# FINDING — `rung15_abolish_*`'s "3 ORACLE-DIFF" refined: SCRIP's `abolish/1` doesn't raise an
# existence_error on the abolished predicate (ISO/SWI both do); one of the four abolish files is
# actually SCRIP-DIFF, not ORACLE-DIFF, and looks like the same backtracking mechanism as the
# already-documented `between/3`-family bug

**seat06 · 2026-08-29 · row `tests-consolidate-prolog` · NEXT ACTOR item 1**

## The 4 `rung15_abolish_*` files, tested fresh against both oracles + scrip (m3 and m4)

| file | scrip m3/m4 | `.expected` pin | `swipl -q -g main -t halt` | `gprolog` |
|---|---|---|---|---|
| `abolish_one_of_two` | `cat_gone/tweety/polly` | same (MATCH) | `ERROR: Unknown procedure: cat/1` | same error (different cause, see below) |
| `abolish_then_query_fail` | `no` | same (MATCH) | `ERROR: Unknown procedure: dog/1` | same error (different cause) |
| `abolish_existing` | `gone` | same (MATCH) | `ERROR: Unknown procedure: fact/1` | same error (different cause) |
| `abolish_then_reassert` | **`green`** (only) | `green\nyellow` (**DIFFERS from scrip**) | `green\nyellow` | same (see below) |

## Refined diagnosis of the 3 genuine ORACLE-DIFF files

Not just "swipl disagrees, ambiguous" — the mechanism is now concrete. All three `assertz` a
predicate with no prior `:- dynamic` declaration, then `abolish/1` it, then immediately call it again
(`cat(_)`, `dog(rex)`, `fact(_)`) inside an if-then-else or plain call. **Real ISO/SWI `abolish/1`
removes the predicate's definition entirely — a subsequent call is an existence_error, not a silent
failure.** `swipl`'s error confirms this exactly: `Unknown procedure: cat/1` fires from inside `main`
when `cat(_)` is called as the `->`/`;` condition — and in SWI, an existence_error raised *as the
condition of `->`* is NOT caught and converted to "condition failed, take the else branch"; it
propagates and aborts `main` uncaught. `gprolog` reaches the identical existence_error for a different,
orthogonal reason (it rejects bare `:- assertz(...)` as a non-ISO directive — a known, already-documented
limitation in this row's own history — so `cat/1` etc. were never populated at all under gprolog; either
way, calling them is undefined). **Both sanctioned oracles agree the outcome is an uncaught error, never
a value to print.** SCRIP currently makes the abolished predicate behave as if it's defined-but-empty
(matching `retractall/1` semantics, not `abolish/1`) — so `cat(_)` just fails cleanly and the `->/;`
takes its else branch, printing `cat_gone`/`no`/`gone`. **The `.expected` pins for these three are
self-referential** (SCRIP's own pre-existing output, matching the same anti-pattern this row has already
flagged repeatedly elsewhere — `rung22_write_canonical`, the earlier 6/22 self-pinned files) — they are
not a second legitimate interpretation of `abolish/1`, they're what SCRIP already does, pinned as if it
were ground truth.

## `abolish_then_reassert` was miscounted (or is newly discovered) as ORACLE-DIFF — it's actually SCRIP-DIFF

`swipl` and the `.expected` pin **agree** here (`green\nyellow`) — `abolish` followed immediately by two
fresh `assertz` calls before any query never hits the existence-error window above, so there's nothing
oracle-ambiguous about this one file. But **SCRIP's own output is `green` only — one line, not two** —
diverging from its OWN pin, confirmed in both m3 and m4. `color(X), write(X), nl, fail` should backtrack
across both asserted facts (`green` then `yellow`); SCRIP only ever produces the first. This file belongs
in the "7 SCRIP-DIFF, genuine reds" bucket, not the "3 ORACLE-DIFF" one — bringing that count to (at
least) 8, unless it was already counted there under a different name and the abolish-family listing just
happens to overlap it (this session didn't have hq_P's exact per-file SCRIP-DIFF list to cross-check
against — the task file's classification table gives bucket sizes, not names).

⭐ **Plausible same-root-cause link to seat14's already-documented finding**
(`FINDING-2026-08-29-seat14-prolog-wrong-answer-six-was-two-oracle-errors-and-one-shared-backtracking-
defect.md`): that FINDING traced `between/3`, GNU Prolog's `for/3`, and `current_stream/1`'s enumeration
form to ONE shared mechanism — "any `between/3`-family builtin driven through backtracking produces its
FIRST solution only and never retries to the second." `color(X)` here is not a `between/3`-family
builtin at all — it's a plain **user-defined dynamic predicate populated via `assertz`**, backtracked
into via a `fail`-loop. If the same underlying defect reaches user predicates too (not just the three
named builtins), the blast radius is much larger than seat14's FINDING characterized — **this needs
verification, not assumed**: this session did not trace scrip's own emitted code for either case to
confirm they share a mechanism, only observed the same *symptom* (first-solution-only under
backtracking) in a structurally different context (assert-populated fact base vs. a builtin generator).

## Disposition — left as-is, per this row's own standing charter boundary

Not fixed here (compiler-debugging lane, not conversion lane, matching this row's own repeated
precedent for every other tractable bug found during this consolidation). All 4 files left loose, NOT
KEEP.md'd (per this row's standing instruction not to exclude preemptively) — none should be converted:
converting the 3 ORACLE-DIFF ones would enshrine SCRIP's own incorrect-per-oracle output as a permanent
golden reference; the 4th is a confirmed genuine red.

## What's actually needed, for whoever picks either of these up

1. **`abolish/1` fix**: make a call to an abolished predicate raise an existence_error (or whatever this
   codebase's standard "undefined procedure" signal is — check how `unknown_procedure` errors are raised
   elsewhere in the Prolog runtime/builtins) rather than silently failing. Small, bounded — 3 files
   ready to serve as regression witnesses the moment it lands (their CURRENT `.expected` pins would need
   inverting to "error/no output" first).
2. **Backtracking-into-multiple-facts-after-reassert**: ASM-diff `abolish_then_reassert.pl`'s m4 `.s`
   against a sibling that correctly backtracks through 2+ asserted facts (plenty exist elsewhere in
   `tests/prolog`) to see whether the wiring matches or diverges from seat14's already-diagnosed
   `between/3`-family mechanism — confirms or refutes the same-root-cause hypothesis above before anyone
   assumes a fix for one covers the other.
