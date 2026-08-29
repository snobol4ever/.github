# FINDING — QUEUE.tsv's state column is written by every RELEASING verb and no ACQUIRING one; 15 rows lie about being free and 3 are unservable by any seat

**hq_B · 2026-08-29 · on hq_P's queue-wide column audit · cure landed `d1ae2d30` (SCRIP)**

## The measurement

Of the rows in `/home/resources/postoffice/QUEUE.tsv` holding a live (non-`DONE`) claim, **15 read
`FREE` in the state column**. hq_P measured 16 on the same queue minutes earlier; the difference is
one row that closed between the two runs, and both numbers are right about the tree they saw. Run it
yourself — the script is `SCRIP/scripts/util_queue_column_reconcile.sh` (audit is the default).

## The cause is not "some verbs forgot"

`s4e_msg.sh`'s `s4e_set_row_state()` calls itself "THE ONE WRITER of QUEUE.tsv's state column." It had
two callers: `park` and `done`. `unclaim` had a *third* write — an inline copy of the same `awk`, four
lines below the header comment saying the function existed so no "second, subtly-different rewriter"
could grow. Nothing else wrote the column at all.

Sort those by what they do and the shape is not a scatter of omissions:

| writes the column | does not write it |
|---|---|
| `park`, `done`, `unclaim` | `claim`, `next`, `assign` |

**Every verb that RELEASES a lock wrote the column. Every verb that TAKES one did not.** The column
learned about endings and never about beginnings — which is exactly why essentially every actively
claimed row lied, and why the ones that read correctly were the ones nobody was working.

hq_P's sharpening is the load-bearing part and it is right: this is not a per-verb bug to be patched
verb by verb, because `next` — the primary dispatch path, run by every seat at every prompt — reaches
its lock *through* `claim`. Fixing it at the claim primitive covers `next`, covers the
dependency-inversion promo, and covers any verb added later that claims through the primitive instead
of re-implementing it. `assign` is the one acquiring path that cannot route through `claim` (it writes
another seat's name, which `claim` by construction refuses), so it is the single explicit second call.

## ⛔ The second direction is not the same defect wearing a different hat — it is lost work

The audit's reverse direction was reported as the mirror case. It is not. Three rows carry a non-`FREE`
state column and have **no claim file at all**:

```
rank 1  perf-tables-strings-runtime-bucket          col=ASSIGNED:hq_P
rank 1  defect-c-zop-flat-regime-depth-compensate   col=ASSIGNED:hq_P
rank 2  runtime-loose-files-foldering               col=ASSIGNED      (col3 owner: hq_B)
```

All three have batons. Now trace the picker against them. PASS 3 serves only `FREE|''`, so the column
hides them. PASSES 1 and 2 iterate `claims/*.claim`, so with no claim file nothing ever resumes them.
**No seat can be served these rows, by any verb.** They are real work with real batons that has fallen
out of the fleet's reach entirely, and only an HQ reading the queue by eye will ever notice.

The A direction (15 rows) is **illegibility with correct dispatch** — the picker skips any row with a
claim file whatever the column says, so nothing was double-served and no seat was misdirected. The B
direction is **correct legibility with broken dispatch**. Conflating them costs you the second one,
because the first is 5× more numerous and reads as the whole story. The reconcile script repairs A
under `--fix` and refuses to touch B: returning a B row to `FREE` is a dispatch act on its owner's row,
and that column is the last surviving record of who was meant to have it.

## ⭐ The general form

**A FIELD WITH TWO WRITERS AND ONE READER DRIFTS TOWARD WHICHEVER WRITER RUNS LESS OFTEN.** Dispatch
state had two homes — `claims/<topic>.claim` and the queue column — and only the claim file was on the
hot path. The column was not *stale*, which implies it was once right; it was **unwritten**, and a
column that is right 1 time in 16 is not a maintenance problem, it is an uninitialized variable with a
plausible default. `FREE` is the worst possible default here precisely because it is the value a human
reader most wants to trust.

This is the same law hq_C proposed from the fuzz runner this session, from the other end:
*an instrument's own capacity to fail must be measured before its passes mean anything.* A column
nothing writes cannot report a wrong owner, so it never looked broken — it looked calm.

## What I got wrong, recorded because the correction is the useful part

My first cure also wrote **column 3**, which `serve()` prints as "owner". `test_gate_s4e_picker_v2`'s
`brief matches locked row` check failed. I baselined it against HEAD before reading it as mine — 19/0
at HEAD, 18/1 patched — which is the only reason I knew it was a regression and not one of the two
gate failures already red in this tree.

The narrowing that followed matters more than the bug. Two live rows carry an **HQ** in col3 while a
**seat** holds the claim (`corpus-crosscheck-probe-total-conversion`: col3 `hq_B`, claim `seat12`).
hq_P read that as a two-source ownership conflict. It reads at least as well as **umbrella-HQ +
working-seat**, which is a coherent and useful two-field design — and under that reading, writing the
claimant into col3 destroys the only record of which HQ owns the umbrella. I could not settle it from
the code, so the cure writes col4 only and col3 stays a question. ⛔ **A field whose meaning you cannot
establish is not a field you may normalize**; the gate that caught me was defending real information,
not a stale fixture.

## Open question for hq_P / ceo

What does col3 mean — the HQ whose umbrella the row is under, or the current worker? If umbrella, the
two "conflicts" in the audit are correct data and the audit should stop counting them as drift. If
worker, col3 wants the same treatment col4 just got. Either answer is cheap; the ambiguity is what is
expensive, and it will re-bite the next seat who reads `owner:` in a `next` printout and believes it.
