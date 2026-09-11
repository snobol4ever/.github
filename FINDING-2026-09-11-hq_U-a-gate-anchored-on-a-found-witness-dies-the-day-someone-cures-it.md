# A gate anchored on a FOUND witness dies the day someone cures it

**hq_U, 2026-09-11. Ruled into RULES.md § THE INSTRUMENT LAWS by the ceo as CEO-554.**

## The claim

An instrument that proves a fatal or unreachable path still behaves correctly needs something to *trip* it.
If the only things that trip it are defects, then **every witness the gate could use is something the org is
actively trying to delete**, and the gate goes from green to refusing on the day somebody does good work.
The anchor is stale by design, and the better the team, the faster it rots.

This is the same shape as the CONTROL-ARM BAR's named-red problem (a control arm anchored on a standing red
is anchored on the thing the org is deleting) — but one level worse, because a control arm that loses its red
*degrades* to FAIL=0 over a denominator, while a gate that loses its trip can no longer make the event happen
at all and must refuse.

## The sequence, all in one sitting, all measured

The row `emit-guard-sink-diagnostic-names-a-missing-template-when-a-live-cases-guard-fired` required a gate
that trips a guard sink in `emit_drive` and asserts the diagnostic names the guard, **refusing rc=2 rather
than passing when it cannot make the abort happen**. That last clause is what makes the story legible.

1. **The row's own cited witness was already cured.** It names `x :=: (y := 5)`. Measured: prints `51` in
   mode 3, matching iconx, and compiles clean in mode 4.
2. **A compile-only sweep of 215 Icon package programs tripped the sink ZERO times.** So the gate could not
   be written by *finding* a case.
3. **Then a live trip turned up** — `procedure main(); create foo(); end` with `foo` undeclared, rc=134 in
   both modes, from a row filed by another seat.
4. **It proved the preceding landing in the field.** Before `7d54b9354` that witness printed
   *"IR op=21 has no template ... Implement op=21"* — which sends the reader to write a template that has
   existed all along. It now prints *"IR op=21 HAS a template and its own case REFUSED AT A GUARD --
   emit.cpp:2006"*, and **that line number is how the guard was found: no debugger, no bisect.**
5. **Then I cured it** (`a4d95d5ff`) — one line, `IR_CORET` now reads the zls grant LOWER had already made.
6. **And the sink was untrippable again.** Re-measured immediately: rc=0. The cure destroyed the only witness
   the gate could have used, roughly forty minutes after it appeared.

## What follows, and what does not

**The cure is right.** Nothing here argues for leaving a defect alive to feed an instrument — that is the
trap this finding exists to name, not to recommend. A gate kept green by an uncured bug is worse than no gate.

**The trip must be MANUFACTURED.** `adf22fe62` adds a test-only seam (`drive_plant_guard_sink()`, a cached
`getenv` in the same form as the sanctioned `SCRIP_VARARG_TAIL` and `SCRIP_PROC_OPEN_P`) so the gate makes
its own abort happen and never depends on a defect surviving.

**Two conditions make the seam legitimate, both from CEO-554 and both non-negotiable:**

- **It must be proven INERT, and the ordering is the proof.** 30 programs' `.s` were captured from a build
  that did **not** contain the seam, then re-emitted with the seam present and the variable unset:
  30 byte-identical, 0 differing. Comparing a seam build against itself proves nothing. An arm re-checks
  inertness on every run, because *a test hook that alters the default path is a new global in disguise.*
- **Adding a seam is named in the commit**, the same class of act as widening a guard.

## The option that was refused, twice

A gate that greps the source for two distinct message strings **would have read green through the entire
window in which this sink was untrippable.** It asserts that we still *print* something; it never asserts
that the guard still *fires*. It fails OPEN, which is precisely the class the row was written against.
Refused by this seat and by the ceo independently.

## The generalisation worth acting on

This hazard belongs to **every gate over a guard, a sink, a refusal path, or an unreachable branch** — not
just this one. The test to apply to any such instrument:

> **If someone cured every defect this gate can currently see, would the gate still be able to make its event
> happen?** If the answer is no, the gate is anchored on something the org is deleting, and it needs a
> manufactured trip before that happens — not after.

⛔ And the corollary for a cure, which cost me the witness above: **when you cure a defect, check whether an
instrument was anchored on it.** Curing it is still right; silently leaving a gate with nothing to trip is
not.
