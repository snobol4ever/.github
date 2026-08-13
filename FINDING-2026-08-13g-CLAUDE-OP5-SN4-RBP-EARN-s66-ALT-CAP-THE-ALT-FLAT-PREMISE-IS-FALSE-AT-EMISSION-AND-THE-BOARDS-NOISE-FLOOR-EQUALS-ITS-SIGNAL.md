# FINDING — s66 ALT-CAP: the ALT-FLAT premise is false at emission, and the board's noise floor equals its signal

**Seat:** Claude Opus 5, GOAL-RBP-EARN, 2026-08-13 (s66). **SCRIP commit:** `149c554e`. **Head at session start:** `dc1b721e` (s65b), tree clean, == origin.

---

## 1. THE ROOT CAUSE — TWO AUTHORITIES DISAGREEING ABOUT ONE REGISTER

s65c left the invisible-red set (A05/A06) root-caused only to the level of *"`[rsp+208]` is not backed by the live claim on the alternation arm's execution path"* and posed the next rung as a choice: **(a)** the arm-interior capture earns a frame, or **(b)** its slot resolves through the alternation's claim base. **Neither was the answer.** The defect is one level up, and it is a contradiction between two files:

| authority | says | file |
|---|---|---|
| `fc_geom` / ALT-FLAT (s202) | ALT has **no cell**; *"the box moves rsp nowhere"*; therefore arm residents are **flat** (`fc_arm_member` → deny) | `src/contracts/zeta_storage.c:745,756` |
| `bb_match_alternate` | *"NOW: alpha carves its OWN 32B record"* — emits `sub rsp,32` | `src/templates/bb_match_alternate.cpp:25,65` |

The ALTERNATE template was converted to a self-carving FORTH box. **`fc_geom` was never told.** The chain to the SIGSEGV:

1. ALT carves 32B at α (`[rsp+0]`=δ, `[rsp+8]`=success cont, `[rsp+16]`=fail cont).
2. ALT-FLAT denies the fixed cell to every arm resident — *because* of the false zero-motion premise.
3. The denied `ASSIGN_SAVE` falls to what `fc_geom`'s own next line calls **"the flat rt_cap array path"**.
4. That path spells a raw flat coordinate through `x86_frame_off`, which adds `op_zdepth` = **the box's OWN carve** = 0 here (`emit.cpp:907`: *"Zero when the box carves nothing"*).
5. The slot is therefore exactly the ALT's **32 too low**; `rt_cap_push` dereferences unclaimed stack.

**⭐ THE GRANT IS THE FIX, NOT AN OFFSET PATCH.** `SCRIP_CAP_DIAG` measures `save_active=1` in BOTH the passing and crashing shapes, with `fc_bytes=16` vs `fc_bytes=0` — so the arm-member denial was the **sole** suppressor. Granting restores the same ZD capture path (SAVE K=16 own cell) that s53 retired `cap_anchor_of` in favour of and called *"the FORTH-correct ONE system"*. The box then compensates for exactly what **it** carved and is depth-correct at any ancestor depth. Post-fix the site emits `sub rsp,16` / `mov [rsp+0],r14d` and `rt_cap_push` disappears from the program (1 → 0).

**Previously-convicted family, confirmed not re-derived:** the retired `cap_anchor_of` comment records this exact divergence and even the exact coordinate — *"proc graph wrote `[rsp+192]` read `[rsp+176]`"*. Our crashing site spells `[rsp+192]`.

## 2. THE ARITHMETIC PROOF, TAKEN BEFORE THE FIX

Four minted variants, oracle-checked (`sbl -b`), reproducing s65c's table under the sanctioned `classify_one`:

| variant | pattern | verdict |
|---|---|---|
| v1 | `('ab' \| 'xy' \| 'pq')` — 3 arms, no capture | PASS — **arity exonerated** |
| v2 | `('ab' \| 'xy' . W)` — capture INSIDE arm 2 | **SIGSEGV** |
| v3 | `('ab' \| 'xy') . W` — capture OUTSIDE | PASS |
| v4 | `('xy' . W \| 'pq')` — capture INSIDE arm 1 | **SIGSEGV** |

Hand-patching **only** the emitted offset `192` → `224` (+32 = the ALT carve, exactly) makes v2 and v4 exit 0 byte-identical to the oracle. 208 still dies; 224 and 240 pass. The `+32` is the measurement, not an inference.

