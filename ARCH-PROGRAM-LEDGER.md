# ⛔⭐⭐⭐ ARCH-PROGRAM-LEDGER — THE ACCOUNTING FOR EVERY SOURCE PROGRAM

**Opened 2026-09-11 16:2x CDT by the ceo on Lon's direct in-chat order, verbatim: *"Fix the accounting of every single source program we are measuring for completeness, correctness, and for speed."*** (CEO-566). It follows the same sitting's exchange in which Lon asked *"Do you have an accounting for every single Icon, SNOBOL4, and Prolog program with their feature sets? We did that for some. Check to see if for all."* — and the measured answer was **no**: the accounting covers the master suites and stops at the package boundary, which is where most programs live.

⛔ This page is SOVEREIGN for the ledger's shape. `RULES.md` carries the one-line FACT RULE; `SCORE.md` carries the numbers; this page says what a row means and what it may not say.

## THE LAW — three axes, one row per program, and UNKNOWN is a value

**Every source program in the corpus carries exactly one ledger row with three independent axes.** A program is accounted only when all three are stated. The axes do not substitute for one another: a program can be fast and wrong, or correct and unmeasured for speed, and a ledger that lets one axis stand in for another is how a suite reads green while a third of it is invisible.

| axis | question it answers | allowed values |
|---|---|---|
| **COMPLETENESS** | which language features does this program exercise? | a feature vector over the language's declared feature set · `NONE` (measured, exercises no declared feature) · `UNKNOWN` (never derived) |
| **CORRECTNESS** | does it produce the oracle's output? | `PASS` · `FAIL` · `OUTSIDE-BASELINE` (the one oracle refuses it — with the measurement that put it there) · `UNGRADABLE` (no oracle output obtainable — with the reason) · `UNGRADED` (gradable, nobody graded it) |
| **SPEED** | how fast is it against the rival engines? | a multiple on the faster axis per rival (`2.00x`) · `UNPROVEN` (an angle could not measure it) · `NOT-A-BENCHMARK` (declared: deterministic sub-second fixture) · `UNKNOWN` |

⛔⭐ **`UNKNOWN` IS NOT `ZERO` AND IS NOT `NONE`.** The defect this page exists to cure is the third kind of silence: gimpel printed `109/116` while 28 programs sat in neither the numerator nor its own TSV, `swi_tests` ships 251 programs against a board that reads `11/118`, and the Prolog benchmark TSV fell from 22 kernels to 8 without one instrument noticing. In each case a real population was invisible because nothing required it to be named. **A count is honest only when PASS + FAIL + OUTSIDE + UNGRADABLE + UNGRADED equals the population the tree actually ships** (the sixteenth instrument law, applied to programs instead of checks).

⭐ **A WRONG EXCLUSION COSTS MORE THAN A WRONG CURE**, because a red stays visible and an excluded name cannot be red (hq_V, standing practice since 2026-09-10). Any name entering `OUTSIDE-BASELINE` or `UNGRADABLE` carries the measurement that put it there, never just the name.

## THE IDENTITY — what a row is about

A program is one of exactly two things, and the ledger holds both without merging them:

1. **A FILE** — `corpus/<tree>/<lang>/…/<name>.<ext>`, identified by repo-relative path.
2. **A MASTER ENTRY** — a named entry inside a `tests/<lang>/ALL.<ext>` container, identified by its `entry` name in `ALL.csv`. ⛔ A master file is a CONTAINER, never a program; its entries are the programs.

A file absorbed into a master keeps BOTH rows while the file survives on disk, and the ledger states the absorption, because the two are graded by different runners and drift apart in exactly the way the Icon rung board did (CEO-552).

## THE INSTRUMENT — derived live, never hand-maintained

`scripts/util_program_ledger.py` emits the ledger by GLOBBING the tree and joining live sources; it computes nothing itself and grades nothing itself (`util_score_row.py`'s discipline). Sources: `ALL.csv` feature columns · each package's `UNGRADED.tsv` / `UNGRADABLE.tsv` / `OUTSIDE_*_BASELINE.tsv` / `ORACLE_ACCEPTANCE.tsv` · the progress DB's latest reading per program×mode · the per-language triangulation TSVs.

⛔ **A HAND-MAINTAINED LIST IS THE DEFECT, NOT THE CURE** (`test_prolog_gnu_suite.sh`'s own header states the rule it was built on: *"a blanket exclusion and a named list give the same number today and different numbers forever after"*). The ledger self-corrects on every run; `one_runner_gate_arms.txt` is the counter-example — a 16-line hand list that silently missed `test_gate_harness_refusal_is_rc2.sh` and stopped `make test` for every non-coo seat.

⛔ The ledger REFUSES (rc=2) rather than printing a partial table when a source it joins is missing, and it prints its own denominator on every run. A ledger that cannot see a package prints that it cannot see it.

## THE MEASURED STATE AT OPENING (ceo, 2026-09-11 16:1x CDT, SCRIP `aaae4f979` · corpus `e662a8b56`)

**THE POPULATION — 2,801 source files + 3,580 master entries across the three live languages:**

| language | tests | packages | benchmarks | demos | programs | include | files | master entries |
|---|---|---|---|---|---|---|---|---|
| Icon | 199 | 1090 | 37 | 9 | 1 | — | **1336** | 957 |
| SNOBOL4 | 153 | 630 | 38 | 26 | 99 | 4 | **950** | 1930 |
| Prolog | 54 | 315 | 141 | 4 | 1 | — | **515** | 693 |

**AXIS 1 — COMPLETENESS.** Feature vectors exist for the 3,580 master entries and for NOTHING ELSE. Within them: Icon 957 rows over 61 features, **0 blank**; SNOBOL4 1930 over 39, **264 blank (14%)**; Prolog 693 over 39, **94 blank (14%)** plus a dead `assert` column no row ever sets. **The 1,735 package programs carry no feature vector at all.** ⛔ A feature vector is today a property of the MASTER SUITE, not of the language: *"which programs exercise `OPSYN`"* is unanswerable outside `tests/`, and the 100%-of-the-industry-standard-language claim is asserted against the curated entries rather than the real-world corpus.

**AXIS 2 — CORRECTNESS.** Nine of fourteen package directories carry inventories. **Four carry none:** `swi_tests` (251 programs, against a board reading 11/118 — 133 programs outside even the failing denominator), `inriasuite`, `jcon-compiler` (20), `jcon-ref` (1).

**AXIS 3 — SPEED.** Only the `benchmarks/` trees are measured at all. The Prolog cell is the worked example of the failure mode: its triangulation went **22 kernels / 12 AGREE / 8 DISAGREE (09-02) → 8 kernels / 32 UNPROVEN (09-04, twice)**, the surviving 8 being alphabetically the first 8 of 21 — a TRUNCATED run, not a chosen subset — and it destroyed 12 agreements and 8 real divergences on the way. Nothing detected it, because no gate reads a triangulation TSV back.

## WHAT MAY NOT BE SAID

- ⛔ A suite may not print a pass count whose denominator excludes programs it ships without naming them in the same breath.
- ⛔ A benchmark grid may not shrink its kernel population silently; the runner REFUSES when the measured kernel count is below the globbed population and names the missing kernels.
- ⛔ `UNGRADED` may not be reported as `0` when it has never been derived; the value is `UNKNOWN` and it is printed as `UNKNOWN`.
- ⛔ No document quotes a ledger number without its tree label (SCRIP and corpus hashes), per the watermark law.
