# FINDING: gimpel was vendored from upstream's SNOBOL4 edition and graded against a SPITBOL oracle — 18 of 28 "outside the SPITBOL baseline" rows were our own vendoring choice

**Seat:** hq_P · **Date:** 2026-09-11 · **Ordered by:** Lon, in-chat
**Landed:** corpus `60920eec7`

## Lon's word

> the gimpel programs have two versions, one SNOBOL4 and one SPITBOL … Catspaw had both. We want to
> support the SPITBOL versions. … get our corpus repo with the proper SPITBOL versions of Gimpel and AI
> SNOBOL.

He is right, and it overturned both the ceo's brief and my own first answer.

## What we had

`/home/resources/gimpel` ships `SNOBOL4/` and `SPITBOL/` **side by side**. This package was vendored from
`SNOBOL4/` — byte-identical after CRLF stripping, with only include paths rewritten
(`-INCLUDE "sqrt.inc"` → `"SQRT.sno"`). We then graded that edition with `sbl -bf`. **The oracle is
SPITBOL.**

⛔ **So every refusal the package recorded as a property of the program was, for these files, a property
of our vendoring choice.**

Upstream says it in its own words — `SPITBOL/SQRT.INC` begins:

> `* SQRT.inc - SQRT is a built-in function in SPITBOL,`
> `*	     therefore the entire routine is commented out.`

while `SNOBOL4/SQRT.INC` `DEFINE`s it. That is exactly **ERROR 248, redefinition of system function** —
the largest class in `OUTSIDE_SPITBOL_BASELINE.tsv` (9 rows). The same shape runs through the file:

| class | rows | what it really was |
|---|---|---|
| 248 redefinition of system function | 9 | SNOBOL4-edition includes redefining SPITBOL built-ins |
| 042 protected variable, `BAL.sno(11)` | 7 | `BAL.INC` is **SNOBOL4-only**; SPITBOL ships `BALX.INC` (`BAL` is a SPITBOL built-in pattern) |
| 116 / 160 inappropriate file spec | 6 | SNOBOL4+ puts the file name in a **fourth** argument; Catspaw takes it **third** |

## It looks exactly like a fixture problem, and is not

The ERROR 116 rows read as a missing data file or a wrong cwd — the ceo's brief proposed curing them that
way, and the package's own reason column called it *"the same environment class"*. **I staged every
upstream `.IN` under the lower-case names the programs open, and it changed nothing — still ERROR 116.**

Minimal witness, same directory, same fixture present, only the argument position differing:

    INPUT(.V,5,,'phrases.in')  -> ERROR 116          INPUT(.V,5,'phrases.in')  -> reads the file
    OUTPUT(.D,10,,'asmtemp')   -> ERROR 160          OUTPUT(.D,10,'asmtemp')   -> opens it

Documented in the oracle's own manual (v3.7 p.12, *Converting to SPITBOL*): *"SNOBOL4+ places file names
in a fourth argument."*

## Result

**18 of the 28** outside-baseline rows no longer draw a SPITBOL error. Still refused, named: `BAL_driver`
(042 — the module SPITBOL dropped), `SNOPUT_driver` (038), `INFINIP_driver` (022), `PHYSICAL_driver`
(002), `FTRACE_driver` (248), `RSEASON_lib_driver` (041), `TRIG_driver` + `VISIT_driver` (022),
`TIMEGC_driver` + `TIMER_driver` (285).

⛔ **"No longer refused" is not "graded."** Several answer 0 lines because their drivers run on empty
stdin; refs and stdin scripts are still owed. `OUTSIDE_SPITBOL_BASELINE.tsv` was deliberately **not**
touched — the denominator is the coo's.

## Two corrections to the brief, both measured

- **The two ERROR 285 rows were never among the gradeable ones.** `TIMER_driver`/`TIMEGC_driver` are
  already ruled NONDETERMINISTIC in `UNGRADABLE.tsv` on the cfo's two-run evidence: resolving their
  includes only makes them *build* before they become ungradable for a permanent reason.
- **The count of eight was right; my own recount of six was wrong.** `ASM_driver` names both 160 and 116,
  so it is one row in two categories. I checked this rather than picking a number, because the
  occurrence-vs-row confusion is the same one that put a doubled count into a gate header last week.

## The control arm is the part worth keeping

**The first cut re-vendored everything and destroyed deliberate local state** — the cfo's DOS include
aliasing in `TIMER.sno`/`TIMEGC.sno` (recorded in `UNGRADED.tsv`) and rewritten commented-out includes in
four more: **six files whose two editions are byte-identical, changed for nothing.** The rule that fixed
it — *re-vendor only what actually differs between the editions* — came from the check, not from
foresight: **"did any file change whose two upstream editions are the same?"** ⭐ That question is worth
more than the fix, and it belongs in any re-vendoring.

The `_lib` collision mapping was likewise **read out of the tree, not invented**: where upstream ships a
module and a program under one basename (`INFINIP`, `RSEASON`), this package puts the program at
`NAME.sno` and the module at `NAME_lib.sno`. My first pass silently mapped both to one file.

Over all 117 checked-in refs, before and after: **111 matched before, 110 now.** `RAMM_driver.ref` was
re-cut in the same commit because its **source** legitimately changed (the editions carry different Knuth
constants: `3141. + 110795., 524288.` vs `3141 + 11079., 524288`); deterministic ×3 before minting.

⛔ **One tolerated red, named:** `DEXTERN_driver`. `DEXTERN` is a **template** module in both editions —
SNOBOL4 ships an inert placeholder the driver worked around; SPITBOL ships
`INPUT(.LIB_FILE,.LIB_,"Library File Name")`, a placeholder that **executes** and needs `LIB_` bound to a
channel before the include (supplying a file of that literal name does not satisfy it — measured). Its
driver's own header documents the SNOBOL4 placeholder by name. Routed for driver rework rather than
binding vendored upstream source unilaterally.

## AI SNOBOL needed nothing — verified, not assumed

`packages/snobol4/aisnobol` is **already** the SPITBOL edition: `ATN`, `BUILDLIB`, `ENDING`, `HSORT`,
`KALAH`, `WANG` are byte-identical to their `.SPT` upstreams, and `SIR`/`TEST` are the `.SPT` plus one
deliberate `-INCLUDE "SPITCORE.sno"`. Lon named both packages; only gimpel was on the wrong edition.

## The class

⭐ **An exclusion reason written from the symptom the oracle printed.** A diagnostic names **where** a
program died, never **why** — hq_R said the identical thing to me an hour earlier, after three csnobol4
misclassifications taken from ref error text. Here, 18 rows carried a cause nobody had probed, and the
wording *"environment class"* actively pointed the next reader away from it. **A package can accumulate a
baseline that is mostly a record of one unexamined decision.**
