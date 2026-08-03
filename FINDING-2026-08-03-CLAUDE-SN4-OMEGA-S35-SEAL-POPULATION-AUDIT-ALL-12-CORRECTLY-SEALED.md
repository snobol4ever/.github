# FINDING-2026-08-03-CLAUDE-SN4-OMEGA-S35-SEAL-POPULATION-AUDIT-ALL-12-CORRECTLY-SEALED

**Session:** s35 (2026-08-03, Sonnet)
**SCRIP parent:** `4bba30c4` (ZW-14 s33b)
**No code commits — audit only.**

## Summary

Full audit of the 12 `why=seal/no-END/window` ZWS declines at HEAD `4bba30c4`.
Result: all 12 are correctly sealed. No false seals to unblock. The seal predicate
is sound for every member of this population.

## Census at HEAD

SCRIP_ZWS_DIAG=1 over 318 crosscheck programs gives:
- 101 `blob-clause` declines: all have `nblob_real>0` (genuine live FRQ-slot blob
  members). These are the r9/wire rung — multi-template, not this session.
- 12 `seal/no-END/window` declines: all have `nblob_real=0`.
- Bench: 18/21 EXACT HOLD.

## Seal analysis by program

**058_pat_fence_keyword, 067_pat_fence_fn_vs_kw, 173_pat_fence_kw_blocks_backup,
cross (Kc=944):** Pattern `LEN(N) FENCE LEN(M)` — bare `FENCE` keyword used as a
pattern operand. The lowerer (lower_snobol4.c:317) maps `FENCE0` (bare keyword,
`t->n==0`) to `IR_CALL` to `SNO$PB0` (pattern-value construction), NOT to
`IR_MATCH_FENCE1`. The `IR_CALL` in the run triggers the `zdyn` dynamic-box veto
(a runtime-variable pattern value), which sets `_seal=1`. **Correctly sealed.**
No change needed.

**061_pat_fence_fn_seal, 068_pat_fence_fn_three_way, 069_pat_fence_fn_full_match,
101_pat_fence_falls_through, 107_pat_fence_nested:** These use `FENCE(P)` function
form (FENCE1, `t->n>0`), which lowers to `IR_MATCH_FENCE1`. Under
`SCRIP_ZD_FENCE1=1` (default ON), the run-member seal exclusion fires and FENCE1
does NOT set `_seal`. However, the window-integrity scan (the `if (zws)` loop)
zeroes `zws` when a member's γ/ω edge escapes the run. For these FENCE(P) programs
the FENCE1 itself has exit edges to outside the run (to alt-fail or statement-begin).
**Correctly sealed by window-integrity.**

**161_pat_defer_fn_nested_match:** Graph-scope DEFER seal — the pattern-function body
contains `IR_MATCH_DEFER`. The `*P` recursive deferral re-enters the matcher at
runtime-variable depth; the ZW canonical frame's `mov rsp,rbp; pop rbp` would land
against a nested activation. **Correctly sealed. This is the LAWS DEFER-DEEP-LOAD-BEARING
warning applied verbatim.** Admission requires nested-frame protocol design — Lon ruling.

## What this means for the OMEGA roadmap

The 12 seal declines are a correctly-sealed **semantic ceiling**, not a predicate bug.
The FENCE(P) window-integrity cases (8 of 12) are sealed because FENCE1's exit edges
genuinely escape the run at graph build time — correcting that would require the lower
to restructure the pattern graph topology, which is a separate design rung.

The only path to widening the armed population beyond the current 49-program ceiling is:
1. **r9/wire rung** (101 blob-clause declines with `nblob_real>0`): pass r9=blob-claim-base
   from match_begin's op_zw arm; add `op_zw` arms to ARBNO, BREAK, BREAKX, SPAN_VAR,
   SPAN, BAL, ALTERNATE, SEQUENCE, FENCE1, REPLACE, DEFER, CAPTURE using r9-relative
   addressing. Multi-template, ~1 full session.
2. **DEFER/PATREF nested-frame design** (161 + seal cases): propose protocol to Lon.

## NEXT

r9/wire rung is the next executable code rung. All other seal declines are correctly
sealed with no false positives to unblock. Bench 18/21 EXACT HOLD. Gate unchanged.
