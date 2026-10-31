---
name: gates-and-witnesses
description: Writing the fleet's tests -- a test_gate_*.sh (1,596 on file, one population, a board line, rc 0 green, rc 1 red, rc 2 REFUSE when it cannot measure), a construct ladder rung, a design step harness (test_design_*_steps.sh), a witness program with its ref cut from the oracle (util_add_ladder_witness.py, the suite masters and their sidecars), the fail-once proof (CEO-1680: a proper test, never planted breakage, no XFAIL), declared sizes per entry, a DONE-WHEN and PREMISE-WHEN a deletion cannot satisfy (CEO-553/555), the one-testing-officer split (the coo runs suites and boards; a lander runs the handful and the smokes), the stale-binary preflight, the run slots. Load before writing or editing any gate, rung, witness, ref, STEPS.tsv, ALL.csv row or baton criterion, and for any question about what a test may assert, what refuses, what a board line is, or who runs what.
---

# Gates and witnesses: the craft

The fleet proves everything by a runnable command that reads RED now and GREEN when the work is done (CEO-1386: a row exists only while a measurement says the problem exists). Four kinds of test carry that: a GATE (a hermetic census or invariant over a population, with a board line and three exit codes), a WITNESS (one program with a ref cut from the oracle, graded in both modes), a RUNG (a witness of one construct on the language's ladder) and a DESIGN STEP HARNESS (the witnesses of a DESIGN-PLAN, step by step). The law is RULES.md (CEO-1386 A ROW EXISTS ONLY WHILE A MEASUREMENT SAYS SO; CEO-1680 NO PLANTED BREAKAGE and THERE IS NO XFAIL; CEO-553/555 a criterion a deletion satisfies is false; CEO-1342/1671/1673/1893/1926/1928/2068 ONE TESTING OFFICER; CEO-1696/1934 NO ORACLE ANSWER → EXCLUDED; CEO-1353/1281 DECLARED SIZES; CEO-576 a gate anchored on a found witness dies the day someone cures it; CEO-1676 STORED PARTITIONS; CEO-2060 A DIRTY-TREE READING IS UNREAD). Lines quoted below are from harness 230edb1 and corpus at 2026-10-31.

## 1. THE RULES (each with its receipt)

- **THREE EXIT CODES, ONE BOARD LINE**: rc 0 GREEN over a MEASURED population, rc 1 RED naming what is red, rc 2 REFUSE when the test cannot measure (no `./scrip`, a stale binary, an empty population, a program that did not compile, a missing oracle); a gate prints one greppable board line (`<NAME>_BOARD lang=<l> ...=<n> programs=<p> (tree <hash>)`) and ends `GATE OK [name]: ...` or `GATE FAIL [name]: ...`. A test NEVER edits itself to return 0; a measurement it cannot take is a refusal, not a pass (`[ "$un" = 0 ] || { echo "REFUSE(2): ..."; exit 2; }`).
- **THE STALE-BINARY PREFLIGHT ON LINE 2** (`util_require_fresh.sh --gate "$(basename "${BASH_SOURCE[0]}" .sh)" || exit $?`: *"THE ONE-LINE STALE-BINARY PREFLIGHT, callable from ANY language ... CONTAINS NO STALENESS LOGIC AND MUST NEVER GROW ANY"*): every gate that grades `./scrip` refuses rc 2 on a binary older than HEAD; rebuild after every commit or the gates refuse.
- **A CRITERION FAILS ONCE BEFORE IT IS TRUSTED, AND NEVER BY A PLANT** (CEO-1680, Lon to hq_snobol4, verbatim: *"Do not add broken code just to enable a test to determine a bug in PATTERN matching is fixed. Just create a proper test instead."*): a new ref is shown red against a corrupted copy, or the gate red on the commit before the cure (`<cure>^`); no test-only seam in the code; a gate that can no longer trip once the defect is cured is dead (CEO-576) and is re-anchored on a synthetic population or deleted with its row.
- **THERE IS NO XFAIL**: the `xfail` column of a suite table is 0 or the entry is EXCLUDED with a reason; a known-red entry stays red on the board as debt (CEO-749/1518); what the oracle cannot answer leaves the denominator as `NO_ORACLE_ANSWER` (CEO-1696/1934); a test that cannot measure REFUSES rc 2.
- **A DONE-WHEN IS A COMMAND, GRADED ON ORIGIN, THAT A DELETION CANNOT SATISFY** (CEO-553: a row retired, not closed, *"its DONE-WHEN would pass on deleting correct code"*; CEO-555: *"a criterion is a hypothesis about what done looks like, and when the measurement contradicts it, the criterion loses"*; `mint` refuses a prose DONE-WHEN and a second column-0 DONE-WHEN): it reads the denominator it grades, never pins a population count, carries its PREMISE-WHEN (what must exist for the question to make sense), and `done` runs it and refuses a red. It begins `cd "${S4E_HOME:?REFUSE(2): S4E_HOME unset}" &&`.
- **A WITNESS IS ONE PROGRAM, ITS REF CUT FROM THE ORACLE, GRADED IN BOTH MODES**: the oracle through its accessor (`sbl_correctness_bin()`, `icont_bin()`/`iconx_bin()`, `swipl_bin()`, `gprolog_bin()`, `xsb_bin()`, `fpc_bin()`, `rakudo_bin()`, `unicon_bin()` in `lib_oracle_flags.sh`; a bare oracle path outside the accessor is a gate's red), run under `timeout -k 5` with `< /dev/null` when it reads no stdin; a `.ref` is bytes, binary to git, compared with `cmp`; `--modes m3,m4` is mandatory and each mode is graded against the oracle, never against the other.
- **EVERY ENTRY DECLARES ITS SIZES** (CEO-1353/1281; `ALL.csv`: `rank,entry,origin,family,kind,xfail,n_lines,heap_kb,stack_kb,compile_args,run_args,<feature columns>`): runners pass `-d<kb>k -s<kb>k` from the row, never an environment knob; the declared size is a HARD CAP; a program out of stack gets a bigger declared `-s`, never data moved to the heap (CEO-1354).
- **A MASTER IS A CONTAINER, NEVER A PROGRAM**: `corpus/tests/<lang>/ALL.<ext>` with `ALL.ref`, `ALL.csv`, `ALL.wantrc`, `PARTITION.tsv` (built by `util_suite_partition.py build`, regenerated by any landing that changes `ALL.csv`, CEO-1676); the one extraction authority is `corpus_suite_harness.py extract`; the one add-a-witness path is `util_add_ladder_witness.py` (*"Before this script, none existed ... three prior sessions ... hit this exact wall"*).
- **A RUNG IS ≤ 20 LINES, ONE CONSTRUCT, DECLARED NEVER DERIVED** (`corpus/tests/<lang>/config/LADDER.tsv`: *"THE CONSTRUCT CENSUS. DECLARED, NEVER DERIVED; the LAST rung line is the TOP"*): a declared rung not built is RED; rung N+1 opens when N is green in both modes (`test_<lang>_ladder.sh --to N | --only N`).
- **A DESIGN STEP HARNESS READS A STEPS.tsv** (`step slug executor probe witnesses ruling landing_files`): `--list` prints the plan, `--step N` grades the step's witnesses in both modes from the witness folder plus the step's probe, outputs under `/tmp` never the root; the DONE-WHEN of a design row is `--list` succeeding and each step's red today recorded on the page.
- **ONE TESTING OFFICER** (CEO-1342 and its amendments): the coo runs suites, boards, the blocking set (`make test`) and the `.s` regeneration, up to FOUR tests at once with one run slot left free (CEO-2068), and alone writes the SUITE TABLE rows; a lander fixes ONE program, re-grades THAT program in both modes, runs `test_feature_reps.sh <lang> <feature>` (≤ 8 core entries, CEO-1677) and `test_smoke_<lang>.sh` for every language its diff touches (all eight for shared code), and asks for named tests by `s4e_test_request.sh <suite-key> <entry>...` (≤ 8 programs); `lib_one_runner.sh` refuses a board (rc 2) to any seat but the runner. `make preflight` is not a per-push check; heavy verification once per batch of 3-4 (CEO-1316).
- **A DIRTY-TREE READING IS UNREAD** (CEO-2060): a board line stamped `-dirty` assembles no row; grade in a clean worktree outside the root; never edit the tree a loop is running on. Every hand run takes a run slot (`util_run_slot.sh`, the `flock` loop over `/tmp/s4e-run-slots/slot0..7`).
- **NO SYMLINKS, NO ENV OVERRIDES, FIXED RELATIVE PATHS** (CEO-1817/1819/1820/1853): a script finds its siblings by `HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; ROOT="$(cd "$HERE/../.." && pwd)"`; a scratch worktree needs harness and corpus siblings beside it.

## 2. THE FILES

- `harness/scripts/test_gate_*.sh` (1,596; the ONE population is `gate_wiring.tsv` with its class column, written only by `util_gate_wiring.py`; a new gate is adopted into the wiring floor by running `make preflight` after writing it), `test_smoke_<lang>.sh` (eight), `test_feature_reps.sh`, `test_<lang>_ladder.sh`, `test_design_*_steps.sh` (12: `test_design_clause_source_record_steps.sh`, `test_design_unicon_steps.sh`, ...), `test_rtx_unit.sh`, `test_bootstrap_parsers.py`, the package runners (`test_icon_unicon_suite.sh`, ...).
- The libraries: `lib_oracle_flags.sh` (the accessors), `lib_one_runner.sh`, `lib_bb_block_label_prefix_check.py`, `util_require_fresh.sh`, `util_run_slot.sh`, `util_spine_population.sh` (the compile population of the placement gates), `util_suite_partition.py`, `corpus_suite_harness.py` (`run ... --lang <l> --modes m3,m4 --partition entry:<name>`, `extract`, `convert`, `pin-ref`, `list`), `util_add_ladder_witness.py`, `monitor_run.sh` (the bracket), `util_instr_count.sh`, `util_quiet_slice.sh`, `s4e_msg.sh` (`mint`, `done`), `s4e_test_request.sh`, `handoff_status.sh`.
- `corpus/tests/<lang>/`: `ALL.<ext> ALL.ref ALL.csv ALL.wantrc PARTITION.tsv`, `config/LADDER.tsv`, the design folders (`prolog/clause_source_record/`, `prolog/lifo/`, `icon/unicon/`: `*.pl|*.icn`, `*.ref`, `STEPS.tsv`, `KEEP.md`); `corpus/demos/` and `corpus/benchmarks/` (the only trees with committed `.s`); `corpus/packages/<lang>/` (the vendored suites with their own tables and runners).
- The record: `SCRIP/Makefile` `test` (the blocking set) and `preflight` (the cheap hermetic arms, `preflight_arms.txt`, pinned by `test_gate_preflight_arms_stay_cheap.sh`); `/home/resources/progress/{results.tsv,SUITES.tsv,SMOKE.tsv}` (the boards the coo writes); `.github/SCORE.md` § THE SUITE TABLE.

## 3. WORKED EXAMPLES (quoted)

A gate in full shape, `test_gate_no_rsp_reset_at_beta.sh` (36 lines): the population from one authority, each program compiled once from its own directory under a timeout, a census over the output, a board line per language and in total with the tree hash, the three exit codes with the refusal reasons named.

```bash
[ -s "$T/list" ] || { echo "REFUSE(2): the population is empty${L:+ for $L}"; exit 2; }
while IFS=$'\t' read -r lang f; do
    i=$((i+1)); mkdir -p "$T/$lang"
    ( cd "$(dirname "$f")" && timeout -k 5 300 "$SC" --compile --out="$T/$lang/$i.s" "$(basename "$f")" < /dev/null >/dev/null 2>&1 ) || { rm -f "$T/$lang/$i.s"; un=$((un+1)); }
done < "$T/list"
echo "RSP_RESET_AT_BETA_BOARD total beta=$tb functions=$tf programs=$tp unmeasured=$un (tree $(git -C "$ROOT/SCRIP" rev-parse --short HEAD))"
[ "$tp" -gt 0 ] || { echo "REFUSE(2): nothing compiled"; exit 2; }
[ "$un" = 0 ] || { echo "REFUSE(2): $un program(s) did not compile -- the count does not cover the population"; exit 2; }
[ "$tb" = 0 ] && { echo "GATE OK [test_gate_no_rsp_reset_at_beta]: no beta resets rsp in $tp programs"; exit 0; }
echo "GATE FAIL [test_gate_no_rsp_reset_at_beta]: $tb beta reset(s) of rsp"; exit 1
```

A design step harness grading one witness in both modes, `test_design_unicon_steps.sh` 59-69: mode 3 in process, mode 4 compiled, assembled and linked the harness's way (PIE, `-lscrip_rt`, the rpath), each byte-equal to its `.ref` with rc 0, the reds named by mode and witness.

```bash
for w in $wits; do
    n=$((n + 1)); src="$WD/$w.icn"; ref="$WD/$w.ref"; o="$OUT/step$step/$w"
    [ -f "$src" ] && [ -f "$ref" ] || refuse "witness $w has no .icn or .ref in $WD"
    ( cd "$WD" && timeout -k 5 60 "$SC/scrip" "$w.icn" < /dev/null > "$o.m3.out" 2> "$o.m3.err" ); rc=$?
    if [ "$rc" = 0 ] && cmp -s "$o.m3.out" "$ref"; then m3p=$((m3p + 1)); else reds="$reds m3:$w(rc$rc)"; fi
    if ( cd "$WD" && timeout -k 5 120 "$SC/scrip" --compile --out="$o.s" "$w.icn" < /dev/null > /dev/null 2> "$o.m4c.err" ) \
       && gcc -c "$o.s" -o "$o.o" 2> /dev/null && gcc "$o.o" -L"$SC/out" -lscrip_rt -lm -lpthread -Wl,-rpath,"$SC/out" -o "$o.bin" 2> /dev/null; then
        ( cd "$WD" && timeout -k 5 60 "$o.bin" < /dev/null > "$o.m4.out" 2> "$o.m4.err" ); rc=$?
        if [ "$rc" = 0 ] && cmp -s "$o.m4.out" "$ref"; then m4p=$((m4p + 1)); else reds="$reds m4:$w(rc$rc)"; fi
    else reds="$reds m4:$w(no-build)"; fi
done
```

A suite row with its declared sizes, `corpus/tests/snobol4/ALL.csv` line 2 (the header's first eleven columns, then one feature column per construct the partition builds shells from):

```text
rank,entry,origin,family,kind,xfail,n_lines,heap_kb,stack_kb,compile_args,run_args,FENCE,ARB,ARBNO,POS,...
1,simple_assign_1,probe_conformance__n04_terminal,probe_conformance,line,0,1,131072,4096,--stlimit,,0,0,0,0,...
```

A DONE-WHEN that a deletion cannot satisfy and that reads its own denominator (the craft-skills row, CEO-2076): it tests the files exist, then runs the checker over them and the installer's `--check`; deleting a skill turns it red, and `done` runs it.

```bash
DONE-WHEN: cd "${S4E_HOME:?REFUSE(2): S4E_HOME unset}" && for s in box-templates rtx-asm-leaves lowering scrip-c-code gates-and-witnesses; do test -f .github/skills/$s/SKILL.md || { echo "RED: no skill $s"; exit 1; }; done && python3 harness/scripts/util_skill_check.py --craft box-templates rtx-asm-leaves lowering scrip-c-code gates-and-witnesses && bash .github/scripts/propagate_skills_ceo_2071.sh --check
PREMISE-WHEN: test -d "${S4E_HOME:?}/.github/skills"
```

Cutting a ref from the oracle, the shape every witness follows (Prolog shown; `timeout -k 5` because a blocked oracle read ignores SIGTERM; the accessor, never a bare path): `timeout -k 5 60 "$(swipl_bin)" -q -t halt -g main w.pl < /dev/null > w.ref` run TWICE and compared, then the witness red on today's tree before it is committed.

## 4. THE PROVING INSTRUMENTS (harness/scripts)

- For a new gate: run it on the tree where it should be red (the commit before the cure, or a corrupted copy of the ref in a scratch worktree) and on the tree where it is green; `util_require_fresh.sh` on line 2; a board line; `gate_wiring.tsv` regenerated by `util_gate_wiring.py` (then `make preflight`); `test_gate_preflight_arms_stay_cheap.sh` if the gate joins `preflight_arms.txt`; `test_gate_template_watch_names_a_planted_violation_by_commit.sh` is the model of a gate proven on a planted commit in a scratch repo, never in the tree.
- For a new witness: `util_add_ladder_witness.py` (a rung) or the design folder with `STEPS.tsv`; the ref cut twice from the oracle through its accessor; `corpus_suite_harness.py run ... --modes m3,m4 --partition entry:<name>`; `util_suite_partition.py build` when `ALL.csv` changed; `git add` the `.ref` as the binary it is.
- For a new design harness: clone the newest `test_design_*_steps.sh`, change `WD`, the extension, the probes; `--list` is the row's DONE-WHEN; every step's reading today goes on the ARCH page.
- For the lander's proof: `test_feature_reps.sh <lang> <feature>` (`--entries` needs a feature every named entry carries), `test_smoke_<lang>.sh`, `s4e_test_request.sh <suite-key> <entry>...` for the coo's verdict by telegram; `handoff_status.sh` pasted verbatim at the hand-off.
- The bracket for a red: `monitor_run.sh <prog> --oracle` (the bug lies between the last event both agree on and the first they diverge on), ASM-DIFF-FIRST beside a passing sibling within one mode, gdb last with a breakpoint and a hit count; validate an instrument by running it; a null result bounds the probe.

## 5. THE FORBIDDEN FORMS

A test edited to exit 0; an `xfail` cell set to 1; a prose DONE-WHEN, or one that pins a count (`== 274`), or one a deletion satisfies (`! grep -q defect`), or one without `S4E_HOME`; a planted seam in `src/` so a gate can trip; a gate with no refusal arm (a missing binary graded as a pass or a fail); a gate anchored on one found witness; a board run by a seat that is not the runner, or a suite table row written by anyone but the coo; a ref cut from the other mode, from a `.std` alone, or from a bare oracle path; a run without `timeout -k 5`, without `< /dev/null` when it reads no stdin, or with `< /dev/null` on a piped run; `SCRIP_HEAP_KB` or any environment size knob in a runner (the row's `-d`/`-s`); outputs under the root (proof dumps die in `/tmp`); a reading from a `-dirty` tree; a worktree without its harness and corpus siblings; a symlink; `pkill -f`; a `grep -q` pipe under `pipefail` (drain with `grep >/dev/null`); a `python3 - <<EOF` that reads stdin from a pipe (the heredoc eats it); a measurement loop writing outputs to `/tmp` while the box is busy; a clock outside `util_quiet_slice.sh`; `util_instr_count.sh` called with a pipe or socket stdin (it drains stdin to its end and the caller hangs: `< /dev/null` unless the program reads stdin; hq_jvm 2026-10-31).

## 6. THE ARCH PAGES

| question | page |
|---|---|
| the laws of rows, criteria, refusal, no XFAIL, one testing officer, declared sizes, partitions, dirty trees | RULES.md (grep `A ROW EXISTS ONLY WHILE`, `NO PLANTED BREAKAGE`, `ONE TESTING OFFICER`, `DECLARED SIZES`, `STORED PARTITIONS`, `DIRTY-TREE`) |
| the stored partition of a suite (core, shells, chunks) | ARCH-SUITE-PARTITIONS.md |
| the design-plan shape (steps, witnesses, probes, the harness) | ARCH-PROLOG-DATABASE.md § 23 (clause-source-record), ARCH-UNICON.md § 2, ARCH-FLEET-PLAN-TO-100.md |
| the monitor bracket and the oracle forks | the language skills' § 6, `/home/resources/{icon,gprolog,swipl,fpc,rakudo}-mon/` |
| the score, the suite table, the boards | SCORE.md § THE SUITE TABLE, `/home/resources/progress/` |
| the receipts: CEO-553/555 (the criterion), CEO-576 (a gate anchored on a witness), CEO-1316 (verification cost), CEO-1342/2068 (one runner), CEO-1386 (a row is a measurement), CEO-1676 (partitions), CEO-1680 (no plant), CEO-1696/1934 (no oracle answer), CEO-2060 (dirty tree) | GOAL-CEO.md |

## 7. HOW A LANDING IS PROVED

1. Write the criterion first, as a command: red on today's tree (run it, keep the red output), its PREMISE-WHEN true; `mint` it with `--stdin` and a quoted heredoc (no backtick, no `$(`).
2. Build the instrument: a gate with its three exit codes, its board line and its line-2 preflight; or a witness with its oracle-cut ref and its row (sizes declared) and the partition rebuilt; or a step harness over its `STEPS.tsv`. Show it red once without a plant.
3. Prove the cure with it: green after, in both modes for a witness; `test_feature_reps.sh` and the smokes for the lander's part; the coo's named test request for the suite's part; the gate adopted into the wiring floor.
4. Land: harness and corpus before `.github`; the baton's LEDGER and NEXT; `claim` + `done` (which runs the DONE-WHEN and refuses a red); `handoff_status.sh` at the sitting's end.
