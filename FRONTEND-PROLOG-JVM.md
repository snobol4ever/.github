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
| **Prolog JVM** | `main` PJ-64 — baseline 20/20 rung11–rung23 ✅ | `e897666` PJ-64 | M-PJ-STRING-IO |

### CRITICAL NEXT ACTION (PJ-65)

**Baseline: 20/20 rung11–rung23 ✅. snobol4x HEAD `e897666`.**

**Next milestone: M-PJ-STRING-IO — implement `atom_string/2`, `number_string/2`, `string_concat/3`, `string_length/2`, `string_lower/2`, `string_upper/2`.**

**Implementation plan:**
1. Create `test/frontend/prolog/corpus/rung24_string_io/` — 5 test cases (t01–t05), `.pro` + `.expected`
2. Add JVM helper methods + `pj_emit_goal` dispatch in `prolog_emit_jvm.c` following `atom_concat`/`atom_chars` pattern
3. Register names in builtin whitelist (`prolog_builtin.c` / whitelist array near line 2941)
4. Build, run rung24 to green, confirm rung11–23 no regressions
5. Commit snobol4x, update §NOW + PLAN.md, push both repos

**Bootstrap PJ-65:**
```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y --fix-missing default-jdk nasm libgc-dev swi-prolog
make -C snobol4x/src
# Read §NOW above. Start at CRITICAL NEXT ACTION.
```

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
| **M-PJ-ASSERTZ** | `assertz/1`, `asserta/1` — dynamic DB (Scripten dep) | ✅ |
| **M-PJ-RETRACT** | `retract/1` — peek-then-remove, 5/5 rung14 | ✅ |
| **M-PJ-ATOP** | `@<`/`@>`/`@=<`/`@>=` as parser infix operators — Scripten dep | ✅ |
| **M-PJ-SORT** | `sort/2`, `msort/2` — insertion sort, optional dedup | ✅ |
| **M-PJ-SUCC-PLUS** | `succ/2`, `plus/3` — successor/addition builtins | ✅ |
| **M-PJ-FORMAT** | `format/1`, `format/2` — ~w ~a ~n ~d ~i directives | ✅ |
| **M-PJ-NUMBER-VARS** | `numbervars/3` — name unbound vars as A,B,...Z,A1,...; `$VAR` write support | ✅ |
| **M-PJ-CHAR-TYPE** | `char_type/2` — alpha/alnum/digit/space/upper/lower/to_upper/to_lower/ascii | ✅ |
| **M-PJ-WRITE-CANONICAL** | `writeq/1`, `write_canonical/1`, `print/1`; atom quoting + symbolic token rules | ✅ |
| **M-PJ-SUCC-ARITH** | `max/min/sign/truncate/msb`; bitwise `/\ \/ xor >> <<`; `** ^`; prefix `\`; parser op table | ✅ |

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

**Sprint order:** ASSERTZ → RETRACT → SORT → SUCC-PLUS → FORMAT → STRING-OPS → AGGREGATE → COPY-TERM → EXCEPTIONS → NUMBER-OPS → DCG.



*FRONTEND-PROLOG-JVM.md = L4. §NOW = ONE bootstrap block only — current session's next action. Prior session findings → SESSIONS_ARCHIVE.md only. Completed milestones → MILESTONE_ARCHIVE.md. Size target: ≤8KB total.*
