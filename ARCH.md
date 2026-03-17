# ARCH.md — Shared Architecture Concepts (L3)

Concepts that span all backends. Backend-specific implementation → BACKEND-C.md, BACKEND-JVM.md, BACKEND-NET.md.

---

## The Fundamental Model — Statement IS a Byrd Box

```
label:  subject  pattern  =replacement  :S(x)  :F(y)
          α          →          γ           γ      ω
```
α = evaluate subject. Pattern = Byrd box labeled gotos. γ = success. ω = failure.
Hot path: pure gotos, zero overhead. Cold path: longjmp for ABORT/FENCE/errors only.

This model applies to ALL backends — the execution semantics are the same whether
the target is C, JVM bytecode, or MSIL. The pattern match is always a Byrd box.
The S/F routing is always a two-port exit.

---

## Byrd Box (universal concept)

```
┌─────────────────────────┐
│  DATA: cursor, locals,  │
│        captures, ports  │
├─────────────────────────┤
│  CODE: α/β/γ/ω gotos   │
└─────────────────────────┘
```

- **α** (proceed) — normal entry, cursor at current position
- **β** (resume) — re-entry after backtrack from child
- **γ** (succeed) — match succeeded, advance cursor
- **ω** (fail) — match failed, restore cursor

Four-port wiring connects nodes: γ of one node → α of next, ω chains back.
ARBNO wires α→γ repeatedly until ω, then proceeds.
FENCE blocks β — prevents backtrack past this point.

**C implementation:** see BACKEND-C.md §Four Techniques for *X.
**JVM implementation:** match.clj `loop/case` state machine.
**.NET implementation:** ThreadedExecuteLoop.cs dispatch.

---

## M-BYRD-SPEC (pending — language-agnostic specification)

A written spec of the four-port lowering rules (α/β/γ/ω wiring per node type)
that all three backends implement independently. Shared contract, not shared code.
When written, it lives here in ARCH.md or as BYRD-SPEC.md.

Node types requiring specification:
- LIT, ANY, NOTANY, SPAN, BREAK, BREAKX
- ARB, ARBNO
- LEN, POS, RPOS, TAB, RTAB, REM
- Conditional assign (`.`), immediate assign (`$`)
- REF (*X) — static and dynamic
- FENCE, ABORT, FAIL, SUCCEED, BAL

---

## Corpus Ladder (shared across all backends)

```
Rung 1:  output      Rung 5:  control     Rung 9:  keywords
Rung 2:  assign      Rung 6:  patterns    Rung 10: functions
Rung 3:  concat      Rung 7:  capture     Rung 11: data
Rung 4:  arith       Rung 8:  strings     Rung 12: beauty.sno
```
All three backends (TINY, JVM, DOTNET) climb the same ladder against the same
corpus in snobol4corpus/crosscheck/. Stop at first failing rung. Fix. Move up.

---

## Oracle Hierarchy

| Oracle | Role | Status |
|--------|------|--------|
| CSNOBOL4 2.3.3 | Primary — `snobol4 -f -P256k -I$INC file.sno` | ✅ installed |
| SPITBOL x64 4.0f | Secondary — `spitbol -b file.sno` | install if needed |

SPITBOL disqualified for full beauty.sno (error 021 at END — indirect function call
semantic difference). Use CSNOBOL4 as primary for beauty tests.
