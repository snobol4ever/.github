# MILESTONE-JS-SNOBOL4.md — SNOBOL4 × JavaScript Milestone Ladder

**Session:** SJ · **Oracle:** `emit_byrd_c.c` + `stmt_exec.c` · **Trampoline:** `trampoline.h`
**Invariant cell:** `snobol4_js` (added to `run_invariants.sh` at M-SJ-A01)
**Emit-diff gate:** 981/4 throughout (JS artifacts absent = skip, not fail)

---

## Organizing principle: the 5-phase statement executor

The x86 backend (`stmt_exec.c`) defines SNOBOL4 execution as exactly five phases:

```
Phase 1: build_subject  — extract string from variable or expr, set Σ/Δ/Ω
Phase 2: build_pattern  — walk pattern AST → live Byrd box graph / DT_P
Phase 3: run_match      — drive root box α/β, collect captures
Phase 4: build_repl     — evaluate replacement expression → DESCR_t
Phase 5: perform_repl   — splice into subject, assign, take :S/:F branch
```

The JS milestone ladder is organized around building `sno_engine.js` as a
direct port of this executor.  Every milestone adds exactly the JS machinery
needed for one more class of statement to pass through all 5 phases correctly.

The old Phase A/B/C split is retired.  Everything flows from the executor spine.

**Key files:**
| File | Role |
|------|------|
| `src/backend/emit_js.c` | JS emitter — main work file |
| `src/runtime/js/sno_engine.js` | 5-phase executor (port of `stmt_exec.c`) |
| `src/runtime/js/sno_runtime.js` | Value types, builtins, I/O |
| `test/js/run_js.js` | Node runner shim |

---

## Phase 1 — Scaffold + Value Layer (no pattern matching yet)

### M-SJ-A01 — Scaffold: emit_js.c builds, hello passes

**Depends on:** nothing (first milestone)
**Scope:**
- Create `src/backend/emit_js.c` — empty EKind switch, `J()` macro,
  file header/footer emitting `"use strict";`
- Create `src/runtime/js/sno_runtime.js` — `_print(s)`, `_to_str()`,
  `_to_int()`, `_to_float()`; DESCR_t as `{v, s}` JS object
- Create `src/runtime/js/sno_engine.js` — stub `exec_stmt()` that handles
  Phase 1 (subject resolution) only; no pattern, no replacement
- Create `test/js/run_js.js` — Node runner: `require('./sno_runtime.js')`
- Wire into Makefile: `FRONTEND=snobol4 BACKEND=js` produces `.js`
- Handle: `E_QLIT`, `E_ILIT`, `E_VAR`, `E_NUL`, `E_ASSIGN`, OUTPUT statement
- Trampoline: `let pc = block_START; while (pc) pc = pc();`

**Gate:** `snobol4_js` cell: hello/literals pass · emit-diff 981/4 ✅

---

### M-SJ-A02 — Phase 4 complete: full value expression layer

**Depends on:** M-SJ-A01
**Rationale:** Phase 4 (`build_repl`) evaluates the replacement expression.
Before we can test matching we need the full value layer working so Phase 4
can produce any SNOBOL4 value.
**Scope:**
- `E_ILIT`, `E_FLIT`, `E_ADD`, `E_SUB`, `E_MPY`, `E_DIV`, `E_MOD`, `E_POW`
- `E_NEG`, `E_PLS` (unary)
- `E_CONCAT` (value context)
- Integer/float/string coercion: `_to_int(v)`, `_to_float(v)`, `_to_str(v)`
- Arithmetic builtins: `INTEGER()`, `REAL()`, `CONVERT()`
- String builtins: `SIZE()`, `REPLACE()`, `DUPL()`, `REVERSE()`, `TRIM()`,
  `SUBSTR()`, `LPAD()`, `RPAD()`
- `E_INDR` (`$expr` indirect reference)

**Gate:** rung4 (410–414) · rung8 (810–816) all pass · emit-diff 981/4 ✅

---

### M-SJ-A03 — Phase 1+5 complete: subject/goto/label/assignment

**Depends on:** M-SJ-A02
**Rationale:** Phase 1 resolves the subject; Phase 5 performs assignment and
takes the :S/:F branch.  With no pattern (pattern=null), Phase 3 is vacuous
and Phase 5 just does the assignment.  This milestone locks in the control
flow spine before any pattern work.
**Scope:**
- `exec_stmt()` Phase 1: named-variable subject OR expression subject
- `exec_stmt()` Phase 5 (no-pattern path): `NV_SET`, splice, :S/:F
- Goto dispatch: `:S(L)F(L)`, unconditional goto
- Label blocks as trampoline functions: `function block_L() { ... }`
- `E_KEYWORD` (read/write `&ANCHOR`, `&TRIM`, etc.)
- Fix Node v22 IIFE bug in forward-decl section

