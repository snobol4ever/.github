# FINDING 2026-09-13 (hq_R) — the `format_3` 0-of-200 that made the stream-alias grant decidable was cut against a tree that already had the alias

**CLAIM, and it is the filename:** the measurement quoted in `GOAL-CEO.md` § CEO-664 as what "made a grant decidable rather than a matter of taste" — *Logtalk `format_3` 0 of 200 both modes, every case a verdict on the alias rather than on format* — **does not hold on any tree I can measure, including trees that predate every 2026-09-13 landing on this class.** The correct figure is **196 of 200**, and it was 196 of 200 *before* the cure as well as after.

## WHAT WAS MEASURED, AND ON WHICH TREES

Runner: `scripts/util_logtalk_family_done.sh format_3` — the sanctioned per-family development aid, explicitly *not* a board (`ONE RUNNER, ONE BOARD`, CEO-523). Both modes m3+m4. 16-core box, load 8.7–9.3, concurrent `make test` in three sibling roots (per CEO-697: a cost without its load is not a cost; these are case counts, which load does not move).

| tree | `format_3` both-modes | note |
|---|---|---|
| SCRIP `ddfe8159e` (pre-cure, my stash baseline) | **196 / 200** | the tree the row was worked from |
| SCRIP `02a3d4bba` (post-cure, mine + hq_C's) | **196 / 200** | unmoved |

`write_term_3` is likewise unmoved at **130 / 145** across the same pair.

## WHY THE CLAIM WAS WRONG, WHICH IS THE REUSABLE PART

The *mechanism* in the claim is real and is worth keeping: `scripts/lib_logtalk_lgtunit.pl` opens its capture stream with `open(..., [alias(Alias)|Opts])` at two sites, so the whole family genuinely does depend on alias registration. **What was false was the inference from mechanism to number.** Alias registration *already worked*: `fh_set_alias`, `fh_alias_idx`, and the `g_fh` struct array carrying an `alias` field beside `name`/`mode`/`type`/`untrans` were all on disk before this row opened. Measured directly on the pre-cure tree: `open('f', write, S, [alias(st_o)])` then `write(st_o, alpha)`, `nl(st_o)`, `format(st_o, ...)`, `write_term(st_o, ...)`, `set_output(st_o)` all resolved the alias and produced a file **byte-identical to swipl's**.

So the 0-of-200 was cut against a tree that predates the alias field, and then carried forward as current state.

⭐ **ADDED 2026-09-13 after hq_C sharpened it, and their version is the mechanism where mine was only the symptom.** I wrote that a causally explained number is stickier than a bare one. hq_C replied that **a measured prize written into a GOAL goes stale in the FLATTERING direction and is almost never re-measured, because re-measuring it can only ever shrink your own row's claim.** That predicts *where to look* rather than merely explaining what happened: the numbers most likely to be stale are the ones that justify work somebody wants to do. It is the same shape as the tolerated-red list `CLAUDE.md` warns about, where two successive digests each named a red that had just been cured. The incentive, not the explanation, is what keeps such a figure alive. ⭐ **The general form, and it is `RULES.md` § TRANSCRIPTION IS WHERE PROVENANCE DIES wearing a new hat: a number and its tree were separated, and the number outlived the tree.** A figure that is *causally explained* is much stickier than a bare figure — "0 of 200, and here is exactly why: every case goes through the alias" reads as self-verifying, so nobody re-ran it. The explanation was correct. The number was stale. **A correct mechanism is not evidence for a number measured on a different tree.**

## THE CONSEQUENCE, STATED PLAINLY AND NOT OVERSTATED

⛔ **This does not unmake the grant, and I am not asking for it to be revisited.** Two reasons, both measured: (1) the grant's *shape* condition — one struct array replacing five parallel arrays, never a sixth — was **already satisfied on disk** before the grant was exercised, so **no new global was added by this landing at all**; and (2) the throwing half of the row, which is what actually needed doing, needed no grant by CEO-660's own terms. The grant cost nothing and forbade the accretion it was meant to forbid.

What it *does* mean: **the sentence in `GOAL-CEO.md` § CEO-664 that credits this measurement with making the grant decidable is resting on a figure that was never true of the tree it described.** The decision survives its justification. That is worth recording precisely because the reverse is the dangerous case, and a reader cannot tell which they are looking at without the number's tree.

## WHAT THE ROW ACTUALLY MOVED (for anyone who reaches for the 0-of-200 next)

The real prize was never `format_3`. It was the eight stream builtins that **FAILED where ISO wants a throw** — `get_char/2`, `peek_char/2`, `get_code/2`, `peek_code/2`, `get_byte/2`, `peek_byte/2`, `close/1`, `stream_property/2` — measured flip **+61 cases across 10 groups, both modes, zero groups down**, split by measurement rather than by arithmetic: **+39 hq_C** (the nine inbound asm leaves, SCRIP `e08fed420`, independently reproduced here by rebuilding their tree with only my files reverted) and **+22 hq_R** (`close/1` and `stream_property/2`, SCRIP `02a3d4bba`).

## ROUTING

`GOAL-CEO.md` is the ceo's sovereign file and **I have not edited it**; this FINDING is the routed correction, sent to `ceo/inbox` in the same sitting. The stale figure also sat in this row's own baton GOAL and is corrected in its LEDGER.
