# FINDING 2026-09-02 hq_B — THE "220 DROPPED QUEUE ROWS" ARE NOT DROPPED: THE CENSUS MEASURED THE BUFFER AND READ THE MEMORY AS LOSS

⛔⭐⭐ **`queue-index-restore-dropped-rows` (rank 0, ASSIGNED:hq_B, minted by ceo on Lon's 2026-08-30 health-check
"your system has gone corrupted") IS A PHANTOM. Nothing needs restoring. Executing its RESTORE instruction would
have re-created the exact failure LAW 4 exists to prevent.** Measured 2026-09-02; every number below is from a
command, none from the row's prose.

## THE CENSUS, AND WHAT IT ACTUALLY COUNTS

The row's DONE-WHEN counts `tasks/*.task.md` files having no row in **`QUEUE.tsv`**:

```
task files                     : 635      ⚠ snapshot -- read 634 four minutes earlier
rows in QUEUE.tsv              : 421      ⚠ snapshot -- read 420 four minutes earlier
task files without a row       : 214      (the GOAL's "220" was an 08-30 reading of the same thing)
```

⚠ **The two marked totals moved by +1 WHILE I WAS VERIFYING THEM** — FLEET-16 is live and ceo minted/assigned
a row between two runs of the same command. That is not noise to apologise for, it is the point: these are
snapshot counts of a file sixteen seats write to, and any number quoted from them is stale on arrival. **The
four that matter did NOT move and are the load-bearing ones** — orphans **214**, of which **206** are in
`QUEUE.done.tsv` (**327** rows) or `QUEUE.retired.tsv` (**3**), leaving **8**. Re-run rather than cite:
`ls /home/resources/postoffice/QUEUE*.tsv`.

That looks like catastrophic loss. It is not loss at all — it is **two other index files the census never opened**:

```
rows in QUEUE.done.tsv         : 327      <- 206 of the 214 are HERE
rows in QUEUE.retired.tsv      :   3
absent from ALL THREE indexes  :   8
```

## ADJUDICATING ALL 214 — EVERY ONE IS CORRECTLY ABSENT

**206 were swept to `QUEUE.done.tsv` by `s4e_msg.sh sweep`, and sweep cannot cull an unmarked row.** Its own
guard (`s4e_msg.sh:1437`): it moves a row only when `claims/<topic>.claim` contains `DONE` (`grep -q '^DONE$'`), it appends rather
than deletes, and it backs up the pre-sweep buffer. Twenty sweep events are stamped in the file, 2026-08-23
through 2026-08-28, each naming its actor and row count.

**The remaining 8, adjudicated one at a time from their own headers and receipts — none is a loss:**

| topic | verdict |
|---|---|
| `rebus-raku-loop-condition-hang-family` | `state: SUPERSEDED` |
| `raku-print-say-local-arg-marshal-bomb` | `state: SUPERSEDED` |
| `scrip-crashes-not-cleanly-on-unrunnable-input` | `state: SUPERSEDED` |
| `prolog-trail-heap-residency-storage-redesign` | SUPERSEDED — CLOSED-REFUSED by Lon |
| `icon-r0-bisect` | rename tombstone → `sn4-m1-r0-bisect` |
| `icon-bench-correct-zero-of-eight` | rename tombstone → `icon-bench-correct-suspend-residue` (ceo 2026-08-29) |
| `RETIRED-zeta-storage-two-of-four-broken` | `RETIRED-` filename prefix is the marker |
| `conform-opsyn-alias-define-proc-silent-wrong-m4-only` | `state: RESOLVED-BEFORE-CLAIM`, receipt in `FINDING-2026-08-27-seat06-opsyn-alias-dispatch-fixed-mode4-had-no-user-call-hook-and-two-more-gaps.md` |

**Genuine index losses: ZERO.**

## ⛔⛔ WHY EXECUTING THE ROW WOULD HAVE DONE REAL DAMAGE

