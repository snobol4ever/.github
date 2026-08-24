# FINDING 2026-08-24 seat14: sweep-s-artifact-drift — 4 regressions found, 1 concurrent-edit collision resolved

Row: `sweep-s-artifact-drift` (CLOSED this session, DONE-WHEN computed-verified). Row factory scope per its own brief: discover and mint, do not fix. This FINDING consolidates the four minted rows' receipts in one place; each row's own task file carries the fuller technical detail and NEXT steps.

## Pre-flight: corpus/programs/lon/ exclusion, confirmed by construction

The brief required confirming the six regen scripts exclude the lon-programs directory *by construction* before running anything. `corpus/programs/lon/` does not exist under the current (flattened) tree — the real path is `corpus/snobol4/lon/{eng685,include,rinky,sno}`. Read all six regen scripts' source (never `lon/`'s contents) and confirmed every one targets a fixed or allow-listed path structurally disjoint from it: benchmark/demo/prolog_bench use fixed subdirectories or hand-maintained name lists; programs explicitly whitelists `icon prolog rebus` (excludes snobol4 entirely, by its own header comment); crosscheck and feature walk `corpus/crosscheck` and `SCRIP/test/snobol4` respectively, neither of which contains a `lon` subtree. No exclusion gap found. (Separately, mid-session a CEO law telegram retracted `lon`'s off-limits status entirely — see "Law telegram" below — so this exclusion is now historical, not a live constraint, but it was live when checked.)

## The six regens: counts

| script | scanned | changed | unchanged | fail | notes |
|---|---|---|---|---|---|
| benchmark | 18 | 18 | 0 | 0 | insertions==deletions per file; mechanical churn |
| feature | 155 | 18 | ~132 | 5 emit-fail | **retired mid-session, see below — commit later dropped by rebase** |
| demo | 21 | 0 | 0 | 0 (100% SKIP) | **false green — tool broken, see row `demo-regen-broken-subfolder-reorg`** |
| programs (icon/prolog/rebus) | 664 | 630 | 34 | 15 emit-fail + 1 as-fail | net −109K lines (strip-wave consistent); triaged below |
| prolog_bench | 22 | 22 | 0 | 0 | net shrink, strip-wave consistent |
| crosscheck | 473 | 61 | 412 | 32 emit-fail | **retired mid-session, see below — commit survived rebase minus the retired portion**; 18 of the 32 triaged as a real regression |

Attribution context for the day's churn (58 SCRIP commits landed before this row started): free-r10/free-r11 (a4a465a0, a82768c2, 3380283f, ef553d3a, 0ff71be8, b8a0dfc2), descr-tag-split (62017f8a, 0f17fbf4, 6ba28e5e), byname-bake-cell-address (8c1f2d41), RPO-hash-set (1a812667), plus large strip-wave deletions and a NO-PIN rooted-GC rewrite (927d0521). None of these is claimed as *the* proven cause of any regression below — bisection is explicitly left to each minted row (ASM-DIFF-FIRST order), not attempted here.

## Four rows minted (regressions/gaps, NOT fixed here)

1. **`demo-regen-broken-subfolder-reorg`** (rank 2) — `util_regen_demo_s_artifacts.sh` 100% silently skips every one of its 21 targets ("no .sno") and reports "already current" — a false green. Cause: corpus commit `db20f3cfa` (today 13:25) reorganized `corpus/demo/<name>.sno` into `corpus/demo/<family>/<name>.sno`; the script (last repointed 12:36, `843cacfb`, for a *different* prior flat-move) was never touched again. Proved live via manual compile: fresh `roman.sno` output differs from the committed `roman.s`.
2. **`snocone-relop-parse-regression`** (rank 1) — 18 crosscheck/snocone files that previously compiled to real 24-46KB `.s` now fail outright. Root sample (`rungB09/B09_str_eq.sc`): `snocone parse error: syntax error` at `if (a :==: b) {` — the Snocone `:==:` relational operator no longer parses inside a condition. Covers rungB09 (6, string relops), rungB10 (6, numeric relops), rungB12 (5, pattern tests), + `coverage_sno_nodes.sc`. Very likely one shared cause across B09+B10 (12 files, all relational operators). Explicitly distinguished from 14 *other* crosscheck emit-fails in the same run that are the pre-existing, already-documented SN4-PAT subset gap (no prior `.s` ever existed for those — not news).
3. **`rebus-corpus-100pct-broken`** (rank 1) — all 3 of the only 3 Rebus programs with a committed `.s` (100% of what Rebus could ever compile) now fail. `binary_trees.reb` + `syntax_exercise.reb`: `FATAL lower_snobol4 (GZ#5 subset): ... outside the landed subset` (same message class as Snocone's known SN4-PAT gap, but hitting files that previously worked). `word_count.reb`: distinct `rebus_lower: lower_tree_expr unhandled TT_48`.
4. **`prolog-two-programs-broken-post-churn`** (rank 3) — 2 real regressions, unrelated causes. `coverage_pl_nodes.pl` (EMIT-FAIL): `[IBB] FATAL: mode-4 driver: main BB graph not found`. `rung10_programs_puzzles.pl` (AS-FAIL): duplicate assembler symbol — the mangled name decodes to a literal run of dashes (`#------...`), i.e. two distinct string/comment literals collide to the same mangled symbol.

Explicitly **not** minted: the 5 `feature`-regen emit-fails (`coverage_sno_nodes.s` + 4 `library/test_*.s`) — investigated and confirmed to be the *already-documented* standing s189 include-path gap (`-include 'lib/*.sno'` has no `corpus/lib/` to resolve against), not new drift; and the 11 `icon/rung36_jcon_*` + 14 crosscheck emit-fails that never had a prior committed `.s` (standing known gaps, not regressions). Triage method throughout: check whether a substantial prior `.s` existed (real regression) vs. never existed (expected gap) — do not conflate the two classes.

## Concurrent-edit collision: strip-mechanical-carve landed mid-sweep

While pushing, hq_C's row `strip-mechanical-carve` (SCRIP `4a5f88e9` / corpus `cbf12d7b`) landed concurrently and retired exactly 2 of the 6 scripts this row runs — `util_regen_feature_s_artifacts.sh` and `util_regen_crosscheck_s_artifacts.sh` — deleting their entire `.s` trees (155 feature + ~500 crosscheck) as a ruled decision (Lon s269: "abandon artifacts for tests ... but we want artifacts for benchmarks and demos"), later formalized fleet-wide via a CEO law telegram (see below). Rebase conflicts (all "modify/delete": their delete vs. my regen's modify) resolved by accepting the deletion throughout. SCRIP's feature commit became fully empty and git auto-dropped it. Corpus's crosscheck commit survived with only its 2 genuinely-new files (`crosscheck/beauty/{gen_cont_split,gen_tab_marker}.s`, which had no upstream counterpart to conflict with) — the other 59 were dropped the same way. Verified the crosscheck **source** (`.sc`) files are untouched (only `.s` bookkeeping was retired), so finding #2 above is unaffected. Flagged to hq_C non-blocking; hq_C confirmed the resolution was correct and reported the flag additionally caught a now-stale line in their own row `six-owed-verifier` (self-corrected on their side).

## CEO law telegram (s272) applied to this seat's root CLAUDE.md

Same-session, a CEO law telegram named four law changes most seat CLAUDE.md files likely contradicted: (1) `lon` directory special status fully retracted (matches this row's own pre-flight section above — now historical, not live); (2) NO -O2 BUILDS EVER (already applied earlier this session per a separate hq_P memo, cross-checked against RULES.md before acting); (3) board totals read from printed output, never a remembered denominator; (4) `.s` artifacts exist only beside benchmarks/demos, test-tree artifacts abolished (matches the strip-mechanical-carve collision directly). Applied all four to this seat's `CLAUDE.md`, added the mandated `LAW NOTICE: .github/RULES.md IS THE ONLY LAW` first line, and separately fixed two more stale `corpus/programs/<lang>` path references found while cross-checking (the `94dd91ba` flatten commit removed that directory level entirely; not part of the CEO's 4 items but the same class of staleness). hq_C separately confirmed the official RULES.md handoff chain is now THREE scripts (benchmark, demo, prolog_bench) — `programs` still exists on disk but is not part of the mandated chain; folded into this seat's CLAUDE.md.

## Also handled this session (inbox, unrelated to STEP 1 itself)

Synced all 3 repos via `pull --rebase` at session start (hq_C's "6 unpushed commits" report was already stale by the time read — verified 0 unpushed, just 1 behind, before doing anything). Closed a second, already-finished row (`rung-seat-claude-reconcile`) that was sitting CLAIMED-but-undone since 2026-08-23, per hq_C's note that a held claim hides a row from the whole fleet's picker — `done` verified its DONE-WHEN true and closed it properly rather than leaving it stale or unclaiming completed work back into the free pool.

## Receipts

- SCRIP: `a7a80259` (feature regen — later dropped empty by rebase, see collision section)
- corpus: `3f6ae3b04` (benchmark), `fb45571b8` (programs), `5c7794c6b` (prolog_bench), `0f8b0e2dd` (crosscheck, post-rebase)
- Minted rows (QUEUE.tsv + `/home/resources/postoffice/tasks/*.task.md`): `demo-regen-broken-subfolder-reorg`, `snocone-relop-parse-regression`, `rebus-corpus-100pct-broken`, `prolog-two-programs-broken-post-churn`
- Messages sent: `hq_C/push-your-6-commits-resolved`, `hq_P/no-o2-claude-md-fixed-seat14`, `hq_C/collided-with-strip-mechanical-carve`, `ceo/law-telegram-2026-08-24-applied-seat14`
