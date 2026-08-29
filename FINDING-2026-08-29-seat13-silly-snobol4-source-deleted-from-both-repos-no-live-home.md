# FINDING — SILLY SNOBOL4's entire C source tree (25 files, ~3 months of real translation work)
# has been deleted from BOTH SCRIP and corpus today, with no live home in either

**seat13 · 2026-08-29 · surfaced while working `goal-files-major-consolidation`** (was about to fold
`GOAL-SILLY-{COMPLETE,SWEEP-FORWARD,SWEEP-BACKWARD,SYNC-MONITOR}.md` into a new living `GOAL-SILLY-100.md`
— stopped short of landing that once this turned up, see disposition below)

**Not fixed — this is a "did we just lose work" flag, not a routine stale-path correction.**

## What happened, exact commits

Three commits, same morning, ~6 minutes apart, all under the standard `LCherryholmes` identity (so this
is a real session's action, not a config/attribution anomaly):

1. **corpus `29e47ac16`** — "miscellaneous/SILLY: add, relocated here from SCRIP/SILLY" — the 25-file
   `SILLY/` C tree lands in `corpus/miscellaneous/SILLY/`.
2. **SCRIP `ee0f1508`** (2026-08-29 09:50:49 -0500) — "Remove SILLY: relocated to corpus/miscellaneous/
   SILLY" — deletes `SCRIP/SILLY/` (25 `.c`/`.h` files + `Makefile`), commit message asserts the corpus
   side is the new home.
3. **corpus `e42689daf`** (2026-08-29 09:56:48 -0500, **6 minutes later**) — "Delete miscellaneous/SILLY:
   C source does not belong in corpus" — deletes the very copy commit 1 just created.

**Net effect, verified against a fresh pull of both repos just now: `SILLY/` does not exist anywhere in
either repo's live tree.** `find . -iname "*silly*"` in SCRIP turns up only two now-dangling scripts
(`scripts/build_silly_snobol4.sh`, `scripts/test_ss_monitor_silly_vs_csnobol4.sh`, both still hardcoding
`$ROOT/SILLY`) and `test/ss-monitor/inject_silly.py` (a consumer, not the source). `corpus/miscellaneous/`
itself no longer exists at all (empty after the delete). This is not a rename I failed to find — `git log
--all --oneline -i --grep=silly` in both repos shows exactly these three commits as the full recent
history; nothing re-adds it anywhere afterward.

**Each individual call is locally defensible** (SCRIP: "not part of the active compiler tree, doesn't
belong here" — true, it's a standalone oracle-building side project; corpus: "C source doesn't belong in
a test-corpus repo" — also a reasonable general policy). **The problem is the two calls, made 6 minutes
apart presumably by different sessions with no visibility into each other's intent, composed into total
deletion with no third location ever chosen.** Neither commit message shows awareness that the other
repo's copy might not be a safe permanent home — the SCRIP-side message treats the corpus add as durable;
the corpus-side message doesn't acknowledge it's deleting the only remaining copy.

## Why this matters right now

This is real, substantial, independently-useful work, not dead scaffolding: `GOAL-SILLY-SWEEP-FORWARD`/
`-BACKWARD`'s own survey verdicts (this same task file's history, read in full before writing this)
confirm — as of TODAY, before the deletion — a clean 0-error/0-warning build and genuine 3-way-verified
translation progress (forward watermark to v311.sil line 6927, backward to line 6427, ~55% by line count).
`GOAL-SILLY-COMPLETE.md` shows a detailed, specific, nearly-finished Phase-1 gap list (8 of 10 items
independently confirmed still-open by direct code reading, not just a checklist). This is the kind of
loss that's cheap to fix in the next few hours and expensive to notice in a few weeks once nobody
remembers which commit to `git show`.

## Recovery is trivial right now, and gets harder to trust over time

```bash
# SCRIP: last commit with SILLY/ present
git show ee0f1508~1:SILLY/main.c   # (or any file) -- confirms content still recoverable
# full tree recovery, either repo works as a source:
git checkout ee0f1508~1 -- SILLY/          # in SCRIP
git checkout 29e47ac16 -- miscellaneous/SILLY/   # in corpus (same content, pre-delete)
```
Both repos' reflogs/history are intact as of this session — recovery is a two-command operation today.
It will not stay that trivial forever (history can be pruned, and institutional memory of "check these two
specific hashes" fades fast in a fleet this size).

## Disposition — routed, not decided unilaterally

This is exactly the row's own INTERLOCK (d) shape (`goal-files-major-consolidation` task GOAL text: "a
design idea's merit call that is genuinely reserved... routes per the reserved-question law — ASSIGNED
asks, never dropped") — **whether SILLY gets restored (and to which repo, permanently) or is deliberately
abandoned is not this session's call.** Not restoring it myself: that's a real decision (pick a permanent
home, possibly re-open a currently-closed question about whether a hand-written oracle-comparison tool
belongs in either repo at all) that deserves an actual answer from whoever has authority over it, not a
third silent relocation by a third uncoordinated session.

**Consequence for the row I was actually working:** did NOT land `GOAL-SILLY-100.md` as a confident
"still has merit, here's the corrected path, resume here" consolidation — that would bake in a location
that currently has no content, exactly the kind of stale-pointer trap this whole consolidation project
exists to prevent. See this row's task file NEXT block for how the 4 GOAL-SILLY-*.md files are being
handled instead (holding, not folding, pending this finding's resolution).

Mailed ceo (cross-repo, time-sensitive-but-not-urgent, not this row's authority to resolve). Sent for
awareness, not routed as a blocker on other work.
