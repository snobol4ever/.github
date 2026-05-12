# GOAL-PROLOG-BB-COMPLETE.md — All Prolog Byrd-Box constructs in modes 1/2/3 (then 4)

**Repo:** one4all + .github
**Sister docs:** `GOAL-LANG-PROLOG.md`, `GOAL-CHUNKS.md`
**Carved:** 2026-05-12

**Done when:**
1. Every AST kind reachable from a `--ir-run` PASS Prolog program lowers via `lower.c` to pure SM — no `emit_push_expr + SM_BB_ONCE` / `SM_BB_PUMP_AST` legacy fallthrough fires. Legacy block physically deleted.
2. `--ir-emit` byte-identical to pre-rung baseline for every corpus program.
3. `SCRIP_NO_AST_WALK=1 ./scrip --sm-run` == `./scrip --ir-run` for every program in the `--ir-run` PASS set (the *honest* gate).
4. Every SM opcode emitted by Prolog lowering has a `sm_codegen_x64` mirror.
5. Prolog `is_suspendable` / `coro_eval` not reachable from SM dispatch under `SCRIP_NO_AST_WALK=1`.

⛔ **"Cheating":** `--sm-run` silently calls `coro_eval` for un-migrated kinds. `SCRIP_NO_AST_WALK=1` aborts on this. Output equality alone is not sufficient.

---

## Architecture

```
.pl → prolog_parse() → PlClause* → prolog_lower() → AST_t*
  --ir-emit  → ir_print_program()                        Mode 1
  --ir-run   → execute_program() → interp_eval()         Mode 2  (AST walker)
  --sm-run   → lower() → SM_Program → sm_interp_run()   Mode 3
  --jit-run  → lower() → sm_codegen_x64() → run         Mode 3.5
  --jit-emit → lower() → sm_codegen_x64() → binary      Mode 4
```

Prolog lowering in `prolog_lower.c` transforms parsed clauses into:
- One `TT_CHOICE` node per predicate (OR-box over all clauses)
- Each `TT_CLAUSE` child: head unification args + body goals, wrapped in `TT_TRAIL_MARK` / `TT_TRAIL_UNWIND`
- Body goals: `TT_UNIFY` (=/2), `TT_CUT` (!), `TT_CHOICE` (recursive calls), `TT_CLAUSE` (clause body)

Current SM opcode repertoire for Prolog:
- `SM_BB_ONCE_PROC` — named predicate call (lower_choice fast path ✅)
- `SM_BB_ONCE` — pop bb_node_t* + drive once (used with AST-pump ⛔)
- `SM_BB_PUMP_AST` — fallthrough for TT_CLAUSE/TT_CUT/TT_UNIFY/TT_TRAIL_* ⛔

JCON reference: n/a (JCON is Icon-only). Prolog reference implementation:
`src/frontend/prolog/pl_broker.c` — `pl_box_choice`, `pl_box_clause`, `pl_box_cut`, `pl_box_unify`.

---

## Session Setup

```bash
cd /home/claude/one4all
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
bash scripts/build_spitbol_oracle.sh
```

Baseline gates (all green before picking up next rung):
```bash
bash scripts/test_smoke_icon.sh                          # PASS=5
bash scripts/test_smoke_unified_broker.sh                # PASS=10 (pre-existing Icon failures)
bash scripts/test_prolog_bb_honest.sh                    # honest dial (31 at carve 2026-05-12)
```

⚠️ `test_prolog_bb_honest.sh` must be created at PB-0 (see below). Until then, run manually:
```bash
for f in $(find /home/claude/corpus/programs/prolog/rung* -name "*.pl" -o -name "*.s"); do
  base="${f%.*}"; exp="$base.expected"; [ -f "$exp" ] || exp="$base.ref"; [ -f "$exp" ] || continue
  want=$(cat "$exp")
  got=$(SCRIP_NO_AST_WALK=1 timeout 5 ./scrip --sm-run "$f" 2>/dev/null)
  [ "$got" = "$want" ] && echo "PASS: $(basename $f)" || true
done | wc -l
```

---

## Honest-mode-3 protocol

A rung is **honestly complete** iff:
(a) output matches `--ir-run` for all targeted programs,
(b) passes under `SCRIP_NO_AST_WALK=1 --sm-run`,
(c) no `SM_BB_PUMP_AST` fires for the migrated kind corpus-wide,
(d) smokes unchanged,
(e) ≥1 program flipped from FAIL→honest PASS.

---

## Prolog AST kinds requiring migration

All currently fall through to `lower_prolog_child` (emit_push_expr + SM_BB_ONCE ⛔)
or `lower_choice` unnamed arm (emit_push_expr + SM_BB_ONCE ⛔):

