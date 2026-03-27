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
| **Prolog JVM** | `main` PJ-83b | `fb09892` PJ-83b | M-PJ-SWI-BASELINE |

### ⚠️ CANONICAL ARCHITECTURE — READ BEFORE TOUCHING SWI TESTS

**DO NOT use `wrap_swi.py`. DO NOT preprocess SWI `.pl` files in Python.**
**DO NOT invent a new shim layer. The right machinery already exists in `prolog_emit_jvm.c`.**

The canonical pipeline for SWI plunit tests:
1. Feed raw SWI `.pl` files **directly** to `sno2c -pl -jvm`
2. The **plunit linker** inside `prolog_emit_jvm.c` detects `use_module(library(plunit))`, scans `begin_tests`/`end_tests` directives and `test/N` clause heads, and emits `assertz(pj_suite/pj_test)` facts + bridge predicates at JVM init time
3. The embedded `pj_plunit_shim_src[]` C-string (in `prolog_emit_jvm.c`) provides `run_tests`, `pj_run_one`, counters etc — **this is the shim**, not `test/frontend/prolog/plunit.pl`
4. `test/frontend/prolog/plunit_mock.pro` is an **alternative** stand-alone mock — DO NOT mix it with the linker; pick one approach

Key functions in `prolog_emit_jvm.c`:
- `pj_linker_prescan()` — called from `main.c` BEFORE `prolog_program_free()`, walks `PlProgram` in source order to map each `test/N` clause to its `begin_tests` suite
- `pj_linker_has_plunit()` — detects `use_module(library(plunit))`
- `pj_linker_scan()` — pass1: suite names from `begin_tests` directives; pass2: test/1 test/2 clause heads → `PjTestInfo[]`, uses prescan map for suite assignment
- `pj_linker_emit_plunit_shim()` — parse+lower+emit embedded shim, skipping user-defined predicates AND synthetics (forall/2, forall_fails/2)
- `pj_linker_emit_main_assertz()` — emit `assertz(pj_suite/pj_test)` in JVM `<clinit>`

**Bridge naming:** methods are `p_pjt__{suite}_{testname}_0` (prefix `pjt__` avoids user predicate collision; `_N` suffix for repeated test names in same suite).

**RESOLVED (fb09892):**
1. ~~Multi-suite test files~~: **FIXED** — `pj_linker_prescan()` walks `PlProgram` in source order before free, maps test clauses to correct suite.
2. ~~Variable sharing in `true(Expr)` tests~~: **Already implemented** — `pj_inline` path + self-reporting bridge inlines body+check in same JVM frame.
3. ~~`forall` duplicate method~~: **FIXED** — shim now skips `forall/2` and `forall_fails/2`.
4. ~~Bridge name collision with user predicates~~: **FIXED** — `pjt__` prefix + `_N` suffix for repeated test names.
5. ~~Unary `+` parse error~~: **FIXED** — `+` now handled as `fy 200` prefix, fixes `:- style_check(+no_effect)`.

**Remaining known limitations (NEXT ACTIONS):**
1. **`=@=` structural equivalence**: not implemented — skip tests using it.
2. **`unifiable/2`**: not implemented.
3. **`cut_to`**: cut across catch boundary — not implemented.
4. **`test_arith` parse errors**: 98 parse errors in test_arith.pl (line 633: spaced integer literals `0b10000000 00000000...`). Parser does not handle spaced numeric literals.
5. **`memberchk` variable sharing** (`test_list`): `test(memberchk, true(X==y)) :- memberchk(X,[y])` fails — bridge not detecting this pattern correctly.
6. **`f()` zero-arity compound** (`test_unify:unify_arity_0`): `X == f()` — `f()` is parsed as atom `f`, not compound arity 0.

**SWI baseline pass/fail (tests/core/) — as of fb09892, raw SWI files via sno2c -pl -jvm:**

| Test file | Passed | Failed | Skipped | Notes |
|-----------|--------|--------|---------|-------|
| `test_list` | 0 | 1 | 0 | `memberchk` var-sharing |
| `test_arith` | — | — | — | 98 parse errors (spaced numeric literals) |
| `test_unify` | 2 | 10 | 0 | unifiable/2, cycle, f(), var-sharing |
| `test_dcg` | ? | ? | ? | not yet re-run with new linker |
| `test_misc` | 0 | 3 | 0 | `cut_to`, `read_only_flag` |

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
