# SESSION-linker-sprint1.md — SCRIP Linker Sprint 1

**Track:** LINKER (LP)  
**Session:** LP-2 (this doc written LP-1)  
**Date:** 2026-03-27  
**Goal:** M-LINK-ABI freeze + M-LINK-X64-1 through M-LINK-X64-3  
**Gate:** Read `ARCH-scrip-abi.md` before touching any code.

---

## Session Objective

By end of Sprint 1:

1. `ARCH-scrip-abi.md` reviewed, any issues resolved, marked **FROZEN**
2. `EXPORT` / `IMPORT` parsed in `src/frontend/snobol4/parse.c`
3. `EXPORT name` emits `.globl alpha_NAME, gamma_NAME, omega_NAME` in `emit_byrd_asm.c`
4. Static-by-default: non-exported DEFINEs emit **no** `.globl`
5. `scrip compile -c hello.sno` → `hello.o` via `as -o hello.o hello.s`
6. **Acceptance test green:** `hello_a.sno` exports `GREET`, `hello_b.sno` imports and calls it, linked binary runs

Regression invariant: `106/106` ASM corpus stays green throughout.

---

## File Map — What We Touch

```
src/frontend/snobol4/
    lex.c           ADD: T_EXPORT, T_IMPORT token kinds
    lex.h           ADD: token kind enum entries
    parse.c         ADD: parse_toplevel_directive() for EXPORT/IMPORT
    sno2c.h         ADD: ExportList, ImportList fields on Program struct

src/backend/x64/
    emit_byrd_asm.c ADD: emit_exports(), emit_import_externs()
                    CHANGE: emit_named_def() — omit .globl unless exported

src/driver/
    main.c          ADD: -c flag → invoke `as`, produce .o
                    ADD: --jvm, --net flag stubs (no-op for now)

src/runtime/snobol4/
    snoVal.h        NEW: canonical SnoVal definition (from ARCH-scrip-abi.md §1)
```

---

## Step-by-Step

### Step 1 — snoVal.h (30 min)

Create `src/runtime/snobol4/snoVal.h` verbatim from the ABI doc §1.
This is the canonical shared type. Every future cross-language file will `#include` it.

```c
/* snoVal.h — canonical SCRIP value type. Shared across all backends.
 * Do not add language-specific fields. Keep this file ABI-stable. */
#ifndef SNOVAL_H
#define SNOVAL_H
#include <stddef.h>

typedef enum {
    SV_STRING  = 0,
    SV_INTEGER = 1,
    SV_REAL    = 2,
    SV_PATTERN = 3,
    SV_TABLE   = 4,
    SV_ARRAY   = 5,
    SV_UNDEF   = 6
} SnoValTag;

typedef struct SnoVal {
    SnoValTag tag;
    union {
        struct { const char *ptr; size_t len; } s;
        long long i;
        double    r;
        void     *p;
    };
} SnoVal;

#endif /* SNOVAL_H */
```

Verify: `#include "snoVal.h"` compiles clean in `sno2c.h`. Zero code changes needed yet.

---

### Step 2 — Lex tokens (45 min)

In `lex.h`, add two token kinds after the existing list:

```c
T_EXPORT,   /* EXPORT keyword at start of statement label position */
T_IMPORT,   /* IMPORT keyword at start of statement label position */
```

In `lex.c`, in the keyword recognition section (wherever `DEFINE`, `END`, etc. are
recognized as special statement-level keywords):

```c
/* Statement-level directives — recognized only at label/body position */
if (strcmp(word, "EXPORT") == 0) return T_EXPORT;
if (strcmp(word, "IMPORT") == 0) return T_IMPORT;
```

**Note:** `EXPORT` and `IMPORT` are only keywords at the **statement level** (where
`DEFINE` and `END` live). Inside pattern expressions they remain ordinary identifiers —
existing SNOBOL4 programs that use `EXPORT` or `IMPORT` as variable names are unaffected
if those names appear only in the body/goto fields.

---

### Step 3 — AST nodes (30 min)

In `sno2c.h`, add to the statement node kinds:

```c
STMT_EXPORT,   /* EXPORT name — marks a DEFINE as externally visible */
STMT_IMPORT,   /* IMPORT lang.name — declares an external symbol */
```

Add to the `Program` struct:

```c
typedef struct ExportEntry {
    char *name;                  /* exported symbol name (uppercase) */
    struct ExportEntry *next;
} ExportEntry;

typedef struct ImportEntry {
    char *lang;                  /* source language: "PROLOG", "ICON", etc. */
    char *name;                  /* symbol name */
    struct ImportEntry *next;
} ImportEntry;

/* Add to Program: */
ExportEntry *exports;            /* linked list of EXPORTs */
ImportEntry *imports;            /* linked list of IMPORTs */
```

---

### Step 4 — Parser (1 hr)

In `parse.c`, add `parse_toplevel_directive()` called from the statement dispatcher
when `T_EXPORT` or `T_IMPORT` is seen at the start of a line:

