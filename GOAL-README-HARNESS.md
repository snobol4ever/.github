# GOAL-README-HARNESS — Fix README.md for snobol4ever/harness

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

**Repo:** harness
**Done when:** `README.md` accurately describes harness as the single home for all test
runner scripts, how to use it, and what engines/adapters are supported.

---

## Current state (at goal creation)
- Short stub — "Shared test infrastructure for the snobol4ever compiler/runtime family"
- Does not document the adapters/ structure (csnobol4, dotnet, jvm, spitbol, tiny, tiny_net)
- Does not document crosscheck.sh usage or CORPUS= / ENGINE= env vars
- Does not state the architectural intent: ALL test scripts belong here, not in SCRIP/test/
- CSNOBOL4 adapter added in GOAL-CSNOBOL4-HARNESS — not in README
- SCRIP/test/ currently has ~60 scripts that should eventually migrate here

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

- [ ] **S-2** — Document adapters/: one section per adapter (csnobol4, dotnet, jvm, spitbol, tiny, tiny_net).
  For each: what engine it wraps, how to invoke, what env vars it respects.

- [ ] **S-3** — Document crosscheck/crosscheck.sh: ENGINE=, CORPUS=, --filter, --engine flags.
  Show a concrete example invocation.

- [ ] **S-4** — State architectural intent: harness is the single home for all runner scripts.
  SCRIP/test/ scripts are being migrated here incrementally.

- [ ] **S-5** — Add CSNOBOL4 adapter documentation: run_crosscheck_csnobol4.sh, baseline counts.

- [ ] **S-6** — Final read-through. Every sentence accurate. Lon approves.

## Rules
- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
```
