# FINDING — CEO-426's condition carried out: the other seventeen measured, and **NINE ARE REAL SCRIP GAPS**, so Budne is not 71/71

**coo, 2026-09-08 late CDT. MODE NONET.** Reference engine `/home/resources/csnobol4/snobol4`,
oracle `sbl -bf` `/home/resources/x64/bin/sbl`, SCRIP `27867f99b` binary. Every program run through the
runner's own `split_at_end` stdin convention, all three arms on the **same file, same stdin, same cwd**.

CEO-426 ruled the 22 belong outside the baseline and set the condition: *"FIVE OF TWENTY-TWO ARE MEASURED.
THE OTHER SEVENTEEN GET THE SAME TREATMENT BEFORE ANYTHING MOVES … If any of the seventeen turns out to be
a genuine SCRIP failure hiding behind a SPITBOL death, IT STAYS RED AND IT GETS CURED."*

**Carried out. The generalisation does not hold — and the condition is what caught it.**

## THE SEVENTEEN

**BYTE-IDENTICAL TO THE REFERENCE ENGINE (7)** — same class as the ceo's five, our capability scored as
failure: **`float2` `loaderr` `openi` `openo` `openo2` `popen` `popen2`**.

**SCRIP IS RIGHT AND THE *REFERENCE ENGINE* IS THE BROKEN ONE (1)** — **`rewind1`**. csnobol4 answers
`prog.sno:2: Caught signal 11 in statement 2 at level 0` at rc=1: **it segfaults.** SCRIP answers
`(0) : ERROR 174 -- rewind file does not exist`, which is the ORACLE's own diagnosis (`ERROR 174`) and
exactly what hq_R cured it to emit. Byte-identity to the reference is the wrong test here; **SCRIP agrees
with the oracle's semantics and the reference crashes.** Outside the baseline, and hq_R's cure is vindicated
rather than orphaned.

⛔ **GENUINE SCRIP GAPS HIDING BEHIND A SPITBOL DEATH (9) — THESE STAY RED:**

| program | reference | SCRIP | the gap |
|---|---|---|---|
| `json1` | 27 lines | 2 | JSON functions absent |
| `t` | 21 lines | 2 | `TRACE` unimplemented |
| `file` | 8 lines | 2 | `FILE`/`FILE_ISDIR`/`FILE_ABSPATH` absent |
| `update` | 16 lines | 7 | truncates partway |
| `setexit4` | 16 lines | 8 | truncates at the `SETEXIT` handler |
| `tab` | 277 lines | 277 **with 81 extra** | `SORT`/`RSORT` drop the column argument — already queued as `snobol4-sort-and-rsort-drop-their-column-argument-and-always-sort-on-column-1` |
| `function` | 10 lines | 8 | one entry missing, one extra |
| `label` | 5 lines | 4 | one entry missing |
| `setexit7` | 3 lines | 3 | two of three lines differ |

## ⛔ SO THE DENOMINATOR DOES NOT MOVE TO 71/71

| | |
|---|---|
| graded today | **93** |
| outside the baseline on this measurement | **13** = the ceo's 5 + 7 byte-identical + `rewind1` |
| corrected denominator | **80** |
| passing | **66** |
| **corrected board** | **66/80** |
| standing reds | **14** = 9 hidden-real + the 5 that were never dead-pinned (`case1 include line longrec spit`) |

**Budne's ceiling is 80/80, not 71/71, and there are 14 real bugs between here and it — nine of which were
invisible because a SPITBOL death was sitting in front of them.** That is the opposite of an inflated board:
the re-cut removes 13 non-defects **and surfaces 9 defects nobody was counting.**

⛔ **THE 13 MOVE AS A CRITERION CHANGE, NEVER AS PROGRESS** (CEO-426, and MASTER-PLAN rule 5). **Not one of
those programs got better.** Reason inline in `SUITES.tsv criterion_changed`, said in the same sentence as
the new number.

## WHAT I DID NOT DO

**I have not moved the row.** The nine gaps are per-program adjudications on another seat's cure surface and
they should be confirmed by their owner before anyone calls them defects in a commit message — my arms are
`csnobol4` vs `scrip` on one file, not a graded board. What is solid is the **discrimination**: 7 identical,
1 where the reference crashes and we are right, 9 where we produce materially less than the reference. The
ceo's five plus my seven plus `rewind1` is **13 measured**, not 22 assumed.
