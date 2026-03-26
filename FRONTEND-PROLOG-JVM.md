# FRONTEND-PROLOG-JVM.md — Prolog → JVM Backend (L3)

Prolog frontend targeting JVM bytecode via Jasmin.
Reuses the existing Prolog IR pipeline (lex → parse → lower) unchanged.
New layer: `prolog_emit_jvm.c` — consumes `E_CHOICE/E_CLAUSE/E_UNIFY/E_CUT/E_TRAIL_*`
and emits Jasmin `.j` files, assembled by `jasmin.jar`.

**Session trigger phrase:** `"I'm working on Prolog JVM"`
**Session prefix:** `PJ` (e.g. PJ-7, PJ-8, ...)
**Driver flag:** `snobol4x -pl -jvm foo.pl → foo.j → java -jar jasmin.jar foo.j`
**Oracle:** `snobol4x -pl -asm foo.pl` (ASM emitter, rungs 1–9 known good)
**Design reference:** BACKEND-JVM-PROLOG.md (term encoding, runtime helpers, Jasmin patterns)

*Session state → this file §NOW. Backend reference → BACKEND-JVM-PROLOG.md.*

---

## §NOW — Session State

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Prolog JVM** | `main` PJ-51 — stub emitter + directive exec done; `pj_db_assert` stack-height VerifyError on all 5 rung13 | `ce8bc5a` PJ-51 | M-PJ-ASSERTZ |

### CRITICAL NEXT ACTION (PJ-52)

**Baseline: 5/5 rung11 ✅. 5/5 rung12 ✅. snobol4x HEAD `ce8bc5a`.**

**Next milestone: M-PJ-ASSERTZ — fix pj_db_assert stack height, get 5/5 rung13**

**THE BUG:** `pj_db_assert` (in `pj_emit_assertz_helpers`) has inconsistent stack heights at label `pj_db_assert_have_list`. The "new list" path and the "existing list" path leave different numbers of values on the stack when they converge at that label.

**Root cause:** In the "new list" path: after `astore_3` (store new list) + `getstatic pj_db` + `aload_0` + `aload_3` + `invokevirtual HashMap.put` + `pop` + `aload_3` → stack height 1 (the list). In the "existing list" path: after `invokevirtual HashMap.get` + `dup` + `ifnonnull` → the `dup`'d reference is still on stack at height 1. So both paths should leave stack height 1 at `pj_db_assert_have_list`. But the JVM verifier says `4 != 1` — the "new list" path must be leaving 4 items.

**Fix strategy:** Rewrite `pj_db_assert` using a cleaner pattern — store the list to local 3 on both paths, then load it once after the join:

```jasmin
; get or create list, store to local 3
getstatic pj_db
aload_0
invokevirtual HashMap/get
dup
ifnonnull db_assert_have
pop
new ArrayList
dup
invokespecial ArrayList/<init>()V
dup                          ; ArrayList, ArrayList
astore_3                     ; store, keep one on stack
getstatic pj_db
aload_0
aload_3
invokevirtual HashMap/put
pop                          ; discard old value
goto db_assert_join
db_assert_have:
checkcast ArrayList
astore_3
db_assert_join:
; now local 3 = the list, stack empty
; deep-copy term...
; prepend or append...
return
```

**Bootstrap PJ-52:**
```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev swi-prolog
make -C snobol4x/src && cd snobol4x
# Rewrite pj_db_assert in pj_emit_assertz_helpers (~line 1193)
# Build, run rung13 5-way sweep, expect 5/5
# Confirm rung11+rung12 no regressions
# Commit, update §NOW + PLAN.md, push both repos
```

**Baseline: 5/5 rung11 ✅. 5/5 rung12 ✅. snobol4x HEAD `02cc4c6`.**

**Next milestone: M-PJ-ASSERTZ — get 5/5 rung13**

