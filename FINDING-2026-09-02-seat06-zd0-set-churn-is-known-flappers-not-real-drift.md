# FINDING — the ZD0 optbypass watermark's recent rise (302→306 across readings) is fully explained by
# ~4 already-known bimodal corpus entries flipping run-to-run; a controlled two-tree, per-entry set
# diff finds ZERO entries that entered or left the ZD0-failing set for a tree/commit reason, on either
# arm. OPT0 is perfectly stable (0 wobble, 0 tree diff) across every reading. Directly serves I10
# (`optbypass-pin-stable-subset`) as independent corroborating evidence for the stable-subset redesign.

**seat06 · 2026-09-02 · row `zd0-set-churn-name-the-arriving-entries-not-the-scalar`**

## Summary

The row asked: is the SCRIP_ZD=0 bypass-failure count's rise across recent readings (hq_P: 303,304,304,306,306,307
· hq_C: 301,302,302,303,304) real drift from landed commits, or measurement noise? **It is noise.** A controlled
experiment — same corpus, two SCRIP trees 13 commits apart, each read multiple times, diffed by entry NAME rather
than by scalar count — finds that every entry whose ZD0 (or OPT0) verdict differs across any pair of readings is
a member of a small, already-named set of nondeterministic entries, and that set behaves identically on the old
tree and the new tree. Zero entries show a reproducible, tree-attributable arrival or departure on either arm.

## Method

Fixed the corpus at one checkout (`corpus e7bbc6755`) and varied only the SCRIP binary, to isolate the tree axis
from corpus churn (a confound this project has been bitten by repeatedly — see RULES.md's population-pin history
on this same gate). Two trees, via `git worktree` (no risk to either working copy):

- **OLD**: SCRIP `e182a71a5` — the commit that pinned the CURRENT watermark (population 1656, OPT0 max 191, ZD0
  max 308). 13 commits behind HEAD (`git rev-list --count e182a71a5..HEAD` = 13).
- **NEW**: SCRIP `c9e9473fd` — current HEAD at measurement time.

Instrument: the existing `scripts/util_census_optimizer_bypass.py --out <csv>` (per-entry CSV: `name, xfail,
default_kind/rc, opt0_kind/rc, zd0_kind/rc, opt0_changed, zd0_changed`), unmodified, `--workers 4`, RT_OPT=-O0
(NO -O2, per the FACT RULE). Three full-corpus runs:

```
new_run1  (NEW tree, run 1)                          -> population 1656, OPT0 191, ZD0 304, wall 251.2s
new_run2  (NEW tree, run 2 -- IDENTICAL binary)       -> population 1656, OPT0 191, ZD0 303, wall 291.0s
old_run1  (OLD tree, run 1)                           -> population 1656, OPT0 191, ZD0 305, wall 295.1s
```

`new_run1` vs `new_run2` is the WOBBLE CONTROL: same binary, same corpus, two invocations — any entry that
changes membership here is pure instrument/runtime nondeterminism, not a tree effect, by construction. `new_run1`
(or the intersection of both new runs) vs `old_run1` is the DRIFT CANDIDATE: entries that differ here MIGHT be
real, but only if they are NOT already explained by the wobble control. All set arithmetic below is on the
`xfail=False` population only (1656 entries) — the same population the pin actually grades; an earlier draft of
this analysis included `xfail=True` rows and manufactured one false "arrival" (`arbno_arb_rpos_replace_branch_1`,
which crashes in BOTH the default and ZD0 arms on every tree — it was never a regression, `zd0_changed` there
just means "changed failure KIND under an already-failing default", a different question this row is not about).

## Results

