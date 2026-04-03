# MILESTONE-JS-SNOBOL4.md — SNOBOL4 × JavaScript Milestone Ladder

**Session:** SJ · **Oracle:** `scrip-interp.c` (interpreter) · `emit_byrd_c.c` (emitter, Phase D)
**Architecture:** Interpreter first → Emitter after (interpreter proven)
**Gate (Phases A–C):** Interpreter regression only — no emit-diff, no snobol4_x86 invariants
**Gate (Phase D+):** emit-diff + snobol4_js invariants added when emitter work begins

---

## Organizing principle

One track, two sequential phases of work:

1. **Interpreter (Phases A–C):** Lex → Parse → IR → execute via stack machine +
   JS Byrd-box sequencer. Oracle: `scrip-interp.c`. IR is identical to what
   `scrip-cc` builds. The two execution engines are:
   - **Stack machine** — evaluates expressions, drives Phases 1, 4, 5
   - **Byrd-box sequencer** — drives pattern match, Phases 2, 3

   JS Byrd boxes live in `one4all/src/runtime/boxes/*/bb_*.js`.
   The interpreter does NOT walk the IR tree the way `scrip-interp.c` does —
   it executes via the stack machine + sequencer instead.

2. **Emitter (Phase D+):** `emit_js.c` static code generation, built on the
   proven interpreter. Oracle: `emit_byrd_c.c`. Added after Phase C complete.

---

## 5-Phase statement execution

Every SNOBOL4 statement runs through 5 phases (oracle: `stmt_exec.c`):

```
Phase 1: build_subject  — resolve subject variable or expression → Σ/Δ/Ω
Phase 2: build_pattern  — IR pattern node → live {α,β} JS Byrd box graph
Phase 3: run_match      — drive root.α() via trampoline, collect captures
Phase 4: build_repl     — evaluate replacement expression → value
Phase 5: perform_repl   — splice into subject, assign, take :S/:F branch
```

Pattern-free statements skip Phases 2+3.

---

## Key files

| File | Role |
|------|------|
| `src/runtime/js/sno-interp.js` | **Main interpreter** — stack machine + BB sequencer |
| `src/runtime/boxes/*/bb_*.js` | **JS Byrd boxes** — one per box type |
| `src/runtime/js/sno_runtime.js` | Value types, builtins, I/O |
| `src/driver/scrip-interp.c` | **Oracle** — C tree-walk interpreter (reference only) |
| `src/runtime/dyn/stmt_exec.c` | **Oracle** — 5-phase executor |
| `src/backend/c/emit_byrd_c.c` | Oracle for Phase D emitter (future) |

---

## Phase A — Lexer, Parser, IR, Scaffold

### M-SJ-A01 — Lexer: tokenize SNOBOL4 source

**Depends on:** nothing (first milestone)
**Oracle:** `src/frontend/snobol4/lex.c`
**Scope:**
- `src/runtime/js/lex.js` — tokenize SNOBOL4 source file
- Token types: label, subject, pattern, replacement, goto, continuation
- Output: token stream consumable by parser
- Corpus `rungJS00/`: lex smoke tests

**Gate:** rungJS00 lex tests pass ✅

---

### M-SJ-A02 — Parser: token stream → IR tree

**Depends on:** M-SJ-A01
**Oracle:** `src/frontend/snobol4/parse.c` · `src/frontend/snobol4/scrip_cc.h`
**Scope:**
- `src/runtime/js/parse.js` — produce IR identical to `scrip-cc`
- `Program` → linked list of `STMT_t`
- `STMT_t` fields: label, subject `EXPR_t*`, pattern `EXPR_t*`, replacement `EXPR_t*`, goto
- `EXPR_t` node kinds: all E_* from `ir.h`
- Corpus `rungJS01/`: parse smoke (round-trip label/subject/goto)

**Gate:** rungJS01 parse tests pass ✅

---

### M-SJ-A03 — Stack machine: Phase 1 + Phase 5 (no pattern)

