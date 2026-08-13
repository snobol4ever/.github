# FINDING — B-12's missing "anchor-relative ARBNO cell" (W-7 guard, `bb_match_arbno.cpp`) is not an
# open design question. `GOAL-RBP-EARN.md`'s EARN DESIGN OF RECORD already specifies it, verbatim, for
# an unrelated reason (offset-earning under the EARN predicate). Same mechanism, two motives, one fix.

**Author:** Claude Sonnet 5 · **Date:** 2026-08-13 · **Repos at read time:** SCRIP `5547de99` · `.github` `58f0b0ee`
**Rung:** GOAL-SN4-HOME-BOARD B-12 (resumable generator through a DEFER) — this finding is diagnostic /
cross-referential, not a landed fix. No code changed. Session-start reading (manual Ch.9 pp.121-123) not
yet done — the PDF was not available this session; do not treat the manual citations below as re-verified,
they are carried forward from the existing in-repo comments that already cite them (SEQ-RESUME-GATE,
`lower_snobol4.c:1182`; W-7 guard, `bb_match_arbno.cpp:222-233`).

## The observation

`bb_match_arbno.cpp`'s W-7 guard refuses to emit `bb_match_arbno_frameless()` whenever the ARBNO body
carries an `IR_MATCH_DEFER` with `pat_static==0` (the manual's `ARBNO(","‚*ITEM)` / `ARBNO(*group)`
idiom), because that arm's control cell is addressed **`[rsp+0]/[rsp+4]`, relative to the current
frontier at each site**. A DEFER body can transitively recurse back through the *same* ARBNO node's own
activation (self-reference through `*name`); the nested activation then reads/writes the identical
`[rsp+K]` cell as the outer one, at a different actual depth — a live aliasing stomp, gdb-confirmed on
D12/D13 (`FINDING-2026-08-12k`). The guard's own comment names the fix it's waiting for:

> "the real fix needs an anchor-relative ARBNO cell (W-4's arena layout)"

That fix has already been specified — not by BOARD, not for this bug — in `GOAL-RBP-EARN.md`'s **EARN
DESIGN OF RECORD** (s28, Lon in-chat, ARBNO section):

> *"On ARBNO you would not setup another RBP at BETA, you would use RBP to access ARBNO's RESULT or
> LOCAL."* ... *"ENTER once, at α. β is the SAME activation — the frame is already live. β reaches
> ARBNO's cell at `[rbp+K]` and the anchor at `[rbp+ANCHOR]`."* ... *"a cell addressed off rbp is immune
> to whatever P does to the spine beneath it. P's growth stops mattering entirely."*

RBP-EARN derived this because their EARN predicate (`byte distance to RSP not a compile-time constant`)
fires on ARBNO's rolling cell for offset reasons that have nothing to do with DEFER or recursion — but
**the mechanism is identical to what W-7 is refusing to emit without**: one frame established at α,
ARBNO's delta/yield-cursor cell at a fixed `[rbp+K]`, read through the live frame at β regardless of how
deep rsp has moved. A frame per activation means a *recursive* activation (the DEFER-body self-reference
case) gets its *own* frame and its own `[rbp+K]` — the aliasing W-7 exists to prevent cannot occur,
because there is no longer a single shared rsp-relative address for two activations to collide on.

## What this does and doesn't establish

- **Does:** the two seats' independently-reached designs are the same shape. RBP-EARN's EARN-4 rung
  text (`GOAL-RBP-EARN.md`, "EARN-4, RESTATED UNDER THIS DESIGN") already reads as an implementable spec
  for W-7's blocker: *"DELETE the `sub rsp,16` carve and every `[rsp+0]`/`[rsp+4]` cursor access. Rebuild
  as: ONE frame at α; ARBNO's control datum ... at a fixed `[rbp+K]`; β reads through it; exhaustion read
  from the cell."*
- **Does not:** confirm EARN-4 as written also solves the *recursive re-entry* case the way this finding
  assumes. EARN-4's own gate is `arb1.sno` T1/T2 + N22–N33 + probe `181` + `board_patterns_set.sh` — none
  of those are named as DEFER/recursion witnesses. The design was proven against the OFFSET hazard;
  whether "one frame per activation" mechanically also clears the ALIASING hazard (rather than just
  relocating it — e.g. if the recursive call reuses the *same* rbp instead of establishing a fresh one)
  is an implementation question, not yet checked against either seat's code.
- **Does not:** replace the manual grounding both goal files prescribe before implementation. The p.122
  `*P`/recursive-pattern semantics are cited by existing comments (SEQ-RESUME-GATE, W-7) but I have not
  independently re-read those pages this session — the uploaded manual PDF was unavailable when this
  finding was written.

## Recommendation for whoever picks up B-12 next

Read `GOAL-RBP-EARN.md`'s EARN-4 rung as the starting *spec* for the "anchor-relative ARBNO cell," not as
prior art to rediscover independently. Before implementing: (1) get the manual's Ch.9 pp.121-123 read as
prescribed, specifically to confirm what "one frame per recursive activation" must guarantee for a
self-referential `*group`; (2) check RBP-EARN's live cursor for an in-flight claim on `bb_match_arbno.cpp`
before landing anything — EARN-4 is RBP-EARN's own rung and this seat (BOARD) owns B-12 solely per Lon's
s44 ruling, so a merge of intent, not a race, is wanted here, and it should be said in-chat which seat
implements EARN-4 / the W-7 fix rather than both independently opening it.
