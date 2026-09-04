# FINDING 2026-09-04 hq_T — SPITBOL DREAL literals are unlexed, so SPITBOL's own test program #1 does not parse

**Row:** `snobol4-spitbol-testpgms-vendored-as-a-package-suite-with-a-runner-and-a-score-cell` (Lon 2026-09-04 17:57 CDT via ceo: *SPITBOL's own testpgms 1-4 must run*).
**Found by:** the runner's first measurement, on the run that created it.

## The witness, minimal, with its control

```
$ printf '\tOUTPUT = 1.0D2\nEND\n' > dreal.sno && scrip dreal.sno
snobol4:1: error: parse error: syntax error
snobol4:0: error: missing END statement

$ printf '\tOUTPUT = 1.0E2\nEND\n' > ereal.sno && scrip ereal.sno
100.

$ sbl -bf dreal.sno   →  100.        $ sbl -bf ereal.sno   →  100.
```

SCRIP accepts an `E`-exponent real and rejects a `D`-exponent one. The oracle accepts both. In SPITBOL a `D` exponent is a **DREAL** — a double-precision real literal — and the lexer has no rule for it.

## Why it matters more than one literal form

`test1.spt` is SPITBOL's own diagnostics program #1, and its DREAL section sits at line 280 of 500-odd:

```
*        TEST DREALS
         TEST = DIFFER(1.0D2 + 2.0D2,3.0D2) STARS
```

One unlexed literal form fails the **whole file** at parse time, so SCRIP produces no output at all for a program the oracle runs to 120 lines. The suite's first board is therefore `total=4 scored=1 unscored=3 m3_pass=0 m3_fail=1 m4_pass=0 m4_fail=1` — the single program the oracle can grade is red in both modes, for this one reason.

⛔ **Not a harness artifact, and the extension is not the cause.** `.spt` is not in the driver's extension list, and the first hypothesis was that the driver rejected the file. Measured: copying the same bytes to `test1.sno` produces the identical parse error at the identical line. The driver reads `.spt` as SNOBOL4 fine.

**Owner:** SNOBOL4 correctness, not the instrument lane. Filed, not fixed.

## The other three programs are UNSCORED, and that is a measurement, not a gap

| program | oracle | scored? |
|---|---|---|
| test1 | rc=0, 120 lines | yes — RED both modes (this finding) |
| test2 | rc=139 (SIGSEGV) after 8 lines, **and rc=231 on a re-run of the same program** | no |
| test3 | rc=139 after 5 lines | no |
| test4 | rc=139 after 5 lines | no |

⭐ **The re-run difference is the ceo's witness holding up in a second place.** hq_P's oracle row says `sbl -bf` SIGSEGVs on *about half* its ERROR 212 runs; here the same program under the same input produced a real SIGSEGV once and a plain `rc=231` error exit the next. That nondeterminism is exactly why this runner decides on the oracle's **run status** and never on its output bytes — the truncated 8 lines look like an answer either way.

⛔ It is also why the runner **counts** the unscored three instead of skipping them. A board that silently shrinks its denominator to whatever happened to work reports a percentage of the wrong thing. And it refuses `rc=2` outright if the oracle ever dies on all four, because every counter would then read 0 and `m3_fail=0 && m4_fail=0` would print a perfect green board over an empty population.

## Two instrument defects cured on the way (SCRIP `7b18a3c52`)

* **The gimpel runner wrote into the tree it graded.** `ASM_driver.sno` opens a work file `ASMTEMP`, the scorecard runs each program in the program's own directory, so `ASMTEMP` landed in `corpus/packages/snobol4/gimpel/` and left the tree dirty — whereupon `util_score_row.py` correctly refused the leaderboard row **that the same run exists to produce**. Cured with a scratch `CORPUS` overlay, rather than a cwd change, because the scorecard's per-program cwd is load-bearing and this runner does not own that shared instrument.
* **A refused scorecard run printed a green board.** `scorecard_snobol4.sh` truncates `results.tsv` before doing anything, so its own board-contention refusal (*another SNOBOL4 board is running on this box*) left an **empty** `results.tsv`; the gimpel runner then printed `total=0 … m3_fail=0 m4_fail=0` and **exited 0**. A perfect green board over a run that never started. It refuses `rc=2` now and prints the scorecard's own log.

## One leaderboard defect, named and not cured here

The suite's V cell had to be **hand-edited**. `util_score_row.py write` refuses any text containing `;`, because `;` is `merge_clause`'s own delimiter — and this cell was hand-written months ago **with** semicolons. ⛔ So a cell that ever received a hand edit containing a semicolon can never again be written by its runner, which quietly breaks THE ONE LEADERBOARD's own FACT RULE for that row: *every suite run rewrites its row*. The refusal is right to protect the delimiter; refusing forever is the wrong shape. hq_T's tooling row.
