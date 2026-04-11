# SESSION-linker-sprint1.md — SCRIP Linker Sprint 1

**Track:** LINKER (LP)  
**Session:** LP-2 (this doc written LP-1)  
**Date:** 2026-03-27 (revised: JVM before x64)  
**Goal:** M-LINK-JVM-1 · M-LINK-JVM-2 · M-LINK-JVM-3  
**Gate:** Read `GENERAL-SCRIP-ABI.md` before touching any code.

---

## Why JVM First

JVM and .NET already have object file infrastructure. `.class` is an object format
with a built-in symbol table. The JVM classloader **is** the linker — free, correct,
and already installed. `EXPORT` becomes `public static`. `IMPORT` becomes a foreign
class reference resolved at load time. Zero ELF relocation logic. Zero `ld` invocation.

x64 comes after — once the pattern is proven on JVM, the x64 ELF work is mechanical.

**Sprint order:**

| Sprint | Milestones | Depends on |
|--------|-----------|------------|
| LP-2 (this) | M-LINK-JVM-1,2,3 — EXPORT/IMPORT in JVM, per-file .class, two-file SNOBOL4 link | ABI frozen |
| LP-3 | M-LINK-JVM-4,5 — **PROOF OF CONCEPT**: SNOBOL4 calls Prolog, SNOBOL4 calls Icon | LP-2 green |
| LP-4 | M-LINK-NET-1,2,3 — same pattern, .NET | LP-2 green (parallel) |
| LP-5 | M-LINK-X64-1..4 — x64 last, informed by JVM lessons | LP-3 green |

---

## Session Objective

By end of Sprint 1 (LP-2):

1. `GENERAL-SCRIP-ABI.md` reviewed, any issues resolved, marked **FROZEN**
2. `EXPORT` / `IMPORT` parsed in `src/frontend/snobol4/parse.c`
3. `EXPORT NAME` emitted as `public static` method in Jasmin output
4. Non-exported DEFINEs emitted as `private static` (static-by-default)
5. Each `.sno` file → its own named `.class` (not monolithic `SnobolProg`)
6. **Acceptance test green:** `greet_lib.sno` exports `GREET`, `greet_main.sno`
   imports and calls it, `java` runs and prints `Hello, World`

Regression invariant: `1896 tests / 0 failures` on snobol4jvm throughout.

---

## File Map — What We Touch

```
src/frontend/snobol4/
    lex.c               ADD: T_EXPORT, T_IMPORT token kinds
    lex.h               ADD: token kind enum entries
    parse.c             ADD: parse_toplevel_directive()
    scrip-cc.h             ADD: ExportEntry, ImportEntry fields on Program struct

src/backend/jvm/
    emit_byrd_jvm.c     CHANGE: class name from hardcoded → derived from filename
                        ADD: jvm_is_exported(), public/private static dispatch
                        ADD: emit_jvm_import_call() — invokestatic for IMPORTs

src/runtime/snobol4/
    snoVal.h            NEW: canonical C SnoVal definition (ABI §1)

src/runtime/jvm/
    SnoVal.java         NEW: JVM SnoVal stub (full impl LP-3)

src/driver/
    main.c              ADD: --jvm flag routes to JVM emitter
                        ADD: -c flag → compile to .class via jasmin.jar, do not run
```

---

## Step-by-Step

### Step 1 — snoVal.h (20 min)

Create `src/runtime/snobol4/snoVal.h`:

```c
/* snoVal.h — canonical SCRIP value type. ABI-stable.
 * Java equivalent: src/runtime/jvm/SnoVal.java (LP-3 full impl). */
#ifndef SNOVAL_H
#define SNOVAL_H
#include <stddef.h>

typedef enum {
    SV_STRING=0, SV_INTEGER=1, SV_REAL=2,
    SV_PATTERN=3, SV_TABLE=4, SV_ARRAY=5, SV_UNDEF=6
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

#endif
```

### Step 2 — SnoVal.java stub (20 min)

Create `src/runtime/jvm/SnoVal.java`:

```java
/* SnoVal.java — SCRIP universal value type for JVM.
 * Sprint 1 stub. Full union fields + SnoValRT added LP-3.
 * Ref: GENERAL-SCRIP-ABI.md §1, §3. */
public class SnoVal {
    public static final int SV_STRING=0, SV_INTEGER=1, SV_REAL=2,
                             SV_PATTERN=3, SV_TABLE=4, SV_ARRAY=5, SV_UNDEF=6;
    public int    tag;
    public String s;
    public long   i;
    public double r;

    public SnoVal(String s) { this.tag = SV_STRING;  this.s = s; }
    public SnoVal(long   i) { this.tag = SV_INTEGER; this.i = i; }
    public SnoVal(double r) { this.tag = SV_REAL;    this.r = r; }

    /* Thread-local result slot — ABI §3.2 */
    public static final ThreadLocal<SnoVal> RESULT = new ThreadLocal<>();
}
```

