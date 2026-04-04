# PARSER-PROLOG.md — Prolog Parser

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Status:** AUTHORITATIVE

---

## Role

Consumes Prolog source and produces the shared IR (Program*).
Driver flag: `one4all -pl foo.pl`

## Prolog-Specific IR Nodes

The Prolog frontend uses these EKind nodes (defined in `src/ir/ir.h`):

| Node | Meaning | children[] |
|------|---------|------------|
| `E_CHOICE` | Predicate with multiple clauses | [0..N-1] = E_CLAUSE nodes |
| `E_CLAUSE` | One clause: head + body | [0] = head, [1..] = body goals |
| `E_UNIFY` | Unification `X = Y` | [0] = left, [1] = right |
| `E_CUT` | Prolog cut `!` | none |
| `E_FNC` | Goal call / builtin | sval=functor, children=args |
| `E_VAR` | Prolog variable | sval=name |
| `E_QLIT` | Atom literal | sval=text |
| `E_ILIT` | Integer | ival |
| `E_COMPOUND` | Compound term f(a,b) | sval=functor, children=args |

## Clause Structure

```prolog
foo(X) :- bar(X), baz(X).
foo(a).
```

Compiles to:
```
E_CHOICE (foo/1)
  E_CLAUSE
    E_COMPOUND foo [E_VAR X]     ; head
    E_FNC bar [E_VAR X]          ; body goal 1
    E_FNC baz [E_VAR X]          ; body goal 2
  E_CLAUSE
    E_COMPOUND foo [E_QLIT "a"]  ; head (fact — no body goals)
```

## Source Layout

```
src/frontend/prolog/prolog_parse.c   Parser: Prolog source → IR
src/frontend/prolog/prolog_lex.c     Lexer: Prolog source → tokens
```

## Output

IR (Program*) → SM-LOWER → SM_Program → INTERP-JVM or EMITTER-JVM

## References

- `IR.md` — the shared IR this produces
- `INTERP-JVM.md` — JVM execution model for Prolog (four-port Byrd box)
- `EMITTER-JVM.md` — Jasmin bytecode emission for Prolog

---

## Design Philosophy

Prolog is a first-class citizen of the IR — not a guest of SNOBOL4. New node types
are introduced only where existing ones do not match semantics. The emitter gets new
`case` branches that lower to Byrd box (α/β/γ/ω) sequences. The backends see only
Byrd box output — same as today.

---

## Why Prolog Fits the Byrd Box Model

Byrd invented the four-port box *for Prolog*:

| Port | SNOBOL4 pattern | Prolog SLD resolution |
|------|-----------------|----------------------|
| α    | proceed         | try next clause head  |
| β    | resume          | retry on backtrack    |
| γ    | succeed         | head unified, enter body |
| ω    | fail            | all clauses exhausted |

Cut (`!`) maps to FENCE: β becomes unreachable. No new mechanism needed.

---

## IR Node Reuse vs New

### Reused nodes
`E_QLIT` (atom literals), `E_ILIT`, `E_FLIT`, `E_VART` (Prolog variables),
`E_FNC` (body goals and builtins), `E_ADD/SUB/MPY/DIV` (is/2 arithmetic).

### New node kinds (6 total)

| New node | Why new |
|----------|---------|
| `E_UNIFY` | Unification `=/2` — binds variables, needs trail, ω on failure |
| `E_CLAUSE` | One Horn clause — head + body[] + EnvLayout |
| `E_CHOICE` | All clauses for one functor/arity — α/β chain |
| `E_CUT` | Seals β of enclosing choice point |
| `E_TRAIL_MARK` | Save trail.top into env slot |
| `E_TRAIL_UNWIND` | Restore trail to saved mark |

---

## Term Representation — TERM_t

New type, independent of `DESCR_t`. Lives in `src/frontend/prolog/term.h`.

```c
typedef enum { TT_ATOM, TT_VAR, TT_COMPOUND, TT_INT, TT_FLOAT, TT_REF } TermTag;

typedef struct Term {
    TermTag tag;
    union {
        int         atom_id;
        int         var_slot;   /* compile-time slot in env DATA block */
        struct { int functor; int arity; struct Term **args; } compound;
        long        ival;
        double      fval;
        struct Term *ref;       /* TT_REF: dereference chain */
    };
} Term;
```

