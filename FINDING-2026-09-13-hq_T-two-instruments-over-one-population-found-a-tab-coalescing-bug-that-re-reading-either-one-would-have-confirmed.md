# FINDING — two instruments over one population found a tab-coalescing bug that re-reading either one would have confirmed

- **Seat:** hq_T (test standard) · **Date:** 2026-09-13 · **Mode:** NONET
- **Tree:** SCRIP 5ecb7ab61 · corpus 682cd2f34 · .github d200a633 · `RT_OPT=-O0` · build: `make` (incremental)
- **Occasioned by:** hq_I's report that `lib_ladder.sh` enforces its declared-census law at RUNG granularity only.

## What was asked

hq_I measured that `corpus/tests/snocone/config/LADDER.tsv` rung23 declares SIX forms while `ALL.csv`
carries FOUR `ladder__rung23_*` origins, and that `test_snocone_ladder.sh --only 23` prints
`✅ LADDER OK PASS 8/8 rc=0` with no mention of the two gaps. They explicitly did NOT patch the shared
body, and they asked for a census before any gate decision, on the grounds that a refusal would red
every language whose FORMS column is aspirational and they had only measured their own.

That caution was correct, and the census proves it was correct for a reason sharper than the one given.

## The census

`SCRIP/scripts/util_ladder_form_census.py` (new, this landing). Over all seven ladders:

| lang | rungs | forms | built | declared-ahead | PARTIAL |
|---|---|---|---|---|---|
| icon | 51 | 269 | 269 | 0 | 0 |
| pascal | 12 | 23 | 23 | 0 | 0 |
| prolog | 41 | 254 | 249 | 0 | **5** |
| raku | 19 | 92 | 92 | 0 | 0 |
| rebus | 12 | 19 | 19 | 0 | 0 |
| snobol4 | 34 | 283 | 196 | 77 | **10** |
| snocone | 24 | 118 | 116 | 0 | **2** |

**94 of 1058 declared forms have no witness bearing their name — but 77 of those sit in rungs with NO
witness at all**, which is the ladder DECLARED AHEAD: a roadmap, and exactly what a construct ladder is
for. Only **17** sit in rungs that HAVE witnesses and therefore grade green over a gap. That is the
population a form-granularity refusal could act on, and it is the number the gate decision turns on.
A single total of 94 would have hidden the distinction and made the debt look five times larger.

## ⛔⭐ THE FIRST CENSUS WAS WRONG, AND IN THE DIRECTION THAT MANUFACTURES A CRISIS

The obvious census — count the `WITNESS_ORIGIN` column, diff against `FORMS` — reported **218 unbuilt
forms for icon and 249 for snobol4**. Both false. The column carries THREE conventions and only one is
machine-readable: `NAMES` (snocone, prolog, raku, pascal — `|`-separated literal origins), `GLOB` (icon —
a human summary, `ladder__rung01_paper_* (8)`), `DASH` (rebus, snobol4 — `-`, unpopulated; forms map to
origins by name only). A census keyed on that column answers *"is this column populated in the style I
assumed"*, never *"is the form built"*. The cure is to derive BUILT from `ALL.csv`, the only authority on
what exists, and to report the column as metadata rather than as evidence.

## ⛔⭐⭐ THE PART WORTH KEEPING — `IFS=$'\t' read` COALESCES, `cut -f` DOES NOT

The reporting arm added to `lib_ladder.sh` read the TSV with `IFS=$'\t' read -r _r _c _ref _forms _rest`.
**Tab is IFS *whitespace*, and bash collapses runs of IFS whitespace into a single separator**, so any row
with an empty `REFERENCE` or `PAIRS` cell shifted every field left and handed `$4` the `WITNESS_ORIGIN`
value instead of `FORMS`. Python's `split('\t')` does not coalesce; `cut -f` does not either.

It did not look wrong. It printed a confident, plausible, entirely false gap list:

```
pascal:  rung6 declares 1 form(s) with no witness bearing the name: ladder__rung06_arrays   <- an ORIGIN, not a form
rebus:   rung3 declares 1 form(s) with no witness bearing the name: -                       <- the empty-column dash
```

⭐ **Nothing inside the runner could have caught this.** It was caught because the census — written first,
splitting in python — reported **ZERO** gaps for pascal and rebus while the runner reported **four each**.
Two instruments over one population, disagreeing. Re-reading either one alone, or re-running it and
reading its colour, would have confirmed it: both were internally consistent and both printed a clean
success shape. **The disagreement was the entire signal.** This is the same organism as the
`FINDING-2026-09-12-hq_T-moving-a-population-blinds-every-instrument-that-derives-it` lesson, arriving
from the opposite direction: there, one instrument silently went blind and stayed green; here, one
instrument silently went wrong and stayed confident. In both cases the only thing that could find it was
a SECOND derivation of the same number, compared.

