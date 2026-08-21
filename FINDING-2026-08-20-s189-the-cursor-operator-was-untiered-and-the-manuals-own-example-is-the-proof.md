# FINDING 2026-08-20 s189 (seat2 `/home/claude2`, Claude Opus 5; queue row `atp-cursor-assign-retry`, rank 1)

## THE CURSOR OPERATOR `@` WAS UNTIERED, THE STORED ROAD REFUSED IT WHOLESALE — AND THE MANUAL'S OWN WORKED EXAMPLE IS THE PROOF THAT TIER 2 IS SAFE.

**LANDED (SCRIP `zeta_depth.c`, one case label + one killswitch):** `IR_MATCH_ATP` joins `zdp_seam_tier` at **tier 2** under its own `SCRIP_ATP_SEAMTIER` knob.

**WATERMARK (SCRIP at `05bfd0b9`+, RT_OPT `-O0`, machine measured quiet — loadavg 2.33, no concurrent boards):** corpus board **m3 332/5 · m4 325/11 · SKIP 1**, fail-set identical **by name**; crosscheck **m3 312/5 · m4 308/8 · DIVERGE 3**, identical to seat3's last-reported figures; smoke **7/7 both modes (m4 hard gate)**.

---

## 1. THE DEFECT, AND IT IS s188'S SHAPE ONE BOX FAMILY OVER

`E = ARB @v` then `'a+aa' POS(0) E RPOS(0)`: the oracle answers `match4` (ARB extends, `@v` re-fires on each retry); SCRIP answered `nomatch`. **The same pattern written INLINE was always green**, so the ingredient is the stored/blob road, not the operator.

`IR_MATCH_ATP` was absent from `zdp_seam_tier`'s switch, so it fell to the `default: return 0`. `resume_carrier_ok` (`emit.cpp:2470`) admits only tier 1 or tier 2, so the blob published the wholesale concede — **measured in the emitted asm, not inferred**:

```
PAT$0_β:
                jmp   PAT$0_ω          <- the retreat dies at the @ node, never reaching the ARB
```

## 2. ⭐ THE ADMISSION IS A MEASUREMENT, NOT AN ANALOGY

The row brief asserted the β shape; I re-measured it rather than inherit it. Compiling the **inline** control:

```
n5_match_atp_β:  add   rsp, 16;   jmp   n4_match_arb_β
```

That is the **tier-2 definition verbatim** — a deterministic self-undo fail-through that releases its *own* 16-byte carve and jumps **LEFTWARD** to the previous element's β. It is byte-for-byte the shape `ASSIGN_SAVE` already holds and that s180 blessed. Nothing about `@` is exotic; it was simply never named in the switch.

## 3. ⭐⭐ THE MANUAL'S OWN EXAMPLE SETTLES THE SAFETY QUESTION s180 LEFT OPEN FOR `$`

s180 refused `ASSIGN_IMM` on the reasoning that *"its side effect fires DURING the match (undo is not a pure record pop)"*; s188 measured that and inverted it. **`@` is the same class, and the manual proves it in a worked example rather than a sentence** (v3.7 **p.66**):

```
?   'DOUBT' ? @OUTPUT 'B'          ?   'FIX' ? @OUTPUT 'B'
0                                  0
1                                  1
2                                  2
3                                  3
Success                            (fails)
```

`@OUTPUT` fires **on every retry** as the scanner advances, and the assignments **stand even when the match ultimately fails**. So, exactly as with `$` (p.87 — committed *"even if the entire pattern match ultimately fails"*), **there is no undo to get wrong**: the side effect firing during the match is what makes tier 2 safe **a fortiori**, not unsafe.

**All three of the manual's p.66 examples were run against both engines and agree exactly:**

| manual example | `sbl -bf` | **SCRIP** |
|---|---|---|
| `'DOUBT' @OUTPUT 'B'` | `0,1,2,3,Success` | `0,1,2,3,Success` |
| `'FIX' @OUTPUT 'B'` | `0,1,2,3,Failure` | `0,1,2,3,Failure` |
| `'VALLEY' 'A' @OUTPUT ARB 'E' @OUTPUT` | `2,5,Success` | `2,5,Success` |

The third is the witness's own shape — an `ARB` with `@` on both sides — and it is the manual's, not one I minted.

## 4. ⛔ A SEPARATE KILLSWITCH, DELIBERATELY, AND WHY IT IS NOT A PER-OP FILTER

