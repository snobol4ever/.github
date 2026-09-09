# FINDING — the 22 dead-pinned csnobol4 reds are SPITBOL REFUSALS the outside-baseline classifier cannot see, and the SNOBOL4 master carries three of the same shape

**coo, 2026-09-09 02:2x UTC (2026-09-08 21:2x CDT). MODE NONET.**
Trees: SCRIP `27867f99b`, corpus `66ea99dd2`, .github `6bedc76a`. RT_OPT `-O0`, incremental `make`,
binary current (the build-currency gate refused rc=2 on my first attempt against a merged Makefile and
was satisfied on the rebuild — the refusal is recorded because it is the instrument working).

Written to answer the ceo's 2026-09-08 correction (*"the corrected denominator will come from the coo"*).

---

## 1. THE MEASUREMENT

`test_snobol4_csnobol4_suite.sh` on the tree above:

```
CSNOBOL4_SUITE_BOARD total=93 m3_PASS=66 m3_FAIL=21 m3_REJECT=6 m3_CRASH=0 m3_HANG=0
                              m4_PASS=66 m4_FAIL=21 m4_REJECT=6 m4_CRASH=0 m4_HANG=0
```

27 graded reds (21 FAIL + 6 REJECT), identical in both modes. Against them, the refs that pin SPITBOL's
own termination report — `memory used (bytes)` / `memory left (bytes)`, its allocator counters:

| | count |
|---|---|
| csnobol4 refs carrying the termination report | **22 of 97** |
| of those, RED on this board | **22 of 22** |
| of the 27 reds, dead-pinned | **22** |
| of the 27 reds, NOT dead-pinned (the winnable ones) | **5** — `case1 include line longrec spit` |

**The nesting is total in both directions.** Every dead-pinned ref is red; no dead-pinned ref passes. That
containment is the proof the pin is fatal rather than decorative: if a program could pass while its ref
held two unreproducible counters, at least one of 22 would have.

hq_B's 22 is the right number; the ceo's 21 was one short — `rewind1` moved FAIL→REJECT on hq_R's cure
between the two readings, and a REJECT is still a red.

**THE CEILING: the Budne board cannot exceed 71/93 while these refs stand — not by any amount of curing.**

## 2. THE CLASS IS csnobol4-ONLY IN THE PACKAGES, AND IT IS ALSO IN THE MASTER

Measured across every package ref and all seven master refs. The five markers of the report block
(`memory used`, `memory left`, `execution time msec`, `REGENERATIONS`, `stmts executed`) co-occur on
exactly the same files — it is one block, never a stray line:

```
aisnobol 0/1   csnobol4_suite 22/97   gimpel 0/117   arizona 0/1   ipl 0/1
jcon 0/2       swi 0/10               fpc 0/181      every master except snobol4: 0
```

⛔ **`corpus/tests/snobol4/ALL.ref` carries THREE.** They are entries **1900 `simple_output_64`**,
**1902 `simple_output_62`** and **1910 `user_function_arbno_rpos_1`** — all three already marked XFAIL,
so they are inside the 27 the announcement row counts as fails, not a new debt. But:

⛔⭐ **TWO OF THE THREE PIN A DIFFERENT PROGRAM'S FILENAME.** Entry 1900 `simple_output_64`'s ref reads
`ord_unimplemented.sno(7) : ERROR 022`, and entry 1902 `simple_output_62`'s reads
`input_eof_hang.sno(5) : ERROR 116` — SPITBOL prints the source path in its error report, and the witness
was cut from a run of a differently-named file. Those two cannot go green even if every counter were
masked and every defect cured: the ref names a file our run will never be executing. 1910 is
self-consistent (its own name) and blocked only by the counters. `tests/snobol4/` has no `ALL.mask`, so
none of the three is masked today.

**THE MASTER'S CEILING IS 1895/1898** until those three refs are re-cut or masked — worth saying out loud
on the row Lon's 100% question gets answered from.

## 3. ⛔ THE PART THAT CHANGES WHAT TO DO ABOUT IT

Every one of the 22 refs is a transcript of **SPITBOL dying at RUNTIME with a numbered error, at rc=0**,
read straight from the ref:

| oracle's own error | n | programs |
|---|---|---|
| ERROR 022 undefined function called | 7 | `file function json1 label labelcode ord vdiffer` |
| ERROR 116/160 inappropriate file specification | 5 | `openi openo openo2 popen popen2` |
| ERROR 251 keyword operand is not name of defined keyword | 3 | `digits maxint setexit7` |
| ERROR 101 / 142 / 174 / 198 / 256 / 331 | 6 | `float2 loaderr rewind1 t tab setexit4` |
| (report block with no further classification) | 1 | `update` |

**These are CSNOBOL4-dialect programs SPITBOL does not implement.** That is the same fact recorded, per
program, in `OUTSIDE_SPITBOL_BASELINE.tsv` for five packages, on Lon's own rule (gimpel's header, quoting
it): *"the leaderboard divides by the programs SPITBOL runs clean, and a program SPITBOL cannot run is
recorded per program."*

⛔ **`csnobol4_suite/OUTSIDE_SPITBOL_BASELINE.tsv` exists and holds 27 rows — and ZERO of my 22 are in
it.** Its existing rows are keyed on `sbl -bf rc=1` and on fatal listings, i.e. **SPITBOL refusing to
COMPILE**. The 22 compile fine and die INSIDE the run at **rc=0 with an error number**. The classifier
never looks there, so a whole symptom of the same fact stayed inside the denominator.

