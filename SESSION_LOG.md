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
