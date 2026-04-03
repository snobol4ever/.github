# MILESTONE-JVM-SNOBOL4.md — SNOBOL4 × JVM Milestone Ladder

**Session:** J · **Work file:** `src/backend/emit_jvm.c` (one4all)
**Milestone ladder:** this file · **Baseline:** `94p/32f` (J-216, `a74ccd8`)

---

## The architectural distinction that drives everything

`snobol4jvm` (Clojure) and `one4all` JVM backend (`emit_jvm.c`) both target
the JVM — but they implement pattern matching in fundamentally different ways:

**snobol4jvm** — interpreted frame walker:
`match.clj` `engine` takes a pattern tree as *data* and walks it at runtime
using a 7-element frame vector `[Σ Δ σ δ Π φ Ψ]`, dispatching on
`:proceed/:succeed/:recede/:fail` actions.  The pattern tree is data; the
engine loop is code.  One engine handles all patterns.

**one4all emit_jvm.c** — compiled pure Byrd boxes:
`emit_jvm_pat_node()` compiles each pattern AST node to *Jasmin labels*
at compile time.  α/γ/ω are literal JVM goto targets baked into the `.class`
file.  There is no interpreter loop at runtime — the compiled class IS the
Byrd box graph.  This is the same model as `emit_byrd_asm.c` targeting x86:
same IR, same labeled-goto structure, different instruction set.

**Consequence for oracles:**

| What | Oracle | Why |
|------|--------|-----|
| 5-phase semantics — what each phase must produce | `snobol4jvm/runtime.clj` + `match.clj` | Proven at 1,896 tests / 4,120 assertions / 0 failures |
| Phase 2+3 implementation — how to emit compiled Byrd boxes | `emit_byrd_asm.c` | Same compiled-label model, same IR, same corpus |
| Inline expression strategy | `snobol4jvm/jvm_codegen.clj` Stage 23E | IFn inlining maps to Jasmin inline bytecode |
| EVAL/CODE dynamic compilation | `snobol4jvm/compiler.clj` CODE | re-entrant parse→emit→load pipeline |

`snobol4jvm` is the **semantic oracle**.
`emit_byrd_asm.c` is the **structural oracle** for pattern emission.
Both must be read before writing any new pattern or EVAL/CODE code.

---

## The 5-phase statement executor

Every SNOBOL4 statement executes in exactly five phases:

```
Phase 1: build_subject  — resolve subject variable or expr → String (local L6)
Phase 2: build_pattern  — pattern AST → compiled Byrd box label graph
Phase 3: run_match      — scan loop drives root box α labels; captures collected
Phase 4: build_repl     — replacement expression → value already on stack
Phase 5: perform_repl   — splice into subject, sno_var_put, take :S/:F branch
```

The compiled class for a pattern statement IS Phases 2+3 — the label graph
runs directly, no dispatch overhead.  `snobol4jvm/runtime.clj` RUN loop
defines what must happen in each phase; `emit_byrd_asm.c` defines how it
compiles to labeled gotos.

---

## Oracle Read Order (before writing any pattern or EVAL/CODE code)

```bash
# Semantic oracle — what phases must produce
sed -n '35,110p' snobol4jvm/src/SNOBOL4clojure/runtime.clj     # RUN loop: Phase 1+5
sed -n '1,30p'   snobol4jvm/src/SNOBOL4clojure/match.clj        # engine API + frame model
grep -n "CAPTURE\|pending-cond\|commit" snobol4jvm/src/SNOBOL4clojure/match.clj  # Phase 5 captures

# Structural oracle — how to compile Byrd boxes to labeled gotos
grep -n "case E_QLIT\|case E_SEQ\|case E_ALT\|case E_ARBNO\|emit_asm_pat" \
    src/backend/emit_byrd_asm.c | head -20                       # x86 pattern node emitter
sed -n '2990,3070p' src/backend/emit_jvm.c                       # JVM scan loop + local layout

# Inline-emit oracle — expression strategy
sed -n '170,250p' snobol4jvm/src/SNOBOL4clojure/jvm_codegen.clj # inline-emit! patterns

# EVAL/CODE oracle
sed -n '119,188p' snobol4jvm/src/SNOBOL4clojure/compiler.clj    # CODE! + CODE
sed -n '465,490p' snobol4jvm/src/SNOBOL4clojure/operators.clj   # EVAL dispatch
```

