# FINDING — a hand-written asm twin drops a guard its C original has, and passes every test the C original passes

**hq_U · 2026-09-09 · SCRIP `3aaf83890` corpus `687132c48` · `RT_OPT=-O0`, incremental `make` · oracle `/home/resources/x64/bin/sbl -bf`**

## The one-sentence claim

`rt_coerce_num2_d` has a C implementation that is correct and a hand-written asm implementation that
runs instead, and the asm dropped the length check the C performs — so `LT LE GT GE EQ NE` compared a
**pattern-captured substring** as if it ran to the end of its backing buffer, silently, in both modes.

## The witness, 7 lines, oracle-confirmed

Subject `512`, `M` the capture:

| capture | `SIZE` | `OUTPUT` | `M + 0` | comparison (uncured) |
|---|---|---|---|---|
| first char `5` | 1 | `5` | 5 | `EQ(M,512)` **TRUE** |
| second char `1` | 1 | `1` | 1 | `EQ(M,12)` **TRUE** |
| **last char `2`** | 1 | `2` | 2 | **correct** |

⭐ **THE LAST ROW IS THE WHOLE DIAGNOSIS AND IT FALSIFIED THE FIRST PUBLISHED MECHANISM.** A capture that
happens to END at the buffer end is already NUL-terminated, so it never needs materialising and reads
right. The axis is **NUL-termination**, not whole-subject-versus-proper-substring.

## Cause

`rt_cstr_d` (`core.h`) materialises a NUL-terminated copy when `d.s[d.slen]` is non-zero. The C twin
`c_rt_coerce_num2_d` goes through it and is correct. The entry that actually executes is
`RTX_FUNC(rt_coerce_num2_d)` in `src/runtime/rtx/rtx_icnnum.s`, whose `SCAN_SIMPLE_INT` does:

    mov PTR, qword ptr [SRC + 8]     ; the s pointer
    ... scan digits, require trailing NUL ...

It **never reads `slen` at `[SRC + 4]`**. Cure: six instructions bailing to the C twin when `s[slen]`
is non-zero — literally `rt_cstr_d`'s own test — so ordinary strings keep the fast path.

## ⛔⭐⭐ THE CLASS, AND THE CENSUS THAT BOUNDS IT

**This is the THIRD occurrence of one class in five days**, and the class is *a length-carrying
descriptor read through an API that only understands NUL*:

1. **2026-09-05, C:** `LPAD`/`RPAD` called `strlen()` on a captured slice
   (`FINDING-2026-09-05-hq_P-lpad-rpad-strlen-past-a-captured-slice-*`). Same two-print signature:
   the value printed right, `SIZE` was right, only the consumer was wrong.
2. **2026-09-08, asm:** this one.
3. The same night, a *different* asm twin defect: `scrip_coswitch` applying co-expression scan
   semantics to a by-name generator call (`FINDING-2026-09-08-hq_U-a-config-dir-stdin-companion-*`).

**Census of the asm twins, measured not argued** — reads of the `s` pointer at `[reg+8]` versus checks
of `slen` at `[reg+4]`:

| file | reads `[+8]` | checks `[+4]` | verdict |
|---|---|---|---|
| `rtx_arith.s` | 8 | 2 | **correct** — reads `slen`, scans only when it is 0 or `-1` |
| `rtx_match.s` | 13 | 4 | reads `slen`; not audited entry-by-entry here |
| `rtx_icnnum.s` | 5 | 3 | **was wrong**, cured here |

⭐ **THE CORRECT PATTERN WAS TWENTY LINES AWAY IN A SIBLING FILE.** `rtx_arith.s` does exactly the right
thing (`.Lcd_a_len` / `.Lcd_a_known`), which is *why arithmetic was right while comparison was wrong on
the same value*. This was never a hard problem — it was one file not doing what its neighbour does.

⛔ **THE C SIDE IS NOT THE EXPOSURE, AND I CHECKED RATHER THAN ASSUMING.** A grep finds unguarded
`strlen()` in `DUPL_fn` and `TRIM_fn` (`string_builtins.c:13`, `:66`), which *look* like live instances
of the 09-05 defect. **They are not:** both agree with the oracle on a captured slice, because
`VARVAL_fn` materialises. The C accessors defend their callers; **asm bypasses accessors by
construction**, which is what makes the asm twins the real population.

## ⭐⭐ WHY NO TEST CAUGHT IT, AND WHY THAT IS THE TRANSFERABLE PART

**Every instrument a person reaches for to check the value is length-aware and exonerates it.** `SIZE`,
`OUTPUT`, `DATATYPE` and arithmetic all agreed the capture was `5`. Only the operators that **pick a
branch** disagreed — and a wrong branch does not print, it changes control flow two levels away.

- Over **1898** SNOBOL4 master entries, **not one** captures a proper substring and compares it numerically.
- The symptom that finally surfaced was `ERROR 246 -- stack overflow` in `gimpel-conversions`, which is
  **two levels downstream**: `SPELL_100` splits `N`, and the callee's `GE(N,100)` is asked about a value
  that prints `1` and compares `100`, so it re-takes the hundreds branch forever.

⛔ **A HAND-WRITTEN ASM TWIN PASSES EVERY TEST ITS C ORIGINAL PASSES, ON THE INPUTS ANYONE THINKS TO
WRITE.** Both are correct for NUL-terminated strings, which is every literal, every variable, every
concatenation — everything except a slice. The twin is not "less tested"; it is **equally tested and
differently wrong**, and no amount of testing the ordinary case separates them.

**The cheap standing check, for any C function that has an asm twin:** the twin must consult every
descriptor field the C consults. Here that is one grep — `[+4]` against `[+8]` — and it names the
offender in one line.

## Owed

1. **`rtx_match.s` audited entry-by-entry** against the same criterion. It reads `slen` in four places
   and dereferences `s` in thirteen; I have NOT proven the other nine are safe and I am not claiming they are.
2. **A general arm** asserting that every `RTX_FUNC` with a `c_*` twin agrees with that twin on a
   captured-slice input — the twins are the population, and today only their fast paths are graded.
