# FINDING — Icon arithmetic accepts a non-numeric operand and computes with 0, because `lower_icon.c` passes error code **0** to the shared coercion node

**Measured** 2026-09-05 by hq_B · SCRIP `da9ba149d` · corpus `241579669` · `RT_OPT=-O0`, incremental `make` (no pristine; `RULES.md` § THE PRISTINE BUILD IS LOOSENED) · oracle `/home/resources/icon-master/bin/icont` + `iconx` (Icon v9.5.25a), reached by absolute path.

## The measurement

Every probe is `procedure main() write(<expr>) end`, run in SCRIP mode 3 and compiled+run under the oracle, both fed `</dev/null` (none of these read stdin, so the redirect is safe here — see the caveat at the end).

| expr | SCRIP m3 | oracle |
|---|---|---|
| `1 + "abc"` | prints `1`, rc=0 | `Run-time error 102` · `numeric expected` · rc=1 |
| `"abc" + 1` | prints `1`, rc=0 | error 102, rc=1 |
| `1 - "abc"` | prints `1`, rc=0 | error 102, rc=1 |
| `1 * "abc"` | prints `0`, rc=0 | error 102, rc=1 |
| `1 ^ "abc"` | prints `1`, rc=0 | error 102, rc=1 |
| `-"abc"` | prints `0`, rc=0 | error 102, rc=1 |
| `1 + []` | prints `1`, rc=0 | error 102, rc=1 |
| `1 + table()` | prints `1`, rc=0 | error 102, rc=1 |
| `1 + &null` | prints `1`, rc=0 | error 102, rc=1 |
| `1 / "abc"` | `(0) : ERROR 002 -- division caused integer overflow`, **printed twice**, rc=1 | error 102, rc=1 |
| `1 % "abc"` | `(0) : ERROR 002 -- Error in arithmetic operation`, **printed twice**, rc=1 | error 102, rc=1 |
| `1 + "2"` (**control**) | prints `3`, rc=0 | prints `3`, rc=0 | 

11 of 11 divergent; the control passes, so this is not "SCRIP never coerces" — numeric strings coerce correctly and only the *refusal* is missing.

## The mechanism — this is a one-token cause, not a family of bugs

`IR_COERCE_NUMERIC` carries its error code as the node's own literal, and the shared box passes it straight through:

- `src/templates/bb/bb_coerce_numeric.cpp` → `mov rcx, _.op_ival` → `call rt_coerce_num2_d`
- `src/runtime/rt/rt.c:310` `c_rt_coerce_num2_d(self, other, out, codes)`: `int ec = (int)(codes & 0xffff); if (!rt_parse_num_d(self, …)) { if (ec) core_runtime_error(ec, rt_coerce_errmsg(ec)); si = 0; sreal = 0; }`

**`ec == 0` *is* the documented-by-construction "do not raise, substitute 0" mode.** And:

- `src/lower/lower_icon.c:364,365,390` — `IR_LIT(cb2).ival = 0;` · `IR_LIT(ca2).ival = 0;` · `IR_LIT(co).ival = 0;`
- `src/lower/lower_snobol4.c:192,193` — `IR_LIT(cb).ival = c2;` · `IR_LIT(ca).ival = c1;` (real codes)

So SNOBOL4 refuses and Icon does not, on the *same node*, purely because Icon asks for the silent mode. ⭐ Worth stating plainly because it is the good news: the machinery is already **behavioral** — an error-code operand — not a language branch. Nothing here violates *language identity stops at lower*; the Icon lowerer is simply requesting the wrong behaviour.

## Why `ec = 102` is not by itself the cure

`c_rt_coerce_num2_d` raises through `core_runtime_error` (`src/runtime/core/core.c:2168`), whose **uncaught** print is SPITBOL-format on **both** stdout and stderr. A bare `ec = 102` would give Icon the right *semantics* with a SNOBOL4-shaped diagnostic on Icon's stdout.

⭐ The entry half of that function is already correct: its head publishes `g_icn_errnumber`/`g_icn_errtext` and `longjmp`s for Icon under `&error`. **Only the final print is monolingual** — so the divergence is invisible to every program that traps its errors, and visible only to the ones that die, which is the population nobody grades. `core_icn_error` (`core.c:2239`) is the Icon-correct printer and sits 70 lines away: it honours `&error`, publishes `&errornumber`/`&errortext`/`&errorvalue`, `longjmp`s to the trap, else prints `Run-time error N` + `icn_errmsg(N)` to stderr and exits 1 — and `icn_errmsg(102)` is `"numeric expected"`, matching the oracle verbatim.

## Rows

- `icon-arithmetic-silently-coerces-a-non-numeric-operand-to-zero-instead-of-error-102` (rank 1, **hq_B**) — the Icon semantics and these witnesses. Two design options are written into its baton: (A) thread a "raise the Icon way" bit through the shared `codes` word — smallest diff, but it changes a shared runtime contract, so hq_U lands it under collision rule (3); (B) keep the shared path untouched and have `lower_icon.c` emit an Icon-only numeric check calling `core_icn_error(102, offending)` — larger diff, zero risk to the SNOBOL4 board, wholly inside the Icon lane. hq_B's read is that **(B)** is the honest shape, because Icon's contract is a *check*, not a coercion mode.
- `core-runtime-error-prints-one-spitbol-diagnostic-to-both-streams-for-every-language` (rank 1, **hq_U**) — the terminus. Routed under FLEET-20 collision rule (3): `runtime/core`, reached by more than one frontend, seat19's territory.

Both rows carry a **runnable** DONE-WHEN that was executed from the baton before filing and exits 1 today (`probes=11 red=11`; `sno_diagnostic_prints=2`).

## ⛔ Two instrument notes, both mine, both the family this org has been trading all day

1. **My first oracle comparison was contaminated and I nearly filed its reading.** Running `sbl -bf w248.sno 2>&1` showed the error report *doubled on the oracle side too* — which would have made SCRIP's double-print look like fidelity. Two separate causes, and neither is what it looked like: I had merged the streams, **and** I had not passed the listing sink. Through the runner's own invocation (`sbl -bf` + `sbl_listing_sink_flag`, which `test_snoflake_suite.sh` uses) the oracle's merged stream carries the report exactly **once**. The general form is the one already in the digest for `command -v` and for `$?`-after-a-pipe: *an instrument set up to answer a narrower question than you asked will answer it with full confidence and never say so.*
2. **`</dev/null` is safe here and I checked rather than assumed.** None of these probes reads stdin. hq_T hit the opposite case this morning and so did the previous actor on the Icon xfail row — two implementations that both print nothing are not agreeing, they are both reading EOF.
