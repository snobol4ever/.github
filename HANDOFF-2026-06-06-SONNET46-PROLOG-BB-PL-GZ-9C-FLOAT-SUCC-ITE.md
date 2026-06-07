# HANDOFF 2026-06-06 (Sonnet 4.6) — PROLOG-BB: PL-GZ-9 float/succ/ITE admission

SCRIP commit: `7f4b3db`. .github commit: this doc + GOAL-PROLOG-BB.md update.

## Session summary

### What landed (all in 7f4b3db)

**m3 ratchet 24 → 31** (+7 new PASSes).

**rung18 (5 tests) — succ/2 and plus/3:**
- `pl_flat_goal_is_simple` BUILTIN: added `succ/2` (LV/LIT_I args) and `plus/3` (LV/LIT_I arg triple).
- These builtins were already emitted by `bb_succ_plus.cpp` via `bb_resolve` — the only blocker was the admission gate.

**rung42 (2 tests) — float unify `X = 3.14` and `2.5 = 2.5`:**
- `pl_flat_goal_is_simple` UNIFY: added `IR_LIT_F` to `l_con`/`r_con`; added const=const `(lc && rc)` fold (needed for `2.5 = 2.5` in ITE cond).
- `pl_gz_rule_body_goal_ok` UNIFY: same additions + `IR_LIT_F` in write arg.
- `pl_gz_admit` scan UNIFY: `IR_LIT_F` + `(lc && rc)` admitted.
- `rt_pl_unify_cell_float(void *cell_term, double dval)` added to `src/runtime/unification.c`.
- `bb_cell_unify.cpp`: new cell↔float arm (uses `x86("movsd", "xmm0", F64(fval))` + `rt_pl_unify_cell_float`); const=const extended to `IR_LIT_F` (emit-time eq/neq fold).
- ITE-as-entry γ-chain walk: when `gconj==NULL && !softdisj` and entry is `IR_ITE`, walk the γ-chain collecting non-GCONJ nodes as goals. This admits `main :- (2.5=2.5 -> write(yes) ; write(no)), nl.`.

**rung19_format_format1_nl (1 test):**
- `pl_flat_goal_is_simple` BUILTIN: added `"format"` to `is_io` list; `format/1` with ATOM arg returns 1.
- Template `bb_term_io.cpp` already handled `format` via `bb_resolve`. Pure gate fix.

### What was attempted but NOT landed (discarded via git stash drop)

**rung16 / rung40 / rung43 — ITE-cond-BUILTIN programs:**
Attempted to extend GZ admit for programs whose ITE cond is a bare BUILTIN (atom/1, @>/2, etc.) and add format/1 + type-test + ord-cmp BUILTIN pass-throughs to `pl_gz_build_goal`. Added `gz_fill_goal` IR_BUILTIN fix (`op_sval = g->sval` when `g->t == IR_BUILTIN`).

**Root problem unresolved:** `pl_gz_admit` still returns NULL for these programs even though the scan loop does NOT reject BUILTIN nodes. Added admission logic was functionally correct but the actual rejection site was not pinpointed before context ran out. Separately, an ITE-priority-before-gconj reorder in `goals_buf` construction caused a hard regression (m3 31→19), proving the ITE-as-entry fix only works safely when `gconj==NULL`.

### Root cause of ITE-builtin-cond reject — next session must diagnose

Add `fprintf(stderr, "DBG reject L%d\n", __LINE__)` to each `return NULL` inside the scan body of `pl_gz_admit` (lines 1004–1058 of `src/driver/scrip.c`). Run `./scrip --run /tmp/test_typetest.pl` where test_typetest.pl is:

```prolog
:- initialization(main).
main :- ( atom(hello) -> write(yes) ; write(no) ), nl.
```

The reject must be in the scan loop — the `goals_buf` logic was verified correct. Likely candidates:
- `ngconj >= 2` check firing because GCONJ[2] (the then/else-shared nl-chain gconj) counts as unclaimed, AND some other GCONJ is also unclaimed.
- Or the ITE-BUILTIN cond root's γ/ω (wired to ITE_COMMIT/ITE_GATE) is causing a node type in the graph to be rejected.

Once the exact line is found, fix ONLY that one check. Do NOT reorder the `goals_buf` gconj-vs-ITE priority.

### Gate state at 7f4b3db

GATE-1: 5/5 m2 HARD · 5/5 m3 · 5/5 m4
GATE-3: m2 115/115 HARD · m3 31/84-FAIL · m4 105/0/10-EXC
test_gate_pl_gz7: PASS
test_gate_bb_one_box: PASS
seg_byte/SL_B grep: 0 · g_vstack: 0

### Files changed in 7f4b3db

- `src/driver/scrip.c` — admission gates (flat + GZ): IR_LIT_F, const=const UNIFY, succ/2, plus/3, format/1, ITE-as-entry γ-chain walk
- `src/runtime/unification.c` — `rt_pl_unify_cell_float` added
- `src/emitter/BB_templates/bb_cell_unify.cpp` — float cell↔float arm; const=const LIT_F fold
