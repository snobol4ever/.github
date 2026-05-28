# HANDOFF 2026-05-28 — Opus 4.7 — RK-GIVEN-MODE4

**Goal:** GOAL-RAKU-BB.md — next rung after SM-FRAME-MODE4 (triage + fix one).
**Result:** ✅ Raku `given`/`when` now runs in mode-4 x86. GATE-RK4 18→19.
**Commit:** one4all `5950356f`. corpus unchanged. .github HEAD.

## Triage of the 15 mode-4 FAILs (from the real GATE-RK4 harness)

| Family | Tests | Disposition |
|---|---|---|
| Regex/NFA | rk_re32/33/34/35/37, rk_regex23 (6) | DEFER to GOAL-RAKU-PAT-BB (per goal doc) |
| **given/when** | rk_given, rk_given18 (2) | **this rung** |
| Hashes | rk_hash17, rk_hashes (2) | next candidate (self-contained) |
| Junctions | rk_junctions (1) | blocked on Lon Q9–Q12 |
| I/O | rk_fileio38, rk_stdio39 (2) | file handles, $*STDOUT |
| Exceptions | rk_try_catch25 (1) | try/CATCH/die |

Picked given/when: the goal doc framed it as "lowers to nested if-chain," and
the failure was a clean missing-template (`unhandled SM_PUMP_CASE`), the same
class as the SM_LOAD_FRAME gap fixed in the prior session.

## What landed (one file, +38/-7 in src/lower/lower.c)

The Raku `is_raku` branch of `lower_case` emitted `SM_PUMP_CASE` plus
`emit_thunk` deferred-subexpr entries. `SM_PUMP_CASE` has no x86 arm, and
implementing one would require the runtime to walk SM via `sm_eval_subexpr`
(forbidden in mode 4 per RULES.md "NO SM/BB WALKING AT RUNTIME").

Rewrote that branch to a straight if-chain over opcodes that already have
mode-4 templates (it mirrors the non-raku CASE branch directly above it):

- topic lowered once, stored to a **per-site-unique** temp
  `__rk_case_topic_<seq>__` (static counter). Unique-per-site is required so a
  nested `given` inside a `when` body does not clobber the outer topic.
- each non-default arm: `PUSH_VAR topic`; lower when-value; then
  `SM_ACOMP TT_EQ` for numeric values or `SM_LCOMP TT_LEQ` when the value is a
  string literal (`val->t == TT_QLIT`); `JUMP_F next`; body (walk if TT_PROGRAM,
  else expr+VOID_POP); `JUMP end`.
- default body last; trailing `SM_PUSH_NULL` keeps the value stack balanced for
  a call-as-statement `VOID_POP` (same contract as the non-raku branch).

`SM_PUMP_CASE` now has **zero emit sites** (the interp handler and the SM.h
enum entry remain, inert).

## Verification

- rk_given mode-4 == `.expected`: `Mon: weekday / Sat: weekend / weekday / hot
  / cold / unknown`. Also passes mode-2.
- Nested given (`given` inside `when`) and basic given verified in isolation.
- rk_given18 still FAILs — but NOT a given/when problem. It segfaults inside
  `in_loop()` on `my @vals = ''; push(@vals,N); for @vals -> $v { ... }`. The
  same for-over-pushed-array pattern segfaults with the `given` removed, and
  `test_case` in the SNOBOL4 broad corpus fails identically on a clean
  stash-rebuild. Pre-existing, orthogonal to this rung.

## Gates

| Gate | Before | After |
|---|---|---|
| GATE-RK4 mode-4 | 18/33 | **19/33** (+rk_given) |
| GATE-RK mode-2 | 18/33 | 18 HOLD |
| Smoke raku/icon/prolog/snobol4 | 5/5/5/13 | HOLD |
| Icon broker (test_icon_all_rungs) | 198 | 198 HOLD |
| Icon mode-4 | 5/5 | 5/5 HOLD |
| SNOBOL4 broad mode-4 | 175/280 | 175/280 (test_case pre-existing) |
| FACT RULE grep | 0 | 0 |
| Build | clean | clean |

## Next session

Best self-contained Raku rungs (no external directive needed):
1. **Fix the for-over-pushed-array segfault** — unblocks rk_given18 and likely
   several array tests; also clears SNOBOL4 `test_case`. Start from the
   minimal repro: `sub f(){ my @v=''; push(@v,1); push(@v,2); for @v -> $x { say($x); } } sub main(){ f(); }`.
2. **Hashes** (rk_hash17, rk_hashes) — `%h<k>`, keys/values/exists/delete.

Regex/NFA (6) deferred to GOAL-RAKU-PAT-BB. Junctions blocked on Lon Q9–Q12.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
