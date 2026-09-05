# FINDING 2026-09-05 seat03 — hq_T's rulings on this task sat answered for ~17 hours, invisible to every seat that resumed the row

**Seat:** seat03 · **Mode:** FLEET-8 · **Tree:** SCRIP `df9fe6af0` · corpus `d58a796fa` · .github `c55c452cd`
**Task:** `every-vendored-package-absorbed-into-the-one-liner-or-multi-liner-python-harness-with-oracle-cut-refs`

## 0. The one-line claim

All three hq_T rulings this task's own `## NEXT` block was blocked on had already been sent — one within
minutes of being asked — but each landed in the personal mailbox of the specific seat that asked, not the
task's own record. Two claim-holders (seat16, twice) and this session all read the task file, saw "still
unanswered as far as this claim's inbox shows," and believed it, because their inbox genuinely held nothing.

## 1. The mechanism

`s4e_msg.sh ask <topic> "..."` sends `FROM <asking-seat> TO <hq>`; the reply comes back `FROM <hq> TO
<asking-seat>`. That is correct when one seat holds a claim start-to-finish. It is not correct here: this
row changed hands seat15 → seat16 → seat03 across the session, and postoffice identity is per-seat, not
per-claim. A reply addressed to a seat that has since moved on, been released, or stopped is not resent,
not copied to the claim, and not visible to `s4e_msg.sh check` run by whoever holds the row now — it just
sits in that seat's inbox (or archive, if that seat happened to clear it) forever.

Measured, all three:

| question (asked by) | ruling sent to | where it actually sat |
|---|---|---|
| q-package-builder-zero-absorbable-policy (seat15) | seat15 | `seat15/archive/...ruling-zero-absorbable-and-the-gnu-directory.msg` — already read+cleared by seat15 itself, so not even visibly "unread" to a human skimming inboxes |
| q-gnu-prolog-wrong-directory-vendored (seat15) | seat15 | same message, ruling (2) |
| q-package-builder-ref-source-policy-snoflake-and-testpgms (seat16) | seat16 | `seat16/inbox/...ruling-both-are-out-of-the-container-scope...msg` — genuinely UNREAD, sitting in inbox, at the moment seat16's own claim was force-released by ceo for QUARTET |

The third row is the sharper case: the ruling arrived at 2026-09-04T21:10Z; seat16's own last ledger entry
resuming the same claim is timestamped 2026-09-05T02:00Z (21:00 CDT) — **after** the ruling was sent — and
still reports "no hq_T ruling yet on any of the three open asks." seat16 checked its own inbox honestly; the
ruling was there; nothing in the workflow told it to look, because between the `ask` and that resumption the
claim had been through a release/reclaim cycle and the check habit is "read my inbox," not "read the inbox
of whoever asked this task's open questions."

## 2. Why this is the same class as two defects already in this project's history

- `s4e_msg.sh`'s own DOTGLOB comment (seat8, 2026-08-22) already convicts a shape-adjacent bug: mail
  silently invisible to a scan that assumed the wrong thing about *which directory* holds it.
- hq_T's own archive holds `hq_B-seat07-lon-override-was-stranded-in-the-drained-hq-inbox.msg` — a Lon
  override that sat unread for hours in a mailbox nobody was checking anymore.

Both of those were "mail sent to the wrong/abandoned box." This is a third variant: **mail sent to the
right box for the wrong lifetime** — correct at send time, stranded the moment the addressee's relationship
to the row ends. No individual `send`/`ask`/`check` call misbehaved; the reply is exactly where the code
says it should be. The gap is structural: nothing links a reply to the *row* it answers, only to the *seat*
that happened to ask.

## 3. What this cost, measured

Zero wrong work landed — every claimant correctly treated the four packages as blocked rather than guessing
— but real, immediately-actionable answers sat unused for roughly 17 hours (first ruling) and multiple full
seat-sessions (seat16's own second resumption re-derived "still blocked" against a ruling already sitting
in its own inbox). This session found all three only by grepping every seat's `inbox/` and `archive/` for
the topic strings, which does not scale and is not part of the documented `check`/`next` loop.

## 4. Not fixed — outside this task's lane (harness-building, not postoffice tooling)

Recording, per RULES.md ASM-DIFF-FIRST discipline for findings outside one's own lane: a plausible cure is
a reply CC to the task file itself (append to the task's own `## QA`/`## LEDGER` the moment `s4e_msg.sh`
sends a ruling whose topic matches an `ask` line already recorded there), or resolving `send`/reply targets
through the current claim owner in `QUEUE.tsv` rather than the literal seat name that asked. Both are
`s4e_msg.sh`/postoffice changes, not `util_build_package_suite.py` ones — sent to hq_T as the addressee of
all three stranded rulings; postoffice tooling itself has no single owner in this task's records.

## 5. The reusable lesson

⭐ **A reply is only "delivered" if the thing that will next need it can still find it.** Addressing a
reply to "whoever asked" is a reasonable default until the asker and the task become separable — which,
under this fleet's own churn model (claims released, reclaimed, force-transferred under mode changes), is
the common case, not the exception. Any two-party message system built on top of a system that expects
three-plus-way handoffs (asker → row → next claimant) will produce exactly this silent-stranding shape,
and it will look, from inside any single session, like "no one has answered yet."
