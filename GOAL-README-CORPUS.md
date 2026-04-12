# GOAL-README-CORPUS — Fix README.md for snobol4ever/corpus

**Repo:** corpus
**Done when:** `README.md` accurately describes what corpus contains, what it does NOT contain,
and how to use it.

---

## Current state (at goal creation)
- Short, likely generic
- Corpus structure is currently messy: test scripts proliferated here (run_all.sh),
  crosscheck/ dir contains both programs AND a runner script
- README should clearly state: corpus owns programs and .ref files ONLY — scripts live in harness
- Should document the crosscheck ladder (rungs 1–11, 106 programs)
- Should document csnobol4-suite/ (116 Budne programs + exclusion list)
- Should document beauty/, gimpel/, demo/ structure

## Steps

- [ ] **S-1** — Read full current `README.md`. Mark every sentence: ✅ accurate | ⚠️ stale | ❌ wrong.
  Run `find corpus -name "*.sh"` — document which scripts are present and shouldn't be.
  Gate: audit list produced.

- [ ] **S-2** — Rewrite README to accurately describe directory structure:
  `crosscheck/` (test programs by category), `programs/` (suites by language/tool),
  exclusion list for csnobol4-suite, .ref file conventions.

- [ ] **S-3** — State clearly: corpus owns `.sno`, `.inc`, `.ref` files only.
  Test runner scripts belong in harness. Any `.sh` in corpus is a candidate for removal.

- [ ] **S-4** — Add usage section: how harness/crosscheck.sh points at corpus, CORPUS= env var.

- [ ] **S-5** — Final read-through. Every sentence accurate. Lon approves.

## Rules
- Do not push until "perform hand off".
- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.
