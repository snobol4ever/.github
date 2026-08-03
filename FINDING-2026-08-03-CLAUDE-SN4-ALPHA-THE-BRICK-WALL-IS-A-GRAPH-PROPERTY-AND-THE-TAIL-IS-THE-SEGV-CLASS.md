# FINDING 2026-08-03 · SN4 ALPHA — THE BRICK WALL IS A GRAPH PROPERTY, NOT A CONSTRUCT LIST; AND ITS TAIL IS THE rc=139 CLASS

**Seat:** ALPHA. **Parent:** SCRIP `c0c77585`. **Landed:** SCRIP `d2146360` (census, default OFF).
**Directive (Lon, 2026-08-03c):** *"Continue this for every box and every construct until you hit a BRICK WALL and realize, oh I need a register RBP stable base pointer for what I'm doing... Several constructs we know we'll want RBP for are STATEMENT, FUNCTION and ARBNO and FENCE1."* + *"All your choices."*

---

## 1. THE CLAIM

The brick wall is **not a construct**. It is a **graph property**.

Sliding RSP offsets are well-defined exactly when every box has ONE static entry depth. The wall is a **JOIN whose predecessors arrive at DIFFERENT accumulated depths** — because no `[rsp+k]` spelling can name the same cell down both edges. RBP is needed there and only there.

Consequence: the standing four-construct list (STATEMENT / FUNCTION / ARBNO / FENCE1, s21x-c law 4) should be the **OUTPUT** of a test, not its input. If the measured set is wider, the list was never the rule — it was a sample of the rule.

## 2. THE INSTRUMENT — `SCRIP_ZD_DEPTH=1`

Read-only census in `emit.cpp`, called immediately after `zd_plan`. Zero `g_emit` writes, zero emission, zero `zd_*` mutation. Default OFF ⇒ **318/318 `.s` byte-identical**.

**Arrival-depth model, taken verbatim from the UNWIND four-clause law (HQ 2026-08-03b)** so the census cannot drift from the emission it audits:

| edge | arrives at | law |
|---|---|---|
| γ | `zout[i]` | clause 1 — roll up forward, cell SUSPENDED |
| ω | `zout[i] − K` | clause 2 — box N's ω frees N's OWN K only |

Two edges into one target at unequal depth = **WALL**.

⛔ **DECLINED nodes (`zon=0`) are SKIPPED, not assumed depth 0.** Their depth lives in the UCLAIM wholesale claim — the very regime this census exists to help retire. Counting them as 0 would manufacture disagreements that are artifacts of the claim, not of the graph.

## 3. ⛔⭐⭐⭐ MEASURED — AND MY FIRST NUMBER WAS WRONG BY 3x (self-caught, same session)

**FIRST PASS (BIASED, superseded): 1410 walls.** The arrival model omitted the STAGED WHACK. `zd_plan` computes `zgpop[i]`/`zwpop[i]` — the `add rsp, N` an edge LEAVING its run emits before jumping — so an edge that whacks does NOT arrive at `zout[i]`; it arrives at the whacked depth. `IR_STATEMENT_END`'s γ is the SOLE success release (clause 4) and deliberately resets to statement-entry depth: **it was being scored as a disagreement while working exactly as designed.** That artifact was 1098 of the 1100 γ-side disagreeing edges.

⛔ **This is the [ZD-GAP] disease reproduced in a brand-new instrument, inside one session.** A census that reports a fact without modelling the mechanism it audits will misattribute — and this one would have sent the next rung hunting a 3x-inflated wall population. Corrected by passing `zgpop`/`zwpop` in: `arrival_gamma = zout[i] - zgpop[i]`, `arrival_omega = zout[i] - K - zwpop[i]`.

**CORRECTED — 318 crosscheck programs:**

```
joins 12510 · walls 469   (was 1410 -- 941 were the whack working correctly, 67% phantom)
```

⭐ **96.3% of all joins already agree on depth — they are RSP-flat-safe TODAY.** Lon's "99.999%" is far closer to right than the biased pass suggested.

| kind | walls | share |
|---|---|---|
| `IR_STATEMENT_BEGIN` | 259 | 55.2% |
| `IR_MATCH_BEGIN` | 86 | 18.3% |
| `IR_SAVE_RESTORE` | 58 | 12.4% |
| `IR_MATCH_ASSIGN_SAVE` | 31 | 6.6% |
| tail (7 kinds) | 35 | 7.5% |

