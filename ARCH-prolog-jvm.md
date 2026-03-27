# ARCH-prolog-jvm.md — JVM Prolog Backend Architecture

Prolog frontend IR (E_CHOICE/E_CLAUSE/E_UNIFY/E_CUT) → Jasmin `.j` → `.class`.
Driver flag: `snobol4x -pl -jvm foo.pl` → `foo.j` → assembled by `jasmin.jar`.

*Session state → JVM.md. Milestone dashboard → PLAN.md §Prolog JVM Backend.*

---

## JCON Correspondence

JCON (Proebsting & Townsend, 1999) compiles Icon goal-directed evaluation to JVM
bytecode using exactly the four-port model we need for Prolog.  The runtime classes
in `jcon/` map directly:

| JCON concept | Byrd box port | Jasmin pattern |
|---|---|---|
| `PlProc1.Call(arg,trail)` → non-null | α — entry, first solution | `invokevirtual Call` |
| `PlProc1.Call(arg,trail)` → `null` | ω — deterministic fail | `aconst_null; areturn` |
| `PlClosure.Resume()` → `this` (retval set) | γ — succeed, stay suspended | `aload_0; areturn` |
| `PlClosure.Resume()` → `null` | ω — generator exhausted | `aconst_null; areturn` |
| `result.Resume()` by caller | β — retry for next solution | `invokevirtual Resume` |

The canonical JCON generator pattern (cherry-picked from `test/primes.java`,
`test/factors.java` in the uploaded source):

```java
// α: Call creates closure, fires first Resume() immediately
public vDescriptor Call(vDescriptor a) {
    return new vClosure() {
        int _cs = 0;          // clause index (our addition for Prolog)
        public vDescriptor Resume() {
            // try next clause from _cs
            // on match: retval = <term>; return this;   // γ — suspended
            // exhausted: return null;                    // ω — fail
        }
    }.Resume();               // fire α immediately, return first result
}
```

Caller retry loop (β port) — identical for Icon generators and Prolog backtracking:
```java
vDescriptor result = pred.Call(arg, trail);   // α
while (result != null) {
    // consume result ...
    result = result.Resume();                 // β: next solution
}
```

---

## Value Representation

Prolog terms use a new `PlTerm` hierarchy (in `src/backend/jvm/pl_runtime/pl/`).
We do NOT reuse JCON's `vDescriptor` — Prolog needs compound/var/ref/atom/int
and a trail.  The `Call/Resume` contract is the same; only the value type differs.

```java
package pl;
public abstract class PlTerm {
    public static final int ATOM=0, VAR=1, COMPOUND=2, INT=3, REF=4;
    public int tag;
    public PlTerm deref() {
        PlTerm t = this;
        while (t.tag == REF && ((PlRef)t).ref != null) t = ((PlRef)t).ref;
        return t;
    }
}
// PlAtom(String name), PlVar(int slot), PlRef(PlTerm ref),
// PlInt(long val), PlCompound(String functor, int arity, PlTerm[] args)
```

---

## Resumable Predicate Pattern (Jasmin)

Each `E_CHOICE` for `foo/1` emits a `.j` class with an inner `$Closure`:

