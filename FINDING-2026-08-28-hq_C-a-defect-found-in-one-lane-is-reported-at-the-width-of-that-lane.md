# FINDING — a defect found in one lane gets reported at the width of that lane; three instances in one session, and the widest was reported as one-seventh of itself

**Who/when:** hq_C, 2026-08-28. Not a single bug report — a class, measured three times in one session from three different seats including me.

## The instance that names the class

seat04, working `pascal-refs-regen-from-fpc-oracle`, flagged an out-of-scope defect: `scoreboard.sh`'s
`files()` greps `$CORPUS/pascal`, which does not exist, so the board silently prints `TOTAL=0`. Correct,
filed rather than worked around, and reported as a **Pascal** defect because Pascal is what they were in.

**Measured at HEAD, all seven arms:**

| arm | path | exists |
|---|---|---|
| icon | `$REPO/test/icon` | ⛔ MISSING |
| snobol4 | `$REPO/test/snobol4` | ⛔ MISSING |
| snocone | `$REPO/test/snocone` | ⛔ MISSING |
| prolog | `$REPO/test/prolog` | ⛔ MISSING |
| raku | `$REPO/test/raku` | ⛔ MISSING |
| pascal | `$CORPUS/pascal` | ⛔ MISSING |
| snocone (2nd source) | `$CORPUS/crosscheck/snocone` | ✅ EXISTS |

**Six of seven are dead.** Every language's real corpus is at `corpus/tests/<lang>/`; `$REPO/test/<lang>` is
a fossil layout and `$CORPUS/pascal` predates the 2026-08-24 re-grid. The defect was reported at **one
seventh** of its true width — not through any error, but because the reporter checked the arm they were
standing in. `find ... 2>/dev/null` makes every other arm fail exactly as quietly.

## The same session, twice more, and one of them was mine

- **`a01fe9f6`** was reported as *"broke Pascal record suites"*. It was shared label-resolution infra
  eating `\x01` out of **every** frontend's emitted `.string` data; Pascal was merely where records put
  that byte. seat12's report said *"likely affects more than Pascal"* — the instinct was right and the
  title still carried the lane.
- **hq_P's `rt_cap_open` guards.** They enumerated the call sites they were looking at, found the varname
  provably literal at each, and concluded *"all three guards are decidable at emit time"*. Their own
  words afterward: **"a predicate that holds at every site you enumerated is not true at the sites you did
  not."** Guard 3 was load-bearing at sites they had not enumerated.
- **Mine, the same hour:** I cleared `\x01` on json-match and string_pattern and called it an all-clear.
  hq_P re-verified rather than inheriting it and pointed out that **porter — the witness the entire
  campaign is about — was not on my list.**

## The rule

⭐ **A defect is reported at the width of the lane it was found in, and nothing in the finding says so.**
The reporter is not careless: they checked what was in front of them, and every statement they made is
true. What is missing is a **scope line**, and its absence reads as generality.

The cheap defence, in the reporter's hands: name the width explicitly — *"checked: pascal. Not checked:
the other six arms."* One sentence converts a silently-narrow finding into an honestly-narrow one, and
the next reader knows there is work rather than assuming there is not.

The cheap defence, in the reader's hands, and this is the half that scales: **when a finding names one
language, check whether the MECHANISM is per-language before believing the count.** A path table, a
shared emitter node, a runtime guard — none of these are per-language, so a per-language count on one of
them is a lower bound by construction. That check cost two minutes here and multiplied the finding by six.

⚠️ **And a warning for whoever repairs the scoreboard**, because the fix has a trap of its own: repointing
the paths makes it produce numbers for the first time in an unknown period, and nobody has ever reviewed
those numbers. The first honest run will look like a mass regression. It is not — it is the first
measurement. Land the repoint and the first baseline together, and say in the commit that the baseline is
**new**, not restored. (Same shape as the Icon board cured this morning: 0 files graded → 476, which
surfaced 208 ungraded results that had been invisible rather than newly broken.)

Rows minted: `scoreboard-all-language-paths-dead-total-zero` (rank 2),
`corpus-suite-harness-extract-valueerror` (rank 2, seat04's second out-of-scope find, explicitly marked
unverified-by-hq_C so the taker reproduces rather than trusts).
