# MILESTONE-NET-SNOBOL4.md — SNOBOL4 × .NET Unified Milestone Ladder

**Session:** D · **Repos:** one4all · snobol4dotnet
**Team:** Lon Jones Cherryholmes (arch) · Jeffrey Cooper M.D. (.NET) · Claude Sonnet 4.6 (co-author)

---

## Organizing principle: one unified chain — dynamic → static → optimized

This is a single ladder from interpreted execution to statically optimized
code generation.  There are no parallel tracks.

**The key insight:** the interpreter *is* the dynamic execution engine.
`scrip-interp.cs` instantiates MSIL Byrd box objects (loaded from `boxes.dll`) and runs them directly —
this is not a temporary scaffold, it is Phase D of the full execution model.
Later phases add optimization: box sequence caching, then full IL emission.
The same IR and the same IByrdBox graph serve all phases.

```
Phase D (dynamic — interpreted):
  .sno → Pidgin parser → IR tree → PatternBuilder → IByrdBox graph (in memory) → run

Phase S (static — compiled):
  .sno → scrip-cc IR → emit_net.c → .il → ilasm → .exe
  (same IR node shape; same IByrdBox classes reused at runtime)

Phase O (optimized):
  Cached box sequences · inlined hot paths · AOT IL emission from interpreter
```

