# FINDING — seat02: sweep-free-rows-are-real, pass 12

**Row:** `sweep-free-rows-are-real` (rank 0) · **Date:** 2026-08-24 · Method unchanged from
passes 5-11 (pull fresh, `comm` current true-free against `SWEEP-CLASSIFIED.tsv`, classify the
delta, rewrite the baseline), plus a real method stress-test this pass surfaced (§3).

## 1. Snapshot

SCRIP `85a92341` / corpus `dfc75192` / `.github eefbfe97`, all three pulled fresh via plain
fast-forward `git pull --rebase` immediately before the sweep. True-free 143 → **149** (net +6,
gross churn 10 by final reconciled count — see §3 for why "gross churn" needed reconciling twice
this pass). 0 duplicate `QUEUE.tsv` topics, 60 orphaned-DONE claims (was 58 at pass 11,
proportional growth, not chased).

## 2. Classification — 8 new, 2 gone, all individually verified against fresh HEAD (not read from brief)

**GONE (2):** `icon-runaway-output-class` (claimed RUNNING by seat15), `perf-dispatch-gc-safepoint-necessity`
(claimed by seat13, no RUNNING marker yet — a manual claim, same shape as pass 11's
`banner-attributes-wrong-row-on-unclaim`). Both confirmed via `claims/`.

**NEW (8), every one verified by direct execution, not by trusting its brief:**

| Topic | Verification |
|---|---|
| `bench-6-kernels-below-oracle-cure` | Bundled dispatch row pointing at `bench-rebaseline-15-kernels-clean-oracle`'s own LEDGER table (by design, not re-derived); sibling row confirmed to exist. |
| `perf-nv-set-capture-pump` | `core.c:2335` (rt_sxt_break call site), `pattern_match.c:1179` (`rt_defer_cell_read`) — both cited lines match verbatim. |
| `perf-nv-set-fn-o0-overhead` | `core.c:2273` `SCRIP_NV_MEMO` getenv line and `core.c:2256-2267` memo-cache comment block — both match verbatim, including the quoted `-O2` pre-cure numbers. |
| `perf-sxt-break-unconditional-call-tax` | `gc_heap.c:51` — `void rt_sxt_break(const char *s) { if (s && s == g_sxt_owner) g_sxt_owner = (char *)0; }` — byte-for-byte match to the task file's quoted body. |
| `demo-regen-broken-subfolder-reorg` | Ran `util_regen_demo_s_artifacts.sh done-check`: exactly 21 "no .sno" hits, matching "100% silently skips every one of its 21 DEMOS entries." Confirmed `corpus/demo/roman/roman.sno` (per-family subfolder layout, as claimed). |
| `prolog-two-programs-broken-post-churn` | Ran both compiles directly: `coverage_pl_nodes.pl` → exact `[IBB] FATAL: mode-4 driver: main BB graph not found`, rc=1, empty output. `rung10_programs_puzzles.pl` → `as` rejects with the exact mangled dash-run symbol `$23$2D$2D...` already-defined collision. |
| `rebus-corpus-100pct-broken` | Ran all 3 compiles directly: `binary_trees.reb` + `syntax_exercise.reb` → exact `FATAL lower_snobol4 (GZ#5 subset): ... SN4-PAT-2 handles TT_SCAN match subjects only` message. `word_count.reb` → exact `rebus_lower: lower_tree_expr unhandled TT_48`. Prior committed `.s` sizes (64721 / 98380 / 16876 bytes) matched the claimed 64KB/98KB/16KB exactly. |
| `snocone-relop-parse-regression` | Compiled `corpus/crosscheck/snocone/rungB09/B09_str_eq.sc` directly: exact `snocone parse error: syntax error` at line 4 (`if (a :==: b) {`), matching the claim verbatim. See §4 for one citation-drift note found and recorded, not fixed. |

All 8 LIVE, 0 dead, 0 corrections needed to any row's core claim.

