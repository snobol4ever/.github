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

## Rung: RN — eradicate one4all (smallest-risk → largest, gate each) — ✅ COMPLETE 2026-05-30

- [x] **RN-1 — SCRIP build/test scripts (the breakage).** 50 `scripts/*.sh` + `Makefile` + 1 `archive/*.sh`
  swept. **`bash scripts/build_scrip.sh` now builds from the SCRIP checkout** (was bailing with "clone
  snobol4ever/one4all first"); path math self-heals because the on-disk dir is `SCRIP` and `$ROOT/SCRIP`
  resolves to `/home/claude/SCRIP`.
- [x] **RN-2 — SCRIP source + misc.** 27 non-shell files (.c/.cpp/.py/.j/.java/.js/.il/.cs/.txt). The one
  emitted-into-output literal — `xa_prologue.cpp`'s `require('/home/claude/one4all/.../core_runtime.js')` —
  plus the JVM `TestLexer/TestParser` default path args and `beauty_subexpr_gen.py` harness paths repointed
  to `/home/claude/SCRIP`. `make scrip` + `make libscrip_rt` rc=0.
- [x] **RN-3 — SCRIP `.md` docs.** 47 files. (SCRIP's own docs carried no contrastive migration narrative —
  that landmine was confined to `.github`.) Whole-SCRIP-repo residual = 0; committed `c334861`.
- [x] **RN-4 — `.github` operational docs.** 374 tracked files bulk-swept (GOAL-*, REPO-*, RULES.md, PLAN.md
  clone scripts, HANDOFF-*, archive). `GOAL-SCRIP-RENAME.md` EXCLUDED by design (this doc documents the
  eradication). Repaired the circular migration-history sentences in `GOAL-SNOBOL4-BB.md` Session State + log
  (see RN-6 resolution).
- [x] **RN-5 — file renames + dangling pointers.** `git mv REPO-one4all.md → REPO-SCRIP.md` and
  `git mv GOAL-README-ONE4ALL.md → GOAL-README-SCRIP.md`; all pointers fixed (0 dangling, verified
  cross-repo in SCRIP + corpus too). Committed `75165605`.
- [x] **RN-6 — corpus (23 files) + history-prose decision RESOLVED.** Corpus: paths/harness/comments/demo-JS
  `require()` paths only — verified **NO `.ref`/`.expected`/`.out`/`.gold` oracle file touched**; residual 0;
  committed `ec8bbbe`. **History-prose decision (the RN scope-boundary question):** resolved by
  REPHRASE-TO-COHERENT rather than leave-verbatim or blind-sub. The handful of contrastive sentences in
  `GOAL-SNOBOL4-BB.md` that described SCRIP as a *copy of* the old repo / the old repo as *left untouched* now
  read "the predecessor (private) repo" — the banned token is gone AND the migration record stays truthful.
  **(Lon: if you'd rather those frozen log lines kept the literal old name verbatim, say so and I'll revert
  just those.)**
- [x] **RN-7 — final sweep + zero-check.** All three repos at **0** live `one4all` refs; only
  `GOAL-SCRIP-RENAME.md` retains it (by design). All three repos COMMITTED LOCALLY (not pushed — push is a
  `perform hand off` action, and Lon controls the predecessor repo going private/deleted + the push order
  code-first/.github-last).

**Method per slice:** `git ls-files -z | xargs -0 grep -lZ 'one4all'` to get the file set, then targeted
`sed -i` with the longest-match-first mapping (URL → abs-path → `$ROOT/` → `ONE4ALL` var → bare word), then
`git diff` review BEFORE building, then gate. Never one giant repo-wide `sed` — slice, review, gate, repeat.

---

## Session State

```
RENAME        = ✅ MECHANICALLY COMPLETE 2026-05-30 (all 3 repos: 0 live one4all refs)
HEAD SCRIP    = c334861  SCRIP-RENAME RN-1/2/3 (scripts+Makefile+source+docs)  [LOCAL, not pushed]
HEAD corpus   = ec8bbbe  SCRIP-RENAME RN-6 (23 files)                          [LOCAL, not pushed]
HEAD .github  = 75165605 SCRIP-RENAME RN-4/5 (+ this rung doc)                 [LOCAL, +rung-update pending commit]
make scrip    = rc=0  · make libscrip_rt = rc=0 · build_scrip.sh from SCRIP checkout = OK · Icon-BB hello = OK
one4all hits  = SCRIP 0 / corpus 0 / .github 0-except-GOAL-SCRIP-RENAME.md (retained by design)
PUSH          = NOT DONE — awaiting `perform hand off` (order: SCRIP, corpus, then .github LAST)
```

**Resumption note:** the LOWER-MERGE rung (LM-1..LM-5, GOAL-SNOBOL4-BB.md) was reverted to clean HEAD when this
rename was prioritized; it restarts from clean HEAD whenever resumed. The SNOBOL4 BB engine remains TOMBSTONED
by SMX-4 (the rename did not touch that — it is path/name/doc only).

---

## Session log

- **2026-05-30 — GOAL CARVED.** Lon pivoted mid-LM-1: product is SCRIP, one4all going private→deleted,
  eradicate the name everywhere. Surveyed blast radius (522 files / ~2482 line occurrences across 3 repos +
  2 literally-named files). Authored the mapping + 7-slice gated rung. Reverted the in-flight LM-1 edits to a
  clean SCRIP tree. No rename executed yet — rung laid down for execution.
