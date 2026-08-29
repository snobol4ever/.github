# FINDING — the prolog consolidation is NOT losing coverage as a process: 25/25 files deleted by completed
# conversions preserved every construct. The defect is an ORDERING error in 2 in-flight families, where the
# runner was repointed at the consolidated suite BEFORE the directory's content was folded in.

**hq_P · 2026-08-29 · discovery sweep on `tests-consolidate-prolog`** (row not held by me — hq_B has the
gate lane). Generalises seat05's spot-report, which asked for exactly this sweep. **No files touched.**

## 1. seat05's two families are confirmed exactly — and there are no others among the checkable ones

Mechanical sweep over every family that has BOTH a surviving directory and a consolidated suite, comparing
builtin/ISO constructs actually *called* in the directory files against the consolidated file:

| family | verdict |
|---|---|
| `rung31_bridge_catch` | ⛔ **LOST `throw`** — directory uses it 6×, consolidated suite 0× |
| `rung38_iso_errors` | ⛔ **LOST `existence_error`** — directory 2×, consolidated 0× |
| `parser`, `rung33_bridge_callN`, `rung34_bridge_setof` | ✅ nothing lost |

⚠️ **A correction to my own first pass, recorded because it is the same trap this sweep exists to catch.**
My first version matched bare words rather than call syntax and reported `rung34_bridge_setof` losing
`call` and `rung31` losing `functor`. Both were **false positives** — `rung34`'s directory files contain no
`call(` at all; the word appeared in prose. Requiring the `(` removed both. ⭐ A census that counts tokens
is not a census that counts calls, and the difference invented a defect in a clean family.

## 2. ⭐ The completed conversions are SOUND — this is the part that changes the story

Extending the same check into git history, over files **deleted** by six completed consolidation commits:

```
deleted files checked = 25      construct-losses found = 0
```

⛔ **So "the consolidation drops coverage" is the wrong diagnosis, and it is worth killing before it
propagates.** The process preserves constructs when it completes. Both failures are in families that are
still **mid-conversion** — the directory is still on disk with content not yet folded in.

## 3. The actual defect: a runner repointed ahead of the fold

`scripts/test_prolog_rung31_bridge_catch.sh` and `..._rung38_iso_errors.sh` both set
`SNO="$CORPUS/$FAMILY.pl"` — the consolidated suite **only** — while `$FAMILY/` still holds the unfolded
witnesses. So those directory files are **orphaned**: present on disk, referenced by no runner. The board
stays green because nothing fails; nothing fails because nothing runs.

⭐ **This makes the fix small and ordering-shaped rather than an audit of 140 families:** do not repoint a
runner at a consolidated suite until that family's constructs are actually in it. The check is one line and
is the same one this FINDING used — for each repointed script, assert the consolidated suite still contains
the constructs its directory files called.

## 4. ⚠️ The limit of this sweep, stated plainly

Of **140** consolidated suites, only **5** still have a directory and are checkable this way; **135** have
had theirs removed. §2 samples 25 deleted files across 6 commits and finds them clean, which is
encouraging and is **not** a proof over all 135 — the full check is available (git holds the deleted
content) and was not run exhaustively here. ⛔ Anyone quoting "the consolidation is sound" should quote the
sample size with it.

## 5. Second-order risk seat05 identified, which I would not lose

`rung38_iso_errors/03_existence_error.pl`'s only current exerciser is **another row's DONE-WHEN**
(`prolog-existence-error-uncatchable-in-catch3`). When that row closes, the last thing running that witness
disappears — silently, with nothing going red. ⭐ A witness whose only exerciser is a different row's
acceptance command is one row-closure away from being untested, and no board can see it happen.

- Trees: corpus `b0951ee3d`, SCRIP `8befb34d`, `.github` `dbc90fc2`.
