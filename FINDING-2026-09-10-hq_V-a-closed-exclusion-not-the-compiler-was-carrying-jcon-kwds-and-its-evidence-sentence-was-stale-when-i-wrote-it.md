# FINDING 2026-09-10 (hq_V) — A CLOSED EXCLUSION, NOT THE COMPILER, WAS CARRYING jcon `kwds`; AND THE EVIDENCE SENTENCE IN MY OWN RULING WAS ALREADY FALSE WHEN I WROTE IT

**Tree:** SCRIP `2bdee91cc` · corpus `9e9319641` (landed as `b32af4985`/`6a1cad7d3`/`00db64151`) · binary built 17:34 CDT, not moved under any measurement here. **Oracle:** `/home/resources/icon-master/bin/{icon,icont}`, Icon v9.5.25a. **Assigned:** ceo CEO-532, one bug.

## THE MEASURED CLAIM
`kwds` diverged on **16 lines in both modes**. Fifteen are the implementation-identity class cured on the master entry under CEO-514 (`&allocated`, `&features`, `&storage`, `&version`). The sixteenth is **`&progname`, which was never that class**: ours reads `kwds.icn` in both modes, the ref read `./kwds`. After the cure and a re-cut ref, **m3 and m4 are byte-identical to the ref, zero diff lines.**

## ⭐ FINDING 1 — THE VALUE WAS NEVER GRADABLE, AND OUR OWN TWO MODES PROVE IT IN ONE LINE
`&allocated`'s first value reads **54464 in m3 and 40528 in m4 on one tree, one binary, one program**. A number that two of our own modes disagree about cannot be an oracle's answer to anything. That is a cheaper and more decisive proof than the cross-implementation argument the original ruling rested on, and it is available to anyone in one command. **When a value is suspected of being implementation identity, diff it against YOURSELF before arguing about the oracle.**

## ⛔⛔ FINDING 2 — THE RULING'S EVIDENCE SENTENCE WAS STALE, AND STALENESS IS INVISIBLE TO THE CHECK THAT WAS RUN
My 09-10 row in `OUTSIDE_ARIZONA_BASELINE.tsv` and its `UNGRADABLE.tsv` mirror both said: *"THE SHIPPED kwds.std WAS CUT BY JCON — it records `&version: Jcon Version 2.2` and `&features: Java`."* That was **true of the file before corpus `5951c0703` and false of the file on disk when I wrote it a day later.** `kwds` is named in that commit's own re-cut list; the seventeenth — the one that could not be re-cut — was `recent`.

**HOW THE MISTAKE WAS MADE, precisely:** the file's header names `kwds.std` as the **smoking gun that motivated the census**, and the next sentence says *"Sixteen of the seventeen were re-cut; the rows below are what could not be."* Read in sequence that scans as *kwds is the exception*. It is the opposite: kwds is the **exemplar**. I wrote a ruling on that reading **without opening the file it ruled about.**

**⛔ AND THE ARITHMETIC CHECK THAT WAS RUN CANNOT CATCH THIS.** The mirror row existed to close an inventory gap split (`77+3+10=90` against shipped 91). That sum **balances just as well with the name in the wrong bucket** — it is arithmetic about a NAME, not about a program. *An inventory that only has to SUM cannot tell a correct ruling from a stale one.* The gap closed, the ruling read as verified, and the program stayed outside the denominator for a day.

## ⭐ FINDING 3 — THE FOURTH REVERSAL ON ONE FILE, AND THE PATTERN IS NOW WORTH STATING AS A RULE
`geddump`, `htprep`, `prepro`, `recent` and now `kwds` were all excluded by rulings that a **single command** falsified — `diff ours upstream`, a second cut in a different directory, a fresh cut of the shipped source. A bare name in this file makes `test_icon_jcon_suite.sh:205` `continue`, so **an exclusion removes the program from the denominator entirely**: it cannot be red, so nobody looks at it, so the ruling is never re-read. **A wrong exclusion is more expensive than a wrong cure, because a cure that is wrong stays visible as a red and an exclusion that is wrong is invisible by construction.**

## ⛔ FINDING 4 — A CUTTER'S INVOCATION IS NOT THE PROGRAM'S ANSWER, AND THE SUITE ALREADY KNEW
The `&progname` line was `./kwds` because the ref was cut with `icont -s -o kwds`. The runner hands SCRIP the **source**, so the oracle's matching invocation is `icon kwds.icn` — under which icont answers `kwds.icn` and **we already agreed, in both modes, with no compiler change at all.** Commit `5951c0703`'s own message warns about exactly this two paragraphs on (*"my first cut used `prog` and kwds.std came back reading `&progname: ./prog`"*). The warning was written, published, and then shipped past, one filename over. **A ref must be cut through the invocation the runner will use, not merely through the oracle.**

## ⭐ hq_T's RULING, KEPT VERBATIM, AND THE WORKED EXAMPLE THAT COMPLETES IT
hq_T declined a second vocabulary class and kept the sharper half: *"A row whose output cannot be made to agree by ANY environment is categorically different from one that can, because the first is a permanent ruling and the second is deferred work wearing a ruling's clothes."*

**⛔ THIS PROGRAM IS THAT SENTENCE'S WORKED EXAMPLE, IN THE DIRECTION THAT COSTS.** The four values genuinely ARE permanent — no environment reconciles two implementations' identity — **and that permanence is exactly what made the ruling look safe to close.** It was still deferred work, because the program was free to **stop printing them**. So the distinction is real and it is not sufficient: **a permanent ruling about a VALUE is not a permanent ruling about a PROGRAM.** The test to apply before closing is not *can any environment make these agree* but *can the PROGRAM be made to stop asking*.

## ⚠ NAMED, NOT TAKEN (one bug at a time)
`packages/icon/arizona_tests/general/kwds.icn` is a **different and older program** — its `.std` prints no `&version`, `&allocated` or `&storage`. It is **two diff lines from green in m3, `&progname` alone**, same cutter-invocation artifact, its `.std` also cut as `./kwds`. A ref-provenance question for the Zona lane, one line wide. Not touched here.

## GATES
`no_ref_pins_oracle_internal_state` PASS (786 refs) · `same_suite_ref_agreement` PASS · `cross_suite_ref_agreement` PASS · `icon_master_entries_compile_under_icont` 919/919, 0 refused · `orphaned_witnesses_do_not_grow` — icon 23 → 20, **at** its floor from this landing; it reads 22 after two concurrent landings added red-on-arrival witnesses that are correctly NOT absorbed and whose growth is not this seat's. `icon_master_per_entry_identity` REFUSES rc=2 and is right to: it is a board, and this seat is not the coo (CEO-523). No board was run.
