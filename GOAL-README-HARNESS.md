# GOAL-README-HARNESS — Fix README.md for snobol4ever/harness

**Repo:** harness
**Done when:** `README.md` accurately describes harness as the single home for all test
runner scripts, how to use it, and what engines/adapters are supported.

---

## Current state (at goal creation)
- Short stub — "Shared test infrastructure for the snobol4ever compiler/runtime family"
- Does not document the adapters/ structure (csnobol4, dotnet, jvm, spitbol, tiny, tiny_net)
- Does not document crosscheck.sh usage or CORPUS= / ENGINE= env vars
- Does not state the architectural intent: ALL test scripts belong here, not in one4all/test/
- CSNOBOL4 adapter added in GOAL-CSNOBOL4-HARNESS — not in README
- one4all/test/ currently has ~60 scripts that should eventually migrate here

## Steps

- [ ] **S-1** — Read full current `README.md`. Mark every sentence: ✅ accurate | ⚠️ stale | ❌ wrong.
  Gate: audit list produced.

- [ ] **S-2** — Document adapters/: one section per adapter (csnobol4, dotnet, jvm, spitbol, tiny, tiny_net).
  For each: what engine it wraps, how to invoke, what env vars it respects.

- [ ] **S-3** — Document crosscheck/crosscheck.sh: ENGINE=, CORPUS=, --filter, --engine flags.
  Show a concrete example invocation.

- [ ] **S-4** — State architectural intent: harness is the single home for all runner scripts.
  one4all/test/ scripts are being migrated here incrementally.

- [ ] **S-5** — Add CSNOBOL4 adapter documentation: run_crosscheck_csnobol4.sh, baseline counts.

- [ ] **S-6** — Final read-through. Every sentence accurate. Lon approves.

## Rules
- Do not push until "perform hand off".
- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.
