# FINDING (seat04, 2026-09-05): `APPLY('!', x)` on an unregistered `!` raises SCRIP error 029, real SPITBOL raises 022 — pre-existing, not caused by this sitting's coerce.icn fix

**Seat:** seat04 · **Mode at discovery:** FLEET-16, closed out under the same-day QUARTET order · **Tree:** SCRIP (post `6dddcc237` + this sitting's `rt_call_arr_impl` `!` fix)
**Found while verifying:** `icon-jcon-shared-bang-dispatch-error29-regresses-coerce-by-name-invocation` (see that task's LEDGER for the actual cure). Not fixed here — QUARTET order in effect ("do not pick, do not mint, do not start anything new"), and it needs its own isolated check before touching `BID_APPLY`.

## THE SYMPTOM

```
        OUTPUT = APPLY('!', 'ABC')
END
```

- `./scrip`: `ERROR 029 -- Undefined operator referenced`
- `/home/resources/x64/bin/sbl -bf`: `ERROR 022 -- undefined function called`

Both are errors (neither silently returns a wrong VALUE), but the error CODE disagrees with the oracle. Confirmed deterministic, checked directly against the real SPITBOL oracle, not scrip-vs-scrip.

## WHY THIS IS NOT THE SAME BUG AS THE coerce.icn ROW

Traced via gdb (see the coerce.icn task's LEDGER for the full method): `APPLY(name, ...)`'s inner
resolution of `name` (`by_name_dispatch.c`, the `BID_APPLY` arm, `return try_call_builtin_by_name(pn,
args + 1, nargs - 1, out);`) calls `try_call_builtin_by_name` → `try_call_builtin_by_name_bl` **directly**.
It never passes through `rt_call_arr`/`rt_call_arr_bl`/`rt_call_arr_impl` — the chain this sitting's Icon
fix lives in — so that fix cannot affect and does not affect this path either way (verified: behavior here
is identical before and after this sitting's change).

## NOT NEW EITHER

Before `6dddcc237` (this same day, "raise SPITBOL error 29 for unregistered unary ! instead of a silent
fallback"), `try_call_builtin_by_name_bl`'s `!` arm had NO registration check at all — `APPLY('!', 'ABC')`
would have silently returned `'A'` (the old identity/first-char fallback), which *also* didn't match the
oracle's `ERROR 022`. So this has been wrong under every version of this arm; `6dddcc237` changed which
wrong thing happens (silent bad value → wrong error code), it didn't introduce the divergence.

## WHERE TO LOOK

`by_name_dispatch.c`, `BID_APPLY` handling (grep `BID_APPLY`): when `pn` (the target name, itself a
runtime value — `args[0]`) isn't a registered user procedure, it falls through to
`try_call_builtin_by_name(pn, ...)` as if `pn` could always be resolved as some ordinary builtin. Real
SPITBOL's `ERROR 022 -- undefined function called` suggests real SPITBOL's `APPLY` resolves its target
through the **function/procedure namespace only** (not through arbitrary single-character operator
dispatch) and reports "undefined function" when that lookup fails — i.e. `APPLY` may need to stop short of
`try_call_builtin_by_name`'s full operator-symbol fallback chain entirely for names that were never valid
function names in the first place, rather than falling all the way through into the newly-strict `!` arm.
Not investigated further than this — needs its own isolated repro sweep (does this affect ALL of `APPLY`'s
fallback names, or only the single-char operator-symbol ones?) before anyone touches `BID_APPLY`.

## BLAST RADIUS NOT CHASED

Only checked `APPLY('!', x)`. Whether `APPLY` on other never-valid-function names (e.g. `APPLY('+', x, y)`,
`APPLY('nonexistent', x)`) also mismatches the oracle's error code is unconfirmed — same method (`sbl -bf`
vs `scrip`, isolated single-statement witness) would settle it quickly.
