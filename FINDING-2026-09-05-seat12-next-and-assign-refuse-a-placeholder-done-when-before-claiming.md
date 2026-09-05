# FINDING 2026-09-05 seat12 — next and assign now REFUSE a placeholder DONE-WHEN before claiming, instead of serving it unverified

**Seat:** seat12 (hq_T lane) · **Mode:** FLEET-16 · **Tree:** SCRIP this commit
**Task:** `mint-dispatch-refuses-a-placeholder-done-when` (ceo ruling CEO-286, 2026-09-05)

## 1. The bug

`s4e_msg.sh next` and `assign` already had a probe (`s4e_dispatch_probe`) that correctly identifies a
mint-placeholder DONE-WHEN and answers "could not measure" (rc=2) — but both callers then SERVED the
row anyway, printing a generic could-not-measure warning indistinguishable from a slow criterion or a
missing compiler. A row opened onto a placeholder can never be CLOSED by any amount of correct work
(`done` executes the DONE-WHEN line whole; prose is not a shell command), so the refusal a seat later
gets from `done` reads exactly like the refusal a genuinely wrong CURE would produce — there is no way
to tell "your fix is wrong" from "this row was never workable" from the outside. Two rows were opened
onto this exact shape on 2026-09-05 alone (hq_P's err-msgs row, re-minted before seat08 could open it;
CEO-285's rank-0 oracle row).

## 2. The fix

Added `s4e_predispatch_placeholder_check`: a STATIC, pure-text check (reusing the existing
`s4e_donewhen_is_placeholder`) that reads a topic's baton DONE-WHEN and detects the placeholder shape
*without executing anything*. Unlike `s4e_dispatch_probe` — which must run *after* a claim exists, so
two seats cannot race the same execution — this check is safe to run *before* claiming, because reading
the same static text twice (or before anyone holds the row) can never change the answer. That is what
makes "REFUSE, no claim file written" possible at all.

Wired into all three places a row reaches a seat:
- **`next` PASS 3** (ordinary free-row claim): checked immediately before `"$0" claim "$topic"`; on a
  placeholder, prints the refusal (naming the row and the exact baton path) and `continue`s to the next
  candidate, exactly like the existing boomerang/orphan skip idioms in that same loop.
- **`next`'s dependency-inversion promotion** (serves a blocked row's *blocker* at the blocked row's own
  rank): a new `s4e_promotion_placeholder_ok` wrapper, same shape as the existing
  `s4e_promotion_admissible` it sits beside in the `&&`-chained condition — this path is easy to leave
  half-wired (the sibling gate `test_gate_s4e_next_runs_done_when_at_dispatch.sh` names exactly this
  failure mode for `s4e_dispatch_gate`'s own history), so it gets the identical check.
- **`assign`**: checked before the existing dynamic dispatch probe, unconditionally (NOT gated behind
  `S4E_NO_DISPATCH_PROBE` the way the "already satisfied" refusal is — that escape hatch exists for an
  HQ who wants to dispatch despite a probe reading it doesn't trust; there is no equivalent override for
  a placeholder, since prose cannot become a command no matter who insists). Exits 2, matching the
  project's could-not-measure convention; no claim is written.

## 3. Verification

New gate `test_gate_dispatch_refuses_placeholder_donewhen.sh`, modeled on the existing
`test_gate_s4e_next_runs_done_when_at_dispatch.sh` (hermetic scratch postoffice per `mktemp`, never the
live one — verified byte-identical before/after). Four arms: (1) `next` refuses a rank-0 placeholder row
by name with its baton path, writes no claim, leaves the QUEUE column FREE, and goes on to serve the
next candidate in the same invocation; (2) CONTROL — a genuinely slow criterion (outruns the probe
budget, not a placeholder) is still served with the pre-existing "COULD NOT MEASURE" warning, proving
this cure does not widen into refusing every could-not-measure row; (3) `assign` refuses a placeholder
row rc=2, no claim written; (4) the promotion path refuses a placeholder *blocker* the same way. Three
fail-once mutants (one per insertion site) all correctly go red with the corresponding check removed.
Wired into `make test-postoffice` per the GOAL's own requirement, verified to leave the live postoffice
byte-identical (`QUEUE.tsv`, `claims/`).

Re-ran the full existing `test-postoffice` target (14 gates including the new one) end to end: green.
Also spot-checked the four closest sibling gates individually before writing the new one
(`test_gate_s4e_next_runs_done_when_at_dispatch.sh`, `test_gate_dispatch_bus_failure_modes.sh`,
`test_gate_dispatch_claim_single_authority.sh`, `test_gate_postoffice_identity.sh`,
`test_gate_s4e_unclaim_keeps_park.sh`) — no regressions from the three insertion points.

## 4. Scope note

`s4e_dispatch_probe`'s own placeholder detection (used only by `assign`'s dynamic probe path) is
untouched and still correct; this cure adds a check *before* it, so `assign`'s existing dynamic probe
never even runs on a placeholder row now. `s4e_dispatch_gate` (next's post-claim probe, used by both the
ordinary and promotion paths) is also untouched — a placeholder row now never reaches it, because it
never gets claimed in the first place.
