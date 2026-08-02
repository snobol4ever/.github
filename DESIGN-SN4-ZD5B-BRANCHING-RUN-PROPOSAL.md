# DESIGN-SN4-ZD5B — Planner Extension for Branching Match Runs

**Rung:** A-7 · ZD-5b · WRITTEN PROPOSAL (NO CODE)
**Session:** s23t (2026-08-02)
**Status:** AWAITING LON RULING — O-7 consumes the ruling once granted.
**Measured at:** SCRIP `2fea8565`, corpus `b3f08a4a`.

---

## §1 WHAT THIS IS SOLVING

The current `zd_plan` run walker follows **only γ-wires**: `cur = zd_chase(cur->γ.node)`. A
run is therefore a linear chain — which is correct for the value spine (LIT→BINOP→ASSIGN) but
wrong for the pattern blob, where ALTERNATE/ARBNO/SEQUENCE store their arm entries and resumes as
**operand pairs** `(entry_i, resume_i)`, not γ-children.

The consequence is that the γ-walk hits IR_MATCH_ALTERNATE / IR_MATCH_ARBNO /
IR_MATCH_SEQUENCE as single opaque nodes, `zd_wl_kind` returns 0 (no ZD arm), and the whole
run declines. Every leaf kind reachable only through those nodes (IR_MATCH_LIT, IR_MATCH_LEN,
IR_MATCH_SPAN, IR_MATCH_ANY, IR_MATCH_NOTANY, IR_MATCH_ASSIGN_SAVE, …) is unreachable by the
current walk.

**MEASURED SCOPE (s23t, 318 programs):**
- 198 declined runs across 103 programs have a blob-interior first-blocker
  (ALTERNATE 67 · ASSIGN_SAVE 40 · LIT 29 · LEN 24 · SPAN 14 · SEQUENCE 12 · ANY 5 · etc.)
- That is 57% of the total 349 declined runs
- These are the programs ZD-5b would unlock

---

## §2 THE WIRE MODEL — WHAT WE ARE ACTUALLY PROPOSING TO PLAN

The lowerer builds three branching constructs in the pattern blob (lower_snobol4.c):

**IR_MATCH_ALTERNATE (N arms):**
operands = [(entry_0, resume_0), (entry_1, resume_1), …] — 2N total.
γ = shared success-glue (na_s) → outer γ.
ω = shared fail-glue (na_f) — exhausted alternatives → outer ω.
α: save δ+dcap, alt_i=0, enter operand[0] (entry_0.α).
β: dispatch on alt_i → resume_{alt_i}.β.
na_f: alt_i++, reload δ+dcap, enter next arm or exhaust → ω.
Each arm's inner nodes wire with succ=A, fail=A; inner σ-edges land na_s, inner φ-edges land na_f.
**The branching structure IS the operand tree, not the γ-chain.**

**IR_MATCH_ARBNO (1 body):**
operands = [entry, resume, geometry-bracket, (optional: self if FENCE-rooted)].
γ = succ (outer success). ω = fail (outer fail).
α: try to match one more instance; if body succeeds via σ-edge, loop; if φ-edge, γ.
β: resume the body generator. The body's σ/φ edges both target R.
**Shy, extend-on-retry (manual ch.9): initially matches null; tries longer on every retry.**
RL-licensed: ARBNO's cells ride its own linked iteration-frame (below the claim), not the flat
spine — it is the INDETERMINABLE class of THE WHACK CONTRACT (law 4 RBP construct). Its α
depth is NOT static unless the body is static-extent.