**Gate:** rung2 (210–212) · rung3 (310–312) · rung5 · rung6 pass ·
emit-diff 981/4 ✅

---

## Phase 2 — Pattern Matching (exec_stmt Phases 2+3)

### M-SJ-B01 — Phase 2 bootstrap: pattern builder + Phase 3: literal match

**Depends on:** M-SJ-A03
**Rationale:** `exec_stmt()` Phase 2 builds the Byrd box graph from a pattern
descriptor.  In JS this is `sno_engine.js`'s `build_pattern(pat)`, which
returns a `{α, β}` port-function pair (the root box).  Phase 3 drives
`root.α()`, following the trampoline chain.  This milestone adds the minimal
pattern machinery: E_QLIT literal match + the scan loop.
**Scope:**
- `sno_engine.js`: `build_pattern(pat)` dispatcher skeleton
- Scan loop: `for (cursor=0; cursor<=Σ.length; cursor++)`
- `E_QLIT` α port: `Σ.slice(cursor, cursor+n) === lit` → advance → γ_outer
- `E_QLIT` β port: `return ω_outer` (literals don't backtrack)
- `&ANCHOR`: when non-zero, Phase 3 tries position 0 only
- Phase 5 (match path): splice matched portion out of subject
- Add `rungJ01/` corpus dir: `J01_pat_lit_basic.sno`, `J01_pat_lit_replace.sno`

**Gate:** rungJ01 pass · emit-diff 981/4 ✅

---

### M-SJ-B02 — Phase 2: E_SEQ wiring

**Depends on:** M-SJ-B01
**Scope:**
- `E_SEQ`: `seq_α→left_α`, `left_γ→right_α`, `right_ω→left_β`,
  `right_γ→seq_γ` — identical to C backend `emit_seq()`
- n-ary SEQ: right-fold children (left-to-right evaluation)
- Corpus `rungJ02/`: concatenated pattern tests

**Gate:** rungJ02 pass · emit-diff 981/4 ✅

---

### M-SJ-B03 — Phase 2: E_ALT alternation

**Depends on:** M-SJ-B02
**Scope:**
- `E_ALT`: `alt_α→left_α`, `left_ω→right_α`, `right_ω→alt_ω`
- `_alt_i` counter for backtrack routing (mirrors C backend)
- Corpus `rungJ03/`: `BIRD | BLUE | LEN(1)` style tests

**Gate:** rungJ03 pass · emit-diff 981/4 ✅

---

### M-SJ-B04 — Phase 2: E_ARBNO / E_ARB

**Depends on:** M-SJ-B03
**Scope:**
- `E_ARBNO`: zero-or-more; zero-advance guard (cursor must advance per cycle)
- `E_ARB`: try empty first, β tries longer
- Stack array for ARBNO backtrack state (mirrors C `_1[64]` pattern)
- Corpus `rungJ04/`

**Gate:** rungJ04 pass · emit-diff 981/4 ✅

---

### M-SJ-B05 — Phase 2: all pattern primitives

**Depends on:** M-SJ-B04
**Scope:**
- All 16 E_* pattern primitives from `ir.h`:
  `E_LEN`, `E_POS`, `E_RPOS`, `E_TAB`, `E_RTAB`, `E_REM`,
  `E_ANY`, `E_NOTANY`, `E_SPAN`, `E_BREAK`, `E_BREAKX`,
  `E_FENCE`, `E_FAIL`, `E_SUCCEED`, `E_ABORT`, `E_BAL`
- Each gets α/β port functions; wiring per C backend `emit_pat_node()`
- Corpus `rungJ05/`

**Gate:** rungJ05 pass · emit-diff 981/4 ✅

---

### M-SJ-B06 — Phase 3 captures: COND / IMM / CUR

**Depends on:** M-SJ-B05
**Rationale:** Phase 3 collects captures during match; Phase 5 commits them.
This directly mirrors `stmt_exec.c`'s capture-flush logic (pending-capture
list, flushed after overall match success).
**Scope:**
- `.var` conditional capture (`E_CAPT_COND`): buffer on γ, flush in Phase 5
- `$var` immediate capture (`E_CAPT_IMM`): write on each advance
- `@var` cursor position capture (`E_CAPT_CUR`)
- Phase 5: commit pending capture list after overall match success
- Corpus `rungJ06/` (mirrors rung9 capture tests)

