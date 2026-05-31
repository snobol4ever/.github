# GOAL-SCRIP-RENAME.md — Eradicate "one4all", product is now SCRIP

**Repo:** SCRIP + corpus + .github
**Carved:** 2026-05-30 (Lon directive — recovery from the one4all Ground-Zero fiasco)
**Precedent:** mirrors the cross-cutting `GOAL-LANG-INDEPENDENT-RENAME.md` rename pattern (its own step ledger, gate after each slice).

---

## ⛔ WHY

The product fresh-started as **SCRIP** (public org repo `snobol4ever/SCRIP`). `one4all` is now a
**private** repo, scheduled for **deletion**. Every live reference to `one4all` — repo name, clone
URL, build path, shell variable, Makefile text, doc prose — must point at SCRIP instead, or the build
breaks (it already does: `scripts/build_scrip.sh` hard-codes `$ROOT/one4all` and fails when run from
the SCRIP checkout). This is a `grand master reorg`: PLAN.md Repos table + clone scripts get updated
here (the routine-handoff PLAN.md freeze in RULES.md is explicitly lifted for this goal).

---

## Rename mapping (authoritative — apply EXACTLY, longest-match first)

| From | To | Notes |
|------|----|-------|
| `github.com/snobol4ever/one4all` | `github.com/snobol4ever/SCRIP` | clone URLs (SCRIP repo · .github · corpus · PLAN.md · RULES.md) |
| `snobol4ever/one4all` | `snobol4ever/SCRIP` | bare org/repo refs |
| `/home/claude/one4all` | `/home/claude/SCRIP` | absolute build/test paths (77 sites in SCRIP scripts alone) |
| `$ROOT/one4all`, `$HOME/one4all` | `$ROOT/SCRIP`, `$HOME/SCRIP` | shell path joins |
| `ONE4ALL` (shell var / make var) | `SCRIP` | 122 sites in SCRIP, 5 in .github |
| `One4all` | `SCRIP` | 3 sites |
| `one4all` (prose / "one4all unified build" / "one4all repo") | `SCRIP` | residual case-insensitive sweep |

Counts at carve (case-insensitive, excluding `.git/`): **.github 2046 lines / 374 files · SCRIP 398 / 125 · corpus 38 / 23.** Two files are literally NAMED with the old token and must be `git mv`'d:
`REPO-one4all.md` → `REPO-SCRIP.md`, `GOAL-README-ONE4ALL.md` → `GOAL-README-SCRIP.md`.

