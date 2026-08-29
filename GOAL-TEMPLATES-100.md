# GOAL-TEMPLATES-100.md — the four planned backend ports (JVM, .NET, JS, WASM), all languages

## ⛔⛔⛔⭐⭐⭐ FACT RULE — NO NEW GLOBAL VARIABLES WITHOUT LON'S EXPLICIT PERMISSION (Lon 2026-08-13, in-chat) ⛔⛔⛔

**██ NO SESSION CREATES ANY NEW GLOBAL VARIABLE — file-scope mutable state, pinned VA slot, exported cell, parallel array, or any equivalent — in ANY repo, for ANY reason, without FIRST obtaining Lon's explicit in-chat permission in that same session. Linkage and state ride registers (r10/r11 wires) and the stack. We do not do that here. ██**
**ENFORCEMENT: every diff is checked for new file-scope definitions; a commit adding one without a cited in-chat grant in its message is REJECTED on sight. Precedent: the g_pcall / g_pcall_wires / RT_AB_ANCHOR eradication (s55) — that entire class is what this rule forbids recreating.**
**⛔ THE ASK ITSELF MUST BE A BANNER: any session requesting this permission MUST display the request in-chat as a large unmissable ⛔ banner — the proposed global's name, type, owning file, purpose, and why registers/the stack cannot carry it — so Lon cannot miss the ask. A quiet or inline ask does not count as asking. (Lon 2026-08-13 s55, in-chat.)**

**Consolidated** 2026-08-29 (seat10, row `goal-files-major-consolidation`) from `GOAL-TEMPLATES-{JS,JVM,NET,WASM}.md` (RETIRED NAMES below) — 4 files, one cluster, no content lost. **LIVING ROADMAP, not dormant era** (Lon 2026-08-28, in-chat to CEO, verbatim in substance: *"the plan is to port to JVM, .NET, JavaScript, and Web Assembly"*) — x86 ships first, these four are PLANNED TARGETS and must never be archived as dead scope. `GOAL-TEMPLATES-X86.md` (the current, shipping backend) is a different kind of file and stays separate — not absorbed here.

**Repo:** SCRIP + .github
**Read first (shared):** `ARCH-ENGINE.md` · `RULES.md`

---

## Shared premise (all four backends)

The six frontends (SNOBOL4, Snocone, Icon, Prolog, Raku, Rebus) lower to the shared SM/BB IR. Each of these four backends supplies its own arm (`IS_JS`/`IS_JVM`/`IS_NET`/`IS_WASM` in the unified `emit_core.c` templates — correctly-named future work: **zero hits in `src/` today**, verified this session, matching RULES.md's own "X86 ONLY FOR NOW" line, which uses these identical four names for the same not-yet-built stubs. There is nothing stale about the names; there is simply nothing built yet.) for every SM opcode and BB box-kind, so that every language eventually runs on that target.

⛔ **PATH VOLATILITY — VERIFY BEFORE TRUSTING (found 2026-08-29, during this consolidation).** The shared top-level directory holding each port's oracle-only interpreter prototype + `jasmin.jar` was renamed **five times in one day**, all Lon in-chat rulings, all 2026-08-29: `src/backends` → `backends` → `interpreters` → `miscellaneous` (plus `miscellaneous/driver`→`miscellaneous/interpreters` and `miscellaneous/runtime`→`miscellaneous/runtimes` sub-renames). **Current, verified-this-session path: `miscellaneous/interpreters/{js,jvm,net,wasm}/`; the jar is at `miscellaneous/jasmin.jar`** (confirmed live in the Makefile's own `JASMIN` var, `Makefile:47`). Root `CLAUDE.md`'s Architecture section still says `backends/` — stale, not this row's file to fix, noted for whoever next touches it. Given the demonstrated one-day churn rate, run `git log --oneline -3 -- miscellaneous/` before trusting even this note.

## JVM — Jasmin assembly → `.class` bytecode → `java`

Mode: `--compile --target=jvm`. Read first: `ARCH-JVM.md`.

