# GOAL-README-SNOBOL4JVM — Fix README.md for snobol4ever/snobol4jvm

**Repo:** snobol4jvm
**Done when:** `README.md` is accurate, current, and useful to a new visitor.

---

## Current state (at goal creation)
- Has badge row (AGPL, tests) — test badge count likely stale
- CSNOBOL4 test suite (126 tests via `test_csnobol4_suite.clj`) added in GOAL-CSNOBOL4-HARNESS — not in README
- M-JVM-BEAUTY status (beauty.sno self-beautification ✅) should be prominently noted
- Multiple execution backends (interpreter, IR transpiler, stack-machine VM, JVM bytecode) — verify all still active
- EDN compilation cache speedup figure — verify still accurate

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

- [ ] **S-2** — Run `lein test` and record current tests/assertions/failures.
  Update badge URL to match.
  Gate: actual numbers in hand.

- [ ] **S-3** — Fix all stale/wrong items.

- [ ] **S-4** — Add CSNOBOL4 suite section: 126 tests, `lein test SNOBOL4clojure.test-csnobol4-suite`.

- [ ] **S-5** — Add snobol4ever org context: part of compiler matrix, links to one4all and corpus.

- [ ] **S-6** — Final read-through. Every sentence accurate. Lon approves.

## Rules
- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.
