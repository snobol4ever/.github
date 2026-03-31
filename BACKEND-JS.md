# BACKEND-JS.md — JavaScript Backend Reference (one4all)

**Status:** NEW — SJ-1 / IJ-1 / PJ-1 (2026-03-31)
**Replaces:** WASM backend (parked — see MILESTONE_ARCHIVE.md)

---

## Why JavaScript, Not WASM

WASM is a closed compiled format: no runtime code generation. SNOBOL4's
`EVAL()` and `CODE()` require compiling strings at runtime — a deal-breaker.
JavaScript solves this natively:

- `eval(str)` — evaluate expression string
- `new Function(body)` — compile and instantiate a function from a string
- `function*` generators — native Icon-style backtracking / suspension
- Continuations via callbacks or async/await — Prolog unification/backtrack

---

## Foundation: spipatjs

**Repo:** `github.com/philbudne/spipatjs`
**License:** open source, ES6
**What it provides:** Native SNOBOL4/SPITBOL pattern matching for JavaScript.
PATTERN as first-class composable data type. Non-greedy matching with
backtracking. Full Unicode. Primitive patterns: LEN, POS, RPOS, TAB, RTAB,
REM, ARB, ARBNO, BAL, BREAK, BREAKX, SPAN, ANY, NOTANY, FENCE, ABORT, SUCCEED.
Concatenation (`Pat.and`) and alternation (`Pat.or`). Cursor-function assigns.

This is the pattern runtime for SNOBOL4 JS — we do not reimplement it.

---

## Byrd-Box → JS Encoding

Unlike WASM, JavaScript does not need `return_call`. Byrd boxes become
trampolined objects or closures:

```js
// α = entry, β = resume, γ = succeed, ω = fail
function lit_α(cursor, subject, γ, ω) {
    const end = cursor + LIT_LEN;
    if (subject.slice(cursor, end) === LIT) return γ(end);
    return ω();
}
```

For SNOBOL4 pattern matching specifically, `spipatjs` handles this entirely —
we wire our IR pattern nodes to `spipatjs` constructors rather than emitting
match logic ourselves.

---

## EVAL() / CODE()

```js
// EVAL(expr_string) — evaluate as SNOBOL4 expression
function sno_eval(str) {
    const js = compile_expr_to_js(str);  // scrip-cc partial eval
    return new Function('return ' + js)();
}

// CODE(stmt_string) — compile and jump into
function sno_code(str) {
    const js = compile_stmts_to_js(str);
    return new Function(js)();
}
```

The JS compiler (`emit_js.c`) must be callable at runtime via a bundled
mini-compiler. This is the key milestone that WASM could never reach.

---

## Output Macro Convention

```c
#define J(fmt, ...)  fprintf(js_out, fmt, ##__VA_ARGS__)
#define JFN(name)    fprintf(js_out, "function %s", name)
#define JRET(name)   fprintf(js_out, "  return %s(", name)
```

Mirrors: `W()`/`WFN()`/`WTAIL()` (WASM) · `E()`/`EI()` (x64) · `N()`/`NI()` (.NET)

---

## Runtime Layout

No linear memory. JS objects:

- Variables: plain JS object `{ NAME: value }` — string or number
- Strings: native JS strings (UTF-16, Unicode-correct via spipatjs)
- Arrays: JS arrays
- Tables: JS `Map`
- DATA types: JS classes

---

## Corpus Artifacts

`.js` files alongside `.s` / `.j` / `.il`:

```
corpus/crosscheck/rung4/410_arith_int.js   ← JS artifact
```

New JS rungs (`rungJ01`+) follow same flat layout.

---

## Relation to Other Backends

| Property | x64 | JVM | .NET | ~~WASM~~ | JS |
|----------|-----|-----|------|----------|----|
| IR switch structure | identical | identical | identical | identical | identical |
| EVAL()/CODE() | ❌ | ❌ | ❌ | ❌ | ✅ |
| Byrd-box model | inline labels | Jasmin labels | ilasm labels | return_call | closures/spipatjs |
| Pattern runtime | custom | custom | custom | custom | spipatjs |
| Runner | native | java | mono | node | node / browser |

---

*BACKEND-JS.md — created SJ-1, 2026-03-31, Claude Sonnet 4.6.*
