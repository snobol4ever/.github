# SESSION-linker-net.md — SCRIP Linker: .NET Track

**Track:** LINKER (LP)  
**Session:** LP-4 (parallel with LP-3 JVM proof-of-concept)  
**Date:** 2026-03-27  
**Goal:** M-LINK-NET-1 · M-LINK-NET-2 · M-LINK-NET-3  
**Gate:** Read `ARCH-scrip-abi.md` before touching any code.

---

## Two .NET Tracks — Know Which One You're In

| Track | Repo | Emitter | Owner | Linker relevance |
|-------|------|---------|-------|-----------------|
| **TINY NET** | snobol4x | `src/backend/net/emit_byrd_net.c` | Lon | **This sprint** — add EXPORT/IMPORT here |
| **DOTNET** | snobol4dotnet | Jeff's full C# runtime | Jeff | Later — Jeff's track, independent |

**This sprint targets TINY NET only.** Jeff's snobol4dotnet `@N` bug and M-NET-POLISH
are on a separate track and do not block this work.

---

## State Assessment (as of 2026-03-27)

### TINY NET emitter: well-positioned

`emit_byrd_net.c` is already at N-R4 (Byrd boxes in CIL: LIT/SEQ/ALT/ARBNO ✅).
It emits Mono CIL assembler (`.il` files) assembled by `ilasm`.

**Runtime DLL architecture already split** (N-201):
```
snobol4lib.dll  — all sno_* helpers
snobol4run.dll  — keyword state, I/O
```
This is exactly the right structure for adding a linker layer — the per-program
`.il` already references external assemblies. EXPORT/IMPORT is a small extension
of a pattern that already works.

**PLAN.md stale note:** The `TINY NET` row shows `M-T2-FULL` as next milestone,
but M-T2-FULL is already ✅ (fired N-248, `v-post-t2` tag cut). That row needs
updating. This sprint updates it.

### DOTNET (Jeff's track): independent

Status: 1911/1913, M-NET-SPITBOL-SWITCHES ✅, M-NET-POLISH ❌.
Blocking: `@N` cursor bug (79/80 crosscheck) — diagnosed D-164, fix pending D-165.
This does not block M-LINK-NET at all. Separate repo, separate session.

### Open issues in TINY NET that matter for linker

From BACKEND-NET.md:
- `cross` test: `@N` cursor off-by-one (105/106) — **not a linker blocker**
- Pattern.Bal hang — **not a linker blocker**
- The 110/110 NET corpus is already green (M-T2-NET ✅)

**Conclusion: TINY NET is ready for M-LINK-NET-1 through NET-3.**

---

## Session Objective

By end of this sprint:

1. `EXPORT NAME` in a `.sno` source → compiled CIL method is `.publics`
2. Non-exported DEFINEs → `.private` (static-by-default)  
3. Each `.sno` → its own named `.dll` assembly (not a monolithic `SnobolProg.exe`)
4. `IMPORT LANG.NAME` → `call` to external assembly method in emitted CIL
5. **Acceptance test green:** `greet_lib.sno` exports `GREET`, `greet_main.sno`
   imports and calls it, `mono greet_main.exe` prints `Hello, World`
6. PLAN.md `TINY NET` row updated: M-T2-FULL → M-LINK-NET-3

Regression invariant: `110/110` NET corpus throughout.

---

## CIL ABI (from ARCH-scrip-abi.md §4)

```csharp
// Every exported SCRIP procedure compiles to:
.method public static void FuncName(object[] args,
                                    class [mscorlib]System.Action gamma,
                                    class [mscorlib]System.Action omega) cil managed
```

- `object[]` is the Sprint 1 stand-in for `SnoVal[]` (full SnoVal.cs added LP-5)
- `Action` is `System.Action` — the .NET equivalent of JVM `Runnable`
- Non-exported methods use `.method private static`

**Thread-local result slot** (from ARCH-scrip-abi.md §4.2):
```csharp
// SnoValRT.cs (new file, src/runtime/net/)
public static class SnoValRT {
    [ThreadStatic] public static object Result;
    public static void Succeed(object v, System.Action gamma) {
        Result = v; gamma();
    }
    public static void Fail(System.Action omega) { omega(); }
}
```

**Cross-assembly call** (CIL syntax):
```
call void [PROLOG_ANCESTOR]PROLOG_ANCESTOR::ANCESTOR(object[],
          class [mscorlib]System.Action, class [mscorlib]System.Action)
```

---

## File Map — What We Touch

