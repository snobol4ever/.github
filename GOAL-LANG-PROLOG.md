# GOAL-LANG-PROLOG.md — Prolog Frontend Ladder

**Repo:** one4all
**Done when:** SWI-Prolog conformance suite and GNU Prolog test suite pass
under all three modes (--ir-run, --sm-run, --jit-run). Dynamic predicates,
exceptions, DCG, and arithmetic extensions complete.

**Cross-pollination:** pl_runtime.c fixes (trail, unify, pred table) benefit
interp.c's E_CHOICE/E_CLAUSE/E_UNIFY handling shared with all frontends.
BB broker improvements (BB_ONCE, pl_box_choice) benefit SNOBOL4 alternation.
Share fixes via main — no branches.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
bash /home/claude/one4all/scripts/install_swi_prolog_tests.sh      # see IC-SETUP below
bash /home/claude/one4all/scripts/install_gnu_prolog_tests.sh       # see IC-SETUP below
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_prolog.sh             # PASS=5
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh     # PASS=31
bash /home/claude/one4all/scripts/test_crosscheck_prolog.sh       # 3-mode divergence check
```

---

## Test suite install scripts (write these at PL-1)

### install_swi_prolog_tests.sh
Fetches the SWI-Prolog ISO conformance tests from:
  https://github.com/SWI-Prolog/swipl-devel/tree/master/src/Tests/core
Target dir: `/home/claude/corpus/programs/prolog/swi_tests/`
Tests to include: `arithmetic.pl`, `atom.pl`, `control.pl`, `findall.pl`,
`list.pl`, `meta.pl`, `strings.pl`, `terms.pl`, `exceptions.pl`.
Oracle: run each test under SWI-Prolog (`swipl`) if installed, else use
pre-baked `.ref` files in the corpus.

### install_gnu_prolog_tests.sh
Fetches the GNU Prolog test suite from:
  https://github.com/didoudiaz/gprolog/tree/master/src/TestsPl
Target dir: `/home/claude/corpus/programs/prolog/gnu_tests/`
Tests: `t_arith.pl`, `t_atom.pl`, `t_control.pl`, `t_dcg.pl`, `t_list.pl`.

Both scripts are idempotent. If corpus already present, skip clone. Print SKIP.

---

## Architecture reminder

```
.pl → prolog_compile() → Program* [LANG_PL]
    --ir-run  → execute_program() → interp_eval() E_CHOICE/E_CLAUSE/E_UNIFY
    --sm-run  → sm_lower() → SM_BB_ONCE per stmt → bb_broker(BB_ONCE)
    --jit-run → sm_lower() → SM_BB_ONCE → sm_codegen() → sm_jit_run()

