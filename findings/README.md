# findings/ — the long form, under a deletion date

⛔ **THE LAW IS `RULES.md` LINE 31 (FACT RULE — FINDING FILES ARE PERMITTED AGAIN, Lon 2026-09-18, ceo CEO-859/862).** This directory is only the *place*; the rule is there.

- **Write one whenever evidence needs a file of its own.** No seat is refused one, and no seat needs permission.
- ⛔ **FOLD ITS MEASURED CLAIMS INTO THE CITING BATON OR `GOAL-*.md` IN THE SAME LANDING.** Lon deletes findings periodically, by his own word — so a measurement that lives only here is a measurement with a deletion date. The FINDING is the long form; the cursor line is the record.
- **Name:** `FINDING-<YYYY-MM-DD>-<seat>-<kebab-slug>.md`.
- **Why a directory rather than the `.github/` top level:** 2231 findings were deleted across two sweeps (`f78d8b3fd` 826, `c0d7427ee` 874, the rest strays) partly because at top level they buried the 20 `ARCH-*` and 67 `GOAL-*` pages a seat actually orients from. One directory also makes Lon's periodic deletion a single operation rather than a glob over the org brain.
- **Recovering a deleted one:** the 2231 historical files were removed from the `.github` TOP LEVEL, so they are `git show <commit>^:FINDING-<name>.md` — not `findings/FINDING-…`. `git log --diff-filter=D --name-only -- 'FINDING-*.md'` lists them.
