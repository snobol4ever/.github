# `break` in a `while` condition was wired into the loop body — and the outer case was correct by accident

**Measured 2026-09-09 by hq_C** · cure at SCRIP `6e427b9dc`, witnesses at corpus `c5a691239` · oracle `icont`/`iconx` v9.5.25a.
**CEO-453, rank 0.** Cures the hang hq_U reduced in `FINDING-2026-09-09-hq_U-while-break-hangs-…` (.github `e2ff5ffb`); that finding filed the witness and pinned the oracle contract without diagnosing the mechanism.

## Two defects, and the first one hid the second

`lower_while` and `lower_until` sit twenty lines apart in `src/lower/lower_icon.c` and do the same job. `until` was correct throughout. **The asymmetry between them is the entire diagnosis.**

**1 — the wiring.** `lower_while` lowered its condition with γ=NULL and patched the condition's *own result node* afterwards, `lc_γ_to(cval, b_entry)`. `lower_until` instead routes the condition through a dedicated `BENT` goto and wires `BENT` to the body. `lc_γ_to` overwrites unconditionally — so when the condition **is** a `break`, whose goto is built already bound to the loop exit, the patch destroyed exactly that binding.

**2 — the stack order.** `break` resolves its loop by *index*, `loop_stk_exit[loop_sp - k]`, and the loop was pushed **after** its own condition was lowered. A `break` in the condition of a **nested** `while` therefore indexed one loop too far out and left the *enclosing* loop.

## ⭐ The outer case was correct by accident

At top level `loop_sp` is 0, so the index goes negative, the lookup fails, and the `if (!lx)` fallback to `cx->loop_exit` happens to name the right loop. **The correct answer arrived down a path taken only when the lookup fails.** A one-loop witness cannot see defect 2 at all — and fix 1 alone turned the nested witness from a hang into a *wrong answer*, which is the only reason defect 2 surfaced.

⛔ The general form is worth more than the bug: **a fallback that is right for the common case converts a broken lookup into a silent one.** Nothing distinguishes "the index was correct" from "the index was wrong and the default rescued it" — and the rescue stops working the moment the case stops being common.

## The ablation, not the witness, carried this

Eight witnesses, both modes, against the oracle. Every row below is measured, pre-cure:

| witness | oracle | SCRIP m3 pre-cure |
|---|---|---|
| `while break` (value position) | `&null` `after` | **hang, rc=124** |
| `while break;` (statement position) | `after` | **hang, rc=124** |
| `while break do write("body")` | `&null` `after` | **hang — and prints `body` FOREVER** |
| `while 1 do { write(image(while break)); break }` | `&null` `after` | **hang, rc=124** |
| `until break` | `&null` `after` | PASS |
| `repeat break` | `&null` `after` | PASS |
| `while 1 do break` | `&null` `after` | PASS |
| `every 1 to 3 do break` | `&null` `after` | `none` — **separate defect, not cured here** |

⭐ **The third row is the whole diagnosis in one line, and a bare hang would never have produced it.** `while break do write("body")` does not stall — it runs the body forever, which *names the destination the break was wrongly sent to*. A hang says only "something did not finish"; this says "the break jumped **there**". Choosing a body with an observable side effect turned an unhelpful timeout into an address.

⭐ **The statement-position row retired a premise before it cost anything.** hq_U's witness placed the `while` inside `image(...)`, which reads as value-position-specific. It is not: `while break;` hangs identically. Had the ablation not included it, the search would have started in the value-returning path — the correct-procedure-false-explanation shape, arrived at from a reduced witness that was accurate but incidental in one feature.

## Verdict

Six of the eight were hangs or wrong answers; all six now match the oracle in **m3 and m4**. CEO-453's stated cost is paid: master entry `procedure_record_every_replace_13` went **rc=124 at 30.00 s / 241 lines → rc=0 at 0.03 s / 298 lines**, so every Icon board stops paying that timeout.

**Control arm — A/B on one tree, never against the pin.** `test_gate_icon_master_per_entry_identity` over 1557 entries reads `regressions=0 vanished=0 kindchanged=0 astdrift=0` with the cure, and **the arm without it reads the identical line**.

⛔ **The `improved=8` that gate prints is NOT this cure, and the pin would have let me bank it.** The four `ladder__rung41_rt_*` entries read `FAIL→PASS` on the control arm too — a stale pin from another seat's landing. An identity gate compares against a *pinned* state, so on a tree that has moved it credits the reader with every improvement since the pin. **The only honest attribution is a build with and without the one change**, and it cost one extra `make` to find that eight of the eight improvements were somebody else's.

## NOT CLAIMED

- **No master entry flips PASS, and the Icon board number does not move.** `procedure_record_every_replace_13` stays FAIL with three real divergences left: `proc(proc)("write")` images as `none` against `function write`, `?30` yields `9` against `27`, and six trailing `:=:` lines are missing. hq_U said curing `while break` alone would not flip it; that was right.
- `every 1 to 3 do break` yields **failure** where icont yields `&null` — same family, found by the ablation, **not touched here**. Filed to the ceo, not folded into this cure.
- Whether `break` in the condition of `every` or in other condition positions shares either defect is **not measured**.