**IR_MATCH_SEQUENCE (element list):**
operands = [(entry_0, resume_0), (entry_1, resume_1), …] — 2N total, same 2N convention as ALT.
γ = shared success-glue → outer γ. ω = shared fail-glue → outer ω.
Each element threaded in sequence: element_i.γ = element_{i+1}.α; element_i.ω = seq.β (backtrack into
element_i's own resume, then try element_{i-1}.β, etc.). No branching at the SEQ level itself.
**SEQUENCE is the linear concatenation operator; its depth model is the sum of its elements.**

**Leaf kinds (IR_MATCH_LIT, IR_MATCH_LEN, IR_MATCH_SPAN, IR_MATCH_ANY, IR_MATCH_NOTANY, …):**
γ = their success continuation (next element or arm-success). ω = their failure continuation (arm-fail
or backtrack). Each carries its own literal/charset/count in ival/sval. No operands (or 1 operand
for variable-argument forms like SPAN_VAR). **Each has a fixed K=16 cell for its match position.**

**IR_MATCH_ASSIGN_SAVE / _COND / _IMM (capture):**
SAVE: α pushes the open cursor (16B cell). β pops it. ω → capture's fail.
COND/IMM: α reads the SAVE's stack top via cross-box ZOPQ, calls rt_cap_assign_cursor.
**The SAVE+COND/IMM pair is always a pair; they CANNOT be admitted independently.**

---

## §3 THE FUNDAMENTAL CLAIM: WHAT KIND OF PLANNING IS POSSIBLE

The critical question is **depth-static vs depth-dynamic** across the branching structure.

### 3a. ALTERNATE — depth-static, plannable

Every arm of an ALTERNATE is entered at the SAME rsp depth — the depth at the ALTERNATE's α.
On each retry the na_f glue restores δ+dcap and enters the next arm, so every arm sees the
same RSP base. The leaf kinds within each arm carve their 16B, succeed γ→A-σ→outer-γ or
fail φ→na_f. On the φ path, na_f restores δ (explicitly, via the σ-stack machinery) and
enters the next arm — so the RSP at every arm entry equals the RSP at ALTERNATE.α EXACTLY.

**Consequence:** the depth model at every node inside an ALTERNATE arm is STATIC — it equals
(ALTERNATE.α depth) + (sum of K's for nodes successfully passed in that arm so far). The
planner can compute this at compile time. The claim base is at ALTERNATE.α; cells stack above
it exactly as in the linear case. γ-exits from inside an arm land at the outer-γ (success) at
full statement depth; φ-exits enter na_f which restores and starts the next arm at the same
ALTERNATE.α depth, correctly.

⚠ **CONSTRAINT — CELLS ACROSS BRANCH BOUNDARIES:** a node in arm_i CANNOT be the operand
of a node in arm_j (different arms). This holds by construction: arms are lowered independently,
and the resume dispatches on β pick up from within the same arm. The planner's existing operand
check (op must be an earlier member of the SAME run) is sufficient if the "run" includes all
arm nodes with the correct depth model.

### 3b. SEQUENCE — depth-static, plannable

SEQUENCE is the linear concatenation of its elements. Element_i.γ = element_{i+1}.α; on
backtrack, element_i.ω = seq.β which resumes the element. Depth across a SEQUENCE is the
cumulative sum of element K's — identical to the existing linear chain model. The planner
already handles chains longer than 2 elements; SEQUENCE is just a chain with an n-ary
envelope node that itself carries K=0 (no cell).

### 3c. LEAF KINDS — depth-static, directly plannable

IR_MATCH_LIT, LEN, SPAN, ANY, NOTANY, BREAK, BREAKX, POS, RPOS, TAB, RTAB, ARB, REM, BAL:
all carry K=16 (one position/match cell), all wired γ=next, ω=fail, no cross-statement
operands. **These are the dominant population (198 of 349 declined runs). They are NOT
structurally different from LIT_INTEGER, which already arms. The ONLY reason they don't arm
today is that the run walker cannot reach them through ALTERNATE/SEQUENCE.**

### 3d. CAPTURE PAIR (ASSIGN_SAVE + ASSIGN_COND/IMM) — plannable with the pair law

The SAVE+COND pair is a cross-box read: COND reads SAVE's cell at [rsp + fp(SAVE→COND)].
ZD-5b must admit them as a pair — never one without the other in the same run — and stage
op_zread[0] for COND as the distance from COND's depth-out to SAVE's depth-out. The existing
`op_zread[k]` mechanism handles this exactly as it handles binop reading two operands; the
operand[1] = SAVE convention already registers SAVE as COND's predecessor. This is the same
mechanism as ZD-7c's arg reads.

### 3e. IR_MATCH_ARBNO — NOT plannable in ZD-5b (RBP construct, below the claim)

ARBNO is THE WHACK CONTRACT's INDETERMINABLE class: its body cells ride a linked
per-iteration frame (below the claim, zls2 blocks). Its α depth is not static unless the body
is static-extent AND the body does not cycle. `sno_in_arbno` already gates the SEQ re-point
to prevent FORTH assumptions inside the body. ZD-5b does NOT propose admitting ARBNO runs.
ARBNO is OMEGA's terrain (match template + frame machinery); ALPHA may not touch it.

---

## §4 PROPOSED PLAN EXTENSION — THE THREE-SENTENCE DESIGN

The zd_plan walk extends from a **linear γ-chain** to a **γ-chain with inline subtree descent**:

1. **The run walker gains a SUBTREE-DESCENT arm.** When `zd_chase(cur->γ)` lands on a
   non-admitted node (ALTERNATE, SEQUENCE, or a leaf kind), instead of stopping the run,
   the planner traverses the node's **operand pairs** recursively in execution order and
   enqueues each reachable member into the run[] array with a correctly computed depth model.
   The ALTERNATE node's entry-i sub-runs are enqueued as siblings at the ALTERNATE's depth;
   leaf kinds are enqueued in the order the run visits them.

2. **Each ALTERNATE arm is planned as an independent sub-run at the ALTERNATE.α depth.**
   The depth model resets to ALTERNATE's zout at the start of each arm. Cells within each
   arm are INDEPENDENT — a cell in arm_0 and a cell in arm_1 are at the SAME offsets, which
   is correct because only one arm executes per attempt. The γ-release is staged on the last
   node of each arm whose γ exits the run (γ→outer success), and the φ-release is staged on
   every node whose ω exits the run (ω→outer fail or na_f). The ALTERNATE node itself carries
   K=0 (it is the router; its dispatch table already lives in its ζ-quad).

3. **Leaf kinds gain their ZD arms in their templates** (one per kind, the normal
   zd_wl_kind → template-arm unit of work). The depth at a leaf is its position in the
   execution-order traversal of the run. op_zread for CAPTURE pairs uses the existing
   `predecessor-in-run distance` staging — the SAVE→COND distance is the cell-stack depth
   between their run positions.

**PLANNER CHANGE IS IN `zd_plan` ONLY (ALPHA-owned).** The wl_kind additions are one line per
leaf kind in `zd_wl_kind`. The template arms are in OMEGA-owned `bb_match_*.cpp` files — those
go to OMEGA as a CROSS-FRONT REQUEST per the concurrency contract §2.

---

## §5 CORRECTNESS ARGUMENT — WHY THE DEPTH MODEL IS VALID

**ALTERNATE:** every arm enters at the same depth (the ALTERNATE.α depth). na_f restores δ
before entering the next arm. The planner sees N arms as N sub-runs at the same base depth.
Each arm's cells are independent (non-overlapping execution paths). The cell claimed by arm_0
at offset D is released before arm_1 is tried (na_f restores δ back to base); there is no
aliasing. The planner's ALL-OR-NOTHING gate (comment at line 1967: "any future partial arming
must carry a consumer-side check, i.e. arm a CONVEX region closed under both operand and
consumer edges") is SATISFIED: within each arm, all operands and consumers are in the same arm's
sub-run; the ALTERNATE node and its outer context are outside, and those edges are γ/ω
transitions that trigger releases.

**SEQUENCE:** linear concatenation — same depth reasoning as the existing chain model.

**CAPTURE PAIR:** SAVE's cell is staged at some depth D_S; COND reads it at depth D_C > D_S
(COND executes after SAVE succeeds). op_zread[0] for COND = D_C − D_S, the existing formula.
The pair is admitted together — COND is admitted IFF SAVE is earlier in the same run.

**CLAIM-AT-HEAD (unchanged):** MATCH_BEGIN owns the claim, staged at the head's α. Blob cells
(the PATCTX quads, marks, ASSIGN_SAVE cells) remain in the claim as today. Value-spine cells
(the leaf K=16 match-position cells) go BELOW the claim. The hybrid staging already handles
this (zd_plan's armed arm: "armed members' cells ride BELOW it"). ZD-5b adds no new claim
authority — it only adds more armed members below the existing claim.

---

## §6 SCOPE BOUNDARY — WHAT IS NOT IN THIS PROPOSAL

- **IR_MATCH_ARBNO** — excluded. Its body depth is not static (per-iteration frames). RBP
  construct per law 4. OMEGA terrain.
- **IR_MATCH_FENCE1** — excluded. zdyn-veto, OMEGA-owned. Already declined by the dynamic-box
  veto and pending ZW-6 relocation.
- **IR_MATCH_DEFER / IR_MATCH_PATREF** — excluded. zdyn-veto class; pat_static=1 variants
  already admitted by the existing zdyn logic (s23i). No new planner logic needed for these;
  the template arms are OMEGA's.
- **IR_MATCH_BEGIN / IR_MATCH_END / IR_MATCH_REPLACE** — already admitted (ZD-5 MATCH-SPINE).
  Not changed by ZD-5b.
- **Recursive patterns** — a pattern that references itself (`*LIST` etc.) creates a graph
  cycle through IR_MATCH_DEFER. The zdyn veto already handles this. ZD-5b does not propose
  cycling the run walker through back-edges.

---

## §7 IMPLEMENTATION SEQUENCE (for OMEGA to consume post-ruling)

1. **[ALPHA] zd_plan walk extension** — add subtree descent for ALTERNATE/SEQUENCE operand
   pairs. Gate behind `SCRIP_ZD_5B=0` (default ON after ruling). One new helper
   `zd_plan_subtree(...)` called from within the main run loop.

2. **[ALPHA] zd_wl_kind additions** — one line per leaf kind, in kind-level order:
   IR_MATCH_LIT, IR_MATCH_ANY, IR_MATCH_NOTANY, IR_MATCH_SPAN, IR_MATCH_LEN, IR_MATCH_POS,
   IR_MATCH_RPOS, IR_MATCH_TAB, IR_MATCH_RTAB, IR_MATCH_ARB, IR_MATCH_REM, IR_MATCH_BAL,
   IR_MATCH_SEQUENCE, IR_MATCH_ALTERNATE, IR_MATCH_ASSIGN_SAVE. One rung per kind, with a
   byte-identity sweep on the untouched population per addition.

3. **[OMEGA → CROSS-FRONT REQUEST] template ZD arms** — one ZD arm per leaf template in
   `src/templates/bb_match_*.cpp`. These are OMEGA files; ALPHA files the cross-front request.
   OMEGA works through them kind by kind per their normal rung discipline.

4. **[BOTH] gates** — full §3 crosscheck BY SET both modes + bench board + regen ×4 after
   each rung. Monitor on any diverge.

---

## §8 THE RULING REQUEST

**Three questions for Lon:**

1. **Is the ALTERNATE depth model correct as stated?** (§3a: every arm enters at the same
   depth = ALTERNATE.α depth, cells are arm-local, φ restores before the next arm.) Or is
   there a runtime case where na_f does NOT restore δ before entering the next arm, making the
   depth model wrong?

2. **Pair law for CAPTURE:** SAVE+COND/IMM admitted only as a pair, op_zread[0] = D_C−D_S
   distance. Or does the capture cross-box read require a different mechanism?

3. **ARBNO: confirm out of scope for ZD-5b.** ARBNO body depth is non-static; it belongs to
   the INDETERMINABLE class and to OMEGA's frame/RBP machinery. ZD-5b does not touch ARBNO.
   Correct?

---

*Delivered s23t (2026-08-02). Population measured at HEAD `2fea8565`. Rung A-7 DELIVERED.*
