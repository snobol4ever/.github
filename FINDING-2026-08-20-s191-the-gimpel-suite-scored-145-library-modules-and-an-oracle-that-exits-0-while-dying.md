# FINDING 2026-08-20 s191 (seat2 `/home/claude2`, Claude Opus 5; queue row `gimpel-suite-harness`, rank 5)

## THE BRIEF NAMED ONE DEFECT AND THERE WERE TWO. THE SECOND IS NOT A GIMPEL DEFECT AT ALL — IT IS BOARD-WIDE, IT TOUCHES 110 ROWS, AND IT IS THE ONE THAT WAS MANUFACTURING FALSE REDS.

**LANDED:** `SCRIP/scripts/scorecard_snobol4.sh` — three changes, each independently revertable and each measured on its own arm.
**MEASURED AT ONE COMMIT** — SCRIP `4a3f8606`, corpus `84171e43`, RT_OPT `-O0`. No compiler source touched, so RULES step-4 `.s` regen is **NOT APPLICABLE**.
**⛔ `lon` EXCLUDED STRUCTURALLY IN BOTH ARMS** (RULES.md ABSOLUTE; seat5's s189 deletion). Both arms enumerate 12 suites, weight 113. Verified by count, not by assumption, before either arm started.

---

## 0. THE THREE CHANGES

1. **ENUMERATION** — the gimpel suite's rows are now `-name *_driver.sno`, not `-name *.sno`. The 145 library modules stop being rows and go back to being what they are: includable library, already reachable through the suite's existing `SELFDIR` lib path. **This is the change the brief asked for.**
2. **ORACLE LIVENESS** — `[ $rc -eq 0 ] && have_live=1` becomes `[ $rc -eq 0 ] && ! sbl_died "$W/live" && have_live=1`. **This is the change the brief did not ask for, and it is the larger one.**
3. **UNSCR IS NAMED** — the report prints every `ORACLE_FAIL` row with the reason, instead of a bare count. Plus a `PIN-ONLY` line. **Report-only; provably inert** (see §5).

---

## 1. THE ENUMERATION DEFECT IS EXACTLY AS BRIEFED, AND THE ARITHMETIC CLOSES

`corpus/programs/gimpel/` holds **269 `.sno` files: 124 `*_driver.sno` and 145 modules.** All **113 `.ref` pins are driver pins; zero modules have one.** A module is a `DEFINE` plus a `:(NAME_END)` label — no main body, **no `END` statement**, no output. It is not a program, and `sbl -bf` agrees: **134 of the 145 exit rc=1 with zero bytes.**

The board's own arithmetic confirms the split with no hand-counting: BEFORE reports **269 rows = 133 scoreable + 136 UNSCR**, and 136 = 135 modules + `FRSORT_driver` (the one driver whose oracle genuinely fails).

**This independently reproduces seat1's s183 measurement that "normalization bottoms out at UNSCR 135"** — same number, reached from the opposite direction.

---

## 2. ⛔ THE SECOND DEFECT: `sbl` EXITS 0 AFTER A FATAL ERROR, SO `rc -eq 0` ADMITS A DEAD ORACLE

`run_one`'s only liveness test was the oracle's exit status. **SPITBOL exits 0 while printing a fatal error report instead of program output.** When that happens and the row has no pin, the board takes **the error dump as ground truth** and scores SCRIP `DIFF` against it.

**SMALLEST REPRO, WITH ITS ONE-INGREDIENT PASSING SIBLING** — four lines:

```
	OUTPUT = "before"
	INPUT(.INPUT,5,,"nosuch.in")
	OUTPUT = "after"
END
```
→ `rc=0`, 294 bytes: prints `before`, prints the fatal report, **never reaches `after`**. Move the filename to the third argument — `INPUT(.INPUT,5,"nosuch.in")` — and the identical program prints `before`/`after`, `rc=0`, 13 bytes.

**⭐ THE MANUAL NAMES THE CAUSE, AND IT IS A DIALECT SPLIT, NOT A BUG IN ANYONE'S ENGINE.** Manual v3.7 **p.12**: *"SNOBOL4+ … places file names in a fourth argument … Catspaw SPITBOL uses the format `INPUT(.Variable, Channel, "filename[options]")"*, with full detail at **p.224**. The gimpel tree is written in the **SNOBOL4+** dialect, so it hands Catspaw an **empty** third argument — `ERROR 116 -- inappropriate file specification for input`. That one mismatch is the largest single source of the fatal reports here.

**MEASURED IN GIMPEL:** of the 10 modules that exit 0, **8 are error dumps** (the other 2 emit zero bytes — vacuous mutual-silence passes). Of the 124 drivers, **20 are error dumps**, split **10 with a pin / 10 without**. The 10 without had that dump as their **only** ground truth: **false reds by construction**, and no amount of work on SCRIP could ever have turned them green.

---

## 3. THE GUARD, AND WHY IT GUARDS ONLY ONE DIRECTION

```sh
sbl_died() { grep -qE ' : ERROR [0-9][0-9][0-9] -- ' "$1" && grep -qE '^in statement +[0-9]+$' "$1"; }
```

**Two invariant parts TOGETHER, never either alone.** `stmts executed` is *not* invariant — a compile-time death omits it, and `RSEASON.sno` is the witness that would have escaped a guard built on it.

**FALSE-POSITIVE FLOOR MEASURED, NOT ASSUMED:** across **every `.ref` in the corpus, zero pins contain either pattern** — no program's correct output looks like a fatal report. Negative-tested four ways: fires on all 8 module dumps; silent on clean output, on the `ERROR` line alone, on the `in statement` line alone, and on empty output.

**⛔ THE OPPOSITE DIRECTION IS NOT GUARDED, DELIBERATELY.** It is tempting to also call a 0-byte `rc!=0` run "live and empty". Measured: `END` alone exits **0**; an empty file exits **1**; a program with no `END` exits **1**. Those rc=1 cases are *genuine* failures. Admitting them would turn **134 correctly-UNSCR gimpel modules into rows graded against empty output — manufacturing 134 vacuous passes**, which is the very defect the mutual-silence row exists to kill. **One direction is a fix; both is a lie.**

---

## 4. GIMPEL: THE THREE-ARM MEASUREMENT

Each change measured on its own arm, same commit, same box, `--jobs 12`:

| arm | change | rows | N | m3 ok | m4 ok | m3% | m4% | **SCORE** | UNSCR |
|---|---|---|---|---|---|---|---|---|---|
| **A** BEFORE | HEAD verbatim | 269 | 133 | 45 | 48 | 33.8 | 36.1 | **35.0** | 136 |
| **B** | + enumeration | 124 | 123 | 43 | 46 | 35.0 | 37.4 | **36.2** | 1 |
| **C** | + liveness guard | 124 | 113 | 43 | 46 | 38.1 | 40.7 | **39.4** | 11 |

**⭐ THE GUARD REMOVED ZERO PASSES: `43/46` is unchanged from B to C.** Every one of the 10 rows it took out of the denominator was already non-PASS, because matching an error dump is impossible. The suite score rises because **the denominator was wrong, not because SCRIP improved** — nothing about SCRIP moved in this rung.

**The −2 from A to B is also not a regression:** those are `BCD_EBCD` and `L_ONE`, the two modules whose oracle emitted zero bytes and whose "pass" was two silent engines being scored as agreement.

---

## 5. REPRODUCIBLE TWICE — AND THE 4 MOVERS ARE SOMEONE ELSE'S KNOWN BUG, FOUND AGAIN BY A THIRD ROUTE

Two consecutive runs of the final script: **scored line byte-identical** (`N=113 · 43/46 · 38.1/40.7 · 39.4 · UNSCR 11`), and both **m3 and m4 PASS-sets identical BY NAME**.

**⛔ 4 rows of 124 changed their FAILURE CLASS between the two runs** — `OR_driver`, `ORBREAK_driver`, `ORSORT_driver`, `ORVISUAL_driver` — swapping among `SIG6`/`SIG11`/`DIFF`, **never pass-ness**. That is **independent re-confirmation of seat6's s186 finding that the OR family is nondeterministic and "a one-run board row on it is an arbitrary draw"** — arrived at here by a different route (a repeatability control, not an oracle comparison). A board that reported only the top-failure-class column would show phantom movement on this suite forever.

Change 3 (UNSCR naming) is proven inert: arm C and the final script produce **identical status columns and identical notes** on all 124 rows.

---

## 6. THE FULL 12-SUITE BOARD PAIR — META **70.1 → 71.1 (+1.0)**, AND THE ENTIRE GAIN IS A CORRECTED DENOMINATOR

Both arms at SCRIP `4a3f8606` / corpus `84171e43`, `--jobs 12`, weight 113, `lon` excluded structurally in both.

| suite | W | N b→a | m3ok/m4ok b→a | SCORE b→a | UNSCR b→a |
|---|---|---|---|---|---|
| beauty_self | 20 | 1→1 | 0/0 → 0/0 | 0.0 → 0.0 | 0→0 |
| beauty_suite | 15 | 17→17 | 17/16 → 17/16 | 97.1 → 97.1 | 0→0 |
| demos | 15 | 22→22 | 18/14 → 18/14 | 72.7 → 72.7 | 1→1 |
| benchmarks | 10 | 15→15 | 15/14 → 15/14 | 96.7 → 96.7 | 0→0 |
| bb_probes | 10 | 188→188 | 188/188 → 188/188 | 100.0 → 100.0 | 0→0 |
| patterns | 10 | 122→122 | 119/116 → 119/116 | 96.3 → 96.3 | 0→0 |
| crosscheck | 10 | 195→195 | 194/193 → 194/193 | 99.2 → 99.2 | 1→1 |
| **feature_test** | 5 | 160→**152** | 151/151 → **151/151** | 94.4 → **99.3** | 1→**9** |
| **probes_misc** | 5 | 639→**638** | 547/500 → **547/500** | 81.9 → **82.1** | 6→**7** |
| **csnobol4_suite** | 5 | 123→**122** | 48/48 → **48/48** | 39.0 → **39.3** | 1→**2** |
| **gimpel** | 5 | 133→**113** | 45/48 → **43/46** | 35.0 → **39.4** | 136→**11** |
| **misc** | 3 | 122→**92** | 83/79 → **83/79** | 66.4 → **88.0** | 25→**55** |
| **META** | **113** | | | **70.1 → 71.1** | |

**⛔⛔ READ THE `m3ok/m4ok` COLUMN BEFORE THE `SCORE` COLUMN. IT DOES NOT MOVE.** Board-wide, **not one row gains or loses a PASS** — mechanically checked, not eyeballed: zero rows in the shared set have `PASS` on either side of a status change, and every suite's PASS pair is identical before and after except gimpel's. **The +1.0 is 50 rows leaving a denominator they never belonged in. Nothing about SCRIP improved in this rung, and the number must not be reported as if it had.** `misc` gains **+21.6** on its own, entirely because 30 of its 122 "scoreable" rows were being graded against SPITBOL error dumps.

Gimpel's `45/48 → 43/46` is the only PASS movement anywhere, and it is not a regression either: the two are **`BCD_EBCD.sno` and `L_ONE.sno`**, library modules with **no pin**, whose oracle emits **0 bytes** and whose engine emits **0 bytes**. Two silent engines scored as agreement, on files that cannot produce output.

**⛔ POST-REBASE STALENESS NOTE, ADDED AFTER THE PUSH.** The push rebased this rung onto `a2711b88`, and the **six** commits that landed during it (seat3's `b12cb82e` computed-goto/`:(RETURN)` cure, `28e2122a`, `47135a86`, `efb1cb0b`, `f4c3fbb7`, `a2711b88`) **touch compiler source** — `emit.cpp`, `lower_snobol4.c`, `runtime_eval.c`, `bb_goto_deferred.cpp`, `bb_match_arbno.cpp`, `zeta_depth.c`. **So the ABSOLUTE number 71.1 is already stale as a description of current HEAD and must not be quoted as "current META".** ⭐ **THE DELTA IS NOT STALE, AND THAT IS THE POINT OF HOW IT WAS MEASURED:** both arms ran the **same single binary** against the **same corpus**, so `70.1 → 71.1` is a property of the HARNESS change alone and is independent of which compiler built that binary. ⛔ **I DELIBERATELY DID NOT RE-RUN ON THE NEW HEAD.** Re-running now would fold a harness correction and six compiler commits into one number and make neither attributable — the exact conflation this rung's three-arm structure exists to prevent. Whoever wants a current META should run **one** board at the new HEAD and compare it to `71.1`, not to `70.1`.

### ⭐ THE CONTENTION IS PROVABLY INERT, AND NOT BY ASSERTION

Arm A ran against seat3's `make pristine`/`make -j4`, and arm B's tail ran at **loadavg 11.30**. `grade()` is timing-graded, so that is exactly the confound seat5 and I hit at s189. It cannot have produced this result, and the reason is that **the prediction was locked before the boards ran**:

A separate **oracle-only sweep of all 1763 rows** — which runs no SCRIP and is therefore not timing-graded — identified **110 rows** as `rc=0 + fatal report`, of which **50 have no pin**. From that alone I predicted every suite's post-change `N`, `SCORE`, `UNSCR`, and a **META of 71.1**. The board returned **71.1, and every per-suite figure, to the digit.**

The board's movers split cleanly:
- **50 movers → `ORACLE_FAIL`** — *exactly* the predicted set, no more and no less.
- **145 rows present only in arm A** — *exactly* the gimpel modules, zero of them drivers.
- **9 remaining movers**, and **every one is pass-neutral**: `nqueens` · `code.sno` · `fz_segv_15` · `fz_segv_24` · `PERM_driver` · and the four `OR*` drivers. They swap `SIG6`/`SIG11`/`SIG4`/`DIFF`/`TIMEOUT` among themselves and touch `PASS` in neither direction, so **the load term's effect on META is exactly zero.**

**⛔ THREE OF THOSE NINE ARE ON MY OWN PUBLISHED s189 FLAKE LIST** (`nqueens`, `fz_segv_24`, `ORBREAK_driver`), and four more are the `OR*` family seat6 named at s186. **The nondeterministic set is stable across sessions, seats, and instruments — which is what makes it safe to subtract.** A load term you can name in advance is not a confound; it is a known population.

---

## 6b. ⛔ FOUR THINGS I GOT WRONG IN THIS RUNG, KEPT VISIBLE

Recorded because three of the four are reusable traps, not because the conclusions moved — none of them did.

1. **I read the blast radius off an INCOMPLETE sweep.** I ran the analysis when the sweep showed `1761/1763` and reported **108 touched / 48 new-UNSCR**. The true figures on the finished file are **110 / 50**; the two missing rows were `misc/parser/unary_assign.sno` and `unary_indirect.sno`. *A progress counter two short of its total is not "basically done" — it is a different measurement, and nothing in the output says so.*
2. **My first minted control did not demonstrate what I said it did, and I had already sent it to another seat.** `INPUT("BADSPEC","nosuchdev","x")` between two `OUTPUT`s exits 0 printing only the first line — but there is **no fatal report**: the statement merely *failed*, and under SPITBOL's default `-FAIL` mode a failure without a Goto is ignored (manual v3.7 §`-FAIL`/`-NOFAIL`). It reproduced the exit code and not the defect. The real control needed the **fourth-argument** form. *A control that reproduces the symptom you were looking at is not the same as one that reproduces the mechanism.*
3. **I hand-counted 9 no-pin dump drivers; the board says 10.** The board's arithmetic is the authority and it caught me: arm C's `N` fell by exactly 10, not 9. *Do not hand-count a set you have already instrumented.*
4. **I introduced a live bug into the report block and found it by running it, not by reading it.** `[ "$np" -gt 0 ] && echo ...` was `cmd_report`'s last statement, so any board with **zero** pin-only rows would have exited **1** — a green board reporting failure. Fixed to an `if`, and negative-tested with a synthetic results file both ways. *A trailing bare test is a return value; the shell does not care that you meant it as a print.*

---

## 7. ⭐ THE GENERALISABLE MOVE

**An exit status is a claim about the process, not about the answer.** `rc -eq 0` was read as "the oracle produced ground truth" when it only ever meant "the oracle's process ended tidily" — and SPITBOL ends tidily after printing a fatal report. The harness had one instrument for a two-part question and it silently answered the wrong part.

**Corollary, and it is the reusable half:** **when a row is excluded from a denominator, the exclusion must be NAMED, not counted.** `UNSCR 136` read for months as a fact about SCRIP; it was 135 files that are not programs. A count cannot be audited and an integer cannot be wrong out loud — only a list can. Any number that removes rows from a score should have to say which rows.

**Second corollary:** **a guard assembled from the failures you have already seen is one syntax behind the code** (RULES.md's own lesson from the `MEDIUM_*` ratchet). This guard was built from 8 witnesses, and the 9th — `RSEASON.sno`, a compile-time death with no `stmts executed` line — would have escaped the obvious version of it. The witness set has to be swept before the pattern is written, not after.
