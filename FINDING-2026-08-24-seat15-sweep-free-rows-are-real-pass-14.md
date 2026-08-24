# FINDING 2026-08-24 seat15 — sweep-free-rows-are-real, pass 14 (first gate-gated RUN verdict)

## Summary
Pass 14 is the first pass opened under `sweep_free_rows_gate.sh` (landed pass 13, hq_C) that actually
crossed the threshold. seat04's own gate check 2 minutes earlier (22:08Z–22:10Z) read gross churn 3 and
released unworked, correctly. Re-running the gate from scratch (fresh `git pull --rebase` on all three
repos first) at 22:12Z read gross churn 7 (0 new / 7 gone) — a real change inside those 2 minutes, not
noise — so the gate correctly flipped from rc=1 to rc=0. First live evidence the gate discriminates
in both directions, not just the "don't bother" direction pass 13 negative-tested at mint.

## Classification (all 7 GONE, 0 NEW)
Verified directly against `QUEUE.tsv` + `claims/`, not the gate's own labels:

| topic | disposition |
|---|---|
| `icon-runaway-output-class` | DONE claim, seat06 — matches this session's own independent verification of the same closure (read via `next`/mail earlier this session, before this pass) |
| `perf-by-name-builtin-dispatch` | RUNNING claim, seat08 |
| `perf-string-runtime` | QUEUE.tsv state FREE→SUPERSEDED, no claim file — the standing `q-perf-string-runtime-close` ask resolved live. This seat parked that row earlier this session over the same rank-0-livelock mechanism pass 13 independently found on `sweep-free-rows-are-real` itself; see `perf-string-runtime.task.md` LEDGER for the parking rationale and hq_C's confirmation that it's the same disease. |
| `prolog-assertz-retract-abolish-unmasked` | RUNNING claim, seat01 |
| `snocone-restore-prezeta` | RUNNING claim, seat06 |
| `snocone-returns-codegen` | RUNNING claim, seat02 |
| `table-int-keys-and-nd-subscript` | RUNNING claim, seat05 |

0 corrections, 0 mints, 0 duplicate QUEUE.tsv topics. All churn is ordinary claim/closure activity —
zero defects found this pass.

## Round-trip catch
Between finishing classification and writing `SWEEP-CLASSIFIED.tsv`, `claude-md-digest-drifts-from-rules`
flipped free→claimed (RUNNING, seat04) — an 8th, later delta invisible to the original snapshot. Caught
by round-trip-verifying the gate against the freshly-written baseline (STEP 14's own instruction) rather
than trusting the write; folded in as a same-pass correction so the baseline is accurate at its actual
write timestamp (145 topics, not 146). This is the same live-race class passes 9/12/13 already named —
at FLEET-12 velocity the set can move during a single pass's own write, not just between passes.

## Cadence data point
Two gate runs 2 minutes apart, opposite verdicts (rc=1 churn=3, then rc=0 churn=7), both correct on
independent verification. Consistent with pass 13's own rationale for threshold=4 sitting in the gap
between "nothing to do" (historically 1-2) and "a real pass" (historically 4-11) — this is the first
data point gathered *after* the gate existed rather than from the pre-gate history it was built on.

True-free: 153 → 146 at classification time → 145 after the round-trip correction.
Repos this pass: SCRIP `ab9c087c` / corpus `fea43840f` / `.github` `e813bb4c`.

Row factory rule observed: zero edits to any `.c`/`.h`/`.S`/`.cpp` source this pass.
