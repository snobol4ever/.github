# HANDOFF — 2026-05-27, Opus 4.7 — RK-BB-3b/c WIP (map/grep scaffold)

**Watermark:** one4all `42d2a367` · .github HEAD · corpus unchanged

## Goal

GOAL-RAKU-BB.md, ladder step RK-BB-3b/c. Lower lazy `map`/`grep`
onto the polymorphic BB_ITERATE substrate completed in RK-BB-3a.

## What landed

One commit: one4all `42d2a367` (was `8643abf1` pre-rebase) —
`src/lower/lower.c` +117 lines, pure lowering transform.

Implements `lower_raku_map_or_grep(t, is_grep)`:
- Synthesizes unique `__map_acc_N` / `__grep_acc_N` accumulator.
- Calls `lower_raku_iterate_arr` (RK-BB-3a) to build the BB graph.
- Emits `SM_BB_SWITCH(RK_GEN, bb_idx)`, `JUMP_F → exit`.
- γ body: stores yielded element into `$_`, then:
  - **map**: lowers body, pushes body result via the 3-arg push pattern.
  - **grep**: lowers predicate, `JUMP_F`-gates the push, pushes `$_`.
- `JUMP → switch_pc` for β-resume.
- Patches exit, stamps `a[0].i = exit_pos` for mode-4 ω routing.
- Leaves accumulator value on stack as the map/grep result.

TT_MAP / TT_GREP cases now try the BB path first; on fall-through
the legacy dead-code path (`SM_CALL_FN raku_map`/`raku_grep`) is
preserved (it's unreachable today — `icn_call_builtin` has zero
callers — but the source is untouched for non-regression).

## Verified

```
GATE-RK mode-2:  12/31 HOLD (no regressions)
Mode-3 (--run):  12/31 HOLD
GATE-RK4 mode-4: 13/31 HOLD
Smoke raku:      5/0  HOLD
Smoke icon:      5/5  HOLD
Smoke prolog:    5/5  HOLD
Broker Icon:     198  HOLD
FACT RULE grep:  0
Build:           clean
```

Scaffold structurally works on `rk_map_grep_sort24.raku` in all
three modes:
- BB_ITERATE fires per element.
- `push()` accumulates correctly.
- Final accumulator is read at the end.
- Sort (both string and numeric segments of the test) — GREEN.

## ⛔ Open blocker — `$_` binding bug

The body / predicate reads `$_` as **0 in every iteration**. So:
- `map { $_ * 2 } @nums` → emits `0\n0\n0\n0\n0\n` (expected `2\n4\n6\n8\n10\n`)
- `grep { $_ % 2 == 0 } @nums` → yields all of `@nums` (`1,2,3,4,5`),
  because `0 % 2 == 0` is always true.

Crucially this reproduces in **mode-2 `--interp` too**, which rules
out mode-4-specific codegen. The SM stream itself is somehow
emitting a mis-bound `$_`. Apart from this, the scaffold is sound.

### Hypotheses (ordered by plausibility, untested)

**(a) Implicit `$_` scope registration.** Some pre-lowering pass
(polyglot.c or proc-skeleton phase) may register `$_` into
`g_proc_scope` when it sees the TT_VAR in the body. If so,
`emit_var_store("$_")` correctly emits `SM_STORE_FRAME slot`, but
`lower_expr(body)` was likely tree-traversed BEFORE we emit the
store, so the load-side may resolve `$_` against the OUTER scope
(or against `slot=-1` if not registered yet). Recommended check:
print `scope_get(g_proc_scope, "$_")` at the entry of
`lower_raku_map_or_grep` and again right before `lower_expr(body)`.

**(b) Stack-order interaction with push pattern.** For map I emit:
```
SM_PUSH_LIT_S acc_vname    ; args[0] = mutator marker
SM_PUSH_VAR   acc_vname    ; args[1] = current acc value
lower_expr(body)           ; args[2] = body result   ← side-effects of $_ load may overlap
SM_CALL_FN    "push", 3
```
If `lower_expr(body)` consumes / mutates the stack across the
two earlier pushes — e.g., body lowering does PUSH_VAR `$_` which
goes through some indirect resolver — args could be misaligned.
Recommended check: dump the SM stream with `--sm-dump` (if such
flag exists; if not, add a printf in `SM_emit_*` for one run).
Inspect what `lower_expr($_ * 2)` actually emits when `$_` is in
the by-name table only.

**(c) Closure body tree_t* aliasing.** If the TT_MAP node's `c[0]`
(the body) was already walked once by gather-hoist or another pre-
pass and has stale internal state (e.g., `v.ival` slot indices set
from a prior context), re-lowering it inside the BB loop could read
the wrong slot.

### Recommended diagnostic path

1. Write a side-by-side hand-desugared probe:
   ```raku
   my @r = '';
   for @nums -> $_ { push(@r, $_ * 2); }
   for @r -> $x { say($x); }
   ```
   Verify this works in all modes. If it does, the bug is in HOW
   the BB scaffold differs from the for-loop+push pattern (which
   would point at (a) or (b)). If THIS also fails, then `$_` itself
   has issues independent of map/grep.

2. Add a `fprintf(stderr, "[$_ slot] ...")` probe in
   `emit_var_store("$_")` and `emit_var_load("$_")` to log the
   slot value when `$_` is the vname. Run both paths and diff.

3. If (a) is the cause: the fix is likely either (i) explicitly
   register `$_` in the scope at the entry of
   `lower_raku_map_or_grep` so both store and load see the same
   slot, or (ii) bypass the scope by always emitting
   `SM_STORE_VAR`/`SM_PUSH_VAR` for `$_` regardless of scope.

## NEXT (this rung)

**RK-BB-3b/c-binding-fix** — diagnose and fix the `$_` binding
bug. Once green, `rk_map_grep_sort24` likely flips all three modes
(+1 each gate at minimum: GATE-RK, GATE-RK4, mode-3).

## Then

- **RK-BB-3 close** — confirm `rk_map_grep_sort24` byte-exact;
  consider any sort-related followups (sort currently uses eager
  `raku_sort` SM_CALL_FN; per Open Q3 it stays eager).
- **RK-BB-4** — junctions `any`/`all`/`one`/`none`, infix `|`/`&`
  → `BB_ALTERNATE` with Bool-collapse on ω/γ. REUSE
  `bb_gen_alt.cpp`/`bb_alt.cpp`. New rung.
- Latent: segfault cluster (rk_subs, rk_interp, rk_try_catch25)
  unchanged; Open Q5 union-clobber proper fix unchanged.

## Doctrinal status

100% template/lowering emission preserved. No new BB kinds. No new
runtime helpers. The `$_` bug is fixable inside the lowering
(scope handling) without touching runtime — diagnosis just needed.

FACT RULE grep: 0 (no seg_byte, SL_B, sl_emit_one, emit_standard_blob).
PEERS RULE preserved (no new BB_t fields).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7
