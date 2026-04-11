# GENERAL-SCRIP-ABI.md — SCRIP Cross-Language ABI

**Date:** 2026-03-27  
**Status:** DRAFT — Sprint 1 gate. No cross-language code until this is approved.  
**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6  

*This document is the critical-path gate for all linker work (M-LINK-*).*  
*No cross-language object file work begins until this is reviewed and frozen.*

---

## 0. The One Idea

Every procedure in every SCRIP language is a **Byrd Box** — a four-port machine:

```
         ┌─────────────────┐
  α ────▶│                 │────▶ γ   (success / continue)
         │   Byrd Box      │
  β ────▶│                 │────▶ ω   (failure / backtrack)
         └─────────────────┘
```

- **α** — entry port. Start execution.
- **β** — redo port. Backtrack into this box (retry).
- **γ** — exit port. Success; hand control forward.
- **ω** — fail port. Failure; hand control back.

This four-port model is **identical** for a SNOBOL4 pattern function, an Icon generator,
a Prolog predicate, and a Snocone rule. The ABI formalises how these ports map to
machine-level calling conventions on each backend, enabling direct cross-language calls
with no marshaling layer.

---

## 1. The Shared Value Type: SnoVal

All five languages pass and return `SnoVal`. SnoVal is the universal SCRIP value.

```c
/* snoVal.h — canonical definition, included by all backends */
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
        struct { const char *ptr; size_t len; } s;  /* STRING */
        long long i;                                 /* INTEGER */
        double    r;                                 /* REAL */
        void     *p;                                 /* PATTERN, TABLE, ARRAY */
    };
} SnoVal;
```

**Rule:** No type coercion crosses a language boundary. Both sides must agree on the
SnoVal tag. A Prolog predicate that expects `SV_INTEGER` will fail (ω) if handed `SV_STRING`.
Type coercion is the caller's responsibility, done in source before the call.

---

## 2. x64 ABI

### 2.1 Register Protocol

```
Entry (α port call):
  rdi  =  SnoVal*  args        — pointer to argument array (caller-allocated)
  rsi  =  int      nargs       — argument count
  rdx  =  void*    gamma_addr  — address to jump on success (γ)
  rcx  =  void*    omega_addr  — address to jump on failure (ω)
  r12  =  void*    env_frame   — caller's environment (callee must preserve)

On γ (success):
  rax  =  SnoVal*  result      — pointer to result value (callee-allocated, caller reads)
  then:  jmp [rdx]             — jump to gamma_addr

On ω (failure):
  rax  =  0
  then:  jmp [rcx]             — jump to omega_addr

Preserved across call (callee saves/restores):
  rbx, r12, r13, r14, r15, rbp

Scratch (callee may clobber):
  rax, rdi, rsi, rdx, rcx, r8, r9, r10, r11
```

### 2.2 Stack Frame

Each Byrd Box entry (α) establishes a private stack frame:

```asm
alpha_FUNCNAME:
    push    rbp
    mov     rbp, rsp
    sub     rsp, 64        ; local slots + alignment
    push    r12            ; save caller env
    ; ... body ...

gamma_FUNCNAME:
    pop     r12
    add     rsp, 64
    pop     rbp
    jmp     [rdx]          ; → caller's γ

omega_FUNCNAME:
    pop     r12
    add     rsp, 64
    pop     rbp
    jmp     [rcx]          ; → caller's ω
```

### 2.3 Redo (β port)

A box that supports backtracking (Icon generators, Prolog predicates with multiple
clauses) saves a **choice point** on first entry and restores it on β:

```
Choice point layout (pushed to stack at α):
  [rbp-8]   saved_rsi (nargs)
  [rbp-16]  saved_gamma_addr
  [rbp-24]  saved_omega_addr
  [rbp-32]  saved_state  (language-specific: Prolog trail head, Icon suspension frame, etc.)
```

The β port address is the label `beta_FUNCNAME`. Deterministic boxes (SNOBOL4 patterns
that match once) have no β; the β port address is the same as ω.

---

## 3. JVM ABI

### 3.1 Method Signature

Every exported SCRIP procedure compiles to a `public static` method:

```java
public static void FUNCNAME(SnoVal[] args, Runnable gamma, Runnable omega)
```

- `args` — argument array. Position 0 = first argument. Length = arity.
- `gamma` — continuation to invoke on success. Passes result via thread-local `SnoVal RESULT`.
- `omega` — continuation to invoke on failure.

**Why `Runnable` not return value?** Continuations model the α/β/γ/ω ports without
encoding success/failure in a return type. This matches the x64 jump-based model exactly.
The JVM stack handles depth; no trampolining required for straight-line chains.

### 3.2 Shared Thread-Local Result

```java
/* SnoValRT.java — runtime shared by all language backends */
public class SnoValRT {
    public static final ThreadLocal<SnoVal> RESULT = new ThreadLocal<>();
    
    public static void succeed(SnoVal v, Runnable gamma) {
        RESULT.set(v);
        gamma.run();
    }
    
    public static void fail(Runnable omega) {
        omega.run();
    }
}
```

### 3.3 Cross-Language Invocation

```java
// SNOBOL4 calling a Prolog predicate:
// IMPORT PROLOG.ANCESTOR
// In generated code:
PROLOG_ANCESTOR.ANCESTOR(args, gamma, omega);

// The Prolog compiler exports:
// EXPORT ANCESTOR
public class PROLOG_ANCESTOR {
    public static void ANCESTOR(SnoVal[] args, Runnable gamma, Runnable omega) {
        // Prolog unification + clause selection
    }
}
```

