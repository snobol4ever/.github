# The sanctioned add-a-witness path refuses on FIVE of SEVEN masters, and the cause is cosmetic — which is why it went eight days unnamed

**cfo, 2026-09-13. Tree SCRIP `fbb1db6ef`, corpus `d44a95ca0` at measurement (fix landed at corpus `a401e1e3e`),
`RT_OPT=-O0`, MODE NONET. Found while minting rung22 of
`snobol4-ladder-every-feature-in-isolation-with-variations`: the mint could not begin.**

## THE OUTAGE

`scripts/util_add_ladder_witness.py` — the ONE sanctioned path for adding a witness to a master suite, which exists
because three prior sessions on a task hit the wall of there being none — **refuses rc=2** with
`round-trip proof failed: this language's reader+writer pair does not reproduce the existing master byte-for-byte`.

Measured over all seven masters by running the tool's own proof standalone (`read_suite`/`write_suite` for the mixed
SNOBOL4 shape, `read_block_suite`/`write_block_suite` for the block shape, exactly as the tool chooses them):

| master | round-trip |
|---|---|
| snobol4 | **STALE** |
| icon | **STALE** |
| prolog | **STALE** |
| rebus | **STALE** |
| pascal | **STALE** |
| raku | OK |
| snocone | OK |

## THE CAUSE, AND IT IS ONE LINE OF ARITHMETIC

The writer re-derives each entry's banner number from its **position**. `corpus a6646f04c` removed the 620
`modes=ast` entries from all seven masters on Lon's word and did not renumber, so the printed numbers drifted from
the positions. In the SNOBOL4 master **1111 banner lines were stale** — off by **14** from entry 847 and by **28**
from about 1868, i.e. two removals of fourteen. Nothing the grader reads was wrong; the reader **ignores** the
printed number and re-derives `seq` positionally, which is exactly why the masters kept grading perfectly and the
only visible symptom was a tool refusing to run.

⭐ **The invariant was already written down, in the file that broke on it.** `util_add_ladder_witness.py`'s own
comment says the banner's seq is the entry's POSITION, not its rank, and that *"an entry whose seq is its rank makes
the master fail this tool's OWN round-trip proof on the very next invocation"* — and it names `a6646f04c` as the
commit that separated rank from position. **The prediction was correct, it was written before the fact, and it still
went unnoticed for eight days, because the thing it predicts is a refusal in a tool nobody runs daily.**

## THE PROOF THAT A RENUMBER IS SAFE, CUT BEFORE ANYTHING WAS WRITTEN

Parse the master, re-serialise, re-parse, and compare **every field the grader reads** over all 1957 entries — kind,
name, sno_lines, ref, stdin, xfail, argv, mask, want_rc, xfail_reason: **zero differences**. Every changed line in
either file is a banner line, and **no banner name moved**. `util_build_master_suite.py`'s own header says the same
in words: the grader reads name, body, ref, stdin, xfail, reason, want_rc and **IGNORES seq and file order**.

Landed for SNOBOL4 only, at corpus `a401e1e3e`, with that proof in the commit body; the thirteen rung22 witnesses
then minted through the tool with no further refusal. **Icon, prolog, rebus and pascal are other lanes and were left
alone** — a 1000-line cosmetic diff landing under another seat's feet is worse than a refusal they can read. hq_T
has the census.

## THE SECOND-ORDER FINDING, WHICH IS THE ONE I WOULD FIX FIRST

While chasing why my ladder run wrote no SCORE row, I found the same disease one layer up: `util_score_row.py`
**correctly** refuses a non-coo seat under ONE RUNNER ONE BOARD, printing `⚠ SCORE.md NOT UPDATED — seat cfo is not
coo, THE ONE RUNNER` — and `lib_ladder.sh` pipes that output through `grep -E '^SCORE.md|ROW SKIPPED|^  now:'`, which
the warning-sign-prefixed line matches **none of**. The seat sees **nothing at all**: no SCORE line, no UNWRITTEN
line, rc=0, green verdict. It took `bash -x` to see the refusal. **A guard that works and is invisible reads exactly
like a write that happened**, and the failure mode is a seat believing the leaderboard carries their number.

⛔ And its mirror: `util_score_row.py write --dry-run --measurer cfo` prints `WOULD REWRITE grid L for snobol4` on the
same tree where the real write refuses for identity. **A dry run should answer the same question the real path
answers, identity included** — it is the thing a seat uses to check a cell *before* landing it.

Both are reported to hq_T rather than touched: the first is the ONE RUNNER guard doing its job, and I am not the
runner.

## THE SHAPE COMMON TO ALL THREE

A correct mechanism whose **only** observable is a refusal nobody reads: a renumber invariant asserted in a comment,
a guard whose message is filtered out by its caller, a dry run that does not dry-run the check that matters. None of
them is a wrong answer. Each of them costs the next seat a measurement to rediscover — I spent four on the second one.
