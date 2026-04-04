# EMITTER-JVM.md — JVM Emitter (Jasmin)

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Status:** AUTHORITATIVE — in progress

Walks SM_Program and emits Jasmin `.j` bytecode assembled by `jasmin.jar` → `.class`.
Also covers Prolog×JVM Jasmin emission patterns.

---

## SM_Program Emission

Each `SM_Op` maps to a Jasmin bytecode sequence. Same instruction set as EMITTER-X86.
When INTERP-JVM passes the full corpus on a given SM_Program, this emitter is correct
by construction — because they execute the same instructions.

**Status:** SM_Program not yet defined — emitter currently tree-walks IR via
Clojure pipeline (interpreter → transpiler → stack VM → JVM `.class` bytecode).

---

## Prolog×JVM — Resumable Predicate Pattern (Jasmin)

Each `E_CHOICE` for `foo/1` emits a `.j` class with an inner `$Closure`.
See `INTERP-JVM.md` for the full execution model and runtime class layout.

```jasmin
.class public pl_foo_1
.super pl/PlProc1

.method public Call(Lpl/PlTerm;Lpl/PlTrail;)Lpl/PlDescriptor;
    new pl_foo_1$Closure
    dup
    aload_1 ; arg0
    aload_2 ; trail
    invokespecial pl_foo_1$Closure/<init>(Lpl/PlTerm;Lpl/PlTrail;)V
    dup
    invokevirtual pl_foo_1$Closure/Resume()Lpl/PlDescriptor;
    areturn
.end method

.class pl_foo_1$Closure
.super pl/PlClosure
.field private _arg0 Lpl/PlTerm;
.field private _trail Lpl/PlTrail;
.field private _cs I

.method public Resume()Lpl/PlDescriptor;
    aload_0; getfield _trail Lpl/PlTrail;
    invokevirtual pl/PlTrail/mark()I
    istore_1
    aload_0; getfield _cs I
    tableswitch 0 1
        clause_0
        clause_1
      default: omega
clause_0:
    aload_0; iconst_1; putfield _cs I
    aload_0; areturn
omega:
    aconst_null; areturn
.end method
```

---

## Key Bytecode Sequences

### Atom interning
```jasmin
ldc "hello"
invokestatic pl/PlAtom/intern(Ljava/lang/String;)Lpl/PlAtom;
putstatic ThisClass/atom_hello Lpl/PlAtom;
```

### Variable load + deref (env slot k)
```jasmin
aload_0; getfield _env [Lpl/PlTerm;
bipush k; aaload
invokevirtual pl/PlTerm/deref()Lpl/PlTerm;
```

### Unify two terms
```jasmin
<push t1>
<push t2>
aload_0; getfield _trail Lpl/PlTrail;
invokestatic pl/PlUnify/unify(Lpl/PlTerm;Lpl/PlTerm;Lpl/PlTrail;)Z
ifeq <fail_label>
```

### is/2
```jasmin
<push Expr term>
invokestatic pl/PlArith/eval(Lpl/PlTerm;)J
invokestatic pl/PlInt/New(J)Lpl/PlInt;
<push X term>; swap
aload_0; getfield _trail Lpl/PlTrail;
invokestatic pl/PlUnify/unify(Lpl/PlTerm;Lpl/PlTerm;Lpl/PlTrail;)Z
ifeq <fail_label>
```

### write/1 and nl/0
```jasmin
getstatic java/lang/System/out Ljava/io/PrintStream;
<push term>; invokevirtual pl/PlTerm/deref()Lpl/PlTerm;
invokevirtual pl/PlTerm/toProlog()Ljava/lang/String;
invokevirtual java/io/PrintStream/print(Ljava/lang/String;)V

getstatic java/lang/System/out Ljava/io/PrintStream;
invokevirtual java/io/PrintStream/println()V
```

---

## References

- `SCRIP-SM.md` — SM_Program this emitter walks
- `EMITTER-COMMON.md` — shared emitter architecture
- `INTERP-JVM.md` — JVM interpreter, execution model, runtime classes
- `PARSER-PROLOG.md` — Prolog IR nodes emitted from

---

## snobol4jvm (Clojure) Design — 10 Laws

1. ALL UPPERCASE keywords.
2. Single-file engine. `match.clj` is one `loop/case`. Cannot be split.
3. Immutable-by-default, mutable-by-atom. TABLE and ARRAY use `atom`.
4. Label/body whitespace contract. Labels flush-left, bodies indented.
5. INVOKE is the single dispatch point. Add both lowercase and uppercase entries.
6. `nil` means failure; epsilon means empty string.
7. `clojure.core/=` inside `operators.clj`. Bare `=` builds IR lists.
8. INVOKE args are pre-evaluated. Never call `EVAL!` on args inside INVOKE.
9. Two-tier generator discipline. `rand-*` probabilistic. `gen-*` exhaustive lazy.
10. Two-strategy debugging: (a) run a probe; (b) read SPITBOL source (v311.sil). Never speculate.

## snobol4jvm File Map

| File | Responsibility |
|------|---------------|
| `match.clj` | MATCH state machine — single-file engine |
| `primitives.clj` | LIT$, ANY$, SPAN$, BREAK$, POS#, etc. |
| `patterns.clj` | ANY, SPAN, ARBNO, FENCE, ABORT, BAL, CONJ, DEFER |
| `grammar.clj` | instaparse grammar + parse-statement/parse-expression |
| `emitter.clj` | AST → Clojure IR |
| `operators.clj` | EVAL/EVAL!/INVOKE, comparison primitives |
| `runtime.clj` | RUN: GOTO-driven statement interpreter |
| `jvm_codegen.clj` | Stage 23D: ASM-generated JVM `.class` bytecode |
| `transpiler.clj` | Stage 23B: SNOBOL4 IR → Clojure `loop/case` |
| `vm.clj` | Stage 23C: flat bytecode stack VM |

## Performance Baselines

| Stage | Speedup vs interpreter |
|-------|----------------------|
| EDN cache (`jvm-edn-cache`) | 22× per-program |
| Transpiler (`jvm-transpiler`) | 3.5–6× |
| Stack VM (`jvm-stack-vm`) | 2–6× |
| JVM bytecode (`jvm-bytecode`) | 7.6× |

Test baseline: 1,896 tests / 4,120 assertions / 0 failures.

## Open Issues

| # | Issue | Status |
|---|-------|--------|
| 1 | CAPTURE-COND (`.`) assigns immediately — deferred-assign not built | Open |
| 2 | ANY(multi-arg) inside EVAL string — ClassCastException | Open |

---

## Clojure-EDN Frontend (snobol4jvm)

Clojure-EDN is the native input path for snobol4jvm — allows expressing SNOBOL4
programs as Clojure EDN data structures, consumed directly by the JVM runtime
without a separate parse step.

The EDN cache sprint (`jvm-edn-cache` ✅ `b30f383`) achieved 22× per-program
speedup by caching parsed EDN representations. This is the primary input path
for the JVM backend alongside SNOBOL4 text input.