```jasmin
; pl_foo_1.j

.class public pl_foo_1
.super pl/PlProc1

; α: create closure, call Resume() for first solution
.method public Call(Lpl/PlTerm;Lpl/PlTrail;)Lpl/PlDescriptor;
    .limit stack 6
    .limit locals 3
    new pl_foo_1$Closure
    dup
    aload_1                     ; arg0
    aload_2                     ; trail
    invokespecial pl_foo_1$Closure/<init>(Lpl/PlTerm;Lpl/PlTrail;)V
    dup
    invokevirtual pl_foo_1$Closure/Resume()Lpl/PlDescriptor;
    areturn                     ; null=ω, non-null=γ suspended
.end method

; -----------------------------------------------------------------------
.class pl_foo_1$Closure
.super pl/PlClosure             ; has: PlDescriptor retval; abstract Resume()

.field private _arg0 Lpl/PlTerm;
.field private _trail Lpl/PlTrail;
.field private _cs I            ; clause index (0..N-1)

.method public <init>(Lpl/PlTerm;Lpl/PlTrail;)V
    aload_0; invokespecial pl/PlClosure/<init>()V
    aload_0; aload_1; putfield _arg0 Lpl/PlTerm;
    aload_0; aload_2; putfield _trail Lpl/PlTrail;
    aload_0; iconst_0; putfield _cs I   ; start at clause 0
    return
.end method

.method public Resume()Lpl/PlDescriptor;
    .limit stack 10
    .limit locals 4
    ; save trail mark into local_1
    aload_0; getfield _trail Lpl/PlTrail;
    invokevirtual pl/PlTrail/mark()I
    istore_1

    ; dispatch on _cs
    aload_0; getfield _cs I
    tableswitch 0 1             ; clauses 0..1
        clause_0
        clause_1
      default: omega

clause_0:
    ; unwind trail to mark, re-init env
    aload_0; getfield _trail Lpl/PlTrail;
    iload_1; invokevirtual pl/PlTrail/unwind(I)V
    ; unify _arg0 with atom 'a'
    aload_0; getfield _arg0 Lpl/PlTerm;
    getstatic PrologAtoms/atom_a Lpl/PlAtom;
    aload_0; getfield _trail Lpl/PlTrail;
    invokestatic pl/PlUnify/unify(Lpl/PlTerm;Lpl/PlTerm;Lpl/PlTrail;)Z
    ifeq clause_1               ; fail → try next clause
    ; --- body of clause 0 ---
    ; γ: succeed, advance _cs, return this
    aload_0; iconst_1; putfield _cs I
    aload_0; getstatic PrologAtoms/atom_result Lpl/PlAtom; putfield retval Lpl/PlDescriptor;
    aload_0; areturn            ; γ port

clause_1:
    aload_0; getfield _trail Lpl/PlTrail;
    iload_1; invokevirtual pl/PlTrail/unwind(I)V
    ; ... unify with clause 1 head ...
    ; γ or fall to omega

omega:
    aconst_null; areturn        ; ω port
.end method
```

---

## Cut Semantics

`E_CUT` seals β — set `_cs = N` (past last clause) before the γ return.
On the next `Resume()`, `tableswitch` hits `default: omega` immediately.

```jasmin
; E_CUT: seal beta
aload_0; bipush N; putfield _cs I
```

---

## Trail + Unification Runtime

```java
package pl;
public class PlTrail {
    PlTerm[] stack = new PlTerm[128];
    int top = 0;
    public int mark() { return top; }
    public void push(PlTerm t) { if (top == stack.length) grow(); stack[top++] = t; }
    public void unwind(int mark) {
        while (top > mark) { PlRef r = (PlRef) stack[--top]; r.ref = null; }
    }
    private void grow() { stack = java.util.Arrays.copyOf(stack, stack.length * 2); }
}

public class PlUnify {
    public static boolean unify(PlTerm t1, PlTerm t2, PlTrail trail) {
        t1 = t1.deref(); t2 = t2.deref();
        if (t1 == t2) return true;
        if (t1.tag == PlTerm.VAR) { bind((PlRef)t1, t2, trail); return true; }
        if (t2.tag == PlTerm.VAR) { bind((PlRef)t2, t1, trail); return true; }
        if (t1.tag == PlTerm.ATOM && t2.tag == PlTerm.ATOM)
            return ((PlAtom)t1).name.equals(((PlAtom)t2).name);
        if (t1.tag == PlTerm.INT && t2.tag == PlTerm.INT)
            return ((PlInt)t1).val == ((PlInt)t2).val;
        if (t1.tag == PlTerm.COMPOUND && t2.tag == PlTerm.COMPOUND) {
            PlCompound c1 = (PlCompound)t1, c2 = (PlCompound)t2;
            if (!c1.functor.equals(c2.functor) || c1.arity != c2.arity) return false;
            for (int i = 0; i < c1.arity; i++)
                if (!unify(c1.args[i], c2.args[i], trail)) return false;
            return true;
        }
        return false;
    }
    private static void bind(PlRef v, PlTerm t, PlTrail trail) {
        v.ref = t; trail.push(v);
    }
}
```

---

## Key Bytecode Sequences

