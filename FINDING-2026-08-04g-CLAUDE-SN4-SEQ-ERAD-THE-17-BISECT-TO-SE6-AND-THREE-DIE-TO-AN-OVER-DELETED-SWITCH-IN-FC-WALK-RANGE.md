# FINDING 2026-08-04g — the 17 regressions bisect to SE-6 alone, and 3 of them die to an over-deleted `switch` in `fc_walk_range`

Session: Opus, HQ seat, GOAL-SNOBOL4-BB (SEQ-ERAD / LADDER W). Task as given: *"Attempt to fix the regressions and see if the removal caused them."*
Start state: SCRIP `0f1185e9`, gate **78 pass / 31 xfail / 15 XPASS / 17 REGRESSION** — NOT GREEN.
End state: gate **81 / 34 / 12 / 14**. SCRIP diff = 5 lines in `src/lower/lower_snobol4.c` + 1 line in `scripts/test_monitor_3way_sync_step_auto.sh`. **Gate still RED. Nothing pushed.**

---

## ⭐ HEADLINE 1 — YES, THE REMOVAL CAUSED THEM. BISECTED, NOT INFERRED.

Same corpus, same `XFAIL.run` baseline, compiler the only variable. Each row is a real build + real gate run:

| Commit | Rung | Gate |
|---|---|---|
| `f5389c0c` | pre-ladder baseline | **95 / 46 / 0 / 0** ✅ |
| `3baa8a5d` | SE-5 (immediate parent of the deletion) | **95 / 46 / 0 / 0** ✅ |
| `a1caa5b6` | **SE-6 — the node deletion** | 78 / 31 / 15 / **17** ❌ |

SE-0…SE-5 are clean. **The entire regression set enters at the single deletion commit.** No part of it is pre-existing, and no part of it comes from the MON-RE commit on top.

⚠ METHOD NOTE: the goal file's STANDING FACTS table (`IR_MATCH_SEQUENCE` = 46 refs at `f5389c0c`) is STALE at HEAD — the live census is 11 textual refs, **0 live** (all 11 are inside comments; proved by stripping C comments and string literals programmatically, then re-grepping). CENSUS SHELF LIFE did its job; the table should be re-stamped or deleted.

---

## ⭐ HEADLINE 2 — `fc_walk_range` LOST TEN CASE LABELS, A `break`, AND THE `lit_ok` ARM

`a1caa5b6` was supposed to remove ONE case label from `fc_walk_range` (`lower_snobol4.c`). It removed the entire case body. What it left:

```c
switch (x->op) {
case IR_MATCH_LIT: case IR_MATCH_LEN: case IR_MATCH_ANY: case IR_MATCH_NOTANY:   /* comment */
default: lin = 0;
}
```

Four case labels with **no body and no `break`**, falling straight through into `default: lin = 0`. The switch is unconditionally `lin = 0` — **the function is dead**, returning 0 for every node that reaches it.

The original:

```c
case IR_MATCH_SEQUENCE: case IR_MATCH_LIT: case IR_MATCH_LEN: case IR_MATCH_ANY: case IR_MATCH_NOTANY:
case IR_MATCH_POS: case IR_MATCH_RPOS: case IR_MATCH_ATP:
case IR_MATCH_ASSIGN_SAVE: case IR_MATCH_ASSIGN_COND: case IR_MATCH_ASSIGN_IMM:
case IR_GOTO: break;
case IR_LIT_INTEGER: case IR_LIT_STRING: case IR_LIT_REAL: if (!lit_ok) lin = 0; break;
default: lin = 0;
```

**THE TELL THAT MAKES THIS CHEAP TO CATCH NEXT TIME:** `fc_tail_walk`, the twin function in the very next hunk of the same commit, carries a near-identical switch and was edited CORRECTLY — only `IR_MATCH_SEQUENCE` dropped, `break` intact, every other label kept. The two functions disagreeing IS the defect signature. When a mechanical eradication touches a family of parallel switches, **diff the sibling hunks against each other**, not just against intent.

FIX (landed, working tree): restore the original minus only `IR_MATCH_SEQUENCE`.

