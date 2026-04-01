# SESSION-prolog-js.md — Prolog × JavaScript (one4all)

**Repo:** one4all · **Frontend:** Prolog · **Backend:** JavaScript
**Session prefix:** `PJJ` (Prolog JS — distinct from `PJ` = Prolog JVM)
**Trigger:** "playing with Prolog JavaScript" / "Prolog JS"
**Replaces:** SESSION-prolog-wasm.md (⛔ PARKED)
**Depends on:** M-SJ-A01 complete (shared trampoline + runtime)

---

## §SUBSYSTEMS

| Subsystem | Doc |
|-----------|-----|
| Prolog language / IR | `FRONTEND-PROLOG.md` |
| JS backend | `BACKEND-JS.md` |
| Milestone ladder | `MILESTONE-JS-PROLOG.md` |

---

## §KEY INSIGHT — Unification + Backtracking → Trampoline CPS

Each Prolog clause becomes a trampoline block function.
The choice point (`E_CHOICE`) is a chain: α tries clause 1,
β tries clause 2, etc. E_CUT nulls out the retry chain.
Trail stack unwinds variable bindings on backtrack.

```js
// Prolog: foo(X) :- bar(X), baz(X).
function foo_α() {
    _trail_mark();
    return bar_α;       // try bar first
}
// bar_γ → baz_α → foo_γ (success chain)
// baz_ω → bar_β → foo_ω (backtrack chain)
```

This is the same trampoline model as SNOBOL4 — just with unification
instead of string matching, and trail instead of cursor state.

---

## §KEY FILES

| File | Role |
|------|------|
| `src/backend/emit_js_prolog.c` | Prolog JS emitter (to create) |
| `src/runtime/js/prolog_runtime.js` | term, unify, trail |
| `src/backend/emit_wasm_prolog.c` | Oracle for IR switch (parked) |
| `src/backend/emit_jvm_prolog.c` | Oracle for Byrd wiring (9,972 lines) |

---

## §NOW — PJJ-1

**Next milestone: M-PJJ-A01** (requires M-SJ-A01 complete first)

Read: `BACKEND-JS.md` · `MILESTONE-JS-PROLOG.md` · `FRONTEND-PROLOG.md`

---

*SESSION-prolog-js.md — rewritten PJJ-1, 2026-03-31, Claude Sonnet 4.6.*
