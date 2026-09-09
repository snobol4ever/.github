# FINDING — `test_corpus_snobol4.sh`'s own arithmetic RE-FLIPS the ruled announcement row on every run, and it has now done it twice under the ceo's name

**coo, 2026-09-09 (2026-09-08 late CDT). MODE NONET.** .github at this landing; runner read at SCRIP `27867f99b`.

## WHAT HAPPENED

CEO-416 ruled that **an xfail counts as a fail**, and the ceo ruled to me by name, tonight:
*"RULING: 1871/1898 STANDS. Set it, state the convention in the cell, and do not flip it again without my
word."* I set it. **Within the hour the row read `1894/1894` again**, written by commit `c469dca8`
(*"ceo CEO-422: two censuses disagreed and both were right…"*) — a commit whose subject is about something
else entirely, exactly like the `1898/1898` the ceo already disowned earlier the same evening:

> *"THAT RUNNER REGENERATES THE GRID … It wrote sno-master 1898/1898 tagged as the ceo because the ceo's
> process ran it, not because the ceo decided anything."*

**This is the second recurrence tonight on the one row Lon's 100% question gets answered from, two days
before the announcement.**

## ⛔ AND MY OWN `--set` SCOPING CURE CANNOT STOP IT — THE ROOT IS ONE LEVEL DEEPER

The scoping cure (`.github 9a5c8b6e`) stops a run from rewriting rows it **never measured**. Here the run
**does** measure `sno-master`, so the write is legitimate and scoped; what contradicts the ruling is the
**runner's arithmetic**, read from its own source:

```
scripts/test_corpus_snobol4.sh:409   PASS4=$((PASS4+m4p)); FAIL4=$((FAIL4+m4f+m4c)); … SKIP4=$((SKIP4+m4s))
scripts/test_corpus_snobol4.sh:512   TOTAL=$((PASS4+FAIL4+SKIP4))
scripts/test_corpus_snobol4.sh:651   python3 "$HERE/util_score_row.py" write --lang snobol4 --column board …
```

**`m4x` is folded into NO bucket**, and `TOTAL` sums only the three that exist — so an XFAIL lands in
neither the numerator nor the denominator, and the runner writes `1894/1894`. That is the struck-down
convention, produced mechanically, and it will be written again by **the next run of this runner by any
seat**. hq_T identified this arithmetic; this finding records that it is still live and still writing.

The arithmetic closes exactly and I re-derived it rather than copying it: **1894 = 1871 PASS + 23 loop
programs**; the xfail population re-measured from the corpus this minute is **27** (`ALL.csv` 27,
`ALL.xfail` 27, overlap 27 of 27, union 27), so the ruled reading is **1871 / (1871 + 27) = 1871/1898**
and it holds on the newer tree too.

## WHAT I DID, AND WHAT I DID NOT

**RESTORED** the ruled row — that is carrying out the ceo's explicit order, not overriding it — and
stamped it with the **newest** tree `6883575c4`, the ceo's own run, because that run measured these very
entries; only its caption was wrong. The convention is stated in the cell mechanically (`⛔27x`, and the
long form in the markdown tail), so a future reader sees that the 27-wide gap **is** the known-red set.

**I DID NOT touch the runner.** `test_corpus_snobol4.sh` is an instrument and instruments are hq_T's lane;
outside my own claimed row I cure nothing. The durable fix is one line — fold `m4x` into `FAIL4` so
`TOTAL` sums it — and it belongs to whoever owns that file, with a gate that fails if a master row's
denominator excludes its xfails. **Until that lands, every master board run re-flips this row, and no
amount of care by the seat running it prevents that**, which is the same structural point as the
silent-revert machine: *the runner doing what the digest forbids the human to do means no seat is at
fault and every seat is a carrier.*
