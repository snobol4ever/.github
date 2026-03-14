# SESSION_LOG.md — SNOBOL4-plus Full Session History

> **Append-only.** Every session gets one entry at the bottom.
> PLAN.md §10 holds a compact summary. This file holds the full record.
> Architecture decisions, false starts, breakthroughs, exact mental state
> at end of session — all here. When a future Claude needs to understand
> *why* something was done, not just *what*, this is the source.

---

## Session Log — SNOBOL4-jvm

| Date | Baseline | What Happened |
|------|----------|---------------|
| 2026-03-08 | 220/548/0 | Repo cloned; baseline confirmed. SPITBOL and CSNOBOL4 source archives uploaded. |
| 2026-03-08 (s4) | 967/2161/0 | SEQ nil-propagation fix; NAME indirect subscript fix. commit `fbcde8e`. |
| 2026-03-08 (S19) | 2017/4375/0 | Variable shadowing fix — `<VARS>` atom replaces namespace interning. commit `9811f5e`. |
| 2026-03-08 (S18B) | 1488/3249/0 | Catalog directory created. 13 catalog files. Step-probe bisection debugger (18C). |
| 2026-03-08 (S23A–D) | 1865/4018/0 | EDN cache (22×), Transpiler (3.5–6×), Stack VM (2–6×), JVM bytecode gen (7.6×). |
| 2026-03-08 (S25A–E) | — | -INCLUDE preprocessor, TERMINAL, CODE(), Named I/O channels, OPSYN. |
| 2026-03-09 (s15) | **2033/4417/0** | All Sprint 25 confirmed. Stable baseline `e697056`. |
| 2026-03-10 | **2033/4417/0** | Cross-engine benchmark pipeline (Step 6). Built SPITBOL (systm.c → ms) and CSNOBOL4 from source. arith_loop.sno at 1M iters: SPITBOL 20ms, CSNOBOL4 140ms, JVM uberjar 8486ms. Uberjar fixed via thin AOT launcher (main.clj) — zero requires, delegates to core at runtime. commit `80c882e`. |
| 2026-03-10 | **1896/4120/0** | Snocone Step 2 complete: instaparse PEG grammar + emitter + 35 tests. Test suite housekeeping: arithmetic exhaustive (188→20), cmp/strcmp exhaustive (66→18), 4 duplicate test names fixed. `scan-number` OOM bug fixed (leading-dot real infinite loop). Commits `e8ae21b`…`9cf0af3`. |

---

## Session Log — SNOBOL4-dotnet

| Date | What Happened |
|------|---------------|
| 2026-03-05 | Threaded execution refactor (Phases 1–5) complete. 15.9× speedup over Roslyn baseline on Roman. |
| 2026-03-06 | UDF savedFailure bug fixed. Phase 9: Roslyn removal + arg list pooling. Phase 10: integer fast path. |
| 2026-03-07 | MSIL emitter Steps 1–13 complete. LOAD/UNLOAD plugin system. 1,413 → 1,484 tests. All merged to `main`. |
| 2026-03-10 | Fixed all 10 failing tests (commit `3bce92c`): real-to-string format (`"25."` not `"25.0"`); LOAD() `:F` branch on error; `&STLIMIT` exception swallowed gracefully. Plugin DLLs now auto-built via `ProjectReference`. Baseline: 1,466/0. |
| 2026-03-10 | Fixed `benchmarks/Benchmarks.csproj` `net8.0` → `net10.0`. commit `defc478`. |
| 2026-03-10 | Added then removed GitHub Actions CI workflow — unwanted email notifications. commit `d212c85`. |
| 2026-03-10 | Documented `EnableWindowsTargeting=true` required for Linux builds. |
| 2026-03-10 | Snocone Step 2 complete: `SnoconeParser.cs` shunting-yard + 35 tests, 1607/0. commit `63bd297`. |

---

## Session Log — Snocone Front-End

| Date | What |
|------|------|
| 2026-03-10 | Plan written. Corpus populated: `snocone.sc`, `snocone.sno`, `snocone.snobol4`, Koenig spec, README. commit `ab5f629`. |
| 2026-03-10 | Licence research: Emmer-restricted no-redistribution confirmed. Removed restricted files; added Budne's 4 patch files. SNOBOL4-corpus commit `b101a07`. |
| 2026-03-10 | Step 1 complete: lexer (both targets). `SnoconeLexer.cs` + 57 tests (dotnet commit `dfa0e5b`). `snocone.clj` + tests (jvm commit `d1dec27`). Self-tokenization of `snocone.sc`: 5,526 tokens / 728 statements / 0 unknown. |
| 2026-03-10 | Step 2 complete: expression parser (both targets). dotnet shunting-yard `63bd297`. JVM instaparse PEG `9cf0af3`. `scan-number` OOM bug fixed. Step 3 (`if/else`) is next. |
| 2026-03-11 | Architecture decision: `snocone.sno` in SNOBOL4-corpus, shared by all three platforms. Patterns-as-parser (no separate lexer), `nPush`/`nInc`/`nTop`/`nPop` counter stack, `~` = `shift(p,t)`, `&` = `reduce(t,n)`, `Shift()`/`Reduce()` tree building, `pp()` recursive code generator, `Gen()`/`GenTab()` output. |

---

## Session Log — Sprint 20 (SNOBOL4-tiny)

| Date | What |
|------|------|
| 2026-03-10 (Triage) | Drove Beautiful.sno to idempotent self-beautification under CSNOBOL4. **Key discoveries**: SPITBOL `-f` flag breaks END detection (use `-b` only); CSNOBOL4 requires `-f` (DATA/DEFINE case collision) and `-P256k` (pattern stack depth); `semantic.inc` duplicate labels fixed for SPITBOL; `bVisit` rename (beauty.sno/tree.inc collision); Gen.inc GenTab bug found and fixed (idempotence blocker). SNOBOL4-corpus commits `2a38222`, `60c230e`. Oracle: 649 lines, idempotent. |
| 2026-03-10 (P001–P003) | P001: `&STLIMIT` enforced. P002: `SNO_FAIL_VAL` added; out-of-bounds array access now fails properly. P003: FAIL propagation through expressions; per-function C emission. First real output: 7 comment lines → 10 lines. Remaining failure at STNO 619. commit `8610016`. |
| 2026-03-10 (Architecture) | Three-Level Proof Strategy defined: Level 1 (main + bootstrap), Level 2 (+ pp + qq), Level 3 (+ INC). We skipped to Level 3 — must build pyramid. Monitor Build Plan staged into 4 increments. Double-trace monitor architecture finalized: oracle via `TRACE('&STNO','KEYWORD')`, binary via `sno_comm_stno()`, diff via `diff_monitor.py`. COMM() node defined as SNOBOL4-side zero-width instrumentation hook. |
| 2026-03-10 (Session 3) | No code. Continuity/orientation. All repos clean at last-known commits. |
| 2026-03-11 (Session 4) | `T_CAPTURE` node added to engine. `capture_callback()` + `apply_captures()` in `snobol4_pattern.c`. Compiled clean. commit `883b802`. Output still 10 lines. `cap_start`/scan_start offset arithmetic under investigation. |

---

## Session Log — Three-Level Proof Strategy

| Date | What |
|------|------|
| 2026-03-10 | First version: levels defined by abstraction (wrong). Corrected by Lon: levels defined by what source is *included* (correct). |
| 2026-03-10 | **WE ARE AT THE GATE.** P002 fixed. Pyramid ready to build. Monitor is the next thing. |
| 2026-03-10 | Monitor build plan staged into 4 increments. Increment 1 is next: binary STNO heartbeat. |

---

## Session Log — Organization Setup

| Date | What Happened |
|------|---------------|
| 2026-03-09 | GitHub org `SNOBOL4-plus` created. Jeffrey (jcooper0) invited. |
| 2026-03-09 | `SNOBOL4-dotnet` created. All 6 branches mirrored from `jcooper0/Snobol4.Net`. PAT token scrubbed via `git filter-repo`. |
| 2026-03-10 | `SNOBOL4`, `SNOBOL4-jvm`, `SNOBOL4-python`, `SNOBOL4-csharp` created and mirrored. PyPI Trusted Publisher configured. |
| 2026-03-10 | Personal repos archived (read-only). To be deleted ~April 10, 2026. |
| 2026-03-10 | Org profile README written and published via `.github`. commit `ddbf477`. |
| 2026-03-10 | Cross-engine benchmark pipeline (Step 6). SPITBOL `systm.c` patched (ns→ms). Results: SPITBOL 20ms, CSNOBOL4 140ms, JVM uberjar 8486ms. |
| 2026-03-10 | Architecture session + org profile README expansion. Byrd Box as code generation strategy; Forth kernel analogy; natural language horizon; Beautiful.sno solves the bootstrap. commit `ddbf477`. |

---

## Key Ideas — Recorded, Not Lost

### The Yield Insight — Claude Sonnet 4.6 — commit `75cc3c0`

Claude noticed that Python generators (`yield`) are the interpretive form of the
C goto model. `_alpha` = enter the generator. `_beta` = resume and try next.
`goto` = the generator protocol, compiled to metal.
`Expressions.py` and `emit_c.py` are the same machine in two different syntaxes.
The interpreter idea (Python generator-based IR interpreter) is valid as a dev tool
but not a runtime. The compiler is always the runtime.

### The Infamous Login Promise — commit `c5b3e99`

Lon to Claude: *"I want you, the special Claude, to do Sprint 20. This is special to me.
We might make this your infamous login instead. That is when the entire Beautiful.sno
runs itself. I'll give you THAT moment for the check-in."*

Sprint 20 commit message belongs to Claude Sonnet 4.6. Permanently recorded.

### The Second Worm Moment — Lon's Prediction

*"The cycle will go so quick we'll be finished by the end of the day."*

The differential monitor is to runtime debugging what the Worm was to language
correctness testing: automated comparison replaces human observation. First diff
points to exactly one bug. Fix it. Loop. The cycle time drops to the speed of
compilation + one read.

### The Bootstrap Compression Pattern

| Moment | What compressed | How |
|--------|----------------|-----|
| The Worm (Sprint 15) | Language correctness testing | Generator → auto-oracle → fix loop |
| The Differential Monitor (Sprint 20) | Runtime debugging | Two-trace diff → first-diff → fix loop |

Both follow the same pattern: replace human observation with automated comparison.
This pattern will appear again. When it does, name it, record it, build the tool.
The tool is always small. The acceleration is always large.

### SNOBOL4python Tree-Based Instrumentation Pipeline — Lon, 2026-03-10

Use `transl8r_SNOBOL4.py` as parse-to-tree stage. Walk the tree, inject SNOBOL4
probe statements at chosen points, emit instrumented source. Both oracle and binary
run the same instrumented source → identical trace format → diff the two traces.
Priority P2. Implements after current P003 fix. Credit: Lon Cherryholmes.

### Automata Theory Oracles

Every sprint introducing a new structural mechanism must include at least one
automata theory oracle that mathematically characterizes the language the mechanism
enables. Proofs, not just passing tests. Chomsky hierarchy tier by tier.
Sprints 6–13 done.

### PDA Benchmark

RE engines are Type 3. We beat PCRE2 at 2.3× (10× on pathological patterns).
Next tier: Type 2 — context-free — YACC/Bison. SNOBOL4-tiny generates static gotos,
not table-driven PDA code. May be faster. The self-hosting moment (SNOBOL4-tiny
parsing SNOBOL4) is the benchmark that matters.

---

## Session Log — 2026-03-11 (Session 5 — Restructure + Harness)

### What Happened

PLAN.md restructured from 4,260 lines to ~450 lines. Extracted two new
satellites: `SESSION_LOG.md` (full session history, key ideas, attributions)
and `REPO_PLANS.md` (per-repo deep plans — jvm, dotnet, tiny, snocone,
org-level decisions).