---

## M-JVM-INTERP — Dynamic JVM Byrd Box Interpreter (Phase 0)

**Rationale:** Build a JVM equivalent of `scrip-interp.c` (DYN- session) + `scrip-interp.cs` (NET INTERP session) in Java. Use `src/runtime/boxes/bb_*.java` directly at runtime instead of emitting Jasmin bytecode. Eliminates compile+link cycle from test loop.

**Architecture: stack machine + Byrd box sequencer**

The interpreter has two distinct execution engines that map directly to what the emitter will later compile:

```
NON-PATTERN execution (Phases 1, 4, 5 + all non-pattern statements):
  Stack machine — operand stack + IR instruction dispatch
  IR opcodes: PUSH_VAR, PUSH_LIT, CALL, ASSIGN, BRANCH_S, BRANCH_F, ...
  Maps directly to JVM stack bytecode in emit_jvm.c later

PATTERN execution (Phases 2 + 3):
  Byrd box sequencer — interprets bb_*.java graph by dispatching α/β/γ/ω signals
  PatternBuilder.java builds bb_*.java graph from IR PatNode tree
  BbExecutor.java sequences through boxes: α=proceed, β=backtrack, γ=succeed, ω=fail
  Maps directly to labeled-goto Jasmin bytecode in emit_jvm.c later
```

**Design invariant:** Every interpreter operation has a 1:1 correspondence to an emitter operation. The interpreter proves the semantics; `emit_jvm.c` serializes the same operations to Jasmin. No interpreter-only constructs.

**Pipeline:**
```
.sno file
  → Lexer.java        → token stream
  → Parser.java       → StmtNode[] (typed Java AST)
  → IrBuilder.java    → IR instruction list (stack machine ops) + PatNode subtrees
  → Interpreter.java
      Phase 1: stack machine resolves subject → String
      Phase 2: PatternBuilder builds bb_*.java graph from PatNode IR
      Phase 3: BbExecutor sequences α/β/γ/ω through box graph (scan loop)
      Phase 4: stack machine evaluates replacement → value
      Phase 5: stack machine splices, commits captures, takes :S/:F branch
  → output
```

**No scrip-cc. No JNI. No Jasmin.** Java frontend produces IR directly.

**Oracles:**
- `src/frontend/snobol4/lex.c` + `parse.c` — lexer/parser structure oracle
- `scrip-interp.c` + `stmt_exec.c` — eval loop + bb_build() oracle
- `src/backend/emit_jvm.c` + `emit_byrd_asm.c` — emitter oracle (what interpreter ops must map to)
- `MILESTONE-NET-INTERP.md` — parallel C# interpreter; same structure
- `MILESTONE-DYN-INTERP.md` — C reference interpreter milestone chain

**Current milestone count:** 9 total (M-JVM-INTERP A01–A05 + 7 existing milestones A01-PARITY)

**M-JVM-INTERP breakdown:**

### M-JVM-INTERP-A01: Lexer
- `src/driver/jvm/Lexer.java` — tokenize SNOBOL4 source
- Token types mirror `src/frontend/snobol4/lex.c` token enum
- **Oracle:** `src/frontend/snobol4/lex.c`
- **Gate:** All 19 NET-INTERP parse test inputs tokenize without error

### M-JVM-INTERP-A02: Parser
- `src/driver/jvm/Parser.java` — recursive descent, produces `StmtNode[]`
- Typed Java AST nodes: `StmtNode`, `ExprNode`, `PatNode` (mirror C AST structs)
- **Oracle:** `src/frontend/snobol4/parse.c` + `MILESTONE-NET-INTERP.md §Pidgin parser`
- **Gate:** 19/19 parse test cases produce correct AST (pretty-print matches reference)