RESULT: **78 → 81 pass · 17 → 14 regressions · ZERO newly broken.** Cleared: **L16, N03, N04.**

⭐ **N03 IS THE EXPENSIVE PART OF THIS.** N03 is the exact probe the previous session (`FINDING-2026-08-04f`) spent its entire budget on, producing FIVE falsified hypotheses about the φ-fixup in `sno_seq_nary`, the resume-surface polarity of `res[i]`, and ARBNO's operand triple. **None of those were the bug.** The cause was a mechanical over-deletion two functions away, in code the session never suspected because the session was hunting a *design* error and this was a *typo-class* error. LESSON, and it is the one RULES.md's MONITOR-FIRST rule exists to prevent: **before theorizing about a deletion's semantics, diff the deletion for over-reach.** A `git show` of the commit under suspicion is cheaper than any hypothesis.

---

## ⭐ HEADLINE 3 — THE REMAINING 14 CLUSTER CLEANLY, AND THE NODE-VS-BOX QUESTION IS STILL OPEN

`A05 A06 G04 G05 G08 G09 G21 G22 G23 H24 H25 X02 X06 X11` — all SIGSEGV (rc=139).

| Cluster | Count | Probes |
|---|---|---|
| **FENCE0** | 7 | G04 G05 G08 G09 G21 G22 G23 |
| **nested ARBNO** | 5 | H24 H25 X02 X06 X11 |
| **ALT3 + capture** | 2 | A05 A06 |

Every one is a NESTING case. Two hard facts measured on G05 (`POS(0) LEN(2) FENCE LEN(2) RPOS(0)`):

1. **The program prints its CORRECT output `=S`, THEN crashes.** Crash PC = `0x0000000200000002` — a descriptor-shaped value, not a code address; `ret` into garbage; gdb reports the stack corrupt. This is an RSP imbalance at statement exit, not a wrong-answer defect. Same "correct output THEN CRASH" signature already on record at W-1c.0.
2. **The box inventory delta between the green parent and HEAD is EXACTLY the two `match_sequence_α` boxes.** Nothing else in the emitted asm inventory changed. FENCE emission (`mov rsp, rbp`) is byte-identical between the two builds.

This is direct evidence bearing on the question the ladder itself flagged as untested:

> *"NOT proved, and SE-6 is where it gets tested: every proof so far was about the **box**. The **node** does separate structural work in LOWER (port-identity anchor + 2N operand container). Nothing on record has tested its removal."*

The box was proved pure wiring (twice, byte-identical). **The node's removal demonstrably changes stack accounting on nesting constructs.** Whether that is (a) the node genuinely load-bearing as a claim anchor, or (b) a second over-deletion elsewhere in `a1caa5b6` of the same class as HEADLINE 2, is **NOT ESTABLISHED** and is the next rung.

---

## ⛔ TWO OF MY OWN HYPOTHESES, BOTH FALSIFIED BY MEASUREMENT — DO NOT RETRY

