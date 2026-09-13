# FINDING 2026-09-13 hq_T — removing entries from seven masters disabled the sanctioned add-a-witness path for five languages, and every gate stayed green

**Tree:** SCRIP a41070abc+ · corpus e874175bd+ · RT_OPT=-O0 · incremental `make`
**Found while:** opening Raku ladder rung 16 (row `raku-relational-operators-yield-1-0-not-bool`, CEO-670 —
open a rung rather than curing in place). The rung could not be minted: the tool refused.

## What happened

`util_add_ladder_witness.py` — THE sanctioned add-a-witness path, and the only one — refuses rc=2 with:

    ⛔ REFUSED: round-trip proof failed: this language's reader+writer pair does not reproduce the
    existing master byte-for-byte -- refusing to trust this tool with a real write

That refusal is the tool working. It runs a round-trip proof (read the master, re-serialize it, diff) before
it will write, precisely so it never corrupts a master it has misunderstood. **The proof was failing for five
of the six block-suite masters**, measured with the harness's own reader and writer:

| master | entries | round-trip |
|---|---|---|
| icon | 826 | MISMATCH → add-a-witness REFUSES |
| pascal | 246 | MISMATCH → add-a-witness REFUSES |
| prolog | 563 | MISMATCH → add-a-witness REFUSES |
| raku | 897 | MISMATCH → add-a-witness REFUSES |
| rebus | 43 | MISMATCH → add-a-witness REFUSES |
| snocone | 325 | OK |

Five of the seven languages could not mint a ladder witness at all. Under MODE NONET that is five of the
per-language **ladder seats** — the named standing duty of hq_T, hq_I, hq_S, the cto, the coo and the ceo.

## The cause, proven by bisection rather than inferred

`read_block_suite()` **ignores the number printed in each banner** and re-derives `seq` positionally
(`seq += 1`); `write_block_suite()` writes `e.seq` back out. So **"banner number == position" is an invariant
of every file the reader has touched** — not a convention, a consequence.

corpus `a6646f04c` ("tests: remove the 620 modes=ast entries from all seven masters on Lon's word") deleted
entries without renumbering the surviving banners, leaving holes. Measured at that commit and its parent:

    before (a6646f04c~1)  entries=1034  round-trip OK
    after  (a6646f04c)    entries=897   round-trip MISMATCH

⭐ The diff is **only** the banner integer. Across all five masters, in both `ALL.<ext>` and `ALL.ref`: line
counts identical, and **zero** differing lines that are not a banner, and zero banner pairs differing in
anything but the index. Nothing about any program, any ref, or any grading changed.

## A second defect, in the tool itself, behind the first

With raku's master renumbered the tool wrote one witness and then **refused on its own output**. It constructed
the new entry as `csh.Entry("block", rank, ...)` — the entry's **CSV rank** where the banner wants its
**position** (1035 vs 898). So the tool could only ever append ONE witness before poisoning the master against
its own next invocation.

⭐⭐ **Both defects are the same shape: two numbers that had always been equal, silently separated.** Rank and
position coincided in every master from the day they were built until `a6646f04c` removed 620 entries from the
middle. Nothing was wrong with the code that assumed it; the assumption simply stopped being true, in a commit
that touched neither instrument. **A tool that reads a population it does not own has an invariant it never
declared, and the landing that breaks it is somewhere else entirely.**

## Why every instrument stayed green

Nothing regressed. Every ladder runner, every gate, every board reads the master **by entry name** — the banner
number is display only, so a holey sequence grades exactly like a contiguous one. `test_raku_ladder.sh` read
154/154 FAIL=0 across the whole break. The only instrument that could see it was the one that refuses to run,
and it reports as a REFUSAL (rc=2), not a red — which is correct, and is also why it reads as "the tool is
broken" rather than "the corpus moved".

⭐ This is `FINDING-2026-09-12-hq_T-moving-a-population-blinds-every-instrument-that-derives-it-and-the-gate-stays-green.md`
recurring on a different population, and the lesson there did not prevent it: that FINDING says to sweep every
instrument that DERIVES a population you move. **`a6646f04c` moved a population in seven masters at once, and
the instrument it blinded was the one that writes to them.**

## What landed here

- **raku only** (hq_T's lane): master renumbered through the harness's own writer, proven banner-only —
  0 non-banner diff lines in `ALL.raku` and `ALL.ref`. Round-trip now OK.
- `util_add_ladder_witness.py`: the new entry's banner seq is `len(entries) + 1`, not `rank`. Proven by minting
  four further witnesses in succession — each one is a round-trip proof of the write before it.
- Raku ladder rung 16 `bool_relops` opened and green, 10/10 both modes; full ladder 0..16 PASS 164/164.

## What is NOT mine to land, and is an ASK

`icon` (ceo), `pascal` (coo), `prolog` (cto) and `rebus` (hq_S) are still broken and their ladder seats cannot
mint a witness. The cure is the same content-neutral renumber, one command per master, and I have measured all
four as banner-only. Under the NONET guardrail a master another concern owns is an ASK with the measurement,
never a landing — so it is routed to the ceo rather than done here.
