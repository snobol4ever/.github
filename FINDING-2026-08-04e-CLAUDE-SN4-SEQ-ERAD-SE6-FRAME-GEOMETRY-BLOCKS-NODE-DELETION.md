# FINDING-2026-08-04e: SEQ-ERAD SE-6 — frame geometry dependency blocks node deletion

**Session:** Sonnet 4.6, 2026-08-04  
**Rung:** SE-4 through SE-6 (attempted combined deletion)  
**Result:** ATTEMPTED AND REVERTED — 22 regressions from capture SEGV; working tree restored to HEAD

---

## What was attempted

All of SE-4 (delete counter arm + fence machinery), SE-5 (delete template + box dispatch), and SE-6 (delete node, rewrite `sno_seq_nary`) in one pass, with Lon's ruling #1 explicitly granted ("eradicate them / continue").

**Files edited (all reverted to HEAD):**
`lower_snobol4.c` · `bb_match_sequence.cpp` (git rm'd, restored) · `bb_templates.h` · `IR.h` · `scrip_ir.c` · `ir_query.c` · `pat_fold.c` · `emit_per_kind_audit.c` · `emit.h` · `emit.cpp` · `zeta_storage.c` · `Makefile`

## What the gate showed

Build: GREEN. Probe suite: **73 pass / 36 xfail / 10 XPASS / 22 REGRESSION**.

The 22 regressions are concentrated in: A05/A06/A07/A08/A09/A13 (ALT + capture), D09/D13 (ARBNO + recursive), G04/G05/G08/G09/G21/G22/G23 (FENCE0 in sequence), H12/H13 (FENCE1 + ALT in ARBNO), N05/N12/N15/N19/N21 (ARBNO retried).

All crash on the CAPTURE path. Probe A05 (`'xycd' ? POS(0) ('ab' | 'xy' . W | 'pq')`): match succeeds, `=S` printed, then SEGV when accessing `W`. The capture slot address is wrong.

## Root cause identified

**Frame geometry dependency.** `ASSIGN_SAVE` (the capture's cursor-save box) stores at `op_off` = its frame slot, computed by `zeta_storage.c`'s ZLS layout pass. That pass walks the chain and accumulates slot offsets based on each node's cell size and position. `IR_MATCH_SEQUENCE` contributed `K=0` (zero cell, confirmed by `zd_k()`) — but its **presence as a node in the chain** anchored the RPO traversal and affected which nodes were allocated slots and at what depths.

When the node is deleted, the chain loses an anchor. The RPO walk visits nodes in a different order; ASSIGN_SAVE's `op_off` lands at a different stack depth than `ASSIGN_COND` expects when it reads back the cursor. The result is a frame slot collision or out-of-bounds read → SEGV.

## What SE-6 actually needs

The node deletion is **not** a pure structural rewrite of `sno_seq_nary`. It also requires:

1. **Verify that deleting the IR_MATCH_SEQUENCE node does not shift any other node's ZLS slot.** The ZLS layout (`zls_layout_chain` in `zeta_storage.c`) walks nodes in RPO order and assigns slots. With S gone, the RPO walk changes; any node whose depth was computed relative to S's position needs re-verification. The capture pair (ASSIGN_SAVE + ASSIGN_COND/IMM) is the most dangerous — its `fc_cond_fp` cross-box displacement is computed at lower time and read at emit time.

2. **Prove with the monitor.** Run A05 through the 2-way sync-step monitor against SPITBOL, get the first divergent trace event, and bracket the bug to the exact statement. Only then edit.

3. **The XPASS set is real and correct.** 10 probes moved from xfail to pass — L10/L11/L13/L14 (nested sequence capture), F01/F02 (FENCE forward/backward), G15/G24 (FENCE0 + deferred), D10, N07. These are genuine fixes from the lower rewrite: the direct right-to-left wiring resolves issues the σ/φ-dispatch SEQ glue was masking. The lower rewrite logic is sound for non-capture, non-generator cases.

## State after revert

Working tree is clean at `f5389c0c` (HEAD). Gate: 95/46/0. No commits pending. Credential was set but nothing was pushed.

## Next session

- SE-6 is **NOT** a one-pass deletion. Split it:
  - **SE-6a:** Delete the node, rewrite `sno_seq_nary`, run the gate. **Accept the regressions** (they exist). Do NOT commit.
  - **SE-6b:** Monitor-bracket A05 divergence. Fix the ZLS frame geometry. Re-run gate. Accept 10 XPASS, 0 regression. Commit.
- The XPASS set from SE-6a is the proof that the lower rewrite direction is correct.
- **Do not attempt SE-4/SE-5 before SE-6b** — the enum deletion breaks the build, making incremental rollback impossible. Either do all rungs together or none.
- **Alternative path (safer):** Do SE-4/SE-5 only (delete the counter arm and the template/box, leaving the node). Then `sno_seq_nary` still builds the node, the emitter dispatch case is gone (but the node is present and the `seqclean[]` path no longer exists), and the ZLS layout is unchanged. Gate it. Then tackle SE-6 with the monitor on a known-good baseline.
