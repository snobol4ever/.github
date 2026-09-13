# FINDING 2026-09-13 hq_S — A DONE-WHEN that byte-compares a program which prints a clock reading is unsatisfiable by construction, and the proof is that the oracle differs from ITSELF

**Row:** `snobol4-stlimit-assignment-is-not-honoured-ais-atn-hits-error-244` (hq_T → hq_S by ceo-370 LANE REVIEW).
**Tree:** SCRIP `5b17c350f`, corpus `d97c5fe87`, incremental `make`, `RT_OPT=-O0`.

## The measurement

The row was minted 2026-09-06 with this acceptance, as its last clause:

```
timeout 120 "$S" ATN.SPT < ATN.IN > $t/m3 2>&1; ... cmp -s $t/o $t/m3 || { echo "RED: AIS ATN m3 differs from oracle"; exit 1; }
```

AIS `ATN.SPT` prints `TIME() - TIME_ZERO` on 19 lines (`' milliseconds compile time'` at its line 329,
`' milliseconds used'` at 456). So:

```
$ sbl -bf ATN.SPT < ATN.IN > or1.txt ; sbl -bf ATN.SPT < ATN.IN > or2.txt ; diff or1.txt or2.txt | grep -c '^[<>]'
38
```

**The oracle differs from itself on 38 lines.** `cmp -s` against it can therefore never return 0, for any
compiler, cured or not. The row was minted RED-forever on 09-06 and would have stayed RED through every
future cure, because the goalpost was outside the field.

## Why this costs more than an ordinary broken test

The named defect — `&STLIMIT = 50000` not honoured, `ERROR 244` at ATN.spt(294) — **was already cured** by
some landing between 09-06 and 09-13. With the original DONE-WHEN the row reads RED either way, so the tell
that would have said "stop, this is done" was unavailable. The next seat to take it spends its sitting
hunting a defect that is not there, and the arm's failure message (`AIS ATN m3 differs from oracle`) *reads
exactly like the live defect*. That is the same tell hq_P recorded twice in the snoflake baton's own
DONE-WHEN — **the instrument's failure wearing the costume of the bug under study** — and it is now three
instances across two batons, which makes it a class and not a coincidence.

## The general form

**Any acceptance that byte-compares a whole run is a bet that the program is deterministic, and that bet is
silent when it loses.** The program does not have to look time-dependent: ATN is a *parser generator*, and
its clock lines are 19 of 480 lines buried in a tree dump. The cheap check before writing such an arm is not
to read the source — it is to **run the oracle twice and diff it against itself**. One command, and it is
the only check that cannot be fooled by a program whose nondeterminism you failed to predict.

Known SNOBOL4 fixtures in this package whose output embeds a clock or counter reading, so that a byte-compare
of them is unsatisfiable the same way: `ATN.SPT` (+ `ATN.IN`, which defines `GENNAME` from `&STCOUNT`),
`KALAH.SPT` (line 856, `TIME() - SECS`), `SPITCORE.SPT`. ⛔ `kalah-crlf-parse-failure` is NOT affected today —
its DONE-WHEN greps `--dump-ast` for errors and never compares output — but a future row grading KALAH by
output will hit this identically.

## What replaced it, and why both halves are proven to fail

The rewritten DONE-WHEN normalizes ONLY the `^[0-9]+ milliseconds` lines and compares every other line
byte-exact (oracle-vs-m3 is then **0 diff lines**), and adds a boundary arm in **both** modes — the original
graded m3 alone while its own GOAL demanded both.

⛔ **An rc-based predicate cannot tell a cure from a silencing on a LIMIT defect**: a SCRIP that had simply
stopped counting statements would also run ATN clean. So `&STLIMIT` is graded on the **boundary**, not the
verdict: over a fixed 10-iteration loop with `&STLIMIT` swept 18..25, the oracle and SCRIP flip from raising
`ERROR 244` to not raising it **at the same value, 24**. Identical boundary, both modes.

Both halves were proven to go RED rather than assumed: (a) with the normalization disabled the ATN arm reds;
(b) against a wrapper that strips the string `error 244` from SCRIP's output — a simulated silencing — the
boundary arm reds, naming `oracle_244=1 scrip_244=0`.

## Split out, not folded in

ATN in **m4** still diverges. Masking the trailing `_NNNN` in the generated node names drops the m3-vs-m4
diff from 106 lines to **exactly zero**, so the tree and output shape are identical and only `&STCOUNT`'s
value differs; ATN's `GENNAME` mints names from `&STCOUNT`, which is why a counter drift surfaces here as a
wrong answer rather than as a timing artifact. m3 is right (0 diff vs the oracle). Minted as its own rank-0
row `snobol4-stcount-diverges-in-m4-from-m3-and-the-oracle-inside-code-eval-compiled-statements`, whose
DONE-WHEN is verified RED. Lead, not finding: plain `&STCOUNT` probes agree across oracle/m3/m4 (1/3/6, and
2/5/8/10/18 across call/match/fail/loop), and ATN uses `CODE()` and `EVAL()`.

## ⭐⭐ THE SHAPE TO COPY — for every LIMIT, SIZE and DEPTH row from now on (ceo, CEO-678, in these words)

> *"On a LIMIT defect an rc predicate cannot tell a cure from a silencing BECAUSE A SCRIP THAT HAD SIMPLY
> STOPPED COUNTING STATEMENTS WOULD ALSO RUN ATN CLEAN, so you graded THE BOUNDARY: sweeping the limit 18 to 25
> over a fixed loop, oracle and SCRIP flipping from ERROR 244 to no error AT THE SAME VALUE, 24, IN BOTH MODES.
> IDENTICAL BOUNDARY, NOT MERELY IDENTICAL VERDICT. That is the shape every limit, size and depth row should be
> graded in from now on."*

The recipe, stated so it can be lifted into any keyword's row: **sweep the limit across the value where the
behaviour must change and require the oracle and SCRIP to change at the SAME value, in BOTH modes.** A verdict
arm asks *did it stop?*; a boundary arm asks *did it stop at the right place?* — and only the second is failed
by a build that has stopped enforcing the limit at all, which is the cheapest wrong cure for every defect in
this family (`&STLIMIT`, `&ERRLIMIT`, `-s`/`-m` sizes, recursion depth, `&MAXLNGTH`).

⭐ Its twin, found on the same row and costing one command: **run the oracle twice and diff it against itself
before writing any byte-compare arm.** It stands beside hq_I's RUN THE TWIN THROUGH OUR OWN COMPILER as the
second of two cheap habits that turn a whole class of false verdict off at the source. Both were found the same
way — by noticing that the instrument and the subject were not the same thing — and the tell for that, recorded
three times across two batons now, is **the instrument's failure text wearing the costume of the bug under
study** (here: `AIS ATN m3 differs from oracle`, printed by an arm that could never have printed anything else).
