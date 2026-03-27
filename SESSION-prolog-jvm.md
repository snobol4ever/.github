# SESSION-prolog-jvm.md — Prolog × JVM (snobol4x)

**Repo:** snobol4x · **Frontend:** Prolog · **Backend:** JVM (Jasmin)
**Session prefix:** `PJ` · **Trigger:** "playing with Prolog JVM"
**Driver:** `sno2c -pl -jvm foo.pl -o foo.j` → `java -jar jasmin.jar foo.j -d .` → `java FooClass`
**Oracle:** `sno2c -pl -asm foo.pl` (ASM emitter)
**Deep reference:** all ARCH docs cataloged in `ARCH-index.md`

## Subsystems

| Subsystem | Doc | Go there when |
|-----------|-----|---------------|
| Prolog language, IR nodes | `FRONTEND-PROLOG.md` | parser/AST questions |
| Full milestone history | `ARCH-prolog-jvm.md` | completed work, milestone IDs |
| JVM Prolog runtime design | `ARCH-jvm-prolog.md` | term encoding, trail, clause dispatch |

---

## §BUILD

```bash
cd snobol4x && make -C src
export JAVA_TOOL_OPTIONS=""
```

## Key Files

| File | Role |
|------|------|
| `src/frontend/prolog/prolog_emit_jvm.c` | JVM emitter + linker |
| `test/frontend/prolog/plunit.pl` | plunit shim |

---

## §NOW — Session State

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Prolog JVM** | `main` PJ-79b — parse gaps fixed; all 5 SWI files compile; corpus 107/107 | `75e46c2` PJ-79b | M-PJ-SWI-BASELINE |

### CRITICAL NEXT ACTION (PJ-80)

**PJ-79 findings: test_list/arith/dcg/unify/misc all compile clean. Corpus 107/107. No regressions.**

**What was done PJ-79 (commits PJ-79a, PJ-79b):**
- PJ-79a: suppress unused `loc_mstart` warnings in `emit_byrd_net.c`
- PJ-79b parser fixes (`prolog_parse.c`):
  1. `:-` as binary op (prec 1200) in `BIN_OPS` + Pratt loop (`TK_NECK`) — fixes `(a :- b(...))` inside args
  2. Unary minus before variables and parens (`-V0`, `-(expr)`) — was only `-atom`/`-op`
- PJ-79b lexer fixes (`prolog_lex.c`):
  3. `0o` octal literal support (was missing)
  4. `Xe`/`XeN` float literals without decimal point (e.g. `10e300`)
- PJ-79b `wrap_swi.py` fixes:
  5. Multi-line directive stripping (consume through terminating `.`)
  6. `:- dynamic` with predicate on next line (`STRIP_BARE_RE` relaxed to `\s*$`)
  7. Xfail suites requiring GMP/pushback-DCG: `minint`, `maxint`, `minint_promotion`, `maxint_promotion`, `max_integer_size`, `float_compare`, `context`

**SWI baseline compile status (tests/core/):**
- `test_list.pl` ✅ compiles clean
- `test_unify.pl` ✅ compiles clean
- `test_misc.pl` ✅ compiles clean
- `test_arith.pl` ✅ compiles clean (7 GMP/NaN suites xfailed)
- `test_dcg.pl` ✅ compiles clean (pushback-DCG `context` suite xfailed)
- `test_exception.pl` — NOT YET RUN (throw/catch semantics gaps from PJ-78)

**PJ-80 task: run the 5 compiled test files, assess pass/fail, then tackle test_exception.pl**

```bash
git clone https://TOKEN@github.com/snobol4ever/snobol4x
git clone https://TOKEN@github.com/snobol4ever/.github
apt-get install -y --fix-missing default-jdk nasm libgc-dev swi-prolog
make -C snobol4x/src
export JAVA_TOOL_OPTIONS=""   # suppress proxy JWT spam — saves ~5% context window
# SWI test files: unzip swipl-devel-master.zip to /tmp/
# Then: for each of test_list/arith/dcg/unify/misc:
#   python3 test/frontend/prolog/wrap_swi.py /tmp/swipl/swipl-devel-master/tests/core/TEST.pl /tmp/TEST.pro
#   ./sno2c -pl -jvm /tmp/TEST.pro > /tmp/TEST.j
#   java -jar src/backend/jvm/jasmin.jar /tmp/TEST.j -d /tmp/TESTd
#   java -cp /tmp/TESTd <ClassName>
# Read §NOW above. Start at CRITICAL NEXT ACTION.
```

**Key files:**
- `snobol4x/src/frontend/prolog/prolog_emit_jvm.c` — linker ~line 7040 (`pj_linker_emit_bridge`)
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
