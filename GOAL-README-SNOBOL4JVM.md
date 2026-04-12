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

## Steps

- [ ] **S-1** — Read full current `README.md`. Mark every sentence: ✅ accurate | ⚠️ stale | ❌ wrong.
  Gate: audit list produced before any edits.

- [ ] **S-2** — Run `lein test` and record current tests/assertions/failures.
  Update badge URL to match.
  Gate: actual numbers in hand.

- [ ] **S-3** — Fix all stale/wrong items.

- [ ] **S-4** — Add CSNOBOL4 suite section: 126 tests, `lein test SNOBOL4clojure.test-csnobol4-suite`.

- [ ] **S-5** — Add snobol4ever org context: part of compiler matrix, links to one4all and corpus.

- [ ] **S-6** — Final read-through. Every sentence accurate. Lon approves.

## Rules
- Do not push until "perform hand off".
- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.
