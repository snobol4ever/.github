# SCRIP-SM.md — SCRIP Stack Machine

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Status:** AUTHORITATIVE DESIGN — all interpreter and emitter work derives from this doc.

---

## The Central Idea

Every frontend (SNOBOL4, Icon, Prolog, Snocone, Rebus, Scrip) compiles to one
shared stack machine instruction set. The stack machine is the IR that gets
executed and the IR that gets emitted as native code. They are the same thing.

The interpreter dispatches instructions one by one in C.
The emitter writes the same instructions as x86, JVM bytecode, MSIL, JS, or WASM.
The instruction set is defined once. There is no divergence.

This is exactly the SIL/MINimal model: each instruction is a macro in assembly,
a dispatch case in the interpreter, and an emit call in the backend.

---

## The SNOBOL4 Statement — Five Phases

Every SNOBOL4 statement has five phases. Each can fail. Only Phase 3 backtracks.

```
Label:  Subject  Pattern  =Replacement  :S(goto)  :F(goto)
```

| Phase | Name        | Can Fail | Backtracks | Executor         |
|-------|-------------|----------|------------|------------------|
| 1     | Subject     | yes      | no         | stack machine    |
| 2     | Pattern     | yes      | no         | stack machine    |
| 3     | Match       | yes      | YES        | BB-DRIVER → BB-GRAPH |
| 4     | Replacement | yes      | no         | stack machine    |
| 5     | Assign      | no       | no         | stack machine    |

Phases 1, 2, 4, 5 are straight-line stack machine execution.
Phase 3 is the Byrd Box graph — the only phase with backtracking.
The entire statement is itself a Byrd Box at the outermost level (:S/:F).

---

## The Stack Machine Instructions

Each instruction operates on a value stack of `DESCR_t` (typed descriptors:
STRING, INTEGER, REAL, PATTERN, CODE, NAME, ARRAY, TABLE).

### Control

| Instruction       | Operands         | Effect |
|-------------------|------------------|--------|
| `SM_LABEL`        | name             | define jump target |
| `SM_JUMP`         | label            | unconditional goto |
| `SM_JUMP_S`       | label            | jump if last result succeeded |
| `SM_JUMP_F`       | label            | jump if last result failed |
| `SM_HALT`         | —                | END statement |

### Values

| Instruction       | Operands         | Effect |
|-------------------|------------------|--------|
| `SM_PUSH_LIT_S`   | string, len      | push string literal |
| `SM_PUSH_LIT_I`   | integer          | push integer literal |
| `SM_PUSH_LIT_F`   | double           | push float literal |
| `SM_PUSH_NULL`    | —                | push null/empty |
| `SM_PUSH_VAR`     | name             | push variable value (NV_GET) |
| `SM_STORE_VAR`    | name             | pop → store into variable (NV_SET) |
| `SM_POP`          | —                | discard top of stack |

### Arithmetic / String

| Instruction       | Operands | Effect |
|-------------------|----------|--------|
| `SM_ADD`          | —        | pop r, pop l, push l+r |
| `SM_SUB`          | —        | pop r, pop l, push l-r |
| `SM_MUL`          | —        | pop r, pop l, push l*r |
| `SM_DIV`          | —        | pop r, pop l, push l/r |
| `SM_EXP`          | —        | pop r, pop l, push l**r |
| `SM_CONCAT`       | —        | pop r, pop l, push l\|\|r (string) |
| `SM_NEG`          | —        | pop v, push -v |

### Pattern Construction (Phase 2)

These build a BB-GRAPH in memory. Each pushes a PATTERN descriptor.

| Instruction       | Operands       | Effect |
|-------------------|----------------|--------|
| `SM_PAT_LIT`      | string, len    | push LIT pattern box |
| `SM_PAT_ANY`      | string, len    | push ANY pattern box |
| `SM_PAT_NOTANY`   | string, len    | push NOTANY box |
| `SM_PAT_SPAN`     | string, len    | push SPAN box |
| `SM_PAT_BREAK`    | string, len    | push BREAK box |
| `SM_PAT_LEN`      | —              | pop n, push LEN(n) box |
| `SM_PAT_POS`      | —              | pop n, push POS(n) box |
| `SM_PAT_RPOS`     | —              | pop n, push RPOS(n) box |
| `SM_PAT_TAB`      | —              | pop n, push TAB(n) box |
| `SM_PAT_RTAB`     | —              | pop n, push RTAB(n) box |
| `SM_PAT_ARB`      | —              | push ARB box |
| `SM_PAT_REM`      | —              | push REM box |
| `SM_PAT_BAL`      | —              | push BAL box |
| `SM_PAT_FENCE`    | —              | push FENCE box |
| `SM_PAT_ABORT`    | —              | push ABORT box |
| `SM_PAT_FAIL`     | —              | push FAIL box |
| `SM_PAT_SUCCEED`  | —              | push SUCCEED box |
| `SM_PAT_ALT`      | —              | pop r, pop l, push ALT(l,r) box |
| `SM_PAT_CAT`      | —              | pop r, pop l, push CAT(l,r) box |
| `SM_PAT_DEREF`    | —              | pop pattern-var, push its BB-GRAPH |
| `SM_PAT_CAPTURE`  | varname        | pop pattern, push CAPTURE(pattern, var) box |

