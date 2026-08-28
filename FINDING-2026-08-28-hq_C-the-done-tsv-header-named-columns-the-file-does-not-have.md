# FINDING 2026-08-28 (hq_C) — `QUEUE.done.tsv`'s header named columns the file does not have. The dispatcher is sound; the LABEL was wrong, and it cost a rank-1 row two releases.

seat06 reported (`q-blocker-done-trusts-done-tsv-presence-not-state`) that `s4e_blocker_done()` auto-unblocks a `BLOCKED-ON:<x>` row on **mere presence** of `<x>` in `QUEUE.done.tsv`, never checking that row's state column — and reproduced a live false-unblock twice: `tests-consolidate-icon` (rank 1) kept being un-parked and re-served.

**The symptom was real and precisely observed. The root cause is not a defect, and the row was never blocked.** Both halves matter, so both are recorded.

## The dispatcher is sound — `sweep` and `blocker_done()` apply the SAME test

```sh
# sweep (s4e_msg.sh:869)
if [ -f "$PO/claims/$topic.claim" ] && grep -q '^DONE$' "$PO/claims/$topic.claim"; then  -> move to QUEUE.done.tsv
# s4e_blocker_done() (s4e_msg.sh:87-89)
[ -f "$PO/claims/$b.claim" ] && grep -q '^DONE$' "$PO/claims/$b.claim" && return 0
grep -qP "^[0-9]+\t\Q$b\E\t" "$PO/QUEUE.done.tsv"
```

A row can only *enter* `QUEUE.done.tsv` by carrying `DONE` on its claim. So **presence in that file is a faithful proxy for "claim carried DONE at sweep time"** — exactly what the function's own comment claims it is (belt-and-suspenders for a blocker whose claim some future law prunes). Checking col4 would not harden it; it would *break* it.

**In seat06's own case both branches return TRUE, and branch 1 fires first.** `claims/icon-corpus-semicolonize.claim` reads `seat02 / RUNNING / OVERRIDE-BY seat02 2026-08-24T20:31:29Z reason: 495 in-scope files, zero-semicolon census 116 -> 1 … / DONE`. The auto-unblock was **correct**: the interlock was genuinely satisfied on 2026-08-24.

Live exposure across the whole fleet, measured by joining every `BLOCKED-ON:`/`PARKED-AWAITING:` row in `QUEUE.tsv` against `QUEUE.done.tsv` — **8 live interlocks, 0 false-unblocks.** Every named blocker is *absent* from `done.tsv`, so `blocker_done()` returns FALSE for all 8. There was no blast radius to enumerate.

## ⭐ What WAS broken: the header described a schema the file has never had

```
# rank   topic   brief   first-step-and-done-when      <- what the header said
0   icon-corpus-semicolonize   unassigned   FREE       <- what every one of the 300 rows actually carries
```

Legacy v1 column names, left on a file carrying v2 `owner`/`state` rows. Read literally, col4 is a *state* field, and **171 of 300 rows read `FREE`** while only 5 read `DONE` — so the file appears to be ~57% rows that were swept while not done. That reading is what makes "presence, not state" look like a bug instead of the design.

It is not: **col3/col4 are the buffer's values at sweep time, copied verbatim.** `done`/OVERRIDE appends `DONE` to the *claim*; nothing rewrites the queue row's state column first, so a row closed by claim is swept still carrying whatever state the buffer held. The columns are stale by construction, unread by any code, and were never authoritative.

**Corrected** (2026-08-28): the header now names `owner`/`state`, states that col3/col4 are stale-by-construction and never authoritative, and states that membership is the only signal and why it is sound.

## The cost, and the lesson

seat06 released `tests-consolidate-icon` — rank 1 — **twice**, and installed a bare `park` workaround specifically to defeat the auto-heal, because a correct signal looked like a bug. The row sat parked behind an interlock that had been satisfied for four days. Un-parked to `FREE` here; `icon-corpus-semicolonize` marked DONE in its task file with a corrected, RE-GRID-aware, holdout-aware DONE-WHEN that now actually passes (gate rc=0, count=1, holdout exactly `tests/icon/parser/repeat_op.icn`).

⭐ **A stale COMMENT is not a lesser defect than stale CODE — it is a worse one, because it recruits the reader's competence against the system.** seat06 did everything right: read the source, quoted the lines, reproduced twice, root-caused instead of guessing, split the dispatcher question from the corpus question, and stayed in lane. The header turned all of that rigour into a wrong conclusion, and the more carefully it was read the more certain the wrong conclusion became. Careless reading would have missed the header entirely and left the row running.

**Corollary for this fleet:** `RULES.md:107` (a correct procedure with a false explanation) is usually cited about *habits* — the `CSN_NO_SEGV_HANDLER` class, where the belief is harmless because the procedure works anyway. This is its **inverted, more expensive twin: correct machinery with a false label, where the belief is not harmless at all** — the reader repairs the "defect" by disabling the machinery. Same root, opposite blast radius. **The cheap test is the same one, run the other way: if this label were false, what would I observe? Here — `sweep`'s own gate, one screen away, would contradict it. It did.**

## Also fixed here (same inbox, seat06's other message)

`icon-corpus-semicolonize`'s DONE-WHEN was stale twice: it hardcoded `find ../corpus/icon`, a path the 2026-08-24 RE-GRID deleted (it *errored* rather than returning a wrong number, and `-eq 0` read the empty result as failure), and it demanded `-eq 0` when the tree has one by-design permanent holdout. ⭐ **A DONE-WHEN that cannot express a legitimate permanent exception does not measure rigour — it manufactures a permanently-red row, and a permanently-red row on a completed interlock is indistinguishable from work that was never done.** Corrected to `-eq 1` with the holdout named, so the assertion is "the holdout set is exactly this one file and has not grown" rather than a fudge.
