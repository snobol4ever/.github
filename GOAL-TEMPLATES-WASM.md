# GOAL-TEMPLATES-WASM.md — WebAssembly backend, all languages

**Repo:** one4all + .github
**Backend:** WebAssembly — WAT (`.wat`) → `wat2wasm` → `.wasm` → `node` host. Mode: `--compile --target=wasm`.
**Read first:** `ARCH-WASM.md` · `ARCH-EMITTER.md` · `ARCH-IR.md` · `RULES.md`

---

## Premise

The six frontends lower to the shared SM/BB IR. This backend supplies the WASM arm
(`IS_WASM` in the unified `emit_core.c` templates) for every SM opcode and BB box-kind, so
that **every language runs on a WASM host**. Each box's α/β become exported `func`s; match
state `$Σ`/`$Δ`/`$Ω` are imported mutable globals; ζ lives at a host-allocated linear-
memory offset passed as `$state`.

## Done when

Every SM opcode and BB box-kind reachable from any of the six frontends has a non-stub
WASM template arm, and each language's corpus assembles via `wat2wasm` and runs under the
`node` host producing output matching the x86/oracle reference.

## All-languages coverage

| Language | WASM emit status |
|---|---|
| SNOBOL4 | original target: beauty.sno byte-identical to SPITBOL oracle |
| Snocone | shares the IR; arms follow x86 frontend |
| Icon | shares the IR; arms follow x86 frontend |
| Prolog | shares the IR; arms follow x86 frontend |
| Raku | shares the IR; arms follow x86 frontend |
| Rebus | shares the IR; arms follow x86 frontend |

## Backend-specific notes (detail in ARCH-WASM.md)

- Failure sentinel `i32.const -1`; success returns matched length `i32 ≥ 0`. Host reconstructs the span from cursor+length (`spec_t` not carried across the boundary).
- No in-function `goto` — structured control flow only (`if`/`else`/`block`/`br`); sub-box wiring is one func per port + host-side dispatch (`bb_driver` calls the port fn ptr).
- `EVAL`/`CODE` limitation: WASM has no `new Function()` equivalent — either bootstrap a sub-compiler (large) or fall back to a JS host for those ops (small). Strategy decision is the open architectural question.
- Tools: `wabt` (`apt-get install -y wabt`), `wat2wasm`, `node`. Per RULES.md: zero C Byrd boxes; no AST walking in modes 2/3/4; production only inside templates.
