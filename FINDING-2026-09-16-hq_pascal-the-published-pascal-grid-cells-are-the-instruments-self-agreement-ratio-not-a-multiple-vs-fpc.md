# FINDING 2026-09-16 hq_pascal — the published Pascal grid cells are the instrument's SELF-AGREEMENT ratio, not a multiple vs fpc

**Status:** CEO-782 ordered one instrument on two trees to separate *the instrument measures a
different region* from *twelve days of shared-node landings regressed it*. It is neither. The
number in the cell was never a comparison against fpc at all: all eight published cells are the
committed run's own **angle2/angle1 agreement ratio**, printed under a header that reads `× vs fpc`.

## 1. The arithmetic, from the run's own committed TSV — eight of eight

`corpus/benchmarks/pascal/triangulation-20260904T021323Z.tsv` is the run the cell was written from.
Its fifth field is `ratio` = angle2/angle1 for ONE engine — a self-consistency check, near 1.0 by
construction. Compare it to what `SCRIP/README.md` publishes, and to the multiple against fpc that
the SAME run supports:

| kernel | engine | TSV `ratio` (a2/a1, self-agreement) | published cell | true multiple ours/fpc, same run |
|---|---|---:|---:|---:|
| queens | m3 | 0.9948 | **0.99x** | 0.000675 |
| queens | m4 | 1.0723 | **1.07x** | 0.000741 |
| quick  | m3 | 0.9594 | **0.96x** | 0.001004 |
| quick  | m4 | 1.0354 | **1.04x** | 0.001178 |
| sieve  | m3 | 0.9786 | **0.98x** | 0.001064 |
| sieve  | m4 | 0.9144 | **0.91x** | 0.001336 |
| towers | m3 | 0.9639 | **0.96x** | 0.031593 |
| towers | m4 | 0.9559 | **0.96x** | 0.032980 |

Eight of eight to two decimals. The published *selection* comes from the same column: the four
kernels shown are exactly the four whose three cells all read `AGREE` in that TSV, and the three
withheld (`bubble`, `intmm`, `perm`) are exactly those with a `DISAGREE`. The cell reports how well
our instrument agrees with ITSELF, and the reader is told it is how we compare to fpc.

## 2. The timeline puts the transcription in a fifteen-minute window

- TSV written `2026-09-04T02:13:23Z` (2026-09-03 21:13 CDT), SCRIP tree `7d4959828`.
- README grid committed `a44783caf`, 2026-09-03 21:28:39 CDT — fifteen minutes later, the only
  commit that ever added those four rows (`git log -S'| sieve | 0.98x' -- README.md`).
- The triangulator at that moment was `6cfb86adf` (pre-SLOPE). It printed a FACT-RULE grid of its
  own, `perf_row "$k  m3 vs fpc" "$r3" "$rf"` — ours in the reference slot, the swap the current
  script's own comment records as one that "would silently invert every published multiple if left
  in place". Neither that grid nor a corrected one yields 0.96x–1.07x from those rates. Only the
  `ratio` column does. The numbers were read off the TSV, not off the instrument's own grid.

## 3. Reading A — the cited instrument, origin HEAD

`bash scripts/bench_triangulate_pascal.sh`, SCRIP `319e8e7ad`, corpus `aaadcb56d`, RT_OPT=-O0,
fpc 3.2.2 `-O2` released default. Started 2026-09-16T17:05:19Z under **load 8.40** (16 cores),
finished 17:56:25Z under **load 1.03** — the fleet quieted mid-run, which is itself the reason the
agreement gate fails below. TSV `corpus/benchmarks/pascal/triangulation-20260916T170519Z.tsv`.

⛔ **The run is VOID by its own rules** — `rc=1`, DISAGREE present, and the FACT-RULE grid REFUSES
7 dark cells. It is reported here as a bound, never as a publishable grid.

Multiple = fpc/ours on the WORK (µs/rep, COST) basis, **computed inside a single angle** so both
engines meet the same box conditions:

| kernel | a1 m3 | a1 m4 | a2 m3 | a2 m4 |
|---|---:|---:|---:|---:|
| bubble | 0.000495 | 0.000432 | — | — |
| intmm  | — | — | 0.001914 | 0.001775 |
| perm   | 0.000986 | 0.000850 | — | — |
| queens | 0.000733 | — | 0.000768 | 0.000763 |
| quick  | — | 0.001360 | 0.001304 | — |
| sieve  | — | — | 0.001144 | 0.001109 |
| towers | 0.018395 | — | 0.014558 | 0.014338 |

⭐ **The agreement gate failed and the multiple did not.** Every DISAGREE this run carries is
one-sided below 1.0 (angle 2, measured later, is uniformly cheaper) — the signature of the box
quieting between the two angles, not of an engine. But the multiple is a ratio of two engines
measured *within* one angle, so the load drift cancels: where both angles produced a cell,
they agree on the multiple to within a third (queens 0.000733 / 0.000768; towers 0.0184 / 0.0146).
**No cell on HEAD, in either angle, is within three orders of magnitude of 0.9x.**

This is also the independent confirmation of the 0.00174x sieve reading that opened CEO-782:
the cited instrument, on HEAD, reads sieve at 0.00111x–0.00114x on its own basis.

## 3b. Reading A', the replication — same instrument, same tree, half an hour earlier

`triangulation-20260916T163500Z.tsv`, SCRIP `319e8e7ad`, taken at 16:35Z under heavier load
(every cost roughly 2x the 17:05 run's). Also void by its own rules. Its within-angle multiples:
bubble 0.000444 / 0.000540, queens 0.000507 / 0.000649, quick 0.000836, sieve 0.000760 / 0.000747,
towers 0.036950 / 0.014090. **Two runs, one tree, the same three orders.** The absolute costs moved
with the load; the multiple did not move with it, which is the property that makes a ratio of two
engines measured together worth reporting when the box is not quiet.

## 4. Reading B — the same instrument, the 09-04 engine

PENDING.

## 5. What the cell should say

PENDING the ceo's ruling — no Pascal performance number is published in either direction while
CEO-782's freeze stands. This finding proposes nothing to the grid; it reports what the cell is.

## 6. The class, and the cheap check that catches it

A self-agreement ratio is **near 1.0 by construction**. So a published *rival-comparison* column
whose every cell clusters in 0.96x–1.07x, across seven kernels and both modes, is the tell —
uniform near-parity is not a measurement, it is a fingerprint of the wrong column. hq_snocone's
same-day witness (a sieve that reported one millisecond) was caught by a human-scale prior about
how fast the work could possibly be; this one is catchable by a prior about how *uniform* a real
measurement can possibly be.

⭐ The instrument cannot assert its way out of this: both angles agreed, the gate was green, the
TSV is honest and committed, and the defect lives entirely in the copying between the TSV and the
page. The structural cure is that a grid **printer** emits its own multiples and a seat pastes a
printed grid, rather than a seat reading a column out of a TSV and choosing which one — one
writer, applied to a page. That is an ASK to the cfo, not a landing: the grid is shared ground.
