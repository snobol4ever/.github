# SESSION-prolog-x64.md — Prolog × x64 ASM (snobol4x)

**Repo:** snobol4x · **Frontend:** Prolog · **Backend:** x64 ASM (NASM)
**Session prefix:** `PX` · **Trigger:** "playing with Prolog x64" or "Prolog x86"
**Driver:** `sno2c -pl -asm foo.pl > foo.s` → `nasm -f elf64 foo.s -o foo.o` → `gcc -no-pie foo.o prolog_atom.o prolog_unify.o prolog_builtin.o -o foo`
**Deep reference:** `ARCH-prolog-x64.md` · `FRONTEND-PROLOG.md`

## Subsystems

| Subsystem | Doc | Go there when |
|-----------|-----|---------------|
| Prolog language, IR nodes | `FRONTEND-PROLOG.md` | parser/AST questions |
| Historical session notes | `ARCH-prolog-x64.md` | F-212..F-214 design decisions |
| JVM emitter (mature reference) | `prolog_emit_jvm.c` | algorithm reference |

---

## §BUILD

```bash
cd snobol4x && make -C src
# Compile a Prolog program to x64:
./sno2c -pl -asm foo.pl > foo.s
nasm -f elf64 foo.s -o foo.o
gcc -no-pie foo.o \
  src/frontend/prolog/prolog_atom.o \
  src/frontend/prolog/prolog_unify.o \
  src/frontend/prolog/prolog_builtin.o \
  -o foo
```

---

## §NOW — Session State

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Prolog x64** | `pj-84-bench-baseline` | `a79906e` | M-PJ-X64-1 (multi-clause dispatch) |

**Status:** Single-clause predicates work (`write(hello), nl.` → `hello`).
All multi-clause predicates fail NASM with undefined `pl_PRED_sl_N_cM_α1` symbols.
Systematic emitter bug — retry/β entry label for clause N is referenced but never emitted.
**Root file:** `src/frontend/prolog/prolog_emit.c` (1010 lines).

## CRITICAL NEXT ACTION — M-PJ-X64-1

The emitter generates cross-clause retry calls like:
```nasm
call  pl_tak_sl_4_c1_α1   ; jump to clause 2 retry entry
```
but never emits the `pl_tak_sl_4_c1_α1:` label.

Fix the clause-dispatch loop in `prolog_emit.c` to emit each clause's retry entry label.
Reference: `prolog_emit_jvm.c` clause loop — same four-port Byrd box model.

## Milestone Table

| ID | Description | Gate | Status |
|----|-------------|------|--------|
| M-PJ-X64-1 | Multi-clause dispatch | tak/nreverse/qsort PASS | 🔲 |
| M-PJ-X64-2 | Arithmetic (is/2, comparisons) | times10/log10/ops8 PASS | 🔲 |
| M-PJ-X64-3 | Write/output builtins | crypt/sendmore/queens_8 PASS | 🔲 |
| M-PJ-X64-4 | List builtins (member/append) | nreverse/qsort/flatten PASS | 🔲 |
| M-PJ-X64-5 | Timing grid ≥15/31 vs SWI native | BENCH-prolog-x64.md committed | 🔲 |

## Pre-fix probe (all NASM_FAIL)

Every one of the 31 SWI bench programs fails NASM: `undefined symbol pl_*_α1`.
Single-clause hello world: ✅ works.