**Top four = 92.5%**, mapping onto STATEMENT / the match head (ARBNO+FENCE1 live there) / FUNCTION / capture. `IR_LIT_INTEGER` dropped OUT of the wall set entirely under the correction. On roman: all walls are STATEMENT_BEGIN or SAVE_RESTORE; zero on the value spine.

## 4. ⭐⭐⭐ THE TAIL IS NOT NOISE — IT IS THE SEGFAULT CLASS

39 walls across **14 programs** fall OUTSIDE the four-construct list, in three structurally distinct classes:

- **(a) LABEL-JOIN, `first_depth=0`, preds 5–16** — `IR_LIT_STRING` / `IR_GOTO_DEFERRED`. Programs: `expr_eval`, `test_stack`, `213_indirect_name`, `216_indirect_goto_computed`, `140`/`141_pat_eval_double_fn_*`, `1013_func_nreturn`. These are EVAL/CODE/indirect-goto programs where many `:(LABEL)` edges converge on one landing box and **at least one arrives mid-statement** — a third statement exit, which clause 4 says must not exist.
- **(b) MATCHER BACKTRACK, `first_depth=128/160`, preds=2** — `BREAK`/`TAB`/`SPAN`/`RTAB` in `153_pat_operand_edge_matrix`, `154_pat_construction_time_hoist`, `test_string`. A forward γ and a retry β arriving at different depths.
- **(c) CALL/LIT** — `082_keyword_stcount`, `IR_CALL` preds=2 @16, `IR_LIT_INTEGER` preds=4 @32.

**THE CORRELATION:**

| population | rc=139 |
|---|---|
| 14 tail-wall programs | **9/14 = 64%** |
| other 304 programs | 42/304 = 14% |

**4.6× enrichment.** `test_stack` is the signature shape: verdict PASS, rc=139 — prints correct output, then segfaults. That is exactly the disease HQ named in the U-1a cursor ("value-spine fail-path programs print correct output then rc=139 at HEAD").

⛔ This makes the census an **instrument, not just a design note**: a depth disagreement outside the four constructs is a *predictor* of the segfault class. Class (a) in particular is the one the four-name list does not cover at all, and SNOBOL4 is built on label gotos.


## 4b. ⭐⭐⭐ THE WALLS ARE NOT AN RBP REQUISITION — THEY ARE THE UNWIND GAP

**A-10 AS I FIRST PROPOSED IT IS FALSIFIED.** I hypothesised the tail was `:(L)` gotos leaving mid-statement. Attribution says otherwise. `216_indirect_goto_computed`, verbatim:

```
[ZD-DEPTH] WALL main IR_GOTO_DEFERRED preds=5 first_depth=0
[ZD-DEPTH]   pred ω IR_LIT_STRING   depth=0
[ZD-DEPTH]   pred ω IR_VAR          depth=16   <-- DISAGREES
[ZD-DEPTH]   pred ω IR_BINOP        depth=32   <-- DISAGREES
[ZD-DEPTH]   pred γ IR_ASSIGN       depth=48   <-- DISAGREES
[ZD-DEPTH]   pred ω IR_ASSIGN       depth=48   <-- DISAGREES
```

Not one goto. A **value-spine ω fan-in at ascending depths 0/16/32/48** — every box failing DIRECTLY to the statement terminus carrying its own accumulated depth. That is clause 2's named defect verbatim: *"NO fail site ever computes accumulated depth."*

**CORPUS-WIDE: 1152 of 1342 disagreeing edges (86%) are ω.** γ-side residual is 190. Disagreeing ω predecessors are exactly the kinds HQ's U-1a cursor measured as having NO emitted β: `IR_ASSIGN` 941, `IR_CALL` 431, `IR_LIT_INTEGER` 359, `IR_BINOP` 308, `IR_LIT_STRING` 229, `IR_VAR` 221, `IR_COERCE_NUMERIC` 138.

⭐ **CONCLUSION: 86% of the remaining depth disagreement is DELETED BY CONSTRUCTION when U-1b lands.** Under clause 2 each box's ω frees own K and jumps to pred's β, so a terminus receives ONE edge at ONE depth. **The walls are not evidence that RBP is needed; they are evidence that the unwind is not yet wired.** U-1b is therefore not merely the rc=139 fix — it is the precondition that makes sliding RSP offsets legal at all, which is exactly the architecture Lon is asking for.

