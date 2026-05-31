# GOAL-README-PROFILE — Update snobol4ever/.github/profile/README.md

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** .github (`profile/README.md`)
**Done when:** Every sentence in `profile/README.md` is accurate, current, and consistent
with actual repo state. No stale test counts, milestone names, or architectural claims.

---

## What needs updating (known issues at goal creation)

- **Test counts** — snobol4dotnet says "1,874 / 1,876 tests passing" — must reflect current `dotnet test` count
- **snobol4jvm test count** — says "2,033 tests / 4,417 assertions" — must reflect current `lein test` count
- **SCRIP corpus counts** — "106/106", "110/110" — verify against current `run_interp_broad.sh` output
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

## Verification Technique

Claude reads the README sentence by sentence (or claim by claim for tables/counts).
For each, Claude presents it clearly and asks: **T or F?**

- **T** — sentence is true and accurate. Move to next.
- **F** — sentence is false or stale. Claude drops into fix mode:
  1. Diagnose what is wrong (run commands if needed to get ground truth)
  2. Draft the corrected sentence
  3. Ask Lon to confirm the fix before moving on
  4. Apply the fix, then continue the loop

Claude works through the entire file top to bottom. No edits are made until
a sentence is confirmed false and the fix is confirmed. At the end, Claude
commits the corrected README.

---
## Steps

- [ ] **S-1** — Begin T/F verification loop through README top to bottom.
  Present each sentence to Lon. T = move on. F = diagnose, fix, confirm, continue.
  Gate: all sentences verified T (or corrected and confirmed).

- [ ] **S-2** — Fix all ⚠️ stale items: test counts, milestone status markers, binary names.
  Gate: no stale numbers remain.

- [ ] **S-3** — Fix all ❌ wrong items: corpus description, scrip-interp references,
  CSNOBOL4 FENCE status, harness omission.
  Gate: no factually incorrect sentences remain.

- [ ] **S-4** — Add harness to the repo listing with accurate description.
  Gate: harness section present and accurate.

- [ ] **S-5** — Verify all links (`GRIDS.md`, repo links, badge URLs) resolve correctly.
  Fix any broken links.
  Gate: all links valid.

- [ ] **S-6** — Final read-through: every sentence accurate, consistent with PLAN.md
  active goal states, and consistent with what a visitor to github.com/snobol4ever sees.
  Gate: Lon approves.

---

## Rules
- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.
- Rebase before .github push: `git pull --rebase origin main && git push`.

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
```
