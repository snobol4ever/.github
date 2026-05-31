# HANDOFF 2026-05-28 — Opus 4.7 — PROLOG-BB: WAM-CP-10 catch/throw mode-2

**Goal:** GOAL-PROLOG-BB.md WAM-CP-10. Mode-2 catch/throw correctness landed end-to-end;
mode-4 native emit + longjmp-free CP-barrier unwind deferred to WAM-CP-13.

## State at handoff

- SCRIP HEAD `5427e12e`, tree clean, pushed to origin/main.
- .github HEAD `24d68528`, tree clean, pushed to origin/main.
- corpus untouched this session.

## What landed

### SCRIP `5427e12e` — WAM-CP-10 partial (mode-2)

* New BB node `BB_PL_CATCH` in `src/include/BB.h` + `bb_pl_catch_state_t {goal_g, catcher,
  rec_g}`. Goal and Recovery each lower into their own self-contained `BB_graph_t`;
  Catcher is a term-tree BB node in the OUTER graph so its vars share the surrounding
  clause's env.

* `src/lower/lower_pl.c` recognises `catch/3` (→ BB_PL_CATCH) and `throw/1` (→ BB_BUILTIN
  sval="throw" with ball term hanging off alpha) before the generic call fall-through.
  Both inserted right before the findall/3 block.

* `src/runtime/interp/pl_runtime.{h,c}` exposes the previously-static `Pl_CatchFrame` stack
  via public wrappers: `pl_catch_push` (returns `jmp_buf*` for caller to setjmp),
  `pl_catch_pop_top`, `pl_throw_term` (matches + longjmps, no return on match),
  `pl_catch_take_exception`, `pl_catch_top_trail_mark`, `pl_catch_top_env`.

* `src/lower/bb_exec.c` (added `#include <setjmp.h>`):
  - `BB_PL_CATCH` executor: setjmps the frame, runs `goal_g` via bb_exec_once;
    normal exit pops the frame and propagates goal's result;
    on longjmp(1) re-entry **restores g_pl_env** from the saved frame (CRITICAL — a throw
    originating in a sub-call leaves g_pl_env pointing at the inner callee env at longjmp
    time, so any BB_PL_VAR read in Recovery would otherwise index the wrong slot table),
    unwinds trail to the frame's mark, unifies Catcher with the exception, runs rec_g;
    rethrows via pl_throw_term up the chain if catcher does not match.
  - `BB_BUILTIN "throw"` arm before findall: materialises ball via pl_node_to_term and
    calls pl_throw_term.

* `src/emitter/BB_templates/bb_pl_catch.cpp` (new file, FACT-clean): mode-4 stub template
  — alpha: jmp omega, beta: jmp omega. Catch/3 in mode-4 always fails until WAM-CP-13.
  Every byte inside the template's _str() body; no shared producers.

* `src/emitter/emit_bb.c` + `src/emitter/emit_core.c`: BB_PL_CATCH dispatch to the stub
  template (walk_bb_flat uses EP_RESET/EP_JMP/EP_DEF_JMP/EP_FILL — template-pure routing).

* `src/emitter/BB_templates/bb_templates.h`: bb_pl_catch declaration.

