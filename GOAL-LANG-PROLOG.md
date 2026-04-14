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

- [ ] **PL-2** — Install SWI + GNU test suites.
  Write `scripts/install_swi_prolog_tests.sh` and
  `scripts/install_gnu_prolog_tests.sh`. Run both.
  Gate: test files present in corpus.

- [ ] **PL-3** — S-10e: `assertz/asserta/retract/abolish`.
  Dynamic pred table mutation in `interp_exec_pl_goal`.
  Gate: rung13 5/5, rung14 5/5, rung15 5/5.

- [ ] **PL-4** — S-10f: atom builtins.
  `atom_length/2`, `atom_chars/2`, `atom_codes/2`, `atom_concat/3`.
  Gate: rung12 5/5.

- [ ] **PL-5** — S-10g/h: term ordering + sort.
  `@</2`, `@>/2`, `@=</2`, `@>=/2`, `sort/2`, `msort/2`.
  Gate: rung16 5/5, rung17 5/5.

- [ ] **PL-6** — S-10i/j: `succ/2`, `plus/3`, `format/2`.
  Gate: rung18 5/5, rung19 5/5.

- [ ] **PL-7** — S-10k/l: `numbervars/3`, `char_type/2`.
  Gate: rung20 5/5, rung21 5/5.

- [ ] **PL-8** — S-10m/n: write variants, bitwise arith ext.
  `write_canonical/1`, `writeq/1`, bitwise ops, `max/min`, `**`, `sign`.
  Gate: rung22 5/5, rung23 5/5.

- [ ] **PL-9** — S-10o/p: string/IO builtins, `term_string/2`.
  Gate: rung24 5/5, rung25 5/5.

- [ ] **PL-10** — S-10q/r/s: `copy_term/2`, `nb_setval/nb_getval`,
  `throw/1`, `catch/3`.
  Gate: rung26 5/5, rung27 5/5, rung28 5/5.

- [ ] **PL-11** — S-10t/u: float ops, DCG `-->` expansion, `phrase/2,3`.
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
- bb_broker.c is frozen.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

---

## Current state (2026-04-14, one4all HEAD 43dc03da)

PL-1 done. rung01–11 14/14 PASS --ir-run.
PL-2 through PL-19 open.
Next: PL-2 — write install scripts for SWI and GNU test suites.
Then PL-3 — assertz/asserta/retract/abolish (rung13/14/15).
