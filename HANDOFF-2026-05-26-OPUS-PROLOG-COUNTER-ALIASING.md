# HANDOFF 2026-05-26 (Opus) — Prolog smoke 0/5 root-caused; fix needs a design decision

**Tree: CLEAN at `319b2b6e`. Nothing committed. All baseline gates green/unchanged.**
smoke_icon 5/5 · unified_broker 18 · icon_all_rungs 174 · prolog smoke 0/5 (pre-existing) ·
prolog_bb_honest 128/0/0.

This session diagnosed the long-standing **Prolog `--interp` produces empty output (smoke 0/5)**
failure to its root cause, attempted three fixes, and reverted all of them because each traded the
clean failure for an intermittent crash. The bug is real and the diagnosis is solid; the *fix*
requires a design decision (below) that should go to Lon, because the clean fix conflicts with the
GOLDEN BB rule (no new BB_t fields).

---

## Root cause (confirmed by trace)

Every Prolog program yields empty output because `:- initialization(main)` dispatches all the way
into `bb_exec_once` → `bb_exec_node(BB_PL_SEQ)`, where the SEQ executor immediately hits its
`if (!sq) return nd->ω;` guard (`bb_exec.c` ~1726) and silently fails. The aux-state pointer
(`bb_pl_seq_state_t *` holding the goal vector) read from `nd->counter` is **NULL at exec time.**

**Why NULL:** `bb_reset(cfg)` (`scrip_ir.c:58`) zeroes `nd->counter` for every node. The
2026-05-26d option-(b) work overloaded `counter` to carry **persistent compile-time aux pointers**
for `BB_PL_SEQ`, `BB_CHOICE`, `BB_PL_CALL`, `BB_PAT_ARBNO` (the goal/clause/arg vectors, stashed at
lower time via `nd->counter = (int64_t)(intptr_t)zs;` in `lower_pl.c` / `lower_pat_dcg.c`). The
`counter = 0` line in `bb_reset` predates that overload (it dates to `IR-RN-3 / 4a1fcc63`, the
original transient-runtime-counter semantics). So `bb_exec_once`'s first act — `bb_reset(cfg)` at
line 2020 — wipes the very vectors the executor needs. Prolog interp broke when option-(b) landed
(traces to `1c4e37c7`) and has been 0/5 since.

**This is the field-aliasing hazard the prior watermarks gestured at:** `counter` is simultaneously
(a) transient interpreter runtime state — set DURING exec, reset between runs (BB_PROC_GEN
`bb_exec.c:195`, BB_FIND_GEN `:1216`, lazily re-allocated and NULL-checked), and (b) a persistent
compile-time aux pointer — set at LOWER time, must survive reset (the four kinds above). One field,
two lifetimes.

---

## Fixes attempted, and why each was reverted

### Attempt 1 — `bb_reset` skips zeroing `counter` for the four aux kinds (keyed on `nd->t`)
Result: **smoke 0/5 → 5/5**, broker 18 → 22, snobol4 JIT interp 185 → 188, icon/sno smoke and
icon_all_rungs unchanged (no regression on those). BUT `rung10_programs_puzzles.pl` segfaulted
~30% of runs (parent: 0/30). REVERTED.

### Attempt 2 — also clear transient sub-fields of preserved aux (`zc->cs=NULL`, `BB_CHOICE.cur/mark`)
Rationale: the preserved aux structs mix compile-time vectors with per-activation transient state
(`bb_pl_call_state_t.cs` = live env/trail record). Clearing the transient part on reset.
Result: honest gate flakiness reduced but rung10 still ~crashed; deref of `nd->counter` as
`bb_pl_call_state_t*` is itself unsafe when counter holds a non-aux value. REVERTED.

### Attempt 3 — snapshot/restore around BB_PL_CALL recursive `bb_exec_once`, conditional on real recursion
Rationale & mechanism: BB_CALL (Icon) already guards recursion with
`bb_snapshot_state`/`bb_reset`/`bb_exec_once`/`bb_restore_state` (`bb_exec.c:218-223`), because a
recursive callee shares the same `BB_graph_t` and the inner reset corrupts the outer activation.
BB_PL_CALL (`bb_exec.c:1890`) does NOT snapshot. Added an active-cfg stack (`pl_cfg_is_active`) so
snapshot/restore fires ONLY on true recursion (callee graph already on the exec stack) — because a
NON-recursive Prolog call must stay *resumable* (its BB_CHOICE cursor / `cs` must persist for the
SEQ backtrack pump), so unconditional restore breaks multi-solution backtracking (the `clause`
smoke regressed to printing only `a`).
Result with conditional snapshot: smoke back to **5/5**, valid deep recursion
(`count(50)`+`nrev`+`append`) **0/25 crashes** — the recursion fix is correct for real programs.
BUT rung10 STILL crashed ~7-20/30. REVERTED.

