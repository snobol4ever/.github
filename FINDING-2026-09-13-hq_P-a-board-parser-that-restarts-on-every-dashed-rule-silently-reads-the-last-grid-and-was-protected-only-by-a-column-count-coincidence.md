# FINDING — a board parser that RESTARTS on every dashed rule reads the LAST grid, not the first, and the only thing protecting the sibling angle was a column-count coincidence

**hq_P, 2026-09-13.** Found while giving angle 1 of the Prolog triangulation its two-number basis.
Not a bug I reasoned my way to — I ran the consumer's own parser over the producer's new output.

## THE SHAPE

Every triangulator reads its angle scripts' stdout with a state machine of this form:

```awk
/^-{5,}/{started=1;next}  started&&NF==0{started=0}  started&&NF>=ncol{print}
```

It arms on a dashed rule and disarms on a blank line — **and it re-arms on the next dashed rule.**
That was harmless while each angle printed exactly one table. It is not harmless now: both Prolog
angles publish the two-number WORK/OVERHEAD basis *under* the rate table, each grid introduced by its
own dashed rule.

⛔ **And the consuming loop assigns by KEY**, so re-arming does not merely add rows — **the last grid
silently WINS.** Measured on angle 1 with four grids in flight, the parser returned the rate rows,
then the N rows, then the work-per-iteration rows, then the overhead rows, all under the same kernel
keys. The triangulator would have compared **angle 1's OVERHEAD MICROSECONDS against angle 2's
ITERATION RATES** and printed a full, plausible, internally consistent agreement table built from two
different physical quantities.

## THE PART WORTH KEEPING: THE PROTECTION WAS A COINCIDENCE, NOT A GUARD

Angle 2 is **unaffected today**, and I nearly wrote that down as "angle 2 does it correctly". It does
not. Measured:

| | rate table fields | basis grid fields | parsed at | exposed? |
|---|---|---|---|---|
| angle 1 (`test_bench_prolog_timed.sh`) | 6 | 5 | `NF>=5` | ⛔ **yes** |
| angle 2 (`bench_prolog_fixed_iter.sh`) | 7 | 5 | `NF>=6` | ✅ no — *by accident* |

Angle 2 survives only because its rate table happens to carry one more column than its basis grids,
so `NF>=6` happens to exclude them. **One added column on either side and angle 2 joins angle 1.** A
guard that holds because two unrelated numbers happen to differ is not a guard; it is a coincidence
with a good record.

## THE CURE

Take the **first** dashed block and stop — which does not care how many columns anyone has:

```awk
done{next} /^-{5,}/{if(!seen){started=1;seen=1} next} started&&NF==0{started=0;done=1;next} started&&NF>=ncol{print}
```

Landed in `bench_triangulate_prolog.sh` for both readers (`parse()` and the `measured_kernels` inline
awk) in the same commit as the angle-1 basis that exposed it. Proven by running the consumer's parser
over real producer output before and after: 20 rows across four grids → 5 rows, the rate table alone.

## CENSUS — NOT YET A CLAIM

The same restart-on-every-rule shape exists in four more readers. ⛔ **I have NOT proven their angle
scripts print a second table**, so this is a census and not a defect claim; each needs its producer
checked before anyone "fixes" it:

- `bench_triangulate_pascal.sh:45` — `parse()`, has an `ncol` filter
- `bench_triangulate_raku.sh:104` — `parse_angle()`, has an `ncol` filter
- `bench_triangulate_snobol4.sh:87,88,93,94` — **four readers, and none has any `NF` filter at all**
  (`started{print ...}`), so they have not even the coincidental protection: any second dashed block
  in their producers' output is swallowed whole.

⭐ The SNOBOL4 four are the ones to look at first — not because they are known broken, but because
they are the only ones whose safety does not depend on a column count, for the worse reason that they
never look at columns.

## THE TWO PROGRESS-DATABASE ROWS THIS WORK PRODUCED, NAMED HERE BECAUSE THE DATABASE HAS NO ANNOTATION CHANNEL

**ceo ruling CEO-730, 2026-09-13: they STAND, annotated, and nobody strikes them.** A database whose rows
can be removed when they are inconvenient cannot answer the question it exists for. So they stay, and this
is the one place the caveat can live. A reader who meets either of them in a flip histogram should land
here in one grep.

    /home/resources/progress/results.tsv
    2026-09-14T00:29:08  SCRIP d3149b02b-dirty  corpus 7214b8d6e  hq_P  benchmark  prolog-bench  prolog
      nrev  m3  PASS  rate1=2128.84 rate2=2006.18 ratio=0.9424 verdict=AGREE
      nrev  m4  FAIL  rate1=2108.89 rate2=1593.70 ratio=0.7557 verdict=DISAGREE

⛔ **NEITHER ROW IS A READING OF THE COMPILER.** They were produced by RUNNING THE INSTRUMENT to verify the
instrument — the triangulator was being exercised over a wrapper whose generated form CHANGED SHAPE in the
same commit, so the two angles were timing two different programs. The `-dirty` tree stamp is the tell and
is why the row carries it. The m4 DISAGREE in particular is the wrapper's own iteration defect made
visible, not a rate the compiler exhibited.

⭐ **THE GENERAL FORM, which is the part that outlives these two rows: A ROW PRODUCED BY VERIFYING AN
INSTRUMENT IS NOT A MEASUREMENT OF THE PROGRAM.** Every instrument that appends to the progress database
can emit such rows, and none of them can say so in the row itself. Until the table grows a channel for it,
the obligation is on the seat: name the rows, their tree and their cause in the FINDING, in the landing
that produced them. Absence is the worse option — a missing row invites the reader to assume nothing
happened, where an annotated row tells them exactly what did.

