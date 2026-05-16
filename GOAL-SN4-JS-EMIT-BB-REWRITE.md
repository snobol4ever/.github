# GOAL-SN4-JS-EMIT-BB-REWRITE.md — Delete Interpreter, Emit Real Byrd Boxes

**Repo:** one4all + .github
**Reason:** Previous implementation violated RULES.md § "NO AST WALKING IN MODES 2/3/4" by embedding an interpreter (sno_engine.js, pattern interpreter path in sno_runtime.js). Pattern matching must emit actual Byrd-box factories in JavaScript, matching the semantics of x86/JVM/.NET emitters.

**⚠️ CORRECTION (2026-05-16, session after BB0):**
BB0 (deletion of sno_engine.js) was a mistake caused by Claude confusing two separate concerns:
- `sno_engine.js` is the **runtime pattern-match engine** — it runs the emitted JS output. It is NOT an AST-walking interpreter of SNOBOL4 source. It must be preserved.
- The rule against "AST walking" / "interpreter code" applies to `scrip` compiling SNOBOL4 source — not to the JS runtime that executes already-compiled output.
- **`sno_engine.js` has been RESTORED** from git history (commit `a3eabfc9`).
- The pattern-interpreter sections deleted from `sno_runtime.js` should also be reviewed for restoration.

**⛔ CORRECTED PERMANENT RULE:**
- **DO NOT delete sno_engine.js** — it is the compiled-JS pattern execution runtime, not a SNOBOL4 source interpreter
- Pattern matching in the JS *emitter* (emit_js.c) MUST emit Byrd-box-style factory calls
- The emitted factories run *inside* the sno_engine.js / sno_runtime.js runtime harness
- Every SM_PAT_* opcode in emit_js.c builds emitted pattern factory code, not data structures
- SM_EXEC_STMT emits JS code that calls the harness — the harness itself lives in sno_engine.js
- **This rule is non-negotiable and applies to all emitters** (JS, JVM, .NET, WASM)

---

## Architecture: Stack Machine + Byrd Boxes

### Stack Machine (SM)
The SNOBOL4 compiler (lower.c) converts the AST to SM_Program — a flat array of SM_INSTR_t:
- **Value stack operations**: SM_PUSH_LIT_S, SM_PUSH_VAR, SM_STORE_VAR, SM_ADD, etc.
- **Control flow**: SM_JUMP, SM_JUMP_S, SM_JUMP_F, SM_HALT
- **Pattern building**: SM_PAT_LIT, SM_PAT_ANY, SM_PAT_CAT, SM_PAT_ALT, etc.
- **Pattern execution**: SM_EXEC_STMT (pattern match + optional replace)
- **Function calls**: SM_CALL_FN, SM_RETURN, SM_FRETURN, SM_NRETURN
- **State**: SM_LABEL (entry points), SM_STNO (statement numbers)

### JavaScript Runtime (sno_runtime.js)
Executes SM_Program via switch/case dispatcher:
```javascript
let _pc = 0;
while (true) { switch (_pc) {
  case 0: rt.set_stno(1); _pc = 1; continue;
  case 1: rt.push_int(5); _pc = 2; continue;
  case 2: rt.store_var("X"); _pc = 3; continue;
  ...
```

### Byrd Boxes (bb_boxes.js reference implementation)
Each pattern operator is a **factory function** that returns `{α, β}` port pair:
```javascript
function bb_lit(lit) {
  return {
    α() {
      if (_Δ + len > _Ω) return _FAIL;
      if (_Σ.slice(_Δ, _Δ + len) !== lit) return _FAIL;
      const r = _spec(_Δ, len); _Δ += len; return r;
    },
    β() { _Δ -= len; return _FAIL; }
  };
}
```

### SM → JS Emission Model
1. **SM_PAT_LIT "hello"** → Emit factory function call: `const pat_N = bb_lit("hello")`
2. **SM_PAT_CAT** → Wire two factories: `const pat_N = bb_seq(pat_left, pat_right)`
3. **SM_PAT_ALT** → Wire choices: `const pat_N = bb_alt([pat1, pat2, pat3])`
4. **SM_EXEC_STMT** → Pop pattern from stack, call harness: `rt.exec_pattern_stmt(subj_name, pat_N, has_repl)`

---

## Step 0 — ⚠️ REVERTED (2026-05-16, session after BB0)

BB0 was based on a misunderstanding. sno_engine.js is NOT a SNOBOL4 source interpreter — it is the
pattern execution runtime for compiled JS output. It must NOT be deleted.

- [x] SJ4-JS-BB0a — ~~Delete sno_engine.js entirely~~ **REVERTED — sno_engine.js restored from a3eabfc9**
- [x] SJ4-JS-BB0b — ~~Delete pattern-interpreter sections from sno_runtime.js~~ **NEEDS REVIEW for restoration**
- [x] SJ4-JS-BB0c — ~~Replace deleted sections with stubs~~ **Stubs now redundant — engine restored**
- [x] SJ4-JS-BB0d — ~~Update RULES.md to add permanent rule~~ **RULES.md rule was wrong — see correction above**
- [ ] SJ4-JS-BB0e-FIX — Restore sno_runtime.js deleted pattern sections (review what was lost)
- [ ] SJ4-JS-BB0f-FIX — Commit restoration with note that BB0 was confused about compiled vs interpreter

