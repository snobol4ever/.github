# FRONTEND-PROLOG-JVM.md — Prolog → JVM Backend (L4)

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
| **Prolog JVM** | `main` PJ-77a — parse gaps fixed; corpus 30/30 | `b7b7aa7` PJ-77a | M-PJ-SWI-BASELINE |

### CRITICAL NEXT ACTION (PJ-78)

**PJ-77 findings: 2 parse gaps fixed. Corpus 30/30. No regressions.**

**What was done PJ-77 (commit PJ-77a):**
1. `-atom` prefix fix — `prolog_parse.c` unary minus now handles `-atom` → `-(Atom)` compound (was number-only)
2. `div`/`rdiv` added to `BIN_OPS` table (prec 400, left-assoc) — was missing, caused parse error
3. `else`/`endif`/`f()` already worked — no fix needed
4. `(b:-c)` in list already works via parens — bare `b:-c` in list not a real SWI pattern
- **Context note:** Java proxy noise (`JAVA_TOOL_OPTIONS` JWT spam) consumed ~4% context. Fix: add `2>/dev/null` alias for java at session start.

**SWI baseline so far (tests/core/):**
- `test_list.pl` — 0p/1f: `true(Expr)` opts variable-sharing gap (known)
- `test_exception.pl` — 0p/5f/1s: throw/catch semantics gaps
- `test_arith/unify/dcg/misc.pl` — compile errors (some parse gaps remain)

**PJ-78 task: M-PJ-SWI-BASELINE continued**

**Task 1 — CRITICAL: `true(Expr)` opts variable-sharing fix**
- Problem: `test(name, X==y) :- Body` — bridge emits `pj_term_var()` for `X` in opts, disconnected from `X` in `Body`
- E_CLAUSE layout: `children[0..n_args-1]` = head args, `children[n_args..]` = body goals; `dval`=n_args, `ival`=n_vars
- Fix: store body children pointer+count in `PjTestInfo`; in bridge for test/2 `true(Expr)`: inline `pj_emit_body(body_goals) + pj_emit_goal(expr_check)` in same JVM frame
- `pj_emit_body` signature requires full frame locals setup — non-trivial

**Task 2 — remaining parse gaps (run test_arith/unify/dcg/misc to find)**
- Upload `swipl-devel-master.zip` to get actual failing files

**Task 3 — throw/catch semantics (test_exception.pl)**
- Needs `swipl-devel-master.zip`

```bash
git clone https://TOKEN@github.com/snobol4ever/snobol4x
git clone https://TOKEN@github.com/snobol4ever/.github
apt-get install -y --fix-missing default-jdk nasm libgc-dev swi-prolog
make -C snobol4x/src
export JAVA_TOOL_OPTIONS=""   # suppress proxy JWT spam — saves ~4% context window
# SWI test files: unzip swipl-devel-master.zip to /tmp/
# Read §NOW above. Start at CRITICAL NEXT ACTION.
```

**Key files:**
- `snobol4x/src/frontend/prolog/prolog_emit_jvm.c` — linker ~line 6995 (`pj_linker_*`)
- `snobol4x/test/frontend/prolog/plunit.pl` — shim (keep in sync with C string literal)
- SWI tests: `swipl-devel-master/tests/core/test_*.pl` (58 files)

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



*FRONTEND-PROLOG-JVM.md = L4. §NOW = ONE bootstrap block only — current session's next action. Prior session findings → SESSIONS_ARCHIVE.md only. Completed milestones → MILESTONE_ARCHIVE.md. Size target: ≤8KB total.*
