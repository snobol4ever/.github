> ⚠️ **ANNEX ONLY** — D-168+ unified chain. Canonical doc is `MILESTONE-NET-SNOBOL4.md`.
> This file covers `scrip-interp.cs` pipeline design and implementation notes.

# MILESTONE-NET-INTERP — scrip-interp.cs: SNOBOL4 .NET Interpreter

**Session prefix:** D · **Repo:** one4all · **Frontend:** Pidgin → IR · **Backend:** C# Byrd boxes

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

## What already exists — DO NOT REWRITE

| Component | Location | Status |
|-----------|----------|--------|
| All 27 C# Byrd boxes | `src/runtime/boxes/*/bb_*.cs` | ✅ |
| `ByrdBoxExecutor` (Phase 3) | `src/runtime/boxes/shared/bb_executor.cs` | ✅ |
| `IByrdBox`, `Spec`, `MatchState` | `src/runtime/boxes/shared/bb_box.cs` | ✅ |
| `BbCapture`, `BbAtp`, `BbDvar` | `src/runtime/boxes/capture,atp,dvar/` | ✅ |
| `DESCR.cs`, `ByrdBoxLinkage.cs` | `src/runtime/net/` | ✅ |

`ByrdBoxFactory.cs` bridges Jeff's snobol4dotnet `Pattern` hierarchy — **not used**
by the interpreter. `PatternBuilder.cs` walks IR nodes instead (same logic, different input).

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

## Milestone chain (revised)

| Milestone | Description | Gate |
|-----------|-------------|------|
| **M-NET-INTERP-A00** | IR design: one IR / three consumers; IrNode mirrors EXPR_t | ✅ |
| **M-NET-INTERP-A01** | `IrNode.cs` + Pidgin parser → `IrStmt[]`; build clean; hello/multi/empty_string pass | 3/3 smoke pass ✅ D-167 scaffold (needs IrNode.cs revision) |
| **M-NET-INTERP-A02** | Full rung1: assignments, OUTPUT, gotos, labels, END, arithmetic | rung1 20/20 |
| **M-NET-INTERP-A03** | Phase 2/3: PatternBuilder on IrKind → IByrdBox; LIT ANY SPAN ARB ARBNO wired | rung2–5 60/60 |
| **M-NET-INTERP-A04** | Full corpus vs SPITBOL | ≥ 130/142 |
| **M-NET-INTERP-A05** | All failures closed | 142/142 |
| **M-NET-INTERP-B01** | Captures @var/.var/$var correct by construction | rung9 100% |
| **M-NET-INTERP-B02** | DEFINE/RETURN/NRETURN/FRETURN call stack | rung10 pass |
| **M-NET-INTERP-B03** | EVAL/CODE: Pidgin called at runtime → live IrNode tree | 1016_eval pass |

---

## D-168 first tasks

1. `git pull --rebase` all repos.
2. `export PATH=/usr/local/dotnet8:$PATH` (NOT dotnet10 — not installed).
3. **Replace `Ast.cs` with `IrNode.cs`** — `IrKind` enum (mirrors `EKind` subset for SNOBOL4),
   `IrNode` class (Kind/SVal/IVal/DVal/Children), `IrStmt` class (mirrors `STMT_t`).
4. **Update `Snobol4Parser.cs`** — emit `IrNode`/`IrStmt` instead of bespoke records.
   Pidgin combinator structure is otherwise fine; just change the output types.
5. **Update `PatternBuilder.cs`** — switch dispatch from bespoke records to `IrKind`.
6. **Update `Executor.cs`** — switch dispatch from bespoke records to `IrKind`.
7. Build clean. Run `hello`/`empty_string`/`multi` → 3/3.
8. Fix arithmetic: parser must emit `E_ADD`/`E_MUL` etc. IR nodes (not `FncCall("+",...)`).
   Executor dispatches on `IrKind.E_ADD` etc. directly.
9. Run full crosscheck corpus → establish D-168 broad baseline.
10. Commit + push one4all. Update SESSIONS_ARCHIVE + push .github.

---

*MILESTONE-NET-INTERP.md — revised D-167, 2026-04-03, Claude Sonnet 4.6.*
*D-168 task: replace bespoke Ast.cs with IrNode.cs mirroring ir.h EKind/EXPR_t/STMT_t.*
