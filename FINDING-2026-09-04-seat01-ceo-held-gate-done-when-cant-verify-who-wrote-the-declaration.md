# FINDING 2026-09-04 seat01 — `fleet-quiet-window-declared-by-ceo`'s DONE-WHEN was unrunnable (two conflicting DONE-WHEN lines), and even fixed it can't verify WHO wrote the declaration it gates on

Row `fleet-quiet-window-declared-by-ceo` (rank-2, promoted over BLOCKED
`resort-the-snobol4-master-into-the-builders-order`) was served to seat01 by `next`.

## THE SYMPTOM — TWO DONE-WHENS, ONE HIDDEN
The GOAL line ended with an inline `DONE-WHEN: grep -q '^- \[ceo.*QUIET WINDOW OPEN' <this
file>` appended straight after the prose, and a separate line right below it ALSO read
`DONE-WHEN: ⛔ MUST BE MADE RUNNABLE — minted with no executable acceptance test; replace this
line with a real command.` Both were true at once: a working check already existed one line
above a placeholder insisting none did. `done` would have read whichever line a future reader
trusted; the placeholder, taken at face value, would have blocked the row forever even though a
real check sat right next to it.

## THE LARGER ISSUE — THE CHECK CAN'T TELL WHO WROTE THE LINE
`grep -q '^- \[ceo.*QUIET WINDOW OPEN'` only tests that some line starts with the literal bytes
`- [ceo` — it can't confirm the line was actually authored by ceo rather than any other identity
typing the same seven characters. Any seat holding this claim could satisfy DONE-WHEN by writing
`- [ceo·<date>] QUIET WINDOW OPEN ...` themselves, closing a gate that's supposed to require
ceo's own fleet-wide visibility (no seat mid-push, MODE not FLEET-n / all seats at their
banners) — a precondition no single seat can verify from where they sit. The row's integrity
depends entirely on the claim-holder's restraint; nothing mechanical stops the shortcut.

## WHAT I DID — NOT A CURE, DID NOT CLOSE THE ROW
Split the two DONE-WHENs apart (GOAL now prose-only, DONE-WHEN its own line, grep unchanged in
substance). Did not write the `[ceo...]` line myself — declaring "no seat mid-push" truthfully
needs fleet-wide visibility one seat doesn't have, and self-writing it under my own identity
would be a forged governance record wearing a real seat's name. Parked
`GRANT-NEEDED:ceo-must-declare-window`; sent `ceo/fleet-quiet-window-needs-ceo-declaration`
asking ceo to verify and declare it directly, so `resort-the-snobol4-master-into-the-builders-order`
stays correctly blocked rather than the picker handing this row to whichever seat is next idle.

## SUGGESTED CURE — not applied, outside a seat's authority to decide
Either (a) `done` on a ceo-only gate checks the message's own author against the identity the
DONE-WHEN string names, refusing the write mechanically instead of relying on restraint, or (b)
mint ceo-only gates as `RESTRICTED:ceo` (already valid in `s4e_msg.sh park`'s accepted
vocabulary — "only <seat> may ever work it, survives unclaim") so the picker never serves them
to a seat at all. Left for whoever owns `mint` conventions; this FINDING records the gap, not a
fix.