**Status after restoration:** sno_engine.js back at 620 lines. sno_runtime.js pattern stubs still need review.

---

## Step 1 — Implement exec_pattern Harness (SJ4-JS-BB1) ✅ COMPLETE

The **execution harness** manages match state (_Σ, _Δ, _Ω) and orchestrates pattern execution.

### SJ4-JS-BB1a — Core exec_pattern function ✅ COMPLETE

```javascript
// Harness flow:
// 1. search_pattern(pat) — try α port at each position
// 2. On success, commit captures and apply replacement
// 3. Set _last_ok for :S/:F control flow
```

- [x] SJ4-JS-BB1a-i — Implement `bb_set_subject`, `bb_reset_captures`, `bb_get_pending` ✅
- [x] SJ4-JS-BB1a-ii — Implement `search_pattern(pat)` — tries α at each position ✅
- [x] SJ4-JS-BB1a-iii — Implement `exec_pattern_stmt` harness ✅
- [x] SJ4-JS-BB1a-iv — Test: `"hello" "hello" . X = "MATCH"` ✅ **PASSING**
- [x] SJ4-JS-BB1a-v — Commit: "SJ4-JS-BB1a: exec_pattern harness" ✅ `0a233aad`

---

## Step 2 — Wire Factory Builders in Runtime (SJ4-JS-BB2) ✅ COMPLETE

Each SM_PAT_* opcode now emits code that pushes a factory function onto the stack.

### SJ4-JS-BB2a — Basic Pattern Factories ✅ COMPLETE

Implemented 19 factory functions in sno_runtime.js:

- [x] `bb_lit_factory(lit)` — literal string matching ✅
- [x] `bb_any_factory(chars)` — match char from set ✅
- [x] `bb_notany_factory(chars)` — match char NOT in set ✅
- [x] `bb_span_factory(chars)` — zero+ chars from set (greedy) ✅
- [x] `bb_break_factory(chars)` — match until char from set ✅
- [x] `bb_len_factory(n)` — match exactly n chars ✅
- [x] `bb_pos_factory(n)` — match if at position n ✅
- [x] `bb_rpos_factory(n)` — match if n chars from end ✅
- [x] `bb_tab_factory(n)` — match to position n ✅
- [x] `bb_rtab_factory(n)` — match to n chars from end ✅
- [x] `bb_rem_factory()` — match rest of string (REM) ✅
- [x] `bb_arb_factory()` — match zero+ of anything ✅
- [x] `bb_arbno_factory(body)` — zero+ repetitions ✅
- [x] `bb_fail_factory()` — always fail ✅
- [x] `bb_succeed_factory()` — always succeed (zero-width) ✅

Stack machine operations (pat_lit, pat_any, etc.):
- [x] Pop operand(s), create factory, push factory function ✅

### SJ4-JS-BB2b — Composition Factories ✅ COMPLETE

- [x] `bb_seq_factory(left, right)` — concatenation (PAT_CAT) ✅
- [x] `bb_alt_factory(children)` — alternation (PAT_ALT) ✅

### SJ4-JS-BB2c — Capture Factory ✅ COMPLETE

- [x] `bb_capture_factory(child, varname, immediate)` — variable capture ✅
- [x] Kind 0 (conditional .): accumulate in _bb_pending ✅
- [x] Kind 1 (immediate $): write directly to _vars ✅

**Status:** PASS=24 FAIL=105 (ladder climbing started!)

---

## Step 3 — Backtracking and Choice Points (SJ4-JS-BB3)

### SJ4-JS-BB3a — ALT backtracking (IN PROGRESS)

---

## Step 5 — Ladder Climbing (SJ4-JS-BB5)

Test-suite milestones (csnobol4-suite, snobol4/demo, snobol4/feat):

- [ ] SJ4-JS-BB5a — Target PASS ≥ 10: literals, any, simple patterns
- [ ] SJ4-JS-BB5b — Target PASS ≥ 25: sequences, alternation, captures
- [ ] SJ4-JS-BB5c — Target PASS ≥ 40: backtracking, loops, replacement
- [ ] SJ4-JS-BB5d — Target PASS ≥ 60: advanced patterns (LEN, POS, REM, etc.)
- [ ] SJ4-JS-BB5e — Target PASS ≥ 80: user functions, deferred variables
- [ ] SJ4-JS-BB5f — Target PASS ≥ 100: full corpus parity
- [ ] SJ4-JS-BB5g — Commit at each milestone with ladder-climbing summary

---

## State

```
watermark: SJ4-JS-BB1a (exec_pattern harness, in progress)
head: one4all (baseline PASS=0 FAIL=129 after deletion)
next: SJ4-JS-BB1a-i — implement bb_set_subject, bb_reset_captures, bb_get_pending
ladder: [easy-tests] → [character patterns] → [sequences/alternation] → [backtrack] → [advanced]
```

---

## Key Invariants

- **Pattern factories MUST emit as JavaScript functions** (no data structures like sno_engine)
- **Every factory returns `{α, β}` port pair** (follows bb_boxes.js reference)
- **SM_EXEC_STMT must emit JS code that calls factories and runs the harness** (not an interpreter)
- **bb_boxes.js is the reference** — copy its API and semantics exactly
- **Stack machine emits are unchanged** — only pattern operations are new
- **Test ladder progresses from easy to hard** — verify each rung before moving up

---


