# FINDING — the Icon extended-section endpoint was resolved a SECOND time instead of being required in range

**Seat:** hq_B · **Date:** 2026-09-03 · **Row:** `icon-master-board-is-two-below-watermark-and-the-board-never-names-the-failures` (ICN4)
**Trees:** SCRIP `508c1182` → cure `dec0d7e2` · corpus `2482cbf3` · `.github` `bc74c857` · RT_OPT=`-O0`, incremental `make`

## THE NUMBER, RECONCILED — three readings were three trees, and none was wrong

| reading | tree | m3 / m4 | who |
|---|---|---|---|
| 377 | SCRIP `e751405f` | PASS=377 FAIL=3 | hq_B, earlier session |
| 378 | SCRIP `f4d69ac83` | PASS=378 FAIL=2 | hq_C, two byte-identical arms |
| floor 379 | a third tree | pinned watermark | — |
| **380 FAIL=0** | **`dec0d7e2`** | **PASS=380 both modes** | **this cure** |

The reconciliation is not arithmetic, it is provenance: the suite GREW between readings and the watermark was
re-pinned 377→379 in the same window. ⭐ **A denominator has a timestamp as surely as a numerator** (hq_C's
phrasing, and it is the whole lesson of this row). The cure closes the gap in the only way that reconciles all
four: FAIL=0, so every tree that can still be checked out now agrees.

## THE DEFECT

`subscript_get2_ext` — the entry point for Icon's `x[i+:n]` / `x[i-:n]` — was a **pure passthrough** to
`subscript_get2`, the plain `x[i:j]` section. So the extended forms were graded by the plain rules:

    if (jj < -slen || jj > slen + 1) return FAILDESCR;   /* range -len..len+1  */
    if (jj <= 0) jj = slen + jj + 1;                     /* SECOND resolution  */

Icon's rule is different and stricter: the start is a **position specification** (negative and zero legal), but
the endpoint reached by the arithmetic is an **absolute position** that must land in `1..len+1`. It is never
re-resolved. There is no wraparound. The corpus witness says so in its own source:

    limage("u", x[-3+:6]) | write("u. wraparound failed");   # should fail

**Two compounding halves.** The second was invisible while the first was masking it:

1. The lowering (`lower_icon.c:708-728`) computes the `IR_BINOP` on the **raw** start expression, not the
   resolved absolute one. On a 9-element list `x[-3+:6]` became `-3+6 = 3` where Icon computes `abs(7)+6 = 13`.
2. The runtime then re-resolved that endpoint as a position spec, so an out-of-range result silently wrapped
   into a legal section instead of failing.

Worked, `x = [1..9]`, `len+1 = 10`: `x[-3+:6]` → raw `3`, paired with resolved start `7`, swapped to `(3,7)`
→ `3 4 5 6`. Icon: `7+6 = 13 > 10` → **fail**. And `s = "abcde"`, `s[3+:-8]` → `3-8 = -5`, re-resolved to
`5-5+1 = 1`, giving `s[1:3]` = `"ab"`. Icon: `-5 < 1` → **fail**. Every one of the twelve diverging lines is
reproduced exactly by this model, in both directions (`+:` and `-:`), on both strings and lists.

## THE CURE — and why the frozen lowering did not have to move

Confined to `subscript_get2_ext`. The delta is recovered as `to_int(end) - to_int(i)`, which is `±n`
**whichever way the start was written**, because both operands of the lowered BINOP are raw. So the absolute
start can be computed here, the arithmetic redone on it, and the result range-checked — with no new IR node,
no new operand, and no change to the lowering:

    long raw_i = (long)to_int(i), delta = (long)to_int(end) - raw_i;
    if (raw_i < -len || raw_i > len + 1) return FAILDESCR;
    long a = (raw_i <= 0) ? len + raw_i + 1 : raw_i, b = a + delta;
    if (b < 1 || b > len + 1) return FAILDESCR;
    return subscript_get2(arr, INTVAL(a), INTVAL(b));

⭐ `subscript_get2` is handed two **absolute** positions, so its own resolution is a no-op on them and its
swap-and-slice is reused unchanged. **It is not edited at all** — the plain section and every SNOBOL4 caller
are therefore unaffected *by construction, not by luck*, which is the only form of that claim worth making.

**SHARED-NODE SCOPE, answered before editing rather than after:** the `"+"`/`"-"` sval arm of `IR_SUBSCRIPT` is
written at exactly two lines, `lower_icon.c:712-713`, and read at exactly one, `bb_section.cpp:32`. Rebus has
its own `+:` token but its grammar builds `TT_IDX`, not `TT_SECTION_PLUS`. **This node is Icon-only**, so the
class is not hq_C's to take. The SNOBOL4 board was still run as a control arm, because the *file* is shared
even though the *node* is not.

## ⭐ THE REUSABLE SHAPE — a delegation that is correct for the caller it was copied from

`subscript_get2_ext` existed, was called, was named for the right thing, and did nothing. A one-line
passthrough reads as *deliberate reuse* — the reviewer's eye supplies a justification the code never made — and
it is indistinguishable at the call site from a function that actually implements the narrower contract. It had
been correct for the plain section it delegated to, and it was wrong for the only caller it actually has.

This is the same family as the two other traps measured in this lane today: hq_C's `betas[k] ? betas[k] :
lbls[k]`, a fallback whose guard can never be false, and hq_T's `2>/dev/null` discarding the failure names four
inches from where they were wanted. All three **survived review by looking like the thing they were not**.
The cheap test that catches this one: *what narrower contract does this wrapper's name promise, and where in
its body is that promise kept?* If the answer is "nowhere, it forwards", the wrapper is a comment.

## CONTROL ARMS — `dec0d7e2` / corpus `2482cbf3`, RT_OPT=-O0, incremental

| arm | result |
|---|---|
| Icon master board | **m3 PASS=380 FAIL=0 · m4 PASS=380 FAIL=0 / 381 (XFAIL=1)** · ast 153/153 · rc=0 (was 378 FAIL=2, RED) |
| the two witnesses | byte-identical to `ALL.ref`, **both modes** |
| Icon smoke | 14/14 both modes |
| SNOBOL4 blocking | m3 PASS=1689 FAIL=0 · m4 PASS=1689 FAIL=0 SKIP=0 MISSING=0 · total=1736 xfail=70 |
| `make test` | rc=0 |

The instrument half of this row was cured by hq_T in the same window (the board now prints its non-PASS entries
by name, from a stderr capture that is deliberately not `2>&1`). This session confirmed it by measurement: the
four `FAIL m3/m4 ...` lines printed, and they are what made the cure a ten-minute ablation instead of a search.