**Depends on:** M-SJ-A02
**Oracle:** `scrip-interp.c` `interp_eval()` · `stmt_exec.c` Phase 1 + Phase 5
**Scope:**
- `sno-interp.js`: `eval_expr(node)` stack machine — `E_QLIT`, `E_ILIT`, `E_VAR`,
  `E_ASSIGN`, `E_CONCAT`, arithmetic ops
- `exec_stmt()` Phase 1: resolve subject
- `exec_stmt()` Phase 5 (no-pattern path): assign + `:S/:F` dispatch
- Label table + goto dispatch loop
- `OUTPUT` variable → stdout
- Corpus `rungJS02/`: hello, assignment, goto, label

**Gate:** rungJS02 pass ✅

---

### M-SJ-A04 — Stack machine: full value layer (Phase 4 complete)

**Depends on:** M-SJ-A03
**Oracle:** `scrip-interp.c` `interp_eval()` full switch
**Scope:**
- All arithmetic: `E_ADD`, `E_SUB`, `E_MPY`, `E_DIV`, `E_MOD`, `E_POW`, `E_NEG`
- String builtins: `SIZE`, `REPLACE`, `DUPL`, `REVERSE`, `TRIM`, `SUBSTR`, `LPAD`, `RPAD`
- Conversion: `INTEGER`, `REAL`, `CONVERT`
- `E_INDR` indirect reference (`$expr`)
- `E_KEYWORD` (`&ANCHOR`, `&TRIM`, etc.)
- Corpus `rungJS03/`: arithmetic, string ops, keywords

**Gate:** rungJS03 pass ✅

---

## Phase B — Pattern Matching (Phases 2 + 3)

### M-SJ-B01 — BB sequencer bootstrap: E_QLIT + scan loop

**Depends on:** M-SJ-A04
**Oracle:** `stmt_exec.c` Phase 2+3 · `bb_lit.js` (already written)
**Scope:**
- `sno-interp.js`: `build_pattern(node)` dispatcher → `{α,β}` root box
- Wire `bb_lit.js` for `E_QLIT`
- Scan loop: `for (cursor=0; cursor<=Σ.length; cursor++)`
- `&ANCHOR`: position-0 only when non-zero
- Phase 5 (match path): splice matched portion from subject
- Corpus `rungJS04/`: literal match, literal replace

**Gate:** rungJS04 pass ✅

---

### M-SJ-B02 — E_SEQ wiring

**Depends on:** M-SJ-B01
**Oracle:** `bb_seq.js` · `emit_byrd_c.c` `emit_seq()`
**Scope:**
- `build_pattern()`: `E_SEQ` → wire `seq_α→left_α`, `left_γ→right_α`,
  `right_ω→left_β`, `right_γ→seq_γ`
- n-ary SEQ: right-fold children
- Corpus `rungJS05/`: concatenated patterns

**Gate:** rungJS05 pass ✅

---

### M-SJ-B03 — E_ALT alternation

**Depends on:** M-SJ-B02
**Scope:**
- `build_pattern()`: `E_ALT` → `alt_α→left_α`, `left_ω→right_α`, `right_ω→alt_ω`
- Corpus `rungJS06/`: alternation tests

**Gate:** rungJS06 pass ✅

---

### M-SJ-B04 — E_ARBNO / E_ARB

**Depends on:** M-SJ-B03
**Scope:**
- `E_ARBNO`: zero-or-more; zero-advance guard
- `E_ARB`: try empty first, β tries longer
- Corpus `rungJS07/`

**Gate:** rungJS07 pass ✅

---

### M-SJ-B05 — All pattern primitives

**Depends on:** M-SJ-B04
**Scope:**
- All remaining E_* pattern nodes: `E_LEN`, `E_POS`, `E_RPOS`, `E_TAB`,
  `E_RTAB`, `E_REM`, `E_ANY`, `E_NOTANY`, `E_SPAN`, `E_BREAK`, `E_BREAKX`,
  `E_FENCE`, `E_FAIL`, `E_SUCCEED`, `E_ABORT`, `E_BAL`
- Each wires its `bb_*.js` box into `build_pattern()`
- Corpus `rungJS08/`

**Gate:** rungJS08 pass ✅

---

### M-SJ-B06 — Captures: COND / IMM / CUR + Phase 5 commit

