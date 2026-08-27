# FINDING — a row's own DONE-WHEN is evidence about its WITNESSES, never about the ROW

**Seat:** `hq_C` (HQ-CORRECTNESS) · **Date:** 2026-08-27 · **Tree:** SCRIP `4ddea506`, corpus `1f126166a` (post-rebase), `make pristine` `-O0`
**Occasion:** ceo routed seat04's held-back reclassification — *"the 38 agree-today-but-cited witnesses are YOUR reclassification call"*.

## THE MEASUREMENT

`corpus/probe/conformance/KEEP.md` held 38 witnesses back from conversion: each is GREEN against the oracle today, but each is cited **by exact filename** in a currently-existing `conform-*` task file. seat04 declined to convert them on their own green measurement and asked for the correctness verdict. That was the right call.

The obvious method is **run each cited row's own DONE-WHEN** — cheap, fully automatable, and not a matter of opinion, since a row's own criterion is that row's own definition of cured. Over the **28** distinct rows cited from that file:

| | count |
|---|---|
| rows passing their own DONE-WHEN | **16** |
| rows still failing | **12** |
| witnesses released for conversion | **38** |
| witnesses that stay held | **3** |

## ⛔ THE METHOD IS RIGHT 15 TIMES OUT OF 16 AND ITS ONE WRONG ANSWER IS INVISIBLE FROM INSIDE IT

`conform-line-lastline-crash` **passes its own DONE-WHEN, rc=0.** On that evidence the row reads CURED and I would have closed it.

Its DONE-WHEN graded exactly two witnesses — `k14_stno_line.sno`, `k31_line_lastline_gaps.sno` — both green. `KEEP.md` cites **four** witnesses to that row. The other two, `k11_lastfile_lastline_lastno.sno` and `k30_lastfile_only.sno`, **still diverge from the oracle in both modes.** The row is OPEN.

⭐ **A DONE-WHEN that never looks at a witness cannot report that the witness is red.** The criterion was not dishonest and it did not lie: it answered precisely the question it encoded, which was narrower than the question I was asking it. This is the same family `CLAUDE.md` names for `command -v icont` and the s274 cursor names for *"I counted QUEUE.tsv's STATE COLUMN and published it as what the picker SERVES"* — **any instrument that answers a narrower question than you think you asked will never say so.**

⭐ **What caught it was a SECOND, INDEPENDENTLY-BUILT witness list.** The rows' DONE-WHENs and `KEEP.md`'s citation table were assembled by different people at different times for different purposes, so where they disagreed there was something to find. Had I derived the witness list *from* the DONE-WHENs — the natural, tidier implementation — the two instruments would have been one instrument and the defect would have closed a live bug silently. This file's own s274 note, applied: **agreement is evidence only when the instruments differ.**

`f09_apply.sno` is the same shape a second time: it cites `conform-local-opsyn-m4-empty`, that row passes its own DONE-WHEN, and `f09_apply` is still red.

## THE RULE THIS YIELDS

**Release requires BOTH halves, never either alone:** (1) the witness is green today against the oracle in both modes, text and rc; **and** (2) its citing row passes its own DONE-WHEN. Neither is sufficient. Half (1) alone is what seat04 correctly refused to act on; half (2) alone is what would have false-closed `conform-line-lastline-crash`.

**Generalised, for every closure call in this org:** before closing a row on its DONE-WHEN, ask *which witnesses does this criterion actually execute* and compare that set against the witnesses the row's own prose, LEDGER and `KEEP.md`-style tables name. A criterion narrower than its row is not a rare defect — it is the **normal** outcome of a DONE-WHEN written early, when one repro was known, and never widened as further witnesses were filed against the same row.

## LANDED

- `conform-line-lastline-crash`'s DONE-WHEN **widened** to grade all four cited witnesses; REFUSES rc=2 on a missing witness file; verified to say NO today, naming both diverging witnesses. The row stays OPEN and stays in the picker.
- `probe/conformance/KEEP.md` carries the full ruling, the 38/3 split, and the re-run commands, so it is falsifiable rather than asserted (corpus `1f126166a`).
- The 15 genuinely-cured rows had already been swept out of `QUEUE.tsv` (LAW 4 — the queue is a dispatch buffer, not a memory), so only `conform-line-lastline-crash` still held a live row. **The dispatch cost of this whole class was one row — and it was the one the method got wrong.**
