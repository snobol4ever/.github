# FINDING 2026-08-02g — 067_pat_fence_fn_vs_kw times out under ZD-5b LIT admission

**Rung:** OMEGA s25a merge gate (ALPHA commit `66399568` `[ALPHA] A-7 ZD-5b IR_MATCH_LIT`).
**Severity:** P→T regression in m3 under SCRIP_ZD_MATCH=1 (default ON).

## What happened
067_pat_fence_fn_vs_kw was PASS (m3 and m4) in the open bracket at OMEGA s25a (parent `5c959cab`). After `git pull --rebase` brought in two ALPHA commits (`3dc36147` IR_GOTO admission + `66399568` LIT admission), re-running the full §3 gate shows 067 times out in m3 (rc=124) with SCRIP_ZD_MATCH=1 (default). With SCRIP_ZD_MATCH=0 it passes immediately (exit 0, output "both correct").

## Attribution
Bisect: SCRIP_ZD_MATCH=0 → pass. SCRIP_ZD_MATCH=1 → timeout. Regression is in ALPHA's admission gating, not OMEGA's commits (A-5/O-3/O-4/O-7a/SHED-3 are all 318/318 byte-identical neutral when ZD_MATCH=0 verified pre-rebase).

ALPHA commit `66399568` message claimed "m3 295/22 BY SET IDENTICAL to open bracket" — possible container-speed difference hid the timeout (067 completed in their container, timed out at 8s in ours).

## Impact
- m3: 067 PASS → TIMEOUT (P→T)
- m4: not observed (m4 times out at compile or runs fast enough)
- 173_pat_fence_kw_blocks_backup: FAIL → PASS (improvement from LIT admission)
- test_string: LERR → FAIL in m4 (different error mode; .s changed from ALPHA; harness edge per ALPHA note)
- Net: BY SET has one new P→T member; not zero-regression

## Required action
ALPHA: investigate why 067 times out under ZD_MATCH=1. The program uses FENCE function patterns; LIT admission may have changed the run structure in a way that creates an infinite retry loop. MONITOR-FIRST per RULES.

OMEGA: cannot push through a P→T regression per contract §3. Held pending ALPHA fix or Lon ruling.