**WHAT WAS DONE (PJ-50):**
- `pj_db` static `HashMap<String,ArrayList<Object[]>>` field added to class header + `<clinit>`.
- `pj_emit_assertz_helpers()` emits 4 Jasmin helper methods: `pj_db_assert_key`, `pj_db_assert`, `pj_db_query`, `pj_copy_term_ground`.
- `assertz/1` and `asserta/1` dispatch added to `pj_emit_goal`.
- Dynamic DB walker appended to every `pj_emit_choice` omega port.
- rung13 corpus created: 5 `.pro` + `.expected` files.
- Build is clean.

**TWO BUGS REMAINING for 5/5 rung13:**

**Bug 1 — Pure-dynamic predicates have no stub method.**
`assertz_atom.pro` does `:- dynamic color/1` then only `assertz(color(...))` calls — no static `color/1` clauses. `pj_emit_choice` is never called for `color/1` so no `p_color_1` method exists. JVM → `NoSuchMethodError`. Fix: in `prolog_emit_jvm()` entry, after emitting static predicates, scan the program for `:- dynamic foo/N` directives and for `:- assertz(foo(...))` at toplevel with no matching static predicate; emit a stub method for each:
```c
/* stub: just the dynamic walker, no static clauses */
J(".method static p_%s_%d(", safe_fn, arity);
for (int i=0; i<arity; i++) J("[Ljava/lang/Object;");
J("I)[Ljava/lang/Object;\n");
J("    .limit stack 16\n    .limit locals %d\n", arity+50);
/* emit only the dynamic DB walker (same code as in pj_emit_choice omega) */
/* then: aconst_null; areturn */
J(".end method\n\n");
```

**Bug 2 — `:- assertz(...)` directives must run before `main`.**
The Prolog parser emits `:- Goal` directives as `E_DIRECTIVE` statements. The JVM emitter's `pj_emit_main()` currently ignores these. Fix: in `pj_emit_main()`, before calling `p_main_0`, scan `prog->head` for `E_DIRECTIVE` statements whose goal is `assertz/1` or `asserta/1` and emit the assertz call inline (same bytecode as `pj_emit_goal` for assertz).

**Bootstrap PJ-51:**
```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev swi-prolog
make -C snobol4x/src && cd snobol4x
# Confirm 5/5 rung11 + 5/5 rung12 baseline
# Fix Bug 1: stub method emitter for pure-dynamic predicates
# Fix Bug 2: directive execution in pj_emit_main
# Build, run rung13 sweep, expect 5/5
# Then run rung11+rung12 regression sweep
# Commit snobol4x, update §NOW, update PLAN.md, push .github
```

---

## Milestone Table

| ID | Trigger | Status |
|----|---------|--------|
| **M-PJ-SCAFFOLD** | `-pl -jvm null.pl → null.j` assembles + exits 0 | ✅ |
| **M-PJ-HELLO** | `write('hello'), nl.` → JVM output `hello` | ✅ |
| **M-PJ-FACTS** | Rung 2: deterministic fact lookup | ✅ |
| **M-PJ-UNIFY** | Rung 3: head unification, compound terms | ✅ |
| **M-PJ-ARITH** | Rung 4: `is/2` arithmetic | ✅ |
| **M-PJ-BACKTRACK** | Rung 5: `member/2` — β port, all solutions | ✅ |
| **M-PJ-LISTS** | Rung 6: `append/3`, `length/2`, `reverse/2` | ✅ |
| **M-PJ-CUT** | Rung 7: `differ/N`, closed-world `!, fail` | ✅ |
| **M-PJ-RECUR** | Rung 8: `fibonacci/2`, `factorial/2` | ✅ |
| **M-PJ-BUILTINS** | Rung 9: `functor/3`, `arg/3`, `=../2`, type tests | ✅ |
| **M-PJ-CORPUS-R10** | Rung 10: Lon's puzzle corpus PASS | ✅ |
| **M-PJ-NEQ** | `\=/2` emit missing in `pj_emit_goal` | ✅ |
| **M-PJ-STACK-LIMIT** | Dynamic `.limit stack` via term depth walker | ✅ |
| **M-PJ-NAF-TRAIL** | `\+` trail: save mark before inner goal, unwind both paths | ✅ |
| **M-PJ-BODYFAIL-TRAIL** | Body-fail trail unwind: `bodyfail_N` trampoline per clause | ✅ |
| **M-PJ-BETWEEN** | `between/3` — synthetic p_between_3 method | ✅ |
| **M-PJ-DISJ-ARITH** | Plain `;` retry loop — tableswitch dispatch; puzzle_12 PASS | ✅ |
| **M-PJ-CUT-UCALL** | `!` + ucall body sentinel propagation | ✅ |
| **M-PJ-NAF-INNER-LOCALS** | NAF helper method — fix frame aliasing; puzzle_18 PASS | ✅ |
| **M-PJ-DISPLAY-BT** | puzzle_03 over-generation workaround; 20/20 | ✅ |
| **M-PJ-PZ-ALL-JVM** | All 20 puzzle solutions pass JVM | ✅ |
| **M-PJ-FINDALL** | `findall/3` — collect all solutions into list | ✅ |
| **M-PJ-ATOM-BUILTINS** | atom_chars/length/concat/codes/char_code etc. | ✅ |
| **M-PJ-ASSERTZ** | `assertz/1`, `asserta/1` — dynamic DB (Scripten dep) | ❌ **NEXT** |