**One IR, three consumers** (D-167 invariant):
- `scrip-cc` (C compiler) — emits IL from IR
- `scrip-interp.c` (C interpreter) — tree-walks IR, reference oracle
- `scrip-interp.cs` (C# interpreter) — tree-walks IR, instantiates MSIL `IByrdBox` objects from `boxes.dll`

No C code in the interpreter.  No generated C# code.  scrip-cc never invoked
by the interpreter at runtime or build time.  EVAL/CODE build the same IR
nodes at runtime that the Pidgin parser produces.

---

## What already exists (reuse)

| Component | Location | Status |
|-----------|----------|--------|
| All 27 MSIL Byrd boxes | `src/runtime/boxes/*/bb_*.il` → assembled into `boxes.dll` | ✅ M-NET-BOXES |
| `ByrdBoxExecutor` (Phase 3 trampoline) | `src/runtime/boxes/shared/bb_executor.il` | ✅ |
| `IByrdBox`, `Spec`, `MatchState` | `src/runtime/boxes/shared/bb_box.il` | ✅ |
| Build script | `src/runtime/boxes/build_boxes.sh` → `ilasm` → `boxes.dll` | ✅ |
| `ThreadedExecuteLoop.cs` | snobol4dotnet | ✅ Jeff's pipeline (Phase S reference) |
| `BuildEval` / `BuildCode` | snobol4dotnet | ✅ self-hosted, no Roslyn |

---

## 5-phase statement executor (all phases share this model)

```
Phase 1: build_subject  — resolve subject variable → Σ/Δ/Ω
Phase 2: build_pattern  — IR pattern node → IByrdBox graph (PatternBuilder)
Phase 3: run_match      — ByrdBoxExecutor trampoline, collect captures
Phase 4: build_repl     — evaluate replacement expression
Phase 5: perform_repl   — splice into subject, flush captures, :S/:F branch
```

Captures commit **only on Phase 5 :S** — by construction, no @N bug.

---

## Milestone chain

### Phase B2 — Beauty suite (snobol4dotnet) ⚠️ CURRENT

| Milestone | Description | Gate |
|-----------|-------------|------|
| **M-NET-BEAUTY-19** | ⚠️ **NOW** — All 19 beauty drivers pass. B-BEAUTY-0 (FENCE redef) → B-BEAUTY-9 (ShiftReduce). Ladder in `MILESTONE-NET-BEAUTY-19.md`. Baseline: 7/19. | 19/19 pass |
| **M-NET-BEAUTY-SELF** | **NEXT** — beauty.sno self-beautifies: reads itself as INPUT, writes itself to OUTPUT, output matches input exactly. Gates on M-NET-BEAUTY-19. | output == input |

---

### Phase 0 — Foundation (complete)

| Milestone | Description | Status |
|-----------|-------------|--------|
| **M-NET-BOXES** | 27 MSIL Byrd boxes (`bb_*.il`) assembled via `ilasm` into `boxes.dll` · `ByrdBoxExecutor` · `IByrdBox`/`Spec`/`MatchState` in `bb_box.il` | ✅ one4all `90d5531` |
| **M-NET-INTERP-A00** | IR design locked: one IR / three consumers; no C; no generated C#; scrip-cc never invoked; EVAL/CODE build same IR nodes as parser | ✅ .github `aeee9c2` |

---

### Phase A — Dynamic interpreter: full corpus

| Milestone | Description | Gate |
|-----------|-------------|------|
| **M-NET-INTERP-A01a** | **Lexer** — `Snobol4Lexer.cs` tokenizes `.sno` source; token stream mirrors `lex.c` output on 19 test cases | 19/19 token stream tests pass |
| **M-NET-INTERP-A01b** | **Parser** — `Snobol4Parser.cs` (Pidgin combinators) consumes token stream → `IrStmt[]`; `IrNode.cs` mirrors `ir.h` `EKind`/`EXPR_t`/`STMT_t`; pretty-print AST matches `parse.c` output | 19/19 parse tests pass |
| **M-NET-INTERP-A01c** | **IR tree verified** — `IrNode`/`IrStmt` shape confirmed vs `ir.h`; `Ast.cs` removed; `scrip-interp.csproj` builds clean; hello/empty_string/multi smoke pass | 3/3 smoke + IR shape matches oracle |
| **M-NET-INTERP-A02** | **Stack machine** — Phases 1/4/5: assignments · OUTPUT · gotos · labels · END · arithmetic via explicit value stack dispatching on `IrKind` · `SnobolEnv` dict | rung1 smoke (20 tests) pass |
| **M-NET-INTERP-A03** | **Byrd box sequencer** — Phase 2/3: `PatternBuilder.cs` walks pattern `IrKind` → `IByrdBox` graph · `ByrdBoxExecutor` trampoline wired · LIT ANY SPAN ARB ARBNO first | rung2–5 (60 tests) pass |
| **M-NET-INTERP-A04** | Full corpus run · diff vs SPITBOL oracle · all rungs · crosscheck | ≥ 130/142 pass |
| **M-NET-INTERP-A05** | Remaining failures closed · full corpus clean | 142/142 pass · crosscheck 100% |

---

### Phase B — Dynamic interpreter: advanced features

| Milestone | Description | Gate |
|-----------|-------------|------|
| **M-NET-INTERP-B01** | Captures: `@var` / `.var` / `$var` · Phase 3/5 boundary correct by construction | rung9 capture tests 100% vs SPITBOL |
| **M-NET-INTERP-B02** | Functions: DEFINE / RETURN / NRETURN / FRETURN / call stack | rung10 function tests pass |
| **M-NET-INTERP-B03** | EVAL / CODE: Pidgin parser called at runtime · builds live IR → IByrdBox graph · same node shape as static parse | rung10/1016_eval pass · CODE corpus pass |

---

### Phase C — Static compiler: correctness audit (snobol4dotnet / ThreadedExecuteLoop)

*The interpreter (Phase A/B) is the oracle for this phase.
Any interpreter result that differs from ThreadedExecuteLoop is a compiler bug.*

| Milestone | Description | Gate |
|-----------|-------------|------|
| **M-NET-SNIPPETS** | ⚠️ **CURRENT** — Gimpel/corpus snippet test factory: mine all 145 Gimpel programs + crosscheck corpus for self-contained building-block tests · generate `CorpusRef_GimpelBits.cs` and related files · fix test-code bugs (roman semicolons, sqrt rename, fib base case, trim assertion, fixed-col TRIM, opsyn arg3=0) · fix D-NET-186 (LGT-RHS → error 212) · fix D-NET-187 (OPSYN builtin lookup) · fix TEST_Abend regression · fix 099 DATATYPE casing (`'integer'` not `'INTEGER'`) | ≥ 2040 passed · 0 failed · crosscheck 80/80 · all GimpelBits green |
| **M-NET-P35-FIX** | Fix @N Phase 3/5 capture clobber in `ThreadedExecuteLoop.cs` | crosscheck 80/80 · dotnet test ≥ 1911/1913 |
| **M-NET-PAT-CAPTURES** | Capture audit: `@/./$` vs interpreter + stmt_exec.c oracle | rung9 100% vs SPITBOL |
| **M-NET-PAT-PRIMITIVES** | 16 pattern primitives vs SPITBOL oracle: LEN POS RPOS TAB RTAB REM ANY NOTANY SPAN BREAK BREAKX FENCE FAIL SUCCEED ABORT BAL | rung2–9 100% · dotnet test 1913/1913 |
| **M-NET-EVAL-COMPLETE** | EVAL/CODE edge cases: pattern context · CODE across statement boundaries · AppendCompile jump patching | rung10/1016_eval pass · CODE corpus pass |
| **M-NET-NRETURN** | NRETURN lvalue-assign · follow DYN-42 fix | rung10/1013 pass |

---

### Phase O — Optimization: dynamic → static

*The interpreter generates box graphs in memory and runs them.
Phase O caches, specializes, and ultimately emits IL directly from the interpreter path.*

| Milestone | Description | Gate |
|-----------|-------------|------|
| **M-NET-OPT-CACHE** | Box sequence caching: cache compiled IByrdBox graphs keyed by pattern IR node · avoid rebuild on repeat execution | ≥ 2× throughput on loop-heavy corpus |
| **M-NET-OPT-EMIT** | IL emission from interpreter: hot box sequences → emitted IL stubs · AOT path wired in | selected corpus tests pass via emitted IL |
| **M-NET-OPT-FULL** | Full AOT IL emission: interpreter drives complete IL generation · replaces emit_net.c path | 142/142 via emitted IL · scrip-cc .NET backend retired |

---

### Phase Z — Bootstrap

| Milestone | Description | Gate |
|-----------|-------------|------|
| **M-NET-SNOCONE** | Snocone self-test under .NET interpreter | Snocone self-test ✅ |
| **M-NET-BOOTSTRAP** | snobol4dotnet compiles itself via interpreter | Self-hosting bootstrap ✅ |

---

## Sprint sequence

| Sprint | Milestone |
|--------|-----------|
| D-165 | M-NET-BOXES ✅ |
| D-166 | planning |
| D-167 | M-NET-INTERP-A00 ✅ · IR design locked · unified chain |
| D-168 | M-NET-INTERP-A01a — Lexer (`Snobol4Lexer.cs`, token stream mirrors `lex.c`) |
| D-169 | M-NET-INTERP-A01b — Parser (Pidgin → `IrStmt[]`; `IrNode.cs` mirrors `ir.h`) |
| D-170 | M-NET-INTERP-A01c — IR verified; `Ast.cs` removed; build clean; 3/3 smoke |
| D-171 | M-NET-INTERP-A02 — Stack machine Phases 1/4/5 |
| D-172 | M-NET-INTERP-A03 — Byrd box sequencer Phases 2/3 |
| D-173 | M-NET-INTERP-A04 — Full corpus vs SPITBOL |
| D-174 | M-NET-INTERP-A05 — All failures closed |
| D-175 | M-NET-INTERP-B01 — Captures |
| D-176 | M-NET-INTERP-B02 — Functions |
| D-177 | M-NET-INTERP-B03 — EVAL/CODE |
| D-178 | M-NET-P35-FIX + M-NET-PAT-CAPTURES |
| D-179 | M-NET-PAT-PRIMITIVES |
| D-180 | M-NET-EVAL-COMPLETE + M-NET-NRETURN |
| D-215 | M-NET-BEAUTY-19 — beauty suite 19/19 (B-BEAUTY-0 → B-BEAUTY-9) |
| D-216 | M-NET-BEAUTY-SELF — beauty.sno self-hosting |
| D-217 | M-NET-OPT-CACHE |
| D-182 | M-NET-OPT-EMIT |
| D-183 | M-NET-OPT-FULL |
| D-184 | M-NET-SNOCONE + M-NET-BOOTSTRAP |

---

## EVAL and CODE: runtime IR construction

EVAL parses a SNOBOL4 pattern expression at runtime:
  `Snobol4Parser.ParsePattern(str)` → same IR node types as static parse
  → `PatternBuilder.BuildFromNode()` → live IByrdBox graph
  → `ByrdBoxExecutor` — identical execution path to statically parsed patterns.

CODE does the same for a full statement list.

No special runtime IR.  No Roslyn.  No scrip-cc.  The Pidgin parser *is* the
runtime compiler for EVAL/CODE.

---

*MILESTONE-NET-SNOBOL4.md — unified chain rewritten D-167, 2026-04-02, Claude Sonnet 4.6.*
*One chain: dynamic (interpreted, in-memory box graphs) → static (IL emission) → optimized.*
*MILESTONE-NET-INTERP.md is now a detail annex only — this file is canonical for all SNOBOL4 .NET work.*
