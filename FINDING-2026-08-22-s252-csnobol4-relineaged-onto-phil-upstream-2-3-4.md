# FINDING — s252 HQ: csnobol4 re-lineaged onto Phil Budne's 2.3.4+, FENCE(P) dropped, and the upgrade bought a correctness fix

**Date:** 2026-08-22 · **Seat:** HQ (`/home/claude`, Claude Opus 5) · **Topic:** csnobol4 pristine-replace (Lon in-chat) · **Status:** LANDED, verified, pushed

**Lon's directive, in-chat:** replace `snobol4ever/csnobol4` with a fresh copy of Phil Budne's GitHub tree plus our own patches, **with NO FENCE at all**, then delete `/home/resources/csnobol4-upstream`.

## 1. WHAT THE REPO WAS, AND WHY "A FEW PATCHES" UNDERSTATED IT

`snobol4ever/csnobol4` was **50 commits with NO upstream ancestry** — root `a509cd73` (2026-04-12, *"Initial import of CSNOBOL4 2.3.3 with FENCE(P) groundwork"*), a snapshot import of the 2.3.3 tarball, not a clone. Proven disjoint from Phil's DAG in both directions: `git cat-file -t` on each repo's root fails in the other.

Of the 49 commits above the root, **36 were FENCE(P)/F-2 work** — not "a few patches". The delta also tracked ~10 **generated build products** upstream `.gitignore`s (`isnobol4.c` +266, `snobol4.c` +182, `Makefile2` +987, `data_init.h`, `res.h`, `proc.h`, `equ.h`, `config.*`, `version.h`, `syn.c`). Re-lineaging drops all of them, which is the point: they regenerate from `v311.sil`.

⭐ **FENCE(P) is ours, not Phil's.** Upstream has `&FENCE`, the keyword form, tagged `[PLB67]`. We added `FENCE(P)`, the **function** form — `FNCA` (D6 recursive-SCAN modeled on STAR, Gimpel 1973), `FNCP` builder, `FNCAPT` 4-descriptor template, plus dispatch entries. It is a SPITBOL feature, i.e. exactly the category Phil's own README warns people not to file against him.

## 2. THE REPLACEMENT WAS ALREADY BUILT

`/home/resources/csnobol4-upstream` branch `keepers` **was already** upstream/main + our three patches. Verified FENCE-free the hard way: `keepers:v311.sil` is **byte-identical** to `upstream/main:v311.sil` (`git diff --stat` = 0 lines). ⛔ A first pass grepping `FNCA|FNCP|FNCAPT` reported 11 hits and was WRONG — `FNCP` also matches upstream's own `FNCPAT`/`FNCPL`/`FNCPLE`. **Grep a marker that cannot collide before believing a contamination count.**

The three patches, 5 files, 658 insertions: `lib/init.c` `CSN_NO_SEGV_HANDLER` bypass · `monitor_ipc_runtime.c` + test (IPC monitor) + `Makefile2.m4` wiring · `lib/bsd/mstime.c` CLOCK_MONOTONIC ns.

## 3. THE GATE — BUILD, PATCHES, AND A CONTROL

- **Build:** `./configure && make` rc=0, **zero errors**. Bootstrap required per `00README.git` (regenerating C sources from `v311.sil` needs an existing snobol4 binary); ours preserved at `/home/satirical/backups/snobol4-bootstrap-2.3.3`.
- **Version: CSNOBOL4B 2.3.4+ (April 24, 2026)**, up from 2.3.3 (May 19, 2025).
- **All three patches live:** `CSN_NO_SEGV_HANDLER` in the binary · `monitor_ipc_runtime.o` linked · `TIME()` = `4258.` vs old `5150.`, same nanosecond magnitude (configure selects `lib/bsd/mstime.c`, our patched arm).
- **Upstream suite: 112 passed / 6 failed** (`a`, `dump`, `diag1`, `diag2`, `base`, `json1`).
- ⭐ **CONTROL BUILD SETTLES ATTRIBUTION.** Pristine `upstream/main` (HEAD == `0087b73f`, zero of our commits) built and run through the same suite: **112 / 6, the identical six**. Our patches change nothing. The `a.sno` failure is a **stale `a.ref` upstream** — `&FILL` is defined in Phil's own `v311.sil` (lines 10555/11944/12011, `[BLOCKS]`) and no patch of ours mentions it.