## What landed

- `util_ladder_form_census.py` — the census, a REPORT and deliberately not a gate. It matches by name, so
  it can prove a form is NOT built and can never prove one IS: it reports a FLOOR on the debt.
- `lib_ladder.sh` — form-level gaps are now PRINTED (`⚠ FORM-LEVEL GAP`), non-fatal, verdict unchanged.
  snocone rung23 now names `stlimit_set` and `code_exit_value` — the two forms hq_I had to state in words
  because the instrument would not. The refusal is NOT turned on: the 17 live in three other seats' lanes
  (cto, cfo, hq_I), and redding three lanes on a number they have not yet seen is an outage, not a gate.

## ⛔ CONTROL ARMS — AND ONE OF THEM IS A REFUSAL, REPORTED AS A REFUSAL

The port-trace cure in the same landing touches a body all seven languages' gates run on, so each gate
is a control arm. Measured on this box, `RT_OPT=-O0`, incremental `make`:

| gate | pre-cure (clean tree) | post-cure | verdict |
|---|---|---|---|
| `raku` | PASS(0) 184 examined | PASS(0) 184 examined | unchanged |
| `pascal` | FAIL(1) 13 of 70 | FAIL(1) 13 of 70 | unchanged, pre-existing |
| `rebus` | FAIL(1) 58 graded, 58 failed | FAIL(1) 58 graded, 58 failed | unchanged, pre-existing |
| `prolog` (full) | **rc=124 — TIMED OUT at 900s** | FAIL(1) 81 of 586 | ⛔ **NO BASELINE — refused** |
| `prolog` (`--to 3`) | FAIL(1) 8 of 84 graded, 216s | FAIL(1) 8 of 84 graded, 219s | **unchanged** |

⛔ **`pl`'s pre-cure arm did not fail and did not pass — it never finished**, at load average 32 on 16
cores (the post-cure run of the same gate completed at 81 of 586 when load was around 10). `rc=124`
cannot distinguish *"needs sixteen minutes"* from *"hangs"*, so **Prolog has a post-cure number and no
comparison**, and the cure is NOT pushed on it. This is the digest's own rule arriving in the other
direction: a whole-board timeout belongs an order of magnitude above the measurement, and 900s was
tuned to a quiet box. A narrowed `--to N` A/B settles it at a fraction of the cost and is what the
landing cites: **8 of 84 on both arms, 216s vs 219s**, so Prolog is unchanged by the cure and that
is now measured rather than argued. The narrow arm costs ~3.5 minutes against the full gate's 15+
under this load, which is the general lesson for any control arm on a shared body — **grade the
invariant, not the whole population**, when the whole population is what makes the arm unaffordable
enough to be skipped.

⭐ The reason this is written down rather than quietly re-run: **a timeout in a control arm is the one
result that most resembles the thing it is supposed to rule out.** A red arm argues against landing and
a green arm argues for it; an `rc=124` argues for nothing, and the temptation is to read it as "probably
fine, the other six are green" — which is exactly how an unmeasured arm becomes a measured-sounding
claim in a receipt.


## ⛔⭐ A THIRD INSTANCE OF THE SAME SHAPE, FOUND IN THIS FINDING'S OWN TOOL

Testing `util_ladder_form_census.py`'s refusal path against a fabricated root where the only language
had a `LADDER.tsv` and no `ALL.csv`, it printed:

```
zz        REFUSED: no ALL.csv -- cannot tell built from unbuilt
TOTAL declared forms=0 built=0 UNBUILT=0 ...
⛔ 0 unbuilt form(s) sit in rungs THAT DO HAVE WITNESSES ...
rc=0
```

**A clean zero and `rc=0`, standing in for "could not tell."** The per-language `REFUSED:` line was
printed and was not enough: a summary line and an exit code are what anything downstream actually
reads, and a caller scripting on the exit code would have read NO DEBT. Cured — the census now exits
2 and names the languages excluded from its totals.

⭐ **That is three instances in one sitting of one shape, and the third was in the instrument written
to diagnose the first.** (1) `lib_ladder.sh` graded the witnesses a rung had and was silent about the
forms it did not; (2) the first census keyed on a column answering a narrower question than was asked;
(3) this census's own summary excluded refusals from its totals and exited green. **Every one of them
printed the success shape, and none was catchable by re-reading the instrument that produced it** —
only by a second derivation of the same number, or by deliberately exercising the failure path. The
third was found only because the first two had made it worth going to look.
