# GOAL-PROLOG-100-SWI.md — Climb to 100%: ISO core + GNU surface + the in-scope SWI test suite

**Owner track:** PL-100 (extends `GOAL-PROLOG-BB.md` LADDER A/B — this file is the *test-suite reconquest* arm).
**Created:** 2026-07-15 (Claude Sonnet 4.6, session s58 continuation), grounded in a LIVE measurement of the
uploaded `swipl-devel-master` + `gprolog-master` archives, not prose.

---

## ⬅ LIVE CURSOR (2026-07-15, s58c)
**Baseline MEASURED this session (not asserted):** scrip + libscrip_rt build rc=0; Prolog rung suite **138/138 ×3**
(interp≡run≡compile). SWI archive `tests/` = **231 `.pl` files** across 22 dirs; `tests/core/` = **57 files**.
gprolog admits **38 / 312** exports (PL-ISO tracker). `refs/` symlinked from the uploaded zips.

**SWI-1 STEP 1.1 LANDED (Claude Sonnet, s58d continuation) — SCRIP local HEAD `b17431f8` (NOT pushed; no credential).**
Extracted `tests/core/test_unify.pl` (3 blocks, 12 tests → 5 in-scope probes, 7 correctly SKIPed:
cyclic/rational-tree, `unifiable/3` SWI-ext, `garbage_collect`/`trim_stacks` helpers). Harness went
**3 PASS/2 FAIL → 5 PASS/0 FAIL**. The 2 failures were both `can_compare` = a MISSING ISO builtin `?=/2`
(registered as a 700-xfx operator in prolog_parse.c but no runtime impl). Added `rt_pl_can_compare_cell`
(unification.c) = SWI `can_compare` semantics on the cell model (mark trail, `pl_unify`, succeed iff
non-unifiable OR unify-with-zero-new-bindings, always unwind); wired via `rt_pl_det_builtin_target`
(`?=`/2 → `$can_compare`), a `$can_compare` handler in `script_try_call_builtin_by_name`, and the
builtin-name recognizer; lowering auto-routes through the det-target arm. 6-case m3≡m4 direct test green
(incl. `?=(f(X),f(X))`→ok same-var-no-bind, `?=(f(X),f(Y))`→fail would-bind). The 4 remaining ORACLE_MISS
on test_unify are gprolog tool gaps (no `?=/2`, no `f()` arity-0), NOT SCRIP bugs. Full board held (see commit msg).
**NEXT RUNG: SWI-1 step 1.2 `test_term.pl`** — drives PL-ISO-11 `term_variables/2` ⭐ + `subsumes_term/2` ⭐
(both currently MISSING, ISO core, highest-value gap), `?=/2` (now done), `functor/3` edges, numbervars/variant.
⚠ BLOCKED-ON-PUSH: `b17431f8` is a LOCAL commit only — needs a credential to reach origin; not a real close until pushed.

---

## 🎯 THE HONEST TARGET (scope, stated up front so "100%" means something)

"100%" is THREE finite mountains, NOT "every SWI test green" (that would silently promise SWI's own
out-of-scope extensions, which PL-100 explicitly defers). The achievable, worth-chasing 100%:

| Target | Definition | Measured today | Gate |
|---|---|---|---|
| **T1 — ISO Part 1 core** | every ISO-standard builtin + directive | ~70% (PL-ISO tracker) | tracker `UNASSIGNED=0` for ISO rows |
| **T2 — GNU Prolog surface** | gprolog's 312 real exports minus gprolog-only ext (sockets/linedit/debugger) | 38/312 = 12% | tracker DONE == (312 − `scope=gprolog-ext`) |
| **T3 — SWI test suite, IN-SCOPE subset** | `tests/core` + `tests/library` + `tests/db` + `tests/charset` + `tests/rational` files that exercise ISO+shared features | 0 running (plunit ≠ SCRIP) | each extracted probe m3≡m4≡gprolog |

### ⛔ EXPLICITLY OUT OF SCOPE (SWI extensions — a SEPARATE post-PL-100 conversation with Lon)
These SWI `tests/` dirs and `core/` files test features PL-100 defers (modules, tabling, CLP, attributed
vars, dicts, engines, coroutining, delimited continuations, threads, mmap-save, foreign):
`attvar/ clp/ engines/ tabling/ transaction/ thread/ thread_wait/ save/ foreign/ xsb/ unprotected/ GC/`
and core files `test_dict test_qq test_continuation test_coroutining test_tabling test_det_decl
test_attvar test_read_attvar test_varprops test_meta_predicate test_undo test_prolog_listen test_gc
test_lco test_body_index test_moved_ubody test_hash test_fastrw test_signals test_time test_locale
test_env test_qcall test_inflimit test_resource_error test_unicode test_random`.
A SWI-ext test that is trivially reducible to ISO semantics MAY be pulled in opportunistically, but the
*target* does not include them and no rung fails for lacking them.

