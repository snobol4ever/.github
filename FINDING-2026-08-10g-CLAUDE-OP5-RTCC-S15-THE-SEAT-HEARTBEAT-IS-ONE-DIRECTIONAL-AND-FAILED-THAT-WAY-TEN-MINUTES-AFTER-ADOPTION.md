# FINDING 2026-08-10g — RTCC s15 (Opus 5)
## The seat heartbeat is ONE-DIRECTIONAL: it can only see seats that opened BEFORE yours. It failed exactly that way within ten minutes of being adopted, and the seat it left blind was the one holding the tree.

**Class:** RC-0 / process. **ZERO emitter bytes, ZERO source edits, ZERO script edits, no regen owed.** Docs only.
**Tree:** worked entirely in a PRIVATE clone (`/home/claude/s15-rtcc/dotgithub`). The live peer's worktrees at `/home/claude/{SCRIP,.github,corpus}` were **read, never written** — s12's convicted error not repeated.
**Rung not executed:** none. This session opened intending RC-6/WREG arbitration and discovered that rung was already in flight. See §5.

---

## 1. What happened

s15 opened at **23:54:11Z**, ran the s13b-adopted heartbeat (`touch /home/claude/.seat-rtcc-$$` + `find /home/claude/.seat-* -mmin -30`), and found a **second seat**: `.seat-rtcc-473`, stamped **23:44:14Z**. That peer had committed `FINDING-2026-08-10f-...-RTCC-S14-...` at **23:52:55Z** — an RTCC finding on the WREG r10/r11 question, **the exact rung s15 had selected**. The check saved a full duplicated rung on its first real use.

It also, in the same breath, proved itself broken. The peer's own §8 records:

> `find /home/claude/.seat-* -mmin -30` returned empty ⇒ single seat this session.

That was **true when they ran it** and **false ten minutes later**. Both halves are timestamped and reproduce from the filesystem.

## 2. ⭐ THE MECHANISM — DETECTION IS A FUNCTION OF ARRIVAL ORDER, NOT OF OCCUPANCY

Seat A opens at t0; seat B opens at t1 > t0. A's check runs at t0, when B's file does not exist ⇒ **A sees nothing, forever.** B's check runs at t1, when A's file does exist ⇒ **B sees A.**

⇒ **The later seat always detects; the earlier seat never does.** This is not a tuning problem, it is the shape of a check that runs once at open. And the asymmetry points the wrong way: the seat left blind is the EARLIER one — which is precisely the seat that has already built, already holds the tree, and is mid-flight. The convention informs the seat that can most cheaply yield and conceals the collision from the seat with the most to lose.

**Second, independent failure mode — MTIME STALENESS.** `-mmin -30` is a liveness proxy over a file written once at open. A session that runs longer than 30 minutes ages out of its own window while fully live, and becomes invisible to every later arrival. The two modes compose: a long-running early seat is undetectable in both directions.

## 3. THE FIX (cheap, mechanical, no new infrastructure)

1. **RE-CHECK AT THE MOMENT OF MUTATION, NOT ONLY AT OPEN** — before each commit and again immediately before push. A check at open answers *"who was here when I arrived"*; the question that matters is *"who is here now that I am about to write."*
2. **REFRESH THE BEAT** — re-`touch` the seat file at every rung boundary, so liveness tracks the session rather than its first minute. Kills the staleness mode.
3. **CARRY THE GOAL AND THE OPEN TIME IN THE NAME** — `.seat-<goal>-<pid>` is already the s13b spelling; adding the open timestamp inside the file makes a stale file self-diagnosing.
4. Optional, if this recurs: fold 1–3 into `scripts/seat.sh open|beat|check` so no seat has to remember the sequence.

⛔ **This does not gate work and must not be read as a window.** RULES.md 2026-08-10 is unambiguous — commit and push freely, merge, never park. The heartbeat's only job is to stop two seats *unknowingly executing one rung*; nothing here licenses waiting on a peer.

## 4. ⭐ NEW LAW — A PRESENCE CHECK RUN ONLY AT OPEN MEASURES ARRIVAL ORDER, NOT OCCUPANCY

Any mutual-visibility signal must be re-read at the instant of the action it protects. Read once at session open, it answers a strictly different question than the one asked, and its answer decays monotonically toward wrong for the rest of the session. **Same class as s13b's macro-blind assembly census and s11's `LD_AUDIT` complement: an instrument returning a clean answer to a question nobody asked.** The tell is identical in all three — the answer was *empty*, and empty was never checked against a known-nonempty control. A presence check that has never once returned a hit is indistinguishable from a broken one.

## 5. WHAT THIS COST TODAY — FOURTH OCCURRENCE IN ONE DAY

s11/s12 (worktree misread) · s13/s13b (same goal file, two seats) · s13b (phantom `.so`) · **s14/s15 (same rung, two seats)**. The convention was adopted *because of* the first three and did not prevent the fourth; it converted it from a silent collision into a detected one **for the arriving seat only**. s14's work stands in full and is not duplicated here — s15 read it and stopped.

⚠ **UNEXPLAINED-PROVENANCE EVENT, SECOND OCCURRENCE (s13b's law applied).** s15's orientation clones at `/home/claude/work/{SCRIP,corpus,.github}` were **gone** at rung open, with identically-sized trees present at the canonical `/home/claude/` paths bearing the same 23:35 mtimes. Mechanism unestablished; almost certainly the peer relocating them to the paths the scripts expect. Per s13b, an artifact whose provenance cannot be established is not an artifact: nothing there was trusted or reused, and this rung ran from a fresh clone.

## 6. NOT DONE / OPEN

- **No RTCC ladder rung executed.** RC-5 ANCHOR call-site re-open, RC-6 (blocked on per-family RTX eradication) and RC-6b (⛔ Lon rules) are untouched and remain as s13b/s14 left them.
- **No build, no watermark re-proof.** A build in this container would have raced the peer's; the honest statement is that s15 has no measurement, not that it has a passing one.
- **The WREG r10/r11 arbitration is s14's**, concluded there as a *mechanism* collision (leaf crossings round-trip, re-entrant ones do not), not an allocation collision. s15 adds nothing to it and defers.
- ⛔ **Cursor edit deliberately NOT made.** GOAL-RTCC.md's LIVE CURSOR is being written by the live peer this minute; a competing top-of-section block would manufacture a conflict for zero benefit. This FINDING is a new file and cannot conflict. **Whoever lands last should add the one-line s15 pointer.**
