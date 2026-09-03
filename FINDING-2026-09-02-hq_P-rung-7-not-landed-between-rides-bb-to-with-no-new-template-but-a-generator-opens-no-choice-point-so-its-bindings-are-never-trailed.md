# FINDING 2026-09-02 hq_P — rung 7 NOT LANDED: `between/3` rides `bb_to` with no new template, but a generator opens no CHOICE POINT, so the bindings it must undo were never trailed

⛔ **STATUS: RUNG 7 IS NOT LANDED. Nothing pushed to `src/`.** `test_prolog_ladder.sh --only 7` is **0/4**, exactly as it
was at the start (SCRIP `f5bf7357`, corpus `d4d8a76f0`). The witnesses still REFUSE `rc=2` naming rung 7, which is the
honest state. This FINDING is the deliverable: a measured route, a precisely located blocker, and one correction to my
own reasoning that is worth more than the code was.

WIP saved, not discarded: `/home/resources/postoffice/salvage/hq_P-rung7-between-generator-wip-2026-09-02.patch`
(118 lines, `lower_prolog.c` +34, `bb_to.cpp` +29). ⛔ It COMPILES AND RUNS AND IS WRONG — see the blocker. Do not land it.

## ⭐ WHAT IS ESTABLISHED, AND IT IS THE EXPENSIVE HALF

**`between/3` needs NO NEW TEMPLATE.** ARCH § B.13 (ii) says it is Proebsting's `to(E1,E2)`, and that is literally true:
lowering `between(L,H,X)` to the shared `IR_TO` node plus the `$is_v` sink `is/2` already uses gives, measured:

- the **right number of solutions** — `between(1,3,X), write(X), nl, fail` ran the loop exactly **3 times** and then
  conceded to the second clause. The generator half, cursor and β chunk included, is a box we already ship for `i to j`.
- the **right value**, once the lvalue is on the spine (below).
- **test mode for free** — `between(1,3,2)` succeeds once, because a bound third argument just makes the unify a compare.

`ir_is_generator_kind()` is the right predicate to make `pl_lower_conj` treat a generator as resumable; adding it needed
one clause and covers the rest of § B.13, not just `between`.

## ⚠️ A REAL BUG FOUND AND FIXED ON THE WAY — THE ORPHANED LVALUE

First cut ordered the operands generator-first and evaluated `X`'s lvalue last. The `VAR_REF` was then **orphaned**:
nothing jumps to it, its slot is never populated, and `$is_v` binds through a stale cell. Symptom:
`between(1,3,X), write(X), nl, fail` printed **three empty lines** — the right NUMBER of solutions with no value in any
of them. `is/2` gets this right by ordering lvalue → value → sink, and the generator must do the same.
⭐ **A LITERAL THIRD ARGUMENT HID IT COMPLETELY**: `between(1,3,2)` printed `yes` throughout. The test-mode witness is
not evidence that the bind path works, and a rung that graded only it would have landed the bug.

## ⛔⛔ THE BLOCKER, LOCATED: A GENERATOR OPENS NO CHOICE POINT, SO ITS BINDINGS ARE NEVER TRAILED

With the lvalue fixed, the witness prints **`1`, then `done`** — one solution instead of three. Traced:

1. iteration 1 binds `X = 1` and prints it;
2. `fail` re-enters the generator's β, which offers `2`;
3. **`X` is still bound to 1**, so the unify fails against the stale binding, and again for `3`;
4. the generator drains and concedes. **Right control flow, wrong answer.**

The cure looks obvious — unwind the trail to a mark taken at the generator's α — and I implemented it in `bb_to`
(mark `r12` at α into the box's own state slot, `rt_pl_tr_unwind` on β), keyed on `x86_fb_pinned()`, the same regime
predicate `bb_disjunction` uses for its step unwind, never a language name. **It emits, and it changes nothing.**

⭐ **WHY, AND THIS IS THE PART THAT MATTERS:** `rt_pl_dop_is_v_c` binds through `cx->tr`, so a binding *can* be trailed —
but Prolog trails **conditionally**, and the emitter's own rung-2 comment states the rule: clause locals *"are younger
than this choice, so the log never recorded them"*, which is why the clause step **re-seeds** locals with `rep stosb`
instead of unwinding them. A generator mid-clause registers **no choice point at all**, so `X` is younger than every
choice that exists, nothing trails it, and unwinding to any mark is a no-op over an empty suffix.
✅ **ARCH § B.13 (i) ALREADY SPECIFIES THE MISSING PIECE, IN FOUR WORDS: `F.B := rbp` while more values remain.** The
generator must OPEN a choice point, not merely mark the trail. Until it does, no amount of unwinding can be correct.

⛔ **THAT IS AN ARCHITECTURE DECISION, NOT A CODING ONE, WHICH IS WHY I STOPPED.** `B` (r13) governs cut, `bb_to` is
shared — `grep -c IR_TO src/lower/lower_*.c`: **prolog 3, raku 3, icon 2** — and guessing at B's lifecycle on a shared
box is the exact shape that cost **47 Icon programs** at s272. Routed to ceo for sequencing against hq_C's frame work.

## ⛔⭐ A CORRECTION TO MY OWN REASONING, AND IT IS THE SAME CLASS I SPENT THE DAY CATALOGUING

Mid-investigation I concluded *"`x86_fb_pinned()` is FALSE for a Prolog clause graph"* — inferred from a compiled
disjunction emitting **zero** `PL DISJUNCTION STEP` lines, and I very nearly wrote it up as a live defect in landed
rung 3 (*"its unwind arms are inert"*).

⛔ **IT WAS WRONG, AND THE GUARD WAS TRUE THE WHOLE TIME.** The emitted `.s` carries **no `x86("comment")` prose at all**
— `grep -c 'PL DISJUNCTION STEP'` = 0 and `grep -c 'rung 3'` = 0 on a file that plainly contains four
`rt_pl_tr_unwind` calls. My own generator code was in the output all along:

```
n3_to_β:  mov rdi, [rbp+184];  call rt_pl_tr_unwind;  inc [rbp+176];  jmp .Lto_α
```

⭐ **I READ AN ABSENT MARKER AS AN ABSENT MECHANISM** — hq_B's family exactly (*an instrument answering a narrower
question than the reader thinks it asked*): `grep` answered **does this string appear in the output**, and I read it as
**did this code path run**. Two guards were saved by process rather than by insight, and both are worth keeping:
**(a)** I tested the disjunction-with-binding against swipl before publishing the "rung 3 is broken" claim, and it
printed `1 2` in agreement — the claim died on a measurement, one step short of a FINDING that would have sent hq_C
hunting a bug that does not exist. **(b)** VERIFY-BEFORE-QUOTE is not a formality here; comments being stripped from
`.s` means *no* grep for prose can ever witness a template arm firing. **Grep for the INSTRUCTIONS, never the comment.**

## What the next attempt should do

1. Open a choice point at the generator's α per § B.13 (i) (`F.B`), and restore it at ω — with ceo/hq_C ruling on B's
   lifecycle first, because cut reads it.
2. Keep the trail mark + β unwind from the salvage patch; they are correct and become live the moment (1) exists.
3. Keep the lvalue-on-the-spine ordering; test-mode witnesses cannot catch its absence.
4. Grade on **all three** frontends that lower `IR_TO` — Prolog, Raku, Icon — not Prolog alone.
