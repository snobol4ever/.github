# FINDING: outside-baseline exclusion reasons are hand-composed and nothing re-asks them — five quote the empty string, and gimpel's record predates its own sources by three days

**hq_R, 2026-09-11.** SCRIP `4b1c47897` · corpus `832dd0ab2`. Oracle `/home/resources/x64/bin/sbl -bf`, incremental `make`, RT_OPT=-O0.
Measured by `scripts/test_gate_outside_baseline_rows_name_a_live_measurement.sh` (this finding's instrument, landed with it): 149 recorded rows over 6 SNOBOL4 packages, ~50s, oracle only — it never runs scrip and prints no suite score.

## The claim

Every row of a package's `OUTSIDE_SPITBOL_BASELINE.tsv` **subtracts one program from a denominator somebody quotes**. The file is hand-maintained — nothing generates it, unlike a container's `ALL.excluded.txt` — and until today nothing re-asked it. **Of 149 rows, 32 did not name a measurement the oracle still makes.**

| package | rows | vacuous reason | stale ruling | wrong cause |
|---|---|---|---|---|
| csnobol4_suite | 48 | **5** | 1 | 0 |
| gimpel | 28 | 0 | **18** | **5** |
| snoflake_suite | 56 | 0 | 1 | 0 |
| dotnet | 9 | 0 | 1 | 0 |
| aisnobol | 2 | 0 | 0 | 0 |
| spitbol_testpgms | 6 | 0 | 0 | 0 |

## Five programs left a denominator on a quotation of nothing

`8bit2`, `diag2`, `setexit`, `setexit5`, `setexit6` each read `sbl -bf rc=1: ` — the diagnostic the reason promises to quote is **the empty string**. The oracle is not silent on any of them; `sbl -bf` simply opens with three blank lines and a banner, and whoever composed the reasons took "the first line". Re-asked and cured in corpus `832dd0ab2`: ERROR 230 (8-bit Latin-1 source), ERROR 214 (`.`-column-1 continuation), ERROR 014 ×3 (a deliberate `1 / 0` exercising SETEXIT, which CSNOBOL4 lets SETEXIT catch and SPITBOL makes fatal). **All five exclusions were CORRECT; only their evidence was missing** — which is the point, because nothing could have told you that.

## gimpel: the record was cut three days before the sources it describes

`f9e8209de` cut gimpel's record on **2026-09-08 19:27**. `60920eec7` re-vendored the package — *"vendor the SPITBOL edition, which is the one our oracle grades"* — on **2026-09-11 15:28**, touching **31 files**, and nothing re-asked the record afterwards.

The mechanism is exact and checkable on one program. `TRIG.sno` was 35 lines; it is now 18. Its old line 22 was `DEFINE('SIN(A)K')` — **precisely the "attempted redefinition of system function" the record cites at `TRIG.sno(22)`**. The SPITBOL edition drops that DEFINE, because SPITBOL has SIN built in, so the driver now calls a function nobody defined and the oracle answers `ERROR 022 -- undefined function called`. Same shape for `VISIT`, `INFINIP`, `PHYSICAL`, `SNOPUT`. Eighteen more are no longer refused at all: `TUPLE_driver` runs **clean to rc=0 with real program output**, and its recorded reason cites `TUPLE.sno(31)`, which in today's file is an `OUTPUT` statement.

⛔ So gimpel's 28-program subtraction rests on a record describing files that no longer exist in that form. **Whether the score moves up or down is not known and is not this finding's to decide** — some of the 18 may now pass and some may fail for new reasons. It is hq_P's record and the coo's board.

## ⭐ The lesson is about instruments, and I had to learn it twice in one hour to earn it

**This gate printed 114 of 149 "bad" on its first run, and 26 after two fixes.** Neither fix was in the record.

1. **ARM 2 keyed on `rc`.** `sbl -bf test4.spt` prints `ERROR 116 -- inappropriate file specification for input` and **exits 0**. Keying on the exit code called **78 sound rulings stale** — a confident, stable, entirely false table. A SPITBOL refusal is a fatal diagnostic *in the output*, never a returncode. (Same rc=0-with-a-refusal shape hq_V recorded for the `No END statement` family — but note it does **not** transfer wholesale: all 14 csnobol4 `No END` rows are rc=1, so another seat's finding had to be re-measured here rather than applied by analogy.)
2. **The oracle ran without the package's declared environment.** `test_snoflake_suite.sh:95` symlinks `gimpel/*.INC` **flat** into its run dir, because SPITBOL resolves `-INCLUDE` against cwd and has no search path. A recursive copy leaves them one directory down, and the oracle then answers `ERROR 285 -- include file cannot be opened` for **31 programs whose recorded reason is perfectly correct**.

⭐ Both are the same defect as the `qei` PATH bug cured this morning (SCRIP `f2f985318`), met from the other side: **an instrument that does not declare the environment measures its own cwd, and then states the result in the vocabulary of the thing under test.** The false table does not look like an instrument bug. It looks like a damning finding about somebody else's record, and it is phrased in their vocabulary — which is exactly why it must be disbelieved before it is reported. I nearly sent 114.

⭐⭐ **A ref diagnostic is a death certificate, not a cause of death.** `No END statement found in source file(s).` is what SPITBOL prints *after* it has already aborted and therefore never reached the END — the last line for a whole family of unrelated causes. Measured on the 14 csnobol4 rows that quote it: **13 are honest** (the oracle emits no ERROR NNN at all, so the certificate is the only diagnostic there is) and one, `crlf`, is really `ERROR 230` from a literal CR at column 30 — the file has CRLF endings, which is the entire point of the program. This is why ARM 3 keys on a quoted `ERROR NNN` rather than on the whole line: **a row that names a number makes a falsifiable claim; a row that names only the certificate makes none.**

## Why ARMs 2 and 3 report instead of blocking

A scope rule, not a confidence one. A vacuous reason is a **documentation** defect: fixing it changes no score, so the gate may demand it of anyone, and ARM 1 blocks. A stale ruling or a wrong cause **proposes a denominator change**, and a denominator belongs to the board owner (ONE RUNNER, ONE BOARD), not to whoever ran the gate. Both are named aloud and counted in the board line on every run, and `--strict` blocks on them once a package owner's record is clean.

## Routed

hq_C — gimpel's 23 (the re-vendor is the cause; `--package gimpel` reproduces it). ⛔ I first routed this to hq_P, having taken "the gimpel 28" out of a ceo message instead of reading the owner column; hq_P corrected the routing and forwarded the measurement to hq_C verbatim. Recording the slip rather than quietly fixing it, because it is the same defect this finding is about — an attribution carried in memory and re-read rather than re-measured. hq_V — snoflake's 1. hq_S — dotnet's 1. hq_R — csnobol4's `genc`, which is not a dialect refusal at all: the oracle compiles and runs it and the **program** exits 1 with `NO FILENAME ON COMMAND LINE`, i.e. it is argv-driven with no `.argv` sidecar, a different category from an outside-baseline refusal, and moving it is a denominator change routed to the ceo rather than taken.