### Step 3 — Lex tokens (30 min)

`lex.h` — add after existing token kinds:
```c
T_EXPORT,   /* EXPORT — statement-level directive */
T_IMPORT,   /* IMPORT — statement-level directive */
```

`lex.c` — in keyword recognition alongside `DEFINE`, `END`:
```c
if (strcmp(word, "EXPORT") == 0) return T_EXPORT;
if (strcmp(word, "IMPORT") == 0) return T_IMPORT;
```

**Scope:** Statement-level only. In pattern body/goto fields these remain identifiers.
Existing programs using `EXPORT`/`IMPORT` as variable names are unaffected.

### Step 4 — AST + Program struct (30 min)

`scrip-cc.h`:
```c
STMT_EXPORT,
STMT_IMPORT,

typedef struct ExportEntry { char *name; struct ExportEntry *next; } ExportEntry;
typedef struct ImportEntry {
    char *lang;   /* "PROLOG", "ICON", "SNOBOL4", "SNOCONE", "REBUS" */
    char *name;
    struct ImportEntry *next;
} ImportEntry;

/* Add to Program struct: */
ExportEntry *exports;
ImportEntry *imports;
```

### Step 5 — Parser (45 min)

`parse.c`:
```c
static Stmt *parse_toplevel_directive(Lex *lx, Program *prog) {
    Token t = lex_next(lx);          /* T_EXPORT or T_IMPORT */
    skip_ws(lx);
    Token name_tok = lex_next(lx);
    if (name_tok.kind != T_IDENT) {
        parse_error(lx, "EXPORT/IMPORT: expected identifier"); return NULL;
    }
    if (t.kind == T_EXPORT) {
        ExportEntry *e = xmalloc(sizeof *e);
        e->name = xstrdup(name_tok.text); e->next = prog->exports; prog->exports = e;
        return make_stmt(STMT_EXPORT, name_tok.text);
    }
    /* IMPORT: LANG.NAME  or  bare NAME (defaults to SNOBOL4) */
    ImportEntry *ie = xmalloc(sizeof *ie);
    if (lex_peek(lx).kind == T_DOT) {
        lex_next(lx);
        Token sym = lex_next(lx);
        ie->lang = xstrdup(name_tok.text);
        ie->name = xstrdup(sym.text);
    } else {
        ie->lang = xstrdup("SNOBOL4");
        ie->name = xstrdup(name_tok.text);
    }
    ie->next = prog->imports; prog->imports = ie;
    return make_stmt(STMT_IMPORT, ie->name);
}
```

### Step 6 — JVM Emitter (2 hr — core work)

**6a. Per-file class name** — replace hardcoded `"SnobolProg"`:

```c
static char *derive_jvm_class_name(const char *src_path) {
    const char *base = strrchr(src_path, '/');
    base = base ? base + 1 : src_path;
    char *name = xstrdup(base);
    char *dot = strrchr(name, '.'); if (dot) *dot = '\0';
    char *result = xmalloc(strlen(name) + 10);
    sprintf(result, "SNOBOL4_%s", name);   /* e.g. "SNOBOL4_greet_lib" */
    free(name); return result;
}
```

**6b. Export predicate + visibility dispatch**:

```c
static int jvm_is_exported(Program *prog, const char *name) {
    for (ExportEntry *e = prog->exports; e; e = e->next)
        if (strcmp(e->name, name) == 0) return 1;
    return 0;
}

/* In method header emission — replace current ".method public static" with: */
const char *visibility = jvm_is_exported(prog, def->name)
                         ? "public" : "private";
J(".method %s static %s([Ljava/lang/Object;Ljava/lang/Runnable;Ljava/lang/Runnable;)V\n",
  visibility, def->name);
```

Sprint 1 uses `Object[]` as stand-in for `SnoVal[]`. Descriptor tightens in LP-3
once `SnoVal.class` is on the classpath.

**6c. Import call site** — when emitting a call to an imported name:

```c
static void emit_jvm_import_call(FILE *out, ImportEntry *ie) {
    /* Pushes args, gamma, omega already on stack by caller convention */
    fprintf(out,
        "    invokestatic %s_%s/%s"
        "([Ljava/lang/Object;Ljava/lang/Runnable;Ljava/lang/Runnable;)V\n",
        ie->lang, ie->name, ie->name);
}
```

### Step 7 — Driver flags (30 min)

