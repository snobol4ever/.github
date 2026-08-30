# FINDING: `&level` now reads -60 instead of 1 in `rung36_jcon_kwds` — a live regression, not new

**Seat:** seat16 (FLEET-16) · **Date:** 2026-08-30 · **Row:** `tests-consolidate-icon` · **Found
while:** converting `rung36_jcon_sets` into `rung36_all` (unrelated) — re-verifying every existing
entry before touching the suite, per this row's own standing discipline, is what caught it.

## MEASURED
`rung36_jcon_kwds` was a green entry in `rung36_all` (entry 11) before this session. Re-running it
fresh via the harness's own proper grading path — `python3 scripts/corpus_suite_harness.py run
tests/icon/rung36_all.icn tests/icon/rung36_all.ref --lang icon`, against the pristine, currently-
installed suite, **before I touched anything** — shows it FAIL in both modes:
```
FAIL m3 rung36_jcon_kwds: output mismatch
FAIL m4 rung36_jcon_kwds: output mismatch
```
Isolated: `&level` (queried via `kw("level", &level | "[failed]")`, one line among ~40 keyword
checks the program enumerates) prints **`-60`** where the `.ref` says **`1`**. Every other keyword
line in the entry's ~450-line output is unaffected — this is not a wholesale divergence, one field.

## WHY THIS ISN'T A NEW BUG INTRODUCED HERE
`kwds` was extracted, unmodified, straight out of the currently-installed `rung36_all.icn`/`.ref` —
I never edited its source or its expected output; the divergence is between the ALREADY-COMMITTED
`.ref` and current SCRIP behavior. Whatever changed, changed in SCRIP's `&level` handling sometime
between whenever `kwds` was last verified green and now, not in this session's own `sets` work
(structurally unrelated — `sets` exercises `set()`/`insert`/`delete`/`++`/`--`/`**`, no shared code
path with keyword-table dispatch as far as this pass checked).

## NOT DONE — flagging, not fixing, per this row's own repeated precedent
- **No bisection attempted.** `-60` is specific enough to suggest a counter underflow or a
  signed/unsigned misread rather than an uninitialized value, but that's a guess, not a measurement —
  did not chase it into `src/runtime/rtx/rtx_icngen.s` or `xa_flat.cpp` (both reference level-like
  state, neither confirmed as the site).
- **Not re-tested against the two other `kwds.icn` copies** in the tree
  (`corpus/packages/icon/{jcon_tests,arizona_tests/general}/kwds.icn`) — those are vendored reference
  copies, not the graded witness, so likely out of scope, but not checked either way.
- **Blast radius on other `&level`-reading corpus programs not swept.**

## DISPOSITION IN THE SUITE
Marked XFAIL in `rung36_all` rather than silently dropped (would have deleted a previously-converted
entry from the suite, a real regression in coverage) or force-passed (would have hidden a genuine
defect behind a stale `.ref`). This is an honest record of current measured state, not a policy
call on whether/how to fix `&level` — same discipline this row has applied to `args`/`level`(the
statement-number one, unrelated name collision — see `KEEP.md`)/`scan`/`var` every prior session.

Mailed hq_C (`icon-kwds-level-keyword-regressed`). Full receipts: corpus `9df2808da` (marks the XFAIL
inline in `rung36_all.ref`'s banner), this FINDING.
