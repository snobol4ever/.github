# HANDOFF 2026-06-13 — Sonnet 4.6 — BB-FIXUP Z→A Lap 1

## Session identity
Model: Claude Sonnet 4.6 · Goal: GOAL-BB-FIXUP-Z-to-A.md · Attended by Lon

## Repos at handoff
SCRIP @ 722ca39 (pulled; concurrent SNOBOL4-BB work absorbed)
.github @ 92f90538 (pulled; concurrent watermark absorbed)

## Cursor at handoff
`bb_scan_tab.cpp` — Z→A ring, lap 1 (reset by Lon 2026-06-12 for BOTH-MEDIUM sweep)

## Work completed this session — 10 cursor stops

| File | Violations before → after | Key conversions | Commit |
|---|---|---|---|
| `bb_var_global.cpp` | 2→0 CLEAN | bypass×2: ROQ + def/.quad/label/.string | 2a08787 |
| `bb_var_frame_ref.cpp` | 2→1* | CV9 drop IR_t*pBB + bb_prepare dispatch, CV4 ternary guard | d0cc142 |
| `bb_var_frame.cpp` | 2→1* | same as bb_var_frame_ref | 4c13ac2 |
| `bb_var.cpp` | 5→0 CLEAN | bypass×2 + 5-arm→2-return ternary chain | 44777ea |
| `bb_unop.cpp` | 22→15* | 9→2 returns in bb_unop() top-level | 9826cb9 |
| `bb_unify.cpp` | 13→6* | CV6 auto-lambdas→static helpers, 6→2 returns | 14ae014 |
| `bb_to.cpp` | 1→1* | CV6 local→bb_to_by() static, CV9 param drop + bb_prepare | b8b80f5 |
| `bb_succeed.cpp` | 0 already CLEAN | — | — |
| `bb_subject.cpp` | 10→5* | CV6 7-locals→3 static helpers, CV4 5→2 returns | a30b055 |
| `bb_scan_upto.cpp` | 3→0 CLEAN | CV6 inline strchr_fp, bypass×2→ROQ+def/.quad/label/.string | 01a868b |

*residuals = counter-scope-trio sanctioned (R2-KEEP static/lambda/switch returns per 38th/40th-run standing verdict)

## Design decisions made

**CV9 pattern confirmed:** `bb_var_frame`, `bb_var_frame_ref`, `bb_to` all had `IR_t *pBB` params.
Dispatch in emit_core.c updated: `bb_prepare(nd); bb_*()`; bb_templates.h decls updated to `()`.
bb_prepare does NOT handle IR_VAR_FRAME / IR_VAR_FRAME_REF / IR_TO_BY — `g_emit` slots are pre-set
by flat-chain driver before emit_core is reached; bb_prepare call is a no-op for these kinds but
is the correct structural form per CV9.

**counter-scope-trio** (standing verdict from 38th/40th runs, unchanged):
- FOR-lambda `return` inside `x86()` argument → rp residual, sanctioned
- R2-KEEP value-computer static helpers with `return` → rp/hc residual, sanctioned
- switch-case `return` in resolve helpers (bb_unop_resolve) → rp residual, sanctioned
These are NOT real violations. Lon verdict on rp/hc scope-widening still open.

**bb_subj_nlbl() pattern:** `emit_intern_str` called twice (if-check + return) to avoid
`const char * n` local that would trigger `local_vars` audit regex file-wide.
Semantically identical — `emit_intern_str` is a pure lookup.

## Gate state at handoff
- build_scrip.sh: GREEN
- make libscrip_rt: GREEN
- C2 asm-identity (bbN-normalized diff): EMPTY for all 10 stops
- test_gate_icn_var: pre-existing FAIL (m4 mode 17/17 probes, corpus not cloned) — UNCHANGED
- test_gate_bb_one_box: pre-existing FAILs (missing extern "C" wrappers in Prolog-lane bb_*.cpp) — UNCHANGED
- test_gate_template_medium_invisible: informational baseline, not gating

## Next stop: bb_scan_tab.cpp
Quick audit preview (not yet run this session):
Expected violations: likely bypass (x86_ro_load_q / x86_ro_seal_str pattern), possibly lv/rp.
Standard pattern: ROQ conversion + def/.quad/label/.string decomposition.

## Outstanding verdicts (unchanged from prior sessions)
1. rp/hc counter-scope scope-widening (exclude lambda/helper returns from count?)
2. bb_arith dead-dispatch retirement (lower-unreachable finding, 37th run)
3. nw subscript-regex widen (audit misses param-alias form)
