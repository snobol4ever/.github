# GOAL-ICON-BB-JCON.md — Icon ir-run FAIL triage

**Repo:** one4all + corpus + .github
**Prereq:** GOAL-ICON-BB-NATIVE ✅ `7efdf09a`

## Session Setup

  cd /home/claude/one4all && bash scripts/build_scrip.sh

⚠ No coro subsystem. Icon is pure BB. Do NOT touch coro_runtime.c or coro_*.
⚠ BB RULE: Read `.github/jcon_irgen.icn` before touching any BB.
⚠ NO C BB BOXES. `icon_gen.c` is DELETED. Do NOT create new C BB box functions (no `DESCR_t foo(void *zeta, int entry)` implementations). All BB behaviour is in the C template emitter functions (`emit_bb_icon_*` in `emit_bb.c`). Dispatch in `icn_bb_build` routes to the lazy fallback; fix generators by correcting `lower.c` emission and `icn_bb_build` dispatch to existing template infrastructure, not by writing new C box functions.

## Gates

  GATE-1  bash scripts/test_smoke_icon.sh                 # PASS=5
  GATE-2  bash scripts/test_smoke_unified_broker.sh       # PASS=23
  GATE-3  bash scripts/test_icon_ir_all_rungs.sh          # PASS >= prev
  GATE-4  bash scripts/test_icon_sm_no_ast_walk.sh        # honest PASS >= 273

## Active steps

### IJ-19a — upto(cset,str) scalar dispatch in icn_bb_build

`upto(cset,str)` with scalar args has no dispatch case in `icn_bb_build` — falls to lazy fallback.
Mirrors `find(needle,str)` pattern. Fixes kross/meander/htprep.

- [ ] In `icn_runtime.c` `icn_bb_build` TT_FNC: when `fn=="upto"` and `nargs>=2` and `!is_suspendable(e->c[2])`,
      eval cset+str args, route through the scan_builtins upto path wrapped as a oneshot or
      via existing `icn_bb_build` scan-context upto machinery. GATE-1..4. Commit.

### IJ-19b — icn_drive_node extern + bb_eval_value injection

`icn_drive_node` defined in `icn_runtime.c` but not extern'd in `icn_runtime.h`.
`bb_eval_value` never checks it → `icn_bb_cat` injection silently ignored → `s[1 to 3]`
gives `a,a,a` not `a,b,c` (rung16).

- [ ] Add `extern tree_t *icn_drive_node;` to `icn_runtime.h`.
      Add at top of `bb_eval_value`: `if (icn_drive_node && e==icn_drive_node) return icn_drive_val;`
      GATE-1..4. Commit.

### IJ-19c — drive injection in TT_EVERY/TT_ASSIGN

TT_EVERY/TT_ASSIGN while-loop calls `bb_eval_value(gen)` without setting `icn_drive_node`.
`(1 to n)` rebuilds from α each tick → rung02 gives 5 not 15.

- [ ] In `icn_value.c` TT_EVERY/TT_ASSIGN loop body: save/set/restore
      `icn_drive_node=leaf, icn_drive_val=tick` around `bb_eval_value(gen)`. GATE-1..4. Commit.

### IJ-19d — FRAME.suspending in proc call dispatch

Proc call dispatch checks `FRAME.returning` and `FRAME.loop_break` after
`bb_exec_stmt(st)` but not `FRAME.suspending` → suspend inside while-loop dropped (rung03).

- [ ] In `icn_runtime.c` proc call body loop: add `if (FRAME.suspending) { DESCR_t sv=FRAME.suspend_val;`
      `z->suspend_body=FRAME.suspend_do; z->in_suspend=1; FRAME.suspending=0; return sv; }`
      GATE-1..4. Commit.

### IJ-19e — real to-by generator

`icn_bb_build` TT_TO_BY always uses int path. `icn_bb_to_by_real` was in the deleted
`icon_gen.c` — real `to-by` (rung19: `3.0 to 1.0 by -1.0`) gives ints instead of reals.

- [ ] Implement real to-by dispatch in `icn_runtime.c` `icn_bb_build` TT_TO_BY:
      after coercion, `if (!any_str && IS_REAL_fn(lo_d) && IS_REAL_fn(hi_d) && IS_REAL_fn(step_d))`
      route through appropriate real range machinery (no new C BB box — use template path).
      GATE-1..4. Commit.

## Done when

  ir-run PASS >= 230. Honest PASS >= 268. GATE-1..4 green.

## Invariants

1. GATE-1: smoke_icon PASS=5. Never regress.
2. GATE-2: broker PASS=23. Never regress.
3. GATE-3: ir-run PASS must not decrease.
4. GATE-4: honest PASS must not decrease.
5. One cluster per step, own commit.
6. New test source has matching .expected in same commit.
7. No corpus source modified to work around runtime bugs.

## Watermark

  one4all: 1203986f  corpus: 1fe096c
  ir-run:  PASS=191 FAIL=39 XFAIL=35
  honest:  PASS=276 FAIL=1 ABORT=0   broker: 23/49
  NEXT: IJ-19a — icn_bb_upto Byrd box (scalar args generative)
