# FINDING: the AIS suite graded 2 of 8 shipped programs, and the other six were DRIVER and DIALECT problems, not oracle refusals

Measured 2026-09-06 by hq_T. Suite: `corpus/packages/snobol4/aisnobol` — Michael Shafto, *Artificial
Intelligence Programming in SNOBOL4* (1987). Oracle: `/home/resources/x64/bin/sbl -bf`.

## 1. The board's "AIS 0/2" is a GRADED denominator, not the population

The suite ships **8** programs (ATN BUILDLIB ENDING HSORT KALAH SIR TEST WANG). Two were graded;
four were filed UNGRADABLE `ORACLE_REFUSES` and two UNGRADED `NEEDS_VENDORED_SOURCE`. Reading "0/2"
as "two programs, both red" is how the whole suite stayed invisible: **six shipped programs were not
in any denominator at all.** Always separate shipped / graded / ungraded / ungradable.

## 2. The upstream drop ships a SPITBOL twin of every program, and we vendored the wrong dialect

`/home/satirical/SNOBOL-history/AI-SNOBOL/` holds `*.SNO` (SNOBOL4+) **and** `*.SPT` (Macro Spitbol)
for all 8, plus `SNOCORE.INC`/`SPITCORE.SPT`, `SNOLIB.INC`/`SPITLIB.SPT`, `SNOLIB.IDX`,
`BUILDLIB.BAT`, `README.DOC`. The corpus vendored only the `.SNO` side while grading with a SPITBOL
oracle. The README is explicit: *"Spitbol files must be converted to line-feed terminated records to
operate under the Un*x version of Spitbol-68K."* The `.SPT` files are CRLF; fed as-is every one dies
with ERROR 230 "illegal character". **Strip CR and they run.**

## 3. Four of the six "oracle refuses" verdicts were taken on an error path

| program | recorded reason | MEASURED with the right dialect/driver |
|---|---|---|
| ATN | ERROR 274 `&FULLSCAN` zero — "no ground truth" | `.SPT` runs CLEAN, rc=0, 9432 bytes |
| KALAH | ERROR 160 bad output file spec | `.SPT` runs CLEAN, rc=0 |
| HSORT | ERROR 067 array dimension zero | reason taken with NO driver; its own line 60 is `INPUT(.INPUT,1,HOST(0))` — the filename is an **argv**, not stdin. With `sbl -bf HSORT.SPT HSORT.IN`: CLEAN, 0 errors |
| SIR, TEST | `-INCLUDE 'SNOCORE.sno'` "not vendored anywhere in corpus" | true of the corpus; the file exists on the box. With `SPITCORE.SPT` + two fixes below: **both run clean** (SIR 1704 bytes, TEST 14108) |
| BUILDLIB | ERROR 022 undefined function | GENUINE, and now sharp: `BUILDLIB.SNO:14` needs `TELL(5)`, `BUILDLIB.SPT:21` needs `SET(1,0,1)`. **Our sbl has neither.** Its own header documents the fallback (count characters + 1 per line) |

## 4. Two dialect adaptations SNOLISPIST needs under a modern Spitbol

* **Six DEXTERN prototypes collide with builtins.** `SPITCORE.SPT` DEXTERNs `ATAN COS EXP SIN SQRT
  TAN`; Spitbol-68K (1987) lacked them, ours has them as system functions, so `DEFINE` raises
  ERROR 248 "attempted redefinition of system function". Found by probing all 100 DEXTERN names
  against the oracle one at a time — the error names no culprit. Suppress those six; the builtin is
  the superset.
* **LOADEX's seek is only an optimisation.** `SPITCORE.SPT:122` does `SET(15,POS,0)` before scanning,
  but `LOADEX1` (126-128) *already* scans the library sequentially for the label. With `SET` absent,
  reopening the library at offset 0 and letting that scan run gives the same result, slower. `SET` is
  then needed only for the index existence check.
* The index `SPITLIB.IDX` is the one file upstream never ships (only `SNOLIB.IDX`). A generator was
  written and **validated by reproducing the shipped `SNOLIB.IDX` byte-for-byte** from `SNOLIB.INC`
  (133/133 entries, identical offsets; the shipped file differs only by a trailing `.` the DOS build
  printed on 5-digit offsets).

## 5. SCRIP's own measured gaps against these programs

Landed this sitting:
* **`SETEXIT(.CONTINUE)` raised ERROR 187.** `CONTINUE ABORT RETURN FRETURN NRETURN` are SNOBOL4
  *system* labels; `_SETEXIT_` resolved its argument with `rt_entry_resolve()`, which only knows user
  labels. `sno_setexit_resume()` already distinguished CONTINUE from ABORT — only the acceptance check
  was wrong. Blocked ENDING, HSORT, WANG and all of SNOLISPIST.
* **`REWIND(5)` was a SILENT NO-OP.** Units 5/6 are never entered in `_io_chan`, so `_REWIND_` found no
  `fp` and returned having done nothing. A two-pass program then reads EOF on pass two and prints a
  full, plausible, EMPTY answer — HSORT counted 22 lines and printed 22 blanks. Fixed by falling back
  to `stdin`/`stdout` for units 5/6 rather than binding them into `_io_chan`, whose close path would
  `fclose(stdin)`.
* **`HOST(0)` returned `""` unconditionally.** SPITBOL returns the program's parameter string; SCRIP
  already staged program args via `rt_main_args_stage`, so `_HOST_` selector 0 now joins them.

Still open — one row each, minimal witness given:
* **`INPUT(.INPUT,1,file)` re-associating the BUILT-IN name is a no-op.** Oracle `counted=3`, SCRIP
  `counted=0` on the 6-line witness in the row. This is HSORT's last blocker.
* **`&STLIMIT` assignment not honoured** — ATN sets `&STLIMIT = 50000` and SCRIP still raises ERROR 244.
* **`CODE()` / `EVAL()` are outside the landed lowering subset** — blocks SIR and TEST under SCRIP
  (`FATAL lower_snobol4 (GZ#5 subset)`).
* **`SET()` / `TELL()` file positioning absent** — blocks BUILDLIB in both dialects, and is what forced
  the LOADEX workaround above.
