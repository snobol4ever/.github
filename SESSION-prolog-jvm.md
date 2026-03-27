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
| **Prolog JVM** | `main` PJ-83d | `5854a82` PJ-83d | M-PJ-SWI-BASELINE |

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

**Bridge opts detection:** bare expression opts `X==y` (not wrapped in `true(...)`) are now detected in both `has_true_expr` (bridge emitter) and `is_true_expr` (assertz loop). Both must agree or the test runs twice. The assertz emits `pj_inline` atom → `run_one` pj_inline branch fires → self-reporting bridge. `run_succeed` second clause excludes `pj_inline`.

**RESOLVED (88c6648 / 5854a82):**
1. ~~Multi-suite test files~~: FIXED — prescan.
2. ~~Variable sharing in `true(Expr)` / bare-expr tests~~: FIXED — `pj_inline` bridge path; bare exprs (`X==y`) now detected alongside `true(E)`.
3. ~~`forall` duplicate method~~: FIXED.
4. ~~Bridge name collision~~: FIXED — `pjt__` prefix.
5. ~~Unary `+` parse error~~: FIXED.
6. ~~DCG pushback notation `Head,Pushback --> Body`~~: FIXED — parser head at 1199, `dcg_expand_clause` gains pushback param.
7. ~~`phrase([], List)` → `p____2` undefined~~: FIXED — nil/cons/var-NT cases in direct+ucall+`pj_call_goal` paths; `pj_term_var()` for fresh L1.
8. ~~Spaced numeric literals (`0b10000000 00000000...`)~~: FIXED — lexer absorbs spaces within `0b`/`0o`/`0x`/decimal; NaN/Inf float suffix.
9. ~~`memberchk` variable sharing~~: FIXED — bare-expr opts → `pj_inline`.
10. ~~Stack VerifyError~~: FIXED — all stack floors raised to 512.
11. ~~`garbage_collect/0`, `trim_stacks/0`~~: FIXED — no-op builtins.
12. ~~`?=/2` (can_compare)~~: FIXED — `pj_is_ground` + `pj_can_compare` JVM helpers.
13. ~~Mixed int/float arithmetic~~: FIXED — `E_ADD/SUB/MPY/DIV` now float-aware; `abs`/`min`/`max` float variants; `sign` float path; `copysign/2` added.

**Remaining known limitations (NEXT ACTIONS):**
1. **`=@=` structural equivalence**: not implemented — skip tests using it (affects `test_dcg` nonlin, meta0).
2. **`unifiable/3`**: not implemented.
3. **`cut_to`**: cut across catch boundary — not implemented.
4. **`\+` swallowing exceptions**: `not1_a/b`, `not2_a/b` in `test_dcg` — `\+` catches exception instead of re-raising.
5. **`cut1_b`, `curlycut_b`** in `test_dcg`: cut/`{!}` inside DCG not pruning across `phrase` with unbound rest.
6. **`test_arith` remaining failures (140)**: mixed int/float arithmetic in arithmetic eval still misses runtime variable cases (compile-time `pj_arith_is_float` can't see variable types); `sign`/`copysign`/`float_fractional_part` fixes landed but some tests still fail — investigate `arith_basics` cluster with `goal failed`.
7. **`test_dcg` context suite**: pushback-notation DCG semantics mostly working; `generalcontext`/`vd`/`forprogrammers` still failing (deep DCG features).
8. **`test_misc`**: not re-run this session — `cut_to`, `read_only_flag` still expected to fail.

**SWI baseline pass/fail (tests/core/) — as of 5854a82:**

| Test file | Passed | Failed | Skipped | Notes |
|-----------|--------|--------|---------|-------|
| `test_list` | **1** | 0 | 0 | ✅ memberchk fixed |
| `test_arith` | **63** | 140 | 1 | spaced literals fixed; mixed float WIP |
| `test_unify` | **7** | 4 | 0 | cycle/unifiable still unimplemented |
| `test_dcg` | **7** | 17 | 3 | pushback+phrase fixed; =@=, \+, cut remain |
| `test_misc` | 0 | 3 | 0 | not re-run; cut_to, read_only_flag |

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

**test_dcg parse errors (fb09892):** Lines 196–208 use DCG rules with conjunction in the head (`a, [_] --> !,{fail}.`) — non-standard SWI extension. Parser does not handle `','` as DCG head. These are in the `context` suite. Skipping for now.
