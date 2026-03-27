# FRONTEND-PROLOG.md — Prolog Frontend (snobol4x)

Tiny-Prolog: lex → parse → lower → IR. No session state here.
**Session state** → `SESSION-prolog-x64.md` or `SESSION-prolog-jvm.md`
**Deep reference:** all ARCH docs cataloged in `ARCH-index.md`

---

## Subsystems

| Subsystem | Doc | Go there when |
|-----------|-----|---------------|
| JVM runtime design | `ARCH-prolog-jvm.md` | term encoding, trail, clause dispatch |
| Historical session notes | `ARCH-prolog-x64.md` | F-212..F-214 design decisions |

---

## Design Philosophy

Prolog is a first-class citizen of the IR — not a guest of SNOBOL4.
New node types are introduced only where existing ones do not match semantics.
The emitter gets new `case` branches that lower to Byrd box (α/β/γ/ω) sequences.
The backends see only Byrd box output — same as today.

---

## Why Prolog fits the Byrd Box model

Byrd invented the four-port box *for Prolog* — snobol4ever already uses it
for SNOBOL4 patterns. The symmetry is exact:

| Port | SNOBOL4 pattern | Prolog SLD resolution |
|------|-----------------|-----------------------|
| α    | proceed         | try next clause head  |
| β    | resume          | retry on backtrack    |
| γ    | succeed         | head unified, enter body |
| ω    | fail            | all clauses exhausted |

Cut (`!`) maps to FENCE: β becomes unreachable. No new mechanism needed.

---

## Practical Subset (target)

**In scope:**
- Horn clauses: `head :- body.`
- Unification: `foo(X, bar(X)).`
- Arithmetic via `is/2`: `+`, `-`, `*`, `//`, `mod`
- Comparison: `</2`, `>/2`, `=:=/2`, `=\=/2`, `=</2`, `>=/2`
- Structural equality: `=/2`, `\=/2`
- Cut: `!`
- Lists: `[H|T]` notation, `[a,b,c]` sugar
- Builtins: `write/1`, `writeln/1`, `nl/0`, `read/1`
- Control: `true/0`, `fail/0`, `halt/0`, `halt/1`
- Term inspection: `functor/3`, `arg/3`, `=../2`
- Type tests: `atom/1`, `integer/1`, `var/1`, `nonvar/1`, `compound/1`
- `:- initialization(main)` directive

**Deferred:** `assert/retract`, `setof/bagof/findall`, modules, CLP, DCG, exceptions.

---

## IR Node Reuse vs New

Reuse existing EXPR_t/EKind nodes where semantics match exactly.
Introduce new kinds only where they do not.

### Reused (from sno2c.h EKind)

| Existing node | Prolog use | Match? |
|---------------|-----------|--------|
| `E_QLIT` | atom literals `'foo'`, string args | ✅ exact |
| `E_ILIT` | integer literals `42` | ✅ exact |
| `E_FLIT` | float literals `3.14` | ✅ exact |
| `E_VART` | Prolog variables `X`, `Foo` | ✅ exact — same concept |
| `E_FNC`  | body goals `foo(X,Y)`, builtins `write(X)` | ✅ exact — call with named functor + args |
| `E_ADD/E_SUB/E_MPY/E_DIV` | `is/2` arithmetic subexpressions | ✅ exact |

### New node kinds (genuine semantic additions)

| New node | Why new | Cannot reuse |
|----------|---------|--------------|
| `E_UNIFY` | Unification `=/2` — binds variables, needs trail, ω on failure | No existing node binds with trail + backtrack |
| `E_CLAUSE` | One Horn clause — head + body[] + EnvLayout | No stmt-level equivalent |
| `E_CHOICE` | All clauses for one functor/arity — α/β chain | No existing multi-clause node |
| `E_CUT` | Seals β of enclosing choice point | No FENCE equivalent at expr level |
| `E_TRAIL_MARK` | Save trail.top into env slot | Pure runtime bookkeeping — no equivalent |
| `E_TRAIL_UNWIND` | Restore trail to saved mark | Pure runtime bookkeeping — no equivalent |

That is 6 new node kinds — not 10. `E_TERM_LOAD/STORE` and `E_IS` from the earlier
design are subsumed by `E_VART` (load) + `E_UNIFY` (store with trail) + `E_FNC`
for `is/2` dispatching to existing arithmetic nodes.

---

## Term Representation — `TERM_t`

New type, independent of `DESCR_t`. Lives in `src/frontend/prolog/term.h`.

```c
typedef enum {
    TT_ATOM,      /* 'foo'  — interned string index        */
    TT_VAR,       /* X      — slot index into env frame    */
    TT_COMPOUND,  /* f(a,b) — functor + arity + args[]     */
    TT_INT,       /* 42                                    */
    TT_FLOAT,     /* 3.14                                  */
    TT_REF        /* bound variable — pointer to target    */
} TermTag;

typedef struct Term {
    TermTag tag;
    union {
        int         atom_id;
        int         var_slot;   /* compile-time slot in env DATA block */
        struct {
            int          functor; /* atom_id of functor name */
            int          arity;
            struct Term **args;
        } compound;
        long        ival;
        double      fval;
        struct Term *ref;       /* TT_REF: dereference chain */
    };
} Term;
```

List `[H|T]` lowered to `compound{ functor='.', arity=2, args=[H,T] }`.
Nil `[]` is an atom.

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

void trail_push(Trail *t, Term **slot);
void trail_unwind(Trail *t, int mark);
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

---

## Source Layout

```
src/frontend/prolog/
    pl_lex.c          Hand-rolled lexer
    pl_parse.c        Recursive-descent parser -> ClauseAST
    pl_lower.c        ClauseAST -> E_CLAUSE/E_CHOICE/E_UNIFY/E_CUT/... nodes
    pl_emit.c         New E_* nodes -> Byrd box α/β/γ/ω emission
    pl_unify.c        Runtime unify() + trail_push/unwind
    pl_atom.c         Atom interning table
    pl_builtin.c      write/nl/read/functor/arg/=.. etc.
    term.h            TERM_t definition
    pl_runtime.h      Trail, EnvLayout, entry-point declarations

test/frontend/prolog/corpus/
    README.md
    rung01_hello/ .. rung09_builtins/   (stubs, filled as milestones fire)
    rung10_programs/                    (Lon's word-puzzle solvers -- committed)
        puzzle_01.pro   bank positions Brown/Jones/Smith
        puzzle_02.pro   trades Clark/Daw/Fuller
        puzzle_05.pro   bank chess Brown/Clark/Jones/Smith (WIP)
        puzzle_06.pro   occupations Clark/Jones/Morgan/Smith
        puzzles.pro     stubs for puzzles 3-20
```

---

## Driver Flag

```
snobol4x -pl -asm  foo.pl    ->  foo.s   (x64 NASM)
snobol4x -pl -c    foo.pl    ->  foo.c   (C backend, later)
snobol4x -pl -jvm  foo.pl    ->  foo.j   (JVM Jasmin — see FRONTEND-PROLOG-JVM.md)
```

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

