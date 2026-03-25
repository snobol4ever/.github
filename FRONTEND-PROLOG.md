# FRONTEND-PROLOG.md — Tiny-Prolog Frontend (L3)

Tiny-Prolog is a frontend for snobol4x targeting the x64 ASM backend first,
then C once the design is proven.

*Session state → TINY.md. Milestone dashboard → PLAN.md §Prolog Frontend.*

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

## Session F-212 notes (added 2026-03-22)

### Proebsting PDF — key takeaways

"Simple Translation of Goal-Directed Evaluation" (Todd A. Proebsting, 1996).
Do not re-attach — notes captured here.

The paper's central contribution: every operator in an AST gets four labeled
code chunks (start/resume/fail/succeed = α/β/ω/γ in our notation).
The crucial template for conjunction (`plus(E1, E2)`) is:

```
plus.start   : goto E1.start
plus.resume  : goto E2.resume        ← β port: retry rightmost first
E1.fail      : goto plus.fail        ← ω: all exhausted
E1.succeed   : goto E2.start         ← chain: E1 success starts E2
E2.fail      : goto E1.resume        ← KEY: E2 fail retries E1 (β port)
E2.succeed   : plus.value = E1+E2; goto plus.succeed
```

`E2.fail → E1.resume` is exactly the backtracking wire missing from the
original emit_body. This is what was fixed in the emit_body rewrite.

The `ifstmt(E1,E2,E3)` template (§4.5) uses an **indirect goto** (`gate`
variable) set at runtime — this is the right model for Prolog's `;/2`
disjunction and `->` if-then-else, already implemented in emit_goal.

### What was built in F-212

- `prolog_emit.c` — full C-backend emitter with Byrd box four-port model
- Rung 1 (hello) confirmed running end-to-end
- Rungs 2–4 (facts, unify, arith) output correct but rung 2 only printed
  first solution — backtracking bug identified
- `emit_body` rewritten with proper β-port retry loop for user calls
  (Proebsting plus template). Build/test deferred to F-213.

### emit_body fix summary (for F-213)

Old: all goals chained linearly; fail always jumped to outer omega.
New: `is_user_call()` detects backtrackable goals; `emit_user_call_with_suffix()`
wraps them with a retry loop:

```c
call_β:
    trail_unwind(&_trail, _cm);
    _cr = pl_f_r(args, &_trail, _cs);
    if (_cr < 0) goto omega;
    _cs = _cr + 1;
// suffix goals here — their omega = call_β (retry)
```

This is the direct implementation of E2.fail→E1.resume from Proebsting.

### JCON

JCON (Java Icon) was uploaded but NOT read — context was consumed by
PLAN.md, FRONTEND-PROLOG.md, and prolog_emit.c. Key conceptual note:
JCON's engine uses full unification + backtracking for Icon goal-directed
evaluation — same four-port model. If JCON source is ever examined,
look at how it wires the β port in its conjunction evaluation — likely
directly analogous to the emit_body fix above.

### Session F-214 notes (added 2026-03-22)

**Wrong sandbox — reverted.** F-214 spent context debugging backtracking in `prolog_emit.c` (the C emitter). This was the wrong path. Key findings:

- Rungs 1–4 already PASS via `-pl` C emitter (confirmed this session).
- Rung 5 (backtrack/member) fails because the C emitter's resumable `_r` function loses inner `_cs` state across stack frame returns. Fixing this requires a continuation-passing redesign of `pl_emit.c` — not worth it.
- **The correct path is `-pl -asm`**: wire through `emit_byrd_asm.c` which already has four-port Byrd box stubs (`emit_prolog_choice`, `emit_prolog_clause`, α/β/γ/ω labels). Backtracking is free — β port wires to next clause α, ω port signals exhaustion. No `_cs` state needed.
- The blocker: `driver/main.c` line 144 hardcodes `pl_emit(prog, out)` regardless of `asm_mode`. One-line fix.
- All changes to `prolog_emit.c` were stashed and reverted. Repo is clean at `3ce6673`.

**M-PROLOG-WIRE-ASM — completed (implied by F-217 rungs 1–4 PASS via ASM path)**

1. In `driver/main.c`, replace the hardcoded `pl_emit(prog, out)` with the `asm_mode` branch (call `asm_emit` when `-asm` is set).
2. Link `prolog_atom.c`, `prolog_unify.c`, `prolog_builtin.c` into the ASM binary (add to `Makefile` runtime link or emit inline calls).
3. Test: `sno2c -pl -asm null.pl -o null.s && nasm -f elf64 null.s && ld ... && ./a.out` → exit 0.
4. Then `hello.pl` → M-PROLOG-HELLO fires.
5. Rungs 1–5: Byrd box β port handles backtracking automatically — no C emitter `_cs` hack needed.