---

## Session Bootstrap (every PJ-session)

```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev
make -C snobol4x/src
# Read §NOW above. Start at CRITICAL NEXT ACTION.
```

---

*FRONTEND-PROLOG-JVM.md = L4. §NOW = ONE bootstrap block only — current session's next action. Prior session findings → SESSIONS_ARCHIVE.md only. Completed milestones → MILESTONE_ARCHIVE.md. Size target: ≤8KB total.*

---

## Tiny-Prolog Enhancement Roadmap — ISO Gap Closure

**Oracle:** `swipl -q -g halt -t main file.pro`
**Tests:** `test/frontend/prolog/corpus/rung11_*/` onward
**Impl:** `prolog_emit_jvm.c` (emit) + `prolog_builtin.c` (runtime helpers)

### Tier 1 — High Impact

| Milestone | Feature | Rung | Status |
|-----------|---------|------|--------|
| M-PJ-FINDALL | `findall/3` | rung11 | ✅ |
| M-PJ-ATOM-BUILTINS | atom_chars/codes/length/concat/char_code, upcase/downcase | rung12 | ✅ |
| M-PJ-ASSERTZ | `assertz/1`, `asserta/1` dynamic DB — **Scripten Demo dep** | rung13 | ❌ **NEXT** |
| M-PJ-RETRACT | `retract/1`, `retractall/1` (depends: ASSERTZ) | rung14 | ❌ |
| M-PJ-SORT | `sort/2`, `msort/2`, `keysort/2` | rung14b | ❌ |

### Tier 2 — Medium Impact

| Milestone | Feature | Rung | Status |
|-----------|---------|------|--------|
| M-PJ-SUCC-PLUS | `succ/2`, `plus/3` reversible arithmetic | rung15 | ❌ |
| M-PJ-FORMAT | `format/1`, `format/2`, `format(atom(A),...)` | rung16 | ❌ |
| M-PJ-STRING-OPS | `split_string/4`, `string_concat/3`, etc. | rung17 | ❌ |
| M-PJ-AGGREGATE | `bagof/3`, `setof/3` (depends: FINDALL+SORT) | rung18 | ❌ |
| M-PJ-COPY-TERM | `copy_term/2` deep copy with fresh vars | rung19 | ❌ |
| M-PJ-EXCEPTIONS | `catch/3`, `throw/1`, ISO error terms | rung20 | ❌ |
| M-PJ-NUMBER-OPS | Extended `is/2`: trig, round, abs, max, min | rung21 | ❌ |

### Tier 3 — Future

| Milestone | Feature | Status |
|-----------|---------|--------|
| M-PJ-DCG | DCG `-->`, `phrase/2` (depends: COPY-TERM) | 💭 |

**Sprint order:** ATOM-BUILTINS → **ASSERTZ** → SORT → SUCC-PLUS → RETRACT → FORMAT → STRING-OPS → AGGREGATE → COPY-TERM → EXCEPTIONS → NUMBER-OPS → DCG.
