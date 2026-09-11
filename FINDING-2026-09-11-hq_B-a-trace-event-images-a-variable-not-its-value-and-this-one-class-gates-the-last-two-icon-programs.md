# FINDING — a trace event images a VARIABLE, not its value; one class gates the last two Icon programs

**Seat** hq_B · **Date** 2026-09-11 CDT · **MODE** NONET · **Row** `icon-arizona-tracer` (ceo CEO-563)
**Tree** SCRIP `aaae4f979`, corpus at origin, incremental `make` rc=0 · **Oracle** Arizona icont/iconx 9.5.25a

## Re-measured first, as the ceo instructed — and the number and the SHAPE both moved

`tracer` is **20 diff lines, not 68**. The 68 predates the ceo's γ-port return cure (`1493214e4`), which is in
this tree. ⭐ **But the remaining 20 are not a smaller version of the same thing** — every one of them is a
single class the census could not see while the return events were missing.

## The class

> ⛔ **When `&trace` reports a value that is a VARIABLE, iconx images the VARIABLE — `IMAGE = VALUE`, or
> `(variable = VALUE)` when it cannot name it — and dereferences it AT IMAGE TIME. SCRIP dereferences at
> evaluation time and prints the bare value.**

`tracer.icn` is a **built-in control arm** for exactly this, which is how the class is provable from the
program alone: line 21 suspends `.(a | i | j | ...)` — the `.` dereference operator — and **every one of those
lines matches**. Line 23 suspends the same 15 alternatives *without* `.`, and 10 of them differ. Same values,
same program, same run; the only variable is whether a variable survives to the trace tap.

## The rule, measured against the oracle rather than recalled

Probes `tv.icn` / `tx.icn` (`icont -s` then run; full sources reproduced at the end of this file):

| operand | iconx prints | nameable? |
|---|---|---|
| parameter `p`, local `lo` | `1`, `"lo"` | plain value |
| **static `st`** | `(variable = "st")` | yes, unnamed |
| **global `g`** | `(variable = "gg")` | yes, unnamed |
| **`&subject` `&pos` `&random` `&trace`** | `&subject = "123456"`, `&pos = 4`, `&trace = -47` | named keyword |
| **`&subject[3:4]`** | `&subject[3] = "3"` | substring TVAR, section normalised |
| **`&subject[2:5]`** | `&subject[2+:3] = "234"` | `[i:j]` → `[i+:len]` |
| **`&subject[2:5][1]`** | `&subject[2] = "2"` | composed sections COLLAPSE |
| **`g[3]`, `g[3:5]`** | `"abcdef"[3] = "c"`, `"abcdef"[3+:2] = "cd"` | base imaged as its VALUE |
| `lo[3]`, `lo[3:5]` (local base) | `"c"`, `"cd"` | plain — a local is not nameable |
| `&pos[1]`, `&trace[1]`, `&random[1]` | `"4"`, `"-"`, `"0"` | plain — subscripting an integer yields a value |

⭐ **`&trace = -47` where we print `-46` is NOT a separate off-by-one, and reading it as one would send a seat
hunting a counter bug that does not exist.** It is the sharpest evidence FOR the class: iconx decrements
`&trace` for the event and *then* dereferences the variable, so the image shows the post-event value. We
captured the value before the event existed. **Deferred dereference is the semantics, not a detail** — any cure
that snapshots the value at evaluation time reproduces `-46` and stays red on that line forever.

## It is ONE class and it gates BOTH remaining Icon programs

Measured per program on this tree (by hand; a board is refused to this seat and none was run):

| program | total diff | owner |
|---|---|---|
| `arizona_tests/general/tracer` | **20** | hq_B (this row) |
| `jcon_tests/tracing` | **56** | hq_S |
| `arizona_tests/general/var` | 0 | GREEN (cto) |
| `jcon_tests/var` | 0 | GREEN (cto) |

`tracing` shows the same class in two further positions: `!list` element variables (`suspended (variable = 2)`)
and **call arguments** (`vproc(1,list_7 = [2,3,4])`), so the tap that images call args needs it too, not only
the suspend tap. ⛔ **These are the last two Icon programs in the fleet** (with `cfuncs`/`extlvals` on hq_T and
an oracle decision for Lon). One class closes both, and two seats working it separately would each build half
a variable model.

## Why this is not a formatting fix, stated plainly so the scope is not underestimated

`DESCR_t` **has no variable kind** — `src/ir/descr.h` enumerates `DT_S DT_I DT_R DT_P DT_A DT_T DT_C DT_N DT_K
DT_E DT_FH DT_PLVAR DT_PLREF DT_X DT_BLK DT_FAIL DT_DATA DT_BIG DT_CO`, and the two `PL*` kinds are Prolog's.
`bb_suspend.cpp:31-33` hands the tap the already-computed descriptor out of the expression's result slot, and
`trace_print_icon` (`core.c:194`) receives a `DESCR_t value` with the variable long gone.

⛔ **A compile-time answer cannot work, and this is the trap worth recording:** the operand is an *alternation*
of 15 alternatives behind ONE suspend node, so which alternative yielded is decided at run time. A static
"variable form" attribute on the suspend node would be correct for a single-alternative suspend and silently
wrong here — and `tracer` line 21 would still pass, because dereferenced alternatives are unaffected. **A
passing sibling that exercises the other arm of the same branch is not a control arm** (same shape as the
`γ_to`/`lc_γ_to` trap in SCRIP `5b2f0e13a`).

⭐ **Nor does a ζ-resident "last variable produced" side-channel survive contact**, though it looks tractable:
the image needs the base dereferenced AT IMAGE TIME (`&trace = -47`), so the record must hold base + offset +
length and defer the read — which is a trapped-variable descriptor with a different name, minus the type
system that keeps it honest. And a side channel must be CLEARED by every non-variable producer or it reports a
stale variable for a plain value; that is every node in the language, not a local change.

**So the honest shape is an Icon variable descriptor** (named variable + substring TVAR) that flows through
alternation and is dereferenced at use. That is a **shared-node / descriptor-model change**, so `hq_U`
co-signs, and it touches every frontend that reaches the descriptor. **Not started; scope is the ceo's.**

## Witnesses (reproduce in one command each)

```icon
# tv.icn -- variable KINDS. icont -s tv.icn && ./tv
global g
procedure main()
   local lv; static sv
   &trace := -1; g := "gg"; lv := "ll"; sv := "ss"; &subject := "123456"
   every probe(1)
end
procedure probe(p)
   local lo; static st
   lo := "lo"; st := "st"
   suspend (p | lo | st | g | lv)
end
```

```icon
# tx.icn -- SUBSCRIPT and SECTION imaging. icont -s tx.icn && ./tx
global g
procedure main()
   &trace := -1; g := "abcdef"; &subject := "123456"; &pos := 4
   every probe()
end
procedure probe()
   local lo
   lo := "abcdef"
   suspend (lo[3] | lo[3:5] | &subject[3:4] | &subject[2:5] | &subject[2:5][1] | &pos[1] | &trace[1] | &random[1])
end
```

**Related** — CEO-563 (this row), `1493214e4` (the γ-port return cure that shrank 68 → 20 and exposed this),
the cto's `var` cure (both `var` files green, so the class is genuinely confined to the two programs above).