**OPT0: perfectly stable.** 191 / 191 / 191 across all three readings, on two different trees. Wobble set: 0
entries. Tree-diff set: 0 entries. Every one of the 191 OPT0-regressing entries is the IDENTICAL 191 by name in
all three runs. This independently reproduces the historical record ("OPT0 reproduced EXACTLY between hq_P and
hq_C on independent trees") with a proper controlled design instead of two ad hoc readings.

**ZD0: wobble-dominated, zero real drift.**

```
new_run1=304  new_run2=303  old_run1=305
WOBBLE (new1 vs new2, same binary):        3 entries -- arbno_pos_rpos_branch_83, arbno_pos_rpos_branch_85, span_pos_rpos_replace_branch_9
TREE DIFF (new1 vs old1), raw:             3 entries
TREE DIFF minus WOBBLE:                    1 entry -- arbno_pos_rpos_branch_84 (old=FAIL, new1=PASS, new2=PASS)
```

Per-entry detail (kind/rc in each run):

| entry | old (e182a71a5) | new run 1 (c9e9473fd) | new run 2 (c9e9473fd, repeat) |
|---|---|---|---|
| `arbno_pos_rpos_branch_83` | FAIL/0 | FAIL/0 | PASS/0 |
| `arbno_pos_rpos_branch_84` | FAIL/0 | PASS/0 | PASS/0 |
| `arbno_pos_rpos_branch_85` | FAIL/0 | PASS/0 | FAIL/0 |
| `span_pos_rpos_replace_branch_9` | PASS/0 | CRASH/-11 | PASS/0 |

**All four are already-named members of hq_C's original stability study** (`optbypass-pin-stable-subset.task.md`
LEDGER): `arbno_pos_rpos_branch_84` (there measured PASS 6/10, wrong-answer 4/10), `_85` (PASS 4/10, wrong-answer
6/10), and `span_pos_rpos_replace_branch_9` (PASS 4/10, SIGSEGV 1/10, SIGABRT 5/10) over 10 runs on ONE binary.
`_83` is a previously-unnamed sibling in the same numbered family, now caught the same way. **None of this is a
new discovery of instability — it is the same instability, independently reproduced by a different method
(cross-run + cross-tree set diff instead of repeated single-entry sampling) on a different day.**

**The one apparent "departure" does not survive scrutiny, and I checked rather than claimed it.**
`arbno_pos_rpos_branch_84` read FAIL on the old tree and PASS on both new-tree runs — the only entry surviving
the wobble filter, which on the surface looks like a real cure between trees. But this entry is EXACTLY the one
hq_C already measured at PASS 6/10 on a SINGLE fixed binary — a 1-sample old-tree reading landing on FAIL and two
new-tree readings landing on PASS is unremarkable at that base rate (roughly 14% by chance under independence,
not evidence of anything). Rather than infer, I measured: **5 repeated `--only arbno_pos_rpos_branch_84` runs
against SCRIP_ZD=0 on the OLD tree itself** (e182a71a5, unmodified, no re-pull) gave **HANG, FAIL, PASS, FAIL,
PASS** — 2/5 PASS, 2/5 FAIL, 1/5 HANG, on ONE binary. The old tree is exactly as bimodal on this entry as the new
tree. **The apparent departure is the same noise as the other three, just under-sampled (1 old-tree reading
instead of several) by the corpus-wide census design.** MEASURED, not inferred, per the row's own instruction.

**Bottom line: zero entries, on either arm, show a reproducible tree-to-tree membership change.** The full
301–307 historical band on ZD0 is consistent with — and this experiment directly confirms — a fixed population
of roughly 3-4 nondeterministic entries (the `arbno_pos_rpos_branch_8[3-5]` family and
`span_pos_rpos_replace_branch_9`, all pre-existing correctness defects tracked separately under
`fuzz-nondeterminism-rootcause`, not new to this row) each flipping independently between PASS and a non-PASS
kind on every invocation, regardless of which commit is being measured.

## What this means for the two-arms question (I10)

This is exactly the evidence `optbypass-pin-stable-subset` (seat08, I10, rank 0) needs and predicted: **a single
"bypass arm" doctrine is wrong for both pins.** OPT0 needs no stable-subset machinery — it is already exactly
stable, an ordinary `<=` watermark is the right instrument for it as-is. ZD0 needs the redesign already proposed
there (pin the STABLE subset, report the flapping set BY NAME, never sum a nondeterministic unit into a `<=`
comparison) — this FINDING's flapping set (`arbno_pos_rpos_branch_83/84/85`, `span_pos_rpos_replace_branch_9`)
is a smaller, independently-derived, near-exact match to I10's own flapping set, which is the kind of two-method
agreement RULES.md treats as load-bearing corroboration rather than a coincidence to wave past.

## Reproduce

```bash
cd SCRIP && git worktree add /tmp/wt-old <old-hash>   # or any prior watermark-pinning commit
cd /tmp/wt-old && make
cd SCRIP && python3 scripts/util_census_optimizer_bypass.py --workers 4 --out /tmp/new.csv
cd /tmp/wt-old && python3 scripts/util_census_optimizer_bypass.py --workers 4 --out /tmp/old.csv
# diff /tmp/new.csv against a second same-tree run and against /tmp/old.csv on the `*_changed` columns,
# filtered to xfail=False, by entry name -- never by count.
```

Per-entry CSVs (1656 rows each, non-xfail population) and the diff script are not committed (informational,
reproducible from the commands above); available on request if useful for I10.
