# EMITTER-JS.md — JavaScript Emitter (one4all)

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Status:** AUTHORITATIVE — Active (SJ-4 pivot, 2026-04-02)

Walks SM_Program and emits JavaScript source. Also covers the JS dynamic Byrd box model.
**Session prefixes:** SJ (SNOBOL4 JS) · IJJ (Icon JS) · PJJ (Prolog JS)
**Replaces:** WASM backend (parked)

---

## Why JavaScript

SNOBOL4's `EVAL()` and `CODE()` require runtime code generation. WASM cannot do this.
JavaScript solves it natively: `new Function(body)` compiles and runs arbitrary code strings.
Functions are first-class — Byrd-box ports are just function refs.
Dynamic Byrd boxes: `{α, β}` objects built at runtime from pattern values.

---

## Byrd Box Model — Static vs Dynamic

### Static path (emit_js.c)

For patterns known at compile time, `emit_js.c` emits hardwired port functions:

```js
// Emitted by emit_js.c for E_QLIT "HELLO" (node uid N)
function P_N_α() {
    const end = cursor + 5;
    if (subject.slice(cursor, end) === "HELLO") {
        cursor = end; return γ_outer;
    }
    return ω_outer;
}
function P_N_β() { return ω_outer; }
```

**Oracle for emit_js.c:** `src/backend/c/emit_byrd_c.c`

### Dynamic path (sno_engine.js)

For runtime-constructed patterns (EVAL/CODE, pattern variables), `build_pattern()` walks
the pattern descriptor and constructs a live `{α, β}` graph:

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

---

## EVAL() / CODE()

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

`new Function()` creates JIT-compiled functions — same performance as statically emitted code.

---

## The Trampoline Model

**Oracle:** `backend/c/trampoline.h`

```js
let pc = block_START;
while (pc) pc = pc();
```

Every SNOBOL4 statement compiles to a zero-argument function returning the next function.

---

## Runtime Layout

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

---

## Dependency Chain

```
Step 1  emit_js.c scaffold — builds clean, empty EKind switch
Step 2  sno_runtime.js — print/OUTPUT, value types, coercion
Step 3  sno_engine.js stub — exec_stmt Phase 1+5 (no pattern)
Step 4  Arith + string + goto/labels (rung2/3/4/8)
Step 5  Pattern: Phase 2 build_pattern() + Phase 3 scan loop (rungJ01–J06)
Step 6  Arrays / Tables / DATA (rung10/11)
Step 7  User-defined functions / DEFINE (rung10)
Step 8  EVAL() / CODE() — _scrip_compile + new Function() (rungJ07)
```

---

## References

- `SCRIP-SM.md` — SM_Program this emitter walks
- `EMITTER-COMMON.md` — shared emitter architecture
- `INTERP-JS.md` — JS interpreter (5-phase executor details)
- `RUNTIME.md` — unified execution model (EVAL, CODE)

---

## Output Handling (decided SJ-1)

```js
const _vars = new Proxy({}, {
    set(o,k,v) { o[k]=v; if(k==="OUTPUT") process.stdout.write(String(v)+"\n"); return true; }
});
```

---

## Corpus Artifacts

`.js` files alongside `.s` / `.j` / `.il`:
```
corpus/crosscheck/rung2/210_indirect_ref.js
corpus/crosscheck/rung4/410_arith_int.js
```

JS-specific pattern rungs: `rungJ01`–`rungJ07`.
