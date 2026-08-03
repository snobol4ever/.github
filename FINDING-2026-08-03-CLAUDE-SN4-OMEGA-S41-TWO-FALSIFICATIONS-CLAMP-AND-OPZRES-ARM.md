# FINDING-2026-08-03-CLAUDE-SN4-OMEGA-S41: TWO FALSIFICATIONS — UMIN CLAMP AND NAIVE OP_ZRES ARM

**Session:** s41 (2026-08-03, Sonnet 4.6) **Parent:** SCRIP `c9d84615` **SCRIP unchanged this session.**

---

## §1 O-PB-2b FALSIFICATION: umin CLAMP

**Hypothesis (cursor):** The 224B residual Kc inflation after O-PB-2a (PATREF/DEFER excluded from span) is cross-statement closure contamination. Blob-closure members from stmt1 enter stmt2's `cm[]` via PATREF operand walk and pull `umin` below stmt2's own allocation floor. A clamp `umin = max(umin, run_base)` where `run_base = min zls_node_off over K=0 run members` should eliminate the contamination.

**What was built:** Added `SCRIP_ZD_GAP_CLAMP=1` instrument to emit.cpp (the Kc span walk, ~line 2037). Under `SCRIP_ZD_DYNARM=7 SCRIP_ZD_PATREF=1`, any.sno stmt2 Kc dropped from 480B to 224B — exactly the predicted 256B reduction.

**Gate result (DYNARM=7 PATREF=1 with vs without clamp):**
- Without clamp: m3 277P/29F/11T · m4 268P/38F/10T
- With clamp: m3 270P/36F/11T · m4 258P/47F/11T
- **Net: −7 m3 passes, −10 m4 passes. 11 regressions all in the arbno/fence/defer family.**

**Root cause of regressions:** The clamp is wrong because the blob-closure members below `run_umin` are **genuine** accesses. stmt2's PATREF pattern references nodes from stmt1's allocation space (IR_MATCH_ASSIGN_SAVE, LIT_STRING, ASSIGN_IMM etc.) at their actual zls offsets. Those nodes are real dependents of stmt2's match — PATREF indirection reaches them at runtime, and their zls offsets ARE the right coordinates. The 224B residual is not spurious; it reflects the actual span of stmt2's cross-statement pattern closure.

**Verdict:** O-PB-2b is **ALPHA terrain**. The closure scoping lives in `zvo_resolve` / `zd_plan`'s `cm[]` walk. ALPHA owns those data structures. The correct fix is in the owner-table base scoping, not a span clamp. The clamp edit was reverted; gate confirmed back to bracket (282/274 BY SET).

**Transferable lesson:** `umin` in the Kc span walk is NOT contaminated. It correctly reflects the minimum offset of everything the run actually touches through its closure — cross-statement or not. An inflation at that level is an admission question, not a measurement question.

---

## §2 O-PB-3 FALSIFICATION: NAIVE OP_ZRES ARM

**Hypothesis (cursor):** `bb_match_defer.cpp` has zero `op_zres` references. Adding an `op_zres` arm that: (a) routes null-fn-ptr to omega instead of the slow arm (L0), (b) gates the entire slow arm body in `IF(!_.op_zres, ...)`, (c) adds a β stub (`x86_beta_trampoline()`) after the fast arm — would make PATREF work correctly under ZD regime and allow flipping `SCRIP_ZD_PATREF` default ON.

**What was built:** Three edits to `bb_match_defer.cpp`:
1. `IF(_.op_zres, x86_omega("jz"))` + `IF(!_.op_zres, x86("jz","L0"))` — routes null fn ptr to ω when ZD-armed.
2. `IF(_.op_zres, x86_beta_trampoline())` — β stub after fast arm.
3. Wrapped entire slow arm in `IF(!_.op_zres, ...)` — suppresses dead code.

**First failure:** `PORT_OMEGA` string is retired (Lon 2026-07-08) — used `x86("jz", PORT_OMEGA)` instead of `x86_omega("jz")`. Fixed.

**Gate result (after PORT_OMEGA fix, DYNARM=7 PATREF=1):** m3 274P/32F/11T · m4 265P/34F/10T. Still 8 regressions vs bracket.

**Root cause:** 053_pat_alt_commit (`P = ('a'|'b'|'c'); X P . V`) — `P` is admitted as a static PATREF, fast arm fires, null-fn-ptr check passes (fn is set), `bb_glue_pass_wires(4,5)` is called. But when the alternation inside `P` needs to **backtrack** (try 'b' after 'a' fails), it calls the PATREF's β. The β stub I added just jumps to ω — but the alternation's retry pump is gone. The slow arm's `rt_defer_open` + `rt_defer_step` loop IS the backtrack mechanism for patterns with internal alternatives.

**Architectural clarification:** `pat_static=1` means the pattern variable NAME is statically determined — NOT that the pattern VALUE is deterministic. `('a'|'b'|'c')` stored in P is static-named but has three alternatives. The slow arm's pump loop threads through each alternative. The op_zres arm cannot simply suppress the slow arm.

**What the cursor ACTUALLY means:** "The slow arm is GLUE #2 (FRAMED): replace with emitted `push rbp; mov rbp,rsp` + `bb_glue_pass_wires` + `mov rsp,rbp; pop rbp`." This means the slow arm's **C-level frame** (`xfer_enter`/`xfer_leave`) must be replaced with an **emitted RBP frame** — preserving the pump loop semantics but making it mechanism-2 compliant. This is the O-PB-4 nested-RBP work, not a slow-arm bypass.

**Verdict:** O-PB-3 requires GLUE #2 implementation (emitted `push rbp; mov rbp,rsp` wrapping the `rt_defer_open` pump loop). The naive suppression is wrong. All template edits reverted. Gate confirmed back to bracket (281/274 BY SET, the 282→281 m3 delta is 127 flake confirmed by 3 direct reruns).

---

## §3 GATE AT SESSION END

**SCRIP HEAD: `c9d84615` (unchanged).** Gate: m3 **281P/25F/11T** · m4 **274P/32F/10T** · BY SET identical to bracket · bench not re-run (no codegen change).

**O-PB-2b:** ALPHA terrain. Coordinate with ALPHA on `zvo_resolve` owner-table base scoping before attempting further span fixes.

**O-PB-3:** Prerequisite is GLUE #2 — emit `push rbp; mov rbp,rsp` + pump loop + `mov rsp,rbp; pop rbp` in `bb_match_defer.cpp` for the slow arm when `op_zres=1`. This is the same mechanism-2 nested-RBP frame needed for ARBNO and FENCE1 (O-PB-4). Sequence: O-PB-4 design → apply to `bb_match_defer.cpp` slow arm → then O-PB-3 gate flip.
