> ⚠️ **ANNEX ONLY** — D-168+ unified chain. Canonical doc is `MILESTONE-NET-SNOBOL4.md`.
> This file covers `scrip-interp.cs` pipeline design and implementation notes.

# MILESTONE-NET-INTERP — scrip-interp.cs: SNOBOL4 .NET Interpreter

**Session prefix:** D · **Repo:** one4all · **Frontend:** Pidgin → IR · **Backend:** MSIL Byrd boxes (ilasm → boxes.dll)

---

## What it is

`scrip-interp.cs` is a standalone C# SNOBOL4 interpreter:

```
.sno source
  → Lexer (C# — mirrors lex.c token stream)
  → Pidgin parser (C# — mirrors parse.c, produces IR nodes)
  → IrNode tree  (C# mirror of EXPR_t / STMT_t from ir.h / scrip_cc.h)
  → 5-phase executor
      Phase 1: resolve subject → string (Σ/Δ/Ω)
      Phase 2: PatternBuilder walks IR pattern subtree → IByrdBox graph
      Phase 3: ByrdBoxExecutor.Run() — scan loop (Byrd box trampoline)
      Phase 4: evaluate replacement IR subtree → SnobolValue
      Phase 5: splice into subject, commit captures, :S/:F branch
  → output
```

**No scrip-cc. No ilasm. No mono startup per test.**

---

## The IR mirror invariant

The C# IR types **mirror** `EXPR_t` / `STMT_t` / `EKind` from `ir.h` + `scrip_cc.h` exactly.
This is the "one IR, three consumers" design principle:

| Consumer     | Language | IR source               |
|--------------|----------|-------------------------|
| `scrip-cc`   | C        | `ir.h` `EXPR_t`/`EKind` |
| `scrip-interp.c` | C    | same `EXPR_t`/`EKind`   |
| `scrip-interp.cs` | C#  | **C# mirror of same**   |

The C# mirror uses the **same node kind names** (`EKind` → `IrKind` enum in C#),
same tree shape (children array, sval/ival/fval payloads), same `STMT_t` fields
(label, subject, pattern, replacement, has_eq, is_end, goto onsuccess/onfailure/uncond).

This means: a corpus failure isolates to the C# consumer, not IR shape divergence.
EVAL/CODE at runtime call the Pidgin parser to build live IR trees — same node kinds.

---

## Execution layer vs oracle — CRITICAL DISTINCTION

The `bb_*.cs` files are **oracle/reference only** — exactly parallel to `bb_*.java` for the JVM session.
They are NOT the execution layer. Do not invoke them from the interpreter.

**Execution layer = MSIL (ilasm → boxes.dll):**

| Component | Location | Status |
|-----------|----------|--------|
| `bb_box.il` — `IByrdBox` interface, `Spec` valuetype, `MatchState` class | `src/runtime/boxes/shared/bb_box.il` | ✅ D-169 |
| `bb_executor.il` — `ByrdBoxExecutor`, `MatchResult` | `src/runtime/boxes/shared/bb_executor.il` | ✅ D-169 |
| All 27 `bb_*.il` box implementations | `src/runtime/boxes/*/bb_*.il` | ✅ D-169 |
| Assembled `boxes.dll` | `ilasm /dll` from all `bb_*.il` | ✅ D-169 |

**Oracle only — do NOT invoke from interpreter:**

| Component | Location |
|-----------|----------|
| `bb_*.cs` — C# authoring oracle | `src/runtime/boxes/*/bb_*.cs` |
| `bb_executor.cs` | `src/runtime/boxes/shared/bb_executor.cs` |
| `bb_box.cs` | `src/runtime/boxes/shared/bb_box.cs` |

**Why MSIL:** the generator (`emit_net.c`) emits `.il` files assembled by `ilasm`.
The interpreter tests the same artifact — `boxes.dll` assembled from `bb_*.il` — so
there is zero semantic gap between interpreted and generated execution.

`scrip-interp.cs` loads `boxes.dll` via `Assembly.LoadFrom` and invokes `Alpha`/`Beta`
through the `IByrdBox` interface defined in `bb_box.il`.

