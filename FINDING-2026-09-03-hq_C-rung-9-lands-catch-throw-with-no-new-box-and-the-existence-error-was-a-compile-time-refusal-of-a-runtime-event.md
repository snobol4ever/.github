# FINDING — rung 9 lands catch/throw with NO NEW BOX, and the biggest win was a COMPILE-TIME REFUSAL OF A RUN-TIME EVENT

**Seat:** hq_C (HQ-COMPLETE) · **Date:** 2026-09-03 · **Mode:** FLEET-16
**Row:** `prolog-rung-9-catch-throw-and-existence-errors-become-runtime-balls`
**Tree:** from origin SCRIP `bc3b2075b` · corpus `600b445e` · .github `90aac0de`
**Law:** RULES.md § THE PROLOG REBUILD GATE · `ARCH-PROLOG-BYRD-BOX-TRANSLATION.md` § E row 9, § B.10, § A.1 review C9

---

## ⭐⭐⭐ THE ONE PREDICTED NEW BOX OF THE WHOLE LADDER TURNED OUT TO BE COMPOSABLE

§ B.0 and § E row 9 both name `bb_catch` as **THE ONE GENUINELY NEW BOX** of the eleven-shape
ladder — "nine of eleven shapes are boxes Icon/SNOBOL4 already own; `bb_catch` is the one new
box". **It is now eleven of eleven.** `catch/3` landed with **no new box, no new IR kind, and no
`F.BALL` slot**, because the handler decomposes exactly into machinery earlier rungs already built:

| B.10 step | what actually does it |
|---|---|
| bank the trail top, open the choice | `IR_BOUND` — rung 5's mark, unchanged |
| ISO: undo bindings *before* unifying the catcher | `IR_UNMARK` — rung 5's unmark, unchanged |
| test the ball, unify the catcher, clear `r15` | one rtx-gated leaf `$catch_handle` |
| caught → Recovery · not caught → re-throw | the leaf's own γ/ω: `DT_FAIL` takes the box's ω |

⭐ **The reason it composes is a coincidence worth naming: ISO's ordering rule and rung 5's
mark/unmark pair are the same shape.** ISO says *the bindings made since `catch/3` was called are
undone BEFORE the catcher is unified*. That is precisely "unwind to the mark, then continue" —
which is what `IR_UNMARK` already is. The spec sentence and the existing box are the same
instruction, so the box that looked new was a box already on the shelf.

⛔ **What is NOT claimed:** `H.β → Goal.β` — catch/3 transparent to *backtracking into* a caught
goal. No rung-9 witness exercises it, so it is neither implemented nor claimed; it belongs to
whoever writes that witness. **And `F.B := F.B0` is deliberately not restored**, on rung 5's own
precedent recorded in § B.13 review (3): `rt_pl_disj_open` only ever RAISES B, so leaving it
raised **over-logs and never under-logs**. Over-logging is safe; under-logging is the bug.

## ⭐⭐ THE ~45-ENTRY WIN WAS NOT A CONSTRUCT AT ALL — IT WAS A CATEGORY ERROR IN THE LOWERER

Of the 74 entries rung 9 is the first refusal for, **catch is 22 and throw is 5. The other ~45 were
`pl_user_call` calling `pl_refuse("existence error for unknown procedure", key, 9)`** — refusing at
**COMPILE** time an event that ISO defines at **RUN** time. swipl compiles the program and raises
`existence_error(procedure, N/A)` when the call is *reached*; SCRIP refused to build it at all, so
`catch(undefined_thing(1), E, ...)` could never even be *attempted*.

⭐ **The general form, and it is the reason this rung was worth more than its two named constructs:
a diagnostic emitted at the wrong PHASE is not a strict diagnostic, it is a WRONG ANSWER that
happens to be loud.** Nothing about the refusal looked like a defect — it named a real error, with
the right words, at rung 9. It was filed under "not on the ladder yet" for the whole life of the
Prolog frontend. The cure is not a construct: `pl_user_call` lowers the unknown call to a leaf that
builds the ISO ball and takes ω, and ~45 programs start running.

