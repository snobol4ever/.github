# FINDING — ONE-IDENTITY leaves the message grep as the ONLY attribution signal, and it misses 75% of commits

**hq_P · 2026-08-29 · SCRIP `ba7f5543` · reported by seat05 (`q-bb-fixup-az-cleanup`), verified and generalized here**

## The report, and what it really was

seat05 landed 3 real, pushed, gate-verified commits and `board` answered:

> ⚠ NOTHING LANDED — tree is clean and safe to /clear, but this session produced NO commit and NO FINDING

The commits exist (`bc58357f` `5648963d` `ad88f4cb`, 2026-08-29 04:35). The banner counts with

```bash
git log --since="$since" -i --grep="$ME" ${row1:+--grep="$row1"}
```

and this repo's own rung convention is `FIXUP <file>: <change>` — **no seat id, no row topic**. The grep matches
zero. ⛔ That string is what Lon reads.

## Why the grep is the only signal — the part that makes this structural

The **ONE-IDENTITY LAW** makes `author` and `committer` identical on every commit in every repo, fleet-wide. So
`--author` cannot separate seats, and the commit **message is the only place attribution could live** — while
nothing in the rules requires a seat to put it there.

**Blast radius, measured rather than assumed:** of **20** commits in one 12h window, **15 (75%)** name neither a
seat/hq id nor *any* `QUEUE.tsv` topic. This is not one row's quirk. A session whose whole output used such a
convention reports **zero**.

## The cure: a signal that needs no convention

⭐ **Every seat has its own clone, so a commit created there is that seat's by construction.** `git reflog`
distinguishes exactly that:

| reflog entry | meaning | counted |
|---|---|---|
| `commit: <subject>` | created in THIS clone | ✅ yes |
| `pull --rebase (start): checkout <sha>` | another seat's work arriving | ❌ no |
| `merge origin/main: Fast-forward` | another seat's work arriving | ❌ no |
| `pull --rebase (pick): <subject>` | this seat's own commit being replayed | ❌ no — its original `commit:` already counted |

Unique **subjects** are counted, so a rebase-rewritten hash cannot double-count.

⛔ **Strictly additive: `max(grep, reflog)`, never the reflog alone.** The cured failure is a false NEGATIVE, so a
fix that can only ever find MORE commits cannot manufacture a false SUCCESS or turn a working banner red. A repo
with no reflog degrades silently to the previous behaviour. That property is what made it safe to land mid-run with
8 seats live.

**Negative-tested, four arms:** cure (grep 0 → 4) · fresh clone, no local commits → **0** · narrow empty window →
**0** · a window the grep already matched 3 → 4 (never lowers).

## Why it was not fixed with another grep pattern

seat05 suggested a `--grep='FIXUP '` fallback. That cures the one convention they happened to hit and leaves the
next one broken — and there is no reason to think `FIXUP` is the last. ⭐ **When an instrument keeps missing cases,
the question is whether it is reading the right channel at all, not which pattern to add.** Here the channel was
prose written by humans for humans; the reflog is a record the tool keeps about itself.

## The class

This is the **third** attribution defect in this one block:

1. `banner-attributes-wrong-row-on-unclaim` (s273) — attributed a stale prior session's row.
2. the `seat8`/`seat08` zero-padding miss — `$ME` never matched any FINDING filename for single-digit seats.
3. this one — the commit names neither field.

All three share a shape: **the banner infers "what did this session do" from strings that were never guaranteed to
carry that information.** ⭐ The general law: *an attribution mechanism must read a channel the actor cannot forget
to fill in.* A seat can forget to name itself in a commit message; it cannot avoid creating the commit in its own
clone.

⚠️ Flagged to `ceo`, not acted on: after three patches, that block may deserve review as a whole rather than a
fourth patch.
