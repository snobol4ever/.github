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

## Step 0 — Delete All Interpreter Code (Current)

- [ ] SJ4-JS-BB0a — Delete sno_engine.js entirely; replace with comment explaining why
- [ ] SJ4-JS-BB0b — Delete pattern-interpreter sections from sno_runtime.js (pat_lit, pat_any, pat_span, exec_stmt, sno_engine require)
- [ ] SJ4-JS-BB0c — Replace deleted sections with stubs that throw "NOT IMPLEMENTED: Byrd-box pattern factories"
- [ ] SJ4-JS-BB0d — Update RULES.md to add permanent rule against restoring interpreter code
- [ ] SJ4-JS-BB0e — Commit: "SJ4-JS-BB0: delete interpreter code, stubs only"

After Step 0: Tests should fail at pattern operations with "NOT IMPLEMENTED" (no silent success via interpreter).

---

## Step 1 — Build Pattern Factory Closures (SJ4-JS-BB1)

Each SM_PAT_* opcode emits a **factory function** that returns a pattern object:

```javascript
// Example: PAT_lit("hello") emits:
function PAT_lit_FACTORY_N() {
    return {
        alpha(state) { ... },
        beta(state, text) { ... },
        gamma(state) { ... },
        omega(state) { ... }
    };
}
```

- [ ] SJ4-JS-BB1a — Implement `emit_pat_lit_factory()` in emit_js.c
- [ ] SJ4-JS-BB1b — Implement factory helpers for LIT, ANY, NOTANY, SPAN, BREAK, LEN, POS, RPOS, TAB, RTAB
- [ ] SJ4-JS-BB1c — Test: emit a simple `"hello"` pattern, verify factory structure in JS output
- [ ] SJ4-JS-BB1d — Implement `emit_pat_seq_factory()` (concatenation) — wires child factories
- [ ] SJ4-JS-BB1e — Implement `emit_pat_alt_factory()` (alternation)
- [ ] SJ4-JS-BB1f — Commit: "SJ4-JS-BB1: pattern factories for basic operators"

---

## Step 2 — Implement Pattern Execution Harness (SJ4-JS-BB2)

SM_EXEC_STMT pops the pattern factory from the stack and builds a **runner**:

```javascript
case SM_EXEC_STMT:
    // Pattern factory on stack, subject on stack
    // Emit code that instantiates the factory and runs the match
    fprintf(out, "rt.exec_pattern(subj_name, has_repl);");
```

- [ ] SJ4-JS-BB2a — Implement `rt.exec_pattern(subj_name, has_repl)` runtime function
- [ ] SJ4-JS-BB2b — Implement pattern state machine runner (follows α→β/γ/ω transitions)
- [ ] SJ4-JS-BB2c — Implement capture-variable commit/discard on success/failure
- [ ] SJ4-JS-BB2d — Test: match "hello" against "hello world", verify capture
- [ ] SJ4-JS-BB2e — Commit: "SJ4-JS-BB2: pattern execution harness"

---

## Step 3 — Backtracking and Choice Points (SJ4-JS-BB3)

Implement ALT (alternation) with backtracking:

- [ ] SJ4-JS-BB3a — Implement choice-point stack for ALT branches
- [ ] SJ4-JS-BB3b — Implement ω-port (fail) to pop choice point and try next
- [ ] SJ4-JS-BB3c — Test: `"a" | "b"` matches against "a" and "b" separately
- [ ] SJ4-JS-BB3d — Test backtracking: `(ARBNO(ANY) . REM)` enumerates positions
- [ ] SJ4-JS-BB3e — Commit: "SJ4-JS-BB3: backtracking and choice points"

---

## Step 4 — User-Defined Functions in Patterns (SJ4-JS-BB4)

Implement `SM_PAT_USERCALL` — deferred function calls:

- [ ] SJ4-JS-BB4a — Implement `exec_pattern_usercall(fname, args)` runtime
- [ ] SJ4-JS-BB4b — Integrate with pattern match engine (check ω on function failure)
- [ ] SJ4-JS-BB4c — Test: pattern with `*func()` call
- [ ] SJ4-JS-BB4d — Commit: "SJ4-JS-BB4: user-defined functions in patterns"

---

## Step 5 — Ladder Climbing (SJ4-JS-BB5)

Incrementally improve test-suite pass count:

- [ ] SJ4-JS-BB5a — Target PASS ≥ 10 (basic patterns)
- [ ] SJ4-JS-BB5b — Target PASS ≥ 25 (alternation + backtrack)
- [ ] SJ4-JS-BB5c — Target PASS ≥ 40 (user functions + complex patterns)
- [ ] SJ4-JS-BB5d — Target PASS ≥ 49 (parity with baseline)
- [ ] SJ4-JS-BB5e — Target PASS ≥ 60 (ladder climb)
- [ ] SJ4-JS-BB5f — Commit at each milestone

---

## State

```
watermark: SJ4-JS-BB0 (deletion phase, stubs only)
head: one4all (pre-deletion baseline PASS=49)
next: SJ4-JS-BB0a — delete sno_engine.js
```

---

## Key Invariants

- **Pattern factories MUST emit as JavaScript functions**, not data structures
- **NO interpreter code** (sno_engine.js, no re-adding pattern interpreter path)
- **Byrd semantics ONLY** — α/β/γ/ω ports, choice-point stack, frame save/restore
- **SM_EXEC_STMT must emit JS code that instantiates and runs the pattern harness**, not call an interpreter
- **Every pattern factory is isolated** — can be understood without reading interpreter code

---