The `.class` IS the Byrd-box graph — labels and gotos compiled at emit time, no interpreter loop at runtime. `snobol4jvm` (Clojure, separate repo) remains the separate semantic oracle (1,896 tests baseline); it is not this emitter, but the correctness reference for it.

**Done when:** every SM opcode and BB box-kind reachable from any of the six frontends has a non-stub JVM template arm, and each language's corpus assembles via `jasmin.jar` and runs on `java` producing output matching the x86/oracle reference.

| Language | JVM emit status |
|---|---|
| SNOBOL4 | original target: beauty.sno byte-identical to SPITBOL oracle |
| Snocone | extend in-tree JVM host (oracle prototype at `miscellaneous/interpreters/jvm/`) |
| Icon | shares the IR; arms follow once x86 frontend lands the opcodes |
| Prolog | resumable-predicate pattern (Closure + tableswitch on clause state) — see ARCH-JVM.md |
| Raku | shares the IR; arms follow x86 frontend |
| Rebus | shares the IR; arms follow x86 frontend |

Backend-specific (detail in ARCH-JVM.md): one class per box; α/β public methods; γ/ω = return value (`Spec` or null sentinel); ζ in instance fields, GC-reclaimed. Four-column form preserved; port exits compile to `goto` / `areturn` / `aconst_null + areturn`. Tools: `javac`, `java`, `miscellaneous/jasmin.jar`. Boxes assemble to `bb/*.class`, packaged into `boxes.jar`.

## .NET — MSIL (`.il`) → `ilasm` → CLR (`dotnet`)

Mode: `--compile --target=msil`. Read first: `ARCH-NET.md`.

⚠️ **Distinct from the `snobol4dotnet` repo.** This section covers the **SCRIP** MSIL emitter arms only. Jeffrey Cooper's standalone C# runtime lives in the separate `snobol4dotnet` repo and is tracked by its own `GOAL-NET-*` files (`GOAL-NET-BEAUTY-19.md` / `-SELF.md` / `-OPSYN-248.md` / `-OPTIMIZE.md` / `-SNIPPETS.md` / `-DATATYPE-LOWERCASE.md`) — do NOT fold those in here; they are a separate, still-unresolved cluster per this row's own task-file history. The `snobol4dotnet` runtime serves as a semantic oracle/reference; the oracle-only prototype at `miscellaneous/interpreters/net/` (`Program.cs` / `Snobol4Parser.cs` / `Executor.cs` / `BoxFactory.cs` / `Ast.cs` / `IrNode.cs` / `PatternBuilder.cs` / `SnobolEnv.cs`) is never referenced by the interpreter build.

Byrd boxes emit as MSIL classes (`bb_*.il` → `boxes.dll` via `ilasm`); labels and gotos at emit time, no interpreter loop at runtime.

**Done when:** every SM opcode and BB box-kind reachable from any of the six frontends has a non-stub .NET template arm, and each language's corpus assembles via `ilasm` and runs on `dotnet` producing output matching the x86/oracle reference.

| Language | .NET emit status |
|---|---|
| SNOBOL4 | original target: beauty.sno byte-identical to SPITBOL oracle |
| Snocone | extend in-tree .NET host (oracle prototype at `miscellaneous/interpreters/net/`) |
| Icon | shares the IR; arms follow x86 frontend |
| Prolog | shares the IR; arms follow x86 frontend |
| Raku | shares the IR; arms follow x86 frontend |
| Rebus | shares the IR; arms follow x86 frontend |

Backend-specific (detail in ARCH-NET.md): one class per box implementing `IByrdBox` with `Alpha(MatchState)` / `Beta(MatchState)`; `Spec` value type with `Of(start,len)` / `Fail`; ζ in instance fields, CLR GC-reclaimed. Label naming `LEN_A_FAIL` (UPPERCASE_PORT); four-column form preserved structurally. Build: `dotnet-sdk-10.0`, always `-p:EnableWindowsTargeting=true`. `scrip.csproj` references `boxes.dll` directly (NOT `bb_boxes.csproj`).

