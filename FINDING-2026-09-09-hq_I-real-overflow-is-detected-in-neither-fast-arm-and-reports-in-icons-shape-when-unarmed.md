# FINDING 2026-09-09 hq_I — real overflow was detected in NEITHER fast arm, and still reports in Icon's shape when no recovery mechanism is armed

**Measured on** SCRIP `bc9812abe` + this cure, corpus `62759d5ea`, `RT_OPT=-O0`, incremental `make`, box 2026-09-09.
**Witness** `corpus/packages/snobol4/snoflake_suite/real-overflow-recoverable.sno` (snoflake, hq_I's Q–Z slice; red on coo's clean board of 2026-09-09T00:53:36Z).

## What was wrong

`BIG * BIG` with `BIG = 1e192` printed `inf` and took the `S` branch. SPITBOL raises
`ERROR 263 -- multiplication caused real overflow`, and with `&ERRLIMIT` set the statement FAILS to its `F` goto.

The runtime's C authority `rt_num_arith_impl` (`src/runtime/arithmetic.c`) **already had** the finiteness check.
It was never reached, because the same operation has **two** fast arms in front of it, and neither checked:

1. `src/templates/bb/bb_binop_arith.cpp` — the inline `addsd`/`subsd`/`mulsd` arm stores the result as `DT_R` unconditionally.
   Its **integer** twin on the very next lines deflects on overflow (`x86("jo", L(0))`); the real twin had no equivalent.
2. `src/runtime/rtx/rtx_arith.s` — `rt_add`/`rt_sub`/`rt_mul` repeat the identical shape one layer down:
   an integer arm with `jo → .L*_slow`, a real arm with no check at all.

⭐ **The reusable part: a check in the authority is worth nothing while a fast arm answers first.** Both arms were written
by analogy to the integer path and both copied the arithmetic while dropping the guard — and the guard is the only line that
distinguishes "this arm may answer" from "this arm must defer". Fixing arm 1 alone moved the bug from `inf` to `inf`, because
arm 2 caught the deflection and gave the same wrong answer. **Grep for every arm of an operation before crediting a check in
its authority** — here `grep -n 'mulsd' src/` was the whole census and it returned both.

## The cure

Both arms now deflect a non-finite result (all-ones exponent, i.e. `(bits << 1) >= 0xFFE0000000000000`) to the C authority,
exactly as `jo` does for integers. Deferring is always safe: when an *operand* was already non-finite the authority returns the
same value, so the guard costs a slow path only on an already-exceptional operation.

`rt_num_arith_impl` then routes the event by **which recovery mechanism is armed — state, not a language name**
(`rt_real_overflow`): Icon's `&error` counter (`g_error`), else SNOBOL4's `&ERRLIMIT` (`kw_errlimit`) via
`core_runtime_error` with the SPITBOL per-op codes 261/262/263/264/266 — the shape `core.c` already used for REMDR 312.

## ⛔ RESIDUE — NOT CURED HERE, and it is a real defect

When **neither** mechanism is armed, an overflowing SNOBOL4 program still prints Icon's diagnostic:

```
$ scrip ovr2.sno          # same program, no &ERRLIMIT
Run-time error 204 / real overflow, underflow, or division by zero      rc=1
$ sbl -bf ovr2.sno
ovr2.sno(7) : ERROR 263 -- multiplication caused real overflow          rc=0
```

Left alone deliberately: the unarmed path is also **Icon's correct output** (verified against
`/home/resources/icon-master/bin/iconx`, which prints the same two lines plus a traceback), so choosing a diagnostic shape
there needs a state carrier saying which surface the program reports on. Guessing one regresses Icon. No snoflake fixture
depends on it. Worth a row of its own.
