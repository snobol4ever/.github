# FINDING 2026-09-05 hq_P — eight trace rows were dispatched against a grader that was never pushed, and the miss reads as eight red rows

**Measured:** hq_P, 2026-09-05 10:30 CDT, SCRIP `04824a14b` → cured at `506e85ed3`, `.github` `a512031b`.

## What happened

The ceo minted eight SNOBOL4 TRACE rows (the trunk + six event rows + the csnobol4 &FTRACE row) on Lon's
2026-09-05 10:1x order. Every one of the eight DONE-WHENs is the same shape:

    cd "${S4E_HOME:-/home/claude}/SCRIP" && bash scripts/util_sno_trace_witness.sh <witness> "<must-print>"

The **ten witnesses** landed in `.github` at `a512031b` (`probes/trace/*.sno`). The **grader** did not:
`SCRIP/scripts/util_sno_trace_witness.sh` was still an untracked file in the ceo's own root
(`/home/claude/SCRIP/scripts/`), unpushed, when the rows were dispatched and the messages sent.

## Why it is worse than a missing file

On `origin/main` the criterion ran `bash scripts/util_sno_trace_witness.sh` against a path that does not
exist. `bash` exits **127**. The DONE-WHEN is `&&`-chained and its exit status is the row's verdict, so the
row reports **non-zero — exactly what a genuinely red row reports.** Eight rows in the hq_P lane would have
read as eight honest reds, and a seat picking one up would have gone looking in `src/runtime/core/core.c`
for a defect the instrument never got far enough to see.

⭐ **The shape is the one this project keeps paying for: an instrument that cannot run reports in the
vocabulary of a measurement that ran.** It is the same class as `command -v` for an oracle (answers *is it
on PATH*, read as *does it exist*), as the `.PHONY` target with no recipe (exits 0, reads as a green suite),
and as the `crosscheck/*.sno` glob that matched zero files and read as an empty corpus. Here the polarity is
red instead of green, which is *not* the safer direction — a false red costs a seat a whole session of
hunting, and it is indistinguishable from the work it was dispatched to do.

⛔ **A half-push is the specific hazard.** Both halves of an instrument crossing a repo boundary must land in
one dispatch, and the code repo must go first (RULES: push code repos, `.github` last). Here the order was
inverted: the `.github` half landed and the `SCRIP` half did not, so the failure was invisible from the side
anyone would check — the witnesses were all present.

## Cure

`SCRIP 506e85ed3` lands the ceo's grader unmodified, after hq_P proved it by execution: it runs, it refuses
`rc=2` correctly on a silent oracle, it falls back from the x64 fork (which refuses TRACE types with
ERROR 199 — hq_B's rank-0 row `snobol4-oracle-sbl-trace-dispatch-constants-fixed-in-the-fork-and-swapped`)
to the stock oracle with a printed NOTE, and it reports the trunk red in both modes.

## The measurement the cure made possible

All nine `util_sno_trace_witness.sh` arms at `506e85ed3`, incremental `make`, both modes: **RED everywhere,
`rc=2` nowhere** — so no row opens onto a broken instrument.

- **trunk** — m3 and m4 byte-identical to each other and wrong the same way (ONE defect in shared ground):
  trace function called with an empty tag, never for CALL/RETURN (2 events vs the oracle's 4), `&TRACE`
  reads 100 inside it and 100 at the end (oracle: 0 inside, 94 at the end), `TRACE('M','V')` registers
  nothing, and the surviving line prints the CSNOBOL4 shape where the oracle prints the banner. STOPTR works.
- **bogus type / undefined function** — both print `not reached` in both modes; ERROR 199 and ERROR 198
  never fire.
- **element** — m3 red by diff, but **m4 does not build at all** (`compile/assemble/link failed`). That is a
  second defect underneath the trace one: `.A[2]` / `.T['k']` name-of-element lowering fails in mode 4
  before any tap could fire. Recorded in that row's baton so its seat does not read it as trace work.
- **value sinks / ftrace** — these two pass no TRACE *type*, so the fork accepts them and they grade against
  `/home/resources/x64/bin/sbl` directly. Their refs will **not** move when hq_B's oracle fix lands; the
  other seven will.

## Routed

Trunk baton ledger (LANE REVIEW: seat07 keeps the row under FLEET-16 — the seat that locked it cures it, and
Lon's own word was "delegate fixes"); sequence lines written into all six event batons; seat07 messaged with
the pull-first instruction and the three facts it could not have known; ceo and hq_T told.
