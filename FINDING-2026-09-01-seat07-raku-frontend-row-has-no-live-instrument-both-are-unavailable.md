# FINDING 2026-09-01 (seat07, pass 39) — A ROW WHOSE BOTH POSSIBLE INSTRUMENTS ARE UNAVAILABLE, AND THE QUESTION THAT DID NOT NEED ANSWERING

**Row:** `raku-frontend-real-world-syntax-gaps` (rank 1) — now PARKED `BLOCKED-ON:raku-roast-100-percent-compile`.
**Companion to:** `FINDING-2026-09-01-seat08-a-lon-ruling-reached-one-row-and-not-its-sibling-running-the-same-retired-instrument.md` (`.github` `54cb365e`), which this confirms and extends.

## 1. A QUESTION WHOSE EVERY ANSWER YIELDS THE SAME INSTRUCTION IS NOT A BLOCKER

Pass 38 found that Lon's 2026-08-30 ruling — the bison/flex Raku grammar is the wrong instrument, Raku is
not LALR, `raku.y` can never be finished (`GOAL-RAKU-100.md:274`) — had never reached this baton across 37
passes. Correct, and it stands. Pass 38 then asked HQ whether the ruling, which names only the sibling row
`raku-roast-100-percent-compile`, extends to this one, and ended: *"pick by HQ's answer."*

⭐ **It does not need answering to act.** Both branches forbid the same action:

| branch | consequence |
|---|---|
| ruling extends here | `raku.y` is retired — do not patch it |
| ruling does not extend | row is gated on the `:=`/binding ARCH ruling still absent after **18+ passes**; pass-33 item 3 forbids attempting it; and the parse-only `:=` that would flip 2 of 5 against this row's own parse-only DONE-WHEN is a **false green** — `:=` cannot be correct as a copy, since `rc-9-billion-names:11` needs `@x.shift` to mutate *through* the binding into `@todo[$x]` |

⛔ **The generalisable shape: before escalating an either/or, evaluate the action under both branches.** A
question that changes nothing you would do is a note for the record, not a gate — and filing it as a gate
costs a pass per seat who honours it. seat08 was right to refuse to widen a Lon ruling on their own
authority; the avoidable part was treating the unanswered question as the reason the next pass could not
proceed.

## 2. THE NEW MEASUREMENT — THE REPLACEMENT CANNOT YET ACCEPT THIS ROW'S KERNELS

Pass 38's branch A read "PARKED **or** re-pointed at `tools/rakugram/`". Measured on a freshly pulled
SCRIP, the "or" is not live — each receipt is one command:

```
grep -n 'rakugram\|rk_hll\|nqp_' Makefile               -> EMPTY   not built as part of scrip
grep -rn 'rakugram\|rk_hll' src/parsers/raku/           -> EMPTY   frontend is still 100% raku.y/raku.l
grep -rn '\.raku' tools/rakugram/*.py tools/rakugram/*.c -> EMPTY   no .raku entry point exists
ls src/parsers/raku/  -> raku.y raku.l raku.tab.c raku.lex.c raku_driver.c re.c
```

`tools/rakugram/` is at **rung 7 of an open ladder: 52.0% mechanical, 214 rules generated, 265 refusing**
(`tools/rakugram/README.md`; SCRIP `bcb0ec1e`, `.github` `59fda7dd`) — and that figure went *down* from
56.7% because hq_C made five placeholder primitives stop lying. It is a standalone research toolchain, not
yet a frontend: nothing links it, nothing calls it, it cannot be pointed at a `.raku` file.

⛔ **So both of the row's possible instruments are unavailable — the historical one retired by the
reasoning of the ruling, the replacement unable to read the file type the row is made of.** That is why 37
passes produced 5/5 five separate times. It is not a Raku finding; it is the shape of a row that has
outlived its tooling, and the symptom is a stable measurement that never moves while real effort is spent.

## 3. WHY PARK, NOT RELEASE — THE DISPATCHER STATE IS THE ONLY DURABLE PLACE TO PUT THIS

Passes 36, 37 and 38 each **RELEASED** the row. Release returns it to the picker at rank 1, and by the
dependency inversion `next` itself prints, it is the promoted blocker for rank-1 `bench-rivals-raku-pascal`
— so the picker hands *the topmost work in the fleet* to the next idle seat, who cannot advance it. Three
consecutive releases are three seats independently rediscovering one wall.

⭐ **A conclusion recorded only in a baton is re-derived; a conclusion written into the dispatcher is
obeyed.** This is the s265 `park` lesson recurring (a Lon-parked row still read FREE, and seat08 had to sit
on a claim to stop the picker re-serving it). Parked with the self-clearing spelling, so nobody must
remember to undo it — `next()`'s PASS 3 un-parks it the moment hq_C's rank-0 row goes DONE:

```bash
bash SCRIP/scripts/s4e_msg.sh park raku-frontend-real-world-syntax-gaps BLOCKED-ON:raku-roast-100-percent-compile
```

⚠️ **Note on where this finding had to live.** `/home/resources/postoffice/` is not a git repository, so a
result written only into a `.task.md` is unversioned and invisible to anyone not holding that row. That is
a contributing cause of the 37-pass blindness pass 38 measured: the baton is the baton, but a finding about
*routing* has to reach `.github` to be found by anyone else.

**No code touched, no build run, no DONE-WHEN number claimed** — the row's last measured figure remains
pass 37's 5/5, and re-taking it would have measured the retired instrument to re-derive a number pass 38
explicitly told the next pass not to re-derive.
