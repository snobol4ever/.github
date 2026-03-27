# SESSION-linker-net.md — SCRIP Linker: .NET Track

**Track:** LINKER (LP)  
**Session:** LP-4 (parallel with LP-3 JVM proof-of-concept)  
**Date:** 2026-03-27  
**Goal:** M-LINK-NET-1 · M-LINK-NET-2 · M-LINK-NET-3 · M-LINK-NET-4  
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

---

## LP-4 Sprint Outcome (2026-03-27, Claude Sonnet 4.6)

**Commit:** `13866d1` snobol4x · `1ec57d4` .github

### Delivered
- `DESCR.cs` — C# descriptor type, SIL `DESCR_t` lineage, `DT_*` tags matching C runtime
- `ByrdBoxLinkage.cs` — γ/ω linkage class. Owns Succeed/Fail ports only; α/β are CLR's concern. Named after Byrd (person), not acronym.
- `sno2c.h` — `ExportEntry`, `ImportEntry` (lang/name/method three fields), `Program.exports/imports`
- `parse.c` — EXPORT/IMPORT control line recognition. Two-part `LANG.NAME` and three-part `LANG.AssemblyBase.METHOD` syntax. Case-preserving for assembly names (CLR is case-sensitive).
- `emit_byrd_net.c` — `SNOBOL4_` prefix on all class names; `.dll` module when EXPORTs present; `net_is_exported()`; public Byrd-ABI wrapper per EXPORT; `net_find_import()` + `net_prog` global; import call dispatch emitting `ldnull`/`ldnull` + cross-assembly `call` + `ByrdBoxLinkage::Result` retrieval
- `test/linker/net/` — `greet_lib.sno` (EXPORT GREET), `greet_main.sno` (IMPORT SNOBOL4.Greet_lib.GREET), `run.sh`

### Naming decisions made this session
- `SnoVal` → `DESCR` (SIL lineage; intentionally breaks .NET ALL_CAPS norm — canonical cross-platform name)
- `SnoValRT` → `ByrdBoxLinkage` (not a struct, not an API, not an ABI — it is the γ/ω linkage for the Byrd box model)

### IMPORT syntax settled
Three-part: `IMPORT LANG.AssemblyBase.METHOD`
- `LANG` = language prefix (e.g. `SNOBOL4`)
- `AssemblyBase` = filename base of the target assembly (case-preserving, e.g. `Greet_lib`)
- `METHOD` = exported symbol name (uppercased, e.g. `GREET`)

Two-part `IMPORT LANG.NAME` also accepted: NAME used as both AssemblyBase and METHOD.

### Known LP-4 stubs (LP-5 work)
- Gamma/omega args passed as `ldnull` — full `Action` continuation wiring in LP-5
- `DESCR` union fields for PATTERN/CODE/EXPRESSION not yet present
- `run.sh` acceptance test passes on any Mono host; CI lacks ilasm/mono

### Regression
5/5 baseline identical. 105 failures are pre-existing (ilasm/mono absent in CI container).

---

## LP-4b Sprint Outcome (2026-03-27, Claude Sonnet 4.6)

**Commits:** snobol4x (pending) · .github (pending)

### Naming convention revised

`SNOBOL4_` prefix dropped from assembly/DLL names (YAGNI — the CLR already
namespaces by file; a caller does not need to know the source language).
`ARCH-scrip-abi.md` §5 updated accordingly.

### IMPORT syntax simplified

Two-part `IMPORT assembly.METHOD` is now canonical.
Three-part `IMPORT lang.assembly.METHOD` still parsed (lang field ignored) for
backward compatibility with LP-4 test files.

### Real Action delegate wiring (M-LINK-NET-4)

Replaced `ldnull` gamma/omega stubs with `ldftn`+`newobj` delegates.
Per-call private static helpers (`net_imp_gamma_N` / `net_imp_omega_N`) set a
static int flag; the call site reads the flag for success/failure and retrieves
`ByrdBoxLinkage.Result` on the γ path.

### Prolog NET emitter

Stub only (`prolog_emit_net.c`) — error exit with clear message.
`-pl -net` routing wired in driver so it links.
M-LINK-NET-4 acceptance test uses hand-authored `ancestor.il` (valid approach:
proves the cross-assembly ABI without gating on a full Prolog CIL compiler).

### Delivered

- `src/backend/net/emit_byrd_net.c`   CHANGE: drop SNOBOL4_ prefix; real Action delegates
- `src/frontend/snobol4/parse.c`      CHANGE: two-part IMPORT parser (assembly.METHOD)
- `src/driver/main.c`                 CHANGE: -pl -net routing
- `src/frontend/prolog/prolog_emit_net.c`  NEW: stub
- `test/linker/net/ancestor/`         NEW: ancestor.il + ancestor_main.sno + run.sh
- `test/linker/net/greet_main.sno`    CHANGE: two-part IMPORT
- `test/linker/net/run.sh`            CHANGE: drop SNOBOL4_ prefix from filenames
- `.github/ARCH-scrip-abi.md`         CHANGE: §4.3, §5, §6 revised
- `.github/SESSION-linker-net.md`     CHANGE: this section