## 4. ⭐ THE UPGRADE BOUGHT A CORRECTNESS FIX

Full crosscheck equivalence, new vs old binary over 322 programs: **257 identical, 65 divergent**. 64 of the 65 are FENCE(P) programs — the expected, accepted cost. **The 65th is an improvement:**

`crosscheck/patterns/172_pat_fail_forces_retry.sno` — OLD 2.3.3 prints `a c failed as expected`; **NEW 2.3.4+ prints `a b c failed as expected`, matching SPITBOL `-bf` AND the pinned `.ref`.** Phil fixed a pattern-retry defect between 2.3.3 and 2.3.4 and we inherited it. Our oracle was quietly wrong on that shape for four months.

## 5. THE FENCE(P) COST, AND ITS CURE

65 crosscheck programs can no longer be run by csnobol4. **Non-blocking:** `test_corpus_snobol4.sh` — the one blocking runner under SNOBOL4-FIRST — never references csnobol4, and SPITBOL (the s189 authority) has `FENCE(P)` natively. What is lost is csnobol4 as a *third opinion* on those programs in `cmp3_snobol4.sh` / `test_broad_unified_broker.sh` / `test_monitor_3way_sync_step_auto.sh`.

⭐ **LON'S CURE, in-chat, recorded here because it is the design of record:** FENCE(P) belongs in csnobol4 as **SNOBOL4 source, not SIL** — a `FENCE.inc` carrying `DEFINE('FENCE(P)')` etc. That keeps our lineage patch-thin against upstream forever. Lon also ruled the IPC concern moot: *"we will not use csnobol4 for 2-way IPC."*

## 6. WHAT LANDED, AND THE GUARDS

- `snobol4ever/csnobol4` **`main` = `8d35dbaa`** — Phil's 4,505 commits + our 3 = **4,508**, real ancestry, `git merge upstream/main` now works forever.
- **`legacy-2.3.3-fence` = `c5ead01`** — the old 50-commit history, pushed BEFORE the force-push. The 36 FENCE commits and 34 `docs/F-*` stay reachable by URL.
- Force-push, not delete-and-recreate: keeps URL, stars, issues; reversible from either mirror.
- **Guards inherited and negative-tested in the new tree:** remote named `upstream` not `origin` · `pushurl = DISABLED_NEVER_PUSH_TO_PHILBUDNE` (refused first) · `.git/hooks/pre-push` refuses any philbudne URL (rc=1) while allowing snobol4ever (rc=0).
- `/home/resources/csnobol4-upstream` **DELETED** after proving both its branch tips are ancestors of the new `main`.
- Backups: `/home/satirical/backups/Aug-21-21-51/csnobol4.git` and a fresh `csnobol4-PRE-REPLACE.git`, both at `c5ead01`, 50 commits.

## 7. FOR THE NEXT SESSION

⛔ `handoff_status.sh` now discovers **13** repos (was 12) — csnobol4 has an `origin` remote and lives under the workspace root, so it must stay clean and pushed or it blocks every handoff.
⛔ The `.s`-artifact and scorecard scripts that name `csnobol4/snobol4` (24 of them) still work — the directory name is unchanged, as required.
⭐ Open follow-up: `lib/ansi/mstime.c` and `lib/dummy/mstime.c` still return **milliseconds** while `lib/bsd/` returns nanoseconds. configure picks `bsd` here, so it is inert on this box — but the three arms disagree on units, and that is a portability defect in our own patch.