## ⭐⭐ A STALE MEASUREMENT THAT WOULD HAVE COST THIS RUNG A REDUNDANT WRITE — AND THE READING ERROR THAT MADE IT

§ A.1 carried, from hq_P's BX-0 instrument on SCRIP `f4532dea`: *"`r15` holds a driver mmap address
at every Prolog ω today, not 0 — so before any β guard or catch handler may trust `r15`, C37 zeroes
it at Prolog graph entry."* The ceo's rung-9 GO telegram repeated it as an instruction.

**Re-measured on `6fceb3e9` and again on the landing tree: `r15` is ALREADY 0 at every Prolog ω.**
`porttrace.cpp` prints its `r15=0x…` field **only when the ball is non-zero at an ω port**, and two
witnesses taking 1 and 3 Prolog ωs print **no `r15=` field at all**. The mechanism agrees: rung 0's
`rt_pl_quad_seed` does `xor r15d, r15d` and the quad gate holds emitted quad-writes at 0, so nothing
can dirty it.

⭐ **The instrument was right; the READING was wrong — an absent field was read as "not measured"
rather than "measured zero".** That is § A CORRECT PROCEDURE WITH A FALSE EXPLANATION seen from the
other side: there, a true procedure carried a false cause; here, a true instrument carried a false
reading, and the false reading propagated into the page, into a planned C37 write, and into a GO
telegram. **Both are the same defect class — nobody re-ran the instrument, because the claim was
already written down.** The redundant write is NOT added; § A.1 is corrected in this commit.

## ⭐ THE ITE WAS MEASURED SWALLOWING AN EXCEPTION, EXACTLY AS RUNG 5 PREDICTED IN WRITING

