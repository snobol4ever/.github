# FINDING 2026-09-04 (seat05) — SCORE.md conflict resolution can silently drop content; verified recurrence, not a one-off

## What happened

Landing two small SCORE.md measurements (the `test_corpus_snobol4.sh` board-text fraction fix, and — earlier the same sitting — the Prolog INRIA bindings-comparator cell) each required **3-4 sequential `git pull --rebase` conflicts** against SCORE.md within about 15 minutes, confirming this file is under extreme concurrent write pressure (this session alone observed the ceo, hq_C, hq_P, hq_T and multiple numbered seats all landing SCORE.md writes in the same window).

While resolving one of those conflicts, `git log --oneline` surfaced an existing commit from earlier the same session:

```
2ac5f004 SCORE: re-apply the snobol4 grid M cell a concurrent merge dropped
```

— i.e. this is **not the first time** a conflict resolution on this file has silently lost content. Independently, this session found a **second, uncaught instance** of the same failure mode: `602c2a6a` (this seat's own earlier commit landing the INRIA-bindings measurement — grid V-cell "TIGHTENED to the suite's own criterion" text, the display vendor-cell's `INRIA-bindings:` clause, and its provenance clause) was confirmed via `git merge-base --is-ancestor 602c2a6a HEAD` to be an ancestor of the current tip, **yet none of its content was present** in `HEAD:SCORE.md` — it had been dropped by some later conflict resolution and nobody had caught it (unlike the grid-M-cell drop, which 2ac5f004 shows *was* caught and fixed by someone else).

## Root cause (mechanism, not blame)

SCORE.md rows are single very long lines (one Markdown table row = one physical line, often 2000-4000+ characters). Git's line-based diff/merge has no way to do a fine-grained three-way merge *within* one line: when two sessions edit **different portions of the same row** in overlapping rebase windows, the conflict resolution is an all-or-nothing choice per line, and a resolver who takes "theirs" (or picks the visually-longer/more-recent-looking side) without diffing byte-for-byte against **both** parents can silently discard the other side's edit with no error, no warning, and nothing in `git status` to catch it — the merge reports success.

## What worked to detect and fix it, this session

1. Never trust a rebase resolution by inspection alone on this file — after resolving, explicitly grep the resolved content for every string your own earlier commit was known to have added, not just "does it look right."
2. When something appears to be missing that you're confident you landed, don't just re-apply from memory — `git log` for a commit that *should* contain it, confirm ancestry (`git merge-base --is-ancestor <sha> HEAD`), then diff that commit's blob directly against `HEAD`'s blob (`git show <sha>:path` vs `git show HEAD:path`) to get the *exact* missing text and re-splice it precisely, rather than re-typing from memory (which risks a byte-level mismatch with what other tooling — e.g. `util_score_row.py agree`'s fraction parser — expects).
3. A small Python script that (a) always fetches `git show HEAD:SCORE.md` fresh (never the working-tree conflicted file, which can accumulate corruption across repeated failed attempts), (b) applies each known fix as an idempotent anchor-text substitution (skip if already present, apply if the anchor is found exactly once, warn if the anchor is ambiguous or missing), and (c) **unconditionally writes the result at the end of the script, never inside a branch that can exit early** — this last point mattered: an earlier draft of this script called `sys.exit(1)` inside the per-check loop on an anchor-not-found, which skipped the write entirely and left the raw conflict markers on disk, and a subsequent Edit call then matched an anchor *inside* one of the still-present conflict-marker blocks without that being obvious from the tool's success message. Re-verify with `grep -c '^<<<<<<<\|^=======\|^>>>>>>>' SCORE.md` after every resolution before trusting it, not just after the first attempt.
4. `util_score_row.py agree` is a genuinely useful cross-check (0 same-denominator conflicts) but is not sufficient alone: it returned a false-reassuring `GATE PASS(0)` with `0 mirrored cell pair(s)` checked while the file still had live conflict markers in it, because the markers broke `find_table`/`find_grid`'s parsing enough to make it see nothing to compare, not enough to make it refuse. A `0 mirrored cell pair(s)` result should itself be treated as suspicious on a file known to have >10 languages' rows.

## Not fixed here (out of scope for this sitting)

No code or process change proposed — this FINDING is measurement, not a cure. Possible follow-ups for whoever owns SCORE.md tooling (hq_T per its role): (a) have `util_score_row.py agree` (or a new gate) refuse loudly rather than report `PASS(0)` when it parses zero rows from a file that should have several; (b) consider whether `write`'s own conflict-safety (it already refuses on a dirty tree) could be extended to a post-write self-check that greps for conflict markers before declaring success.

## Verified state after this session's fixes

`origin/main` `.github` @ `82fdd7d7`: 0 conflict markers, `INRIA-bindings` present exactly twice (vendor cell + provenance) on the Prolog row, `TIGHTENED to the suite's own criterion` present once on the grid, `61 xfail` absent from both SNOBOL4 board cells, `util_score_row.py agree` reports 0 same-denominator conflicts over 11 mirrored cell pairs.
