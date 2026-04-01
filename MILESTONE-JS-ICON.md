# MILESTONE-JS-ICON.md — Icon × JavaScript Milestone Ladder

**Session:** IJJ · **Oracle:** `emit_wasm_icon.c` (IR switch) + `emit_jvm_icon.c` (Byrd wiring)
**Invariant cell:** `icon_js` (added at M-IJJ-A01)
**Emit-diff gate:** 981/4 throughout

---

## Dependency answer: SNOBOL4 JS runtime first

Icon JS **depends on** M-SJ-A01 (scaffold + runtime). The `sno_runtime.js`
provides the trampoline engine and base types that Icon JS extends.
Icon-specific: generators via `function*` OR trampoline continuations.
Recommendation: use trampoline (consistent with other backends, no
generator frame overhead for deeply nested expressions).

---

## Phase A — Foundation

### M-IJJ-A01 — Scaffold + hello/arith parity

**Depends on:** M-SJ-A01 (shared trampoline engine)
**Scope:**
- Create `src/backend/emit_js_icon.c` — mirrors `emit_wasm_icon.c` IR switch
- `icon_runtime.js` extending `sno_runtime.js`: `_icon_fail`, `_icon_succ`
- Handle: literals, arithmetic, string ops, `E_ASSIGN`, `E_VAR`
- OUTPUT: `write()` procedure

**Gate:** `icon_js` cell: hello/arith pass · emit-diff 981/4 ✅

---

### M-IJJ-A02 — Goal-directed: E_TO, E_GENALT, numeric relational

**Depends on:** M-IJJ-A01
**Scope:**
- `E_TO`: `i to j` — trampoline state machine with `_to_i` counter
  (Proebsting §4.4 template directly)
- `E_GENALT` (`|` alternation): `_alt_i` counter routing
- `E_LT/E_LE/E_GT/E_GE/E_EQ/E_NE` — numeric relational (goal-directed:
  succeed yielding rhs if condition holds, else ω)
- `E_EVERY` drive-to-exhaustion loop

**Gate:** `(1 to 5)` · `(1 to 3) * (1 to 2)` · `5 > ((1 to 2)*(3 to 4))`
match Proebsting Figure 2 optimized output · emit-diff 981/4 ✅

---

### M-IJJ-A03 — Suspension: E_SUSPEND, co-expressions

**Depends on:** M-IJJ-A02
**Scope:**
- `E_SUSPEND` (`@` — suspend/yield from procedure)
- `create expr` co-expression constructor
- `@coexpr` activation — swap continuation

**Gate:** rung03_suspend tests pass · emit-diff 981/4 ✅

---

## Phase B — String Scanning and Structures

### M-IJJ-B01 — String scanning: E_MATCH / E_SCAN_AUGOP

**Depends on:** M-IJJ-A03
**Scope:**
- `E_MATCH` (`subject ? pattern`) — Icon scanning
- `E_SCAN_AUGOP` augmented scan
- String positional functions: `pos()`, `move()`, `tab()`, `many()`, `upto()`

**Gate:** icon string scanning tests pass · emit-diff 981/4 ✅

---

### M-IJJ-B02 — Structures: lists, records, E_MAKELIST, E_FIELD

**Depends on:** M-IJJ-B01
**Scope:**
- `E_MAKELIST` `[e1,e2,...]` → JS array
- `E_RECORD` declaration → JS class
- `E_FIELD` `.name` → property access
- `E_ITER` `!E` — iterate list/string elements
- `E_SECTION` `E[i:j]` string/list section

**Gate:** icon structure tests pass · emit-diff 981/4 ✅

---

### M-IJJ-PARITY — Full corpus parity

**Depends on:** M-IJJ-B02
**Gate:** `icon_js` ≥ `icon_x86` pass count · emit-diff 981/4 ✅

---

*MILESTONE-JS-ICON.md — created IJJ-1, 2026-03-31, Claude Sonnet 4.6.*
