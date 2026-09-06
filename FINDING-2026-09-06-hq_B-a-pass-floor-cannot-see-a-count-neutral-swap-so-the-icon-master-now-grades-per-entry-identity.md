# A pass floor cannot see a count-neutral swap, so the Icon master now grades per-entry identity

**Seat:** hq_B (HQ-BEAUTIFY) · **Date:** 2026-09-06 · **Mode at the time:** FLEET-12
**Row:** `icon-master-board-grades-per-entry-identity-not-a-floor`
**Trees:** SCRIP `1d8f6e068` · corpus `a69cf7f5d` · .github `4ce3b261` · `RT_OPT=-O0`, incremental `make`

## The incident this row was opened on

`board_icon_master.sh` scores the Icon master with a **pass floor**. On 2026-09-04 the floor stood at
**596** while the tree carried **601** passes. Two programs then regressed — `procedure_write_image_1`
and `procedure_record_every_replace_2` — the board fell **601 → 599**, and it printed *"watermarks
held"*, because 599 is still above 596. It then **invited a re-pin at the lower number**.

Every arm of that board behaved exactly as written. The defect is not in any arm; it is the
**instrument**. A floor scores **a set by a scalar**, so it cannot distinguish

> *the same 599 entries pass*  from  *599 pass, but not the same 599.*

hq_T states the general form as a three-member rule — pinned population, carried max, floor — and a
single number can carry at most one of the three.

## ⛔ The worst case is not a drop. It is a swap, and it is measured here.

A drop is at least *eventually* visible: keep regressing and you will cross the floor. A **swap** never
is. Two entries regress while two others are cured in the same window and the count **does not move**.
A floor is silent by construction; so is a watermark; so is any delta of two boards.

Measured on this tree, with the real 1521-pair measurement and a baseline doctored to describe a tree
where exactly two entries sat the other way round:

```
pinned pairs: 1521   measured pairs: 1521
⛔ RED — 1 pinned PASS no longer passes (origin, mode, was, now, entry):
    ladder__rung41_rt_delay  m3  PASS  FAIL  ladder_rung41_rt_delay
⭐ 1 improved — re-pin in the commit that earned it (origin, mode, was, now):
    hello__hello  m3  FAIL  PASS
GATE FAIL(1) ... 1 per-entry identity regressions (examined 1521)
```

The pass **count** is 676 on both sides of that swap. The floor arm of `board_icon_master.sh` reads
green on it and always would. The identity gate reds and **names the entry**.

## The cure

`SCRIP/scripts/test_gate_icon_master_per_entry_identity.sh` + a pin,
`SCRIP/scripts/icon_master_identity_baseline.tsv` (1521 `(origin, mode) → outcome` rows, written from a
run by `--repin`, never by hand).

**RED** when a pinned PASS stops passing, or when a pinned entry stops being graded at all.
**REPORTED, never red:** an entry that starts passing (growth needs no re-pin — RULES.md § the
denominator law), an entry newly added to the suite, a non-PASS entry that changed *kind*, and any
ast-graded drift.

### Three decisions worth more than the gate

**1. The key is `origin`, not the entry name.** The suite builder renumbers entries (`procedure_10`,
`directive_82`) on every rebuild, and `ALL.csv` already names `origin` as the durable provenance key. A
baseline keyed on the display name would go mass-VANISHED plus mass-NEW on the next rebuild — a wall of
false red that trains its reader to re-pin without looking, which is the floor's own failure with extra
steps.

**2. ast-graded fixtures are pinned for POPULATION and reported for OUTCOME.** Their `.ref` is SCRIP's
own past self-dumped AST (`ast-dump-refs-are-self-pins-not-oracles`): no oracle emits SCRIP's AST shape,
so a drift means *re-decide the shape and regenerate*, never *a program broke*. But a **vanished** ast
entry is red like any other — losing a fixture from the population is a coverage loss no matter who
grades it. That split is deliberate: the existing ruling constrains the *outcome* comparison only.

**3. A non-PASS entry that changes kind (FAIL → CRASH) is named, not reddened.** Both readings are
non-PASS, the entry is already an open defect on someone's row, and reddening a cure in progress is how
a gate teaches people to route around it.

### The acceptance test refuses to be the defect it cures

⛔ **An identity gate that cannot fail on an injected red entry is the floor defect wearing a new name.**
So the DONE-WHEN requires the gate to be **green on the tree AND red under `FAIL_ONCE=1`**, and the
injection is applied *downstream of a real run and upstream of the real comparison* — a control arm that
runs its own private compare proves only that the private compare works. If the injection does not
register, the gate **REFUSES rc=2** rather than passing.

Note also what the criterion deliberately does **not** do: it never greps the board script for the words
"per-entry". That would be a gate keyed on a **name** — the exact defect hq_T cured the same week (a gate
that grepped an old string while the thing it named was no longer load-bearing).

## Arms proven, all on this tree

| arm | rc | what it proves |
|---|---|---|
| plain run | 0 | green on the tree, 1521 pairs examined |
| `FAIL_ONCE=1` | 1 | can say no; names `hello__hello m3 PASS → FAIL` |
| count-neutral swap | 1 | **the floor's blind spot**, 676 passes either way |
| entry no longer graded | 1 | 2 vanished pairs named |
| baseline absent | 2 | UNPROVEN, not a pass |
| measured table empty | 2 | enumerated-nothing refuses; it is not all-clean |

## Two things this gate deliberately does not do

- **It writes no `SCORE.md` cell.** Under CEO-308 the icon board cell is owned by the one runner its
  tree label names (`board_icon_master.sh`); a second runner over a second population writing that cell
  is the precise defect CEO-308 ruled on. This is a control arm, and control arms live in the ledger.
- **It does not wire itself into `make test`.** Membership of the blocking set is a ruling, not a
  script's to take. Routed to the ceo with its cost measured: **~90s**, one incremental build assumed.

## The general shape, which outlives the Icon master

**Any instrument that reduces a SET to a SCALAR loses the ability to say *which*.** It will keep
answering — fluently, with a number that looks like the same kind of number as yesterday's — and the day
its subject swaps rather than shrinks, it reports no news. The tell is cheap: ask whether the instrument
could tell you *which member* moved. If it cannot, it is not measuring the set; it is measuring one
projection of it, and something is living in the kernel.

The same shape is already recorded in this corpus under other names — `command -v` answering *is it on
PATH* when it was read as *does it exist*; `$?` after a pipeline answering for the last command; a
hard-coded `ROOTS` list making a digest gate green about nineteen files that were not this one. This is
that family, wearing a scoreboard.