**Scope boundaries (do NOT blindly rewrite):**
- **Git history / commit messages / tags** — frozen, never rewritten. The rename touches the WORKING TREE only.
- **Frozen historical narration** in `HANDOFF-*.md` and the `## Session log` / `## Session State` blocks that
  literally DOCUMENT the `one4all → SCRIP` migration (e.g. "one4all UNTOUCHED at `a0bb9be4`", "renaming
  one4all→X was REJECTED"). Blind substitution turns these into nonsense. **Decision point (confirm with Lon):**
  default is to LEAVE migration-history prose intact (it is a frozen record of how/why the rename happened) and
  rename only the LIVE operational references in those files (paths, clone URLs, "build from one4all" instructions).
  An aggressive "erase the word entirely" pass over history is a separate explicit sub-decision (RN-6).
- **`one4all`-as-a-word inside SPITBOL/SNOBOL4 corpus test DATA** (if any of the 23 corpus hits are test
  fixtures rather than path/URL refs) — verify each before touching; a `.ref` oracle value must NOT change.

---

## Session Setup

```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
make -j4 scrip            # rc=0 on clean base
make libscrip_rt          # rc=0 on clean base
```

Gate after EVERY slice (rename must be behavior-neutral):
```bash
make -j4 scrip            # rc=0
make libscrip_rt          # rc=0
SCRIP_ICN_BB=1 ./scrip --dump-sm /dev/stdin <<<'procedure main();write("hi");end'   # Icon SM count=0 sanity
git grep -nI 'one4all' -- . ':(exclude).git'                                          # shrinking → 0 (live refs)
```
(SNOBOL4 mode-2/3 is TOMBSTONED by SMX-4; the rename does not revive it — only `make` + Icon-BB hello gate it.)

---

## Rung: RN — eradicate one4all (smallest-risk → largest, gate each)

- [ ] **RN-1 — SCRIP build/test scripts (the breakage).** `scripts/*.sh` + `Makefile`: `ONE4ALL`→`SCRIP`,
  `$ROOT/one4all`→`$ROOT/SCRIP`, `/home/claude/one4all`→`/home/claude/SCRIP`, the "one4all unified build" /
  "Must be run from one4all root" comments. **Gate target: `bash scripts/build_scrip.sh` works from the SCRIP
  checkout** (currently fails with "clone snobol4ever/one4all first"). 50 .sh files + Makefile.
- [ ] **RN-2 — SCRIP source + misc (.c/.cpp/.py/.j/.java/.js/.il/.cs/.txt).** Path/URL/comment refs only — these
  are ~25 non-shell SCRIP files (6 .c, 1 .cpp, 8 .j, 6 .py, …). Verify none is a string literal an emitter
  bakes (grep the hit's line; a baked path would need the SCRIP path anyway). Gate: `make scrip` + `make
  libscrip_rt` rc=0.
- [ ] **RN-3 — SCRIP `.md` docs (README, MIGRATION, SESSION-*, non-history prose).** "one4all"→"SCRIP" in
  operational prose; leave the migration-history paragraphs per the scope boundary above.
- [ ] **RN-4 — `.github` operational docs.** PLAN.md (Repos table row `one4all`→`SCRIP` + `REPO-one4all.md`
  pointer; clone scripts), RULES.md (clone URL, "code repos first"), all `GOAL-*.md` live refs, all `REPO-*.md`.
  **`git mv REPO-one4all.md REPO-SCRIP.md`** and fix every pointer to it. This is the 2046-line bulk.
- [ ] **RN-5 — file renames + dangling pointers.** `git mv GOAL-README-ONE4ALL.md GOAL-README-SCRIP.md`;
  fix every cross-reference to both renamed files across all three repos. `git grep -n 'REPO-one4all\|README-ONE4ALL'` == 0.
- [ ] **RN-6 — corpus (23 files) + history-prose decision.** Inspect each corpus hit; rename path/URL refs,
  leave test-data/`.ref`-affecting hits untouched (verify with the SPITBOL oracle if any look like fixtures).
  Then settle the RN-history-prose decision with Lon (leave-as-frozen-record [default] vs total erasure) and,
  if total erasure is chosen, sweep `HANDOFF-*.md` + session-log blocks last.
- [ ] **RN-7 — final sweep + zero-check.** `git grep -niI one4all` across all three repos == 0 for live refs
  (or == only-the-agreed-frozen-history if RN-6 chose leave-as-record). Full gate. Commit per RULES.md handoff
  order: **code repos first (SCRIP, corpus), `.github` LAST.**

**Method per slice:** `git ls-files -z | xargs -0 grep -lZ 'one4all'` to get the file set, then targeted
`sed -i` with the longest-match-first mapping (URL → abs-path → `$ROOT/` → `ONE4ALL` var → bare word), then
`git diff` review BEFORE building, then gate. Never one giant repo-wide `sed` — slice, review, gate, repeat.

---

## Session State

```
HEAD SCRIP    = (clean checkout; LM-1 partial edits REVERTED this session — tree clean)
HEAD corpus   = 447c05b
make scrip    = rc=0  (verified this session on clean base)
make libscrip = rc=0  (verified this session on clean base)
one4all hits  = SCRIP 398 / .github 2046 / corpus 38  (case-insensitive, pre-rename baseline)
named files   = REPO-one4all.md, GOAL-README-ONE4ALL.md  (to be git-mv'd)
```

**Note:** the LOWER-MERGE rung (LM-1..LM-5) in GOAL-SNOBOL4-BB.md was IN PROGRESS (LM-1 half-applied) when
this rename was prioritized; LM-1 was reverted to a clean tree, so LOWER-MERGE restarts from clean HEAD when
resumed. No partial credit to reconcile.

---

## Session log

- **2026-05-30 — GOAL CARVED.** Lon pivoted mid-LM-1: product is SCRIP, one4all going private→deleted,
  eradicate the name everywhere. Surveyed blast radius (522 files / ~2482 line occurrences across 3 repos +
  2 literally-named files). Authored the mapping + 7-slice gated rung. Reverted the in-flight LM-1 edits to a
  clean SCRIP tree. No rename executed yet — rung laid down for execution.