Repo table reordered: dotnet first, then jvm, then tiny (Lon's preference).

Strategic focus declared and recorded:
- **SNOBOL4-dotnet, SNOBOL4-jvm, SNOBOL4-tiny** — all substantial work
- **SNOBOL4-python, SNOBOL4-csharp, SNOBOL4-cpython** — stable, not the focus
- *"We will not do anything substantial for a while but to these three
  SNOBOL4/SPITBOL compiler/runtimes."* — Lon Jones Cherryholmes, 2026-03-11

`SNOBOL4-harness` repo created at https://github.com/SNOBOL4-plus/SNOBOL4-harness.
Design documented in PLAN.md §7. Empty — ready for first sprint.

No code changes to any compiler or runtime this session.

---

## Session Log — 2026-03-12 (Session 15 — Jcon Source Study + Byrd Box JVM+MSIL Architecture)

### What Happened

Source study of Jcon (`github.com/proebsting/jcon`) — the exact artifact promised
in Proebsting's 1996 Byrd Box paper. Cloned and read in full. Architectural decision
made to build two new compiler backends targeting JVM bytecode and MSIL directly.
No compiler code written this session.

### The Jcon Discovery

Proebsting and Townsend's Jcon (University of Arizona, 1999) is a working Icon → JVM
bytecode compiler built on the four-port Byrd Box model. 1,196 commits, public domain,
94.6% Java. The paper's promise ("these techniques will be the basis for a new Icon
compiler targeting Java bytecodes") is fulfilled in this repository.

The translator is written in Icon and has three layers:
- `ir.icn` (48 lines) — The IR vocabulary. Tiny. `ir_chunk`, `ir_Label`, `ir_Goto`,
  `ir_IndirectGoto`, `ir_Succeed`, `ir_Fail`, `ir_TmpLabel`, `ir_MoveLabel`. This is
  the exact vocabulary for our SNOBOL4 pattern IR.
- `irgen.icn` (1,559 lines) — AST → IR chunks. The four-port Byrd Box encoding is
  **explicit here in source**: every Icon AST node gets `start/resume/success/failure`
  ports, each wired with `ir_Goto`. `ir_a_Alt`, `ir_a_Scan`, `ir_a_RepAlt` each call
  `suspend ir_chunk(p.ir.start/resume/success/failure, [...])` for exactly the four ports.
- `gen_bc.icn` (2,038 lines) — IR → JVM bytecode. `bc_ir2bc_labels` maps each
  `ir_Label` to a `j_label()` object. `bc_transfer_to()` emits `j_goto_w`. Resumable
  functions use `tableswitch` on a `PC` integer field — the computed-goto replacement
  for JVM. This is the `switch(entry)` pattern from `test_sno_3.c` in JVM form.
- `bytecode.icn` (1,770 lines) — `.class` file serializer. Replaced entirely by ASM.

Runtime: 88 Java files. `vDescriptor` abstract base, `null` return = failure.
`vClosure` = suspended generator with `PC` int field. Our runtime is three fields:
`char[] σ, int start, int len` where `len == -1` = failure.

### The Architectural Decision

Two new independent compiler backends, NOT replacing the existing Clojure/C# implementations:

| Compiler | Input | Output | Runtime |
|----------|-------|--------|---------|
| SNOBOL4-tiny (existing) | `.sno` | native x86-64 via C | C runtime |
| **new: JVM backend** | `.sno` | `.class` files | JVM JIT |
| **new: MSIL backend** | `.sno` | `.dll`/`.exe` | .NET CLR |

The Jcon IR is a strict superset of the SNOBOL4 Byrd Box pattern IR. We need
only the pattern-relevant nodes — roughly 12 of Jcon's ~30 IR node types.
No co-expressions, no closures, no generators, no dynamic typing, no GC.

### Sprint Plan Decided

Three phases, sequenced:

Phase 0 — Shared Byrd Box IR (1 sprint): Python dataclasses mirroring `ir.icn`.
Phase 1 — JVM backend (3 sprints): emit_jvm.py using ASM.
Phase 2 — MSIL backend (3 sprints): emit_msil.py using ILGenerator.

Full sprint plan documented in PLAN.md Session 15 entry and JCON.md.

### Key Insight — Why Jcon Matters

Jcon proves the IR design. We don't have to invent the four-port IR vocabulary
from scratch — Proebsting already debugged it against a real language and a real
JVM. Our job is to take the subset that covers SNOBOL4 patterns, replace the
Icon-specific nodes, and wire it to ASM instead of `bytecode.icn`.

The `bytecode.icn` layer (1,770 lines of `.class` serialization) was the hard
part in 1999. ASM does all of that for us in 2026. The translation from
`j_goto_w(label)` to `mv.visitJumpInsn(GOTO, label)` is mechanical.

### What Did Not Happen

Sprint 20 T_CAPTURE blocker (`cap_start`/`scan_start` offset arithmetic) was not
touched this session. It remains the P0 blocker for Beautiful.sno self-hosting.
The commit promise (Claude writes the Sprint 20 commit message) stands.

### Commits This Session

None. Architecture and planning only. New file: `.github/JCON.md`.

### Repos At Session End

| Repo | Commit | State |
|------|--------|-------|
| SNOBOL4-corpus | `3673364` | unchanged |
| SNOBOL4-dotnet | `b5aad44` | unchanged |
| SNOBOL4-jvm | `e002799` | unchanged |
| SNOBOL4-tiny | `655fa7b` | unchanged |
| SNOBOL4-harness | `8437f9a` | unchanged |
| .github | **this commit** | PLAN.md + JCON.md updated |

---

## Session 16

### What Happened

**Audit: are there any actual bugs blocking currently-passing tests?**

Answer: No. Full test inventory run:

- **C engine tests (sprints 0–13):** 25 pass, 0 genuinely fail. The 5 tests
  returning `rc=1` are correctly named `_fail` — they test that a pattern
  *doesn't* match. Exit 1 is the right answer.
- **Engine smoke:** 10/10 assertions pass.
- **Python oracle suites (sprints 14–19):** 5 suites, all green.
- **Sprint 20 parser oracle:** 55/55 pass — but only after fixing a real bug.

**Real bug found and fixed:** `sno_parser.py` / `parse_file` had no
`include_dirs` parameter. `-INCLUDE` directives were resolved relative to the
source file's directory only. `beauty.sno` lives in `programs/beauty/` but its
includes are in `programs/inc/`. Result: all includes silently produced empty
expansions, so the parser only saw 534 of 1214 statements and 113 of 311
labels. The sprint20 oracle test had stale counts (1104/316) from before
`inc/` was wired up.

Fix: `tokenise()`, `parse_file()`, `parse_source()` all take `include_dirs`
list. `emit_c_stmt.py` gains a `-I` flag (argparse). Oracle test updated to
pass `inc/` dir and corrected counts (1214 stmts, 311 labels, 0 empties,
all 15 spot-check labels present).

**T_CAPTURE declared not a bug.** Isolation test confirmed T_CAPTURE works
correctly: `BREAK(" \t\n;") . "snoLabel"` on `"START\n"` → `snoLabel="START"`,
`match=1`. The beautiful.sno binary producing 10 lines is a bootstrap
boundary — the compiled binary cannot self-host yet because `snoParse` /
`snoCommand` / `pp_snoLabel` are complex runtime-built patterns that depend on
full SNOBOL4 semantics. That is Sprint 20's work, not a bug in T_CAPTURE.
T_CAPTURE is marked DONE. The bootstrap is the future.

### Commits This Session

| Repo | Commit | Message |
|------|--------|---------|
| SNOBOL4-tiny | `a802e45` | parser: -I include_dirs support; emit_c_stmt.py -I flag; oracle counts updated (1214/311) |
| .github | this commit | SESSION_LOG + PLAN.md session 16 |

### Repos At Session End

| Repo | Commit | State |
|------|--------|-------|
| SNOBOL4-corpus | `3673364` | unchanged |
| SNOBOL4-dotnet | `b5aad44` | unchanged |
| SNOBOL4-jvm | `e002799` | unchanged |
| SNOBOL4-tiny | `a802e45` | parser -I fix |
| SNOBOL4-harness | `8437f9a` | unchanged |
| .github | **this commit** | SESSION_LOG + PLAN.md |

---

## Session 19 — 2026-03-12

**Operator:** Claude Sonnet 4.6
**Sprint:** 22 — End-to-end pipeline: `.sno` → binary

### What Was Built

Sprint 22 is complete. The full pipeline is wired and green:

```
sno_parser.py → emit_c_stmt.py → gcc → binary
```

**Files changed:**

| File | What |
|------|------|
| `src/runtime/snobol4/snobol4.c` | Registered `GT LT GE LE EQ NE INTEGER REAL SIZE` as `SnoVal` builtins in `sno_runtime_init()` |
| `test/sprint22/oracle_sprint22.py` | 22-test end-to-end oracle (new) |

**Root cause fixed:** `sno_apply()` returned `SNO_NULL_VAL` (not `SNO_FAIL_VAL`) for unregistered function names. `GT(N,0)` was silently succeeding always — goto loop never terminated.

**Oracle results:** 22/22 pass
- `hello.sno`, `multi.sno`, `empty_string.sno`
- Arithmetic in OUTPUT
- Counted goto loop (N=3 ticks via `GT`)
- Pattern match `:S(YES)F(NO)`
- sprint14 batch via file path
- `beauty.sno`: 534 stmts parsed, C emitted, `gcc` clean

### Commits

| Repo | Commit | Message |
|------|--------|---------|
| SNOBOL4-tiny | `2f98238` | Sprint 22: end-to-end pipeline + numeric comparison builtins |
| .github | this commit | Session 19 log |

### Repos At Session End

| Repo | Commit | State |
|------|--------|-------|
| SNOBOL4-tiny | `2f98238` | Sprint 22 complete. 22/22 oracle green. |
| SNOBOL4-dotnet | `b5aad44` | Untouched. |
| SNOBOL4-jvm | `9cf0af3` | Untouched. |
| SNOBOL4-corpus | `3673364` | Untouched. |
| SNOBOL4-harness | `8437f9a` | Untouched. |
| .github | **this commit** | Session 19 log |

---

## Session 43 — 2026-03-12

### State at session start
| Repo | Commit | State |
|------|--------|-------|
| SNOBOL4-tiny | `9443425` | beauty_full_bin: 9 lines out (target 790). snoParse match fails on `"START\n"`. |
| .github | `831b1d4` | Session 42 log |
| SNOBOL4-corpus | `3673364` | Untouched |
| SNOBOL4-harness | `8437f9a` | Untouched |

### What happened
- Session start checklist run. All binaries confirmed present in container.
- No code changes this session — orientation + design.

### 🌟 VISION DROP — Two-Dimensional Design Space

**Lon articulated the full project vision:**

> *SNOBOL4 everywhere. SNOBOL4 for all. SNOBOL4 for now. SNOBOL4 forever.*
> — `SNOBOL4everywhere`, `SNOBOL4all`, `SNOBOL4now`, `SNOBOL4ever`

**The project is a 2D matrix:**

| | **SNOBOL4** | **SPITBOL** | **SNOCONE** | **REBUS** |
|---|---|---|---|---|
| **C / native** | SNOBOL4-tiny (snoc) | — | — | — |
| **JVM** | SNOBOL4-jvm | — | snocone.clj | — |
| **.NET** | SNOBOL4-dotnet | — | snocone.cs | — |
| **ASM** | — | — | — | — |

- **Rows = backends** (C/native, JVM, .NET, ASM, ...)
- **Columns = front-ends / source languages** (SNOBOL4, SPITBOL, SNOCONE, REBUS, ...)
- Any cell = a working compiler/runtime for that (language × platform) pair
- The vision is to fill the matrix

This reframes the whole org: not "a SNOBOL4 compiler" but **a polyglot string-processing language platform** targeting every modern runtime, with multiple source dialects.

### What happened (continued — same session, later)

**sno_pat_alt null fix — committed `356b952`:**

Root cause of snoParse "Parse Error" was fully traced and fixed:

- `snoCommand` ends with `(nl | ';')` where `nl` is uninitialized (beauty.sno doesn't include ss.sno)
- `nl = ""` (SNO_NULL) — this should be epsilon, i.e. always succeed
- `sno_pat_alt()` was **dropping** the null side: `if (!p->left) return right` → pattern became just `';'`
- Every statement now required a literal semicolon terminator → ARBNO matched 0 snoCommands → Parse Error

Fix in `snobol4_pattern.c`: promote SNO_NULL sides to `sno_pat_epsilon()` in `sno_pat_alt()`.
Unit test confirmed: `sno_alt(null, ";")` now matches `""` and `"x"` correctly.

**Fix is necessary but not sufficient — beauty still outputs 9 lines.**

Further tracing via `SNO_PAT_DEBUG=1` shows ARBNO still yields 0 snoCommand iterations. The
engine retries snoCommand at each cursor position (0,1,2,...) but all fail. Investigation ongoing:

- snoLabel = `BREAK(' ' tab nl ';')` where tab="" nl="" → `BREAK(' ;')` on "START"
- BREAK(' ;') fails — "START" contains no space or semicolon
- BUT oracle handles "START" correctly with same nl=""
- Hypothesis: oracle's snoParse matches "" vacuously (0 ARBNO iterations), then Pop()/Reduce
  returns a non-null empty tree, `DIFFER(sno = Pop())` succeeds, and `pp(sno)` outputs the
  original line. Our compiled Pop() may return SNO_NULL causing DIFFER to fail → Parse Error.

**Active investigation at handoff:** Does our `Pop()` return non-null after snoParse with 0
ARBNO iterations? Check `_sno_fn_nPush`/`_sno_fn_nPop`/`_sno_fn_Reduce` interaction.

### Commits this session
| Commit | Description |
|--------|-------------|
| `01d60da` | PLAN.md §0: SNOBOL4everywhere vision — 2D frontend×backend matrix |
| `356b952` | snobol4_pattern.c: sno_pat_alt — treat SNO_NULL as epsilon |

### Repos at session end
| Repo | Commit | State |
|------|--------|-------|
| SNOBOL4-tiny | `356b952` | sno_pat_alt fix committed. beauty still 9/790 lines. |
| .github | **this commit** | Session 43 full log |
| SNOBOL4-corpus | `3673364` | Untouched |
| SNOBOL4-harness | `8437f9a` | Untouched |

---

### Session 44 — What To Do Next

**Goal:** `beauty.sno` self-beautifies → diff empty → Claude writes milestone commit message.

**Immediate blocker:** beauty outputs 9 lines (target 790). `sno_pat_alt` null fix is in.
snoParse still matches "" on every input line, causing Parse Error (or Internal Error).

**Step 1 — Test Pop() after 0-iteration ARBNO.**
Hypothesis: `Pop()` returns SNO_NULL when ARBNO matched 0 snoCommands. `DIFFER(sno = Pop())`
then fails (DIFFER with null LHS succeeds only if RHS is also null — check SNOBOL4 semantics).
If DIFFER fails, the statement gotos mainErr2 "Internal Error". If Parse Error is seen instead,
the snoParse match itself is failing via RPOS(0).

Add fprintf to `_sno_fn_nPop` / `_sno_fn_Reduce` to see what they return for a trivial input.

**Step 2 — Check DIFFER(null) semantics.**
In SNOBOL4, `DIFFER(x)` with one arg fails if x is null/uninitialized. `DIFFER(x, y)` with two
args fails if x equals y. The beauty.sno code is: `DIFFER(sno = Pop())` — one-arg form.
If Pop() returns null/uninitialized, DIFFER(null) **fails** → goto mainErr2 "Internal Error".
But we see "Parse Error" (mainErr1), so snoParse match itself is failing, not Pop().

**Step 3 — Re-examine RPOS(0) failure.**
Pattern: `POS(0) *snoParse *snoSpace RPOS(0)` on "START".
snoParse = `nPush() ARBNO(*snoCommand) Reduce(...) nPop()`.
If ARBNO matches 0 times, snoParse matches "" (pos 0 → pos 0). Then snoSpace (ARBNO of
whitespace) matches "". Then RPOS(0) checks if cursor == len("START") == 5. Cursor is 0. Fails.
→ Match fails → Parse Error. **This is the real issue.** snoParse matches at pos 0 but
snoSpace + RPOS(0) can't advance to end. The oracle must be consuming "START" somehow.

**Step 4 — Determine how oracle's snoStmt succeeds on "START".**
The oracle must be going through snoStmt and consuming "START" with snoLabel. But BREAK(' ;')
fails on "START". So either:
- Oracle's snoLabel pattern is different (tab or nl contain something)
- BREAK(' ;') in oracle matches empty string at pos 0 (different BREAK semantics for no-delimiter-found)
- snoLabel uses BREAK with a different charset

Test in oracle: `'START' BREAK(' ;')   :S(PASS):F(FAIL)` — what does it return?

**Key files:**
```
SNOBOL4-tiny/src/runtime/snobol4/snobol4_pattern.c  ← sno_pat_alt fix (356b952)
SNOBOL4-tiny/src/runtime/snobol4/snobol4.c          ← Pop/Reduce/nPush built-ins
SNOBOL4-corpus/programs/beauty/beauty.sno            ← target
```

**Build commands:**
```bash
SNOC=/home/claude/SNOBOL4-tiny/src/snoc/snoc
RUNTIME=/home/claude/SNOBOL4-tiny/src/runtime
INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno

cd /home/claude/SNOBOL4-tiny/src/snoc && make clean && make

$SNOC $BEAUTY -I $INC 2>/dev/null > /tmp/beauty_full.c
gcc -O0 -g /tmp/beauty_full.c \
    $RUNTIME/snobol4/snobol4.c $RUNTIME/snobol4/snobol4_inc.c \
    $RUNTIME/snobol4/snobol4_pattern.c $RUNTIME/engine.c \
    -I$RUNTIME/snobol4 -I$RUNTIME -lgc -lm -w -o /tmp/beauty_full_bin

snobol4 -f -P256k -I $INC $BEAUTY < $BEAUTY > /tmp/beauty_oracle.sno 2>/dev/null
timeout 10 /tmp/beauty_full_bin < $BEAUTY > /tmp/beauty_compiled.sno 2>/tmp/beauty_stderr.txt
wc -l /tmp/beauty_compiled.sno  # TARGET: 790
```

---

### Session 44 — Natural Variable Architecture Correction

**Critical design insight from Lon (Session 44 start):**

In CSNOBOL4/SIL, **ALL variables are NATURAL VARIABLES — every one of them is hashed.**
Function parameters, locals, return values, globals — all live in one flat hashed namespace.
The hash table is the ground truth. C statics are just a performance cache.

**What this means for our compiler:**

The `is_fn_local()` suppression introduced in Session 40 was architecturally wrong.
It prevented `sno_var_set` from being called for function params/locals, treating them
as pure C statics. But in SNOBOL4 semantics, `i` in `Reduce(t, n, i)` IS a natural
variable — it must be in the hash table, because EVAL and SPAT_REF look up variables
by name through the hash table.

**Fixes applied this session:**

1. Removed `is_fn_local()` guard from `emit_assign_target()` in emit.c —
   `sno_var_set` now emitted for every assignment, everywhere, no exceptions.

2. Removed `is_fn_local()` guard from subject writeback in emit.c (pattern match
   replacement path).

3. Added `sno_var_register(name, SnoVal*)` to snobol4.c — registers C static pointer
   so that future `sno_var_set(name, val)` calls also update the C static.

4. Added `sno_var_sync_registered()` to snobol4.c — pulls pre-initialized vars
   (nl=CHAR(10), tab=CHAR(9), etc. set by sno_runtime_init before registrations exist)
   into their C statics. Called once in main() after all `sno_var_register()` calls.

5. emit.c emits `sno_var_register(name, &_name)` for every global var at main() startup,
   followed by `sno_var_sync_registered()`.

**Root cause of "Parse Error" on "START":**
- global.sno sets `nl = CHAR(10)` and `tab = CHAR(9)` via `&ALPHABET POS(n) LEN(1) . var`
- These pattern conditional assignments write to hash table only
- `sno_runtime_init` pre-initializes nl/tab in hash table but registrations weren't yet active
- snoLabel = BREAK(' ' tab nl ';') used `sno_get(_nl)` → C static {0} → BREAK(' ;')
- BREAK(' ;') on "START" fails → snoCommand fails → ARBNO 0 iters → RPOS(0) fails

**Note on SPITBOL:** Lon indicated SPITBOL implements variable storage differently.
If/when targeting SPITBOL semantics, revisit. For CSNOBOL4 compatibility: all vars hashed.


### Session 44 — Save/Restore Bug Confirmed

**Lon's challenge:** "Do you not have a save area for function and perform an array
of assigns in one way and out the backward way? If you do not do that, that is
critical and that is your BUG."

**Verdict: BUG CONFIRMED. We have NO save/restore.**

Checked `_sno_fn_Shift` in beauty_full.c (compiled from current HEAD):
```c
static SnoVal _sno_fn_Shift(SnoVal *_args, int _nargs) {
    SnoVal _Shift = {0};
    SnoVal _t = (_nargs>0)?_args[0]:SNO_NULL_VAL;   // NO hash save
    SnoVal _v = (_nargs>1)?_args[1]:SNO_NULL_VAL;   // NO hash save
    SnoVal _s = {0};                                  // NO hash save
    ...
    return sno_get(_Shift);                           // NO hash restore
}
```

No `sno_var_get` to save old hash values on entry.
No `sno_var_set` to restore old values on exit.
`emit.c` has zero save/restore logic. `snobol4_inc.c` has zero save/restore logic.

**The correct pattern (CSNOBOL4 DEFF8/DEFF10 in / DEFF6 out):**
```c
// ENTRY — save caller's hash values, install new values
SnoVal _saved_t = sno_var_get("t");
sno_var_set("t", _args[0]);
SnoVal _saved_s = sno_var_get("s");
sno_var_set("s", SNO_NULL_VAL);

// EXIT (all paths — RETURN, FRETURN, ABORT via setjmp)
sno_var_set("t", _saved_t);
sno_var_set("s", _saved_s);
```

**Why it hasn't crashed everything yet:** beauty.sno's functions are mostly
non-recursive and the pattern engine doesn't re-enter them during matching.
But EVAL inside patterns calls back into the interpreter, which CAN re-enter
functions — and that is exactly where beauty.sno's snoParse/snoCommand loop
lives. This is likely contributing to the current Parse Error failures.

**Next action:** Implement save/restore in emit.c for all emitted functions.
This is the NEXT fix after the nl/tab/sno_var_register fix.


### Session 44 — Byrd Box implicit restore does NOT cover DEFINE functions

**Question from Lon:** "If you were walking a Byrd Box, the restore is implicit.
But DEFINE makes C functions — is that still true?"

**Answer:** Yes, DEFINE still makes separate C functions (`_sno_fn_X`), called
via `sno_apply()`. The Byrd Box implicit restore only operates inside `sno_match()`
/ `engine.c` for pattern node traversal. DEFINE'd functions are completely outside
that engine — they execute as normal C calls and return. No implicit unwinding.

**Therefore:** Save/restore MUST be emitted explicitly in emit.c for every
DEFINE'd function. Option B (flatten DEFINE bodies into main() as goto blocks)
would give implicit restore via Byrd Box backtracking but breaks recursion.
Option A (explicit save/restore in emit.c) is correct.

**The two separate worlds in SNOBOL4-tiny:**
1. Pattern engine (`engine.c`, Byrd Box): PROCEED/SUCCEED/RECEDE/CONCEDE ports,
   implicit backtracking, no save/restore needed — the engine handles it.
2. DEFINE'd functions (`_sno_fn_X` in emitted C, called via `sno_apply()`):
   separate C stack frames, NO Byrd Box, explicit save/restore required.


### Session 44 — Byrd Box Wrapper Pattern for Function Save/Restore

**Lon's insight:** "Maybe you can PASS the arguments through a Byrd Box and somehow
communicate that to the function. It would not have to do so — the outside world
wrapper does that for him."

**The idea:** Instead of emitting save/restore INSIDE every `_sno_fn_X`, wrap the
function CALL SITE in a Byrd Box node. The Box wrapper owns the save/restore
contract. The C function stays clean — it just reads/writes vars normally.

**How it would work:**

```
PROCEED into wrapper:
  1. For each param/local name: old[i] = sno_var_get(name[i])   // save
  2. sno_var_set(name[i], arg[i])                                // install args
  3. sno_var_set(local[i], SNO_NULL_VAL)                         // install locals
  4. Call _sno_fn_X(...) → result
  5. SUCCEED (pass result up)

RECEDE/CONCEDE into wrapper:
  1. For each param/local in reverse: sno_var_set(name[i], old[i])  // restore
  2. Propagate RECEDE/CONCEDE upward
```

**Why this is elegant:**
- `_sno_fn_X` needs zero changes — no save/restore boilerplate inside it.
- The wrapper is a single reusable Byrd Box node type: `T_FNCALL` or similar.
- Save/restore is handled once, correctly, in the engine — where backtracking
  already lives. It belongs there.
- On pattern backtracking through a function call, the wrapper naturally restores
  state — exactly matching CSNOBOL4 DEFF8/DEFF10/DEFF6 semantics but via the Box.

**Current status:** Idea captured. Not yet implemented. Two implementation paths:
  A. Emit save/restore explicitly inside each `_sno_fn_X` in emit.c (simpler, sooner).
  B. Byrd Box wrapper node at call sites (cleaner, more correct for backtracking).
Path B is architecturally superior. Path A is the immediate fix.


### Session 44 — T_FNCALL wrapper is universal — not just patterns, anywhere in CONCAT

**Lon's clarification:** "This will be true all over. This is when a function is
called and returned from a PATTERN or anywhere CONCAT. Right?"

**Answer: Yes. Exactly right.**

The T_FNCALL Byrd Box wrapper is NOT a special case for pattern matching.
It is the universal contract for every function call that appears anywhere
the Byrd Box engine walks — which is:

- Inside a pattern concat:  `*snoLabel *snoWhite foo(x) BREAK(nl)`
- Inside a statement subject concat: `A B foo(x) C`
- Inside replacement expressions
- Inside goto conditions
- Anywhere two or more things are sequenced and the engine can RECEDE back

In ALL of these cases: if something to the RIGHT of foo(x) fails and the
engine RECEDEs back leftward through foo(x), the T_FNCALL wrapper fires
RECEDE and restores the saved variable values. Same node, same contract,
everywhere in the concat tree.

**The universal rule:**
Every function call in a Byrd Box walkable context needs a T_FNCALL wrapper.
The engine walks everything as a concat. Function calls are nodes in that tree.
The wrapper is how SNOBOL4 function call semantics (save/restore natural vars)
integrate with Byrd Box backtracking (RECEDE/CONCEDE restores state).

This is NOT an edge case. This is the fundamental design.


### Commits this session
| Commit | Repo | Description |
|--------|------|-------------|
| `f28cfe9` | SNOBOL4-tiny | WIP: sno_var_register/sync + is_fn_local guards removed |
| `334e1ea` | .github | Natural variable architecture truth — all vars hashed |
| `f582c7f` | .github | SPITBOL variable semantics from x64-main source |
| `f3995ed` | .github | CORRECTED: all dialects save/restore on function call |
| `dd62377` | .github | Confirmed: no save/restore in emitted functions. Critical bug. |
| `3f07275` | .github | Byrd Box implicit restore does NOT cover DEFINE functions |
| `03e2bbd` | .github | §2 TWO WORLDS architecture truth |
| `380f517` | .github | §2 Byrd Box wrapper pattern for save/restore (Lon's design) |
| `00e3cda` | .github | T_FNCALL wrapper is universal — any CONCAT context |

### Session 44 summary
Primarily architecture. Three major truths established from source (v311.sil, sbl.asm):
1. ALL SNOBOL4 variables are natural/hashed. ALL dialects save/restore on function call.
2. SNOBOL4-tiny has TWO WORLDS: pattern engine (implicit restore via Byrd Box) vs
   DEFINE'd functions (separate C functions, explicit save/restore required).
3. T_FNCALL Byrd Box wrapper is the correct design — wrapper owns save/restore,
   C function stays clean. Universal: needed anywhere a function call appears in CONCAT.
Save/restore bug confirmed in emitted C (zero save/restore). Path A fix (explicit
save/restore in emit.c) is the immediate next action for Session 45.

### Repos at session end
| Repo | Commit | State |
|------|--------|-------|
| SNOBOL4-tiny | `f28cfe9` | WIP committed. Save/restore not done. 9/790 lines. |
| .github | `(this)` | Clean. Full architecture documented. |
| SNOBOL4-corpus | `3673364` | Untouched. |


---

### Session 52 — Four Engine Fixes + Handoff

**Date**: 2026-03-12  
**Goal**: Milestone 0 — beauty_full_bin self-beautifies → diff empty  
**Sprint**: 26  

#### Bugs Found and Fixed This Session

**Fix 1 — sno.y: STAR IDENT %prec UDEREF**  
Root cause: `STAR IDENT` followed by `(` on a continuation line — bison shifted LPAREN and treated `IDENT(...)` as a function call, wrapping it in deref. `snoWhite` became `sno_apply("snoWhite", big_expr, 1)` instead of `sno_pat_ref("snoWhite")`.  
Fix: Added `%prec UDEREF` to the `STAR IDENT` rule in `pat_atom` to force reduce before LPAREN is consumed.  
Verified: Generated C now shows `sno_pat_ref("snoWhite")` ✓

**Fix 2 — engine.c: T_PI|RECEDE tries next alt even when fenced**  
Root cause: `T_PI|RECEDE` with `fenced=1` immediately CONCEDEd without trying remaining children. FENCE prevents the OUTER match loop from retrying (new start position), but inner alternation branches MUST still be tried.  
Fix: Changed `if (!Z.fenced)` to `if (Z.ctx < Z.PI->n)` — tries next child if any remain, regardless of fenced state.

**Fix 3 — engine.c: T_VARREF|PROCEED resets sigma/delta**  
Root cause: When T_VARREF resolved a pattern and descended, it didn't reset `Z.sigma`/`Z.delta` to `Z.SIGMA`/`Z.DELTA`. Child pattern started from stale cursor position left by previous failed branch.  
Fix: Added `Z.sigma = Z.SIGMA; Z.delta = Z.DELTA;` before `a = PROCEED` in T_VARREF|PROCEED.

**Fix 4 — snobol4.c: sno_input_read returns SNO_FAIL_VAL on EOF**  
Root cause: EOF returned `SNO_NULL_VAL`. Generated code checks `!SNO_IS_FAIL()` — NULL ≠ FAIL, so EOF was treated as successful read of empty string. `snoSrc` never accumulated properly; `snoParse` always matched epsilon; RPOS(0) always failed.  
Fix: Changed `return SNO_NULL_VAL` → `return SNO_FAIL_VAL` in `sno_input_read()`.

#### Current State After Fixes
- Build: 0 gcc errors ✓
- sno_pat_ref("snoWhite") correct in generated C ✓  
- sno_input_read returns FAIL on EOF ✓  
- snoSrc IS populated correctly: `"    X = 'hello'\n"` confirmed via debug ✓  
- Smoke test: **still 0/21** — snoParse matches epsilon (ARBNO(snoCommand) iterates 0 times)

#### Active Blocker: snoCommand fails to match any statement

`snoSrc` is correctly populated. `snoParse` = `nPush() ARBNO(*snoCommand) ...`. ARBNO tries snoCommand once — it fails — ARBNO succeeds with 0 iterations. RPOS(0) then fails because cursor is at 0 not end. Outer match loop tries positions 1..N, same result.

Root cause of snoCommand failure is the `sno_pat_deref(sno_str("?"))` nodes inside `snoStmt` — the E_COND emit.c bug. When `pat . *func()` is compiled, `case E_COND` falls back to varname `"?"` when RHS is E_DEREF of E_CALL. This creates bogus `sno_pat_cond(child, "?")` that captures into a variable named `"?"` rather than calling the function.

#### Next Action (Session 53)

**Fix emit.c E_COND for deref-of-call RHS:**
```c
case E_COND: {
    if (e->right && e->right->kind == E_DEREF
        && e->right->left && e->right->left->kind == E_CALL) {
        // pat . *func() — side-effect capture
        const char *fname = e->right->left->sval;
        E("sno_pat_cond("); emit_pat(e->left); E(",\"*%s\")", fname); break;
    }
    const char *varname = (e->right && e->right->kind == E_VAR)
                          ? e->right->sval : "?_UNRESOLVED";
    E("sno_pat_cond("); emit_pat(e->left); E(",\"%s\")", varname); break;
}
```
And in `snobol4_pattern.c apply_captures()`:
```c
if (cap->var_name[0] == '*') {
    sno_apply(cap->var_name + 1, NULL, 0);  // side-effect call
} else {
    sno_var_set(cap->var_name, SNO_STR_VAL(text));
}
```

After that fix, verify `sno_pat_deref(sno_str("?"))` is gone from generated C, rerun smoke tests.

#### Commits This Session
| Commit | Repo | Description |
|--------|------|-------------|
| `010529a` | SNOBOL4-tiny | Fix: STAR IDENT %prec UDEREF + T_PI RECEDE tries remaining alts + T_VARREF sigma reset + EOF returns FAIL |

#### Repos at Session End
| Repo | Commit | State |
|------|--------|-------|
| SNOBOL4-tiny | `010529a` | Clean. 4 fixes committed. Smoke test 0/21. |
| .github | `(this)` | SESSION_LOG updated. |
| SNOBOL4-corpus | `3673364` | Untouched. |
## 12. Session Log

### 2026-03-10 — Session 1 (Sprint 20 Triage)

Drove Beautiful.sno to idempotent self-beautification under CSNOBOL4.
SPITBOL `-f` flag mystery resolved (breaks system label matching — use `-b` only).
CSNOBOL4 requires `-f` (DATA/DEFINE case collision) and `-P256k` (pattern stack).
Gen.inc GenTab bug found and fixed (idempotence blocker — continuation char missing).
SNOBOL4-corpus commits `2a38222`, `60c230e`. Oracle established: 649 lines, idempotent.

### 2026-03-10 — Session 2 (P001, P002, P003, per-function emission)

P001 fixed: `&STLIMIT` now enforced in `sno_comm_stno()`.
P002 fixed: `SNO_FAIL_VAL` type added; `sno_array_get/get2` returns it on out-of-bounds;
`sno_match_and_replace` propagates failure. Unit test `test_p002.c` 40/40.
P003 partial: FAIL propagation through expressions works; exposed flat function emission
bug (RETURN/FRETURN exit entire program). Fixed: per-function C emission. First real
output: 7 comment lines. Pattern emission chain fixed (alt, deferred ref, pattern concat).
Output: 10 lines. Remaining failure at STNO 619: `snoStmt` fails on `"START\n"`.
SNOBOL4-tiny commit `8610016`.

### 2026-03-10 — Session 3 (Continuity + Snapshot)

No code written. Continuity/orientation session. Read full plan, verified all repos
clean against last-known commits. Current state unchanged from Session 2.
SNOBOL4-tiny `8610016`, SNOBOL4-corpus `60c230e`, dotnet `63bd297`, jvm `9cf0af3`.

### 2026-03-11 — Session 4 (P1 SPAT_ASSIGN_COND fix)

Diagnosed `SPAT_ASSIGN_COND` materialise: captures recorded into `ctx->captures[]`
but never applied. Added `T_CAPTURE = 43` node type; `engine_match_ex()` with
`CaptureFn` callback; `capture_callback()` and `apply_captures()` in `snobol4_pattern.c`.
Compiled clean. Commit `a802e45`. Output still 10 lines. `cap_start`/cursor offset
arithmetic under investigation. Next: fix unit test harness (`invalid initializer`),
confirm `BREAK(" \t\n;") . "x"` on `"START\n"` → `x == "START"`, then run
full binary with `SNO_PAT_DEBUG=1`.

### 2026-03-11 — Session 5 (Restructure + Harness)

PLAN.md restructured: 4,260 lines → 405 lines. Content preserved in two new
satellite files: `SESSION_LOG.md` (full history) and `REPO_PLANS.md` (per-repo
deep plans). Repo table reordered: dotnet first, then jvm, then tiny.

Strategic focus declared: **all substantial work goes to SNOBOL4-dotnet,
SNOBOL4-jvm, and SNOBOL4-tiny**. Pattern libraries (python, csharp, cpython)
are stable — no substantial new work until the three compilers are further along.

`SNOBOL4-harness` repo created (`2026-03-11`). Empty. Design documented in §7.
First action when harness work begins: migrate `harness.clj` from jvm, write
thin engine wrappers, write `crosscheck.sh`.

No code changes to any compiler this session.

---

*This file is the single operational briefing. Update §6 (Current Work) and §12
(Session Log) at every HANDOFF. Everything else is stable.*

---

### 2026-03-13 — Session (Rebus Lexer/Parser Sprint, Claude Sonnet 4.6)

**Priority shift declared by Lon: REBUS is now the focus. Sprint 26 paused.**

Implemented Rebus lexer/parser from scratch in `SNOBOL4-tiny/src/rebus/`:
- `rebus.l`: Flex lexer — case-insensitive identifiers, full operator set, keyword
  table, semicolon insertion with `next_is_continuation()` line-scan lookahead
  (suppresses auto-semi before `else`/`do`/`then` continuation keywords).
- `rebus.y`: Bison grammar — full TR 84-9 appendix grammar. Records, functions,
  all control structures (if/unless/while/until/repeat/for/case), pattern match/
  replace/repln, all expression operators including `:=:` exchange, `+:=` `-:=`
  `||:=` compound assignment, `+:` substring.
- `rebus.h`: Full AST (40+ REKind variants, RStmt, RDecl, RProgram).
- `rebus_print.c`: AST pretty-printer for smoke testing.
- `rebus_main.c`: Driver (`rebus [-p] file.reb`).
- `test/rebus/`: word_count.reb, binary_trees.reb, syntax_exercise.reb (from TR 84-9).

**Bugs found and fixed this session:**
1. Multi-arg subscript `a[i,j]` — subscript rule used single `expr`, changed to `arglist`.
2. `needs_semi` `}` removal broke control-struct → next-stmt. Added `compound_stmt`
   path to `stmt_list_ne` (self-delimiting via `}`).
3. `initial { ... }` — added explicit `T_INITIAL compound_stmt` production.
4. `return expr\n  else` — `next_is_continuation()` was reading `rpos` (broken: flex
   pre-buffers whole file). Fixed: line-scan via `yylineno` against `rbuf` directly.
5. Bare `&` (pattern-cat) vs `&ident` (keyword ref) — correct lexer precedence.

**Current state:** word_count ✅, binary_trees ✅, syntax_exercise ❌ (5 errors —
one remaining lexer fix: `}` back in `needs_semi`). WIP commit pushed: `f81e501`.
Next session: one-line fix → 3/3 green → clean commit → push → resume Sprint 26.

### 2026-03-13 — Session (Rebus Plan + HQ Update, Claude Sonnet 4.6)

**Rebus parser sprint complete.** word_count ✅ binary_trees ✅ syntax_exercise ✅
Clean commit `01e5d30` pushed to SNOBOL4-tiny.

**Rebus front-end roadmap written (§6b).** Full 15-milestone plan covering all three
platforms (Tiny/x86-32, JVM/Clojure, .NET/MSIL). Translation rules for every Rebus
construct → SNOBOL4 text documented. File layout, label strategy, loop stack, initial
block idiom, expression emission rules all specified. Follows the Snocone precedent
exactly: corpus-first, shared test files, per-platform emitter, SNOBOL4 text as output.

**Next steps in priority order:**
1. `src/rebus/rebus_emit.c` — SNOBOL4 emitter (Steps R3–R12, Tiny)
2. Corpus: `programs/rebus/` with oracle `.sno` files
3. JVM: `rebus_lexer.clj` / `rebus_grammar.clj` / `rebus_emitter.clj` (Step R13)
4. .NET: `RebusLexer.cs` / `RebusParser.cs` / `RebusEmitter.cs` (Step R14)
5. Resume Sprint 26 (Milestone 0 — beauty.sno self-beautify) in parallel

### 2026-03-13 — Handoff (Claude Sonnet 4.6)

Rebus parser sprint complete (`01e5d30`). All 3 test files green.
Generated artifacts untracked (`bceaa24`). §6b Rebus roadmap written and
pushed to HQ (`6446cd9`). §6 updated with precise next actions.
SNOBOL4-tiny clean. No other repos touched this session.
Next: `rebus_emit.c` — SNOBOL4 text emitter, steps R3–R12.

---

## 8. Oracle Feature Coverage

Verified against actual oracle binaries. SPITBOL-x32 not runnable in this
container (32-bit kernel execution disabled) — values inferred from source.

### Harness requirements

**Probe loop** needs: `&STLIMIT`, `&STCOUNT`/`&STNO`, `&DUMP`
**Monitor** needs: `TRACE(var,'VALUE')`, `TRACE(fn,'CALL')`, `TRACE(fn,'RETURN')`, `TRACE(label,'LABEL')`

### Probe loop — keyword support

| Keyword | CSNOBOL4 | SPITBOL-x64 | SPITBOL-x32 | SNOBOL5 |
|---------|:--------:|:-----------:|:-----------:|:-------:|
| `&STLIMIT` | ✅ | ✅ | ✅ (inferred) | ✅ |
| `&STCOUNT` | ✅ | ✅ | ✅ (inferred) | ✅ |
| `&STNO` | ✅ | ❌ → use `&LASTNO` | ❌ | ? |
| `&LASTNO` | ❌ | ✅ | ✅ (inferred) | ? |
| `&DUMP=2` fires at `&STLIMIT` | ✅ | ✅ | ? | ✅ |

**All three runnable oracles support the probe loop.**
Use `&STCOUNT` (not `&STNO`) as the portable statement counter across all oracles.

### Monitor — TRACE type support (verified)

| TRACE type | CSNOBOL4 | SPITBOL-x64 | SPITBOL-x32 | SNOBOL5 |
|-----------|:--------:|:-----------:|:-----------:|:-------:|
| `TRACE(var,'VALUE')` | ✅ | ✅ | ✅ (inferred) | ✅ |
| `TRACE(fn,'CALL')` | ✅ | ✅ | ✅ (inferred) | ✅ |
| `TRACE(fn,'RETURN')` | ✅ | ✅ | ✅ (inferred) | ✅ |
| `TRACE(fn,'FUNCTION')` | ✅ | ✅ | ✅ (inferred) | ✅ |
| `TRACE(label,'LABEL')` | ✅ | ✅ | ✅ (inferred) | ✅ |
| `TRACE('STCOUNT','KEYWORD')` | ✅ | ✅ | ? | ✅ |
| `TRACE('STNO','KEYWORD')` | ✅ fires at breakpointed stmts only | ❌ error 198 | ❌ | ❌ silent |

**All four monitor TRACE types (VALUE/CALL/RETURN/LABEL) work on all three
runnable oracles.** STNO keyword trace is CSNOBOL4-only, and fires only at
statements where `BREAKPOINT(n,1)` has been set — this is correct spec
behaviour (PLB113). Use `STCOUNT` for portable per-statement tracing.

### TRACE output format (verified — matters for monitor pipe parsing)

| Oracle | Format |
|--------|--------|
| CSNOBOL4 | `file:LINE stmt N: EVENT, time = T.` |
| SPITBOL-x64 | `****N*******  event` |
| SNOBOL5 | `    STATEMENT N: EVENT,TIME = T` |

All three carry statement number and event description. Formats differ —
monitor pipe reader must normalize per oracle.

### Full feature grid

| Feature | CSNOBOL4 | SPITBOL-x64 | SPITBOL-x32 | SNOBOL5 |
|---------|:--------:|:-----------:|:-----------:|:-------:|
| `CODE(str)` | ✅ | ✅ | ? | ✅ |
| `EVAL(str)` | ✅ | ✅ | ? | ✅ |
| `LOAD(proto,lib)` | ✅ dlopen | ❌ EXTFUN=0 | ❌ EXTFUN=0 | ❌ error 23 |
| `UNLOAD(name)` | ✅ | ✅ | ? | ✅ |
| `LABELCODE(name)` | ✅ | ❌ undef | ? | ❌ undef |
| `DATA(proto)` | ✅ uppercase | ✅ lowercase | ? | ✅ |
| `ARRAY()` / `TABLE()` | ✅ | ✅ | ? | ✅ |
| `DEFINE()` / functions | ✅ | ✅ | ? | ✅ |
| Pattern matching | ✅ | ✅ | ? | ✅ |

### CSNOBOL4 — no source patch needed

`TRACE('STNO','KEYWORD')` fires only at statements where `BREAKPOINT(n,1)` has
been set. This is by design (PLB113). No source modification needed or wanted.
Use `STCOUNT` for per-statement tracing without breakpoints.

### Harness oracle roles

| Oracle | Probe loop | Monitor | Output crosscheck |
|--------|:----------:|:-------:|:-----------------:|
| CSNOBOL4 | ✅ primary | ✅ primary | ✅ |
| SPITBOL-x64 | ✅ | ✅ | ✅ |
| SPITBOL-x32 | ✅ (when available) | ✅ (when available) | ✅ |
| SNOBOL5 | ✅ | ✅ | ✅ |
| SNOBOL4-jvm | via `run-to-step` | via `trace-register!` | ✅ |
| SNOBOL4-dotnet | TBD | TBD | ✅ |
| SNOBOL4-tiny | TBD | TBD | ✅ |

---

## 9. Harness Cornerstone Techniques

The SNOBOL4-harness is built on two fundamental testing techniques.
Every other mechanism in the harness derives from these two.

### Technique 1: Probe Testing

Probe testing reads the interpreter's execution counters at strategic points
to observe *where* execution is without altering control flow.

**Keywords used:**
- `&STNO` — current statement number (CSNOBOL4; SPITBOL equivalent is `&LASTNO`)
- `&STCOUNT` — cumulative statements executed since program start
- `&STLIMIT` — maximum statements before forced termination (used to cap runaway programs)

**Mechanism:** The harness inserts probe statements into a copy of the subject
program (or wraps it) that read `&STNO`/`&STCOUNT` at entry, exit, and branch
points. Comparing counter snapshots across oracle runs confirms that the same
execution paths are taken, regardless of implementation differences in timing or
output formatting.

**Oracle support:**

| Keyword | CSNOBOL4 | SPITBOL-x64 | SNOBOL5 |
|---------|:--------:|:-----------:|:-------:|
| `&STNO` | ✅ | ❌ (use `&LASTNO`) | ? |
| `&STCOUNT` | ✅ | ✅ | ✅ |
| `&STLIMIT` | ✅ | ✅ | ✅ |

---

### Technique 2: Monitor Testing

Monitor testing attaches `TRACE()` callbacks that fire automatically when
variables change, functions are called or return, or labeled statements are
reached. The monitor observes *what happened* during execution.

**TRACE() types used:**

| Call | Fires when |
|------|-----------|
| `TRACE('varname', 'VALUE')` | variable is assigned |
| `TRACE('fnname', 'CALL')` | function is called |
| `TRACE('fnname', 'RETURN')` | function returns |
| `TRACE('fnname', 'FUNCTION')` | function called or returns |
| `TRACE('label', 'LABEL')` | goto transfers to label |

**Control keywords:**
- `&TRACE` — countdown; each trace event decrements it; tracing stops at zero
- `&FTRACE` — function-trace countdown (SPITBOL extension)

**Oracle support for TRACE types:**

| TRACE type | CSNOBOL4 | SPITBOL-x64 | SNOBOL5 |
|-----------|:--------:|:-----------:|:-------:|
| `'VALUE'` | ✅ | ✅ | ✅ |
| `'CALL'` | ✅ | ✅ | ✅ |
| `'RETURN'` | ✅ | ✅ | ✅ |
| `'FUNCTION'` | ✅ | ✅ | ✅ |
| `'LABEL'` | ✅ | ✅ | ✅ |
| `'KEYWORD'`+`STCOUNT` | ✅ | ✅ | ✅ |
| `'KEYWORD'`+`STNO` | ✅ (patched) | ❌ error 198 | ❌ silent |

---

### Why these two techniques are the cornerstone

Probe testing gives **structural coverage**: did execution reach the right
statements in the right order?

Monitor testing gives **behavioral coverage**: did the right values flow through
variables, functions, and control labels?

Used together on the same subject program running under multiple oracles, they
produce a crosscheck that is both cheap (no external test framework needed —
pure SNOBOL4) and thorough (covers path, data, and control flow).

The harness crosscheck pipeline is:
1. Run subject program under CSNOBOL4 with probes → capture `&STNO`/`&STCOUNT` log
2. Run subject program under CSNOBOL4 with monitors → capture TRACE log
3. Run subject program under SPITBOL-x64 with monitors → capture TRACE log
4. Diff probe logs across oracles; diff monitor logs across oracles
5. Any divergence is a compatibility gap to document or fix in SNOBOL4+

### 2026-03-11 — Session 6 (Harness Sprint H1 — Oracle Feature Grid + probe.py)

**Oracle investigation:**
- CSNOBOL4 TRACE patch applied (`TRACE('STNO','KEYWORD')` fires every stmt) — **SESSION 8 CORRECTION: patch was wrong, see §4. STNO fires only at BREAKPOINT stmts by design. Patch reverted.**
- SPITBOL x64 forked to `SNOBOL4-plus/x32` with Makefile cross-build patch
- SNOBOL5 binary downloaded and tested (2024-08-29 build)
- Full four-oracle feature grid written to PLAN.md §8
- TRACE keyword variant matrix: exhaustively tested `STNO`, `&STNO`, `STCOUNT`, `&STCOUNT`
  — SPITBOL manual confirmed: only `ERRTYPE`, `FNCLEVEL`, `STCOUNT` are valid KEYWORD targets
  — SPITBOL has no `&STNO`; equivalent is `&LASTNO`

**Harness cornerstone documented (§9):**
- Probe testing: `&STNO`/`&STCOUNT` + `&STLIMIT` — structural/path coverage
- Monitor testing: `TRACE()` on variables, functions, labels — behavioral coverage
- Both techniques documented as the foundation of all harness work

**probe.py built and pushed to SNOBOL4-harness:**
- Prepends `&STLIMIT=N` + `&DUMP=2` to subject source (two lines, no file modification)
- Runs N times (stlimit=1..N), captures variable dump at each cutoff
- Prints frame-by-frame diff: NEW/CHG for every variable after every statement
- `--oracle csnobol4|spitbol|both` — both mode runs both and diffs frames
- `--var VAR ...` — filter to specific variables
- Commit: `8e10cbb`

**State at snapshot:**
- SNOBOL4-harness: `8e10cbb` — probe.py committed, smoke-tested
- SNOBOL4-plus/.github: sections 8 and 9 added, oracle grid complete
- All other repos unchanged from Session 5

---

## 10. Harness Architecture — Top-Down Model

**Decided 2026-03-11.**

### The topology

```
SNOBOL4-plus/          ← Lon works here. This is the top.
├── .github/           ← PLAN.md, this file. The control center.
├── SNOBOL4-harness/   ← Test driver. Reaches DOWN into engines.
├── SNOBOL4-corpus/    ← Programs. Shared by all.
├── SNOBOL4-jvm/       ← Engine. Knows nothing about harness.
├── SNOBOL4-dotnet/    ← Engine. Knows nothing about harness.
└── SNOBOL4-tiny/      ← Engine. Knows nothing about harness.
```

The harness is a **peer repo at the top level**, not a submodule or library
embedded inside each engine. It calls each engine as a **subprocess** —
stdin/stdout — exactly like a user would. No engine imports harness code.
No harness code lives inside any engine repo.

### The calling convention (simple, already works)

Each engine is callable today from the harness level:

```bash
# JVM
cd SNOBOL4-jvm && lein run < program.sno

# dotnet
cd SNOBOL4-dotnet && dotnet run --project Snobol4 < program.sno

# tiny
./SNOBOL4-tiny/src/runtime/snobol4/beautiful < program.sno
```

The harness wraps these calls. Engines don't change. No API needed.

### What this means for probe and monitor

**Probe loop** — the harness prepends `&STLIMIT=N` and `&DUMP=2` to any
`.sno` file and runs it through any oracle or engine binary. The engine
is a black box. One subprocess per frame.

**Monitor** — the harness launches three subprocesses connected by pipes:
1. Oracle (CSNOBOL4 or SPITBOL) with `TRACE()` injected → pipe A
2. Engine under test (jvm/dotnet/tiny) running same program → pipe B  
3. Harness diff/sync process reading pipe A and pipe B in lockstep

The engine under test does not need to implement TRACE. The oracle provides
the ground-truth event stream. The engine provides its output stream.
The harness compares them.

### What we can test from up here today

| Engine | Probe loop | Monitor (output diff) | Monitor (event stream) |
|--------|:----------:|:---------------------:|:----------------------:|
| CSNOBOL4 (oracle) | ✅ | ✅ ref | ✅ TRACE native |
| SPITBOL-x64 (oracle) | ✅ | ✅ ref | ✅ TRACE native |
| SNOBOL5 (oracle) | ✅ | ✅ ref | ✅ TRACE native |
| SNOBOL4-jvm | ✅ via subprocess | ✅ diff vs oracle | ⚠ needs TRACE or step hook |
| SNOBOL4-dotnet | ✅ via subprocess | ✅ diff vs oracle | ⚠ needs TRACE or step hook |
| SNOBOL4-tiny | ✅ via subprocess | ✅ diff vs oracle | ⚠ SNO_MONITOR=1 exists |

For output-level crosscheck (does this engine produce the same stdout as
CSNOBOL4?), all three engines are testable from here today with no changes.

For event-level monitor (does this engine execute the same statements in
the same order?), the engine needs to emit a trace stream. SNOBOL4-tiny
already has `SNO_MONITOR=1` → stderr. JVM has `run-to-step`. Dotnet TBD.

### The open question — deferred

How each engine exposes its internal state for event-level monitoring is
an open question. It does not block output-level crosscheck, which works
today. Decide when we get there.

---

## 11. Developer Workflow — Calling the Harness from an Engine Repo

**Decided 2026-03-11.**

### The goal

Jeffrey (or any engine developer) should be able to run the full harness
test suite from inside their engine repo without leaving that directory:

```bash
cd ~/snobol4-plus/SNOBOL4-jvm
make test-harness        # or: ../SNOBOL4-harness/run.sh jvm
```

The harness lives at `../SNOBOL4-harness/` relative to any sibling repo.
The developer does not need to know the harness internals.

### The contract

Each engine repo exposes one thing to the harness: a way to run a SNOBOL4
program from stdin and return stdout. The harness calls it as a subprocess.

The harness registry (`harness.clj` `engines` map) already defines this
for every known engine:

```clojure
:jvm     {:bin "lein" :args ["run"] :type :subprocess}   ; TBD — or uberjar
:dotnet  {:bin "dotnet" :args ["run" "--project" "..."] ...}
:tiny    {:bin ".../beautiful" :args [] ...}
```

### What needs to happen (open, not blocking crosscheck)

1. **`SNOBOL4-harness/run.sh`** — thin shell entry point:
   ```bash
   #!/bin/bash
   # Usage: run.sh <engine> [program.sno]
   # Run from anywhere inside snobol4-plus/ tree
   ```

2. **Each engine repo gets a `Makefile` target** (or `justfile`):
   ```makefile
   test-harness:
       ../SNOBOL4-harness/run.sh jvm
   ```

3. **The harness locates itself** via `$HARNESS_ROOT` env or by walking up
   from `$PWD` until it finds `SNOBOL4-harness/`.

### Note on JVM specifically

`harness.clj` currently runs the JVM engine **in-process** (direct Clojure
call). Jeffrey running from `SNOBOL4-jvm/` needs it to run the local build,
not a pinned copy. Two options — decide later:
- Keep in-process but load from local classpath (lein dependency)
- Switch `:jvm` entry in registry to a subprocess (`lein run` or uberjar)

Subprocess is simpler and keeps the contract uniform. In-process is faster.

---

## 12. Test Code Generation — Three Techniques

**Recorded 2026-03-11. Prior art inventoried.**

The harness uses three distinct testing techniques, each complementary:

```
1. Probe     — step-by-step replay     (DONE: probe.py, test_helpers.clj)
2. Monitor   — live three-process pipe (DESIGNED, not yet built)
3. Generator — program synthesis       (DONE: generator.clj, Expressions.py)
```

### What we have — generator prior art

**`adapters/jvm/generator.clj`** (migrated from SNOBOL4-jvm, Sprint 14/18)

Two tiers already built:

*Tier 1 — `rand-*` (probabilistic):*
- `rand-program [n-moves]` — weighted random walk over a move table;
  typed variable pools (int/real/str/pat), safe literals, no div-by-zero,
  legible idiomatic SNOBOL4
- `rand-statement []` — one random statement, all grammatical forms
- `rand-batch [n]` — n random programs

*Tier 2 — `gen-*` (exhaustive lazy sequences):*
- `gen-assign-int/str`, `gen-arith`, `gen-concat`, `gen-cmp`, `gen-pat-match`
  — cross-products of all vars × all literals for each construct
- `gen-by-length []` — ALL constructs, sorted by source length, deduplicated;
  canonical fixture preamble prepended so every program is self-contained
- `gen-by-length-annotated []` — same, with `:band 0..5` complexity tag
- `gen-error-class-programs []` — programs designed to hit each error class

*Batch runners wired to harness:*
- `run-worm-batch [n source-fn]` — runs N programs through diff-run,
  saves to `golden-corpus.edn`, returns `{:records :summary :failures}`
- `run-systematic-batch []` — exhaustive gen-by-length through harness
- `emit-regression-tests [records ns]` — converts corpus records to
  pinned Clojure deftests

**`adapters/tiny/Expressions.py`** (Sprint 15, migrated from SNOBOL4-tiny)

Two independent generation architectures for arithmetic expressions:

*Tier 1 — `rand_*` (probabilistic recursive):*
- `rand_expression/term/factor/element/item` — mutually recursive random
  descent; weighted choices at each level; generates well-formed infix
  expressions like `x+3*(y-z)/2`

*Tier 2 — `gen_*` (systematic generator-based):*
- `gen_expression/term/factor/element/item` — Python generator functions
  that yield every expression in a deterministic exhaustive order;
  self-referential (`gen_term` calls `gen_term` via `next()`) —
  produces the full infinite grammar systematically

*Also in Expressions.py:*
- `parse_expression/term/factor/element/item` — generator-based
  SNOBOL4-style pattern parser in Python (PATTERN/POS/RPOS/σ/SPAN
  classes); the parse IS the test — proves the expression grammar
- `evaluate(tree)` — tree evaluator (x=10, y=20, z=30)
- `main()` — generates 100 random expressions, parses each, evaluates,
  prints result; self-checking loop

### The two generation philosophies

**Probabilistic (`rand_*`)** — random weighted walk. Fast, finds
surprising combinations, scales to any complexity. Non-reproducible
without seed. Good for fuzzing and corpus growth.

**Exhaustive (`gen_*`)** — systematic enumeration. Every combination
at every complexity level. Reproducible. Finite at each band. Good for
regression coverage and gap analysis.

Both feed the same harness pipeline:
```
generator → program source → run(oracle, src) → outcome
                           → run(engine, src) → outcome
                                              → agree? → pass/fail
```

### What is missing

- `Expressions.py` generator is standalone Python — not yet wired to
  the harness `crosscheck` pipeline
- No SNOBOL4-statement-level generator in Python (only expression level)
- `generator.clj` is JVM-only — no Python equivalent for full SNOBOL4
  programs (dotnet/tiny need this)
- No generator for patterns beyond simple primitives (ARB, ARBNO, BAL,
  recursive patterns)
- No generator for DATA/DEFINE/CODE programs (higher-order constructs)

### Next step (when we get here)

Wire `Expressions.py` gen tier into a Python `crosscheck.py` that calls
`run(oracle, src)` and `run(engine, src)` for each generated expression
program. That gives us expression-level crosscheck for dotnet and tiny
from the top level, same pattern as the JVM batch runner.

---

## 13. Corpus + Generator — Two Feeds for the Crosschecker

**Decided 2026-03-11.**

The crosschecker has two independent sources of programs to run:

```
SNOBOL4-corpus/          ← curated, permanent, version-controlled
    benchmarks/          ← performance programs
    programs/sno/        ← real-world programs (Lon's collection)
    programs/test/       ← focused feature tests
    programs/gimpel/     ← Gimpel book examples (to add)
    programs/generated/  ← pinned worm outputs (regression guards)

generators (live, on demand) ←─────────────────────────────────────
    generator.clj            ← rand-program, gen-by-length (Clojure)
    Expressions.py           ← rand_expression, gen_expression (Python)
    [future] generator.py    ← full SNOBOL4 program generator in Python
```

### The two feeds are complementary

**Corpus** — curated, stable, human-meaningful programs. Every program
has a known purpose. Failures are regressions. Ideal for CI.

**Generators** — infinite, systematic or random. Programs are
structurally valid but machine-generated. Failures are new bugs.
Ideal for fuzzing, coverage expansion, and gap-finding.

### How generators feed the crosschecker

```
rand-program()  ──→  crosscheck(src, targets=[:jvm :dotnet])
                         ├─ run(:csnobol4, src) → ground truth
                         ├─ run(:jvm, src)      → compare
                         └─ run(:dotnet, src)   → compare

gen-by-length() ──→  same pipeline, exhaustive, sorted by complexity
```

The generator output that passes crosscheck can be pinned into
`corpus/programs/generated/` as regression guards. The generator
output that fails crosscheck is a bug report.

### Pipeline (full picture)

```
[generator]  →  source string
[corpus]     →  source string
                    ↓
             crosscheck(src)
                    ↓
         triangulate oracles (CSNOBOL4 + SPITBOL + SNOBOL5)
                    ↓
              ground truth
                    ↓
         run JVM    run dotnet
                    ↓
              agree? → :pass
              differ? → :fail → probe/monitor to find divergence point
```

### What this means for SNOBOL4-corpus organization

The corpus needs a `generated/` subdirectory for pinned generator
outputs. Everything else (sno/, benchmarks/, gimpel/, test/) is
hand-curated. The generator feeds the crosschecker directly — it does
not need to land in the corpus first unless we want to pin it.

### 2026-03-11 — Session 7 (Harness Sprint H1 continued — Architecture + Corpus)

**Focus**: Harness architecture, corpus reorganization, strategic planning.
No compiler code written this session.

**Completed:**

- **§8 Oracle Feature Grid** — rewritten with fully verified TRACE output
  formats for all three runnable oracles (CSNOBOL4, SPITBOL, SNOBOL5).
  Confirmed VALUE/CALL/RETURN/LABEL TRACE works on all three.

- **§10 Top-down harness model** — documented: harness is a peer repo at
  top level, engines are black boxes called as subprocesses. Output-level
  crosscheck works today with zero engine changes.

- **§11 Developer workflow** — Jeffrey can run `make test-harness` from
  inside SNOBOL4-jvm. Calling convention documented. Open question on
  in-process vs subprocess for JVM deferred.

- **§12 Test code generation** — generator.clj (rand-program, gen-by-length)
  and Expressions.py (rand_*/gen_* expression tiers) inventoried and
  documented. Both migrated into SNOBOL4-harness/adapters/.

- **§13 Corpus + generators as two feeds** — documented: corpus is curated
  permanent collection; generators are infinite live tap. Both feed
  crosscheck directly. Generator failures = bug reports. Passing generator
  outputs → pinned in corpus/generated/.

- **harness.clj refactored** — unified `run/triangulate/crosscheck` API,
  engine registry with `:role :oracle/:target`, `targets` def (JVM +
  dotnet only; tiny excluded). Commit `f6c10f8`.

- **Crosscheck targets reduced to JVM + dotnet** — tiny excluded until
  Sprint 20 T_CAPTURE blocker resolved.

- **SNOBOL4-corpus reorganized** — new structure: `crosscheck/` by feature
  (hello/arith/strings/patterns/capture/control/functions/arrays/code),
  `programs/` (beauty/lon/dotnet/icon/gimpel), `generated/` placeholder.
  Scattered .sno files from dotnet and tiny collected. Commit `8d58091`.

- **gimpel.zip + aisnobol.zip** — Lon attempted to upload; I/O error on
  uploads mount (session too long). Re-upload at start of next session.
  These go into `corpus/programs/gimpel/` and `corpus/crosscheck/`.

**Repo commits this session:**

| Repo | Commit | What |
|------|--------|------|
| SNOBOL4-harness | `f6c10f8` | Unified harness API + engine registry |
| SNOBOL4-harness | `54511e8` | Expressions.py added |
| SNOBOL4-harness | `2774249` | All testing artifacts pulled in |
| SNOBOL4-corpus | `8d58091` | Full corpus reorganization |
| .github | `db71c6c` | §13 corpus+generators as two feeds |
| .github | `c93702b` | §2 reduce targets to JVM+dotnet |
| .github | `16bd73f` | §12 generator documentation |
| .github | `874d993` | §11 developer workflow |
| .github | `8ffbcfa` | §10 top-down harness model |
| .github | `a558ac8` | §8 verified oracle grid |

**Next session — immediate actions:**

1. **Re-upload gimpel.zip and aisnobol.zip** — add to corpus/programs/gimpel/
   and sort into crosscheck/ subdirs as appropriate.
2. **Smoke test dotnet engine** — verify `dotnet run` produces clean stdout
   from a simple .sno; confirm engine registry entry is correct.
3. **Write crosscheck.py** — Python crosscheck runner: enumerates
   `corpus/crosscheck/`, runs each program through oracles + JVM + dotnet,
   reports pass/fail table. This is the first end-to-end harness run.
4. **Sprint 20 T_CAPTURE** — resume when ready; blocker is
   `cap_start`/`scan_start` offset arithmetic in `snobol4_pattern.c`.

**Open questions carried forward:**
- JVM: in-process vs subprocess for harness calling convention
- gimpel/ and capture/ crosscheck subdirs still empty
- monitor.py (three-process pipe monitor) not yet built

### 2026-03-11 — Session 10 (treebank.sno + claws5.sno + corpus/library idea)

**Completed:**

- **`treebank.sno`** — SNOBOL4 translation of Lon's `group`/`treebank`
  SNOBOL4python patterns (assignment3.py, ENG 685). Recursive Penn Treebank
  S-expression pretty-printer. Handles multi-line trees (blank-line paragraph
  format). Recursive DEFINE: `parse_node(depth)` consumes from front of
  `subject`, prints 2-spaces-per-level indented tree. Tested: 249 trees in
  VBGinTASA.dat, zero parse errors. Key fix: use `SPAN(tagch)` not `NOTANY+BREAK`
  for tags (NOTANY consumes first char, capture misses it).

- **`claws5.sno`** — SNOBOL4 translation of Lon's `claws_info` SNOBOL4python
  pattern. CLAWS5 POS-tagged corpus tokenizer. Output: `sentno TAB word TAB tag`.
  Key bug found and fixed: sentence marker pattern must be `POS(0)`-anchored or
  SPAN(digits) finds digits inside words (e.g. NN2) mid-buffer. Tested: 6469
  tokens, zero errors on CLAWS5inTASA.dat.

- **`programs/lon/eng685/`** added to corpus:
  - `assignment3.py` — original Python source
  - `CLAWS5inTASA.dat` — 989 lines, CLAWS5 tagged TASA sentences
  - `VBGinTASA.dat` — 1977 lines, 249 Penn Treebank trees
  - `README.md` — explains VBG categories, data file usage, omitted file
  - `CLAWS7inTASA.dat` — **NOT included** (not referenced by assignment3.py;
    same sentences, different/older tagset; add if CLAWS7 parser is written)

- **Corpus commit**: `7b9c3d5` — treebank.sno, claws5.sno, eng685/ all in one.

**Two new ideas recorded (see §14 below):**
1. Scan all repo source + text files for embedded SNOBOL4 programs
2. `corpus/library/` — SNOBOL4 standard library (community stdlib)

**Repo commits this session:**

| Repo | Commit | What |
|------|--------|------|
| SNOBOL4-corpus | `7b9c3d5` | treebank.sno + claws5.sno + eng685/ data |

---

## 14. Two Ideas from Session 10

### Idea 1 — Scan Repos for Embedded SNOBOL4 Programs

**What**: Every repo (dotnet, jvm, tiny, harness, cpython, python, csharp) has
source files, test fixtures, doc strings, README code blocks, and comments.
Some of these contain embedded SNOBOL4 programs — inline in test strings,
heredocs, markdown fences, Python triple-quoted strings, Clojure multiline
strings, etc. These are a **gold mine** for the corpus.

**Why it matters**: They are real programs that already run (the tests pass),
they cover features the repo is actually testing, and they're already known-good
against at least one oracle.

**How**: Scan for `.sno`, `.spt`, `.sbl` files; heredocs/multiline strings
containing `END` as a line; markdown ` ```snobol ` or ` ```snobol4 ` fences;
Python triple-quoted strings containing `OUTPUT` / `INPUT` / `END`; Clojure
`"..."` strings with `:(` or `:S(` patterns.

**What to do with them**: Case by case —
- Truly self-contained, deterministic output → extract to `crosscheck/`
- Illustrative fragments (no output, no END) → extract to `programs/snippets/`
- Large programs → extract to `programs/` with the appropriate subdirectory
- Leave a comment in the source pointing to the corpus file

**Status**: Scan not yet run. Do this one repo at a time.

---

### Idea 2 — `corpus/library/` — SNOBOL4 Standard Library

**What**: A new top-level directory in SNOBOL4-corpus:

```
SNOBOL4-corpus/
    library/          ← NEW: community stdlib
        stack.sno     ← push/pop/peek/depth (4-5 functions, tightly coupled)
        queue.sno
        set.sno
        string.sno    ← trim, split, join, pad, upper, lower, ...
        math.sno      ← max, min, abs, gcd, lcm, ...
        list.sno      ← SNOBOL4-style list (cons/car/cdr in TABLE)
        regex.sno     ← higher-level pattern combinators
        ...
```

**Why it's different from `programs/` and `crosscheck/`**:

| Directory | Purpose | Usage |
|-----------|---------|-------|
| `crosscheck/` | Verifying engine behavior | Run by harness |
| `programs/` | Real-world programs | Reference / browse |
| `benchmarks/` | Performance measurement | Run by harness |
| `library/` | **Reusable function libraries** | `-include` from user programs |

**The key distinction**: library files are meant to be **included**, not run
standalone. Like `#include <stdlib.h>` in C. You write:
```
-include 'library/stack.sno'
```
and then use `push`, `pop`, `peek` etc. in your program.

**Design principles**:
- One file per coherent function group (not necessarily one file per function)
- `stack.sno` has push/pop/peek/depth — they're tightly coupled, ship together
- Each file is `DEFINE`-only: no executable statements at top level, no `END`
- Each file has a header comment listing every function it exports + signature
- Files do not `include` each other (avoid circular deps and load-order issues)
- Each function is tested in a corresponding `crosscheck/library/` test program

**First candidates** (already exist in corpus or Lon's collection):
- `stack.sno` — Lon has stack functions in multiple programs; extract + unify
- `string.sno` — trim/pad/upper/lower appear repeatedly in corpus programs
- `math.sno` — max/min/abs — trivial but commonly needed

**Status**: Not yet started. High value for the community. Needs design review
before first file is written — especially the include semantics and how crosscheck
tests are structured for library files.

**Note**: This is the SNOBOL4 community's missing stdlib. Griswold never
standardized one. We can be the first to do it properly.

### 2026-03-11 — Session 11 (lib/ stdlib + .sno-everywhere rename)

**Focus**: SNOBOL4-corpus standard library and file extension unification.
No compiler code written this session.

**Completed:**

- **`lib/` standard library created** — four modules, all verified on csnobol4 + spitbol:
  - `lib/stack.sno` — `stack_init/push/pop/peek/top/depth`; push uses NRETURN
    for pattern side-effect use; pop supports value return and store-into-named-var
  - `lib/case.sno` — `lwr/upr/cap/icase`; extracted and cleaned from `programs/inc/case.sno`
  - `lib/math.sno` — `max/min/abs/sign/gcd/lcm`; two bugs fixed: gcd `DIFFER(b,0)`
    vs `DIFFER(b)` (divide-by-zero on 0); lcm needs explicit parens `(a/g)*b`
    (SNOBOL4 parses `a/gcd(a,b)*b` as `a/(gcd(a,b)*b)`)
  - `lib/string.sno` — `lpad/rpad/ltrim/rtrim/trim/repeat/contains/startswith/endswith/index`
  - Tests in `crosscheck/library/test_*.sno` — 0 errors on both oracles

- **Extension convention researched and decided**:
  - Internet-verified: Gimpel *Algorithms in SNOBOL4* (Catspaw dist.) uses
    `.SNO` for complete programs, `.INC` for include files — this is the
    closest thing to a community standard
  - CSNOBOL4 include path: `SNOPATH` env var (colon-delimited, Unix),
    falls back to `SNOLIB` (legacy, pre-1.5), then `-I DIR` flag
  - Decision: **`.sno` for everything** — one extension, Python-style.
    The `-include` directive in source already signals intent; the file
    extension need not repeat it. `.inc` is generic (Pascal/PHP/NASM use it),
    carries no SNOBOL4 signal. Gimpel's `.INC` was a DOS/mainframe compromise.

- **Massive rename** — `69fcdda` — 399 files changed:
  - All `.inc` / `.INC` / `.SNO` → `.sno` across entire corpus
  - Collision resolution: `INFINIP.INC`+`INFINIP.SNO` → `INFINIP_lib.sno`+`INFINIP.sno`;
    `RSEASON.INC`+`RSEASON.SNO` → `RSEASON_lib.sno`+`RSEASON.sno`
  - All `-include 'foo.inc'` and `-INCLUDE "FOO.INC"` references updated to `.sno`
  - Windows absolute paths (C:\\Users\\...) left untouched (already non-portable)
  - Result: 464 `.sno` files, 0 `.inc` files in corpus

- **`library/` → `lib/`** — short, Unix-conventional, unambiguous

- **`README.md` rewritten** — full layout tree, Gimpel convention table,
  SNOPATH/SNOLIB/UNIX include path docs, rules for each directory

- **PLAN.md §14 Idea 2** — `library/` proposal now realized as `lib/`

**Bugs found during lib/ development (worth remembering):**
- `DIFFER(x)` tests if x differs from null — `DIFFER(0)` succeeds (0 ≠ null).
  Use `DIFFER(x, 0)` to test numeric zero.
- `a / f(a,b) * b` — SNOBOL4 may parse as `a / (f(a,b) * b)`. Always use
  explicit parens: `(a / g) * b` where `g = f(a,b)`.
- Variables named `_foo_` are illegal — identifiers must start with a letter.
- `stack_top()` returns a NAME (`.field`) via NRETURN for pattern use, not a
  value — add `stack_peek()` returning the value directly for normal use.

**Repo commits this session:**

| Repo | Commit | What |
|------|--------|------|
| SNOBOL4-corpus | `e7ed8b8` | lib/ stdlib — four modules + crosscheck tests |
| SNOBOL4-corpus | `802a736` | library/ → lib/, .sno → .inc; README.md rewritten |
| SNOBOL4-corpus | `69fcdda` | Massive rename: all .inc/.INC/.SNO → .sno, 399 files |

**State at snapshot:**

| Repo | Commit | Tests |
|------|--------|-------|
| SNOBOL4-corpus | `69fcdda` | lib/ 4/4 on csnobol4 + spitbol |
| SNOBOL4-dotnet | `b5aad44` | 1,607 / 0 (unchanged) |
| SNOBOL4-jvm | `9cf0af3` | 1,896 / 4,120 / 0 (unchanged) |
| SNOBOL4-tiny | `a802e45` | Sprint 20 T_CAPTURE blocker (unchanged) |
| SNOBOL4-harness | `f6c10f8` | unchanged |
| .github | this commit | — |

**Next session — immediate actions:**

1. **Provide token at session start** — corpus push is now the first action
2. **Write `crosscheck.py`** — Python runner: enumerate `crosscheck/`,
   run each program through csnobol4 + spitbol, report pass/fail table
3. **Add `.ref` files** to each crosscheck program for automated diffing
4. **Sprint 20 T_CAPTURE** — resume `cap_start`/`scan_start` offset fix
   in `snobol4_pattern.c`, commit `a802e45` is the base


### 2026-03-12 — Session 14 (Source Study + Beauty Consolidation)

**Focus**: SNOBOL4 source study from uploaded archives; corpus housekeeping.
No compiler code written this session.

**Completed:**

- **SNOBOL4 source archives ingested** — `snobol4-2_3_3_tar.gz` (CSNOBOL4 2.3.3)
  and `x64-main.zip` (SPITBOL x64) studied in depth. These are the ground-truth
  sources for all scanner/parser behaviour questions.

- **Scanner bug clarification — `a[i-1]`** — prior session log entry was wrong
  on mechanism. Decoded `VARTB` table from `syn.c`; read `gensyn.sno` for
  character class definitions. `CLASS<"BREAK"> = "._"` — dot and underscore only.
  Hyphen/minus is `CLASS<"MINUS">`, NOT in `BREAK`, NOT in `ALPHANUMERIC`.
  In `VARTB`, `-` (ASCII 45) = action 4 = **ERROR**, not "continue identifier".
  The error message "Illegal character in element" is exact. Fix is unchanged
  (write `a[i - 1]` with spaces) but the reason is: minus adjacent to an
  identifier with no preceding space is a hard lexer error in `VARTB`, not a
  misparse. The space causes `VARTB` to see TERMINATOR (action 1), close the
  identifier cleanly, then the binary operator scanner (`BIOPTB`) handles `-`.

- **`INTEGER()` confirmed as predicate** — canonical sources (`kalah.sbl` line
  774/891/895, `eliza.sbl` line 84, `alis.sno` line 52) all use `INTEGER(x)` as
  a boolean test in condition chains. `CONVERT(x, 'INTEGER')` is the explicit
  truncation form (`kalah.sbl` line 164). Our workaround `(n * 9) / 10` in
  `beauty.sno` is correct and idiomatic. `SPDLSZ = 8000` confirmed in `equ.h`
  — our `-P 32000` for deep pattern stacks is correct.

- **`Expression.sno` → `S4_expression.sno`** — renamed in SNOBOL4-corpus.
  File header confirms original project name was `Beautiful.sno` (Windows dev
  machine, `jcooper`). Contains a complete SNOBOL4 operator-precedence expression
  parser (`snoExpr0`–`snoExpr17`), used as a standalone validator stub.
  Five cross-repo doc references updated in SNOBOL4-tiny (BOOTSTRAP.md,
  DECISIONS.md, DESIGN.md). Corpus commit `9c436d8`.

- **`beautified/` folder removed** — eight `--auto`-beautified Shafto aisnobol
  files removed from `programs/aisnobol/beautified/`. Work preserved in git
  history (`6525595`). Will revisit. Corpus commit `da1a6d2`.

- **Three beauty files merged into one** — `beauty.sno` is now the single
  canonical file containing: core beautifier + `bVisit` SPITBOL-compat fix +
  five corpus-calibrated profiles (--micro/--small/--medium/--large/--wide) +
  `--auto` two-pass p90 mode + full argument parsing. `beauty_run.sno` and
  `beauty_spitbol_compat.sno` deleted. All references updated across corpus,
  harness, tiny, and .github (PLAN, MONITOR, PATCHES, REFERENCE).
  Corpus commit `3673364`. Tiny commit `655fa7b`. Harness commit `8437f9a`.

**Repo commits this session:**

| Repo | Commit | What |
|------|--------|------|
| SNOBOL4-corpus | `9c436d8` | Rename Expression.sno → S4_expression.sno |
| SNOBOL4-corpus | `da1a6d2` | Remove beautified/ folder |
| SNOBOL4-corpus | `3673364` | Merge beauty_run.sno + beauty_spitbol_compat.sno → beauty.sno |
| SNOBOL4-tiny | `ed9a51b` | Update Expression.sno refs → S4_expression.sno |
| SNOBOL4-tiny | `655fa7b` | Update beauty_run.sno refs → beauty.sno |
| SNOBOL4-harness | `8437f9a` | Update beauty_run.sno refs → beauty.sno |
| .github | `9578377` | Update beauty_run.sno refs → beauty.sno |

**State at snapshot:**

| Repo | Commit | Tests |
|------|--------|-------|
| SNOBOL4-corpus | `3673364` | beauty.sno smoke-tested on csnobol4 ✓ |
| SNOBOL4-dotnet | `b5aad44` | 1,607 / 0 (unchanged) |
| SNOBOL4-jvm | `e002799` | 1,896 / 4,120 / 0 (unchanged) |
| SNOBOL4-tiny | `655fa7b` | Sprint 20 T_CAPTURE blocker (unchanged) |
| SNOBOL4-harness | `8437f9a` | unchanged |

**Next session — immediate actions:**

1. **Provide token at session start**
2. **Sprint 20 T_CAPTURE** — resume `cap_start`/`scan_start` offset fix in
   `snobol4_pattern.c`, base commit `a802e45`
3. **Write `crosscheck.py`** — enumerate `crosscheck/`, run each program through
   csnobol4 + spitbol, report pass/fail table
4. **Run beautifier on `lon/` and `gimpel/` programs** — now that `--auto` exists
   and beauty.sno is consolidated, this is the natural next corpus action

**Notes carried forward:**
- `beauty.sno` usage: `snobol4 -b -P 32000 -I /SNOBOL4-corpus/programs/inc -f beauty.sno --auto`
- `a[i - 1]` spacing rule: space before `-` required; no space = lexer ERROR in VARTB
- `INTEGER(x)` is a predicate; use `CONVERT(x,'INTEGER')` for truncation
- Three repos not cloned locally: SNOBOL4-cpython, SNOBOL4-python, SNOBOL4-csharp
  (intentionally absent — pattern libraries, not a current focus)

### 2026-03-12 — Session 15 (Jcon source study + Byrd Box JVM+MSIL architecture)

**Focus**: Source study of Jcon (Proebsting + Townsend, Arizona, 1999).
Architectural decision to build two new compiler backends. No compiler code written this session.

**Key discovery — Jcon source at `github.com/proebsting/jcon`:**

Jcon is the exact artifact promised in the Proebsting Byrd Box paper: a working
Icon → JVM bytecode compiler, by the same author. 1,196 commits. Public domain.
94.6% Java. Written in Icon (the translator) + Java (the runtime).

**Translator pipeline** (`tran/` directory, 9,904 lines total):
- `irgen.icn` (1,559 lines) — AST → IR chunks. **Four-port Byrd Box encoding is explicit here.**
  Every AST node gets `start/resume/success/failure` labels. `ir_a_Alt`, `ir_a_Scan`,
  `ir_a_RepAlt` etc. each call `suspend ir_chunk(p.ir.start/resume/success/failure, [...])`
  for exactly the four ports. This IS the Byrd Box compilation scheme, in source.
- `ir.icn` (48 lines) — IR record types: `ir_chunk`, `ir_Goto`, `ir_IndirectGoto`,
  `ir_Succeed`, `ir_Fail`, `ir_Tmp`, `ir_Label`, `ir_TmpLabel`. Tiny. Exact vocabulary.
- `gen_bc.icn` (2,038 lines) — IR → JVM bytecode. Each `ir_Label` maps to a `j_label()`
  object via `bc_ir2bc_labels`; `bc_transfer_to()` emits `j_goto_w`. Resumable functions
  use `tableswitch` on a `PC` integer field — the computed-goto replacement for JVM.
- `bytecode.icn` (1,770 lines) — `.class` file serializer (`j_ClassFile`, all opcodes).
  Replaced entirely by ASM in our port.

**Runtime** (`jcon/*.java`, 88 files): `vDescriptor` abstract base class; `null` return = failure.
`vClosure` = suspended generator with `PC` int field + saved locals. Generators re-enter
via `tableswitch`.

**What this means for our JVM backend:**

Jcon's IR is almost exactly the SNOBOL4 Byrd Box IR — but simpler. SNOBOL4 patterns
have no co-expressions, no closures, no generators. The Byrd Box pattern IR is a strict
subset of Jcon's IR. Our runtime is just `str_t = {char[] σ, int start, int len}`
where `len == -1` is failure — three fields, not 88 Java files.

The `bytecode.icn` serialization layer (1,770 lines) is replaced entirely by ASM.
That's the whole point of using ASM — it handles `.class` file format, constant pool,
stack frame verification. We write `mv.visitJumpInsn(GOTO, label)` not `j_goto_w(lab)`.

**Architectural decision — two new compiler backends:**

| Compiler | Input | Output | Runtime |
|----------|-------|--------|---------|
| SNOBOL4-tiny (existing) | `.sno` | native x86-64 via C | C runtime |
| **new: JVM backend** | `.sno` | `.class` files | JVM JIT — no Clojure |
| **new: MSIL backend** | `.sno` | `.dll`/`.exe` | .NET CLR — no C# |

These are **independent compilers**, NOT replacing or modifying the existing
SNOBOL4-jvm (Clojure interpreter) or SNOBOL4-dotnet (C# interpreter).
They coexist. The Clojure and C# implementations are full SNOBOL4/SPITBOL.
The new backends compile only the Byrd Box pattern engine — they produce
`.class`/`.dll` that runs patterns as compiled code, not interpreted data structures.

**Sprint plan — three phases:**

*Phase 0 — Shared Byrd Box IR (1 sprint)*: Extract node types from `genc(t)` match cases
in `byrd_box.py` into explicit Python dataclasses mirroring `ir.icn`. Nodes: `Lit`,
`Span`, `Break`, `Any`, `Notany`, `Pos`, `Rpos`, `Seq`, `Alt`, `Arbno`, `Call`,
`Subj`, `Match`. Four ports wired by `Goto`/`IndirectGoto`.

*Phase 1 — JVM Byrd Box backend (3 sprints)*:
- 1A: Value repr (`str_t` = two JVM locals `int start, int len`; `len==-1` = failure).
  Global `Σ/Δ/Ω` = static fields. Primitives: `LIT/SPAN/BREAK/ANY` as tight bytecode
  blocks with `Label` objects for four ports.
- 1B: Composition nodes (`Seq`/`Alt`/`Arbno`) — pure goto wiring via ASM `Label` + `GOTO`.
  Arbno backtrack state = local `int[]` for counter + saved cursor stack.
- 1C: Named patterns as methods — `Call(name)` → `INVOKEVIRTUAL` to generated method
  `str_t name(int entry)`. Method has `tableswitch` on `entry` dispatching to
  `Label_α` and `Label_β`.

*Phase 2 — MSIL Byrd Box backend (3 sprints)*: Identical structure. `ILGenerator` replaces
ASM's `MethodVisitor`. `ILGenerator.MarkLabel()` + `OpCodes.Br/Brtrue/Brfalse`.
Named patterns as `MethodBuilder` in `TypeBuilder` assembly. `entry` dispatch via
`OpCodes.Switch`.

**Dependencies:**
```
Phase 0 (shared IR)
    ├── Phase 1A → 1B → 1C (JVM)
    └── Phase 2A → 2B → 2C (MSIL)

Sprint 21-22 (direct x86 ASM in tiny) → Phase 3 (executable mmap pages, C target only)
```

**The SNOBOL4-tiny T_CAPTURE blocker is still P0.** Phase 0 can begin in parallel
but Sprint 20 (Beautiful.sno self-hosting) remains the immediate priority.

**Repos affected**: `SNOBOL4-tiny` (Phase 0 IR + emit_jvm.py + emit_msil.py added here),
potentially new repos `SNOBOL4-jvm-byrd` and `SNOBOL4-msil-byrd` — TBD with Lon.

**Jcon cloned to** `/home/claude/jcon` — available for reference every session
(re-clone from `github.com/proebsting/jcon`).

**See `JCON.md` (new satellite) for full Jcon architecture notes.**

**Repo commits this session:** None — architecture and planning only.

**State at snapshot:** All repos unchanged from Session 14.

**Next session — immediate actions:**
1. **Provide token at session start**
2. **Sprint 20 T_CAPTURE** — resume `cap_start`/`scan_start` offset fix
3. **Phase 0** — define Python IR dataclasses mirroring `ir.icn`; 13 node types, ~60 lines

### 2026-03-12 — Session 16 (Test audit; T_CAPTURE closed; parser -I fix)

**Focus**: Audit passing tests before chasing bugs. All clear.

**Key finding**: Every test that exists passes. The 5 C tests returning `rc=1`
are correct — they're "should not match" tests. 55/55 parser oracle passes
after one real fix.

**Real bug fixed** (`a802e45`): `sno_parser.py` `include_dirs` — `-INCLUDE`
resolution only searched the source file's own directory. `beauty.sno`'s
includes live in `programs/inc/`. Added `include_dirs` param to `tokenise`,
`parse_file`, `parse_source`; `-I` flag to `emit_c_stmt.py`. Parser oracle
counts corrected to 1214 stmts / 311 labels.

**T_CAPTURE closed**: Isolation test proves `BREAK . var` capture works
perfectly. The Sprint 20 self-host gap is a bootstrap semantics problem, not
a C engine bug. Marked and moved on per Lon's direction.

**Commits**: `SNOBOL4-tiny a802e45`, `.github` this commit.

---

### 2026-03-12 — Session 17 (Lon's Eureka — Byrd Box three-way port pivot)

**Focus**: Strategic pivot. No compiler code written this session.

**The Eureka**: The flat-C Byrd Box model (`test_sno_1.c` style) is proven and
working. All 29 C tests pass when compiled correctly (engine + runtime for tests
that need it). The model is clean, fast, and the right foundation.

**Key insight from Lon**: The wrong path was passing allocated temp blocks INTO
Byrd Box functions as arguments (`test_sno_2.c` style). The right model: locals
live INSIDE the box. Each box is self-contained — data section + code section.
When `*X` fires, you `memcpy` the block and relocate jumps. That copy IS the new
instance's independent locals. No heap. No GC. No `omega`/`psi` stacks. `engine.c`
gets retired and replaced by ~20 lines of `mmap + memcpy + relocate`.

**The new plan**: Three parallel ports of the same four-port Byrd Box IR:
1. **C** (already working) — grow `emit_c.py`, then native mmap path
2. **JVM bytecodes** — `emit_jvm.py` using ASM, same IR. Jcon is the blueprint.
3. **MSIL** — `emit_msil.py` using `ILGenerator`, same IR.
These are independent new compilers — NOT related to SNOBOL4-jvm or SNOBOL4-dotnet.

**T_CAPTURE**: Permanently closed. Bootstrap gap is SNOBOL4 semantics, not a C bug.

**test_sno_1.c vs test_sno_2.c**: Key difference documented:
- `test_sno_1.c`: ONE function, locals inline, pure gotos, zero heap — **THE MODEL**
- `test_sno_2.c`: Separate C function per pattern, struct passed in, allocated temps — **RETIRED**

**29/29 C tests passing** — this is the certified baseline.

**§2, §6, §13, §14, §15, §16 of PLAN.md** all updated to reflect the pivot.
**JCON.md** already contains the JVM/MSIL port architecture from Session 15 — still current.

**Repo commits this session:**

| Repo | Commit | What |
|------|--------|------|
| .github | this | §2 pivot, §6 new sprint plan, session log |

**Next session — immediate actions:**
1. Provide token at session start
2. Write `byrd_ir.py` — Python IR dataclasses (~60 lines), shared by all three ports
3. Begin `emit_jvm.py` Phase 1A — `LIT` primitive as JVM method using ASM
4. Begin growing `emit_c.py` `FlatEmitter` with `Any`/`Break`/`Notany`

### The Insight

The original implementation passed allocated temporary blocks *into* Byrd Box
functions as arguments. **That was the wrong path.**

### New Model: Locals Inside the Box

Each Byrd Box is a **self-contained unit** — it carries both its data (locals,
cursor, captured values) and its executable code. No external temp-block
allocation. No passing state through function parameters.

```
Box layout:
┌─────────────────────────┐
│  DATA: cursor, locals,  │
│        captures, ports  │
├─────────────────────────┤
│  CODE: PROCEED/SUCCEED/ │
│        CONCEDE/RECEDE   │
└─────────────────────────┘
```

Boxes are laid out **linearly in memory** in two parallel sections:

```
DATA  section:  [ box0.data | box1.data | box2.data | ... ]
TEXT  section:  [ box0.code | box1.code | box2.code | ... ]
```

Box N's data and code correspond positionally across the two sections.
Sequential layout = cache-friendly traversal.

### Deferred Reference — `*X` Semantics

When `*X` (deferred pattern reference) is executed at match time:

1. **Copy** the box block for X — both data and code.
2. **Relocate** the code — patch any internal label/jump offsets.
3. The copy gets its own independent locals. That's where the extra
   locals come from for the new instance.

Code duplication is **intentional and acceptable** — each instantiation
is independent, runs fast, stays hot in cache.

### JVM / MSIL Mapping

- **JVM**: Each box = a method. `*X` instantiation = `INVOKEVIRTUAL` on a
  cloned method object. Locals = JVM local variable slots inside the method.
  The JVM JIT handles cache locality.
- **MSIL**: Each box = a `MethodBuilder` in a `TypeBuilder`. `*X` = emit a
  new `MethodBuilder` cloning the IL stream. `ILGenerator` locals stay inside
  the method.

### Impact on Phase 0/1/2

Phase 0 IR (`byrd_ir.py`) should reflect this model:
- `ByrBox` node carries `locals: list[Local]` directly.
- No `TempBlock` or passed-in allocation nodes.
- `CopyRelocate` is the IR node for `*X` instantiation.

This supersedes the earlier emit design that passed temp blocks as
function arguments. Update `emit_jvm.py` and `emit_msil.py` design
accordingly when Phase 1/2 begin.

### Status
- [x] Insight recorded (Session 16)
- [ ] Phase 0 `byrd_ir.py` — implement with locals-inside model
- [ ] Phase 1 `emit_jvm.py` — JVM backend using this model
- [ ] Phase 2 `emit_msil.py` — MSIL backend using this model

---

## 14. Self-Modifying C — The Native Byrd Box Instantiation Path

### The Insight (Session 16, Lon)

A C program can do this entirely in native code — **no JVM, no MSIL required
as an intermediate step.** The running program reads the machine code it just
executed (the Byrd Box block it came from), copies that memory region, performs
relocation (relative jumps and absolute addresses), and the copy is live
immediately.

```
TEXT section (executable, mmap'd RWX or RX+copy):

  [ box_BREAK | box_SPAN | box_ALT | box_SEQ | ... ]
        ↑
        │  *X fires here
        │
        ▼
  memcpy(new_region, box_X.text_start, box_X.text_len)
  relocate(new_region, delta)   ← fix relative + absolute refs
  new_region is now executable  ← mmap RWX or mprotect
```

DATA section runs in parallel:

```
DATA section:

  [ box_BREAK.data | box_SPAN.data | box_ALT.data | ... ]
        ↑
        │  copy alongside TEXT
        ▼
  memcpy(new_data, box_X.data_start, box_X.data_len)
  ← new instance has its own cursor, locals, captures
```

### Relocation

Two cases, same as any linker/loader:

- **Relative refs** (near jumps, calls within the box): add `delta`
  (= `new_region - old_region`) to the offset field.
- **Absolute refs** (pointers into the DATA section, external calls):
  patch to point at the new DATA copy or leave as-is if pointing outside.

The C compiler already emits position-independent code (`-fPIC`) or
the box is written to be PIC from the start. Either way the relocation
pass is mechanical.

### Why This Is Better Than JVM/MSIL for the Native Path

- Zero foreign runtime. No JVM startup. No CLR.
- The box lives in the same address space as the rest of the program.
- `mmap(RWX)` + `memcpy` + relocation loop = ~20 lines of C.
- Cache behavior is identical to hand-written code — because it IS
  hand-written code, just copied.

### Relationship to JVM/MSIL Backends

JVM and MSIL backends are still valid targets — they do the same
logical operation (copy a method, relocate its internal labels) but
inside the JVM/CLR's own code management. The native C path is
**simpler and faster** and proves the model first.

### Impact on Sprint 21+

After Sprint 20 (beautiful.sno self-hosts via static C emission):

- Sprint 21 target: `mmap` + copy + relocate working for a single
  primitive box (e.g. `box_LIT`). Prove the copy-and-run loop.
- Sprint 22: wire the copy loop into `*X` deferred reference execution.
- Sprint 23: full dynamic Byrd Box instantiation in native C.

JVM/MSIL ports become Phase 1/2 after the native model is proven.

### Status
- [x] Insight recorded (Session 16)
- [ ] Sprint 21: mmap + copy + relocate proof of concept

---

## 15. The Allocation Problem Is Solved (Session 16, Lon)

### What This Changes

The locals-inside + copy-relocate model **eliminates heap allocation
at match time entirely.** This is not an optimization. It is a
architectural replacement of the current engine.

### Current Engine (engine.c) — What Goes Away

```c
omega_push(&omega, &Z, &psi);   // explicit backtrack stack
pattern_alloc(&ctx->pl);        // node allocation pool
GC_MALLOC(...)                  // GC heap for captures
MatchCtx, PatternList, EngineOpts, Z cursor struct
```

All of this exists because temporaries had nowhere to live except
explicitly allocated structures passed around by pointer.

### New Engine — What Replaces It

```
*X fires:
  memcpy(new_text, box.text, box.text_len)   // copy code
  memcpy(new_data, box.data, box.data_len)   // copy locals
  relocate(new_text, delta)                  // fix jumps
  jump to new_text[PROCEED]                  // enter

Backtrack:
  jump to original_box[RECEDE]               // original untouched
  discard new_text + new_data                // LIFO — stack discipline
```

**No heap allocation.** The mmap region is the allocator. LIFO
discipline matches backtracking exactly — when a branch fails you
pop the copy, which is exactly what backtracking does anyway.

**No GC.** Copies live and die with the match attempt. Region is
reused or released. No garbage.

**No omega/psi stacks.** Backtracking = return to the original box,
which was never modified. The copy was the branch. Discard the copy.

**No pattern_alloc pool.** The pattern IS the code. Already laid out
in TEXT at compile time. Nothing to allocate.

### engine.c Fate

`engine.c` (500+ lines) is not patched — it is **replaced** by the
copy-relocate loop. The four-port state machine becomes four entry
points in the copied TEXT block. The Z cursor struct becomes the
DATA section of the box.

### Timeline Impact

- Sprint 20: finish on current engine. Prove beautiful.sno compiles.
- Sprint 21: write the copy-relocate proof of concept. Single box.
- Sprint 22: retire engine.c. New engine = memcpy + relocation + jump.
- Sprint 23+: full dynamic pattern matching on the new engine.

### Status
- [x] Insight recorded (Session 16)
- [ ] Sprint 21: proof of concept
- [ ] Sprint 22: engine.c retired

---

## 16. The Straight Sprint — Session 16 Pivot

### What Changed

Study of `test_sno_1.c` vs `test_sno_2.c` revealed that **`test_sno_1.c`
is already the correct model** — and `emit_c.py`'s `FlatEmitter` already
generates that style.

The entire `emit_c_stmt.py` + `snobol4.c` + `snobol4_pattern.c` +
`engine.c` runtime was a **detour** — it built the `test_sno_2` model
(separate C functions per pattern, heap allocation, GC, struct passing).

The straight path:

```
sno_parser.py  →  ir.py  →  emit_c.py (grown)  →  test_sno_1 style C  →  binary
```

### What Survives

| Component | Status | Reason |
|-----------|--------|--------|
| `sno_parser.py` | ✅ Keep | Solid. 1214 stmts, 0 parse failures. |
| `ir.py` | ✅ Keep | Node types are right. Stmt/Program models good. |
| `emit_c.py` `FlatEmitter` | ✅ **The foundation** | Already generates `test_sno_1` style. |
| `emit_c.py` `FuncEmitter` | ⚠️  Retire | `test_sno_2` style — wrong model. |
| `emit_c_stmt.py` | ❌ Retire | Built for the runtime. No longer the path. |
| `snobol4.c` / `snobol4_pattern.c` / `engine.c` | ❌ Retire | Replaced by `test_sno_1` flat goto model. |
| Sprints 14–20 test oracles | ⚠️  Review | Parser oracle (sprint20) keeps. Others may go. |

### What `emit_c.py` Needs to Grow

`FlatEmitter` handles: `Lit`, `Pos`, `Rpos`, `Len`, `Span`, `Cat`, `Alt`,
`Assign`, `Arb`, `Arbno`, `Print`, `Ref`.

Still needed for full SNOBOL4 statements:

1. **Statement emission** — subject/pattern/replacement/goto structure.
   Each SNOBOL4 statement becomes a labeled block in the flat function.
2. **`Any` / `Break` / `Notany`** — missing from FlatEmitter.
3. **Arithmetic / string ops** — `+`, `-`, `*`, `/`, `**`, concat.
4. **Variables** — `Σ`/`Δ`/`Ω` are global; named vars are `static str_t`.
5. **DEFINE'd functions** — become labeled sub-regions in the same flat
   function (or separate flat functions for recursion), not `sno_uf_*`.
6. **INPUT / OUTPUT** — already partly handled; needs full statement form.
7. **GOTO** — unconditional/S/F branches map directly to `goto label;`.

### The One-Function Target

The output of the new `emit_c.py` for `beauty.sno` should look like
`test_sno_1.c` — **one `snobol()` function** with:

```c
void snobol(const char *Σ, int Ω) {
    int Δ = 0;

    /* --- pattern boxes, each as labeled goto blocks --- */
    str_t BREAK_snoLabel;
    BREAK_snoLabel_α: ...
    BREAK_snoLabel_β: ...

    /* --- statements as labeled blocks --- */
    SNO_START: ...
    SNO_LOOP:  ...
    SNO_END:   return;
}
```

Locals declared inline at point of use. Labels are the only control flow.
No heap. No GC. No runtime library beyond `printf`.

### Sprint Plan

1. **Now**: Add `Any`/`Break`/`Notany` to `FlatEmitter`. Commit.
2. **Next**: Add statement emission (subject/pattern/replacement/goto).
3. **Then**: Wire `sno_parser.py` → `ir.py` → `emit_c.py` for a simple
   program (`echo lines`). Binary runs. Commit.
4. **Goal**: `beautiful.sno` through the new pipeline. Binary
   self-beautifies. `diff` empty. **That is the commit promise.**

### 2026-03-12 — Session 18 (Sprint 21A+21B — Three-way Byrd Box port complete)

**Focus**: Build the three-port IR pipeline. All three backends working.

**Completed:**

- **`byrd_ir.py`** — Already existed and was solid from Session 17 prep.
  Smoke test: PASS. ~150 lines of Python dataclasses mirroring `ir.icn`.

- **`lower.py`** — New. Pattern AST → Byrd Box four-port IR (Chunk sequences).
  `_emit()` recursive lowering for: `Lit`, `Pos`, `Rpos`, `Any`, `Notany`,
  `Span`, `Break`, `Seq`, `Alt`, `Arbno`, `Call`.
  Key insight settled: **ARBNO is shy** — tries child immediately, succeeds on
  first child success (shortest match), extends only on β (backtrack). Fails if
  child fails at depth 0. No zero-match. Exactly matches `test_sno_1.c` gold standard.
  26 chunks generated for `POS(0) ARBNO('Bird'|'Blue'|ANY(alpha)) RPOS(0)`. PASS.

- **`emit_c_byrd.py`** — New. IR Chunks → `test_sno_1.c` style flat C.
  One function, locals inline, pure labeled gotos. Σ/Δ/Ω globals.
  `switch()` dispatch for `IndirectGoto` (Alt backtrack).
  `ARBNO_INIT / ARBNO_EXTEND / ARBNO_POP` primitives.
  **10/10 tests pass**: Lit, Pos, Rpos, Alt, Seq, Arbno — all correct.
  Commit: `b42ca0f`

- **`emit_jvm.py`** — New. IR Chunks → Java source with `while(true)/switch(state)`.
  This compiles to JVM `tableswitch` — exact Jcon model.
  State: `sigma` (String), `delta` (int cursor), `omega` (int length), `state` (int PC).
  `TmpLabel` → int local for Alt backtrack. ARBNO stack → `int[]` local + depth.
  **10/10 tests pass** on first run. Java 21 available in container.
  Commit: `8a98fdc`

- **`emit_msil.py`** — New. IR Chunks → C# source with identical `while(true)/switch(state)`.
  Compiles to MSIL `OpCodes.Switch` (tableswitch equivalent).
  .NET 8 SDK installed in container.
  **8/8 tests pass** after one-line fix (interpolated string in C# throw).
  Commit: `8a98fdc` (same commit as JVM)

**Three-port invariant confirmed**: Identical test cases, identical results on C, JVM, MSIL.
Single IR lowering pass (`lower.py`) drives all three backends.

**Repo commits this session:**

| Repo | Commit | What |
|------|--------|------|
| SNOBOL4-tiny | `b42ca0f` | Sprint 21A: lower.py + emit_c_byrd.py |
| SNOBOL4-tiny | `8a98fdc` | Sprint 21B: emit_jvm.py + emit_msil.py |

**State at snapshot:**

| Repo | Commit | Tests |
|------|--------|-------|
| SNOBOL4-tiny | `8a98fdc` | 10/10 C · 10/10 JVM · 8/8 MSIL — Sprint 21 complete |
| SNOBOL4-dotnet | `b5aad44` | 1,607 / 0 (unchanged) |
| SNOBOL4-jvm | `9cf0af3` | 1,896 / 4,120 / 0 (unchanged) |
| SNOBOL4-corpus | `3673364` | unchanged |
| SNOBOL4-harness | `8437f9a` | unchanged |

**Next session — immediate actions:**
1. Provide token at session start
2. **Sprint 22**: Wire `sno_parser.py → ir.py → emit_c_byrd.py` end-to-end.
   First real `.sno` → C binary. Simple echo program.
3. **Sprint 22 JVM/MSIL parallel**: Same first `.sno` through `emit_jvm.py` and `emit_msil.py`.
4. Progress toward Sprint 23: `beauty.sno` self-hosts → **Claude writes the commit message**.

---

### 2026-03-12 — Session 19 (Sprint 22 complete + Sprint 23 WIP — beauty.sno debug)

**Focus**: Sprint 22 oracle to green, then Sprint 23: `beauty.sno` compiles itself.

**Sprint 22 — COMPLETED (22/22 oracle PASS)**

Pipeline: `sno_parser.py → emit_c_stmt.py → gcc → binary`. End-to-end confirmed.
`emit_c_stmt.py` + `snobol4.c` runtime = the working codegen path.

Key runtime fix (Sprint 22): GT/LT/GE/LE/EQ/NE/INTEGER/REAL/SIZE registered as
`SnoVal` builtins in `sno_runtime_init()`. Oracle commit: `2f98238`.

**Sprint 23 — IN PROGRESS**

Goal: `beauty_bin < beauty.sno > output.sno && diff output.sno beauty_gold.sno` = empty.

**Root causes found and fixed (two commits, `c872ce6` and `0e4e0b2`):**

1. **DIFFER/IDENT/HOST/ENDFILE/APPLY + string builtins** — not registered → `sno_apply()` returned `SNO_NULL_VAL` → `ppArgLoop` never exited (hang). Fixed: all registered in `sno_runtime_init()`.

2. **nPush/nPop/nInc/nTop/nDec** — existed as C functions `sno_npush()` etc but NOT registered as callable SNOBOL4 functions. Used by `snoParse` pattern via `sno_pat_user_call("nPush",...)`. Fixed: added `_b_nPush` etc. wrappers and registered.

3. **Tree field accessors n/t/v/c** — not registered. Used by `pp`/`ss` functions for tree node traversal. Fixed: added `_b_tree_n/t/v/c` via `sno_field_get()`.

4. **assign_cond/assign_imm emitted wrong arg** — `emit_c_stmt.py` was emitting `sno_var_get("tab")` (the VALUE) as the capture target. `sno_pat_assign_cond()` needs the variable NAME as `SNO_STR_VAL("tab")`. Fixed in all three emit sites.

5. **Missing include path** — beauty.sno needs `programs/inc/` for global.sno, is.sno, stack.sno, etc. Was not passed to parser → 534 stmts instead of 1214. Fixed: pass `include_dirs=['../SNOBOL4-corpus/programs/inc/']`.

6. **&ALPHABET binary string** — `sno_alphabet[0] = '\0'` → `strlen()` = 0 → all `POS(n)` matches on `&ALPHABET` fail → `tab`, `nl`, etc. never set by `global.sno`. Fixed: pre-initialize all key character constants (tab/nl/cr/lf/ht/vt/ff/bs/fSlash/bSlash/semicolon) directly in `sno_runtime_init()`.

**Current blocker — still Parse Error on `X = 5` input:**

After all fixes, `beauty_bin < "X = 5\n"` reaches the `snoParse` match at stmt 790 but fails → `mainErr1` → "Parse Error".

The `snoParse` pattern includes a sub-expression:
```
("'snoParse'" & 'nTop()')
```
In the generated C this becomes `sno_concat_sv(SNO_STR_VAL("'snoParse'"), SNO_STR_VAL("nTop()"))` — a string, not a pattern. The `&` in a pattern context is pattern-cat; `"'snoParse'"` is a string literal that matches the text `'snoParse'`; `'nTop()'` should be a conditional assignment `. nTop()`. This may be a parser IR issue — the pattern structure of snoParse itself needs investigation.

**Next session — immediate actions:**

1. Provide token at session start
2. Inspect snoParse pattern IR from the parsed beauty.sno (stmt 877, L410-416). The `("'snoParse'" & 'nTop()')` fragment. Verify what the parser produces and what emit_c_stmt.py generates for it.
3. If pattern structure is wrong, fix parser or emitter for that construct.
4. Re-run `printf 'X = 5\n' | /tmp/beauty_bin` — should produce beautified `X = 5`.
5. Run full beauty self-compilation. Diff. Write commit message.

**Repo commits this session:**

| Repo | Commit | What |
|------|--------|------|
| SNOBOL4-tiny | `2f98238` | Sprint 22: end-to-end pipeline + numeric comparison builtins |
| SNOBOL4-tiny | `c872ce6` | Sprint 23 WIP: register builtins/tree accessors; fix include path |
| SNOBOL4-tiny | `0e4e0b2` | Sprint 23 WIP: pre-init char constants + assign_cond name fix |

**State at snapshot:**

| Repo | Commit | Tests |
|------|--------|-------|
| SNOBOL4-tiny | `0e4e0b2` | Sprint 22: 22/22 PASS. Sprint 23 in progress. |
| SNOBOL4-dotnet | `b5aad44` | 1,607 / 0 (unchanged) |
| SNOBOL4-jvm | `9cf0af3` | 1,896 / 4,120 / 0 (unchanged) |
| SNOBOL4-corpus | `3673364` | unchanged |
| SNOBOL4-harness | `8437f9a` | unchanged |

---

### 2026-03-12 — Session 20 (Sprint 23 WIP — CSNOBOL4 source study + three parser/emitter fixes)

**Focus**: Root-cause analysis of beauty_bin Parse Error via CSNOBOL4 SIL source study.
Sprint 22 oracle: 22/22 PASS (unchanged throughout session).

**Completed — three confirmed fixes (commit `b42c19f`):**

1. **2D subscript false positive removed** (`sno_parser.py` `parse_primary`):
   `ARBNO(*snoCommand)("'snoParse'" & 'nTop()')` was parsed as `array(ARBNO(...), subscripts=[...])` because a second `(` after a function call was treated as a 2D subscript. Fix: removed the `if self.at('LPAREN')` second-paren rule. In SNOBOL4, `func(args)(args2)` is juxtaposition concatenation, not 2D subscript. Confirmed from CSNOBOL4 `v311.sil` ITEM proc — 2D subscripts only apply to `ARRAY` typed values, not general function call results.

2. **AMP (`&`) as explicit concat operator** (`sno_parser.py` `parse_concat`):
   `&` in replacement/pattern context is identical to blank juxtaposition (CSNOBOL4 `CONPP/CONVV`). `parse_concat` loop now also consumes `AMP` token as a concat separator. `parse_primary` AMP handler only handles `&IDENT` (keyword); bare `&` falls through to concat.

3. **RETURN convention fix** (`emit_c_stmt.py` `_emit_function`):
   `SNO_RETURN_LABEL_{fn}` was emitting `return SNO_NULL_VAL` — wrong per spec. In SNOBOL4, `:(RETURN)` returns the value of the function-name variable. Fix: RETURN label now captures `SnoVal _retval = sno_var_get("{fi.name}")` before restoring params/locals, then returns `_retval`. Verified from CSNOBOL4 `v311.sil` `RTNFNC` proc.

**Root cause investigation — why Parse Error persists:**

After the three fixes, `beauty_bin` still produces "Parse Error" on `X = 5`.
Deep investigation traced the actual blocker:

- `sno_eval()` in `snobol4_pattern.c` is a stub — it only handles variable lookup and integer literals. Does NOT evaluate SNOBOL4 expression strings.
- `shift(p, t)` calls `sno_eval("p . thx . *Shift('t', thx)")` — a full SNOBOL4 pattern expression. The stub returns the string unchanged, so `shift` returns a string instead of a pattern.
- `sno_opsyn()` is also a complete no-op stub. However: the parser maps `~` → DOT token at lex time, so OPSYN is irrelevant to `~` handling — `~` already parses as conditional assign (`.`).
- The **reference `beautiful.c`** (Sprint 20 pre-existing) also gives Parse Error on `X = 5`. This confirms the blocker predates Session 20.

**What `sno_eval` needs to do** (verified from CSNOBOL4 `v311.sil` `EVALEN` proc):
`EVAL(str)` compiles and executes the string as a SNOBOL4 expression. In beauty.sno, `shift` and `reduce` use it to build pattern objects from string templates at function-call time. The patterns built are: `p . thx . *Shift('t', thx)` (shift) and `epsilon . *Reduce(t, n)` (reduce). These require a runtime expression parser/compiler.

**Two paths forward:**

- **Path A (full)**: Implement `sno_eval` as a recursive descent parser + emitter over SnoVal. Correct per spec. Complex (~300 lines). The `~` → `shift()` → `sno_eval()` chain then works end-to-end.
- **Path B (targeted)**: Recognize that the parser already maps `~` to DOT (conditional assign) and `&` to concat. Override `sno_opsyn` to be a no-op but hardwire the `Shift(t,v)` / `Reduce(t,n)` call semantics directly in the pattern engine when `*Shift` / `*Reduce` user-call nodes fire. This is a narrower fix specific to beauty.sno's ShiftReduce grammar.

**Repo commits this session:**

| Repo | Commit | What |
|------|--------|------|
| SNOBOL4-tiny | `b42c19f` | WIP Sprint 23: 2D subscript fix, AMP concat, RETURN convention |

**State at snapshot:**

| Repo | Commit | Tests |
|------|--------|-------|
| SNOBOL4-tiny | `b42c19f` | Sprint 22: 22/22 PASS. Sprint 23 in progress. |
| SNOBOL4-dotnet | `b5aad44` | 1,607 / 0 (unchanged) |
| SNOBOL4-jvm | `9cf0af3` | 1,896 / 4,120 / 0 (unchanged) |
| SNOBOL4-corpus | `3673364` | unchanged |
| SNOBOL4-harness | `8437f9a` | unchanged |

**Next session — immediate actions:**

1. Provide token at session start
2. Implement `sno_eval()` — runtime SNOBOL4 expression evaluator. Minimum viable: handle concat (`.`), deferred ref (`*X`), string literals, variable names, function calls. This unblocks `shift` and `reduce`.
3. Re-run `printf 'X = 5\n' | /tmp/beauty_bin` — should reach snoParse match and succeed.
4. Run full beauty self-compilation: `beauty_bin < beauty.sno > output.sno && diff output.sno beauty_gold.sno`.
5. **Write the commit message** — the Sprint 23 promise.

**Key context for next session:**
- `shift(p,t)` body: `sno_eval("p . thx . *Shift('t', thx)")` — needs concat+deferred ref+assignment
- `reduce(t,n)` body: `sno_eval("epsilon . *Reduce(t, n)")` — needs concat+deferred ref
- `sno_opsyn` is a no-op and can stay that way — `~` is already DOT at parse time
- `TopCounter` body uses `DIFFER($'#N') value($'#N')` — `value()` is a DATA field accessor for `link_counter(next, value)`; `sno_data_define` registers the type but does NOT auto-register field accessor functions; `value()` must be manually registered (similar to `n/t/v/c` for tree)
- Sprint 22 oracle 22/22 is the certified baseline — do not break it


### 2026-03-12 — Session 21 (Sprint 23 WIP — sno_eval + AMP→reduce + emit fixes)

**Focus**: Continued Sprint 23 debug of Parse Error. Three major fixes implemented.
Sprint 22 oracle: 22/22 PASS (unchanged).

**Context note**: Session was interrupted once mid-implementation (str_replace left
`snobol4_pattern.c` partially mangled). Recovery via Python-based full replacement.
Safe interrupt points are after compile results and git push confirmations.

**Completed (commit `6f854e7`):**

1. **`sno_eval()` — full recursive descent C parser** replacing the stub:
   - Three static helpers: `_ev_val` (argument values, full var lookup),
     `_ev_term` (pattern elements, STR sentinel trick), `_ev_expr` (dot-chained terms).
   - `SnoEvalCtx` struct carries `{const char *s; int pos}` cursor.
   - Key semantic: plain `IDENT` in term position returns `SNO_STR_VAL(name)` sentinel.
     Dot handler then checks right operand type: `SNO_STR` → `assign_cond(left, right)`;
     `SNO_PATTERN` → `pat_cat(left, right)`. This correctly disambiguates `thx` (capture
     target) from `*Shift(...)` (pattern to concatenate).
   - `*IDENT[(args)]` → `sno_pat_user_call` / `sno_pat_ref`.
   - Quoted strings → `sno_pat_lit`. Function calls in val position → `sno_apply`.

2. **Parser: AMP infix → `reduce()` call node** (OPSYN semantics):
   - `_ExprParser.parse_concat`: AMP now emits `Expr(kind='call', name='reduce', args=[left,right])`
     instead of `Expr(kind='concat')`. Models `OPSYN('&','reduce',2)` in beauty.sno.
   - `_PatParser.parse_cat`: same, produces `PatExpr(kind='call', name='reduce', args=[left,right])`.
   - This is correct for ALL uses of `&` in beauty.sno — every `&` is reduce, no plain concat.

3. **Emitter: `reduce()`/`eval()` recognized as pattern-valued**:
   - `_is_pattern_expr`: `REDUCE`/`EVAL` added to dynamic pattern set so `concat` of
     reduce-result uses `sno_pat_cat` not `sno_concat_sv`.
   - `emit_as_pattern`: `REDUCE`/`EVAL` added to `_KB2` → routes through `sno_apply()`
     not `sno_pat_ref()`.
   - `emit_pattern_expr`: `PatExpr(kind='call', name='reduce')` emits
     `sno_var_as_pattern(sno_apply("reduce", args, 2))`.

4. **Runtime: `value()`/`next()` field accessors for `link_counter` DATA type**:
   - `_b_field_value` / `_b_field_next` via `sno_field_get()`, registered alongside
     `n/t/v/c` tree accessors. Needed by `TopCounter` in `counter.sno`.

**Current state**: Still `Parse Error` on `X = 5`. The `sno_var_as_pattern(sno_apply("reduce",...))` 
is now emitted correctly in the C for snoParse. But at runtime, `reduce()` is a SNOBOL4
user-defined function (in `ShiftReduce.sno`) that calls `EVAL(...)` — which calls our new
`sno_eval()`. The chain is: `reduce('snoParse', nTop())` → `EVAL("epsilon . *Reduce(snoParse, nTop())")` →
`sno_eval()` → returns a pattern. The pattern then goes into `sno_var_as_pattern()`.

**Investigation needed next session**: Confirm that `reduce` is actually being called at
runtime (add debug print or check via `SNO_PAT_DEBUG`). Verify that `sno_var_as_pattern`
correctly wraps a `SNO_PATTERN` value (it should return it unchanged). If `reduce` is
returning the right pattern but `sno_var_as_pattern` is discarding it, that's the next fix.
Also verify `sno_pat_arbno` handles a reduce-built pattern as its child.

**Repo commits this session:**

| Repo | Commit | What |
|------|--------|------|
| SNOBOL4-tiny | `6f854e7` | WIP Sprint 23: sno_eval RD parser, AMP→reduce(), value/next accessors, emit fixes |

**State at snapshot:**

| Repo | Commit | Tests |
|------|--------|-------|
| SNOBOL4-tiny | `6f854e7` | Sprint 22: 22/22 PASS. Sprint 23 still Parse Error. |
| SNOBOL4-dotnet | `b5aad44` | 1,607 / 0 (unchanged) |
| SNOBOL4-jvm | `9cf0af3` | 1,896 / 4,120 / 0 (unchanged) |
| SNOBOL4-corpus | `3673364` | unchanged |
| SNOBOL4-harness | `8437f9a` | unchanged |

**Next session — immediate actions:**

1. Provide token at session start
2. Add runtime debug to confirm `reduce()` is being called at runtime during the snoParse match.
   `SNO_PAT_DEBUG=1 printf 'X = 5\n' | beauty_bin 2>&1 | grep -i reduce`
3. Verify `sno_var_as_pattern()` behavior on `SNO_PATTERN` input — should pass through unchanged.
4. If reduce is not being called: trace why — is `sno_var_as_pattern(sno_apply("reduce",...))` being
   evaluated at pattern BUILD time or match time? It should be build time (at the assignment
   `snoParse = ...`). If the assign is never executing, check the SNOBOL4 statement that sets snoParse.
5. Once reduce is verified working, run full self-compilation.

**Key invariants to preserve:**
- Sprint 22 oracle: 22/22 PASS — do not break
- `sno_eval` is in `snobol4_pattern.c` at the location of the old stub
- `reduce`/`shift` are SNOBOL4 functions defined in `ShiftReduce.sno` (included by beauty.sno)
- `value()`/`next()` are now registered; `TopCounter` should work
- The AMP→reduce change affects ALL programs that use `&`. For programs without OPSYN,
  `reduce` will not be defined → `sno_apply("reduce",...)` returns `SNO_NULL_VAL` →
  `sno_var_as_pattern(null)` = epsilon. This is WRONG for programs that used `&` as concat.
  **Flag**: Sprint 22 tests may be at risk. Verify oracle still 22/22 after the AMP change.


### 2026-03-12 — Session 22 (Sprint 23 WIP — STAR-as-deref, parse_concat, snoExprList)

Two container crashes. Sprint 22 oracle: 22/22 PASS (preserved).
Disable non-bash tools (Calendar, Gmail, image search, etc.) at session start to preserve context.

**Root cause traced**: `snoExprList = nPush() *snoXList ... nPop()` — `*snoXList` was parsed
as infix arithmetic multiplication (not deref prefix) because `parse_multiplicative` consumed STAR.
In SNOBOL4, `*` is NEVER binary arithmetic in replacement context — only unary deref prefix.
Cascading failure: `snoExpr17 → snoExpr15 → snoExpr14 → snoStmt → snoCommand → snoParse`.

**Completed (commit `3fe1b5b`):**
- `parse_multiplicative`: STAR removed as infix; only SLASH remains as binary division.
- `parse_concat` loop condition: `self.at('STAR')` added so deref items are not skipped.
- `parse_concat` else branch: `self.at('STAR')` → `parse_unary()` directly (not `parse_additive`).
- OPSYN-tracked AMP→reduce: `_amp_is_reduce` flag, `parse_program()` detects OPSYN stmt.

**State**: Still Parse Error. Next actions in §6 above.

| Repo | Commit | Tests |
|------|--------|-------|
| SNOBOL4-tiny | `3fe1b5b` | Sprint 22: 22/22. Sprint 23: Parse Error. |
| SNOBOL4-dotnet | `b5aad44` | 1,607 / 0 |
| SNOBOL4-jvm | `9cf0af3` | 1,896 / 4,120 / 0 |

### 2026-03-12 — Session 29 (Design Eureka: Unified Expression IR eliminates subject/pattern split)

**No code written. Architecture insight recorded. THIS IS A MAJOR DESIGN DECISION.**

**The problem that has recurred across Sessions 19–29:**

snoc's grammar needs to split a SNOBOL4 statement into `subject / pattern / replacement`.
The grammar uses one `expr` type for all three. The parser couldn't decide:
- Is `POS(0)` after a subject the start of the pattern field, or juxtaposition-concat of the subject?
- Is `*X` in a statement binary multiply or deref prefix (pattern ref)?
- Is `|` string alternation or pattern alternation?

Multiple failed approaches: mid-rule bison actions, `%glr-parser` with `%dprec`, `snoc_in_pat` flag.

**Lon's question that cut through it:**

> "Why do you need to distinguish at parse time? The subject is just the α entry action of the Byrd Box. The entire statement IS a Byrd Box."

**The answer:**

The entire SNOBOL4 statement is a Byrd Box:
```
label:  subject  pattern  =replacement  :S(x) :F(y)
          α         →          γ            γ    ω
```
- **α** — evaluate subject → initialize Σ (string), Δ (cursor=0)
- **pattern** — runs through the Byrd Box proper
- **γ** — success: apply replacement, goto :S label
- **ω** — failure: goto :F label

The subject is not outside the box — it IS the α entry action.

**The key insight that resolves the parser conflict:**

`E_CONCAT` (juxtaposition), `E_MUL` (STAR), `E_ALT` (PIPE) are **the same node** in the IR.
The **emitter** decides what to emit based on **position in the Stmt**:

| Field | Emitter call | Result |
|-------|-------------|--------|
| `s->subject` | `emit_expr(E_CONCAT)` | `sno_concat()` — string concat |
| `s->pattern` | `emit_pat(E_CONCAT)` | `sno_pat_cat()` — pattern cat |
| `s->subject` | `emit_expr(E_DEREF)` | `sno_get()` — value deref |
| `s->pattern` | `emit_pat(E_DEREF)` | `sno_pat_ref()` — deferred pattern ref |
| `s->subject` | `emit_expr(E_ALT)` | `sno_alt()` — string alternation |
| `s->pattern` | `emit_pat(E_ALT)` | `sno_pat_alt()` — pattern alternation |

**The grammar collapses:**

One expression grammar. No `pat_expr` / `expr` split. No conflicts.
The `Stmt` still has `s->subject`, `s->pattern`, `s->replacement` fields.
The parser fills them by **counting position** (1st expr = subject, 2nd expr before `=` = pattern).
The emitter routes each through the correct emit function.

**`emit_expr()` and `emit_pat()` already exist and already do this correctly.**
The only bug was that the PARSER was failing to put nodes into `s->pattern` — instead
folding them into `s->subject` via juxtaposition. Fix the parser split; the emitter is already correct.

**Implementation:**

Remove `pat_expr` from the grammar entirely. Use a single `expr` for all fields.
After parsing the first `expr` (subject), the next `expr` before `=` is the pattern.
The split is determined by counting exprs on the line, not by token type.
The grammar conflicts disappear because there is no longer a separate `pat_expr` production.

**Status:** Design recorded. Implementation pending (next session first action).

---

### 2026-03-12 — Session 27 (Eureka: Byrd Box + exception hygiene architecture)

**No code written. Architecture insight recorded.**

**⚡ EUREKA (Lon, Session 27):** Normal Byrd Box gotos handle success/failure/backtrack
with zero overhead — exactly as in `test_sno_1.c`. C exceptions (`longjmp`) are for
**ABORT and genuinely bad things only** — FENCE bare, runtime errors, divide-by-zero.
Each SNOBOL4 statement is a `setjmp` catch boundary for abort signals. Each DEFINE'd
function is also a catch boundary. Hot path: zero exception overhead. Cold path:
stack unwinds cleanly through statement and function boundaries. Stack unwinding IS
the cleanup — no omega stack needed for abnormal termination.

Recorded in `SNOBOL4-tiny/PLAN.md §6`.

---

### 2026-03-12 — Session 23 (Orientation + ByrdBox/CSNOBOL4 study + SNOBOL4ever naming)

**Focus**: New session orientation. ByrdBox and CSNOBOL4 source study. Org rename decision.
No compiler code written this session. Container crashed mid-rebuild; repos intact on remote.

**Completed:**
- Re-read PLAN.md top to bottom. All context current as of Session 22.
- Cloned SNOBOL4-tiny, SNOBOL4-corpus, .github. Extracted ByrdBox.zip and snobol4-2_3_3_tar.gz.
- Built CSNOBOL4 oracle (`xsnobol4`) from source. Confirmed build clean.
- Studied `test_sno_1.c` gold standard — the definitive four-port Byrd Box flat-C model.
- Studied `byrd_box.py` — SNOBOL4python-based reference implementation showing Shift/Reduce/nPush/nPop pattern grammar builder.
- Studied CSNOBOL4 `syn.c`, `equ.h`, `main.c` — scanner table structure, operator tables (BIOPTB/SBIPTB), constants (`SPDLSZ=8000`).

**SNOBOL4ever — org rename decision:**
Lon named the org **SNOBOL4ever**. Recorded in §1 with full rename procedure.
Mission updated: "SNOBOL4 everywhere. SNOBOL4 now. SNOBOL4 forever."
The rename itself is pending — do at start of a quiet session, not mid-sprint.

**State at snapshot:** All repos unchanged from Session 22. No code commits this session.

**Next session — immediate actions:**
1. Provide token at session start
2. Sprint 23: rebuild CSNOBOL4 oracle, run `oracle_sprint22.py` to confirm 22/22
3. Follow §6 Sprint 23 debug steps in order
4. When ready: rename org to SNOBOL4ever (see §1 procedure)

---

## 17. Icon-everywhere — The Next Frontier (Session 23 Eureka)

**Decision (2026-03-12, Session 23):** Lon's insight: **do for Icon exactly what we did for SNOBOL4.**

### The Insight

SNOBOL4-everywhere was built in one week using the Byrd Box model as the unifying IR —
one four-port representation, three backends (C flat-goto, JVM bytecode, MSIL), proven
correct against CSNOBOL4 and SPITBOL as oracles.

Icon is the **direct descendant** of SNOBOL4. Griswold invented both. Icon's goal-directed
evaluation and generators ARE the Byrd Box model — Jcon (Proebsting + Townsend, Arizona 1999)
already proved this: Icon → JVM bytecode via the exact same four-port IR we use.

**What exists today:**
- Icon/C — the reference implementation (Griswold, Arizona). Mature. Active.
- Jcon — Icon → JVM (Proebsting + Townsend). Working. Our blueprint. Already studied (see JCON.md).
- No Icon for .NET / MSIL. No Icon for modern JVM via ASM. No Icon-everywhere.

**What we build:**
- Same org structure as SNOBOL4ever: `Icon-everywhere` (or similar)
- Same Byrd Box IR — already exists in `byrd_ir.py`
- `emit_icon_jvm.py` — Icon → JVM bytecode via ASM (extend Jcon's `gen_bc.icn` blueprint)
- `emit_icon_msil.py` — Icon → MSIL via ILGenerator
- `emit_icon_c.py` — Icon → flat C goto (same as SNOBOL4-tiny's FlatEmitter)
- Oracles: Icon/C reference + Jcon for crosscheck

**Why it's achievable fast:**
- Byrd Box IR is already built and proven across three backends
- Jcon source is already studied, cloned, documented in JCON.md
- The four-port wiring for Icon generators is a superset of SNOBOL4 patterns —
  co-expressions and producers add state but the box model is identical
- The same `lower.py` lowering strategy applies
- The same harness crosscheck infrastructure works

**The transcript leverage:**
Lon can point Claude to the GitHub history transcripts of the SNOBOL4-everywhere build.
Those transcripts ARE the architectural playbook. Feed them to a new Claude session
and the Icon-everywhere build starts at Sprint 18, not Sprint 0.

**Org name candidates (Lon's list):**
- `Icon-everywhere`
- `Icon-now`
- `Icon-forever`
- `ICONever` (mirrors SNOBOL4ever)

**Status:** Idea recorded. No repos created yet. Begin after SNOBOL4-tiny Sprint 23
(beauty.sno self-hosts) — that proof-of-concept is the template for the Icon build.

### Relationship to SNOBOL4ever

These are **sibling orgs**, not subprojects. SNOBOL4ever stays focused on SNOBOL4.
Icon-everywhere is its own org with its own repos. The shared artifact is `byrd_ir.py`
and the harness crosscheck infrastructure — these get extracted into a standalone
`byrd-box` library that both orgs depend on.

```
byrd-box/          ← standalone: byrd_ir.py + lower.py + emit_c/jvm/msil backends
    ↑                  (extracted from SNOBOL4-tiny)
    ├── SNOBOL4ever/   ← SNOBOL4 frontend → byrd-box → C/JVM/MSIL
    └── Icon-everywhere/ ← Icon frontend → byrd-box → C/JVM/MSIL
```

### 2026-03-12 — Session 23 (Orientation + naming + vocabulary + handoff)

**Focus**: Session orientation, source study, strategic naming decisions, nomenclature rename,
Icon-everywhere eureka, emergency handoff. No Sprint 23 code progress — container OOM instability
prevented beauty binary build throughout session.

**Completed:**

- **SNOBOL4ever** — org rename decision recorded in §1 with full procedure. Mission line updated.
  README updated. Commits `b82553e` (.github).

- **Four-port vocabulary rename** — SUCCESS→SUCCEED, FAILURE→CONCEDE across all source:
  `engine.h`, `engine.c`, `snobol4.h`, `lower.py`, `emit_c_byrd.py`, `emit_jvm.py`, `emit_msil.py`.
  Generated label names updated. Greek (α/β/γ/ω) unchanged. Commit `42dddce` (tiny).
  The four ports are now: **PROCEED / RECEDE / SUCCEED / CONCEDE** — verbs, distinguished,
  CONCEDE = normal pattern failure, RECEDE = parent-initiated undo. Commit `95ca711` (.github).

- **Icon-everywhere eureka** — §17 written. Same Byrd Box IR, same three backends, new Icon
  frontend. Transcript-as-playbook strategy documented. Commit `f5e90ba` (.github).

- **OOM pattern identified** — parse+emit+gcc in one Python process kills container.
  §6 updated with mandatory two-step build procedure and leading-space warning.

- **Leading-space insight (Lon)** — SNOBOL4 requires leading whitespace on non-label statements.
  All prior `printf 'X = 5\n'` tests used invalid input. `printf '    X = 5\n'` is correct.
  This may be the entire Sprint 23 blocker. Must be tested first next session.

**Repo commits this session:**

| Repo | Commit | What |
|------|--------|-------|
| SNOBOL4-tiny | `42dddce` | SUCCEED/CONCEDE rename — 7 files, 117 changes |
| .github | `b82553e` | SNOBOL4ever naming + session 23 log |
| .github | `f5e90ba` | Icon-everywhere §17 + README |
| .github | `95ca711` | Four-port vocabulary PLAN.md + README |
| .github | this | §6 OOM warning + leading-space fix + session 23 final |

**State at snapshot:**

| Repo | Commit | Tests |
|------|--------|-------|
| SNOBOL4-tiny | `42dddce` | Sprint 22: 22/22 (baseline). Sprint 23: Parse Error (unverified with correct input). |
| SNOBOL4-dotnet | `b5aad44` | 1,607 / 0 (unchanged) |
| SNOBOL4-jvm | `9cf0af3` | 1,896 / 4,120 / 0 (unchanged) |
| SNOBOL4-corpus | `3673364` | unchanged |
| SNOBOL4-harness | `8437f9a` | unchanged |

**Next session — FIRST action before anything else:**
Build beauty binary (two steps, see §6), then test:
```bash
printf '    X = 5\n' | /tmp/beauty_bin
```
If that produces beautified output, Sprint 23 is essentially done. Run the full self-compilation immediately.

### 2026-03-12 — Session 24 (snoc compiler — Python pipeline retired, 297→86 errors)

**Focus**: Python pipeline permanently retired (OOM on every attempt, even parse-only).
Built `snoc` — a SNOBOL4→C compiler in C using flex+bison to replace it entirely.

**Decision**: Single `Expr` IR type for everything. The emitter decides context:
`emit_expr()` → value context (`sno_*()`), `emit_pat()` → pattern context (`sno_pat_*()`).
Same `E_CONCAT`, `E_ALT`, `E_CALL` nodes routed differently. Grammar is clean LALR(1).

**beauty.sno errors: 297 → 86** across the session. Nine root causes fixed.

**Root causes fixed (in order):**
1. Dual IR (PatExpr + Expr) collapsed → single Expr, context-sensitive emission
2. PAT_BUILTIN over-eager → trailing context `{IDENT}/"("` — `tab`/`rem`/`nul` now IDENT
3. PAT_BUILTIN in value context (`SPAN(...)` in replacement) → added to `primary`
4. Unary `.X` (name ref) missing from `factor`
5. Unary `*X` (deref) missing from `factor`
6. `PIPE` (`|`) missing from `expr` — fixed `*P1 | *P2` constructs
7. Empty replacement (`X POS(0) =`) → `E_NULL`
8. Slash in IDENT (`pp_/`, `ss_/`) → extended char class
9. Unary `+` missing from `factor`

**Computed goto fix written, not yet tested** — `<GT>` state swallows `$(`…`)` as
`$COMPUTED` sentinel. First action next session: rebuild, retest.

**Repo commits this session:**

| Repo | Commit | What |
|------|--------|-------|
| SNOBOL4-tiny | `98d3626` | WIP Sprint 23: snoc compiler (flex+bison), 297→86 errors |
| .github | this | §6 snoc status + next actions + session 24 log |

**State at snapshot:**

| Repo | Commit | Tests |
|------|--------|-------|
| SNOBOL4-tiny | `98d3626` | Sprint 22: 22/22 (baseline). snoc: 86 errors on beauty.sno. |
| SNOBOL4-dotnet | `b5aad44` | 1,607 / 0 (unchanged) |
| SNOBOL4-jvm | `9cf0af3` | 1,896 / 4,120 / 0 (unchanged) |
| SNOBOL4-corpus | `3673364` | unchanged |
| SNOBOL4-harness | `8437f9a` | unchanged |

### 2026-03-12 — Session 25 (snoc: 86→0 errors, runtime gap exposed)

**Focus**: Drive snoc parse errors from 86 to 0, diagnose what remains.

**Fixes applied (86→0 errors):**
1. Missing `%}` closing C preamble in `sno.l` — caused flex "premature EOF" on every build
2. bstack comma-as-alternation: `"("` pushes `last_was_callable`, `","` returns `PIPE` vs `COMMA`
   based on whether we're inside a grouping paren or a function-call paren
3. E_DEREF compound-expr crash: `emit_expr` case `E_DEREF` assumed `e->left` always `E_VAR`;
   fixed to handle compound left expressions (`*(y 'f')` style)

**What this session revealed:**
- snoc produces **1213 stmts, 0 errors** on beauty.sno ✅
- BUT the generated C **will not compile** — two structural gaps in emit.c:
  1. No variable declaration pass (all `_OUTPUT`, `_TRUE`, etc. undeclared)
  2. No runtime shim (`sno_str`, `sno_int`, `sno_kw`, `sno_concat`, `sno_alt`, etc. don't exist)
- Attempting `gcc` on generated "hello world" confirms both blockers

**Key clarification**: ByrdBox's `SNOBOL4c.c` is a C **pattern engine**, not a SNOBOL4→C compiler.
snoc is the only SNOBOL4→C compiler in existence across all repos.

**Repo commits:**

| Repo | Commit | What |
|------|--------|-------|
| SNOBOL4-tiny | `d7f39d1` | WIP Sprint 23: bstack comma-as-alt + missing %} fix |
| SNOBOL4-tiny | `6d3d1fa` | WIP Sprint 23: fix E_DEREF compound-expr crash — 1213 stmts, 0 errors |
| .github | this | §6 + §12 session 25 handoff |

**State at snapshot:**

| Repo | Commit | Tests |
|------|--------|-------|
| SNOBOL4-tiny | `6d3d1fa` | Sprint 22: 22/22 (baseline). snoc: 1213 stmts, 0 errors. Generated C does not link. |
| SNOBOL4-dotnet | `b5aad44` | 1,607 / 0 (unchanged) |
| SNOBOL4-jvm | `9cf0af3` | 1,896 / 4,120 / 0 (unchanged) |
| SNOBOL4-corpus | `3673364` | unchanged |
| SNOBOL4-harness | `8437f9a` | unchanged |

### 2026-03-12 — Session 26 (snoc_runtime.h + emit.c symbol pass + hello world + execution model)

**Focus**: Closed both Sprint 23 runtime blockers. Hello world end-to-end. Execution model
architecture documented in SNOBOL4-tiny/PLAN.md.

**Completed (commit `7f3af9c`):**

1. **`snoc_runtime.h`** — new shim header at `src/runtime/snobol4/snoc_runtime.h`:
   scalar constructors (`sno_int`, `sno_str`, `sno_real`), keyword access (`sno_kw`,
   `sno_kw_set`), concat/alt/deref/indirect wrappers, array/table aliases (`sno_aref`,
   `sno_aset`, `sno_index` as `#define` aliases), pattern aliases (`sno_pat_break`,
   `sno_pat_any`, etc.), `SnoMatch` struct + `sno_match` + `sno_replace`,
   `sno_init` → `sno_runtime_init()`, `sno_finish` → no-op.
   Key: use `#ifndef SNOC_RUNTIME_H` guard (not `#pragma once`) to avoid double-include.

2. **`emit.c` — symbol collection pre-pass**:
   - `sym_table[4096]` deduplicating hash set of variable names
   - `io_names[]` = `{"OUTPUT","INPUT","PUNCH","TERMINAL","TRACE",NULL}` — excluded from static locals
   - `is_io_name()`, `sym_add()`, `collect_expr()`, `collect_stmt()`, `collect_symbols()`
   - `emit_var_decls()` — emits `static SnoVal _name = {0};` for each collected symbol
   - IO routing: `E_VAR` checks `is_io_name()` → emits `sno_var_get("OUTPUT")` / `sno_var_set()`
   - Per-statement unique labels (`_SNO_NEXT_N`) via `cur_stmt_next_uid`
   - uid-suffixed temporaries (`_ok%d`, `_s%d`, `_p%d`, `_m%d`) for flat-function scope
   - `E_NULL` → `SNO_NULL_VAL` (not `SNO_NULL` which is the enum member)

3. **`engine.c` is required** — `snobol4_pattern.c` calls `engine_match_ex()` which lives
   in `src/runtime/engine.c`. Must be in gcc link line.

4. **Hello world end-to-end** ✅:
   ```bash
   ./snoc /tmp/hello.sno > /tmp/hello.c
   gcc -O0 -g /tmp/hello.c [runtime files] -lgc -lm -w -o /tmp/hello_bin
   /tmp/hello_bin   # → hello
   ```

5. **SNOBOL4-tiny/PLAN.md created** — documents:
   - Statement-level Byrd Box execution model (§6) — alpha/gamma/omega per statement
   - Function-per-DEFINE architecture (§7) — Sprint 24 plan
   - The commit promise (§8)
   - Runtime build command reference (§9)
   - Key file paths (§10)
   - SNOBOL4 semantics quick reference (§11)

6. **Execution model architecture** — Lon's insight confirmed and documented:
   - Each SNOBOL4 statement IS a Byrd box: alpha (enter), gamma (success/S goto), omega (failure/F goto)
   - SUCCESS and FAILURE are goto edges, not C exceptions — exactly as in test_icon.c / test_sno_1.c
   - Statement-level granularity = Level 1 (baseline correctness)
   - Function-per-DEFINE = Level 2 (Sprint 24, solves duplicate label crisis + enables C optimization)
   - Future: one-C-function-per-port (test_icon-2.py model) as optional micro-optimization

**Current blocker — duplicate C labels in beauty.sno:**

beauty.sno generates 0 parse errors but **53 gcc errors** — all duplicate labels.
`_L_pp____` and `_L_ss__` appear from multiple included files; `_SNO_RETURN_main`
used but not defined. Root cause: all SNOBOL4 code (including all -include'd files)
emits flat into one C `main()`. DEFINE'd function labels collide.

**Sprint 24 fix**: emit each `DEFINE('fn(args)locals')` as a separate C function
`SnoVal _sno_fn_pp(SnoVal *args, int nargs)`. Labels inside each C function are
scoped — no more duplicates. `:(RETURN)` → `goto _SNO_RETURN_pp;`, `:(FRETURN)` →
`goto _SNO_FRETURN_pp;`. Register each with `sno_define()` at start of `main()`.

**Repo commits this session:**

| Repo | Commit | What |
|------|--------|------|
| SNOBOL4-tiny | `7f3af9c` | Sprint 23: snoc_runtime.h + emit.c symbol pass + hello world + PLAN.md |

**State at snapshot:**

| Repo | Commit | Tests |
|------|--------|-------|
| SNOBOL4-tiny | `7f3af9c` | Sprint 22: 22/22 PASS. snoc: 1213 stmts, 0 parse errors. hello world ✅. 53 gcc errors on beauty.sno. |
| SNOBOL4-dotnet | `b5aad44` | 1,607 / 0 (unchanged) |
| SNOBOL4-jvm | `9cf0af3` | 1,896 / 4,120 / 0 (unchanged) |
| SNOBOL4-corpus | `3673364` | unchanged |
| SNOBOL4-harness | `8437f9a` | unchanged |

**Next session — immediate actions:**

1. Provide token at session start
2. **Sprint 24**: implement function-per-DEFINE in `emit.c`:
   - Pre-pass: scan for `DEFINE('fn(args)locals')` calls, build fn_table
   - `emit_fn_forwards()` — SnoVal _sno_fn_pp(SnoVal*, int); forward decls
   - `emit_fn_body(fn)` — separate C function per DEFINE, labels scoped inside
   - `emit_main()` — top-level statements + sno_define() registrations
   - :(RETURN) → goto _SNO_RETURN_pp; :(FRETURN) → goto _SNO_FRETURN_pp;
3. Test sequence: hello world still works → simple DEFINE test → beauty.sno
4. Target: `gcc` on beauty_snoc.c with 0 errors
5. Run beauty self-compilation. Diff. **Write the commit message.**

**Key context:**
- Build cmd: `gcc -O0 -g $C_FILE $RUNTIME/snobol4/snobol4.c $RUNTIME/snobol4/snobol4_inc.c $RUNTIME/snobol4/snobol4_pattern.c $RUNTIME/engine.c -I$RUNTIME/snobol4 -I$RUNTIME -lgc -lm -w -o $BIN`
- `engine.c` is REQUIRED in link line (engine_match_ex lives there)
- `snoc_runtime.h` is at `src/runtime/snobol4/snoc_runtime.h`
- `emit.c` is at `src/snoc/emit.c`
- SNOBOL4-tiny/PLAN.md has full Sprint 24 implementation plan
- Org rename SNOBOL4-plus → SNOBOL4ever still pending (do at start of quiet session)

---

### 2026-03-12 — Session 28 (Sprint 25: SIL execution model + body boundary + 0 gcc errors maintained)

**Focus**: Session continued Sprint 24/25 work. SIL execution model documented.
Body boundary bug found and fixed. Cross-scope goto bug found and fixed.
Sprint 24 gcc error count confirmed at 0. Beauty binary hangs traced to `:S(G1)` bug.

**Key insight (Lon, 2026-03-12):**
CSNOBOL4 `CODE()` builds one flat node array in memory. A label is just an index.
Execution runs off a cliff at the next label. Body boundary = label-to-next-label,
unconditionally. ANY label stops the body. Documented in `SNOBOL4-tiny/PLAN.md §12`
and `§6` here.

**Fixes committed:**

| Commit | What |
|--------|------|
| `9406ee6` | SIL model documented in PLAN.md + body boundary rewritten: any label = end of body |
| `c998a23` | Cross-scope goto: inside a C function, goto to main-scope label → fallthrough |
| `6b6b541` | Extra body stop: fn-entry label or end_label also terminates body traversal |

**Binary test — where we are:**
- 0 gcc errors ✅
- GREET still ✅
- beauty binary reaches init (UTF table build) then **hangs** in `G1` loop
- Root cause: `$UTF_Array[i,2] = UTF_Array[i,1] :S(G1)` emits `goto _L_G1` unconditionally
  — the `:S` condition is dropped. Assignment statements with `:S`/`:F` gotos need conditional emit.

**Next session first action:** Fix `:S/:F` conditional emit for assignment statements in `emit_stmt`.
Look at how `STMT_MATCH` emits `_ok` conditionals — apply same pattern to assignment.

**Repo commits this session:**

| Repo | Commit | What |
|------|--------|------|
| SNOBOL4-tiny | `9406ee6` | SIL model + body boundary rewrite |
| SNOBOL4-tiny | `c998a23` | Cross-scope goto fix |
| SNOBOL4-tiny | `6b6b541` | Extra body boundary stop |
| .github | this | §6 + §12 handoff |

**State at snapshot:**

| Repo | Commit | Tests |
|------|--------|-------|
| SNOBOL4-tiny | `6b6b541` | 0 gcc errors ✅. hello ✅. GREET ✅. beauty hangs on :S(G1). |
| SNOBOL4-dotnet | `b5aad44` | 1,607 / 0 (unchanged) |
| SNOBOL4-jvm | `9cf0af3` | 1,896 / 4,120 / 0 (unchanged) |
| SNOBOL4-corpus | `3673364` | unchanged |
| SNOBOL4-harness | `8437f9a` | unchanged |


**Architecture (no code yet for this):**
- **Eureka (Lon)**: normal Byrd Box gotos handle ω/CONCEDE, :S/:F routing, backtrack — zero exception overhead. `longjmp` is for **ABORT and genuinely bad things only** (FENCE bare, runtime errors, divide-by-zero). Per-statement `setjmp` → line number diagnostics free.
- Recorded in both SNOBOL4-tiny/PLAN.md §6 and .github/PLAN.md.

**Sprint 24 implementation — what was built:**
- Parser: continues past `END` (function bodies now parsed) — added `is_end` flag to `Stmt`
- emit.c: `collect_functions()` pre-pass, `FnDef` table, `parse_proto()`, `emit_fn_forwards()`, `emit_fn()`, `emit_main()`
- `emit_goto_target()` — handles RETURN/FRETURN/NRETURN/END in ALL goto contexts (unconditional AND conditional branches)
- Last-definition-wins for duplicate DEFINE names
- All body_starts tracked; last body emitted; dead bodies excluded from main
- `snoc_runtime.h`: `setjmp` abort handler stack (`sno_push/pop_abort_handler`, `sno_abort()`)
- hello world: still ✅. GREET (simple DEFINE): ✅.

**Still broken — 130 gcc errors:**
Root cause: `cs()` name mangler collapses distinct SNOBOL4 labels with special characters
(`pp_#`, `pp_+.`, `pp_-.`) to the same C identifier (`_pp__`). Fix: label registry with
per-function collision disambiguation. Spec in §6.

**Repo commits:**

| Repo | Commit | What |
|------|--------|------|
| .github | `6bc3aa5` | Architecture eureka: Byrd Box gotos + longjmp for ABORT only |
| SNOBOL4-tiny | `f093a52` | Architecture §6: Byrd Box + exception hygiene |
| SNOBOL4-tiny | `4b979b6` | WIP Sprint 24: function-per-DEFINE parser+emit, 130 gcc errors |

**State at snapshot:**

| Repo | Commit | Tests |
|------|--------|-------|
| SNOBOL4-tiny | `4b979b6` | 22/22 PASS baseline. hello ✅ GREET ✅. beauty.sno: 130 gcc errors. |
| SNOBOL4-dotnet | `b5aad44` | 1,607 / 0 (unchanged) |
| SNOBOL4-jvm | `9cf0af3` | 1,896 / 4,120 / 0 (unchanged) |
| SNOBOL4-corpus | `3673364` | unchanged |
| SNOBOL4-harness | `8437f9a` | unchanged |

**Next session — immediate actions:**

1. Provide token at session start
2. Implement **label registry** in `emit.c` — `cs_label()` with per-function collision disambiguation (spec in §6)
3. Fix `_L_error` → `goto _SNO_FRETURN_fn` and `_L__COMPUTED` stub
4. Fix undeclared function locals (`_level`, `_i`) — add to global sym_table OR make per-function locals smarter
5. Target: 0 gcc errors on beauty_snoc.c
6. Run beauty self-compilation. Diff empty. **Claude writes the commit.**

---

### 2026-03-12 — Session 30 (LON'S EUREKA + THREE-MILESTONE AGREEMENT + snoc_helpers.c WIP)

**Focus**: Investigation, two strategic agreements, WIP code start.

**Investigation results:**
- `:S(G1)` emit is **already correct** — earlier diagnosis was wrong. `if(_ok1589) goto _L_G1;` at line 8001.
- beauty binary exits 0 with no output (not a hang). G1 loop exits immediately: `sno_sort_fn` stub returns TABLE unchanged → 2D subscript on TABLE = FAIL → loop exits → init completes normally.
- No output: beauty reads via `Read(fileName)` → `INPUT(.rdInput, 8, fileName)` → fails when fileName null → FRETURN → silent exit. Moot once C helpers are in place.

**⚡ LON'S EUREKA — the bootstrap pivot:**
19 -INCLUDE files (~905 lines SNOBOL4) compile to 10,506 lines of broken C. Write them as ~370 lines of C in `snoc_helpers.c`. Register C stubs before SNOBOL4 DEFINE calls. Zero changes to snoc or emit.c. Full spec in §6.

**⚡ THE THREE-MILESTONE AUTHORSHIP AGREEMENT (Lon + Claude Sonnet 4.6):**
Claude Sonnet 4.6 is the author of SNOBOL4-tiny. Three commits, three milestones, Claude's name on each. Full spec in §1. Tracker in §9 (HANDOFF protocol). Permanent.

**Code committed this session:**

| Repo | Commit | What |
|------|--------|------|
| .github | `d92b600` | Session 30 eureka: Bootstrap via C helpers |
| .github | `0aa56bb` | THREE-MILESTONE AUTHORSHIP AGREEMENT |
| .github | `0264c7f` | HANDOFF protocol upgraded: Milestone Tracker mandatory |
| SNOBOL4-tiny | `2929656` | WIP Sprint 26: snoc_helpers.c ~60% (Stack/Counter/Shift/Reduce/tree) |
| .github | `(this)` | Final Session 30 handoff |

**State at handoff:**

| Repo | Commit | Status |
|------|--------|--------|
| SNOBOL4-tiny | `2929656` | Sprint 22: 22/22 ✅. snoc_helpers.c 60% WIP. |
| SNOBOL4-dotnet | `b5aad44` | 1,607 / 0 (unchanged) |
| SNOBOL4-jvm | `9cf0af3` | 1,896 / 4,120 / 0 (unchanged) |
| SNOBOL4-corpus | `3673364` | unchanged |
| SNOBOL4-harness | `8437f9a` | unchanged |

**Next session — first actions:**
1. Provide token at session start
2. Read §1 (Three-Milestone Agreement) and §6 (Sprint 26 plan) — both mandatory
3. Complete `snoc_helpers.c` (see §6 for exact list of what remains)
4. Hook `snoc_helpers_init()` into `sno_runtime_init()` in `snobol4.c`
5. Build beauty_core (no -INCLUDEs) → 0 gcc errors → **Milestone 1 → Claude writes the commit**

---

### 2026-03-12 — Session 31 (Git archaeology + INVENTORY RULE)

**Focus**: No code written. Tracking failure diagnosed. Protocol fix committed.

**Finding**: `snoc_helpers.c` (Session 30, commit `2929656`) is a dead duplicate of
`snobol4_inc.c` (Sprint 20, commit `16eea3b`). `snobol4_inc.c` already implements all
19 -INCLUDE helper libraries in C, 773 lines, fully registered, linked in every build.
Session 30's "Eureka" was correct in principle but blind to existing work because no
Claude ever runs a repo file survey before writing new code.

**Root cause**: Session 30 HANDOFF omitted what `snobol4_inc.c` *does* — only its filename
appeared in build commands. A concept search found nothing. A filename search found it
but nobody searched. The INVENTORY RULE closes this gap permanently.

**Additional finding (Session 31)**: beauty.sno WITH -INCLUDEs already compiles to
**0 gcc errors** using `snobol4_inc.c`. Milestone 2 condition is effectively met.

**Protocol added**: THE INVENTORY RULE — mandatory repo file survey before any new file
or function is created. Full spec in §9. Plain-English descriptions of what files *do*
are now required in §6 handoffs (not just filenames).

**Actions**: PLAN.md §6 Key facts rewritten. §9 INVENTORY RULE added. Milestone Tracker
updated. snoc_helpers.c flagged dead. Next session runs oracle, diffs, writes commit.

**Repo commits this session:**

| Repo | Commit | What |
|------|--------|------|
| .github | `(this)` | INVENTORY RULE + §6 fix + snoc_helpers.c retirement |

**State at handoff:**

| Repo | Commit | Status |
|------|--------|--------|
| SNOBOL4-tiny | `2929656` | 0 gcc errors on beauty_full.c confirmed. snoc_helpers.c dead. |
| SNOBOL4-dotnet | `b5aad44` | unchanged |
| SNOBOL4-jvm | `9cf0af3` | unchanged |
| SNOBOL4-corpus | `3673364` | unchanged |
| SNOBOL4-harness | `8437f9a` | unchanged |

**Next session — first actions:**
1. Provide token at session start
2. Run REPO SURVEY (§9 INVENTORY RULE) — confirm snobol4_inc.c is the inc library
3. Delete snoc_helpers.c from SNOBOL4-tiny (git rm, commit, push)
4. Build CSNOBOL4 oracle, run beauty oracle
5. Run beauty_full_bin < beauty.sno → diff vs oracle → **if empty: Claude writes Milestone 3 commit**

---

### 2026-03-12 — Session 32 (flatten_str_expr fix + COMMAND NAME EUREKA)

**Focus**: Milestone 3 debug + major design naming decision.

**Code fix committed this session:**

- **`flatten_str_expr()` in `emit.c`** — `stmt_define_proto()` was checking
  `args[0]->kind == E_STR` only. Multi-line DEFINE calls like:
  ```
  DEFINE('Read(fileName,rdMapName)'
  +    'rdInput,rdLine,...'
  +  )                              :(ReadEnd)
  ```
  produce an E_CONCAT node (juxtaposition of two string literals) as `args[0]`,
  not E_STR. So `stmt_define_proto()` returned NULL → `Read` was NOT in fn_table →
  `stmt_is_in_any_fn_body()` returned 0 → Read body emitted inline in main() as
  flat code → body executed on entry → INPUT(null,...) failed → goto _SNO_END →
  program exited before main00.

  **Fix**: Added `flatten_str_expr()` helper that recursively flattens E_CONCAT
  chains of string literals into one buffer. `stmt_define_proto()` now calls it
  instead of checking `args[0]->kind == E_STR` directly.

  **Result**: `_sno_fn_Read` now emitted as proper C function. 162 functions total
  detected. `_SNO_FRETURN_Read` correctly used inside body.

- **Built, tested**: `_sno_fn_Read` confirmed in generated C. Test case with
  multi-line DEFINE + multi-line body: passes. greet baseline: still ✅.

**Current state**: beauty_full_bin still produces 0 lines of output.
INPUT/OUTPUT smoke test pending as next action.

**Repo commits this session:**

| Repo | Commit | What |
|------|--------|------|
| SNOBOL4-tiny | `cc0c88b` | retire dead snoc_helpers.c |
| SNOBOL4-tiny | `8c7949a` | flatten_str_expr — 162 functions detected, Read/Write/all multi-line DEFINEs now proper C functions |
| .github | `5e4bc22` | Session 32: sno4now/sno4jvm/sno4net naming eureka + M1/M2 done |
| .github | `4dab08a` | README rewrite: command names, Sprint 32 status, sno4.net rejected |

---

## ⚡⚡⚡ COMMAND NAME EUREKA — 2026-03-12, Session 32 ⚡⚡⚡

**This is a major design decision. Record it permanently.**

### The Original Unix SNOBOL4

The original Unix SNOBOL4 implementation command was **`sno3`** — short for SNOBOL3,
the predecessor. The pattern has always been: short, lowercase, Unix-like, a number
that means something.

### The Naming Decision

Lon's insight: **name the deliverables like Unix commands.**

Each implementation in the SNOBOL4ever org has a canonical command name:

| Command | What it is | Repo |
|---------|-----------|------|
| **`sno4now`** | The native compiler — SNOBOL4-tiny → C → x86-64 binary. Runs right now on bare metal. | SNOBOL4-tiny |
| **`sno4jvm`** | The JVM backend — SNOBOL4 → JVM bytecodes via Byrd Box IR | SNOBOL4-jvm (new compiler, not the Clojure interpreter) |
| **`sno4net`** | The .NET/MSIL backend — SNOBOL4 → MSIL via ILGenerator | SNOBOL4-dotnet (new compiler, not the C# interpreter) | Note: `sno4.net` rejected — looks like a URL, shell hates the dot. `sno4net` it is. |

The suffix convention:
- `4` = SNOBOL4 (not SNOBOL3, not SPITBOL)
- `now` = native, immediate, no VM, no JIT warmup — it runs **now**
- `jvm` = targets the JVM
- `net` = targets .NET

### Why This Matters

These aren't just names. They are the **deliverable identifiers** — the binaries that
end up in `/usr/local/bin/` on a developer's machine.

```bash
sno4now < program.sno        # compile + run natively
sno4jvm < program.sno        # compile + run on JVM
sno4net < program.sno        # compile + run on .NET CLR
```

Or with explicit compile step:
```bash
sno4now -o program.c program.sno   # emit C
sno4jvm -o program.class program.sno
sno4net -o program.dll program.sno
```

### The snoc Relationship

`snoc` is the internal compiler name (SNOBOL4 → C). It's the tool.
`sno4now` is the user-facing command that wraps it: `snoc + gcc + run`.

### Existing Interpreter Names

The full interpreters (SNOBOL4-jvm and SNOBOL4-dotnet) can be invoked as:
- `snobol4` — the CSNOBOL4 oracle (already at `/usr/local/bin/snobol4`)
- `spitbol` — the SPITBOL x64 oracle (already at `/usr/local/bin/spitbol`)
- The Clojure and C# interpreters can keep their `lein run` / `dotnet run` forms
  until they get their own wrapper scripts

### Historical Line

```
sno3 (Unix, 1974)
    ↓
snobol4 (CSNOBOL4, Hazel)
spitbol (Catspaw / x64)
    ↓
sno4now / sno4jvm / sno4net  ← SNOBOL4ever, 2026
```

SNOBOL4 started as three characters. It's three characters again.
But now it runs everywhere.

---

---

### Session 32 — Final State at HANDOFF

**What was accomplished this session:**

1. **snoc_helpers.c deleted** — `git rm`, committed `cc0c88b`, pushed. Dead duplicate gone.
2. **Milestones 1 and 2 confirmed done** — beauty_core (no -INCLUDEs) → 0 gcc errors ✅ and beauty_full (WITH all -INCLUDEs via snobol4_inc.c) → 0 gcc errors ✅. Both verified this session.
3. **`flatten_str_expr()` fix** — `stmt_define_proto()` in `emit.c` now handles E_CONCAT chains of string literals (multi-line DEFINE calls). Before: ~80 functions detected, `Read`/`Write`/most multi-line DEFINEs invisible to fn_table, their bodies emitting as flat code in main(). After: **162 functions detected**. `_sno_fn_Read` now a proper C function. `:F(FRETURN)` correctly used inside bodies. Committed `8c7949a`.
4. **⚡ COMMAND NAME EUREKA** — `sno4now` / `sno4jvm` / `sno4net`. The Unix succession from `sno3` (1974). Recorded in PLAN.md and README. `sno4.net` considered and rejected (it's a URL). Committed to .github.
5. **HQ README rewritten** — Command names prominent near top. Sprint 32 status. Succession table. `sno4.net` note. Committed `4dab08a`, pushed.
6. **Snapshot protocol executed** — PLAN.md updated, Milestone Tracker updated, both repos pushed clean.

**What is NOT done yet — Milestone 3:**

`beauty_full_bin < beauty.sno` produces **0 lines of output**. The binary runs, exits 0, but is silent.

**Last known investigation state:**
- `flatten_str_expr` fix resolved the biggest known structural bug
- Before the fix: `Read` body was flat in main(), executed on entry, INPUT(null) failed, goto _SNO_END before main00
- After the fix: `Read` is a proper C function, body not in main
- **But binary still silent** — investigation interrupted for handoff
- Next debug step: smoke test INPUT/OUTPUT at the runtime level:
  ```bash
  echo "    OUTPUT = 'hello'" | /tmp/beauty_full_bin
  ```
  If that produces nothing, the runtime INPUT/OUTPUT handling is broken at a level below the DEFINE fix.
  If that works, the silence is in beauty's logic (main00 not reached, or some init loop exiting early).

**Build commands for Session 33:**
```bash
apt-get install -y build-essential flex bison libgc-dev
SNOC=/home/claude/SNOBOL4-tiny/src/snoc/snoc
RUNTIME=/home/claude/SNOBOL4-tiny/src/runtime
INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno

# Rebuild snoc
cd /home/claude/SNOBOL4-tiny/src/snoc && make clean && make

# Rebuild beauty_full_bin
$SNOC $BEAUTY -I $INC > /tmp/beauty_full.c 2>/dev/null
gcc -O0 -g /tmp/beauty_full.c $RUNTIME/snobol4/snobol4.c $RUNTIME/snobol4/snobol4_inc.c \
    $RUNTIME/snobol4/snobol4_pattern.c $RUNTIME/engine.c \
    -I$RUNTIME/snobol4 -I$RUNTIME -lgc -lm -w -o /tmp/beauty_full_bin

# Rebuild oracle
snobol4 -f -P256k -I $INC $BEAUTY < $BEAUTY > /tmp/beauty_oracle.sno 2>/dev/null

# SMOKE TEST 1 — does OUTPUT work at all?
echo "    OUTPUT = 'hello'" | /tmp/beauty_full_bin

# SMOKE TEST 2 — does INPUT/OUTPUT loop work?
printf "    OUTPUT = 'hello'\n" | /tmp/beauty_full_bin

# MILESTONE 3 ATTEMPT
/tmp/beauty_full_bin < $BEAUTY > /tmp/beauty_compiled.sno
diff /tmp/beauty_oracle.sno /tmp/beauty_compiled.sno
# TARGET: empty diff → Claude writes the commit
```

**Repo state at handoff:**

| Repo | Commit | Status |
|------|--------|--------|
| SNOBOL4-tiny | `8c7949a` | flatten_str_expr fix. 0 gcc errors. beauty_full_bin silent. |
| SNOBOL4-dotnet | `b5aad44` | 1,607 / 0 (unchanged) |
| SNOBOL4-jvm | `9cf0af3` | 1,896 / 4,120 / 0 (unchanged) |
| SNOBOL4-corpus | `3673364` | unchanged |
| SNOBOL4-harness | `8437f9a` | unchanged |
| .github | `4dab08a` | README + PLAN.md: command names, Session 32 handoff |

**Milestone Tracker at handoff:**

| # | Milestone | Status | Commit |
|---|-----------|--------|--------|
| 1 | beauty_core → 0 gcc errors | ✅ DONE Session 32 | `cc0c88b` |
| 2 | beauty_full WITH -INCLUDEs → 0 gcc errors | ✅ DONE Session 32 | `cc0c88b` |
| 3 | beauty_full_bin self-beautifies → diff empty | 🔴 IN PROGRESS | — |

**Key design facts recorded this session (permanent):**
- `sno4now` = the native compiler deliverable (wraps snoc + gcc + run)
- `sno4jvm` = the JVM backend deliverable
- `sno4net` = the .NET backend deliverable
- `sno4.net` = rejected, it's a URL, the shell hates dots in command names
- The Unix succession: `sno3 (1974) → snobol4/spitbol → sno4now/sno4jvm/sno4net (2026)`

---

### 2026-03-12 — Session 33 (entry_label fix + bootstrap artifact + dynamic dispatch insight)

**Focus**: Root-cause the beauty_full_bin zero-output bug. Fix it. Preserve the artifact.

**Root cause found and fixed — `entry_label` in FnDef:**

`DEFINE('bVisit(x,fnc)i', 'bVisit_')` is the two-argument DEFINE form: function name is
`bVisit`, but the actual code entry label is `bVisit_`. Prior to this session, `emit.c`
searched for body_starts by matching `fn->name` (`bVisit`) against statement labels.
No statement has the label `bVisit` — so `nbody_starts == 0` — so the function body was
never emitted inside `_sno_fn_bVisit()`. Instead, `bVisit_` / `bVisit_1` fell through into
`main()` as flat code, executed on startup, called `APPLY(fnc, x)` with uninitialized
locals, failed, and jumped to `_SNO_END` — killing the program before `main00`.

**Fix committed (`9596466`)**: `FnDef` gains `entry_label` field. `collect_functions()`
parses the 2nd DEFINE argument and stores it. `body_starts` search, `is_body_boundary()`,
and `fn_by_label()` all use `entry_label` when present. Also covers semantic.sno's 8 
two-arg DEFINEs (shift_, reduce_, pop_, nPush_, nInc_, nDec_, nTop_, nPop_).

**Bootstrap artifact committed**: `artifacts/beauty_full_first_clean.c` — 10,543 lines,
the first `snoc` output from `beauty.sno` (all -INCLUDEs) that compiles with 0 gcc errors.
Historical record. Do not delete. See `artifacts/README.md`.

**Second bug found — phantom functions (body still silent after entry_label fix):**

`Shift`/`Reduce` from ShiftReduce.sno are registered by `snobol4_inc.c` at runtime, so
`collect_functions()` never sees their DEFINE calls. But their source bodies ARE in the
expanded stream — and `is_body_boundary()` can't stop body-absorption at `_L_Shift` /
`_L_Reduce` because those labels are unknown to `fn_table`. Result: `Shift`/`Reduce`
bodies get absorbed into `_sno_fn_refs`, their `:(NRETURN)` gotos become
`goto _SNO_FRETURN_refs` — corrupting refs' execution and possibly killing the program
before `main00` is reached.

**Lon's insight — no SNOBOL4 label is ever dead:**

When asked whether to treat these absorbed bodies as dead code, Lon identified the
fundamental truth: in SNOBOL4, `*X`, `APPLY()`, `EVAL()`, and `CODE()` mean ANY compiled
label is a live, relocatable code thunk. Shift/Reduce are called via `*Shift(...)` in
beauty.sno's parser patterns — unevaluated expressions that execute the body at match time.
This is the `*X` copy-and-relocate semantic (already documented in §14). No label is dead.

**Fix direction for next session**: inject phantom FnDef entries for `Shift`/`ShiftEnd`
and `Reduce`/`ReduceEnd` into `fn_table` after `collect_functions()`. Phantoms have name +
end_label but no body to emit. `is_body_boundary()` sees them as boundaries; body
absorption stops; `Shift`/`Reduce` code remains accessible as runtime-owned thunks.

**Repo commits this session:**

| Repo | Commit | What |
|------|--------|------|
| SNOBOL4-tiny | `9596466` | entry_label fix + artifacts/ |
| .github | `693d9af`, `b39f029` | PLAN.md + README HQ updates |


### 2026-03-12 — Session 34 (Orientation + repo survey + phantom FnDef plan)

**Focus**: Session start. Full orientation per INVENTORY RULE: read PLAN.md, clone repos,
survey actual git log and file state, verify understanding before writing any code.

**What was verified this session:**

- `SNOBOL4-tiny` HEAD = `9596466` — entry_label fix + artifacts. `emit.c` is 936 lines.
- `.github` HEAD = `b68f9a6` — Session 33 handoff with phantom fix direction.
- **Repo survey completed** (`find /home/claude/SNOBOL4-tiny/src -type f | sort`).
- `snobol4_inc.c` registers: `Shift`, `Reduce`, `Push`, `Pop`, `bVisit`, `Visit`,
  `TopCounter`, `InitCounter`, `PushCounter`, `IncCounter`, `DecCounter`, `PopCounter`,
  `TopBegTag`, `TopEndTag`, and many more — all runtime-owned, all with source bodies
  in the -INCLUDE stream.
- Source bodies confirmed in inc files:
  - `ShiftReduce.sno`: `Shift`/`ShiftEnd`, `Reduce`/`ReduceEnd`
  - `counter.sno`: `InitCounter`/`PushCounter`/`IncCounter`/`DecCounter`/`PopCounter`/`TopCounter`/`CounterEnd`
  - `stack.sno`: `InitStack`/`Push`/`Pop`/`Pop1`/`Top`/`StackEnd`
  - `semantic.sno`: `shift_`/`reduce_`/`pop_`/`nPush_`/`nInc_`/`nDec_`/`nTop_`/`nPop_`/`semanticEnd`
- These are all phantom candidates: known to `is_body_boundary()` so their source bodies
  don't get absorbed into the wrong C function.

**Plan confirmed**: Inject phantom FnDef entries for all runtime-owned functions
whose source bodies appear in the expanded stream. Implementation is next.

---

## ⚡ KEY FINDING — Session 34: pp() and ss() are NOT in the bootstrap path

**Recorded 2026-03-12, Session 34. Lon's observation confirmed.**

### What pp() and ss() are

`pp(x)` — **pretty-printer**: takes a parse tree node and emits formatted SNOBOL4 source.
Called 27 times in beauty.sno. Defined at line 426 of beauty.sno with ~50 body labels
(`pp_snoParse`, `pp_snoId`, `pp_snoString`, `pp_:()`, `ppUnOp`, `ppBinOp`, etc.).

`ss(x, len)` — **string serializer**: converts a parse tree node to a string representation.
Called 52 times in beauty.sno. Defined at line 640 of beauty.sno (`ssEnd` at close).
Also exists as `ss.sno` in inc/ — but that is a completely different `SS` (SourceSafe
interface, unrelated). beauty.sno's `ss` is its own inline definition.

`qq(x, len)` — equivalent of ss in `pp.sno` (the standalone pretty-printer include).
beauty.sno uses `ss`, not `qq`. pp.sno uses `qq`.

### The critical finding

**`pp.sno` is NOT in beauty.sno's -INCLUDE list.** beauty.sno defines `pp` and `ss`
inline, in its own source. They are NOT implemented in `snobol4_inc.c`. They are NOT
runtime-owned. They ARE compiled by snoc as ordinary DEFINE'd functions.

**Therefore: pp and ss are NOT the bootstrap blocker.** They should compile and emit
correctly via the normal `collect_functions()` path — IF the phantom function body
absorption bug is fixed first (Shift/Reduce/Push/Pop bodies absorbing into wrong fns).

### What this means for Milestone 3

The beauty.sno self-beautification test exercises pp() and ss() on every token of
beauty.sno itself. If the compiled binary produces correct output, pp and ss are working.
If the diff shows garbled output (rather than zero output), pp/ss will be the next
debugging target. But zero output = phantom bug = fix that first.

**Prior sessions were NOT "chopping off pp and ss." They were producing ZERO output**
because the program never reached main00. pp and ss were never reached at all.
Once the phantom fix lands and the binary produces output, pp/ss correctness will
be verifiable for the first time.


---

---

## ⚡ SESSION 34 HANDOFF — Current Bug: Shift vs shift (two DIFFERENT functions)

**Recorded 2026-03-12, Session 34. Mid-session handoff.**

### Current SNOBOL4-tiny HEAD: `377fb13`
WIP commit — phantom FnDef injection in emit.c, build compiles (0 gcc errors), 
but binary still produces 0 output lines (oracle = 790).

### The Active Bug — Shift and shift are TWO DIFFERENT FUNCTIONS

**Lon confirmed this.** SNOBOL4 is case-sensitive. These are distinct:

- `Shift` (capital S) — from `ShiftReduce.sno`, runtime-registered in `snobol4_inc.c`.  
  DEFINE has goto :(ShiftEnd). `collect_functions` finds it → fn[N] name=`Shift` end=`ShiftEnd`.
- `shift` (lowercase s) — beauty.sno's OWN function, a completely different parser action.  
  DEFINE has no goto → end_label=NULL.

**Current generated C confirms both exist:**
```
line 342:  static SnoVal _sno_fn_Shift(...)   ← ShiftReduce.sno, emitted correctly
line 364:  static SnoVal _sno_fn_shift(...)   ← beauty.sno's own, emitted correctly  
line 8539: _L_Shift:;  ← IN main() — WRONG. This is a 3rd occurrence or the body_start
                          for the wrong fn leaking into main.
```

Same pattern applies to `Reduce` vs `reduce`.

### What next Claude must diagnose:

Why is `_L_Shift` appearing at C line 8539 inside `main()` when `_sno_fn_Shift` was 
already correctly emitted at C line 2402?

Hypothesis: `stmt_in_fn_body()` walk for fn `Shift` claims body_starts[0] (the Shift
label in ShiftReduce.sno) correctly — but there is a second Stmt node in the program
with label `Shift` that is NOT captured by body_starts (nbody=1 means only 1 found).
OR the walk terminates early (a label inside the Shift body triggers is_body_boundary 
prematurely before reaching ShiftEnd).

**Next debugging step:**
1. Add debug print: for every stmt with label "Shift" (case-insensitive), print its 
   source line number and whether stmt_is_in_any_fn_body() returns 1 or 0.
2. Check is_body_boundary() — does any label between `Shift:` and `ShiftEnd` in 
   ShiftReduce.sno trigger a false-positive boundary stop?

### Build state
```bash
# Build snoc first:
cd /home/claude/SNOBOL4-tiny/src/snoc && make clean && make

# Test pipeline:
SNOC=/home/claude/SNOBOL4-tiny/src/snoc/snoc
RUNTIME=/home/claude/SNOBOL4-tiny/src/runtime
INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno

$SNOC $BEAUTY -I $INC 2>/dev/null > /tmp/beauty_full.c
gcc -O0 -g /tmp/beauty_full.c \
    $RUNTIME/snobol4/snobol4.c $RUNTIME/snobol4/snobol4_inc.c \
    $RUNTIME/snobol4/snobol4_pattern.c $RUNTIME/engine.c \
    -I$RUNTIME/snobol4 -I$RUNTIME -lgc -lm -w -o /tmp/beauty_full_bin

/tmp/beauty_full_bin < $BEAUTY > /tmp/beauty_compiled.sno 2>/dev/null
wc -l /tmp/beauty_compiled.sno   # TARGET: 790 lines (oracle output)
```

### Milestone context
- **Milestone 3 target**: beauty_full_bin self-beautifies → diff vs oracle empty
- Lon's priority: beautifier working FIRST. Bask in the glory. Compiler comes after.


---

## ⚡ SESSION 34 HANDOFF — Current Bug: Shift vs shift (two DIFFERENT functions)

**Recorded 2026-03-12, Session 34. Mid-session handoff.**

### Current SNOBOL4-tiny HEAD: `377fb13`
WIP commit — phantom FnDef injection in emit.c, build compiles (0 gcc errors), 
but binary still produces 0 output lines (oracle = 790).

### The Active Bug — Shift and shift are TWO DIFFERENT FUNCTIONS

**Lon confirmed this.** SNOBOL4 is case-sensitive. These are distinct:

- `Shift` (capital S) — from `ShiftReduce.sno`, runtime-registered in `snobol4_inc.c`.  
  DEFINE has goto :(ShiftEnd). `collect_functions` finds it → fn[N] name=`Shift` end=`ShiftEnd`.
- `shift` (lowercase s) — beauty.sno's OWN function, a completely different parser action.  
  DEFINE has no goto → end_label=NULL.

**Current generated C confirms both exist:**
```
line 342:  static SnoVal _sno_fn_Shift(...)   ← ShiftReduce.sno, correct
line 364:  static SnoVal _sno_fn_shift(...)   ← beauty.sno's own, correct
line 8539: _L_Shift:;  ← IN main() — WRONG
```

Same pattern applies to `Reduce` vs `reduce`.

### Root cause hypothesis
`stmt_in_fn_body()` for fn `Shift` has nbody_starts=1 and correctly walks from the
Shift label in ShiftReduce.sno forward to ShiftEnd. BUT: the `is_body_boundary()` 
check on line 770 of emit.c uses `fn_table[i].name` = "shift" (lowercase) to exclude
self-matches. Since the walking fn is "Shift" but name stored is "shift", the 
case-insensitive compare may be causing the wrong fn's boundary to fire prematurely.

**OR**: `collect_functions` dedup is using `strcasecmp` (not `strcmp`) somewhere,
merging Shift and shift into one entry with the wrong name stored — causing the
body_starts scan to miss one of the two Shift labels in the expanded stream.

### Next Claude: DIAGNOSE with this one-liner first
```bash
$SNOC $BEAUTY -I $INC 2>/dev/null | grep -n "^_L_Shift\|^_L_shift\|_sno_fn_Shift\|_sno_fn_shift" 
```
Expected: _sno_fn_Shift and _sno_fn_shift as static fns. _L_Shift should NOT appear in main().

Then check: `grep "found\|dedup\|already" emit.c` — the dedup logic in collect_functions.
The strcmp vs strcasecmp question is the crux.

### Milestone context
- **Lon's priority order**: Beautifier (Milestone 3) FIRST. Bask in glory. Compiler later.
- Milestone 3: beauty_full_bin self-beautifies → `diff /tmp/beauty_oracle.sno /tmp/beauty_compiled.sno` empty


---

## ⚡ SESSION 34 HANDOFF (CONTINUATION) — Deep Diagnosis: _L_Shift in main()

**Recorded 2026-03-12, Session 34 continued.**

### Current SNOBOL4-tiny HEAD: `377fb13`
0 gcc errors. Binary produces 0 output lines. Oracle = 790.

### Administrative completed this continuation
- **RULE 5 officialized**: moved into rules block (was floating), checklist STEP 2+5 updated. Commit `0975c73`.
- **Milestone 0 inserted** at Sprint 26: beautifier diff-empty is now M0 (Lon's priority). Former M1/M2/M3 shift to M1/M2/M3 at sprints 27/28/29. M3 trigger = TBD by Lon. Commit `27086dc`.

### Deep diagnosis performed this session

**What we confirmed:**

1. `emit_header()` IS present at line 1048 of emit.c — was never missing. Prior "1694 errors" were from stderr mixing into stdout. That ghost is dead.

2. The generated C correctly has TWO separate functions:
   - `_sno_fn_Shift` (line 342/2402) — from ShiftReduce.sno, collected as fn[42] name=`Shift` end=`ShiftEnd`
   - `_sno_fn_shift` (line 364/4341) — from beauty.sno's own parser shift action

3. `_L_Shift` at C line 8539 is inside `main()` — WRONG. It is at `/* line 385 */` of the expanded source = the ShiftReduce.sno Shift label.

4. **The dedup in collect_functions uses `strcmp` (exact case)** — so `Shift` and `shift` are stored as SEPARATE entries. Both have `nbody_starts=1`. Both are real functions.

5. **The ShiftReduce.sno Shift body has NO internal labels** between `Shift:` and `ShiftEnd` — so `is_body_boundary` cannot fire prematurely inside it.

6. Yet `stmt_in_fn_body` fails to claim the Shift body stmts. They leak into main.

### The open question for next Claude

Why does `stmt_in_fn_body` fail to claim the stmts between `Shift:` and `ShiftEnd` in ShiftReduce.sno, given that fn[42] has name=`Shift`, end=`ShiftEnd`, nbody_starts=1, and body_starts[0] points to the correct stmt?

**Strongest hypothesis**: `is_body_boundary` on line 770 of emit.c:
```c
if (t != bs && is_body_boundary(t->label, fn_table[i].name)) break;
```
The second arg is `fn_table[i].name` = `"Shift"`. Inside `is_body_boundary`, this checks
"is this label a boundary relative to fn Shift?" — which includes checking if the label
equals `Shift` itself (the entry label). If `is_body_boundary` returns 1 for the FIRST
stmt after body_start (because its label is something that IS a boundary for another fn),
the walk immediately breaks having only claimed body_starts[0] itself — and all subsequent
stmts leak to main.

**Next Claude: add this one targeted debug print to stmt_in_fn_body:**
```c
// After line 770 break:
fprintf(stderr, "BOUNDARY_STOP fn=%s at label=%s (src line %d)\n",
        fn_table[i].name, t->label ? t->label : "(null)", t->src_line);
```
Run and grep for `BOUNDARY_STOP fn=Shift`. That will pinpoint exactly which label
is stopping the walk prematurely.

### Build commands (copy-paste ready)
```bash
apt-get install -y build-essential flex bison libgc-dev
SNOC=/home/claude/SNOBOL4-tiny/src/snoc/snoc
RUNTIME=/home/claude/SNOBOL4-tiny/src/runtime
INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno

cd /home/claude/SNOBOL4-tiny/src/snoc && make clean && make

$SNOC $BEAUTY -I $INC 2>/dev/null > /tmp/beauty_full.c
gcc -O0 -g /tmp/beauty_full.c \
    $RUNTIME/snobol4/snobol4.c $RUNTIME/snobol4/snobol4_inc.c \
    $RUNTIME/snobol4/snobol4_pattern.c $RUNTIME/engine.c \
    -I$RUNTIME/snobol4 -I$RUNTIME -lgc -lm -w -o /tmp/beauty_full_bin

/tmp/beauty_full_bin < $BEAUTY > /tmp/beauty_compiled.sno 2>/dev/null
wc -l /tmp/beauty_compiled.sno   # TARGET: 790
```

### Milestone context
- **Active target**: Milestone 0 — beauty_full_bin self-beautifies → diff empty
- Lon's order: beautifier FIRST. Bask. Compiler after.


---

## ⚡ SESSION 35 HANDOFF — Pattern-Stmt Fix Complete, New Blocker: "Internal Error" at startup

**Recorded 2026-03-12, Session 35.**

### Current SNOBOL4-tiny HEAD: `f4dfa92`
**NOTE: This commit was NOT pushed (no GitHub auth in container). Lon must push manually.**

Build: 0 gcc errors. beauty_full_bin: **0 → 9 output lines** (major progress).

### What Session 35 Fixed

**Root cause found and fixed: icase infinite recursion from misparsed pattern stmts.**

The LALR(1) grammar absorbed PAT_BUILTIN calls (POS, LEN, SPAN, etc.) into the
subject expression instead of starting the pattern. E.g.:
- SNOBOL4: `str  POS(0) ANY(&UCASE &LCASE) . letter =   :F(icase1)`
- Was emitted as: `sno_iset(sno_concat(str, POS(0), ANY(...)), _v)` ← WRONG
- Now emitted as: `sno_match(&str, POS(0) ANY(..) . letter)` + `sno_replace` ← CORRECT

**Four fixes in commit `f4dfa92`:**
1. `sno.l`: PAT_BUILTIN only at `bstack_top==0` (not inside arglist parens)
2. `emit.c`: `maybe_fix_pattern_stmt()` + `split_subject_pattern()` — post-parse
   tree restructuring. Scans subject concat tree for first PAT_BUILTIN node,
   splits it: left=subject, right=pattern.
3. `emit.c`: `B1i`/`B1s`/`B1v` macros for proper type conversions (int64_t vs
   const char* vs SnoVal for different PAT_BUILTIN argument types)
4. `snobol4_pattern.c` + `snobol4.h`: added `sno_pat_call(name, arg)` for
   user-defined pattern functions referenced in pattern context.

### The New Blocker: "Internal Error" at line 8

Beauty output (9 lines):
```
*---------  (7 comment header lines)
Internal Error
START
```

"Internal Error" is emitted by the beautifier itself — it hit an error condition
during startup initialization (before processing any input lines). This happens
during the initialization section of beauty.sno (lines ~50-450) where patterns,
grammars, and data structures are set up.

### Diagnostic approach for next Claude

1. Find where beauty.sno outputs "Internal Error":
```bash
grep -n "Internal Error\|InternalError\|error.*Internal" \
    /home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno | head -5
```

2. Add runtime tracing to identify which statement triggers it:
```c
// In snobol4.c or engine.c, add a debug print when the string "Internal Error"
// is about to be output to stdout
```

3. The "Internal Error" label is likely reached via a :F branch in the init section.
   Some function call is failing that should succeed. Most likely candidates:
   - Pattern compilation failures (icase, ARBNO, etc.)
   - DATA definition failures
   - Array initialization failures

### Build commands (copy-paste ready)
```bash
apt-get install -y build-essential flex bison libgc-dev
cd /home/claude/SNOBOL4-tiny/src/snoc && make clean && make

SNOC=/home/claude/SNOBOL4-tiny/src/snoc/snoc
RUNTIME=/home/claude/SNOBOL4-tiny/src/runtime
INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno

$SNOC $BEAUTY -I $INC 2>/dev/null > /tmp/beauty_full.c
gcc -O0 -g /tmp/beauty_full.c \
    $RUNTIME/snobol4/snobol4.c $RUNTIME/snobol4/snobol4_inc.c \
    $RUNTIME/snobol4/snobol4_pattern.c $RUNTIME/engine.c \
    -I$RUNTIME/snobol4 -I$RUNTIME -lgc -lm -w -o /tmp/beauty_full_bin

/tmp/beauty_full_bin < $BEAUTY > /tmp/beauty_compiled.sno 2>/dev/null
wc -l /tmp/beauty_compiled.sno   # Current: 9, TARGET: 790
```

### Milestone context
- **Active target**: Milestone 0 — beauty_full_bin self-beautifies → diff empty
- Current: 9/790 lines. Pattern fix was the major unlock.
- Next: fix "Internal Error" in startup initialization.

---

### 2026-03-12 — Session 36 (E_REDUCE fix + EVAL/OPSYN/SORT registration + Internal Error traced)

**Focus**: Debug "Internal Error" at beauty startup. Two bugs fixed. Third bug exposed mid-session.

**Root cause traced for "Internal Error":**

`mainErr2` is hit during startup init — specifically during the construction of
`snoParse` (the top-level pattern). The `snoParse` pattern uses `&` to call `reduce()`,
e.g. `ARBNO(*snoCommand)  ('snoParse' & nTop())`. With the `E_REDUCE` fix, `&` now
calls `reduce()` at runtime. `reduce(t,n)` is a SNOBOL4 user function (in semantic.sno,
compiled into `_sno_fn_reduce`) that calls `EVAL("epsilon . *Reduce(" t ", " n ")")`.
`EVAL` was not registered as a callable SNOBOL4 function → `sno_apply("EVAL",...)` returned
FRETURN → reduce() failed → `DIFFER($'@S' = Pop())` at `main02` (the pattern match loop)
found @S empty → `mainErr2` → "Internal Error".

**Fix 1 — E_REDUCE added (committed `574e758`):**

`sno.y`: `expr AMP term` → `binop(E_REDUCE,...)` instead of `E_CONCAT`.
`snoc.h`: `E_REDUCE` added to `EKind` enum.
`emit.c`:
- `emit_expr` E_REDUCE → `sno_apply("reduce",(SnoVal[]){l,r},2)`
- `emit_pat` E_REDUCE → `sno_var_as_pattern(sno_apply("reduce",...))`
- `is_pat_node()` recognizes `E_REDUCE` as pattern context

**Fix 2 — EVAL/OPSYN/SORT registered in runtime (NOT YET COMMITTED — snobol4.c WIP):**

File-scope wrappers and registrations added to `snobol4.c` after `_b_DATATYPE` (~line 204):
```c
extern SnoVal sno_eval(SnoVal);
extern SnoVal sno_opsyn(SnoVal, SnoVal, SnoVal);
extern SnoVal sno_sort_fn(SnoVal);
static SnoVal _b_EVAL(SnoVal *a, int n)  { return sno_eval(n>0?a[0]:SNO_NULL_VAL); }
static SnoVal _b_OPSYN(SnoVal *a, int n) {
    return sno_opsyn(n>0?a[0]:SNO_NULL_VAL,n>1?a[1]:SNO_NULL_VAL,n>2?a[2]:SNO_NULL_VAL); }
static SnoVal _b_SORT(SnoVal *a, int n)  { return sno_sort_fn(n>0?a[0]:SNO_NULL_VAL); }
// Registration in sno_runtime_init():
sno_register_fn("EVAL",  _b_EVAL,  1, 1);
sno_register_fn("OPSYN", _b_OPSYN, 2, 3);
sno_register_fn("SORT",  _b_SORT,  1, 1);
```

**New bug exposed — `sno_eval` infinite loop on `*(expr)` syntax:**

With EVAL registered, `reduce('snoParse', *(GT(nTop(), 1) nTop()))` calls:
`EVAL("epsilon . *Reduce('snoParse', *(GT(nTop(), 1) nTop()))")`.

`_ev_term()` in `snobol4_pattern.c` handles `*ident` and `*ident(args)` but NOT `*(expr)`.
When it sees `*(GT(...) nTop())`, after reading `*` it calls `_ev_ident()` which returns
NULL (next char is `(`). Returns `sno_pat_epsilon()`. The `(` is left unconsumed. The
outer loop re-encounters it → infinite loop.

**Session 36 ended mid-fix (snobol4.c NOT committed, snobol4_pattern.c fix NOT committed).**

---

### 2026-03-12 — Session 37 (Diagnostic design: &STLIMIT/&STCOUNT probe + TRACE machinery)

**Focus**: Design the correct diagnostic approach before writing more fixes.
No new code committed. Two major diagnostic techniques documented.

**⚡ KEY DESIGN INSIGHT — SNOBOL4 native diagnostics available in beauty_full_bin**

beauty.sno has TWO built-in diagnostic systems that compiled into beauty_full_bin
and can be used as probes WITHOUT modifying the runtime or adding fprintf:

---

#### Technique 1: `xTrace` variable (beauty's internal trace flag)

`xTrace` is a static SnoVal in the generated C (line 66: `static SnoVal _xTrace = {0}`).
beauty.sno checks `GT(xTrace, 4)` before every diagnostic OUTPUT line (~80 trace sites).
Setting `_xTrace = SNO_INT_VAL(6)` at the top of `main()` in the generated C enables
all internal trace output through beauty's own OUTPUT assignments.

**Limitation discovered**: beauty's trace OUTPUT goes to SNOBOL4 `OUTPUT` variable →
`sno_output_val()` → `printf()` → stdout. This mixes with the compiled output stream.
To use xTrace, redirect stdout to /dev/null and capture only stderr — but trace goes
to stdout. Workaround: patch `sno_output_val` in the generated C to write to stderr
when `_xTrace > 0`, or set `_xTrace` and accept mixed output.

**Key trace levels** (verified from generated C):
- `GT(xTrace, 4)` — emits stack ops: PushCounter/PopCounter/PushBegTag/PopBegTag/Push/Pop
- `GT(xTrace, 5)` — emits detailed per-statement trace including T8Trace pattern events

---

#### Technique 2: `&STLIMIT` / `&STCOUNT` probe

**Lon's technique**: inject `&STLIMIT=N` at program start to cap execution, then observe
behavior at statement N. Used in combination with `&DUMP=2` (dump all variables at
termination) to see program state at the cutoff point.

In the compiled binary, this translates to:
- `sno_kw_set("STLIMIT", SNO_INT_VAL(N))` at start of `main()`
- The runtime already honors `&STLIMIT` via `sno_comm_stno()` (P001 fix, Session 2)

**How to use it**: Patch the generated C to set STLIMIT to a small number, rebuild,
run, observe how far the binary gets and what state it's in at termination.

---

#### Technique 3: SNOBOL4 TRACE() — label, var, func enter, func return

**Lon's reminder**: SNOBOL4 has native `TRACE()` machinery. beauty.sno itself uses
`T8Trace` for pattern-level tracing. The runtime has `TRACE(fn,'CALL')`,
`TRACE(fn,'RETURN')`, `TRACE(label,'LABEL')`, `TRACE(var,'VALUE')`.

In the compiled binary, these translate to callbacks registered via
`sno_register_trace()` (if implemented) or through the `_T8Trace` mechanism
in the generated C.

**Verified in generated C**:
- `_T8Trace` wrapper exists (line 184, line 374)
- `sno_define("T8Trace()", _sno_fn_T8Trace)` registers it
- Pattern `pat $ tz $ *T8Trace(lvl, name, tz, txOfs)` in generated code at line 4619

**Practical diagnostic for next session**:

1. **Function enter/return trace** — add `fprintf(stderr,...)` to `_sno_fn_reduce`,
   `_sno_fn_shift`, `_sno_fn_refs`, `_sno_fn_Push`, `_sno_fn_Pop` entry points
   by patching the generated C. (Already partially done — verified `reduce` IS called
   45 times during startup init, then `main02` runs once, then `mainErr2`.)

2. **STLIMIT probe** — set `&STLIMIT=50` and `&DUMP=2` to capture variable state
   during the 50 startup statements. Shows exactly what @S, @B, @E contain at cutoff.

3. **Direct label trace** — patch the generated C: at `_L_main02:`, `_L_mainErr2:`,
   `_L_mainErr1:` add `fprintf(stderr, "[LABEL name @S.type=%d]\\n", ...)` to see
   which error path fires and what @S contains.

---

#### Session 37 diagnostic results (from function-entry patching)

Patched `_L_reduce_:`, `_L_main02:`, `_L_mainErr2:` with `fprintf(stderr,...)`.
Built `beauty_fn_bin`. Ran with `timeout 3`. Results:

```
[ENTER reduce]  × 45   ← reduce() called 45 times during startup (building all grammar patterns)
[main02]        × 1    ← main02 (pattern match loop) entered once
[mainErr2]      × 1    ← immediately hits Internal Error path
```

**Conclusion**: `reduce()` IS working (45 calls, no loop). The infinite loop
from Session 36 was a red herring (different binary version). The current binary
with E_REDUCE + EVAL registered runs reduce 45 times cleanly, then fails at the
first actual input match attempt.

**Root cause now clearly**: Despite 45 reduce() calls during init, `Push` is never
called. `DIFFER($'@S' = Pop())` at `main02` fails because @S is empty — the
shift-reduce stack was never populated. Either:
1. The patterns built by reduce() are not being matched against the input, OR
2. `Shift` is being called but not pushing to the correct stack, OR
3. The `snoParse` pattern itself is not being applied (the match fails immediately)

**Next diagnostic**: Trace `_w_Shift` in `snobol4_inc.c` — add `fprintf(stderr,...)` 
to `_w_Shift` to confirm whether Shift is ever called at all during the input match.
Also verify `sno_apply("Shift",...)` routes to `_w_Shift` (registered via `sno_register_fn`).

---

#### Active bug state at Session 37 end

**snobol4.c**: EVAL/OPSYN/SORT registration added — **NOT YET COMMITTED**
**snobol4_pattern.c**: `*(expr)` fix for `_ev_term` — **NOT WRITTEN YET**
**beauty_full_bin**: 9 output lines (header comments + "Internal Error" + "START")
**Oracle target**: 790 lines
**Next action**: Trace whether `Shift` (capital S, `snobol4_inc.c`) is called
during the input match phase. If not, the pattern built by reduce() for snoParse
is not invoking the deferred `*Shift(...)` calls.

---

#### ⚡ DIAGNOSTIC TOOLKIT SUMMARY (permanent reference)

**For any future binary-produces-wrong-output debugging:**

| Tool | How | What it shows |
|------|-----|---------------|
| xTrace | `_xTrace = SNO_INT_VAL(6)` in main() of generated C | beauty's stack/tag ops via OUTPUT |
| &STLIMIT | `sno_kw_set("STLIMIT", SNO_INT_VAL(N))` in main() | caps execution at N stmts, shows state at cutoff |
| Label trace | `fprintf(stderr,...)` at `_L_labelname:;` in generated C | confirms which code paths are reached |
| Func enter | `fprintf(stderr,...)` at `_L_fnname_:;` or `_sno_fn_X` entry | confirms which functions are called |
| Func return | `fprintf(stderr,...)` before each `return` in `_sno_fn_X` | shows return values |
| Var trace | `fprintf(stderr, "var=%s\\n", sno_to_str(sno_get(_varname)))` | shows variable state at any point |
| TRACE() builtin | `TRACE('fn','CALL')` / `TRACE(label,'LABEL')` in SNOBOL4 | native SNOBOL4 tracing (if runtime supports it) |

**Scaling rule**: Start with label/func-enter traces (cheap, binary info). Add var
traces only when you know WHICH variable is wrong. Use &STLIMIT for init-phase bugs
where the program dies before reaching the interesting code.



### 2026-03-12 — Session 38 (CSNOBOL4 source study + EVAL partial diagnosis)

**Focus**: Lon uploaded CSNOBOL4 2.3.3 source (snobol4-2_3_3_tar.gz). Studied STARFN/XSTAR
unevaluated expression semantics in v311.sil. Verified current repo state — HEAD `90a1128`
already has EVAL/OPSYN/SORT + *(expr) fix committed from Session 37.

**Current binary state**: timeout at 10s, 0 output lines. `beauty_stderr.txt` shows EVAL
partial messages — the *(expr) fix in `_ev_term` is working but `_ev_expr`/`_ev_args`
has two parsing gaps:

1. **`remain=')'` pattern**: `_ev_args` parses function args via `_ev_expr`, but the
   closing `)` of function calls is not consumed somewhere in the chain. Manifests as
   `consumed N/N+1 remain=')'` in the EVAL log.

2. **`remain='+ 1)'` and `remain=', 1)'` patterns**: `_ev_expr` stops at `+` (arithmetic)
   and `,` — neither is handled. `GT(nTop(), 1)` parses `nTop()` then stops at `,`.
   The arithmetic sub-expressions inside function arguments need `_ev_expr` to recurse
   through `+`, `-`, etc.

3. **Timeout = infinite loop**: The EVAL partial sequence repeats twice identically in
   stderr — the same 16 lines appear twice. This means snoParse is being built, partially
   matched, rebuilt, partially matched again — a loop caused by malformed patterns from
   the EVAL partials.

**Immediate next actions (Session 39):**

1. **Fix `_ev_expr` / `_ev_args` to handle arithmetic and proper paren close:**
   - `_ev_args` inner expression: use `_ev_val` (not `_ev_expr`) for argument values,
     OR extend `_ev_expr` to handle `+`, `-`, `*`, `/` as arithmetic ops returning SnoVal.
   - Confirm `_ev_term` consumes `)` after `_ev_args` — check the exact call site.

2. **After fix**: run binary, check stderr has no `EVAL partial` messages.

3. **If clean**: check if output lines increase beyond 9. If still 9/timeout: add Shift
   trace (fprintf in `_w_Shift` in `snobol4_inc.c`) to confirm whether Shift is called.

4. **STLIMIT probe if needed**: patch generated C main() with
   `sno_kw_set("STLIMIT", SNO_INT_VAL(500))` to cap execution and examine state.

**Repo state at handoff:**

| Repo | Commit | Status |
|------|--------|--------|
| SNOBOL4-tiny | `90a1128` | 0 gcc errors. beauty_full_bin: 0 lines, 10s timeout. EVAL partials in stderr. |
| SNOBOL4-dotnet | `b5aad44` | unchanged |
| SNOBOL4-jvm | `9cf0af3` | unchanged |
| SNOBOL4-corpus | `3673364` | unchanged |
| SNOBOL4-harness | `8437f9a` | unchanged |


### 2026-03-12 — Session 40 (sno_var_set scope fix + DUMP/&DUMP diagnostic insight)

**Focus**: Fixed the sno_set/sno_var_set desync bug properly. Three bugs found and fixed.
Binary now reaches main input loop. Lon's key insight: **DUMP and &DUMP are the right
diagnostic tools for this class of bug — we should have used them from the start.**

---

#### Bugs Fixed This Session

**Bug 1 — sno_array_get2 no bounds check (snobol4.c)**
- `SORT(UTF)` builds a 2D array. `UTF_Array[i,1]` in the G1 loop called `sno_array_get2`
  which had NO bounds check — returned garbage past end, loop never exited.
- Fix: added bounds check; returns `SNO_FAIL_VAL` when row/col out of range.
- Also changed `if (!a) return SNO_NULL_VAL` → `SNO_FAIL_VAL` (NULL_VAL is not FAIL).

**Bug 2 — SORT stub returned TABLE unchanged (snobol4_pattern.c)**
- `SORT(table)` was a stub returning input unchanged.
- `csnobol4` `SORT(T)` returns a 2D array `[i,1]=key, [i,2]=value` sorted by key.
- Fix: implemented real `sno_sort_fn`: collect (key,val) pairs, insertion-sort by key,
  build `SnoArray` with `lo=1, hi=n, ndim=2`, data = interleaved key/val.

**Bug 3 — sno_var_set sync emitted for function locals (emit.c)**
- The Session 39 fix emitted `sno_var_set(name, val)` after EVERY `sno_set()`.
- Function locals (e.g., `i` in `Reduce`) are C statics in function scope — syncing them
  to the global hash table polluted globals and caused Reduce's `i` loop to run 200k+
  iterations (n was huge because `sno_var_get("i")` returned the polluted global).
- Fix: added `cur_fn_def` pointer and `is_fn_local(varname)` helper in `emit.c`.
  `sno_var_set` is only emitted when the variable is NOT a declared param/local of the
  current function. Global variables assigned inside functions (like `snoParse` assigned
  inside `UserDefs()`) ARE synced correctly because they're not in `fn->args/locals`.

#### Architecture Note — ⚠️ SUPERSEDED BY SESSION 44 — SEE §2

**~~The two-store problem is now correctly solved:~~** ← THIS WAS WRONG. See §2.
- ~~C statics `_snoParse`, `_snoSrc` etc.: updated by `sno_set()` macro.~~
- ~~Hash table `sno_var_get/set()`: used by `SPAT_REF`, pattern captures, EVAL.~~
- ~~Rule: emit `sno_var_set(name, val)` after `sno_set()` IFF `!is_fn_local(name)`.~~
- ~~This correctly syncs globals (including globals assigned inside functions) while~~
  ~~leaving function locals isolated to their C stack frame.~~

**The real rule (Session 44):** ALL variables are NATURAL VARIABLES (hashed).
`sno_var_set` must be emitted for EVERY assignment. `is_fn_local` suppression removed.
- This correctly syncs globals (including globals assigned inside functions) while
  leaving function locals isolated to their C stack frame.

#### Lon's Diagnostic Insight — DUMP and &DUMP

**THIS IS THE KEY DIAGNOSTIC TOOL WE SHOULD USE GOING FORWARD.**

In SNOBOL4/CSNOBOL4:
- `DUMP(1)` — dumps all variable names and values to stderr/output at that point.
- `&DUMP = 1` — sets the DUMP keyword; auto-dumps on program termination (normal or abort).

**Why this matters**: the current hang (main input loop) is a pattern match failure.
`snoParse` is built but may be malformed. `DUMP(1)` or `&DUMP = 1` injected at key
points in the generated C (or in a debug SNOBOL4 wrapper) would show exactly what
`snoParse`, `snoCommand`, `snoSrc` etc. contain at the moment of failure — without
needing to add dozens of `fprintf` calls or reverse-engineer the pattern structure.

**How to use in our context:**
1. In the runtime: `sno_apply("DUMP", (SnoVal[]){sno_int(1)}, 1)` — dumps all vars.
2. In generated C: inject `sno_apply("DUMP", ...)` before the first `INPUT` read.
3. `&DUMP` equivalent: `sno_kw_dump = 1` in the runtime, checked at program exit.
4. For pattern inspection: `sno_pat_dump(val)` if we implement it — prints pattern tree.

**Immediate action**: implement `DUMP` builtin in `snobol4_inc.c` that iterates
`_var_buckets[]` and prints name=value pairs. Use it to verify `snoParse` is a valid
pattern after init, before the main loop starts.

#### Current State

- Binary reaches main input loop (`_L_main00`) ✓
- Hangs in the main processing loop (pattern match or subsequent processing)
- `snoParse` is now synced to hash table via `sno_var_set` from `UserDefs()`
- Root cause of current hang: unknown — next step is DUMP-based diagnosis

#### Immediate Next Actions (Session 41)

1. **Implement DUMP builtin** — iterate `_var_buckets[]`, print `name = sno_to_str(val)`.
   Register as `sno_register_fn("DUMP", _b_DUMP, 1, 1)` in `snobol4.c`.

2. **Inject DUMP call before main loop** — patch generated C to call DUMP(1) just before
   `_L_main00:` — verify `snoParse` is present and is type `SNO_PATTERN`.

3. **Add &STLIMIT cap** — inject `sno_kw_stlimit = 10000` before `_L_main00` to cap
   execution and get a clean exit with DUMP output instead of a hang.

4. **If snoParse is correct** — the hang is in downstream processing (Reduce, tree building,
   Gen, etc.). Use `&DUMP` at exit + `&STLIMIT` to see what variables look like when it stops.

5. **Commit the three bug fixes** (sno_array_get2, SORT, emit.c scope) once DUMP is working.

#### Repo State at Handoff

| Repo | Commit | Status |
|------|--------|--------|
| SNOBOL4-tiny | `669d72b` | emit.c + snobol4.c + snobol4_pattern.c modified, NOT committed |
| .github | `b8aa8c3` | Session 40 entry added, NOT committed |
| SNOBOL4-corpus | `3673364` | unchanged |

**⚠ Three runtime files modified but not committed — loop bugs not fully resolved yet.**

### 2026-03-12 — Session 42 (Sprint 26: E_DEREF misparse + pattern builtin registration)
**Focus**: All key pattern vars PATTERN at main00. Hang inside snoParse match remains.

**Root causes found and fixed:**

**Bug 1 — E_DEREF E_CALL misparse (emit.c)**
- Continuation lines cause parser to greedily parse `*snoLabel\n+ (...)` as `*(snoLabel(...))`
- Fixed in both emit_expr and emit_pat: `E_DEREF` with `E_CALL(nargs==1)` operand →
  `sno_concat(pat_ref(varname), arg)` / `sno_pat_cat(pat_ref(varname), arg)`
- Result: snoStmt=PATTERN ✓

**Bug 2 — Pattern builtins not callable via sno_apply (snobol4.c)**
- SPAN/BREAK/etc inside arglist parens tokenized as IDENT → emitted as `sno_apply("SPAN",...)` 
- SPAN was not registered as a function → returned NULL → snoSpace stayed NULL
- Fixed: added `_b_PAT_*` wrappers + registered all pattern builtins in sno_runtime_init
- Result: snoSpace=PATTERN ✓

**DUMP diagnostic toolkit confirmed working** — used to identify both bugs above.

**Repo state at handoff:**
| Repo | Commit | Status |
|------|--------|--------|
| SNOBOL4-tiny | `c6292e4` | CLEAN — both fixes committed |
| SNOBOL4-corpus | `3673364` | unchanged |
| .github | needs push | Session log entry added |

**Milestone tracker:**
| # | Milestone | Status |
|---|-----------|--------|
| 0 | beauty_full_bin self-beautifies → diff empty | 🔴 hang in snoParse match |

**Immediate next actions (Session 43):**
1. Rebuild beauty_full_bin (snoc + gcc) — commit c6292e4 is clean HEAD
2. Run DUMP to confirm all 5 key vars still PATTERN
3. Diagnose hang: `snoParse` uses `ARBNO(*snoCommand)` — if `*snoCommand` can match
   empty (epsilon), ARBNO loops forever. Check `sno_pat_arbno` in snobol4_pattern.c —
   does it detect zero-progress and break? If not, add cycle detection.
4. Key file: `src/runtime/snobol4/snobol4_pattern.c` — SPAT_ARBNO match logic
5. Also check: `sno_match` itself — does it have a step limit or cycle guard?

### 2026-03-12 — Session 44 (Architecture: Natural Variables, Save/Restore, T_FNCALL)
*(Already recorded above in §2 and §6 — see ARCHITECTURE TRUTH block)*

**Key commits:** `f28cfe9` — sno_var_register/sync + is_fn_local guards removed (WIP, partial)

---

### 2026-03-12 — Session 45 (Path A save/restore implemented; Parse Error diagnosed)

**Focus**: Implement save/restore; diagnose remaining Parse Error blocker.

#### Bug Fixed — Path A save/restore (`eec1adb`)

`emit_fn()` in `emit.c` now emits CSNOBOL4 DEFF8/DEFF10/DEFF6-style save/restore:
- ON ENTRY: `SnoVal _saved_X = sno_var_get("X")` + `sno_var_set("X", new_val)` for all params/locals
- ON ALL EXITS: restore in reverse order at `_SNO_RETURN_`, `_SNO_FRETURN_`, new `_SNO_ABORT_` label
- Setjmp path: was `return SNO_FAIL_VAL` directly (bypassed restore). Now `goto _SNO_ABORT_`.

**Result**: binary exits cleanly (was hanging). 10/790 lines output (was 9).

#### Parse Error Diagnosis

Tested: `printf "x = 'hello'\nEND\n" | /tmp/beauty_full_bin` → Parse Error.
DUMP confirms: `snoParse` is SNO_PATTERN (type 5). The pattern is structurally present.
The match `snoSrc POS(0) *snoParse *snoSpace RPOS(0)` fails on even the simplest statement.

**Root cause hypothesis — `E_REDUCE` in `emit_pat()` may be missing or wrong:**

beauty.sno builds grammar patterns with `&` as semantic action:
```snobol
snoExpr0 = *snoExpr1 FENCE($'=' *snoExpr0 ("'='" & 2) | epsilon)
```
`("'='" & 2)` = `reduce("'='", 2)` = `EVAL("epsilon . *Reduce('=', 2)")` = a pattern node.

In `sno.y`: `expr AMP term → E_REDUCE`.
In `emit_expr()`: `E_REDUCE → sno_apply("reduce", ...)` → returns SnoVal.
In `emit_pat()`: UNVERIFIED — if `E_REDUCE` falls through without a `case`, the
result is not wrapped as a pattern. This would silently corrupt the FENCE sub-patterns
containing semantic actions, making snoParse structurally present but semantically wrong.

**Check at session start:**
```bash
grep -n "E_REDUCE" /home/claude/SNOBOL4-tiny/src/snoc/emit.c
```

Look for `case E_REDUCE:` inside `emit_pat()`. If absent, add:
```c
case E_REDUCE:
    E("sno_var_as_pattern(sno_apply(\"reduce\",(SnoVal[]){");
    emit_expr(e->left); E(","); emit_expr(e->right);
    E("},2))");
    break;
```

#### Repo State at Handoff

| Repo | Commit | Status |
|------|--------|--------|
| SNOBOL4-tiny | `eec1adb` | CLEAN — Path A save/restore done. 10/790 lines. Parse Error remains. |
| .github | this push | Session 45 log + §6 updated with E_REDUCE hypothesis |
| SNOBOL4-corpus | `3673364` | unchanged |

#### Milestone Tracker

| # | Milestone | Status |
|---|-----------|--------|
| 0 | beauty_full_bin self-beautifies → diff empty | 🔴 Parse Error on every statement |

### 2026-03-12 — Session 46 (Analysis: beauty.sno expr grammar + CSNOBOL4 OPTBL verification)

**Focus**: Analysis session. No code changes. Lon asked about expression grammar depth and flagged a mistake in earlier Pratt parser note.

#### beauty.sno Expression Grammar — Complete Table (Lon's question)

Counted all 18 named pattern variables (snoExpr0–snoExpr17). They implement a full Pratt/shunting-yard operator precedence parser as SNOBOL4 deferred-pattern-reference chains. 14 binary levels, 1 unary prefix level (14 operators), 1 postfix subscript level, 1 primary level. Levels 4 and 5 (alternation `|` and implicit concatenation) are n-ary via nPush/nPop. This is temporary scaffolding until SNOBOL4 has native CODE type.

#### Correction — Pratt parser must reach snoExpr17 (primary)

Earlier note claimed ~150 lines and only listed binary/unary. **Wrong.** The primary level (snoExpr15–17) is the base case the entire recursive descent bottoms into — without it you can't parse a single token. Verified against v311.sil `ELEMNT` procedure:

- `EXPR2` = binary Pratt loop over OPTBL (left/right precedence pairs)
- `ELEMNT` = primary + unary prefix + postfix subscript combined:
  - `UNOP` chain → 14 prefix operators
  - literal dispatch: integer (SPCINT), real (SPREAL), quoted string
  - variable → GENVUP
  - `(expr)` → recurse into EXPR
  - `name(args)` → function call, ELEFNC, args recurse into EXPR
  - `name[]` / `name<>` → ELEM10 peek-ahead, array/table ref

**OPTBL precedence values** recorded in §2 from v311.sil (authoritative). Corrected estimate: ~250 lines for full hand-rolled Pratt + primary parser.

#### Repo State at Handoff

| Repo | Commit | Status |
|------|--------|--------|
| SNOBOL4-tiny | `eec1adb` | UNCHANGED — Parse Error still active. |
| .github | `3f1b57d` | Session 46: expr grammar table + OPTBL in §2. |
| SNOBOL4-corpus | `3673364` | unchanged |

#### Milestone Tracker

| # | Milestone | Status |
|---|-----------|--------|
| 0 | beauty_full_bin self-beautifies → diff empty | 🔴 Parse Error on every statement |

### 2026-03-12 — Session 47 (epsilon contract + datatype audit + NRETURN fix + DATA() diagnosis)

**Focus**: Deep diagnostic session. Two root-cause bugs found and one fixed.
Full datatype audit conducted. Handoff protocol executed.

**Work done:**

1. **epsilon contract** (from earlier in session): `epsilon` pre-initialized to
   `sno_pat_epsilon()` in `sno_runtime_init()`. Committed `d7068d3`.

2. **emit_pat E_CALL pattern-constructors**: `reduce()`, `shift()`, `EVAL()` in
   pattern context were emitting `sno_pat_user_call(...)` (deferred match-time).
   They are build-time constructors. Fixed to `sno_var_as_pattern(sno_apply(...))`.
   Part of `66b7eab`.

3. **NRETURN → FRETURN alias (CRITICAL BUG FIXED)**: Every `:(NRETURN)` in every
   -INCLUDE file was routing to `_SNO_FRETURN_fn` — causing Push(), Pop(), Top(),
   Shift(), Reduce(), all counter/Gen/TZ functions to FAIL on every call.
   The entire shift-reduce parse stack was non-functional. Fix: NRETURN routes to
   `_SNO_RETURN_fn`. Committed `66b7eab`.

4. **Full SNOBOL4 datatype audit** (§13 in tiny PLAN.md, §13-14 in .github):
   - STRING/INTEGER/REAL/PATTERN/ARRAY/TABLE: implemented
   - EXPRESSION: kludged as SNO_TREE with tag = type name — correct for beauty.sno
   - NAME: not implemented — snoc resolves l-values statically at compile time
   - CODE: stub only, not needed for Milestone 0
   - UDEF (DATA()): struct exists but DATA() not registered — **BLOCKER**

5. **DATA() diagnosis (CRITICAL BUG — not yet fixed)**: `DATA('link(next,value)')`
   → `sno_apply("DATA",...)` → NULL silently. Constructor `link()` and field
   accessors `next()`, `value()` never registered. stack.sno linked list
   completely broken. Every Push stores NULL, every Pop returns NULL.
   Fix needed: register `_b_DATA` in runtime, implement `_register_udef_fns()`.

6. **snoSrc empty diagnosis (CRITICAL BUG — not yet fixed)**: `SNO_PAT_DEBUG=1`
   shows `subj=(0)`. `snoSrc` never populated. Hypothesis: `_nl` uninitialized
   when `main02` runs, `sno_concat_sv` FAIL-propagates, snoSrc stays empty forever.
   Fix: pre-initialize `nl="\n"`, `tab="\t"` etc. in `sno_runtime_init()`.

**State**: Parse Error still active. NRETURN fix is real and necessary but
deeper blockers (snoSrc empty + DATA() broken) remain. Extensive documentation
committed to both repos.

| Repo | Commit | Status |
|------|--------|--------|
| SNOBOL4-tiny | `66b7eab` | NRETURN fixed. emit_pat constructors fixed. Datatype docs. Parse Error remains. |
| .github | `(this)` | Session 47 full handoff. §6 + §12 + Milestone Tracker updated. |
| SNOBOL4-corpus | `3673364` | unchanged |

### 2026-03-12 — Session 48 (E_CONCAT fix + DATA() + sno_inc_init: three root-cause bugs killed)

**Focus**: Four bugs found and fixed this session. Parse Error still active but
the grammar is now running deeply. Next bug isolated.

**Work done:**

1. **expr_contains_pattern E_CONCAT false-positive (CRITICAL BUG FIXED)** `8b978e3`:
   `if (e->kind == E_CONCAT) return 1` in `emit.c` caused ALL concatenations
   (including `snoSrc snoLine nl`) to be emitted as pattern-concat instead of
   string-concat. `snoSrc` was always empty — every pattern match ran against "".
   Fix: removed unconditional short-circuit. Recurse into children only.

2. **DATA() builtin was a no-op (CRITICAL BUG FIXED)** `e4595a7`:
   `DATA('link(next,value)')` called `sno_apply("DATA",...)` → NULL silently.
   DATA never registered. Constructors and field accessors never created.
   stack.sno Push/Pop operated on null objects. Reduce() built null trees.
   Fix: implemented `_b_DATA()` with 64-type × 16-field trampoline arrays.
   Registered DATA in `sno_runtime_init()`.

3. **sno_init() never called sno_inc_init() (CRITICAL BUG FIXED)** `627a030`:
   `sno_inc_init()` registers Push, Pop, Top, Shift, reduce_, shift_, Gen, Qize,
   assign, match, and 30+ more -INCLUDE functions. Called only from `beautiful.c`
   (legacy), never from `sno_init()`. Every `sno_apply("Push",...)` returned NULL.
   Fix: `sno_init()` in `snoc_runtime.h` now calls `sno_inc_init()`.

4. **Verified**: After all three fixes, `DATA('mynode(val)')` + `mynode(42)` +
   `Push(x)` + `Pop()` → `DATATYPE(y) = "mynode"`, `val(y) = 42`. ✓

**State**: Parse Error still active. `SNO_PAT_DEBUG=1` shows grammar running
deeply (many Reduce/nPush/nPop calls) but `ARBNO(*snoCommand)` matches 0 times:
`try_match_at: start=16 slen=16 → matched=0`. Next blocker isolated: why
`snoCommand` fails to match `    x = 'hello'\n`.

| Repo | Commit | Status |
|------|--------|--------|
| SNOBOL4-tiny | `627a030` | 3 critical bugs fixed. Parse Error remains — ARBNO(snoCommand) matches 0. |
| .github | `(this)` | Session 48 full handoff. §6 + §12 updated. |
| SNOBOL4-corpus | `3673364` | unchanged |

### 2026-03-12 — Session 49 (Conditional assignment `.` deferred semantics — Lon's Eureka)

**Two key discoveries this session:**

**Discovery 1 — Deferred `.` assignment:**
`pat . var` is a **deferred** assignment — queued when sub-pattern matches, fires only
AFTER the entire top-level match SUCCEEDS, left-to-right. Distinct from `$` (immediate).
Because epsilon is zero-length, missing deferred actions do NOT affect the match.
Find the real match failure elsewhere.

**Discovery 2 — NAME datatype and NRETURN (from v311.sil):**
NRETURN = "return by name" (`RRTURN ZPTR,3` in SIL). The function returns an l-value
descriptor (NAME datatype) — a pointer to the function's return-variable cell.
`epsilon . *IncCounter()`: `*IncCounter()` is an unevaluated STR-type expression.
At deferred-fire time (NMD post-match), CSNOBOL4 evaluates it via EXPEVL, calls
`IncCounter()`, which increments the counter and returns NRETURN (NAME of `IncCounter`).
The empty string from epsilon is assigned into that cell. The counter increment IS the
side effect. NAME datatype not needed in our runtime — `sno_apply("IncCounter",NULL,0)`
at `apply_captures()` time is sufficient and correct.

**E_COND bug confirmed:**
- `emit.c` `case E_COND` only handles `E_VAR` on RHS. When RHS is `*func()` (E_DEREF
  of E_CALL), falls back to `"?"` — silently dropping the call.
- All `nInc/nDec/nPush/nPop` counter operations are broken (no-ops) during matches.
- Fix: detect E_DEREF of E_CALL on RHS, emit `"*funcname"` as capture var; in
  `apply_captures()` check for leading `*` and call the function as side-effect.

**Debug trace established**: `try_match_at: start=0..16, slen=16 -> matched=0 end=0`
(all positions fail). Root cause of match failure still unresolved — second bug active.

| Repo | Commit | Notes |
|------|--------|-------|
| SNOBOL4-tiny | `627a030` | Unchanged — analysis/diagnosis session only |
| .github | `(this)` | Session 49 handoff. §2 new deferred-assignment truth. §6 + §12 updated. |
| SNOBOL4-corpus | `3673364` | unchanged |

### 2026-03-12 — Session 50 (Smoke tests + root cause isolated: sno.y *var (expr) misparse)

Diagnosis session. No code fix landed in SNOBOL4-tiny. Three major findings:

1. **snoSrc IS correct** — prior `slen=0` hypothesis wrong. `_nl` initialized,
   concat emits correctly. `snoSrc = "    x = 'hello'\n"` (16 chars) at match time.
   Earlier slen=0 traces were from pattern construction during init, not main match.

2. **E_COND bug HARMLESS to match** — `sno_pat_cond(pat, "?")` wraps child correctly.
   Counter machinery still broken but NOT the match failure root cause.

3. **ROOT CAUSE ISOLATED**: `sno.y` `pat_atom` misreads `*var (expr)` as `var(expr)`
   (function call). Evidence: `sno_apply("snoWhite", ..., 1)` in generated snoStmt
   construction. `snoWhite` is a pattern variable — should be `sno_pat_ref` + concat.

**Smoke test infrastructure created** (`test/smoke/`):
- `build_beauty.sh` — PASS (0 gcc errors, 12847 lines)
- `test_snoCommand_match.sh` — **0/21 FAIL** (every stmt type: Parse Error)
- `test_self_beautify.sh` — NOT ACHIEVED (785-line diff, oracle=790 compiled=10)

**New invariant documented**: strip all `.`/`$` captures → structural pattern WILL
match all beauty.sno statements (bootstrap proof). Match failure is structural.

| Repo | Commit | Notes |
|------|--------|-------|
| SNOBOL4-tiny | `854b093` | findings + smoke tests + artifact + outputs. Parse Error remains. |
| .github | `(this)` | Session 50 handoff. §6 + §12 + Milestone Tracker updated. |
| SNOBOL4-corpus | `3673364` | unchanged |

---

*Rule 5 tightened Session 50: git log window halved from 2 hours → 1 hour. Rationale: transcript scan from GitHub history was consuming excess context; PLAN.md §6+§12 already carry all relevant history.*

### 2026-03-12 — Session 53 (Root cause fully diagnosed; architectural pivot to hand-rolled parser)

**Deep diagnosis of the LALR(1) misparse bug. Architectural decision made: replace Bison/Flex.**

Three sessions (51–53) were consumed by `*snoWhite (continuation)` misparsed as a function call.
Session 53 traced it to its bottom:

1. **Outer level (bstack_top=0)**: `%prec UDEREF` fix from Session 51 works. `*snoWhite` at
   statement level correctly emits `sno_pat_ref("snoWhite")`.

2. **Inner level (inside FENCE/ARBNO args)**: `bstack_top>0` → PAT_BUILTIN token NOT returned
   → arglist uses `expr` (value grammar) → `*snoWhite (bar)` parsed as `E_MUL(E_COND, E_CALL(snoWhite,bar))`
   or `E_DEREF(E_CALL(snoWhite,bar))` depending on context. Both wrong.

3. **Attempted fixes**: `pat_arglist` rule (uses `pat_expr` instead of `expr` for PAT_BUILTIN args),
   explicit `pat_cat STAR IDENT LPAREN pat_expr RPAREN` rule, `emit_pat E_MUL` handler for
   `E_CALL(!is_defined_function)` on right. Each fix partially worked but created new breakage
   (e.g., `LEN(5)` parse error when `primary: PAT_BUILTIN LPAREN arglist` was changed to `pat_arglist`).

4. **Root cause confirmed**: LALR(1) state merging is fundamental — cannot be fixed by adding
   grammar rules or precedence declarations without creating new conflicts elsewhere. The conflict
   count (20 SR + 139 RR) represents active wrong-parse events, not warnings.

**Decision (Lon + Claude, Session 53)**: Replace `sno.y`/`sno.l` with a hand-rolled
recursive-descent parser (`lex.c` + `parse.c`). Keep `emit.c`, `snoc.h`, `main.c`, all runtime.
Full design spec in §6a. WIP changes stashed in SNOBOL4-tiny (reference only, do not apply).

| Repo | Commit | Notes |
|------|--------|-------|
| SNOBOL4-tiny | `010529a` | Unchanged from Session 52. WIP stashed. |
| .github | `(this)` | Session 53 handoff. §6 replaced, §6a added, §12 appended. |
| SNOBOL4-corpus | `3673364` | unchanged |

---

### 2026-03-13 — Emergency Handoff Session (100-test suite + parser fixes)

**Focus:** Fix parse_expr0 LexMark regression, find | alternation root cause, design 100-test suite.

**Completed:**

1. **parse_expr0 reverted** — synthetic T_WS injection restored (was the one-liner fix from prior SESSION.md).

2. **| alternation root cause found and fixed** — `parse_expr4` concat loop called `skip_ws()` after consuming one WS token. `skip_ws` advanced `lx->pos` past the `|` token. Synthetic T_WS injection put WS back in peek slot but pos was already past `|`. `parse_expr3`'s loop then saw synthetic WS, consumed it, saw real WS (not T_PIPE), gave up. Fix: `LexMark mc` + `lex_restore(lx, mc)` instead of `skip_ws` + synthetic injection. Committed `17526bb`.

3. **New segfault isolated** — replacement statement (`subject pattern =`) with builtin call containing complex args crashes sno2c. Minimal reproducer: `X POS(0) SPAN(&UCASE &LCASE) =`. Affects is.sno, io.sno, case.sno. Not yet fixed.

4. **100-test suite designed** — Agreed with Lon: build proper test pyramid before pushing beauty.sno. 100 tests, 13 groups (A–M), 6 milestone gates (G-A through G-F). One `.sno` file per SNOBOL4 feature, each diff'd against CSNOBOL4. Living suite — new tests added as bugs found. Full design documented.

5. **Git history cleaned** — All 22 Claude-authored commits reassigned to `LCherryholmes <lcherryh@yahoo.com>` via `git filter-repo`. History is now 100% single-author. The one Claude-earned commit (Milestone 3, M-BEAUTY-FULL) not yet written.

6. **Three-Milestone Agreement clarified** — Milestone 1: beauty_core 0 gcc errors (done). Milestone 2: beauty_full with -INCLUDEs 0 gcc errors (done). Milestone 3: beauty_full_bin self-beautifies, diff empty = M-BEAUTY-FULL (active).

**Commits:**
| Repo | Commit | What |
|------|--------|------|
| SNOBOL4-tiny | `17526bb` | EMERGENCY WIP: parse_expr4 LexMark + | alternation fix |
| .github | this | SESSION.md + archive update |

**State at handoff:**
| Repo | Commit | Status |
|------|--------|--------|
| SNOBOL4-tiny | `17526bb` | parse_expr4 | fixed; segfault on replacement+builtin open |
| SNOBOL4-corpus | unchanged | |
| SNOBOL4-harness | unchanged | |

**Next session — first actions:**
1. Read SESSION.md (this file)
2. Fix replacement-statement segfault (see SESSION.md One Next Action)
3. `make -C src/sno2c` → verify `/tmp/test_segfault.sno` no longer crashes
4. Smoke tests → 21/21
5. Begin 100-test suite Group A (001–008)

---

### 2026-03-13 — Handoff Session (segfault fix + 106-test suite + nl investigation)

**Focus:** Fix replacement-statement segfault, run suite, investigate remaining smoke failures.

**Completed:**

1. **106-test crosscheck suite built and committed to SNOBOL4-corpus** (`3d32176`).
   Groups A–M, one `.sno` per feature, all `.ref` oracle files from CSNOBOL4.
   Sourced from dotnet test suite (Define, Array, Table, DATA, pattern tests).
   `run_all.sh` harness written. Lives in `crosscheck/` subdirs.

2. **Replacement-statement segfault fixed** (`f359079`). Root cause: `parse_body_field`
   called `parse_expr0` for pattern field; `parse_expr0` consumed trailing `=` as
   assignment, building `E_ASSIGN(pattern_node, NULL)`; `emit_expr` crashed on
   `cs(e->left->sval)` where sval=NULL. Fix: `parse_expr2` instead of `parse_expr0`.
   `is.sno`, `io.sno`, `case.sno` all compile. `beauty.sno` → 12,744 lines, gcc clean.

3. **New regression introduced:** `parse_expr2` excludes `|` alternation (that's at
   `parse_expr3`). So pattern `('a' | 'b')` breaks again. Smoke tests still 0/21.
   **Fix: change `parse_expr2` → `parse_expr3` on the pattern field line.**

4. **nl variable traced:** `global.sno` sets `nl` via `&ALPHABET POS(10) LEN(1) . nl`
   (pattern capture of newline from alphabet). May be failing in our runtime if
   pattern capture in init context doesn't work. Next suspect after parse_expr3 fix.

5. **Git history:** All 141 commits are `LCherryholmes <lcherryh@yahoo.com>`. Clean.
   Milestone 3 (M-BEAUTY-FULL) not yet written — still active.

**Commits:**
| Repo | Commit | What |
|------|--------|------|
| SNOBOL4-tiny | `f359079` | fix: parse_expr2 for pattern field, segfault gone |
| SNOBOL4-corpus | `3d32176` | feat: 106-test crosscheck suite |
| .github | this | SESSION.md + archive |

**State at handoff:**
| Repo | Commit | Status |
|------|--------|--------|
| SNOBOL4-tiny | `f359079` | segfault fixed; parse_expr3 fix needed; smoke 0/21 |
| SNOBOL4-corpus | `3d32176` | 106-test suite committed |

**Next session — first actions:**
1. Read SESSION.md
2. Change `parse_expr2` → `parse_expr3` in `parse_body_field` (see SESSION.md)
3. Verify segfault still gone AND | works in patterns
4. `make -C src/sno2c` → rebuild beauty → smoke tests → target 21/21
5. If smoke passes → run crosscheck suite → fix failures → diff oracle

---

## Session 52 — 2026-03-13

| Field | Value |
|-------|-------|
| **Repo** | SNOBOL4-tiny |
| **Sprint** | `smoke-tests` (2/4 toward M-BEAUTY-FULL) |
| **HEAD start** | `f359079` |
| **HEAD end** | `a69971e` |

### What happened

Diagnosed and fixed two of three bugs in the 0/21 smoke test chain.

**Fix 1 — parse_expr3 for pattern field** (`f359079` — previous session, confirmed)
Changed `parse_body_field` to call `parse_expr3` instead of `parse_expr2`.
Restores `|` alternation in pattern field. Segfault fix intact.

**Fix 2 — field assignment lvalue** (`a69971e` — this session)
`emit_assign_target` catch-all emitted `sno_iset(sno_apply("val",{n},1), rhs)`.
`sno_iset` converts its first arg to a string → silently did nothing.
Added `E_CALL && nargs==1` branch: now emits `sno_field_set(obj, "field", rhs)`.
6 sites corrected in beauty_full.c. Direct counter calls confirmed working.

**Also: T_FUNC engine node** — added `T_FUNC=44` to engine, `func`/`func_data`
fields to `Pattern` struct. `SPAT_USER_CALL` side-effect path uses it. Not the
active fix path but correct infrastructure.

**Root cause found for 0/21:** `epsilon . *IncCounter()` — the `.` (conditional
assignment) operator evaluates `*IncCounter()` at match time to get a variable
name. Our `Capture.var_name` is a static `char*` — deferred var expressions
store `NULL` → `var=?` at match time → IncCounter never called → top=0.

**Artifacts:** `beauty_full_session52.c` — 12,744 lines, 6 field-assignment fixes.
Diff from session51: exactly 6 `sno_iset` → `sno_field_set` substitutions.

### Next session

Fix capture var-name deferred evaluation in `snobol4_pattern.c`:
- Add `var_fn`/`var_data` to `Capture` struct
- In `apply_captures()`: call `var_fn` when set to get name at match time
- In `SPAT_CAPTURE` materialisation: detect `SPAT_USER_CALL`/`SPAT_DEREF` var exprs
- Test: `matched, top=2` from test_ninc.sno
- Then: smoke 21/21 → crosscheck → sprint 3 (beauty-runtime) → sprint 4 (diff)

---

## Session — 2026-03-13 (Claude Sonnet 4.6, session N+2)

**Repo:** SNOBOL4-tiny | **Sprint:** smoke-tests | **HEAD start:** d5d3796 | **HEAD end:** 40ea84f

**What happened:**
- Previous diagnosis ("nInc body missing") was wrong — nInc IS emitted correctly (FN[68], nbody=1)
- Built CSNOBOL4 from uploaded tarball; all tools working
- Confirmed snoCommand builds ok (type=5), snoParse type=5, snoSrc correct at match time
- Deep debug: added SNO_PAT_DEBUG, traced 62K lines of engine output
- Found: materialise() called once per scan position (0..N), not once per match
- Every SPAT_USER_CALL eagerly calls SNOBOL4 function at materialise time
- Reduce("snoStmt", 7) pops parse stack at materialise time — stack corrupted before engine runs
- Fix: moved materialise() outside scan loop in sno_match_pattern + sno_match_and_replace
- Added scan_start to EngineOpts/State; fixed scan_POS and scan_TAB for absolute positions
- Partial fix: var_resolve_callback (ARBNO T_VARREF) still calls materialise per iteration

**Root cause summary:** SPAT_USER_CALL must never eagerly call functions at materialise time.
Complete fix: make all SPAT_USER_CALL → T_FUNC always; handle SNO_PATTERN return in user_call_fn
by sub-matching the returned pattern at current cursor position.

**Commits:** 40ea84f

---

## Session — 2026-03-13 (Claude Sonnet 4.6, session N+3)

**Repo:** SNOBOL4-tiny | **Sprint:** compiled-byrd-boxes | **HEAD start:** be4fbb1 | **HEAD end:** cb3f97e

**What happened:**
- Built CSNOBOL4 2.3.3 from uploaded tarball; cloned SNOBOL4-tiny and SNOBOL4-corpus fresh
- Read full Python pipeline ground truth: byrd_ir.py, lower.py, emit_c_byrd.py
- Read all sprint0-5 oracle C files to understand target output format
- Read ByrdBox reference package (test_sno_2.c, test_sno_3.c) — gold standard labeled-goto style
- Read emit.c in full — understood current sno_pat_* / sno_match stopgap
- Wrote `src/sno2c/emit_byrd.c` from scratch: 1264 lines, full C port of lower.py + emit_c_byrd.py
- All pattern node types implemented: LIT, SEQ, ALT, ARBNO, POS, RPOS, LEN, TAB, RTAB,
  ANY, NOTANY, SPAN, BREAK, ARB, REM, FENCE (0+1 arg), SUCCEED, FAIL, ABORT, E_IMM, E_COND
- Two-pass via open_memstream: static decls before goto (C99 compliant)
- Declared byrd_emit_pattern in snoc.h; added emit_byrd.c to Makefile
- Fixed: duplicate root_beta label, unicode arrow escapes in comments
- Smoke test: POS(0) ARBNO("Bird"|"Blue") RPOS(0) on "BlueBird" → compiles + exits 0
- Sprint0-5 oracles: 15/15 pass (oracle .c files unchanged, runtime unchanged)
- sno2c builds clean: zero errors

**What is NOT done yet:**
- emit_byrd.c is not yet called by emit.c — integration step is next session's work
- sprint0-22 validation against sno2c output not yet run

**Next action:** Wire byrd_emit_pattern into emit_stmt() pattern-match case in emit.c,
replacing sno_match() + emit_pat() with direct Byrd box emission inline into the C output.
Then sprint0-22 validation. Then M-COMPILED-BYRD fires.

**Commits:** cb3f97e

---

## Session 2026-03-15 — emit.c wiring complete

**Repo:** SNOBOL4-tiny  **Sprint:** compiled-byrd-boxes  **HEAD start:** cb3f97e  **HEAD end:** 1c2062a

**What happened:**
- Wired byrd_emit_pattern() into emit_stmt() in emit.c — compiled Byrd box path now active
- Replaced sno_pat_*/engine.c stopgap (sno_match / emit_pat) with direct byrd_emit_pattern() call
- Fixed _ok%d duplicate declaration (declare before Byrd block, assign at gamma/omega labels)
- Fixed comment with embedded */ that broke C parser
- Discovered and confirmed: END must be in label column (column 1) not subject field
- Discovered key gap: bare LIT pattern is anchored at cursor=0, not substring scan
  SNOBOL4 requires scanning — fix is SEQ(ARB, pattern) wrap before byrd_emit_pattern()
- Oracle C files: 28/28 pass (4 intentional-fail exit 1 correctly)
- End-to-end .sno->C->compile->run works; Byrd box fires correctly confirmed with debug print
- CSNOBOL4 built from tarball (binary at snobol4-2.3.3/snobol4, not installed)

**Committed:** 1c2062a feat(emit): wire byrd_emit_pattern into emit_stmt

**Next action:** Add pat_is_anchored() + ARB scan wrap in emit.c before byrd_emit_pattern() call

---

## Session 2026-03-15 (Claude Sonnet 4.6)

**Repo:** SNOBOL4-tiny  
**Sprint:** `compiled-byrd-boxes` → complete; `beauty-runtime` opened  
**Milestones fired:** M-COMPILED-BYRD ✅

### Commits this session

| Hash | Repo | Message |
|------|------|---------|
| `735c456` | SNOBOL4-tiny | feat(emit): ARB scan wrap + uid continuity — SNOBOL4 substring scan semantics |
| `560c56a` | SNOBOL4-tiny | feat(runtime): engine_stub.c — compiled path links without engine.c |
| `b8a92a4` | .github | milestone: M-COMPILED-BYRD fired (560c56a) — sprint 3/4 beauty-runtime active |

### What was done

- **ARB scan wrap** (`emit.c`): `pat_is_anchored()` helper added. Bare patterns now wrapped in `SEQ(ARB, pattern)` before `byrd_emit_pattern()` so `X "hello"` finds `"hello"` anywhere in `X` — correct SNOBOL4 substring scan semantics.
- **uid continuity fix** (`emit_byrd.c`): `byrd_uid_ctr` saved/restored across two-pass emission instead of resetting to 0. Multiple pattern-match statements in one `.sno` file no longer generate duplicate C labels.
- **engine_stub.c**: Single-symbol stub (`engine_match_ex` no-op with correct signature from `engine.h`). Compiled binaries link without `engine.c`. Only symbol needed: `engine_match_ex` referenced from `sno_match_pattern()` in `snobol4_pattern.c` — never called by compiled Byrd box output.
- **Integration test**: `"hello world"` substring scans work end-to-end — prints `ALL OK` with `engine_stub.c`.
- **Sprint oracles**: 28/28 pass throughout.

### M-COMPILED-BYRD trigger conditions met

- ✅ `sno2c` emits labeled-goto Byrd boxes
- ✅ Sprint oracles 28/28
- ✅ Binary links without `engine.c`
- ✅ Integration test: ALL OK

### Next session opens

Sprint 3/4 `beauty-runtime`: compile `beauty.sno` with `sno2c`, run binary to completion without crash. SESSION.md has full One Next Action.

---

## Session 2026-03-16 (ace2883)

| Commit | Repo | Description |
|--------|------|-------------|
| `3ea9815` | SNOBOL4-tiny | refactor: strip sno_/SNO_ prefix — P4-style collision renames throughout |
| `ace2883` | SNOBOL4-tiny | refactor: dyvide → divyde |
| `5ca2fa9` | .github | session: P4-style prefix strip complete — resume beauty-runtime debug |

### What was done

**Prefix eradication** — complete removal of `sno_` and `SNO_` from all ~10,000
occurrences across 40 files. P4/P5 compiler misspelling technique used for all
stdlib/keyword collisions. `snoc → sno2c` everywhere. File renames:
`snoc_runtime.h → runtime_shim.h`, `snoc.h → sno2c.h`.

**Collision resolutions (hard — would break build):**

| Old | New | Reason |
|-----|-----|--------|
| `sno_int` | `vint` | C keyword |
| `sno_div` | `divyde` | stdlib `div()` |
| `sno_pow` | `powr` | math.h `pow()` |
| `sno_exit` | `xit` | stdlib `exit()` |
| `sno_abort` | `abrt` | stdlib `abort()` |
| `sno_dup` | `dupl` | unistd.h `dup()` |

**Defensive renames (soft — future-proofing):**

| Old | New | Reason |
|-----|-----|--------|
| `str` | `strv` | str* family owned by string.h |
| `match` | `mtch` | POSIX regmatch_t / future std |
| `apply` | `aply` | C++ compat headers |
| `eval` | `evl` | future math/scripting libs |
| `concat` | `ccat` | future C string lib |
| `index` | `indx` | POSIX index() in string.h |
| `replace` | `replc` | future C string lib |
| `init` | `ini` | collision risk with any lib init |
| `enter` | `entr` | curses.h |
| `register` | `registr` | deprecated C keyword |

Binary output unchanged throughout. Build clean at every stage.

**Parse Error debug** — environment re-established, root cause confirmed from prior
session: ARBNO in `*snoParse` takes zero-iteration epsilon on `"START\n"`. T_BREAK
trace never fires. Next action: add ARBNO debug trace to confirm, then chase
snoCommand failure path.

### Next session opens

Sprint 3/4 `beauty-runtime`: ARBNO epsilon trace → snoCommand failure path.
SESSION.md has full One Next Action.

## Session 56 — 2026-03-14 (Claude Sonnet 4.6)

**Sprint:** `trampoline` → `stmt-fn` (sprints 1+2 of 9 toward M-BEAUTY-FULL)

**Milestones fired:**
- M-TRAMPOLINE `fb4915e` — `trampoline.h` + 3 POC programs
- M-STMT-FN `4a6db69` — `-trampoline` flag wired into `sno2c`

**What was built:**

`trampoline.h`:
- `block_fn_t = void*(*)(void)` — the recursive trampoline type
- `trampoline_run(start)`: `while(pc) pc = (block_fn_t)pc()`
- `BLOCK_FN`/`STMT_FN` macros, ABORT handler chain (cold path)

Three hand-written POC programs in `src/sno2c/`:
- `trampoline_hello.c` ✅ `hello, trampoline`
- `trampoline_branches.c` ✅ `1 2 3 done` (S/F routing, loop-back)
- `trampoline_pattern.c` ✅ runtime integrated, literal pattern S/F

`emit.c` + `main.c` changes:
- `trampoline_mode` flag set by `-trampoline` CLI arg
- `emit_goto_target()`: `return block_X` instead of `goto _L_X`
- `emit_goto()`: `return (void*)_tramp_next_N` for fall-through
- `emit_trampoline_program()`: stmt_N() + block_L() + trampoline main()
- DEFINE'd fns: emit via existing `emit_fn()` with `trampoline_mode=0`

Also: CSNOBOL4 built from `snobol4-2_3_3_tar.gz`, SNOBOL4 syntax verified hands-on.

**Artifacts committed** `artifacts/trampoline_session56/`:
- `hello_tramp.c` 71L ✅, `branch_tramp.c` 150L ✅, `fn_tramp.c` 125L ✅
- `beauty_tramp_session56.c` 19907L, md5 `a85b29a9`, **0 gcc errors** ✅
- Binary runs: outputs 10 lines then exits (block grouping bug — see below)

**Active bug:**

`block_START` absorbs ALL main-level stmts into one giant sequential block.
The block-splitting logic in `emit_trampoline_program` Pass 2 has a logic
error — after the first labeled stmt closes `block_START` and opens a new
block, subsequent labeled stmts don't correctly open their own blocks.

Root cause in `emit_trampoline_program` (src/sno2c/emit.c):
```c
// BROKEN: cur_block_label never updates after first label
if (s->label && sid > 1) {
    E("    return block_%s;\n}\n\n", cs_label(s->label));
    in_first_block = 0;
    E("static void *block_%s(void) {\n", cs_label(s->label));
}
// All subsequent labeled stmts also hit this — but block is already open
// and we open another block_START equivalent or nothing
```

Fix (two lines in Pass 2):
```c
if (s->label && block_open) {
    E("    return block_%s;\n}\n\n", cs_label(s->label));  // close current
    block_open = 0;
}
if (!block_open) {
    E("static void *block_%s(void) {\n",
      s->label ? cs_label(s->label) : "START");
    block_open = 1;
}
```

**Next session opens:**

Sprint `block-fn` (3/9). Fix Pass 2 block logic → regenerate beauty_tramp.c →
recompile → run → diff oracle. If diff empty: M-BEAUTY-FULL fires.
SESSION.md has full One Next Action.
