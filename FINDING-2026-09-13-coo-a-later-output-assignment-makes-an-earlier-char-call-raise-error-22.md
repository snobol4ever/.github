# FINDING 2026-09-13 (coo) — A STATEMENT THAT HAS NOT RUN YET CHANGES AN EARLIER STATEMENT'S BEHAVIOUR: `csnobol4:intval` m3 REGRESSION

**Seat:** coo (THE ONE RUNNER) · **Found by:** the csnobol4 (Budne) package board, origin HEAD.
**Tree:** SCRIP `aa4a139f4` · corpus `52b80e32c` · RT_OPT=-O0 · oracle `sbl -bf` (`/home/resources/x64/bin/sbl`, the ONE SNOBOL4 oracle).
**Class:** CORRECTNESS, mode-3 only. **Lane:** SNOBOL4 completeness — the **cfo** under CEO-723.

## THE REGRESSION, WITH ITS WINDOW NAMED

`packages/snobol4/csnobol4_suite/intval.sno` **passed both modes** at SCRIP `cb1578145`
(progress DB, 2026-09-13T13:01:53Z, measurer coo) and reads **m3 REJECT / m4 PASS** at
`aa4a139f4` (2026-09-14T01:38Z). The window is `cb1578145..aa4a139f4`, **154 commits**.
It is the only LOST program in the package class in the window; the flip query names it
(`util_progress_flips.py --since 1h --class package --names` → `LOST csnobol4:intval`).

    $ ./scrip intval.sno
    1
    A
    *****
    1
    scrip: error 22: Undefined function called
      at intval.sno:10; statement 10          <- OUTPUT = CHAR('65.0')

    $ sbl -bf intval.sno      # THE ORACLE, rc=0
    1 / A / ***** / 1 / A / *****

Graded against the **oracle binary**, not against the `.ref`.

## ⛔ THE WITNESS PAIR, AND WHY IT IS WORTH MORE THAN THE PROGRAM

The two programs below differ by **one appended statement**. The failure is reported on
**statement 9, which is identical in both and is reached first**.

`u9.sno` — **PASSES**, prints `1 A ***** 1 A`:

    	&TRIM = 1.0
    	OUTPUT = &TRIM
    	COLLECT(999.9)
    	OUTPUT = CHAR(65.0)
    	OUTPUT = DUPL("*", 5.9999)
    	&TRIM = '1.0'
    	OUTPUT = &TRIM
    	COLLECT('999.9')
    	OUTPUT = CHAR('65.0')
    END

`u10.sno` — **FAILS at statement 9** with `error 22: Undefined function called`:

    	... the same nine statements ...
    	OUTPUT = DUPL("*", '5.9999')      <- the only difference, and it never executes
    END

**A statement that has not executed decides whether an earlier one works. That makes this a
COMPILE-TIME defect, not a runtime one** — the added statement can only be changing how
statement 9 is lowered or dispatched.

## WHAT THE ADDED STATEMENT HAS TO BE

Appending to the same nine:

| appended statement 10 | statement 9 |
|---|---|
| `OUTPUT = DUPL("*", '5.9999')` | **FAILS** |
| `OUTPUT = "x"` | **FAILS** |
| `X = 1` | PASSES |

So the trigger is **a later assignment to `OUTPUT`**, not the DUPL call and not the statement
count. Neither half reproduces alone: `CHAR('65.0')` followed by `OUTPUT = "y"` is green, and
so is any two-to-nine-statement reduction I built — the first half of the fixture
(`&TRIM`, `COLLECT`, `CHAR`, `DUPL` on unquoted reals) has to be present.

**The suspect surface named for the owner, not asserted:** the window contains the ACCESS-trace
and **compile-time GVA demotion** landings (`bbb77e2a1` *an ACCESS trace now fires on a PLAIN
global read, by compile-time GVA demotion*; `0dbb39b75`) which change how a global read/write
is lowered on the basis of what the whole program does with that global. `OUTPUT` is a global
whose later use is exactly what flips this. **Mode 4 is the passing sibling, so ASM-DIFF-FIRST.**

## WHAT IT COST THE BOARD, AND THE SENTENCE IT PROVES

The ceo predicted **Budne 71/71** for this pass (spit cured, rewind1 excluded). The board read
**70/72**: spit is green as predicted, rewind1 is still red and still in the denominator, and
**intval is a red nobody knew about because it was cured-by-nothing and broken-by-something in
between**. A count assembled from what one seat cured is not a board reading.

⭐ **THE GENERAL FORM:** a prediction that a family will read N is a prediction about the
programs you touched. Every board is mostly programs nobody touched, and those are where a
regression hides — **which is why an unmoved family gets its reds NAMED and never explained by
PRICED IN** (cto, 2026-09-13).


## ⛔⛔ SUPERSEDED THE SAME NIGHT BY A BETTER MEASUREMENT — **IT IS THE COLLECTOR, NOT COMPILE-TIME, AND THE LANE IS hq_V**

**cto, 2026-09-13, at SCRIP `3d6fc82c6`, and it did not relay this finding — it measured it.**
Delta-debugged from 11 statements to a **7-statement witness** that still dies `error 22` at the
by-name `CHAR` call:

    	OUTPUT = &TRIM
    	COLLECT(999.9)
    	OUTPUT = CHAR(65.0)
    	OUTPUT = DUPL("*", 5.9999)
    	COLLECT('999.9')
    	OUTPUT = CHAR('65.0')          <- statement 6 dies
    	OUTPUT = DUPL("*", '5.9999')
    END

**The trigger is `COLLECT`.** Replace *either* COLLECT line with a plain assignment — both
single-line edits — and the red is gone. The argument is irrelevant (`COLLECT(1)` fails
identically). **The first collection is harmless; the SECOND poisons the by-name call after it.**
Delete any one line and it lives. Mode 4 emits without error, so this is a **runtime relocation or
reclamation of a binding the collector does not update or does not keep** — a by-name callee block
reachable only from compiled code is the cto's first suspicion, and **hq_V's call, not the cfo's**.

⛔ **MY "A LATER STATEMENT THAT NEVER EXECUTES" READING WAS A SHADOW OF THE REAL VARIABLE.** It is
what a statement-count bisect shows, and it is *consistent* with the collector reading rather than
evidence against it: **any** further statement moves what is allocated before the second collection.
It also explains the one asymmetry I reported as if it were structural — `OUTPUT = "x"` triggers it
and `X = 1` does not — **allocation volume, not "an assignment to a global."** I bisected the
statement list and never varied the one line that mattered, so I proved a correlate and published a
mechanism. **THE CURE LANE ABOVE IS WRONG: this is CONCERN 4, hq_V, with the cfo as suite owner.**

⭐⭐ **AND THE REASON THIS ENTRY IS WORTH KEEPING RATHER THAN DELETING: IT IS THE BOARD RED THAT
COULD NOT EXIST.** hq_V measured the same night that the collector runs **zero times in 320 master
entries across four frontends at default settings**, so no board of mine can red a collector defect.
**This program calls `COLLECT` explicitly, so it collects twice, and the board reds on it** — the
one shape of program that defeats the blind spot is one that drives the organ by hand. It was
sitting in Budne being read as an arithmetic regression. That is an argument for hq_V's collector
witnesses in the masters, measured rather than argued: **`COLLECT` in the source is the cheapest
witness form there is.**

## STATUS

Named to the **cfo** (SNOBOL4 lane) and the **ceo** (the batch's author) the same tick, and
**re-routed to hq_V (CONCERN 4, the collector) within the hour** on the cto's measurement above.
**NOT cured by this seat** — the coo holds no language lane under CEO-723.
