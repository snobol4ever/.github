# FINDING — the sanctioned "regenerate the SCORE.md grid" instruction deletes every row's provenance

**Measured 2026-09-03 ~18:00 CDT box clock · hq_T (HQ-TEST) · SCRIP `7cc472145` · .github `0a5d5a76` · static, no run required**

## THE CLAIM

`.github/SCORE.md` tells its readers, twice and in bold, **not** to hand-edit the standardized-display grid but to
regenerate it:

> regenerate it with `python3 scripts/util_build_score_md.py` (from `SCRIP/`, after `make pristine`) rather than hand-editing a cell
>
> (The top grid above is now exempt from hand-editing entirely — regenerate it instead.)

Followed today, that instruction **destroys the `Vendor / package suites` and `Tree · box clock · by` columns of every
row in the grid** — the second of which is every row's provenance, the thing this same file spends three long
paragraphs establishing as non-negotiable ("a scoreboard row whose provenance is unresolvable is not a weaker claim
than one with a hash; it is an **unfalsifiable** one").

## THE EVIDENCE — two literals and one missing guard

The generator's header is a **4-column literal**, `SCRIP/scripts/util_build_score_md.py:206`:

```
"| Language | Master suite (`ALL.csv`) | Floor/smoke gate | Master board (`ALL.<ext>` via `corpus_suite_harness.py run`, m3 · m4) |"
```

The live board is **6 columns**:

```
| Language | Master suite (`ALL.csv`) | Floor / smoke gate | Master board (m3 · m4, PER MODE, never summed) | Vendor / package suites | Tree · box clock · by |
```

`util_apply_score_grid.py` splices **by position** — from the `| Language |` header through the `_tree:` stamp — and
its only guard was:

```python
assert g.startswith('| Language |') and re.search(r'^_tree: ...$', g, re.M), "new grid malformed or unstamped"
```

A 4-column grid satisfies both halves. It starts with `| Language |`. It carries a stamp. The splice proceeds and the
two right-hand columns of all eight rows cease to exist.

**Reproduced on a copy** (2026-09-03, before the cure): a hand-built 4-column grid in exactly the generator's shape
spliced cleanly into a copy of the live `SCORE.md`, rc=0, no warning.

## WHY NOBODY HIT IT

Because the instruction is expensive to follow. A full regeneration invokes all seven languages' floor gates **and**
all seven master boards — ~30–40 minutes on a loaded box, which is precisely the "hour away of running tests" Lon
ruled against at 15:55. So for weeks every seat that measured a suite **hand-edited its row instead**, in direct
contradiction of the file's own instruction, and by doing so silently kept the two columns alive. The grid grew from
four columns to six through those hand edits; the generator was never taught them.

⭐ **The general form, and the reason this is worth a FINDING rather than a commit message: a workflow that is
documented but too expensive to run does not fail loudly, it falls out of use — and then decays out of step with the
artifact it maintains, undetected, because the thing that would detect the drift is the workflow nobody runs.** The
divergence is invisible for exactly as long as everyone keeps ignoring the instruction, and becomes destructive the
first time somebody obeys it. The most likely person to obey it is a new seat doing what the file says.

## THE CURE LANDED, AND WHAT IT DELIBERATELY IS NOT

`util_apply_score_grid.py` now **REFUSES** when the generated grid's column count differs from the live board's,
naming both counts, the columns at risk, and the two ways forward. Two-part proof, both on copies: a 4-column grid
refuses with the file byte-identical afterwards; a 6-column grid still splices normally (rc=0). This is a
**non-destruction guard, not a repair** — it does not teach the generator the two columns it is missing, because the
generator does not collect vendor-suite results or per-column provenance at all, and inventing empty cells for them
would publish "nobody measured this" for every row, which is a false claim where a refusal is a true one.

⛔ **Still open, and rowed rather than taken:** `util_build_score_md.py` must learn the board's real column set, or the
grid must stop claiming to be generator-owned. Until one of those happens the honest workflow is per-row: the
`SCRIP/scripts/util_score_row.py` helper landed this session (row
`score-md-rows-are-rewritten-by-the-runner-that-measured-them`), which rewrites one cell in place from numbers a
runner already measured and **runs no suite** — the FACT-RULE-shaped answer, and the reason the expensive workflow no
longer needs to be anyone's default.

## ONE MORE THING THE SAME MEASUREMENT SHOWED

The grid's whole-file stamp read `_tree: SCRIP=e182a71a corpus=e7bbc675 .github=8e4fc55d-DIRTY generated
2026-09-02T02:35Z_` while **six of its eight rows carried 2026-09-03 provenance from four different sessions**. That
is not a stale label — it is a **wrong** one: it asserts a coverage it does not have, and unlike a stale row, nothing
about it looks old. A row-write now demotes it to `(LAST FULL REGENERATION ONLY -- rows rewritten since carry their
own tree in the last column)`.
