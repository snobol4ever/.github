# GOAL-TEMPLATES-NET.md — .NET backend, all languages

**Repo:** one4all + .github
**Backend:** .NET — MSIL (`.il`) → `ilasm` → CLR (`dotnet`). Mode: `--compile --target=msil`.
**Read first:** `ARCH-NET.md` · `ARCH-EMITTER.md` · `ARCH-IR.md` · `RULES.md`

---

## Premise

The six frontends lower to the shared SM/BB IR. This backend supplies the .NET arm
(`IS_NET` in the unified `emit_core.c` templates) for every SM opcode and BB box-kind, so
that **every language runs on the CLR**. Byrd boxes emit as MSIL classes (`bb_*.il` →
`boxes.dll` via `ilasm`); labels and gotos at emit time, no interpreter loop at runtime.

⚠️ **Distinct from the snobol4dotnet repo.** This goal covers the **one4all** MSIL emitter
arms only. Jeffrey Cooper's standalone C# runtime lives in the separate `snobol4dotnet`
repo and is tracked by its own `GOAL-NET-*` files — do not fold those in here. The
snobol4dotnet runtime serves as a semantic oracle/reference (see ARCH-NET.md); the
`bb_*.cs` files are oracle-only and never referenced by the interpreter build.

## Done when

Every SM opcode and BB box-kind reachable from any of the six frontends has a non-stub
.NET template arm, and each language's corpus assembles via `ilasm` and runs on `dotnet`
producing output matching the x86/oracle reference.

## All-languages coverage

| Language | .NET emit status |
|---|---|
| SNOBOL4 | original target: beauty.sno byte-identical to SPITBOL oracle |
| Snocone | extend in-tree .NET host (code in `src/driver/net/`) |
| Icon | shares the IR; arms follow x86 frontend |
| Prolog | shares the IR; arms follow x86 frontend |
| Raku | shares the IR; arms follow x86 frontend |
| Rebus | shares the IR; arms follow x86 frontend |

## Backend-specific notes (detail in ARCH-NET.md)

- One class per box implementing `IByrdBox` with `Alpha(MatchState)` / `Beta(MatchState)`; `Spec` value type with `Of(start,len)` / `Fail`; ζ in instance fields, CLR GC-reclaimed.
- Label naming `LEN_A_FAIL` (UPPERCASE_PORT); three-column form preserved structurally.
- Build: `dotnet-sdk-10.0`, always `-p:EnableWindowsTargeting=true`. `scrip.csproj` references `boxes.dll` directly (NOT `bb_boxes.csproj`).
- Per RULES.md: zero C Byrd boxes; no AST walking in modes 2/3/4; byte production only inside templates.
