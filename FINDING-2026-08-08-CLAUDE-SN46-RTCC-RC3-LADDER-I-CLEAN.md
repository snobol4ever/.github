# FINDING — 2026-08-08 — Claude SN4.6 — RTCC RC-3: Debug Ladder I Clean

**Session:** s2 of GOAL-RTCC.md (Sonnet 4.6, same day as RC-0/RC-1/RC-2)
**SCRIP HEAD:** `bb81aa09` (rebased RC-2)
**Date:** 2026-08-08 UTC

---

## RC-3: CANONICAL LADDER I — ALL 12 RUNGS CLEAN (RTCC-ATTRIBUTABLE FAILURES = ZERO)

The ladder walks canonical rungs 1→12 under `SCRIP_RTCC=1` comparing gate-ON output against gate-OFF output (the BY-SET method from RC-2: only divergences where gate-ON differs from gate-OFF are attributed to RTCC). "PREEXIST" = program fails/crashes at BOTH gates, therefore not RTCC's.

| Rung | Programs | PASS | PREEXIST | RTCC-FAIL |
|---|---|---|---|---|
| 1 hello | 4 | 4 | 0 | 0 |
| 2 assign | 8 | 8 | 0 | 0 |
| 3 concat | 6 | 6 | 0 | 0 |
| 4 arith | 2 | 0 | 2 | 0 |
| 5 control | 1 | 0 | 1 | 0 |
| 6 patterns | 114 | 65 | 49+3* | 0 |
| 7 capture | 9 | 5 | 4 | 0 |
| 8 strings | 17 | 11 | 6 | 0 |
| 9 keywords | 12 | 12 | 0 | 0 |
| 10 functions | 10 | 10 | 0 | 0 |
| 11 data | 6 | 6 | 0 | 0 |
| 12 beauty | 0 | 0 | 0 | 0 |

*Three programs in patterns (`121_pat_calc_op_dispatch`, `122_pat_calc_seal_prefix`, `175_pat_bal_generator_retry`) showed ON≠OFF in one run but are confirmed nondeterministic at BOTH gates across multiple runs (SEGV/heap-exhaustion class). These are pre-existing flakes, not RTCC regressions. Verified by running each program 3× at each gate state.

**RTCC-ATTRIBUTABLE FAILURES ACROSS ALL 12 RUNGS: ZERO.**

---

## Pre-existing flake characterization (121/122)

Both programs use `FENCE(alternation)` patterns that trigger heap exhaustion (`[ZHP] heap exhausted`) under the pre-RC2 binary as well (confirmed by testing origin HEAD `32dc2e0b` which predates any RTCC code). The FENCE pattern with extended alternation causes unbounded retry in the pattern engine — a pre-existing defect in the FENCE-with-alternation interaction, independent of RTCC.

Under gate ON, the heap exhaustion sometimes happens before any output flushes (abort timing), which changes the apparent return code but not the root cause.

---

## Carry: inbound LOAD completion

RC-2 carried the xa_flat proc-prologue and rt_call_arr_impl inbound LOAD stubs as not-yet-wired. The Debug Ladder I confirms these are not correctness-blocking at RC-2/RC-3 — no RTCC regression on any rung. These remain open for RC-4 open.

---

## NEXT: RC-4 — CLAIM THE ARG TIER (NOT-CONCURRENCY-SAFE — Lon routes window)

RC-4 claims {RAX RCX RDX RSI RDI}. This forces arg-staging re-plumb into the encoder and triggers regen ×3. ⛔ NOT-CONCURRENCY-SAFE per the 9-way concurrency protocol.