### Why rung10 keeps crashing regardless of the recursion guard
`rung10_programs_puzzles.pl` has a **pre-existing parse error at line 187** (`expected . at end of
fact` — confirmed at parent too; the corpus file is truncated/malformed). It NEVER executes and
NEVER contributed to any PASS count (the honest gate skips it: `[ $ir_rc -ne 0 ] && continue`). The
crash prints the parse-error message FIRST, then segfaults during teardown of the partially-built
graph. So the crash is NOT the recursion-corruption — it is that **preserving `counter` by node
type is unsound on a partial/aborted graph**: a node with `t==BB_PL_CALL/CHOICE/...` may have
`counter` holding garbage or a stale transient value (not a valid aux pointer) in a graph that was
never fully lowered, and any later code that treats counter-as-aux-pointer (or the preserved value
surviving into teardown) derefs bad memory. Type alone does not tell you whether `counter`
currently holds the aux pointer or transient state — that's the unsound core of all three attempts.

---

## The design decision needed (for Lon)

The clean fix is to **stop aliasing two lifetimes into one field.** Options:

- **(A) Restore a dedicated field.** Give the four aux kinds a separate slot for the compile-time
  aux pointer (e.g. reuse `ival`/`dval` bit-casts, or a small union) so `counter` stays purely
  transient and `bb_reset` can keep zeroing it. ⛔ GOLDEN BB rule currently forbids adding
  fields / `opaque`. Needs Lon's ruling on whether a bit-cast into existing `ival`/`dval`
  (which ARE "compile-time IR payload" per BB.h) is acceptable for the aux pointer. This is the
  cleanest and matches the field's documented purpose.

- **(B) Side table.** Store the aux pointers in a `cfg`-level side table indexed by node, untouched
  by `bb_reset`. Survives reset, no struct change, no teardown aliasing (teardown frees the table
  wholesale, GC-managed). Slightly more plumbing.

- **(C) Re-derive lazily like PROC_GEN/FIND_GEN.** Have the executor rebuild the aux vector on
  first touch from a stable source. Problem: the goal/clause/arg vectors come from the parse tree,
  which mode-2/3 may not retain — likely not viable without re-lowering.

Recommendation: **(A) via `ival`/`dval` bit-cast** if Lon permits (BB.h already calls these
"compile-time IR payload"; an aux pointer is compile-time payload), else **(B)**.

Once disambiguated, the recursion guard from Attempt 3 (active-cfg stack + conditional
snapshot/restore in BB_PL_CALL) is independently correct and SHOULD be re-added — it's needed for
deep Prolog recursion regardless of the counter fix, and it does not regress backtracking.

---

## Verified facts to build on next session
- Prolog AST/lowering is correct: `--dump-ast` shows `(TT_CHOICE main/0 (TT_CLAUSE ...))`;
  `lower_pl_predicate` returns a valid graph; `pl_bb_register`/`pl_bb_lookup` match on `main/0`;
  `bb_graph_of_pred` returns the right graph (`bb_idx=0`, `sm.bb_count=1`). The ONLY break is the
  `counter` wipe.
- `bb_snapshot_state`/`bb_restore_state` save/restore `value`+`counter`+`state` — usable as-is.
- The Attempt-3 recursion guard fixed valid deep recursion (count(50)+nrev+append: 0/25 crashes)
  and kept backtracking correct (clause smoke 5/5).
- `nrev`/`append` style programs hit a SEPARATE pre-existing gap: `[NO-AST] SM_BB_ONCE_PROC stub`
  for some predicate-call shapes — independent of this bug, worth a look after.

## Separately discovered (raised with Lon): the "honest gate" is now a no-op
`SCRIP_NO_AST_WALK=1` is **not read by any C code** (grep-verified). The `NO_AST_WALK_GUARD` macro
(`icn_runtime.c:18`) is a relic of the era when the AST walker still existed in the binary; mode 1
(`interp_exec.c`) was physically deleted at CLI-3M-9, so there is nothing left to "cheat" to. The
GOAL-ICON-BB "Done when #3" (`SCRIP_NO_AST_WALK=1 ./scrip == ./scrip`) is tautologically satisfied
and should be struck. Candidate cleanup ("grand master reorg"): retire the dead env var, the guard
macro, and the "honest/plain" language — BUT first confirm `g_ast_pump_active` (live in the
`SM_BB_PUMP_PROC` path, `sm_interp.c:625`) is not load-bearing beyond the tripwire; assess the
guard and those globals separately.
