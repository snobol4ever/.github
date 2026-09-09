# FINDING 2026-09-09 hq_U — the ARBNO casualty/survivor split is REACHABILITY, not structure, so the CEO-437 ablation has no answer to find; the recede lands on a callee frame that has moved rbp

**Trees** SCRIP `01eb996ca` corpus `f7c68a8c5` .github `2d59f6e6` (all three ff-merged to origin before measuring).
**Build** incremental `make`, `RT_OPT=-O0`. Baseline fingerprints `scrip` `52cd0c0468307184cf58a0448f45990d` · `out/libscrip_rt.so` `b2c37a9a519e1d1fc0a2ff07c9bf2363`. Both restored byte-identical after every experimental arm below; tree clean.
**Oracle arm** live-oracle (`/home/resources/x64/bin/sbl -bf`), swap stamp **20260909T033439Z** (CEO-440 clause f). Pinned-ref arm is `corpus/tests/snobol4/ALL.ref`. Both arms agree on all thirteen entries at baseline.

## THE HEADLINE — THE ABLATION CEO-437 ORDERED HAS NO ANSWER, AND THAT IS THE RESULT

CEO-437 asked for an ablation separating the 7 casualties from the 82 surviving signature carriers; CEO-439 named **FENCE over a choice point, below the source text** as the next axis. I ran the asm diff it asked for and **the axis is falsified at the strongest possible level**.

⭐ **`arbno_fence_pos_branch_20` (survivor) and `arbno_fence_pos_branch_30` (casualty) have BYTE-IDENTICAL INSTRUCTION STREAMS.** Same generated family, same `FENCE('a' | 'ab')` over the same choice point, same `ARBNO(*cmd)`, 1152 asm lines each. With comments and data stripped, the entire diff is **three string-length immediates**:

```
557c557   mov dword ptr [rsp + 4], 2      ->  3     ; subject 'aa' -> 'aab'
851c851   mov dword ptr [rsp + 4], 25     ->  32    ; OUTPUT message length
927c927   mov dword ptr [rsp + 4], 31     ->  28    ; OUTPUT message length
```

By ASM-DIFF-FIRST step 2, an instruction identical across both is exonerated — and here **every instruction is identical**. The two programs differ only in their **subject string**. No source-level or emission-level predicate can separate them, because there is nothing to separate. ⛔ **A discriminator hunt over a population whose members emit the same code cannot terminate**, and three axes have now been tried against it (FENCE-bearing → 50% vs 1.3% enrichment, not a separator; FENCE-over-a-choice-point → falsified here).

## THE ACTUAL DISCRIMINATOR, AND ITS CONTROL

**A carrier moves iff it commits ≥1 ARBNO instance AND the overall match must still FAIL** — i.e. iff it traverses the recede `jmp` the predicate suppresses. Measured by rebuilding with the arm unconditional (`IF(true, …)` in `bb_match_arbno.cpp:120`, no other change — "Arm C") and grading all thirteen `arbno_fence_pos_branch_*` entries the family contains, m3 and m4, under `setarch -R`:

| moved | expected verdict | why |
|---|---|---|
| `_3` hang rc=124, `_30` `_31` `_34` `_35` SIGSEGV rc=139, `_36` wrong answer | **match FAILS** | commits ≥1 instance, then must recede |
| `_20` `_27` `_28` `_32` `_33` unmoved | match SUCCEEDS | never recedes past exhaustion |
| `_29` unmoved | match FAILS | `*outer` is used **before** it is assigned — no ARBNO is ever built |
| `_19` unmoved | match FAILS | **the control** — see below |

The six that moved are **exactly** the six casualties named in the LIVE CURSOR (`30/31/34/35/36/3`). Nothing else moved.

⭐ **`_19` IS THE CONTROL THAT MAKES THE STATEMENT EXACT, AND IT LOOKS LIKE A COUNTER-EXAMPLE UNTIL YOU READ IT.** `ARBNO(FENCE('zz'))` against `'aa'` expects a failed match and does recede — but its body cannot match even once, so it reaches exhaust with **zero** committed instances, `r14d == AFC(0)`, and it leaves by the `je L(3)`, never by the recede `jmp`. In the suppressed build `je L(3)` and the fall-through both land on ω, so the zero-instance case is correct **whether or not the arm is emitted**. That is why "expected verdict is FAIL" is not the rule and "traverses the recede jmp" is.

## ⛔ THE REFRAME: THE PREDICATE IS NOT PROTECTING A POPULATION — IT IS MANUFACTURING ACCIDENTAL GREENS

