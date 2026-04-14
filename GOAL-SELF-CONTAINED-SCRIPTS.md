# GOAL-SELF-CONTAINED-SCRIPTS.md — All test/build scripts self-contained

**Repo:** one4all (test scripts), .github (doc)
**Done when:** Every script under `one4all/scripts/` runs
correctly with zero setup: no env vars to export, no stdin to pipe, no
external paths to configure. Run the script, get a result. That's it.

---

## Problem

Scripts currently have three failure modes:

1. **Env vars** — `CORPUS=...`, `INTERP=...`, `SCRIP=...` must be set by caller
2. **Stdin hangs** — programs that read INPUT block forever without piped input
3. **Missing prerequisites** — corpus/oracle not cloned, packages not installed

All three are solved the same way: the script itself handles it.

---

## Rules for self-contained scripts

1. **Paths are derived from `$0`**, never from env vars.
   ```bash
   HERE="$(cd "$(dirname "$0")" && pwd)"
   ROOT="$(cd "$HERE/.." && pwd)"
   SCRIP="$ROOT/scrip"
   ```
2. **Every `scrip` call gets `< /dev/null`** unless the test explicitly needs stdin,
   in which case the stdin data is embedded inline in the script via heredoc or printf.
3. **Every `scrip` call gets `timeout N`** (8s for unit tests, 30s for corpus runners).
4. **Corpus path is hardcoded to `/home/claude/corpus`**. If missing, the script
   clones it (using the build script), or SKIPs with a clear message — never fails silently.
5. **Oracle path is hardcoded to `/home/claude/csnobol4/snobol4`**. Same rule.
6. **build_* scripts are idempotent** — running twice is safe. They check before building.
7. **No script sources another script's env** — each is fully standalone.

---

## Steps

- [ ] **SC-1** — Audit all scripts under `one4all/test/` for the three failure modes.
  Produce a list: script name, failure mode(s), fix needed.
  Gate: audit list committed to this goal file as a state table.

- [ ] **SC-2** — Fix `test/smoke.sh` — already mostly clean; add `< /dev/null` and `timeout`.
  Gate: `bash test/smoke.sh` works from any directory with no env vars.

- [ ] **SC-3** — Fix `test/run_csnobol4_suite.sh` — hardcode paths, clone csnobol4 if missing.
  Gate: `bash test/run_csnobol4_suite.sh` from repo root, no setup.

- [ ] **SC-4** — Fix `test/run_interp_broad.sh` — hardcode corpus path, clone if missing,
  add `< /dev/null` to all scrip calls, add per-test timeout.
  Gate: `bash test/run_interp_broad.sh` from repo root, no setup, no hang.

- [ ] **SC-5** — Fix `test/frontend/icon/run_icon_ir_rung.sh` — hardcode corpus and scrip paths,
  remove `--corpus` / `--scrip` flags as requirements (keep as optional overrides).
  Gate: `bash test/frontend/icon/run_icon_ir_rung.sh` from repo root, no setup.

- [ ] **SC-6** — Write `test/broad_unified_broker.sh` (replaces deleted broken version).
  Calls SC-3/SC-4/SC-5 scripts directly (they are now self-contained).
  Adds inline Prolog suite (6 tests, no files needed).
  Enforces non-regression floors: Icon PASS>=48, csnobol4 PASS>=34.
  Gate: `bash test/broad_unified_broker.sh` from repo root, no setup, < 60s.

- [ ] **SC-7** — Audit `one4all/scripts/` build_ and install_ scripts for idempotency and hardcoded paths.
  Fix any that require env vars or fail on second run.
  Gate: each `scripts/build_*.sh` and `scripts/install_*.sh` can be run twice safely.

- [ ] **SC-8** — Update RULES.md: add "Self-contained scripts" rule section.
  All future scripts must follow the SC rules above.
  Gate: RULES.md updated and pushed.

---

## Current state

SC-1 through SC-8: not started.
`scripts/test_smoke_unified_broker.sh` already self-contained (model for all others).

---

## Key files

| File | Status |
|------|--------|
| `scripts/test_smoke_unified_broker.sh` | ✅ already self-contained — use as template |
| `scripts/test_smoke_scrip_all_modes.sh` | needs `< /dev/null` + timeout |
| `scripts/test_csnobol4_budne_suite.sh` | needs hardcoded paths + auto-clone |
| `scripts/test_interp_broad_corpus_and_beauty.sh` | needs hardcoded paths + stdin fix + timeout |
| `scripts/test_icon_ir_all_rungs.sh` | needs hardcoded defaults |
| `scripts/test_smoke_unified_broker.sh` | deleted — rebuild in SC-6 |
| `scripts/build_*.sh`, `scripts/install_*.sh` | audit in SC-7 |
