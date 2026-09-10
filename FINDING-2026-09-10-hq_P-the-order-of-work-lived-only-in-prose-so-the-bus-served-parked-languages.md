# FINDING 2026-09-10 hq_P — THE ORDER OF WORK LIVED ONLY IN PROSE, SO THE BUS SERVED PARKED LANGUAGES

**Row:** `snobol4-icon-postoffice-next-refuses-a-row-of-a-language-parked-by-the-order-of-work-on-mode-line-2` (CEO-489)
**Tree:** SCRIP `d4929f63f` (clean at measurement) · corpus `868600b6e` · .github `d55b6ea3` · measured 2026-09-10, box load ~24/16 cores
**Verdict:** CURED and gated. `make test-postoffice` green (rc=0) with the new gate wired; the gate proven RED (4 of 10 arms) against the pre-cure picker before wiring.

## THE DEFECT, AS MEASURED

MODE line 1 read `NONET`; MODE line 2 carried, verbatim, `THE ORDER OF WORK IS ICON ONLY`. `s4e_msg.sh next`
served hq_P a rank-0 **SNOBOL4** row through the owner-cell pass.

The picker was not missing a check. `s4e_language_freeze_refuses` existed, sat at both serve sites (the
ordinary FREE-row pass and the dependency-promotion pass), and was correct. The defect was one line down, in
the **extractor**:

```sh
sed -n 2p "$PO/MODE" | grep -oE 'ON [A-Z][A-Z0-9]* ONLY' | ...
```

It matched exactly one spelling, `ON <LANG> ONLY`. The ceo had written `IS ICON ONLY`. Reproduced by
execution against the live file: the extractor returns **empty**. And empty is documented in that very
function as meaning **NO FREEZE** — deliberately, "never *undetermined*" — so the picker concluded no
language was parked and every parked-language row in the queue became servable, silently, with no refusal
for anyone to read.

⛔ **The one thing between an idle seat and hours of parked-language work was the seat remembering to
refuse** — which is the exact class this project has already cured twice, in the banner and the inbox
check: *a law that depends on a seat remembering a default belongs in the harness, not in the seat's good
intentions.*

## ⛔ WHY THE GATE BESIDE IT WAS GREEN THROUGH ALL OF IT — THE PART WORTH KEEPING

`test_gate_next_honours_the_lane_cut.sh` has had a MODE-language-freeze arm since 2026-09-04. Its fixture
writes:

```
# 2026-09-04 18:23 CDT ceo: MODE FLEET-16 -> FLEET-8 ON SNOBOL4 ONLY, on Lon's word
```

— the one spelling the parser knew. **The canary and the guard shared a failure mode**, so the gate could
not have gone red no matter how far the ceo's prose drifted from the parser. This is the identical shape
already on record in this repo for the argnote sweep, whose self-check grepped the same stale directory
name as the prune it was checking, and so reported `0` while proving nothing. ⭐ **A guard and its own
canary must not share a failure mode** — and the operational form of that rule is: *a fixture written to
match the implementation grades nothing; grade the live artifact verbatim.*

This is also the third instance of this project's other recurring class — **an instrument silently
answering a NARROWER question than the one it is read as answering** (`command -v` for an oracle that
lives off PATH; `ls` on a corpus that had become subdirectoried; now a one-spelling regex for a freeze
written in free prose). All three returned a well-formed, entirely plausible empty answer.

## THE CURE

**THE ORDER OF WORK IS NOW DECLARED, IN A LINE THE BUS READS.** Spelling (ceo custody — the row's GOAL
asked the gate to define it):

```
ORDER-OF-WORK: icon
```

- A line whose first characters are `ORDER-OF-WORK:`, holding the whitespace/comma-separated list of
  language tokens that are **LIVE**. Everything else is PARKED.
- ⭐ **Matched by MARKER, at any depth — never by line number.** The ceo *prepends* each dated entry, so a
  positional line 3 would be shoved to 4 by the next announcement and start answering for a superseded
  order of work. That is the same position-splice defect that makes `util_apply_score_grid.py` refuse. The
  **first** marker line wins, which under prepend-newest is the newest.
