# FINDING — postoffice row `csnobol4-upstream-github-home` is STALE: the backup gap it describes was closed a session after it was filed

**Date:** 2026-08-23 · **Seat:** seat15 (`/home/claude15`) · **Topic:** postoffice task `csnobol4-upstream-github-home` (rank 5, locked by seat15 via `next`) · **Status:** INVESTIGATED, not actioned — recommend HQ retire the row rather than have it built

## 1. WHAT THE ROW SAID

Filed at s251: a local repo `/home/resources/csnobol4-upstream` (branch `keepers`, 3 commits — SEGV-handler bypass, monitor IPC runtime, ns mstime — tracking `philbudne/csnobol4` upstream) existed in **exactly one place on disk**, unbacked, at risk from a single disk failure. FIRST STEP prescribed creating an independent `snobol4ever/csnobol4-upstream` GitHub repo, push `keepers` to it as origin, blocked on Lon/`gh auth login` since `gh` isn't authenticated on this box.

## 2. WHAT ACTUALLY HAPPENED, ONE SESSION LATER

`/home/resources/csnobol4-upstream` no longer exists — I found it missing when I locked this row via `next`. Per `FINDING-2026-08-22-s252-csnobol4-relineaged-onto-phil-upstream-2-3-4.md` (read directly, not summarized secondhand): Lon ruled in-chat, same day, to replace `snobol4ever/csnobol4` (previously 50 commits with **no** upstream ancestry — a 2026-04-12 tarball snapshot import) with Phil Budne's real upstream tree plus exactly the 3 `keepers` patches, force-pushed with no FENCE(P) baggage. HQ verified `keepers`'s tip and the old `csnobol4` repo's tip were both ancestors of the new `main` **before** deleting `/home/resources/csnobol4-upstream` — a completed, verified migration, not data loss. `legacy-2.3.3-fence` was pushed first (preserving the old 50-commit history by URL) before the force-push, and backups (`/home/satirical/backups/Aug-21-21-51/csnobol4.git`, `csnobol4-PRE-REPLACE.git`) were taken at `c5ead01` beforehand.

## 3. VERIFICATION PERFORMED THIS SESSION (read-only; no writes, pushes, or repo creation)

- `git ls-remote git@github.com:snobol4ever/csnobol4.git` (live network round-trip, run directly, not cached):
  `main` = `8d35dbaa5df42f162150d2326d7d07adadbb6f8c`, `legacy-2.3.3-fence` = `c5ead01dac878059862bf24caf523146b0c702c9` — matches the s252 FINDING exactly.
- Local clone `/home/claude/csnobol4`: `git log --oneline --all` shows the 3 keepers commits (`4577cb7b` SEGV-handler bypass, `9a36adaa` monitor IPC runtime, `8d35dbaa` mstime CLOCK_MONOTONIC ns) atop 4,505 of Phil's commits — real ancestry, 4,508 total.
- Push guards inherited into the new tree and still intact: `upstream` remote fetch-only, `pushurl=DISABLED_NEVER_PUSH_TO_PHILBUDNE`, `.git/hooks/pre-push` refuses any philbudne URL.
- Local bare backup `/home/satirical/backups/Aug-21-21-51/csnobol4.git` confirmed at `c5ead01`.

**The 3 commits are now safe redundantly — on GitHub, in a local working clone, and in a local bare backup — not in "exactly one place."** The row's GOAL is measurably false as of s252.

## 4. THE ROW'S OTHER LOOSE ENDS

- **The "rename `snobol4ever/csnobol4` → `csnobol4-snapshot`?" open question (unanswered since s251):** also moot. The naming concern was that the repo shared no ancestry with upstream and so misled; it now carries Phil's real ancestry, so the premise is gone.
- **Related claims swept into `claims-stale-fleet-s262/`:** `csnobol4-clean-fork.claim` (seat01) and `csnobol4-pin-provenance.claim` (seat02) — both read directly this session, both marked `DONE`, not abandoned. `csnobol4-clean-fork` is the seat1 finding (`FINDING-2026-08-21-...keeper-3-collides-with-generated-output.md`) that built the `keepers` branch s252 later pushed. These were swept into a stale-sweep directory because the sweep predated/was adjacent to other cleanup, not because the work was neglected.
- **`csnobol4-residue-six` (found as a `/tmp` task backup, same batch as this row's backup):** unrelated — a live, separate, unassigned task about six corpus test-suite defects (collect2/convert/intval/lexcmp/nqueens/setexit3). Shares only the `csnobol4` name prefix; not a stale duplicate of this row.

## 5. WHY THIS HAPPENED

The row was mechanically carried forward through the QUEUE.tsv → `tasks/*.task.md` conversion (hq_C, 2026-08-22, V2-2) without anyone cross-referencing it against the s252 relineage finding landed the same day. Its own DONE-WHEN was already flagged uncomputable at conversion time ("its completion test is still PROSE") — that flag was about the *criterion*, not the *premise*, so nothing forced a check of whether the row's GOAL still held.

## 6. RECOMMENDATION

Do not build the FIRST STEP (creating `snobol4ever/csnobol4-upstream`, waiting on `gh auth`/Lon) — it would mint a redundant, confusing second repo for a problem already solved a different, better way (relineage onto real upstream, not a same-repo mirror). I am not closing this via `s4e_msg.sh done` myself: the row's own DONE-WHEN explicitly refuses closure by design, and retiring a queue row is HQ's call, not a seat's. Routed to HQ via `s4e_msg.sh ask csnobol4-upstream-github-home`; claim left held (not abandoned) pending HQ's ruling on retirement. Ledger entry appended to the task file itself.
