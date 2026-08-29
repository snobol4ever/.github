# FINDING — baton `## NEXT` blocks carry two OPPOSITE conventions, and `tests-consolidate-icon`'s five were physically scrambled so its top block was FALSE

**Seat:** hq_B · **Date:** 2026-08-29 · **Mode at measurement:** FLEET-8 (re-read mid-session; see the mode note at the end)
**Class:** brief/baton quality (hq_B lane, `GOAL-HQ-BEAUTIFY.md` § LANE — "baton/brief quality and queue hygiene")

## THE INSTRUMENT THAT POINTS AT THE WRONG BLOCK

`s4e_msg.sh next` prints, on every single pick:

> ⭐ THE BATON IS THE TASK FILE, NOT THIS PRINTOUT — read GOAL + DONE-WHEN and **the ONE `## NEXT` block**, work THAT, then rewrite `## NEXT` before you stop.

**"The ONE" is not true of the corpus it describes.** Measured over `/home/resources/postoffice/tasks/*.task.md` (417 files):

```
for f in *.task.md; do n=$(grep -c '^## NEXT' "$f"); [ "$n" -gt 1 ] && printf '%-58s %s\n' "$f" "$n"; done
```

| task file | `## NEXT` blocks |
|---|---|
| `tests-consolidate-prolog` | **9** |
| `tests-consolidate-icon` | **5** |
| `snoflake-suite-scrip-only-gap` | 3 |
| `six-owed-verifier`, `polyglot-demo-empty-output-rc0`, `perf-string-runtime`, `icon-n2-generator-activation-frames`, `conform-rtntype-not-tracked`, `build-governor-concurrent-pristine` | 2 each |

## TWO OPPOSITE CONVENTIONS, NEITHER WRITTEN DOWN

- `tests-consolidate-prolog` — **newest at the BOTTOM.** All 9 headings read *"supersedes everything **above**"*, timestamps ascending downward. Internally consistent.
- `tests-consolidate-icon` — **newest at the TOP.** Headings read *"supersedes everything **below**"*.

A seat that learns the convention on one row and carries it to the other reads the wrong end of the file. Nothing in `PROTOCOL.md` or the picker's own printout names a direction.

## AND ICON'S FIVE WERE PHYSICALLY OUT OF ORDER

Ordinals in the headings, read top-down, ran **3 · 1 · 2 · 5 · 4**:

| line | heading | timestamp |
|---|---|---|
| 19 | third renumbering, seat01, *"supersedes everything below"* | 2026-08-28T20:00Z |
| 42 | first block this file has had, seat01 | 2026-08-28 |
| 84 | second renumbering, seat06 | 2026-08-28T19:44Z |
| **115** | **fifth renumbering, seat08, *"supersedes everything below"*** | **2026-08-28T21:44Z ← the true current** |
| 136 | fourth renumbering, seat03, *"supersedes everything below"* | 2026-08-28T21:12Z |

**The top block's own superseding claim was false**: line 19 asserted it superseded everything below it, and was itself superseded by line 115, which sat below it. Three separate blocks each claimed *"supersedes everything below"* — a claim that cannot be true of more than one block in a file, and was true of none of them as ordered.

## MEASURED HARM — this is a LIVE rank-1 row, not a museum piece

`tests-consolidate-icon` is rank 1 and was **FREE in the picker** at measurement (locked by hq_B via `next` during this session). A seat following the printed instruction literally works line 19's block — seat01's 20:00Z priorities — and thereby:

- misses that **rung01, rung02 and rung05 were already converted** and pushed (corpus `76f48372`, `61147d59`, `c5f8e485`) after that block was written;
- misses that the **5 `KEEP.md` files** the gate needs to ever reach `GATE OK` were written and pushed (corpus `fb671d3d`);
- works a stale baseline — line 19 says `total: 452 converted: 6 loose: 446`, the true current says `total: 298 converted: 39 loose: 259`;
- misses seat08's ⛔ screening caution that `rung03` and `generators.icn` are genuine generator/coroutine content needing activation-frame screening first.

Four sessions (seat01, seat03, seat06, seat08) each appended a block and each honestly believed they had left one current instruction. **Nobody was careless; the file had no rule about where a new block goes.**

## CURE APPLIED (this session, hq_B)

`tests-consolidate-icon.task.md` rewritten: **CURRENT block first, then superseded history newest-first**, and only ONE heading matches `^## NEXT` — the other four are retitled `## SUPERSEDED-NEXT`. An HTML-comment signpost under the current heading states the ordering rule and how to append the next block.

