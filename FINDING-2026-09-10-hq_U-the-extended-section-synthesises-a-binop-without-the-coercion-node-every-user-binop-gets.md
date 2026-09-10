# The extended section synthesises a BINOP without the coercion node every user-written binop gets

**hq_U, 2026-09-10.** SCRIP `b84976b17` + the subscript-index cure of this sitting. Oracle: Arizona icont/iconx 9.5.25a (`/home/resources/icon-master/bin`).

## The claim

`s[i+:n]` and `s[i-:n]` with a non-numeric bound **fail with no error account at all**, where icont
converts a **102** (`numeric expected`). Not a subscript defect — the section box never sees the bad
operand. It is a **missing `IR_COERCE_NUMERIC`** on the addition the Icon lowerer synthesises for the
extended form.

## The measurement

```
procedure main()
   local q; q := "q";
   &error := -1;
   if x := "abcdef"[2+:q] then write("plus ok ", x) else write("plus failed");
   write("  n=", &errornumber) | write("  NO ACCOUNT");
end
```

| arm | icont | SCRIP m3 and m4 |
|---|---|---|
| `"abcdef"[2+:"q"]` | fails, `n=102` | fails, **NO ACCOUNT** |
| `"abcdef"[2-:"q"]` | fails, `n=102` | fails, **NO ACCOUNT** |
| `"abcdef"[2+:q]`   | fails, `n=102` | fails, **NO ACCOUNT** |
| `"abcdef"[q+:2]`   | fails, `n=102` | fails, **NO ACCOUNT** |
| `2 + q` written by hand | fails, `n=102` | fails, `n=102` ✅ |

The last row is the whole finding: **the same addition raises correctly when the programmer writes it
and silently coerces when the lowerer writes it.**

## Where it goes wrong

`--dump-ir-verbose` on the third arm gives `BINOP [23,24] binop=0` feeding `SUBSCRIPT [22,23,25]` — an
ordinary `IR_BINOP` ADD with **no `IR_COERCE_NUMERIC` above it**. A hand-written `2 + q` lowers to
`n14_coerce_numeric_bx` → `c_rt_coerce_num2_d` (`src/runtime/rt/rt.c:332`) → `core_icn_error(102, …)`,
confirmed under gdb. The synthesised one goes straight to `rt_add` → `c_rt_add` → `rt_num_arith_impl`,
which is the **SNOBOL4-shared** arithmetic path and coerces `"q"` to `0` without raising — also
confirmed under gdb (breakpoint on `c_rt_add` hits, breakpoint on `core_icn_error` never does). The
section box is then handed a perfectly numeric end of `2` and has nothing to object to.

**Lane:** `src/lower/lower_icon.c` — reachable through the Icon frontend only, so by CLAUDE.md's
custody rule it is the language HQ's, not the shared engine's. `IR_SUBSCRIPT` itself is shared
(Icon 3 sites, SNOBOL4 4) and is cured this sitting by
`test_gate_icn_subscript_index_is_checked_and_the_account_is_written.sh`, which **deliberately
excludes** `+:` / `-:` from its want so the gate does not claim a shape it does not cover.

## ⭐ The general form, and why it cost three false readings before it was pinned

**A DIAGNOSTIC THAT PERSISTS BETWEEN OBSERVATIONS TURNS ANY UNRAISED FAILURE INTO A GREEN ROW.**
`&errornumber` survives until the *next* converted error, so a probe whose expression fails without
raising reads back the **previous** probe's number and looks cured. Three readings were wrong this way
before the reset went in:

1. `"abcdef"[2+:"q"]` read `n=101` in a multi-row probe — it was the preceding row's 101.
2. `L["q"]` read `n=101` — the preceding row's, confirmed by a `core_icn_error` breakpoint that never fired.
3. Cutting the want **from icont itself** produced three rows carrying `101` where icont raises nothing
   at all. The oracle is not a defence: the oracle has the same sticky keyword.

The cure is one line per row — `errorclear(); &error := -1;` — and it is what makes `n=-` an
*observable* rather than an absence. Three of the twenty rows in the landed gate assert `n=-`, and two
of those are shapes where icont deliberately raises nothing (a record field name that is not a field,
an out-of-range index). A gate written without the reset would have graded those green by accident and
a gate written to "fix" them would have raised where Icon must not.

This is the same shape hq_T named on 2026-09-10 as **the fast block** (an answer returned ahead of its
own error machinery) and hq_P as **the wrong oracle** (agreement with the wrong authority): the output
is non-empty, well-formed, stable and wrong, so rc, range and run-to-run agreement all bless it.
Here the sticky keyword adds a fourth: **agreement with your own previous answer**.

## The row

`icon-extended-section-bound-coerces-where-icont-raises-102` — DONE-WHEN: the four arms above report
`n=102` in m3 and m4 with the account reset per row, and the subscript gate stays green.
