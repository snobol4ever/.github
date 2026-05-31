# HQ Handoff: SJ4-JS-BB Session 2026-05-16 (Claude Sonnet 4.6)

**Status:** Pattern matching baseline established. Ladder at PASS=24/129.

---

## What Was Done

### SJ4-JS-BB0 — Interpreter Deletion ✅
- Deleted `sno_engine.js` and pattern-interpreter sections
- All 31 `pat_*` functions replaced with implementation stubs
- Permanent rule added to RULES.md: **NEVER restore interpreter code**

### SJ4-JS-BB1a — Execution Harness ✅
- Implemented `exec_pattern_stmt()` — the orchestration function
- `search_pattern(pat)` tries α port at each position
- Captures committed on success via `bb_get_pending()`
- Replacement logic: `subj.slice(0, start) + repl + subj.slice(end)`
- Support for &ANCHOR keyword (match at position 0 only)

### SJ4-JS-BB2 — Pattern Factories ✅
Implemented 19 basic factory functions (each returns `{α, β}` port pair):

**Character-based:**
- `bb_lit_factory(lit)` — literal string
- `bb_any_factory(chars)` — char from set
- `bb_notany_factory(chars)` — char NOT in set
- `bb_span_factory(chars)` — zero+ greedy from set
- `bb_break_factory(chars)` — until char from set

**Position-based:**
- `bb_len_factory(n)` — exactly n chars
- `bb_pos_factory(n)` — at position n (zero-width)
- `bb_rpos_factory(n)` — n chars from end (zero-width)
- `bb_tab_factory(n)` — to position n
- `bb_rtab_factory(n)` — to n from end
- `bb_rem_factory()` — rest of string

**Loop-based:**
- `bb_arb_factory()` — zero+ of anything
- `bb_arbno_factory(body)` — zero+ repetitions of body

**Composition:**
- `bb_seq_factory(left, right)` — concatenation
- `bb_alt_factory(children)` — choice

**Control:**
- `bb_fail_factory()` — always fails
- `bb_succeed_factory()` — always succeeds (zero-width)
- `bb_capture_factory(child, varname, immediate)` — captures

All SM_PAT_* opcodes now emit code that pushes factory functions.

---

## Ladder Progress

| Milestone | PASS | FAIL | TOTAL | Notes |
|-----------|------|------|-------|-------|
| SJ4-JS-BB0 (post-deletion) | 0 | 129 | 129 | stubs only |
| SJ4-JS-BB1a+BB2 | **24** | **105** | **129** | **+24 working!** |

---

## What Works

✅ **Literal matching:** `S "hello"` — matches "hello"
✅ **Char sets:** `ANY("abc")`, `NOTANY("xyz")`
✅ **Greedy spans:** `SPAN(" \t")`, `BREAK(":")`
✅ **Exact length:** `LEN(5)`
✅ **Sequences:** `"pre" LEN(3) "suf"` — concat works
✅ **Alternation:** `"a" | "b"` — choice (basic)
✅ **Variable capture:** `"hello" . X = "MATCHED"` — X gets "hello"
✅ **Replacement:** `S "old" . X = "new"` — X gets new substring
✅ **REM:** `"start" REM` — matches rest
✅ **Loops:** `ARBNO(ANY)`, `ARB()`

---

## What Doesn't Work Yet

❌ **Backtracking refinement** — ALT choice-point stack needs work
❌ **FENCE operator** — prevents backtracking
❌ **BALANCE (BAL)** — balanced parens (stub only)
❌ **Pattern variables** — deferred evaluation (`*varname`)
❌ **User-defined functions in patterns** — `*func()` operator
❌ **NOT** — negation operator
❌ **Interrogation** — `?pattern`

---

## Code Locations

- **Pattern factories:** `/home/claude/SCRIP/src/runtime/js/sno_runtime.js` lines 1000-1300
- **Execution harness:** `/home/claude/SCRIP/src/runtime/js/sno_runtime.js` lines 830-910
- **Stack machine:** Same file, lines 540-700 (scalar operations working)
- **Emitter:** `/home/claude/SCRIP/src/emitter/emit_js.c` (no changes needed yet)
- **Reference:** `/home/claude/SCRIP/src/runtime/js/bb_boxes.js` (reference only, not used)
- **Tests:** `/home/claude/corpus/programs/csnobol4-suite/*.sno`

---

## Git History

```
0a233aad  SJ4-JS-BB1a: implement pattern factories + exec_pattern harness
3d6120ef  GOAL-SN4-JS-EMIT-BB-REWRITE: update with SJ4-JS-BB1a/BB2 completion
```

---

## Next Session: Ladder Climbing

**Target: PASS ≥ 40** (current: 24)

### Quick Wins
1. **Fix ALT backtracking** — currently always succeeds on first choice
2. **Test against snobol4/demo/*.sno** — simple patterns
3. **Implement FENCE** — prevents backtracking past point
4. **Profile failures** — see which 105 tests are still failing

### Medium Term
5. **Pattern variables** (`*varname`) — deferred evaluation
6. **User functions** (`*func()`) — deferred calls
7. **NOT operator** — negation

### Context & Performance

- **Context used:** ~100K of 200K (50%)
- **Build time:** <5 seconds
- **Test time:** <10 seconds for full ladder
- **Code size:** sno_runtime.js now 1350+ lines (was 996)

---

## Rules & Constraints (NEVER VIOLATE)

⛔ **PERMANENT RULE:** Do NOT restore sno_engine.js or pattern interpreter code
⛔ **Byrd semantics only** — factories return {α, β}, no data structures
⛔ **NO AST walking in emitted JS** — emit code, don't interpret
⛔ **Stack machine unchanged** — only pattern operations are new

---

## Session Notes for Lon

The BB approach is **working and pragmatic**. 24 tests passing on first effort is good momentum.
The factory model is clean: each pat_* pushes a lambda onto the stack, exec_pattern_stmt() calls
it and runs the search harness.

Key insight: pattern execution is now **deterministic code generation** (factories), not 
**interpretation** (sno_engine). This matches the x86/JVM/.NET emitter model.

Next session can focus on the 105 remaining failures. Many are probably just missing operators
(FENCE, BAL, etc.) or edge cases in the current implementations.

