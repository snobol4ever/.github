# ARCH-WASM.md — WASM Backend

Backend: WebAssembly. Emitter: unified `emit_core.c` (`IS_WASM` arms in `SM_templates/` + `BB_templates/`); the former silo `emit_wasm.c` was deleted in the EC series — see ARCH-EMITTER.md.
Tools: `wabt` (`apt-get install -y wabt`), `wat2wasm`, `node`.

## Byrd Box model

Each box's α and β become exported `func`s with `i32` parameters for
the box's per-instance state.  Match state (`$Σ`, `$Δ`, `$Ω`) is
imported as mutable globals from the host.

```wat
(module
  (memory (import "env" "memory") 1)
  (global $Σ (import "env" "Σ") (mut i32))
  (global $Δ (import "env" "Δ") (mut i32))
  (global $Ω (import "env" "Ω") (mut i32))

  (func $bb_len_a (export "bb_len_a")
        (param $n i32) (param $p1 i32) (param $state i32)
        (result i32)
    (if (i32.gt_u (i32.add (global.get $Δ) (local.get $n)) (global.get $Ω))
      (then (return (i32.const -1))))
    (global.set $Δ (i32.add (global.get $Δ) (local.get $n)))
    (local.get $n))

  (func $bb_len_b (export "bb_len_b")
        (param $n i32) (param $p1 i32) (param $state i32)
        (result i32)
    (global.set $Δ (i32.sub (global.get $Δ) (local.get $n)))
    (i32.const -1))
)
```

## Failure sentinel

`i32.const -1` is the ω sentinel.  Success returns the matched length
as `i32 ≥ 0`.

## Span representation

WASM cannot easily carry the C `spec_t { σ, δ }` struct, so the host
reconstructs the span from cursor + length using `_Σ` (linear memory
or imported string).  Boxes return only the length on γ; the host
recovers the substring after the call.

## Per-instance state ζ

ζ lives at a host-allocated offset in linear memory.  The `$state`
parameter on each box function is the byte offset; the box reads/
writes ζ fields via `i32.load` / `i32.store` at known offsets within
that block.  Lifetime: host allocates ζ on α call, host discards on
γ/ω.

## EVAL / CODE limitation

WASM cannot do EVAL / CODE natively — no `new Function()` equivalent.
Either bootstrap a sub-compiler in WASM (large) or fall back to a JS
host for those ops (small).

## Three-column form on WASM

Three-column structure compiles to:
- LABEL: implicit at function entry (single function per port)
- ACTION: s-expression body
- GOTO: `return` (γ — value), `return (i32.const -1)` (ω), no
  in-function `goto` (WASM has no goto; structured control flow only,
  via `if/else/block/br`).

For sub-box wiring within named patterns, the emitter generates one
function per port and wires them via host-side dispatch (the
`bb_driver` calls the port function pointer rather than `goto`-ing
into it).

## Tools

- `wabt` (`apt-get install -y wabt`)
- `wat2wasm` — assembles `.wat` → `.wasm`
- `node` — host runtime
- `emit_wasm.c` — emitter (one4all)

## Status

Per-box `.wat` files were hand-written under prior work (see Goal
GOAL-SCRIP-BOOTSTRAP for the unified template-based replacement).
WASM cell is the last in PLAN.md's Milestone 3 grid; CB-15 spike
decides emcc-bootstrap vs hand-emit strategy.