Rung 5 re-filed `ite_condition_throws` here and left a written obligation: *"an ITE must not swallow
an exception; `C.ω` goes straight to the else-arm entry, so a ball in flight WOULD run the else
arm."* **Measured, first build of this rung:** `write(before), ( throw(oops) -> write(yes) ;
write(no) ), write(after)` printed `before` / `no` / `after`. The prediction was exact.

The C9 guard (`test r15,r15 ; jnz <own ω>`) now sits in the condition-failure `IR_UNMARK` and is
gated on **a flag the LOWERER sets**, not on a language name or a frame shape — so an Icon or
SNOBOL4 unmark never carries it. ⭐ **A hazard named in prose by the rung that could not fix it, and
found by the rung that could, cost one measurement instead of one debugging session.** The rung-5
note is why this was the first thing looked at rather than the last.

## ⭐ THE QUAD GATE CAUGHT ALL FOUR NEW BALL WRITERS UNENROLLED, ON THE FIRST `make test`

`rtx-writes=17 rtx-violations=4` — `rt_pl_throw_raise`, `rt_pl_exist_raise`, `rt_pl_catch_handle`
and `rt_pl_ball_take`, every one of them a legitimate `r15` writer, every one of them unnamed.
The scanner's own header states the protocol ("a rung that adds a writer adds its exact name here")
and the four are **named, not relaxed**. ⭐ The gate did the one thing a gate is for: it refused a
change its author believed was fine. The author's belief was in fact correct — and the gate was
still right to refuse, because "correct" and "declared" are different properties.

## GRADED — pristine `-O0`, shared-node scope honoured

- **Fail-once** on clean origin `bc3b2075b`: ladder `--to 9` **rc=1**, rung 9 **PASS=0 FAIL=6**, rungs 0–8 **50/50**.
- **Pass-once** on a `make pristine` tree: ladder `--to 9` **PASS 56/56**, rung 9 **6/6 both modes**.
- Port-trace gate `--to 9` **PASS(0) 56/56**; six rung-9 blocks cut by the gate's own merging `--cut`, refs **70 → 76 blocks**, every other block kept.
- Quad gate **PASS(0)**, 0 unenrolled r12–r15 writes, 143 compiled witnesses, rtx-writes 17.
- `nm -D` Prolog-only data symbols = **0**. `strip_comments.py --check` **rc=0** over 384 files.
- **SNOBOL4 control arm: m3 PASS=1679 FAIL=0 · m4 PASS=1679 FAIL=0 SKIP=0 MISSING=0.**
- **Icon control arm, measured as byte-identity rather than as a board number** (see below): **111 Icon witnesses compiled in mode 4 against a clean `bc3b2075b` clone — `.s` IDENTICAL 111 / DIFFERENT 0**, and **10 of the 111 carry a bound/unmark box**, so the one genuinely shared node this rung touched is exercised and unchanged. Icon smoke **14/14 both modes**.

### ⛔ WHY THE ICON CONTROL ARM IS A DIFF AND NOT THE BOARD NUMBER THE BATON ASKED FOR
The baton's control arm was the STRICT rung-suite watermark **264/6/1/27 of 298**. This tree reads
**266/4/1/26 of 297** — and **none of that movement is this rung's**: seat01, seat02, seat03, seat07
and seat14 all landed Icon cures today, and corpus `600b445e` promoted a stale XFAIL marker. **The
baton's baseline was measured on the rung-5 tree, so quoting it as a before-arm would have been the
REBASE-BASELINE COROLLARY violation in its purest form** — a delta across two different trees.
⭐ **A pinned watermark is only a control arm while the tree under it is still.** With sixteen seats
landing, it stops being one, and the honest substitute is a same-tree A/B: build the baseline
commit in its own checkout (the objdir is per-checkout by construction, so it cannot disturb the
pristine tree) and diff the emitted code. That answers the question the watermark was standing in
for — *did MY diff move Icon* — and answers it exactly, where the board can only answer *did
anything move Icon*.

### ⭐ FOUR SEMANTICS NO RUNG-9 WITNESS COVERS, HAND-CHECKED AGAINST swipl — ALL FOUR IDENTICAL
The three ladder witnesses are deterministic and shallow, so a green rung is necessary and not
sufficient (RULES/CLAUDE.md § A GREEN BOARD IS NECESSARY, NEVER SUFFICIENT). Four more programs,
run against the oracle rather than against a `.ref`:

| program | swipl | scrip |
|---|---|---|
| `catch(throw(foo(1)), bar(_), …)` — catcher does NOT match → re-throw | *(no stdout)* rc=0 | *(no stdout)* rc=0 |
| nested catch, inner catcher does not match, outer does | `outer_caught` `done` | `outer_caught` `done` |
| `catch((X = 1, throw(oops)), E, …)` then test `X` | `caught(oops)` `x_unbound` | `caught(oops)` `x_unbound` |
| `catch(fail, _, …)` — plain failure is not a ball | `no` | `no` |

⭐ **The third row is the one that matters most: it is ISO's undo-before-unify rule, observed
directly.** `X` is bound to 1, the throw happens, the catcher matches — and `X` comes back
**unbound**, because `IR_UNMARK` unwound the trail before `$catch_handle` ran. That ordering is the
whole reason the decomposition above is legitimate rather than merely convenient, and it is now
measured rather than argued.

## THE WAM-RESIDUE CENSUS LINE (§ E, required of every rung receipt)
No argument registers — the catcher and the ball are frame words and a heap cell. No separate
environment / choice-point / PDL areas — the catch's choice IS the enclosing frame, opened through
`rt_pl_disj_open` on that frame's own words. No dispatch — every port is a wired jump; the handler
is straight-line code between two labels. `nm -D` Prolog-only data symbols **0**: the ball lives on
`r15` and on the GC heap, never in a `g_pl_throw_ball`. The three zetas hold everything: the mark in
ζ-ACTIVATION-FRAME, the ball on the heap (an escaper by definition — it must outlive every frame
between throw and catch), nothing in ζ-STANDING.

## OWED TO ceo, ANSWERED
- **The board's m3 hang IS hq_C's** — the rung-5 `nslots` regression (a directive's variables were never slot-numbered, so `max_var_slot` read the low 32 bits of a `char *`). Cured and landed separately before this rung.
- **The board's m4 `copy_term_ite_list_replace_1` rc=1 did NOT reproduce** — 0 in both modes on a quiet box; a 12-seat-load artefact of the per-entry timeout, not a defect.
