# ARCH-NET.md — .NET Backend

Backend: .NET (MSIL → CLR). Two implementations:
- `one4all/src/driver/scrip-interp.cs` — tree-walk interpreter
- `snobol4dotnet` — Jeffrey Cooper's full C# runtime

## snobol4dotnet model

5-phase executor in `ThreadedExecuteLoop.cs`.
Phase 3 (match): `Scanner.cs` `Match()` trampoline drives pattern node graph.
Byrd boxes: `AbstractSyntaxTreeNode.cs` — Subsequent/Alternate = γ/β ports.
JIT: `BuilderEmitMsil.cs` `DynamicMethod` compiles token lists to IL delegates.

## MSIL Byrd boxes (one4all interp)

`bb_*.il` assembled into `boxes.dll` via `ilasm`.
`bb_*.cs` are oracle/reference ONLY — never referenced by interpreter build.
`scrip-interp.csproj` references `boxes.dll` directly, NOT `bb_boxes.csproj`.

## Build

```bash
apt-get install -y dotnet-sdk-10.0
dotnet build Snobol4/Snobol4.csproj -c Release -p:EnableWindowsTargeting=true
```
Always `-p:EnableWindowsTargeting=true`.

*Populate further from archive/INTERP-NET.md + archive/EMITTER-NET.md when a .NET goal is active.*