List `[H|T]` lowered to `compound{ functor='.', arity=2, args=[H,T] }`. Nil `[]` is an atom.

---

## Environment Frame (per-invocation DATA block)

```c
typedef struct EnvLayout {
    int   n_vars;           /* distinct variables in clause    */
    int   n_args;           /* arity of head predicate         */
    int   trail_mark_slot;  /* reserved slot for trail mark    */
} EnvLayout;
```

`r12` points at live env frame (T2 convention). Slot `k` at `[r12 + k*8]`.

---

## Trail

```c
typedef struct Trail {
    Term  ***stack;    /* pointers to bound Term* slots */
    int      top;
    int      capacity;
} Trail;
```

---

## Byrd Box Wiring — Clause Selection

For `foo/1` with two clauses:

```
P_FOO_α:
    E_TRAIL_MARK               ; save trail.top
    E_UNIFY(env[0], ATOM_a)    ; try clause 1 head; failure -> P_FOO_β
    <body of clause 1>
    jmp [ret_γ]

P_FOO_β:
    E_TRAIL_UNWIND             ; undo clause 1 bindings
    E_TRAIL_MARK               ; fresh mark
    E_UNIFY(env[0], ATOM_b)    ; try clause 2 head; failure -> P_FOO_ω
    <body of clause 2>
    jmp [ret_γ]

P_FOO_ω:
    E_TRAIL_UNWIND
    jmp [ret_ω]
```

Cut seals the β slot → ω. Exactly FENCE semantics.

---

## Practical Subset (target)

**In scope:** Horn clauses, unification, arithmetic via `is/2`, comparison operators,
cut, lists `[H|T]`, builtins (`write/1`, `nl/0`, `read/1`), term inspection
(`functor/3`, `arg/3`, `=../2`), type tests, `:- initialization(main)`.

**Deferred:** `assert/retract`, `setof/bagof/findall`, modules, CLP, DCG, exceptions.

---

## Corpus — Prolog Ladder

```
Rung 1:  hello       write('hello'), nl.
Rung 2:  facts       deterministic fact lookup
Rung 3:  unify       head unification, compound terms
Rung 4:  arith       is/2, integer arithmetic
Rung 5:  backtrack   member/2 — first backtracking
Rung 6:  lists       append/3, length/2, reverse/2
Rung 7:  cut         differ/N, closed-world negation via !, fail
Rung 8:  recursion   fibonacci/2, factorial/2
Rung 9:  builtins    functor/3, arg/3, =../2, type tests
Rung 10: programs    Lon's word-puzzle constraint solvers
```

---

## Source Layout

```
src/frontend/prolog/
    pl_lex.c          Lexer
    pl_parse.c        Recursive-descent parser → ClauseAST
    pl_lower.c        ClauseAST → E_CLAUSE/E_CHOICE/E_UNIFY/E_CUT nodes
    pl_emit.c         New E_* nodes → Byrd box emission
    pl_unify.c        Runtime unify() + trail_push/unwind
    pl_atom.c         Atom interning table
    pl_builtin.c      write/nl/read/functor/arg/=.. etc.
    term.h            TERM_t definition

test/frontend/prolog/corpus/
    rung01_hello/ .. rung09_builtins/
    rung10_programs/   puzzle_01.pl .. puzzle_06.pl
```

## Driver Flags

```
one4all -pl -asm  foo.pl    →  foo.s   (x64 NASM)
one4all -pl -jvm  foo.pl    →  foo.j   (JVM Jasmin)
```

---

## Closed-World Negation (puzzle pattern)

```prolog
hasHeardOf(fuller, daw) :- !, fail.
hasHeardOf(_, _).
```

Compiles as two `E_CLAUSE` nodes under one `E_CHOICE`. The `!` in clause 1
emits `E_CUT` which seals β. On matching `(fuller, daw)`, head unifies,
cut fires, then `fail/0` (an `E_FNC` to the builtin) forces ω.
The catch-all clause 2 is only reachable when clause 1's head fails to unify.
No `\+` needed — simpler to compile than negation-as-failure.
