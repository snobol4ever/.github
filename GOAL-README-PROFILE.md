# GOAL-README-PROFILE — Update snobol4ever/.github/profile/README.md

**Repo:** .github (`profile/README.md`)
**Done when:** Every sentence in `profile/README.md` is accurate, current, and consistent
with actual repo state. No stale test counts, milestone names, or architectural claims.

---

## What needs updating (known issues at goal creation)

- **Test counts** — snobol4dotnet says "1,874 / 1,876 tests passing" — must reflect current `dotnet test` count
- **snobol4jvm test count** — says "2,033 tests / 4,417 assertions" — must reflect current `lein test` count
- **one4all corpus counts** — "106/106", "110/110" — verify against current `run_interp_broad.sh` output
- **scrip-interp references** — binary is now `scrip`; any mention of `scrip-interp` must be removed
- **corpus description** — says "Oracle runner scripts" — corpus does not own runner scripts (harness does); fix
- **harness** — not mentioned at all in profile; should be
- **CSNOBOL4 as oracle** — FENCE now implemented; update any language implying CSNOBOL4 lacked FENCE
- **Monitor section** — "Infrastructure complete. Full five-way launch: M-MONITOR-IPC-5WAY" — verify current state
- **GRIDS.md links** — `[GRIDS.md](../GRIDS.md)` — verify file exists and is accurate
- **snobol4artifact** — still accurate? Verify repo exists and description matches
- **Performance numbers** — 33ns / 0.7ns / 44ns — verify these are still from current build, not stale
- **Beauty/compiler bootstrap status** — update M-BEAUTIFY-BOOTSTRAP, M-JVM-BEAUTY status markers

---

## Steps

- [ ] **S-1** — Clone all repos. Run current test suites and record actual counts:
  - `dotnet test` on snobol4dotnet → record passing/total
  - `lein test` on snobol4jvm → record tests/assertions/failures
  - `bash test/run_interp_broad.sh` on one4all → record PASS count
  - Gate: numbers in hand before touching a single line of README.

- [ ] **S-2** — Audit every sentence in the README top to bottom. For each sentence:
  - Mark: ✅ accurate | ⚠️ stale | ❌ wrong | 📝 needs wording improvement
  - Produce a marked-up list before making any edits.
  - Gate: complete sentence-by-sentence audit list produced.

- [ ] **S-3** — Fix all ⚠️ stale items: test counts, milestone status markers, binary names.
  Gate: no stale numbers remain.

- [ ] **S-4** — Fix all ❌ wrong items: corpus description, scrip-interp references,
  CSNOBOL4 FENCE status, harness omission.
  Gate: no factually incorrect sentences remain.

- [ ] **S-5** — Add harness to the repo listing with accurate description.
  Gate: harness section present and accurate.

- [ ] **S-6** — Verify all links (`GRIDS.md`, repo links, badge URLs) resolve correctly.
  Fix any broken links.
  Gate: all links valid.

- [ ] **S-7** — Final read-through: every sentence accurate, consistent with PLAN.md
  active goal states, and consistent with what a visitor to github.com/snobol4ever sees.
  Gate: Lon approves.

---

## Rules
- Do not push until "perform hand off".
- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.
- Rebase before .github push: `git pull --rebase origin main && git push`.