Backtracking: BB_ONCE mode — pl_box_choice is the OR-box.
Trail: g_pl_trail (global in pl_runtime.c).
Pred table: g_pl_pred_table (global in pl_runtime.c).
```

---

## Rung ladder — all modes, x86

Current baseline: rung01–11 14/14 PASS --ir-run.
rung12 and beyond are the ladder for this goal.

### Phase 1 — IR-run builtin ladder (rung 12–30)

- [x] **PL-1** — rung01–11: 14/14 PASS --ir-run. (done)

- [x] **PL-2** — Install SWI + GNU test suites.
  Write `scripts/install_swi_prolog_tests.sh` and
  `scripts/install_gnu_prolog_tests.sh`. Run both.
  Gate: test files present in corpus.

- [x] **PL-3** — S-10e: `assertz/asserta/retract/abolish`.
  Dynamic pred table mutation in `interp_exec_pl_goal`.
  Gate: rung13 5/5, rung14 5/5, rung15 5/5.

- [x] **PL-4** — S-10f: atom builtins.
  `atom_length/2`, `atom_chars/2`, `atom_codes/2`, `atom_concat/3`.
  Gate: rung12 5/5.

- [x] **PL-5** — S-10g/h: term ordering + sort.
  `@</2`, `@>/2`, `@=</2`, `@>=/2`, `sort/2`, `msort/2`.
  Gate: rung16 5/5, rung17 5/5.

- [x] **PL-6** — S-10i/j: `succ/2`, `plus/3`, `format/2`.
  Gate: rung18 5/5, rung19 5/5.

- [x] **PL-7** — S-10k/l: `numbervars/3`, `char_type/2`.
  Gate: rung20 5/5, rung21 5/5.

- [x] **PL-8** — S-10m/n: write variants, bitwise arith ext.
  `write_canonical/1`, `writeq/1`, bitwise ops, `max/min`, `**`, `sign`.
  Gate: rung22 5/5, rung23 5/5.

- [x] **PL-9** — S-10o/p: string/IO builtins, `term_string/2`.
  Gate: rung24 5/5, rung25 5/5.

- [x] **PL-10** — S-10q/r/s: `copy_term/2`, `nb_setval/nb_getval`,
  `throw/1`, `catch/3`.
  Gate: rung26 5/5, rung27 5/5, rung28 5/5.

- [x] **PL-11** — S-10t/u: float ops, DCG `-->` expansion, `phrase/2,3`.
  Gate: rung29 5/5, rung30 5/5.

- [ ] **PL-12** — SWI conformance suite run.
  Script: `scripts/test_prolog_swi_suite.sh`.
  Run each SWI test file under --ir-run. Compare to pre-baked .ref.
  Gate: PASS ≥ 80% of tests in suite.

- [ ] **PL-13** — GNU Prolog suite run.
  Script: `scripts/test_prolog_gnu_suite.sh`.
  Gate: PASS ≥ 80% of tests in t_arith + t_atom + t_control + t_list.

### Phase 2 — SM-run (BB_ONCE via Byrd boxes, x86)

- [ ] **PL-14** — rung01–11 under --sm-run.
  Each stmt routes via SM_BB_ONCE → icn_eval_gen (PL path) → bb_broker(BB_ONCE).
  Gate: 14/14 PASS.

- [ ] **PL-15** — rung12–20 under --sm-run.
  Fix sm_lower.c gaps for Prolog EKinds as needed.
  Gate: all rungs passing under --ir-run also pass under --sm-run.

- [ ] **PL-16** — SWI + GNU suites under --sm-run.
  Gate: PASS count matches --ir-run baseline.

### Phase 3 — JIT-run (x86 in-memory code gen)

- [ ] **PL-17** — rung01–11 under --jit-run.
  Gate: 14/14 PASS.

- [ ] **PL-18** — rung12–20 under --jit-run.
  Gate: all diffs vs --sm-run empty.

- [ ] **PL-19** — SWI + GNU suites under --jit-run.
  Gate: PASS count matches --sm-run baseline.

---

## Prolog test runner script template

```bash
# scripts/test_prolog_rung_NN.sh — template
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIP="${HERE}/../scrip"
CORPUS=/home/claude/corpus/programs/prolog
PASS=0; FAIL=0
for f in "$CORPUS/rungNN"/*.pl; do
    ref="${f%.pl}.ref"
    [ -f "$ref" ] || continue
    actual=$(timeout 8 "$SCRIP" --ir-run "$f" < /dev/null 2>/dev/null)
    expected=$(cat "$ref")
    if [ "$actual" = "$expected" ]; then
        echo "  PASS $(basename $f)"; PASS=$((PASS+1))
    else
        echo "  FAIL $(basename $f)"; FAIL=$((FAIL+1))
    fi
done
echo "PASS=$PASS FAIL=$FAIL"; [ "$FAIL" -eq 0 ]
```

---

## Key files

| File | Role |
|------|------|
| `src/frontend/prolog/prolog_lower.c` | Frontend → IR |
| `src/frontend/prolog/prolog_builtin.c` | Builtin dispatch |
| `src/frontend/prolog/prolog_atom.c` | Atom table |
| `src/frontend/prolog/prolog_unify.c` | Unification + trail |
| `src/runtime/interp/pl_runtime.c` | g_pl_pred_table, g_pl_trail, pl_box_choice |
| `src/driver/interp.c` | E_CHOICE/E_CLAUSE/E_UNIFY in interp_eval |
| `corpus/programs/prolog/` | Prolog corpus + rung tests |

---

## Invariants

- Gate = PASS=31 FAIL=0 on test_smoke_unified_broker.sh after every commit.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

---

## Current state (2026-04-15, one4all HEAD ea80bd8d, corpus HEAD e587489)

PL-1 through PL-11 fully done. PL-12 IN PROGRESS.

PL-12 work done this session:
- build_scrip.sh: SKIP-if-exists guard removed (always runs make). DONE.
- pl_runtime.c: directive no-ops added (dynamic, module, use_module, include,
  discontiguous, style_check, if/endif, etc.) so SWI test directives don't
  crash. DONE.
- pl_runtime.c: user-call dispatch added at top of E_FNC in
  interp_exec_pl_builtin — routes user predicates via interp_eval before
  builtin fallthrough. Expanded is_pl_user_call builtins list. DONE.
- test_prolog_swi_suite.sh: corpus-repo path fixed to corpus; loop uses
  test_*_main.pl wrappers; passes plunit.pl+testfile+main to scrip. DONE.
- corpus/plunit.pl: fully rewritten (136 lines). Multi-clause cut-based
  dispatch; findall-based test collection (no fail-loop); pj_run_* naming.
  DONE but BLOCKER remains (see below).

BLOCKER: -> (if-then) operator fails silently inside single-clause user
predicates when called cross-file via interp_eval/BB_ONCE.
  Symptom: ( SF =:= 0 -> format('PASS ~w~n',[Suite]) ; format('FAIL ...') )
  inside pj_suite_verdict produces NO output at all.
  Root cause hypothesis: interp_exec_pl_builtin is called with wrong env
  pointer when dispatching -> from inside a clause body executed by
  bb_broker. The -> cond check calls interp_exec_pl_builtin(cond, env)
  where env is the clause arg array — but =:=/2 or format/2 may be
  mis-evaluating the args.
  Minimal repro: foo :- nb_setval(x,0), nb_getval(x,V),
                        ( V =:= 0 -> writeln(ok) ; writeln(fail) ).
                 main :- foo.
  Test this in isolation first.

NEXT SESSION PL-12:
  1. Run minimal repro above to confirm -> bug.
  2. In interp_exec_pl_builtin, trace the ; -> branch:
     left->children[0] is V =:= 0, left->children[1] is writeln(ok).
     Check that pl_unified_term_from_expr(V, env) resolves V correctly
     when env is the clause's arg array vs NULL.
  3. Fix: likely need to thread g_pl_env (global) through instead of
     local env param, or unify env with g_pl_env before calling.
  4. Once -> fixed: run test_prolog_swi_suite.sh, gate >= 80%.

---

## --monitor: in-process sync comparator (IM-7/IM-8 complete)

`--monitor` runs IR, SM, and JIT step-by-step over the same program,
snapshot/restoring all mutable state between runs, and reports the first
statement where any two executors diverge.

```bash
./scrip --monitor file.sno    # SNOBOL4
./scrip --monitor file.icn    # Icon
./scrip --monitor file.pl     # Prolog
./scrip --monitor file.raku   # Raku
./scrip --monitor file.snc    # Snocone
./scrip --monitor file.reb    # Rebus
```

**On agreement:** prints per-stmt progress, exits 0.
**On divergence:** exits 1 and prints:
```
DIVERGE at stmt N [label: LABEL, line LL]
  IR   last_ok=?
  SM   last_ok=1
  JIT  last_ok=1
  IR vs SM (N var(s) differ):
    VARNAME    IR=<value>    SM=<value>
```

**Workflow for finding bugs:**
1. Run `./scrip --monitor suspect.sno` to find the first diverging statement.
2. The statement number + variable name pinpoint the root cause.
3. Fix in the appropriate layer (interp.c for IR bugs, sm_interp.c or
   sm_codegen.c for SM/JIT bugs).
4. Re-run `--monitor` to confirm divergence is gone.
5. Run `test_smoke_unified_broker.sh` — must stay PASS=31 FAIL=0.

**Note:** `--monitor` is incompatible with `--ir-run`/`--sm-run`/`--jit-run`
(it drives all three internally). ICN frame locals (IM-10) and Prolog trail
variables (IM-11) are not yet in the snapshot — coming in future IM steps.


---

## Current state (2026-04-16, one4all HEAD 372f5309)

PL-1 through PL-11 fully done. PL-12 IN PROGRESS — 71% coverage.

Session 2026-04-16 work:
- Makefile: removed stale engine.c reference (deleted SN-6, Makefile not updated;
  broke build at session start). DONE.
- corpus repo cloned (/home/claude/corpus).
- Diagnosed ->  blocker from previous session: already resolved in current build.
- Diagnosed 0% SWI suite coverage: root cause was cut scoping bug (see below).
- pl_broker.c: rewrote cut scoping — per-OR-box cut field + g_pl_cur_cut_flag ptr.
  Before: g_pl_cut_flag was global; ! inside pj_run_one/4 leaked to parent
  pj_run_tests/2 OR-box, aborting all tests after the first silently.
  After: each pl_choice_t has own cut field; pl_cut_fn signals through
  g_pl_cur_cut_flag (always points to innermost OR-box); save/restore on entry/exit.
  Standard Prolog cut scoping: cut terminates exactly the predicate containing it.
- SWI suite: 0% -> 71% (PASS=41 FAIL=16 TOTAL=57).
  Fully passing: test_exception, test_list, test_misc.
  Remaining 16 failures: rem, float_zero, bips, arg, length, snip, phrase,
  steadfastness, context, string, string_bytes, term_singletons, and others.

NEXT SESSION PL-12:
  Gate target: >= 80% (need 46/57).
  Currently at 41/57 — need 5 more passing suites.
  Approach: run suite with raw output, identify first 5 failing suites,
  fix builtins/semantics causing those failures one at a time.
  Start with: rem (modulo), arg/2, length/2, snip (cut-in-if-then), phrase/2.

---

## Current state (2026-04-15, one4all HEAD f33686e9, corpus HEAD e587489)

PL-1 through PL-11 fully done. PL-12 IN PROGRESS — 71% coverage. Baseline unchanged.

Session 2026-04-15 work (this session — diagnosis only, no net commit to one4all):

### Root cause diagnosed: catch(Var, _, Recovery) bug

`catch(Goal, _, Recovery)` where `Goal` is an E_VAR (Prolog variable bound at
runtime to an atom like `fail`) always succeeds instead of propagating Goal's
failure. Root cause: in the `!threw` branch of catch/3 in pl_runtime.c, when
`goal_e->kind == E_VAR`, the code falls through to
`interp_exec_pl_builtin(goal_e, env)`. That function's `switch(goal->kind)`
has no E_VAR case, hits `default: return 1` — always success regardless of
what Goal is bound to.

Confirmed minimal repro:
```prolog
wrapper(Goal) :- catch(Goal, _, true), !, writeln(first_clause).
wrapper(_)    :- writeln(second_clause).
main :- wrapper(fail).
% Expected: second_clause   Actual (buggy): first_clause
```

This is why arg:zero / arg:two / arg:big / snip all fail: plunit's
`pj_do_fail(Suite, Name, Goal)` uses exactly this two-clause cut pattern with
`catch(Goal, _, true)`.

### Fix approach (NOT yet committed — regression discovered):

Added `pl_invoke_term(Term *t, Term **env)` to dereference a runtime Term and
call it as a goal. Wired into catch/3 E_VAR branch. Fix is structurally
correct BUT causes regressions in arg:unify, arg:one, bips_occurs_check_error
because `pl_invoke_term` for user-pred calls passes `term_deref(args[i])` as
uenv — raw dereferenced pointers instead of fresh trail-linked var cells that
interp_eval expects. The deep-copy alternative also breaks trailing.

### NEXT SESSION PL-12 fix plan:

1. In pl_runtime.c catch/3 E_VAR branch, add:
   ```c
   if (goal_e->kind == E_VAR) {
       Term *gt = pl_unified_term_from_expr(goal_e, env);
       ok = pl_invoke_term(gt, env);
   } else if (is_pl_user_call(goal_e)) { ...
   ```

2. In pl_invoke_term compound branch, for user-pred calls:
   DO NOT pass raw term_deref(args[i]) or deep copies.
   Instead allocate fresh var cells and UNIFY them with the args:
   ```c
   Term **uenv = pl_env_new(arity);
   Trail *trail = &g_pl_trail;
   for (int i = 0; i < arity; i++) {
       int mark = trail_mark(trail);
       unify(uenv[i], t->compound.args[i], trail);
       // don't unwind — keep bindings
   }
   ```
   This preserves trailing so interp_eval sees properly linked vars.

3. Also handle atom goals that are user-defined 0-arity predicates.

4. Gate: suite must stay at 71% with fix, THEN arg:zero/two/big pass → net gain.

5. After arg fixed, address: snip (cut-in-if-then), bips errors, length/2,
   rem:allq (maplist-as-generator), phrase/2, string/string_bytes.

NEXT SESSION starts at step 1 above. DO NOT re-diagnose — go straight to fix.