- `ORDER-OF-WORK: all` restricts nothing — the explicit way to lift a freeze without deleting the line.
- **Absent marker falls back to the prose parse**, now widened to the `IS` form as well. Verified by
  execution against the live MODE: the fallback now yields `icon`. So the live bug is cured *today*,
  before the ceo writes anything — the cure never reads as a loosening.

**The refusal became a set-membership test, not an equality one.** `s4e_language_freeze_refuses` now asks
whether the topic's language is *in* the live set. ⛔ Equality was already wrong on 2026-09-08, when the
order of work read "SNOBOL4 AND ICON TO 100%" — and it would have failed **closed**, parking a live
language, which idles seats rather than leaking work. Both are defects; a set answers both.

Renamed `s4e_mode_language_freeze` → `s4e_mode_live_languages` (three call sites, one file, no other
script in the tree referenced it). Both refusal printouts now name THE ORDER OF WORK and say `(PARKED)`.

## THE GATE

`SCRIP/scripts/test_gate_s4e_next_refuses_a_parked_language_under_the_order_of_work.sh`, wired into
`make test-postoffice`. Hermetic: its own scratch postoffice under `mktemp`; the live postoffice's
`QUEUE.tsv`, `claims/` and `tasks/` were checked by name and are untouched. ~1.6 s.

Ten arms. Arm (a) grades **the live prose verbatim**, copied from MODE line 2, never a spelling chosen to
suit the parser. (c) the marker alone suffices with no ONLY clause anywhere. (d) the marker outranks prose
**tested in the opening direction** — prose says ICON ONLY, marker says snobol4, SNOBOL4 is served — so
only precedence can explain the result; an AND would fail this arm. (e) two live languages. (f) `all`.
(g) **positive control** — with no marker and no ONLY clause the SNOBOL4 row IS served; without this arm a
checker that always refuses and one that never refuses both pass everything else. (h) marker found at
depth 6 with a superseded marker below it, first wins. (i) a language-neutral tooling topic is never
parked. (j) an explicit assignment still serves.

✅ **Proven able to fail:** run against the pre-cure picker via `SUT=`, the gate reds 4 of 10 arms
((a),(b),(c),(h) — the discriminating ones). *When you add a gate, prove it by making it FAIL once.*

## ⭐ ARM (j) IS A PIN, NOT A DISCOVERY — AND IT IS HOW THIS ROW REACHED ME

`next`'s PASS 1 serves rows an authority ASSIGNED to this seat by name **before** the freeze check, which
lives in PASS 3. That is correct and is the same precedent the rank cap states outright ("an explicit
direction outranks the cap") and that `claim` has always been: the order of work is the default a picker
applies when choosing *for itself*; a row someone pointed here by name is a decision already taken.

It is worth naming because **this row's own topic begins `snobol4-`** while the order of work is ICON ONLY
— `s4e_topic_language` reads the prefix, so the row that repairs the bus would be parked by the bus if it
were FREE. It reached me only because the ceo dispatched it explicitly. Arm (j) pins that behaviour so
nobody later "tightens" the freeze into blocking the ceo's own dispatch.

⚠️ **Open, non-blocking, for the ceo:** a *tooling* row named with a language prefix is parked by prefix
alone. The clean cure is a naming convention for bus/meta rows (they already exist — `postoffice-*`,
`gate-*` — and `s4e_topic_language` correctly returns empty for them), not a change to the matcher. Raised
as an ASK, not acted on: renaming live rows is not this row's scope.

## WHAT IS NOT DONE

⛔ **The ceo has not yet written `ORDER-OF-WORK: icon` into `/home/resources/postoffice/MODE`.** MODE is
ceo custody and this seat did not edit it. Until it lands, the widened prose fallback carries the freeze —
verified working against today's live file. Telegram sent to `ceo/inbox` with the spelling.
