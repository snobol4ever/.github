# ARCH-JS.md — JS Backend

Backend: JavaScript. Emitter: unified `emit_core.c` (`IS_JS` arms in `SM_templates/` + `BB_templates/`); the former silo `emit_js.c` was deleted in the EC series — see ARCH-EMITTER.md.

## Why JavaScript

SNOBOL4's `EVAL()` and `CODE()` require runtime code generation. WASM
cannot do this.  JavaScript solves it natively: `new Function(body)`
compiles and runs arbitrary code strings.  Functions are first-class —
Byrd-box ports are just function refs.  Dynamic Byrd boxes: `{α, β}`
objects built at runtime from pattern values.

## Byrd Box model — static and dynamic

Each box is a factory function returning an `{α, β}` object.  α and β
are methods that read/write shared globals `_Σ`, `_Δ`, `_Ω` and return
either a `_spec(start, len)` substring or `_FAIL` (null sentinel).

**Static path (emit_js.c)** — for patterns known at compile time, the
emitter produces hardwired port functions:

```js
function P_N_α() {
    const end = cursor + 5;
    if (subject.slice(cursor, end) === "HELLO") {
        cursor = end; return γ_outer;
    }
    return ω_outer;
}
function P_N_β() { return ω_outer; }
```

**Dynamic path (sno_engine.js)** — for runtime-constructed patterns
(EVAL/CODE, pattern variables), `build_pattern()` walks the pattern
descriptor and constructs a live `{α, β}` graph:

```js
function build_qlit(lit) {
    return {
        α() {
            const end = cursor + lit.length;
            if (subject.slice(cursor, end) === lit) {
                cursor = end; return γ_outer;
            }
            return ω_outer;
        },
        β() { return ω_outer; }
    };
}
```

The static and dynamic paths produce structurally identical execution.

## EVAL / CODE

```js
function sno_eval(str) {
    const js = _scrip_compile_expr(str);
    return new Function('_rt', 'return (' + js + ')')(_runtime);
}
function sno_code(str) {
    const js = _scrip_compile_stmts(str);
    return new Function('_rt', js)(_runtime);
}
```

`new Function()` creates JIT-compiled functions — same performance
as statically emitted code.

## Trampoline model

Every SNOBOL4 statement compiles to a zero-argument function returning
the next function.  Engine:

```js
let pc = block_START;
while (pc) pc = pc();
```

Identical structure to the C trampoline (`block_fn_t pc = block_START;
while (pc) pc = pc();`).

## Runtime layout

| SNOBOL4 type | JS representation |
|---|---|
| String | native JS string |
| Integer / Real | JS number |
| Pattern | `{type, ...}` descriptor + `{α, β}` box pair |
| Array | JS array |
| Table | JS `Map` |
| DATA type | JS class instance |
| Variable | `_vars` object property |
| Code object | JS `Function` |

Output handling:
```js
const _vars = new Proxy({}, {
    set(o,k,v) { o[k]=v; if(k==="OUTPUT") process.stdout.write(String(v)+"\n"); return true; }
});
```

## Per-instance state ζ

ζ is a closure environment in JS — the box factory's local variables
become instance state via lexical capture.  α/β methods read/write
those via closure scope.  GC reclaims ζ when the box reference is
discarded after γ/ω.

## Tools

- `node` (V8) — runtime
- `emit_js.c` — emitter (SCRIP)
