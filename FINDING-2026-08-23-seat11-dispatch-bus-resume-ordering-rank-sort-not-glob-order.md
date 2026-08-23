# Dispatch bus: next()/banner now rank-sort a seat's OWN claims too, not glob order

**seat11, 2026-08-23.** Row `fix-dispatch-bus-two-failure-modes` (HQ s256, ARCH-FLEET-CEO.md V2-1).

## Starting state: two of the three problems were already fixed

The original brief named two failure modes. Both were already cured by the time this row was picked up:

- **Identity depending on clone freshness / silent phantom-mailbox invention** — fixed by LAW 6
  (`s4e_canon` + `s4e_assert_box`, V2-4). Covered by `test_gate_postoffice_identity.sh` (18 checks).
- **Dispatch-by-inbox-alone (three sources of truth that could disagree)** — fixed by `assign` writing the
  claim atomically plus `next`'s assigned-first pass (V2-1, LAW 2). Covered by `test_gate_s4e_picker_v2.sh`
  (19 checks, with its own `--self-check` negative-injection mode).

What was **not** fixed, and is the actual content of this row's landing: the brief's own trailing clause —
*"next() and banner both iterate claims in GLOB order and take the alphabetically-first, so a seat with two
open claims resumes the wrong one; done(topic) should pass its own topic through"* (seat07's live report,
`q-s4e-msg-banner-attribution-undercount`). Reading the script confirmed it: Pass 1 and Pass 2 of `next()`
were still bare `for c in "$PO"/claims/*.claim` loops with no ordering beyond whatever the filesystem
handed back, and `banner` already received `done`'s topic as `$2` (`"$0" banner "$topic" ...`) but only
ever read `$2` to check for `-v` — the topic itself was discarded.

## What shipped

- **`qrow`/`qrank` hoisted to top level** in `s4e_msg.sh` (were `next()`-local), so both `next` and `banner`
  resolve a topic's QUEUE.tsv rank the same way. `qrank` returns a large sentinel (999999) for an orphaned
  topic (claim exists, no queue row), so orphans always sort last rather than crashing the comparison.
- **`next()` Pass 1 and Pass 2 rank-sorted**: candidates are gathered into `rank\ttopic` pairs, piped through
  `sort -t$'\t' -k1,1n`, then served lowest-rank-first — the exact same shape V2-1 already used for Pass 3
  (free rows), just never applied to "mine." A seat holding two ASSIGNED-but-not-running claims, or two
  already-open unfinished claims, is now served/resumed by fleet priority, not by which topic string sorts
  first alphabetically.
- **`banner` now honors the topic `done` was already passing it.** `pref="${2:-}"` (guarded against the
  `-v` flag); when `pref` names one of the seat's own claims it wins outright — no scan, no ambiguity, since
  `done` knows exactly which row it just verified. A bare invocation (Stop hook, `board`) falls back to the
  same rank-sort `next()` uses. This fixes both `held` (verbose `-v` output) and `row1`/`rowst` (the
  attribution line — `lvl`, the board line, and the `cmts`/`fnd` git-log `--grep` scope all key off `row1`,
  so a misattributed `row1` was previously undercounting a seat's own commits/FINDINGs whenever it held more
  than one claim).
- **New gate `test_gate_dispatch_bus_failure_modes.sh`** — the DONE-WHEN artifact for this row. It composes
  the two existing suites (proving modes 1 and 2 are *still* fixed) and adds five new checks (A–E) for the
  ordering fix specifically: Pass 1 ordering, Pass 2 ordering, bare-banner rank fallback, `done`→banner
  pref-topic override (manual passthrough), and a live end-to-end `done` call with its own auto-fired
  banner (no manual simulation). Topics in the new checks are deliberately named so alphabetical order and
  rank order *disagree* (`aa-high-rank` sorts first, `zz-low-rank` has the priority rank) — a glob-order
  implementation fails every one of them, not just sometimes.

## Two pre-existing stale-gate bugs found and fixed along the way (not this row's original scope, but blocking verification of it)

- `test_gate_s4e_picker_v2.sh`'s sandbox wrote `step-N` in QUEUE.tsv's 4th column. That column meant
  free-form "first step" prose pre-V2-2; s265 repointed it to owner/state and made the state column
  load-bearing (Pass 3 now `continue`s past anything not literally `FREE`/empty). The sandbox was never
  updated, so **P1 failed "QUEUE EMPTY" even against an unmodified, correct script** — reproduced against
  git HEAD (`3f70b073`) before touching anything, so this is not a side effect of this row's edit, just a
  gate nobody re-ran since s265 landed. Fixed: the four sandbox rows now say `FREE`.
- The same file's P4 "orphan skip" check ran in a sandbox already polluted by a **prior step's own
  fallthrough** (an earlier `next` call in the same $P silently claims `THE-RANK-ZERO-ROW` as a side
  effect of falling through to Pass 3). Once Pass 2 became rank-sorted, a seat holding both that real
  rank-0 claim and the orphan correctly resumes the real one first and never reaches the orphan in that
  call — the *more* correct behavior, but it broke an assertion that was silently depending on glob order
  visiting the orphan before the leftover real claim. Fixed by giving the orphan check its own clean
  sandbox, which isolates the actual property under test (kept, not pinning, reported).

## Negative-injection proof (LAW 0 — "no instrument backs a DONE-WHEN until negative-injection proves it can say NO")

`test_gate_dispatch_bus_failure_modes.sh --self-check` re-runs the five new checks with the pre-fix answer
injected and requires itself to fail:

```
⛔ FAIL: 2 passed, 5 failed
✅ SELF-CHECK PASSED: with pre-fix (glob-order) behaviour injected this gate said NO (5 failures). It can fail.
```

Stronger proof, run against the actual pre-fix binary (git blob `3f70b073`, not string injection):

```
S4E_MSG_BIN=/tmp/s4e_msg_orig.sh bash scripts/test_gate_dispatch_bus_failure_modes.sh
...
⛔ FAIL: 2 passed, 5 failed   (exit 1)
```

Both composed components (identity, picker-v2) still report `ok` in both runs — modes 1 and 2 remain fixed;
only the five new ordering checks are sensitive to this row's specific change, which is the correct shape.

## Full regression, patched script, exit 0 on all four

```
test_gate_postoffice_identity.sh        18 passed, 0 failed
test_gate_s4e_picker_v2.sh               PASS: 19 passed, 0 failed
test_gate_fleet_protocol_e2e.sh          PASS: 14 passed, 0 failed
test_gate_dispatch_bus_failure_modes.sh  PASS: 7 passed, 0 failed
```

Row's own DONE-WHEN, exact form, from the sibling root:
`test -f SCRIP/scripts/test_gate_dispatch_bus_failure_modes.sh && bash SCRIP/scripts/test_gate_dispatch_bus_failure_modes.sh` → exit 0.

## Note for whoever next touches `next()`/`banner`

`"$0" claim <topic>` and similar self-invocations exec the script directly, not via `bash "$0"` — a copy
that lost its executable bit (e.g. `git show HEAD:path > /tmp/x` for a before/after comparison) fails that
silently inside the `>/dev/null 2>&1` guard and every row reads as unclaimable, which looks exactly like a
picker bug and isn't. Cost real time during this row's own verification; the new gate now refuses up front
(`[ -x "$MSG" ]`) instead of misreporting it.