`ByrdBoxFactory.cs` bridges Jeff's snobol4dotnet `Pattern` hierarchy — **not used**
by the interpreter. `PatternBuilder.cs` walks IR nodes instead.

---

## D-167 status (what was built — needs revision)

`D-167` built a working scaffold (`fb074c9`) but with a hand-rolled AST (`Ast.cs`)
that does **not** mirror `ir.h`. Specifically:

- `Ast.cs` defines bespoke C# records (`SLit`, `NLit`, `Var`, `Cat`, ...) instead of
  mirroring `EKind` / `EXPR_t` / `STMT_t`
- `Snobol4Parser.cs` is a hand-rolled recursive descent rather than Pidgin combinators
- `PatternBuilder.cs` and `Executor.cs` dispatch on the bespoke records

**D-168 task:** replace `Ast.cs` with `IrNode.cs` (C# mirror of `EXPR_t`/`STMT_t`/`EKind`),
update parser and executor to use the canonical node kinds. The Pidgin parser structure,
`SnobolEnv.cs` builtins, and box wiring are otherwise sound.

---

## Files — target state

```
src/driver/dotnet/
  scrip-interp.csproj     ✅ D-167
  IrNode.cs               ← REPLACE Ast.cs: EKind enum + IrNode (mirrors EXPR_t) + IrStmt (mirrors STMT_t)
  Snobol4Parser.cs        ← revise: Pidgin combinators → IrNode / IrStmt (not bespoke records)
  SnobolEnv.cs            ✅ D-167 (keep — variable store + builtins are correct)
  PatternBuilder.cs       ← revise: dispatch on EKind instead of bespoke record types
  Executor.cs             ← revise: dispatch on EKind instead of bespoke record types
  Program.cs              ✅ D-167
test/run_interp_dotnet.sh ← new: corpus runner diff vs SPITBOL
```

---

## IrNode.cs — design

```csharp
// Mirrors EKind from ir.h — same names, same semantics
public enum IrKind {
    // Literals
    E_QLIT, E_ILIT, E_FLIT, E_NUL,
    // References
    E_VAR, E_KEYWORD, E_INDIRECT, E_DEFER,
    // Arithmetic
    E_MNS, E_PLS, E_ADD, E_SUB, E_MUL, E_DIV, E_MOD, E_POW,
    E_INTERROGATE, E_NAME,
    // Structure
    E_SEQ, E_CAT, E_ALT,
    // Pattern primitives (each → distinct box)
    E_ARB, E_ARBNO, E_ANY, E_NOTANY, E_SPAN, E_BREAK, E_BREAKX,
    E_LEN, E_TAB, E_RTAB, E_REM, E_FAIL, E_SUCCEED, E_FENCE, E_ABORT, E_BAL,
    E_POS, E_RPOS,
    // Captures
    E_CAPT_COND_ASGN, E_CAPT_IMMED_ASGN, E_CAPT_CURSOR,
    // Call/access
    E_FNC, E_IDX, E_ASSIGN, E_SCAN,
}

// Mirrors EXPR_t — same payload fields
public sealed class IrNode {
    public IrKind     Kind;
    public string?    SVal;      // E_QLIT text, E_VAR/E_FNC name
    public long       IVal;      // E_ILIT
    public double     DVal;      // E_FLIT
    public IrNode[]   Children;  // n-ary, mirrors children[]
}

// Mirrors STMT_t
public sealed class IrStmt {
    public string?  Label;
    public IrNode?  Subject;
    public IrNode?  Pattern;
    public IrNode?  Replacement;
    public bool     HasEq;
    public bool     IsEnd;
    public string?  GotoOnSuccess;
    public string?  GotoOnFailure;
    public string?  GotoUnconditional;
}
```

---

## Milestone chain (revised D-168 — lex → parse → IR explicit)

| Milestone | Description | Gate |
|-----------|-------------|------|
| **M-NET-INTERP-A00** | IR design: one IR / three consumers; IrNode mirrors EXPR_t | ✅ |
| **M-NET-INTERP-A01a** | **Lexer** — `Snobol4Lexer.cs` tokenizes `.sno`; token stream mirrors `lex.c` on 19 test cases | 19/19 token stream tests pass |
| **M-NET-INTERP-A01b** | **Parser** — Pidgin combinators consume token stream → `IrStmt[]`; `IrNode.cs` mirrors `ir.h` `EKind`/`EXPR_t`/`STMT_t` | 19/19 parse tests pass |
| **M-NET-INTERP-A01c** | **IR verified** — `IrNode`/`IrStmt` shape confirmed vs `ir.h`; `Ast.cs` removed; build clean; hello/empty_string/multi pass | 3/3 smoke ✅ (D-167 scaffold needs IrNode.cs revision) |
| **M-NET-INTERP-A02** | **Stack machine** — Phases 1/4/5: assignments, OUTPUT, gotos, labels, END, arithmetic via explicit value stack on `IrKind` | rung1 20/20 |
| **M-NET-INTERP-A03** | **Byrd box sequencer** — Phase 2/3: PatternBuilder on `IrKind` → `IByrdBox`; ByrdBoxExecutor trampoline; LIT ANY SPAN ARB ARBNO wired | rung2–5 60/60 |
| **M-NET-INTERP-A04** | Full corpus vs SPITBOL | ≥ 130/142 |
| **M-NET-INTERP-A05** | All failures closed | 142/142 |
| **M-NET-INTERP-B01** | Captures @var/.var/$var correct by construction | rung9 100% |
| **M-NET-INTERP-B02** | DEFINE/RETURN/NRETURN/FRETURN call stack | rung10 pass |
| **M-NET-INTERP-B03** | EVAL/CODE: Pidgin called at runtime → live IrNode tree | 1016_eval pass |

---

## D-168 first tasks — target M-NET-INTERP-A01a (Lexer)

1. `git pull --rebase` all repos.
2. `export PATH=/usr/local/dotnet8:$PATH` (NOT dotnet10 — not installed).
3. Confirm build: `dotnet build src/driver/dotnet/scrip-interp.csproj`.
4. **Write `Snobol4Lexer.cs`** — tokenizes `.sno` source; token stream mirrors `lex.c`.
   Token kinds: `LABEL`, `IDENT`, `QLIT`, `ILIT`, `FLIT`, `OP`, `LPAREN`, `RPAREN`,
   `COMMA`, `COLON`, `GOTO_S`, `GOTO_F`, `GOTO_U`, `CONTINUATION`, `END`, `EOF`.
5. **Wire lexer into `Snobol4Parser.cs`** — replace any ad-hoc splitting with lexer token stream.
6. **Replace `Ast.cs` with `IrNode.cs`** — `IrKind` enum (mirrors `EKind`), `IrNode`
   (Kind/SVal/IVal/DVal/Children), `IrStmt` (mirrors `STMT_t`). Remove `Ast.cs`.
7. **Update `Snobol4Parser.cs`** — emit `IrNode`/`IrStmt` from token stream.
8. **Update `PatternBuilder.cs` and `Executor.cs`** — dispatch on `IrKind`.
9. Build clean. Run `hello`/`empty_string`/`multi` → 3/3 (A01c gate).
10. Run 19 parse tests → A01b gate.
11. Commit + push one4all. Update SESSIONS_ARCHIVE + push .github.
9. Run full crosscheck corpus → establish D-168 broad baseline.
10. Commit + push one4all. Update SESSIONS_ARCHIVE + push .github.

---

*MILESTONE-NET-INTERP.md — revised D-167, 2026-04-03, Claude Sonnet 4.6.*
*D-168 task: replace bespoke Ast.cs with IrNode.cs mirroring ir.h EKind/EXPR_t/STMT_t.*

---

## Execution model (D-167 addendum 2 — stack machine + Byrd box sequencer)

**The interpreter is a stack machine that directly maps to generated code.**

This is not a tree-walk eval loop. It is:

```
IrStmt[]
  → for each stmt: 5-phase executor
      Phase 1: stack machine evaluates subject IrNode subtree → SnobolValue (push/pop)
      Phase 2: PatternBuilder walks pattern IrNode subtree → IByrdBox graph (in memory)
      Phase 3: ByrdBoxExecutor — Byrd box sequencer/trampoline (α/β/γ/ω ports)
      Phase 4: stack machine evaluates replacement IrNode subtree → SnobolValue
      Phase 5: splice, commit captures, :S/:F branch
```

### Stack machine (Phases 1 and 4)

Expression evaluation uses an explicit **value stack**, not recursive C# calls.
Each `IrKind` maps to a stack operation:

| IrKind | Stack operation |
|--------|----------------|
| `E_QLIT` / `E_ILIT` / `E_FLIT` / `E_NUL` | PUSH literal |
| `E_VAR` | PUSH env.Get(sval) |
| `E_KEYWORD` | PUSH env.GetKeyword(sval) |
| `E_ADD` / `E_SUB` / `E_MUL` / `E_DIV` / `E_POW` | POP two, PUSH result |
| `E_MNS` / `E_PLS` | POP one, PUSH result |
| `E_CAT` (n-ary) | POP n, PUSH concatenated string |
| `E_FNC` (n-ary) | POP n args, PUSH return value |
| `E_IDX` | POP base + indices, PUSH element |
| `E_INDIRECT` | POP name-string, PUSH env.Get(name) |
| `E_ASSIGN` | POP value + lvalue-name, SET env, PUSH value |

**Why stack machine:** the same IrNode tree that the interpreter walks to push/pop
is what `emit_net.c` / `emit_x64.c` compile to IL / NASM. The interpreter's stack
operations are a 1-to-1 preview of the emitted instruction sequence. When Phase S
(static compile) is added, the emitter walks the same IrNode tree and emits
the same operations as native instructions. No semantic gap between interpreted
and compiled execution.

### Byrd box sequencer (Phase 3)

`PatternBuilder` walks the pattern `IrNode` subtree and constructs an `IByrdBox`
graph in memory — one box per pattern primitive IrKind:

| IrKind | Box |
|--------|-----|
| `E_QLIT` (in pattern ctx) | `BbLit` |
| `E_SEQ` | `BbSeq` (right-fold) |
| `E_ALT` | `BbAlt` |
| `E_ANY` | `BbAny` |
| `E_SPAN` | `BbSpan` |
| `E_ARB` | `BbArb` |
| `E_ARBNO` | `BbArbno` |
| `E_LEN` | `BbLen` |
| `E_POS` / `E_RPOS` | `BbPos` / `BbRpos` |
| `E_TAB` / `E_RTAB` | `BbTab` / `BbRtab` |
| `E_REM` | `BbRem` |
| `E_FAIL` / `E_SUCCEED` / `E_FENCE` / `E_ABORT` | corresponding boxes |
| `E_BAL` | `BbBal` |
| `E_BREAK` / `E_BREAKX` | `BbBrk` / `BbBreakx` |
| `E_NOTANY` | `BbNotany` |
| `E_CAPT_COND_ASGN` | `BbCapture(immediate:false)` |
| `E_CAPT_IMMED_ASGN` | `BbCapture(immediate:true)` |
| `E_CAPT_CURSOR` | `BbAtp` |
| `E_DEFER` | `BbDvar` |
| `E_VAR` (in pattern ctx) | resolve → BbLit(value) or BbDvar |

`ByrdBoxExecutor.Run()` is the sequencer: it drives α/β/γ/ω ports across
the box graph, advancing the cursor. This is exactly what the static emitter
generates as inline NASM/IL Byrd box trampolines — the interpreter runs the
same sequencing logic interpreted rather than compiled.

### Consequence for IrNode.cs

`IrNode` needs a **context flag** (or the executor infers from position):
`E_VAR` in subject position → stack-machine lookup;
`E_VAR` in pattern position → PatternBuilder resolves to box.
`E_QLIT` in subject/repl position → string value;
`E_QLIT` in pattern position → `BbLit`.
The executor passes context (`SubjectCtx` / `PatternCtx` / `ReplCtx`) when
dispatching, not a flag on the node — mirrors how `emit_net.c` uses emission
context rather than node mutation.

---

*Stack machine + Byrd box sequencer section added D-167 session, 2026-04-03, Claude Sonnet 4.6.*
*Lon Jones Cherryholmes: "interpreter is a stack machine and Byrd box sequencer/interpreter — maps directly to generated code later."*
