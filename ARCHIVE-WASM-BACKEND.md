# ARCHIVE-WASM-BACKEND.md — WebAssembly Backend Reference (one4all) ⛔ INACTIVE — parked 2026-03-31

Pure reference. No session state here.
**Session state** → `SESSION-snobol4-wasm.md`
**Emitter** → `one4all/src/backend/emit_wasm.c` (scaffold M-G2; full impl SW-1+)

---

## What WASM Is

WebAssembly (WASM) is a binary instruction format for a stack-based virtual machine,
designed to run in browsers at near-native speed. The human-readable form is `.wat`
(WebAssembly Text format). The compiler chain:

```
scrip-cc -wasm prog.sno  →  prog.wat  →  wat2wasm  →  prog.wasm  →  node / browser / wasmtime
```

WASM is the **4th active backend** in one4all. Goal: one4all running in the browser —
all six frontends compiling SNOBOL4, Icon, Prolog, Snocone, Rebus, and Scrip programs
to `.wasm` that executes in a standard browser tab.

---

## Toolchain (confirmed SW-1, 2026-03-30)

| Tool | Install | Version tested | Purpose |
|------|---------|----------------|---------|
| `wat2wasm` | `apt-get install -y wabt` | 1.0.34 | Assemble `.wat` → `.wasm` |
| `node` | pre-installed (Ubuntu 24) | v22.22.0 | Execute `.wasm` via V8 |
| `wat2wasm` flag | `--enable-tail-call` | required | Enable `return_call` instruction |

**Tail calls confirmed working:** Node v22 + V8 supports `return_call` natively.
No `--experimental` flag required. Chrome 112+, Firefox 121+, Safari 17+ also supported.

**Node runner shim** (`test/wasm/run_wasm.js`):
```js
const fs = require('fs');
const bytes = fs.readFileSync(process.argv[2]);
WebAssembly.instantiate(bytes).then(r => {
  const { main, memory } = r.instance.exports;
  const len = main();
  process.stdout.write(Buffer.from(new Uint8Array(memory.buffer, 0, len)));
});
```

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

## Control Flow Model: Tail Calls, Not Flat Labels

**x64, JVM (Jasmin), .NET (ilasm)** — all support arbitrary labels + goto/jmp/branch:
```nasm
α_label:  mov rax, ...
          jmp γ_label
β_label:  jmp ...
```

**WASM** — structured only; no arbitrary goto. Each Byrd port becomes a WAT function.
Gotos become `return_call` (zero-overhead tail call — no stack growth):

```wat
(func $node_α (param $cursor i32) (result i32)
  ;; ... match logic ...
  return_call $continuation_γ)   ;; succeed → caller's γ

(func $node_β (result i32)
  return_call $caller_β)         ;; fail → propagate up
```

**The `byrd_box.py` `genc()` function is the structural oracle** for `emit_wasm.c`.
Same IR EKind switch, same α/β/γ/ω four-port wiring, same logic — `.wat` output instead of C goto.

---

## Byrd-Box → WAT Encoding (per EKind)

### E_QLIT (literal string match in pattern context)
```wat
(func $lit_123_α (param $cur i32) (result i32)
  ;; repe-cmpsb equivalent: compare subject[cur..cur+len] against literal
  (if (call $sno_lit_match (local.get $cur) (i32.const LIT_OFFSET) (i32.const LIT_LEN))
    (then return_call $continuation_γ))   ;; match: advance cursor, tail-call γ
  return_call $caller_β)                  ;; no match: tail-call β

(func $lit_123_β (result i32)    ;; no backtrack for LIT
  return_call $caller_β)
```

### E_SEQ (goal-directed sequence)
Wiring: `seq_α → left_α` ; `left_γ → right_α` ; `right_β → left_β` ; `right_γ → seq_γ`

### E_ALT (alternation)
Wiring: `alt_α → left_α` ; `left_β → right_α` ; `right_β → alt_β`

### E_ARBNO (zero-or-more)
Wiring: cursor saved before each attempt; zero-advance guard prevents infinite loop.

---

## Runtime: Linear Memory Layout

