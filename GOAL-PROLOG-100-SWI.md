# GOAL-PROLOG-100-SWI.md — Climb to 100%: ISO core + GNU surface + the in-scope SWI test suite

**Owner track:** PL-100 (extends `GOAL-PROLOG-BB.md` LADDER A/B — this file is the *test-suite reconquest* arm).
**Created:** 2026-07-15 (Claude Sonnet 4.6, session s58 continuation), grounded in a LIVE measurement of the
uploaded `swipl-devel-master` + `gprolog-master` archives, not prose.

---

## ⬅ LIVE CURSOR (2026-07-19, Claude Opus 4.8 — coverage session, parallel to the perf session)
**IN FLIGHT (NOT committed — no credential yet):** SWI-1 Step 1.2 `test_term.pl` gaps, on top of s58d's
`b17431f8`. `term_variables/2` + `/3` LANDED and oracle-exact in mode-3 (dedup on deref'd cell identity;
`/3` tail; variable IDENTITY preserved — binding a list element mutates the source term). Two bugs found+fixed
en route (bracketed, not guessed): (1) dedup on reconstructed `Term*` failed because `pl_cell_to_term` mints a
fresh `Term` per var occurrence → rewrote the walk to be CELL-NATIVE (dedup on `pl_deref` cell address);
(2) SIGSEGV in `VARVAL_fn` core.c:1843 (gdb-bracketed) because the `[]` terminator was built with `pl_make_atom`
= tag `DT_A` which in this DESCR system means SNOBOL4 ARRAY, not Prolog atom — Prolog atoms travel as `DT_S`
string cells (per `pl_term_to_cell_word_m`); fixed the nil. `subsumes_term/2`: WIRED, truth table 5/6 — s2
`subsumes_term(f(a,b),f(X,Y))` returns yes, should be NO (ground general must not subsume var-specific);
bound-of-specific detection needs an empirical debug (NEXT). LIGHT ADMISSION PATH used (no new IR opcode/
template — 4 edits: `rt_pl_term_variables_cell`+`rt_pl_subsumes_cell` in unification.c, name recognizer +
handlers + det-target table in by_name_dispatch.c; lowering auto-routes via `rt_pl_det_builtin_target`).
**NEXT:** (1) debug subsumes s2 empirically; (2) verify BOTH builtins in mode-4 (`--compile`); (3) full board
×3 + smokes + no-new-global floor; (4) regen PROLOG-ISO-TRACKER.md (DONE 38→40); (5) continue test_term.pl
(functor edges, numbervars/variant). refs/ symlinked from uploaded gprolog/swipl zips; oracles gprolog 1.4.5 +
swipl 9.0.4 via apt (needed `apt-get update` first — stale index 404s).

**⬆ SCOPE WIDENED THIS SESSION (Lon 2026-07-19): LADDER C — PL-DIALECT added below** (GNU ∪ SWI superset with
a `--pl-dialect` flavor switch; divergence table MEASURED against both oracles). PL-DIA-0 (flag store) is the
prerequisite AND resolves the parked streams/flags mutable-state question. Highest-value early rungs:
PL-DIA-1 (double_quotes) + PL-DIA-2 (strings). This is now the strategic spine of the coverage track.

---

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

**⬆ SCOPE WIDENED (Lon directive, 2026-07-19): SCRIP is to be a FASTER, FULLY-COMPATIBLE alternative to
BOTH GNU Prolog AND SWI-Prolog — a SUPERSET of both where they coincide, with a DIALECT FLAVOR SWITCH
where they diverge.** The former "SWI extensions are a separate post-PL-100 conversation" deferral is
LIFTED: modules, tabling, CLP, attributed vars, dicts, coroutining, the SWI string type, and unbounded
integers are now IN SCOPE, gated behind the dialect switch (LADDER C — PL-DIALECT). "100%" is now FOUR
mountains:

| Target | Definition | Measured 2026-07-19 | Gate |
|---|---|---|---|
| **T1 — ISO Part 1 core** | every ISO-standard builtin + directive | ~70% (PL-ISO tracker) | tracker `UNASSIGNED=0` for ISO rows |
| **T2 — GNU Prolog surface** | gprolog's 312 real exports minus gprolog-only ext (sockets/linedit/debugger) | 40/312 (term_variables+subsumes s99+1) | tracker DONE == (312 − `scope=gprolog-ext`) under `--pl-dialect=gnu` == gprolog 1.4.5 |
| **T3 — SWI test suite, IN-SCOPE subset** | `tests/core`+`library`+`db`+`charset`+`rational` exercising ISO+shared | 0 running (plunit ≠ SCRIP) | each extracted probe m3≡m4≡ its oracle |
| **T4 — SWI surface + extensions** ⬅ NEW | SWI string type, bignums, modules, tabling, dicts, attvars, CLP, coroutining | ~0% (LADDER C) | under `--pl-dialect=swi` == swipl 9.0.4 on the in-scope surface |

