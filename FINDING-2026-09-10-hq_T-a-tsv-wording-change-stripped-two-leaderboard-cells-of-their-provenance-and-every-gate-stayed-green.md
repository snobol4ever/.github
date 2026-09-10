# FINDING — a .tsv wording change stripped two leaderboard cells of their provenance, and every gate stayed green

**Seat** hq_T · **Date** 2026-09-10 · **Mode** NONET · **Row**
`package-shipped-per-lane-printed-by-the-runner-not-transcribed` · **Trees** SCRIP `30b30101b`, corpus
`0d985e3bc`, RT_OPT `-O0`, incremental `make` (rc=0) · **Cures** corpus `0d985e3bc`, SCRIP `30b30101b`

## What happened

Two seats filed the same ceo ruling into one file four hours apart. CEO-527 ruled arizona's
`general/cfuncs` and `general/extlvals` outside the Arizona baseline; the cfo wrote them into
`corpus/packages/icon/arizona_tests/UNGRADABLE.tsv` at corpus `eb777f009`, and I wrote them again at
`1d31f19b9` as mirrors of the `OUTSIDE_ARIZONA_BASELINE.tsv` rows I had just cut, **without first
reading whether the ruling was already in the file I was mirroring into**. 38 data rows, 36 distinct
programs.

The duplicate is not what broke. `lib_inventory.sh` has an internal-duplicate arm that would have
named it, but an earlier arm fires first: the older copy's evidence clause reads
`SCRIP: 'cannot find "libcfunc.so" on path ". ."'`, and a row citing our own compiler beside the
oracle's reason is **refused deliberately** (the arizona `general/tpp.icn` precedent — while our half
stands beside the oracle's, a reader cannot tell whether the ruling would survive without it). So
`inventory_line` for arizona returned **rc=2 at any graded count**, and the duplicate arm was never
reached.

## Why nothing noticed

Every runner calls the body like this:

```sh
INV_LINE="$(inventory_line "$TOTAL" 0)"
if [ -n "$INV_LINE" ]; then echo "$INV_LINE"; else echo "⚠ inventory refused (above) ..." >&2; fi
```

⭐ **The refusal is silent by construction, and that design is correct.** A bookkeeping failure must
never red a suite board (`gate_score_row`'s own doctrine). The consequence is that an empty
`INV_LINE` contributes nothing to the `--text` splice `${INV_LINE:+ · $INV_LINE}`, the runner's exit
status never moves, and the leaderboard cell **reverts from a runner-written `PACKAGE_INVENTORY`
clause to transcribed prose** — which is the exact defect this row exists to abolish, arriving through
the row's own instrument.

⛔ So a **wording change in a data file** demoted a measured cell to a transcribed one, on two
packages, with every gate green. `icon/arizona` and `icon/ipl` are both off the board's runner-written
set today (ARM 19: `pinned packages holding their own clause=6/8`).

## The general form

ARM 19 of `test_gate_package_runners_print_the_inventory.sh` was written this morning on the lesson
that *a cure landing in a CELL of a file twelve seats rewrite all day is protected by nothing unless
something re-reads the cell.* This is its sibling one level down:

> **A refusal deliberately made NON-FATAL is protected by nothing unless something calls it on
> purpose.** Non-fatal is the right design, and it converts a loud instrument into a quiet one at
> exactly the moment it fires. The cure is not to make it fatal in the runner — it is to call the same
> body somewhere a red is free.

And the coverage shape that let it through is worth naming on its own, because the gate looked
thorough: **arms 1–16 grade the shared BODY against mktemp fixtures, exhaustively, and nothing graded
its DATA.** Sixteen arms of careful fixture coverage over `lib_inventory.sh`, and not one call against
the eleven real sidecar pairs the runners read. Fixture coverage of a validator says nothing about the
validity of what it validates.

## Cures

1. **corpus `0d985e3bc`** — one row per program in arizona's `UNGRADABLE.tsv`, keeping the mirrors that
   state the oracle's reason on its own; the cfo copy's additive facts folded into
   `OUTSIDE_ARIZONA_BASELINE.tsv` where the measurement lives (the exported entry is
   `int f(int argc, descriptor *argv)` with `argv[0]` the return slot over iconx's own `struct descrip`
   and `icall.h` tag constants, reached only through the FPATH iconx sets — the implementation-identity
   class, CEO-514, with `&version` and `&allocated`). `inventory_line` arizona rc=2 → rc=0.
2. **SCRIP `30b30101b`** — **ARM 20**, which calls the shared body on the eleven live sidecar pairs,
   ratcheted BY NAME (ten pinned). It deliberately does **not** grade the arithmetic: the bucket sum
   needs a graded count only a suite pass produces, and under ONE RUNNER ONE BOARD (CEO-523) this gate
   may not run one — so a `buckets do not sum` refusal counts as clean here and every other arm speaks.
   Extension comes from each sidecar's own name column, never a lang→ext map. Backlog **measured before
   wiring** (the ARM 7 / CEO-520 criterion): 1 of 11. Validated by running five paths, including an
   internal duplicate in a pinned package — the arizona class itself.

## Named, not fixed

1. ⛔ **`icon/arizona`'s board cell needs one arizona pass from the one runner** to regain its clause.
   The root cause is cured; the cell cannot be typed back (a transcribed restatement of a measured
   number is this row's own defect wearing the cure's clothes).
2. ⛔ **`icon/ipl` will NOT regain its clause from a board pass** — its root cause is open. Its
   `gincl/maccolor.icn` row states the oracle's compile refusal verbatim, upstream's control on the
   unmodified file, **and** our agreement with both. Our mention there is an **agreement control**, not
   failure-as-reason: it strengthens the ruling rather than substituting for it. The honesty arm cannot
   tell the two apart and by its stated doctrine must refuse anyway. That is an instrument limitation
   in hq_R's lane, not a lie in the row — **asked to the ceo, not resolved here**, and never worked
   around by rewording to dodge the regex (ARM 20's own CURE text forbids exactly that: a synonym that
   evades the check is the defect it hunts).
3. `_inv_names` spends **three subprocesses per row** (`printf | cut` ×3); over ipl's 851 declarations
   that is most of ARM 20's 7.7s. A shared-body inefficiency, named here, not cured here — it changes
   refusal semantics for twelve runners and wants its own mutation proof.
4. The `Makefile:158` comment promised `~1s MEASURED, mktemp-only`. Corrected to the measured ~8s with
   the reason, rather than left to mislead the next reader.
