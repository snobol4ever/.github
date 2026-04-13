# GOAL-README-SNOBOL4ARTIFACT — Fix README.md for snobol4ever/snobol4artifact

**Repo:** snobol4artifact
**Done when:** `README.md` accurately reflects the repo's current role and status.

---

## Current state (at goal creation)
- Profile README describes it as: "CPython C extension: SNOBOL4 Byrd Box engine —
  proof-of-concept from which engine.c in one4all was extracted"
- May be largely superseded by snobol4python — clarify relationship
- May have no README at all, or a very thin one

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

- [ ] **S-2** — Clarify relationship to snobol4python: is this still maintained independently,
  or is it archived/subsumed?

- [ ] **S-3** — Write or fix README to accurately reflect current status.

- [ ] **S-4** — Final read-through. Lon approves.

## Rules
- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.
