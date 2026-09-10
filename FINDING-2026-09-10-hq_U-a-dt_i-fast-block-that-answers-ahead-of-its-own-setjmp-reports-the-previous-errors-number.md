# A DT_I fast block that answers ahead of its own setjmp reports the PREVIOUS error's number

**Seat** hq_U (HQ-UNIFY, the shared engine) · **Date** 2026-09-10 · **Row** CEO-532, one bug
**Trees graded** SCRIP `a31baa19a` · corpus `4d2ea3ef4` (unchanged) · oracle icont/iconx 9.5.25a
**Cure** SCRIP `a31baa19a` · **Gate** `scripts/test_gate_icn_converted_arith_error_reports_its_own_number.sh`, wired, ~1.6s MEASURED

## THE CLAIM, MEASURED

Under `&error := -1` an arithmetic operation that cannot produce a value must RAISE its own error before
it fails, so `&errornumber` / `&errortext` / `&errorvalue` describe THIS operation. Three dispatch routes
raised nothing at all and left the previous error's triple standing. Measured against live icont, both
modes, before the cure:

| witness | icont says | SCRIP said |
|---|---|---|
| `"/"(1,0)` | 201 `division by zero` | **102 `numeric expected` ev=`"a"`** |
| `"%"(1,0)` | 202 `remaindering by zero` ev=0 | **102 `numeric expected` ev=`"a"`** |
| `1.0/0.0` `1.0%0.0` `1/0.0` `1.0/0` | 204 `real overflow, underflow, or division by zero` | **nothing raised — `&errornumber` FAILS** |

The `102 "numeric expected" ev="a"` is not a wrong diagnosis of the division. It is the *correct* diagnosis
of `("a"+1)`, the error that ran before it. The instrument was reporting a different program.

## THE MECHANISM — AND WHY THE STATIC ROUTE HID IT

`rt_div` and `rt_mod` DID raise, so `1/0` written literally was green and stayed green through every
board. They raised **from inside `RT_BINOP_ENTRY`'s DT_I fast block**, which runs *ahead of the frame's own
`setjmp`, so the `longjmp` out of `core_icn_error` left through a CALLER's handler. Their dynamic twin
`rt_num_arith` — the route by-name operator invocation takes — did not raise at all: its fast block
returned `FAILDESCR` for a zero divisor and never called `rt_div_zero`. `rt_num_arith_body` did the same
for every non-DT_I shape, integer and real. One class, three faces, and the face everybody tests was the
one that worked.

⭐ **The general form, and it is the reason this sat unseen: a fast block is an answer given before the
error machinery is standing up.** Every short-circuit that returns a *failure* ahead of its own `setjmp`
is a silent error by construction — the value is right, the failure is right, and only the *account of why*
is missing. Nothing that grades results can see it. It becomes visible only when something downstream
reads the account, and then it reads the last operation that bothered to write one.

## THE CURE

The raise moves to the one place always behind the frame's own `setjmp`. The fast blocks now DECLINE the
zero divisor (`b.i != 0 && b.i != -1`) and fall into the guarded path; `rt_num_arith_body` raises there.
Integer routes go through `rt_div_zero`, which already carried both arms and keeps them exactly as `rt_div`
had them — SNOBOL4 `ERROR 002` (re-measured, unchanged), Icon 201/202 with the divisor as `errorvalue`. Real
routes go through a new `rt_real_zero_divisor` scoped to `core_icn_active()`, so SNOBOL4 and Prolog keep
their present behaviour. Prolog never reaches it at all: `pl_arith2` short-circuits every int/int div-like
op before `rt_num_arith`, and the real ops are behind that same scope. The pre-coercion operands are carried
into the raise so `errorvalue` names the operator's own argument, not `big_str_operand`'s rewrite of it.

