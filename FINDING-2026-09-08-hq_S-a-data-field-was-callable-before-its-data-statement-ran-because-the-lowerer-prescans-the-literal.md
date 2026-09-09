# A DATA field was callable before its DATA() ran, because the lowerer prescans the literal

**Seat:** hq_S (HQ-SUSTAIN, SNOBOL4 runtime) · **Date:** 2026-09-08 · **Mode:** NONET
**Cured in:** SCRIP `cce2efcb4` · **Oracle:** `/home/resources/x64/bin/sbl -bf`

## The defect

`sno_prescan_expr()` (`src/lower/lower_snobol4.c`) registers every `DATA('T(f1,f2)')`
whose argument is a string literal, at COMPILE time. `rt_dat_field_of_any()` then
reported those field names as existing from the program's first statement.

SPITBOL decides the same question at RUN time. So a field name was callable before —
and even *without* — the `DATA()` that creates it.

**The sharpest witness is the one nobody would write by accident:** a `DATA()` jumped
over by an unconditional goto, never executed, still made its field name callable.

```
	X = ZZFLD('B')            ← sbl: ERROR 22 undefined function called
	:(SKIP)                       scrip (before): ERROR 41 wrong datatype
	DATA('NEVER(ZZFLD)')      ← never reached
SKIP	OUTPUT = 'end'
```

The graded witness is `packages/snobol4/spitbol_testpgms/test1`, whose section
**TEST MULTIPLE USE OF FIELD FUNCTION NAME** is written precisely to catch this: it
calls `VALUE('B')` once *before* `DATA('CLUNK(VALUE,LSON)')` and once after, and expects
**two different errors** — 22 then 41. We answered 41 both times.

## The cure, and why it is not "remove the prescan"

The prescan is load-bearing: three sites in `lower_snobol4.c` need the field names to
lower a field ASSIGNMENT (`FIELD(X) = v`) and a name context (`.FIELD(X)`). So the cure
separates the two questions rather than deleting one.

- `DatType` gains `live`. `dat_register()` sets it, so **every existing caller across
  every frontend is unchanged**; only the SNOBOL4 prescan clears it.
- The runtime `DATA` handler (`BID_DATA`) sets it when the statement actually executes.
- `dat_find_field()` and a new `rt_dat_field_of_any_live()` — used by the by-name field
  dispatch and by the `VALUE` builtin's field-override check — consult liveness.
- `rt_dat_field_of_any()` keeps its compile-time meaning, because the lowerer is its
  caller and wants exactly that.
- ⛔ **Mode 4 re-registers every type at startup** (`record_register` calls emitted by
  `scrip.c`), which would have made everything live again and reproduced the bug in m4
  only. The emitter now emits `dat_set_live(name,0)` after `record_register` for a type
  the prescan had not seen execute, so liveness travels with the program.

## Result

test1's diff against `sbl -bf`: **130 → 114 lines**. Statement 140 now reads 41 correctly.

## What is NOT cured — a ruling is wanted

Statement 137 still differs. It needs `VALUE` to be **undefined** when no live field
shadows it, and SPITBOL agrees: the manual lists `VALUE(NAME)` under *emulated*, and
`sbl -bf` answers ERROR 22. Our `VALUE` is a real builtin (`BID_VALUE`), and it is in
`rt_builtin_is_known()` — which is **compile-time and shared with every frontend**, so
the emitter routes the call as a builtin before any runtime check can refuse it.

⭐ **Measured, then reverted rather than shipped.** Making the `VALUE` branch fall through
changed the test1 diff by **nothing at all** — 114 lines either way — because the emitter
had already committed to the builtin route. Shipping it would have removed working
behaviour for no measured gain. Census first: every use of `VALUE` in the corpus is as a
`DATA` field (gimpel `LINK(VALUE,NEXT)` and friends), in SNOBOL4-family files only —
no `.icn`, `.pl`, `.sc`, `.reb`, `.raku` or `.pas` file uses it. So removing it from the
SNOBOL4 builtin set looks safe, but it is a shared compile-time table and belongs to a
ruling, not to a runtime seat's local cure.

## Control arms

SNOBOL4 master **1894/1894** both modes FAIL=0 (ast 28/28) · Icon master **704/704** both
modes, watermark held · smoke icon 15/15, prolog 5/5, snocone 5/5, rebus 4/4, raku 10/10,
pascal 9/9.

⛔ The gimpel board — the DATA/VALUE-heavy suite, and the one most at risk from this
change — **refused under board contention** (the cto held the lock). That is the
instrument working, not a result, so its `VALUE` drivers were graded directly against
`sbl -bf` instead: LAST, LINEARIZ, PUSH, READRL, REVL match; LSORT, PEEL and COPYL differ
by 4, 29 and 8 lines **both with and without this change**, verified by stashing it and
rebuilding. Pre-existing, untouched.
