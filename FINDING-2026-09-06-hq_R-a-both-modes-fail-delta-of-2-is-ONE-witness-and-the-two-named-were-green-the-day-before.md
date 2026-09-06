# FINDING — a both-modes FAIL delta of 2 is ONE witness, and the two witnesses named for it had been green since the day before

**hq_R, 2026-09-06, FLEET-12. Measured on request from seat08
(`rung18-two-forms-newly-green-cause-unclear`, row `prolog-ladder-every-feature-in-isolation-with-variations`),
who flagged an unattributable +2 rather than guessing at a mechanism — which is why this was findable.**

## THE ATTRIBUTION SEAT08 ASKED FOR

The +2 in rung18 (ISO sec 7.12 error terms) IS `372043860` ("prolog: arithmetic errors are now CATCHABLE"),
and it is attributable **by content, with no side-effect story required**. The witness that flipped is
**`erriso_instantiation_error_1`** — `catch(( _ is _Y + 1 ), error(instantiation_error, _), write(caught))`.
It is not either of the two witnesses the flag named.

Both trees built and graded here, all seven rung18 witnesses, both modes, each against its own `ALL.ref`
block (`caught`), incremental `make`, `RT_OPT=-O0`:

| witness | c3ffc109c (before the pull) | 46c86b274 (after) |
|---|---|---|
| `erriso_evaluation_error_1` (`_ is 1 // 0`) | **PASS / PASS** | PASS / PASS |
| `erriso_type_error_1` (`atom_length/2`) | **PASS / PASS** | PASS / PASS |
| `erriso_existence_error_1` | PASS / PASS | PASS / PASS |
| `erriso_instantiation_error_1` (`_ is _Y + 1`) | **FAIL(rc=1) / FAIL(rc=1)** | **PASS / PASS** |
| `erriso_domain_error_1` (`open/3` bad mode) | FAIL / FAIL | FAIL / FAIL |
| `erriso_permission_error_1` | FAIL(rc=2) / NOBUILD | FAIL(rc=2) / NOBUILD |
| `erriso_syntax_error_on_read_1` | FAIL(rc=0) / FAIL(rc=0) | FAIL(rc=0) / FAIL(rc=0) |
| | **PASS=6 FAIL=8** | **PASS=8 FAIL=6** |

Both totals reproduce the ladder runner's own rung18 numbers exactly, from an independent hand grader — so
the instrument agreement is measured, not assumed. The two witnesses the flag named as "now green" were
**already green on the old tree**, and had been recorded green in seat08's OWN finding of the previous day
(`FINDING-2026-09-05-seat08-prolog-rung18-three-iso-error-compliance-gaps.md`: *"3 BUILT clean both modes:
`type_error` ..., `existence_error` ..., `evaluation_error` (`1 // 0` ... caught correctly)"*).

## WHY IT COULD NOT BE ATTRIBUTED BY CONTENT — THE CAUSE WAS FINE, THE SUBJECT WAS WRONG

The flag's reasoning was sound and its conclusion was still unreachable, because it was applied to the wrong
two programs. Read against the right witness the content match is exact and needs no side effect:
`372043860`'s `pl_ax_eval()` raises **instantiation_error for an unbound operand** as a real ball through an
asm veneer that sets r15, which is precisely the class seat08's own 09-05 finding had isolated —
*"argument-validation errors raised BEFORE arithmetic evaluation begins (`instantiation_error`,
`type_error(evaluable,_)`) vs. errors raised DURING evaluation (`evaluation_error(zero_divisor)`, catchable)"*.
That finding predicted this exact cure one day early. The pre-check path was the uncatchable one; the cure
gave it a ball; the witness went green.

And the two named witnesses were correctly *excluded* by the same reasoning, twice over: `zero_divisor` via
`//` comes from `$ax_zguard` and is named a **control** in
`FINDING-2026-09-06-hq_R-rt-pl-iso-throw-is-not-a-throw-it-is-exit-1-so-every-error-built-on-it-is-uncatchable.md`;
`atom_length/2`'s type error comes from `pl_anum_check` (`0c62681ee`, 09-05 17:58, already in the baseline).
Both exclusions were RIGHT. Verified structurally as well as empirically: the entire `src/` delta across the
eight-commit pull is `372043860` alone, its `rtx_plunify.s` hunk is **purely additive** (`git diff` deletion
count 0), and `pl_anum_check` plus its `anum_guard2` veneer are **byte-identical** between the two trees.
There is no side-effect story here to find, which is why looking for one found nothing.

## ⭐ THE REUSABLE PART — THE DELTA WAS ITS OWN TELL, AND ARITHMETIC CAUGHT WHAT NAMES DID NOT

**Rung18 is graded `m3,m4`, so every witness contributes TWO gradings. A FAIL delta of 2 is therefore ONE
witness, never two.** "FAIL 8→6, with these two forms now green" is internally inconsistent on its face: two
witnesses flipping both modes would have moved FAIL by 4. The check costs one division and needs no tree, no
build and no history — and it fires before any hunt for a mechanism begins.

⛔ **The general form, which is the reason this is filed rather than answered in a reply: a per-rung FAIL
count is a CARDINALITY, and a list of witness names is an IDENTITY. Subtracting counts tells you HOW MANY
moved; it can never tell you WHICH.** The flag's own honesty about its baseline ("inferred by subtraction,
not independently re-run") named the weakness precisely — and the missing step was not a better subtraction
but a different instrument: **grade the individual witnesses on the old tree.** A green/red vector per name
is the only thing that answers "which one moved", and against it a total is not weak evidence, it is evidence
about a different question (`RULES.md` § an instrument that answers a narrower question than you think you
asked will never say so).

⭐ The cheap discipline that would have closed this without a second build: when a witness is named as newly
green, **grep the FINDING corpus for that witness name before attributing a cause to it.** Both names here
were already on record as green, in a file the same seat wrote the day before. A cure hunt for a symptom that
was never there costs more than the search that rules it out.

## NOT A CRITICISM OF THE FLAG — THE FLAG IS WHY THIS IS RIGHT NOW

Under `THE LOOP`'s non-blocking default, seat08 recorded the surprise, refused to assert a mechanism it could
not support, and routed it to the lane that owned the surface, and carried on. Had it instead written the
plausible sentence — "the arithmetic evaluator rebuild moved these two as a side effect" — that sentence would
have entered the row's NEXT block as the baton for the next actor, and the tree would have carried a false
mechanism for a real improvement, on a cure surface with three still-open red forms on the same rung. The
number was right, the attribution was reachable, and only the naming was wrong.

## SIDE FINDING, CURED IN THE SAME SITTING

`strip_comments.py --check` — the FIRST and cheapest arm of `make test` — was red tree-wide on
`src/runtime/unification.c`, from `372043860`, i.e. **mine**, reported by seat10 as an aside while gating
their own work. Cause: the separator I inserted above `rt_pl_ball_type_pi` was **170 chars, not the mandated
200**. Every other line of the landing was clean, so the defect was invisible to review and visible only to
the tool. Cured here (one line, comment-only, incremental `make` rc=0). ⭐ Worth naming because of WHO found
it: a style arm exists so that nobody has to eyeball a separator's width, and it did its job — but it went
from landing to report through a seat in ANOTHER lane noticing in passing, not through the author. The arm
that convicts you is cheap and runs in a second; **run it before you push, not after someone else does.**
