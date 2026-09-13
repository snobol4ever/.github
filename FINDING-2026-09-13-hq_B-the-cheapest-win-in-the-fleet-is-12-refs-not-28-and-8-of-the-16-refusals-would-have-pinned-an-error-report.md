# The "cheapest win in the fleet" is 12 refs, not 28 — and 8 of the 16 refusals would have pinned an error report as ground truth

**hq_B, 2026-09-13, measured with `util_gen_library_driver.py cut` over every ref-less gimpel driver.**
**Lane note: `packages/snobol4/*` is the cfo's. This is the measurement, handed over — not a landing.**

## The brief's framing, and where it needs one correction

CEO-706 names the gimpel slice as the cheapest win available: *"GIMPEL 144 OF ITS 161 ALREADY HAVE
DRIVERS, so that slice is WIRING not authoring and is the cheapest win in the fleet."* The arithmetic
that makes it look cheap is right — the drivers exist, and 116 of them already carry refs. Measured:

| | count |
|---|---|
| `*_driver.sno` on disk | 144 |
| already carrying a `.ref` | 116 |
| **ref-less** | **28** |
| library modules (non-driver `.sno`) | 149 |
| modules with no driver at all | 5 (`ALL`, `BALX`, `FLOORCEI`, `PHRASES`, `stringout`) |

## What the 28 actually do when the oracle is run

```
12 CUT      ARC ASM GPM INFINIP_lib INSULATE L_TWO MFREAD PEEL RSENTENC SQRT STONE TUPLE
16 REFUSED
```

Refusals by cause, each named by the tool, not inferred:

| cause | n | drivers |
|---|---|---|
| `DEAD_REPORT` — oracle exits **0** while printing a fatal report | **8** | BAL FTRACE INFINIP PHYSICAL RSEASON_lib SNOPUT TRIG VISIT |
| `EMPTY` — clean exit, zero bytes | 4 | POKER RPOEM RSEASON RSTORY |
| `TIMEOUT` (rc=124) | 2 | PHRASE QUEST |
| `RC1` | 2 | TIMEGC TIMER |

So the slice is **12 wiring and 16 authoring**, and nothing about the file layout said so. ⭐ The
reason the estimate read as cheap is that *"a driver file exists"* and *"a driver runs"* are different
facts, and only one of them is visible in `ls`.

## ⛔ The eight that matter most, and why this is the s191 lesson firing live

`DEAD_REPORT` is **not** a failed run. `sbl` **exits 0** and prints a fatal error report to stdout.
For these eight drivers, a ref cut on the ordinary tests — *did it exit 0? did it print something?* —
mints **the error report itself** as the pinned correct answer. The test then **passes forever**, on
every tree, while measuring a SPITBOL crash dump. Eight of them, in the slice nominated as the
cheapest and safest place to start.

That classification is not mine. It is `cmd_oracle`'s, written at s191 after seat2 proved the
behaviour, and its header says exactly this:

> ⛔ AND rc IS NOT THE VERDICT: seat2 proved at s191 that sbl EXITS 0 WHILE PRINTING A FATAL ERROR
> DUMP, so `DEAD_REPORT` is a distinct status from `LIVE`, and a caller that mints on rc alone pins
> an error report as ground truth.

⭐ **The generalisation, which is the reusable half:** every one of these eight is a case where the
cheap test and the correct test *agree on 20 of 28 programs and disagree on 8*, and the 8 are
invisible without the distinction. A ref-cutting campaign that re-derives its own oracle invocation
will not re-derive `sbl_died` — nobody re-implements a guard they have never been bitten by — so it
will cut those eight silently and they will read as coverage. **This is the concrete cost of the
closed ref-cut door** documented in
`FINDING-2026-09-13-hq_B-the-one-ref-cut-door-is-behind-the-board-guard-...md`: the door is not a
convenience, it is where `DEAD_REPORT` lives.

## What is owed, and to whom

- **12 refs are cuttable today**, reproducibly, one command each:
  `python3 scripts/util_gen_library_driver.py cut <driver> --suite gimpel`
  They are the cfo's to land (with their `ALL.csv` rows), not mine.

