# SESSION HANDOFF — 2026-05-23 (orientation only, no code changes)

## Repos at handoff

| Repo | HEAD |
|------|------|
| SCRIP | `cf9284f5` |
| corpus | `3e223db` |
| .github | `db558a72` |

## Gate

**PASS=409 FAIL=0 STUB=645** — confirmed at session start. Zero regressions.
Icon --interp: PASS=195 FAIL=36 XFAIL=35 TOTAL=266 (normal mode)
Icon --interp honest (SCRIP_NO_AST_WALK=1): PASS=195 FAIL=36 XFAIL=35

## What was done this session

Orientation only. Three repos cloned, PLAN.md + GOAL-ICON-BB.md + RULES.md read.
Session-start gates confirmed clean. No code written, no commits, no regressions.

### Key findings

- rung01 `to_by` passes in all modes (--interp, SCRIP_NO_AST_WALK=1, --run)
  because lower_icn.c emits BB_TO_BY (old SNOBOL4 node) for Icon `to by`, not BB_ICN_TO_BY.
  ICN-T-2's x86 arm in bb_icn_to_by.c will require lower_icn.c to emit BB_ICN_TO_BY
  for Icon (TT_TO_BY → BB_ICN_TO_BY instead of BB_TO_BY).

- GATE-PK script is `scripts/test_per_kind_diff.sh` (PASS=409 FAIL=0 STUB=645).

- Non-rung36 honest failures (pre-existing, not new):
  - rung06_cset_upto_basic: infinite output (both normal + honest) — scan loop bug
  - rung13_alt_alt_filter: no output (both normal + honest) — conjunction-in-every bug

## NEXT: complete ICN-T-2 (same steps as SESSION-2026-05-22-HANDOFF-B.md)

1. emit_core.c: pull BB_ICN_TO_BY out of stub fallthrough → `bb_icn_to_by(nd); return 0;`
2. lower_icn.c: change TT_TO_BY arm to emit BB_ICN_TO_BY (not BB_TO_BY) for Icon lang
3. Implement IS_X86 arm in bb_icn_to_by.c (semantics: step in ival3, lo in ival, hi in ival2;
   on α seed counter=lo; on β counter+=step; exhaust if (step>0 && counter>hi) or (step<0 && counter<hi))
4. Makefile: add bb_icn_to_by.c to SRCS
5. make -j4 scrip
6. bash scripts/test_per_kind_diff.sh  # must hold PASS=409 FAIL=0
7. bash scripts/test_icon_all_rungs.sh # rung01_paper_to_by must PASS
8. SCRIP_NO_AST_WALK=1 bash scripts/test_icon_all_rungs.sh  # same
9. Mark ICN-T-2 [x] in GOAL-BB-TEMPLATE-LADDER.md, update watermark → NEXT ICN-T-3
10. Update PLAN.md BB Template Ladder row
11. Commit SCRIP; commit .github last; push both

## Session health note

Context window was ~40-45% at handoff. Session was deliberately kept short to preserve headroom.
