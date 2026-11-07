---
name: fleet-ops-industry
description: Industry practice for many agents on one box and repo: jobserver, cgroups/PSI, semaphores, leases, merge queues, affected sets, flakes, DORA; each mapped to a box-scheduler step. Load before designing a fleet mechanism.
---

# Fleet operations: what the industry already solved (the cio, 2026-11-04; Lon: "consolidate industry best practices regarding load management of build and test systems, on concurrent development using a single repo, how to share and queue ... let's get grounded in what's possible")

The sources, with what each was read for and how far to trust it, are in `reference.md` beside this file. A claim marked VERIFY there was read from a secondary source. Every mechanism below ends with OURS (the step or instrument that adopts it) and GAP (what we still do by hand or not at all).

## 1. One box, shared compute: weights, quotas, pressure, a controller

The detail is `reference.md`, the section of the same number (the summary that stood here was folded into it 2026-11-07; the map in section 8 is what a design reads first).

## 2. Build load: one compile budget, caches that cannot lie

The detail is `reference.md`, the section of the same number (the summary that stood here was folded into it 2026-11-07; the map in section 8 is what a design reads first).

## 3. Admission and queuing: slots by class, fair share, leases

The detail is `reference.md`, the section of the same number (the summary that stood here was folded into it 2026-11-07; the map in section 8 is what a design reads first).

## 4. Concurrent development on one repo

The detail is `reference.md`, the section of the same number (the summary that stood here was folded into it 2026-11-07; the map in section 8 is what a design reads first).

## 5. Test selection and reliability

The detail is `reference.md`, the section of the same number (the summary that stood here was folded into it 2026-11-07; the map in section 8 is what a design reads first).

## 6. Outcomes, toil, automation that proves itself

The detail is `reference.md`, the section of the same number (the summary that stood here was folded into it 2026-11-07; the map in section 8 is what a design reads first).

## 7. Many agents, one repo (the newest literature, thin and vendor-heavy)

The detail is `reference.md`, the section of the same number (the summary that stood here was folded into it 2026-11-07; the map in section 8 is what a design reads first).

## 8. The map

A step's state is its probe, never a column here: `bash harness/scripts/test_design_box_scheduler_steps.sh --list` and `--step N` (fleet-queue, box-budget, test-cycle and skills-complete likewise, each by its own harness). The 2026-11-04 state column is gone (the cio 2026-11-07: it read open for steps that had been green for days).

| industry mechanism | box-scheduler step |
|---|---|
| make jobserver shared box-wide | 1-2 |
| PI-like controller, dead band, rate limit, per-slice PSI | 3-6, 26 |
| grader as a service with an SLO | 5 |
| sweep closes green, retires refusing, escalates stale (lease expiry, DLQ) | 8, 9 |
| Stop hook as the wake (auto-remediation with a cool-down) | 10 |
| one verb per ruling (a record written once) | 12 |
| change-impact proof, blast-radius query | 13, 24 |
| MODE and batons capped, archives | 14, 15 |
| RESUME line (a lease's heartbeat for the seat's own state) | 16 |
| RULES index, redirect map, ruling by number | 17, 30 |
| landing command as a serial merge queue; generated tables regenerated | 18, 19 |
| red set per origin hash (culprit attribution) | 20 |
| claim notice by touched-path overlap (ConE) | 21 |
| background handle, kill only your own (a lease with an owner) | 22 |
| done holds the identity only for its write (lock only for the write) | 28 |
| GNU grep in the seat shell as in bash -c | 29 |
| park on a request id; next in assign order and writes nothing; mint writes a real NEXT; premise budget; done unblocks; worktree helper; banner once; sweep selection | 31-38 |
| outcome ledger with bars; the controller's lap | 39, 40 |

## 9. What we do not do, knowingly

Distributed compilation (one box); predictive (ML) test selection (the affected set from the graph is enough at our size); a hosted remote cache (the FETCHED cache is local); gang scheduling; a true merge queue with speculation (a serial landing command with a pre-push combined-state check is the right size); Redlock-style multi-node locks (one box, one filesystem, `noclobber` and a token suffice).
