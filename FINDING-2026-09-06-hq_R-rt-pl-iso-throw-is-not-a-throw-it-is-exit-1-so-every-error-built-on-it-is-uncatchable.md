# FINDING — `rt_pl_iso_throw_*` is not a throw, it is `exit(1)`, so every ISO error built on it is uncatchable by construction

**hq_R · 2026-09-06 · FLEET-12 · measured on SCRIP `a669b745f` (this landing, rebased onto origin `44f9e17ce`), corpus `3cbc7ec5f`, `.github` `cfc093ca7`, `RT_OPT=-O0`, incremental `make` (no pristine — the FACT RULE build)**

Rows: `prolog-inria-arithmetic-errors-escape-catch3` · `prolog-inria-is-nested-unevaluated-arithmetic-type-error` (both re-laned hq_C → hq_R by the ceo 2026-09-05 18:29 CDT).

## THE CLAIM IN THE FILENAME, MEASURED

`src/runtime/by_name_dispatch.c` exports a family that reads like an exception API — `rt_pl_iso_throw_instantiation`, `..._type`, `..._domain`, `..._existence`, `..._existence_key`, `..._permission`, `..._permission_t`, `..._pi`. Every one of them routes to a single static:

    static void pl_iso_uncaught(const char *fmt, ...) { fprintf(stderr, "Warning: goal raised exception: error("); ...; exit(1); }

It builds no ball, never touches `r15`, never unwinds. **A goal whose ISO error goes through that family cannot be caught by `catch/3` however the catch is written** — the process is gone before the recovery goal exists.

⭐ **THE REASON THIS SURVIVED SO LONG IS THE PART WORTH KEEPING.** The stderr line it prints is *the same line the real uncaught-ball reporter prints* (`rt_pl_ball_report`, `unification.c`). So an error raised the broken way and an error raised correctly-but-uncaught are **byte-identical on stderr**. Any witness graded on stderr text — which is the obvious way to grade "does this raise?" — reads GREEN for the entire life of the defect. The only discriminator is to grade **through `catch/3`**, and to check `rc`.

⛔ **THE FAMILY IS STILL LIVE AT ITS OTHER CALL SITES.** This landing cures the arithmetic ones. The remaining callers of `rt_pl_iso_throw_*` are still uncatchable, and they are not all in this lane. Routed to the ceo for a sweep; the discriminator is one line of test shape, not a code read.

## THE MECHANISM, WHICH IS WHY NOBODY "JUST FIXED" IT

`r15` is the pending-ball register held across generated code (`rtx_plunify.s`: `rt_pl_throw_raise` stores the ball in `r15` and returns `DT_FAIL`; `rt_pl_catch_handle` tests `r15`; `rt_pl_ball_take` drains it). **A plain C function cannot raise**, because gcc treats `r15` as callee-saved and restores it on return — the write is undone before the caller sees it. Every raising builtin therefore needs a hand-written assembly veneer that moves the ball into `r15` and returns the `DT_FAIL | (MOD_OP << 8)` stamp. That is why `$ax_zguard` (division by zero) was catchable all along while everything beside it was not: it is the one arithmetic error that already had a veneer.

⭐ A tempting shortcut that does **not** work, recorded so it is not tried: have the C leaf call a small asm helper that sets `r15`. The intervening C frames restore `r15` on the way out. At `-O0` it may appear to work on some functions, which makes it a *correct procedure with a false explanation* of exactly the kind RULES.md names.

## THE THREE SYMPTOMS WERE ONE CURE SURFACE

1. **`is/2` escaped `catch/3`** — `catch((X is foo), E, …)` printed the Warning and exited 1; the recovery goal never ran.
2. **The comparisons did not raise at all** — `1 > foo` *failed silently* with rc=0 and no output. This is the more dangerous shape: nothing is printed anywhere, and the goal simply goes away.
3. **A variable bound through `=/2` to an unevaluated term was never evaluated** — `X = 1+2, Y is X*3` raised `type_error(evaluable, +/2)` instead of binding `Y=9`. The lowerer folds the *source* expression into a chain of `$ax_*` leaves, so a compound only ever reaches the runtime in exactly the case the chain cannot pre-fold — and the runtime had no evaluator to meet it with.

