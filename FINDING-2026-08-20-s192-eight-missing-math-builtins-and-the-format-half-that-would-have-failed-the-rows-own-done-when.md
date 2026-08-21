# FINDING s192 (seat4) — eight missing math builtins, and the format half that would have failed the row's own DONE-WHEN

**Row:** `real-fn-family` (rank 1). **SCRIP `84966023`** · **corpus `3c38c4ad`** · RT_OPT `-O0` (O0-DEV) · pristine before every verdict.

## The row as briefed, and the one thing it had costed wrong

The brief was accurate and well-scoped: eight SPITBOL real-number builtins — `ATAN CHOP COS EXP LN SIN SQRT TAN` —
answered `** Error 5 -- Undefined function or operation` while the live oracle computes every one. It named the
registration site correctly and said the work was "EIGHT UNREGISTERED FUNCTIONS OVER A WORKING TYPE: no codegen, no
templates, no pattern machinery." That is right about the mechanism.

⛔ **It was wrong about one premise, and the premise was load-bearing.** The brief said *"THE REAL TYPE ITSELF IS
ALREADY CORRECT -- 3.9 + 1.1 = 5. and DATATYPE(3.9) = REAL agree with the oracle."* Both samples do agree. But
`real_str` (`src/runtime/string_ops.c`, the ONE authority) rendered the **shortest round-trippable** double, while
SPITBOL renders a **FIXED significant-digit count** (`cfp$s`, sbl.min:1230 *"number of significant digits to
produce"*). The two agree only when the shortest round-trip happens to be short:

| expression | oracle | SCRIP before |
|---|---|---|
| `COS(1.0)` | `0.54030230586814` | `0.5403023058681398` |
| `1.0 / 3.0` | `0.333333333333333` | `0.3333333333333333` |
| `1.0 / 7.0` | `0.142857142857143` | `0.14285714285714285` |
| `3.14159265358979323846` | `3.14159265358979` | `3.141592653589793` |
| `123456789012345678.0` | `0.123456789012346e+18` | `0.12345678901234568e+18` |

The row's DONE-WHEN requires the 8 to be *"oracle-identical (value AND printed format)"*. Every one of the eight
would have been **value-correct and format-wrong**. Registering them without touching `real_str` would have produced
eight functions that pass a value check and fail the row.

⭐ **The generalisable move: a premise that was verified on two samples is not a verified premise.** `3.9 + 1.1` and
`DATATYPE(3.9)` are exactly the two cases where a wrong digit-count is invisible — one is integral, the other returns
a type name. The cheapest way to find this was to print a real that needs 16 digits, which cost one probe line.

## The count is 15, and a checked-in probe says 14

`corpus/probe/gimpel/gim_real_print_precision.sno`'s header reads *"The oracle emits 14 significant digits (Spitbol's
&FMT)"*. That was inferred from `2 ** 0.5` → `1.4142135623731`, which **is** 14 printed digits — because its 15th
digit is a `0` and trailing zeros strip. The probe's own `.ref` disproves it on the next line: `1/3` is
`0.333333333333333`, fifteen threes. Measured 15 across `1/3`, `2/3`, `1/7`, sqrt 2, pi, `1.0e20`, `1.0e-20`,
`123456789012345678.0`. The four checked-in gimpel driver `.ref`s corroborate independently (`ARC_driver.ref` carries
`1.0471975511966`), as oracle-generated files nobody wrote by hand.

⭐ **That probe was RED and is now GREEN, uncommanded** — the row's bonus cure. The fix is one line: `real_str`'s
shortest-round-trip search loop becomes a fixed `%.14e` (15 significant digits), and the existing trailing-zero strip
below it already produced the rest of SPITBOL's shape.

## The eight, and their error arms

Registered in `src/runtime/core/core.c` beside `REMDR`. Each takes ONE argument, coerces INT/REAL/STRING through
`to_real`, and **returns REAL always** — `DATATYPE(SQRT(4))` is `REAL` and `CHOP(7)` is `7.`, both measured. `CHOP`
truncates **toward zero**: `CHOP(-3.9)` = `-3.`, and `CHOP(-0.5)` = `0.` not `-0.` (`real_str` already handled the
negative-zero case correctly).

Domain and overflow arms carry SPITBOL's **own numbered errors**, taken from sbl.min:13223-15753 rather than invented,
and verified against the oracle by number AND message: 301 atan/302 chop/303 cos/304 exp/306 ln/308 sin/309 tan
argument-not-numeric · 305 exp overflow · 307 ln overflow (`LN(0.0)`) · 310 tan overflow · 313 sqrt-not-numeric ·
314 sqrt-negative · 315 ln-negative. These are **hard errors, not statement failures** — measured: `X = SQRT(-1.0)`
with an `:S()F()` goto does not take the F branch, it dies.