## JavaScript → `node`

Mode: `--compile --target=js`. Read first: `ARCH-JS.md`.

Each box is a factory returning an `{α, β}` object; ports are function refs reading/writing shared globals `_Σ`/`_Δ`/`_Ω`. JS is the one backend that supports `EVAL`/`CODE` natively (`new Function(body)` JIT-compiles arbitrary code strings) — static and dynamic pattern paths produce structurally identical execution.

**Done when:** every SM opcode and BB box-kind reachable from any of the six frontends has a non-stub JS template arm, and each language's corpus runs on `node` producing output matching the x86/oracle reference.

| Language | JS emit status |
|---|---|
| SNOBOL4 | **PIVOT (active):** climb the SNOBOL4 test-suite ladder; beauty self-host on hold |
| Snocone | climb the Snocone test-suite ladder; extend in-tree JS host (oracle prototype at `miscellaneous/interpreters/js/`) |
| Icon | shares the IR; arms follow x86 frontend |
| Prolog | shares the IR; arms follow x86 frontend |
| Raku | shares the IR; arms follow x86 frontend |
| Rebus | shares the IR; arms follow x86 frontend |

Backend-specific (detail in ARCH-JS.md): trampoline model, every statement compiles to a zero-arg function returning the next; `while (pc) pc = pc();` — identical to the C trampoline. ζ is a closure environment (box factory locals captured lexically); GC reclaims on γ/ω. `EVAL`/`CODE` via `new Function()`; runtime types map to native JS (string/number/Map/array/class/Function); OUTPUT via a `_vars` Proxy setter. Tools: `node` (V8).

## WebAssembly — WAT (`.wat`) → `wat2wasm` → `.wasm` → `node` host

Mode: `--compile --target=wasm`. Read first: `ARCH-WASM.md`.

Each box's α/β become exported `func`s; match state `$Σ`/`$Δ`/`$Ω` are imported mutable globals; ζ lives at a host-allocated linear-memory offset passed as `$state`.

**Done when:** every SM opcode and BB box-kind reachable from any of the six frontends has a non-stub WASM template arm, and each language's corpus assembles via `wat2wasm` and runs under the `node` host producing output matching the x86/oracle reference.

| Language | WASM emit status |
|---|---|
| SNOBOL4 | original target: beauty.sno byte-identical to SPITBOL oracle |
| Snocone | shares the IR; arms follow x86 frontend |
| Icon | shares the IR; arms follow x86 frontend |
| Prolog | shares the IR; arms follow x86 frontend |
| Raku | shares the IR; arms follow x86 frontend |
| Rebus | shares the IR; arms follow x86 frontend |

Backend-specific (detail in ARCH-WASM.md): failure sentinel `i32.const -1`; success returns matched length `i32 ≥ 0`. Host reconstructs the span from cursor+length (`spec_t` not carried across the boundary). No in-function `goto` — structured control flow only (`if`/`else`/`block`/`br`); sub-box wiring is one func per port + host-side dispatch (`bb_driver` calls the port fn ptr). `EVAL`/`CODE` limitation: WASM has no `new Function()` equivalent — either bootstrap a sub-compiler (large) or fall back to a JS host for those ops (small). Strategy decision is the open architectural question. Tools: `wabt` (`apt-get install -y wabt`), `wat2wasm`, `node`.

## RETIRED NAMES

| Old file | Where its content lives now |
|---|---|
| `GOAL-TEMPLATES-JS.md` | § JavaScript, above |
| `GOAL-TEMPLATES-JVM.md` | § JVM, above |
| `GOAL-TEMPLATES-NET.md` | § .NET, above |
| `GOAL-TEMPLATES-WASM.md` | § WebAssembly, above |

`GOAL-TEMPLATES-X86.md` is **NOT** retired here — it describes the current, shipping backend (not a planned port) and stays a standalone file; its own citation of dead `GOAL-{SNOBOL4,ICON,PROLOG}-BB.md` names is a separate, pre-existing staleness issue this consolidation does not touch.
