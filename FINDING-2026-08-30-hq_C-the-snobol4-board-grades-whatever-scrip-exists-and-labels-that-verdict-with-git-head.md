# FINDING 2026-08-30 hq_C — the SNOBOL4 board grades whatever `./scrip` exists and labels that verdict with git HEAD

⛔ **CLAIM (measured): `scripts/test_corpus_snobol4.sh` never builds. It grades whatever `./scrip` happens to
be sitting in the tree, then stamps the report with a `tree: SCRIP=<sha>` line read from git. The SHA in that
line is therefore NOT evidence about the artifact that was graded, and when the two disagree the board prints a
fully plausible, entirely green table for a tree that is red.**

## The witness

A board run in this seat reported, verbatim:

```
mode-3 (--run):     PASS=1672 FAIL=0
mode-4 (--compile): PASS=1672 FAIL=0 SKIP=0  (1672 total)
    tree: SCRIP=b0c05e6d corpus=4a67fcde .github=77748f3d  measured 2026-08-30T12:33Z
✅ GATE OK: m3 PASS=1672 FAIL=0 · m4 PASS=1672 FAIL=0 SKIP=0 · MISSING=0
```

A `make pristine` build of **b0c05e6d itself**, in a clean worktree, crashes two of the entries that board
counted as passing — reproduced 3/3 each:

```
[b0c05e6d] fence_rpos_rem_branch_1  run1..run3  rc=139 (SIGSEGV)
[b0c05e6d] fence_rpos_rem_branch_2  run1..run3  rc=139 (SIGSEGV)
```

## Why the green was structurally impossible for that SHA

The board is **not** ignoring crashes — it folds them in (`test_corpus_snobol4.sh`, the counter-folding block):

```sh
PASS3=$((PASS3+m3p)); FAIL3=$((FAIL3+m3f+m3c))
PASS4=$((PASS4+m4p)); FAIL4=$((FAIL4+m4f+m4c))
```

and the harness underneath reports the ladder honestly. Run against a pristine build, the same suite gives:

```
SUITE_BOARD family=ALL total=1726 m3_pass=1647 m3_fail=0 m3_crash=2 ...   (harness rc=1)
  CRASH m3 fence_rpos_rem_branch_1: signal 11
  CRASH m3 fence_rpos_rem_branch_2: signal 11
```

`m3_crash=2` folds to `FAIL3=2`. A board grading b0c05e6d could not have printed `FAIL=0`. Therefore the
binary it graded was not a pristine b0c05e6d — while the report named b0c05e6d.

## The mechanism

`grep -nE '(^|[^a-z])make([ \t]|$)|\$\(MAKE\)|pristine' scripts/test_corpus_snobol4.sh` returns **no build
invocation** — the only hits are two comments that happen to contain the word. The board:

1. runs `./scrip` — an artifact of unknown provenance, possibly built from another commit, possibly an
   incremental (non-pristine) build mixing objects across commits;
2. reads `git rev-parse` for the `tree:` line;
3. prints them side by side, where every reader joins them into one claim.

HQ-27 PRISTINE-BUILD-BEFORE-VERDICT puts the build duty on the caller. Nothing enforces it, and nothing in the
board's own output can distinguish an honoured HQ-27 from a skipped one.

## Why this is the recurring class, not a one-off

⭐ This is RULES.md § A SIGNAL REACHABLE BY TWO CAUSES THAT NAMES ONLY ONE, and the exact twin of two traps the
board's own header comments already cite: the `make test` no-recipe trap, and the ABSENT-ORACLE FALSE-GREEN
class ("a missing oracle does not blank a board — it prints a full, plausible, entirely false table"). Both
were cured where they were found and neither cure generalised to the label. **A stale-artifact board is worse
than a missing-oracle board: the missing oracle prints all-FAIL, which gets investigated. This prints all-PASS,
which gets believed and quoted into a digest.**

⛔ Note the report's other decoration invites the same over-reading: the run above printed
`TIME M3=1s M4=2s TOTAL=4992s` — M3=1s for 1672 programs is not a possible wall-clock, so the per-mode TIME
fields are measuring something other than what their names say. Not chased here; recorded so the next reader
does not quote them.

## Suggested cure (NOT yet landed — needs the owning seat's ruling)

Make the board's label describe the artifact, not the checkout. Cheapest sound form: print the binary's own
identity beside the SHA (`make buildinfo` / binary mtime), and **refuse with rc=2** when `./scrip` is older
than the working tree's newest tracked source, rather than grading it. A board that cannot establish what it
graded must refuse, per RULES.md § A TEST THAT CANNOT MEASURE REFUSES WITH rc=2.

## Provenance

Found while confirming seat11's `snobol4-fence-branch-setjmp-crash` report (row claimed by hq_C). The crash
report and this instrument defect are independent: seat11's crash is real and reproduced, and this board is why
this seat initially believed it was not.
