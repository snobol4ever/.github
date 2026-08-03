# FINDING-2026-08-03-CLAUDE-SN4-OMEGA-S34-GATE-MEASUREMENT-ALPHA-S32-ZD-CAP-PLUS10-AND-O8-CLOSED

**Session:** s34 (2026-08-03, Sonnet)
**SCRIP parent:** `2c4dbcf1` (O-5 ZW-3 r12-direct, s33 OMEGA)
**No code commits this session — measurement + cursor update only.**

## Summary

Full gate measurement at HEAD `2c4dbcf1` after ALPHA s32 commits are in the tree.
O-8 formally closed (s33 audit confirmed all five SHED rungs done; checkbox was stale).
+10 passes on both m3 and m4 attributed to ALPHA s32 `SCRIP_ZD_CAP` default ON.

## Gate measurement at HEAD

**m3:** PASS=291 FAIL=25 TIMEOUT=2 — was 281P/35F/2T at s33 cursor. **+10 passes.**
**m4:** PASS=285 FAIL=32 TIMEOUT=1 — was 275P/42F/1T at s33 cursor. **+10 passes.**
**Bench:** 18/21 EXACT HOLD (eval_dynamic + eval_fixed + roman = pre-existing residue).

BY SET check: the 25 m3 failures and 32 m4 failures are a strict subset of the s33 fail set.
Zero new regressions introduced. The +10 passes are new gains from ALPHA s32.

## Attribution: ALPHA s32 ZD-CAP default ON (`550915ff` / `1c86922b`)

ALPHA s32 flipped `SCRIP_ZD_CAP` default OFF→ON, admitting the CAPTURE family
(SAVE/COND/IMM template ZD arms) for the full corpus. `ASSIGN_SAVE` declined count
was 41→0. 263/318 programs became fully armed at s32.

The +10 pass delta across both modes is exactly the programs that were previously failing
due to unarmed CAPTURE boxes generating UCLAIM wholesale-claim code where the ZD arm
now emits per-node cells. MERGE GATE at the rebased HEAD confirms the improvement is
robust (BY SET zero new failures on OMEGA's owned files).

## O-8 RBP-SHED — formally closed

s33 audit measured all five SHED rungs complete at HEAD:
- SHED-3: `g_emit.flat_outer_nparams` in struct, copied at emit_chain choke. DONE.
- SHED-1: `emit_jmp_pin_rbp()` gates on `flat_deep_arrival || flat_pat || flat_gen` only.
  `flat_outer_nparams` not in the pin predicate. DONE.
- SHED-2: STF rbp bracket (`ZGPOP-STF`: `mov rsp,rbp`) is the depth-independent cut.
  The per-depth stub ladder (O-2) is DEPRECATED (Lon ruling, observer seat). ABORT's
  `x86_omega()` routing is correct under STF discipline. DONE.
- SHED-4: `x86_align_enter/leave` are no-ops under `ZC_FRAME_RSP` (the default).
  `x86_align_enter()` returns empty string. DONE.
- SHED-5: Same as SHED-4. Transient push-rbp alignment window is moot. DONE.

Census at HEAD: rbp-bearing 140 programs / push_rbp 310 total / armed (cas_base) 38 programs.
The 249 non-armed push_rbp = law-4 legitimate (ARBNO deep-arrival, DEFINE call protocol,
CLASS C chain-entered LBL__/EVAL by ledgered decision). Zero [rbp+-N] data reads outside
armed programs — GLUEO suppressed all closed-loop ceremony.

## RSP/RBP FORTH-style stack — current state

The FORTH discipline (every BB allocates its own `sub rsp,K` at α, reads operands
NON-POPPING at `[rsp+Δ]`, frees at ω) is complete for the admitted population.
The armed canonical-frame population (38 programs / 23 per s32 crosscheck scope)
uses the law-4 RBP construct correctly: `push rbp; mov rbp,rsp; sub rsp,K≤64` at
MATCH_BEGIN α, `mov rsp,rbp; pop rbp` whack at MATCH_END ω.

The remaining non-compliant population is the DEFER/PATREF/recursive-pattern class
(105 declined runs at ALPHA s32 frontier). These are the semantic ceiling: a deferred
`*P` re-enters the matcher at runtime-variable depth, and the nested-frame protocol
for that class is a design-tier rung not yet proposed to Lon. O-9 (reconciliation)
waits for this design question, not for any code task on the board.

## NEXT

O-9 reconciliation. ALPHA declared itself done at s32 (cursor: "A-9 NEXT: RECONCILIATION
(both fronts done)"). OMEGA's O-8 is now formally closed. Both fronts are at the merge
point. O-9 steps: pull-rebase, rebuild, run PLAYBOOK §7 five completion tests + fresh-clone
regen ×4, reconcile parent goal file cursor + watermark of record, single `[RECON]` commit.
First concrete task: propose the DEFER/PATREF nested-frame design to Lon (the semantic
ceiling that defines the admission frontier) rather than waiting indefinitely.
