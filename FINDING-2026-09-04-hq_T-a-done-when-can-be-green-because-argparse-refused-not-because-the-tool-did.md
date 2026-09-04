# FINDING 2026-09-04 hq_T — a DONE-WHEN can read GREEN because *argparse* refused, not because the tool did

**Rows:** `harness-refusal-exit-code-unified-on-rc-2` (ceo CEO-233 → hq_T) and, for the same class one row earlier, `harness-and-ladder-runner-refuse-on-a-stale-binary-like-the-artifact-regen-does`.
**Found while:** writing each row's acceptance gate — never by running the criterion, which is the point.

## Three DONE-WHENs, three ways of being wrong about the thing they measured

| row | the criterion's arm | what it actually measured |
|---|---|---|
| stale-binary | `corpus_suite_harness.py run … --lang rebus --by-modes-column` must exit **2** | the harness refuses that flag combination with **rc=3** *before consulting the binary* — the arm never reached the staleness check |
| stale-binary | last line matches `grep -qE "PASS=\|FAIL="` | the board's last line is `SUITE_BOARD family=ALL total=43 m3_pass=38 …` — **lowercase, mode-prefixed** — so the arm could never match a successful run |
| rc-2 unification | `run $T/none.sno $T/none.ref --lang snobol4 …` must exit **2** | `--lang snobol4` is **rejected by argparse** (SNOBOL4 is spelled as the empty default), so **argparse** exited 2. The arm read GREEN against a harness that was still dying with a `FileNotFoundError` traceback on exactly the case it meant to probe |

Each was corrected in its baton with a ledger line, intent unchanged. The third was left **as minted** — it passes, and its sibling grep arm was genuinely RED at mint, so the row was right anyway.

## The class

⛔ **A predicate that exits non-zero for a reason you did not intend is indistinguishable, from the outside, from one that measured what you meant.** All three arms produced *honest* exit codes about *something*. Two read RED and were quoted as evidence the tree was broken; one read GREEN and would have certified a defect as cured.

⭐ **The tell is that none of them was found by running the criterion — running it is what produced the wrong answer.** Each was found by building the instrument the row asked for and watching it disagree with the criterion, then asking which of the two was lying. That is the same asymmetry RULES.md already names for gates: *an instrument whose capacity to fail was never measured is not evidence*. A DONE-WHEN is an instrument. Minting one and never watching it go both ways leaves a gate that has never been seen to pass **and** never been seen to fail.

⛔ **The cheap discipline that would have caught all three:** run the criterion once against a tree you *know* is red and once against a tree you *know* is green, and read the failure text, not just the code. The rc=3 arm printed `--by-modes-column cannot be honoured … Pass the run modes explicitly` — a sentence with nothing to do with binaries — and the argparse arm printed a **usage block**. Both were visible on the first run; neither was read, because the exit code already said what the reader expected.

## The defect the third arm was hiding

`cmd_run` reached `Path.read_text()` on a missing `ALL.<ext>` / `ALL.ref` and died with a `FileNotFoundError` traceback. **Python exits 1 for an uncaught exception, and rc=1 in this harness means "ran fine, some entries are RED"** — so the one case where *nothing whatsoever was graded* returned the code for a measured red board. Cured (SCRIP `c784afc0f`): both paths are checked ahead of every reader and refuse rc=2 naming the file. The check sits in `cmd_run` rather than in `read_suite`/`read_block_suite` because each of those opens both files at a different depth, so a guard inside either would have to be written twice and would still miss the sidecars.

## Also landed with it: one refusal code

`refuse()` exited **3** by this file's own local convention while `lib_gate.sh` and every bash gate use **2**. It became untenable when the stale-binary preflight landed *inside* the same harness and correctly exited 2: one tool spoke two refusal codes, and no caller could ask "did it refuse?" without knowing which refusal it hit. ⭐ The old convention was not silly — it wanted to distinguish *could not measure* from a red board — but **rc=1 already carries the red board**, so the third code bought nothing the law did not give and cost the one question every caller asks. ⛔ **A local convention that disagrees with a fleet law is a trap even when its reasoning is sound, because the reasoning lives in one file and the callers live everywhere.**

The one caller that pinned 3 (`test_gate_capture_stdin_and_red_exit.sh` arm 5) was re-pointed in the same push, and rewritten to assert the **property** — *"no oracle wired" must not read as "some stems were RED"*, which is a statement about rc=1 and did not change — rather than the number. An arm that pins a number has to be edited on every unification; an arm that pins the property does not.
