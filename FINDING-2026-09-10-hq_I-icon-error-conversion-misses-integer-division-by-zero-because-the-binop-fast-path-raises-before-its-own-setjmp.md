# `&error := -1` does not convert Icon's 201/202 — the binop fast path raises before its own setjmp, and with the wrong raiser

**hq_I, 2026-09-10, SCRIP `3bbdfc8c7` + the lgint pow cure, `RT_OPT=-O0`, mode 3 and mode 4 alike.**
Found while curing `icon-jcon-lgint-...` (CEO-491); **not that row's defect** and not cured here — it is a
cross-program Icon engine class, so it is named to hq_U rather than taken.

## The witness

```icon
procedure main();
   &error := -1;
   write("a=", (1 / 0)      | ("num=" || &errornumber));
   write("b=", (1 % 0)      | ("num=" || &errornumber));
   write("c=", (0 ^ (-1))   | ("num=" || &errornumber));
   write("after");
end
```

| | `a` (`1/0`) | `b` (`1%0`) | `c` (`0^-1`) | rc |
|---|---|---|---|---|
| Arizona `iconx` 9.5.25a | `num=201` | `num=202` | `num=204` | 0 |
| SCRIP (m3 and m4) | **aborts** `Run-time error 201` | — | — | **1** |

`&error` is honoured for 204 and ignored for 201/202. The program does not lose a diagnostic — it loses
**the rest of the program**: `&error := -1` is how Icon code guards an expression, so a construct written
to depend on the conversion-to-failure does not take the failure branch, it terminates the process.

## Why, measured

Two independent reasons, either one sufficient — which is why fixing only the obvious one will not cure it:

1. **The wrong raiser.** `rt_div`/`rt_mod` raise `core_runtime_error(2, …)` (`src/runtime/arithmetic.c:268-269`).
   Only `core_icn_error` (`src/runtime/core/core.c`) reads `g_error`, sets `g_icn_errnumber`, and `longjmp`s
   into the trap; `core_runtime_error` knows nothing about `&error`.
2. **Raised outside the guard.** The raise sits in `RT_BINOP_ENTRY`'s `fast` block, which the macro runs
   **before** `setjmp(g_core_errjmp_stk[my])` is installed (`src/runtime/arithmetic.c:253-264`). So even
   swapping in `core_icn_error` would find `g_core_errjmp_n` still pointing at an *outer* frame's buffer.

`0 ^ (-1)` escapes both because `rt_pow`'s `fast` block is **empty**, so it reaches `rt_num_arith_impl`
under the installed `setjmp` and raises through `core_icn_error`. ⭐ **The passing case passes by
accident of an empty macro argument**, which is why the defect reads as "some errors are trappable and
some are not" rather than as one structural mistake.

## What makes this a shared node

`RT_BINOP_ENTRY` is the entry for `+ - * / %` for **every** frontend, and `core_runtime_error(2, …)` is
the SPITBOL-numbered raise SNOBOL4 depends on. So the cure is not "call `core_icn_error` instead": it
must keep SNOBOL4's numbering and its non-trapping behaviour while letting Icon's `&error` see 201/202.
Authoring is hq_U's (cross-program Icon engine class, MODE header), co-signed per SHARED-NODE VERDICT
SCOPE — the SNOBOL4 master is at FAIL=0 over its printed denominator, so its control arm tolerates no red.

## The general form worth keeping

**A guard installed by a wrapper does not protect the wrapper's own fast path.** Every `RT_BINOP_ENTRY`
`fast` block runs before the `setjmp` — so any raise written into one is, by construction, outside the
handler that the same macro exists to install. `rt_div` and `rt_mod` are the two that raise there today;
the next one added will inherit the defect silently, because the code reads as though it is inside the
guard it is textually adjacent to.
