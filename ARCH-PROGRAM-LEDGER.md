# ⛔⭐⭐⭐ ARCH-PROGRAM-LEDGER — THE ACCOUNTING FOR EVERY SOURCE PROGRAM

**Opened 2026-09-11 16:2x CDT by the ceo on Lon's direct in-chat order, verbatim: *"Fix the accounting of every single source program we are measuring for completeness, correctness, and for speed."*** (CEO-566). It follows the same sitting's exchange in which Lon asked *"Do you have an accounting for every single Icon, SNOBOL4, and Prolog program with their feature sets? We did that for some. Check to see if for all."* — and the measured answer was **no**: the accounting covers the master suites and stops at the package boundary, which is where most programs live.

⛔ This page is SOVEREIGN for the ledger's shape. `RULES.md` carries the one-line FACT RULE; `SCORE.md` carries the numbers; this page says what a row means and what it may not say.

## THE LAW — three axes, one row per program, and UNKNOWN is a value

**Every source program in the corpus carries exactly one ledger row with three independent axes.** A program is accounted only when all three are stated. The axes do not substitute for one another: a program can be fast and wrong, or correct and unmeasured for speed, and a ledger that lets one axis stand in for another is how a suite reads green while a third of it is invisible.

| axis | question it answers | allowed values |
|---|---|---|
| **COMPLETENESS** | which language features does this program exercise? | a feature vector over the language's declared feature set · `NONE` (measured, exercises no declared feature) · `UNKNOWN` (never derived) |
| **CORRECTNESS** | does it produce the oracle's output? | `PASS` · `FAIL` · `OUTSIDE-BASELINE` (the one oracle refuses it — with the measurement that put it there) · `UNGRADABLE` (no oracle output obtainable — with the reason) · `UNGRADED` (gradable, nobody graded it) · `DEFERRED` (in our language by ruling, not yet implemented, deliberately not counted as a failure — with the ruling that put it there) |
| **SPEED** | how fast is it against the rival engines? | a multiple on the faster axis per rival (`2.00x`) · `UNPROVEN` (an angle could not measure it) · `NOT-A-BENCHMARK` (declared: deterministic sub-second fixture) · `UNKNOWN` |

⛔⭐ **`UNKNOWN` IS NOT `ZERO` AND IS NOT `NONE`.** The defect this page exists to cure is the third kind of silence: gimpel printed `109/116` while 28 programs sat in neither the numerator nor its own TSV, `swi_tests` ships 251 programs against a board that reads `11/118`, and the Prolog benchmark TSV fell from 22 kernels to 8 without one instrument noticing. In each case a real population was invisible because nothing required it to be named. **A count is honest only when PASS + FAIL + OUTSIDE + UNGRADABLE + UNGRADED equals the population the tree actually ships** (the sixteenth instrument law, applied to programs instead of checks).

⭐ **A WRONG EXCLUSION COSTS MORE THAN A WRONG CURE**, because a red stays visible and an excluded name cannot be red (hq_V, standing practice since 2026-09-10). Any name entering `OUTSIDE-BASELINE` or `UNGRADABLE` carries the measurement that put it there, never just the name.

### ⛔⭐ `DEFERRED` — IN SCOPE, NOT BUILT, NOT A FAILURE (Lon 2026-09-11, in-chat to ceo, verbatim: *"Do not count the FD as failures for us."*; CEO-579)

**`DEFERRED` IS NOT `OUTSIDE-BASELINE` AND THE DIFFERENCE IS THE WHOLE POINT.** `OUTSIDE-BASELINE` says *the oracle refuses this; it is not our language*. `DEFERRED` says *this IS our language, we intend to implement it, we have not, and we have decided it will not depress the score while it waits*. One is a fact about the oracle; the other is a scheduling decision by Lon. They must never be collapsed, because an `OUTSIDE` name is closed forever and a `DEFERRED` name is owed.

**CONDITIONS, all three mandatory — a `DEFERRED` row that fails any of them is a `FAIL`:**

1. **A RULING NAMES IT.** The ledger row carries the in-chat ruling verbatim, dated, with its CEO number. No seat may defer anything on its own judgement, ever.
2. **IT IS PRINTED, NEVER SUBTRACTED IN SILENCE.** A board showing `DEFERRED` prints the count and the names beside its pass line. ⛔ The denominator identity still holds: **PASS + FAIL + OUTSIDE-BASELINE + UNGRADABLE + UNGRADED + DEFERRED == the population the tree ships.** A suite that drops deferred programs out of its population entirely is lying by a different arithmetic than the one this page was written to stop.
3. **IT CARRIES THE WORK IT IS WAITING ON.** The row names the subsystem, the prerequisite, and the measured size, so a deferral can never quietly become an abandonment. ⭐ **A DEFERRED NAME IS A DEBT ON THE BOARD, NOT AN ABSENCE FROM IT.**

