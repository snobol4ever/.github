# ARCH-overview.md — Shared Architecture Concepts

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

## Technique 2 — The Long-Term Architecture (stackless, post-M-BOOTSTRAP)

Lon's insight (B-202 session): **CODE is shared and reentrant. DATA is per-invocation.**

Each Byrd box is a CODE+DATA pair:
- **CODE** — the α/β/γ/ω labeled-goto sequence. Never changes. Marked RX (execute-only).
  Shared across all simultaneous invocations of the same box. One copy in the binary.
- **DATA** — locals: cursor, captures, param values, saved ports. One copy per *live invocation*.
  Allocated on demand. Discarded on backtrack (LIFO = free reclamation, no GC needed).

When `*X` fires (or a function is called recursively):
1. `memcpy(new_data, box_X.data_template, sizeof(box_X.data))` — copy DATA for new invocation
2. Point a dedicated register (e.g. `r12`) at `new_data`
3. Jump to `box_X.α`
4. All locals accessed as `[r12+offset]` — same instruction in CODE, different data per call
5. On γ/ω return: discard `new_data` (LIFO) and restore caller's `r12`

**This is completely stackless.** No `push rbp`. No `[rbp-8]` global slots. No save/restore
boilerplate at call sites. The mechanism *is* the architecture — α allocates a DATA copy
(that IS the save), γ/ω discards it (that IS the restore). Byrd boxes running forward and
backward ARE save and restore.

**2026-03-21 PIVOT — M-BOOTSTRAP prerequisite removed.**
`emit_byrd_asm.c` already knows every box's full structure at compile time.
It emits relocation tables as NASM data sections directly — no self-hosting needed.
Implementation begins post M-MERGE-3WAY. The C-stack bridge (Near-Term Bridge below)
is superseded by T2 once M-T2-FULL fires.

**Milestone chain:** M-T2-RUNTIME → M-T2-RELOC → M-T2-EMIT-TABLE → M-T2-EMIT-SPLIT →
M-T2-INVOKE → M-T2-RECUR → M-T2-CORPUS → M-T2-JVM → M-T2-NET → M-T2-FULL.
**Documented in full:** BACKEND-X64.md §Technique 2.

---

## Near-Term Bridge — Per-Invocation Stack Frames (M-ASM-RECUR)

Until Technique 2 is available, each user-defined function's α port establishes its own
C stack frame. This gives each invocation private `[rbp-8/16/32/48]` slots — the same
isolation guarantee as Technique 2's per-invocation DATA block, using the hardware stack
as allocator instead of `memcpy`.

Fix location: `emit_asm_named_def()`, `is_fn` branch, in `src/backend/x64/emit_byrd_asm.c`.

```nasm
; α — establish own frame
P_ROMAN_α:
    push    rbp
    mov     rbp, rsp
    sub     rsp, 56        ; [rbp-8/16/32/48] are now private to this invocation
    ; ... load args, jmp body ...

; γ — tear down before dispatch
fn_ROMAN_gamma:
    add     rsp, 56
    pop     rbp
    jmp     [P_ROMAN_ret_γ]

; ω — tear down before dispatch
fn_ROMAN_omega:
    add     rsp, 56
    pop     rbp
    jmp     [P_ROMAN_ret_ω]
```

Call sites already use stack push/pop for param save/restore (fixed in session197) — no
change needed there. The per-frame fix is three lines at α and two lines each at γ/ω.

**Optimization note (Lon):** Do NOT implement Technique 2 prematurely. Static code is
hard enough to debug. The stack bridge works correctly and keeps the generated `.s` files
fully inspectable. Optimize when the architecture is proven, not before.

**Milestone:** M-ASM-RECUR fires when recursive SNOBOL4 functions work correctly via the
ASM backend. roman.sno (which exercises mutual/self-recursion) is the acceptance test.

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

## Compatibility Target — SPITBOL (D-001)

**snobol4x targets SPITBOL** as its primary compatibility reference. See DECISIONS.md D-001.

- All SPITBOL language extensions supported (HOST, LOAD, OPSYN, CLEAR, indirect calls, etc.)
- Command-line switches match SPITBOL identically
- CSNOBOL4 is a monitor participant but not authoritative when it diverges from SPITBOL
- FENCE semantic difference in CSNOBOL4 disqualifies it as full target

## Oracle Hierarchy

| Oracle | Role | Status |
|--------|------|--------|
| SPITBOL x64 4.0f | **Primary** — `spitbol -b file.sno` | ✅ installed |
| CSNOBOL4 2.3.3 | Secondary participant — `snobol4 -f -P256k -I$INC file.sno` | ✅ installed |

## Dialect Notes — Known Semantic Differences (D-001, D-002, D-004)

### DATATYPE() return case
| Implementation | `DATATYPE(pattern_val)` |
|----------------|------------------------|
| CSNOBOL4 | `"PATTERN"` (uppercase) |
| SPITBOL | `"pattern"` (lowercase) |
| **snobol4x** | `"PATTERN"` (uppercase — traditional spec, D-002) |

Monitor ignore-point: case differences in DATATYPE output are normalised. Tests are case-insensitive.

### .NAME (unary dot) semantics — three dialects (D-004)
| Implementation | `.NAME` inside fn body | `DIFFER(.NAME,'NAME')` |
|----------------|------------------------|------------------------|
| CSNOBOL4 | DT_S `"NAME"` | Fails |
| SPITBOL | DT_S `"name"` | Succeeds |
| **snobol4x** | DT_N ptr→`"NAME"` | Succeeds (type mismatch) |

snobol4x is a **third dialect** — matches SPITBOL's observable behaviour (IsSpitbol
passes, IsSnobol4 fails) via a different internal mechanism. Monitor ignore-point covers
DT_N vs DT_S differences. See DECISIONS.md D-004.

### FENCE semantics
CSNOBOL4 has a known FENCE difference. snobol4x follows SPITBOL FENCE semantics.
