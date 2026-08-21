# FINDING — s188 (seat1, Opus 5; queue row `fuzz-abort-batch`, rank 2)

## THE TWO FUZZ SIGABRTs ARE ONE MECHANISM, THE BOMB IS TELLING THE TRUTH, AND THE DEFECT IS `cap_in_repeat_body`'s FENCE1 ARM MISSING THE INNER MEMBER OF A STACKED CAPTURE PAIR

**Watermark:** SCRIP `2cf31532` **after `make pristine`** (the tree binary was **11 commits stale** on `src/` — HQ-27, and seat5's s186 lesson that a stale build is indistinguishable from a current one by inspecting its output). RT_OPT `-O0`. corpus `7aa87e81` + 3 new probe witnesses. **No compiler source touched — classification row, no fix attempted.** RULES step-4 `.s` regen NOT APPLICABLE.
**GATE RECEIPT (corpus board, pristine binary at this HEAD): m3 332/5 · m4 325/11 · SKIP 1 (337)** — the standing watermark to the digit, fail-set unchanged. The three new witnesses live in `probe/fuzz/`, which the board never enumerates, so a no-op there is the correct result.

## 1. THE ROW'S OWN PREDICTION WAS RIGHT — THE ABORT NAMES ITS CAUSE

The brief said *"an abort usually names its own cause, so this may be the cheapest row on the board."* Both witnesses print the **identical** message on stderr — which the fuzzer discarded, which is the whole reason the row existed:

```
libscrip_rt: BOMB — IR_MATCH_CAPTURE_SAVE: no home -- neither a ζ-SPINE cell (op_zres) nor a
ζ-STANDING slot (frame_need_of: DEFER-hazard / ALT-arm classes); classifier and ZD plan disagree
on this node -- the legacy C rt_cap_push fallback is deliberately not rebuilt (s83)
```

Site: **`src/templates/bb_match_capture.cpp:88`**, the phase-0 final `else` arm. **ONE mechanism, two faces** — `fz_abort_05` and `fz_abort_25` are the same defect, so the batch's classification question is answered: they do not need separate rows. **m3 ≡ m4**: rc=134 in both modes with the same message, and the bomb is **baked into the emitted `.s`** (2 occurrences), so this is a COMPILE-TIME classification disagreement, not a runtime accident.

## 2. VERDICT — THE INVARIANT IS RIGHT, THE CALLER IS WRONG

The row asks for exactly this. The phase-0 decision tree in `bb_match_capture.cpp` is: activation-frame slot (`op_frame_need && op_cap_frame_off != -1`) → DEFER-unsafe-boundary bomb (`op_frame_need`, no offset) → ζ-SPINE cell (`havehome()` = `op_zres || op_cap_anchor`) → **else this bomb.** Our witnesses reach the last arm because the classifier said *no standing frame needed* AND the ZD plan granted *no spine cell*. **The bomb is an honest refusal of a genuinely homeless node** — it should stay. The defect is upstream, in `frame_need_of`.

**THE CLASSIFIER TESTIFIES DIRECTLY** (`SCRIP_EARN_DIAG=1 SCRIP_CLASS_DIAG=1`), green control vs bombing witness:

| | `ASSIGN_SAVE` | `ASSIGN_SAVE` | `ASSIGN_COND` | `ASSIGN_IMM` |
|---|---|---|---|---|
| **green** (one capture) | `need=1` NOWHACK | — | `need=1` NOWHACK | — |
| **bomb** (two stacked) | `need=1` NOWHACK | **`need=0`** | **`need=0`** | `need=1` NOWHACK |

Two `IR_MATCH_ASSIGN_SAVE` nodes exist (one per capture in the stack). The **OUTER** pair is classified correctly; the **INNER** pair gets `need=0` from both members. `frame_need_of` (emit.cpp:786) defines a SAVE's need as *"whatever my reader needs"*, so SAVE#2 simply inherits its COND's 0 — the COND is where the verdict is lost.

## 3. THE MINIMISATION — 383 BYTES OF FUZZER OUTPUT DOWN TO ONE LINE, TWO INGREDIENTS

`fz_abort_05` is `P = FENCE(((SPAN('ab')) . v0) $ v0) ARBNO(FENCE(BREAK('ab')))` matched through a defer `*P`. Ablated across four ladders (30 variants), **every one of those ingredients is inert**: the ARBNO tail, the SPAN, the BREAK, the stored pattern `P`, and the defer `*P` all drop out. The floor is:

```
          'ab' FENCE(('ab' . v0) $ v0)
```

**TWO ingredients, both necessary and together sufficient:** (a) a **one-argument FENCE1**, and (b) **two STACKED captures** on its body. Neither alone bombs. It is not about the variable (`. v0` + `$ v1` bombs identically), not about which operators (`. .`, `$ $`, `. $` all bomb), and not about order.

**⛔ A METHOD TRAP THAT WOULD HAVE MIS-CLASSIFIED TWO ROWS OF MY OWN LADDER: THE BOMB IS AN EMITTED INSTRUCTION, SO A CLEAN RUN DOES NOT MEAN A CLEAN COMPILE.** `'ab c' 'x' FENCE(('ab' . v0) $ v0)` runs rc=0 and prints `nomatch` — because the match fails at `'x'` and never reaches the bomb, which is *sitting in the binary*. Classify this family by `grep 'no home' on the emitted .s`, never by exit status. (Same shape as the vacuous-PASS class in this session's other FINDING: mutual silence is not agreement.)

## 4. ⭐⭐ THE DEFECT IS FENCE1-SPECIFIC, AND THE CONTROL PAIR PROVES IT

`cap_in_repeat_body` (`emit.cpp:721`) is the predicate that is supposed to catch exactly this — *"a capture pair whose SAVE (or the pair node itself) lies INSIDE the body span of an IR_MATCH_ARBNO … or an IR_MATCH_FENCE1 … has NO ζ-SPINE home … so it rides a ζ-STANDING slot."* It brackets the two containers **differently**: ARBNO by `operands[1]..operands[2]`, FENCE1/FENCE0 by `operands[0]..operands[1]`, then asks whether the pair's `all[]` index `ni` or its SAVE's `si` falls in `[lo..hi]`.

The **same two stacked captures** in each container:

| body | emits bomb? |
|---|---|
| `ARBNO(('ab' . v0) $ v0)` | **clean** |
| `(('ab' . v0) $ v0 \| 'zz')` — ALT arm | **clean** |
| `(('ab' . v0) $ v0)` — plain group | **clean** |
| **`FENCE(('ab' . v0) $ v0)`** | **⛔ bomb** |

**The ARBNO arm of the predicate contains a stacked pair; the FENCE1 arm does not.** Its `operands[0]..operands[1]` endpoints bracket the OUTER capture only, so the INNER pair's indices fall outside the window and the predicate returns 0 for a node that is plainly inside the fence body. Checked-in as a witness plus **two green controls** (`_ctl` = one capture; `arbno_stackcap_ctl` = the identical stack in an ARBNO body), so the next seat gets the discriminator, not just the failure. Depth is not the limit: `FENCE((('ab' . v0) $ v0) . v1)` (triple) bombs too.

⭐ **AND IT IS A SURVIVING FACE OF R-0, NOT A NEW CLASS.** The bomb's own source comment names R-0 and cites the `m1_alt_*` witnesses. **All 40 `corpus/probe/m1/` witnesses were re-run on the pristine binary and NOT ONE still reaches this bomb** — the hand-minted grid is cured and this face is not in it. That is the fuzzer earning its keep exactly as the brief argued: *a hand-written grid contains only the shapes its author thought of*.

## 5. NEXT RUNG (not attempted — this row's first deliverable is the classification)

Reconcile the FENCE1 arm of `cap_in_repeat_body` with its ARBNO arm so a stacked capture pair inside a FENCE1 body is contained. It touches `emit.cpp`, so it wants the `fz3-flip`/`span-frame-flip` treatment: killswitch, full two-arm `.s` sweep with movers named, corpus fail-set identical by name, and the RULES step-4 regens. ⛔ **Do NOT "fix" it by relaxing the bomb** — the bomb is the only thing that turned this into a 5-minute diagnosis instead of a silent wrong answer.

## 6. REPRODUCTION
```bash
cd corpus/probe/fuzz
../../../SCRIP/scrip --run fz_abort_fence1_stackcap.sno            # rc=134, message names the site
../../../SCRIP/scrip --compile -o /tmp/w.s fz_abort_fence1_stackcap.sno; grep -c 'no home' /tmp/w.s
SCRIP_EARN_DIAG=1 SCRIP_CLASS_DIAG=1 ../../../SCRIP/scrip --compile -o /dev/null fz_abort_fence1_stackcap.sno 2>&1 | grep EARN
```
