# FINDING 2026-09-05 (hq_B) — every Icon class cured today had a LOUD half and a SILENT half, and only value-grading saw both

Four classes were cured or routed in one sitting. Each was **raised by its loud symptom** — a parse error, an
abort, a FATAL — and each turned out to contain **a second shape that exits 0 and prints a wrong answer**. In
three of the four, a cure graded on the loud symptom alone would have closed the row with the silent half intact.

| class | loud half (how it was raised) | silent half (found only by grading values) |
|---|---|---|
| braced control branch as an operand | `case x of {...} + 2` → `parse error: expected ;` | `if x then {1} else {9} + 2` must be **1** (operator absorbed into the else branch), not 3 — a cure that binds both as a left operand compiles cleanly and is wrong |
| chained swap | `x :=: y :=: z` → rc=134 FATAL | `x :=: (y := 5)` → rc=0 printing `21` where iconx prints `51`: the inner assignment's effect dropped, the two names swapped anyway |
| Icon arithmetic coercion | seat05's rung41 witness failed | `x := "abc"; write(2 + x)` → rc=0 printing `2`; and `&error`/`&errornumber`/`errorclear` looked broken **only because there was never a real error event to catch** |
| SNOBOL4 immediate capture (routed to hq_S) | `P $ *(N = N + 1)` → rc=134 `[IDX] BOMB` | hq_S then found `P $ *(.N)`, a name-VALUED target: prints `MATCH N=A` where sbl prints `NOMATCH N=0`, **no crash**, never filed by anyone |

## Why the loud half is the misleading one

A crash is self-reporting: it names itself, it stops the program, and any census with an `rc != 0` predicate
finds it. The silent half is invisible to exactly those instruments — **a crash census, a compile-delta, an
xfail sweep, and a green board all miss it**. hq_I measured the braced-branch class as 203 of 307 remaining IPL
compile failures; had that lever been graded by compile-delta, we would have booked 203 files as cured and
shipped a wrong answer inside every `if`-`else` that carried a trailing operator.

⭐ **The two-forms trap generalises:** `case x of {default: 1} + 2` is 3 in iconx (the case value IS the left
operand) while `if x then {1} else {9} + 2` is 1 (the operator joins the else branch). One cure, two required
answers. *Any* fix that treats "let the expression continue after `}`" as the whole story returns 3 and 3.

## The near-miss that proves the method (hq_S, same day, on my gate)

The strongest evidence is a cure that **passed both of our witnesses and was still wrong**. For the capture
class, the obvious fix reuses the existing `-1` retreat path for a non-name target. It turns the core dump into
a clean `NOMATCH` — correct on my witness and on hq_S's. Only the **side-effect count** betrays it: a target that
FAILS makes the node recede once per scan position (`N=3`), while a non-name target ABORTS the whole match
(`N=1`). hq_S built it, measured it, and it failed 4 of 17 oracle-diffed witnesses. **A gate that accepted
`NOMATCH` would have shipped it.**

## What this changes about how a gate is written

1. ⛔ **Grade by VALUE against the oracle, never by rc, and never by "does it still crash".** rc is not evidence
   about semantics; the absence of a FATAL is not evidence of a correct answer.
2. ⭐ **Run the oracle inside the gate rather than hardcoding its output.** Two gates written today do this and
   both earned it: the expectation cannot drift, and the next reader learns *why* the answer is the answer.
   hq_S: *"I would have hardcoded NOMATCH and N=1 and never learned that the deferred and immediate forms reach
   the same answer by different routes."*
3. ⭐ **Put the already-correct sibling in the gate as a control arm.** `"12" + 2 = 14` and `"3" * "4" = 12`
   are what stop the coercion cure from making every string operand an error; the conditional capture twin is
   what stops a cure that refuses every non-name target earlier. A control arm that is **red before the cure**
   is not a control arm — it discriminates nothing about the cure direction (hq_I caught and renamed one of
   their own today).
4. ⛔ **Refuse rc=2 unless every required run was graded.** Each gate counts its runs; a gate that grades three
   of four prints the success shape over the gap.

## The residues, named rather than hidden

- Chained swap re-derives the left target, so a side-effecting subscript base (`x :=: (L[f()] := 3)`) evaluates
  it twice where icont evaluates once. Zero such shapes in the corpus (all 36 chained `:=:` lines in IPL are
  plain names).
- The coercion cure is correct in C and shortcut in assembly: `2 + &null` and `2 + ""` still print 2 because
  `rtx_icnnum.s` answers for `DT_SNUL` and the blank string without consulting the protocol code. **Proved by
  ablation** — the same programs under `SCRIP_RTX_ICNNUM=0` raise 102 — and routed to hq_I with the ablation
  built into the gate as a control arm, so a "fix" that weakens the C path turns that arm red instead of turning
  the gate green.