### Atom interning (class static init)
```jasmin
.field static atom_hello Lpl/PlAtom;
; in <clinit>:
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

### Unify two terms (inline)
```jasmin
<push t1>
<push t2>
aload_0; getfield _trail Lpl/PlTrail;
invokestatic pl/PlUnify/unify(Lpl/PlTerm;Lpl/PlTerm;Lpl/PlTrail;)Z
ifeq <fail_label>
```

### is/2: X is Expr (integer arithmetic)
```jasmin
; evaluate Expr to long via PlInt.eval(), unify with X
<push Expr term>
invokestatic pl/PlArith/eval(Lpl/PlTerm;)J   ; returns long
invokestatic pl/PlInt/New(J)Lpl/PlInt;
<push X term>
swap
aload_0; getfield _trail Lpl/PlTrail;
invokestatic pl/PlUnify/unify(Lpl/PlTerm;Lpl/PlTerm;Lpl/PlTrail;)Z
ifeq <fail_label>
```

### write/1
```jasmin
getstatic java/lang/System/out Ljava/io/PrintStream;
<push term>; invokevirtual pl/PlTerm/deref()Lpl/PlTerm;
invokevirtual pl/PlTerm/toProlog()Ljava/lang/String;
invokevirtual java/io/PrintStream/print(Ljava/lang/String;)V
```

### nl/0
```jasmin
getstatic java/lang/System/out Ljava/io/PrintStream;
invokevirtual java/io/PrintStream/println()V
```

---

## Runtime Class Layout

```
src/backend/jvm/pl_runtime/
    pl/PlTerm.java          abstract base — tag + deref()
    pl/PlAtom.java          atom(String name) + intern table
    pl/PlVar.java           unbound variable(int slot)
    pl/PlRef.java           bound variable(PlTerm ref) — trail entry type
    pl/PlInt.java           integer(long val) + New(long)
    pl/PlCompound.java      compound(String functor, int arity, PlTerm[] args)
    pl/PlTrail.java         mark() / push(PlTerm) / unwind(int)
    pl/PlUnify.java         static unify(t1, t2, trail) → boolean
    pl/PlArith.java         static eval(PlTerm) → long  (is/2 rhs)
    pl/PlDescriptor.java    abstract base: PlDescriptor retval; Resume()
    pl/PlClosure.java       abstract resumable: PlDescriptor retval; Resume()
    pl/PlProc1.java         1-arg predicate: Call(PlTerm, PlTrail)
    pl/PlProc2.java         2-arg predicate
    pl/PlBuiltin.java       write/nl/functor/arg/=../type tests
    pl/PrologAtoms.java     static field per interned atom (class-init)
```

JCON source reference: `jcon/vClosure.java` ↔ `pl/PlClosure.java` (same `retval` +
`Resume()` contract). `jcon/vProc1.java` ↔ `pl/PlProc1.java`. `test/primes.java`
and `test/factors.java` are the direct model for the `$Closure` inner class pattern.

---

## Driver Wire-up (M-PJ-WIRE)

One-line change in `src/driver/main.c` at the `-pl` dispatch (line ~147):

```c
if (pl_mode) {
    if (asm_mode)
        asm_emit_prolog(prog, out);
    else if (jvm_mode)
        jvm_emit_prolog(prog, out, infile);   /* ADD */
    else
        pl_emit(prog, out);
}
```

New function at bottom of `emit_byrd_jvm.c`:

```c
void jvm_emit_prolog(Program *prog, FILE *out, const char *filename) {
    jvm_out = out;
    jvm_uid_ctr = 0;
    emit_pl_jvm_preamble(filename);
    for (STMT_t *s = prog->head; s; s = s->next)
        if (s->subject && s->subject->kind == E_CHOICE)
            emit_pl_jvm_choice(s->subject);
    emit_pl_jvm_main(prog);
}
```

Model: `asm_emit_prolog()` / `emit_prolog_program()` in `emit_byrd_asm.c` ~line 5041.
Model for `emit_pl_jvm_choice()`: `emit_prolog_choice()` in `emit_byrd_asm.c` ~line 6235.

---

*BACKEND-JVM-PROLOG.md = L3. No session state. No step content. Ever.*
