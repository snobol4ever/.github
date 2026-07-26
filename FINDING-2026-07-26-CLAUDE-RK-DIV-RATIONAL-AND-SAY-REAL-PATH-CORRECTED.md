# FINDING 2026-07-26 — RK-DIV: Int/Int division is rational, not truncating · AND the `say`-real path is CORRECTED (twice-stale)

**Session:** s2026-07-26 · Claude Opus 5 · goal `GOAL-RAKU-BB.md` (RAKU-100 arc)
**SCRIP commit:** `0a2ce9b5`
**Watermark:** m3 **655 → 661**, m4 **655 → 661**, zero regressions. Peers unchanged: Icon 14/14, SNOBOL4 7/7, Prolog 5/5/5, Rebus 4/4.

---

## PART 1 — THE RUNG THAT LANDED: `/` yields a rational value

**Defect (the prior cursor's own #1 recommendation, and it was right to rank it first):** `7/2` → `3`, `(7/2)*2` → `6`, `1/3` → `0`. This is **wrong arithmetic**, not a missing feature — the highest-severity class of gap on the ladder.

**Canonical source read BEFORE any edit** (`refs/rakudo/src/core.c/Rat.rakumod`):
- `multi sub infix:</>(Int:D $a, Int:D $b) { DIVIDE_NUMBERS($a, $b, $a, $b) }` — line 256, exactly as the prior cursor cited.
- `DIVIDE_NUMBERS` (line 76): gcd-reduces numerator/denominator, normalizes sign onto the numerator, and on `$de == 0` constructs a denominator-0 Rational rather than throwing at the division site.
- `Rational.Str` (`Rational.rakumod:114`): **no fractional part ⇒ prints as a bare whole number** (so `8/2` prints `4`, NOT `4.0`); otherwise ~6 significant digits for denominators < 100_000; denominator 0 ⇒ `DIVIDE_BY_ZERO`.

**Why the fix is Raku-routed and NOT a change to the shared arith box.** `TT_DIV` maps through `lc_binop_code` → op `3` → the SHARED `IR_BINOP` arith box, whose truncating semantics are **CORRECT** for SNOBOL4 / Icon / Prolog / Pascal. Measured before touching anything:

| Language | `7/2` | `8/2` | `-7/2` | correct for that language? |
|---|---|---|---|---|
| Icon | 3 | 4 | -3 | YES (Icon `/` on integers truncates) |
| SNOBOL4 | 3 | 4 | -3 | YES (SPITBOL) |

Editing `DIVIDE_fn` / the arith box would have silently broken four peers — the same trap as the s2026-07-25b `arr_get`-is-shared-with-Pascal note. **Same lesson, different helper: measure the peer set before editing anything in `src/runtime/` or the shared boxes.**

**Implementation (three files, all Raku-local):**
1. `src/lower/lower_raku.c` — one line, placed immediately **before** the generic `rk_is_binop` arm: `if (t->t == TT_DIV && t->n > 1) { return lower_rcall(cx, t, "__rk_div", 0, γ, ω, res); }`. `TT_DIV` is intercepted at a **Raku-only lowering site**, so no language token exists downstream — FACT-RULE clean, lang-blind gate green.
2. `src/runtime/by_name_dispatch.c` — `__rk_div` fold: both-int ⇒ exact division stays **integral** (`8/2`→`4`, faithful to a Rat with denominator 1 stringifying bare), inexact ⇒ **REALVAL** (`7/2`→`3.5`); `b == -1` special-cased before the `%` to avoid the INT64_MIN overflow trap; zero divisor ⇒ `rt_script_die_surface("Attempt to divide by zero")` (canonical message).
3. Registered `"__rk_div"` in `rt_builtin_is_known` so mode-4 emits `@PLT` — both modes work identically.

**BONUS FIX, previously unlogged anywhere:** `say 1/0` used to die with **SIGFPE, rc=136** — a hard crash — because the emitted inline `idiv` fast path carries no zero guard. Routing division through a runtime call means Raku no longer reaches that instruction; it now raises catchably with rc=1. **NOTE for peers: the inline-idiv SIGFPE is still live for SNOBOL4/Icon/Prolog/Pascal `x/0`.** Not fixed here (peer semantics are Lon's call); worth its own rung.

**Verification:** 6 new smokes (`div_inexact_rational`, `div_exact_stays_integral`, `div_roundtrip_multiply`, `div_by_zero_dies`, `div_var_operands`, `div_in_expression`), all `[m3 PASS] [m4 PASS]`. Pre-existing `compound_div_eq` (`24/6`→`4`) still passes — `/=` routes through the new path and stays exact. 12 committed `.s` artifacts recompiled byte-identical (zero codegen drift). All builds `-O0`.

---

## PART 2 — ⚠ THE `say`-REAL PATH: the cursor's "STALE" correction was ITSELF WRONG

The s2026-07-25b LIVE CURSOR says:

> ⚠ The inherited "`say` reaches `real_str`" note is **STALE** — Raku `say` goes via `to_cstring`→`rtos` (`by_name_dispatch.c:331`), NOT the peer-shared SPITBOL `real_str`; the fix may be containable in `rtos`. Verify before trusting.

It told you to verify. **Verified: that correction is wrong, and `rtos` is NOT on the `say` path at all.** Disproof is two lines: `rtos` is `gcvt(r, 14)`, which renders `4.0` as `4` and `sqrt(2)` as `1.4142135623731`. Observed actual output is `4.0` and `1.4142135623730951`. Different function, therefore different path.

**THE MEASURED PATH (traced through the emitted call, not inferred):**

```
say <expr>  →  TT_SAY (Raku-EXCLUSIVE AST node; grep: only lower_raku.c references it)
            →  lower_raku.c:234  lower_rcall(..., "write", ...)      ← SHARED builtin name
            →  rt_call_arr → rt_call_arr_impl → out_write_descr()
            →  reals formatted by  icon_real_str()                    ← ICON's formatter
```

So **Raku is borrowing Icon's real formatter**, which is why Raku prints `4.0` (Icon-correct) while SNOBOL4 prints `4.` (SPITBOL-correct, via `real_str`). Three formatters already coexist: `real_str` (SPITBOL), `icon_real_str`, `pas_real_str`. **That trio is the precedent for how this codebase does per-language real rendering — by NAME, selected by the lowerer, never by a language flag in the runtime.**

**Consequence: the fix is NOT containable in `rtos`, and NOT in `rt_format_float` either.** (`rt_format_float` in `io_format.c` delegates to `real_str` and feeds `rt_write_any_nl`, reached from `bb_call_write_slot.cpp` — a genuinely language-blind template. It is a *different* sink that Raku `say` does not use. The ORIGINAL "say reaches real_str" note was describing this sink and was therefore also wrong for `say`.)

**THE ACTUAL SEAM for the next rung, already mapped:** `TT_SAY`/`TT_PRINT` are Raku-exclusive, so `lower_raku.c:234-235` can point at Raku-specific builtins (`"rk_write"`/`"rk_writes"`) whose runtime arms mirror `write`/`writes` but format reals with a new `rk_real_str`. That is FACT-RULE clean by construction (the difference is named by behavior; each lowerer calls the variant it needs). Register the new names in `rt_builtin_is_known` for m4.

`rk_real_str` should implement `Rational.Str`: whole values print bare (`7` not `7.0`), fractional values print to ~6 significant digits (`1/3`→`0.333333`, `2/3`→`0.666667`).

⚠ **But mind the Rat/Num split before writing it:** canonical Raku prints `1/3` as `0.333333` (Rat, 6 digits) and `sqrt(2)` as `1.4142135623730951` (Num, full double). SCRIP has ONE real type, so a single 6-digit formatter would REGRESS `sqrt(2)`, which is currently correct. Either carry a Rat/Num distinction in the descriptor (the honest fix, its own rung) or scope the formatter to whole-value trimming only (`7.0`→`7`) and leave fractional precision alone. **Do not blanket-truncate to 6 digits.**

---

## KNOWN DIVERGENCES CREATED/REMAINING (stated plainly, not buried)

1. **`(7/2)*2` → `7.0`, canonical `7`.** Value is now CORRECT (was `6`); only the rendering differs. Fixed by the Part-2 rung above.
2. **`1/3` → `0.3333333333333333`, canonical `0.333333`.** Rat 6-digit stringification not implemented.
3. **No exact `Rat` type.** `(1/3)*3` is `0.9999999999999998`, canonical exactly `1`. Raku Rats are exact rationals; SCRIP approximates with a double once the division is inexact. A true `Rat` (numerator/denominator pair in the descriptor, gcd-normalized, propagating through `+ - * /` and comparison) is a substantial multi-rung arc — it is the honest ceiling on Raku numeric fidelity and should be scheduled deliberately, not slipped into a formatting rung.
4. **`.WHAT` on a division result** reports the underlying Int/Real, not `(Rat)`.
5. **Peer `x/0` still SIGFPEs** (inline idiv, no zero guard) for SNOBOL4/Icon/Prolog/Pascal.

---

## METHOD NOTE — why two stale claims survived multiple sessions

Both bad claims in Part 2 were *plausible prose about a call path*, and prose about call paths rots silently because nothing re-checks it. The disproof in each case cost ONE command (read the function, compare to observed output). **When a cursor names a specific function as "the sink," read that function and compare its formatting to actual program output before building on it.** The s2026-07-25b cursor did the right thing by writing "verify before trusting" — that hedge is what made this cheap to catch. Keep writing it.
