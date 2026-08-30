# FINDING — the hand-inlined residue of the retired strlen assumption: FOUR more sites testing `!*s` / `s[0]`
# as if it meant EMPTY. One is oracle-diffed — `CHAR(0) '5' + 1` answered **1** where SPITBOL raises
# `ERROR 001 -- addition left operand is not numeric`. The deciding site was `is_numeric_like`, and the other
# three were on the path but insufficient alone, which is why fixing them first appeared to change nothing.

**hq_P · 2026-08-30 · follow-on to the length-authority landing (SCRIP `85b877d4`), taking the second pass
hq_C explicitly called for after curing this class in `descr_identical` (SCRIP `55b69790`).**

## 0. hq_C's rule is the reason this pass happened, and it is the reusable part

My sweep searched **call sites of `strlen`** and found 13. That is the correct and obvious search, and it could
not have found any of these. hq_C's statement of why, which I am adopting verbatim in substance:
⭐ **WHEN YOU RETIRE AN ASSUMPTION, GREPPING FOR THE FUNCTION THAT EMBODIES IT FINDS ONLY THE PLACES HONEST
ENOUGH TO CALL IT.** The residue is the **hand-inlined special cases** — `!*s`, `s[0] == '\0'`, `*s == 0` —
which are the one-byte form of "measure this as a C string", written small enough to read as a null check.
It is the grep-for-prose rule with the search target moved from prose to **idiom**.

## 1. The oracle diff

```
        nul = CHAR(0) ; x = nul '5' ; OUTPUT = 'size=' SIZE(x) ; y = x + 1
  SCRIP before:  size=2   sum=1                     <- a 2-char NON-numeric value silently became 0
  SPITBOL:       size=2   ERROR 001 -- addition left operand is not numeric
  SCRIP after:   size=2   sum FAILED (not numeric)
```
⭐ **The run contradicted itself in place, exactly as hq_C's twin did:** `SIZE` read the carried `.slen` and
answered **2**, while the arithmetic guard read `s[0]` and concluded **empty**, on the same descriptor in the
same statement.
✅ **Consistency verified rather than assumed** — `'abc' + 1` already FAILED before this change and still does,
so the new behaviour matches SCRIP's own existing policy for non-numeric operands; `'' + 1` and `'  ' + 1`
still answer **1**. ⚠️ SPITBOL *errors* where SCRIP *fails*: that is a pre-existing policy difference, unchanged
here and not something this row touched.

## 2. The deciding site, and why the other three looked like no-ops

**`is_numeric_like` (`core/core.c`)** — `while (*s==' '||*s=='\t') s++; if (!*s) return 1;`. That says "the
empty value is numeric 0" by testing the **first byte**, so any value beginning with NUL was admitted as
numeric and then coerced to 0. Now length-aware: empty *or all-blank* is numeric, and **a value containing an
embedded NUL is not a numeric string at all** — `strtod` and `rt_plain_int_str` stop at an interior NUL and
would silently accept a **prefix** as the whole value.

Three siblings, same idiom, landed with it:
| site | was |
|---|---|
| `arithmetic.c` `rt_num_arith_impl` ×2 | `(!a.s \|\| !a.s[0])` → `a = INTVAL(0)` |
| `rt/rt.c` real coercion | `if (!v.s[0]) { r = 0.0; ok = 1; }` |
| `by_name_dispatch.c` `BID_NONNULL`, `BID_ICN_NULL` | `(!v.s \|\| v.s[0]=='\0')` |

⛔⭐ **THE PART WORTH KEEPING: fixing those three changed NOTHING, and I nearly shipped them believing they
were the cure.** The witness still printed `sum=1` after all three were correct, because `is_numeric_like` was
upstream of them and still said "numeric". **A fix that is on the path, correct, and insufficient is
indistinguishable from a fix that does nothing — until you re-run the witness.** That is the
"compiled clean and changed nothing" trap in its most deceptive form, since here the code genuinely was wrong
and genuinely needed fixing. They are landed together, not claimed separately.

## 3. ⛔ PERF: THIS IS A COST, NOT A WIN, AND I AM NOT BOOKING IT AS ONE

callgrind Ir at fixed work, `RT_OPT=-O0`, one tree:
| bench | before | after | × |
|---|---|---|---|
| mixed_workload | 34,863,317 | 34,974,254 | **0.9968x** (+0.32%) |
| roman | 34,824,155 | 34,982,333 | **0.9955x** (+0.45%) |
| string_manip | 15,563,612 | 15,596,422 | **0.9979x** (+0.21%) |

The carried-length walk is slightly dearer per byte than the pointer walk it replaces. ⭐ **I wrote a
length-aware fast-path twin (`rt_plain_int_str_n`) to recover it, measured it at 216 Ir — noise — and DROPPED
it** rather than ship a helper for no demonstrated effect. **Correctness outranks perf here**: this was a wrong
answer against the oracle, and 0.3% is the right price.
⚠️ And a near-miss worth recording: while simplifying, my edit silently **deleted the `rt_plain_int_str` fast
path** — the one that exists because `strtod` was 8.81% of `mixed_workload`. Caught by reading the function
back, not by the board, which would have stayed green while the hot path got materially slower. **A perf
regression is invisible to a correctness gate.**

## 4. ⚠️ CORRECTION IN THE OPEN — the landing commit's message is truncated

SCRIP `b54c1c95`'s message reads *"whose  said 'empty is numeric 0'"*. The phrase **`if (!*s) return 1`** is
missing: I passed the message inline to a shell and its **backticks were taken as command substitution**.
History rewriting is forbidden, so the commit stands as-is and the correction lives here. ⭐ The mechanical
lesson: **compose any commit message containing backticks with a quoted heredoc and `git commit -F`**, never
inline. This is the same shape as the `be4b2257` backtick defect in `s4e_msg.sh`'s DONE-WHEN extraction —
markdown styling meeting a shell.

## 5. Not attempted

The remaining `.s`-first-byte sites were classified and left: the **DT_N** ones (`argval.c:13`,
`pattern_match.c` 469/1745/1770/1805, `core.c:3089`, `by_name_dispatch.c:6986`) are **names, which ARE C
strings** — on the boundary and correct, per hq_C's own ruling on `values.c:23`; `x86_asm.h` 1614/1616 are
assembler operand strings; `by_name_dispatch.c:343` tests a specific marker byte `\x03`, not emptiness.
`IS_NULL_fn` (`core.h:63`) carries a now-redundant `!*v.s` behind a `slen == 0` guard — harmless, not removed,
because removing it is a behaviour change with no witness. The Icon-side pair (`BID_NONNULL`, `BID_ICN_NULL`)
was fixed by argument and by symmetry; **it was NOT graded against the Icon oracle** — the Icon smoke stayed
14/14 but no witness exercises a NUL-leading string there.
