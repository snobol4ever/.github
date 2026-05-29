# GOAL-TEMPLATES-JS.md — JavaScript backend, all languages

**Repo:** one4all + .github
**Backend:** JavaScript → `node`. Mode: `--compile --target=js`.
**Read first:** `ARCH-JS.md` · `ARCH-EMITTER.md` · `ARCH-IR.md` · `RULES.md`

---

## Premise

The six frontends lower to the shared SM/BB IR. This backend supplies the JS arm
(`IS_JS` in the unified `emit_core.c` templates) for every SM opcode and BB box-kind, so
that **every language runs on node**. Each box is a factory returning an `{α, β}` object;
ports are function refs reading/writing shared globals `_Σ`/`_Δ`/`_Ω`.

JS is the one backend that supports `EVAL`/`CODE` natively (`new Function(body)` JIT-
compiles arbitrary code strings) — static and dynamic pattern paths produce structurally
identical execution.

## Done when

Every SM opcode and BB box-kind reachable from any of the six frontends has a non-stub
JS template arm, and each language's corpus runs on `node` producing output matching the
x86/oracle reference.

## All-languages coverage

| Language | JS emit status |
|---|---|
| SNOBOL4 | **PIVOT (active):** climb the SNOBOL4 test-suite ladder; beauty self-host on hold |
| Snocone | climb the Snocone test-suite ladder; extend in-tree JS host (code in `src/driver/js/`) |
| Icon | shares the IR; arms follow x86 frontend |
| Prolog | shares the IR; arms follow x86 frontend |
| Raku | shares the IR; arms follow x86 frontend |
| Rebus | shares the IR; arms follow x86 frontend |

## Backend-specific notes (detail in ARCH-JS.md)

- Trampoline model: every statement compiles to a zero-arg function returning the next; `while (pc) pc = pc();` — identical to the C trampoline.
- ζ is a closure environment (box factory locals captured lexically); GC reclaims on γ/ω.
- `EVAL`/`CODE` via `new Function()`; runtime types map to native JS (string/number/Map/array/class/Function); OUTPUT via a `_vars` Proxy setter.
- Tools: `node` (V8). Per RULES.md: zero C Byrd boxes; no AST walking in modes 2/3/4; byte/text production only inside templates.