---

## 📏 THE MEASUREMENT (live, this session — the ground truth every rung builds on)

```
tests/ dir      .pl   in-scope?   notes
core/            57    PARTIAL     ~28 ISO/shared, ~29 SWI-ext (split above)
library/         39    PARTIAL     apply/lists/aggregate/assoc/pairs/... ISO-adjacent; dicts/yall OUT
db/               6    YES         assert/retract/clause semantics
charset/          1    YES         char_type / code_type
rational/         3    MAYBE       rationals are a numeric extension — Lon scope call
GC/               8    NO          garbage collector internals
attvar/           4    NO          attributed variables
clp/              1    NO          constraint logic programming
compile/          1    MAYBE       clause compilation (ISO-adjacent)
debug/            5    NO          SWI debugger
eclipse/          1    NO          ECLiPSe-compat layer
engines/          1    NO          engines
files/            4    MAYBE       file I/O — depends on PL-ISO-7b stream decision
save/             6    NO          qsave_program
signals/          1    NO          signals
tabling/         19    NO          tabling
thread/          30    NO          threads
thread_wait/      3    NO          threads
transaction/      4    NO          transactions
unprotected/     24    NO          low-level VM
xsb/             12    NO          XSB-compat (tabling)
```

SWI tests use **plunit** (`:- begin_tests(Block). test(Name,[Opts]) :- Body. :- end_tests(Block).`).
plunit does not exist in SCRIP or gprolog, so tests cannot run as-is. THE BRIDGE is a mechanical
extractor (SWI-0) that turns each `test(Name,Opts):-Body` into a standalone probe whose expected
outcome is read from `Opts`:
- `test(N) :- G.`               → `G` must succeed (probe prints `ok`)
- `test(N, true) :- G.`         → succeed
- `test(N, fail) :- G.`         → `G` must fail (probe prints `ok` iff `\+ G`)
- `test(N, X == V) :- G.`       → run `G`, then check `X == V`
- `test(N, [error(E,_)]) :- G.` → `catch(G, error(E,_), true)` must succeed
- `test(N, [sto(rational_trees)|_])` → SKIP (cyclic/rational-tree territory, out of scope)
- `test(N, [nondet|_])`, `all(X==L)`, `set(...)` → findall-collect and compare
Each probe is then run in all three modes and against gprolog 1.4.5 as the observable oracle
(SWI's own expected value is the design intent; gprolog is the second witness). MONITOR-FIRST on any
divergence (RULES.md).

---

## 🪜 THE LADDER

Every rung gates on the FULL board (Prolog rung suite ×3 + bench 20/22-or-better + SNOBOL4 smoke 7/7 +
Icon smoke 14/14 + no-new-global floor + emit_no_lang) — no rung lands green-minus. `.s` byte-identity
is NEVER a gate (tracks design churn). PROEBSTING IS CANON; gprolog/SWI are observable oracles only.

### RUNG SWI-0 — THE EXTRACTOR + THE HARNESS ⭐ (prerequisite for every SWI-* rung; no test runs without it)
The single highest-leverage rung — like MON-RE, a working harness is worth more than any one fix because
it makes every subsequent SWI test mechanical.
- [ ] **Step 0.1** — `scripts/swi_extract_tests.py`: parse a `tests/**/*.pl` file's plunit blocks into a
      list of `(block, name, opts, body)` tuples. Handle the `:- begin_tests(B, [Opts]).` head options
      too (whole-block conditions like `[condition(current_prolog_flag(bounded,false))]` → SKIP if the
      flag doesn't hold). Emit ONE `.pl` probe per test into `corpus/programs/prolog/swi/<file>/<name>.pl`
      with the shape `main :- ( <body/checked> -> write(ok) ; write(fail) ), nl.` and a sibling
      `.expected` = `ok\n` (or the SKIP marker `.xfail` with reason).
- [ ] **Step 0.2** — `scripts/test_swi_suite.sh <dir>`: run every extracted probe in m3 + m4 + gprolog,
      diff against `.expected`, print `PASS=n FAIL=n SKIP=n ORACLE_MISS=n` per source file and a total.
      Reuses the rung-suite runner shape; `< /dev/null` on scrip; `timeout 8s` per probe.
- [ ] **Step 0.3** — self-test the extractor on ONE tiny in-scope file end-to-end (`test_unify.pl`,
      3 blocks) so the pipeline is proven before scaling. **GATE:** extractor + runner green on
      `test_unify.pl`; every extracted probe classified (pass/fail/skip) with zero crashes; full board held.

### RUNG SWI-1 — CORE ISO: the finite, close-to-done block
Extract + drive the in-scope `tests/core/` files, easiest-first. Each sub-step: extract, run, triage into
{already-green / one-builtin-gap / genuine-bug}, fix the one-builtin-gaps via the PL-ISO admission recipe
(GOAL-PROLOG-BB.md §"Admission recipe"), MONITOR-FIRST any bug, land, move on.
- [x] **Step 1.1 — `test_unify.pl`** (3 blocks: unify/occurs_check/`?=`). DONE (s58d, local `b17431f8`): 5/0,
      added ISO `?=/2` (`$can_compare`). Occurs-check ties to PL-ISO-11 `acyclic_term`. Established the whole loop.
- [ ] **Step 1.2 — `test_term.pl`** (5 blocks: numbervars/variant/compound/`?=`/functor). Drives
      PL-ISO-11 `term_variables/2` ⭐, `subsumes_term/2` ⭐, `?=/2`, `functor/3` edges. Highest-value ISO gap.
- [ ] **Step 1.3 — `test_arith.pl`** (26 blocks — the big one, but pure `is/2` + comparisons). Mostly
      already covered; will surface float-format + evaluable-function gaps (`gcd`, `truncate`, `msb`,
      `**` vs `^`, `atan2`, bit ops). Each gap = one `pl_arith2` flavor.
- [ ] **Step 1.4 — `test_sort.pl`** (4: sort/2/4, msort, predsort, keysort). Ties PL-ISO-11 `sort/4`.
- [ ] **Step 1.5 — `test_call.pl`** (9: call/N, apply, `\+`, once, forall, catch through call). Exercises
      the PL-ISO-0 bridge + PL-ISO-14 var-goal GEN bug ⭐ head-on — this is where that correctness fix lands.
- [ ] **Step 1.6 — `test_exception.pl`** (2: catch/throw, ISO error terms). Ties PL-ISO-1 + the s56 THIRD
      FINDING (static unknown-pred silent-fail — the single highest-value correctness fix).
- [ ] **Step 1.7 — `test_write.pl`** (8) + **`test_read.pl`** (3) + **`test_op.pl`** (2). Round-trip
      write/read + operators. Ties PL-ISO-8 (op/3, done) + PL-ISO-9 (write_term options).
- [ ] **Step 1.8 — `test_copy_term.pl`** (3) + **`test_syntax.pl`** (2) + **`test_bags.pl`** (findall/bagof/setof).
      Ties PL-ISO-2 (setof/bagof, done) + copy_term attvar-free subset.
- [ ] **Step 1.9 — `test_format.pl`** (1, but dense) + **`test_string.pl`** (2, ISO subset only — SWI
      strings-as-type are OUT; only the `atom`/`codes`/`chars` overlap). Ties PL-ISO-9 format directives.
- [ ] **Step 1.10 — sweep the remaining small in-scope core files**: `test_acyclic test_skip_list
      test_code_type test_occurs_check test_subsumes test_prolog_flag test_list test_misc(ISO subset)`.
      **GATE (SWI-1 done):** every in-scope core probe PASS or documented-SKIP; PL-ISO tracker ISO rows
      UNASSIGNED=0; full board ×3 held; each landed fix has a MONITOR bracket or a reduced reproducer.

### RUNG SWI-2 — LIBRARY: the ISO-adjacent standard library
`tests/library/` (39 files). In-scope: `lists apply aggregate pairs ordsets assoc(subset) nb_set
error(iso term shapes)`. OUT: `yall dicts tabling clpfd record`.
- [ ] **Step 2.1** — extract + triage `tests/library/`; auto-partition in-scope vs OUT by a feature grep
      (any file using `:- use_module(library(dict|clpfd|yall|tabling))` or dict `_{}` syntax → OUT).
- [ ] **Step 2.2** — `lists` (append/member/reverse/nth/last/sum_list/max_list/msort-via/permutation/…):
      most are pure-Prolog library preds SCRIP can just *consult and run* — verify `phrase`/DCG path and
      the list builtins, admit the missing ones as ordinary clauses where SWI ships them in Prolog.
- [ ] **Step 2.3** — `apply` (maplist/2..5, foldl, include/exclude/partition). maplist over a GEN builtin
      is the PL-ISO-14 stress case again (`maplist(between(1,3),L)`).
- [ ] **Step 2.4** — `aggregate` (aggregate_all count/sum/max/min/bag/set) — ties DESIGN §1.10.
      **GATE:** in-scope library probes green ×3; board held.

### RUNG SWI-3 — DB + CHARSET: dynamic database + character classification
- [ ] **Step 3.1** — `tests/db/` (6: assert/retract/clause/abolish/retractall + logical-update view).
      Ties PL-ISO-6 (clause/current_predicate, done) + its TWO documented limitations (consult-time
      `:- assertz` → static proc invisibility; head-arg var-sharing into body). Fixing #1 is the
      prerequisite for `listing/1` (PL-ISO-13) and for these tests to pass honestly.
- [ ] **Step 3.2** — `tests/charset/` (1) + `test_code_type.pl` — `char_type/2`, `code_type/2` full table
      vs gprolog `char_type`. **GATE:** db + charset probes green ×3; the logical-update-view test
      (assert/retract during a running goal over the same pred) passes — MONITOR-FIRST it, it's the
      classic immutable-during-iteration semantics trap.

### RUNG SWI-4 — THE ISO CONFORMANCE STANDARD (the real 100% anchor for T1)
Beyond SWI's own tests: the canonical ISO conformance suite (Prolog ISO/IEC 13211-1 test cases — the
"Deransart/Dagpunar" inmalvo suite, mirrored in gprolog's `src/BipsPl/` self-tests and in the public
`iso_test` corpus). This is what makes T1 measurable independent of any one vendor.
- [ ] **Step 4.1** — locate/vendor the ISO conformance cases (gprolog's own `tests/` in the archive, +
      the standard `inriasuite.pl` if present). Extract to `corpus/programs/prolog/iso/`.
- [ ] **Step 4.2** — run ×3 + gprolog; every ISO-mandated behaviour (error terms, determinism, standard
      order of terms, `read_term`/`write_term` options, arithmetic evaluable functions) green or a filed
      rung. **GATE:** ISO conformance pass-rate MEASURED and tracked in `PROLOG-ISO-TRACKER.md`; T1
      declared at 100% only when this rung is green.

### RUNG SWI-FENCE — the milestone
- [ ] **T1 (ISO core) = 100%** (tracker ISO rows + SWI-4 green) ∧ **T2 (GNU surface) = 100%** (tracker
      DONE == 312 − gprolog-ext, the ext set being Lon's explicit scope call) ∧ **T3 (in-scope SWI tests)
      green ×3** ∧ Prolog rung suite (grown) ×3 ∧ bench ≥ 20/22 ∧ full cross-language board held ∧
      no-new-global floor held ∧ every landed correctness fix carries a MONITOR bracket or reduced
      reproducer. SWI extensions beyond this (modules/tabling/CLP/attvars/dicts/engines) → the separate
      post-PL-100 conversation, NOT part of this fence.

---

## 🔗 DEPENDENCY MAP (why the order is the order)
- SWI-0 blocks everything (no harness → no test runs).
- SWI-1 Step 1.5/1.6 are where the TWO known correctness bugs die (PL-ISO-14 var-goal GEN + s56
  static-unknown-pred silent-fail) — these make every *other* coverage gap LOUD instead of a wrong answer,
  so they pay for themselves across all later rungs.
- SWI-1 Step 1.2 lands `term_variables/2` (PL-ISO-11) — ISO core, blocks nothing, trivially reachable.
- SWI-3 Step 3.1 (consult-time assertz → dyn store) unblocks `listing/1` (PL-ISO-13) and honest db tests.
- SWI-4 is the vendor-independent T1 anchor; do it once the SWI-driven gaps are closed so it measures a
  near-complete surface rather than a sea of red.

## 📌 METHOD NOTES (fold into each rung; do NOT re-derive)
- **Extraction is mechanical, triage is the work.** Most core-ISO probes will already be green — the value
  is the SORTED list of what's NOT, each of which is one admission-recipe application or one MONITOR hunt.
- **gprolog is the second witness, not the authority.** Where SWI's expected value and gprolog disagree on
  an ISO-underspecified point, record BOTH and ask Lon; do not silently pick one.
- **SWI-ext creep is the failure mode.** The moment a "core" test needs dicts/attvars/tabling to pass, it's
  OUT — mark `.xfail scope=swi-ext`, don't chase it into the weeds.
- **Every fix touches the runtime or LOWER, never a template's language identity** (FACT RULE: language-blind
  templates). New builtins → `rt_pl_*_cell` + by-name dispatch + LOWER arm, per the recipe.