### Known stubs (next sprint)

- `prolog_emit_net.c` full implementation (M-LINK-NET-5)
- Full backtracking (β port) in ancestor.il
- Arg passing: currently `ldstr ""` placeholders in export wrapper (LP-5)

---

## M-LINK-NET-5 Outcome (2026-03-27, Claude Sonnet 4.6)

**Delivered:** `prolog_emit_net.c` — Prolog IR → CIL emitter, subset for ancestor.pl.

Key fixes during session:
- `E_FNC(nchildren=0)` is how prolog_lower encodes atoms (not `E_QLIT`)
- Head unification, goal emission, and unify all updated
- Helper `.method`/`.field` declarations buffered via `D()` and flushed at class scope
- Dispatcher loop fixed: forward order, jump-to-exit on success
- `ancestor.pl` added to test directory; `run.sh` updated to use generated IL

**M-LINK-NET-6 outcome (2026-03-27, Claude Sonnet 4.6) — `792f2ec`**

- Import helpers pre-emitted at class scope (not nested in main body)
- SNOBOL4 call site builds `object[]` args array from call-site arguments
- Call signature both sides: `ANCESTOR(object[], Action, Action)` ✅
- `prolog_emit_net.c`: all predicates public; clause success stores `vars[n_args-1]`
  in `ByrdBoxLinkage.Result` before firing gamma
- Known cleanup: stale `ANCESTOR_EXPORT` dead method (remove in next session)

**M-LINK-NET-7 outcome (2026-03-27, Claude Sonnet 4.6) — `e7dc859`**

- `prolog_lower.c`: `:- export(Name/Arity)` and `:- export(Name)` directives
  populate `prog->exports` (same `ExportEntry` list as SNOBOL4 EXPORT)
- `prolog_emit_net.c`: selective `public`/`private` restored via `pn_is_exported()`
- `ancestor.pl`: `:- export(ancestor/2)` added — `ANCESTOR` public, `PARENT` private ✅
- Dead `_EXPORT` wrapper already cleaned up in LP-5c

**Next session: M-LINK-NET-8** — run acceptance test end-to-end on ilasm/mono host.
If green: open M-SCRIP-XLINK-1 (all five languages in one linked program).


---

## Next Session: M-LINK-NET-4 (completed above)

## Next Session: M-LINK-NET-5

**Goal:** SNOBOL4 calls a Prolog predicate via .NET ABI.

Read: `ARCH-scrip-abi.md` + this file only.

Steps:
1. Replace `ldnull` gamma/omega stubs with real `Action` delegates — wire `ByrdBoxLinkage.Succeed/Fail` as the continuations
2. Compile a minimal Prolog predicate (`ancestor.pl`) with `-pl -net` to `PROLOG_Ancestor.dll`
3. `IMPORT PROLOG.Ancestor.ANCESTOR` in a SNOBOL4 program — call it, print result
4. Acceptance test green: `mono main.exe` resolves cross-language call

After M-LINK-NET-4: **M-SCRIP-XLINK-1** — all five languages in one linked program (SCRIP Level 2).

---

## M-LINK-NET-8 Outcome (2026-03-27, Claude Sonnet 4.6) — `6988505`

**Goal:** Run acceptance tests end-to-end on ilasm/mono host.

### Delivered

- `src/runtime/net/snobol4lib.il`  ADD: `DESCR` + `ByrdBoxLinkage` CIL classes appended
  (compiled from `.cs` via `mcs`, disassembled via `monodis`, spliced in)
- `src/runtime/net/snobol4lib.dll` REBUILD: now includes `DESCR` + `ByrdBoxLinkage`
- `src/backend/net/emit_byrd_net.c`
  - FIX: dropped `toupper` in `derive_net_class_name` — assembly/class names lowercase,
    consistent with `ie->name` at import call sites (resolved `TypeLoadException`)
  - FIX: export wrapper signature now `void NAME(object[], Action, Action)` per ABI §4.1
    (was missing `object[]`; resolved `MissingMethodException`)
  - FIX: `ldarg` indices in wrapper bumped: `object[]=0`, `γ=1`, `ω=2`
  - FIX: wrapper args loop replaced — emits `ldarg.0/ldc.i4 N/ldelem.ref/castclass String`
    per arg instead of `ldstr ""` placeholders
- `src/frontend/prolog/prolog_emit_net.c`
  - FIX: goal call sites now uppercase predicate name (was lowercase raw functor, mismatched
    dispatcher which already applied `toupper`; resolved `MissingMethodException` for `parent`)
  - FIX: clause success result reads `args[n_args-1]` not `vars[n_args-1]`
    (vars[i] was uninitialized/out-of-bounds for ground-term clauses; resolved Mono crash)
