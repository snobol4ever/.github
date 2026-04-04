# INTERP-JVM.md — JVM Interpreter (Java)

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Status:** AUTHORITATIVE — ⬜ in progress

Executes SM_Program on JVM. Written in Java. Also covers Prolog×JVM execution model
(the four-port Byrd box model as JVM Call/Resume contract).

---

## SM_Program Execution (SNOBOL4 / all frontends)

The JVM interpreter executes `SM_Program` instructions in Java. Same instruction set
as INTERP-X86. When it passes the full corpus, EMITTER-JVM is correct by construction.

**Status:** ⬜ SM_Program not yet defined — interpreter currently runs via Clojure
pipeline (interpreter → transpiler → stack VM → JVM `.class` bytecode).

---

## Prolog×JVM — Four-Port Byrd Box as Call/Resume

The Prolog frontend compiles `E_CHOICE`/`E_CLAUSE`/`E_UNIFY`/`E_CUT` IR nodes to
Jasmin `.j` → `.class`. Driver flag: `one4all -pl -jvm foo.pl`.

### JCON Correspondence

JCON (Proebsting & Townsend, 1999) compiles Icon goal-directed evaluation to JVM
bytecode using exactly the four-port model needed for Prolog:

| JCON concept | Byrd box port | Jasmin pattern |
|---|---|---|
| `PlProc1.Call(arg,trail)` → non-null | α — entry, first solution | `invokevirtual Call` |
| `PlProc1.Call(arg,trail)` → `null` | ω — deterministic fail | `aconst_null; areturn` |
| `PlClosure.Resume()` → `this` | γ — succeed, stay suspended | `aload_0; areturn` |
| `PlClosure.Resume()` → `null` | ω — generator exhausted | `aconst_null; areturn` |
| `result.Resume()` by caller | β — retry for next solution | `invokevirtual Resume` |

### Canonical Generator Pattern

```java
// α: Call creates closure, fires first Resume() immediately
public vDescriptor Call(vDescriptor a) {
    return new vClosure() {
        int _cs = 0;          // clause index
        public vDescriptor Resume() {
            // try next clause from _cs
            // on match: retval = <term>; return this;   // γ — suspended
            // exhausted: return null;                    // ω — fail
        }
    }.Resume();
}
```

Caller retry loop (β port):
```java
vDescriptor result = pred.Call(arg, trail);   // α
while (result != null) {
    // consume result ...
    result = result.Resume();                 // β: next solution
}
```

### Value Representation

Prolog terms use `PlTerm` hierarchy (NOT JCON's `vDescriptor`):

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

### Trail + Unification Runtime

```java
public class PlTrail {
    PlTerm[] stack = new PlTerm[128];
    int top = 0;
    public int mark() { return top; }
    public void push(PlTerm t) { if (top == stack.length) grow(); stack[top++] = t; }
    public void unwind(int mark) {
        while (top > mark) { PlRef r = (PlRef) stack[--top]; r.ref = null; }
    }
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
}
```

### Cut Semantics

`E_CUT` seals β — set `_cs = N` (past last clause) before the γ return:
```jasmin
; E_CUT: seal beta
aload_0; bipush N; putfield _cs I
```
On next `Resume()`, `tableswitch` hits `default: omega` immediately.

### Runtime Class Layout

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

JCON source reference: `jcon/vClosure.java` ↔ `pl/PlClosure.java` (same contract).
`test/primes.java` and `test/factors.java` are the direct model for the `$Closure` pattern.

---

## Driver Wire-up (M-PJ-WIRE)

One-line change in `src/driver/main.c` at the `-pl` dispatch (~line 147):

```c
if (pl_mode) {
    if (asm_mode)      asm_emit_prolog(prog, out);
    else if (jvm_mode) jvm_emit_prolog(prog, out, infile);   /* ADD */
    else               pl_emit(prog, out);
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

Model: `asm_emit_prolog()` / `emit_prolog_choice()` in `emit_byrd_asm.c`.

---

## References

- `SCRIP-SM.md` — SM_Program this interpreter executes
- `EMITTER-JVM.md` — Jasmin bytecode emission patterns
- `PARSER-PROLOG.md` — Prolog IR nodes (E_CHOICE, E_CLAUSE, E_UNIFY, E_CUT)
- `BB-GRAPH.md` — the graph structure executed in Phase 3
Contains BB-DRIVER in Java + bb_*.java boxes.
See MILESTONE-JVM-SNOBOL4.md for milestone ladder.
