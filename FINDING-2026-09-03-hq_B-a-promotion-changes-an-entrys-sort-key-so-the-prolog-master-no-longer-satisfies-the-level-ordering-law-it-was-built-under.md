# FINDING — a promotion changes an entry's sort key, so the Prolog master no longer satisfies the level-ordering law it was built under

**Seat:** hq_B · **Date:** 2026-09-03 (TRIO) · **Tree:** SCRIP `4f847224`, corpus `3a40f8e3` (master 404 entries) · Found while building `--reindex` for row `master-builder-needs-a-csv-only-reindex-path`

## The law, and what broke it

`util_build_master_suite.py` orders the master by `(xfail, feature-count, line-count, name)` — Lon's level ruling, *"a smoke test would be say the first 20-50 tests… the last level all 1200+"* — so **`rank` is the position and a level is a prefix**, which requires green before xfail.

**Flipping an xfail therefore changes an entry's sort key.** The seven promotions of corpus `2b71e9a2` moved seven entries out of the xfail block without re-sorting the file.

## Measured

Full builder run in a scratch clone vs. the committed tree, comparing the 404 common entries:

| | |
|---|---|
| relative order identical | **no** |
| entries whose rank differs | **265 of 404** |
| first divergence | committed `simple_program_91` vs. builder `format_directive_6`, then `atomconv_directive_1` — a promoted entry |

⛔ **Nothing is inconsistent.** `ALL.pl` and `ALL.csv` agree with each other, every gate is green, and `test_gate_pl_xfail_marker_consistent.sh` passes because it checks the three *marker* locations, not the ordering. What has drifted is the **law**: the file is no longer sorted the way its own builder sorts, so `rank <= N` no longer selects the greenest N.

## Why `--reindex` deliberately does not fix it

Re-sorting inside an index rebuild would churn `ALL.pl` and `ALL.ref` on every run and would break this row's own oracle — a correct hand-edited CSV must reproduce byte-identically. So `--reindex` sets `rank` to the entry's **position in the master as it stands** and reorders nothing.

**Two defensible answers, and it is a corpus-policy call, not an instrument's:**

1. **A promotion re-sorts the master**, and the churn is the price of keeping the law true.
2. **`rank` is position and the ordering is a build-time convention only** — in which case the level-prefix property is a claim the docs should stop making.

Routed to the ceo. Either way the fix is one decision plus a gate; what must not happen is the current state persisting *unstated*, because a level-prefix runner would silently select a set that is no longer greenest-first.

## ⭐ The shape

The promotion gate I wrote yesterday checks that an XFAIL marker agrees in all three places. It does — and the suite still drifted, because **the marker and the ORDER are two different derived things, and I only guarded the one the row named.** A promotion has a second consequence that no gate was watching. Same family as the rest of this week: an instrument answering exactly the question it was given, while the question next to it went unasked.