The JVM class loader resolves `PROLOG_ANCESTOR` at link time. No reflection. No dynamic
dispatch. Direct `invokestatic`.

### 3.4 Redo on JVM

Icon generators and Prolog predicates with multiple clauses use a **suspension object**:

```java
public interface Suspension { void resume(Runnable gamma, Runnable omega); }

// Generator returns suspension on first γ; caller invokes resume() for β
```

The suspension captures the generator's local state. This is the Icon `suspend`/`resume`
model made explicit.

---

## 4. .NET ABI

### 4.1 Method Signature

```csharp
public static void FuncName(SnoVal[] args, Action gamma, Action omega)
```

Identical semantic model to JVM. `Action` = `Runnable` equivalent.

### 4.2 Shared Result

```csharp
/* SnoValRT.cs */
public static class SnoValRT {
    [ThreadStatic] public static SnoVal Result;
    
    public static void Succeed(SnoVal v, Action gamma) {
        Result = v;
        gamma();
    }
    
    public static void Fail(Action omega) { omega(); }
}
```

### 4.3 Assembly Reference

```csharp
// In SNOBOL4 assembly (hello.dll):
// IMPORT ancestor.ANCESTOR
// (two-part: assembly name . method name — no language prefix)

// In generated MSIL:
.assembly extern ancestor {}
call void [ancestor]ancestor::ANCESTOR(SnoVal[], Action, Action)
```

---

## 5. Symbol Naming Convention

**Method names** use the exported symbol name verbatim (uppercased by convention).
**Assembly/DLL names** are the bare source basename — no language prefix.

```
Assembly:  {basename}          e.g. greet_lib.dll, ancestor.dll
Method:    {EXPORTED_NAME}     e.g. GREET, ANCESTOR, FIBONACCI
```

The language prefix (`SNOBOL4_`, `PROLOG_`, etc.) is **not** applied to assembly
or file names. A caller does not need to know what language a library is written
in — only the assembly name and method name. This follows the same convention as
native object files (`.o`, `.so`, `.dll`) which carry no language tag.

Arity is **not** part of the symbol name. Arity is enforced at compile time by the
calling language's type checker. Mismatch = compile error, not link error.

---

## 6. EXPORT / IMPORT Syntax

Added to all five language parsers. Syntax is identical regardless of source language.

```snobol4
* SNOBOL4 syntax
EXPORT  WORDCOUNT
IMPORT  ancestor.ANCESTOR
IMPORT  fibonacci.FIBONACCI
```

```prolog
% Prolog syntax  
:- export(ancestor/2).
:- import(icon, fibonacci/1).
```

```icon
# Icon syntax
$export fibonacci
$import ancestor.ANCESTOR
$import wordcount.WORDCOUNT
```

```snocone
(* Snocone syntax *)
EXPORT WORD_RULE
IMPORT classify.CLASSIFY
```

**Semantics:**
- `EXPORT name` — the named Byrd Box is visible in the object symbol table (`.globl` on x64, `public` on JVM/.NET)
- `IMPORT assembly.METHOD` — an external reference; the compiler emits a relocation/reference; the linker/class-loader resolves it
- All other DEFINEs are **static** by default — no external visibility

---

## 7. The scrip Driver (New)

```
scrip compile  hello.sno          →  hello.sno.o  (x64)
scrip compile  hello.sno --jvm    →  Hello.class
scrip compile  hello.sno --net    →  hello.dll
scrip compile  ancestor.pl --jvm  →  PROLOG_ANCESTOR.class
scrip compile  fib.icn --jvm      →  ICON_FIBONACCI.class

scrip link     hello.sno.o ancestor.pl.o fib.icn.o  →  hello  (x64 binary)
scrip link     *.class --jvm                         →  hello.jar
scrip link     *.dll --net                           →  hello.exe

scrip run      hello              (compile + link + run, single command)
```

This is `cc`/`gcc` semantics. `-c` for compile-only. No flag = compile+link+run.

---

## 8. Static-by-Default Enforcement

The compiler enforces that internal symbols are not accidentally exported.

**x64:** Labels that are not `EXPORT`ed have no `.globl` directive. The assembler
makes them local to the `.o` by default.

**JVM:** Non-exported methods are `private static`. The JVM enforces access at load time.

**.NET:** Non-exported methods are `internal`. The CLR enforces access at assembly boundary.

**Practical consequence:** Name collisions between two `.sno` files are impossible.
`helper` in `wordcount.sno` and `helper` in `palindrome.sno` are different symbols —
both static, neither visible to the linker, no collision.

---

## 9. Decision Log

| # | Decision | Rationale |
|---|----------|-----------|
| ABI-001 | Continuation-passing (not return value) for γ/ω | Matches the x64 jump model exactly; no impedance between backends |
| ABI-002 | ThreadLocal for JVM/.NET result passing | Avoids allocating a wrapper object on every call; zero GC pressure |
| ABI-003 | Static-by-default, explicit EXPORT | Prevents namespace pollution; matches C `static` idiom that 50 years proved correct |
| ABI-004 | No arity in symbol name | Arity checked at compile time; baking it in creates link-time type errors that are harder to diagnose |
| ABI-005 | SnoVal passed by pointer on x64, by reference on JVM/.NET | Avoids copy on every call; JVM/CLR manage lifetime via GC |
| ABI-006 | `scrip` as unified driver | Single entry point for all compile+link operations; parallels `cc`/`gcc` user experience |

---

*GENERAL-SCRIP-ABI.md — freeze before Sprint 2 begins.*  
*Review checklist: SnoVal definition agreed · x64 register protocol agreed · JVM signature agreed · .NET signature agreed · symbol naming agreed · EXPORT/IMPORT syntax agreed per language.*