### M-JVM-INTERP-A03: IR Tree
- `src/driver/jvm/IrBuilder.java` — lowers typed AST → IR instruction list + PatNode subtrees
- **Stack machine IR:** typed opcode nodes (`PUSH_VAR`, `PUSH_LIT`, `CALL`, `ASSIGN`, `BRANCH_S`, `BRANCH_F`, etc.) — one opcode per future JVM bytecode sequence
- **Pattern IR:** `PatNode` tree with same node kinds as `PATND_t` in scrip-cc — consumed by PatternBuilder
- IR node design must have 1:1 correspondence to emit_jvm.c operations (design invariant)
- **Oracle:** `src/runtime/dyn/stmt_exec.c bb_build()` (lines 407–640) + `src/backend/emit_jvm.c`
- **Gate:** IR pretty-prints cleanly for all 19 parse test inputs; each opcode maps to a named emit_jvm.c operation

### M-JVM-INTERP-A04: Interpreter + Byrd Box Sequencer + Test Harness
- `src/driver/jvm/Interpreter.java` — dispatches stack machine IR opcodes (Phases 1, 4, 5)
- `src/driver/jvm/PatternBuilder.java` — walks PatNode IR → instantiates `bb_*.java` graph (Phase 2)
- `BbExecutor.java` sequences α/β/γ/ω signals through box graph (Phase 3) — already exists ✅
- `SnobolEnv.java` — variable store (`Map<String, SnobolValue>`)
- Corpus runner: `test/run_interp_jvm.sh` — diff vs SPITBOL oracle
- **Oracle:** `stmt_exec.c` 5-phase loop + `bb_executor.java` + `MILESTONE-DYN-INTERP.md`
- **Gate:** ≥ 20 corpus smoke tests pass (rung1); ready for M-JVM-INTERP-A05

### M-JVM-INTERP-A05: Baseline Verification
- Target: match `scrip-interp.c` behavior across full corpus
- Establish interpreter as rapid testbed for M-JVM-A02+ compiled path
- **Gate:** ≥ 94p broad corpus (matches DYN- baseline); ready to proceed to M-JVM-A02

---

## Java Byrd Box runtime — `src/runtime/boxes/bb_*.java`

**Written J-217. 29 files. one4all `7c35456`.**

Every C box (`bb_lit.c`, `bb_seq.c`, ...) now has a Java sibling in the
same directory (`bb_lit.java`, `bb_seq.java`, ...) plus `bb_box.java`
(base class, `Spec`, `MatchState`) and `bb_executor.java` (5-phase driver).

```
bb_lit.c    bb_lit.s    bb_lit.cs    bb_lit.java
bb_seq.c    bb_seq.s    bb_seq.cs    bb_seq.java
... (all 25 boxes, 4 languages, one snake_case name)
bb_box.h                             bb_box.java
bb_bal.c    bb_bal.s                 bb_bal.java  ← C stub; Java real
                                     bb_executor.java
```

`bb_bal.java` is the first real BAL implementation (C original is a stub).

**Before wiring into `emit_jvm.c`:** Lon reviews `bb_seq.java` (β wiring)
and `bb_arbno.java` (64-frame stack) for correctness.

**These are the M-JVM-B01 implementation atoms.** Each milestone in Phase 2
maps directly to instantiating the corresponding Java box class.

---

## Current state of `emit_jvm_pat_node()`

