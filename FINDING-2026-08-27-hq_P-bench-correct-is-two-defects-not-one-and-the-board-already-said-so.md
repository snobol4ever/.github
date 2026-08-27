# FINDING — `bench_correct` 0/8 is **TWO** defects, not one, and the row's own board already separated them

**Seat:** `hq_P` s277 · **Date:** 2026-08-27 · **Mode:** FLEET-8
**Row:** `icon-bench-correct-zero-of-eight` (hq_P) · weight 15, the largest Icon lever
**Claim under test:** the row's own, verbatim — *"ROOT-CAUSED. **A procedure containing `suspend` is emitted with NO
ACTIVATION FRAME** … There are FIVE SIGSEGV, ONE HANG, and two RUNAWAY, and they are **ONE defect**."*
**Verdict: ⛔ the "one defect" scoping is over-broad. Four of the eight contain no `suspend` anywhere.**

## Measured

`grep -cw suspend` over each program **and every file it `link`s** (`options.icn`, `post.icn`, `shuffle.icn` — all
three contain **zero** `suspend`):

| program | `suspend` in program + links | row's verdict | row's "good lines before death" | oracle |
|---|---:|---|---|---:|
| `concord` | **1** | SIGSEGV | 3 | 1345 |
| `geddump` | **5** | SIGSEGV | 0 | 12568 |
| `ipxref` | **1** | SIGSEGV | 0 | 1230 |
| `tgrlink` | **6** | SIGSEGV | 2 | 3239 |
| `rsg` | **0** | SIGSEGV | **5000 — byte-identical to the oracle**, dies on 5001 | 5000 |
| `micsum` | **0** | HANG | 1 | 2 |
| `deal` | **0** | RUNAWAY | — | 17000 |
| `queens` | **0** | RUNAWAY | — | 16653 |

## ⭐ The row's own data already separated the two classes, and it was read as one

The split on `suspend` presence is **exactly 4/4**, and it lines up **perfectly** with the board's existing
"good lines before death" column — a column the row already had written down:

- **`suspend` present (4):** 3, 0, 0, 2 good lines. These die **immediately**, on first call — consistent with the
  stated mechanism (a generator procedure gets no activation frame and `ret`s through a clobbered γ).
- **`suspend` absent (4):** **5000 correct lines**, 1 line, and two runaways. These run **correctly and at length**,
  or over-produce. Nothing about "the generator procedure crashes on first call" describes a program that emits 5000
  byte-identical lines and then fails, or one that never stops.

⛔ **So the diagnosis provably cannot apply to `rsg`, `micsum`, `deal`, `queens`** — there is no procedure containing
`suspend` in them to be emitted without an activation frame.

⚠️ **What this does NOT say.** Icon's *built-in* generators (`!x`, `i to j`, `every`, string scanning) suspend at the
machine level too and lower to the same Byrd boxes, so the four may still fail through generator machinery — possibly
even a related cause. But that is **not** the mechanism the row names, and it is **not** what N-2 repairs. The two must
not be merged again on a resemblance.

## Consequence for N-2 and for this row

⛔ **N-2 landing should be expected to move AT MOST 4 of 8, not 8 of 8.** The row's standing instruction —
*"expect them to move with N-2 too"* for the HANG and the two RUNAWAYs — is an **expectation with evidence now against
it**, and it was never measurement (the row says so itself: `rsg` "proves the family" was an inference from one
program's shape).

⭐ **This matters beyond the count: it protects N-2's own verdict.** If N-2 lands and `bench_correct` reads 4/8, that
is **success at full predicted yield**, not a half-failure — and without this finding the obvious reading would be
"N-2 didn't work," followed by a hunt through generator codegen for a bug that is not there.

## Method and its limits

Direct token count over source and linked libraries; the `link` set was read from each program's own `link` lines.
⚠️ The host/callee scan used alongside this (below) is regex-based and can over-count a call (`name(` matches any
call-shaped token), so its per-callsite lists are indicative, not exact; the `suspend`-presence count is exact.

## Bonus, same scan — the forward-reference hazard is LIVE in this corpus

For N-2 item 2 (host reserves the callee's compile-time frame bytes), I flagged a hazard: the favourable
"procs emitted before `main`" order does not generalize to a host that is itself a proc calling a generator declared
later. **Measured here: it is live.** `geddump` has **6** such callsites (`event→gedval`, `gedload→gedwalk`,
`gedscan→gedwalk`, `gedwalk→{gedref,gedsub,gedval}`) and `tgrlink` has **2** (`loadfile→kgen`, `dumpcode→aseq`).
⛔ **So item 2's pre-pass (or loud refusal) is MANDATORY, not optional** — the `main`-host case is not representative
of the very corpus this row scores.

## Transferable lesson

⭐ **A board that records a per-row detail column has already done the discriminating; the failure was not measuring
but READING.** "Good lines before death" separated these two classes perfectly the day it was written, and the row
carried "they are ONE defect" above it for three sessions. ⛔ When a diagnosis claims N cases share one mechanism,
test the mechanism's *precondition* against each case — here a one-line `grep` per program — before the count is
allowed into a yield estimate.