1. **"`res[i] = g->all[before]` picks up the INNER call's `IR_GOTO` sentinel on nested elements, so φ-edges resume into a sentinel."** Plausible from reading `sno_seq_nary` (the inner call's first allocation IS its own sentinel). **FALSE.** An env-gated instrument (`SCRIP_SEQDBG2`) printing `res_is_sentinel` per element reports **0 on the failing probes** (G05, X02) as well as on the passing control (N02). Instrument removed after measuring.

2. **"FENCE makes RSP absolute mid-run, so STATEMENT_END's compile-time ΣK desynchronizes — divergent `add rsp,N` sizes are the discriminator."** G05 looked like a perfect fit: the green build releases a uniform `add rsp,224` on both exits, HEAD releases **176 / 192 / 192 / 208** on four exits against one carve. **FALSE AS A GENERAL CAUSE.** Checked across clusters: passing control **N02 has TWO distinct large releases** (256, 288) while crashing **A05 has exactly ONE** (272) and zero absolute resets. Divergent release sizes do not separate pass from crash. The G05 asymmetry may still be real and local; it is NOT the family's root cause.

Running total for this defect family: **seven falsified hypotheses across two sessions** (five in `FINDING-2026-08-04f`, two here). That number is the argument for finishing the monitor, not for a smarter guess.

---

## ✅ MON-RE DEFECT A — FIXED (one line, as the prior finding specified)

`scripts/test_monitor_3way_sync_step_auto.sh`, `want_scr` launch block: added `SCRIP_TRACE="${SCRIP_TRACE:-99999}"`. The block set `MONITOR_BIN`/`READY_PIPE`/`GO_PIPE`/`NAMES_OUT` but never `SCRIP_TRACE`, so `comm_var` (core.c:446) returned before emitting VALUE — **even though the script's own header comment says the catch-all is activated via `SCRIP_TRACE`/`SCRIP_FTRACE` only.** Defects **B** (stno base mismatch, `snobol4.y:233`) and **C** (second LABEL carries wrong stno; emitter EXONERATED by `SCRIP_TAPDBG`) remain OPEN. **C is where the next seat starts** — unchanged from the prior finding.

---

## ADDITIONAL FALSIFICATIONS FROM CONTINUED INVESTIGATION (after the fc_walk_range fix)

Two further hypotheses were tried and falsified by measurement — DO NOT RETRY:

3. **"The second pass in `sno_seq_nary` fires on nested constructs and mis-wires their edges to `fail`/`succ`."** — Instrumented with a counter: the second pass fires **zero times** on every probe, passing and failing alike. The tagging loop converts all `ω.node==S` edges to φ/σ tags before the fixup runs; the fixup's pointer-identity check never matches. Dead code, not the bug.

4. **"The σ-edge fixup resolves to wrong targets on nested constructs."** — Instrumented each σ-resolution and decoded the op numbers. On G05 (nested two-sequence: outer `i=0,1` at lo=31..34, inner at lo=26..29), both the inner and outer resolutions are topologically correct: FENCE→LEN(2) on the inner, FENCE→statement-assignment-sink on the outer.

**CONCLUSION ON THE 14:** The 14 regressions were already present in `a1caa5b6` before the `fc_walk_range` fix — confirmed by gating `a1caa5b6` directly (81/34/12/14, identical). The fix cleared exactly L16/N03/N04 and nothing else. The 14 are a separate defect in `sno_seq_nary`'s wiring strategy for nested constructs — not yet located.

The IR_GOTO sentinel's σ/φ tags ARE read correctly by the emitter (lines 2472–2473 of emit.cpp chase IR_GOTO chains and detect tags). Lines 2490–2491 are intentional no-ops (`node_γ = node_γ`) because LOWER already wired the real target. The sentinel itself emits nothing (line 2751: `case IR_GOTO: return 0`). The bug is not in these paths.

**Running total: FOUR falsified hypotheses this session, seven across two sessions.** Finish MON-RE Defect C and use the monitor.

## STATE AT CLOSE

- Gate: **81 pass / 34 xfail / 12 XPASS / 14 REGRESSION**, rc=1. **RED. Do not use for performance measurement.**
- The 12 XPASS still need dropping from `corpus/probe/bb/XFAIL.run` — deliberately NOT done, per the standing convention that the rung which greens the gate owns that edit.
- Working tree: 2 modified files, **UNCOMMITTED, UNPUSHED** (no credential this session). Proposed split: one commit for the `fc_walk_range` restore, one for the monitor line — they are independent.
- ⛔ **THE LADDER'S OWN LAW IS STILL VIOLATED AND THIS SESSION DID NOT FIX IT:** *"Every rung ships a killswitch giving byte-identical revert… Do not half-land."* SEQ-ERAD's deletion is unconditional — `seq_static_on` is 0 refs, the only surviving `SCRIP_SEQ*` gate is the unrelated `SCRIP_SEQ_FOLD`. **There is no byte-identical revert path for SE-6.** This is the `zeta_choices.h:288` shape the LAW cites as its own standing example. Needs a Lon ruling: retrofit a killswitch, or accept the ladder as unrevertable and green it forward.