**REVISED SEQUENCING:** do NOT open a label-join rung. Land U-1b, then re-run this census. Predicted residual: the γ-side 190 plus the match-family, collapsing toward Lon's four constructs. **The census is the acceptance test for U-1b** — walls should fall from 469 toward ~200, and the value-spine kinds should vanish from the disagreeing-pred list entirely.

## 5. WHAT THIS SAYS ABOUT SEQUENCING

**SUPERSEDED BY §4b — kept as the record of a falsified hypothesis.** I proposed the tail was gotos failing to whack. Attribution falsified it within the session: the disagreement is the value-spine ω fan-in, not the goto. Read §4b for the standing conclusion.

## 6. ELIDE — THE KILLSWITCH ALREADY EXISTS AND IS NOT THE BLOCKER

Lon: *"You might want to remove temporarily the ELIDE OPTIMIZATION which eliminates RESULTS that are unreferenced."*

`SCRIP_SLOT_ELIDE=0` already exists (`zeta_storage.c:494`) and is **LIVE**: roman 2713 → 2847 lines (+4.9%). Second elide `SCRIP_BETA_ELIDE_OFF=1` (BP-9 dead-β) also exists.

⭐ **MEASURED: the wall set is INVARIANT under elide-off** (roman: 10 walls either way). The elide is orthogonal to depth disagreement and is **not** what is blocking the accumulated-offset traversal. Recorded so the next session does not spend the rung. This corroborates `zeta_storage.c:494`'s own s21x-r note that the "hole-free accumulated-offset traversal" rationale for forcing elide-off "is NOT load-bearing at HEAD."

## 7. `proc_LBL__ROMAN_α` — THE HOLD-UP, MEASURED

Lon: *"In roman.s, get rid of `proc_LBL__ROMAN_α` already. What is the hold up?"*

The hold-up is on record and was **awaiting exactly this ruling**. s26 HQ cursor, residue (a): the `_α_body` alias line was left standing because suppressing it for `is_lbl` means conditionally skipping a define while the jmp-entry `res` machinery sits between α and α_body in the binary medium — judged a media-divergence risk "not worth 1 cosmetic line without a ruling." The `.globl` suppression already landed (s26, `scrip.c:887`/`:1348`).

**RE-MEASURED AT HEAD (this session) — residue (b) is the real target and is still live:**

```
roman.s = 2713 lines.  LBL section (lines 4–899) = 896 lines = 33% of the file.
LBL chain emits 69 boxes; main emits 189; the LBL 69 ARE main's last 69, re-emitted with fresh uids.
```

**The whole LBL section is a duplicate.** Its only real job is to provide an entry point at label ROMAN — i.e. it should be the 2-line trampoline s26 proposed, or nothing at all.

⛔ **NOT ATTEMPTED THIS SESSION, DELIBERATELY.** The fix needs main's landing-node label name at LBL-emission time, but `uid` = emission-order counter and LBL is emitted FIRST. The cheap correct version is *emit main first, then LBL sections as trampolines* — which reorders every `.s` artifact in the tree and touches the jmp-entry `res` machinery. That is a 33%-of-file restructure; starting it with a third of the session's context left and a 93-second gate cycle is how a broken commit happens. **Recipe is above; it wants a fresh session and it is HQ/OMEGA-adjacent terrain (`scrip.c` proc loops + `emit_chain`), not the ALPHA admission cluster.**

## 8. GATE

- `.s` **318/318 byte-identical** (default OFF).
- m3 **BY SET IDENTICAL modulo `127_pat_json_keyvalue`** (281→282 PASS).
  ⛔ **That flip is the NAMED s23i env-pad flake, not a fix.** ALPHA cursor s23q item 6: 127's `.s` is byte-identical gate-on/gate-off and *anything* shifting initial rsp flips it. Adding a function changed the compiler binary's layout. **Fourth witness to that flake. No credit claimed.**
- Census cost: full 318-program sweep = **2 seconds**.

## 9. CHEAP GATES DISCOVERED (worth reusing)

`--compile` md5 over all 318 = **4s**; m3 verdict sweep = **93s**. So `.s` byte-identity is essentially free and should be run on *every* edit, not just at handoff.