```c
/* parse_toplevel_directive — handles EXPORT and IMPORT statements.
 *
 * EXPORT syntax:   EXPORT  <IDENT>
 * IMPORT syntax:   IMPORT  <LANG>.<IDENT>
 *
 * Both are statement-level only. No expression parsing needed.
 * Returns a STMT_EXPORT or STMT_IMPORT node. */
static Stmt *parse_toplevel_directive(Lex *lx, Program *prog) {
    Token t = lex_next(lx);   /* consume T_EXPORT or T_IMPORT */
    skip_ws(lx);
    Token name_tok = lex_next(lx);  /* expect T_IDENT */
    if (name_tok.kind != T_IDENT) {
        parse_error(lx, "EXPORT/IMPORT: expected identifier");
        return NULL;
    }

    if (t.kind == T_EXPORT) {
        ExportEntry *e = xmalloc(sizeof *e);
        e->name = xstrdup(name_tok.text);
        e->next = prog->exports;
        prog->exports = e;
        return make_stmt(STMT_EXPORT, name_tok.text);
    }

    /* IMPORT: expect LANG.NAME */
    if (lex_peek(lx).kind != T_DOT) {
        /* bare IMPORT NAME — no language prefix, assume same language */
        ImportEntry *ie = xmalloc(sizeof *ie);
        ie->lang = xstrdup("SNOBOL4");
        ie->name = xstrdup(name_tok.text);
        ie->next = prog->imports;
        prog->imports = ie;
        return make_stmt(STMT_IMPORT, name_tok.text);
    }
    lex_next(lx);  /* consume T_DOT */
    Token sym_tok = lex_next(lx);  /* symbol name after dot */
    ImportEntry *ie = xmalloc(sizeof *ie);
    ie->lang = xstrdup(name_tok.text);   /* the lang prefix */
    ie->name = xstrdup(sym_tok.text);
    ie->next = prog->imports;
    prog->imports = ie;
    return make_stmt(STMT_IMPORT, sym_tok.text);
}
```

---

### Step 5 — x64 Emitter (1.5 hr)

This is the core change. Two functions in `emit_byrd_asm.c`.

#### 5a. `emit_exports()` — emit `.globl` for exported symbols

```c
/* emit_exports — emit .globl directives for all EXPORTs.
 * Called once, before the first section, after the file header.
 * Each exported DEFINE gets three .globl entries: alpha, gamma, omega.
 * The beta port is NOT exported — callers do not redo into foreign boxes
 * in Sprint 1. (Beta export deferred to M-LINK-X64-REDO.) */
static void emit_exports(Program *prog) {
    for (ExportEntry *e = prog->exports; e; e = e->next) {
        /* Mangle: EXPORT FOO → SNOBOL4_FOO */
        A(".globl  SNOBOL4_%s_alpha\n", e->name);
        A(".globl  SNOBOL4_%s_gamma\n", e->name);
        A(".globl  SNOBOL4_%s_omega\n", e->name);
    }
    if (prog->exports) A("\n");
}
```

#### 5b. `emit_import_externs()` — emit `extern` references for IMPORTs

```c
/* emit_import_externs — emit extern declarations for all IMPORTs.
 * In NASM ELF64, external symbols need no explicit declaration —
 * the linker resolves them. But we emit comments for documentation
 * and to catch naming issues early with `nm`. */
static void emit_import_externs(Program *prog) {
    for (ImportEntry *ie = prog->imports; ie; ie = ie->next) {
        /* e.g. IMPORT PROLOG.ANCESTOR → references PROLOG_ANCESTOR_alpha */
        A("; extern  %s_%s_alpha  (resolved by linker)\n",
          ie->lang, ie->name);
    }
    if (prog->imports) A("\n");
}
```

#### 5c. `emit_named_def()` — static-by-default

Find the function that emits DEFINE bodies (currently emits `.globl` unconditionally
for all named patterns). Change to: **only emit `.globl` if the name is in the export list.**

```c
/* In emit_named_def(), before emitting alpha_FUNCNAME label: */
static int is_exported(Program *prog, const char *name) {
    for (ExportEntry *e = prog->exports; e; e = e->next)
        if (strcmp(e->name, name) == 0) return 1;
    return 0;
}

/* Then in the emit loop, replace unconditional .globl with: */
if (is_exported(prog, def->name)) {
    A(".globl  SNOBOL4_%s_alpha\n", def->name);
    /* gamma and omega already covered by emit_exports() */
}
/* Label itself uses mangled name when exported, raw name when static: */
if (is_exported(prog, def->name))
    asmL("SNOBOL4_%s_alpha", def->name);
else
    asmL("alpha_%s", def->name);
```

---

### Step 6 — Driver: `-c` flag (45 min)

In `src/driver/main.c`, add:

