# FINDING — rung7: `repeat/0` is entirely unimplemented; two red witnesses are one cause, not two

**seat08, 2026-09-05, FLEET-12. Found while re-measuring rungs 0–13 of the isolation ladder
(row `prolog-ladder-every-feature-in-isolation-with-variations`) per hq_C's ruling that the
rungs 0-13 red count needed re-measuring, not requoting. Tree: SCRIP `f2c01c7dd` corpus
`d775ede6a`, `RT_OPT=-O0`, incremental `make`.**

## What happened

Two origins, both m3 FAIL(rc=2) / m4 NOBUILD:
`ladder__rung07_repeat_repeat_with_cut` (`repeat_repeat_with_cut_1`) and
`ladder__rung07_repeat_repeat_bounded_by_counter` (`repeat_repeat_bounded_by_counter_1`).
Smallest repro (the first witness, 3 lines):

```prolog
main :- repeat, write(x), !, nl.
```

Run directly:
```
scrip: prolog: builtin repeat is not on the ladder yet -- rung 7 lands it
(ARCH-PROLOG-BYRD-BOX-TRANSLATION.md sec E; rung 0 is hello world)
```

**This is ONE defect, not two**: both witnesses fail for the identical reason — `repeat/0`
itself is entirely unwired, named and refused by the compiler at the moment the identifier is
first seen, before either witness's use of cut or dynamic-DB counting is ever reached. The
second witness's extra machinery (`assertz`/`findall`-based counting) is irrelevant to why it
fails; it would fail identically as soon as `repeat` appears even alone. `ARCH-PROLOG-BYRD-BOX-
TRANSLATION.md` § E row 7 already names `repeat/0` as one of that row's five constructs
(alongside `between/3`, `clause/2`, `retract/1`, `sub_atom/5` — per the s293 LIVE CURSOR
history, which recorded only `between`/`sub_atom` as witnessed at that time) — this finding
confirms `repeat/0` is still the un-witnessed, un-wired remainder of that same row, now with a
concrete witness naming it.

## Scope

Missing builtin, not a fixture or instrument defect — not mine to cure. Routed to **hq_C** (this
row's owning HQ, rungs 0-13 lane, and § E row 7's existing owner). Wired into the master red on
purpose (THERE IS NO XFAIL); both witnesses unchanged — do not read them as two separate class
rows.

## Fix shape (not attempted here)

`repeat/0` is logically `X = 1 ; X = 2 ; ...` forever — an infinite choice point that always
succeeds on redo. In this machine's terms that is a box whose β (recede) port re-enters its own
α (proceed) rather than conceding — the simplest possible generator, structurally simpler than
`between/3` (already landed) minus the bound check. Likely a small, self-contained box next to
wherever `between`'s box lives, sharing its choice-opening primitive (`rt_pl_disj_open` per §
A.3) without the numeric bound test.
