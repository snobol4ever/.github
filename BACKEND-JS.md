# BACKEND-JS.md — JavaScript Backend Reference (one4all)

**Status:** NEW — SJ-1 / IJ-1 / PJ-1 (2026-03-31)
**Replaces:** WASM backend (parked — see MILESTONE_ARCHIVE.md)
**Session prefixes:** SJ (SNOBOL4 JS) · IJJ (Icon JS) · PJJ (Prolog JS)

---

## Why JavaScript

SNOBOL4's `EVAL()` and `CODE()` require runtime code generation. WASM's
closed binary format cannot do this. JavaScript solves it natively:

- `new Function(body)` — compile and run arbitrary code strings at runtime
- `eval(str)` — evaluate expression strings
- Functions are first-class values — Byrd-box ports are just function refs
- `function*` generators — native Icon-style suspension/resumption

---

## The Trampoline Model (oracle: `backend/c/trampoline.h`)

The C backend already solved dispatch. Every SNOBOL4 statement compiles to
a `block_fn_t` — zero-argument function returning the next function:

```c
block_fn_t pc = block_START;   /* C */
while (pc) pc = pc();
```

In JavaScript this is **identical**:

```js
let pc = block_START;          /* JS */
while (pc) pc = pc();
```

Every Byrd-box port (α/β/γ/ω) is a JS function returning the next port.
No recursion. No stack growth. EVAL()/CODE() work because `new Function()`
creates new port functions at runtime and wires them into the dispatch table.

**`emit_byrd_c.c` is the direct oracle for `emit_js.c`.**
Same EKind switch. Same four-port wiring per node. Same trampoline engine.
Replace `C(fmt,...)` with `J(fmt,...)`. Replace C syntax with JS syntax.

---

## Byrd-Box → JS Encoding

```js
// E_QLIT — literal string match (node id N)
function P_N_α() {
    const end = cursor + LIT_LEN;
    if (subject.slice(cursor, end) === "LIT_STR") {
        cursor = end; return γ_outer;
    }
    return ω_outer;
}
function P_N_β() { return ω_outer; }   // literals don't backtrack
```

For value expressions: JS expression syntax for values, trampoline for
control — same split as C backend.

---

## EVAL() / CODE()

```js
function sno_eval(str) {
    const js = _scrip_compile_expr(str);   // mini-compiler (M-SJ-C01)
    return new Function('return (' + js + ')')();
}
function sno_code(str) {
    const js = _scrip_compile_stmts(str);
    return new Function('_rt', js)(_runtime);
}
```

Mini-compiler added in M-SJ-C01 after full corpus parity is established.

---

## Runtime Layout

| SNOBOL4 type | JS representation |
|---|---|
| String | native JS string |
| Integer / Real | JS number |
| Pattern | `{α, β}` port function pair |
| Array | JS array |
| Table | JS `Map` |
| DATA type | JS class instance |
| Variable | `_vars` object property |

---

## Corpus Artifacts

`.js` files alongside `.s` / `.j` / `.il`:
```
corpus/crosscheck/rung2/210_indirect_ref.js
corpus/crosscheck/rung4/410_arith_int.js
```

JS-specific pattern rungs: `rungJ01`–`rungJ07`.

---

## Dependency Chain — Chicken and Egg

The correct order (each step gates the next):

```
Step 1  emit_js.c scaffold — builds clean, empty EKind switch
Step 2  sno_runtime.js stub — print/OUTPUT, variable get/set
Step 3  Trampoline + arith + assignment (rung2/3/4) — 981/4 holds
Step 4  String ops: concat, SIZE, REPLACE, DUPL (rung8)
Step 5  Control flow: goto, :S/:F, labels (rung5/6)
Step 6  Pattern matching: E_QLIT→E_ALT→E_ARBNO (rungJ01–J04)
Step 7  Captures: E_CAPT_COND / E_CAPT_IMM (rungJ05)
Step 8  Arrays / Tables / DATA (rung10/11)
Step 9  User-defined functions / DEFINE (rung10)
Step 10 EVAL() / CODE() mini-compiler (M-SJ-C01)
```

Runtime before tests. Scaffold before runtime. Emit-diff gate holds from
step 3 — JS artifacts don't exist yet for steps 1–2, checker skips absent
artifact types.

---

## Relation to Other Backends

| | x64 | JVM | .NET | JS |
|---|---|---|---|---|
| Oracle for JS | — | — | — | `emit_byrd_c.c` |
| Port encoding | inline labels | Jasmin labels | ilasm labels | trampoline fns |
| EVAL()/CODE() | ❌ | ❌ | ❌ | ✅ |
| Browser target | ❌ | ❌ | ❌ | ✅ |
| Runner | native | java | mono | node / browser |

---

*BACKEND-JS.md — rewritten SJ-1, 2026-03-31, Claude Sonnet 4.6.*
