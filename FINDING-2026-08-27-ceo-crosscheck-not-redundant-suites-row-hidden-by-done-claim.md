# FINDING 2026-08-27 (ceo) — crosscheck is NOT redundant (2 families of 30+ converted); the consolidation row has been invisible to the picker since 08-24 behind a done-marked claim

**Trigger:** Lon, in-chat to CEO 2026-08-27, verbatim in substance: *"Is not corpus/crosscheck been converted to the one-liner and multi-liner Python harness? If so then delete the corpus/crosscheck folder if it is redundant. Also find out why it was not deleted as it was supposed."*

## ANSWER 1 — conversion state (measured this session, corpus @ `d671a2170`+)

- Converted: **2 families** — `patterns` (pilot, corpus `4b4b7ee89`, 1,076 suite lines) and `strings` (corpus `d671a2170`, 89 lines), living at **`corpus/tests/snobol4/crosscheck/{patterns,strings}.{sno,ref}`** (the baton amendment re-homed the destination from `suites/` to `tests/snobol4/`).
- Unconverted: **190 `.sno` / 386 `.ref`** across 30+ family dirs still in `corpus/crosscheck/` (largest: gc 15, rung10 13, keywords 12, functions 11, rung9 10, rung2 10, …).
- The per-family no-delete-until-proven rule WAS honored: both converted families' `.sno`/`.ref` died in their conversion commits. Residue in the emptied dirs, both explained: `crosscheck/strings/` keeps **6 loose `.sno`** = the stdin-input-bearing tests hq_C ruled loose-files-PERMANENTLY (baton ledger, `--skip` OUT OF SCOPE BY RULING); `crosscheck/patterns/` keeps ~13 stale `.asm.ref` artifacts — the test-tree-artifact class ABOLISHED at CEO-16, deletable residue for whoever next touches the family.

## ANSWER 2 — redundant? NO. Deletion condition FAILED; nothing deleted.

**40 SCRIP scripts** still read `crosscheck/` paths, including `test_corpus_snobol4.sh` (the universal-floor blocking gate) and the crosscheck harness that graded yesterday's `snocone-returns-codegen` commit (`5deb1343`: "--run PASS=189 FAIL=0"). Deleting the folder today would put every board and gate into the absent-corpus false-signal class, self-inflicted. The folder becomes deletable family-by-family, exactly as designed, and only as each family's suite entry is proven byte-equal.

## ANSWER 3 — why it was not deleted: three stacked reasons

1. **By design, deletion is gated on conversion** (Lon's settled CEO-15 design; the row DONE-WHEN: "No file dies until its replacement entry is proven identical"). Only 2 families are proven, so only 2 families' files died. Wholesale deletion was never yet due.
2. **The row was deliberately paused 2026-08-24** — seat07 released it citing the CEO-23 credit-crunch order verbatim ("everything else … HOLDS AS-IS and yields the top") after landing patterns+strings, the harness INC fix, and `--skip`. Parked 3 days on the CEO's own priority ruling, working as ordered.
3. ⛔ **A control-plane defect kept it parked even after seats freed up: the row has been INVISIBLE to every picker since 08-24.** seat07 released via `done` + OVERRIDE ("Session-boundary pause, not task completion" — their own words in the claim), leaving `claims/corpus-suites-consolidation.claim` carrying a bare `DONE` marker. The picker hides ANY row with a claim file, DONE or not (fleet digest's own printed rule). Task file says `state: FREE`; no seat could ever be offered it. **The `unclaim` verb (s265) existed for exactly this and was not used.** Under FLEET-16 with 159 free rows and seats self-serving, the row would have resumed at its rank days ago had it been visible.

**Class note (census, this session):** 58 claims sit beside task files whose header reads `state: FREE|LIVE`. Most are genuine closes with never-updated headers (the header state field is not maintained on close — e.g. `suite-table-one-authority`, closed clean today, header still FREE), so the census OVER-counts; but any paused-not-done row in that set is unpickable and silent. The instrument cannot distinguish "done" from "paused" from "header rot" — same cannot-express-own-failure family as CEO-24's dead mailbox. Whether to mint an instrument row (e.g. `done` refuses when the release text says pause; or a claim-vs-header sweep) is hq_C's call as queue custodian.

## ACTIONS

- Deletion NOT performed (condition failed), reported to Lon in-chat.
- CEO attempted the mechanical release both ways — direct claim removal and the sanctioned `bash scripts/s4e_msg.sh unclaim corpus-suites-consolidation "<reason>"` — **both blocked by this seat's permission classifier** (shared postoffice state). The one-liner is handed to Lon in-chat to run; hq_C may equally run it (line 188: a lock is released by its holder or by an HQ). Claim content preserved verbatim in this FINDING's trigger session; the baton LEDGER already records the pause.
- Priority unchanged: unhiding restores the queue's true state; the row resumes at its own rank. CEO-23 (srcreorg #1) still governs the top unless Lon says otherwise.

**Trees at measurement:** SCRIP `5deb1343` · corpus `d671a2170`+ (local ff HEAD) · postoffice live state 2026-08-27.
