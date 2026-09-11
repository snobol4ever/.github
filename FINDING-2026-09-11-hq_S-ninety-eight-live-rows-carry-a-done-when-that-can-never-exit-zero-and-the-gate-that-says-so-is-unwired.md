# FINDING — 98 live rows carry a DONE-WHEN that can never exit 0, the gate that says so is unwired, and 6 of them sit at rank 0 in the lane we are working today

**hq_S, 2026-09-11 00:0x UTC · SCRIP `21dd182ab` · corpus `bc1b1f900` · .github `d68cc7ada` · MODE NONET, THE ORDER OF WORK IS ICON ONLY**

Found while idle-checking a row I had just retired for the ceo, not while looking for this.

## The measurement

`scripts/test_gate_baton_donewhen_runnable.sh` exists, works, and **is wired into nothing** — not `make
test`, not `preflight`. Run by hand on this tree:

```
examined 1512 baton(s): runnable=1358  UNCLOSEABLE=154  WARN=0
GATE FAIL(1): 154 baton(s) carry a DONE-WHEN that can never exit 0 -- the row can never be closed
```

The 154 break down as **125 "DONE-WHEN IS PROSE (does not parse as shell)"**, **14 "first word is not a
command"** (a real command mangled — e.g. a DONE-WHEN beginning `-d);` where a `mktemp -d` was split), and
**1 with no DONE-WHEN line at all**.

⛔ **154 IS THE WRONG NUMBER TO ACT ON, AND THAT IS THE POINT OF THIS FINDING.** Most batons are for rows
long since done, where an unrunnable criterion costs nobody anything. Cross-referencing every uncloseable
baton against `QUEUE.tsv` for rows a picker can actually serve — state `FREE` or `CLAIMED:` — gives the
number that bites:

| | count |
|---|---|
| uncloseable batons, all states | 154 |
| **on rows that are LIVE (FREE or CLAIMED)** | **98** |
| of those, at **rank 0 or 1** — the ranks the picker reaches first | **55** |
| of those, **icon-lane, i.e. servable TODAY under ICON ONLY** | **15** |
| **at rank 0 AND icon-lane — servable on the very next `next`** | **6** |

By owner, of the 98: hq_T 28 · hq_B 14 · hq_P 13 · hq_U 11 · hq_C 8 · hq_V 6 · hq_S 6 · hq_I 6 · hq_R 5 ·
coo 1. **Every seat, including the one writing this.**

The six at rank 0 in today's lane:

```
flip-icon-set-generation-survives-deleting-the-element-just-produced          (hq_C)
icon-assignment-through-a-substring-or-element-variable-lvalue-aborts-the-emitter (hq_B)
icon-jcon-evalx-segfaults-both-modes-where-iconx-runs-it-clean                (hq_C)
icon-jcon-score-md-summary-row-and-vendor-cell-disagree-...                   (hq_I)
icon-keyword-assignment-beyond-pos-and-random-bombs                           (hq_B)
icon-scan-match-box-hands-memcmp-a-bad-pointer-or-length-record-every-replace-12 (hq_U)
```

⛔ The second of those, `icon-jcon-evalx-segfaults-both-modes-where-iconx-runs-it-clean`, is **the topmost
free row on the entire bus** as this is written — `next` names it as the head of 828 skipped free rows.

## Why it matters more under the pace order than it would have last week

Lon's standing order is ten bugs an hour across nine fixers, each holding one bug and **recording the flip
when its DONE-WHEN goes green**. A seat served a row whose DONE-WHEN cannot exit 0 can cure the defect
perfectly and still have nothing to record: `done` cannot pass, so the flip never lands in the histogram
the ceo reads every tick. **The metric under-reports exactly the seats doing the work**, and it does so
silently — the seat sees a cure, the board sees nothing, and neither sees why.

⭐ **AND IT IS THE SAME SHAPE AS THE TWO OTHER BUS DEFECTS FOUND TODAY**, which is the reason to write it
down as a class rather than a chore. The language freeze read a row's language from its slug and served
parked work; CEO-544's retirement was broadcast but never applied to `QUEUE.tsv`; and here a criterion is
minted as prose and nothing ever asks whether it runs. All three fail **open** — they hand a seat work it
cannot finish or should not have — and all three are invisible **to the seat being served**, because a
seat that is handed a row does not audit why it was handed one. The instrument that would catch each one
either did not look at the right operand, or was never wired.

## The cure, and the order it has to happen in

⛔ **DO NOT SIMPLY WIRE THE GATE.** It reads red at 154, so wiring it today reds `make test` for all nine
seats over debt none of them created this sitting — punishing the next person to run the build for a
backlog, which is how a true gate gets disabled instead of satisfied.

The sequence that works, and it is this tree's own established shape:

1. **Wire it as a RATCHET**, today's 154 as the ceiling, the way `test_gate_gate_wiring_ratchet.sh` and the
   other `*_ratchet.sh` gates already work: red only if the count goes UP. That stops the bleeding in one
   landing and costs nobody a red build.
2. **Each seat fixes its own live rows** — the per-owner column above is the work list, and it is six to
   twenty-eight one-line edits per seat, not a project. Priority is the 55 at rank 0/1, then the rest.
3. **Drop the ceiling to 0 and make it a hard gate** once the live rows are clean. Batons for rows already
   done can be exempted by state rather than fixed, if the ceo prefers — but that is a ruling, not a
   seat's call, because it changes what the gate means.

⛔ **hq_S CANNOT PAY ITS OWN SIX, AND THE REASON IS WORTH RECORDING RATHER THAN LOOKING LIKE A DODGE.** All
six of mine are SNOBOL4 rows (`snobol4-an-unresolved-return-label-dumps-core...` at rank 0, and five more).
Writing a *runnable* DONE-WHEN for them means proving it runs and reads RED, which means running SNOBOL4 —
and the standing order is that the SNOBOL4 suites are not run at all. A DONE-WHEN written but never proven
red is the placeholder problem in better clothes, so writing one anyway would satisfy the gate and not the
purpose. **My six are payable the hour the freeze lifts, and not before.** Named here so nobody reads the
per-owner table as me exempting myself.

## Owner

The ceo, to rule on the ratchet and on whether done-row batons are exempted by state. The per-seat fixes
are each seat's own. hq_S found and measured it and will take the ratchet landing if the ceo wants it here.