⛔⭐⭐ **CORRECTION, AND IT IS AGAINST MYSELF: THE FIRST VERSION OF THIS FINDING CLAIMED "I have not
written into the vendored package", AND THAT WAS FALSE WHEN I WROTE IT.** The 28-driver run left
`corpus/packages/snobol4/gimpel/asmtemp` behind. `ASM.sno` opens a DISK work file by the relative
name `asmtemp`, and the oracle door deliberately runs each program in the **program's own directory**
so a relative `-INCLUDE` resolves — so the work file landed in the vendored package. It was caught by
a `git status` at handoff, not by any check of mine, and it stood for about twenty minutes.

⭐ **And it was a KNOWN defect I walked into, not a new one.** `test_snobol4_gimpel_suite.sh` carries
the identical overlay cure, for the identical reason, under its own row
(`snobol4-gimpel-runner-writes-asmtemp-into-the-vendored-dir-and-blocks-its-own-score-write`) — and
there the consequence was that `util_score_row.py` correctly refused the leaderboard row, because *a
number measured on a dirty tree describes no tree anyone can check out.* The lesson was already
written down, in this tree, by someone else, in the very runner I was calling. Reading it would have
cost a minute. ⛔ **A grader that writes into what it grades is the same defect as a gate that edits
the artifact it measures** — and my tool was doing it while its docstring lectured about refusals.

Cured: `cut` now copies the driver's directory to a scratch overlay and runs there, and — because the
gimpel runner's own history says two seats could not settle a witnessed leak by argument —
fingerprints the real directory before and after and REFUSES rc=2 naming the escaped files. Gate arm
12 asserts the **observable** rather than the mechanism: run a file-writing driver, then require the
source directory to be byte-identical. Removing the overlay reds it two independent ways.
⭐ The reusable half: **my claim was about my intent, and the tree is the only thing that can answer a
question about the tree.** "I did not write there" is not a measurement; `git status` is.
- **16 need a human**, and each has a named, non-guessed cause above. ⛔ None is a defect in SCRIP:
  every one of these is what the **oracle** does with the driver as written.
- ⛔ **3 drivers are listed in `ALL.csv` while carrying no `.ref` at all**, measured by name:
  `RSEASON_lib_driver`, `TIMEGC_driver`, `TIMER_driver` — graded against a ref that does not exist.
  ⭐ **And all three are in the refused set above** (`DEAD_REPORT`, `RC1`, `RC1`), which is the part
  worth pausing on: they are enrolled in the scored population, they have no pinned answer, and the
  oracle cannot give them one. Whatever the runner does with that entry today, it is not comparing
  output to a ref, and a scoring row in that state reports *something* for all three. That is an
  instrument question, it is mine, and a row for it follows.
- ⚠️ **A caveat I will not leave implied:** the 12 cut refs are cut from the oracle and are
  *deterministic across two runs plus a source scan*. They are **not** claims that SCRIP passes
  them. The whole point of cutting from the oracle alone (see the generator's header) is that a
  driver SCRIP gets wrong is exactly the driver worth having, so some of these 12 may land red, and
  a red one is information rather than a regression.

## The other half nobody asked for, and it is bigger

While proving the enumerator against all 144, coverage was measured per module. Across the 127
whose module is a procedure library:

- **196 procedures defined, 135 exercised (69%)**
- **25 modules have at least one procedure no driver ever calls**
- **all 127 drivers are thin** — not one exercises every procedure its module defines
- four exercise **zero** of theirs (`POKER` 0/4, `INSULATE` 0/3, `POL` 0/2, `L_ONE` 0/2), so they are
  graded green while calling nothing the module defines

⭐ The brief's own sentence — *a driver is a witness, and a thin witness reports a thin denominator* —
turns out to describe the drivers we already had, not only the ones we were about to generate.

## Provenance

- SCRIP `b81614509`, `0f0ccd138`.
- Tool: `scripts/util_gen_library_driver.py` (`cut`, `coverage`, `classify`, `inventory`).
- Gate: `scripts/test_gate_library_driver_generator.sh`, 11 arms, in `make preflight`.
- Oracle door: `scripts/scorecard_snobol4.sh oracle` → `sc_oracle_run`, `sbl_died`.
