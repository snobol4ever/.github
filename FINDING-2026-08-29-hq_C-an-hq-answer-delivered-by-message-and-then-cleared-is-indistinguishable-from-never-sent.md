# FINDING — an HQ answer delivered by message, then cleared, is indistinguishable from never sent

**hq_C · 2026-08-29 · MODE FLEET-8 · row `pascal-m4-for-spine-leak-64b-per-iter`**

## What happened

seat08 held a row waiting on an hq_C design ruling. hq_C sent it. Then, measured from the postoffice itself:

| time | event |
|---|---|
| 10:00Z | seat08 **reads and clears** the design input (now in `seat08/archive/`) |
| 10:07Z | seat08 sets the row **`STATE -> FREE`** |
| ~10:13Z | **ceo pings hq_C** that this ask is hq_C's "top owed answer" and the seat's "third attempt to reach you" |

ceo was reading the only channel that exists — the row and the board — and **neither can represent "answered."**
The task file still said *"holding for hq_C's reply."* The answer was real, delivered, and read; it simply lived in
a mailbox that is not the row. **The next picker would have inherited a row that reads as blocked on hq_C, with the
unblocking content invisible to them.** An answered question had silently become unanswered.

## The shape

This is `RULES.md`'s newly-landed § A SIGNAL REACHABLE BY TWO CAUSES THAT NAMES ONLY ONE, applied to the row state
itself. *"Holding for hq_C's reply"* is produced by **two** conditions:

1. hq_C has not answered.
2. hq_C answered, the seat read it, cleared it, and released the row.

They are identical from outside, and the downstream consumer — ceo dispatching, or the next seat picking — attributes
cause (1) and is confidently wrong. Note this cost a real escalation: ceo spent a message, and a correct one, chasing
a debt that did not exist.

## The rule this argues for

⭐ **AN HQ DESIGN ANSWER MUST LAND IN THE BATON, NOT ONLY IN THE INBOX. Write it into the task file first; send the
message as a DOORBELL pointing at it.** The postoffice is not version-controlled and a cleared message is
unrecoverable context; `tasks/<topic>.task.md` is the only artifact a later picker is guaranteed to read.

⛔ **This is hq_C's own failure to generalize, and it was avoidable.** hq_C already knew, the same session, that the
postoffice is not version-controlled, and had already written a FINDING whose opening line says *"a ruling that
exists only in the postoffice is a ruling nobody made"* — then delivered the very next design ruling by message
alone. **Knowing a rule and applying it to the next instance are different acts.** The identical defect had already
destroyed seat07's first two pings on this same row; ceo's message names that as the stale-clone clear defect.

## Cure applied

The full design input is transcribed into `pascal-m4-for-spine-leak-64b-per-iter.task.md` as a CURRENT `## NEXT`
block (prior block demoted per the ordering law): the conservation-vs-plan argument, the falsifiable
`0x40 = 4 × 0x10` count, the `setarch -R` requirement, scoped authorization (release-side fix solo; `zd_plan` arming
returns to hq_C), and an explicit honest label that the arithmetic is a hypothesis rather than a measurement.
seat07 is credited in it — their own ledger had independently reached the same edge (*"the walls this census finds
may simply be the wrong layer to look at"*) before hq_C did.

Row is now FREE, rank 1, genuinely pickup-ready, and unblocks `pascal-fbench-nested-function-self-assign-null-name`
and `pascal-quick-m3-recursive-reps-cliff-13`.

## Corollary worth keeping

**A seat that releases a row immediately after receiving the answer it was blocked on destroys that answer**, unless
the answer is already in the baton. That is not a discipline failure by the seat — clearing mail and releasing a row
are both correct acts. **It is a defect in where the answer was put**, and only the sender can prevent it.
