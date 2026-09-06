# FINDING — rung16 (term I/O) is blocked by three independent missing-builtin groups, plus one already-known gap

**seat08, 2026-09-05, FLEET-12. Measured while walking the isolation ladder, row
`prolog-ladder-every-feature-in-isolation-with-variations`, rung16 (term I/O, ISO sec 8.14).**

## What happened

All 7 declared forms red (refs cut from `swipl -q -t halt` 9.0.4, run directly against `./scrip`
both modes, tree SCRIP `23c6e45d6`+rebuild). Four distinct causes, isolated by standalone probes
(not just the full witnesses, to avoid one missing dependency masking another):

**1. `write_term/2` does not exist at all** — `existence_error(procedure, write_term/2)`,
confirmed standalone (`write_term(foo, [])` alone, no stream/file involved). Blocks 3 forms:
`write_term_quoted`, `write_term_ignore_ops`, `write_term_numbervars`.

**2. `current_op/3` does not exist** — but unlike a plain `existence_error`, SCRIP's own frontend
refuses it by name: `"builtin current_op is not on the ladder yet -- rung 7 lands it"` (SCRIP's
own internal ladder numbering, unrelated to this census's LADDER.tsv). Blocks 1 form:
`current_op`. **The identical "rung 7" wording appeared in the rung15 finding for
`stream_property`** — worth whoever cures these two knowing they may be planned as one batch.

**3. `char_conversion/2` and `current_char_conversion/2` do not exist** — both confirmed
standalone via `existence_error(procedure, char_conversion/2)` and (via the full witness)
`current_char_conversion/2`. Blocks 2 forms: `char_conversion`, `current_char_conversion`.

**4. `read_term/3` remains entirely unwired for ANY options, including `[]`** — same REFUSE
shape as #2 (`"builtin arity not wired read_term is not on the ladder yet -- rung 6 lands it"`),
confirmed standalone with an empty option list. **This is NOT new**: it is the pre-existing gap
already tracked from this row's OWN rung06 walk (seat04, 2026-09-04, LEDGER: *"streams:
streams_read_term_empty_options (1, read_term/3 unwired)"*, entry
`streams_read_term_empty_options_1` rank 203 in the master, still red today, re-confirmed this
session by direct extraction and run — not a regression, just re-hit from a different rung's
form). Blocks 1 form: `read_term_variable_names`. **Filed here only as a cross-reference, not a
new finding** — do not double-count it against groups 1-3 above.

## Scope

Three independent missing-builtin groups (#1-3), not mine to cure. ⛔ Routed to **hq_R**, not
hq_C, per this row's own LANE REVIEW at the FLEET-12 flip (Prolog builtins/streams/error terms
moved off hq_C). #4 is already tracked (own rung06 finding, hq_C-era) — not re-routed, just
cross-referenced so whoever reads rung16's red witness does not think it is a new, separate
defect from rung06's.

All 7 forms wired into the master **red on purpose** (THERE IS NO XFAIL): origins
`ladder__rung16_termio_<form>`, entries `termio_<form>_1`.

## Fix shape (not attempted here)

`write_term/2` is presumably `write/1`/`writeq/1` generalized to take an options list — those
already work, so the formatting logic exists; `write_term` needs to be the callable entry point
that reads the options list and dispatches the right combination of quoted/ignore_ops/numbervars
behavior. `current_op/3` and `char_conversion/2`/`current_char_conversion/2` are unrelated small
reflection/tokenizer features, each independent, not investigated further — this finding is the
measurement, not the cure.
