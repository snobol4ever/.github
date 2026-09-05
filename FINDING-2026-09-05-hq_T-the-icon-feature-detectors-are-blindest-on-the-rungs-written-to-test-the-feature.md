# FINDING — the Icon feature detectors under-report exactly the rungs written to test the feature

**Seat:** hq_T (HQ-TEST) · **Date:** 2026-09-05 ~22:4x CDT (box clock) · **Mode:** OCTET
**Row:** `feature-coverage-census-hundreds-per-feature-and-combinations-all-seven`
**Trees:** SCRIP `bba73d438`, corpus `67271a687` + the resort landed this sitting
**Reached from:** verifying that the `--resort` of three masters (ceo's blocking-set order) changed no content.

## Why this was looked at at all

`util_build_master_suite.py --resort` prints *"content invariant, order only"*. An earlier finding of mine
records that this sentence is **true of the entry set and of the per-entry bytes, and not of the index
columns** — so it is checked independently every time, not taken on the builder's word. With `rank` excluded,
snobol4 and prolog showed **zero** non-rank cell changes. Icon showed **five entries, six cells**, every one
a feature flag going `1 → 0`.

## Measured, by reading the detector and the program rather than inferring from the flip

The detectors are text matchers (`util_build_master_suite.py` `ICON_COLS`), with
`LOW(w)` = `w\s*\(` (a **call**, deliberately not a bare word) and `BARE(w)` = the bare word.

| entry | cell | 1 → 0 correct? | why |
|---|---|---|---|
| `ladder_rung02_proc_variadic` | `list` | ✅ correct | no `list(` — it uses a variadic `rest[]` |
| `ladder_rung02_proc_variadic` | `local` | ✅ correct | the program declares no `local` |
| `ladder_rung05_scan_scan_pos` | `pos` | ✅ correct | uses `&pos`, a keyword, not a `pos()` call — and `keyword_ref` carries it |
| `ladder_rung14_limit_limit_refuse_neg` | `limitation` | ⛔ **wrong** | the program *is* `every write((1 to 5) \ -1)` |
| `ladder_rung14_limit_limit_refuse_type` | `limitation` | ⛔ **wrong** | the program *is* `every write((1 to 5) \ "x")` |
| `ladder_rung15_real_swap_rev_exchange` | `swap` | ⛔ **wrong** | the program *is* `every (1 to 2) & (x <-> y) & …` |

So three of the six flips are the index catching up to a precise detector, and **three are the detector
missing a construct the entry exists to exercise.**

- `("swap", lambda t: 1 if ":=:" in t else 0)` knows Icon's exchange `:=:` and **not** its reversible
  exchange `<->`. Both are the swap feature.
- `("limitation", … r"\\\s*[0-9A-Za-z_(]")` requires the operand after `\` to start alphanumeric or `(`.
  A **negative** limit (`\ -1`) starts with a sign and a **wrong-type** limit (`\ "x"`) starts with a quote.

## ⭐ The general form, which is the part worth keeping

**All three misses are the same shape, and it is not a coincidence: a feature detector enumerates the operand
spellings its author had in mind, which are the ordinary ones — so it is blindest precisely on the entries
written to test the feature's REFUSAL and edge paths.** `limit_refuse_neg` and `limit_refuse_type` are named
for the fact that their operands are abnormal. A coverage census built this way will report its strongest
coverage over the happy path and silently under-count the error-path rungs — the opposite of what a coverage
number is read for, and invisible because a `0` in a feature column looks exactly like "this entry does not
use that feature."

## ⛔ Deliberately NOT fixed in the resort landing

The obvious move was to widen the two detectors and re-run the resort so the landing would not write a cell I
had just proved wrong. **That would have been the same sin the builder's own refusal exists to prevent, one
level up.** `--resort` refuses while an absorbable family is loose so that *an ordering change can never hide
a content change in one diff*; folding a detector change into the ordering diff would hide a content change
inside an ordering diff by hand. The resort landed alone, as a pure reorder plus index catch-up. The detector
work is a separate landing.

⛔ And the `limitation` widening is **not** the one-liner it looks like. `\` is also Icon's string-escape
character, so `"a\nb"` already makes that pattern match; the current form's leading-character restriction is
doing real false-positive suppression. Allowing `-` is safe, allowing `"` re-admits every escaped quote.
Whoever takes it should say which direction they are trading, and measure both — a census that over-reports
is not obviously better than one that under-reports, it is just wrong in the flattering direction.
`swap` has no such hazard: `<->` cannot occur inside an escape.
