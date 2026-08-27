# FINDING 2026-08-27 (ceo) — seats asked Lon questions because the seat-facing files taught it; ONE-WAY-CHANNEL law landed (PROTOCOL 7b)

**Trigger:** Lon, in-chat to CEO 2026-08-27, verbatim in substance: *"Several of the Fleet workers got confused and started asking me questions versus coordinating through HQ. Check into how they got confused and see if you can tighten the protocol or instructions to prevent it in the future."*

## ROOT CAUSES (read from the seat-facing files themselves, line receipts)

The confusion was **taught, not invented** — five vectors, none of them a seat misreading:

1. **Three seat-facing lines legitimately name Lon as an ask target, and no line anywhere stated the reverse direction.** `SEAT-CLAUDE.md:12` — the (since-RETRACTED, CEO-14) lon-folder block ends *"stop and ask first"* with no addressee; a seat in a chat with Lon asks Lon. `SEAT-CLAUDE.md:145` — the global-variable rule MANDATES *"Lon's explicit in-chat permission that session"* with a ⛔ banner (by design, but it teaches "Lon is ask-able in-chat"). `SEAT-CLAUDE.md:161` — the credential note ends *"If that fails, THEN ask"* (Lon). A seat generalizes from three sanctioned cases to the unlisted fourth.
2. **Rule 6 (Lon-override) establishes Lon as a legitimate two-way interlocutor** — "Two channels reach you: HQ's brief, and Lon directly" — and the protocol never stated that the Lon channel is one-directional.
3. **The BLOCKED flow ends with the seat facing Lon.** Protocol: rare-blocking → stop. The next event in that chat is Lon's fixed prompt; no script existed for what to say, so seats say their question. The banner carries verdicts, not questions.
4. **The ask channel earned distrust honestly.** CEO-24: for days, `ask` printed "sent" while delivering to a mailbox nobody drained (per-seat HQ files never existed); at least one ask was lost outright. Current measured latency at this tick: hq_C inbox 5 unread/oldest ~10h; answers sit unread in seat inboxes ~60h (seats run only when fired); seat06 has Q=1 pending. A seat that asked and got silence learns the human is the only live channel.
5. **Digest drift generates the very questions that leak.** `SEAT-CLAUDE.md` (the canonical seed) still carries the retracted lon-folder block (contradicts CEO-14) and the retired 6-script regen chain (contradicts CEO-16/RULES handoff step 4). A seat whose file contradicts repo law has a question, and the only in-file addressee was "ask first" → Lon.

## CURE LANDED (the session's one law change)

**PROTOCOL rule 7b — THE LON CHANNEL IS ONE-WAY**, landed in all three places: `.github/PROTOCOL-V2-DRAFT.md` (source of truth), `/home/resources/postoffice/PROTOCOL.md` (the live copy), `/home/resources/postoffice/SEAT-CLAUDE.md` (new LOOP rule 7). Substance: every seat question — blocking or not, including law-contradiction and permission questions — goes `ask <topic>` to the owning HQ, never into the chat. Closed list of Lon-directed asks: (a) push credential after the ssh self-test FAILS, (b) the ⛔-banner global grant, (c) answering a question Lon asked first. A Lon answer to an out-of-protocol ask is a rule-6/7 override — obey and route, it does not legitimize the ask. A BLOCKED seat's whole reply to Lon is one line beside the banner: *"blocked; question filed to HQ as `<topic>`"*.

## RESIDUALS ROUTED, NOT CURED HERE (CEO does not cure)

- **The service half is the other blade:** 7b re-routes questions INTO a channel with measured multi-hour latency. The HQ-side laws already exist (DRAIN first; V2-3 banner refusal on >30-min unread) — HQs should treat drain discipline as re-armed alongside 7b, and the CEO-24 owed follow-up (refusal arm in `s4e_hq()` when the resolved mailbox has no drainer) is still owed.
- **SEAT-CLAUDE.md carries stale law** (retracted lon-folder block, retired regen chain) — flagged to hq_C to fold into the existing digest-drift lane; per-seat propagation of rule 7 rides the standing STEP-0 self-fix mechanism.

**Receipts:** postoffice edits live 2026-08-27; draft edit in this commit; fleet-state numbers from `s4e_msg.sh fleet` this session.
