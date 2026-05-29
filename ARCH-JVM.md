# ARCH-JVM.md — JVM Backend

Backend: JVM (Jasmin assembly → .class bytecode).
Emitter: unified `emit_core.c` (`IS_JVM` arms in `SM_templates/` + `BB_templates/`).
The former silo `emit_jvm.c` was deleted in the EC series — see ARCH-EMITTER.md.
`snobol4jvm` (Clojure) is the separate semantic oracle, not the emitter.

## Byrd Box model (compiled)

`emit_jvm.c` compiles each AST node to Jasmin α/γ/ω labels at compile time.
The `.class` IS the Byrd box graph. No interpreter loop at runtime.
Same model as `emit_x64.c` — labels + gotos, never execution at emit time.

**One class per box.**  α and β are public methods; γ/ω are return
values (typically a `Spec` object or null sentinel).  Sub-box wiring
uses `goto` / `if_icmpgt` / `if_icmplt` against internal labels.
Label naming convention: `len_omega`, `len_gamma` (lowercase suffix).

**Per-instance state ζ** lives in instance fields on the box class:
```jasmin
.field private final n I
.field private final dyn Ljava/util/function/IntSupplier;
```
α reads ζ at entry; γ/ω discard the box reference at return.  JVM's
GC reclaims ζ — no manual save/restore needed.

## Three-column form on JVM

The α/β methods preserve the canonical three-column shape, with port
exits compiled to `goto` or `areturn`/`aconst_null + areturn`:

```
.method public α()Lbb/bb_box$Spec;
    aload_0; getfield ms ; getfield delta I    ; column-1 entry
    aload_0; invokevirtual val()I              ; column-2 action
    iadd
    aload_0; getfield ms ; getfield omega I
    if_icmpgt len_omega                        ; column-3 goto
    ; ... advance cursor, build Spec, areturn  ; γ
len_omega:
    aconst_null
    areturn                                    ; ω
.end method
```

## snobol4jvm (oracle)

Interpreted frame walker. `match.clj` walks pattern tree as data using 7-element
frame vector, dispatching on :proceed/:succeed/:recede/:fail.
Role: semantic oracle for emit_jvm.c. Baseline: 1,896 tests, 0 failures.

## Prolog × JVM — resumable predicate pattern

Each `E_CHOICE` for `foo/1` emits a `.j` class with an inner `$Closure`
holding per-call state.  `tableswitch` on a clause-state field selects
the next clause to try; backtracking unwinds via the trail.

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
.end method
```

## Per-instruction emit (SM_Program)

Each `SM_Op` maps to a Jasmin bytecode sequence.  Same instruction set
as the x86 backend — when the SM interpreter passes the full corpus
on a given SM_Program, this emitter is correct by construction
because they execute the same instructions.

Today emit_jvm.c tree-walks IR via the Clojure pipeline (interpreter
→ transpiler → stack VM → JVM `.class` bytecode); migrating it onto
SM_Program is part of the broader emitter unification work.

## Tools

- `javac`, `java` (JDK + JRE)
- `jasmin.jar` — bundled at `src/backend/jasmin.jar`
- `jvm_codegen.clj` uses `clojure.asm.ClassWriter` — no Jasmin (snobol4jvm path)

## Build

Boxes: `bb_*.j` files assembled by `jasmin.jar` → `bb/*.class`,
packaged into `boxes.jar` for the JVM runtime.
