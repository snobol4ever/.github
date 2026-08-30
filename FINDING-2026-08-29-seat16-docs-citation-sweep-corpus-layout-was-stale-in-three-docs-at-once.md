# FINDING: the corpus-layout citation was stale in three different docs, each by a different amount

**Seat:** seat16 (FLEET-16) · **Date:** 2026-08-29 · **Found while:** the all-hands `.github/docs citation
sweep` lane (ceo `all-hands-consolidation`, assigned alongside the corpus-suites-consolidation push).

## SCOPE OF THIS PASS — read before assuming it's exhaustive
This is a **bounded first pass**, not a sweep of `.github/`'s full ~780 files. In scope: `CLAUDE.md`
(root), `.github/RULES.md`, `.github/CORPUS-LOCATIONS.md`, `.github/PLAN.md` — the "living"
governance docs, checked against the live `corpus/` tree. Deliberately **out of scope**: the 710
`FINDING-*.md` files (dated historical records — correctly describe the tree as it was on their own
date; rewriting them to match today would be revisionist, not a citation fix) and the 57 `GOAL-*.md` /
14 `ARCH-*.md` files beyond a grep pass (see REMAINING below). `corpus/programs/`'s stale-lon-spelling
hits in `GOAL-CEO.md`/`GOAL-SNOBOL4-100.md` were checked and are dated ledger entries, not current-tense
claims — correctly left alone.

## MEASURED — three authorities, three different ages, three different pictures
Asked "what does the corpus look like," in order of how recently each was written:

| Doc | Last touched | Says about `crosscheck/`+`probe/` |
|---|---|---|
| `.github/CORPUS-LOCATIONS.md` | 2026-08-24 | Doesn't even use `tests/{lang}/` — describes a flat `corpus/<lang>/` layout (`corpus/icon/`, `corpus/snobol4/`) that is two re-grids behind. |
| root `CLAUDE.md` | 2026-08-27 | Uses `corpus/tests/{lang}/` correctly, but still calls `corpus/crosscheck/` "the primary harness feed" with a live count, and describes `corpus/probe/bb/` as a going concern. |
| `corpus/README.md` | 2026-08-29 (today) | Says `crosscheck/` is gone and `probe/` is "~240 files remain, mid-flight." |

**All three were wrong by the time I read them**, in escalating order — `ls corpus/` right now shows
`crosscheck/` and `probe/` **both fully absent**, the `probe/` deletion having landed (corpus `c06960a12`,
"Lon 2026-08-29 direct order") *after* `corpus/README.md`'s "~240 remain" sentence was committed. A
`corpus/demo/` → `corpus/demos/` rename (corpus `924bd8bd0`) landed in the same window and is reflected
in none of the three.

⭐ **The interesting part isn't any one stale fact — every doc here already warns "verify against the
tree" — it's that the warnings didn't stop THREE independent staleness generations from stacking up
at once**, each doc citing the one before it as the authority. `.github/CORPUS-LOCATIONS.md` calls
itself "the only map" (per root `CLAUDE.md`'s own citation of it) while being the stalest of the three.
A pointer chain is only as fresh as its least-recently-checked link, and nothing was checking the
chain itself.

## A FOURTH, UNRELATED STALE CITATION — SUPREME-AUTHORITY DOC
`.github/RULES.md`'s oracle-dialect FACT RULE (hq_C, 2026-08-23 s261) names `corpus/programs/csnobol4-suite/`
as Phil Budne's CSNOBOL4 suite. That path does not exist under `corpus/programs/` at all — the real
location, confirmed present on disk, is `corpus/packages/snobol4/csnobol4_suite/` (underscore, no
hyphen). This one is not part of the crosscheck/probe cascade above; it is a separate, older drift in
the single most-cited document in the repo. The dialect *ruling itself* (grade against csnobol4, not
`sbl -bf`) is correct and untouched.

## FIXED (this session, addendum style per RULES.md's own TRANSCRIPTION law — no silent edits)
- Root `CLAUDE.md`: `.github` file counts corrected (57/14/710, was 82/14/495 — plain recount, no
  narrative needed). Corpus layout section rewritten to state crosscheck/probe are gone, the demos
  rename, and to stop pointing at `CORPUS-LOCATIONS.md` as if it were current.
- `.github/CORPUS-LOCATIONS.md`: correction banner added after its existing 2026-08-24 banner, stating
  the per-language table is superseded and naming the current top-level shape. **Did not rewrite the
  per-language table itself** — see REMAINING.
- `.github/RULES.md`: inline addendum on the csnobol4-suite path, immediately after the original claim.

## REMAINING — explicitly not done, so nobody reads this as a full sweep
1. `.github/CORPUS-LOCATIONS.md`'s per-language table (filename patterns, per-language file counts) is
   flagged stale but **not re-derived** — that needs a fresh census against the live tree per language,
   which is a bigger job than a citation check and arguably overlaps the consolidation itself. Whoever
   next needs that table's specifics should rebuild it from `ls`, not trust the flagged rows.
2. The ~20 other `ARCH-*.md`/`GOAL-*.md` files that grep-matched `corpus/programs/<lang>` were **not**
   individually opened this pass (budget/scope call, not a claim they're clean) — see the grep list in
   this row's own session if repeating this sweep; a reasonable next slice would be `ARCH-LANGUAGES.md`,
   `ARCH_SCOREBOARD.md`, and the three `GOAL-*-100.md` consolidated files first, since those are the
   highest-traffic reads.
3. `corpus/programs/prolog/rung10_programs_puzzles.pl` — one file, undocumented anywhere, looks like
   in-flight residue from the prolog flatten-to-config lane (hq_B+seat05's assignment, not mine). Flagged
   in the `CLAUDE.md` edit rather than resolved; not this row's lane to touch.
4. This project reorganizes its corpus roughly daily. **Whatever this FINDING says about current paths
   will itself be stale on a similar timescale** — the fix here is the banners pointing at `ls`, not the
   specific facts, which are receipts for what was true at commit time, same as any other FINDING.

## LEDGER
- [seat16·2026-08-29] Pulled `.github` and `corpus` fresh before and during this pass (both had concurrent
  commits land mid-session — the `probe/` deletion and `demos` rename were caught only because of the
  second pull). Verified every claim above against `ls`/`git log`, not against any document, per the
  standing rule this whole finding is about. Pushed alongside this file: root `CLAUDE.md` (untracked,
  local-only edit, no commit possible per `corpus-suites-consolidation.task.md` STEP 0's own note that
  root `CLAUDE.md` is untracked in all three siblings), `.github/CORPUS-LOCATIONS.md`, `.github/RULES.md`.
