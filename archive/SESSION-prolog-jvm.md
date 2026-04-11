# SESSION-prolog-jvm.md — Prolog × JVM (one4all)

**Repo:** one4all · **Frontend:** Prolog · **Backend:** JVM (Jasmin)
**Session prefix:** `PJ` · **Trigger:** "playing with Prolog JVM"
**Driver:** `scrip-cc -pl -jvm foo.pl -o foo.j` → `java -jar jasmin.jar foo.j -d .` → `java FooClass`
**Oracle:** `scrip-cc -pl -asm foo.pl` (ASM emitter)
**Deep reference:** all ARCH docs cataloged in `PLAN.md`

## Subsystems

| Subsystem | Doc | Go there when |
|-----------|-----|---------------|
| Prolog language, IR nodes | `PARSER-PROLOG.md` | parser/AST questions |
| Full milestone history | `ARCHIVE-PROLOG-JVM-HISTORY.md` | completed work, milestone IDs |
| JVM Prolog runtime design | `INTERP-JVM.md` | term encoding, trail, clause dispatch |

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

**RESOLVED (2ddc784 / PJ-83e):**
1. ~~Multi-suite test files~~: FIXED — prescan.
2. ~~Variable sharing in `true(Expr)` / bare-expr tests~~: FIXED — `pj_inline` bridge path.
3. ~~`forall` duplicate method~~: FIXED.
4. ~~Bridge name collision~~: FIXED — `pjt__` prefix.
5. ~~Unary `+` parse error~~: FIXED.
6. ~~DCG pushback notation~~: FIXED.
7. ~~`phrase([], List)` → undefined~~: FIXED.
8. ~~Spaced numeric literals~~: FIXED.
9. ~~`memberchk` variable sharing~~: FIXED.
10. ~~Stack VerifyError~~: FIXED.
11. ~~`garbage_collect/0`, `trim_stacks/0`~~: FIXED.
12. ~~`?=/2` (can_compare)~~: FIXED.
13. ~~Mixed int/float arithmetic~~: FIXED — float-aware ops.
14. ~~**Float unification missing**~~: FIXED — `pj_unify` now has float-float case (numeric `dcmpl`).
15. ~~`ceil/1` alias~~: FIXED — `ceil` recognized alongside `ceiling`.
16. ~~`integer/1` semantics~~: FIXED — rounds to nearest (was truncating).
17. ~~`float_fractional_part(int)` → float~~: FIXED — returns integer `0`.
18. ~~`sign/1` normalizes `-0.0`~~: FIXED — `+0.0` normalize.
19. ~~`copysign/2` result type~~: FIXED — follows magnitude arg.
20. ~~`float/1` double-conversion~~: FIXED — pass-through for float arg.
21. ~~`=:=` with runtime float variable~~: FIXED — `pj_num_cmp` + `pj_arith_has_var`.
22. ~~`min`/`max` mixed int+float result type~~: FIXED — `pj_min_mixed`/`pj_max_mixed`.
23. ~~`Long.MIN_VALUE` literal parsing~~: FIXED — `strtoull` cast in lexer.
24. ~~Hyperbolic functions missing~~: FIXED — `sinh/cosh/tanh/asin/acos/asinh/acosh/atanh`.
25. ~~`mod/2` truncating instead of floor~~: FIXED — `pj_mod` helper.
26. ~~`pj_num_cmp` uses `Double.compare` (breaks -0.0==0.0)~~: FIXED — `dcmpl`.
27. ~~`>>`/`<<` wrap on large counts~~: FIXED — `pj_shr`/`pj_shl` saturating.
28. ~~`nan`/`inf`/`infinity` constants~~: FIXED — recognized in arith emit.
29. ~~`between/3` deterministic check (bound 3rd arg)~~: FIXED — fast path bypasses iteration.
30. ~~**var+float binary arith**~~: FIXED — `pj_varnum_*` + `pj_obj_to_bits/is_float/to_double` + generalized `pj_emit_arith_as_double`.
31. ~~**succ/2 slot collision**~~: FIXED — `.limit locals 6`, `astore 4` for domain_error Object (avoids clobber of long in slots 2-3). Passes in isolation; large-file failure = item 8.
32. ~~**InvocationTargetException unwrap**~~: FIXED — `pj_reflect_call` now unwraps before PROLOG_THROW check.

**Remaining known limitations (NEXT ACTIONS):**
1. **`=@=` structural equivalence**: not implemented — skip tests using it.
2. **`unifiable/3`**: not implemented.
3. **`cut_to`**: cut across catch boundary — not implemented.
4. **`\+` swallowing exceptions**: `not1_a/b`, `not2_a/b` in `test_dcg`.
5. **`cut1_b`, `curlycut_b`** in `test_dcg`.
6. **`succ/2` domain_error**: throws wrong term (local slot conflict in throw construction) — WIP commit `ef4c596`. Fix: increase `.limit locals` in `pj_succ_2` to 6, use local slot 4 instead of 2 for the domain_error Object term. The `astore_2` in the neg path clobbers the long in slots 2-3.
7. ~~**var+float binary op**~~: FIXED — `pj_varnum_{add,sub,mul,div}` Object[]-level helpers; `pj_emit_arith_as_double` generalized to `pj_arith_has_var`; `round/1`/`integer/1` use `pj_emit_arith_as_double` when child has var. +7 tests (all hyperbolic + a_add_fc_float).
8. **`test_arith` `between_1`/`plus_1`** fail in large-file context but pass in isolation — likely label collision or method table size issue in Jasmin for very large classes.
9. **`format/3` with atom output** `format(atom(A), Fmt, Args)` not implemented — blocks `minint`/`maxint` suites (16 tests).
10. **bignum**: `bigint`/`minint_promotion`/`maxint_promotion` require arbitrary precision — out of scope for JVM long.
11. **`test_dcg` context suite**: `generalcontext`/`vd`/`forprogrammers` still failing.
12. **`test_misc`**: not re-run — `cut_to`, `read_only_flag` still expected to fail.

**SWI baseline pass/fail (tests/core/) — as of ef4c596:**

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
