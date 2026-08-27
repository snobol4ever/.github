# FINDING — &LINE / &LASTLINE were ABSENT from the keyword table, not broken

**Seat:** hq_C (HQ-CORRECTNESS) · **Date:** 2026-08-27 · **Row:** `conform-line-lastline-crash`
**Landed:** SCRIP `c4b454e5` · corpus `973a04e8a` · **Grant cited:** Lon 2026-08-27 in-chat to CEO (CEO-30)

## What was wrong

Reading `&LINE` or `&LASTLINE` truncated program output and exited rc=1 in **both media**, while the
sibling statement-number keywords `&STNO` / `&LASTNO` worked correctly. The visible error was:

```
** Error 342 in statement 0
   &constant read before its one-time assignment: &LINE
```

`src/runtime/keywords.c`'s `g_kwb[]` binding table had rows for STNO / LASTNO / STCOUNT and **none for
LINE / LASTLINE**. Root-caused at source level by seat10 (2026-08-24), who was blocked on the FACT RULE
and correctly did not implement it; Lon's grant landed 2026-08-27 and this seat implemented it.

## ⭐ THE GENERALISABLE LESSON: A FALLBACK ARM TURNS "MISSING" INTO "MISCLASSIFIED", AND THE ERROR MESSAGE THEN NAMES THE FALLBACK'S RULE RATHER THAN THE REAL CAUSE

`&LINE` was not broken. It was **absent** from the table that turns a protected-keyword NAME into a
runtime cell. `ARCH-SN4-CONSTANTS.md` defines a three-tier `&` namespace, and tier 3 is the catch-all
*"every other `&name` = USER CONSTANT"*. So an unlisted keyword does not fail as *unknown keyword* — it
is silently **reclassified** as a user constant and then dies on that tier's own one-time-assignment
check. Every word of Error 342 is true about the tier it came from and false about the actual defect:
there was no constant, no assignment and no read-before-write. An investigator reading it is pointed at
the constant machinery, which is exactly where the bug is not.

⛔ **The cheap test for this shape:** when an error names a *category* the thing should never have been
in, suspect the classifier, not the category's machinery. Ask *"what would have to be true for this
message to be right?"* — here, that `&LINE` was a user constant, which one look at the table refutes.

This is the same family as the `command -v` lesson in `CLAUDE.md` (a tool answering a narrower question
than you think you asked, and never saying so) and `RULES.md:107` (a correct procedure with a false
stated cause). Here the *instrument* is a table lookup with a default arm: it cannot report a miss,
because a miss is indistinguishable from a tier-3 hit **by construction**.

## ⭐ A DEFECT CAN HIDE BEHIND ANOTHER DEFECT, AND CLEARING THE FIRST IS WHAT MAKES THE SECOND MEASURABLE

`k11_lastfile_lastline_lastno.sno` tests three keywords and died on the second, so its `&LASTFILE` read
was **never executed**. `&LASTFILE` therefore read as *untested*, not as *confirmed working* — a
distinction the row's own STEP 1 note (seat08) was careful to make and which turned out to be exactly
right. With `&LASTLINE` fixed, k11 advances precisely one statement and stops on `&LASTFILE`.

⛔ **The trap this sets for the next seat:** a witness that fails at the same visible place before and
after a real cure looks like a cure that did nothing. It is not — the failure MOVED. Read *which*
statement failed, never just that the witness is still red. New witness `k30_lastfile_only.sno` exists
to make `&LASTFILE` measurable on its own rather than behind an earlier failure.

## ⭐ THE SOURCE LINE AND THE STATEMENT NUMBER ARE NOT INTERCHANGEABLE, AND THE EXISTING WITNESS COULD NOT TELL

In `k14_stno_line.sno` every statement sits on its own matching line, so `&STNO` and `&LINE` coincide
and an implementation returning the **wrong one of the two** would still pass. Comment runs and blank
lines pull them apart. Measured against SPITBOL: stno **2** sits on line **4**; later stno 5 on line 9.
New witness `k31_line_lastline_gaps.sno` pins that divergence and is byte-identical to the oracle in
both modes. ⭐ **A witness whose two variables happen to be equal is not a test of either.**

