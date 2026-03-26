# BACKEND-NET.md — snobol4dotnet Reference

Jeff Cooper's complete SNOBOL4/SPITBOL implementation in C#, targeting .NET/MSIL.
Compiler pipeline: Lexer → Parser → threaded `Instruction[]` → MSIL delegate JIT.
Plugin system: C-ABI `.so` extensions, .NET assembly extensions, VB.NET fixtures.

*Session state → DOTNET.md. Testing protocol → TESTING.md.*

---

## Architecture Overview

The runtime is a **threaded interpreter** driven by `ThreadedExecuteLoop.cs`.
Every SNOBOL4 statement compiles to an `Instruction[]` thread. Execution is a
tight loop dispatching on `OpCode` — or, when the thread is MSIL-only, a fast
path spinning over `Func<Executive,int>[]` delegates with no switch overhead.

**Key classes:**

```
Snobol4.Common/
  Builder/
    Builder.cs                  full compile pipeline (parse → emit)
    BuilderEmitMsil.cs          MSIL delegate JIT — hot path code generation
    Lexer.cs / Parser.cs        SNOBOL4 source → AST
    Token.cs                    Token.Type enum + Token class
    DeferredExpression.cs       lazy evaluation for deferred pattern args
    ConstantPool.cs             interned constant Var objects
  Runtime/Execution/
    Executive.cs                partial class root — all runtime state
    ThreadedExecuteLoop.cs      main dispatch loop (fast path + full switch)
    StatementControl.cs         RunExpressionThread(), sub-expression dispatch
    SystemStack.cs              SNOBOL4 semantic stack (StatementSeparator etc.)
    Function.cs                 DEFINE/RETURN/FRETURN/NRETURN, _reusableArgList
  Runtime/Pattern/              One class per pattern primitive (LiteralPattern,
                                ArbNoPattern, AnyPattern, PosPattern, …)
  Runtime/PatternMatching/
    Scanner.cs                  PatternMatch() outer loop; anchor/unanchored scan
    AbstractSyntaxTree.cs       builds Subsequent/Alternate link graph from Pattern tree
    AbstractSyntaxTreeNode.cs   node: Self, Subsequent, Alternate, LeftChild, RightChild
  Runtime/Variable/
    Var.cs                      base class; subclasses: IntegerVar StringVar RealVar
                                PatternVar ArrayVar TableVar CodeVar NameVar …
    IArithmeticStrategy.cs      strategy interfaces (conversion, comparison, …)
TestSnobol4/
  MsilEmitterTests.cs
  ThreadedCompilerTests.cs
```

---

## Pattern Matching Engine

`Scanner.PatternMatch()` is an **unanchored outer loop** over cursor positions.
For each start position it calls `Match(ast.StartNode)`, which walks the
`AbstractSyntaxTreeNode` graph via `Subsequent` (concatenation successor) and
`Alternate` (backtrack target) links. Each terminal node's `Scan()` method
either advances the cursor and returns SUCCESS, returns FAILURE (triggers
backtrack), or returns ABORT (propagates immediately).

`AbstractSyntaxTree.Build()` converts the `Pattern` tree (left/right children)
into a flat indexed node list, then computes Subsequent and Alternate for each
terminal in a single pass. The result is cached on the `Pattern` object so
repeated matches on the same compiled pattern pay zero rebuild cost.

---

## Extension / Plugin System

| Layer | Mechanism | Status |
|-------|-----------|--------|
| C-ABI `.so` | `LOAD('fname(proto)')` → dlopen + xncbp/xn1st/xndta[] | ✅ M-NET-XN |
| .NET assembly | `LOAD('Assembly.dll:Fn(proto)')` — reflection + IExternalLibrary fast path | ✅ M-NET-LOAD-DOTNET |
| VB.NET fixture | string/long/double returns, null→fail, static, multi-load, UNLOAD | ✅ M-NET-VB |
| XNBLK opaque state | xndta[] private per-entry Dictionary; C-side alloc helpers | ✅ M-NET-EXT-XNBLK |

---

## Open Issues

| # | Issue | Severity |
|---|-------|----------|
| 1 | Pattern.Bal — hangs under threaded execution | Medium |
| 2 | Deferred expressions `pos(*A)` — TEST_Pos_009 | Low |
| 3 | TestGoto _DIRECT — CODE() dynamic compilation | Medium |
| 4 | Function.InputOutput — Linux (hardcoded Windows paths) | Low |
| 5 | `cross` test — `@N` cursor value off by one (105/106) | High |

**CRITICAL build flag:** Always pass `-p:EnableWindowsTargeting=true` on Linux.

---

## SPITBOL Oracle Rule

When CSNOBOL4 and SPITBOL MINIMAL diverge: **SPITBOL MINIMAL wins.**
Key semantics: DATATYPE builtins lowercase; user DATA types `ToLowerInvariant`;
`&UCASE`/`&LCASE` = exactly 26 ASCII letters; `@N` is **0-based** cursor position.

---

## Performance Baseline (session159, post-hotfix A–D)

| Benchmark | Mean | Alloc/run |
|-----------|-----:|----------:|
| ArithLoop_1000 | 39.8ms | 1662 KB |
| VarAccess_2000 | 103.2ms | 6279 KB |
| Fibonacci_18 | 286.6ms | 11855 KB |
| MixedWorkload_200 | 223.2ms | 13928 KB |
| FuncCallOverhead_3000 | 40.6ms | 837 KB |

Full numbers + hotfix analysis → `perf/post_hotfix_session159.md`.
