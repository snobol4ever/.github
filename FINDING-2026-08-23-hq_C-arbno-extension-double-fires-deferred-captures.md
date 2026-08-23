# FINDING — an ARBNO that EXTENDS double-fires an enclosing deferred capture; this is `demo_calculator-2`'s wrong answer

**Seat:** hq_C · **Date:** 2026-08-23 s261 · **Status:** root-caused to the instruction, witness minted and oracle-refed, **NOT cured** (the fix needs a ζ slot — see § The fix).

## The defect, in one line

A deferred conditional capture — `P . *FN()` — whose captured sub-pattern contains an **ARBNO that extends after the capture's first success** fires its action **TWICE**: once at the premature shorter extent, once at the final extent.

## Witness

`corpus/probe/retry/rty_arbno_extend_double_fires_cond_capture.sno`, oracle-refed via `x64/bin/sbl -bf`.

```
F = SPAN('0123456789') . *P()
T = F ARBNO('*' F)
X = T ARBNO('+' T . *A())
C = POS(0) X RPOS(0)
'1+2*3' C
```

| | output |
|---|---|
| oracle (`sbl -bf`) | `P P P A ok` |
| scrip m3 **and** m4 | `P P A P A ok` — **one extra `A`** |

⭐ `m3 ≡ m4`, so this is not a medium split.

## Ablation — what is and is not required

| ingredients | verdict |
|---|---|
| nested ARBNO, outer **and** inner capture | ⛔ doubles |
| nested ARBNO, outer capture, **no inner capture** | ⛔ **doubles — the inner capture is NOT required** |
| inner capture, **no outer capture** | ✅ correct |
| **no inner ARBNO** at all (`T = F`) | ✅ correct |
| nested ARBNO but input has no inner instance (`1+2`) | ✅ correct |

**Minimal ingredient set: an outer deferred capture whose sub-pattern contains an ARBNO that actually extends.** Plain alternation backtracking over a deferred capture, and a bare `ARBNO(LEN(1)) . *ACT()`, are both **correct** in scrip — the deferral machinery itself is sound.

## Mechanism, read off the emitted box

`src/templates/bb_match_capture.cpp`, `IR_MATCH_CAPTURE_COND` (the deferred arm):

```
α:   mov [r12+0],rcx / [r12+8],rsi / [r12+16],rdx ; add r12,24     ← APPEND the pend entry
γ:   (succeed onward)
β:   sub r12,24                                                     ← RETRACT
ω:   (concede)
```

The retract sits **only on the β→ω concede path**. `src/lower/lower_snobol4.c` (TT_ARBNO, ~:1447) picks its retry target `ri` **inside the ARBNO body**, so an extension re-enters the body and runs the capture's α again — **without ever traversing the capture's β**. The abandoned attempt's entry is never retracted, and `rt_dcap_pump` replays it.

⛔ **`src/templates/bb_match_arbno.cpp` contains ZERO references to `r12`** — the ARBNO box does not touch the pend cursor at all. Nothing truncates it per instance. That is the hole.

## ⛔ This is NOT `rung-arbno-selfloop`, which is genuinely cured

I first named that row as the suspect (same `TT_CAPT_COND_ASGN` family) and **falsified it**: `corpus/probe/retry/rty_arbno_leftctx_cond.sno` passes at HEAD. seat11's cure is intact. This is a **sibling defect in the same family** — retry re-entering past an enclosing box — which is exactly why curing that row did not cover this shape. Naming the family is useful; assuming the row is not.

## The fix

The ARBNO box must **save the `r12` pend mark at each instance start and truncate back to it when that instance is retried**, so entries appended by an abandoned attempt die with it.

⛔ **Deliberately not attempted in this session.** It needs a per-instance storage slot, and the natural home is the **rsp iteration-frame chain (`ZC_PORT_FORTH`, GOAL-SNOBOL4-BB **ZB-ITER-1a**)** that `lower_snobol4.c:1433` already names in its own fatal message for nested ARBNO. That is a ζ-storage change under the no-new-globals rule, not a template one-liner, and rushing it risks the cured `rung-arbno-selfloop`.

⛔ **A pump-time dedupe is NOT the fix and must not be substituted:** in `calculator-2` the inner `MUL` capture fires **legitimately once per ARBNO instance**, so collapsing repeated entries by name would break correct programs.

## Why it matters

This is the whole of `demo_calculator-2`'s red on the demos board — a 1944-line diff from one defect. Minimal user-visible repro, both modes:

| expression | oracle | scrip | scrip computes |
|---|---|---|---|
| `1+2*3` | 7 | 9 | `(1+2)*3` |
| `10-2*3` | 4 | 24 | `(10-2)*3` |
| `20-3*4` | 8 | 68 | `(20-3)*4` |

⭐ It **presents** as an operator-precedence bug, and that reading is wrong in an instructive way: precedence here is structural in the SNOBOL grammar (`T` nested inside `X`), and the match structure is correct. What is wrong is that a deferred action fires early against the shared operand stack, so the arithmetic regroups. A trace of the firing order is what settled it — `PSH PSH ADD PSH MUL` against the oracle's `PSH PSH PSH MUL ADD`.