**Gate:** rungJ06 pass · emit-diff 981/4 ✅

---

## Phase 3 — Functions, Data Structures, EVAL

### M-SJ-C01 — Arrays / Tables / DATA types

**Depends on:** M-SJ-B06
**Scope:**
- `ARRAY()` → JS array, `TABLE()` → JS `Map`
- `DATA()` → JS class definition; `FIELD()` → property access
- `E_IDX` subscript (read and lvalue assignment)

**Gate:** rung10 (array/table tests) · rung11 pass · emit-diff 981/4 ✅

---

### M-SJ-C02 — User-defined functions / DEFINE

**Depends on:** M-SJ-C01
**Scope:**
- `DEFINE('fname(p1,p2,...)')` → JS function declaration
- `E_FNC` call ABI: save/restore `_vars` scope
- `RETURN` / `FRETURN` / `NRETURN` wiring
- Recursion: each call gets fresh local scope object

**Gate:** rung10 function tests pass · emit-diff 981/4 ✅

---

### M-SJ-C03 — EVAL() / CODE()

**Depends on:** M-SJ-C02
**Rationale:** EVAL/CODE are the whole reason we chose JS over WASM.  They
work because `new Function()` creates new port functions at runtime and wires
them into the dispatch table — the same 5-phase executor handles dynamically
compiled statements identically to static ones.
**Scope:**
- `_scrip_compile_expr(str)` — SNOBOL4 expr → JS expr string
- `_scrip_compile_stmts(str)` — SNOBOL4 stmts → JS trampoline block
- `sno_eval(str)` / `sno_code(str)` wrappers using `new Function()`
- Corpus `rungJ07/`: `J07_eval_basic.sno`, `J07_code_basic.sno`

**Gate:** rungJ07 pass · emit-diff 981/4 ✅

---

### M-SJ-PARITY — Full corpus parity

**Depends on:** M-SJ-C03
**Scope:** All rung2–rung11 + rungJ01–J07 passing.
`snobol4_js` invariant cell at parity with `snobol4_x86`.

**Gate:** `snobol4_js` ≥ `snobol4_x86` pass count · emit-diff 981/4 ✅

---

## Sprint Sequence

| Sprint | Milestone | Key work |
|--------|-----------|----------|
| SJ-5 | M-SJ-A03 | Fix Node v22 IIFE bug · wire goto/labels · Phase 5 assign path |
| SJ-6 | M-SJ-A02 residual | `remdr`, float fmt, `_to_str` fixes; rung4/8 clean |
| SJ-7 | M-SJ-B01 | `build_pattern()` + scan loop + E_QLIT + Phase 5 splice |
| SJ-8 | M-SJ-B02–B03 | E_SEQ right-fold · E_ALT |
| SJ-9 | M-SJ-B04–B05 | ARBNO/ARB + all 16 primitives |
| SJ-10 | M-SJ-B06 | Captures: COND/IMM/CUR + Phase 5 commit |
| SJ-11 | M-SJ-C01 | ARRAY/TABLE/DATA |
| SJ-12 | M-SJ-C02 | DEFINE/user-fns/RETURN |
| SJ-13 | M-SJ-C03 | EVAL()/CODE() via `new Function()` |
| SJ-14 | M-SJ-PARITY | Full corpus sweep |

---

## How JS sno_engine.js relates to x86 stmt_exec.c

The x86 `exec_stmt` is a C function called at runtime by emitted NASM.
The JS equivalent is `sno_engine.js`'s `exec_stmt(subj, pat, repl, has_repl)`:

| Aspect | x86 (`stmt_exec.c`) | JS (`sno_engine.js`) |
|--------|---------------------|----------------------|
| Phase 1 subject | `NV_GET_fn` → `spec_t` | `_vars[name]` → string |
| Phase 2 pattern | `PATND_t*` → bb graph | `{α,β}` JS object tree |
| Phase 3 drive | C goto trampoline | JS function trampoline |
| Phase 4 repl | `DESCR_t` already eval'd | `{v,s}` object |
| Phase 5 splice | `memmove` + `NV_SET_fn` | `slice + concat + _vars[]=` |
| Captures | pending array, flush on :S | JS array, flush on :S |

`stmt_exec.c` is the oracle for `sno_engine.js`.
`emit_byrd_c.c` is the oracle for `emit_js.c`.
Both oracles must be read before writing any JS pattern code.

---

*MILESTONE-JS-SNOBOL4.md — rewritten SJ-4, 2026-04-02, Claude Sonnet 4.6.*
*Reorganized around 5-phase executor (stmt_exec.c model). Old Phase A/B/C retired.*