## REMDR re-probed as ordered, and it split in two

The brief excluded `REMDR` honestly and told the next seat to re-probe `REMDR(7,3)` first. Done: `REMDR(7,3)` = `1`,
correct — the brief was right to exclude it. But `.cmth` extends remdr to reals **in the same sentence that names the
eight** (sbl.min:260, *"x**y and remdr(x,y) are extended to include reals"*), and `REMDR(7.5,2.0)` gave `1` where the
oracle gives `1.5`. Fixed via `fmod`, reusing `arithmetic.c`'s `operand_is_real_str` as the ONE real/int authority
rather than spelling that decision a second time.

⛔ **REMDR was itself spelled twice** — the s68/s70 disease, live: `core.c`'s `_REMDR_` is **dead** (patching it changed
nothing observable) and `by_name_dispatch.c`'s `bn_remdr` is the live path. Both now agree. I did not delete the dead
one; that is a separate deletion with its own proof burden.

⛔ **NOT FIXED, MEASURED AND NAMED:** REMDR-by-zero raises `ERROR 167 -- remdr caused integer overflow` / `ERROR 312 --
remdr caused real overflow` in the oracle, where SCRIP FAILs the statement. That is a separate divergence whose blast
radius is every program relying on the failure signal. Left red deliberately rather than half-widening this row.

## ⛔ The board moved and IT IS NOT MINE — control-built, said plainly

Final board at post-rebase pristine: **m3 334/3 · m4 327/9 · SKIP 1**. The s191 watermark was **m3 332/5 · m4 325/11**.
That is +2/+2, and **none of it is this rung**.

I built a **control tree** — same commit, my four files stashed, rebuilt, board re-run — and it scored **identically to
the changed tree, fail-set identical BY NAME** (m3 333/4 · m4 326/10 at that moment; both trees). The movement came
from other seats' commits already on origin, arriving through my `git pull --rebase`. Claiming it would have been this
project's own false-signal class in its most flattering direction. **This change is board-neutral by measurement, not
by assumption.**

Independent confirmations that it is codegen-inert: all **five** RULES step-4 regens returned rc=0 having changed
**zero** artifacts (no commit created). Prolog and Icon are unaffected **by construction** — they render reals through
`icon_real_str`/`%g`, a separate path — and the two float-bearing prolog `.ref`s were verified byte-unchanged.

## What did NOT move, checked rather than assumed

The four float-bearing gimpel drivers (`POKEV RAMM TRIG ARC`) still differ from their `.ref`s: all four are
**pre-existing PARSE ERRORS** from the real-literal gap (batch B's `gim_real_literal_parse`), so they never reach
execution and my change cannot touch them. ⭐ **They are, however, the next beneficiaries:** their `.ref`s are made of
exactly the output this rung now produces, so closing the real-literal parse gap should turn them green without
further math work. s190 already named that gap the highest-yield defect in the gimpel corpus; this rung removes its
downstream half.

Snocone smoke is 4/5 — the failing case is `function Double(n)` returning `Error 22 Undefined function called`, a
Snocone function-declaration gap containing none of the eight names. Prolog smoke 3/5 is the s165 standing watermark.

⛔ **The shadowing risk was checked, not waved off:** registering eight new names is exactly Lon's *"reserved words that
are not really reserved"* hazard — a program may use `EXP` or `LN` as an ordinary variable. Swept the SNOBOL4/Snocone
corpus: the only hit is `beauty.sc`, and there the eight appear **inside a string literal** listing SNOBOL4 function
names for the beautifier, not as variables. The identical control board over 337 programs is the mechanical proof.

## Deliverables

`corpus/probe/math/` — 10 probes (one per function + `math_real_precision` + `math_remdr_real`), **every `.ref` live
oracle output**, every one **read before commit** per the s190 lesson that a keyword guard is necessary and not
sufficient (`sbl` exits 0 after a fatal error, so a `.ref` can be an error dump that passes both rc and grep). All 10
green in BOTH modes. `f19_real_numbers.sno` PASSes both modes and gains its live-oracle `.ref`.

Gates green: `emit_no_lang` · `template_medium_invisible` · `icn_no_stack` · `icn_one_reg_frame`.

## NEXT

1. **Real-literal parse gap** (`gim_real_literal_parse`) — now the sole thing between the 4 gimpel float drivers and green.
2. **REMDR-by-zero** 167/312 vs FAIL — named above, needs its own row for the blast radius.
3. **Delete the dead `_REMDR_`** in core.c — a spelled-twice residue, wants its own proof that nothing reaches it.
