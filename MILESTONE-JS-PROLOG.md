# MILESTONE-JS-PROLOG.md — Prolog × JavaScript Milestone Ladder

**Session:** PJJ · **Oracle:** `emit_wasm_prolog.c` (IR switch) + `emit_jvm_prolog.c` (Byrd wiring)
**Invariant cell:** `prolog_js` (added at M-PJJ-A01)
**Emit-diff gate:** 981/4 throughout

---

## Dependency answer: SNOBOL4 JS runtime first, then Icon JS optional

Prolog JS **depends on** M-SJ-A01 (trampoline engine). It does NOT depend
on Icon JS. Prolog uses continuation-passing style for unification and
backtracking — different from Icon's generator model, same trampoline engine.

Each Prolog clause becomes a trampoline block. The choice point (E_CHOICE)
becomes a chain of α/β functions — try first clause on α, second clause on
β, etc. E_CUT seals the β chain.

---

## Phase A — Foundation

### M-PJJ-A01 — Scaffold + hello/facts/unify parity

**Depends on:** M-SJ-A01 (shared trampoline engine)
**Scope:**
- Create `src/backend/emit_js_prolog.c` — mirrors `emit_wasm_prolog.c` IR switch
- `prolog_runtime.js`: term representation, `_unify(t1,t2,trail)`,
  trail stack, undo trail on backtrack
- Handle: atoms, integers, `E_UNIFY`, `E_CLAUSE`, `E_CHOICE` (single clause)
- Simple facts: `foo(a). foo(b).` → two block functions chained via `E_CHOICE`

**Gate:** `prolog_js` cell: hello/atom/fact pass · emit-diff 981/4 ✅

---

### M-PJJ-A02 — Multi-clause predicates + backtracking

**Depends on:** M-PJJ-A01
**Scope:**
- `E_CHOICE` α/β chain across N clauses
- Trail unwind on β: `_trail_unwind(mark)` restores variable bindings
- `E_TRAIL_MARK` / `E_TRAIL_UNWIND` wiring
- Variable terms: unbound var → JS object `{ref: null}`, bound → `{ref: term}`
- Tests: `member/2`, `append/3`

**Gate:** rung multi-clause backtrack tests pass · emit-diff 981/4 ✅

---

### M-PJJ-A03 — Arithmetic: E_FNC(is), comparison

**Depends on:** M-PJJ-A02
**Scope:**
- `is/2` — evaluate arithmetic expression, unify with lhs
- Numeric comparison: `</2`, `>/2`, `=:=/2`, `=\=/2`
- `E_FNC` dispatch for Prolog builtins

**Gate:** Prolog arithmetic tests pass · emit-diff 981/4 ✅

---

## Phase B — Lists and Control

### M-PJJ-B01 — Lists: `[H|T]` unification, list builtins

**Depends on:** M-PJJ-A03
**Scope:**
- List term: `[H|T]` → JS `{head, tail}` cons cell
- Unification over cons cells (recursive)
- `length/2`, `member/2`, `append/3` corpus tests

**Gate:** Prolog list tests pass · emit-diff 981/4 ✅

---

### M-PJJ-B02 — Cut, negation-as-failure

**Depends on:** M-PJJ-B01
**Scope:**
- `E_CUT` — seal β of enclosing `E_CHOICE` (trampoline: null out retry fn)
- `\+` negation-as-failure — try goal, succeed if it fails, fail if it succeeds
- `once/1`

**Gate:** cut/negation tests pass · emit-diff 981/4 ✅

---

### M-PJJ-B03 — assert/retract (dynamic predicates)

**Depends on:** M-PJJ-B02
**Scope:**
- `assert(Clause)` → add to JS predicate table at runtime
- `retract(Clause)` → remove from table
- Predicate table: JS `Map` from functor/arity to clause list
- This is Prolog's analog of SNOBOL4's `CODE()` — runtime clause addition

**Gate:** assert/retract tests pass · emit-diff 981/4 ✅

---

### M-PJJ-PARITY — Full corpus parity

**Depends on:** M-PJJ-B03
**Gate:** `prolog_js` ≥ `prolog_x86` pass count · emit-diff 981/4 ✅

---

*MILESTONE-JS-PROLOG.md — created PJJ-1, 2026-03-31, Claude Sonnet 4.6.*