**Depends on:** M-SJ-B05
**Oracle:** `stmt_exec.c` capture-flush logic
**Scope:**
- `.var` conditional capture: buffer on γ, flush in Phase 5
- `$var` immediate capture: write on each advance
- `@var` cursor position capture
- Phase 5: commit pending capture list after overall match success
- Corpus `rungJS09/`

**Gate:** rungJS09 pass ✅

---

## Phase C — Functions, Data Structures, EVAL

### M-SJ-C01 — Arrays / Tables / DATA types

**Depends on:** M-SJ-B06
**Scope:**
- `ARRAY()` → JS array · `TABLE()` → JS `Map`
- `DATA()` → JS class · `FIELD()` → property access
- `E_IDX` subscript (read + lvalue)
- Corpus `rungJS10/`

**Gate:** rungJS10 pass ✅

---

### M-SJ-C02 — User-defined functions / DEFINE

**Depends on:** M-SJ-C01
**Oracle:** `scrip-interp.c` `call_user_function()` · `prescan_defines()`
**Scope:**
- `DEFINE('fname(p1,p2,...)')` registration
- `E_FNC` call: save/restore local scope
- `RETURN` / `FRETURN` / `NRETURN`
- Recursion: fresh local scope per call
- Corpus `rungJS11/`

**Gate:** rungJS11 pass ✅

---

### M-SJ-C03 — EVAL() / CODE()

**Depends on:** M-SJ-C02
**Scope:**
- `sno_eval(str)` — compile + execute SNOBOL4 expression string
- `sno_code(str)` — compile + execute SNOBOL4 statement block
- Reuses the lexer/parser/interpreter pipeline recursively
- Corpus `rungJS12/`

**Gate:** rungJS12 pass ✅

---

### M-SJ-INTERP — Interpreter parity

**Depends on:** M-SJ-C03
**Scope:** All rungJS00–JS12 + rung2–rung11 passing through interpreter.
Interpreter at parity with `scrip-interp.c` on full corpus.

**Gate:** interpreter pass count ≥ `scrip-interp.c` on same corpus ✅

---

## Phase D — Emitter (after interpreter proven)

### M-SJ-D01 — emit_js.c scaffold + hello

*(Unlocked after M-SJ-INTERP)*
**Oracle:** `emit_byrd_c.c` · proven interpreter as reference
**Scope:** `emit_js.c` emitter scaffold, `sno_engine.js` static fast path.
Gates reintroduce emit-diff + `snobol4_js` invariants.

*(Milestones D02+ to be specified at M-SJ-INTERP time.)*

---

## Sprint Sequence

| Sprint | Milestone | Key work |
|--------|-----------|----------|
| SJ-6 | M-SJ-A01 | Lexer (`lex.js`) |
| SJ-7 | M-SJ-A02 | Parser (`parse.js`) → IR |
| SJ-8 | M-SJ-A03 | Stack machine Phase 1+5 · goto · label · OUTPUT |
| SJ-9 | M-SJ-A04 | Full value layer — arithmetic, builtins, keywords |
| SJ-10 | M-SJ-B01 | BB sequencer bootstrap · E_QLIT · scan loop |
| SJ-11 | M-SJ-B02–B03 | E_SEQ · E_ALT |
| SJ-12 | M-SJ-B04–B05 | ARBNO/ARB + all 16 primitives |
| SJ-13 | M-SJ-B06 | Captures + Phase 5 commit flush |
| SJ-14 | M-SJ-C01 | ARRAY/TABLE/DATA |
| SJ-15 | M-SJ-C02 | DEFINE/user-fns |
| SJ-16 | M-SJ-C03 | EVAL()/CODE() |
| SJ-17 | M-SJ-INTERP | Interpreter parity sweep |
| SJ-18+ | M-SJ-D01+ | Emitter phase begins |

---

*MILESTONE-JS-SNOBOL4.md — rewritten SJ-6, 2026-04-02, Claude Sonnet 4.6.*
*Interpreter-first architecture. Emitter (Phase D) follows after interpreter proven.*
*Oracle for interpreter: scrip-interp.c. Oracle for emitter: emit_byrd_c.c.*