### Statement Execution (five-phase call)

| Instruction       | Operands              | Effect |
|-------------------|-----------------------|--------|
| `SM_EXEC_STMT`    | has_repl, s_label, f_label | pop repl(opt), pop pat, pop subj → call BB-DRIVER → jump :S or :F |

`SM_EXEC_STMT` is the boundary between stack machine and BB-DRIVER.
The stack machine builds subject (Phase 1) and pattern (Phase 2),
then hands off to BB-DRIVER for Phases 3-5, then resumes at :S or :F.

### Functions

| Instruction       | Operands    | Effect |
|-------------------|-------------|--------|
| `SM_CALL`         | name, nargs | pop nargs, call function, push result or fail |
| `SM_RETURN`       | —           | return top of stack to caller |
| `SM_FRETURN`      | —           | failure return |
| `SM_DEFINE`       | spec        | register user function |

### Type Dispatch and Indirect Control (SIL BRANIC / SELBRA)

| Instruction       | Operands     | Effect |
|-------------------|--------------|--------|
| `SM_JUMP_INDIR`   | —            | pop CODE descriptor, set PC to its code block (SIL `BRANIC` / `GOTG :<VAR>`) |
| `SM_SELBRA`       | table[], n   | pop integer index, jump to table[index] (SIL `SELBRA` — type dispatch in INTERP/ARITH) |

### Interpreter State Save/Restore (for EXPVAL — RT-6)

| Instruction       | Operands | Effect |
|-------------------|----------|--------|
| `SM_STATE_PUSH`   | —        | push full interpreter state: OCBSCL, OCICL, NAMICL, NHEDCL, PDLPTR, PDLHED (SIL `ISTACKPUSH`) |
| `SM_STATE_POP`    | —        | restore interpreter state from state stack |

### Integer / Address Arithmetic (inline — no SM_CALL overhead)

| Instruction       | Operands | Effect |
|-------------------|----------|--------|
| `SM_INCR`         | n        | pop d, push d+n (SIL `INCRA`) |
| `SM_DECR`         | n        | pop d, push d-n (SIL `DECRA`) |
| `SM_ACOMP`        | —        | pop r, pop l (integers); push -1/0/1 for l<r/l==r/l>r (SIL `ACOMP` — inline EQ/GT/LT predicates) |
| `SM_RCOMP`        | —        | pop r, pop l (reals); push -1/0/1 (SIL `RCOMP`) |
| `SM_LCOMP`        | —        | pop r, pop l (strings); push -1/0/1 lexicographic (SIL `LEXCMP` — inline LGT/LLT/LGE/LLE) |

### String Coercions (inline — eliminates SM_CALL for common numeric-parse paths)

| Instruction       | Operands | Effect |
|-------------------|----------|--------|
| `SM_SPCINT`       | f_label  | pop string, push integer; jump f_label if not numeric (SIL `SPCINT`) |
| `SM_SPREAL`       | f_label  | pop string, push real; jump f_label if not numeric (SIL `SPREAL`) |
| `SM_TRIM`         | —        | pop string, push with trailing blanks removed (SIL `TRIMSP`) |

---

## The Instruction Stream

A compiled program is a flat array of `SM_Instr` tagged unions:

```c
typedef enum { SM_PUSH_LIT_S, SM_PUSH_VAR, SM_PAT_LIT, SM_PAT_ALT,
               SM_PAT_CAT, SM_EXEC_STMT, SM_JUMP, SM_JUMP_S, SM_JUMP_F,
               SM_CALL, SM_RETURN, SM_FRETURN, SM_LABEL, SM_HALT,
               /* ... all instructions above ... */
} SM_Op;

typedef struct {
    SM_Op    op;
    union {
        struct { const char *s; int len; } str;   /* SM_PUSH_LIT_S, SM_PAT_LIT, etc. */
        long     ival;                             /* SM_PUSH_LIT_I */
        double   dval;                             /* SM_PUSH_LIT_F */
        const char *name;                          /* SM_PUSH_VAR, SM_STORE_VAR, SM_CALL */
        int      target;                           /* SM_JUMP, SM_JUMP_S, SM_JUMP_F (index) */
        int      nargs;                            /* SM_CALL */
        struct { int has_repl; int s_idx; int f_idx; } exec; /* SM_EXEC_STMT */
    } u;
} SM_Instr;

typedef struct {
    SM_Instr *code;
    int       len;
} SM_Program;
```

