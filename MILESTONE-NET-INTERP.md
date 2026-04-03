> ⚠️ **ANNEX ONLY** — D-167 unified chain. Canonical doc is `MILESTONE-NET-SNOBOL4.md`.
> This file kept for detail reference on scrip-interp.cs internals only.

# MILESTONE-NET-INTERP — scrip-interp.cs: SNOBOL4 .NET Interpreter

**Session prefix:** D · **Repo:** one4all (or snobol4dotnet) · **Frontend:** Pidgin parser · **Backend:** C# bb boxes

---

## What it is

`scrip-interp.cs` is a standalone C# SNOBOL4 interpreter that:

1. **Parses** `.sno` source using the **Pidgin parser combinator** (no scrip-cc, no MSIL emit)
2. **Evaluates** statements directly via a C# tree-walk eval loop
3. **Drives pattern matching** through the existing `IByrdBox` graph (`src/runtime/boxes/`)
4. **Eliminates compile+assemble+link** from the .NET test cycle — `dotnet run foo.sno` only

This is the .NET analogue of `scrip-interp.c` (DYN- session), and the fastest
path to running the full corpus against the C# Byrd box implementations.

### Pipeline

```
.sno file
  → Pidgin parser → StmtNode[] (typed C# AST)
  → C# eval loop
      Phase 1: resolve subject variable → string (Σ/Δ/Ω)
      Phase 2: build IByrdBox graph from pattern Node (via ByrdBoxFactory-style builder)
      Phase 3: ByrdBoxExecutor.Run() — scan loop
      Phase 4: evaluate replacement expression
      Phase 5: splice into subject, commit captures, :S/:F branch
  → output
```

No scrip-cc. No ilasm. No mono startup per test.

---

## What already exists (reuse)

| Component | Location | Status |
|-----------|----------|--------|
| All 27 C# Byrd boxes | `src/runtime/boxes/*/bb_*.cs` | ✅ M-NET-BOXES |
| `ByrdBoxExecutor` (Phase 3 trampoline) | `src/runtime/boxes/shared/bb_executor.cs` | ✅ |
| `ByrdBoxFactory` (pattern tree → IByrdBox) | `src/runtime/boxes/shared/bb_factory.cs` | ✅ partial |
| `IByrdBox`, `Spec`, `MatchState` | `src/runtime/boxes/shared/bb_box.cs` | ✅ |
| Pidgin parser | `src/driver/dotnet/Snobol4Parser.cs` (to create) | — |
| Variable store | new `SnobolEnv` dict (simple) | — |

The `ByrdBoxFactory` currently bridges Jeff's `Pattern` hierarchy.
For the interpreter it needs a parallel `BuildFromNode(Node)` method
that walks Pidgin AST pattern nodes instead — straightforward extension.

---

## Milestone chain

| Milestone | Description | Gate |
|-----------|-------------|------|
| **M-NET-INTERP-A00** | IR design locked (D-167): one IR / three consumers; no C; no generated C#; scrip-cc never invoked; EVAL/CODE build same IR nodes at runtime as parser | ✅ Design doc committed |
| **M-NET-INTERP-A01** | Project scaffold + Pidgin parser: parse all 19 test cases, pretty-print AST | 19/19 parse tests pass |
| **M-NET-INTERP-A02** | Eval loop Phase 1/4/5: assignments, OUTPUT, gotos, labels, END | 20 smoke corpus tests pass (rung1) |
| **M-NET-INTERP-A03** | Phase 2/3: pattern matching via IByrdBox — literal, ANY, SPAN, ARB, ARBNO | 60 pattern corpus tests pass (rung2–5) |
| **M-NET-INTERP-A04** | Full corpus run — diff vs SPITBOL oracle | ≥ 130/142 match |
| **M-NET-INTERP-B01** | Captures: @var / .var / $var — Phase 3/5 boundary correct by construction | rung9 capture tests 100% |
| **M-NET-INTERP-B02** | Functions: DEFINE / RETURN / NRETURN / FRETURN / call stack | rung10 function tests pass |
| **M-NET-INTERP-B03** | EVAL / CODE self-hosted (reuse snobol4dotnet BuildEval if convenient) | rung10/1016_eval pass |

---

## Files to create

```
src/driver/dotnet/
  scrip-interp.cs          — main entry point (dotnet run)
  Snobol4Parser.cs         — Pidgin parser (from Snobol4Pidgin.cs sketch)
  SnobolEnv.cs             — variable store + builtin functions
  PatternBuilder.cs        — Pidgin Node → IByrdBox (extends ByrdBoxFactory logic)
  Eval.cs                  — expression evaluator: Node → SnobolValue
  Executor.cs              — 5-phase statement executor
  scrip-interp.csproj      — project file (Pidgin NuGet ref)
test/run_interp_dotnet.sh  — corpus runner: diff interp vs SPITBOL oracle
```

---

## IR design (D-167 — canonical)

**One IR, three consumers.** The IR tree shape is identical across:

| Consumer | Language | Role |
|----------|----------|------|
| `scrip-cc` | C | compiler — emits IL/NASM/JVM bytecode |
| `scrip-interp.c` | C | tree-walk interpreter (DYN- reference) |
| `scrip-interp.cs` | C# | this interpreter |

This is a design invariant, not a convenience. Consequences:

- Corpus tests are a true oracle across all three — failures isolate to the consumer, not IR shape
- EVAL/CODE in C# build the same IR node types that the parser produces — no special runtime IR
- `PatternBuilder.cs` walks the same node kinds that `Snobol4Parser.cs` emits
- No scrip-cc involvement at any point — the C# parser produces the shared IR directly

**No C code. No generated C# code.** scrip-interp.cs is entirely hand-written managed C#.
scrip-cc is not invoked at runtime or build time for the interpreter track.

---

## Key design decisions

### Parser: Pidgin (not Irony, not Sprache)
- Clean typed record AST maps directly to eval loop dispatch
- `ExpressionParser.Build()` handles full operator tower
- Significant-whitespace handled naturally as parser combinators
- No LALR(1) limitations; no opaque `ParseTreeNode`

### Variable store: simple Dictionary<string, SnobolValue>
- `SnobolValue` = discriminated union: `String | Integer | Real | Pattern | Unset`
- No threading; no GC pressure from snobol4.h's `DESCR_t`
- Captures write directly — Phase 3/5 boundary correct by construction
  (unlike `ThreadedExecuteLoop.cs`'s @N bug — this interpreter avoids it structurally)

### Box wiring: PatternBuilder.cs
- Mirrors `bb_build()` in `stmt_exec.c`
- Input: Pidgin `Node` subtree from pattern position
- Output: `IByrdBox` rooted graph
- Captures registered as `BbCapture` wrappers — committed only on Phase 5 :S

---

## Routing

- **Session doc:** `SESSION-snobol4-net.md` (D- session)
- **Predecessor milestones:** M-NET-BOXES ✅ · M-NET-P35-FIX (parallel — interp avoids the bug structurally)
- **Oracle:** SPITBOL (`snobol4ever/x64`) · `scrip-interp.c` (C reference)
- **Deep ref:** `ARCH-byrd-dynamic.md` §The SNOBOL4 Statement · `MILESTONE-DYN-INTERP.md`

---

*MILESTONE-NET-INTERP.md — created D-166, 2026-04-02, Claude Sonnet 4.6.*
*D-167, 2026-04-02: IR design section added — one IR / three consumers invariant; M-NET-INTERP-A00 added.*
*Pidgin parser + C# bb boxes = zero compile/link overhead in .NET test cycle.*