Two `&LASTFILE` semantics were also established against the oracle rather than assumed, and are pinned
in k30: it names the **previous** statement's file (reading it as the first statement answers null), and
it answers the source path **as invoked** — so a witness printing the bare path would carry a `.ref`
that changes with the caller's cwd. k30 reports only the basename tail and is verified identical under
relative and absolute invocation.

## The cure

Two granted globals `g_line` / `g_lastline` mirroring `g_stno` / `g_lastno` exactly, two `KWB_PROT` rows
carrying `sym` `"g_line"` / `"g_lastline"`, the by-name read fallback, and `rt_stmt_enter` advancing the
line pair the way it already advances the stno pair. `SNO$STMT` takes a second operand (reusing the
existing builtin id, so the generated `builtin_ids.h` is untouched); `sno_kw_is_stmt` learns the two
names so `&LINE` arms the same per-statement hook `&STNO` arms; lowering threads each statement's
compile-time-known `:line`.

⭐ **Two things made this small rather than invasive.** (1) `:line` already rode on the *same* `st[i]`
node whose index yields correct `&STNO`, so line and stno agree **by construction**, not by coincidence
— no new plumbing and no second source of truth. (2) A non-NULL `sym` is what unlocks the emitter's KW-D
direct-cell path (`bb_keyword_snobol4.cpp`), so both media get the fast path with **no medium branch
added**: TEXT renders the assembler symbol, BINARY bakes the address. BOTH-MEDIUM fell out of using the
existing mechanism correctly rather than being engineered.

## Measured (make pristine EXIT=0 first, HQ-27; re-proven after rebase)

| arm | result |
|---|---|
| `k14_stno_line` | **m3=PASS m4=PASS** (was: output truncated, rc=1, both media) |
| `k31_line_lastline_gaps` (new) | **m3=PASS m4=PASS** |
| SNOBOL4 board | m3 **365/365 FAIL=0** · m4 **365/365 FAIL=0 SKIP=0 MISSING=0** (identical to baseline) |
| `test_gate_emit_no_lang` | EXIT=0 |
| `test_gate_template_medium_invisible` | EXIT=0 |
| SHARED-NODE control arms | icon smoke 14/14 FAIL=0 · rebus 4/4 FAIL=0 |
| prolog `clause`, snocone `procedure` | RED but **PRE-EXISTING — proven by A/B**, not assumed |
| `.s` regen ×3 (benchmark, demo, prolog-bench) | **changed=0** on all three |

⛔ **The two red control arms were A/B'd, not explained away.** Both fail identically with the three
changed files stashed and rebuilt. A pre-existing red that a session merely *asserts* is pre-existing is
indistinguishable from a regression it caused; the stash-and-rebuild costs minutes and settles it.

⭐ **`changed=0` across all three regens is itself the blast-radius measurement.** The hook is gated on
`g_sno_uses_stmtkw`, so only programs that actually use statement keywords can move — and no benchmark,
demo or prolog bench does. This is a stronger statement than "the board stayed green", which would also
be true of a change that quietly moved bytes everywhere without changing behaviour.

## Left undone, deliberately, and why

⛔ **`&LASTFILE` IS NOT IMPLEMENTED, AND THAT IS A SCOPE RULING, NOT AN OVERSIGHT.** Lon's grant is
explicit: *"Scope of the grant is exactly these two cells for &LINE/&LASTLINE — not a general license."*
`&LASTFILE` needs its **own** new global (a source-filename cell; measured — the runtime has no such
state today, so there is nothing to repoint to) and therefore its own grant. This row's DONE-WHEN
requires k11 to pass, and k11 reads `&LASTFILE`, so **the DONE-WHEN cannot go green on this row's own
scope**. Routed to ceo as `q-lastfile-needs-its-own-grant`. Sibling row `kw-missing-4` owns `&FILE` /
`&LASTFILE`.

⭐ **The row's DONE-WHEN is over-scoped relative to its GOAL** — the GOAL names `&LINE`/`&LASTLINE`, the
DONE-WHEN demands a third keyword nobody granted. Worth noting as a class: a DONE-WHEN assembled from
*whole witness files* inherits every keyword those files touch, including ones outside the row.
