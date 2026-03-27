# ARCH-prolog-jvm-history.md — Prolog × JVM Milestone History
Operational §NOW → SESSION-prolog-jvm.md.
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
| **M-PJ-ASSERTZ** | `assertz/1`, `asserta/1` — dynamic DB (Scrip dep) | ✅ |
| **M-PJ-RETRACT** | `retract/1` — peek-then-remove, 5/5 rung14 | ✅ |
| **M-PJ-ATOP** | `@<`/`@>`/`@=<`/`@>=` as parser infix operators — Scrip dep | ✅ |
| **M-PJ-SORT** | `sort/2`, `msort/2` — insertion sort, optional dedup | ✅ |
| **M-PJ-SUCC-PLUS** | `succ/2`, `plus/3` — successor/addition builtins | ✅ |
| **M-PJ-FORMAT** | `format/1`, `format/2` — ~w ~a ~n ~d ~i directives | ✅ |
| **M-PJ-NUMBER-VARS** | `numbervars/3` — name unbound vars as A,B,...Z,A1,...; `$VAR` write support | ✅ |
| **M-PJ-CHAR-TYPE** | `char_type/2` — alpha/alnum/digit/space/upper/lower/to_upper/to_lower/ascii | ✅ |
| **M-PJ-WRITE-CANONICAL** | `writeq/1`, `write_canonical/1`, `print/1`; atom quoting + symbolic token rules | ✅ |
| **M-PJ-SUCC-ARITH** | `max/min/sign/truncate/msb`; bitwise `/\ \/ xor >> <<`; `** ^`; prefix `\`; parser op table | ✅ |
| **M-PJ-STRING-IO** | `atom_string/2`, `number_string/2`, `string_concat/3`, `string_length/2`, `string_lower/2`, `string_upper/2`; rung24 5/5 | ✅ |
| **M-PJ-TERM-STRING** | `term_to_atom/2`, `term_string/2` (forward); rung25 3/3 | ✅ |
| **M-PJ-COPY-TERM** | `copy_term/2`, `string_to_atom/2`, `atomic_list_concat/2,3`, `concat_atom/2`; rung26 5/5 | ✅ |
| **M-PJ-AGGREGATE** | `aggregate_all/3` (count/sum/max/min/bag/set), `nb_setval/2`, `nb_getval/2`, `succ_or_zero/2`; rung27 5/5 | ✅ |
| **M-PJ-EXCEPTIONS** | `catch/3`, `throw/1` — ISO exception machinery; rung28 5/5 | ✅ |
| **M-PJ-NUMBER-OPS** | `sqrt/sin/cos/tan/exp/log/atan/atan2/float/float_integer_part/float_fractional_part/pi/e`; `truncate/ceiling/floor/round` float→int; `gcd/2`; rung29 5/5 | ✅ |
| **M-PJ-DCG** | DCG `-->` rules, `phrase/2,3`, `{}/1` inline goals, pushback notation; rung30 5/5 | ✅ |
| **M-PJ-PLUNIT-SHIM** | SWI `tests/core/` converted to standalone `.pro` (564 tests); loads+runs under SWI | ✅ |
| **M-PJ-LINKER** | plunit linker in prolog_emit_jvm.c — raw SWI .pl files compile directly; test_list 10/11 | ✅ |
| **M-PJ-TRUE-EXPR** | `true(Expr)` var-sharing fix — self-reporting bridge, pj_inline shim path; 2/2 pass | ✅ |
| **M-PJ-SWI-BASELINE** | Run all 564 converted tests against JVM backend; record pass/fail baseline | ❌ |

---

## Session Bootstrap (every PJ-session)

```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y --fix-missing default-jdk nasm libgc-dev swi-prolog
make -C snobol4x/src
# Read §NOW above. Start at CRITICAL NEXT ACTION.
```

---

**Sprint order:** ASSERTZ → RETRACT → SORT → SUCC-PLUS → FORMAT → STRING-OPS → AGGREGATE → COPY-TERM → EXCEPTIONS → NUMBER-OPS → DCG.



