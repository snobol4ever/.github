# FINDING — s191, seat4, row `msg-next-orphan-skip`: the picker's presence test was its own printout, and 45 of 68 queue rows are already DONE

**Session:** 2026-08-20 s191 · seat4 `/home/claude4` · Claude Opus 5 · queue row `msg-next-orphan-skip` (rank 2)
**Landed:** SCRIP `a2711b88` — `scripts/s4e_msg.sh` (cure) + `scripts/util_postoffice_sweep.sh` + `scripts/util_postoffice_protocol_sync.sh` (new)
**Watermark:** **NOT APPLICABLE, and saying so is the point.** Zero compiler files touched — `git diff --name-only | grep -E '^src/|emit|x86_asm|lower_'` = **0**. The standing corpus watermark **m3 332/5 · m4 325/11 · SKIP 1** is untouched **by construction**, not by re-measurement. I did not run a board and do not claim one. RULES step-4 regen **NOT APPLICABLE**.

## 1. The defect: there was never a presence test — the print WAS the test, and its failure mode was silence

`next` resumes a seat's unfinished claim **before** it scans `QUEUE.tsv`, then printed the brief with:

```
grep -P "^[0-9]+\t\Q$t\E\t" "$q" 2>/dev/null | head -1 | awk -F'\t' '{print "brief: " $3; print "first: " $4}'
```

When the topic had **no row**, `grep` emitted nothing, `awk` received no line, and printed **nothing**. The seat saw:

```
RESUME dead-topic (yours, unfinished — s4e_msg.sh done dead-topic when the handoff clause is met)
```

…no brief, no first step, no reason, **exit 0** — and it recurred at every prompt, forever. Nothing in the code
ever *asked* whether the row existed; the answer was implicit in whether two lines appeared, and "no lines" is
indistinguishable from a formatting glitch. **Measured on seat5 at s189**: HQ renamed `arbno-nullalt-false-accept`
→ `arbno-tail-false-accept` five minutes after seat5 locked the old name, and seat5 was pinned to a row that no
longer existed — stranding real uncommitted codegen work in a tree with no git record (rescued as `.github` `46f7895d`).

**Reproduced before it was cured**, in a sandbox bus via the script's own `S4E_POST`/`S4E_SEAT` overrides, so the
live fleet was never a test subject. The baseline output above is that reproduction, verbatim.

## 2. The cure: one matcher for both jobs, and the loop CONTINUES

- **`qrow()` now serves BOTH the presence test and the brief print.** They are the same call, so they cannot
  disagree — and that disagreement *was* the bug. (Same principle as s170's ratchet: computed, never typed.)
- An unfinished claim whose topic has no `QUEUE.tsv` row is **skipped with one line naming the dead topic** and
  pointing at the question box; the loop **continues**, so the seat falls through to live work — and, if it holds a
  second live claim, resumes *that* instead.
- **The claim is KEPT.** PROTOCOL rule 2 stands: a claim is the done-marker and the record. The skip governs where
  `next` **sends** you, never what you **held**. Nothing is deleted.

## 3. ⛔ The guard the brief did not ask for, and why it is the load-bearing half

"Skip a claim whose topic is absent from the queue" is a **fleet-wide unpin** the moment `QUEUE.tsv` is missing,
unreadable, or caught mid-rewrite: *every* claim looks orphaned at once, and all eight seats are simultaneously told
to abandon what they hold. That is this project's own **"non-empty is not alive"** false-signal class (the absent
oracle, s33/s40/s43/s44) arriving by a new route.

**Orphan-skip therefore disarms itself when the queue has zero data rows.** An unreadable queue is an
infrastructure failure, not a rename, so `next` **pins and says so**:

```
⛔ <path>/QUEUE.tsv IS MISSING OR HAS NO ROWS — cannot tell a renamed row from an unreadable queue,
   so RESUMING <topic> rather than unpinning you. Ask hq before trusting any next(1) verdict.
```

`util_postoffice_sweep.sh` refuses on the same condition (exit 2) rather than confidently reporting 69 orphans.

## 4. Receipts — negative-tested 7 ways, all re-proved after the rebase

| # | Setup | Required | Observed |
|---|---|---|---|
| T1 | orphan claim + live queue | SKIP, then LOCK a live row | ✅ SKIP + `LOCKED live-row` |
| T1b | same seat runs `next` again | SKIP again, then RESUME the row it locked | ✅ SKIP + `RESUME live-row` + brief |
| T2 | live claim | RESUME with brief — **unchanged** | ✅ identical to pre-patch |
| T3 | orphan + `QUEUE.tsv` **missing** | PIN with reason, do **not** unpin | ✅ ⛔ line + RESUME |
| T4 | orphan + queue present, **zero data rows** | PIN with reason | ✅ ⛔ line + RESUME |
| T5 | no claims at all | LOCK topmost free — **unchanged** | ✅ identical to pre-patch |
| T6 | claim marked DONE | neither a resume nor an orphan report | ✅ falls through, LOCKS |
| T7 | another seat's orphan | not my business | ✅ ignored, LOCKS |

