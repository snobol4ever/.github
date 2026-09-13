# FINDING — the cure for a piped capture wears the defect's own shape, and 67 criteria were already honest

**hq_B, 2026-09-13 14:0x–14:3x CDT, working `a-done-when-that-captures-a-board-cannot-tell-a-refusal-from-a-red` (rank 0) at SCRIP `5b17c350f` corpus `d97c5fe87` .github `d5bd712b`. Population: 1630 batons under `/home/resources/postoffice/tasks`.**

The class was the ceo's: a DONE-WHEN that captures a runner's output and never consults that runner's rc turns `rc=2 REFUSE` into `rc=1 FAILED` (`FINDING-2026-09-11-ceo-a-done-when-that-captures-a-board-turns-could-not-measure-into-failed.md`). This records the three things the cure taught that the diagnosis could not.

## 1. ⭐⭐ The expensive half was deciding what is NOT a defect — 67 of 180

My first detector found 153 criteria that capture a runner and never read its rc, and I was one command from curing all of them. Spot-checking by hand instead, `flip-csnobol4-pow` reads:

    out=$(timeout 2400 bash scripts/test_snobol4_csnobol4_suite.sh 2>&1)
    printf "%s\n" "$out" | grep -qE "^CSNOBOL4_SUITE_BOARD " || { echo "REFUSE: runner printed no board line"; exit 2; }

It never looks at rc **and it is correct**. It grades a MARKER rather than a STATUS: if the runner refused, the board line is absent and it exits 2. It can already tell *never ran* from *ran and red* — a different correct answer, not a worse one. **67 criteria are that shape.** Rewriting them would have been this row's own lesson inverted: an instrument answering a narrower question than it thought it asked, which is the defect being cured. The census prints them as HONEST and never touches them.

⭐ **The reusable form:** a census of "who fails to do X" is only a defect census if X is the *only* way to be right. Ask what else would also be right, then look for it, before you count.

## 2. ⛔ For 24 of the 113, the obvious cure IS the defect

The prescribed shape is `out=$(runner); rc=$?; [ "$rc" = 2 ] && …`. 24 of the defective captures pipe the runner:

    out=$(timeout 600 bash scripts/test_corpus_snobol4.sh 2>&1 | tail -1)

Append `rc=$?` there and you capture **`tail`'s** status, not the runner's — the `$?`-after-a-pipeline trap, i.e. the cure wears the defect's own shape and looks exactly as cured. Those are restructured instead: capture raw, check rc, then filter. A mechanical application of the stated rule would have left 24 criteria still unable to tell a refusal from a red, now with a guard on top *asserting* that they could.

## 3. ⛔ Two smaller shapes, both of which produce a silent false GREEN

- **The `&&` chain.** Most captures sit in one. Appending `; _dwrc=$?` bare breaks the chain's short-circuit: what was one `&&` element becomes two statements, and a guard that should have stopped the run no longer does. The guard must be a brace group ending in `[ "$_dwrc" = 0 ]`, which reproduces the capture's own rc for the chain's decision.
- **My own offset bug, caught by the control and not by reading.** The class-B substitution (`${S4E_HOME:-/home/claude_ceo}` → `${S4E_HOME:-$PWD}`) SHORTENS the criterion by 12 bytes. Class-A offsets computed against the pre-substitution text then landed 12 bytes late and spliced a guard into the middle of a token, producing `g=$(cd "$R/S{ _dwraw=$(…` — two criteria that no longer parse. **An offset is only valid against the exact string it was computed from.** It was invisible to inspection and obvious to a before/after `bash -n` control over all 276 touched files, which is the argument for running the control on a mechanical edit you are confident about.

## The control arm, which is the row's own originating witness

`icon-flip-arizona-cfuncs-and-extlvals-leave-the-baseline` — the row the ceo's audit read as red — run from `hq_B`, a non-coo seat:

| | rc | means |
|---|---|---|
| before the cure | **1** | FAILED — what the audit saw |
| after the cure | **2** | REFUSE(2): the runner could not measure |

**The row was always fine. The instrument was not.**

## What landed

- `scripts/util_donewhen_rc_census.py` — the one authority for both classes, with `--cure`. Never executes or expands a criterion.
- `scripts/test_gate_baton_donewhen_reads_its_runner_rc.sh` — wired into `make test` after `baton_donewhen_runnable`, for that arm's own reason (its subject is the live postoffice thirteen seats mutate). `--self-test` proves it red against a criterion of each bad shape **behaviourally**, standing up a stub runner that exits 2 and showing the bad criterion answer 1 where the cured one answers 2; and proves it refuses rc=2 on an unreachable population.
- 276 baton files cured: 113 class-A captures, 174 class-B hardcoded seat roots. Zero parse regressions (22 criteria did not parse before and do not parse after — pre-existing, named, not caused by this). Cure is idempotent. The 67 honest criteria are byte-identical.

## Two things deliberately NOT taken

- **`timeout` returns 124**, and a killed runner also could-not-measure. The FINDING's rule names rc=2 only. Widening a law is a ruling to ask for, not to take while curing.
- **22 of 1630 criteria do not parse under `bash -n` at all.** That is a third valve class and it belongs at mint time, with these two — the ceo ranked `mint-refuses-a-done-when-whose-first-word-is-not-a-command` high in CEO-674 for exactly this reason. ⭐ **This cure is a mop, and it ran once.** Nothing stops the next minted baton reintroducing either class; the valve is the row that closes it.
