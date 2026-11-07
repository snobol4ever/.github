---
name: scrip-backends
description: SCRIP's backends: x86-64 the one live target; JVM, .NET, JavaScript and WebAssembly as future template sets over the same pipeline (CEO-2114); the 2026-08 prototypes. Load before any backend question; the ports are skill ports.
---

# SCRIP's backends

## 1. The plan of record (Lon 2026-11-01, in the cto's window, verbatim: "The plan for SCRIP's backends is to produce new templates and keep the rest of the entire system except runtime system identical."; CEO-2114)

- **A backend is two things: a template set and a runtime.** The driver, the parsers, lower, the optimizer, the planner and the emitter are shared by every target, unchanged. The IR graph and the plan table are the contract a target's templates read.
- **Consequence for every landing today:** nothing target-shaped may enter the IR, the planner or the emitter. The x86-64 templates (`src/templates/bb/`, `xa/`, `x86/`) and the x86 runtime (`src/runtime/rtx/`, the C runtime's asm-facing half) are the only places that know the machine. A box that decides in the emitter what belongs in a template blocks a second backend.
- **Do not confuse the ports.** snobol4jvm (Clojure) and snobol4dotnet (C#) are separate SNOBOL4 implementations in their own repos, graded as `<suite>@jvm` and `<suite>@dotnet` (skill `ports`). They are neither SCRIP backends nor their oracles.

## 2. Where things stand (checked 2026-11-01 on SCRIP 9cb24d2ca)

- `--target=x86` (or none) is the only target. Any other name refuses rc 1 with "--target=NAME removed (Stack-Machine codegen removed)" (`src/driver/scrip.c`); the usage text still lists jvm, js and wasm, which is stale.
- The 2026-08 emitter scaffolding (`emit_core.c` with `IS_JVM`, `IS_NET`, `IS_JS`, `IS_WASM` arms, `SM_templates/`, `BB_templates/`, `emit_jvm.c`, `emit_js.c`, `emit_wasm.c`) is deleted.
- The prototypes survive under `SCRIP/miscellaneous/` (last touched 2026-08-29): `runtimes/jvm/` (Jasmin `.j` boxes and runtime, `SnoPat.java`), `runtimes/net/` (MSIL `.il` boxes and runtime, `DESCR.cs`, `ByrdBoxLinkage.cs`), `runtimes/js/` (`bb_boxes.js`, `sno_engine.js`, `sno_runtime.js`), `runtimes/wasm/` (`bb_boxes.wat`, the SNOBOL4 and Prolog runtimes, `sno_host.mjs`), tree-walk interpreters under `interpreters/`, and `jasmin.jar`.
- Tool chains on the box: `java`, `javac` and `dotnet` are installed; `ilasm`, `node` and `wat2wasm` are not.
- Dead harness scripts that drive the deleted `scrip -jvm`: `run_snobol4_via_jvm_backend.sh`, `test_icon_jvm_runner.sh`, `test_prolog_jvm_rung.sh`, `test_crosscheck_jvm_rung.sh`, `generate_demo_jvm_artifacts.sh`.

## 3. The recorded box shapes per target (the 2026-07/08 design; it predates the three zetas and the plan table)

- **JVM** (Jasmin assembly to `.class`): one class per box, α and β public methods, γ and ω as return values (a `Spec` object or null); per-instance state ζ in the box's instance fields; internal wiring by `goto` and `if_icmp*` to labels. A Prolog predicate is a class with a `$Closure` holding per-call state and a clause-state field driven by `tableswitch`; backtracking unwinds by the trail.
- **.NET** (MSIL assembled by `ilasm`): one class per box implementing an `IByrdBox` with `Alpha(MatchState)` and `Beta(MatchState)`; `Spec` a value type with `Of(start, len)` and a static `Fail`; ζ in instance fields, reclaimed by the CLR's collector.
- **JavaScript**: a box is a factory returning an `{α, β}` object over shared `_Σ`, `_Δ`, `_Ω`; EVAL and CODE compile through `new Function(...)`; a statement is a zero-argument function returning the next (`while (pc) pc = pc();`); ζ is the factory's closure.
- **WebAssembly** (WAT through `wat2wasm`): α and β are exported functions with i32 state parameters; `i32.const -1` is ω and a non-negative length is γ; the match registers are imported mutable globals; ζ lives at a host-allocated offset in linear memory. WASM has no goto and no run-time code generation: structured control only, and EVAL/CODE needs a JS host or a compiler built into the module.

## 4. What the plan leaves to design (the cto's, when a backend row opens)

How each target realises the three zetas (the JVM and CLR operand stack and locals, a WASM shadow stack in linear memory, JS closures), how its templates read the plan rows the x86 boxes read, how its collector meets the frame-map law, and how mode 3's run-time compilation (EVAL, CODE, `call/N`) works on a target without a sealed slab. No backend row exists today; until one does, the rule of § 1 is the whole of the work: keep the shared stages target-blind.
