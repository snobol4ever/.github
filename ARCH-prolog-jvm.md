# ARCH-prolog-jvm.md — Prolog × JVM: Milestone History

Operational §NOW → FRONTEND-PROLOG-JVM.md.
JVM runtime design → ARCH-jvm-prolog.md.

## Milestone Table

| ID | Feature | Status |
|----|---------|--------|
| M-PJ-SCAFFOLD | `-pl -jvm null.pl → null.j` assembles + exits 0 | ✅ |
| M-PJ-HELLO | `write('hello'), nl.` → JVM output | ✅ |
| M-PJ-FACTS | Rung 2: deterministic fact lookup | ✅ |
| M-PJ-UNIFY | Rung 3: head unification, compound terms | ✅ |
| M-PJ-ARITH | Rung 4: `is/2` arithmetic | ✅ |
| M-PJ-BACKTRACK | Rung 5: `member/2` — β port, all solutions | ✅ |
| M-PJ-LISTS | Rung 6: `append/3`, `length/2`, `reverse/2` | ✅ |
| M-PJ-CUT | Rung 7: `differ/N`, closed-world `!, fail` | ✅ |
| M-PJ-RECUR | Rung 8: `fibonacci/2`, `factorial/2` | ✅ |
| M-PJ-BUILTINS | Rung 9: `functor/3`, `arg/3`, `=../2`, type tests | ✅ |
| M-PJ-CORPUS-R10 | Rung 10: Lon's puzzle corpus PASS | ✅ |
| M-PJ-NEQ | `\=/2` emit missing | ✅ |
| M-PJ-STACK-LIMIT | Dynamic `.limit stack` via term depth walker | ✅ |
| M-PJ-NAF-TRAIL | `\+` trail: save mark before inner goal, unwind both paths | ✅ |
| M-PJ-BODYFAIL-TRAIL | Body-fail trail unwind: `bodyfail_N` trampoline per clause | ✅ |
| M-PJ-BETWEEN | `between/3` — synthetic p_between_3 method | ✅ |
| M-PJ-DISJ-ARITH | Plain `;` retry loop — tableswitch dispatch | ✅ |
| M-PJ-CUT-UCALL | `!` + ucall body sentinel propagation | ✅ |
| M-PJ-NAF-INNER-LOCALS | NAF helper method — fix frame aliasing | ✅ |
| M-PJ-DISPLAY-BT | puzzle_03 over-generation workaround; 20/20 | ✅ |
| M-PJ-PZ-ALL-JVM | All 20 puzzle solutions pass JVM | ✅ |
| M-PJ-FINDALL | `findall/3` | ✅ |
| M-PJ-ATOM-BUILTINS | atom_chars/length/concat/codes/char_code etc. | ✅ |
| M-PJ-ASSERTZ | `assertz/1`, `asserta/1` | ✅ |
| M-PJ-RETRACT | `retract/1` | ✅ |
| M-PJ-ATOP | `@<`/`@>`/`@=<`/`@>=` infix operators | ✅ |
| M-PJ-SORT | `sort/2`, `msort/2` | ✅ |
| M-PJ-SUCC-PLUS | `succ/2`, `plus/3` | ✅ |
| M-PJ-FORMAT | `format/1,2` — ~w ~a ~n ~d ~i | ✅ |
| M-PJ-NUMBER-VARS | `numbervars/3`, `$VAR` write support | ✅ |
| M-PJ-CHAR-TYPE | `char_type/2` | ✅ |
| M-PJ-WRITE-CANONICAL | `writeq/1`, `write_canonical/1`, `print/1` | ✅ |
| M-PJ-SUCC-ARITH | `max/min/sign/truncate/msb`; bitwise ops; `** ^` | ✅ |
| M-PJ-STRING-IO | `atom_string/2`, `number_string/2`, string ops | ✅ |
| M-PJ-TERM-STRING | `term_to_atom/2`, `term_string/2` | ✅ |
| M-PJ-COPY-TERM | `copy_term/2`, `atomic_list_concat/2,3` | ✅ |
| M-PJ-AGGREGATE | `aggregate_all/3`, `nb_setval/2`, `nb_getval/2` | ✅ |
| M-PJ-EXCEPTIONS | `catch/3`, `throw/1` | ✅ |
| M-PJ-NUMBER-OPS | trig/exp/log/float/round/gcd | ✅ |
| M-PJ-DCG | DCG `-->` rules, `phrase/2,3` | ✅ |
| M-PJ-PLUNIT-SHIM | SWI `tests/core/` 564 tests converted | ✅ |
| M-PJ-LINKER | plunit linker — raw SWI .pl files compile directly | ✅ |
| **M-PJ-SWI-BASELINE** | All 564 converted tests pass JVM backend | ❌ NEXT |
