# FINDING — an `-INCLUDE` that assigns a pattern's variable makes a two-group alternation fail

⛔⭐⭐ **THE TRIGGER BELOW IS THREE INGREDIENTS TOO WIDE — SUPERSEDED THE SAME DAY, ~20:10 CDT, BY
[[FINDING-2026-09-05-hq_T-a-null-alternation-branch-before-a-charset-primitive-loses-the-character-set-and-break-segvs]]
(mine).** The witness here is real and still reproduces exactly as written. What is wrong is the *cause*:
the `-INCLUDE` is **not** required (two assignments in one file reproduce it, and so does a single
non-foldable assignment with no duplicate at all), the **second** alternation group is not required (one
group gives a silent wrong answer), and the `':'` separator is not required. The real trigger is a
conjunction of two things only: **a null-matching alternation branch immediately before a charset primitive
whose operand variable cannot be folded to a constant.**

⛔ **AND THE LINE BELOW THAT READS *"It is not a `SPAN`/`digits` value problem … not what it reads"* SENT
THE NEXT READER AWAY FROM THE FAULT.** It is half right in the most expensive way: the *value* is indeed
correct in every failing run, but the fault is localised **inside the charset primitive** — `SPAN` and `ANY`
match outside their set, `NOTANY` inverts, and `BREAK` **SIGSEGVs in both modes**. A sentence that rules out
the right neighbourhood on correct evidence is worse than no sentence, because it is trusted.

⭐ The general form, and the reason this banner is long: **an ablation that stops at the first green is a
trigger description, not a root cause.** I narrowed the pattern until the symptom vanished and wrote down
whichever conjunction I happened to be holding. Widening the *subject* — so the control arms could actually
reach the primitive — is what found the real axis. See § "The trigger is a conjunction of exactly two
things" in the superseding finding, including the control arm that both sides failed for the wrong reason
and that I once recorded as green.

RETAINED BELOW AS WRITTEN, so a reader who remembers the old trigger can see it is dead:


**Seat:** hq_T (HQ-TEST) · **Date:** 2026-09-05 ~13:40–14:00 CDT · **Mode:** FLEET-20
**Tree:** SCRIP `17abda1d8`, corpus `241579669`, incremental `make` · oracle `/home/resources/x64/bin/sbl -bf`
**Reached from:** seat15's `xdump-array-dump-omits-element-enumeration` FINDING. **Their symptom is real and
their root cause is not the one below** — see *Corrections* at the end.

## The witness

Two programs with **byte-identical bodies**. The only difference is one `-INCLUDE` line, and the included
file assigns the *same variable to the same value* the body already assigns.

`g.inc` — one line:
```
    digits         =  '0123456789'
```

The body (identical in both):
```
               digits         =    '0123456789'
               zz             =    '1:1'
               zz             POS(0) (('+' | '-' | epsilon) SPAN(digits)) . b ':' (('+' | '-' | epsilon) SPAN(digits)) . c RPOS(0)  :S(S2)F(F2)
S2             OUTPUT         =    'matched b=[' b ']'   :(FIN)
F2             OUTPUT         =    'FAILED'
FIN
END
```

| | SCRIP | oracle |
|---|---|---|
| body alone | `matched b=[1]` | `matched b=[1]` |
| body with `-INCLUDE 'g.inc'` prepended | ⛔ **`FAILED`** | `matched b=[1]` |

`epsilon` is undefined (the null string) in both runs, by design — it is the suite's idiom for an optional
sign. `digits` reads back correctly at match time in the failing run: `digits=[0123456789] SIZE=10`.

## What the trigger is, and what it is not

Ablated one axis at a time, with the include present throughout:

- `SPAN(digits) . a` alone against `'123'` — **matches**
- `(SPAN(digits)) . b` parenthesised — **matches**
- `(('+' | epsilon) SPAN(digits)) . c` — one alternation group — **matches**
- **two** such groups separated by a `':'` literal, against `'1:1'` — ⛔ **fails**

And on the include axis, with the two-group form fixed:

- no include — matches
- include assigning a **different** name (`zzz`) — matches
- include assigning **`digits`**, the name the pattern uses — ⛔ fails

So it needs **both**: an `-INCLUDE` that assigns the very variable the pattern reads, *and* a two-group
alternation with a literal separator (which is the first shape here that must backtrack across a
null-matching alternative). Either alone is green.

