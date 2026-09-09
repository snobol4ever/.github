# FINDING 2026-09-08 hq_C — a CONVERT-built EXPRESSION used as a pattern was matched by neither of the two defer closes

**Seat:** hq_C (HQ-COMPLETE) · **Mode:** NONET · **Lane:** Gimpel G-P (Lon 2026-09-08 19:58 CDT — all twelve working seats on the SNOBOL4 package reds until SNOBOL4 is 100%)
**Measured at:** SCRIP `1c5917d9e` (the cure), corpus `e825262b9`, RT_OPT=-O0, oracle `sbl -bf` at `/home/resources/x64/bin/sbl`
**Row:** `flip-gimpel-ONCE_driver` · **Cure:** `src/runtime/pattern_match.c`, one file

## The defect

`CONVERT(s,'EXPRESSION')` produces a value that, **used in pattern position**, was never evaluated.
The match simply failed — no error, no diagnostic, and in the function case **the function was never
called**. `ONCE_driver.sno` in the gimpel package diffed on exactly one line out of seven.

## What localised it

The driver's *other* arm already worked. `ONCE.sno` has two branches, and `ONCE('TAG')` — which goes
through `NAME = 'ONCE..' ID; ONCE = $NAME; $NAME = FAIL`, i.e. indirect reference plus a
pattern-valued variable — produced **correct output in both modes**. Only the null-ID branch, which
returns `CONVERT('ONCE(' &STCOUNT ')','EXPRESSION')`, failed. One driver, one line, two branches, one
of them already green: that is what made this cheap.

## The ablation

Factorial rather than one-at-a-time, and the fourth arm is the one that names the bug:

| # | witness | SPITBOL | SCRIP (before) |
|---|---|---|---|
| T1 | `P = *FN()` — the **star operator** as a pattern | matched, FN called | matched, FN called |
| T2 | `Q = CONVERT('FN()','EXPRESSION')` as a pattern | matched, FN called | **failed, FN never called** |
| T3 | `EVAL(Q)` on that identical `Q` | `xy` | `xy` |
| T4 | `CONVERT("'xy'",'EXPRESSION')` — a bare **literal** — as a pattern | matched | **failed** |

T3 proves the value is well-formed and evaluable. T4 proves **the content is irrelevant**, so this is
not the `&STCOUNT` trunk class (cto's lane — `&STCOUNT` reads correctly here) and not the function-call
path. It is the **tag**. `CONVERT`, `DATATYPE` and `EVAL` were each independently correct the whole time.

## Mechanism

`CONVERT(s,'EXPRESSION')` returns one of two tags: `DT_X` for a bare name, `DT_E` (a compiled eval
chain) for anything else. A variable in pattern position lowers to `IR_MATCH_DEFER` over a manufactured
`PATV$0`, and every producer on that path — `rt_defer_take`, `rt_dtx_drain`, the `DT_X` arms of
`c_rt_defer_open` / `rt_defer_step` / `rt_defer_run_all` — **drains `DT_X`**. Nothing anywhere drained
`DT_E`. Both consumers test for a string-ish tag and fall off the bottom to `return -1`.

⭐ **The two halves of one builtin were split across a handled and an unhandled tag.** The bare-name
half of `CONVERT` always worked; the compiled-chain half never did. A single builtin looked half-alive,
which is why it read as an exotic self-modifying-pattern bug rather than a missing case.

## ⛔ THE PART THAT COST THE MOST: THERE ARE TWO CLOSES, NOT ONE

`c_rt_defer_close` drains the dfx stack; `rt_defer_close_v` takes the value directly and is reached
from `rt_defer_probe_run` → `rt_defer_run_all_v`. They carry **the same literal-matching arms in two
spellings**. The first cure went into `c_rt_defer_close` alone — it **compiled, linked, and changed
nothing**, and the witness output was byte-identical to before. Instrumenting both entry points showed
the failing path reached *neither* probe: it was on the other close entirely.

⭐ **A duplicated rule does not announce itself when you fix one copy — the build is green, the test is
unchanged, and "no effect" reads as "wrong diagnosis" rather than "right diagnosis, wrong copy."** The
cure is therefore a single `rt_defer_expr_value` helper called by *both* closes, not the same four
lines written twice. Anyone adding a tag to one close must add it to the other, or move that arm into
the helper too.

## Regression protection — and it already existed

The SNOBOL4 master already carried this exact program as entry
**`user_function_convert_indirect_branch_1`**, marked **XFAIL** since the gimpel_triage class-6 sweep. It
now **PASSES both modes**, so this landing removes the marker from all three places that record it
(`ALL.sno` banner, `ALL.xfail` attribution, `ALL.csv` xfail column) and the entry becomes real,
blocking protection. This answers the ceo's 2026-09-08 audit order directly: the cure's witness is
**not** leaving a denominator, it is **entering** one.

⭐ Its XFAIL attribution described m3 as `Error 22, undefined function called` and m4 as a compile
refusal — a **mode-divergent** reading that routed the entry to a class row
(`snobol4-xfail-class-convert-expression-indirect-self-reference-mode-divergent`, hq_P). The true
defect was neither mode-divergent nor about undefined functions: both modes failed identically, for
one missing tag. **A marker's diagnosis is a snapshot of what one seat saw once, and it keeps
routing work on that reading long after the reading stops being true.**

## Instrument note — a gate that could not pass

The row's own DONE-WHEN extracted the board's pass count with
`grep -oE "m3_pass=[0-9]+" | grep -oE "[0-9]+"`. That inner grep matches **the `3` in `m3_pass`** as
well as `105`, yielding `3\n105`, so `[ "$v" -ge 105 ]` died with *integer expression expected* and the
gate printed RED **on a board that had actually moved 104 → 105**. It was proven red before the cure —
but it red on its *first* arm (the program-still-red check), so the broken arm was never reached. ⭐ **A
DONE-WHEN proven red is only proven for the arm that fired**; the arms behind it are untested until the
first one goes green, which is exactly when you most want to trust them. Fixed to `cut -d= -f2`.

## Scope

Seven gimpel modules use `EXPRESSION` (`FIND FASTBAL BAL ONCE TEST TSORT VISIT`); `ONCE_driver` was the
only one of the twelve current reds reaching this path, so the flip is one program and the cure guards
the other six. `IR_MATCH_DEFER` is emitted by `lower_snobol4.c` **only** (`grep -rln IR_MATCH_DEFER
src/lower/`), and `DT_E` is produced by no other frontend, so this is not a shared node; the control
arm is the SNOBOL4 master at FAIL=0 over its printed denominator.

## ⭐ Postscript — the seq number moved between the measurement and the landing

The entry was **1912** when measured and **1913** when landed: corpus `4501d2f98` inserted the REWIND
witness ahead of it in the same hour. The rebase conflicted in all four master records, and was
resolved by taking upstream wholesale and re-applying the one edit **by entry name**, deriving the
banner from the file rather than retyping it. ⭐ **A seq is a position in a file other seats are
appending to** — it is the last thing that should anchor an edit, and it is exactly what a marker,
a commit message, or a class row tends to quote.
