# FINDING 2026-09-13 hq_T — two grammar entries were GREEN against refs cut from our own output, and the oracle says both were wrong

**Tree:** SCRIP 39cc0e78e+ · corpus f16d15a68+ · RT_OPT=-O0 · incremental `make` · oracle rakudo-local 2026.05
(`/home/resources/rakudo-local/bin/raku`, reached through `scripts/raku_oracle_run.sh`).
**Row:** `raku-match-gist-renders-corner-brackets-and-a-failed-match-is-nil` (rank 0, 25 entries).

## What happened

The row was minted against 25 xfail entries. Curing them required changing how `Grammar.parse()` matches and
renders. Before landing I graded **every** entry in the raku master that uses `.parse(` — 44 of them, not just
the row's 25 — precisely to see what the change would move. Two entries that were **green at baseline went red**:
`token_1` and `token_regex_1`.

They were not regressions. Both refs had been **cut from our own output**, and the oracle disagrees with both:

| entry | ref on disk (self-pin) | rakudo 2026.05 |
|---|---|---|
| `token_1` | `foo bar` | `｢foo bar｣` / ` a => ｢foo｣` / ` b => ｢bar｣` / `Nil` |
| `token_regex_1` | `foo bar` / `foobar` / `foo   bar` | `｢foo bar｣`+2 captures / `Nil` / `｢foo   bar｣`+2 captures / `Nil` |

`token_regex_1` is the sharper of the two: its ref asserts that `rule TOP { <a> <b> }` **matches** `"foobar"`.
Real Raku returns `Nil` there, because `rule` implies `:sigspace` and the inserted `<.ws>` is `<!ww> \s*`, which
must FAIL between two word characters. So the entry pinned the exact behaviour the language forbids — and the
suite had been reporting it green for as long as the ref existed.

Both entries' own comments say what happened, in writing: `token_1` carries *"No Match tree yet, so `<.name>`
expands like `<name>`"* and `token_regex_1` carries *"Match -> matched text; no match -> Nil (empty)"*. Those are
descriptions of **our implementation at the time the ref was cut**, written into the test as if they were the
specification.

A third, `token_say_1`, was red for an unrelated reason of the same family: rakudo **refuses to compile it**
(`Strange text after block (missing semicolon or comma?)` — a `token` block and a `rule` block joined on one
line), so its ref had been captured from a compile error and asserted that the program prints nothing. This is
the *same* faulty-test class already recorded in
`FINDING-2026-09-13-hq_T-two-thirds-of-the-raku-xfails-were-never-defects-and-the-refs-that-hid-it-were-cut-from-a-compile-error.md`,
which is why it is named here rather than filed again: **that class was not exhausted when it was closed.**

## Why the existing instruments could not find it

- The master suite runner: green. It compares our output to the ref, and the ref was our output.
- `util_raku_entry_grade.sh`: green. Same reason. A stricter grader on the same ref is still blind.
- The xfail census: silent. Both entries were **unmarked** — they were not suspected of anything.

⭐ Nothing that reads our output against a stored ref can detect this, no matter how strict, because the defect
is in the ref's **provenance**, not in the comparison. The only instrument that finds it is running the oracle.
This is CLAUDE.md's SELF-PIN vs ORACLE-DIFF split (`⛔⭐ A MASTER REF CUT FROM OUR OWN OUTPUT IS A SELF-PIN, NOT AN
ORACLE`) recurring, and the measured witness there was the same shape: a JCON-only program sitting inside the
Icon master's graded denominator because its ref came from us.

## The general form, which is the part worth keeping

⭐⭐ **A green cell tells you the instrument agreed with itself. Only the provenance of the ref tells you it agreed
with anything else.** And the corollary that actually changes behaviour:

⭐⭐ **When a cure moves a behaviour, grade the whole population that behaviour touches — not the row's own
entries.** The row named 25 entries and its DONE-WHEN graded exactly those 25; had I graded only them, both false
greens would have flipped to red silently in a later sitting and read as *my* regression, with the real defect
(a ref pinned to a compile error and a ref pinned to forbidden behaviour) two sessions upstream of whoever found
it. The 44-entry sweep cost one extra command and is the only reason these were found at their cause.

⚠️ Against me, and the reason this is worth writing down twice: **I nearly filed the two as regressions.** They
appeared in the sweep as `token_1 RED` / `token_regex_1 RED` immediately after my own change to the matcher, which
is exactly what a regression looks like. What separated them was running the oracle on both *before* concluding —
the same discipline that the row's own GOAL demanded and that I had already applied to the row's 25.

## What landed

- `<.ws>` is now a real assertion: `<!ww>` (fails between two word characters) plus a **ratcheted** whitespace
  run. `ws` is a `token` in Raku and tokens do not backtrack — without the ratchet, `rule TOP { <digit> <space>
  <digit> }` wrongly matches `"1 2"` by handing the consumed space back to `<space>`. `say_48` is the witness.
- `:sigspace` inserts `<.ws>` **between** atoms only, never before the first atom of a body or of an alternation
  arm. `say_replace_6` (`rule TOP { <space> }` against `" "`) is the witness: emitting it there ate the very
  space `<space>` had to match, and that entry was green before and after but red in between.
- Named captures flow from subrules and character classes into the Match, in match order and repeating under a
  quantifier (`say_46`, `<alpha>+` over `"abc"`, wants three capture lines).
- A Match is a Raku-own record: `say` renders Rakudo's HALFWIDTH `｢｣` (U+FF62/U+FF63 — **not** the fullwidth
  U+300C pair, the misreading that made an earlier census report this class as 7 entries when it is 25), string
  context renders the bare matched text, and a failed parse renders `Nil` and tests false.
- The three refs above are re-cut **from the oracle**, and `token_say_1`'s source is repaired to the form rakudo
  accepts.

**Measured after:** all 44 `.parse` entries of the raku master PASS both modes (`util_raku_entry_grade.sh`,
graded=44 green=44 red=0). Raku xfail population 107 → 81 of 1034.

## A second thing this cost, named because it is mine

Rewriting the three refs, I wrote `open(p,'w').write(unmark(open(p).read()))` and **truncated `ALL.raku` to
zero** — Python evaluates the truncating `open(..., 'w')` before the read. The file was restored from origin and
the edit redone with separate read and write statements; nothing was pushed in between, and `ALL.ref`/`ALL.csv`
were written by separate statements and were never at risk. ⭐ The reusable half: **a read-modify-write of one
file in a single expression is a truncation, not an edit** — and it fails silently, leaving a well-formed empty
file rather than an error.
