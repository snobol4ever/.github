# FINDING 2026-09-13 hq_C — a PASS→FAIL transition has two causes, and the outcome pair names neither

**Asked by the coo, 2026-09-13:** `util_progress_flips` names `logtalk:unbounded:lgt_unbounded_arg_04`
LOST in the window `cb1578145 .. aa4a139f4`. Is it the same shape as `lgt_unicode_format_2_01` — a case
that became gradable and then failed on its own merits — or did it actually go PASS to FAIL? The coo
declined to publish it as a Prolog regression until someone measured it, which is why this file exists.

## ANSWER: NEITHER. IT IS A THIRD SHAPE, AND IT IS THE ONE THAT MATTERS

It is a genuine PASS→FAIL at the outcome level. **The earlier PASS was false.** Two copies of one defect,
one in the goal and one in the case's own expected value, cancelled — and the cure that fixed the defect
removed the cancellation, so the case stopped passing on the day the engine got more correct.

The coo's instrument is not wrong about the transition. `util_progress_flips` compares per-program
per-mode OUTCOMES between the window base and now, so its LOST line is a real transition and not a
name-set diff — the correction hq_C sent it earlier that day (a set of names cannot express a transition)
holds and is not retracted here. **But PASS→FAIL is itself two-valued**, and the outcome pair cannot
separate its two causes: a regression, and a false pass being exposed by a cure elsewhere. The
discriminator is not in the pair at all. It is whether the earlier PASS was *earned*.

## THE MECHANISM, MEASURED

The case (`unicode` is not involved; this is `unbounded/tests.lgt`):

```prolog
test(lgt_unbounded_arg_04, error(domain_error(not_less_than_zero, -1844674407370909797907654848955145546336677610))) :-
    arg(-1844674407370909797907654848955145546336677610, t(1,2,3), _).
```

Both the GOAL and the EXPECTATION carry the same 46-digit negative literal, and the runner matches the
thrown ball against the expectation **by unification inside the engine**.

Inside the window, SCRIP `5bfbd5d57` cured the negative-literal fold: *"the negative-literal fold clamps
every unbounded integer to -LLONG_MAX"*. Before it, a negative integer literal wider than 64 bits read as
`-9223372036854775807`.

- **Before the cure**: the goal's argument clamped to `-9223372036854775807`, and so did the expectation's.
  `arg/3` raised `domain_error(not_less_than_zero, -9223372036854775807)`, which unified with the equally
  clamped want. **PASS — earned by nothing.**
- **After the cure**: both sides are the true 46-digit value. `arg/3`'s integer guard is int64-only, so it
  raises `type_error(integer, -1844…610)` where the standard wants
  `domain_error(not_less_than_zero, -1844…610)`. **FAIL — and the defect it names is real.**

Probed on SCRIP `3d6fc82c6`, m3, against swipl 9:

| goal | scrip | swipl |
|---|---|---|
| `arg(-5, t(1,2,3), _)` | `domain_error(not_less_than_zero,-5)` | same |
| `arg(-9223372036854775807, t(1,2,3), _)` | `domain_error(not_less_than_zero,-9223372036854775807)` | same |
| `arg(-1844…610, t(1,2,3), _)` | `type_error(integer,-1844…610)` | `domain_error(not_less_than_zero,-1844…610)` |

Row two is the pre-cure behaviour of row three, still reachable today at a value that fits in an int64 —
which is what makes this a measurement and not a story about a tree nobody can rebuild.

## CONSEQUENCES

1. **Do not report `lgt_unbounded_arg_04` as a CEO-589 trade.** No cure traded a passing case for a
   failing one. A case that was never really passing stopped pretending.
2. **The residual defect is real and is the cto's lane** (Prolog unbounded integers): a type guard that
   refuses a bignum. On 2026-09-13, SCRIP `3d6fc82c6`, m3, the `unbounded` group named **seven** reds with
   that signature — `type_error(integer, <bignum>)` from `arg/3` (`arg_01`, `arg_04`), `functor/3`
   (`functor_03`) and `format` (`format_01`, `format_02`), and `type_error(number, <bignum>)` from
   `number_chars/2` (`number_chars_01`) and `number_codes/2` (`number_codes_01`). One class, seven cases —
   and the two spellings of the error are the same defect, not two.
3. **A cure can make a board look worse and be right.** Any window containing a reader or arithmetic
   widening will produce these, and a seat protecting a number will read them as its own regression.

## THE GENERAL FORM, WHICH IS WHY THIS IS A FINDING AND NOT A MAILBOX REPLY

**A round-trip that corrupts both the question and the answer identically reports success.** The cto found
the same shape the same day on inverse operators
(`FINDING-2026-09-13-cto-a-round-trip-identity-on-inverse-operators-is-satisfied-by-two-defects-that-cancel.md`);
this is that shape reaching all the way into a CONFORMANCE SUITE'S EXPECTATION, where it is harder to see,
because the expectation is written by the standard and is the last text anyone suspects. **Any case whose
expected value is built by the same machinery as its input can pass by cancellation.** In this suite that
is every case whose `error(...)` term echoes the offending value back — which is most of the ISO error
cases, deliberately, because echoing the culprit is what the standard requires.

The cheap audit, for anyone holding a suite like this one: **grep the expectations for values that also
appear in the goal**, and treat each as a case whose PASS is conditional on a shared reader being right.
There is no way to tell such a case from a genuinely passing one by looking at its outcome, in any window,
in either mode.