| Kind | Current handler | Migration target |
|------|----------------|-----------------|
| `TT_CHOICE` (named) | `SM_BB_ONCE_PROC` ✅ | already honest |
| `TT_CHOICE` (unnamed/dynamic) | `emit_push_expr + SM_BB_ONCE` ⛔ | `SM_BB_ONCE_PROC` via dynamic lookup |
| `TT_CLAUSE` | `emit_push_expr + SM_BB_ONCE` ⛔ | inline head-unify + body SM sequence |
| `TT_UNIFY` (=/2) | `emit_push_expr + SM_BB_ONCE` ⛔ | `SM_CALL_FN "PL_UNIFY" 2` |
| `TT_CUT` | `emit_push_expr + SM_BB_ONCE` ⛔ | `SM_CALL_FN "PL_CUT" 0` |
| `TT_TRAIL_MARK` | `emit_push_expr + SM_BB_ONCE` ⛔ | `SM_CALL_FN "PL_TRAIL_MARK" 0` |
| `TT_TRAIL_UNWIND` | `emit_push_expr + SM_BB_ONCE` ⛔ | `SM_CALL_FN "PL_TRAIL_UNWIND" 0` |

---

## Phase A — drain legacy fallthrough (one AST kind per rung)

#### PB-0 — tripwire + test script
- [x] Add `test_prolog_bb_honest.sh` script (mirrors `test_icon_sm_no_ast_walk.sh`).
- [x] Baseline: run and record honest dial count (17 at carve 2026-05-12 via --ir-run oracle; PLAN.md estimated 31 via .expected files).
- [x] Files: `scripts/test_prolog_bb_honest.sh`

#### PB-1 — TT_UNIFY (=/2)
- [x] Add `SM_CALL_FN "PL_UNIFY" 0` handler in `sm_interp.c` — pops DT_E tree_t*, calls `pl_unified_term_from_expr` on both children with `g_pl_env`, then `unify()`. No coro_eval.
- [x] In `lower.c`: split `TT_UNIFY` from `lower_prolog_child` fallthrough → `emit_push_expr(t)` + `SM_CALL_FN "PL_UNIFY" 0`.
- [x] Gate: honest dial 17 (unchanged — TT_UNIFY programs also need TT_CLAUSE+TT_TRAIL migrated; no regression). Smoke PASS=1 FAIL=4 pre-existing.
- [x] Files: `src/runtime/x86/sm_interp.c`, `src/runtime/x86/lower.c`

#### PB-2 — TT_CUT (!)
- [x] Add `SM_CALL_FN "PL_CUT" 0` handler in `sm_interp.c` — pops DT_E (ignored), sets `g_pl_cut_flag=1`, succeeds.
- [x] In `lower.c`: `TT_CUT` → `emit_push_expr(t)` + `SM_CALL_FN "PL_CUT" 0`.
- [x] Gate: no regression. Honest dial unchanged (TT_CLAUSE still blocked).
- [x] Files: `sm_interp.c`, `lower.c`

#### PB-3 — TT_TRAIL_MARK / TT_TRAIL_UNWIND
- [x] Add `SM_CALL_FN "PL_TRAIL_MARK" 0` and `SM_CALL_FN "PL_TRAIL_UNWIND" 0` handlers in `sm_interp.c`.
- [x] In `lower.c`: wire `TT_TRAIL_MARK` → `PL_TRAIL_MARK`, `TT_TRAIL_UNWIND` → `PL_TRAIL_UNWIND`.
- [x] NOTE: `prolog_lower.c` does not yet emit TT_TRAIL_MARK/UNWIND nodes. They are planned sentinels; trail management is currently inside `pl_box_choice`/`pl_box_clause` in the broker. Wiring is correct prep; nodes activate when PB-4 emits them.
- [x] Gate: no regression.
- [x] Files: `sm_interp.c`, `lower.c`

#### PB-4 — LANG_PL stmt lowering fix (initialization + assertz/asserta)
- [x] Suppress `:- initialization(Goal)` directive in SM (TT_CHOICE stmt for `Goal/0` already calls it, preventing double-call).
- [x] Route other TT_FNC directives (assertz/asserta/retract/abolish) via `emit_push_expr + SM_CALL_FN "PL_BUILTIN" 0`.
- [x] Add `PL_BUILTIN` handler in `sm_interp.c`: pops DT_E tree_t*, calls `interp_exec_pl_builtin(goal, g_pl_env)`.
- [x] Gate: honest dial 17 → **105** (+88). No smoke regression.
- [x] Files: `src/runtime/x86/lower.c`, `src/runtime/x86/sm_interp.c`

#### PB-5 — TT_CHOICE stmt arity=0 fix
- [x] `emit_prolog_call_arity0()`: calls `SM_BB_ONCE_PROC` with arity=0 for Pass 3 TT_CHOICE stmts, matching IR semantics (IR calls `pl_box_choice` with arity=0 for all stmts).
- [x] Gate: honest dial 105 → **106**. Remaining 14 FAIL are rung10 puzzle programs (proper head unification needs PB-6). Smoke unchanged.
- [x] Files: `src/runtime/x86/lower.c`

