# BACKEND-JS.md — JavaScript Backend Reference (one4all)

**Status:** Active — SJ-4 pivot (2026-04-02)
**Replaces:** WASM backend (parked — see MILESTONE_ARCHIVE.md)
**Session prefixes:** SJ (SNOBOL4 JS) · IJJ (Icon JS) · PJJ (Prolog JS)

---

## Why JavaScript

SNOBOL4's `EVAL()` and `CODE()` require runtime code generation. WASM's
closed binary format cannot do this. JavaScript solves it natively:

- `new Function(body)` — compile and run arbitrary code strings at runtime
- Functions are first-class values — Byrd-box ports are just function refs
- Dynamic Byrd boxes: `{α, β}` objects built at runtime from pattern values
- Same 5-phase executor handles static and dynamic patterns identically

---

## The 5-Phase Executor Spine

Every SNOBOL4 statement — pattern or not — runs through `exec_stmt()` in
`sno_engine.js`, which is a direct JS port of `src/runtime/dyn/stmt_exec.c`:

```
Phase 1: build_subject  — resolve subject variable or evaluate expression
Phase 2: build_pattern  — pattern value → live {α,β} Byrd box graph
Phase 3: run_match      — drive root.α() via trampoline, collect captures
Phase 4: build_repl     — replacement expression already evaluated
Phase 5: perform_repl   — splice into subject, assign, :S/:F branch
```

Pattern-free statements skip Phases 2+3. EVAL/CODE-constructed patterns use
the same executor as statically emitted ones — `new Function()` produces
real JS port functions that wire into the same trampoline.

**Oracle for `sno_engine.js`:** `src/runtime/dyn/stmt_exec.c`
**Oracle for `emit_js.c`:** `src/backend/c/emit_byrd_c.c`

---

## The Trampoline Model (oracle: `backend/c/trampoline.h`)

Every SNOBOL4 statement compiles to a zero-argument function returning
the next function. The engine is identical in C and JS:

```c
block_fn_t pc = block_START;   /* C */
while (pc) pc = pc();
```

```js
let pc = block_START;          /* JS */
while (pc) pc = pc();
```

---

## Byrd Box Model — Static vs Dynamic

### Static path (emit_js.c)

For patterns known at compile time, `emit_js.c` emits hardwired port
functions directly into the output `.js` file — same as `emit_byrd_c.c`:

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

### Dynamic path (sno_engine.js)

For runtime-constructed patterns (EVAL/CODE, pattern variables), Phase 2
of `exec_stmt()` calls `build_pattern(pat)`, which walks the pattern
descriptor and constructs a live `{α, β}` graph:

```js
function build_pattern(pat) {
    switch (pat.type) {
        case DT_QLIT: return build_qlit(pat.s);
        case DT_SEQ:  return build_seq(pat.children);
        case DT_ALT:  return build_alt(pat.left, pat.right);
        // ... all 16 E_* pattern types
    }
}

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

Phase 3 drives the root box: `let port = root.α; while (...) port = port();`

The static and dynamic paths produce structurally identical execution — the
trampoline doesn't know or care which path built the port functions.

---

## EVAL() / CODE()

```js
// EVAL: SNOBOL4 expression string → value
function sno_eval(str) {
    const js = _scrip_compile_expr(str);
    return new Function('_rt', 'return (' + js + ')')(_runtime);
}

// CODE: SNOBOL4 statement block string → executable code object
function sno_code(str) {
    const js = _scrip_compile_stmts(str);
    return new Function('_rt', js)(_runtime);
}
```

`new Function()` creates real JS functions — JIT-compiled, same performance
as statically emitted code. EVAL-constructed patterns run through the dynamic
Byrd box path in `exec_stmt()` Phase 2. No special cases needed.

Example — EVAL pattern at runtime:
```snobol4
P = EVAL("'HELLO' | 'WORLD'")   * DT_ALT pattern built at runtime
X P = 'FOUND'                   * exec_stmt Phase 2: build_pattern(P)
```
Phase 2 calls `build_alt(build_qlit("HELLO"), build_qlit("WORLD"))`.
Phase 3 trampolines through the resulting `{α, β}` graph.
Phase 5 splices and assigns. Identical to any static pattern statement.

---

## Runtime Layout

| SNOBOL4 type | JS representation |
|---|---|
| String | native JS string |
| Integer / Real | JS number |
| Pattern | `{type, ...}` descriptor + `{α, β}` box pair (dynamic) |
| Array | JS array |
| Table | JS `Map` |
| DATA type | JS class instance |
| Variable | `_vars` object property |
| Code object | JS `Function` |

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

---

## Dependency Chain

```
Step 1  emit_js.c scaffold — builds clean, empty EKind switch
Step 2  sno_runtime.js — print/OUTPUT, value types, coercion
Step 3  sno_engine.js stub — exec_stmt Phase 1+5 (no pattern)
Step 4  Arith + string + goto/labels (rung2/3/4/8) — Phase 4 value layer
Step 5  Pattern: Phase 2 build_pattern() + Phase 3 scan loop (rungJ01–J06)
Step 6  Arrays / Tables / DATA (rung10/11)
Step 7  User-defined functions / DEFINE (rung10)
Step 8  EVAL() / CODE() — _scrip_compile + new Function() (rungJ07)
```

---

## Relation to Other Backends

| | x64 | JVM | .NET | JS |
|---|---|---|---|---|
| Oracle for JS | — | — | — | `emit_byrd_c.c` + `stmt_exec.c` |
| Port encoding | inline NASM labels | Jasmin labels | ilasm labels | trampoline fns |
| Dynamic boxes | via DYN/stmt_exec.c | ❌ | ❌ | ✅ native |
| EVAL()/CODE() | ❌ | ❌ | ❌ | ✅ `new Function()` |
| Browser target | ❌ | ❌ | ❌ | ✅ |
| Runner | native | java | mono | node / browser |

---

*BACKEND-JS.md — rewritten SJ-4 pivot, 2026-04-02, Claude Sonnet 4.6.*
*Added: dynamic Byrd box model, static vs dynamic path distinction, EVAL/CODE mechanics.*
