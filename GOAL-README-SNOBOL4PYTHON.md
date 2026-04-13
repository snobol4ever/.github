# GOAL-README-SNOBOL4PYTHON — Fix README.md for snobol4ever/snobol4python

**Repo:** snobol4python
**Done when:** `README.md` is accurate, current, and useful. PyPI install works.

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

- [ ] **S-2** — Fix all stale/wrong items. Remove "(README v2 grid sprint: DEFERRED…)" notice
  if that work is now done, or update it if still deferred.

- [ ] **S-3** — Add snobol4ever org context: part of compiler matrix, links to one4all and corpus.

- [ ] **S-4** — Final read-through. Every sentence accurate. Lon approves.

## Rules
- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.
