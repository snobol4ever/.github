# FINDING — three INRIA entries contradict their own comments, SCRIP is right on all three, and 445/445 is therefore unreachable

**hq_R, 2026-09-06 ~23:5x CDT.** Measured on SCRIP `6433a618d` + corpus `98b075332`, clean stamps, incremental
`make`, RT_OPT `-O0`. Found while picking the next flip row out of this lane's remaining INRIA reds — the three
`functor-bis` goals looked like they had *inverted* expectations, which is usually a sign of one's own parser,
so I read the vendored file instead of trusting my index.

## THE MEASUREMENT

Three entries in `corpus/packages/prolog/inriasuite/functor-bis` carry a `%` comment **contradicting the
machine-readable expectation on the same line**, and the runner's parser strips `%` comments before grading
(`decomment()`), so the comment is invisible to the board and the wrong expectation is what we are scored on:

```
[functor(foo(a),foo,2), success].   % Must fail
[functor([_|_],'.',2), failure].    % Must succeed
[functor(X, foo, a),
 failure].                          % type_error(integer,a) expected ('a' not an integer)
```

Graded against both vendored oracles and SCRIP, same witness goal, 2026-09-06:

| goal | swipl 9.x | gprolog 1.4.5 | SCRIP | suite declares | suite's own comment |
|---|---|---|---|---|---|
| `functor(foo(a),foo,2)` | fails | fails | **fails** | `success` | "Must fail" |
| `functor([_|_],'.',2)` | fails | **succeeds** | **succeeds** | `failure` | "Must succeed" |
| `functor(X, foo, a)` | `type_error(integer,a)` | `type_error(integer,a)` | **`type_error(integer,a)`** | `failure` | "type_error(integer,a) expected" |

**SCRIP is correct on all three.** They are not defects and no cure can turn them green without making the
engine wrong.

## ⛔ THE THREE ARE NOT ALL THE SAME KIND, AND CONFLATING THEM WOULD BE THE ERROR

- `functor(foo(a),foo,2)` and `functor(X,foo,a)` are **plain transcription errata**: both independent oracles
  agree with SCRIP and against the suite, and the suite's own annotation agrees with them. `foo(a)` has arity 1,
  so the first must fail; `a` is not an integer, so the third must raise. Nothing is in dispute.
- `functor([_|_],'.',2)` is **NOT an erratum — it is an ISO-versus-SWI divergence**, and the oracles split on it.
  ISO 13211-1 makes the list constructor `'.'/2`, so gprolog succeeds and so does SCRIP; modern SWI uses `'[|]'`
  and therefore fails. The suite's machine-readable expectation follows the **non-ISO** reading while its own
  comment follows ISO. ⭐ So grading against that cell actively **penalises ISO conformance** — the thing the
  suite exists to measure. Filing it as an erratum would paper a real disagreement; filing it as a SCRIP defect
  would be worse.

## ⛔ THE EXISTING MECHANISM DOES NOT COVER THESE, AND THAT IS EASY TO GET WRONG

`KNOWN_SUITE_ERRATA` in `test_prolog_inria_suite.sh` (seat05, for `sub_atom`) relaxes the **bindings** comparison
to outcome-class-only for one named goal. All three entries here have a wrong **outcome class** — success vs
failure, failure vs success, failure vs error — which is the axis that mechanism deliberately does not touch.
Registering them there would silently do nothing and read as done. A sibling mechanism is needed, with the same
evidentiary bar the existing one already sets: an independent oracle cross-check on the same witness goal, in the
open, never a silent edit to the vendored file (the suite's README keeps its data verbatim).

## ⛔⭐ THE CONSEQUENCE ABOVE THIS LANE: 445/445 IS UNREACHABLE

Lon's bar is *"100% means 100% of the industry standard language"*. Three of the 445 cells cannot be satisfied by
a conforming engine. The honest denominator is therefore **442 gradeable + 3 named**, not 445 — and a lane
chasing 445 will burn time on three goals whose only "cure" is a regression. This is a ceo-level fact about the
target, not a runner detail, which is why it is filed rather than quietly registered.

## WHAT I DID NOT DO

I did not edit the vendored suite and I did not register the three anywhere. The runner is the instrument lane's
(hq_T), and the denominator question is the ceo's. This file is the evidence for both; the measurements are
reproducible from the table above with the two oracle binaries named in ORACLES.md.

⭐ **The reusable half, for anyone reading a suite's reds:** when an expectation looks inverted, read the vendored
source before believing your own index — and then read the *comments the parser strips*. Three of this lane's
remaining reds were the suite telling us, in its own words, that its machine-readable half was wrong, and every
tool in the chain was built to discard exactly that sentence.
