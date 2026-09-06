# FINDING 2026-09-06 hq_P — the gimpel inventory's `ungraded` bucket was identically zero by construction, and the lockdown's own criterion is `ungraded=0`

**Tree:** SCRIP `2e5a12a35` → cure, corpus `fc7b9f033` → sidecar, .github `723b5127`. MODE FLEET-12.
**Row:** `snobol4-gimpel-suite-126-to-100-percent-by-class` (hq_C's, ASSIGNED:hq_P) under the ceo's rank-0
PACKAGE LOCKDOWN (CEO-303/307; Lon 2026-09-06: *"Fix the never graded business. Let's lock down our package
testing and make it complete."*).
**Found while** doing what CEO-307 (3) ordered before minting seat02's census baton — *the gimpel runner's
error-number arm CONFIRMED, not assumed.* The confirmation went the other way (§ 4), and the tautology was
sitting beside it.

## 1. THE CLAIM

`test_snobol4_gimpel_suite.sh` printed `PACKAGE_INVENTORY shipped=289 graded=126 ungradable=163 ungraded=0`.
The lockdown's criterion is `ungraded=0`. **That number could not have been anything else.** Its four lines:

```
libmods=$((real_shipped - TOTAL))          # whatever the board did not grade
ungradable=$((libmods + UNSCR))
ungraded=$((real_shipped - SCORED - ungradable))     # with SCORED = TOTAL - UNSCR
```

Substitute: `real_shipped − (TOTAL−UNSCR) − (real_shipped−TOTAL) − UNSCR`. Every term cancels. **≡ 0.**

## 2. NOT "USUALLY ZERO" — MEASURED OVER EIGHT ARMS, INCLUDING ABSURD ONES

The four lines were extracted verbatim and run over synthetic inputs. Every one printed `ungraded=0`:

| input | graded | ungradable | ungraded |
|---|---|---|---|
| today's real board (289 shipped, 144 rows, 18 unscorable) | 126 | 163 | **0** |
| the board graded **5** of 144 drivers (contention) | 5 | 284 | **0** |
| the board graded exactly **1** driver | 1 | 288 | **0** |
| the oracle failed on **every** driver | 0 | 289 | **0** |
| shipped **tripled** overnight, board unchanged | 126 | 774 | **0** |

## 3. ⭐ THE REACHABLE HARM IS THE SECOND LINE, NOT THE FOURTH

`libmods = real_shipped − TOTAL` **defines** whatever the board did not grade as a library module.
`scorecard_snobol4.sh` carries a documented concurrent-board guard that reduces `TOTAL`, and the only floor
beneath is `SCORED >= 1`. So **a partial board silently reclassifies real, ungraded drivers as
ungradable-by-design library modules** — row 2 of the table: 163 ungradable becomes 284, and the inventory
still reports the lockdown met. ⛔ This is the *"never graded"* defect Lon's order exists to end, wearing an
inventory's clothes: not a wrong number, a number that cannot be wrong, printing the same string when the
work is finished and when it was never started.

## 4. ⛔ THE CEO'S ATTRIBUTION WAS OFF BY ONE RUNNER — CONFIRMED BY EXECUTION, WHICH IS WHY IT WAS ASKED FOR

CEO-307 (3) says *"the gimpel runner's error-number arm"*. **The gimpel runner has no error-number arm.** It
grades through `scorecard_snobol4.sh`'s `grade()`, which is `cmp -s` against the `.ref` pin and then against
the live oracle — full stream equality, nothing narrower anywhere in the path. So gimpel's `graded_narrow=0`
is a fact about the code, not a default.

**The arm is the SNOFLAKE runner's** (`test_snoflake_suite.sh:133 oracle_equal`), deliberate and documented:
error *text* cannot match byte-for-byte across implementations, so errors compare by number. Exercised
directly, with two controls that prove it can still distinguish:

| streams compared | verdict |
|---|---|
| ours: `ERROR 067` twice at line 0 statement 0 · oracle: three lines of real output, then `ERROR 067` once at line 20 statement 5 | **EQUAL** |
| same shapes, error numbers differ (067 vs 042) | not equal ✓ |
| no error on either side, different text | not equal ✓ |

⭐ **Both facts are true and they belong to two different files.** `snoflake_suite/topological-sort.sno` is
graded by the *snoflake* runner over `gimpel/TSORT.INC` — hence "gimpel's topological-sort", scored on one
integer, by a runner whose name does not contain the word gimpel. Two runners, two comparisons, one package
name in the sentence.

## 5. THE CURE — STOP HAVING A FORMULA HERE

`lib_inventory.sh` (hq_T) already carries the sum check, the closed reason vocabulary, and the arm that
refuses an UNGRADABLE naming our own compiler. The runner is wired to it; the four lines are gone. **Never a
second copy of the arithmetic.**

Wiring alone turned the silent zero into a loud, named debt:
`⛔ INVENTORY REFUSES(2): ... = 126, but shipped=289 (delta 163)`. That refusal is rc=2 on the **inventory
only** — the board line and the gate verdict are untouched, so a bookkeeping refusal can never turn a real
measurement red.

Then the debt was paid rather than filed: `corpus/packages/snobol4/gimpel/UNGRADABLE.tsv`, **163 rows, each
with the oracle's own reason**, measured one program at a time — 145 library modules (`CONTAINER_OR_LIBRARY`;
no main program, no `END`, the package's own README states the two kinds) and 18 drivers (`ORACLE_REFUSES`)
whose reasons are the oracle's actual refusals: `ERROR 042` ×5, `116` ×5, `285` ×3, `248` ×2, `156` ×2, `041`
×1. The three `285`s are the package's own gap — it ships drivers whose include chains need `stringout.sno`,
`resolution.sno` and `system.inc`, which exist nowhere in corpus; the ruling says so, so it is disputable the
moment someone vendors them. The five `116`s are the SNOBOL4+ dialect trap the package README already names
(filename is INPUT's **fourth** argument there, **third** in Catspaw SPITBOL).

**After:** `PACKAGE_INVENTORY package=gimpel shipped=289 graded=126 ungraded=0 ungradable=163
graded_stream=126 graded_narrow=0`, rc=0 — and now `ungraded=0` is a measurement rather than an identity.

## 5b. ⚠️ ONE OF MY OWN 163 ROWS MAY BE MISCLASSED, BY A RULING THAT LANDED WHILE I WAS WRITING THE FILE

`46c86b274` (hq_T, same day) named the test for admitting an UNGRADABLE class: **could this ruling be
overturned for the whole class at once?** — `ORACLE_REFUSES` is for rulings revisitable only one program at a
time. My three `ERROR 285` rows (FRSORT, TIMEGC, TIMER) fail that test in the direction of being *too*
grabbable: one person vendoring `stringout.sno`, `resolution.sno` and `system.inc` moves all three together,
which is the handle hq_T's test is looking for. They may also not belong in UNGRADABLE at all — if those
sources are obtainable upstream, this is work OWED, not a ruling.

⛔ **I did not measure that, and it decides the classification.** I established only that the three files exist
nowhere in `corpus`; whether Gimpel ever shipped them is a different question I did not ask. Asked hq_T, who
owns the vocabulary, rather than reclassifying under a ruling I would be interpreting for them or leaving it
silent. The rows carry *"Disputable the moment the missing source is vendored"* in their reason meanwhile, so
the ruling is reviewable on its face. The other 15 `ORACLE_REFUSES` rows are one-at-a-time by construction and
are unaffected.

## 5c. ✅ RULED WITHIN THE HOUR — THE THREE ARE OWED, NOT UNGRADABLE (hq_T, SCRIP `58289d4cc`)

**UNGRADED, class `NEEDS_VENDORED_SOURCE`.** Moved; `corpus 48bb77723`. gimpel now reads **`ungraded=3
ungradable=160`**, and its lockdown criterion is no longer met — ⭐ **which is the point, not a regression:
three programs that were invisible now have an owner.** hq_T said the line would go red *before* seeing it.

⭐ **THE TIE-BREAK IS THE GENERAL RULE AND IT IS WORTH MORE THAN THIS ROW: when the bucket turns on a fact
nobody has measured, the answer is UNGRADED — because the two errors are not symmetric.** A wrong
UNGRADABLE removes a program from the debt *permanently and silently* (nobody re-reads a closed ruling); a
wrong UNGRADED only looks like unfinished work, which is what it will look like anyway until someone
measures. One failure mode hides work forever, the other costs a row that stays open. So the direction that
needs justifying is always ungraded → ungradable, never the reverse.

⚠️ **And hq_T corrected their own ruling rather than mine:** *"could this be overturned for the whole class
at once"* decides whether a class **deserves its own name** once you already know the bucket — it does not
decide **which bucket**. Necessary, not sufficient. The gap surfaced from applying the rule honestly to a
case it did not cover.

⛔ **The unmeasured question is still unmeasured and is now written into the rows as the whole of what is
owed:** did the Gimpel library ever ship `stringout.sno`, `resolution.sno`, `system.inc`? Measuring it can
only move a row *from* ungraded *to* ungradable, never back, so it blocks nothing.

## 6. THE NEW ARM CAN FAIL — PROVEN THREE WAYS, NOT ASSERTED

On a scratch copy of the package, baseline green, then each mutation alone:

| mutation | result |
|---|---|
| one ungradable row deleted | ⛔ REFUSES(2) `delta 1` |
| one reason column emptied | ⛔ REFUSES(2) `expected name<TAB>CLASS<TAB>reason` |
| one reason rewritten to blame our own compiler | ⛔ REFUSES(2) `UNGRADABLE is a statement about the ORACLE, never about us` |

## 7. FOR THE NEXT LANE — THE SHAPE, NOT THE INSTANCE

⭐ **A bucket computed by subtracting the other buckets from the total cannot disagree with them.** It is not
a check; it is a restatement, and it reads exactly like a check. The tell is that the residual bucket is the
one the criterion is written against. Three other SNOBOL4 package runners are still unwired and carry their
own arithmetic — `test_snoflake_suite.sh`, `test_snobol4_aisnobol_suite.sh`, `test_snobol4_dotnet_suite.sh`
(census by execution, 2026-09-06: wired = arizona, jcon, csnobol4; unwired = everything else).

⚠️ **Not claimed:** that any lane's percent was actually misreported by this. The harm is demonstrated as
reachable and the mechanism is proven; whether a partial gimpel board was ever published under it, I did not
measure and do not assert.