---

## Puzzle Corpus — rung10 Sprint Plan (added 2026-03-23)

`puzzles.pro` has been split into individual stub files, one per puzzle.
Each stub contains the full problem text as comments and a `main` that prints `'puzzleNN: stub\n'`.
Milestones are ordered from easiest to hardest based on problem structure:

| ID | File | Puzzle | Status |
|----|------|--------|--------|
| **M-PZ-14** | puzzle_14.pro | Golf scores (Bill/Ed/Tom wives) | ✅ real search — swipl PASS + JVM PASS |
| **M-PZ-17** | puzzle_17.pro | Country Club dance pairings | ✅ real search — swipl PASS; JVM PASS |
| **M-PZ-15** | puzzle_15.pro | Vernon/Wilson/Yates offices + secretaries | ✅ real search — swipl PASS |
| **M-PZ-16** | puzzle_16.pro | Train crew relations | ✅ real search — swipl PASS |
| **M-PZ-20** | puzzle_20.pro | Pullman car readers | ❌ hardcoded write stub — needs real search |
| **M-PZ-13** | puzzle_13.pro | Murder case roles | ❌ hardcoded write stub — needs real search |
| **M-PZ-18** | puzzle_18.pro | Shopping day scheduling | ❌ hardcoded write stub — needs real search |
| **M-PZ-19** | puzzle_19.pro | Office floors + professions | ❌ hardcoded write stub — needs real search |
| **M-PZ-04** | puzzle_04.pro | Milford occupations + salaries | ✅ real search — swipl PASS; JVM PASS |
| **M-PZ-09** | puzzle_09.pro | Empire Dept Store positions | ✅ real search — swipl PASS; JVM PASS |
| **M-PZ-08** | puzzle_08.pro | Dept Store positions (Ames/Brown/Conroy…) | ✅ real search — swipl PASS; JVM PASS |
| **M-PZ-11** | puzzle_11.pro | Smith family positions | ✅ real search — swipl PASS; JVM 2L (over-generates) |
| **M-PZ-07** | puzzle_07.pro | Brown/Clark/Jones/Smith professions | ✅ real search — swipl PASS; JVM PASS |
| **M-PZ-10** | puzzle_10.pro | Five J-names + last names | ✅ real search — swipl PASS; JVM PASS |
| **M-PZ-03** | puzzle_03.pro | Triple engagement party | ✅ real search — swipl PASS; JVM 20L (over-generates) |
| **M-PZ-12** | puzzle_12.pro | Stillwater High teachers | ❌ hardcoded write stub — needs real search |

Each milestone trigger: the puzzle file prints the correct solution and exits 0 via swipl.

### Source layout

```
test/frontend/prolog/corpus/rung10_programs/
    puzzle_01.pro   ✅ solved (bank positions)
    puzzle_02.pro   ✅ solved (trades Clark/Daw/Fuller)
    puzzle_03.pro   ✅ solved (triple engagement party)
    puzzle_04.pro   ✅ solved (Milford occupations)
    puzzle_05.pro   ✅ solved (bank chess Brown/Clark/Jones/Smith)
    puzzle_06.pro   ✅ solved (occupations Clark/Jones/Morgan/Smith)
    puzzle_07.pro   ✅ solved (professions Brown/Clark/Jones/Smith)
    puzzle_08.pro   ✅ solved (dept store Ames/Brown/Conroy…)
    puzzle_09.pro   ✅ solved (Empire dept store)
    puzzle_10.pro   ✅ solved (five J-names)
    puzzle_11.pro   ✅ solved (Smith family)
    puzzle_12.pro   ✅ solved (Stillwater High teachers)
    puzzle_13.pro   ✅ solved (murder case)
    puzzle_14.pro   ✅ solved (golf scores)
    puzzle_15.pro   ✅ solved (Vernon/Wilson/Yates)
    puzzle_16.pro   ✅ solved (train crew)
    puzzle_17.pro   ✅ solved (Country Club dance)
    puzzle_18.pro   ✅ solved (shopping day)
    puzzle_19.pro   ✅ solved (office floors)
    puzzle_20.pro   ✅ solved (Pullman car readers)
    puzzles.pro     source anthology (read-only reference)
```

---

### Recommendation for F-213

1. `cd snobol4x && make -C src` — rebuild with emit_body fix
2. Test rungs 1–5: `./sno2c -pl test/.../rungN.pro -o /tmp/t.c && gcc ... && ./a.out`
3. If rung 5 (backtrack/member) passes, rungs 6–8 likely follow
4. Consider pivot: instead of C backend, target x64 ASM emitter directly
   (emit native NASM α/β/γ/ω labels). Read ARCH.md + BACKEND-X64.md.
   The C path is good for debugging; ASM is what the design spec calls for.