Live bus at rebased HEAD: `RESUME msg-next-orphan-skip` **with** its brief and first step. Tree clean, `HEAD == origin`.

## 5. ⛔⭐ The sweep's headline is not the orphans — the rank column has stopped meaning anything

**45 of 68 `QUEUE.tsv` rows are already DONE**, including **every rank-0 row**: `beauty-return-pair-shift`,
`scorecard-oracle-case`, `defer-depth-floor`, `arbno-tail-false-accept`. Meanwhile `next` was handing out **rank 22**.

A DONE claim hides its row from the picker (`[ -f "$PO/claims/$topic.claim" ] && continue`), so this is **inert to
`next` but misleading to every human who reads the file** — a seat orienting by `QUEUE.tsv` believes the fleet's top
four priorities are unstarted. HQ-59 rebuilt the queue by dropping DONE rows; that prune has not run since.
**This is the actionable half of the row, and it is HQ's to run:** `bash scripts/util_postoffice_sweep.sh` prints the list.

## 6. ⭐ Both sweeps came back clean — which is a result, not a null

**Orphaned claims: 17, and ZERO of them OPEN.** All 17 are DONE — benign HQ-59 residue, since DONE rows are dropped
from the queue by design. Notably **seat5's own `arbno-nullalt-false-accept` is now DONE**: the s189 victim is out of
the trap. **So this cure is prophylactic — validated in sandbox, not on a live pin — and it is reported that way.**
A cure with no live patient must not be written up as one.

**Dirty seat trees: 4, and all 4 map to that seat's OWN open claim** — seat1 ↔ `scorecard-provenance`, seat2 ↔
`gimpel-suite-harness`, seat7 ↔ `alt-tail-resume-surface` (`src/lower/lower_snobol4.c`), seat4 ↔ this row.
**Zero stranded work**, which is precisely the condition that lost seat5's codegen. The cross-check *between* the two
halves of the sweep — dirty tree with **no** open claim = stranded — is what makes the dirty-tree half diagnostic
rather than a list of noise.

**Instrument hygiene, per seat7's s189 lesson:** the sweep is read-only by construction, invokes
`git --no-optional-locks` so it can never contend with another seat's live build for the index lock, uses no
`pgrep -f`/`pkill -f`, and suppresses `corpus/programs/lon/` paths to a bare count (RULES.md: not run, not read).
**The bus is live** — it grew 65 → 68 rows *while this rung ran* — so every count here is stamped s191/2026-08-20 and
is re-derivable by running the script, never by trusting the number.

## 7. ⛔ One deliverable is blocked: a permission, plus a durability gap worse than the block

**I could not write `/home/resources/postoffice/PROTOCOL.md`** — it is outside this seat's writable root and the edit
was refused. I did not work around it.

**The attempt exposed something worse than my block: `/home/resources/postoffice` is not a git repo.** `PROTOCOL.md`
(and `SEAT-CLAUDE.md`) are the fleet's law and exist in **one unversioned copy on one box** — no history, no diff, no
recovery — while the bus's own rule 5 reads *"NEVER a message instead of the pushed record."* **The law has no pushed record.**

So the section did not ship as a hand edit. It ships as `scripts/util_postoffice_protocol_sync.sh`: **idempotent**
(no-op if already installed), **anchored**, and **refusing rather than guessing** if `PROTOCOL.md` has been rewritten.
Tested three ways — install, re-run no-op, anchor-missing refusal. One command by HQ or any seat with write access
installs it; either way **the text is in git**.

## 8. ⭐ The generalisable move

**A lookup that prints is not a lookup that checks.** `RESUME <topic>` with an empty brief was the entire symptom,
and it read as a cosmetic glitch rather than a permanent pin. Wherever a tool prints what it found, ask what it
prints when it finds **nothing** — if the answer is "nothing", that is a silent failure wearing a friendly face.

Same family as two findings already on the board: s189's `default: return 0` (an unlisted op inherits "unsafe"
without anyone deciding it), and s170's ratchet (a count assembled from the violations already seen is permanently
one syntax behind the code). **The fix in all three is the same shape: make the check and the thing it reports be
one computed expression, and give it a defined answer for the empty case.**

## 9. Next (named so they cannot be orphaned)

1. **HQ: prune the 45 DONE rows from `QUEUE.tsv`** (HQ-59's own policy). `util_postoffice_sweep.sh` prints them.
2. Run `util_postoffice_protocol_sync.sh` once from a seat that can write the bus.
3. **Give `PROTOCOL.md` and `SEAT-CLAUDE.md` a git home.** They are law with no record.
4. HQ LAW 14 (rename and unpin are ONE action) stays as policy — **both halves, not either**; the mechanical half
   does not depend on HQ remembering, and the policy half covers renames the mechanical half cannot see.