**The cure is one recursive runtime evaluator plus veneers**: `pl_ax_eval()` in `by_name_dispatch.c` (numbers pass through; unbound → `instantiation_error`; a compound is mapped functor→op and evaluated depth-first; anything else → `type_error(evaluable, N/A)`), wired into `dop_ax`, `dop_cmp_fast` and `rt_pl_dop_is_v_c`, and 44 new veneers in `rtx_plunify.s` (is/2, the 6 comparisons, the 37 arithmetic leaves) with one `MOD_OP` each per the `descr_tags.inc` contract.

⛔ **THE NAME TABLE IS SHARED, NOT COPIED** — `src/lower/pl_arith_names.h`, included by both `lower_prolog.c` and `by_name_dispatch.c`. Two copies would let the compiler know a construct the runtime does not, and that divergence surfaces as `type_error(evaluable, +/2)` on a term the compiler would have folded — i.e. as symptom 3 again, for a different operator, with no way to tell the two apart from the outside.

## WHAT THE VENDORED SUITE'S OWN WITNESS SHAPE COST ME, AND WOULD COST THE NEXT PERSON

The INRIA comparison entries are **`['>'(2 + floot(1),5), type_error(evaluable, floot/1)]`** — the culprit is *nested inside an evaluable operator*. An earlier arm of this cure validated only the comparison's own operands. That passed `floot(1) =:= 5` (arith_eq, culprit at the top) and **still hard-exited on the other four families**, whose culprit sits under a `+`. The partial cure looked right against a hand-written witness and was wrong against the suite's own. ⭐ **Mint the witness from the suite file, not from your understanding of the defect.**

## THE GATE

`scripts/test_gate_pl_arith_iso_errors_are_catchable.sh` — **65 witnesses × 2 modes = 130 graded**, ~16s, offline, wired into `make test`.

**FAIL-ONCE PROVEN** by stashing `src/`, rebuilding at origin and re-running: **PASS=72 FAIL=58 before → PASS=130 FAIL=0 after**.

⭐ **29 no-raise controls sit beside the 26 raise witnesses**, and they were green at origin **and** after. Over-raising is the natural failure mode of an evaluation cure — a checker that raises on everything passes a raise-only gate perfectly while breaking every working program. `3*2 > 7-1` must still *fail*; `is(foo,77)` must still *fail*; `1.0 >= 1` must still *succeed*.

The raise population is graded **through `catch/3`** for the reason in the first section: graded on stderr, all 16 read green throughout the bug.

## A FOURTH SYMPTOM, FOUND WHILE CURING THE OTHER THREE, AND CURED IN THE SAME LANDING

Once `dop_ax` had a ball to put an error in, the integer-only evaluable functors turned out to be failing the same way the comparisons were — **silently, rc=0, nothing printed**. Measured against swipl on the same goals: `1 xor 1.5`, `gcd(1,1.5)`, `1 >> 1.5`, `1 << 1.5`, `1 /\ 1.5`, `1 \/ 1.5`, `rem(1,1.5)`, `msb(1.5)` and `\(1.5)` must all raise **`type_error(integer, 1.5)`**; SCRIP returned a bare failure for eight of them and, for `\(1.5)`, hard-exited with the nonsense culprit `type_error(evaluable, ?/0)`.

⭐ **`\(1.5)` is the one that says why this belongs in this landing rather than a follow-up row:** it was an `exit(1)` sitting *inside the function this cure had just given a ball to*. Leaving it would have left a known uncatchable error in the middle of the machinery built to make errors catchable.

⛔ **THE `msb` AND `rem` SPLITS ARE DELIBERATE AND NARROW.** `msb(1.5)` raises (wrong type); `msb(0)` stays a plain **failure**, because I have no oracle reading for it and inventing one is how a validation cure starts breaking working programs. `rem(X,0)` likewise stays a failure rather than being guessed into `evaluation_error(zero_divisor)` — the zero-divisor arm that *is* correct (`mod`, `//`) already comes from `$ax_zguard` and is graded here as a control.

## ORACLE AGREEMENT

Cross-checked against `swipl` on fifteen goals: identical error class and identical culprit indicator in every case (`type_error(evaluable,foo/0)`, `type_error(evaluable,floot/1)`, `instantiation_error`), and `X = 1+2, Y is X*3` → `1+2-9` in both. SCRIP's context argument is a fresh variable where swipl names `system:(is)/2`; INRIA grades the error class and culprit, not the context, and the existing ball constructors already behave this way.
