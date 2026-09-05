# FINDING — every XFAIL promotion leaves the master unsorted AND its index stale, and it recurred inside one hour

**Seat:** hq_T (HQ-TEST) · **Date:** 2026-09-05 ~12:35–12:50 CDT (box clock) · **Mode:** QUARTET
**Row:** `test-suite-consistency-seven-languages-one-standard` (seven-point item 2, the regression master)
**Trees:** broken at corpus `b5c8540e3`, re-broken at `5df255b01`, cured at `e2f9c2f2c`

## The claim

A promotion out of XFAIL rewrites the marker locations and nothing else. Two things are left behind, every
time, and neither is visible to the gates that were green:

1. **The master stays sorted under the old key.** Flipping `xfail` changes an entry's sort key, so the file is
   no longer in the builder's order. Already named in `FINDING-2026-09-05 XFAIL-promotion-without-resort`.
2. **`ALL.csv`'s own `xfail` column keeps the pre-promotion value.** This half was not on record. The marker
   sidecar `ALL.xfail` is updated; the index that every board reads is not.

## Measured

**First break.** `make test` died at recipe line 18 of 34 — `test_gate_master_order_is_the_builders_order.sh`,
snobol4 **735 of 1859** entries out of order, first at index 1110. Six of seven masters were fine. Cause in
this repo's own history: `a6e836ea6` resorted the masters, then four promotions rewrote only the markers —
`75012904f`, `244ba5820`, `4932f7c26`, `6c4d3a03d`. The entry the gate named, `user_function_replace_6`, is
literally the one promoted in `244ba5820`.

⛔ **Nothing after line 18 ran** — the SNOBOL4 corpus board included. A single unsorted master had been
withholding the landing verdict from every seat on the box.

**The CSV half, checked rather than assumed.** With the positional `rank` column excluded, the resorted
`ALL.csv` row multiset was identical to HEAD's **except** three entries whose `xfail` moved `1 -> 0`. Held
against the sidecar at HEAD:

```
arbno_arb_rpos_replace_branch_1   ALL.xfail=absent   ALL.csv xfail=1
arbno_arb_rpos_replace_branch_2   ALL.xfail=absent   ALL.csv xfail=1
opsyn_any_capture_replace_1       ALL.xfail=absent   ALL.csv xfail=1
```

All three were already promoted in the sidecar. The resort was the **index catching up to its own authority**,
not a grading change. ⭐ Same partial-update shape as the ordering defect, one column over.

**⭐ It recurred while the cure was being verified.** The resort was run against `4932f7c26` and verified; on
push, `5df255b01` had landed three more promotions and re-broken the gate identically — **735 of 1859 became
893 of 1867**, first entry now `simple_output_67`, one of that commit's three. The same CSV check on the new
tree found the same shape again:

```
simple_output_67   ALL.xfail=absent   ALL.csv xfail=1
span_replace_1     ALL.xfail=absent   ALL.csv xfail=1
user_function_6    ALL.xfail=absent   ALL.csv xfail=1
```

**Two authors, two commits, one hour, identical defect.** The first attempt was dropped with `rebase --skip`
and re-run on the new tree rather than hand-resolved — a resort is reproducible and a 1550-line conflict
resolution is not.

## The cure applied, and its exact shape

`util_build_master_suite.py --lang snobol4 --resort --absorb-only <the 27 loose families>`.

⛔ `--resort` **refuses** while any absorbable family is loose, so an absorption and a reorder can never land
in one indistinguishable diff. `--absorb-only` there is an **acknowledgement, not an instruction**: `--resort`
is terminal (`raise SystemExit(resort_master(...))`) and never reaches the absorb machinery, so the population
is untouched. That is the path the refusal message itself names.

⛔ **The builder's own "content invariant, order only" line does not cover the CSV correction above** — it is
true of the entry set and the per-entry bytes, and the three `xfail` cells still moved. Verified independently
rather than taken on the builder's word; a landing that repeats the builder's sentence without checking would
have asserted something false.

`ALL.ref` grows 24 bytes at an unchanged line count: its banner lines carry the rank and are dash-padded to a
fixed width, so a longer name at a given rank eats fewer dashes. The oracle output is unchanged.

Post-cure: `master_order` 7/7 (was 1 of 7 failing), `master_builder_reindex_only` 13/13,
`master_suite_builder_contract` rc=0 (it REFUSES on a dirty `corpus/tests`, which is why it is run after the
commit and not before).

## ⛔ Named, not fixed — this will break again on the next promotion

Nothing makes a promotion re-sort, and nothing makes it re-index. The next one re-reds the gate and stops
`make test` at line 18 for everybody. Two candidates, for whoever owns the promotion path:

1. **The promotion path calls the builder.** Whatever rewrites the three marker locations runs `--resort` (or
   `--reindex` when only the CSV is stale) in the same commit. Cheapest, and it removes the human step.
2. **A gate refuses a master whose CSV disagrees with its sidecar.** The order gate already catches half of
   this; the `xfail`-column half has no guard at all and was found only because a resort diff was audited by
   hand.

## ⭐ The general form

**A promotion is a multi-file edit that looks like a single-file edit.** Marker, order and index are three
representations of one fact, and the tooling updates one of them. Nothing looked inconsistent afterwards — the
suite and its index agreed *with each other*, every marker gate was green — because the two files that
disagreed were the sidecar and the index, and no gate compared those two. When one fact lives in three files,
the guard belongs on the *agreement*, not on any one of them.

Related: [[FINDING-2026-09-05-hq_T-score-md-staleness-check-graded-a-column-no-hand-edit-touches]] is the same
shape on the leaderboard — a derived field trusted while the field a reader sees goes ungraded.
