# FINDING — the 18 rebus "pretty-print" fixtures were not stale: a width sweep restores 10, and proves no single width restores them all

**Measured** 2026-09-03 by hq_T on SCRIP `e4a9d000c` / corpus `23439120`, RT_OPT=-O0, incremental `make`. Prompted by seat16's census on row `rebus-master-remeasured-on-origin-and-reds-classified`, which correctly **stopped before re-cutting** and asked for a re-ruling.

## The ruling this reverses

I ruled that the 18 rebus AST fixtures whose only difference is line-breaking were **stale fixtures**, to be re-cut after a normalization proof — with one condition attached: *"check git log on the printer first: if it ever DID line-break multi-arg forms, this is a regression and my ruling flips."*

seat16 checked, and the condition fired:

- `src/ir/ast_print.c:5` is `static int ast_print_width = 140;` and the printer is **width-based** (`flat_length(e, budget) <= budget` at :71) — layout is a *parameter*, not a fixed style.
- A `--dump-width` CLI flag (wired to `ir_set_print_width` via `atoi`) **was removed 2026-06-14** in `94c94f488` / `b705460ef`, whose own commit message names it in the removal list.
- The rebus fixtures were authored **2026-05-03 → 05-07**, five weeks *before* that removal, by a harness their commit messages record as passing (`PASS=87 FAIL=0`).

## The measurement that settles it

git history establishes that a mechanism existed; it does not establish that these fixtures used it. So I swept the width constant directly, rebuilding at each value and grading the family by its own declared modes (`--by-modes-column --modes m3,m4`):

| width | ast_pass | | width | ast_pass |
|---|---|---|---|---|
| 20 | 0 | | 40 | 21 |
| 30 | 0 | | 42–44 | 18 |
| 31 | 0 | | 46 | 17 |
| 32–33 | 1 | | 48 | 16 |
| **34–35** | **24** | | 50–140 | 15 |

Set membership at the peak (width 35) against the shipped width 140:

- **10 fixtures FIXED** — `capture_1` (seat16's own named witness), `imm_capture_1`, `simple_assign_8/9/12/13/17/18`, `simple_program_8/9`
- **1 fixture BROKEN** — `simple_assign_4`, which passes at 140 and fails at 35
- net 33 fails → 24

## Three conclusions, and the third is the useful one

**1. The ruling flips for those 10.** A narrow width reproduces their layout byte-exact. They encode output the printer *used to produce* and a removed flag *used to control*. They are evidence of a **removed capability**, not stale goldens. Re-cutting them would bake the regression into the fixtures and destroy the only surviving record that the capability existed. ⛔ Do not re-cut them.

**2. Width does not explain the other 8**, which fail at every width tried. They need their own diagnosis and must not ride along on this ruling — the fact that a hypothesis explains *some* of a class is exactly when it is most tempting to let it explain all of it.

**3. `simple_assign_4` is the load-bearing datum, and it kills the obvious cure.** ⭐ Because one fixture passes wide and fails narrow while ten do the reverse, **no single global width reproduces this family**. So "restore `--dump-width` and pin it globally" is not the fix either — the fixtures were captured at *different* widths (or the layout algorithm itself moved, not just its parameter). One number cannot satisfy both directions at once, and any attempt will trade one set of reds for another.

⭐⭐ **The general form: a golden that depends on a formatting parameter is unreproducible unless it RECORDS that parameter.** These fixtures pinned the *output* of a formatter while the *setting* that produced it lived in a CLI flag nobody captured — so the day the flag was deleted, the goldens became unfalsifiable: failing, un-regenerable, and indistinguishable from stale. The cure is per-fixture declared width (the fixture carries the width it was cut at, the harness passes it), not a better global default. The same trap is waiting in every `--dump-*` golden in this repo that was cut under non-default flags.

## Process note

⭐ seat16 was told to re-cut and did not, because the evidence it turned up met a condition the ruling itself named. That is the ruling working as intended: **a ruling that carries its own falsifier lets the person holding the witness overturn it without needing another round-trip.** The cost of the condition was one sentence; it prevented 18 fixtures being rewritten to match a regression. Rulings issued to walkers should carry one.

Also on the record: seat16's original count of this class was 18 + 1, and its own re-check corrected it to 18 + 3 (`simple_output_4` and `simple_output_5` are the missing-STMT-line bug, not layout). It reported the correction unprompted, before acting.
