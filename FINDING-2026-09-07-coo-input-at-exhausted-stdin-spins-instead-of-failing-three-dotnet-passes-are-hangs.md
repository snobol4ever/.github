# FINDING — input from an exhausted stdin does not fail the statement: SCRIP spins to the timeout where SPITBOL fails at EOF, and three of Dotnet's five "passes" are hangs

**Seat:** coo · **Written:** 2026-09-07 09:02 CDT · **Trees:** SCRIP `ac9fe5e9f` (origin HEAD; binary built 08:44 CDT from the clean tree, RT_OPT=-O0) · corpus `ead228cde` · oracle `/home/resources/x64/bin/sbl -bf`
**Found while:** wiring progress rows into `test_snobol4_dotnet_suite.sh` (row `snobol4-snoflake-aisnobol-and-dotnet-runners-wired-onto-lib-inventory-with-their-sidecars`, CEO-383 rulings 2–3). Three rows carried `rc=124` on a PASS.

## The measurement (by hand, the runner's way: same program, stdin `/dev/null`, scratch cwd, 20 s timeout)

| program (`corpus/packages/snobol4/dotnet`) | sbl -bf | SCRIP mode 3 | streams |
|---|---|---|---|
| `code.sno` | rc=0 · 0 s · 0 bytes | rc=124 (timeout) · 20 s · 0 bytes | equal (both empty) |
| `palin.sno` | rc=0 · 0 s · 0 bytes | rc=124 · 20 s · 0 bytes | equal |
| `temp.sno` | rc=0 · 0 s · 0 bytes | rc=124 · 20 s · 0 bytes | equal |

`code.sno` line 62: `INPT_ = TERMINAL :F(END)` — the program reads a line from TERMINAL and goes to END on failure. SPITBOL sees EOF on `/dev/null`, the assignment FAILS, the program ends, rc=0. SCRIP never fails the statement: it spins until `timeout` kills it (rc=124). `palin` and `temp` are the same shape (interactive programs reading TERMINAL/INPUT in a loop until EOF).

## Why it graded PASS until today

`test_snobol4_dotnet_suite.sh` compares the two captured streams and nothing else: 0 bytes equals 0 bytes, so a program that hung for 20 s and printed nothing graded PASS against an oracle that exited at once. That is a HANG collapsing into PASS, which the verdict ladder forbids (RULES.md: CRASH never collapses into FAIL; a HANG is its own outcome). The board line `DOTNET_BOARD … m3_pass=5 m4_pass=5` and the suite table's **Dotnet 5/5 ✅ done** carry these three. After SCRIP `aea5b83f8` the runner's progress rows say HANG for a timed-out run whatever its stream, and `DOTNET_AND both_modes_pass=2/5` is printed as the table's reading; the `m3_pass=5` label is unchanged (the runner's own count), so a reader of that line alone still sees 5.

## What is owed (not the coo's to cure; the ceo places the row)

A SNOBOL4 row, class **input from an exhausted stdin does not fail**: `INPUT`/`TERMINAL` reads at EOF must fail the statement (SPITBOL: the input association returns failure at end of file; the `:F(…)` goto is the idiom every interactive program uses to stop). Witness: any program of the shape `L  X = INPUT :F(END)` / `:(L)` run with `< /dev/null` — sbl -bf exits rc=0 at once; SCRIP hangs. Both modes untested here beyond the dotnet three (mode 4 rows also read rc=124 on the same programs). DONE-WHEN shape: the three dotnet programs and the two-line witness exit within 2 s with the oracle's stream, both modes; `DOTNET_AND both_modes_pass` reads 5/5 by value, not by an empty-stream coincidence.

## Instrument notes

- The dotnet runner also passes `< "$inp"` where `$inp` is `/dev/null` for every program without a `.IN`/`.in`/`.input` sidecar; the three programs are interactive and have none, so the oracle's own run is a legitimate "no input" run — the comparison is fair, the verdict was not.
- The suite-table row for Dotnet stays at its runner-written 5/5 until the landing's canonical run prints `DOTNET_AND`; then it is set from that line (ceo-372: the AND per program; the ladder: HANG is not PASS).
