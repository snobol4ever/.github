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

## The second near-miss, twenty minutes later, on the same row (hq_S)

hq_S had **17 of 17 oracle-diffed witnesses green in both modes and this gate green**, and could have stopped.
Instead they asked what shape the witness set could not see, and the answer was **nesting** — a capture target
whose own evaluation opens a second match:

| probe | shape | result |
|---|---|---|
| n1 | nested match inside a by-name target | agreed |
| n2 | inner match aborts, **and still reaches its own END** | agreed (`MATCH N=A Q=1`) |
| n3 | inner match aborts and **never reaches its END** | oracle `MATCH N=A Q=1`, theirs `NOMATCH` ⛔ |

The inner abort leaked into the OUTER match and failed a statement that must succeed. The only difference
between the passing and failing probe is whether the inner match reaches its own END — so seventeen green
witnesses and a green gate said nothing at all about the one shape that mattered.

⛔⭐ **The cause was a documented mechanism that is not implemented.** `src/ir/zeta_storage.c:94` states that
`head.capgen_save` is the outer match's `g_cap_gen`, "read at alpha … both exits restore it through
`rt_match_ctx_restore`". That function **takes a capgen argument and ignores it** — `rtx_match.s:180-186`
restore Σ and Σlen and nothing else, and no box writes `g_cap_gen` either. The save half of the sentence is
true; the restore half is fiction.

⭐ **The transferable rule, in hq_S's words:** *a comment that describes a save AND a restore is TWO claims, and
the save half being true is not evidence for the restore half.* For any state you are told is restored, **find
the store**; if the only thing you can find is the function said to do it, open that function. This is the same
family as this org's standing rule about a correct procedure with a false explanation — here the procedure was
not even correct, and the explanation is what made it look finished.

Both near-misses on that row were found by **asking what the witness set could not see**, not by anything going
red. That is the only method that catches a silent half once the loud half is cured.