---

## Example: SNOBOL4 Statement → Instructions

```snobol4
LINE  'HELLO' LEN(5) . WORD  =UPPER(WORD)  :S(FOUND) :F(DONE)
```

Compiles to:

```
SM_PUSH_VAR     "LINE"          ; Phase 1: subject
SM_PUSH_LIT_S   "HELLO", 5     ; Phase 2: pattern build
SM_PAT_LIT                      ;   → LIT box
SM_PUSH_VAR     "LEN"           ;   (builtin function)
SM_PUSH_LIT_I   5
SM_CALL         "LEN", 1        ;   → LEN box
SM_PAT_CAT                      ;   → CAT(LIT, LEN) box
SM_PAT_CAPTURE  "WORD"          ;   → CAPTURE box
SM_PUSH_VAR     "WORD"          ; Phase 4: replacement
SM_CALL         "UPPER", 1
SM_EXEC_STMT    has_repl=1, s="FOUND", f="DONE"
```

The interpreter dispatches each instruction. The x86 emitter writes each
instruction as native code. They produce identical behavior by construction.

---

## The Lowering Pass

The compiler pipeline:

```
Source text
  → LEXER        (per language)
  → PARSER       (per language)
  → IR           (EXPR_t / STMT_t — shared Program* representation)
  → SM-LOWER     (IR → SM_Program — one pass, language-aware)
  → SM_Program   (flat instruction array — language-independent)
       ├─ INTERP  (dispatch loop — interpret SM_Program directly)
       └─ EMITTER (walk SM_Program, emit native code per backend)
```

`SM-LOWER` is the missing component. It replaces the tree-walk in
`scrip-interp.c` and is the correct foundation for both the interpreter
and all emitters.

---

## Relationship to Byrd Boxes

The stack machine and the BB-GRAPH are complementary, not competing:

- Stack machine handles all **straight-line** computation (phases 1, 2, 4, 5).
- BB-GRAPH handles all **backtracking** computation (phase 3 only).
- `SM_EXEC_STMT` is the clean handoff point between them.
- `SM_PAT_*` instructions build the BB-GRAPH during phase 2.

The BB-GRAPH nodes are allocated in `bb_pool` during phase 2 execution.
`SM_EXEC_STMT` calls `BB-DRIVER` with the root node of the graph.

---

## Relationship to Generated Code

Each SM instruction maps 1-to-1 to generated code in every backend:

| SM Instruction    | x86                        | JVM              | .NET MSIL       | JS              |
|-------------------|----------------------------|------------------|-----------------|-----------------|
| `SM_PUSH_VAR`     | `call NV_GET_fn`           | `invokestatic`   | `call NV_GET`   | `nv_get(name)`  |
| `SM_PAT_LIT`      | `call pat_lit`             | `invokestatic`   | `call pat_lit`  | `pat_lit(...)`  |
| `SM_PAT_ALT`      | `call pat_alt`             | `invokestatic`   | `call pat_alt`  | `pat_alt(...)`  |
| `SM_EXEC_STMT`    | `call stmt_exec_dyn`       | `invokevirtual`  | `call exec`     | `exec_stmt()`   |
| `SM_JUMP_S`       | `test eax,eax / jnz`       | `ifne`           | `brtrue`        | `if (r)`        |

The x86 column is the SM interpreted natively. Zero semantic gap.

---

## What Does NOT Exist Yet (2026-04-04)

- `SM_Instr` typedef and `SM_Program` struct — **not written**
- `SM-LOWER` pass (IR → SM_Program) — **not written**
- Interpreter dispatch loop over `SM_Program` — **not written** (scrip-interp.c tree-walks IR instead)
- x86 emitter over `SM_Program` — **not written** (emit_x64.c tree-walks IR instead)

The bb_pool, bb_emit, and all 25 bb_*.c boxes are complete and correct.
They are waiting for SM_EXEC_STMT to call them properly.

---

## References

- `IR.md` — the EXPR_t/STMT_t IR that SM-LOWER compiles from
- `BB-GRAPH.md` — the Byrd Box graph that SM_PAT_* instructions build
- `BB-DRIVER.md` — the executor called by SM_EXEC_STMT
- `GENERAL-SIL-HERITAGE.md` — SIL/MINimal heritage, E_* node origins
- `INTERP-X86.md` — the C interpreter that dispatches SM_Program
- `EMITTER-X86.md` — the x86 emitter that compiles SM_Program to native code
