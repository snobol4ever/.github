# HANDOFF 2026-06-10 · Sonnet 4.6 · GOAL-SNOBOL4-BB · OLD SNOBOL4 LOWERER DELETED

**SCRIP commit: `bdb18d7`** (rebased over parallel Pascal `0d32565` + Prolog `cb127cb`, no conflicts, post-rebase smoke green).

## Lon directives executed this session
1. "Remove the old SNOBOL4 lower source file to eliminate confusion." — DONE.
2. "lower_pattern.c [my interim relocation of the old lowerer] is old code, delete it. The new lower_snobol4.c [nl/] is IT. THE ONLY. SNOBOL4 is isolated." — DONE.
3. "Leave [lower.c / ground-zero v_*] sources alone" — OBEYED after one overreach (see Pitfalls).

## What changed (all in SCRIP `bdb18d7`)
- **DELETED**: `src/lower/lower_snobol4.c` (1746-line old lowerer), `src/lower/lower_pattern.c` (its short-lived relocation), `src/lower/lower_snobol4_internal.h`.
- **SPLIT-PRESERVED**: the live `--dump-sno` AST→SNOBOL4-source transpiler (old file lines 1–661, fully independent of the lowerer half) is now `src/lower/tree_to_sno.c`, verbatim except the self-naming comment. Used by `scrip.c:1647` and `scripts/run_parser_sync_monitor.sh`. Verified working.
- **lower.c**: removed every SNOBOL reference — the `IR_LANG_SNO||SCO||REB → lower_sno` dispatch, the `ROLE_PATTERN → lower_pattern` case, the `TT_SCAN → v_scan` case, and the 4 SNOBOL pattern entry wrappers (`lower_subject_entry`, `lower_pat_build_entry`, `lower_match_entry`, `lower_pattern_entry`). **The v_* ground-zero family (16 fns) is untouched** — Lon: not SNOBOL, soon-to-be-dead, leave alone.
- **lower_internal.h**: dropped `lower_sno`/`v_scan`/`lower_pattern`/`lower_pattern_build` decls.
- **prove_lower.c**: dropped the 4 SNOBOL entry externs, 5 SNOBOL dump helpers (`dump_subject`/`dump_ref_invariant`/`dump_match`/`dump_pat`/`dump_sno_value`), and both SNOBOL test ranges in `main`. Icon Fig-1 + Prolog tests byte-untouched.
- **Makefile + scripts/prove_lower.sh**: `lower_snobol4.c` → `tree_to_sno.c`; pattern substrate dropped.

## SNOBOL4 isolation — verified facts
- `nl/lower_snobol4_nl.c` defines `lower_snobol4()` / `lower_snobol4_label(s)()` and calls NOTHING in lower.c (no `lower()`, no `nalloc`, no `wire_*`). Self-contained, as reported.
- Production routing unchanged: `lower_program.c:542` LANG_SNO → `lower_sno_nl` → NL. Snocone (.sc) and Rebus never touched the deleted code in production (Rebus has `rebus_lower()`; Snocone routes LANG_SNO→NL).
- Zero `lower_sno`/`v_scan`/`lower_pattern` references remain anywhere in src/ or scripts/.

## Gates (floor at bdb18d7 — record honestly)
- smoke 7/7/7 HARD ✅ · fence (test_gate_sno_pat_reg.sh) HARD ✅ · `--dump-sno` ✅
- **pat-rung: M4 16/19** — FAIL 050_pat_alt_two / 051_pat_alt_three / 054_pat_arbno_alt ("no match"). PRE-EXISTING b11a963 regression (NL default flip; its cross-check only ran m2). **The `SCRIP_NL=0` old-lowerer fallback NO LONGER EXISTS — fix forward only.** M2/M3 18/19 (053_pat_alt_commit = the D7-RB-1 target).
- **prove_lower: rc=0, NEW BASELINE 38 PASS** (was "68P"; delta = the 30 deleted SNOBOL tests). The 3 Prolog FAILs (`X is 2+3` expects 5 got 2; both `TT_IF g_ite` shapes off by 2) **pre-exist at the parent commit** — verified by stash-rebuild-run. Not this session's doing; do not chase them under this goal.

## Pitfalls discovered (read before touching anything near this)
1. The old file was TWO subsystems: lines 1–661 transpiler (LIVE), 662+ lowerer. Boundary surgically clean (zero cross-references). Anyone "restoring" the old lowerer from git history must not resurrect the transpiler duplicate.
2. `prove_lower` was the only caller of the deleted entry wrappers, but its harness reached `lower_sno` for VALUE tests too (the abort fired at `OUTPUT = "hello"`, not at a pattern test) — the old substrate was the whole SNOBOL arm of ground-zero lower.c, not just patterns.
3. v_* functions in lower.c serve ground-zero + old-Raku (`lower_raku.c:226/306/309 → lower_value_shared`). They are NOT SNOBOL. I briefly deleted them; Lon corrected; fully reverted from the git index. Hands off until Lon kills ground-zero itself.

## NEXT (unchanged)
Execute **D7-RB-1** exactly per `HANDOFF-2026-06-10-SONNET46-SNOBOL4-BB-D7-RB1-DESIGN.md` (125-byte LIT proto + 36-byte HEAD proto live-verified there; encoder gaps + IR_interp.c arms enumerated). Targets 053; plausibly resolves 050/051/054.
