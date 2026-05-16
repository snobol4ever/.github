# GOAL-SN4-JS-EMIT-BB-REWRITE.md — Delete Interpreter, Emit Real Byrd Boxes

**Repo:** one4all + .github
**Reason:** Previous implementation violated RULES.md § "NO AST WALKING IN MODES 2/3/4" by embedding an interpreter (sno_engine.js, pattern interpreter path in sno_runtime.js). Pattern matching must emit actual Byrd-box factories in JavaScript, matching the semantics of x86/JVM/.NET emitters.

**⛔ PERMANENT RULE (added to RULES.md):**
- **NEVER restore deleted interpreter code** (sno_engine.js, sno_runtime.js pattern-matching sections)
- Pattern matching MUST emit Byrd-box-style closures that implement α/β/γ/ω semantics
- Every SM_PAT_* opcode builds pattern factories (functions), not data structures
- SM_EXEC_STMT wires factories into a runtime harness that steps through ports
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

## Step 0 — Delete All Interpreter Code ✅ (COMPLETE 2026-05-16)

- [x] SJ4-JS-BB0a — Delete sno_engine.js entirely
- [x] SJ4-JS-BB0b — Delete pattern-interpreter sections from sno_runtime.js
- [x] SJ4-JS-BB0c — Replace deleted sections with stubs that throw "NOT IMPLEMENTED"
- [x] SJ4-JS-BB0d — Update RULES.md to add permanent rule
- [x] SJ4-JS-BB0e — Commit and push

**Status:** PASS=0 FAIL=129 (expected — no pattern matching implemented yet)

---

## Step 1 — Implement exec_pattern Harness (SJ4-JS-BB1)

The **execution harness** is the runtime function that:
1. Takes a pattern factory and subject string
2. Manages match state (_Σ, _Δ, _Ω) and capture lists
3. Calls α port at each position to search for a match
4. Commits or discards captures on success/failure
5. Returns success/failure to set _last_ok

### SJ4-JS-BB1a — Core exec_pattern function (THIS SESSION)

```javascript
function exec_pattern_stmt(subj_name, pat_factory, has_repl) {
    const subj = _str(_vars[subj_name || ''] || '');
    const pat = pat_factory();  // instantiate
    bb_set_subject(subj);       // set _Σ, _Δ, _Ω in bb_boxes module
    bb_reset_captures();        // clear _pending
    
    // Phase 1: Search for match (try every position)
    const result = search_pattern(pat);
    if (!result) {
        _last_ok = false;
        return;
    }
    
    // Phase 2: Commit captures
    const caps = bb_get_pending();
    for (const cap of caps) {
        _vars[cap.varname] = cap.value;
    }
    
    // Phase 3: Replacement (if requested)
    if (has_repl && subj_name) {
        const repl = _str(_stack.pop());  // replacement on stack
        const newsubj = subj.slice(0, result.start) + repl + subj.slice(result.end);
        _vars[subj_name] = newsubj;
    }
    
    _last_ok = true;
}
```

- [ ] SJ4-JS-BB1a-i — Implement `bb_set_subject(subj)`, `bb_reset_captures()`, `bb_get_pending()`
- [ ] SJ4-JS-BB1a-ii — Implement `search_pattern(pat)` — tries α port at each _Δ position
- [ ] SJ4-JS-BB1a-iii — Implement `exec_pattern_stmt` harness function
- [ ] SJ4-JS-BB1a-iv — Test: `"hello" "hello" . X = "MATCH"` should set X="hello"
- [ ] SJ4-JS-BB1a-v — Commit: "SJ4-JS-BB1a: exec_pattern harness (basic search)"

### SJ4-JS-BB1b — &ANCHOR and &FULLSCAN support

- [ ] SJ4-JS-BB1b-i — Check &ANCHOR keyword — if 1, search only at position 0
- [ ] SJ4-JS-BB1b-ii — Check &FULLSCAN keyword — if 1, search exhaustively; else greedy
- [ ] SJ4-JS-BB1b-iii — Test: `&ANCHOR = 1; "hello" "hello" . X` should succeed at offset 0 only
- [ ] SJ4-JS-BB1b-iv — Commit: "SJ4-JS-BB1b: &ANCHOR and &FULLSCAN"

