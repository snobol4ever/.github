# FRONTEND-PROLOG-JVM.md — Prolog → JVM Backend (L3)

Prolog frontend targeting JVM bytecode via Jasmin.
Reuses the existing Prolog IR pipeline (lex → parse → lower) unchanged.
New layer: `prolog_emit_jvm.c` — consumes `E_CHOICE/E_CLAUSE/E_UNIFY/E_CUT/E_TRAIL_*`
and emits Jasmin `.j` files, assembled by `jasmin.jar`.

**Session trigger phrase:** `"I'm working on Prolog JVM"`
**Session prefix:** `PJ` (e.g. PJ-1, PJ-2, PJ-3)
**Driver flag:** `snobol4x -pl -jvm foo.pl → foo.j → java -jar jasmin.jar foo.j`
**Oracle:** `snobol4x -pl -c foo.pl → foo.c → gcc → ./a.out` (the C emitter, rungs 1–9 known good)

*Session state → this file §NOW. Backend reference → BACKEND-JVM.md.*

---

## §NOW — Session State

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Prolog JVM** | `main` PJ-4 — anon wildcard fix, head unify arg index fix, `->` flat n-ary | `3986172` PJ-4 | M-PJ-BACKTRACK |

### Session PJ-4 summary (2026-03-24)

- Fixed anonymous `_`: `pj_emit_term` slot=-1 now emits `pj_term_var()` not `aconst_null`; list head unification `member(X,[X|_])` was failing on tail `pj_unify(rest,null)`
- Fixed head unification arg index: was `aload var_locals[ai]` (wrong — var slot map, not param position); corrected to `aload ai`; `var_locals[1]` was 0 (calloc zero-init) for clauses with 1 named var
- Flattened `->` in `prolog_lower.c`: explicit n-ary `E_FNC("->")`, children[0]=Cond, children[1..]=Then goals (right-spine conjunction unwound); both emitter `->`  handlers updated to `nchildren >= 2`
- rung05 partial: first solution `a` now prints; `b`/`c` not yet — retry loop `cs` progression issue remains

### CRITICAL NEXT ACTION (PJ-5)

```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev
cd snobol4x && make -C src
# rung05 retry: after p_member_2 returns ci=0, cs=1, retry calls clause1
# member(X,[_|T]):-member(X,T) — clause1: T=var_locals[1 in clause1]
# Inspect: ./sno2c -pl -jvm rung05/backtrack.pro -o /tmp/b.j
#          grep -A40 "p_member_2_clause1:" /tmp/b.j
# Check: is T (the tail var) properly aliased to arg1's tail on head unify?
#        Does the recursive call member(X,T) pass the bound T cell?
# Fix order: rung05 retry loop → rung08 arith deref → rung06 list write → rung07 cut → rung09 builtins
BASE=backtrack; PRO=test/frontend/prolog/corpus/rung05_${BASE}/${BASE}.pro
./sno2c -pl -jvm $PRO -o /tmp/$BASE.j && java -jar src/backend/jvm/jasmin.jar /tmp/$BASE.j 2>&1 | grep Generated
java -cp /tmp Backtrack   # expected: a\nb\nc
```

---

---

## Why JVM — Design Rationale

The ASM backend emits Byrd-box four-port code as NASM labels + `jmp`.
The JVM backend does the same thing — but labels become Jasmin `label:` targets
and `jmp` becomes Jasmin `goto`. The four-port model is identical.

Structural oracle: `emit_byrd_jvm.c` (187KB, snobol4x `src/backend/jvm/`).
That file already handles SNOBOL4 → JVM via the same Byrd-box IR.
`prolog_emit_jvm.c` is its sibling: same output format, different input nodes.

Key differences from SNOBOL4 JVM backend:
- No `sno_var_*` static String fields — Prolog uses per-clause local variables
- Trail + unification replace pattern matching primitives
- Choice points replace pattern ALT/ARBNO nodes
- Terms (TERM_t) replace SNOBOL4 strings as the value type

