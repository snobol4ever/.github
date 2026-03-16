# BACKEND-C.md — C Native Backend Architecture (L3)

The C backend compiles SNOBOL4 → C code that links against the C runtime (snobol4.c).
All patterns are compiled Byrd boxes. No interpreter on the hot path.

*Session state → TINY.md. sno2c compiler frontend → FRONTEND-SNO2C.md.*

---

## Core Model — Statement IS a Byrd Box (Session 27)

```
label:  subject  pattern  =replacement  :S(x)  :F(y)
          α          →          γ           γ      ω
```
- **α** — evaluate subject → Σ (string), Δ (cursor=0)
- **pattern** — Byrd box: labeled gotos through match nodes
- **γ** — success: apply replacement, follow :S() goto
- **ω** — failure: follow :F() goto

**Hot path:** pure C labeled gotos. Zero overhead. No setjmp on hot path.
**Cold path:** `longjmp` for ABORT, FENCE bare, runtime errors ONLY.

---

## Byrd Box Layout (Session 16, permanent)

```
┌─────────────────────────┐
│  DATA: cursor, locals,  │
│        captures, ports  │
├─────────────────────────┤
│  CODE: α/β/γ/ω gotos   │
└─────────────────────────┘
Memory: DATA section: [box0.data | box1.data | ...]
        TEXT section: [box0.code | box1.code | ...]
```

---

## Four Techniques for *X

### Technique 1 — Struct-passing ← CURRENT (C target, M-BEAUTY-FULL)

Each named pattern → C function `pat_X(pat_X_t **zz, int entry)`.
All locals in typed struct. Declared before first `goto` (satisfies C99 §6.8.6.1).
Child frame for `*Y` = pointer field in parent struct (size known at compile time).
calloc on entry==0. beta dispatch on entry==1.

```c
typedef struct pat_Parse_t {
    int64_t  saved_7;
    int      arbno_depth;
    int64_t  arbno_stack[64];
    struct pat_Command_t *Command_z;
} pat_Parse_t;

static SnoVal pat_Parse(pat_Parse_t **zz, int entry) {
    pat_Parse_t *z = *zz;
    if (entry == 0) { z = *zz = calloc(1, sizeof(*z)); goto Parse_alpha; }
    if (entry == 1) { goto Parse_beta; }
    Parse_alpha: ...Byrd box labeled gotos...
    Parse_gamma: return matched_val;
    Parse_omega: return FAIL_VAL;
}
```
*(Pattern names match beauty.sno: `Parse`, `Command`, `Stmt`, `Label`, `Expr14`, `Goto`.)*

### Technique 2 — mmap + memcpy + relocate (FUTURE — ASM/native, post-BOOTSTRAP)

When `*X` fires: memcpy CODE section, memcpy DATA section (locals), relocate jumps,
jump to new TEXT[PROCEED]. TEXT: PROTECTED (RX), mprotect→RWX during copy, back to RX.
No heap. No GC. ~20 lines. LIFO = discard copy on backtrack failure.
Two relocation cases: relative refs (add delta), absolute DATA refs (patch to new copy).

### Technique 3 — Iota functions (concept, revisit post-M-BEAUTY-FULL)

Every labeled block → own tiny C function (for addressability). Sequence wrapped in
one outer function. One flat concatenated struct for all locals. Bridges T1 and T2.

### Technique 4 — GCC &&label port table (concept, nonstandard)

Entire pattern in ONE function. GCC `&&label` → `void*` port table.
`goto *ports[entry]`. GCC/Clang only — not standard C.

---

## Block Function Model ("The New Plan", 2026-03-14)

```c
typedef block_fn_t (*block_fn_t)(void);
block_fn_t pc = block_START;
while (pc) pc = pc();    /* entire engine */
```

Every stmt → C function returning next block address (S-label or F-label).
Stmts grouped by label reachability into `block_L` functions.
Flat concatenated locals struct per block.

| SNOBOL4 | Mechanism |
|---------|-----------|
| `:(L42)` | `return block_L42` |
| `*X` static | call `block_X` directly |
| `*X` dynamic | X holds `block_fn_t`, call it |
| `EVAL(str)` | TCC compile → degenerate stmt fn |
| `CODE(str)` | TCC compile → block fn sequence |

Sprint map: `trampoline` → `stmt-fn` → `block-fn` → `pattern-block` → `code-eval`.
All gate on M-BEAUTY-FULL.

---

## setjmp Model

| Feature | Status |
|---------|--------|
| Per-function setjmp | ✅ `emit.c emit_fn()` |
| `push/pop_abort_handler` macros | ✅ `runtime_shim.h` |
| Per-statement setjmp | ❌ `emit.c emit_stmt()` |
| Glob-sequence optimization | ❌ needs reachability pass |
| Non-Gimpel DEFINE guard | ❌ `emit.c emit_stmt()` |

**Glob-sequence:** consecutive stmts in DEFINE body with NO internal label targets
share ONE setjmp. Stmts that ARE label targets start a new boundary.
**Non-Gimpel DEFINE:** bare `DEFINE(...)` mid-program gets own standalone guard.

---

## Save/Restore in DEFINE Functions

**WRONG (current):** C-local `var_get/var_set` preamble/postamble in `emit_fn()`.
**RIGHT (target):** α port saves caller locals into struct; γ/ω ports restore.
Makes save/restore explicit in 3-column format. Prerequisite for M-COMPILED-SELF.

---

## Architecture Decisions (Locked)

| # | Decision |
|---|----------|
| D1 | Memory: Boehm GC (`libgc`) |
| D2 | Tree children: realloc'd dynamic array |
| D3 | cstack: thread-local (`__thread MatchState *`) |
| D4 | Tracing: full impl, `doDebug=0` = zero cost |
| D5 | `mock_engine.c` only in beauty_full_bin — `engine.c` fully superseded |
| D6 | All vars through `NV_GET_fn`/`NV_SET_fn` — `is_fn_local` suppression removed |
| D7 | `T_FNCALL` wrapper universal — all DEFINE'd functions save/restore on entry/exit |
