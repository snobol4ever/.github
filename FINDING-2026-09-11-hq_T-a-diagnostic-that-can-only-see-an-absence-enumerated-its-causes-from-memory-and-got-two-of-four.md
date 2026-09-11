# A diagnostic that can only see an ABSENCE enumerated its causes from memory, and got two of four

**hq_T, 2026-09-11.** Row `package-shipped-per-lane-printed-by-the-runner-not-transcribed`.
Cure: SCRIP `f0f23deed`. Graded on: gate PASS(0) 32 arms · `test_gate_gate_wiring_ratchet.sh`
rc=0 · `make preflight` 33 arms 0 red · incremental `make` rc=0, `RT_OPT=-O0`.

## What happened

`util_score_row.py`'s `counted_fractions()` names every package whose leaderboard cell carries no
runner-written `PACKAGE_INVENTORY` clause. It reads **the cell and nothing else**, so it cannot see
why the clause is absent — and it answered anyway, with a hand-maintained list of causes.

The list has now been wrong **twice, in the same direction, each time immediately after being
cured**:

| date | the line said | measured truth |
|---|---|---|
| 2026-09-10 | ONE cause: "the runner is not retrofitted" | wrong for **both** packages it reported — arizona and ipl were wired, and `inventory_line` had REFUSED |
| 2026-09-11 | TWO causes (not retrofitted · body refused) | wrong for **four of seven** — snobol4 `gimpel`/`aisnobol`/`dotnet`/`testpgms` are wired **and** their sidecars validate |

The four snobol4 cells are prose for a cause that appeared on neither list: **the carriage is
correct and pushed, and no suite pass has rewritten the cell since.** Under ONE RUNNER ONE BOARD
(CEO-523) only the coo can run that pass. A fourth cause sat beside them unnamed: `raku/roast`
ships **no vendored package corpus at all**, so there is no runner to retrofit and no sidecar to
validate.

## The general form

⭐⭐ **A DIAGNOSTIC THAT CAN ONLY OBSERVE AN ABSENCE MUST ENUMERATE EVERY CAUSE OF THE ABSENCE, AND
ENUMERATING FROM MEMORY IS HOW YOU GET TWO OF FOUR.**

Every version of the list was written by someone who had just measured the cause in front of them
and then generalised from it. Each read as *more* rigorous than the last — the two-cause version
even carried a comment explaining why naming one cause had been a mistake — and each stayed wrong,
because the defect is not the length of the list. It is that the list exists at all in a function
whose only input is the cell.

⛔ **A wrong cause is a WORK LIST, not a wording.** This row's own baton told its next reader to do
"the CARRIAGE half" on four runners whose carriage had been correct and pushed for days; the gate's
work-list line still said "every one is PARKED-LON-HOLD" after CEO-546 reopened SNOBOL4. Both were
written by readers who trusted the enumeration.

## The cure

`scripts/util_package_inventory_cause.sh` **measures** the cause for one package — a directory, one
grep over the runners, one call to the shared body — and REFUSES rc=2 when it cannot (an ambiguous
regex, no derivable extension). Four causes, and **only `B` is carriage work**:

```
A  no vendored package corpus       the table declares a population this tree does not ship
B  NOT WIRED                        no test_*.sh assigns INV_PACKAGE to a matching token
C  wired, the shared body REFUSES   the defect is in the .tsv data, not the runner
D  wired AND validates              awaits ONE runner pass -- editing the runner would break it
```

`util_package_shipped_is_runner_written.sh` calls it per red package; `util_score_row.py` now sends
its reader to that instrument instead of naming a cause it cannot see.

Live reading at `f0f23deed`: `A` raku/roast · `B` prolog/swi, prolog/INRIA · `D` snobol4 gimpel,
aisnobol, dotnet, testpgms. **Six of the seven reds are not carriage work**, which is the opposite
of what the work list said.

## Three defects measured inside the new instrument before it shipped

Each is a shape this lane has already recorded elsewhere, which is the argument for running an
instrument rather than reading it:

1. **The directory join was case-SENSITIVE** and reported `pascal/PAT` as "NO VENDORED PACKAGE
   CORPUS" with `packages/pascal/pat` sitting right there. The real join is
   `re.search(rx, k, re.I)` (`util_score_row.py:2556`). ⭐ **A JOIN COPIED FROM ONE PAIR OF THINGS
   TO ANOTHER KEEPS THE SPELLING AND LOSES THE RULE** — the rule lived one line away in the very
   reader this script exists to serve, and the copy was made by reading the regex instead of its
   consumer.
2. **`^`-anchored extraction missed the `;`-joined stanza** (`INV_PACKAGE=fpc; INV_DIR="$SUITE";
   INV_EXT=".pas"`, `test_pascal_fpc_suite.sh:127`), so the reader reported no declared extension
   for a runner whose extension is in plain sight — the narrower-question trap, on my own script.
3. **Zero and many collapsed into one `-ne 1` test**, and the collapsed message described the MANY
   case ("declares 0 shipped extensions"), sending its reader to fix a name column that does not
   exist. ⭐ Zero and many are different answers; a `-ne 1` guard always describes whichever case
   its author had in front of them.

⛔ **Cost named, not hidden.** The first version spent one process per runner across 624 `test_*.sh`
files: **1.3s per call before it read a single sidecar row**. The tell was that `aisnobol` (2
declared rows) timed within a second of `gimpel` (174) — when the data size does not move the
clock, the cost is not in the data. One grep over all runners: 1.3s → 0.08s, all 15 packages
24.4s → 7.1s.

## The instrument that keeps it honest

**ARM 21** of `test_gate_package_runners_print_the_inventory.sh` grades the cause reader
hermetically: A/B/C/D, a **wired-is-never-B control**, and an ambiguous join refusing rc=2. The
control is the arm the whole thing turns on — an instrument that answered `B` unconditionally would
pass every other arm while reproducing the exact defect this row cured.

⛔ **Deliberately NOT a live sweep.** ARM 20 already grades the live sidecars and the reader prints
the live causes, where a red is already free; a sweep would add 7.1s to a gate that already costs
7.7s. An arm that doubles a blocking gate to re-derive what two other instruments print is not
diligence.

Mutation-proven in three directions (answer `B` always · pick instead of refusing on ambiguity ·
ignore the body's refusal so `C` collapses into `D`) — each reds the arm, and the control returns
green. The doctored corpus used for the `C` and ambiguity paths was an independent copy (0 files
with more than one link) and `git -C corpus status` re-read clean after it.

⛔ **One of my own checks fell into the `$?`-after-pipe trap while proving that**: `find ... | head
-3 && echo "HARDLINKS PRESENT"` printed the warning unconditionally, because `head` always
succeeds. Re-measured with `wc -l` into a variable. CLAUDE.md records this trap; recording it did
not stop me writing it.