```
src/frontend/snobol4/
    lex.c / lex.h               (shared with JVM sprint — T_EXPORT/T_IMPORT already added)
    parse.c / sno2c.h           (shared — ExportEntry/ImportEntry already added)

src/backend/net/
    emit_byrd_net.c             CHANGE: class name → derived from filename, prefixed SNOBOL4_
                                ADD: net_is_exported() — public/private dispatch
                                ADD: emit_net_import_call() — cross-assembly call instruction
                                CHANGE: emit_named_def_net() — .publics / .private

src/runtime/net/
    SnoVal.cs                   NEW: C# SnoVal stub (mirrors SnoVal.java, LP-5 full impl)
    SnoValRT.cs                 NEW: ThreadStatic result slot + Succeed/Fail helpers

src/driver/
    main.c                      ADD: --net flag (if not already present from JVM sprint)
                                ADD: -c flag for .NET → invoke ilasm, produce .dll

test/linker/net/
    greet_lib.sno               NEW (same as JVM test — reuse)
    greet_main.sno              NEW (same as JVM test — reuse)
    run.sh                      NEW: ilasm + mono acceptance test
```

---

## Step-by-Step

### Step 1 — SnoVal.cs and SnoValRT.cs (30 min)

`src/runtime/net/SnoVal.cs`:
```csharp
// SnoVal.cs — SCRIP universal value type for .NET backend.
// Sprint 1 stub. Full union fields added LP-5.
// Ref: ARCH-scrip-abi.md §1, §4.
public class SnoVal {
    public const int SV_STRING=0, SV_INTEGER=1, SV_REAL=2,
                     SV_PATTERN=3, SV_TABLE=4, SV_ARRAY=5, SV_UNDEF=6;
    public int    Tag;
    public string S;
    public long   I;
    public double R;

    public SnoVal(string s) { Tag = SV_STRING;  S = s; }
    public SnoVal(long   i) { Tag = SV_INTEGER; I = i; }
    public SnoVal(double r) { Tag = SV_REAL;    R = r; }
}
```

`src/runtime/net/SnoValRT.cs`:
```csharp
// SnoValRT.cs — thread-local result slot for cross-language calls.
// ABI spec: ARCH-scrip-abi.md §4.2.
public static class SnoValRT {
    [System.ThreadStatic] public static SnoVal Result;

    public static void Succeed(SnoVal v, System.Action gamma) {
        Result = v;
        gamma();
    }
    public static void Fail(System.Action omega) {
        omega();
    }
}
```

Compile these into `snobol4lib.dll` (already referenced by every `.il`).
No change to existing programs — the new classes are additive.

### Step 2 — Per-file assembly name (30 min)

In `emit_byrd_net.c`, replace the hardcoded `"SnobolProg"` class name:

```c
/* "greet_lib.sno" → "SNOBOL4_greet_lib" */
static char *derive_net_class_name(const char *src_path) {
    const char *base = strrchr(src_path, '/');
    base = base ? base + 1 : src_path;
    char *name = xstrdup(base);
    char *dot = strrchr(name, '.'); if (dot) *dot = '\0';
    char *result = xmalloc(strlen(name) + 10);
    sprintf(result, "SNOBOL4_%s", name);
    free(name); return result;
}
```

The `.il` assembly directive:
```
.assembly SNOBOL4_greet_lib {}
.assembly extern snobol4lib {}
.assembly extern snobol4run {}
```

### Step 3 — Export predicate + visibility (45 min)

```c
static int net_is_exported(Program *prog, const char *name) {
    for (ExportEntry *e = prog->exports; e; e = e->next)
        if (strcmp(e->name, name) == 0) return 1;
    return 0;
}
```

In the method header emission (CIL `.method` directive):
```c
/* Replace current ".method public static" with: */
const char *vis = net_is_exported(prog, def->name) ? "public" : "private";
N(".method %s static void %s(object[], class [mscorlib]System.Action,"
  " class [mscorlib]System.Action) cil managed\n", vis, def->name);
```

### Step 4 — Import call site (45 min)

```c
static void emit_net_import_call(FILE *out, ImportEntry *ie) {
    /* Extern assembly reference at top of .il file: */
    fprintf(out, ".assembly extern %s_%s {}\n", ie->lang, ie->name);

    /* Call site (inline at use point): */
    fprintf(out,
        "call void [%s_%s]%s_%s::%s(object[],"
        " class [mscorlib]System.Action,"
        " class [mscorlib]System.Action)\n",
        ie->lang, ie->name,   /* assembly name */
        ie->lang, ie->name,   /* class name */
        ie->name);             /* method name */
}
```

`emit_net_import_call()` called wherever an IMPORT symbol is invoked in the
statement body — same call sites as where `invokestatic` is emitted in the JVM path.

### Step 5 — Driver `--net` flag (20 min)

```c
static int flag_net = 0;  /* --net */

/* After emitting .il, if --net -c: */
if (flag_net && flag_compile_only) {
    char cmd[512];
    snprintf(cmd, sizeof cmd,
        "ilasm %s /dll /output:%s.dll", il_path, class_name);
    if (system(cmd) != 0) { fprintf(stderr, "ilasm failed\n"); exit(1); }
    fprintf(stderr, "sno2c: wrote %s.dll\n", class_name);
}
```

