# MILESTONE-JS-SNOBOL4.md — SNOBOL4 × JavaScript Milestone Ladder

**Session:** SJ · **Oracle:** `emit_byrd_c.c` · **Trampoline:** `trampoline.h`
**Invariant cell:** `snobol4_js` (added to `run_invariants.sh` at M-SJ-A01)
**Emit-diff gate:** 981/4 throughout (JS artifacts absent = skip, not fail)

---

## Dependency answer: scaffold → runtime → trampoline → features → patterns → EVAL

The egg comes first: `emit_js.c` must exist and build before any test can
run. The runtime JS stub must exist before the emitter can produce runnable
output. Parity with existing backends (rung2/3/4) gates everything else.
Pattern matching gates on arithmetic+control. EVAL()/CODE() gate on parity.

---

## Phase A — Foundation (no prior JS work exists)

### M-SJ-A01 — Scaffold: emit_js.c builds, hello passes

**Depends on:** nothing (first milestone)
**Scope:**
- Create `src/backend/emit_js.c` — empty EKind switch, `J()` macro,
  file header/footer emitting `"use strict"; let _vars={};`
- Create `src/runtime/js/sno_runtime.js` — `_print(s)`, `_vars` get/set,
  `_trampoline(start)` engine
- Create `test/js/run_js.js` — Node runner: `require('./prog.js')`
- Wire into Makefile: `FRONTEND=snobol4 BACKEND=js` produces `.js`
- Handle: `E_QLIT` (string literal), `E_ILIT`, `E_VAR`, `E_NUL`,
  `E_ASSIGN` (simple var=expr), OUTPUT statement
- Trampoline engine: `let pc=block_START; while(pc) pc=pc();`

**Gate:** `snobol4_js` cell: hello/literals pass · emit-diff 981/4 ✅

---

### M-SJ-A02 — Arithmetic parity (rung4)

**Depends on:** M-SJ-A01
**Scope:**
- `E_ILIT`, `E_FLIT`, `E_ADD`, `E_SUB`, `E_MPY`, `E_DIV`, `E_MOD`, `E_POW`
- `E_NEG`, `E_PLS` (unary)
- Integer/float coercion: `_to_int(v)`, `_to_float(v)`, `_to_str(v)`
- Arithmetic builtins: `INTEGER()`, `REAL()`, `CONVERT()`

**Gate:** rung4 (410–414) all pass · emit-diff 981/4 ✅

---

### M-SJ-A03 — String ops (rung8)

**Depends on:** M-SJ-A02
**Scope:**
- `E_CONCAT` (value context — `+` in JS)
- `SIZE()` → `str.length`
- `REPLACE()`, `DUPL()`, `REVERSE()`, `TRIM()`
- `SUBSTR()`, `LPAD()`, `RPAD()`

**Gate:** rung8 (810–816) all pass · emit-diff 981/4 ✅

---

### M-SJ-A04 — Indirect refs and control flow (rung2/3/5/6)

**Depends on:** M-SJ-A03
**Scope:**
- `E_INDR` (`$expr` indirect reference)
- Goto dispatch: `:S(L)F(L)`, unconditional goto
- Label blocks as trampoline functions: `function block_L() { ... }`
- `br_table` equivalent: JS `switch` or object map on label name
- `E_MATCH` (subject-only, no pattern — bool result)

**Gate:** rung2 (210–212) · rung3 (310–312) pass · emit-diff 981/4 ✅

---

## Phase B — Pattern Matching

### M-SJ-B01 — E_QLIT: literal match + scan loop (rungJ01)

**Depends on:** M-SJ-A04
**Scope:**
- Add `rungJ01/` corpus dir with `.sno` / `.ref` / `.js` for basic literal match
- Scan loop: `cursor` global, scan from pos 0 to `subject.length`
- `E_QLIT` α/β port functions: compare `subject.slice(cursor, cursor+n)`
- Subject eval + assignment (`=` replacement)
- Corpus: `J01_pat_lit_basic.sno`, `J01_pat_lit_replace.sno`

**Gate:** rungJ01 pass · emit-diff 981/4 ✅

---

### M-SJ-B02 — E_SEQ: sequential patterns (rungJ02)

**Depends on:** M-SJ-B01
**Scope:**
- `E_SEQ` wiring: `seq_α→left_α`, `left_γ→right_α`, `right_ω→left_β`,
  `right_γ→seq_γ` — identical to C backend `emit_seq()`
