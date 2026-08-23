# FINDING — an ARBNO that EXTENDS double-fires an enclosing deferred capture; this is `demo_calculator-2`'s wrong answer

**Seat:** hq_C · **Date:** 2026-08-23 s261 · **Status:** ⭐ **CURED** — SCRIP `ba628703`. Root-caused, witness minted and oracle-refed, fix landed and regression-verified. See § THE CURE at the end.

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


---

## ⭐ FIX DESIGNED AND LOCALISED (added same session, after an attempt that was reverted)

The cure is a **per-instance pend mark**, and the placement is not the obvious one:

- **α** — bank `r12` into the ARBNO cell.
- **PAIR(2), after progress is recorded** — re-bank `r12`. ⛔ **This step is what makes it correct.** Rolling back to the α mark on every recede would wipe entries from instances that *legitimately completed* — `calculator-2`'s inner `MUL` fires once per ARBNO instance and must keep every one. The mark has to advance as each instance commits.
- **β, before `jmp PAIR(0)`** — restore `r12` from the cell, discarding exactly the abandoned attempt's entries.

### ⛔ Where it is blocked — measured, not assumed

`SCRIP_ARBNO_DIAG=1` on the witness reports **`ARBNO-FRAME` for both ARBNO nodes** — never `FRAMELESS`. That is not incidental: `bb_match_arbno()` selects `ARBNO-FRAME` when `op_arbno_body_defer_unsafe`, and **a deferred capture in the body is precisely what makes it defer-unsafe.** So this defect always lands on the FRAME arm, and:

| arm | cell | free quad? |
|---|---|---|
| `bb_match_arbno_frameless` | `sub rsp,16`, uses `[rsp+0]`/`[rsp+4]` only | ✅ **`[rsp+8]` is free** — but this arm can never carry the defect |
| **`bb_match_arbno_frame`** | rbp-relative `op_arbno_frame_off`, uses `AFC(0)`/`AFC(4)` | ⛔ **unproven** — the slot comes from the shared `frame_slot_scan`/`frame_slot_off` activation-frame allocator (`emit.cpp:2345`), which also serves `fence_frame_slot` and `leaf_frame_slot` by index. Whether bytes 8–15 belong to this node or its neighbour is not established. |

⭐ `AFCQ()` (`x86_asm.h:971`) already exists as the **quad** accessor for this cell, so quad-width access there is anticipated by the contract — the open question is ownership, not addressability.

⛔ **An attempt was made and REVERTED.** I patched the `frameless` arm first, and the witness did not move — because, as above, it never uses that arm. Left in, it would have cost two memory operations per iteration of every frameless ARBNO for zero correctness benefit, in exactly the code `hq_P` is optimising. Reverted rather than kept as "harmless".

**Next step for whoever takes it:** establish the unit size and neighbour of a `frame_slot_scan` grant, and either prove `AFCQ(8)` is owned by this node or take a grant for one more quad. Writing into an unproven activation-frame slot is the silent-corruption class and must not be done on inference.


---

## ⭐⭐ THE CURE — LANDED, SCRIP `ba628703`

Three instructions on the **ARBNO-FRAME** arm, and the middle one is the whole subtlety:

| port | instruction | why |
|---|---|---|
| **α** | `mov AFCQ(8), r12` | bank the pend cursor before any instance runs |
| **PAIR(2)**, after progress is recorded | `mov AFCQ(8), r12` | ⭐ **RE-BANK: this instance committed.** Its entries must SURVIVE the next retry |
| **β**, before `jmp PAIR(0)` | `mov r12, AFCQ(8)` | roll back exactly the abandoned attempt |

⛔ **Rolling back to the α mark on every recede would have been wrong** — it wipes entries from instances that legitimately completed, and `calculator-2`'s inner `MUL` fires once per ARBNO instance. The mark has to *advance as each instance commits*. That is why this is three instructions and not two.

### Slot ownership — proven, not inferred

`frame_slot_off()` (`emit.cpp:2239`) is `-(base + 16 * idx)` — **16 bytes of stride per slot index** — and `frame_slot_scan` advances `k += zdp_scratch_cell(m) ? 2 : 1`, so a node claiming a scratch cell takes two indices. The ARBNO node therefore owns its full 16-byte slot; the FRAME arm uses only bytes 0–7 (`AFC(0)`, `AFC(4)`). **`AFCQ(8)` is this node's own memory**, and `AFCQ` already existed as the quad accessor (`x86_asm.h:971`). **No new global, no new grant, no ζ-plan change.**

### Measured

| | before | after |
|---|---|---|
| witness `rty_arbno_extend_double_fires_cond_capture` | `P P A P A` | ✅ `P P P A` — byte-matches its oracle ref |
| `calculator-2` vs its pin (non-timing lines) | **1944** | ✅ **0** |
| `1+2*3` · `10-2*3` · `20-3*4` · `1+2*3*4` | 9 · 24 · 68 · 4 | ✅ 7 · 4 · 8 · 25 |
| corpus | m3 357/359 · m4 355/359+2SKIP | **unchanged, identical fail set** |
| `test_gate_emit_no_lang` · `test_gate_template_medium_invisible` | | ✅ PASS |
| seat11's `rty_arbno_leftctx_cond` | passing | ✅ **still passing** — sibling defect, not a re-opening of that row |

`.s` artifacts regenerated across benchmark / feature / demo / programs / crosscheck trees.