**THE FIRST AND ONLY `DEFERRED` POPULATION TODAY: the 30 GNU Prolog finite-domain programs** in `packages/prolog/gnu_fd`. Ruled INTO the superset by Lon (CEO-572, *"I say the FD is superset"*) and ruled NOT-A-FAILURE the same sitting (CEO-579). What they wait on, measured: GNU's own FD is `EngineFD` 4,932 + `BipsFD` 8,636 = **13,568 lines, about a quarter of their entire Prolog system**; the 30 programs need 11 constraint operators (`#<=>` alone 96 times — reification, a second layer rather than more propagators) and 14 `fd_*` builtins; and **we hold no attributed-variable/suspension substrate at all** (zero hits in `src/` for `attr_var`, `put_attr`, `when/2`, coroutining, wake), which is the prerequisite nothing else can start before.

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

## ⛔⭐⭐⭐ THE KERNEL CONVENTION — PRISTINE SOURCE, GENERATED WRAPPING, A REF FOR EVERY PROGRAM

**Lon 2026-09-11 16:3x CDT, in-chat to ceo, two statements, verbatim (CEO-567):** *"The test kernel convention we want is a source program that is the meat of the test. And all wrapping and messaging happens after that source is written prestine. The program will have a REF file."* and *"All tests will be self timing and self iteration counting using the 3-angle approach where the tests are run with a process wrapper which measures perf process data in addition to the self measured iters and time."*

**THE SHAPE — one program, one pristine source, everything else generated around it:**

1. **THE KERNEL IS THE MEAT AND NOTHING ELSE.** The source file holds the computation under test. It carries no timing calls, no iteration driver, no result-printing bolted on for a harness's benefit, and no per-engine accommodation. It is written pristine and it stays pristine.
2. **WRAPPING AND MESSAGING ARE APPLIED AFTER, BY THE HARNESS, AROUND THAT SOURCE** — the iteration driver, the self-timing hooks, the result emission. They are generated, never hand-edited into the kernel, so the kernel compared across engines is byte-identical by construction rather than by discipline.
3. **EVERY PROGRAM HAS A `.ref`.** The kernel is graded for CORRECTNESS by ref diff like every other corpus program. ⛔ A benchmark is not exempt from being right: a fast wrong answer is a defect, and a speed number taken from a program nobody diffed is a number about an unknown computation.
4. **THE WRAPPED FORM IS SELF-TIMING AND SELF-ITERATION-COUNTING.** The program reports its own iteration count and its own WORK time — the two-number basis's WORK half — from inside.
5. **IT RUNS UNDER A PROCESS WRAPPER THAT MEASURES PERF PROCESS DATA** (`tools/bench_rusage`), *in addition to* the self-measured iters and time. The wrapper's numbers and the program's own numbers are independent measurements of the same run, and disagreement between them is a finding, not a rounding question.
6. **THREE ANGLES, UNCHANGED:** fixed time, fixed iterations, process wrapper. A single-angle number is a scouting datum, never a grid.

⛔⭐ **WHY THE BAKED-IN WRAPPER IS THE DEFECT, MEASURED THIS SITTING (ceo, corpus `e662a8b56`):** `benchmarks/prolog/bench/` ships **two incompatible conventions in one directory** — 13 kernels emit a deterministic result signature and 10 call `wall_us/1` to time themselves — so a sweep of that one tree grades 13 programs and raises `existence_error(procedure, wall_us/1)` on the other 10. `benchmarks/prolog/vanroy/` bakes a frozen `main :- l__(N).` iteration count into each source, making N historical data inside the artifact being measured. Both are the same mistake: **wrapping that lives in the kernel becomes part of what you are comparing**, and it drifts per file, per engine and per calibration run until the population is no longer one population.

⛔ **REF COVERAGE AT THE RULING (ceo, `find`, 2026-09-11 16:3x CDT):** `benchmarks/prolog` **0 refs over 141 programs** (bench 23, vanroy 21, src/gnu-examplespl 22, src/swi-bench 35, src/swi-vanroy 37, root 3) · `benchmarks/icon` **0 refs over 23** · `benchmarks/snobol4` **18 refs over 23**. Only the SNOBOL4 tree has any correctness axis at all, and none of the three is complete. Every one of those programs is, today, a speed number about a computation no instrument has checked.

⭐ **THE CONVENTION UNIFIES THE THREE AXES.** The same pristine kernel carries a feature vector (COMPLETENESS), a `.ref` (CORRECTNESS) and a wrapped three-angle measurement (SPEED). That is the whole point: one program, one identity, three axes, and no axis inferred from another.

## WHAT MAY NOT BE SAID

- ⛔ A suite may not print a pass count whose denominator excludes programs it ships without naming them in the same breath.
- ⛔ A benchmark grid may not shrink its kernel population silently; the runner REFUSES when the measured kernel count is below the globbed population and names the missing kernels.
- ⛔ `UNGRADED` may not be reported as `0` when it has never been derived; the value is `UNKNOWN` and it is printed as `UNKNOWN`.
- ⛔ No document quotes a ledger number without its tree label (SCRIP and corpus hashes), per the watermark law.
