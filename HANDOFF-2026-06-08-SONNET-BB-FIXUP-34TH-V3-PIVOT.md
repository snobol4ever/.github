# HANDOFF — BB-FIXUP 34th run (Sonnet, Lon attending) — STRATEGY PIVOT to OPERATING MODE v3

**Read order next session:** PLAN.md → GOAL-BB-FIXUP.md (**new ⛔ OPERATING MODE v3 section + THE LOOP steps 4–5**) → BB-REVAMP-TRACKER.md (top note, cursor) → this.

## What changed (the point of this run)
Lon: grinding GRAND down ~2 violations/commit, each behind a full rebuild + 10-gate battery + asm-identity proof, pays the verification cost **per helper** when it is fixed **per file**. So the cross-cutting FIX-8 "census lap / ONE HELPER PER COMMIT" cadence is **RETIRED**. New canonical mode (committed to GOAL-BB-FIXUP `3c893d45`):
- **CONVERSION RULES R1–R5** (per file): R1 terse `IR_<KIND>` comment · R2 inline+delete EVERY multi-emit helper · R3 de-escape `ins1/ins2/ins3/Lins*` to real byte-emitting `x86()` · R4 v2 hygiene (one return/platform, kill sig-line decls + static-helper constellations, drop MEDIUM_* wrappers, 1-src=1-asm, ≤200col, comment/blank purge, separators) · R5 absolutes (zero raw bytes, zero emit_fmt, real Greek, EMIT-BLIND; can't-reach → [S] note → FIX-3/FIX-4 split).
- **PER-FILE CHECKS C1–C5** run ONCE after all rules: C1 build · C2 emitted-asm identity per changed box (normalized `.s` diff EMPTY; object-byte-identity INVALID at -O0) + behavior parity · C3 full battery at floors · C4 rank no-growth · C5 ONE-file commit + rebase + push + cursor tick.
- `audit_multi_emit_helpers.py` demoted to a **per-file lookup**, not a cross-file worklist.

## State (all pushed, local==origin)
SCRIP `8d2b7d2` · .github `3c893d45`. **NO-GROWTH CEILING = 114 files / 110 dirty / 4 clean / GRAND 2540.**
Three landings this run (the LAST under the retired per-helper cadence, all asm-identity proven): bb_det_cmp `dcm_rt_call` (42d7c92) + `dcm_const_fold` (295ec11) → **bb_det_cmp 8b-COMPLETE** (44→40); bb_det_is `bdis_const_fold` (bb76d68, 59→57). Rebased cleanly over BB-neutral IRD lower-isolate `f3215f7`+`2a72e35` (src/lower only).

## Next session — start here
**CURSOR = bb_det_is.cpp** — finish it as the clean v3 PILOT (it is GZ-era, zero `ins2`, no [S]): apply R2 to the 3 remaining multi-emit helpers `bdis_var_const` + `bdis_bivar` (sole-site) + shared `bdis_tail` (3 sites) + R1 terse comments + R4 drop the mt=3 `IF(MEDIUM_TEXT)` head-wrappers — **ALL in ONE commit, ONE C1–C5 battery.** Probe that fires the arms: `main :- X is Y op C` / `Y op Z` with bound vars (rt_pl_is_cell_arith / rt_pl_is_cell_bivar); the const arm is `X is 2+3`. Expect bb_det_is 57 → low-single-digits.
Then ring resumes at **bb_aggregate_nb** (rb=5/mt=2 arms are [S] on `emit_term_from_node_bin` term-plumbing → apply mechanical R1–R4, [S]-note the blocked arms).

**Target-selection rule for v3 file picking:** GZ-era PL-GZ boxes = clean `x86()` both media = fast convert; older TEXT arms using `x86("ins2",…)` (bb_list/bb_succ_plus/bb_term_io/bb_io) are R3/FIX-9 work (Cat B needs XK_RIPLBL/XK_LBLDIFF encoders first). bb_call family stays FIX-3-excluded; bb_gvar_assign is FIX-4.

## Outstanding Lon verdicts (UNCHANGED, 6)
x86_movimm uint32-trunc (bb_call_fn) · RING/DIRECTORY RECONCILE · prove rc=0-on-FAIL hardening · PL-GZ-8 arith-is 2-vs-5 (PL-GZ) · m2 disj-backtrack silent-empty (PROLOG-BB) · IRD-2b IR_t.own DEVIATION ratify. No LADDER rungs closed.
