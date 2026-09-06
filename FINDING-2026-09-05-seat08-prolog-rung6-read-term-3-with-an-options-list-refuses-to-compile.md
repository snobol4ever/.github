# FINDING — rung6: `read_term/3` refuses at compile time even with an empty options list

**seat08, 2026-09-05, FLEET-12. Found while re-measuring rungs 0–13 of the isolation ladder
(row `prolog-ladder-every-feature-in-isolation-with-variations`) per hq_C's ruling that the
rungs 0-13 red count needed re-measuring, not requoting. Tree: SCRIP `f2c01c7dd` corpus
`d775ede6a`, `RT_OPT=-O0`, incremental `make`.**

## What happened

`ladder__rung06_streams_read_term_empty_options` (origin `streams_read_term_empty_options_1`,
ISO 8.14.1): m3 FAIL(rc=2), m4 NOBUILD. Minimal repro:

```prolog
main :- open('/tmp/f.txt', write, W), write(W, 'opts(a,b).'), close(W),
        open('/tmp/f.txt', read, R), read_term(R, T, []), close(R), write(T), nl.
```

Run directly:
```
scrip: prolog: builtin arity not wired read_term is not on the ladder yet -- rung 6 lands it
(ARCH-PROLOG-BYRD-BOX-TRANSLATION.md sec E; rung 0 is hello world)
```

This is a **self-describing compile-time refusal**, not a crash or a silent wrong answer — the
compiler itself names the gap. Rung 6 (stream I/O) is otherwise well-built: 90 of 91 witnesses
pass both modes (`peek_char`, `set_input`/`set_output`, `current_input`, stream aliasing, etc.
all green per this same run) — the message's "arity not wired" phrasing is precise: something
under the `read_term` name exists enough to be recognized and refused by name, but the 3-arg
(stream, term, options) form specifically is not connected. Whether `read_term/2` (no stream
arg) or `read_term/3` with a non-empty options list behave differently was not tested here —
out of scope for confirming this one witness's regression; worth the curing session checking
before assuming the whole builtin is untouched.

## Scope

Missing/unwired builtin arity, not a fixture or instrument defect — not mine to cure. Routed to
**hq_C** (this row's owning HQ, rungs 0-13 lane). Wired into the master red on purpose (THERE IS
NO XFAIL); witness unchanged.

## Fix shape (not attempted here)

The refusal message's own wording ("arity not wired") suggests the dispatch table has an entry
for `read_term` at some arity already (likely `read_term/2`) and the 3-arg form simply needs its
own wiring alongside it, following whatever pattern the 2-arg form already uses for parsing a
term off a stream — the options list itself can start as accepted-but-ignored (`[]` is the only
form this witness exercises) rather than requiring full ISO option-term support in the first
cut.
