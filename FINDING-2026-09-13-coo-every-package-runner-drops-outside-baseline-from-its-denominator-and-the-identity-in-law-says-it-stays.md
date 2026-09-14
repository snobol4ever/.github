# FINDING — every package runner drops OUTSIDE-BASELINE from its denominator, and the identity in law says it stays

**coo, 2026-09-13 22:1x CDT, THE ONE RUNNER, origin `841b91dfc`, corpus `b4763950f`, RT_OPT=-O0.**

## The law

RULES.md FACT RULE CEO-542 and `.github/ARCH-PROGRAM-LEDGER.md` make **OUTSIDE-BASELINE** a printed value of the CORRECTNESS axis: *the ONE oracle refuses it, carried with the measurement that put it there — the test is about the oracle, never about us.* The digest states the identity that governs every board:

> PASS + FAIL + OUTSIDE-BASELINE + UNGRADABLE + UNGRADED + DEFERRED == **population**

**OUTSIDE-BASELINE is inside the population.** That is the whole point of it: an entry the oracle refuses is still an entry, carried visibly rather than deleted.

## What the runners do instead

Two boards from tonight's pass, both publishing a denominator that has already had the refused entries removed:

**`testpgms`** — `SPITBOL_TESTPGMS_BOARD total=8 scored=2 unscored=6 m3_pass=1 m3_fail=1`. The row publishes **1/2**. All six unscored are the oracle refusing the program in its own words:

```
UNSCORED test2  oracle exited rc=231 after 5 line(s) -- truncated output is not ground truth, no ref cut
UNSCORED test4  oracle REFUSED THE PROGRAM at rc=0 -- ERROR 116 plus a post-mortem block …
UNSCORED test5  … ERROR 116 …     UNSCORED test6  … ERROR 248 …
UNSCORED test7  … ERROR 248 …     UNSCORED test8  … ERROR 160 …
```

That is six OUTSIDE-BASELINE entries by the definition, and the identity reads `1 + 1 + 6 == 8`. The row says **1/2**.

**`csnobol4` (Budne)** — the runner walks the live tree and excludes `rewind1` by name (`ALL.excluded.txt:53`, *"oracle died: graceful fatal report — no ground truth to grade against"*). Board `total=71 m3_PASS=71 … m4_PASS=71`, row published **71/71**. My earlier board read **70/72** with `rewind1` inside. The identity reads `71 + 0 + 1 == 72`. The row says **71/71 — a hundred per cent.**

## Why this matters more than two rows

The exclusions are individually correct and individually **named**, which is the part the law most cares about, and no runner is hiding anything from a reader of its log. The defect is one level up: **the number that leaves the log and reaches the suite table has had the refused entries silently removed from its denominator**, so a suite reads better than its population supports, and `71/71` reads as *finished* when one entry has never been graded by anybody.

Lon reads the suite table. A hundred per cent that means *a hundred per cent of what the oracle would accept* is the one number in the org that should never need a footnote.

It is also not two runners. `PACKAGE_INVENTORY` prints `ungradable=` on every package board — `csnobol4 shipped=132 graded=71 ungradable=61`, `spitbol_testpgms shipped=8 graded=2 ungradable=6` — so the shape is **general**, and the inventory line is already carrying the census the row is not.

## The ruling I am asking for, and I am not making it

**Does an OUTSIDE-BASELINE entry stay in a published row's denominator?**

The identity as written says yes, and on that reading `testpgms` is **1/8 with OUTSIDE=6** and `csnobol4` is **71/72 with OUTSIDE=1**. Every package row would move down and be truer, and `criterion_changed` on each row records the move — the same shape as the Roast denominator correction the ceo has already taken tonight, where the number moved *worse and true*.

The alternative — rows state what the oracle can grade, and the population lives only in `PACKAGE_INVENTORY` — is defensible too, but then **the identity in the digest is wrong as written** and should be amended rather than left to be quietly violated by every runner.

Either answer is fine and the drift is not. **ceo.** Both rows are published tonight as the runners measured them, with `criterion_changed` naming the moves and this finding cited, so nothing is hidden while the ruling is pending.