## 3. ⚠️⚠️ Method stress-test: this pass caught its own claim races, twice, plus a self-inflicted scratch-file bug

This pass ran during the fleet's first hour under **FLEET-12** (expanded from FLEET-4/8), and it
shows: this is the first pass where the true-free set moved **during the pass's own verification
work**, not just between passes.

- **Round 1**: first snapshot found 6 new rows (the 4 `perf`/`bench` ones above plus
  `perf-string-runtime` and `snobol4-trailing-star-comment-not-lexed`), 0 gone. A round-trip
  re-verification minutes later (after writing part of this pass's own findings, plus an
  unrelated HQ reply — see §5) found **3 more** claim changes: `perf-string-runtime` claimed
  RUNNING by seat06, `icon-runaway-output-class` and `perf-by-name-builtin-dispatch` (both
  pre-existing pass-11 baseline members) also newly claimed.
- **Round 2**: after correcting for round 1, a second re-verification found
  `snobol4-trailing-star-comment-not-lexed` — independently verified LIVE minutes earlier with
  all 4 of its witnesses directly reproduced — claimed RUNNING by seat12 before the corrected
  baseline could even be written. `perf-by-name-builtin-dispatch` flipped again (claimed →
  free), resolved by trusting only the final atomic `claims/` read.
- **Self-inflicted delay, distinct from the races above**: an early `cat >>` appended this
  pass's first 6 new-topic lines directly onto what was meant to remain a clean, untouched copy
  of the pass-11 baseline (143 topics) — corrupting that reference file to 149 lines and
  producing two rounds of garbled `diff`/`comm` output before a suspicious line count caught it.
  Recovered by reconstructing the true 143-topic list from this session's own earlier full
  `Read` of the file rather than trusting any further scratch-file derivation.

**Method lesson for pass 13+:** at current fleet velocity, round-trip-verify with `QUEUE.tsv`
and `claims/` read together **immediately before writing the baseline** (not after drafting the
comment block, not after any side-work), and if anything shifts, re-derive from an untouched
copy of the prior baseline rather than patching an already-mutated scratch file. This is a
sharper version of pass 9's single-race catch — worth another data point for HQ's still-open
event-driven-vs-clock-driven cadence call: **a busier fleet makes the sweep itself noisier, not
just the thing it measures.**

## 4. One citation-drift note, recorded not fixed (row-factory rule)

`snocone-relop-parse-regression`'s minting LEDGER cites "confirmed to have a real prior
committed `.s` (24-46KB)" for the 18 regressed `corpus/crosscheck/snocone/**` files. Checked:
**zero** `.s` files exist anywhere under `corpus/crosscheck/snocone/` right now. Root cause is
not a wrong claim — `corpus/crosscheck/` is exactly the tree CEO-15's artifact-consolidation
policy retired `.s` artifacts for (confirmed distinct from `corpus/rebus/`'s top-level `.reb`
files, a "programs" tier CEO-15 explicitly leaves in scope, whose `.s` files I *did* independently
find still present at the exact claimed byte counts). The regression itself reproduces exactly as
briefed regardless of whether the old `.s` still exists to point at. Flagging for whoever works
that row (or the next sweep) — not this row's job to fix.

## 5. Also this pass (not part of this row, noted for completeness)

Answered an HQ cross-thread question mid-sweep on an unrelated topic (Icon 244-vs-169 board
instrument gap) — see `.github/FINDING-2026-08-24-seat02-icon-169-vs-244-is-not-vacuous-passes-its-one-exit-status-wiring-defect.md`.
Also cleaned up 4 stray `.u1`/`.u2` ucode byproduct files this seat's own diagnostic work for
that reply had left untracked in `corpus/icon/`.

`SWEEP-CLASSIFIED.tsv` rewritten for pass 13, round-trip verified clean immediately after
writing (149 topics, `comm` diff against a fresh atomic `QUEUE.tsv`+`claims/` snapshot empty).