```
offset 0      : output buffer (up to 64KB)
offset 65536  : variable storage (name→value table, 16KB)
offset 81920  : string heap (growing upward, 128KB)
offset 212992 : array/table heap (growing upward, 64KB)
offset 262144 : end of default 4-page (256KB) allocation
```

Variables stored as length-prefixed UTF-8 strings in the string heap.
Variable table: linear scan (acceptable for programs with <100 variables).
`sno_array_get` returns 0 (null) for uninitialized slots; callers must coerce 0 → "" before string ops.

---

## Output Macros (Naming Law)

```c
#define W(fmt, ...)   fprintf(wasm_out, fmt, ##__VA_ARGS__)   /* raw output */
#define WFN(name)     fprintf(wasm_out, "(func $%s\n", name)  /* function def */
#define WTAIL(name)   fprintf(wasm_out, "  return_call $%s\n", name) /* tail call */
#define WEND()        fprintf(wasm_out, ")\n")                /* close paren */
```

Mirrors: `E()`/`EI()` (x64) · `J()`/`JI()` (JVM) · `N()`/`NI()` (.NET) · `W()`/`WFN()`/`WTAIL()` (WASM)

---

## Corpus Artifacts

`.wat` files sit flat alongside `.s` / `.j` / `.il` — same directory, same stem, one extra extension:

```
corpus/crosscheck/rung4/410_arith_int.sno   ← source (unchanged)
corpus/crosscheck/rung4/410_arith_int.ref   ← oracle (unchanged)
corpus/crosscheck/rung4/410_arith_int.s     ← x64 artifact (unchanged)
corpus/crosscheck/rung4/410_arith_int.j     ← JVM artifact (unchanged)
corpus/crosscheck/rung4/410_arith_int.il    ← .NET artifact (unchanged)
corpus/crosscheck/rung4/410_arith_int.wat   ← WASM artifact (added SW sessions)
```

New pattern-test rungs (`rungW01`–`rungW07`) follow identical flat layout:
```
corpus/crosscheck/rungW01/W01_pat_lit_basic.sno
corpus/crosscheck/rungW01/W01_pat_lit_basic.ref
corpus/crosscheck/rungW01/W01_pat_lit_basic.s
corpus/crosscheck/rungW01/W01_pat_lit_basic.j
corpus/crosscheck/rungW01/W01_pat_lit_basic.il
corpus/crosscheck/rungW01/W01_pat_lit_basic.wat
```

The `rungW0N` prefix avoids collision with existing numeric rungs 2–11.
All four artifacts (`.s` `.j` `.il` `.wat`) are regenerated together via `run_emit_check.sh --update`.

---

## Invariant / Test Gate

| Phase | Gate |
|-------|------|
| Scaffold (M-G2) | builds clean — `scrip-cc` compiles with `emit_wasm.c` linked |
| M-SW-A01 | `snobol4_wasm` cell: 3/3 ✅ |
| M-SW-PARITY | `snobol4_wasm` cell: 106/106 ✅ |

`run_invariants.sh snobol4_wasm` — added when M-SW-A01 fires.
No WASM invariants during scaffold phase; emit-diff gate (738/0) is sufficient.

---

## Relation to Other Backends

| Property | x64 | JVM | .NET | WASM |
|----------|-----|-----|------|------|
| IR switch structure | identical | identical | identical | identical |
| Port encoding | flat labels + jmp | flat labels + goto (Jasmin) | flat labels + br | `return_call` tail-call functions |
| Output assembler | nasm | jasmin.jar | ilasm | wat2wasm |
| Runner | native binary | `java ClassName` | `mono prog.exe` | `node run_wasm.js prog.wasm` |
| Runtime | asm/*.c | runtime/jvm/ | runtime/net/ | runtime/wasm/ (SW-1+) |
| % structural parallel to x64 | — | ~70% | ~65% | ~65% |

The switch-on-EKind emitter structure is **identical** across all four backends.
The Byrd-box wiring logic differs only in output syntax.

---

*BACKEND-WASM.md — updated SW-1, 2026-03-30, Claude Sonnet 4.6.*
*Toolchain confirmed: wabt 1.0.34, node v22.22.0, return_call verified working.*
