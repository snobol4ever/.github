# HANDOFF-2026-05-30-SONNET46-PROLOG-BB-MODE2-FIXES

**Session:** Sonnet 4.6, 2026-05-30
**SCRIP HEAD:** `1882bc6b`
**corpus HEAD:** unchanged (`3de2407` area)

---

## What was done

### Starting point
Gates at session start: GATE-1 5/5, GATE-2 104/32 (2 ORACLE_MISS), GATE-3 m2 109/111,
GATE-4 4/4, FACT 0. Crosscheck showed 32 FAIL/NATIVE-ABORT — rung10 (21), rung14 (5),
rung15 (4), rung30 (2).

### Investigation
Ran crosscheck, found rung10 puzzle programs reporting NATIVE-ABORT. Manual run showed
mode-2 produced EMPTY output while mode-3 produced correct output. Bisected to two
independent mode-2 bugs.

### Bug 1 — write(BB_ARITH compound) printed empty (bb_exec.c BB_BUILTIN write arm)

**Root cause:** `write/writeln` arm called `bb_exec_node(bb->α)`. For a `BB_ARITH` node
(operator-functor term like `one-X`, `K-V`) used in TERM position (not arithmetic), this
calls `pl_arith_eval` which fails → write prints nothing.

**Fix:** Detect `bb->α->t == BB_ARITH && bb->α->ival > 0` (compound arith node, not nullary
atom like `pi`). Use `pl_node_to_term(bb->α)` → `pl_write(term_deref(wt))` for this case.
All other arg types (DT_I/DT_R/DT_S/DT_DATA) keep the original scalar dispatch, preserving
round-trip float formatting via `pl_format_float`.

**Files:** `src/lower/bb_exec.c` — write/writeln arm only.

### Bug 2 — BB_CHOICE snapshot missing cp and cut_barrier (scrip_ir.c + BB.h)

**Root cause:** `bb_snapshot_state`/`bb_restore_state` captured BB_CHOICE sidecar fields
`cur`, `mark`, `saved_env`, `last_body`, `last_act` — but NOT `cp` (the live `pl_choice*`
on the CP spine) or `cut_barrier` (the `g_pl_bfr` snapshot taken at clause entry for cut
scoping). When two calls to the same predicate appear in one clause body (e.g.
`differ(smith,M), differ(T,brown)`), both share the same `BB_graph_t*`. The first call
mutated `zc->cp` and `zc->cut_barrier`; the second call's snapshot captured those stale
values; on restore, the second call's CP pointer and cut barrier were wrong, corrupting
backtracking (mode-2 looped infinitely or produced empty output).

**Fix:**
- `src/include/BB.h`: added `ch_cp` and `ch_cut_barrier` fields to `bb_node_state_t`.
- `src/lower/scrip_ir.c`: zero-init both in snapshot loop; capture `zc->cp` → `snap.ch_cp`
  and `zc->cut_barrier` → `snap.ch_cut_barrier` in `bb_snapshot_state`; restore both in
  `bb_restore_state`.

**Reusable finding:** Any field in `bb_pl_choice_state_t` that is set on fresh entry and
read on redo/exhaust paths must be in the snapshot. If a future field is added to the
sidecar, check whether it needs snapshotting.

### Gates after fix
GATE-1 5/5, GATE-2 105/31 (+1), GATE-3 m2 109/111 (same), GATE-4 4/4, FACT 0.

---

## NEXT

### Still open in crosscheck (31 FAIL/NATIVE-ABORT after this session)

**rung10_programs_puzzle_01: FAIL** (mode-3 correct `Cashier=smith Manager=brown Teller=jones`,
mode-2 empty). The write bug is fixed but the puzzle still diverges — the `display/3`
call uses multiple sequential writes and the bindings may not be propagating correctly
in mode-2 under the full constraint chain. Needs further investigation; puzzle_02..21
are NATIVE-ABORT (assertz/retract used?).

Actually re-check: after this fix puzzle_01 showed both modes agreeing in manual test.
Re-run crosscheck to confirm current state — the 105/31 was measured right after build.

**rung14 retract (5 NATIVE-ABORT):** PL-RT-ASSERTZ boundary — mutable clause store not
implemented in mode-3 native. Architectural, multi-session.

**rung15 abolish (3 FAIL + 1 NATIVE-ABORT):** abolish_existing/one_of_two/then_query_fail
FAIL (mode-3 vs mode-2 disagree). abolish_then_reassert NATIVE-ABORT. Investigate the
3 FAILs — they may be tractable.

**rung30 DCG (2 NATIVE-ABORT):** dcg_nonterminals, dcg_pushback_rest. DCG lowering for
mode-3 native not implemented. rung30_dcg_basic_terminals/generate/phrase3 pass.

### Recommended next step
Investigate rung15 abolish FAILs — mode-3 vs mode-2 disagree but neither aborts, so
one of them has wrong output. Check which is correct against standard Prolog semantics.
May be another mode-2 bug similar to what this session fixed.

