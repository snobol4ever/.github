# FINDING — every Icon derivative inherited the Arizona suite and added only tests for its own extensions

**ceo, 2026-09-11, on Lon's question: *"How many Icon test suites are we missing? Did we find them all? Arizona Icon, JCON, Unicon. What else? Where else?"*** Answer: **we have them all, and the reason is structural, not luck.**

## The census

| source | tests | new to us | gradeable by our oracle |
|---|---|---|---|
| **Arizona Icon** (`icon-master`) | 99 `general` + 10 `bench` + 1 `special` | — | ✅ **fully mined** — all 99 in `arizona_tests`, all 10 bench programs present elsewhere in the corpus |
| **IPL** | 852 programs | — | ✅ vendored |
| **Jcon** | 92 | — | ✅ vendored |
| **Unicon** | 51 general + 26 bench | 5 general, 20 bench | ⛔ 45 of 51 general are the **Arizona tests we already hold**; of 26 bench, `icont` REJECTS 16 as Unicon-only and 5 were already ours — **5 taken** |
| **Object Icon** (`chemoelectric/objecticon`) | 132 `.icn` + 117 `.std` | 33 by name | ⛔ **ALL 33 REJECTED BY `icont`** — classes, packages (`packscope*`), methods (`methp`), threads (`mt_*`), UCS csets, protected/streams. **Zero taken.** |
| **Goaldi** (`proebsting/goaldi`) | 66 `.gd` + 65 `.std` | — | ⛔ **zero `.icn` in the repo.** Goaldi is a different language; its tests carry `#SRC: icon/arith.icn` headers showing they were TRANSLATED from Icon originals, but only the translations ship. **Zero taken.** |

## ⭐ THE STRUCTURAL REASON, and it is the finding

**Every Icon derivative forked the Arizona test suite and then added tests only for the features that make it not-Icon.** Unicon added classes, patterns, threads, POSIX. Object Icon added packages, classes, UCS. Goaldi changed the syntax outright. So a derivative's *shared* tests are duplicates of ours by construction, and its *unique* tests are by definition outside the Icon baseline — which is exactly what the oracle said when asked: 16 of 26 Unicon benchmarks and **33 of 33** Object Icon uniques refused by `icont`.

⛔ **THE CONSEQUENCE FOR THE DENOMINATOR: the Arizona suite IS the Icon test corpus.** There is no large untapped population waiting to be found, the way `logtalk_iso`'s 3,268 cases were waiting for Prolog. Icon's denominator is already honest and already ours. That is why Icon reads 1,079/1,085 while Prolog fell from 83% to 21% the same afternoon: the Prolog number was measured against a seventh of its real population, and the Icon number was not.

⭐ **AND THE METHOD IS THE TRANSFERABLE PART: ask the oracle, never the name.** Vendoring by basename would have taken 66 duplicates and 49 ungradeable programs across the two forks. Every candidate was compiled with `/home/resources/icon-master/bin/icont` before it was taken; that single filter did all the work.

## What remains untapped, and it is small and low-grade

- **Rosetta Code** Icon/Unicon solutions — community-contributed, **no expected-output files**, so each would need a ref cut and reviewed by hand. Volume without a denominator.
- **Icon Analyst / Icon Newsletter** program archives (cs.arizona.edu) — historical, same ref problem.

Neither is worth a row before the announce; both are named here so the next person asking this question does not re-run the search.
