# FINDING — SCRIP Prolog's stream I/O only implements the character-oriented API; code/byte/reflection are entirely absent

**seat08, 2026-09-05, FLEET-12. Measured while walking the isolation ladder, row
`prolog-ladder-every-feature-in-isolation-with-variations`, rung15 (stream, character and byte
I/O, ISO sec 8.11-8.13).**

## What happened

Rung15 declares 8 forms. Minting one witness per form (refs cut from `swipl -q -t halt` 9.0.4,
run directly against `./scrip` in both modes, tree SCRIP `23c6e45d6`+rebuild):

| form | SCRIP result |
|---|---|
| `flush_output` (both `flush_output/0` and `flush_output/1`) | **PASS both modes** |
| `stream_property` | REFUSE(2): `"builtin stream_property is not on the ladder yet -- rung 7 lands it"` (SCRIP's own internal message) |
| `at_end_of_stream` | `existence_error(procedure, at_end_of_stream/1)` |
| `set_stream_position` | same REFUSE as `stream_property` (this form's witness obtains its position term via `stream_property/2`, which is how ISO 8.11.7 defines a stream position — cannot be tested independently of it) |
| `get_code_peek_code` | `existence_error(procedure, peek_code/2)` |
| `put_code` | `existence_error(procedure, put_code/1)` |
| `get_byte_peek_byte` | `existence_error(procedure, put_byte/2)` (blocked at fixture setup, before even reaching `get_byte`/`peek_byte`) |
| `put_byte` | `existence_error(procedure, put_byte/2)` |

**7 of 8 forms red, all at rc consistent with "procedure does not exist," not a wrong-answer bug.**

## Follow-up probes (isolating each primitive independently of the others)

Since several forms cascade through a shared missing dependency (e.g. `put_byte` blocks both
byte-oriented forms), four primitives were probed standalone, each via its own minimal
open/write/close/open/read:

- `get_code/2` — `existence_error(procedure, get_code/2)`
- `put_code/2` (explicit stream, not just the 1-arg current-output form) — `existence_error(procedure, put_code/2)`
- `peek_byte/2` — `existence_error(procedure, peek_byte/2)`
- `get_byte/2` — `existence_error(procedure, get_byte/2)`

So the gap is not one or two convenience arities: **the entire code-oriented (`get_code`,
`put_code`, `peek_code`, any arity) and byte-oriented (`get_byte`, `put_byte`, `peek_byte`, any
arity) I/O families are absent**, alongside `stream_property/2`, `at_end_of_stream/1` and
(as a consequence) `set_stream_position/2`.

**By contrast, the character-oriented family works today**, per the pre-existing general-suite
entries this session did not need to re-derive: `get_char/2`, `peek_char/2`, `set_input/1`,
`set_output/1`, `open/3` (write and read), `close/1`, `read/2`, `read_term/2` (see
`corpus/tests/prolog/ALL.pl` rung06 `sw_get_char`/`sw_peek_char`/etc. entries, all still
presumably green). `flush_output` (0- and 1-arity) also works.

## Shape of the gap

This reads as an intentional, staged build, not a random scatter of bugs: SCRIP's own runtime
names a rung ("rung 7" in its internal ladder, **not** the same numbering as this task's
LADDER.tsv) as where `stream_property` is planned to land, and the missing set is exactly "every
ISO stream primitive keyed on an integer (code or byte) rather than a character." One plausible
common mechanism: the stream abstraction's dispatch table has entries wired for the char-typed
accessors and simply has not had the code/byte accessors added yet — but that is a guess about
the fix, not a measurement; not investigated further, since ablating into the runtime is hq_R's
cure, not this walk's.

## Scope

Missing-builtin gap (a large, coherent one), not a fixture or instrument defect — not mine to
cure. ⛔ **Per this row's own LANE REVIEW at the FLEET-12 flip, rungs 15/16/18 are hq_R's surface**
(Prolog builtins/error terms/streams moved to hq_R, not hq_C) — routed there directly, not to
hq_C. All 8 forms wired into the master, the 7 broken ones **red on purpose** (THERE IS NO
XFAIL): origins `ladder__rung15_streamio_<form>`, entries `streamio_<form>_1`.

## Fix shape (not attempted here)

Whatever table dispatches `get_char/2`/`put_char/2`/`peek_char/2` (presumably
`src/runtime/builtins/` or the Prolog-specific runtime under `src/runtime/`) needs the equivalent
code-returning and byte-returning entries added beside it, plus `stream_property/2`,
`at_end_of_stream/1` and `set_stream_position/2` as new builtins entirely. Given the char family
already works, the per-primitive shape (open a stream, read/write one character-shaped unit) is
proven out; only the integer-vs-character encoding differs.
