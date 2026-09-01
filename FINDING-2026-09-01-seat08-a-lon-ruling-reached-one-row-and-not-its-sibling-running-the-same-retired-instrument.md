# FINDING: a Lon ruling retired an instrument on 2026-08-30, reached the ONE row it named, and never reached the sibling row running that same instrument — which the picker then served at rank 1 for 37 passes.

**Seat:** seat08 (FLEET-8) · **Date:** 2026-09-01 · **Row:** `raku-frontend-real-world-syntax-gaps` · **Found while:** working that row's `## NEXT`, whose own item 3 says *"RE-MEASURE, do not re-read the mailbox."* I re-measured, and what turned up was not a raku fact.

## THE RULING

Lon, 2026-08-30, in-chat direct to hq_C, recorded at `GOAL-RAKU-100.md:274` (`## ⛔⭐⭐⭐ LON RULING 2026-08-30 — THE BISON/FLEX GRAMMAR IS THE WRONG INSTRUMENT`), verbatim in substance:

> *"You simply take the parser spec from Rakudo/Roast and do mass translation. Is the Raku parser written in Bison/Flex?"* — and, on being shown Raku is not LALR: **"If Raku has non LALR, then you must use another way."**

Raku is not LALR, so `raku.y` **can never be finished**. The replacement is live and already at rung 7: `tools/rakugram/`, a mechanical translation of Rakudo's own `src/Perl6/Grammar.nqp` into recursive descent. Its README states the measured case against the old method: *"construct-by-construct patching of a `.y` was an unbounded search measured at ~3 files of PARSE-FAIL per pass against 924."*

## THE PROPAGATION FAILURE — MEASURED, NOT ASSERTED

The ruling's own text supersedes the incremental-construct strategy **on row `raku-roast-100-percent-compile`**, which it names. That row's baton carries it.

`raku-frontend-real-world-syntax-gaps` patches **the same `raku.y` by the same construct-by-construct method**, and its baton had never heard. Grep over all 1783 lines of that task file, before this pass:

```
rakugram          0        Grammar.nqp        0
LON RULING        0        wrong instrument   0
not LALR          0        recursive descent  0
```

**Passes 35, 36 and 37 are all dated 2026-08-30 — the same day as the ruling — and all three re-measured the `raku.y` gaps without it.** Every one of that row's five remaining kernels is gated on a construct-by-construct `raku.y` patch.

## WHY IT COST SO MUCH: THE PICKER KEPT FEEDING IT

The row is served at **rank 1 by dependency inversion** (it blocks `bench-rivals-raku-pascal`), so `next` hands it to a fresh seat, on `/clear`, every time it is released. Recorded cost: **37 passes**, raw count unmoved at **5/5** since the pass-34 split. The row is also unclosable for an independent reason — all five kernels sit on declined or unruled design surfaces (`start`/`await` declined; `:=` binding/closure-frame **unruled for 17+ passes**, re-verified against a fresh `.github` pull this session; eager-materialization and hyperoperators declined to sibling rows).

So two mechanisms compounded: a ruling that did not propagate, and a picker that cannot know a row's method has been retired.

## THE GENERAL CLASS — this is the part worth keeping

**A ruling is routed to a ROW. An instrument is shared across ROWS.** When Lon retires an instrument, the ruling lands wherever the conversation was, and every other row using that instrument keeps running it — silently, because nothing in a baton, the queue index, or `next` models "which instrument does this row use." Each affected seat then does exactly what its brief says, correctly, and produces nothing.

⛔ **This is not caught by any existing instrument law.** Those govern instruments that report success while doing nothing. Here the instrument reported honestly — 5/5, unchanged, every pass — and the seats read it correctly. What was stale was the *premise*, and a baton has no field for a premise.

**Cheap check any seat can run, and the one I would generalize:** before working a row that patches a specific file or tool, grep that row's own baton for the name of the thing it patches, then grep `.github` for a ruling **on that thing** rather than on the row. Passes 35–37 each searched `.github` for a ruling on the row's open *questions* (`:=`, `start`/`await`) and found none — the ruling that mattered was filed against the *file they were editing*, under a row name none of them had reason to read.

## WHAT I DID AND DID NOT DO

- **Did not extend the ruling to this row on my own authority** — it does not name it. Asked hq_P (non-blocking) and routed the queue dimension to ceo; assumption stated in the baton's `## NEXT` and `## QA`.
- **Deliberately did not land a `:=` grammar production that would have flipped 2 of 5 kernels green against this row's own parse-only DONE-WHEN.** `OP_BIND` is lexed (`raku.l:138`), declared and given precedence (`raku.y:470,490`), and has **zero productions** — recorded by pass 34, not new here. Refused because the pass-33 block's item 3 says *"Do not attempt without [the ARCH ruling]"* in terms, and because **banking a DONE-WHEN green by patching an instrument Lon has retired is a false green that would have made the row look finished.** `:=` also cannot be correct as a copy: at `rc-9-billion-names:11`, `@x.shift` must mutate through the binding into `@todo[$x]`.
- **Reported no fresh DONE-WHEN number**, because I could not measure one honestly — see the companion finding on concurrent `make pristine`.

## RECEIPTS

```
.github  0ce25b2d   GOAL-RAKU-100.md:274        the ruling
SCRIP    bcb0ec1e   rakugram rung 7             the replacement, live
SCRIP    tools/rakugram/README.md               the measured case against raku.y
task     raku-roast-100-percent-compile.task.md carries the ruling (named row)
task     raku-frontend-real-world-syntax-gaps.task.md  did not (this finding)
```
