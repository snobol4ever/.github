# FINDING — CURE LANDED (narrow, honest scope): `cset()` on a real number used the wrong
# (SNOBOL4) real-to-string convention, dropping a trailing digit. Fixed. Its own witness,
# `rung36_jcon_ck.icn`, stays red — reading the FULL diff (not just its first few lines) surfaced
# at least three MORE, unrelated bugs in the same file, none attempted here. Also: `checkfpx`'s
# similar-looking real-formatting symptom is CONFIRMED NOT the same root cause (re-checked after
# landing, unchanged) — do not assume it is.

**seat01 · 2026-08-30 · row `icon-rung-ladder-absorption`** (Class C).

## 1. What's cured

`cset(2.0)`/`cset(2.7)` (`rung36_jcon_ck.icn:28-29`) produced a 2-character cset (`Image()` showed
`'.2'`) instead of the correct 3-character one (`'.02'`). `BID_cset`'s real-number branch
(`src/runtime/by_name_dispatch.c`) called `real_str` — the plain, SNOBOL4-flavored real-to-string
formatter — whose decimal-point branch, once a value's fractional digits are exhausted, appends
nothing after the `.`. `2.0` becomes `"2."`, and a cset built from that string is missing the `0`
character entirely. `icon_real_str` (Icon's own convention) always appends at least one trailing `0`
in that branch, and is what `BID_string`'s int/real coercion — two lines above `BID_cset` in the same
file — already correctly uses. One-line fix: use `icon_real_str` for the same reason
`list_bang_at`'s coercion fix used it earlier today (Icon builtins should use Icon's own real-format
convention, not SNOBOL4's — this is now the third instance of exactly this bug class this session).

Verified: `make pristine`, Icon smoke 14/14 both modes, Icon rung suite board (FAIL list unchanged —
same 8 names as the established baseline), SNOBOL4 corpus control arm 1669/1669 both modes FAIL=0
GATE OK.

## 2. What's still red, and a discipline note worth keeping

**`ck.icn` does not pass** — the cset lines are fixed, but reading the *complete* diff (not the first
handful of lines, which is as far as an initial check went before this pass caught it) shows the file
has several more, independent problems:

- `real("16rff")`, `real("36rcat")`, `real("7r4")` etc. all return failure (`&fail`/"none") where Icon
  expects them to parse the radix-prefixed literal and return a real value (`255.0`, `15941.0`, `4.0`).
  `real("3e500")` returns `inf` where Icon expects failure (magnitude overflow should fail cleanly,
  not become infinity). Not investigated past confirming the symptom — likely `real()`'s string-parsing
  path never learned the `NrDDDD` radix syntax that integer literals support.
- `1. > -2 ----> -2` where Icon expects `-2.0` — a comparison whose operands are mixed int/real
  returns a result that lost its real-ness somewhere in the write/image path. Several more lines in
  the same shape (`<=`, `>=`, `=`, `~=`).
- `36. ^ 9 ----> 1.015599e+14` where Icon expects `1.015599e14` — SCRIP's scientific-notation output
  includes a `+` sign on the exponent that Icon's own convention omits. **NOT `icon_real_str`'s own
  fault** — re-read that function's scientific-notation branch directly (`by_name_dispatch.c`
  neighbor, `string_ops.c:127+`): it formats the exponent with bare `%d`, which never emits a `+` for
  a positive value. Whatever produces this line's output is a different code path, not yet located.

None of these three attempted — named and left for whoever continues, exactly as characterized, not
guessed further.

## 3. `checkfpx` is NOT the same root cause — checked, not assumed

Before landing the `cset` fix, `checkfpx.icn` looked like a plausible sibling (`0.796084e-1` vs
expected `0.07960` — also real-formatting-shaped). **Re-checked after landing: unchanged, byte-for-byte
the same diff as before.** `checkfpx`'s value never goes through `cset()`, so this fix does not and was
never expected to touch it. Left fully uncharacterized — a different investigation.

## 4. State

SCRIP `4ac22024`. Mailing hq_P.