* `Makefile`: bb_pl_catch.cpp added to source list + compilation rule (linked via OBJ/*.o).

### .github `24d68528` — Prolog BB documentation update

* GOAL-PROLOG-BB.md: HEAD bumped to `5427e12e`, GATE-3 mode-2 91→96, OPEN classes 16→11
  (rung28 closed), WAM-CP-10 marked partial in dependency tracker, full partial-completion
  paragraph documenting the new BB node, state struct, lowering, runtime wrappers,
  executor longjmp-arm env-restore fix, and mode-4 stub template. catch/3 + throw/1 added
  to mode-2-only list. 5427e12e added to Recent fixes (top-of-cycle).

* PLAN.md: Prolog BB row updated. NEXT pointer: WAM-CP-13 | WAM-CP-6 (LCO) |
  WAM-CP-9 Steps B-D.

## Gates at HEAD

| Gate                          | Baseline | After    | Δ           |
|---|---|---|---|
| GATE-1 smoke                  | 5/5      | 5/5      | =           |
| GATE-2 3-mode crosscheck      | 132/0    | 132/0    | =           |
| **GATE-3 mode-2 (--interp)**  | 91/107   | **96/107** | **+5** ✅ |
| GATE-4 mode-4 minimal         | 4/4      | 4/4      | =           |
| Full mode-4 corpus            | 54/107   | 54/107   | =           |
| FACT RULE grep                | 0        | 0        | clean       |
| **rung28 mode-2 (5 tests)**   | 0/5      | **5/5**  | **+5** ✅ |
| Sister smokes (icn/raku/sno/sc/rb) | green | green   | =           |

## Rebase note

Three concurrent commits landed during the session:
* `4ce8c385` (SCRIP) — MEDIUM_BINARY arms filled in 9 BOMB templates (Sonnet 4.6).
* `2e06b921` (.github) — ICON-BB DIAGNOSIS-only entry (param-shadowing diagnosis).
* `81a5f2f5` (.github) — SONNET BENCH-MODE3 blocker handoff.

All rebased cleanly. PLAN.md had one trivial conflict in the ICON-BB row (remote added
DIAGNOSIS-only paragraph). Resolved by keeping remote's ICON-BB row + my Prolog BB row.
Gates re-verified after rebase against `4ce8c385` — all still pass byte-identically.

## Design notes for whoever picks up next

1. **catch/3 lowering shape.** Goal_g + rec_g are SEPARATE sub-graphs (not part of the
   outer clause's BB_graph_t). They're run via `bb_exec_once` from the BB_PL_CATCH
   executor; bb_reset between calls is required (mirrors how findall handles its gcfg).
   Catcher lives in the OUTER graph because its vars share the surrounding clause's env —
   a fresh sub-graph would allocate fresh slots and unification wouldn't propagate.

2. **The g_pl_env restore on longjmp is load-bearing.** Initial implementation got 3/5
   rung28 (catch_atom_match + no_throw + throw_catch_atom) but failed on rethrow +
   throw_catch_compound. Both failures lost the bound `E` after `write(' ')`. Root cause:
   when `foo :- throw(...)` is called inside catch, BB_PL_CALL switched g_pl_env to foo's
   callee env. At longjmp time, g_pl_env still points at foo's env. Recovery's BB_PL_VAR
   reads then index the wrong slot table — even though unify(catcher, exc, ...) bound the
   outer E correctly via Term* indirection. Fix: pl_catch_top_env() helper returns the env
   captured at push time; BB_PL_CATCH restores g_pl_env from it BEFORE running rec_g.

3. **Why setjmp/longjmp instead of the original "no setjmp" plan.** The handoff doc for
   the prior session sketched CP-barrier longjmp-free unwind via templates. I delivered
   correctness (5/5 rung28) but kept setjmp because (a) the static Pl_CatchFrame
   infrastructure was already wired into pl_throw_iso_error and the legacy interp_exec
   path, (b) reusing it isolated the change to one new BB node + one runtime wrapper
   layer, (c) the "no setjmp" goal naturally pairs with mode-4 emit (which can't use
   setjmp from emitted code anyway) — both fold into WAM-CP-13. Honest framing in GOAL
   doc: "mode-2 correctness 5/5 via Pl_CatchFrame+setjmp; longjmp-free CP-barrier unwind
   deferred to WAM-CP-13 alongside mode-4 emit."

4. **Mode-4 stub.** bb_pl_catch.cpp emits α: jmp ω and β: jmp ω in TEXT mode; BOMB in
   BINARY mode. catch/3 reaching mode-4 always fails. WAM-CP-13 must implement: r12-based
   catch barrier push (mirroring WAM-CP-5's CP record), goal sub-graph emit (walking
   goal_g through walk_bb_flat recursively, like flat_drive_pl_ite does for then/else),
   recovery sub-graph emit, throw/1 mode-4 emit (currently bb_pl_builtin has no "throw"
   arm in MEDIUM_TEXT — needs adding when WAM-CP-13 lands, parallel to the bb_exec.c
   mode-2 BB_BUILTIN "throw" arm).

5. **Pre-existing mode-2 ALT redo bug** observed earlier in the session and noted in the
   prior turn but NOT addressed here: `(X=1 ; X=2 ; X=3), write(X), fail` loops on `1`
   instead of producing `1,2,3` in mode-2. Separate from WAM-CP-10. Would need its own
   small rung when picked up.

## NEXT session candidates (in rough order of impact / readiness)

1. **WAM-CP-13** — mode-4 catch + longjmp-free unwind. Direct continuation of this
   session. Reuses the WAM-CP-9 r12 + saved-state-slot pattern. Gate: rung28 mode-4
   0/5 → ≥3/5 mode-4. Bisectable: step 1 emit goal_g + rec_g sub-graphs in flat layout
   (FAIL-mode preserved); step 2 push CATCH barrier with r12; step 3 throw/1 mode-4 emit;
   step 4 retire setjmp from mode-2 in favor of the same path.

2. **WAM-CP-6 (LCO)** — principled SEGFAULT-CLUSTER fix. Mode-2 first. Gate:
   `count(0). count(N):-N>0,N1 is N-1,count(N1).` to 1e6 runs in O(1) stack.

3. **WAM-CP-9 Steps B–D** — committed-ITE node + disjunction-cut wiring. Folds in the
   pre-existing mode-2 ALT redo bug noted above.

## Verify-before-commit (already done)

- `bash scripts/build_scrip.sh` green (both before AND after rebase against 4ce8c385).
- `make libscrip_rt` green.
- GATE-1: `bash scripts/test_smoke_prolog.sh` → 5/5.
- GATE-2: `bash scripts/test_crosscheck_prolog.sh` → 132/0.
- GATE-3 mode-2: `bash scripts/test_prolog_rung_suite.sh` → 96/107 (+5).
- GATE-4 minimal: `bash scripts/test_prolog_mode4_rung.sh` → 4/4.
- Mode-4 corpus: 54/107 (unchanged — rung28 still fails in mode-4 by design).
- FACT grep: 0 violations in src/ outside *_templates/ and emit_core.c.
- Sister smokes: icn/raku/sno/sc/rb all green.

## Commit identity used

```
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
```

## Verification

```
cd /home/claude/SCRIP && git log origin/main --oneline -1
# 5427e12e WAM-CP-10: catch/throw mode-2 via BB_PL_CATCH + Pl_CatchFrame; rung28 0/5 -> 5/5

cd /home/claude/.github && git log origin/main --oneline -1
# 24d68528 Prolog BB: WAM-CP-10 partial — catch/throw mode-2 (rung28 0/5 -> 5/5)
```
