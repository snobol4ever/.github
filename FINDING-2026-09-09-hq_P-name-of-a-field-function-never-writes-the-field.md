# FINDING: the NAME of a field function never writes the field — `.FIELD(x)` assigns into nothing

**Seat:** hq_P · **Date:** 2026-09-09 · **Tree:** SCRIP `87b80d593`, corpus `9851eb79e`
**Found via:** gimpel `READL_driver.sno`, the topmost red in the hq_P slice (GIMPEL Q–Z) under the
ceo's all-twelve-on-SNOBOL4 order. **Row:** `flip-gimpel-readl-driver`.

## The claim

Assigning through the NAME of a data-type field function is a no-op in SCRIP. `N = .NEXT($N)` then
`$N = LINK(,'b')` leaves the `NEXT` field unset, so every SNOBOL4 linked-list idiom built the
canonical way produces a ONE-ELEMENT list. SPITBOL builds the whole list.

## Minimal witness (8 lines, oracle-verified both ways)

```
    DATA('LINK(NEXT,VALUE)')
    N = .HEAD
    $N = LINK(,'a')
    N = .NEXT($N)
    $N = LINK(,'b')
    OUTPUT = VALUE(HEAD)
    OUTPUT = DATATYPE(NEXT(HEAD))
    OUTPUT = VALUE(NEXT(HEAD))
END
```

| | line 1 | line 2 | line 3 |
|---|---|---|---|
| `sbl -bf` (the oracle) | `a` | `LINK` | `b` |
| `./scrip` (m3) | `a` | `STRING` | `ERROR 041 -- field function argument is wrong datatype` |

The second line is the whole finding: after `$N = LINK(,'b')`, `NEXT(HEAD)` should BE a LINK and is
instead a STRING (the unset null). The ERROR 041 on line 3 is the CONSEQUENCE, not the cause —
`VALUE()` is handed a non-LINK because the field was never written. ⛔ A reader who chases the
error number chases the symptom; the defect is one statement earlier and is SILENT.

## Why it is a class, not one program

The write path EXISTS and NOTHING ROUTES TO IT. `dat_field_set(const char *fname, DESCR_t obj,
DESCR_t val)` is defined at `src/driver/driver_data.c:407` and has **zero callers anywhere in
`src/`** (`grep -rn dat_field_set src/` returns the definition and nothing else). The runtime's own
`_make_fset` (`src/runtime/core/core.c:1704`) is likewise a correct setter. So the field-write
machinery is built; what is missing is the lowering that turns the NAME of a field function into a
reference those setters can be reached through. Reading a field works (`_make_fget`, :1692); only
the name-and-assign direction is unwired.

That makes this a CLASS behind an unknown number of package programs, not a one-program flip:
every `DATA()` linked structure — list, tree, queue, stack — is built with exactly this idiom.
`READL` is simply where it surfaced first in my slice.

## Scope named honestly

⛔ NOT CURED. Wiring it touches the SNOBOL4 parser (the `.` name operator applied to a call), the
lowering, and the runtime dispatch for indirect assignment — three files, so it is outside pace
rule 7's LOCAL cure (one builtin / lexer rule / fixture / ref / runtime helper, ONE file) and is
named to the ceo instead, per the same rule's 30-minute clause.

## Two instrument notes paid for on the way

⛔ **`< /dev/null` made this defect INVISIBLE and the program look GREEN.** `READL_driver` is fed by
`READL_driver.in`. Run with `</dev/null` both SPITBOL and SCRIP print the identical, entirely
plausible `. / . / DONE` — the redirect overrides the input, both sides read EOF, and the diff is
clean. This is the exact trap RULES/CLAUDE.md already names, met in the field: **a run fed by a
file must never be given `</dev/null`**, and "the two agree" is not evidence when neither was fed.

⭐ **The suite's DIFF was against the pinned `.ref`, and the `.ref` is right.** `READL_driver.ref`
matches the oracle exactly. Do not re-cut this ref — the ref is not the problem, the compiler is.