---

## Step 2 — Wire Factory Builders in Emitter (SJ4-JS-BB2)

Update emit_js.c to emit factory-building code:

### SJ4-JS-BB2a — SM_PAT_LIT emission

- [ ] SJ4-JS-BB2a-i — Change `SM_PAT_LIT` handler in emit_js.c to emit: `rt.pat_lit_factory("string")`
- [ ] SJ4-JS-BB2a-ii — Implement `rt.pat_lit_factory(s)` in sno_runtime.js (returns `bb_lit(s)`)
- [ ] SJ4-JS-BB2a-iii — Replace pat_lit stub with real implementation
- [ ] SJ4-JS-BB2a-iv — Test: `"hello"` pattern should match "hello"
- [ ] SJ4-JS-BB2a-v — Commit: "SJ4-JS-BB2a: SM_PAT_LIT → bb_lit factory"

### SJ4-JS-BB2b — SM_PAT_ANY, NOTANY, SPAN, BREAK emission

- [ ] SJ4-JS-BB2b-i — Implement runtime factories: `pat_any_factory`, `pat_span_factory`, etc.
- [ ] SJ4-JS-BB2b-ii — Update emit_js.c handlers for each opcode
- [ ] SJ4-JS-BB2b-iii — Test: `ANY("abc")` matches one char from "abc"
- [ ] SJ4-JS-BB2b-iv — Commit: "SJ4-JS-BB2b: basic character patterns"

### SJ4-JS-BB2c — SM_PAT_CAT and SM_PAT_ALT (sequence and alternation)

- [ ] SJ4-JS-BB2c-i — Implement `pat_cat_factory()` — pops two patterns, pushes `bb_seq(left, right)`
- [ ] SJ4-JS-BB2c-ii — Implement `pat_alt_factory()` — pops N patterns, pushes `bb_alt([...])`
- [ ] SJ4-JS-BB2c-iii — Test: `LEN(5)` matches exactly 5 chars
- [ ] SJ4-JS-BB2c-iv — Test: `"a" | "b"` matches either "a" or "b"
- [ ] SJ4-JS-BB2c-v — Commit: "SJ4-JS-BB2c: sequence and alternation"

---

## Step 3 — Capture Variables and Replacement (SJ4-JS-BB3)

### SJ4-JS-BB3a — Conditional captures (. operator)

- [ ] SJ4-JS-BB3a-i — Implement `pat_capture_factory(varname, kind)` — wraps pattern in `bb_capture`
- [ ] SJ4-JS-BB3a-ii — Kind 0 = conditional (.), kind 1 = immediate ($)
- [ ] SJ4-JS-BB3a-iii — Test: `"hello" . X = "MATCH"` sets X to matched text
- [ ] SJ4-JS-BB3a-iv — Test: replacement via `= "new"` works
- [ ] SJ4-JS-BB3a-v — Commit: "SJ4-JS-BB3a: capture variables and replacement"

---

## Step 4 — Backtracking and Choice Points (SJ4-JS-BB4)

### SJ4-JS-BB4a — ALT backtracking

- [ ] SJ4-JS-BB4a-i — Implement choice-point stack in `bb_alt`
- [ ] SJ4-JS-BB4a-ii — β port pops from choice stack and tries next alternative
- [ ] SJ4-JS-BB4a-iii — Test: `"a" | "b" | "c"` backtracks through alternatives
- [ ] SJ4-JS-BB4a-iv — Commit: "SJ4-JS-BB4a: alternation with backtracking"

### SJ4-JS-BB4b — ARB and ARBNO (greedy loops)

- [ ] SJ4-JS-BB4b-i — Implement `bb_arb()` and `bb_arbno(body)`
- [ ] SJ4-JS-BB4b-ii — Test: `ARBNO(ANY)` matches zero or more chars
- [ ] SJ4-JS-BB4b-iii — Commit: "SJ4-JS-BB4b: greedy loops"

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