Key similarities (reuse directly):
- Jasmin file skeleton (class header, main method, static helpers)
- `J()` / `JI()` / `JL()` output helpers — copy verbatim
- `jvm_safe_name()` identifier sanitization
- Arithmetic helpers: `sno_arith`, `Long.parseLong` / `ddiv` patterns
- `:S/:F` routing via `ifnull` / `ifnonnull` — exact same trick

---

## Term Representation on JVM

SNOBOL4 JVM uses `java/lang/String` for all values.
Prolog JVM uses `java/lang/Object[]` (boxed term arrays) for all values.

```
TERM encoding on JVM heap (Object[] of length 2+):
  [0] = tag string: "atom", "int", "float", "var", "compound", "ref"
  [1] = value:
        atom      → String (atom name)
        int       → String (decimal, as in SNOBOL4 JVM)
        float     → String (decimal)
        var       → Object[] (points to binding cell, initially null slot)
        compound  → Object[] { tagStr, functor, arity, arg0, arg1, ... }
        ref       → Object[] (points to bound-to term)
  null = unbound variable
```

This keeps all terms as Java objects — no native library needed.
Unification and trail are emitted as static helper methods on the class,
same pattern as `sno_arith` in the SNOBOL4 JVM backend.

---

## Design — `prolog_emit_jvm.c`

### File structure (mirrors `emit_byrd_jvm.c`)

```c
/* prolog_emit_jvm.c — Prolog IR → Jasmin text emitter */

// Output helpers: J(), JI(), JL(), JC(), JSep()  — copy from emit_byrd_jvm.c
// Safe name:      pj_safe_name()                 — like jvm_safe_name()

// Sections:
//   pj_emit_class_header()    — .class public, .super, .method main
//   pj_emit_runtime_helpers() — unify(), trail_push/unwind(), term constructors
//   pj_emit_atom_table()      — static String[] for interned atoms
//   pj_emit_choice()          — E_CHOICE → α/β/ω label chain
//   pj_emit_clause()          — E_CLAUSE → head unify + body goals
//   pj_emit_goal()            — E_FNC / E_UNIFY / E_CUT / arithmetic
//   pj_emit_term()            — E_QLIT / E_ILIT / E_VART / E_FNC (term context)
//   pj_emit_main_init()       — initialization directive call
//   prolog_emit_jvm(prog, out) — entry point
```

### Label conventions (parallel to ASM emitter)

| Concept | ASM label | JVM label |
|---------|-----------|-----------|
| Choice α | `P_FOO_1_alpha` | `p_foo_1_alpha` |
| Choice β (clause N) | `P_FOO_2_alpha` | `p_foo_2_alpha` |
| Choice ω | `P_FOO_omega` | `p_foo_omega` |
| Goal succeed | `goal_N_gamma` | `goal_N_gamma` |
| Goal fail | `goal_N_omega` | `goal_N_omega` |
| Trail mark | `trail_mark_N` | `trail_mark_N` |

### Byrd box wiring — clause selection (Jasmin)

```jasmin
; foo/1 with two clauses
; local 0 = arg0 (Object[])
; local 1 = trail Object[] (growable array reference)
; local 2 = trail mark (int)

p_foo_alpha:
    ; trail mark
    invokestatic  ThisClass/trail_mark()I
    istore 2
    ; try clause 1: unify arg0 with head
    aload 0
    ldc "atom_a"
    invokestatic  ThisClass/unify(Ljava/lang/Object;Ljava/lang/String;)Z
    ifeq p_foo_beta   ; unify failed → try next clause
    ; body of clause 1 ...
    goto p_foo_gamma

p_foo_beta:
    ; unwind trail to mark
    iload 2
    invokestatic  ThisClass/trail_unwind(I)V
    ; trail mark again for clause 2
    invokestatic  ThisClass/trail_mark()I
    istore 2
    ; try clause 2: unify arg0 with head
    aload 0
    ldc "atom_b"
    invokestatic  ThisClass/unify(Ljava/lang/Object;Ljava/lang/String;)Z
    ifeq p_foo_omega
    ; body of clause 2 ...
    goto p_foo_gamma

p_foo_omega:
    iload 2
    invokestatic  ThisClass/trail_unwind(I)V
    goto caller_omega

p_foo_gamma:
    goto caller_gamma
```