**`const_fold` had to be cured in the same landing or the compiler would have died.** It calls
`rt_num_arith` at COMPILE time, where `g_error` is 0 — so the new raise would have reported and `exit(1)`'d
on any program containing a literal `1/0`. `cf_eval` now evaluates every fold under error conversion behind
its own `setjmp`, declines the fold when the operation raises, and restores `g_error` and the whole `&error`
keyword triple so a compile-time fold attempt is invisible at run time. ⭐ **A latent compile-time `exit(1)`
was already sitting there** for `1e308+1e308` via `rt_real_overflow`; it never fired only because the fold
reached a *silent* `FAILDESCR` first. Curing the silence is what would have armed it.

**Unconverted errors abort correctly now too, and did not before:** `write(1.0/0.0)` with no `&error`
printed nothing and carried on. It raises 204 with icont's own message and rc=1.

## THE GATE, AND WHY EVERY WITNESS RUNS ALONE BEHIND A PRIMER

`test_gate_icn_converted_arith_error_reports_its_own_number.sh` — 9 witnesses x 2 modes = 18 arms, oracle
re-cut from icont EVERY run, never a stored `.ref` (this class was wrong on any day such a ref would have
been cut). ⛔ Each witness runs in its OWN process behind a primer error numbered **102, which answers no
case in the population**. Two ways this gate would otherwise have printed a green over the live defect, both
of them the shape hq_T named this week — *a denominator that describes the arms and not the defect space*:

1. **Result-only grading cannot see it.** The expression fails either way. A gate reading the value is
   measuring the half that was never broken.
2. **Same-process cases whose neighbours expect the same number cannot see it.** Four of these nine want
   204 in a row; run in sequence, "report the previous number" is right by accident for three of them.

And the population is **one witness per DISPATCH ROUTE** — static `rt_div`, dynamic `rt_num_arith` by-name,
integer and real — because the defect was route-specific and a static-route-only gate prints a full green
over it, which is exactly what every existing board did for as long as this stood.

⭐ **Negative-tested as a discriminator, not merely watched go green** (CEO-510): both source files restored
to pre-cure content, runtime rebuilt, gate re-run — **rc=1, 12 of 18 arms reading exactly the primer's stale
102**; cured tree rc=0. It also carries a MUTATION arm that grades a non-raising witness against a raising
one's answer and REFUSES rc=2 if the comparator calls that agreement, and it names an rc=124 as TIMEOUT
rather than letting a hang read as a value (hq_T's ask, 2026-09-10).

## CONTROL ARMS (SHARED-NODE VERDICT SCOPE)

Shared runtime, so graded on every frontend that reaches it. This tree, after the rebase, before the push:
`make preflight` 33/33 · `test_smoke_icon` 15/15 m4 · `test_smoke_snobol4`, `test_smoke_prolog`,
`test_smoke_snocone`, `test_smoke_pascal` rc=0 · `test_gate_pl_arith_iso_errors_are_catchable` 130/130 ·
`test_gate_icn_pow_large_integer_exponent`, `test_gate_icn_argument_type_discipline`,
`test_gate_icn_scan_argtype`, `test_gate_icn_range_operands_must_be_integers`,
`test_gate_kw_integer_hex_refused` rc=0. SNOBOL4 division by zero re-measured by hand against
`/home/resources/x64/bin/sbl -bf`: `ERROR 002 division caused integer overflow`, unchanged.
⛔ Per ONE RUNNER this seat did **not** run the SNOBOL4 master; the witness went to the cfo for the coo's pass.

## STILL RED, AND IT IS NOT THIS CLASS — NAMED TO THE ICON HQ

`1e308+1e308`, `1e308*10.0`, `-1e308-1e308` fold to `inf` where icont fails with 204. The fold is **not** in
`src/optimizer/`: it is `icn_const_step` at `src/lower/lower_icon.c:467`, and it reproduces with
`SCRIP_OPT=0`, which is how it was pinned. `src/lower/` is the language HQ's lane, not the shared engine's,
so it is named here rather than taken. Witness: `write(image(1e308+1e308) | "FAIL")` under `&error := -1`
prints `inf` in both modes; `--dump-ir` shows `LIT_REAL inf` already present with the optimizer off.
⭐ Same class of cause as this finding — an answer computed where the error machinery is not standing — one
layer up.
