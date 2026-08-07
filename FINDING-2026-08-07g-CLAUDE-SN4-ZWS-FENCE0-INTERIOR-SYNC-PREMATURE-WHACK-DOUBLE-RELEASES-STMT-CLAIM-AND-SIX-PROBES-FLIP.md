# FINDING-2026-08-07g — SN4 ζ-CLIMB C-4 — ZWS FENCE0 interior-sync α prematurely whacks the statement claim; double-release on success path; six probes flip

**Session:** 2026-08-07 (Claude Sonnet 4.6) · **Goal:** GOAL-SN4-ZETA-CLIMB · **Rung:** C-4 ALTERNATION + CAPTURES
**SCRIP before:** `07d31e9d` · **corpus before:** `6f5e8102`
**Fix commit:** see handoff · **Probes flipped:** F04 G05 G09 G17 G18 G21 (m3 + m4, 6 XPASS each)

---

## Symptom

F04 (`('a' . Y) FENCE 'b'`, match succeeds): SEGFAULT after correct output in m3.
G05/G09/G17/G18/G21: same family — FENCE0 interior sync box inside a ZWS-armed statement, success path.
F03 (identical shape but match fails overall): passes — fail path avoids `match_end` entirely.

Monitor: step 8 divergence — csn emits `@5 VALUE OUTPUT = STRING(2)='=S'`; spl jumps to `LABEL stno=INT=7`.
`SCRIP_FENCE_WHACK=0` cures all six → pointed at the FENCE0 whack in `bb_match_fence1.cpp`.

## Root cause

`bb_match_fence1.cpp` ival=0 arm (the FENCE0 interior sync box) emitted under `op_zw=1`:

```cpp
+ IF(x86_port_cstack() && fence_whack_on() && _.op_zw,
      x86("lea", "rsp", "qword ptr [rbp# + -8]"))
```

Under the ZW canonical frame (`op_zw=1`, UCLAIM), the statement claim (`sub rsp,K`) lives **below** the graph rbp floor. The FENCE0 whack freed it at FENCE0's α. Then `match_end`'s ZW-15 teardown (`lea rsp,[rbp-8]; pop rbp`) ran correctly — restoring rsp to claim_base. Then `statement_end`'s staged `add rsp,K` (here 192) freed the already-gone claim a **second time**, launching RSP 192 bytes past the caller's return address → SEGFAULT on the next call.

F03 escaped because `'z'` doesn't match — the fail path (`add rsp,272; jmp n12_match_begin_af`) has its own absolute RSP unwind and never reaches `match_end` or `statement_end`.

The ZWS arm here is the mirror of the non-zw `mov rsp,rbp` arm already retired under FENCE-WHACK-UCLAIM (same double-release disease; cured by `SCRIP_FENCE_WHACK=0` in both cases). WHACK CONTRACT clause 5: `statement_end` is the sole authority for the statement claim. `match_end`'s ZW-15 teardown subsumes everything the FENCE0 sync box was trying to do here.

## Fix

`src/templates/bb_match_fence1.cpp` — ival=0 arm: remove the `IF(op_zw, lea rsp,[rbp-8])` line entirely. The ival=0 FENCE0 box is now a pure pass-through under ZWS: α → γ → ω, no RSP touch. One line deleted.

## Verification

m3 before: 128/14/0/0 · m3 after: **128/8/6/0** (6 XPASS, 0 regressions)
m4 before: 118/24/0/0 · m4 after: **118/18/6/0** (6 XPASS, 0 regressions)
XFAIL entries removed in same commit: F04 G05 G09 G17 G18 G21 (both XFAIL.run and XFAIL.compile).

## Scope / limits

This fix covers the FENCE0 interior sync box (`ival=0`) only. The FENCE1 (`ival=1`, `FENCE(P)`) commit path uses `fence_whack_commit` which already takes `fence_release(off)` (watermark restore, not stmt_claim) — unaffected. C-4 crater members A05/A06 (m4 crash, ALT3+capture) and F03/F05 (m4 crash, capture-behind-FENCE) are separate defects, not touched here.
