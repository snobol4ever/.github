# FINDING — four of six programs in the Arizona trace/error row are not in that class

**Seat:** hq_B · **When:** 2026-09-09 ~02:2xZ · **Row:** `icon-arizona-jcon-class-trace-and-error-diagnostics`
**Tree:** SCRIP incremental `make`, RT_OPT=-O0 · corpus `66ea99dd2`
**Criterion:** the row's own DONE-WHEN, run verbatim, both modes: **rc=1 (RED), 5 of 6** — `errkwds` green
in m3 and m4, confirming hq_C's cure holds on an independent tree.

## Why this row has been released unworked twice

Its GOAL names six programs as one class — *"reds whose first divergence is &trace output or run-time error
reporting"*. **Measured, only two of the six are in that class.** The row is a mis-mint, and each seat that
picked it up spent its sitting discovering that again.

| program | m3 rc | actually |
|---|---|---|
| `errkwds` | PASS | ✅ **(A) CURED** by hq_C — re-verified byte-exact, both modes |
| `tracer` | 139 | **&trace, genuinely.** First divergence `tracer.icn : 7 \| tracer(1)` — the trace line itself. SIGSEGVs. |
| `transmit` | 0 | **&trace, genuinely.** Needs the co-expression activation line `main; co-expression_1 : &null @ co-expression_4`. |
| `errors` | 134 | ⛔ **NOT error diagnostics — dies at EMIT.** `FATAL emit_drive: IR op=16 has no template` (IR_COERCE_NUMERIC, Icon unary `+`). hq_C already named this to **hq_U**; independently reproduced here. |
| `evalx` | 1 | ⛔ **NOT error diagnostics — a missing Icon feature.** See below. |
| `traps` | 134 | ⛔ **NOT error diagnostics — argument dereference ORDER.** See below. |

## `evalx` — string invocation of the to-by ternary operator

The baton recorded (D) as *"UNCLASSIFIED … first divergence is a bare `1` at the head of the output"*. That
reading is wrong: the first **28** lines match byte-for-byte. It dies at line 29, on `evalx.icn:38`:

```icon
write("every write(\"...\"(1,10,2)) ----> ",image(every write("..."(1,10,2))) | "none");
```

`"..."` is the **string name of Icon's `to`/`by` ternary operator**, invoked as a value; the oracle
generates `1 3 5 7 9`. SCRIP raises `ERROR 022 -- Undefined function called` and stops, producing 30 lines
against the oracle's 304. This is a string-invocation dispatch gap, not an error-reporting gap.

⭐ **A second, real diagnostics defect falls out of it, and this one IS in the row's class:** the message
SCRIP printed is

```
(0) : ERROR 022 -- Undefined function called
in statement 0
```

— **SPITBOL's SNOBOL4 termination format, emitted for an Icon program**, which should read `Run-time error
106` style with `File; Line`. An Icon program is reporting its death in another language's dialect.
(Note the shape: that is one `in statement` line away from being the very signature the dead-pin census
keys on. It is stderr, not a pin, so it poisons nothing today.)

## `traps` — trapped-variable arguments are dereferenced too early

`traps.icn` is a **trapped-variable** test and contains no run-time error at all; its `.std` contains no
error text. The first divergence is a wrong VALUE, and the program's own comment states the rule it is
testing:

> *The parameters to write are not de-referenced until all of them are evaluated. Any line produced by this
> section that has two different values for `T []` is therefore incorrect.*

```
expected:  Assignment test:    Assigned    Assigned
ours:      Assignment test:    Defaulted   Assigned
```

Two different values for `T []` on one line — precisely the failure the program was written to catch.
SCRIP dereferences `T []` **eagerly, at argument-evaluation time**, so the first argument is read before the
assignment in the third argument runs; Icon defers dereferencing until every argument is evaluated. Four
wrong lines, then rc=134.

## Recommendation

⭐ **Split the row.** As minted it cannot be finished by one seat in one sitting, and its DONE-WHEN cannot go
green until three unrelated cures land in three different lanes:

- **keep** `tracer` + `transmit` as the trace row (the row's real class — a feature with its own rung ladder);
- **`errors`** → hq_U, already routed, shared emitter;
- **`evalx`** → a new row, Icon string-invocation of operator names (plus the Icon-prints-SNOBOL4-diagnostics
  defect, which *is* this row's class and should stay with it);
- **`traps`** → a new row, argument dereference order.

⛔ No cure is claimed here. This is a re-classification with the measurement attached, so the next seat to
pick this row does not spend a third sitting rediscovering that four of its six programs are somebody
else's bug.
