# BACKEND-WASM.md — WebAssembly Backend Reference (one4all)

Pure reference. No session state here.
**Session state** → SESSION-*-wasm.md (not yet created — add when M-G6 begins)
**Emitter** → `one4all/src/backend/wasm/emit_wasm.c` (scaffold; full impl Phase 6)

---

## What WASM Is

WebAssembly (WASM) is a binary instruction format for a stack-based virtual machine,
designed to run in browsers at near-native speed. The human-readable form is `.wat`
(WebAssembly Text format). The compiler chain:

```
scrip-cc → .wat → wat2wasm → .wasm → browser / Node.js / WASI runtime
```

WASM is the **4th active backend** in one4all. Goal: one4all running in the browser —
all six frontends compiling SNOBOL4, Icon, Prolog, Snocone, Rebus, and Scrip programs
to `.wasm` that executes in a standard browser tab.

---

## Why WASM, Not JavaScript/TypeScript

| | WASM | JS/TS |
|--|------|-------|
| Arbitrary labels/goto | ❌ (structured only) | ❌ (loop labels only) |
| Byrd-box port encoding | ✅ via tail-call functions | ✅ via trampoline, but JIT-opaque |
| Linear memory control | ✅ (required for runtime) | ❌ (GC heap only) |
| Near-native speed | ✅ | ❌ (JIT, non-deterministic) |
| Browser-native | ✅ | ✅ (but TS needs transpile) |
| Typed binary | ✅ | ❌ |

JS/TS has no general `goto` — `label: continue` applies only to loops. The Byrd-box
α/β/γ/ω port model cannot be encoded as flat labels in either language. WASM with
tail calls encodes it correctly and efficiently.

---

## Control Flow Model: Structured, Not Flat-Label

**x64, JVM (Jasmin), .NET (ilasm)** — all support arbitrary labels + goto/jmp/branch:
```
α_label:  mov rax, ...
          jmp γ_label
β_label:  jmp ...
```

**WASM** — structured only. No arbitrary labels, no goto:
```wat
(block $β
  (block $α
    ;; body — br $β to "fail", fall through to "succeed"
  )
  ;; γ continuation here
)
;; ω continuation here
```

This means the flat-label Byrd-box encoding used by x64/JVM/.NET **cannot be
directly ported** to WASM. Two encoding strategies:

---

## Byrd-Box Encoding Strategy: Tail Calls (Option A — Recommended)

Each Byrd port (α, β, γ, ω) becomes a WASM function. Gotos become tail calls.

```
x64 emits:    jmp α_label
WASM emits:   return_call $node_α
```

The WASM tail-call extension (`return_call` / `return_call_indirect`) is now
standardized (2023) and shipping in all major browsers:
- Chrome 112+ ✅
- Firefox 121+ ✅
- Safari 17+ ✅

`return_call` is zero-overhead — no stack growth, no allocation. This makes
Byrd-box port dispatch as fast as a jump.

**Emitter shape:** `emit_wasm_node(e, γ_fn, ω_fn)` where γ_fn and ω_fn are
function indices (not label strings). Each IR node kind emits a WASM function
with four named sub-functions (or inlined via function table).

---

## Alternative: Block-Nesting Encoding (Option B — Not Recommended)

```wat
(block $ω
  (block $γ
    (block $β
      (block $α
        ;; ... br $β to fail, br $γ to succeed
      )
    )
  )
)
```

`br N` to depth N reaches the right port. Mechanically correct but:
- Produces deeply nested, unreadable `.wat`
- Depth limit (typically 100k) is not a practical problem but the structure is opaque
- Harder to debug and audit against x64 reference

Use Option A (tail calls). Reserve Option B only if tail-call support is unavailable
in the target environment (e.g., WASI runtimes without tail-call extension).

---

## Output Macros (Naming Law)

```c
#define W(fmt, ...)   fprintf(wasm_out, fmt, ##__VA_ARGS__)   /* raw output */
#define WI(op, arg)   fprintf(wasm_out, "    %s %s\n", op, arg)  /* instruction */
#define WL(lbl)       fprintf(wasm_out, "  %s:\n", lbl)          /* label (for Option B) */
```

For Option A (tail-call), `WL` is unused. Instead:
```c
#define WFN(name)     fprintf(wasm_out, "(func $%s\n", name)  /* function definition */
#define WTAIL(name)   fprintf(wasm_out, "  return_call $%s\n", name)  /* tail call */
```

Mirrors: `E()`/`EI()` (x64) · `J()`/`JI()` (JVM) · `N()`/`NI()` (.NET) · `W()`/`WI()` (WASM)

---

## Runtime: Linear Memory Layout

The SNOBOL4 runtime (strings, descriptors, TABLE, ARRAY) lives in WASM linear memory.
x64 uses the C heap + custom allocator. WASM must replicate the descriptor model
in `(memory N)` pages.

Reference: `src/runtime/asm/` for the x64 runtime layout. WASM runtime goes in
`src/runtime/wasm/` (currently empty — Phase 6 work).

**Emscripten path (alternative):** Compile `src/runtime/asm/*.c` via Emscripten
to produce a WASM runtime blob. The `emit_wasm.c` emitter then targets the
Emscripten ABI. Lower risk, less control. Evaluate vs hand-written runtime in Phase 6.

---

## Invariant / Test Gate

Current gate (scaffold phase): **builds clean** — `scrip-cc` must compile with
`emit_wasm.c` linked, no errors, no linker failures.

Future gate (M-G6-WASM-SNOBOL4): SNOBOL4 frontend → WASM, X/Y corpus tests pass
via `wasmtime` or `node --experimental-wasm-*`.

---

## Relation to Other Backends

| Property | x64 | JVM | .NET | WASM |
|----------|-----|-----|------|------|
| IR switch structure | identical | identical | identical | identical |
| Port encoding | flat labels + jmp | flat labels + goto (Jasmin) | flat labels + br | tail-call functions |
| Output assembler | nasm | jasmin | ilasm | wat2wasm |
| Runtime | asm/*.c | runtime/jvm/ | runtime/net/ | runtime/wasm/ (TBD) |
| % parallel to x64 | — | ~70% | ~65% | ~60-70% est. |

The switch-on-EKind emitter structure is **identical** across all four backends.
The Byrd-box wiring logic differs only in output syntax. After the reorg, all four
emitters will share `ir_emit_common.c` helpers for n-ary fold and SEQ wiring.

---

## 5×4 Parallel Development (Post-Reorg)

Post M-G7-UNFREEZE, Lon's plan: 5 parallel frontend sessions each covering all
4 backends. WASM backend participation per session:

| Session | WASM milestone |
|---------|----------------|
| SN (SNOBOL4) | M-SN-WASM-1: basic statement compilation |
| ICN (Icon) | M-ICN-WASM-1: expression evaluation |
| PL (Prolog) | M-PL-WASM-1: clause/choice-point encoding |
| SCN (Snocone) | M-SCN-WASM-1: lowered form emission |
| RB (Rebus) | M-RB-WASM-1: AST → WASM |

All sessions share `emit_wasm.c` — coordinate via PR review when adding EKind cases.
Gate: `ir.h` is the single point of truth for node kinds; new kinds require PR to main.

---

*BACKEND-WASM.md — created G-8 s7, 2026-03-29, Claude Sonnet 4.6.*
*No session state. Reference only. Full impl → Phase 6 milestones.*