**THE SUPERSET PRINCIPLE:** most of ISO is shared verbatim; the GNU↔SWI divergences are a BOUNDED,
ENUMERABLE set (measured 2026-07-19 against both installed oracles — see LADDER C's divergence table).
The default dialect (`--pl-dialect=superset`, or the flag `dialect=superset`) ACCEPTS the union and prefers
the more capable behavior; `gnu`/`swi`/`iso` narrow it to bit-exact parity with that oracle. Every
divergence is resolved at PARSE or LOWER time into the shared AST — the flag store (PL-ISO-12 / PL-DIA-0)
is the single mechanism, and NOTHING dialect-related reaches the emitter (FACT RULE: language-blind
templates holds — a dialect is a parser/lower parameter, exactly like the `.pl` first-dispatch string).

### DIALECT-GATED (was "out of scope"; now LADDER C rungs, flavor-switched)
These SWI features are IMPLEMENTED under `swi`/`superset` and correctly ABSENT under `gnu`/`iso`:
modules, tabling, CLP(FD), attributed vars, dicts, coroutining (`freeze`/`dif`/`when`), delimited
continuations, the string type, unbounded integers, rationals. STILL out of scope (host-VM internals, not
language semantics — a later conversation): `thread/ thread_wait/ save/ foreign/ GC/ unprotected/ signals/`
and their core files (`test_gc test_signals test_time test_locale test_env test_resource_error`). A test
needing threads/foreign/save is `.xfail scope=host-vm`; everything else has a LADDER C home.


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

## 🪜 LADDER C — PL-DIALECT: GNU ∪ SWI as a superset, flavor-switched where they diverge (Lon 2026-07-19)

**MEASURED DIVERGENCE TABLE (2026-07-19, both oracles installed via apt — gprolog 1.4.5, swipl 9.0.4):**

| axis | `--pl-dialect=gnu` (== gprolog) | `--pl-dialect=swi` (== swipl) | resolved at | rung |
|---|---|---|---|---|
| `double_quotes` default | `codes` → `[97,98,99]` | `string` → string obj | PARSE | PL-DIA-1 |
| `bounded` / integers | `true`, 64-bit wrap | `false`, unbounded bignum | LOWER+arith | PL-DIA-3 |
| string as a type | absent (`existence_error string/1`) | present | PARSE+runtime | PL-DIA-2 |
| `unknown` | `error` | `error` (COINCIDE — no switch) | — | PL-DIA-9 |
| `occurs_check` | unset (`false`) | `false` | flag | PL-DIA-9 |
| rationals (`1r3`) | absent | present | PARSE+arith | PL-DIA-4 |
| modules (`M:G`, `:- module`) | minimal | full | PARSE+LOWER | PL-DIA-5 |
| tabling (`:- table`) | absent | SLG | LOWER+engine | PL-DIA-6 |
| dicts (`_{k:v}`) | absent | present | PARSE+runtime | PL-DIA-7 |
| attvars (`freeze/dif/when`) | absent | present | runtime | PL-DIA-8 |

**Design premise (why this fits the architecture, not fights it):** a Prolog *dialect* is a sub-parameter
of the Prolog frontend, consumed ONLY in `src/parser/prolog/` and `src/lower/lower_prolog.c`, resolved into
the shared AST/IR before the emitter ever runs. This is identical in kind to the `.pl` first-dispatch
string and the double_quotes flag — the FACT RULE (no language identity past LOWER) is UNVIOLATED because
the dialect never reaches emitter/templates. The flag store (PL-DIA-0) is the ONE mechanism; setting the
dialect sets a bundle of flags; individual `set_prolog_flag/2` calls override within a dialect.

Each rung's shape: (a) implement BOTH behaviors, (b) flag-gate the selection, (c) DUAL-ORACLE verify —
gnu-behavior == gprolog AND swi-behavior == swipl, m3≡m4 for each. Superset dialect = accept the union.

- [ ] **PL-DIA-0 — FLAG STORE + DIALECT SELECTOR ⭐ (prerequisite for the whole ladder; also closes the
      parked PL-ISO-7b/12 "mutable state" design question — this IS the sanctioned per-process store).**
      Implement `current_prolog_flag/2` + `set_prolog_flag/2` (PL-ISO-12 core rows) over a real flag table;
      add `--pl-dialect=gnu|swi|iso|superset` CLI (default `superset`) + `:- set_prolog_flag(dialect, D)`;
      a dialect sets a FLAG BUNDLE (double_quotes, bounded, string-type-on, unknown, occurs_check, …). The
      table is the sanctioned mutable global (Lon sign-off REQUESTED IN WRITING here per the no-new-global
      floor — this rung is where that decision lands). MODE34: mode-4 binaries bake the active flag bundle
      at startup (same shape as the op/3 bake, scrip.c). **Completion: flag round-trip ×3; each dialect's
      default bundle == that oracle's `current_prolog_flag` for {double_quotes,bounded,unknown}; rung55_flags ×3.**
- [ ] **PL-DIA-1 — double_quotes (THE most visible divergence, highest test-unblock value).** Parser
      consults `double_quotes` ∈ {codes, chars, atom, string}; rewrite quoted-string literals at read time.
      gnu/iso default codes, swi default string. `back_quotes` (swi codes) too. **Completion: `"abc"` under
      each flag value == the respective oracle; rung56_dquotes ×3; unblocks every SWI test using `"..."`.**
- [ ] **PL-DIA-2 — SWI STRING TYPE.** First-class string (model on DT_S with a distinct string-vs-atom
      marker so `string/1` ≠ `atom/1`); `string_concat/3 string_chars/2 string_codes/2 string_to_atom/2
      atom_string/2 number_string/2 sub_string/5 split_string/4 string_length/2 text_concat/3 term_string/2
      read_string/5 string_code/3`. Present under swi/superset; under gnu these `existence_error` exactly as
      gprolog. Ties the many `$aop_*` string ops already half-present in by_name_dispatch.c. **Completion:
      SWI `tests/core/test_string.pl` in-scope probes == swipl; gnu dialect errors match gprolog; rung57_string ×3.**
- [ ] **PL-DIA-3 — UNBOUNDED INTEGERS (bignums).** Arithmetic engine grows an arbitrary-precision integer
      path (GMP is already a build dep — `libgmp-dev` in install_system_packages.sh); flag `bounded` selects
      64-bit-wrap (gnu) vs bignum (swi/superset); `max_integer`/`min_integer` flags present only when bounded.
      Touches `arithmetic.c` + the DESCR int representation (a tagged bignum-pointer flavor). **Completion:
      `X is 2^100` = exact 1267650600228229401496703205376 under swi/superset == swipl; gnu matches gprolog's
      bounded result; the van Roy bignum-sensitive rows unaffected; rung58_bignum ×3.**
- [ ] **PL-DIA-4 — RATIONALS + EXTENDED FLOAT.** `1r3` syntax + rational arith (`rational/1 rationalize/1
      numerator/denominator`); `nan`/`inf`, `float_overflow`/`float_zero_div`/`float_undefined` flags. swi/
      superset only. **Completion: SWI `tests/rational/` in-scope == swipl; rung59_rational ×3.**
- [ ] **PL-DIA-5 — MODULE SYSTEM (sub-ladder).** `:- module/2`, `use_module/1,2`, `M:Goal` qualification,
      `library(...)` autoload, `:- use_module(library(L))`. Parse-time qualification + a module-aware proc
      table (predicate key gains a module component; unqualified calls resolve in the current module then
      user/system). gnu = its minimal system, iso = none (bare), swi = full. LARGE — expect PL-DIA-5a
      (parse+qualify), 5b (proc-table keying), 5c (autoload of the shipped libraries), 5d (meta_predicate
      module transparency). **Completion: `tests/core` module probes == swipl under swi; qualified calls
      resolve ×3; rung60_modules ×N.**
- [ ] **PL-DIA-6 — TABLING (sub-ladder).** `:- table p/n`, SLG resolution (memo table + answer subsumption +
      completion detection); the classic left-recursion-terminates + path/2 transitive-closure cases. swi/
      superset only. LARGE — 6a (directive + call-shape recognition), 6b (answer/subgoal tables + variant
      check), 6c (fixpoint/completion), 6d (well-founded negation, if pursued). **Completion: SWI
      `tests/tabling/` in-scope core cases == swipl under swi; rung61_tabling ×N.**
- [ ] **PL-DIA-7 — DICTS.** `_{k:v}` read syntax, `Dict.Key` functional notation, `get_dict/3 put_dict/4
      dict_pairs/3 dict_create/3`. Parser + a dict runtime term. swi/superset only. **Completion:
      `tests/core/test_dict.pl` in-scope == swipl; rung62_dict ×3.**
- [ ] **PL-DIA-8 — ATTRIBUTED VARS + COROUTINING.** `put_attr/3 get_attr/3 del_attr/2`, attr_unify_hook
      protocol, `freeze/2 dif/2 when/2`; the CLP(FD) foundation. swi/superset only. Touches the trail/bind
      core (attr vars fire hooks on binding). LARGE — 8a (attr storage on var cells + hook dispatch on bind),
      8b (freeze/dif/when over it), 8c (CLP(FD) `#= #< in ins label`). **Completion: `tests/attvar/` in-scope
      + `tests/clp/` basic == swipl under swi; rung63_attvar ×N.**
- [ ] **PL-DIA-9 — FLAG + DIRECTIVE PARITY SWEEP.** Full flag set both dialects ({unknown occurs_check
      char_conversion double_quotes back_quotes bounded max_integer min_integer dialect gc last_call_optimisation
      …}) with each dialect's defaults verified vs its oracle; directives `:- dynamic/discontiguous/multifile/
      initialization(_,_)/ensure_loaded/set_prolog_flag` parity. **Completion: rung64_flags_dir ×3 == both oracles
      per dialect; no-new-global floor held or the flag store sanctioned (PL-DIA-0).**
- [ ] **PL-DIA-10 — LIBRARY PARITY (lists/apply/aggregate/assoc/pairs/ordsets/…).** Ship the shared library
      preds (mostly pure Prolog — consult-and-run); flavor-gate where GNU and SWI differ in a pred's presence
      or behavior. Overlaps SWI-2; the dialect switch decides which library surface is visible. **Completion:
      in-scope `tests/library/` probes green ×3 under BOTH dialects against their oracle.**
- [ ] **PL-DIA-11 — I/O + FORMAT + READ/WRITE DIVERGENCES.** format directive UNION (`~p ~q ~e ~f ~g ~r ~c
      ~s ~t ~| ~+ ~d ~D ~* ~a ~w`), write_term option UNION (quoted ignore_ops numbervars max_depth portray
      spacing fullstop), read_term option union, stream aliases. Depends on PL-ISO-7b (streams) + PL-DIA-0
      (flags). Flavor-gate where they differ. **Completion: `test_write test_read test_format` in-scope ==
      both oracles per dialect ×3.**
- [ ] **PL-DIA-12 — EXCEPTION / ERROR-TERM PARITY.** ISO error terms are shared; SWI adds a context arg.
      Ensure each dialect's thrown error terms match its oracle exactly (gnu: `error(E, Context)` gprolog
      shape; swi: `error(E, SwiContext)`). Ties the s56 static-unknown-pred silent-fail fix. **Completion:
      error-term probes == both oracles per dialect ×3.**
- [ ] **PL-DIA-FENCE — the dual-compatibility milestone.** Curated dual conformance corpus:
      `--pl-dialect=gnu` run == gprolog on the full GNU surface (T2) ∧ `--pl-dialect=swi` run == swipl on the
      in-scope SWI surface (T4) ∧ `superset` accepts the union ∧ every divergence flag-documented in the table
      above ∧ per-iteration performance ≤ BOTH oracles on the shared benchmark set (this is the hand-off seam
      to the PERFORMANCE session — LADDER B / the RSP-FINISH work). SWI host-VM internals
      (threads/foreign/save/GC) remain the only deferred set.

**LADDER C DEPENDENCY NOTES:** PL-DIA-0 (flags) blocks the whole ladder — do it FIRST, and it doubles as the
PL-ISO-12 flag rows + the answer to the streams/flags mutable-state question. PL-DIA-1 (double_quotes) and
PL-DIA-2 (strings) are the highest test-unblock value (the most SWI tests fail purely on `"..."` meaning a
string) — do them right after PL-DIA-0. PL-DIA-5/6/8 (modules/tabling/attvars) are the LARGE sub-ladders and
come after the syntax-level divergences are closed, so they land against a near-complete shared surface.


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
