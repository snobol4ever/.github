# FINDING 2026-08-29 (seat10): any unrecognized Raku method call silently returns undef instead of erroring — the same "oracle answers when it should refuse" class this project's FACT RULES exist to catch

**Build:** SCRIP `1584013e`, `make pristine`, `RT_OPT=-O0`. Row: `raku-frontend-real-world-syntax-gaps`. Found as a side effect of root-causing seat06's "xx-operator-with-method-chain-operand" finding (that row's `## NEXT`), which turned out not to be an `xx` bug at all.

## The one cause

A Raku method call whose name matches nothing in the dispatch chain (`rt_str_method` at `src/runtime/by_name_dispatch.c:518`, plus the array/hash-method special-casing around `by_name_dispatch.c:3742-3764` that calls it) does not error — it silently produces an undef-shaped value, and the program continues running as if nothing happened. Contrast: an unrecognized bareword **function** call errors loudly and correctly (`** Error 5 — Undefined function or operation`), confirmed via `srand(42);` before this row implemented it. Methods and functions go through different resolution paths and only one of them refuses.

**Minimal reproduction, both lines behave identically:**
```
my $r = 5.rand;              # .rand was unimplemented at time of writing
say $r;                      # prints nothing (empty string), not an error
my $q = 5.totallyBogusMethodXYZ;
say "after";                 # prints "after" — the program did not stop or complain
say $q;                      # prints nothing
```

This is **not** specific to `.rand` — `.rand` was simply the first unimplemented method this session happened to hit while chasing a different, already-catalogued kernel blocker (`insertion-sort`'s `(SCALE.rand).Int xx SCALE`). `.rand` is now implemented (`srand`/`rand` added this pass, SCRIP `1584013e`) and no longer exercises this path, but the underlying silent-fallthrough mechanism is untouched and will reproduce identically for the next unimplemented method name any future Raku program happens to call.

## Why this matters (not just "add more methods")

RULES.md's own oracle-dialect FACT RULE states the general law plainly: *"AN ORACLE THAT ANSWERS WHEN IT SHOULD REFUSE IS WORSE THAN A MISSING ONE. A missing oracle produces a full plausible all-FAIL table you have been warned about three times; a wrong-*dialect* oracle produces a plausible table that is *partly right*, which is far harder to disbelieve."* A silently-undef method call is the same shape one level down: it doesn't crash, doesn't print an error, and doesn't obviously corrupt output — it just quietly removes a value from a computation and lets everything downstream proceed on a wrong number. A program that happens to `say` the bad value directly (as both repro lines above do) surfaces it as suspicious blank output; a program that uses the bad value in further arithmetic first would not even get that hint. This is a narrower instance of the same class this task's own LEDGER already flagged once this row (seat07's `@array.end` silent crash, since fixed by seat06) — but that one at least halted the program (`exit 1`); this one does not even do that.

## What was verified vs. not

**Verified:** the two repro lines above, on `1584013e` (pre-fix state re-confirmed by temporarily testing an unrelated bogus method name post-fix). **Not traced:** the exact final fallback site that turns "no dispatch arm matched" into a printable-empty value — `rt_str_method` itself returns a plain `0` on no match (ordinary, correct "not mine" signal), so the silence is manufactured somewhere in a caller further up the chain (methcall evaluation, plausibly `stmt_exec.c` or `runtime_eval.c` — not confirmed, named here only as where to start rather than as a finding). Also not assessed: whether this is Raku-specific or a general property of however this codebase's method-call evaluation works across languages that use `TT_METHCALL`.

## Duty this creates

Not this row's fix — `raku-frontend-real-world-syntax-gaps` is scoped to parse/construct coverage on the 17 corpus kernels, none of which currently exercise an unimplemented method by accident (this pass checked). Flagging for whoever owns method-dispatch robustness: the fix shape is very likely a single change at the fallback site — turn "no arm matched" into the same loud `Error 5 — Undefined function or operation` (or a method-flavored equivalent) that unrecognized functions already get, rather than a fabricated value. Small, mechanical, and closes an entire class rather than one method name at a time — but needs the actual fallback site traced first (see above), which this pass did not do.
