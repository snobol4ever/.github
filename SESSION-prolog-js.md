# SESSION-prolog-js.md — Prolog × JavaScript (one4all)

**Repo:** one4all · **Frontend:** Prolog · **Backend:** JavaScript
**Session prefix:** `PJ` (JS) · **Trigger:** "playing with Prolog JavaScript" / "Prolog JS"
**Replaces:** SESSION-prolog-wasm.md (⛔ PARKED)

---

## §SUBSYSTEMS

| Subsystem | Doc | Go there when |
|-----------|-----|---------------|
| Prolog language / IR | `FRONTEND-PROLOG.md` | unification/clause questions |
| JS backend | `BACKEND-JS.md` | JS codegen patterns |

---

## §KEY INSIGHT — Prolog Backtracking → JS Continuations

Prolog's unification and backtracking map to continuation-passing style (CPS)
in JavaScript:

```js
// Prolog: member(X, [H|_]) :- X = H.
//         member(X, [_|T]) :- member(X, T).
function member(X, list, succeed, fail) {
    if (list.length === 0) return fail();
    const [H, ...T] = list;
    // first clause: unify X with H
    succeed(unify(X, H), () => member(X, T, succeed, fail));
}
```

`succeed` = γ continuation. `fail` = ω continuation (retry next clause).
No stack overflow risk on modern JS engines with tail-call opt; for deep
recursion, trampolining can be added.

---

## §MILESTONES

| ID | Scope | Gate |
|----|-------|------|
| **M-PJ-A01** | Scaffold + hello/facts/unify parity | rung2/3 |
| **M-PJ-B01** | Multi-clause predicates + backtracking | rungP01 |
| **M-PJ-B02** | Arithmetic, comparison, is/2 | rungP02 |
| **M-PJ-B03** | Lists, append, member | rungP03 |
| **M-PJ-C01** | Cut (`!`), negation-as-failure | rungP04 |
| **M-PJ-C02** | assert/retract (dynamic predicates) | rungP05 |
| **M-PJ-PARITY** | Full corpus parity | all Prolog rungs |

---

## §NOW — PJ-1

First action: read `FRONTEND-PROLOG.md`, then `BACKEND-JS.md`, then design
`emit_js_prolog.c` scaffold following `emit_wasm_prolog.c` IR switch layout
(parked but useful as template).

---

*SESSION-prolog-js.md — created PJ-1, 2026-03-31, Claude Sonnet 4.6.*
