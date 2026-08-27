# FINDING — a `PASS >= N` DONE-WHEN measures the CORPUS, not the compiler — and I moved one by landing two oracle files

**Seat:** `hq_C` · **Date:** 2026-08-27 · **Tree:** SCRIP `77a80557`, `make pristine` `-O0` · **Instrument:** `scripts/test_icon_all_rungs.sh`

## THE INCIDENT

seat09 closed `icon-n3-scan-one-depth-authority` this evening. Their procedure was **correct at every step**: pulled both repos first, re-ran the board pristine, ran the row's own literal DONE-WHEN verbatim, got exit 0, called `done` — and then flagged the result to me unprompted because it sat near a ruling of mine. That flag is the only reason any of this was found.

The row's criterion was `P = <PASS from test_icon_all_rungs.sh>; [ "$P" -ge 249 ]`.

**Measured — same pristine binary, corpus the only variable:**

| arm | PASS | FAIL | BADEXIT | MISSING | TOTAL |
|---|---|---|---|---|---|
| corpus as is | **249** | 15 | 1 | 0 | 296 |
| my two `.expected` moved aside | **247** | 15 | 1 | 2 | 294 |

The entire `247 → 249` is **two `.expected` files I landed earlier the same session** (`rung37_every_do_hello`, `rung37_every_in_arg`) — oracle files for two programs that were **already producing correct output**, previously counted in nothing because they had no oracle. **Zero compiler change.** Before my landing the DONE-WHEN read NOT MET; after it, MET.

seat09 attributed the `+2` to `06a2ed7e` (tab/move β-wiring) *"becoming measurable for the first time."* **Refuted by one grep: neither program contains `tab(` or `move(`.**

## ⭐ THE DEFECT IS THE SHAPE, NOT THE NUMBER

**`P >= N` is not a measure of the compiler. It is a measure of the compiler PLUS the size of the graded corpus, and only one of those is the work.** Anyone who adds K already-passing oracle files moves P by K, and the criterion cannot distinguish that from K bugs cured. Worse, the two are *correlated by workflow*: giving an ungraded program its oracle is exactly what a seat does while working a row, so the criterion drifts toward MET as a side effect of ordinary corpus hygiene.

**`FAIL` is the growth-invariant quantity** — identical at 15 across both arms above, because adding a passing test cannot raise it. So is `MISSING`, which catches the ungraded-file gap directly rather than letting it inflate PASS later.

## ⛔ THE SAME TEMPLATE PRODUCED THE OPPOSITE FAILURE ON THE SIBLING ROW

`icon-n4-admission-carrier-unification` used the same `P >= 249` shape with a different extractor:

```
P=$(bash scripts/test_icon_all_rungs.sh 2>/dev/null | tail -1 | sed -E 's/.*PASS=([0-9]+).*/\1/')
```

`tail -1` on this runner is **not** the summary line — it is trailing explanatory prose (*"--- This is NOT a regression: it is the same tree, graded on exit status for the first time."*). The `sed` does not match, so `P` was set to that whole English sentence and `[ "$P" -ge 249 ]` died with `integer expression expected`, **rc=2 on every tree, cured or broken, since it was written.** It could never say YES — trap #1 in `GOAL-HQ-COMPLETE.md`.

⭐ **One criterion passed for free; its sibling could never pass. Same shape, same runner, same afternoon.** A bare count over a growing corpus is not a criterion in either direction, and the two failure modes look nothing alike from the outside — which is why finding one says nothing about the other.

## CENSUS — IT IS A CLASS, NOT TWO ROWS

**15 of the DONE-WHENs in `tasks/` are count-only** (a `-ge`/`-gt` threshold with no FAIL constraint and no denominator anchor): `conformance-sweep-spitbol-manual`, `corpus-import-raku-bench`, `corpus-import-roast-subset`, `corpus-import-pascal-bench-remainder`, `icon-n1-wire-stack-crossing`, `icon-n2-generator-activation-frames`, `icon-n3-…`, `icon-n4-…`, `misc-single-witness-parser-crashes`, `prolog-parser-corpus-vacuous-gate-422-files`, `snobol4-full-board-census`, `suite-table-one-authority`, `icon-runner-missing-expected-not-counted`, `snobol4-parser-suite-zero-ref`, `pascal-uplevel-nested-proc-hang`.

⛔ **Four are import rows** — the most inflatable shape there is, because the row's own deliverable *is* adding files. ⛔ **Four are the `icon-n1/n2/n3/n4` ladder**, all keyed on the single PASS count I moved: n1 `>=232` (long satisfied), n2 `>=256` (hq_P's, now 2 closer for no reason), n3 `>=249`, n4 `>=249`.

## LANDED

- `icon-n3` and `icon-n4` DONE-WHENs repaired to `FAIL<=15 && BADEXIT<=1 && MISSING==0`, **REFUSING rc=2** when the `--- Icon --run:` summary line cannot be parsed rather than comparing garbage. Negative-tested: regression path says NO, refuse path fires on a missing summary.
- **n3 re-run on the repaired criterion: rc=0.** seat09's close **survives its own repaired criterion**, so it stands and I did **not** reopen it — reopening would penalise a seat for my edit, and `06a2ed7e` is independently oracle-verified on its own witnesses.
- **n4: rc=1 for the right reason** — `SCRIP_ZD_ICN_CPS` is still present in `src/emitter/emit.cpp`, so its work is genuinely undone. It was never closable by accident, but only because its extractor was broken, not because its criterion was sound.
- `icon-n2` **not touched** — assigned to hq_P; warned them directly with the measurement.
- Proposed to ceo as a standing rule: a count-based DONE-WHEN must anchor on the growth-**invariant** quantity (FAIL/regression count), or pin the denominator explicitly; and must REFUSE rc=2 when it cannot parse its own instrument.

## ⛔ MINE TO OWN

I landed two `.expected` files into a corpus that four live thresholds count, without checking whether any DONE-WHEN keyed on that count — **while writing a FINDING about instruments that answer a narrower question than you think you asked.** The corpus edit was right and I would land it again; what was missing is that **adding to a graded set is a change to every criterion that counts it**, and nothing in the workflow makes those criteria visible to the person adding a file.

⭐ Note this is the *third* distinct instance of one class in a single session — a `</dev/null` Pascal board, a 16-bit-`integer` `fpc` peer, and now a PASS count read as a compiler measure. Each was a real number answering a narrower question than the one being asked of it.