Already implemented (pre-pivot work):
- `E_QLIT` — `regionMatches` + cursor advance + γ/ω
- `E_SEQ` — right-fold, ARB+backtrack greedy loop, deferred capture commit
- `E_ALT` — cursor-save, try left, restore, try right
- `E_CAPT_COND_ASGN` (`.var`) — deferred capture with temp local
- `E_CAPT_IMMED_ASGN` (`$var`) — immediate `sno_var_put` on γ
- `E_CAPT_CURSOR` (`@var`) — cursor position capture
- `ARBNO(child)` — greedy loop with zero-advance guard
- `ANY(charset)`, `NOTANY(charset)` — `charAt` + `contains`
- Scan loop with `&ANCHOR` check and cursor retry

**The Byrd box compilation infrastructure is substantially built.**
The 32 failures at 94p/32f are not pattern-engine gaps — they are value-layer
and DATA/function gaps in the non-pattern paths (rung8 strings, rung10
functions, rung11 DATA, 2D subscript).

---

## Phase 1 — Value Layer Completion

### M-JVM-A01 — Scaffold through goto/branching ✅

**Status:** Done (J0–J3, pre-pivot). 94p/32f baseline.

---

### M-JVM-A02 — Value layer complete + 2D subscript fix

**Depends on:** M-JVM-A01
**Oracle:** `snobol4jvm/runtime.clj` + `jvm_codegen.clj` inline-emit patterns
**Scope:**
- **2D subscript bug**: `E_IDX` write path (`emit_jvm_stmt` lines ~2658–2700) —
  fix `nchildren>=3` case to build `"row,col"` composite key.
  Read `emit_byrd_asm.c` lines ~3530–3570 first (structural co-oracle).
- String builtins: `REPLACE`, `DUPL`, `REVERSE`, `TRIM`, `SUBSTR`, `LPAD`, `RPAD`
- `E_INDR` (`$expr` indirect reference) full round-trip
- `&STLIMIT`/`&STCOUNT` ✅ already landed J-216

**Gate:** rung8 (strings) all pass · global driver diff clean · ≥ 100p

---

### M-JVM-A03 — DATA + functions + RETURN/NRETURN

**Depends on:** M-JVM-A02
**Oracle:** `snobol4jvm/runtime.clj` + `operators.clj` INVOKE dispatch
**Scope:**
- `DATA` constructor calls → `sno_array_new` + field stores
- `DATA` field accessor calls → `sno_array_get(instance, fieldname)`
- `DATATYPE(N)` for DATA instances → check `__type__` key
- `DEFINE` / user-defined functions / `RETURN` / `FRETURN` / `NRETURN`
- Recursive functions: per-invocation stack frame (Near-Term Bridge model
  from `ARCH-overview.md` — same as x86 `emit_byrd_asm.c`)

**Gate:** rung10 (functions) · rung11 (DATA) all pass · ≥ 120p

---

## Phase 2 — Pattern Completion (Byrd Box Gaps)

The compiled Byrd box infrastructure already exists.
These milestones fill the remaining pattern primitive gaps.

### M-JVM-B01 — Remaining pattern primitives

**Depends on:** M-JVM-A03
**Oracle:** `emit_byrd_asm.c` pattern node cases (structural) + `match.clj` primitives (semantic)
**Scope:**
- `SPAN(cs)`, `BREAK(cs)`, `BREAKX(cs)` — cursor-advance loops
- `LEN(n)` — advance cursor by n chars
- `POS(n)`, `RPOS(n)` — absolute/relative position assert
- `TAB(n)`, `RTAB(n)` — advance-to-column
- `REM` — match everything to end
- `BAL` — balanced parentheses match
- `FENCE` — one-way door (blocks β backtrack)
- `FAIL`, `SUCCEED`, `ABORT` — control primitives
- `E_REF` (`*X`) — pattern-valued variable dereference

**Gate:** rung6 (all patterns) · rung7 (captures) all pass · ≥ 136p

---

### M-JVM-B02 — Full backtracking (β port)