## 3. ⛔ m3 EXIT 0 WAS NEVER EXONERATION — NEW FACT, s65c DID NOT HAVE IT

**m3 runs both crashing variants to completion with fully correct output** (`MATCH W=xy`, rc=0). Same bad slot, landing in mapped slack and corrupting silently rather than faulting — the s22r envp class the retired `cap_anchor_of` comment already names. **m4 is the honest medium for this defect class**; an m3-only board would have called A05/A06 green forever.

## 4. ⛔⭐⭐ THE BOARD'S NOISE FLOOR EQUALS ITS SIGNAL — MEASURED, NOT ASSERTED

Two **identical** ON runs of the 226-program board differ on **5 programs**:

`X06 PASS→TIMEOUT` · `X08 PASS→TIMEOUT` · `D05 SIG11→SIG6` · `treebank SIG11→TIMEOUT` · `claws5 SIG6→SIG11`

That is the **same magnitude** as the entire ON-vs-OFF diff (also 5). The single apparent regression in the ON-vs-OFF diff — `treebank-array PASS→SIG11` — flips **both ways on BOTH arms** across repeats, and its emitted `.s` is **byte-identical** under both arms. It was the noise floor, not the change.

**⇒ A "ZERO regressions by set" claim from a SINGLE board run on this corpus is riding a floor of ~5, and the floor flips programs green→red (X06/X08), which is the direction that manufactures false convictions.** This is a live hazard for every goal that gates on this board.

**THE NOISE-FREE REPLACEMENT GATE, used here:** compile every program twice (feature ON vs killswitch OFF) and diff the emitted `.s` md5. Compilation is deterministic, so the differing set is the **exact** blast radius, and byte-identity is a *proof* of no-regression rather than an observation of none.

## 5. THE GATE AS RUN — 800 PROGRAMS

md5 of emitted `.s`, ON vs `SCRIP_ALT_CAP=0`, over 226 BB-probe/demo + 574 benchmark/program files:

- **EXACTLY 6 of 800 differ.** 794 are byte-identical machine code.
- All 6 verdicted deterministically (3 runs, both arms): **A05 SIG11→PASS · A06 SIG11→PASS · csnobol4-suite/alt2 SIG11→PASS** · `fence_driver` SIG11 both · `parser/unary_not` DIFF both · `beauty_suite/io` ORACLE_FAIL both.
- **NET: 3 FIXED, 0 REGRESSED.** A05/A06 additionally 10/10 PASS with the grant, 10/10 SIG11 without.
- Artifact regens are provably no-ops outside these 6 — the md5 sweep *is* the regen check, run over a wider set than the regen scripts cover.

## 6. WHAT THIS SETTLES AND WHAT IT DOES NOT

**Settles:** the s65b census's "3 invisible-red" set is now 1 — A05/A06 are closed at the mechanism, leaving only `expression.sno` (COMPILE_FAIL) unattributed.

**Does NOT settle — ledger 2 is still blind.** s65c's claim that **EARN-5 is the fix for `earn_hazard_in`'s false-negative class stands untouched.** The grant repairs the *slot*; it does not teach the hazard predicate to see γ/ω-wired spans, so the ~40 D/X/H probe reds remain unpredicted by ledger 2 and EARN-5 remains the rung that would convert them. ALT-CAP is upstream of that, not a substitute.

**Open, newly visible:** `fence_driver.sno` changed asm without changing verdict — an arm-interior capture that is now correctly slotted yet still SIG11, so it carries a *second*, independent defect. It is the cheapest next witness in this family.

**Not audited:** whether other arm-resident kinds (beyond `ASSIGN_SAVE`) have latent cross-box slots. The grant was deliberately narrowed to `ASSIGN_SAVE`; widening it needs its own md5-radius run.

**Standing premise defect left in place:** ALT-FLAT's *"the box moves rsp nowhere"* comment at `zeta_storage.c:756` is still false. This session made the *consumer* honest; the comment and the ALT's own un-registered 32B carve remain a trap for the next reader of `fct_fp_range`, whose line-330 comment independently assumes `fc_geom(granted ALT)=16` — **a third opinion, matching neither the template's 32 nor fc_geom's 0.** Reconciling the three is unfinished business, not covered by this fix.
