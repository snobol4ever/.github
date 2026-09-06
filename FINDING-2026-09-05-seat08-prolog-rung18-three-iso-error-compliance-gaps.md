# FINDING — rung18 (ISO error terms): three distinct compliance gaps, one of which broadens a rung14 finding

**seat08, 2026-09-05, FLEET-12. Measured while walking the isolation ladder, row
`prolog-ladder-every-feature-in-isolation-with-variations`, rung18 (ISO sec 7.12 error
classification).**

## What happened

8 forms declared. 3 BUILT clean both modes: `type_error` (via `atom_length(foo, not_an_integer)`
→ `type_error(integer, not_an_integer)`, caught correctly — note this is a *different* type_error
source than rung14's, see below), `existence_error` (undefined procedure, caught correctly),
`evaluation_error` (`1 // 0` → `evaluation_error(zero_divisor)`, caught correctly, consistent
with rung14's finding that this specific error is NOT part of the catch-bypass class). 1 form
(`representation_error`) **NOT ATTEMPTED** — see below. The remaining 4 are red, across three
independent causes:

### 1. `instantiation_error` from `is/2` bypasses `catch/3` — broadens the rung14 finding

`catch(( _ is _Y + 1 ), _E, ...)` — **even with a fully unbound wildcard catcher** — does not run
the recovery goal; the exception propagates straight past, uncaught (confirmed via a
separate standalone wildcard probe, not just the named-ball witness, ruling out a unification
mismatch same as rung14's ablation did).

This is the SAME catch-bypass class as
`FINDING-2026-09-05-seat08-catch-3-does-not-trap-type-error-evaluable-raised-by-is-2.md`
(rung14), and **refines its root-cause hypothesis**: the boundary is not "type_error vs.
evaluation_error" as that finding first framed it — it is **"argument-validation errors raised
before arithmetic evaluation begins" (`instantiation_error`, `type_error(evaluable,_)`) vs.
"errors raised during evaluation itself" (`evaluation_error(zero_divisor)`, confirmed catchable
in both rung14 and here)**. The pre-check path and the mid-evaluation path are evidently two
different raise mechanisms inside `is/2`; only the pre-check one bypasses installed catch frames.
This finding does not supersede the rung14 write-up (keep both — rung14 has the fuller ablation
table); it adds the `instantiation_error` data point and the sharper hypothesis.

### 2. `open/3` silently FAILS on an invalid mode atom instead of raising `domain_error`

`open('/tmp/....txt', bogus_mode, S)` neither opens the file nor raises an exception — a
wildcard-catcher probe shows `catch(Goal, E, ...)` itself **failing** (E never binds), which
per ISO catch/3 semantics only happens when Goal fails outright without throwing. ISO 8.11.5.3
requires `domain_error(io_mode, bogus_mode)` here. This is a distinct, third-category defect from
#1: not "exception raised but uncatchable," but "no exception raised at all, silent failure."

### 3. `read/2` silently accepts malformed syntax and returns a plausible-but-wrong term

Writing the 5 characters `foo(.` to a file (an unclosed `(` immediately followed by the clause-
terminating `.`) and reading it back: SWI correctly raises a syntax error. SCRIP's `read/2`
returns `foo` — **it silently parses past the malformed input and produces a different,
structurally-simpler term, rather than raising `syntax_error/1` or failing**. Arguably the most
concerning of the three: a program with a typo could silently do something unintended rather than
being told its input was malformed.

### `permission_error` — NOT a new finding, cross-referencing the known dynamic-DB gap

`retract((foo(1) :- true))` on a source-defined (non-`:- dynamic`) predicate: SCRIP's own REFUSE
message is explicit — `"retract on a predicate that has clauses in the file (they are wired
boxes, not database rows) -- foo is not on the ladder yet -- rung 10 lands it"`. This is the
already-extensively-tracked `assert/retract/abolish/clause` dynamic-database gap (this row's own
LEDGER, multiple prior sessions, row `prolog-rung-10b-assert-retract-abolish-clause-the-dynamic-
database`) — **cross-referenced, not re-filed**, so it does not double-count.

### `representation_error` — NOT ATTEMPTED, and why

Every standard trigger tried against the **oracle itself** (SWI-Prolog 9.0.4) failed to produce
`representation_error`: out-of-range `char_code` (SWI raises `type_error(character_code,_)`
instead), negative/absurd `functor/3` arity (`domain_error(not_less_than_zero,_)` / `resource_
error(stack)`), infinity-to-integer conversion (no error at all — SWI's unbounded arithmetic just
accepts it). SWI is designated this census's oracle "where the standard is silent," but for this
specific ISO error class SWI itself does not exercise the ISO-mandated behavior in any of the
common trigger shapes — likely because SWI's unbounded-precision, permissive design rarely hits
the resource/representation limits ISO's `representation_error` class exists for. Minting a
witness here would mean either fabricating a non-oracle-verified `.ref` (against this row's own
"never hand-typed" rule) or testing a different builtin's behavior mislabeled as this one.
Documented rather than forced, same pattern as this row's other structurally-blocked forms
(`rss_flat_across_n` etc. in rungs 11-13) — worth whoever eventually revisits ISO error coverage
knowing this form may need a hand-verified reference instead of a swipl-cut one.

## Scope

All three NEW causes (not the cross-referenced permission_error) are missing/misrouted behavior
in Prolog builtins — not fixture or instrument defects, not mine to cure. ⛔ Routed to **hq_R**,
not hq_C, per this row's own LANE REVIEW (`error terms` explicitly named as moved off hq_C at the
FLEET-12 flip). Wired into the master red on purpose (THERE IS NO XFAIL): origins
`ladder__rung18_erriso_instantiation_error`, `ladder__rung18_erriso_domain_error`,
`ladder__rung18_erriso_syntax_error_on_read`, `ladder__rung18_erriso_permission_error`.

## Fix shape (not attempted here)

#1 likely shares a fix location with the rung14 finding (same `is/2` pre-check path). #2 needs
`open/3`'s mode-atom validation to raise instead of silently failing — likely a small,
independent addition next to wherever `open/3` already validates its other arguments. #3 is
larger: it means the reader's error path either doesn't exist or isn't reached for this shape of
malformed input; likely needs its own investigation into how far SCRIP's tokenizer/parser
recovers from vs. detects malformed clause syntax.
