# ARCH-NET.md — .NET Backend

Backend: .NET (MSIL → CLR).
Emitter: unified `emit_core.c` (`IS_NET` arms in `SM_templates/` + `BB_templates/`); MSIL boxes assemble to `boxes.dll` via `ilasm`.
Two related implementations to keep distinct:
- `SCRIP/src/driver/scrip.cs` — tree-walk interpreter (SCRIP)
- `snobol4dotnet` — Jeffrey Cooper's full C# runtime (separate repo; semantic oracle, tracked by its own GOAL-NET-* files)

## snobol4dotnet model

5-phase executor in `ThreadedExecuteLoop.cs`.
Phase 3 (match): `Scanner.cs` `Match()` trampoline drives pattern node graph.
Byrd boxes: `AbstractSyntaxTreeNode.cs` — Subsequent/Alternate = γ/β ports.
JIT: `BuilderEmitMsil.cs` `DynamicMethod` compiles token lists to IL delegates.

Compiler pipeline: Lexer → Parser → threaded `Instruction[]` → MSIL
delegate JIT.  Plugin system: C-ABI `.so` extensions, .NET assembly
extensions, VB.NET fixtures.

**Key classes:**
```
Snobol4.Common/
  Builder/
    Builder.cs                  full compile pipeline (parse → emit)
    BuilderEmitMsil.cs          MSIL delegate JIT — hot path code generation
    Lexer.cs / Parser.cs        SNOBOL4 source → AST
    Token.cs / DeferredExpression.cs / ConstantPool.cs
  Runtime/Execution/
    Executive.cs                partial class root — all runtime state
    ThreadedExecuteLoop.cs      main dispatch loop (fast path + full switch)
    StatementControl.cs         RunExpressionThread(), sub-expression dispatch
    SystemStack.cs              SNOBOL4 semantic stack
    Function.cs                 DEFINE/RETURN/FRETURN/NRETURN
  Runtime/Pattern/              One class per pattern primitive
  Runtime/PatternMatching/
    Scanner.cs                  PatternMatch() outer loop
    AbstractSyntaxTree.cs       Subsequent/Alternate link graph
  Runtime/Variable/
    Var.cs                      base class; subclasses per type
```

`Scanner.PatternMatch()` is an unanchored outer loop over cursor
positions.  For each start position it calls `Match(ast.StartNode)`,
which walks the `AbstractSyntaxTreeNode` graph via `Subsequent`
(concatenation successor) and `Alternate` (backtrack target) links.

## MSIL Byrd boxes (SCRIP interp)

`bb_*.il` assembled into `boxes.dll` via `ilasm`.
`bb_*.cs` are oracle/reference ONLY — never referenced by interpreter build.
`scrip.csproj` references `boxes.dll` directly, NOT `bb_boxes.csproj`.

**One class per box** implementing `IByrdBox` interface with
`Alpha(MatchState ms)` and `Beta(MatchState ms)` methods.  `Spec` is
a value type with `Of(int start, int len)` and `Fail` static.

```msil
.class public auto ansi beforefieldinit Snobol4.Runtime.Boxes.bb_len
       extends [mscorlib]System.Object implements Snobol4.Runtime.Boxes.IByrdBox
{
  .field private int32 _n
  .method public virtual instance valuetype Spec
          Alpha(class MatchState ms) cil managed
  {
    ldarg.1; ldfld Cursor
    ldarg.0; ldfld _n
    add
    ldarg.1; callvirt get_Length()
    bgt        LEN_A_FAIL
    ; ... build Spec, advance cursor, ret ...
  LEN_A_FAIL:
    ldsfld     valuetype Spec Spec::Fail
    ret
  }
}
```

**Label naming:** `LEN_A_FAIL` style (UPPERCASE_PORT format).  Port
exits use `br` / `bgt` / `ldsfld` against the static `Spec.Fail`.

**Three-column form** is preserved structurally: ldarg/ldfld
sequences in column 2 expand the ACTION; `bgt` / `ret` in column 3
carry the GOTO.

**Per-instance state ζ** lives in instance fields; α reads them at
entry, γ/ω discards the instance at return.  CLR's GC reclaims ζ.

## Build

```bash
apt-get install -y dotnet-sdk-10.0
dotnet build Snobol4/Snobol4.csproj -c Release -p:EnableWindowsTargeting=true
```
Always `-p:EnableWindowsTargeting=true`.