**Invocation after this sprint:**
```bash
sno2c --net greet_lib.sno   > SNOBOL4_greet_lib.il
sno2c --net greet_main.sno  > SNOBOL4_greet_main.il
ilasm SNOBOL4_greet_lib.il  /dll /output:SNOBOL4_greet_lib.dll
ilasm SNOBOL4_greet_main.il /exe /output:greet_main.exe
mono greet_main.exe
```

### Step 6 — Acceptance test (30 min)

`test/linker/net/run.sh`:
```bash
#!/bin/bash
set -e
SNO2C=../../../src/sno2c/sno2c
OUT=./out ; mkdir -p $OUT

$SNO2C --net greet_lib.sno  > $OUT/SNOBOL4_greet_lib.il
$SNO2C --net greet_main.sno > $OUT/SNOBOL4_greet_main.il

ilasm $OUT/SNOBOL4_greet_lib.il  /dll /output:$OUT/SNOBOL4_greet_lib.dll
ilasm $OUT/SNOBOL4_greet_main.il /exe /output:$OUT/greet_main.exe

RESULT=$(mono $OUT/greet_main.exe)
[ "$RESULT" = "Hello, World" ] \
    && echo "M-LINK-NET-3 ✅  $RESULT" \
    || { echo "M-LINK-NET-3 ❌  got: '$RESULT'"; exit 1; }
```

Same `greet_lib.sno` / `greet_main.sno` as JVM test — reuse verbatim.

---

## Regression Protocol

```bash
# TINY NET corpus — must stay 110/110
cd snobol4x && make test-net 2>&1 | tail -5

# Existing .NET path still emits valid CIL (class name change is the risk)
echo "OUTPUT = 'smoke'" | sno2c --net /dev/stdin | grep "SNOBOL4_"
```

---

## PLAN.md Updates This Sprint

Two rows to update:

```
BEFORE:
| **TINY NET** | N-248 — 110/110 | `425921a` N-248 | M-T2-FULL |

AFTER:
| **TINY NET** | N-249 — M-LINK-NET-3 ✅ | `<new>` N-249 | M-LINK-NET-4 |
```

Also update SCRIP_DEMOS.md §LINKER Track: flip M-LINK-NET-1, NET-2, NET-3 to ✅.

---

## Commit Message Template

```
LP-4: M-LINK-NET-1,2,3 — EXPORT/IMPORT .NET, per-file .dll, two-file link

- src/runtime/net/SnoVal.cs         NEW: C# SnoVal stub (full LP-5)
- src/runtime/net/SnoValRT.cs       NEW: ThreadStatic result + Succeed/Fail
- src/backend/net/emit_byrd_net.c   CHANGE: per-file class name (SNOBOL4_basename)
                                    ADD: public/private static dispatch on EXPORT
                                    ADD: emit_net_import_call() cross-assembly call
- src/driver/main.c                 ADD: --net -c flags (if not already from LP-2)
- test/linker/net/                  NEW: greet_lib.sno + greet_main.sno + run.sh
- .github/PLAN.md                   UPDATE: TINY NET row (M-T2-FULL → M-LINK-NET done)
- .github/SCRIP_DEMOS.md            UPDATE: M-LINK-NET-1,2,3 → ✅

Regression: 110/110 NET corpus green.
M-LINK-NET-1 ✅  M-LINK-NET-2 ✅  M-LINK-NET-3 ✅
Acceptance: test/linker/net/run.sh → "Hello, World"
```

---

## What LP-5 Opens

With M-LINK-NET-3 green, the .NET proof-of-concept follows:

**M-LINK-NET-4 — SNOBOL4 calls a Prolog predicate via .NET ABI.**

Same structure as M-LINK-JVM-4. Once both JVM and .NET have the cross-language
POC, x64 (LP-5) is the final backend — informed by two working reference
implementations.

After that: **M-SCRIP-XLINK-1** — all five languages in one linked program.
That is SCRIP Level 2.

---

## Note on Jeff's DOTNET Track

Jeff's snobol4dotnet (`D-165` next) is **independent**. When M-NET-POLISH is
eventually done there, a separate linker session will add EXPORT/IMPORT to his
C# compiler pipeline using the same ABI contract — but different implementation
path (C# AST → MSIL, not the TINY sno2c pipeline). That session is not yet
written; file as future work once M-NET-POLISH clears.

---

*SESSION-linker-net.md — LP-4 pickup document.*  
*Next session reads this + ARCH-scrip-abi.md only.*  
*Do not read BACKEND-NET.md or other ARCH docs unless hitting an unfamiliar construct.*
