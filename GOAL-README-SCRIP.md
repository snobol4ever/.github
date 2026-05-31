# GOAL-README-SCRIP — Fix README.md for snobol4ever/SCRIP

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

**Repo:** SCRIP
**Done when:** `README.md` is accurate, current, and useful to a new visitor.

---

## Current state (at goal creation)
- Opens with badge + one-liner — reasonable structure
- Likely contains `scrip-interp` references — must be `scrip`
- Build instructions may reference old binary names or flags
- Test/corpus counts may be stale
- No mention of CSNOBOL4 test suite (`run_csnobol4_suite.sh`) added in GOAL-CSNOBOL4-HARNESS
- Frontend/backend matrix may not match current actual state

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
- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
```
