# SESSION-icon-js.md — Icon × JavaScript (one4all)

**Repo:** one4all · **Frontend:** Icon · **Backend:** JavaScript
**Session prefix:** `IJ` (JS) · **Trigger:** "playing with Icon JavaScript" / "Icon JS"
**Note:** `IJ` prefix previously used for Icon JVM — context distinguishes them.
**Replaces:** SESSION-icon-wasm.md (⛔ PARKED)

---

## §SUBSYSTEMS

| Subsystem | Doc | Go there when |
|-----------|-----|---------------|
| Icon language / IR | `FRONTEND-ICON.md` | generator/suspension questions |
| JS backend | `BACKEND-JS.md` | JS codegen patterns |

---

## §KEY INSIGHT — Icon Generators → JS Generators

Icon's goal-directed evaluation maps almost perfectly to JavaScript's
`function*` generators:

```js
// Icon: every(write(1 to 5))
function* _range(lo, hi) {
    for (let i = lo; i <= hi; i++) yield i;
}
function* _write(gen) {
    for (const v of gen) { process.stdout.write(String(v) + '\n'); yield v; }
}
```

Suspension (`@`) → `yield`. Resume (`@&`) → `.next()`. Failure → generator
exhaustion. This is a natural fit — no trampoline needed for the common case.

---

## §MILESTONES

| ID | Scope | Gate |
|----|-------|------|
| **M-IJ-A01** | Scaffold + hello/arith/string parity | rung2/3/4 |
| **M-IJ-B01** | Generator basics: `to`, `seq`, `every` | rungI01 |
| **M-IJ-B02** | Alternation: `|` operator via chained generators | rungI02 |
| **M-IJ-B03** | Suspension / co-expression basics | rungI03 |
| **M-IJ-C01** | String scanning (`?` operator) | rungI04 |
| **M-IJ-PARITY** | Full corpus parity | all Icon rungs |

---

## §NOW — IJ-1

First action: read `FRONTEND-ICON.md`, then `BACKEND-JS.md`, then design
`emit_js_icon.c` scaffold following `emit_wasm_icon.c` structure (now parked
but useful as template for IR switch layout).

---

*SESSION-icon-js.md — created IJ-1, 2026-03-31, Claude Sonnet 4.6.*
