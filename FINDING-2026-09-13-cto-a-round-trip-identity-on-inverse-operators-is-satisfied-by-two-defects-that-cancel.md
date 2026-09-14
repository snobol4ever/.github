# FINDING (cto, 2026-09-13) — A ROUND-TRIP IDENTITY ON A PAIR OF INVERSE OPERATORS IS SATISFIED BY TWO DEFECTS THAT CANCEL

**Row**: `prolog-the-shift-operators-are-implemented-for-one-int64-window-and-every-input-outside-it-raises-wraps-or-runs-c-undefined-behaviour`
**Gate**: `scripts/test_gate_pl_a_shift_outside_the_int64_window_is_computed_not_wrapped.sh` (6 arms × m3/m4 = 12), wired into `test-sequential`, adopted into the wiring floor.
**Tree**: cured on SCRIP `4b65bca4e`; red-before measured on that same commit with the cure stashed **and the tree rebuilt**.
**Oracle**: swipl 9 (unbounded integers). Every `want_out` in the gate is cut from the oracle, never from our output.
**Suite**: Logtalk ISO `unbounded` 87 → **89 of 111, BOTH MODES**, the two moved cases being `lgt_unbounded_left_shift_01` and `lgt_unbounded_right_shift_01` — a fully attributed delta, and no other family was predicted to move.

## 1. The claim

`(1 << 100) >> 100` answered `1` on the **uncured** tree, and `1` is the right answer.

It was right for no reason. `<<` wrapped its count to `100 - 64 = 36`, `>>` masked its own count the same way, and the two defects cancelled exactly. I had written that goal down as a **control** — an arm expected green in both trees — and the red-before measurement said otherwise only because I had put three further goals beside it in the same arm. Had that arm contained the round trip alone, it would have passed in both trees and I would have recorded a control where I had a blind spot.

**A round-trip identity asks whether two operators AGREE. It never asks whether either one is RIGHT.** On a pair of inverse operators that is the first test anyone reaches for, and it is precisely the test a symmetric defect survives. The arm is kept in the gate, green in both trees, as the standing demonstration — renamed from `control_f` to `subject_f_the_round_trip_alone_is_blind_because_the_two_defects_cancel`.

## 2. What the class actually was, and why the suite could only see a third of it

The row was reachable from the Logtalk `unbounded` family, where two cases failed with `type_error(integer, <bignum>)`. Described by that route, the bug is *"the shifts raise on bignums"*. Described by the **property** — what does this operator do outside the window it was written for — the census is three faces from the same two lines of `src/runtime/by_name_dispatch.c`:

| | face | witness in the suite | uncured answer | oracle |
|---|---|---|---|---|
| 1 | a bignum operand raises, because `pl_big_binop` carried no `shl`/`shr` clause and DT_BIG fell through to a DT_I-only line | **yes**, 2 cases | `type_error(integer, 123456789012345678901234567890)` | `2071261215926550121592655012157194240` |
| 2 | an int64 pair whose result exceeds int64 **silently wraps** | **none** | `1 << 64` = `1` | `18446744073709551616` |
| 3 | a count outside 0..63, negatives included, evaluates C's undefined shift and returns the hardware's masked count | **none** | `1 << (-2)` = `4611686018427387904` | `0` |

Two of the three faces have **no witness anywhere in the suite**. Curing what the suite could see would have taken the family to 89/111, closed the row green, and shipped `1 << 64 =:= 1` in both modes.

⛔ **This is the same shape as CTO-46 and it is the second time in two rows.** There the class was defined by *the lines that raise `int_overflow`*, which found every site that raises and no site that refuses. Here the class was offered as *the cases the suite fails on*, which finds every input that raises and no input that lies. **A defect that RAISES announces itself and gets a row; a defect that returns a wrong answer of the right type cannot be told from a correct one at the call site.** The face with no witness is systematically the more dangerous face, and it is systematically the one a suite-derived class omits.

## 3. The cure

One helper, `pl_ax_shift`, reached from both entry points — `pl_big_binop` (bignum operand) and `dop_ax` (int64 operands). It normalises a negative count by mirroring the operator, returns an exact int64 answer when one exists, and otherwise composes the bignum core the tree already carries: a left shift is `rt_big_mul` by `rt_big_pow(2, n)`, a right shift is the **existing `divf` clause** against that same power — floor division, which is what the oracle does for negative operands (`-123456789012345678901234567890 >> 4` = `-7716049313271604931327160494`, not the truncating `...493`). **No new code in `bignum.c`.**

The asm runtime defines `rt_pl_dop_ax_shl`/`_shr`, which looked like a second implementation that would shadow the cure. It is not: `PL_AX_VENEER` in `src/runtime/rtx/rtx_plunify.s` is a thin veneer that calls the `_c` function and propagates the ball. Read before assuming, and then confirmed by the arms being green in **both** modes rather than m3 alone.

## 4. What this cure does not claim, named rather than left to be discovered

- A shift **count that is itself a bignum** (`1 << 10000000000000000000000`) still raises `type_error(integer, <bignum>)` where swipl raises `resource_error`. This tree has **no `resource_error` vocabulary at all** (grep: zero sites in `src/runtime/`); inventing one is a policy decision, not this bug.
- A count above 2^20 with a bignum operand declines to the old path. The honest answer needs a bit-length accessor `bignum.c` does not export, and returning the sign bit would be a **guess that is wrong for any operand wider than the count**. Returning a plausible answer there would have been face 2 all over again, committed deliberately.

Both remainders are outside every arm of the gate **by construction**, not by oversight.

## 5. Tolerated reds, each named with the commit it was read at

Read on SCRIP `4b65bca4e` with this cure applied; both pre-date it and both already have an owner:

- `make preflight` — **42 of 43 arms green**; `test_gate_picker_lane_table_agrees_with_mode.sh` red on `s4e_lane_owner_of_language`, a MODE-line-2-vs-code disagreement from CEO-723. Postoffice tooling, with the ceo for scope; hq_C confirms nothing in flight against it. Not a seat's landing and not curable inside a language row.
- `test_gate_pl_integer_division_floors_and_int64_overflow_promotes.sh` — its two **witness** arms (the subject) green in both modes; its `test_arith` arm red at `declared=220 graded=220 hit=0 miss=220` against a floor of 55. A matcher that hits **nothing** of its own declared population is a plumbing failure, not 220 arithmetic defects; it is with the ceo for an owner and the coo is keeping it out of board receipts as a red with no subject.

Green and unmoved: `test_gate_pl_an_int64_overflow_promotes_to_the_bignum_core_instead_of_raising` (14/14), `test_gate_gate_wiring_ratchet` (0 violations), `strip_comments.py --check` (0 files).

## 6. A second gate adopted, and why it is not a hijack

`util_gate_wiring.py adopt` swept in `test_gate_pl_a_text_stream_reads_characters_not_bytes.sh` alongside mine. That gate is **already landed** (`5feb8e0be`) and **already on a Makefile recipe line**; its seat simply never recorded it in `gate_wiring.tsv`. Adopting it closes a real gap rather than ratcheting the floor onto someone's in-flight work — and it was **verified green on this tree before the ratchet was allowed to stand**, because adopting a red gate makes the floor red for thirteen seats. hq_R is told in the same breath.
