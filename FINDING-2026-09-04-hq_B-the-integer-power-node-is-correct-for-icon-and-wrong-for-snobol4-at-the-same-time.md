# FINDING 2026-09-04 hq_B — the integer-power node is correct for Icon and wrong for SNOBOL4 at the same time

**Row:** `snobol4-snoflake-suite-180-to-100-percent-by-class` (witness `integer-negative-exponent`)
**Tree:** SCRIP `a34b693e9` · corpus `33e747c2c` · RT_OPT=-O0 · oracles: `sbl -bf` (post-swap `c0dc231`), `/home/resources/icon-master/bin/icon`

## The witness

snoflake's `integer-negative-exponent` is three lines. SCRIP prints `0`, SPITBOL prints
`0.111111111111111`. That looks like a one-line fix, and it is not.

## What SPITBOL requires

Measured across nine forms — **integer ^ NEGATIVE integer is ALWAYS a REAL in SPITBOL**, with no
exceptions for the cases the code special-cases:

| expr | `sbl -bf` | SCRIP today |
|---|---|---|
| `2 ^ -1` | `0.5` REAL | `0` INTEGER |
| `9 ^ -1` | `0.111111111111111` REAL | `0` INTEGER |
| `2 ^ -3` | `0.125` REAL | `0` INTEGER |
| `-2 ^ -2` | `0.25` REAL | `0` INTEGER |
| `1 ^ -5` | `1.` **REAL** | `1` INTEGER |
| `-1 ^ -3` | `-1.` **REAL** | `-1` INTEGER |
| `0 ^ -1` | `0.` **REAL** | *(nothing — fails)* |
| `10 ^ -20` | `0.999999999999992e-20` REAL | `0` INTEGER |

⭐ Note `1 ^ -5` and `-1 ^ -3`: SPITBOL returns the right *number* but the wrong *type* compared to
SCRIP, so a fix that only chased the visibly-wrong rows would still leave `DATATYPE` divergent on
the rows that "already looked right". And `0 ^ -1` is `0.`, not the `inf` C's `pow()` produces —
that one needs an explicit arm.

## Why it is not a one-line fix

`src/runtime/arithmetic.c:190`:

```c
static DESCR_t rt_ipow_descr(int64_t li, int64_t ri) {
    if (ri >= 0) { int64_t acc = 1; for (int64_t k = 0; k < ri; k++) acc *= li; return INTVAL(acc); }
    if (li == 1)  return INTVAL(1);
    if (li == -1) return INTVAL((ri & 1) ? -1 : 1);
    if (li == 0)  return FAILDESCR;
    return INTVAL(0);
}
```

That reads like an oversight. **It is not — it is Icon's semantics, implemented correctly.** The
same node serves `BINOP_POW` for both frontends, and the Icon oracle disagrees with SPITBOL:

```
$ icon  : write(2 ^ -1) -> 0      write(9 ^ -1) -> 0      write(1 ^ -5) -> 1
$ scrip : write(2 ^ -1) -> 0      write(9 ^ -1) -> 0      write(1 ^ -5) -> 1     (icon frontend, matches)
$ sbl   : OUTPUT = 2 ^ -1 -> 0.5  OUTPUT = 9 ^ -1 -> 0.111…  OUTPUT = 1 ^ -5 -> 1.
```

⛔ **So the node is simultaneously right and wrong, and which one it is depends on who is asking.**
Changing it to satisfy SPITBOL breaks four Icon witnesses on the spot; leaving it keeps snoflake
red. This is SHARED-NODE VERDICT SCOPE arriving in its purest form: the defect is not in the
function, it is in the fact that one function is answering two different languages' questions.

⭐ **The thing that makes this class dangerous is that the code looks careless.** Four special-cased
`if`s returning integers is exactly what a hasty implementation looks like, so the tempting move is
to "clean it up" into the mathematically obvious `pow()` — a change that is correct by SPITBOL, an
improvement by appearance, and a silent four-witness regression in another language. **The tell that
saved it here was cheap and general: before editing a shared runtime helper, run the OTHER
frontend's oracle on the same expression.** Two minutes.

## What the cure has to look like

Not a language name. `RULES.md` forbids `LANG_*` past the frontend/lower boundary, and shared
helpers must branch on *what* differs — a behavioural description — never on who is asking. The
difference here has a clean name: **does `integer ^ negative-integer` promote to real, or truncate
toward zero in the integer domain?** That is a property of the arithmetic contract the frontend
lowers under, and it belongs in the operation's own description, carried from lower, in the same
way other behavioural distinctions already are.

Filed as `snobol4-integer-negative-exponent-promotes-to-real-without-breaking-icon`, with the
constraint written into the GOAL so the next person does not rediscover the Icon half by breaking it.

## Also measured, and deliberately not acted on

Two further snoflake witnesses were characterised the same sitting and are *not* this class:
`stlimit-nonnegative` (SPITBOL raises `ERROR 244 statement count exceeds stlimit`; SCRIP enforces
nothing and runs to the runner's timeout) and `string-pad` (both engines refuse the program, with
different wording and no ERROR number on either side — the one shape the CEO-251 error-number
normalisation cannot compare). ⭐ A census of that last shape over all 70 m3 failures found exactly
**2**, which is why no third normalisation was added: the measurement said the gap was not worth a
rule change, and saying so is the result.