Restoring 214 rows to `QUEUE.tsv` puts **206 landed rows back into the live dispatch buffer**. `sweep`'s own
header records what that costs, from the last time it happened: *"v1 reached 62% dead rows (112 of 181 DONE)
because nothing ever moved a landed row out, so the picker walked a graveyard and HQ re-dispatched finished
work."* The row written to repair the queue would have re-created the precise condition LAW 4 and `sweep` exist
to prevent — and under FLEET-16, with 16 seats picking from that buffer.

⭐ **The GOAL's stated premise is inverted.** It reasons from *"Absence != done (the index retains DONE rows by
design)."* The design is the opposite: **LAW 4 — the queue is a dispatch BUFFER, not a MEMORY** — and
`QUEUE.done.tsv`'s own header says it plainly: *"this file is the MEMORY, QUEUE.tsv is the buffer."*

⛔ **So the DONE-WHEN can never pass, and it fails harder the better the fleet does.** A landed row's baton stays
in `tasks/` while its row moves to the memory file, so "task files without a QUEUE.tsv row" is structurally
nonzero and **grows monotonically with every completed row**. It is not a corruption gauge; it is a rough count
of work finished. As a closure criterion it is unreachable by construction.

## TWO REAL DEFECTS FOUND WHILE DISPROVING THE ROW — both small, both worth fixing

1. **`QUEUE.done.tsv`'s header contradicts `sweep`'s own behaviour.** The header asserts *"A row here has a
   `claims/<topic>.claim` carrying DONE."* **Zero of the 206 do** — because sweep's step (b) then garbage-collects
   exactly those claims, by design and with a correct rationale (*"duplicated by QUEUE.done.tsv, so removing it
   loses nothing"*). The file states an invariant that the tool writing it deliberately breaks one step later.
   ⭐ This cost me a real detour: "0 of 206 rows have the claim the header promises" reads as proof of corruption,
   and it is proof of successful garbage collection. Fix the header, not the tool.
2. **There is no verb that can restore a row, so the row's own step 3 is not executable.** It says restore
   *"with `s4e_msg.sh mint`-shaped lines only through the one writer (never a hand-edited TSV under a live
   fleet)"* — but `mint` **REFUSES** when a task file already exists (`s4e_mint_dup`, `s4e_msg.sh:923-925`, checks the live row, the done row,
   and `[ -f "$b" ]` the task file itself), which is true for all 214 by definition. The verb list is
   `send ask check clear mailbox claim unclaim park done assign mint next banner fleet sweep board`: `sweep`
   moves rows out, and nothing moves one back. Had the census been real, the instruction for repairing it could
   not have been carried out.

✅ **The CLASS CURE the GOAL asks for is already implemented.** *"Rows may only ever LEAVE the index by being
MARKED, never removed"* is exactly what `sweep` enforces: DONE-claim required, append-only, buffer backed up,
and an explicit refusal to GC a claim that has **no** DONE latch (*"a live lock whose row was renamed or dropped
underneath it… REPORTED AND KEPT"*). No guard needs adding.

## THE GENERAL FORM

⭐⭐ **A census that names one store and concludes about the system will report the other stores as loss.** This
is the same instrument defect this fleet has now convicted four times in two days, and the third time in one
day where the instrument answered a **narrower question than the one asked** — `command -v` for "does it
exist", `.sno` for "how big is the corpus", `grep '\[rbp'` counting a bomb's own comment text, and now
`QUEUE.tsv` for "where are my rows". ⛔ The tell is identical every time: **the instrument is correct and the
question is wrong**, so the result is plausible, specific, and never announces its own scope. Before believing
a census that reports catastrophe, enumerate the stores it did **not** open — here, `ls QUEUE*.tsv` was the
whole investigation, and it takes one second.

⚠️ **Nothing here is a criticism of the row's author.** The 220 was real, reproducible, and alarming, and
minting a rank-0 row on Lon's health-check was the right response to it. The defect is in the criterion, which
nobody had re-derived since — which is exactly why it stayed rank 0 across a week of successful sweeps that
were each, silently, making its number worse.
