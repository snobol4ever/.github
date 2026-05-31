# GOAL-SESSION-SETUP-REFINEMENT.md — HQ files as session setup authority

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

**Repo:** .github (doc), SCRIP (scripts)
**Done when:** Every active Goal file has a `## Session Setup` section listing
exactly the scripts needed for that goal. REPO files and RULES.md reflect this
as the canonical pattern. No goal requires running more than it needs.

---

## Problem

`build_full_session_environment.sh` builds everything — packages, scrip, spitbol,
csnobol4 — regardless of what the goal actually needs. Most goals need only a
subset. The current REPO-SCRIP.md has a loose generic table mapping goal *types*
to script lists, but:

- It is not goal-specific
- It is easy to ignore or get wrong
- It requires reading a separate doc to know what to run
- It encourages over-building

---

## Design decisions (already agreed)

1. **Granularity is correct** — individual scripts (`build_scrip.sh`,
   `build_csnobol4_oracle.sh`, etc.) are each one thing. Do not change them.

2. **No switches** — a big script with flags defeats the naming convention and
   creates a maintenance problem. Rejected.

3. **HQ files are the authority** — each Goal file and REPO file carries a
   literal `## Session Setup` block: copy-paste bash commands, nothing more.
   The script names are self-describing; the list reads like English.

4. **`build_full_session_environment.sh`** — rename to
   `install_everything_full_stack.sh`. Useful for one-shot full installs.
   Nobody should run it for a specific goal session.

5. **RULES.md** — add rule: "Session setup is defined in the Goal file's
   `## Session Setup` section. Run exactly those scripts, no more."

---

## Steps

- [x] **SR-1** — Rename `scripts/build_full_session_environment.sh` to
  `scripts/install_everything_full_stack.sh`. Update internal references.
  Update REPO-SCRIP.md reference. Commit SCRIP.
  Gate: file renamed, old name gone, docs updated.

- [x] **SR-2** — Add `## Session Setup` to REPO-SCRIP.md replacing the
  generic goal-type table. New format: named categories with literal script
  lists. Each category maps to a family of goals (interp, x86, jvm, net,
  monitor/silly). Canonical — Goal files reference this for the full picture.
  Gate: REPO-SCRIP.md has clean per-category setup blocks.

- [x] **SR-3** — Add `## Session Setup` section to each active Goal file.
  List only the scripts that goal actually needs. No more.
  Active goals to update (from PLAN.md ☐ column):

  | Goal file | Scripts needed |
  |-----------|---------------|
  | GOAL-UNIFIED-BROKER.md | install_system_packages, build_scrip, build_csnobol4_oracle, build_spitbol_oracle |
  | GOAL-SCRIP-INTERP-SPLIT.md | install_system_packages, build_scrip |
  | GOAL-SNOCONE-IR-BB.md | install_system_packages, build_scrip |
  | GOAL-SILLY-SWEEP-FORWARD.md | install_system_packages, build_csnobol4_oracle |
  | GOAL-SILLY-SWEEP-BACKWARD.md | install_system_packages, build_csnobol4_oracle |
  | GOAL-SILLY-SYNC-MONITOR.md | install_system_packages, build_csnobol4_oracle, build_spitbol_oracle, build_monitor_ipc_shared_library, build_ss_monitor_harness |
  | GOAL-SILLY-COMPLETE.md | install_system_packages, build_csnobol4_oracle |
  | GOAL-PROLOG-IR-RUN.md | install_system_packages, build_scrip, build_spitbol_oracle |
  | GOAL-CROSS-LANG-VERIFY.md | install_system_packages, build_scrip, build_spitbol_oracle, build_csnobol4_oracle |
  | GOAL-SNOCONE-BEAUTY.md | install_system_packages, build_scrip, build_spitbol_oracle |
  | GOAL-SUBEXPR-ORACLE.md | install_system_packages, build_scrip, build_spitbol_oracle |
  | GOAL-REMOVE-CMPILE.md | install_system_packages, build_scrip, build_spitbol_oracle |
  | GOAL-TWO-STEP-HUNT.md | install_system_packages, build_scrip, build_spitbol_oracle |
  | GOAL-SCRIP-BEAUTY.md | install_system_packages, build_scrip, build_spitbol_oracle |
  | README goals (×9) | install_system_packages, build_scrip |

  Gate: every active ☐ goal file has a `## Session Setup` section.

- [x] **SR-4** — Update RULES.md: add "Session setup" rule.
  Content: "Session setup is defined in the Goal file's `## Session Setup`
  section. Run exactly those scripts, no more. Do not run
  `install_everything_full_stack.sh` for a specific goal unless the goal
  explicitly lists it."
  Gate: RULES.md rule added and pushed.

- [x] **SR-5** — Update PLAN.md `## ⛔ SESSION START` section.
  Step 5 currently says "Follow the REPO file `## Session Start` section".
  Clarify: "Run the scripts listed in the Goal file's `## Session Setup`
  section. If the Goal file has no `## Session Setup` yet, fall back to the
  REPO file's setup blocks."
  Gate: PLAN.md session start protocol updated.

---

## Session Setup template

Every Goal file gets this block, filled in for that goal:

```markdown
## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
# add only what this goal needs:
# bash /home/claude/SCRIP/scripts/build_spitbol_oracle.sh
# bash /home/claude/SCRIP/scripts/build_csnobol4_oracle.sh
# bash /home/claude/SCRIP/scripts/build_monitor_ipc_shared_library.sh
# bash /home/claude/SCRIP/scripts/build_ss_monitor_harness.sh
# bash /home/claude/SCRIP/scripts/install_java_and_jasmin.sh
```
```

---

## Current state

SR-1 through SR-5: DONE. All steps complete this session (2026-04-13).