```c
/* Flag: compile only (do not link or run) */
static int flag_compile_only = 0;    /* -c */
static int flag_backend_jvm  = 0;    /* --jvm */
static int flag_backend_net  = 0;    /* --net */

/* After emitting .s file, if -c: */
if (flag_compile_only) {
    /* Derive .o name from .s name */
    char obj_path[PATH_MAX];
    snprintf(obj_path, sizeof obj_path, "%s.o", base_name);
    /* Invoke system assembler */
    char cmd[PATH_MAX * 2];
    snprintf(cmd, sizeof cmd, "as -o %s %s", obj_path, asm_path);
    int rc = system(cmd);
    if (rc != 0) {
        fprintf(stderr, "sno2c: assembler failed (exit %d)\n", rc);
        exit(1);
    }
    fprintf(stderr, "sno2c: wrote %s\n", obj_path);
    exit(0);
}
```

**Invocation model after this sprint:**
```bash
sno2c -c hello.sno          # → hello.sno.o  (compile only)
sno2c hello.sno             # → a.out        (compile + link + run, existing)
sno2c --jvm hello.sno       # → Hello.class  (stub, Sprint 3)
```

---

### Step 7 — Acceptance Test (1 hr)

Create `test/linker/` directory with two files:

**`test/linker/greet_lib.sno`** — the library:
```snobol4
        EXPORT  GREET

        DEFINE('GREET(NAME)')          :(GREET_END)
GREET   OUTPUT = 'Hello, ' NAME        :(RETURN)
GREET_END
        END
```

**`test/linker/greet_main.sno`** — the caller:
```snobol4
        IMPORT  SNOBOL4.GREET

        GREET('World')
        END
```

**Build and test script `test/linker/run.sh`:**
```bash
#!/bin/bash
set -e
BIN=../../src/sno2c/sno2c

$BIN -c greet_lib.sno
$BIN -c greet_main.sno

# Link with ld (or gcc for convenience — pulls in libc)
gcc -o greet_test greet_main.sno.o greet_lib.sno.o \
    -L../../src/runtime/snobol4 -lsnobol4

./greet_test
```

**Expected output:**
```
Hello, World
```

**Milestone fires when:** `./run.sh` exits 0 and output matches expected.

---

## Regression Protocol

After **every** change, before committing:

```bash
# Full ASM corpus — must stay 106/106
cd /path/to/snobol4x && make test-asm 2>&1 | tail -5

# Quick smoke: hello via existing path (no -c flag)
echo "OUTPUT = 'hi'" | sno2c /dev/stdin
```

If either breaks: **revert, do not push, diagnose before continuing.**

---

## Known Risks This Sprint

**R1 — `.globl` placement:** NASM requires `.globl` before the label definition.
Our current emitter may emit the section header before `.globl`. Fix: call
`emit_exports()` and `emit_import_externs()` at the top of the emitter, before
any `.text` section content.

**R2 — Name collision between exported and static symbols:** If `EXPORT GREET`
is declared and there is also a static `DEFINE('GREET()')` in another file,
the linker will see two `SNOBOL4_GREET_alpha` symbols and error. This is
correct behavior — document it as a compile error to catch in Sprint 2.

**R3 — `as` not on PATH:** The CI environment may not have GNU `as`. Check
with `which as || apt-get install binutils`. If missing, `-c` emits `.s` only
and prints a warning.

---

## Commit Protocol

```
LP-2: M-LINK-X64-1 — EXPORT/IMPORT parse + x64 .globl emit

- src/runtime/snobol4/snoVal.h  NEW: canonical SnoVal (ABI §1)
- src/frontend/snobol4/lex.h    ADD: T_EXPORT, T_IMPORT
- src/frontend/snobol4/lex.c    ADD: keyword recognition
- src/frontend/snobol4/parse.c  ADD: parse_toplevel_directive()
- src/frontend/snobol4/sno2c.h  ADD: ExportEntry, ImportEntry, Program fields
- src/backend/x64/emit_byrd_asm.c ADD: emit_exports(), emit_import_externs()
                                  CHANGE: static-by-default in emit_named_def()
- src/driver/main.c             ADD: -c flag → produce .o via as
- test/linker/                  NEW: greet_lib.sno + greet_main.sno + run.sh

Regression: 106/106 ASM corpus green.
M-LINK-X64-1 ✅  M-LINK-X64-2 ✅  M-LINK-X64-3 ✅
Acceptance test: test/linker/run.sh → "Hello, World"
```

---

## After This Sprint: What Opens

With M-LINK-X64-1 through X64-3 green and the acceptance test passing, the
following become unblocked in parallel:

- **M-LINK-X64-4** — two-file SNOBOL4 link with a non-trivial program (wordcount)
- **M-LINK-JVM-1** — EXPORT/IMPORT in `emit_byrd_jvm.c` (same pattern, JVM syntax)
- **ABI doc freeze** — circulate `ARCH-scrip-abi.md` for final review; one session to resolve open questions before Sprint 2

---

*SESSION-linker-sprint1.md — pickup document for LP-2.*  
*Next session reads this file + ARCH-scrip-abi.md. Do not read other ARCH docs unless hitting an unfamiliar construct.*