`main.c`:
```c
static int flag_compile_only = 0;  /* -c */
static int flag_jvm          = 0;  /* --jvm */

/* After emitting .j Jasmin text, if --jvm -c: */
if (flag_jvm && flag_compile_only) {
    char cmd[512];
    snprintf(cmd, sizeof cmd,
        "java -jar %s/jasmin.jar %s -d %s",
        jasmin_dir, jasmin_path, output_dir);
    if (system(cmd) != 0) { fprintf(stderr, "jasmin failed\n"); exit(1); }
}
```

### Step 8 — Acceptance Test (30 min)

`test/linker/jvm/greet_lib.sno`:
```snobol4
        EXPORT  GREET

        DEFINE('GREET(NAME)')          :(GREET_END)
GREET   OUTPUT = 'Hello, ' NAME        :(RETURN)
GREET_END
        END
```

`test/linker/jvm/greet_main.sno`:
```snobol4
        IMPORT  SNOBOL4.GREET

        GREET('World')
        END
```

`test/linker/jvm/run.sh`:
```bash
#!/bin/bash
set -e
SCRIP_CC=../../../src/scrip-cc/scrip-cc
JASMIN=../../../src/backend/jvm/jasmin.jar
OUT=./out ; mkdir -p $OUT

$SCRIP_CC --jvm greet_lib.sno  > $OUT/SNOBOL4_greet_lib.j
$SCRIP_CC --jvm greet_main.sno > $OUT/SNOBOL4_greet_main.j
java -jar $JASMIN $OUT/SNOBOL4_greet_lib.j  -d $OUT
java -jar $JASMIN $OUT/SNOBOL4_greet_main.j -d $OUT

RESULT=$(java -cp $OUT SNOBOL4_greet_main)
[ "$RESULT" = "Hello, World" ] \
    && echo "M-LINK-JVM-3 ✅  $RESULT" \
    || { echo "M-LINK-JVM-3 ❌  got: '$RESULT'"; exit 1; }
```

**M-LINK-JVM-3 fires when `run.sh` exits 0.**

---

## Regression Protocol

After every change, before committing:
```bash
# snobol4jvm — must stay 1896/0
cd snobol4jvm && lein test 2>&1 | tail -3

# Existing JVM path still emits valid Jasmin (class name change is the risk)
echo "OUTPUT = 'smoke'" | scrip-cc --jvm /dev/stdin | grep "class SNOBOL4_"
```

---

## Commit Message Template

```
LP-2: M-LINK-JVM-1,2,3 — EXPORT/IMPORT JVM, per-file .class, two-file link

- src/runtime/snobol4/snoVal.h      NEW: canonical C SnoVal (ABI §1)
- src/runtime/jvm/SnoVal.java       NEW: JVM SnoVal stub (full LP-3)
- src/frontend/snobol4/lex.h/.c     ADD: T_EXPORT, T_IMPORT
- src/frontend/snobol4/parse.c      ADD: parse_toplevel_directive()
- src/frontend/snobol4/scrip-cc.h      ADD: ExportEntry, ImportEntry, Program fields
- src/backend/jvm/emit_byrd_jvm.c   CHANGE: per-file class name (SNOBOL4_basename)
                                    ADD: public/private static dispatch on EXPORT
                                    ADD: emit_jvm_import_call() invokestatic
- src/driver/main.c                 ADD: --jvm -c flags
- test/linker/jvm/                  NEW: greet_lib.sno + greet_main.sno + run.sh

Regression: 1896/0 snobol4jvm green.
M-LINK-JVM-1 ✅  M-LINK-JVM-2 ✅  M-LINK-JVM-3 ✅
Acceptance: test/linker/jvm/run.sh → "Hello, World"
```

---

## What LP-3 Opens (the big one)

**M-LINK-JVM-4 — SNOBOL4 calls a Prolog predicate.** This is the proof-of-concept.

Requires:
- `SnoVal.java` fully implemented + `SnoValRT.java` with `ThreadLocal<SnoVal> RESULT`
- Prolog JVM emitter updated: `EXPORT` → `public static` with ABI signature
- A Prolog file `ancestor.pl` with `EXPORT ANCESTOR` → compiles to `PROLOG_ANCESTOR.class`
- A SNOBOL4 file with `IMPORT PROLOG.ANCESTOR` → `invokestatic PROLOG_ANCESTOR/ANCESTOR`
- Integration test: SNOBOL4 hands a string to Prolog, Prolog unifies, returns via γ

When M-LINK-JVM-4 passes: **every other cross-language combination is a variation
on this same pattern.** SCRIP Level 2 is real.

---

*SESSION-linker-sprint1.md — revised 2026-03-27: JVM → .NET → x64 order.*  
*Next session reads this file + GENERAL-SCRIP-ABI.md only. Do not read other ARCH docs unless hitting an unfamiliar construct.*
