---
name: gates-and-witnesses
description: Fleet tests: test_gate_*.sh, witnesses and refs, ALL.csv, STEPS.tsv, every DONE-WHEN and PREMISE-WHEN; the three exit codes, fail-once, the instrument laws. REQUIRED by the skill gate before editing a test or a criterion.
---

# Gates and witnesses

Every claim is proved by a command that reads RED now and GREEN when the work is done (CEO-1386). The law is RULES.md; this page is the working summary. The detail, with quoted examples, is in `reference.md` beside this file: read only the section you need.

## 1. THE RULES

- **Three exit codes.** rc 0 GREEN over a measured population; rc 1 RED, naming what is red; rc 2 REFUSE when it cannot measure (no or stale `./scrip`, empty population, a program that did not compile, a missing oracle). A refusal is never a pass. A test never edits itself to return 0.
- **One board line** per gate (`<NAME>_BOARD ... (tree <hash>)`), ending `GATE OK [name]` or `GATE FAIL [name]`.
- **Stale-binary preflight on line 2** of any gate that runs `./scrip`: `util_require_fresh.sh --gate "$(basename "${BASH_SOURCE[0]}" .sh)" || exit $?`.
- **Fail once, never by a plant** (CEO-1680): show it red on the commit before the cure, or on a corrupted copy of the ref in scratch. No test-only seam in `src/`. A gate that can no longer trip is dead (CEO-576).
- **No XFAIL.** A known red stays red as debt; what the oracle cannot answer is excluded as `NO_ORACLE_ANSWER` (CEO-1696/1934).
- **A DONE-WHEN is a command** graded on origin that a deletion cannot satisfy (CEO-553/555). It starts `cd "${S4E_HOME:?REFUSE(2): S4E_HOME unset}" &&`, reads the denominator it grades, never pins a count, and carries a PREMISE-WHEN.
- **A witness** is one program, its ref cut from the oracle through its accessor in `lib_oracle_flags.sh`, graded in both modes (`--modes m3,m4`), each mode against the oracle.
- **Declared sizes** (CEO-1353): every entry's `heap_kb`/`stack_kb` in `ALL.csv`; runners pass `-d<kb>k -s<kb>k`, never an env knob.
- **One testing officer** (CEO-1342/2068): the coo runs suites, boards and the blocking set and writes the suite table. A lander re-grades its one program in both modes, runs `test_feature_reps.sh` and the smokes of every language its diff touches, then asks `s4e_test_request.sh <suite-key> <entry>...` (8 at most).
- **A dirty-tree reading is unread** (CEO-2060): grade in a clean worktree outside the root.
- **The landing gate is not the close criterion** (2026-11-05, the coo's ruling and the cao's `--land N`): a row or step whose pass reads the coo's graded readings (`results.tsv`, the board) cannot gate its own landing. Land on what the lander can prove (the witnesses in both modes, the census, the smoke; a design harness's `--land N`), file `s4e_test_request.sh`, park `PARKED-AWAITING:<request-id>`, and close by `done` on the coo's verdict (`--step N`, unchanged).
- **A probe reads an order of events, never a wall-clock bound**: a lease held "at most 3 s" or a timeout race reads red under box load and blocks every lander (`s4e_land.sh --probe` arm 7 and `util_run_slot.sh --probe-sem`, 2026-11-05).
- **A probe writes only scratch state**: a scratch postoffice (`S4E_POST`) and scratch tubes, never the live queue, `QUEUE.tsv` or a live baton.
- **A sparse worktree keeps `include/` and `library/`**: `sparse-checkout set --no-cone '/*' '!/benchmarks/' '!/demos/'`. Without `corpus/include` a SNOBOL4 program cannot open its `.inc` and exits 231 with empty output, a false red (2026-11-05).
- **An absence counts only after the tool spoke**: a DONE-WHEN that reads a tool's output first requires that tool's own board line, then checks the program is absent (`grep -q '^SUITE_ROW suite=K ' f && ! grep -qE '^SUITE_ROW_RED ([^ ]*:)?NAME ' f`); a bare `! grep` after a refused tool is a false green.

## 2. THE FILES