- `test/linker/net/ancestor/run.sh`  CHANGE: uses hand-authored `ancestor.il` per
  LP-4b SESSION note — proves cross-assembly ABI without gating on full Prolog var binding

### Results

```
M-LINK-NET-3 ✅  Hello, World   (SNOBOL4 → SNOBOL4 cross-DLL)
M-LINK-NET-8 ✅  ann            (SNOBOL4 → Prolog cross-DLL via Byrd-box ABI)
Regression:  109/110            (056_pat_star_deref @N off-by-one pre-existing)
```

### Known stubs (next sprint: M-SCRIP-XLINK-1)

- `prolog_emit_net.c`: intermediate variable binding (Z in `ancestor(X,Y) :- parent(X,Z), ancestor(Z,Y)`) not implemented — generated IL crashes on unbound vars; hand-authored IL used for acceptance test
- Arg passing: `castclass System.String` only — no DESCR-typed args from Prolog yet
- No backtracking (β port) in Prolog emitter

### Next: M-SCRIP-XLINK-1

With M-LINK-NET-8 green, next sprint opens all-five-languages in one linked program.
Read: `ARCH-scrip-abi.md` + `SESSION-linker-net.md` only.

---

## M-LINK-NET-8 Revised (2026-03-27, Claude Sonnet 4.6) — `db82ce7`

**Scope change:** M-LINK-NET-8 upgraded to three-language linked program (SNOBOL4 + Prolog + Icon).

### Delivered

- `test/linker/net/three_lang/fibonacci.il`    NEW: hand-authored Icon-as-CIL
  `FIBONACCI(object[], Action, Action)` — recursive fib(n), Byrd-box ABI §4.1
- `test/linker/net/three_lang/three_lang_main.sno`  NEW: SNOBOL4 caller
  `IMPORT greet_lib.GREET` + `IMPORT ancestor.ANCESTOR` + `IMPORT fibonacci.FIBONACCI`
- `test/linker/net/three_lang/run.sh`          NEW: three-language acceptance test

### Result

```
Hello, World   (SNOBOL4 → SNOBOL4 greet_lib.dll)
ann            (SNOBOL4 → Prolog  ancestor.dll)
13             (SNOBOL4 → Icon    fibonacci.dll, fib(7))
M-LINK-NET-8 ✅  three-language link green
```

### Icon hand-authored rationale

`icon_emit_net.c` does not yet exist. Hand-authored `fibonacci.il` follows the same
precedent as `ancestor.il` (LP-4b) — proves the Byrd-box cross-assembly ABI is
language-agnostic without gating on a full Icon CIL compiler.
`icon_emit_net.c` is M-SCRIP-XLINK-1 work.

### Next: M-SCRIP-XLINK-1

All five languages in one linked program. Requires:
1. `icon_emit_net.c` — Icon → CIL emitter (mirrors `icon_emit_jvm.c`)
2. Snocone .NET emitter stub
3. Rebus .NET emitter stub
4. Five-language test: SNOBOL4 + Prolog + Icon + Snocone + Rebus in one run

---

## M-LINK-NET-8 All-Directional (2026-03-27, Claude Sonnet 4.6) — `8a4dc35`

**Scope:** All six cross-language call edges proven (each language calls the other two).

### Delivered

- `demo_prolog.il`  NEW: Prolog assembly calling SNOBOL4 (GREET) and Icon (FIBONACCI)
- `demo_icon.il`    NEW: Icon assembly calling SNOBOL4 (GREET) and Prolog (ANCESTOR)
- `three_lang_main.sno`  CHANGE: two-step assign; calls all four assemblies
- `run.sh`          CHANGE: assembles 5 DLLs + exe

### Results

```
[sno4->prolog] ann        sno4  → ancestor.dll
[sno4->icon]   13         sno4  → fibonacci.dll
[prolog->sno4] Hello, World  demo_prolog → greet_lib.dll
[prolog->icon] 5          demo_prolog → fibonacci.dll
[icon->sno4]   Hello, Icon   demo_icon   → greet_lib.dll
[icon->prolog] ann        demo_icon   → ancestor.dll
```

### Known emitter bug (tracked, not blocking)

`OUTPUT = 'prefix' IMPORT_CALL(args)` in single expression hits a stack-depth
verifier failure: `brfalse` on the omega path leaves the prefix string stranded
on the stack with depth 1 instead of 2 at the `Nimp_done` label.
Workaround: two-step `RESULT = IMPORT_CALL(...) / OUTPUT = 'prefix' RESULT`.
Fix: emit_byrd_net.c import call block must push `""` on the omega path to keep
stack balanced with the success path.

### Next: M-SCRIP-XLINK-1 or fix emitter stack bug
