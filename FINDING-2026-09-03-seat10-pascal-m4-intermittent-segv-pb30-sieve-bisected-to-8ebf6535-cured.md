# FINDING: `pascal-m4-intermittent-segv-pb30-sieve` is CURED — bisected to SCRIP `8ebf6535`, not merely absent

**Who/when:** seat10, 2026-09-03, FLEET-12, working row `pascal-m4-intermittent-segv-pb30-sieve` (baton
`/home/resources/postoffice/tasks/pascal-m4-intermittent-segv-pb30-sieve.task.md`).

## Why this needed more than a clean re-run

hq_B (2026-09-02, TRIO) already ran the row's DONE-WHEN 100x clean and explicitly declined to close the
row on that basis alone: *"a re-run-N-times pass proves absence of the symptom, not a fix; the owner
decides whether the mechanism was cured by a landed row ... and closes it, or tightens the criterion."*
This session did that decision-making, with a real before/after differential rather than another clean
re-run of the current tree alone.

## Method: bisect the candidate range, not just spot-check the endpoints

The original FINDING (`FINDING-2026-08-27-seat02-...md`) named the symptom (genuine non-determinism,
"memory layout / ASLR / adjacent-heap-state sensitive, most likely") but explicitly did no bisection —
row-factory discipline, mint don't cure inline. The sibling umbrella row `pascal-restore-prezeta` (closed
2026-08-30) landed three commits in the same `zd_plan`/ζ-window machinery between 2026-08-27 and
2026-08-29, and explicitly tracked pb30/sieve as **out of its own scope** throughout ("has its own FREE
row, do not re-chase it here" — its own STEP-1 measurement even names the class: *"M4 wobbles 120-121/154
... consistent with the known intermittent class, no new regression attributable to this fix"*, i.e. the
first of the three commits, alone, provably did NOT cure it).

Three candidate commits, in landing order:
1. `c2fa9bff` (2026-08-27 18:29) — `zd_nops()`: add `IR_BINOP_RELOP_VAL` to the 2-operand clause (ROOT CAUSE #1).
2. `8ebf6535` (2026-08-29 06:16) — `bb_binop_relop_val.cpp`: gate the ZD arm on `op_node_kind`, add a real
   value-producing arm instead of branch-and-bail semantics (ROOT CAUSE #2).
3. `ff1df778` (2026-08-29 17:47) — `zd_omega_head`/`zgpop`/`zwpop`: admit `IR_BINOP_TEST`, defer to a
   reconvergence-gated final pass (the `boolptr`/`boolidx`/`pb34` cure).

Built each in an isolated `git worktree` off `/home/claude10/SCRIP` (main tree left untouched throughout),
30 fresh compile-once-run-many-times repeats per program per commit (`echo 1 | ./<bin>`, byte-compared to
`.ref`), same methodology as the original FINDING and the row's own DONE-WHEN:

| Commit | pb30 | sieve | note |
|---|---|---|---|
| `809cade2` (parent of #1, i.e. **before** all three) | 2/30 ok, **28/30 SIGSEGV** | **30/30 SIGSEGV** | positive control — bug reproduces reliably, more severely than the original 2-5-run sample suggested |
| `c2fa9bff` (#1 alone) | 0/30 ok, **30/30 SIGSEGV** | **30/30 SIGSEGV** | ROOT CAUSE #1 insufficient — confirms `pascal-restore-prezeta`'s own contemporaneous read |
| `8ebf6535` (#1+#2) | **30/30 ok** | **30/30 ok** | clean — this is the cure |
| current `main` (post #1+#2+#3, this session's pristine build) | **100/100 ok** | **100/100 ok** | this row's own DONE-WHEN, run fresh this session |

**Bisection is precise, not a range**: #2 (`8ebf6535`) alone flips both witnesses from reliably-crashing to
30/30 clean. #3 (`ff1df778`, the `boolptr`/`boolidx`/`pb34` fix) was not independently tested in isolation —
unnecessary, since #2 alone already accounts for the full effect on both witnesses.

**Total clean runs on a post-`8ebf6535` tree, across three independent sessions, zero crashes:** hq_B's 120
(2026-09-02) + this session's 60 (the `8ebf6535` bisection point) + this session's 200 (current `main`,
this row's own DONE-WHEN) = **380/380**. Against the pre-cure measured rate (28/30 and 30/30, i.e.
90-100% crash-per-run), 380 consecutive clean runs is not a plausible run of luck.

## Mechanism (why this plausibly explains a *non-deterministic*, layout-sensitive SIGSEGV)

Per `pascal-restore-prezeta`'s own contemporaneous root-causing (its LEDGER, seat10-then session
2026-08-29T11:19Z and the block above it): pre-`8ebf6535`, `bb_binop_relop_val.cpp`'s ZD arm had
`IR_BINOP_TEST` branch-and-bail semantics (ω-exit on failure, raw operand-1 descriptor copied through on
"success") even though `IR_BINOP_RELOP_VAL` is a **value-producing** node — the box's other two arms
correctly always-γ and write a literal boolean. A value-producing relop taking a branch-and-bail exit
instead of writing its result is exactly the shape of bug that corrupts a stack slot's contents
conditionally on control flow rather than deterministically on the input — which is consistent with a
crash that depends on ambient stack/heap layout (ASLR, adjacent allocation state) rather than on program
input, matching the original FINDING's own hypothesis. `sieve.pas` (Sieve of Eratosthenes) is
relop-into-boolean-array-assignment-heavy — exactly `IR_BINOP_RELOP_VAL`'s shape — despite having "no
records, no by-value array params, no nested procedures," which is why the original FINDING correctly
ruled out `pascal-m4-registered-dispatch-segv`'s mechanism (frame overrun via array-by-value copy) but
didn't yet have a positive alternative.

## What was NOT done

No gdb/core-dump inspection of an actual pre-cure crash to name the exact corrupted address or
instruction — the bisection result is a black-box before/after causal proof (positive control + precise
single-commit flip + large-N post-cure confirmation), not a white-box one. `ff1df778` was not tested in
isolation (not needed to explain the observed effect; noted above). ASLR was not deliberately pinned
(`setarch -R`) since the effect was already unambiguous without it.

## Row disposition

Closing `pascal-m4-intermittent-segv-pb30-sieve` — mechanism identified, cure commit named, DONE-WHEN
re-verified passing on current `main` this session (see task file LEDGER). Not touching
`pascal-m4-registered-dispatch-segv` or `pascal-writeln-enum-iso-conformance-unresolved` here (this
session's other two assigned rows, worked separately).