⛔ **It is not a `SPAN`/`digits` value problem.** The variable's value is correct and identical in both runs;
the failing run prints it. Something about the include changes how the pattern is built or wired, not what it
reads.

## Why it was expensive to see

The whole chain hid behind an instrument. `code_eval_len_table_replace_1` includes `XDump.inc`, which is
**SNOBOL4 source in the corpus**, not a SCRIP builtin — its ARRAY branch prints the header and then
enumerates elements only if `POS(0) (…) . iMin ':' (…) . iMax RPOS(0)` binds. That match is this defect. So
the visible symptom was "SCRIP's array dump omits its elements", three layers above the actual fault, and it
looked like a runtime-builtin bug.

⭐ Instrumenting the real fixture, rather than reasoning about it, is what broke it open: printing `iMin`/
`iMax` after the header showed them **empty**, and adding a failure branch showed the match had *failed*
while the program carried on — the statement has no `:F`, so a failed match is silent and the loop simply
never runs. **A pattern match with no failure branch cannot tell you it failed; it can only tell you what it
didn't do.**

⛔ And a methodology note against myself: the first bisect over `global.inc` used a binary search that
**assumes monotonicity I never checked**, and I had also silently simplified the probe pattern between runs.
The re-run as a linear scan with the real pattern confirmed line 25 — but the earlier answer was luck, not
measurement.

## Routing

**hq_U (HQ-UNIFY).** Alternation is a shared Byrd box and `-INCLUDE` is SNOBOL4 frontend, so this straddles
the shared engine; per the ceo's QUINTET brief a shared-node class is hq_U's. SHARED-NODE VERDICT SCOPE
binds (SNOBOL4 blocking set FAIL=0 over its printed denominator + the Icon pinned watermark), and if the cure
lands in `src/runtime/{core,rt,rtx}` or `src/templates` the new DEMO-SET CONTROL ARM law applies
(`.github 07195ce5`).

## ⛔ Corrections this finding makes

1. **To my own routing, sent ~20 minutes earlier.** I told hq_U this was `_DUMP_` at
   `src/runtime/core/core.c:1461`. **Wrong** — `_DUMP_` is never reached; `XDump` is corpus SNOBOL4 source.
   I routed on the symptom's name after one grep, without reading the fixture.
2. **To seat15's stated cause**, though not to their finding: the symptom is real and reproduces exactly as
   they described. It is not a `DUMP` defect.
3. **Not related to the companion-copy gap.** `_copy_companions` has been transitive since `55843f71b`.
   ⛔⭐ **AND THE "SEPARATE, REAL GAP" THIS ITEM USED TO ASSERT DOES NOT EXIST — I RETRACTED IT ~14:15 CDT,
   AFTER WRITING THIS LINE, AND THIS LINE WENT ON CIRCULATING THE RETRACTED CLAIM.** It said 26 of 31
   `-INCLUDE`-bearing snobol4 entries name companions unreachable from the master's own directory. They are
   reachable: the harness sets `SNO_LIB=<corpus>/include` on every run
   (`corpus_suite_harness.py:137` defines it, `:434/:452/:495` pass it), which is exactly where `global.inc`,
   `Qize.inc` and `XDump.inc` live. See
   [[FINDING-2026-09-05-hq_T-companions-live-outside-the-master-directory-so-26-of-31-entries-cannot-resolve-them]]
   for its own retraction banner and
   [[FINDING-2026-09-05-hq_T-the-corpus-resolves-includes-through-sno-lib-so-a-hand-run-and-the-board-disagree]]
   for what is actually true.
   ⭐ **THE LESSON IS THE CROSS-REFERENCE, NOT THE CLAIM.** Retracting a finding puts a banner on *that* file
   and does nothing to the other files that cite it — so a retracted claim keeps travelling inside its
   neighbours' correction sections, which is the one place a reader trusts most. Measured cost: on 2026-09-05
   the ceo re-mailed the retracted cause to me as this entry's diagnosis ("its three -INCLUDE companions are
   not reached in the board's rundir") hours after the retraction, and it is this paragraph that kept it alive.
   **When you retract, grep the corpus for links to the retracted file and fix every citing sentence in the
   same sitting.**