The LIVE CURSOR recorded the previous arm as *"the predicate is PROTECTING a real population: it suppresses an arm 7 graded programs cannot survive."* **That reading is now measured wrong, and the correction matters because it inverts the cure's acceptance test.** When the arm is suppressed, what remains is `cmp r14d, eax` followed by an unconditional fall-through to ω — ARBNO **concedes at exhaustion**. For a program whose expected verdict is a *failed* match, conceding is the right final answer. So those six are green today **for the wrong reason**: the missing edge produces their expected output by accident, and they are the only six entries in the family that would ever have exercised the edge. They are not a population to protect; **they are the entire test population for the cure**, and their being green is what has hidden the defect.

## THE MECHANISM, MEASURED UNDER gdb — rbp WALKS ONE FRAME PER LAP

Witness `_34` (`cmd = FENCE('a' | 'ab')`, `outer = ARBNO(*cmd)`, subject `'ab'`), m4, Arm C, `setarch -R`. The ARBNO box's ζ cells are **rbp-relative** (`AFC(0)`/`AFC(4)`/`AFCQ(8)` = `[rbp-48]`/`[rbp-44]`/`[rbp-40]`) and the recede `jmp` targets the deferred body's β port (`n10_match_defer_β`). The whole arm is laid down correctly; it faults on its **first** instruction:

```
=> 0x401411 <n9_match_arbno_bx+83>:  mov -0x30(%rbp),%eax      ; rbp = 0x0
```

Breaking on the exhaust entry (`0x40140a`) and continuing:

```
lap rbp=0x7ffffffedfe8 rsp=0x7ffffffedfb0 r14=1
lap rbp=0x7ffffffee048 rsp=0x7ffffffedff0 r14=1
lap rbp=0x7fffffffe120 rsp=0x7ffffffee050 r14=1
lap rbp=0x7fffffffe180 rsp=0x7fffffffe128 r14=1
lap rbp=(nil)          rsp=0x7fffffffe188 r14=1   -> SIGSEGV
```

⭐ **Two facts in one trace.** (1) `rbp` climbs **outward one activation frame per lap** — the deferred body owns an activation frame (`op_arbno_body_actframe` is exactly this shape), its concede path pops that frame, and control lands back on the ARBNO host's exhaust entry with rbp pointing at the **enclosing** frame. Every subsequent `AFC(n)` read therefore reads a *different frame's* cells, and the arm's own rollback write `mov %eax,-0x2c(%rbp)` lands in a frame nobody will read. (2) `r14` **stays 1 across every lap** — the cursor never rolls back, which is the direct consequence of (1) and is why the loop makes no progress. rbp finally reaches the outermost saved value, `0`, and the read faults. The SIGSEGV and the `_3` hang are the same loop, differing only in whether it runs out of stack chain before the timeout.

This is the amended **BB FRAME-PLACEMENT CRITERION** (RULES.md, as amended 2026-09-06, CEO-380): a host that survives a suspend must be a real RBP activation frame and **promote itself** rather than assume one exists. The ARBNO host here assumes one and reads it after a callee has torn it down.

## ⛔ A NEGATIVE RESULT, RECORDED SO NOBODY RE-WALKS IT

`emit_arbno_rbp()` and `emit_arbno_rbp_unwind()` in `src/emitter/emit.cpp:2276,2281` are a **fully-written, hardcoded-off** feature that looks exactly like the designed cure: `emit_arbno_rbp()` makes `zd_k()` give ARBNO 32 bytes of ζ instead of 16, and `x86_arbno_rbp_unwind_at()` (`src/templates/x86/x86_asm.h:1772`) walks `rbp = [rbp+24]` outward to a marked frame. I set **both to 1** with the arm still unconditional (Arm E) and **nothing moved** — the same six, the same rc's.

⭐ **And the kind of negative result matters more than the result.** The emitted `_34` asm contains **zero** `arbno_rbp_unwind` notes: the four call sites are in `bb_match_begin.cpp`, `bb_match_end.cpp` and `bb_match_fence1.cpp`, and none is on this path. So the honest statement is **"the feature does not reach the ARBNO exhaust arm at all"**, not "it was tried and was insufficient" — a distinction that decides whether the next seat extends the feature or looks elsewhere.

## NOT CLAIMED

- **No cure is landed and none is attempted here.** The tree is byte-identical to the baseline it was measured on.
- I did **not** re-run the whole SNOBOL4 master. The 89-carrier population is quoted from the prior LIVE CURSOR, not re-measured; what I re-measured is the thirteen-entry family, exhaustively.
- Whether the remaining 82 carriers are all unreachable-by-input (rather than merely unreached by *their* inputs) is **not** established — the `_20`/`_30` pair proves the split is input-driven for that pair and is the reason to expect it generally, which is not the same as having measured it.
- hq_S's aisnobol/SPITCORE non-executable-page jump remains **predicted, not reproduced**.