### Runtime helpers (emitted inline in class)

```
trail_mark()I          — returns trail.size() as int
trail_unwind(I)V       — restores trail to saved mark, unbinds vars
unify(Object,Object)Z  — WAM-style unification, returns boolean
term_atom(String)      — allocate atom term
term_int(long)         — allocate integer term
term_var()             — allocate unbound variable cell
term_compound(String,int,Object[]) — allocate compound
deref(Object)Object    — dereference chain
write_term(Object)V    — write/1 builtin, mirrors sno_write in JVM backend
```

All implemented as `static` methods in the emitted class — same pattern as
`sno_arith`, `sno_write`, `sno_output_assign` in `emit_byrd_jvm.c`.

---

## Milestone Table

| ID | Trigger | Depends on | Status |
|----|---------|-----------|--------|
| **M-PJ-SCAFFOLD** | `prolog_emit_jvm.c` exists; `-pl -jvm null.pl → null.j` assembles and exits 0; driver wired | — | ✅ |
| **M-PJ-HELLO** | `hello.pl` → `write('hello'), nl.` → JVM output `hello` | M-PJ-SCAFFOLD | ✅ |
| **M-PJ-FACTS** | Rung 2: deterministic fact lookup, `write(answer)` | M-PJ-HELLO | ✅ |
| **M-PJ-UNIFY** | Rung 3: head unification, compound terms | M-PJ-FACTS | ✅ |
| **M-PJ-ARITH** | Rung 4: `is/2` arithmetic — reuse JVM `sno_arith` helpers | M-PJ-UNIFY | ✅ |
| **M-PJ-BACKTRACK** | Rung 5: `member/2` — first backtracking via β port | M-PJ-ARITH | ❌ |
| **M-PJ-LISTS** | Rung 6: `append/3`, `length/2`, `reverse/2` | M-PJ-BACKTRACK | ❌ |
| **M-PJ-CUT** | Rung 7: `differ/N`, closed-world `!, fail` pattern | M-PJ-LISTS | ❌ |
| **M-PJ-RECUR** | Rung 8: `fibonacci/2`, `factorial/2` | M-PJ-CUT | ❌ |
| **M-PJ-BUILTINS** | Rung 9: `functor/3`, `arg/3`, `=../2`, type tests | M-PJ-RECUR | ❌ |
| **M-PJ-CORPUS-R10** | Rung 10: Lon's puzzle corpus — all solved puzzles PASS | M-PJ-BUILTINS | ❌ |

---

## Oracle Comparison Strategy

For each rung, the C emitter is the correctness oracle:
```bash
snobol4x -pl -c   foo.pl -o /tmp/foo.c && gcc /tmp/foo.c -o /tmp/foo_c && /tmp/foo_c
snobol4x -pl -jvm foo.pl -o /tmp/foo.j && java -jar jasmin.jar /tmp/foo.j -d /tmp/ && java -cp /tmp/ FooClass
diff <(/tmp/foo_c) <(java -cp /tmp/ FooClass)
```
Both must produce identical output for the milestone to fire.

---

## Session Bootstrap (every PJ-session)

```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev
make -C snobol4x/src
# Read FRONTEND-PROLOG-JVM.md §NOW for current milestone
# Start at first ❌ in milestone table
```

---

*FRONTEND-PROLOG-JVM.md = L3. ~3KB sprint content max per section. Archive completed milestones to MILESTONE_ARCHIVE.md on session end.*
