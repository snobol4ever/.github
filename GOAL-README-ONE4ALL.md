# GOAL-README-ONE4ALL — Fix README.md for snobol4ever/one4all

**Repo:** one4all
**Done when:** `README.md` is accurate, current, and useful to a new visitor.

---

## Current state (at goal creation)
- Opens with badge + one-liner — reasonable structure
- Likely contains `scrip-interp` references — must be `scrip`
- Build instructions may reference old binary names or flags
- Test/corpus counts may be stale
- No mention of CSNOBOL4 test suite (`run_csnobol4_suite.sh`) added in GOAL-CSNOBOL4-HARNESS
- Frontend/backend matrix may not match current actual state

## Steps

- [ ] **S-1** — Read full current `README.md`. Mark every sentence: ✅ accurate | ⚠️ stale | ❌ wrong.
  Gate: audit list produced before any edits.

- [ ] **S-2** — Verify actual build instructions work from a clean clone:
  `git clone … && make scrip && bash test/run_interp_broad.sh`
  Record actual PASS count.
  Gate: confirmed working build command in hand.

- [ ] **S-3** — Fix all stale/wrong items. Replace `scrip-interp` → `scrip` everywhere.
  Update test counts, backend status, frontend status.

- [ ] **S-4** — Add CSNOBOL4 suite to testing section: `run_csnobol4_suite.sh`, 126 tests, baseline 8/126.

- [ ] **S-5** — Ensure frontend × backend matrix matches PLAN.md and actual build output.

- [ ] **S-6** — Final read-through. Every sentence accurate. Lon approves.

## Rules
- Do not push until "perform hand off".
- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.