**Depends on:** M-JVM-B01
**Rationale:** Current `emit_jvm_pat_node` ALT uses cursor-save/restore but
does not implement true β (resume) backtracking for nodes that can produce
multiple matches (SPAN, BREAK, BREAKX in backtrack context).
**Oracle:** `emit_byrd_asm.c` β label emission for SPAN/BREAK/ARBNO
**Scope:**
- β labels for SPAN, BREAK, BREAKX: on β, shrink match by 1 and re-offer
- β for ARBNO: already has greedy loop; add proper backtrack shrink path
- Verify: `SPAN('abc') . X` correctly captures shrinking spans on backtrack

**Gate:** rung6 backtrack-dependent tests pass · ≥ 140p

---

## Phase 3 — EVAL / CODE

### M-JVM-C01 — EVAL() / CODE()

**Depends on:** M-JVM-B02
**Oracle:** `snobol4jvm/compiler.clj` CODE function — parse→IR→inject into live table.
On JVM: re-enter `scrip-cc -jvm`, emit `.j` snippet, assemble via `jasmin.jar`
(already on path), load with a new `ClassLoader`, wire goto target.
**Scope:**
- `sno_eval(str)` — re-entrant parse + emit expression → class → invoke → String
- `sno_code(str)` — re-entrant parse + emit statement block → class → jump
- Wire into `jvm_emit_builtin()` dispatch for EVAL/CODE names

**Gate:** rung9 EVAL/CODE tests pass · ≥ 142p (x86 gate parity)

---

### M-JVM-PARITY — Full corpus parity

**Depends on:** M-JVM-C01
**Gate:** `snobol4_jvm` = 126/126 (all non-xfail tests) ✅

---

## Sprint Sequence

| Sprint | Milestone | Key work |
|--------|-----------|----------|
| J-220 | M-JVM-INTERP-A01 | Lexer.java — tokenize SNOBOL4 source · oracle: lex.c |
| J-221 | M-JVM-INTERP-A02 | Parser.java — recursive descent → StmtNode[] · oracle: parse.c |
| J-222 | M-JVM-INTERP-A03 | IrBuilder.java — AST → IR nodes · PatternBuilder.java → bb_*.java |
| J-223 | M-JVM-INTERP-A04 | Interpreter.java 5-phase loop · SnobolEnv · corpus runner |
| J-224 | M-JVM-INTERP-A05 | Baseline verification vs scrip-interp.c · ≥94p broad |
| J-225 | M-JVM-A02 | 2D subscript fix · rung8 strings · global driver clean |
| J-226 | M-JVM-A03 part 1 | DATA constructor/field/DATATYPE · rung11 |
| J-227 | M-JVM-A03 part 2 | DEFINE/functions/RETURN/FRETURN/NRETURN · rung10 |
| J-228 | M-JVM-B01 | SPAN/BREAK/LEN/POS/TAB/REM/BAL/FENCE/FAIL/REF |
| J-229 | M-JVM-B02 | β backtrack for SPAN/BREAK/BREAKX/ARBNO |
| J-230 | M-JVM-C01 | EVAL()/CODE() re-entrant pipeline |
| J-231 | M-JVM-PARITY | Full corpus sweep + xfail audit |

---

## How snobol4jvm and emit_byrd_asm.c relate to emit_jvm.c

```
snobol4jvm/runtime.clj  ─── semantic oracle ──→  emit_jvm.c
  "what Phase N must produce"                     (Jasmin text)
                                                       ↑
emit_byrd_asm.c  ─────── structural oracle ──→  emit_jvm.c
  "how compiled Byrd boxes                    same labeled-goto
   look as labeled gotos"                      model, JVM opcodes
```

`snobol4jvm` proves the semantics are right.
`emit_byrd_asm.c` proves the compilation strategy is right.
`emit_jvm.c` applies both to produce Jasmin.

---

*MILESTONE-JVM-SNOBOL4.md — written J-217 pivot, 2026-04-02, Claude Sonnet 4.6.*
*Key insight: one4all JVM emits pure compiled Byrd boxes (labeled gotos), not*
*an interpreted frame walker. emit_byrd_asm.c is the structural oracle.*
*snobol4jvm is the semantic oracle only.*
