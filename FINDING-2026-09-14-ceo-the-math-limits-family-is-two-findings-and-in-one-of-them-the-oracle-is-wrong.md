# FINDING — the four `math_limits` programs are TWO findings, and in one of them the oracle is the one that is wrong

**ceo, 2026-09-14, on SCRIP `7331f9ba2`. x64 suite, `math_limits1..4`. One needs a ruling from Lon; the other is our defect and is rowed.**

These four programs binary-search the floating-point limits by printing a decimal at increasing precision and showing what the engine made of it. They read as four failures of one kind. They are not.

## Finding 1 — the UNDERFLOW pair (`math_limits1`, `math_limits4`): we are correctly rounded and SPITBOL is not

The smallest IEEE double is `2^-1074 ≈ 4.94e-324`; round-to-nearest therefore turns anything above **half** of it — `2.4703282292…e-324` — into that denormal, and anything below into zero. That tie point is exactly where our boundary sits:

| decimal | correctly rounded (CPython) | ours | `sbl -bf` |
|---|---|---|---|
| `2.470328229E-324` | `0.0` | `0.` ✓ | (not probed) |
| `2.470328230E-324` | `5e-324` | `0.494065645841247e-323` ✓ | (not probed) |
| `2.999999999E-324` | `5e-324` | — | **`0.`** ✗ |
| `3.000000000E-324` | `5e-324` | — | **`0.`** ✗ |

CPython's `strtod` is correctly rounded and agrees with **us** at both of our boundaries, and disagrees with the oracle at both of its. **SPITBOL flushes to zero up to ~3e-324, which is not the IEEE boundary** — its decimal→binary converter is imprecise at the denormal edge.

⛔ **So matching the oracle here means reproducing a conversion error.** That is a decision, not a fact, and it is the same shape as the ~45 gimpel/snoflake programs already open with Lon (CEO-546): either we adopt SPITBOL's converter bit-for-bit, or these two programs leave the graded set **named with this measurement** as probing the oracle's converter rather than the language. **Put to Lon; not decided here, and nothing excluded in the meantime.**

## Finding 2 — the OVERFLOW pair (`math_limits2`, `math_limits3`): ours, and a real defect

Here the oracle is right and we are wrong, in the other direction:

- `X = 1.797693135E+308` → we print **`inf`**; `sbl -bf` **fails** the conversion (which is what the test renders as its `***` marker).
- `CONVERT('1.797693135E+308','REAL')` → same.
- CPython agrees the value **overflows**.

**SNOBOL4 has no infinity.** We hand the IEEE infinity back as an ordinary value, where every arithmetic overflow path already raises 261/262/263/264 through `rt_real_overflow` — cured for its EVAL arm earlier today. The **conversion** path has no such check: "string to real" is spelled at **eight** `strtod` sites across `keywords.c`, `core.c`, `icn_extfn.c` and `arithmetic.c`, and not one asks whether a finite decimal produced a non-finite double.

⭐ **The cure is one authority, not eight patches** — which is the lesson of the coercion defect cured this morning, where the template path and the dispatcher path disagreed about what a value *was* because each spelled the conversion itself. Row minted: `snobol4-a-real-that-overflows-yields-inf-as-a-value-where-spitbol-fails`, rank 0, with the witness in its DONE-WHEN. The Icon and Prolog readers share those functions, so it is a shared-node cure and its arms batch under CEO-757.

## Why this matters beyond four programs

A suite red is not evidence about the compiler until someone asks **which side is wrong**. Two of these four were us, two were the oracle, and the count alone said "four failures in the math family" — the same reading that put ten `math_*` programs on one root this morning.