- `harness/scripts/`: `test_gate_*.sh` (wired through `gate_wiring.tsv` by `util_gate_wiring.py`), `test_smoke_<lang>.sh`, `test_feature_reps.sh`, `test_<lang>_ladder.sh`, `test_design_*_steps.sh`, `lib_oracle_flags.sh`, `util_require_fresh.sh`, `util_run_slot.sh`, `corpus_suite_harness.py`, `util_add_ladder_witness.py`, `util_suite_partition.py`, `util_suite_row_at_100.sh`.
- `corpus/tests/<lang>/`: `ALL.<ext>`, `ALL.ref`, `ALL.csv`, `ALL.rc`, `PARTITION.tsv`, `LADDER.tsv`, `ALL.path`, and nothing else (CIO-24, CIO-55: `python3 harness/scripts/util_tests_layout_census.py --lang <lang> --check`; the design folders that still stand are being absorbed).
- The boards: `/home/resources/progress/{results.tsv,SUITES.tsv,SMOKE.tsv}`, written by the coo.

## 3. WORKED EXAMPLES

The standard DONE-WHEN of a suite row (every suite-to-100 row uses it; `done` reads the board and runs nothing):

```bash
DONE-WHEN: cd "${S4E_HOME:?REFUSE(2): S4E_HOME unset}" && bash harness/scripts/util_suite_row_at_100.sh fpc
PREMISE-WHEN: cd "${S4E_HOME:?REFUSE(2): S4E_HOME unset}" && bash harness/scripts/util_suite_row_at_100.sh fpc; [ "$?" = 1 ]
```

A gate's ending, `test_gate_no_rsp_reset_at_beta.sh` (refuse, then the verdict):

```bash
[ "$tp" -gt 0 ] || { echo "REFUSE(2): nothing compiled"; exit 2; }
[ "$un" = 0 ] || { echo "REFUSE(2): $un program(s) did not compile -- the count does not cover the population"; exit 2; }
[ "$tb" = 0 ] && { echo "GATE OK [test_gate_no_rsp_reset_at_beta]: no beta resets rsp in $tp programs"; exit 0; }
echo "GATE FAIL [test_gate_no_rsp_reset_at_beta]: $tb beta reset(s) of rsp"; exit 1
```

Cutting a ref (run twice and compare; then show the witness red on today's tree):

```bash
timeout -k 5 60 "$(swipl_bin)" -q -t halt -g main w.pl < /dev/null > w.ref
```

## 4. THE PROVING INSTRUMENTS

- A gate: red on `<cure>^` or a corrupted ref, green after; wired in the same landing (`SCRIP/Makefile` line if it joins the blocking set, then `util_gate_wiring.py adopt`).
- A witness is a container entry (CIO-24), added by `util_add_ladder_witness.py` (`--dialect D` cuts a Pascal answer in fpc's mode D and writes the row's `dialect` cell; `--file X` carries a companion standing beside the source as the entry's file fence, format 2 only; the cfo 2026-11-12), never a loose pair or a design folder; `corpus_suite_harness.py run ... --modes m3,m4 --partition entry:<name>`; `util_suite_partition.py build` when `ALL.csv` changed.
- A design step row: `test_design_<x>_steps.sh --step N` is its DONE-WHEN; the plan row's is `--list`.
- A red: `monitor_run.sh <prog> --oracle` first, then asm-diff beside a passing sibling, gdb last.

## 5. THE FORBIDDEN FORMS

A test edited to exit 0; an `xfail` of 1; a prose DONE-WHEN, one that pins a count, or one a deletion satisfies (`! grep -q defect`); a plant in `src/`; a gate with no refusal arm; a gate anchored on one found witness; a board or suite row written by anyone but the coo; a ref cut from the other mode or from a bare oracle path; a run without `timeout -k 5`, or without `< /dev/null` when it reads no stdin; an env size knob in a runner; outputs under the root; a symlink; `pkill -f`; `grep -q` under `pipefail`; a wall-clock assertion in a probe; a proof row on the live queue; a pass probe that reads the coo's readings used as a landing gate; a sparse worktree without `include/`; a timeout (rc 124) folded into a crash or a refusal (a verdict that turns on time records the duration, since an rc is no measure of time).

## 6. WHERE THE REST LIVES

RULES.md (`A ROW EXISTS ONLY WHILE`, `NO PLANTED BREAKAGE`, `ONE TESTING OFFICER`, `DECLARED SIZES`, `DIRTY-TREE`); skill `suites-and-grading` (the masters, stored partitions, the progress store, the suite table, test requests); skill `design-plans` (STEPS.tsv and the step harnesses); skill `fleet-bus` (a DONE-WHEN on a row).

## 7. HOW A LANDING IS PROVED

The landing recipe is skill `fleet-bus` section 7 (one copy, there). What it owes this skill: the criterion written first and red once without a plant (section 1); the cure green in both modes with the feature reps and the smokes; the land gate split from the close criterion when the pass reads the coo's readings (section 1); the coo's test request for the suite's part.