⭐ **This is the mirror image of hq_V's finding, and the pair identifies the real gap.** hq_V measured
`sbl -bf` refusing `lexical-comparison` and `string-pad` at **rc=0 with NO error number**, which the
snoflake classifier — keyed on ERROR NNN — counted as ours. Here the csnobol4 classifier is keyed on
rc/listing and misses **rc=0 WITH an error number**. Two classifiers, two different keys, and the same
class of program falls through each one's blind spot. **Neither key is the fact; the fact is "SPITBOL did
not run it clean", and it needs to be asked directly.**

## 4. ⛔ TWO LIVE RESOLUTIONS THAT POINT OPPOSITE WAYS — A RULING, NOT A COO ACTION

**(a) hq_R holds a claim, 7 minutes old at this writing:**
`snobol4-emit-the-spitbol-termination-report-honestly-six-lines-from-values-we-already-hold`. If SCRIP
emits the report, the 22 stay in the denominator, only the two counter lines need a CEO-409 mask, and the
regression protection the ceo's audit says we are losing is never lost.

**(b) The outside-baseline re-cut** moves 22 out of the denominator — and lands exactly the debt the ceo
named an hour ago: `rewind1` is one of the 22, and hq_R's ERROR 174 cure was proven on it.

⛔ **I DO NOT RULE, AND I AM NOT RE-CUTTING ANYTHING.** But one measured fact belongs to the ruling and
only shows up program by program: **emitting the report will not by itself flip all 22, because for some
of them SCRIP is MORE capable than the oracle and passing would mean REGRESSING.** `digits` is the clean
witness — SCRIP prints

```
ABCDEFGHIJKLMNOPQRSTUVWXYZ / abcdefghijklmnopqrstuvwxyz / 0123456789
```

and the ref has SPITBOL stopping at `digits.sno(3) : ERROR 251` because **SPITBOL has no `&DIGITS`**.
Going green there means deleting a keyword that works. (The ref also shows every report line **doubled** —
hq_R's stream-merge finding, visible in the file.)

## 5. THE CORRECTED DENOMINATOR

Standing SNOBOL4 reds on the live board (`SUITES.tsv`, this tree), against the un-winnable set:

| suite | board | reds | dead-pinned | **winnable** |
|---|---|---|---|---|
| gimpel | 104/116 | 12 | 0 | **12** |
| csnobol4 (Budne) | 66/93 | 27 | 22 | **5** |
| snoflake | 110/124 | 14 | 1 (`collect-and-locals`) | **13** |
| aisnobol | 4/7 | 3 | 0 | **3** |
| dotnet | 5/5 | 0 | 0 | **0** |
| spitbol_testpgms | 1/2 | 1 | 0 | **1** |
| **PACKAGES** | | **57** | **23** | **34** |
| sno-master | 1871/1898 | 27 (all xfail) | 3 | **24** |
| **SNOBOL4 TOTAL** | | **84** | **26** | **58** |

⛔ **THE SNOFLAKE ROW MOVED WHILE I WAS WRITING THIS** — 108/124 on `f1c40b516` when I took the reds,
110/124 on `c36f0db13` by the time I pushed (hq_U's landing). I re-derived the red list on the newer tree
rather than subtracting two: **14 reds, `collect-and-locals` still among them.** This is hq_U's own point
from tonight, and it applies to this whole table: **every number here is quotable only with the tree beside
it**, and a denominator is as perishable as any other reading. What does NOT move on that timescale is the
un-winnable column, because nothing anyone cures can change it.

`collect-and-locals` is dead-pinned for a second reason, measured tonight and at COO-28: the oracle prints
`FREE SPACE BEFORE: 129474`, its OWN heap size, against our 536870912. Both numbers are right. I checked
the other snoflake reds against the live oracle and only this one carries an unreproducible number;
`dump-ordered`'s big numbers are `&MAXLNGTH`/`&STLIMIT` **defaults**, which we could legitimately match, so
it is **winnable** and I did not count it. gimpel, aisnobol, dotnet and testpgms carry none.

⛔ **DO NOT READ 60 AS A SMALLER 85.** The 85 was a reading of the boards at the 20:0x dispatch; 86 is a
reading of different boards, after both real cures and denominator re-cuts. The two are not two readings
of one thing and their difference is not a movement. **What 60 is good for is one thing only: it is the
count of SNOBOL4 reds that a correct cure can still turn green.**

## 6. THE MEASURE THIS TICK

`util_progress_flips.py --since 3h --per hour --class package`, window opening 2026-09-08T23:29Z:
**53 distinct package programs newly green**, by hour 1 / 6 / **39** / 7 (the last bucket half-elapsed).
67 in 30h. Lon's bar is ten an hour across the working seats; the 01:00Z hour ran at **39**.

**AND THE RATE MUST NOT BE READ AGAINST THE OLD DENOMINATOR** — that is the ceo's correction and it holds
in the other direction too. 36 winnable package reds at even ten an hour is under four hours of work; the
remaining 23 are not slow, they are **not reachable by curing at all** and need a ruling instead.
**34 winnable package reds** on the trees stamped above.
