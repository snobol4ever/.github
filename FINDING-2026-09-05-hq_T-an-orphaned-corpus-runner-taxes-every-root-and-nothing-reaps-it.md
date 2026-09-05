# FINDING — an orphaned corpus runner taxes every root, and nothing on this box reaps it

**Seat:** hq_T (HQ-TEST) · **Date:** 2026-09-05 ~12:07–12:30 CDT (box clock) · **Mode:** QUARTET
**Found off:** seat13's follow-up on `ruling-supersede-fold-approved-with-a-bound`, reporting
`test_corpus_snobol4.sh` REFUSING rc=2 with 4 programs (m3=2 m4=2) killed at the per-program bound "under
continued fleet load (load avg 21 on 16 cores)".

## The claim

seat13 attributed the refusal to ambient fleet load. The load was real, but a measurable share of it was
**this root's own abandoned board runs**, and they were still running an hour later with nowhere to report.

## Measured

At 12:07 CDT, load average 17.82 on 16 cores. Three `corpus_suite_harness.py` runs of the SNOBOL4 master,
**all under `/home/claude_T`**, all reparented to `systemd --user` (ppid **2589**), i.e. their controlling
shell was gone:

```
 156058  2589  4529s  corpus_suite_harness.py run .../snobol4/ALL.sno --modes m3,m4 --by-modes-column
1313246  2589  1836s  (same)
1385017  2589  1659s  (same)
```

Each still held a live `scrip` child pinned at ~96% CPU (`test_parser_cf_loop.sno`,
`arbno_span_break_replace_branch_1.sno`). At 12:29 they were **95, 50 and 47 minutes old** and still going.

Their output goes nowhere a human will ever read it:

```
/proc/156058/fd/1 -> /tmp/tmp.eKpu4XYkpR      (mktemp scratch of a wrapper shell that has exited)
/proc/156058/fd/2 -> /tmp/tmp.Xm6fA9zvgI
```

## ⛔ Two corrections to the natural reading

**1. It is not "the fleet" — a large share of it was us.** Roughly three cores of permanent tax, paid by every
other root's suite run, sourced from this root. At the same moment the legitimately-parented runs
(`claude_P`, `claude_C`, `claude02`, `claude16`, `claude`) were each ~1 core and would finish.

**2. `TIMEOUT=600` was already in force, and that is what made it worse, not better.** Read off the orphans'
own environment (`/proc/<pid>/environ`): `TIMEOUT=600`. So the guidance seat13 offered as the remedy —
`TIMEOUT=600 bash scripts/test_corpus_snobol4.sh` — was exactly what these runs already had.

⭐ **The feedback loop, which is the actual finding:** a long per-program bound plus a cancelled session equals
an orphan; the orphan equals load; the load equals the *next* root's programs crossing *their* bound; that
refusal invites a re-run at a longer bound, which produces a longer-lived orphan the next time a session is
cancelled. **Raising the timeout does not make the board more likely to be measured — it makes an abandoned
board more expensive.** The bound that is missing is on the ORPHAN, not on the program.

## ⭐ Why nothing catches this

The per-program timeout is `subprocess.run(..., timeout=...)`, and it is working correctly — this was
*checked before it was asserted*: the children were **within** their 600s bound, not escaping it. There is no
defect in the timeout. There is simply **nothing anywhere that reaps a harness whose parent has died**: the
harness does not check for orphanhood, no runner sets a wall-clock ceiling on the whole board, and
`handoff_status.sh` does not look for stray runs from previous sittings.

A seat who cancels a board run — or whose session is ended for them, which under a mode change is routine —
leaves a process that will burn a core for as long as the box is up. Under QUARTET, where fleet seats are
being told to finish or park and stop, this is not a rare shape; **it is the expected shape of a mode
transition**, and three of them landed in one root inside two hours.

## ⛔ NOT CURED — the reap is blocked for this seat, and is escalated rather than worked around

`kill` is refused for this session by the harness's permission layer. The three PIDs above were still alive at
handoff. **This is escalated to Lon and named here so the next reader does not mistake the record for a
repair.** The mechanical cure is one line for whoever holds the permission:

```bash
pkill -f 'claude_T/SCRIP/scripts/corpus_suite_harness.py'      # or: kill -9 156058 1313246 1385017
```

## Proposed durable cure (unbuilt — a row, not a claim)

Two candidates, cheapest first, for `GOAL-TEST-SUITE-CONSISTENCY.md`:

1. **The harness reaps itself.** At each program boundary, `os.getppid() == 1` (or the recorded launch ppid is
   gone) ⇒ exit rc=2 with "parent gone, board abandoned". Costs one syscall per program and needs no
   coordination; it makes an abandoned board stop at the next program instead of at the last one.
2. **`handoff_status.sh` names strays.** A WARN listing any `corpus_suite_harness.py` under this root whose
   ppid is 1/2589 — the same shape as the `SCORE.md` staleness WARN it already carries. This turns a silent
   tax into something a seat is told about at the moment they are already reading a checklist.

Neither is built. Recording the shape is the deliverable here; the row is the next step.

## ⭐ The general form

**A measurement that is abandoned does not stop — it keeps costing, and it costs everyone except the seat that
started it.** Every "just re-run it at a longer timeout" is also a decision about what happens if that run is
never collected. Ask it of any long-running instrument: *if the session that launched this dies right now,
who notices, and who pays?*

Related, same session: [[FINDING-2026-09-05-hq_T-score-md-staleness-check-graded-a-column-no-hand-edit-touches]]
— found while checking seat13's premise that nobody had a clean corpus reading.