#### PB-6 — TT_CHOICE full inline (OR-box via BB broker, not SM coroutine)
- [ ] **Architecture note (corrected from carve):** PB-6 is NOT an SM coroutine. The correct target is BB-land: `SM_BB_ONCE_PROC` already calls `pl_box_choice` → `bb_broker` → `pl_box_clause` for each clause. The 14 remaining FAIL (rung10 puzzles) fail because `interp_exec_pl_builtin` inside `pl_box_goal_from_ir` doesn't properly bind clause variables when calling user predicates like `person(X)`. Fix: ensure `g_pl_env` (the clause cenv) is properly passed as the env for nested `is_pl_user_call` goals inside `interp_exec_pl_builtin`.
- [ ] Probe: in `pl_runtime.c` `interp_exec_pl_builtin`, the `is_pl_user_call` branch allocates `uenv` for the callee but uses `env` (the caller's env) to evaluate goal arg expressions. Verify `env` is the clause's `cenv` not NULL when called from `pl_box_goal_from_ir`.
- [ ] Gate: ≥1 of the 14 rung10 puzzle programs flips to honest PASS; ABORT still 0.
- [ ] Files: `src/runtime/interp/pl_runtime.c` (reference only — do not modify if fix is in broker), `src/frontend/prolog/pl_broker.c`

#### PB-7 — fallthrough delete
- [ ] After PB-1–PB-6: remove `lower_prolog_child` legacy path, replace with `abort()`.
- [ ] Gate: zero `SM_BB_ONCE` / `SM_BB_PUMP_AST` fires on any Prolog corpus program.

---

## Phase B — sm_codegen_x64 mirrors

For each new `SM_CALL_FN` handler added in Phase A, add a JIT mirror in `sm_codegen.c` so `--jit-run` matches `--sm-run`.

- [ ] **B1** `PL_UNIFY` JIT mirror
- [ ] **B2** `PL_CUT` JIT mirror
- [ ] **B3** `PL_TRAIL_MARK` / `PL_TRAIL_UNWIND` JIT mirrors
- [ ] **B4** `PL_CHOICE_DYNAMIC` JIT mirror
- [ ] **B5** clause-inline shape in JIT

---

## Active next targets (honest dial: 106/294 at sess 2026-05-12, one4all 695aed00)

**Architecture confirmed correct — this is NOT the Icon off-rails problem:**
- `SM_BB_ONCE_PROC` → `pl_box_choice` → `bb_broker` → pure BB-land ✅
- PB-6 spec corrected: do NOT build SM coroutines (SM_GEN_TICK etc.) for Prolog
- ABORT=0: no coro_eval reached from SM dispatch ✅

Remaining 14 FAIL: all rung10 puzzle programs. `puzzle` calls `person(X)` etc. inside
clause body via `interp_exec_pl_builtin` / `pl_box_goal_from_ir`. Bug: nested user
predicate calls don't properly bind clause variables (X gets slot-index integer, not atom).
Fix target: `g_pl_env` / cenv threading in `pl_box_goal_from_ir` for `is_pl_user_call`
goals — ensure callee sees caller's cenv for arg evaluation.

**NEXT: PB-6** — fix cenv threading in `pl_box_goal_from_ir` for nested user predicate
calls. BB-land fix (pl_broker.c / pl_runtime.c), NOT SM coroutines.

---

## Invariants

1. Mode 1 (`--ir-emit`) byte-identical at every rung.
2. Prolog `--ir-run` corpus PASS count stable until PB-6 (clause inline may shift).
3. No `tree_t*` in SM bytecode — ONCE/PUMP opcodes take integer registry IDs.
4. Fallthrough delete (PB-7) is one-way.
5. Trail mark/unwind must bracket every clause arm — never omit.

---

## Closed rungs

| Rung | Commit | Honest gain | Notes |
|------|--------|-------------|-------|
| (carve baseline) | — | 17 honest | TT_CHOICE named → SM_BB_ONCE_PROC already migrated |
| PB-0 | f63a07cd | 17 | test_prolog_bb_honest.sh; baseline 17 (not 31) |
| PB-1 | f63a07cd | 17 | TT_UNIFY → PL_UNIFY SM_CALL_FN |
| PB-2 | e765733c | 17 | TT_CUT → PL_CUT SM_CALL_FN |
| PB-3 | e765733c | 17 | TT_TRAIL_* → PL_TRAIL_* SM_CALL_FN (infra) |
| PB-4 | 1af5368e | **105** | initialization suppressed; assertz/asserta → PL_BUILTIN. +88. |
| PB-5 | 695aed00 | **106** | TT_CHOICE stmt calls arity=0 (matches IR). +1. |

---

## File ownership

| Path | Touches? |
|------|----------|
| `src/runtime/x86/lower.c` | Yes (every rung) |
| `src/runtime/x86/sm_interp.c` | Yes (PL_UNIFY / PL_CUT / PL_TRAIL / PL_CHOICE_DYNAMIC) |
| `src/runtime/x86/sm_codegen.c` | Yes (Phase B JIT mirrors) |
| `src/frontend/prolog/pl_broker.c` | Reference only — do not modify |
| `src/frontend/prolog/pl_runtime.c` | Reference only — do not modify |
| `scripts/test_prolog_bb_honest.sh` | New (PB-0) |
