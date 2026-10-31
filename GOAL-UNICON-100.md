# GOAL-UNICON-100 — SCRIP Icon is the Unicon superset; Unicon's own tests at 100 percent

**Opened 2026-10-31 by the ceo on Lon's word** (in-chat to the ceo, verbatim: *"Let's extend Icon to Unicon with a command-line switch, or if it is a super set then a switch is not needed."* · *"Let's keep HQ-ICON on performance and let the /home/claude_unicon take UNICON."*; rulings CEO-2072 and CEO-2074). The lane is hq_unicon's; hq_icon keeps the Icon suites (all six at 100 on 2026-10-31) and Icon's speed rows (CEO-2035).

## ⛔ THE RULE

- **Unicon is the superset, so there is no switch** (RULES.md ONE ORACLE, ONE FEATURE SET; the Prolog precedent CEO-391 and ARCH-PROLOG-DIALECTS.md). SCRIP's one Icon front end (`src/parsers/icon/`, `src/lower/lower_icon.c`) accepts every Icon program and every Unicon program. Where the two conflict (Unicon reserves `class`, `method`, `package`, `import`, `initially` and a few more that Icon allows as identifiers), the program's OWN markers decide: a `class`, `package`, `import` or `method` header marks it Unicon; a program without one is Icon and answers as Arizona Icon does. The exact marker set is the cto's design (ARCH-UNICON.md), measured against the IPL (89 files carry one of those words somewhere) and Unicon's own tests.
- **The oracle is `unicon`**, built from `/home/resources/unicon` (the git drop at d784f58, 2026-09-06) and reached only through `unicon_bin()` in `harness/scripts/lib_oracle_flags.sh`; a ref is cut from the oracle, never from a `.std` file alone and never from our output. What the oracle cannot answer is `NO_ORACLE_ANSWER` (CEO-1696). Graphics are EXCLUDED as the IPL's are (CEO-1315).
- **One front end, two seats:** hq_unicon lands Unicon's surface in the shared Icon parser, lowerer and runtime; hq_icon's suites must stay green under every landing (the Icon smoke and the IcnRungs core before every push, CEO-1928), and a landing that moves an Icon suite is reverted first and reworked. The two seats name their files to each other by bus before touching the same one.

## DEFINITION OF DONE

The suite row `unitests` (Unicon's own tests under `corpus/packages/icon/unicon_tests/`, runner `test_icon_unicon_suite.sh`) reads PASS == TOTAL with its exclusions named, on SCORE.md § THE SUITE TABLE, in both modes, with every Icon row still at 100.

## THE ROWS (the bus is the state; this list is the map)

1. `design-unicon-scrip-icon-extends-to-the-unicon-superset-with-no-switch-the-dialect-markers-the-class-and-package-model-and-the-oracle-ceo-2072` -- the cto: ARCH-UNICON.md with a DESIGN-PLAN, witnesses under `corpus/tests/icon/unicon/`, `test_design_unicon_steps.sh`.
2. `icon-unicon-the-oracle-unicon-is-built-from-home-resources-unicon-and-reached-only-through-unicon-bin-in-lib-oracle-flags-ceo-2072` -- hq_unicon: the oracle build, the accessor, the no-bare-name gate, the NO_ORACLE_ANSWER census of the 267 tests.
3. `icon-unitests-unicons-own-test-suite-is-the-package-suite-unitests-graded-against-refs-cut-from-unicon-and-its-row-reads-100-ceo-2072` -- hq_unicon, blocked on 2: the package suite, its row, then the programs to 100 in the order of the design's steps.

## THE MANUALS

`/home/resources/manuals/icon/unicon-book-*.txt` (the Unicon book by chapter), `unicon-utr*.txt` (the technical reports), `icon-book-3rd-edition.txt`, `icon-doc-*.txt`; the tests' README as `unicon-tests-README.txt`. The skill is `/icon` until a `/unicon` skill is written (the cto's, after the five of CEO-2071).

## LIVE CURSOR

- **2026-10-31 09:5x CDT (ceo, CEO-2074)** -- the seat created: `/home/claude_unicon` with SCRIP, corpus, harness and .github cloned from origin, its settings, its generated CLAUDE.md, the skills installed, the bus identity `hq_unicon`, the roster line. Rows 2 and 3 reowned from hq_icon. Lon seats the session (Sonnet 5.5 xhigh). Nothing landed yet; the oracle is not built.
