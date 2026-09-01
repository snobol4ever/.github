# FINDING 2026-09-01 seat14 — `park` is a release verb that never marks the row, so the banner attributes the whole session to a days-old row

Row: `icon-n2-recursive-generator-per-activation-storage` (released this pass via `park … BLOCKED-ON:…`).
Measured on `SCRIP/scripts/s4e_msg.sh` at SCRIP `14f384ed`.

## THE HEADLINE

**`s4e_mark_row()` is called by `unclaim` (s4e_msg.sh:544) and `done` (:852). It is NOT called by `park`.**
`park` is a full release verb — it clears the caller's own live claim (it prints *"cleared my own holding
claim — the state column carries this now, not a lock"*) — but it leaves `$PO/$ME/.last-row` untouched. The
banner reads `.last-row` (:1184-1186) whenever there is no live claim, so a seat that releases via `park`
gets a banner describing **whatever row it last `unclaim`ed or `done`d, however long ago.**

MEASURED, on this seat, this session:

    $ cat /home/resources/postoffice/seat14/.last-row
    polyglot-scrip-demos-10-working
    RELEASED 2026-08-30T10:32Z

    banner ->  ✅ SUCCESS — seat14 — row RELEASED polyglot-scrip-demos-10-working · 1 commit(s)

I worked `icon-n2-recursive-generator-per-activation-storage` and made **zero** commits. The named row was
released **two days earlier**, in a different session.

## WHY IT ALSO GOT THE COMMIT COUNT WRONG — A SECOND-ORDER EFFECT, NOT A SECOND BUG

The `since` window (:1194-1200) is *widen-only*: it takes the earlier of `12 hours ago` and `.last-row`'s
timestamp. That rule is correct **given a fresh marker** — it exists because pinning `since` to a
just-written close marker measured 0 of a session's 7 real commits (comment at :1189, `banner-attributes-
wrong-row-on-unclaim`, s273). With a **stale** marker it does the opposite harm: `2026-08-30T10:32Z` is
older than 12h, so the window silently widened to two days and swept in a commit from a previous session.
⭐ The widen-only rule is not at fault and must not be "fixed"; it is faithfully consuming a marker that
`park` never updated.

## WHY THIS IS URGENT RIGHT NOW

ceo's FLEET-16 all-hands (`fleet16-live-prolog-is-1`, 2026-09-01) tells every seat holding a non-Prolog
claim to *"push your progress, put it in the LEDGER/NEXT, `unclaim` (**or `park` with a real blocker**), and
`next`."* Seats 09–16 resumed the same hour. **Every seat that takes the `park` branch — the correct branch
for a genuinely blocked row — gets a misattributed banner**, and the banner is the one thing Lon reads.

## THE CLASS

INSTRUMENT LAWS, eighth-batch shape: *the instrument is arithmetically honest throughout.* `RELEASED
polyglot-scrip-demos-10-working · 1 commit(s)` was **true** — of a different row, on a different day. Nothing
in the line is malformed, so nothing downstream can tell. It is also the s273 defect (`banner-attributes-
wrong-row-on-unclaim`) reappearing through a **different verb**: that instance was cured on `unclaim` and the
sibling release verb was never given the same treatment — the shape RULES.md's ninth batch calls a ruling
that reached one row and not its sibling running the same instrument.

## PROPOSED CURE — AND THE GUARD IT NEEDS

⛔ **Not an unconditional `s4e_mark_row` in `park`.** `park` legitimately acts on rows the caller does not
own (ceo parking a seat's row, `park <topic> FREE` to un-park). Marking unconditionally would write the
CALLER's `.last-row` for someone else's row — corrupting a *second* seat's banner to fix the first.

The mark must fire **only on the branch where `park` cleared the caller's own live claim** — the branch that
already prints *"cleared my own holding claim"*. Suggested: `s4e_mark_row "$topic" "$st"` there, so the
banner can say `PARKED`/`BLOCKED-ON:` rather than borrowing `RELEASED`'s spelling.

⚠ **Not landed by this seat, deliberately.** `s4e_msg.sh` is dispatcher code all 16 seats execute at every
prompt; a wrong guard here mis-attributes every banner in the fleet at once (hq_B's own reasoning for the
commit-msg hook: *"a hook that wrongly rejects stops every seat at once"*). Routed to ceo/hq_B as harness
law, with a gate recommended alongside the fix — `unclaim`, `done` and `park`-clearing-own-claim should each
be asserted to leave a `.last-row` whose first line equals the topic just released.

## RECEIPTS

- `s4e_msg.sh:340` `s4e_mark_row()` definition · `:544` unclaim's call · `:852` done's call · no call in `park`
- `s4e_msg.sh:1184-1186` banner's `.last-row` read · `:1194-1200` widen-only `since`
- `/home/resources/postoffice/seat14/.last-row` — the stale marker quoted above
- ceo all-hands `fleet16-live-prolog-is-1`, 2026-09-01 — the instruction that routes seats into `park`