- Corpus: concatenated pattern tests

**Gate:** rungJ02 pass · emit-diff 981/4 ✅

---

### M-SJ-B03 — E_ALT: alternation (rungJ03)

**Depends on:** M-SJ-B02
**Scope:**
- `E_ALT` wiring: `alt_α→left_α`, `left_ω→right_α`, `right_ω→alt_ω`
- `_alt_i` counter for backtrack routing (mirrors C backend)
- Corpus: `BIRD | BLUE | LEN(1)` style tests

**Gate:** rungJ03 pass · emit-diff 981/4 ✅

---

### M-SJ-B04 — E_ARBNO / E_ARB (rungJ04)

**Depends on:** M-SJ-B03
**Scope:**
- `E_ARBNO`: zero-or-more with zero-advance guard (cursor must advance)
- `E_ARB`: try empty first, β tries longer
- Stack array for ARBNO backtrack state (mirrors C `_1[64]` pattern)

**Gate:** rungJ04 pass · emit-diff 981/4 ✅

---

### M-SJ-B05 — Pattern primitives: LEN/POS/RPOS/SPAN/BREAK/ANY/NOTANY (rungJ05)

**Depends on:** M-SJ-B04
**Scope:**
- All 14 E_* pattern primitives from `ir.h`:
  `E_LEN`, `E_POS`, `E_RPOS`, `E_TAB`, `E_RTAB`, `E_REM`,
  `E_ANY`, `E_NOTANY`, `E_SPAN`, `E_BREAK`, `E_BREAKX`,
  `E_FENCE`, `E_FAIL`, `E_SUCCEED`, `E_ABORT`, `E_BAL`
- Each gets α/β port functions; wiring per C backend `emit_pat_node()`

**Gate:** rungJ05 pass · emit-diff 981/4 ✅

---

### M-SJ-B06 — Captures: E_CAPT_COND / E_CAPT_IMM / E_CAPT_CUR (rungJ06)

**Depends on:** M-SJ-B05
**Scope:**
- `.var` conditional capture: save `subject.slice(before, cursor)` on γ
- `$var` immediate capture: save on each advance
- `@var` cursor position capture

**Gate:** rungJ06 pass (mirrors rung9 capture tests) · emit-diff 981/4 ✅

---

## Phase C — Functions, Arrays, Data

### M-SJ-C01 — Arrays / Tables / DATA types (rung10/11)

**Depends on:** M-SJ-B06
**Scope:**
- `ARRAY()` → JS array, `TABLE()` → JS `Map`
- `DATA()` → JS class definition
- `FIELD()` → property access
- `E_IDX` subscript

**Gate:** rung10 (array/table tests) · rung11 pass · emit-diff 981/4 ✅

---

### M-SJ-C02 — User-defined functions / DEFINE (rung10 functions)

**Depends on:** M-SJ-C01
**Scope:**
- `DEFINE('fname(p1,p2,...)')` → JS function declaration
- `E_FNC` call ABI: save/restore `_vars` scope
- `RETURN` / `FRETURN` / `NRETURN` wiring
- Recursion: each call gets fresh local scope object

**Gate:** rung10 function tests pass · emit-diff 981/4 ✅

---

### M-SJ-C03 — EVAL() / CODE() (rungJ07)

**Depends on:** M-SJ-C02 (need full emitter working first)
**Scope:**
- `_scrip_compile_expr(str)` — SNOBOL4 expr → JS expr string
  (uses existing frontend parse + JS value emitter)
- `_scrip_compile_stmts(str)` — SNOBOL4 stmts → JS trampoline block
- `sno_eval(str)` / `sno_code(str)` wrappers using `new Function()`
- Corpus: `J07_eval_basic.sno`, `J07_code_basic.sno`

**Gate:** rungJ07 pass · emit-diff 981/4 ✅

---

### M-SJ-PARITY — Full corpus parity

**Depends on:** M-SJ-C03
**Scope:** All rung2–rung11 + rungJ01–J07 passing.
`snobol4_js` invariant cell at parity with `snobol4_x86`.

**Gate:** `snobol4_js` ≥ `snobol4_x86` pass count · emit-diff 981/4 ✅

---

*MILESTONE-JS-SNOBOL4.md — created SJ-1, 2026-03-31, Claude Sonnet 4.6.*