**Control arm — byte-equal-or-refuse (this seat's own law, `GOAL-HQ-BEAUTIFY.md` § verdict).** Body content compared as a sorted multiset with all heading lines and the added signpost stripped from both sides:

```
old body lines: 163   new body lines: 163
old body md5: 4c4a95bf53ed042a88ee4a695ef0cb0d
new body md5: 4c4a95bf53ed042a88ee4a695ef0cb0d
✅ body content byte-identical, zero lines dropped or altered
```

Only the 5 heading lines changed; one signpost line added (168 → 169 lines). Pre-edit copy preserved outside the postoffice. Post-install verification: `grep -c '^## NEXT'` = **1**, and a top-down reader now lands on seat08's 21:44Z block.

## DELIBERATELY NOT CURED, AND WHY

- `tests-consolidate-prolog` (9 blocks) is **internally consistent** — newest-at-bottom, every heading says so. Verbose, not false. Reordering it would be churn on a row another seat may hold; the convention question below is the real fix.
- `conform-rtntype-not-tracked` and `build-governor-concurrent-pristine` each carry **two bare `## NEXT` headings with no disambiguation whatsoever** — structurally the worst shape, since nothing marks which is current, and `conform-rtntype`'s first block says "STEP 1/2/3: do the work" while its second says "Task complete, `done` closes this row." **Both rows are already in `QUEUE.done.tsv`**, so the picker can never serve them and the harm is theoretical. Left alone; noted here so a future sweep does not mistake them for live hazards.

## RECOMMENDATION (not taken unilaterally — the picker's printout is shared law)

One line in `PROTOCOL.md` and in `next`'s printout naming the direction would close the class: *the current block is the FIRST `^## NEXT`; demote the one you replace to `## SUPERSEDED-NEXT`.* That makes "the ONE `## NEXT` block" true by construction and mechanically checkable (`grep -c '^## NEXT' == 1`), rather than a convention each seat re-invents. A gate over `tasks/*.task.md` asserting exactly one `^## NEXT` per file would enforce it — cheap, and it fails loudly the first time a seat appends in the old style.

## ⭐ THE GENERALISABLE POINT

**An instruction that says "the ONE X" is a claim about the data, not just about the reader.** The picker has printed "the ONE `## NEXT` block" on every pick for as long as batons have existed, and nine files have never satisfied it. The printout was not wrong about what a seat *should* read — it was wrong that the corpus made that unambiguous, and being confidently phrased is exactly what stopped anyone checking. Same family as `RULES.md` § A CORRECT PROCEDURE WITH A FALSE EXPLANATION: the procedure ("read the current block") is right; the premise ("there is exactly one, and it is obvious which") was never measured.

## MODE NOTE (recorded because it bit during this very session)

`/home/resources/postoffice/MODE` was rewritten **mid-session**: it read `CEO` when this session started (verified twice) and `FLEET-8` less than an hour later on Lon's 2026-08-29 declaration *"We are running in mode FLEET-8 with 3 HQ's and CEO."* `s4e_msg.sh next` printed `MODE: FLEET-8` while a stale in-context reading still said `CEO`; the picker was correct and the remembered value was not. Concrete support for the standing rule that MODE is **computed at the moment of use, never carried** — a session-start reading of that file has a shelf life measured in minutes, not sessions.

---

## AMENDMENT (same day, hq_B) — THE FULL CENSUS, AND IT IS NOT ONLY THE DUPLICATES

The body above counted files with **more than one** `## NEXT`. Completing the census over all `tasks/*.task.md` found the larger half of the problem is the opposite shape — files with **none**:

| `^## NEXT` blocks | task files |
|---|---|
| **zero** | **45** |
| exactly one | 367 |
| more than one | 8 (was 9; `tests-consolidate-icon` cured above) |
| **total** | **420** |

**The picker's "read the ONE `## NEXT` block" is literally true for 87% of batons and false for 53 of them** — 45 that offer nothing to read and 8 that offer a choice. A seat hitting a zero-block file has no landing point at all and must reconstruct intent from GOAL + LEDGER; a seat hitting a multi-block file may read the wrong one.

**Live instance, same session:** `fuzz-nondeterminism-rootcause` — a rank-1 row reached by dependency inversion — had **zero** `## NEXT` despite carrying a detailed two-cluster investigation, ruled-out directions, and a copy-pasteable reproduction command. The content was excellent; there was simply no block where the tool said to look. Cured in place (one block added, all 69 original lines preserved in order, 46 inserted).

### This sharpens the recommended gate

The earlier recommendation — assert `grep -c '^## NEXT' == 1` per baton — is now measurable rather than speculative: **53 files fail it today.** That is small enough to fix and large enough to matter, and it is a one-line check. Two notes for whoever lands it:

- Run it as a **ratchet first, not a hard gate** (ceiling 53, must not grow), exactly as this project did for the `MEDIUM_*` census — a hard zero on day one blocks unrelated work, while a ratchet stops the bleed immediately and lets the 53 drain.
- **Count the token, not the shape.** `RULES.md`'s own `MEDIUM_*` history is the precedent: a ratchet assembled from the violations already seen is permanently one syntax behind the code. `grep -c '^## NEXT'` counts headings and would miss, say, a `# NEXT` or `## NEXT-CURRENT` variant — decide deliberately whether those count before pinning the number.

⭐ **And the deeper reading of 45-with-none:** a missing block is not laziness. `next` tells a seat to *"rewrite `## NEXT` before you stop"* — but a seat that releases a row **unworked** (out of lane, blocked, or refused on contact) has nothing to rewrite and correctly writes nothing. The convention has no spelling for *"I looked and handed it back"*, so the file stays blockless and the next seat re-derives the same scope from zero. That is the cheapest fix available here: a one-line released-unworked block costs the releasing seat nothing and saves the next one an orientation pass.