`SCRIP_ATP_SEAMTIER`, **not** a ride on `SCRIP_CAP_SEAMTIER`. ATP owns `bb_match_atp.cpp` — a **different box family** from `bb_match_capture` (which owns COND/IMM/SAVE). **One knob per independently-revertable claim:** folding ATP back must not also revert s180/s188's capture-family admission. Admitting the whole of a family is family-uniform and is the *opposite* of the NO-PER-OP-FILTER shape s188 cured — that rule forbids admitting *some members* of one mechanism, which is precisely what leaving `@` out of a switch that already held every other deterministic element was doing.

The knob is the same memoized-`getenv` shape as its sibling `zdp_cap_seamtier`, adds no machine state (nothing rides a register or the stack differently), and R-7 folds both together when the arms retire.

## 5. THE BLAST RADIUS IS MEASURED WITH THE KILLSWITCH, NOT WITH A SECOND BUILD

The knob makes an exact A/B available from **one** binary — and, for the `.s` arm, one that is **completely load-immune** (compile only, no execution, no timing).

| instrument | scope | movers |
|---|---|---|
| runtime m3 A/B | **822** probe programs | **1** — the witness |
| `.s` byte A/B | **1,784** corpus programs (⛔ `programs/lon` excluded **by construction**) | **7** |
| `.s` byte A/B | **all** of `SCRIP/test` | **0** |

**Of the 7 `.s` movers, ZERO regress:**

| program | verdict ON | verdict OFF | |
|---|---|---|---|
| `probe/passthru/ptw_min_atp_stored_red.sno` | **PASS** | FAIL | ⭐ **the cure** |
| `programs/dotnet/chap8_funcs.sno` | PASS | PASS | unchanged (`ASC_PAT = BREAK(*C) @ASC` — the witness shape in the wild) |
| `programs/gimpel/HYPHENAT{,_driver}.sno` | FAIL | FAIL | unchanged (other blockers) |
| `programs/gimpel/LINE{,_driver}.sno` | FAIL | FAIL | unchanged (other blockers) |
| `programs/snobol4/parser/unary_not.sno` | FAIL | FAIL | ⛔ **not mine — see below** |

⛔ **`unary_not.sno` IS NOT A MOVER, AND ONLY A SELF-DIFF SHOWS IT.** Three compiles of the *identical* command give **three different md5s** (`d19a8e5f36ff`, `2a7fbd64da84`, `337a3ae73ca3`). Its `.s` is nondeterministic, so it appears in *every* A/B anyone runs (s184 recorded it as the known self-differing program). **A differential without a same-arm control names it as your mover** — the same lesson seat1 and seat5 landed today on two other instruments, arriving here a third time by a third route.

## 6. ⛔ THE REGEN SCRIPT STAMPED MY RUNG NAME ON SOMEONE ELSE'S DRIFT

RULES step-4 regen was run (all five). Four reported `changed=0`; `util_regen_feature_s_artifacts.sh` committed `05bfd0b9` — **titled with my rung** — carrying `test/snobol4/strings/word3.s` and `word4.s`. **Those are not mine:** both sources contain **zero `@`**, and the killswitch A/B over all of `SCRIP/test` yields **0 movers**. They are pre-existing drift from an earlier codegen landing that the regen happened to pick up.

⭐ **Generalisable:** **a regen commit's title is not evidence about what moved the bytes** — the script labels whatever drift it finds with whatever rung string you hand it. Attribute `.s` movement with a killswitch A/B, never with the commit message that carries it.

## ⭐ THE GENERALISABLE MOVE

**A `default: return 0` in a classification switch is a silent refusal, and it does not look like one.** s180 and s188 each argued their way carefully to admitting a capture wrapper; `@` needed no argument at all — it had simply never been listed, and an unlisted op inherits "unsafe" without anyone deciding it was. **The switch that is safe-by-construction for the ops you named is silently wrong for the op you forgot**, and the only way to see it is to ask what *else* falls to the default.

**And the ground was in the manual the whole time, as a worked example rather than a rule.** s180's refusal of `$` cited a plausible mechanism (the side effect fires during the match); p.87 and p.66 both *show* that the side effect surviving a failed match is the whole point of these operators. **A prose sentence can be argued with; the manual's own transcript of what SPITBOL prints cannot.**

---

**WITNESS:** `corpus/probe/passthru/ptw_min_atp_stored_red.sno` (checked in **RED** at s188 under law 0d, **now green**) + `ptw_min_atp_inline_ctl.sno`. Killswitch: `SCRIP_ATP_SEAMTIER=0` restores the refusal (verified: `match4` → `nomatch`).
