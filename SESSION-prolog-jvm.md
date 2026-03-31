# SESSION-prolog-jvm.md — Prolog × JVM (one4all)

**Repo:** one4all · **Frontend:** Prolog · **Backend:** JVM (Jasmin)
**Session prefix:** `PJ` · **Trigger:** "playing with Prolog JVM"
**Driver:** `scrip-cc -pl -jvm foo.pl -o foo.j` → `java -jar jasmin.jar foo.j -d .` → `java FooClass`
**Oracle:** `scrip-cc -pl -asm foo.pl` (ASM emitter)
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
TOKEN=ghp_xxx bash /home/claude/.github/SESSION_BOOTSTRAP.sh
```

All tools, repos, and oracles installed by bootstrap. `export JAVA_TOOL_OPTIONS=""`  if JVM is noisy.


## Key Files

| File | Role |
|------|------|
| `src/frontend/prolog/prolog_emit_jvm.c` | JVM emitter + linker |
| `test/frontend/prolog/plunit.pl` | plunit shim |

---

## §NOW — Session State

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Prolog JVM** | `pj-84-bench-baseline` PJ-84a | `a79906e` PJ-84a | M-PJ-SWI-BASELINE |

**SWI bench suite: 31/31 ✅** (was 19/31 at PJ-83e). See `BENCH-prolog-jvm.md` for grid.

### ⚠️ CANONICAL ARCHITECTURE — READ BEFORE TOUCHING SWI TESTS

**DO NOT use `wrap_swi.py`. DO NOT preprocess SWI `.pl` files in Python.**
**DO NOT invent a new shim layer. The right machinery already exists in `prolog_emit_jvm.c`.**

The canonical pipeline for SWI plunit tests:
1. Feed raw SWI `.pl` files **directly** to `scrip-cc -pl -jvm`
2. The **plunit linker** inside `prolog_emit_jvm.c` detects `use_module(library(plunit))`, scans `begin_tests`/`end_tests` directives and `test/N` clause heads, and emits `assertz(pj_suite/pj_test)` facts + bridge predicates at JVM init time
3. The embedded `pj_plunit_shim_src[]` C-string (in `prolog_emit_jvm.c`) provides `run_tests`, `pj_run_one`, counters etc — **this is the shim**, not `test/frontend/prolog/plunit.pl`
4. `test/frontend/prolog/plunit_mock.pl` is an **alternative** stand-alone mock — DO NOT mix it with the linker; pick one approach

Key functions in `prolog_emit_jvm.c`:
- `pj_linker_prescan()` — called from `main.c` BEFORE `prolog_program_free()`, walks `PlProgram` in source order to map each `test/N` clause to its `begin_tests` suite
- `pj_linker_has_plunit()` — detects `use_module(library(plunit))`
- `pj_linker_scan()` — pass1: suite names from `begin_tests` directives; pass2: test/1 test/2 clause heads → `PjTestInfo[]`, uses prescan map for suite assignment
- `pj_linker_emit_plunit_shim()` — parse+lower+emit embedded shim, skipping user-defined predicates AND synthetics (forall/2, forall_fails/2)
- `pj_linker_emit_main_assertz()` — emit `assertz(pj_suite/pj_test)` in JVM `<clinit>`

**Bridge naming:** methods are `p_pjt__{suite}_{testname}_0` (prefix `pjt__` avoids user predicate collision; `_N` suffix for repeated test names in same suite).

**Bridge opts detection:** bare expression opts `X==y` (not wrapped in `true(...)`) are now detected in both `has_true_expr` (bridge emitter) and `is_true_expr` (assertz loop). Both must agree or the test runs twice. The assertz emits `pj_inline` atom → `run_one` pj_inline branch fires → self-reporting bridge. `run_succeed` second clause excludes `pj_inline`.


**Resolved bugs (PJ-83e, 32 items):** See SESSIONS_ARCHIVE PJ-84a. All fixed at `2ddc784`.


| Test file | Passed | Failed | Skipped | Notes |
|-----------|--------|--------|---------|-------|
| `test_list` | **1** | 0 | 0 | ✅ |
| `test_arith` | **92** | 111 | 1 | +7 this session (var+float fixed); bignum/format remain |
| `test_unify` | **7** | 4 | 0 | cycle/unifiable unimplemented |
| `test_dcg` | **7** | 17 | 3 | pushback+phrase fixed; =@=, \+, cut remain |
| `test_misc` | 0 | 3 | 0 | not re-run |

```bash
TOKEN=ghp_xxx bash /home/claude/.github/SESSION_BOOTSTRAP.sh
```

**Key files:**
- `one4all/src/frontend/prolog/prolog_emit_jvm.c` — linker ~line 7040 (`pj_linker_emit_bridge`)
- `one4all/test/frontend/prolog/plunit.pl` — shim (keep in sync with C string literal)
- SWI tests: `swipl-devel-master/tests/core/test_*.pl` (58 files)

## Milestone Table

| ID | Trigger | Status |
|----|---------|--------|
| **M-PJ-SCAFFOLD** | `-pl -jvm null.pl → null.j` assembles + exits 0 | ✅ |
| **M-PJ-HELLO** | `write('hello'), nl.` → JVM output `hello` | ✅ |
| **M-PJ-FACTS** | Rung 2: deterministic fact lookup | ✅ |
| **M-PJ-UNIFY** | Rung 3: head unification, compound terms | ✅ |
| **M-PJ-ARITH** | Rung 4: `is/2` arithmetic | ✅ |
| **M-PJ-BENCH-BASELINE** | SWI bench 31/31 PASS | ✅ PJ-84a `a79906e` |

**test_dcg parse errors (fb09892):** Lines 196–208 use DCG rules with conjunction in the head (`a, [_] --> !,{fail}.`) — non-standard SWI extension. Parser does not handle `','` as DCG head. These are in the `context` suite. Skipping for now.
