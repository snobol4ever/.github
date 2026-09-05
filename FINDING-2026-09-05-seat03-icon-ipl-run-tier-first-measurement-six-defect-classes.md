# FINDING: IPL's first RUN-tier measurement (60 oracle-cut refs) — six defect classes, two already known

Task `icon-ipl-851-run-graded-against-iconx-refs-and-cured-by-class` (hq_B lane). `test_icon_ipl_suite.sh`
gained a RUN tier (SCRIP `f72ea9426`); `util_cut_icon_ipl_refs.sh` cut 60 deterministic refs from the real
Icon oracle (see that script's own header for the isolation/determinism-check discipline it took two real
incidents to arrive at). First measurement: m3 22/60 m4 22/60, fail 36/36, crash 2/2, hang 0/0 — both modes
disagree with the same 38 programs, not independently.

Investigated a representative witness set (26 of the 36 FAILs, both CRASHes) rather than trust aggregate
counts. Six classes, grouped by shared signature per RULES.md discipline ("group by shared signature,
never force one bucket; a genuinely new shape is reported by name, not absorbed") — do not re-triage these
26+ names individually without re-reading this finding first.

## Classes A/B are NOT NEW — same defects the compile tier already named and scoped out of this row

**A. linkgap** (≥24 of 36, confirmed: vnq/ipldoc/deal/ibrow/icontent/morse/iplindex/itrcsum/empg/makepuzz/
isrcline/envelope/lineseq/colm/toktab/lindcode/conman/ipxref/scramble/fract/streamer/diskpack/queens/
oldicon/ilnkxref): `icon: link: cannot open .../options.icn (linked from .../NAME.icn)` — SCRIP's link
resolver is single-directory-only (icon_driver.c:26-45), IPL's progs/procs split is upstream's normal
organization. This is `test_icon_ipl_suite.sh`'s own pre-existing compile-tier class, unchanged; the RUN
tier just makes it visible a second way (m4 can't build, so it can't run either). Not this row's to cure.

**B. parseerr** (2 confirmed: igrep line 118 "expected ; got if", roffcmds line 44 "expected ; got IDENT"):
same pre-existing compile-tier class (SCRIP's explicit-`;` requirement vs upstream's implicit statement
separation). Not new, not this row's to cure.

## Classes C-H are NEW to this task — first time IPL has been RUN-graded at all

**C. `open(cmd, "p")` (pipe/popen mode) is silently non-functional** (≥4 confirmed: cwd, fileprep,
kwicprep, procprep — all four call `open("ls ...", "p")` or `open("pwd", "p")`; grep for `, "p")` across
the remaining OWED population before assuming this list is exhaustive). Effect: `open` fails, the
surrounding `read(open(...)) ? {...}` or loop body never executes, program exits rc=0 with **zero output
and no error** — the single most dangerous shape in this whole census, because it looks like a clean pass
to anything that only checks rc. Witness: `cwd.icn` is 30 lines, does exactly one thing
(`read(open("pwd","p")) ? {...; write(tab(0))}`), and produces nothing.

**D. `system()` builtin is unimplemented** (≥2 confirmed: declchck, banner — both call `system(...)`
directly). Effect: `(0) : ERROR 005 -- Undefined function or operation` printed once, then the program
aborts (only 1 output line captured where multi-hundred were expected). Note the SNOBOL4-style `(0) :
ERROR NNN --` format surfacing from Icon execution — worth a look by whoever owns the shared error-report
path, independent of `system()` itself being missing.

**E. `&error`-scoped `runerr()` does not convert to a catchable failure** (1 confirmed: irunerr.icn, 20
lines, its entire body is `every i := 100 to 500 do { &error := 1; runerr(i); write(&errornumber," ",...) }`
— deliberately triggers every defined runtime error under error-conversion mode to print Icon's own error
catalog). SCRIP's actual output is one line, "Run-time error 100" (SCRIP's own uncaught-error banner, not
the program's `write()` — compare the oracle's first line "101  integer expected or out of range", i.e.
error 100 isn't even defined and the oracle silently continues to 101). Reads as: `&error := 1` does not
suppress the abort the way it must, so the loop dies on iteration 1 instead of surviving all 401. This is
a language-conformance gap, not merely a missing builtin — worth flagging as possibly the single
highest-leverage class here since `&error`/`runerr` is core control flow, not a corpus-specific feature.

**F. Date formatting inserts an extra space before a single-digit day** (1 confirmed: gftrace — diff is
exactly `"September  5, 2026"` (SCRIP, two spaces) vs `"September 5, 2026"` (oracle, one space); both runs
happened the same calendar day, so this is a formatting bug, not a date-rollover artifact). Small, cheap,
isolated — likely a `%2d`-style fixed-width pad in a date/`&dateline`-adjacent runtime routine that should
suppress the leading space (or use `%-2d`/trim) for single-digit days.

**G. Same ERROR-005 signature, cause NOT confirmed** (1: ifncsgen.icn) — shares class D's exact error text
but does not call `system()` anywhere in its source (checked directly). Do not fold into D without
independently confirming its trigger; reported separately on purpose.

**H. CRASH, both modes, both a compiler/runtime defect on ordinary real-world programs** (2: miu, genqueen
— both SIGSEGV in m3 AND m4, i.e. not mode-specific). Same shape as the aisnobol ENDING/WANG crashes and
csnobol4_suite's nqueens crash already on record elsewhere (FINDING/LEDGER entries from seat15/seat16,
different suites) — a growing pattern of real-program SIGSEGVs worth a cross-suite look, not just a
per-suite one. Not root-caused here (ASM-DIFF-FIRST is a separate undertaking per RULES.md); named, not
chased, consistent with this row's own lane (harness + census, not compiler debugging).

## Scope note

Per this row's own GOAL: "the HQ cures src/, a seat cures fixture- and instrument-level reds." All of
C-H are src/-level (runtime builtins, error-handling, formatting, crashes) — none are corpus-fixture or
harness-instrument defects, so none were cured in this pass; census only, per the GOAL's own division of
labor. Minted as child rows (rank 1) in this lane per the GOAL's explicit method ("mint each class as a
child row").
