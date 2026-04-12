# GOAL-README-SNOBOL4DOTNET — Fix README.md for snobol4ever/snobol4dotnet

**Repo:** snobol4dotnet
**Done when:** `README.md` is accurate, current, and useful to a new visitor.

---

## Current state (at goal creation)
- Opens with centered `<center>SNOBOL4.NET</center>` — likely predates org merge
- References Jeffrey Cooper's original standalone project framing
- May not reflect current test count, dotnet version, or install instructions
- BEAUTY-19 progress (currently partway through) not reflected
- DATATYPE behavior (lowercase, intentional) not documented for users

## Steps

- [ ] **S-1** — Read full current `README.md`. Mark every sentence: ✅ accurate | ⚠️ stale | ❌ wrong.
  Gate: audit list produced before any edits.

- [ ] **S-2** — Run `dotnet test` and record current passing/total count.
  Gate: actual number in hand.

- [ ] **S-3** — Fix header: remove `<center>` tag, align with snobol4ever org branding.

- [ ] **S-4** — Fix all stale/wrong items: test counts, dotnet version requirements,
  install/build instructions, oracle information.

- [ ] **S-5** — Add note on DATATYPE returning lowercase (SPITBOL-compatible, intentional).

- [ ] **S-6** — Add snobol4ever org context: part of compiler matrix, links to one4all and corpus.

- [ ] **S-7** — Final read-through. Every sentence accurate. Lon approves.

## Rules
- Do not push until "perform hand off".
- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.
