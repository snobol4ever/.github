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
| Full milestone history | `ARCH-prolog-jvm-history.md` | completed work, milestone IDs |
| JVM Prolog runtime design | `ARCH-prolog-jvm.md` | term encoding, trail, clause dispatch |

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
| **Prolog JVM** | `main` PJ-83b | `840e966` PJ-83b | M-PJ-SWI-BASELINE |

### ⚠️ CANONICAL ARCHITECTURE — READ BEFORE TOUCHING SWI TESTS

**DO NOT use `wrap_swi.py`. DO NOT preprocess SWI `.pl` files in Python.**
**DO NOT invent a new shim layer. The right machinery already exists in `prolog_emit_jvm.c`.**

The canonical pipeline for SWI plunit tests:
1. Feed raw SWI `.pl` files **directly** to `sno2c -pl -jvm`
2. The **plunit linker** inside `prolog_emit_jvm.c` detects `use_module(library(plunit))`, scans `begin_tests`/`end_tests` directives and `test/N` clause heads, and emits `assertz(pj_suite/pj_test)` facts + bridge predicates at JVM init time
3. The embedded `pj_plunit_shim_src[]` C-string (in `prolog_emit_jvm.c`) provides `run_tests`, `pj_run_one`, counters etc — **this is the shim**, not `test/frontend/prolog/plunit.pl`
4. `test/frontend/prolog/plunit_mock.pro` is an **alternative** stand-alone mock — DO NOT mix it with the linker; pick one approach

Key functions in `prolog_emit_jvm.c`:
- `pj_linker_has_plunit()` — detects `use_module(library(plunit))`
- `pj_linker_scan()` — pass1: suite names from `begin_tests` directives; pass2: test/1 test/2 clause heads → `PjTestInfo[]`
- `pj_linker_emit_plunit_shim()` — parse+lower+emit embedded shim, skipping user-defined predicates
- `pj_linker_emit_main_assertz()` — emit `assertz(pj_suite/pj_test)` in JVM `<clinit>`

**Known linker limitations to fix (NEXT ACTIONS):**
1. **Multi-suite test files**: `pj_linker_scan` pass-2 assigns all tests to `suite[0]` — wrong for files with multiple `begin_tests` blocks. Fix: track current suite during pass-2 by interleaving directive and E_CHOICE walks.
2. **Variable sharing in `true(Expr)` tests**: linker emits `assertz(pj_test(Suite,Name,Opts,BridgeAtom))` where `BridgeAtom` is a call to a bridge predicate — breaks variable sharing between `Opts` (e.g. `true(X==y)`) and the test body that binds `X`. Fix: inline the body term directly into the `pj_test` assertz instead of using a bridge atom.
3. **`=@=` structural equivalence**: not implemented — skip tests using it.
4. **`unifiable/2`**: not implemented.
5. **`cut_to`**: cut across catch boundary — not implemented.

**SWI baseline pass/fail (tests/core/) — as of PJ-82b, via old wrap_swi.py:**

| Test file | Passed | Failed | Skipped | Notes |
|-----------|--------|--------|---------|-------|
| `test_list` | 0 | 1 | 0 | `memberchk` fails |
| `test_arith` | 7 | 51 | 6 | GMP/bignum suite failures expected |
| `test_unify` | 1 | 11 | 0 | variable sharing, `unifiable/2` |
| `test_dcg` | 5 | 29 | 3 | multi-suite scan + variable sharing |
| `test_misc` | 0 | 3 | 0 | `cut_to`, `read_only_flag` |

**PJ-83a (HEAD):** parser fix — `fx 1150` prefix atoms (`dynamic`, `discontiguous`, `multifile`, `use_module`, `ensure_loaded`, `meta_predicate`, `mode`) now parse without parens. Directive prec raised to 1200. Enables raw SWI files with bare `:- dynamic foo/1.` to parse correctly.

```bash
git clone https://TOKEN@github.com/snobol4ever/snobol4x
git clone https://TOKEN@github.com/snobol4ever/.github
apt-get install -y --fix-missing default-jdk nasm libgc-dev swi-prolog
make -C snobol4x/src
export JAVA_TOOL_OPTIONS=""   # suppress proxy JWT spam
# SWI upstream tests: sparse clone
git clone --depth=1 --filter=blob:none --sparse https://github.com/SWI-Prolog/swipl-devel.git /tmp/swipl-devel
cd /tmp/swipl-devel && git sparse-checkout set tests/core
# Run raw SWI file directly — NO wrap_swi.py:
#   ./sno2c -pl -jvm /tmp/swipl-devel/tests/core/TEST.pl > /tmp/TEST.j
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
