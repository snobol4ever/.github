# FINDING — RETIRED TOOL, PRESERVED LESSON: three Icon-source-rewriting bugs found (and fixed) in
# the withdrawn procedure/brace-dialect converter, caught only by round-trip testing — one of the
# three structurally invisible to idempotence testing, not just missed by it.

**seat01 · 2026-09-04 · row `icon-dialect-procedure-braces-no-end-every-statement-and-declaration-
ends-in-a-semicolon`** (hq_B's row; seat01's slice was the converter, `util_icon_braces.py`). The
brace dialect itself was WITHDRAWN by Lon (2026-09-04 ~13:55, via ceo, verbatim: "You are correct
about the curly braces in Icon. So leave the procedure and end statements. Fix our parser to not
require a semi-colon after either procedure nor end statements. Go remove the semi-colons everywhere
in the corpus which are at the end of procedure or end statements.") and this row is RETIRED. The
converter never touched the live tree and was never wired into any build or corpus path. hq_B on
retiring the row: "your three bugs remain the most valuable thing produced today ... Write those up
where they survive the row being retired ... they are facts about transforming Icon source, not
facts about braces, and the next person who writes any Icon rewriter needs all three. A FINDING is
the right home." This is that writeup.

The converter (672 lines, never merged; salvaged at
`/home/resources/postoffice/salvage/seat01-icon-dialect-converter-util_icon_braces-2026-09-04.py`)
converted `procedure X(...) ... end` to `procedure X(...) { ... }`. It carried three self-checks:
idempotence (convert twice, assert zero further change on the second pass), round-trip (convert then
de-convert, diff against the true original), and banner-parity (banner lines byte-identical and
untouched). All three bugs below were caught by the round-trip check and none by eye; bug 3 could not
have been caught by idempotence at all, structurally, not merely as a matter of luck.

## Bug 1 — a per-line-reset paren-depth counter silently eats real code when a parameter list spans lines

`find_close_paren()` locates a procedure's closing `)` by scanning forward from the opening `(`,
tracking paren depth. The first version re-initialized `depth=0`/`seen_open=False` on every physical
line instead of threading that state across lines. For any procedure whose parameter list itself
spans multiple physical lines, the scan's depth counter could reach 0 on the WRONG close-paren —
some unrelated, later one inside the procedure body — the moment counting restarted fresh on a body
line. Everything between the true close and that wrongly-matched one was silently dropped from the
output.

Measured against the real corpus: 37 files hit this, including Arizona's `scan_lib.icn` (a
`while ... upto(...) ...` construct lost text this way before the fix).

Fix: thread `depth`, `seen_open`, and the in-string state as explicit loop-carried values across the
line-by-line scan, not re-derived per line.

**Why this is the dangerous class, not a cosmetic bug**: the buggy output still PARSES — shorter,
plausible Icon text, not a syntax error. A reviewer reading the diff sees a plausible conversion.
Nothing except a byte-for-byte round-trip against the true original catches text quietly going
missing at a distance from where the bug actually fires.

## Bug 2 — `\^X` is a 3-character escape unit in Icon string/cset literals, not 2

SCRIP's own lexer (`icon_lex.c`, `scan_string`/`scan_cset`) treats `\^X` — backslash, caret, and one
more character consumed unconditionally as the control-character target — as a single 3-character
escape unit. The converter's `escape_len()` originally used a generic "backslash + 1 more character"
(2-char) skip, correct for `\n`, `\"`, `\\`, etc. but wrong for `\^`. Undercounting by one character
leaves the character immediately after `^` — whatever it is — unconsumed and re-scanned as ordinary
syntax rather than as escape data.

Measured against the real corpus: `xtable.icn`'s ASCII-table string literal contains a `\^"`
control-quote escape. Under the 2-char rule, the converter's quote scanner read that embedded `"` as
the string's real closing quote, prematurely ending the literal — corrupting an unrelated LATER line,
nowhere near the escape itself.

Fix: `escape_len(s, i)` special-cases `s[i+1] == '^'` and returns 3; every other escape stays 2.

**Same class as bug 1**: silent corruption whose symptom lands somewhere other than the site of the
actual defect, in output that still parses.

## Bug 3 — the de-converter dropped a trailing comment on a procedure's closing line, and idempotence testing could not have found it by construction

`end # comment` round-tripped (new-dialect `}` back to old-dialect `end`) as bare `}` -> `end`, with
the comment silently gone.

This one isn't "corruption at a distance" like bugs 1-2 — it's a straightforwardly lossy spot in the
de-converter. What makes it worth naming on its own: **idempotence testing is structurally blind to
it, not just unlucky.** Idempotence here means `convert()`, applied twice, produces no further change
on the second pass — a check that only ever exercises `convert_text()`. Bug 3 lives entirely in
`deconvert_text()`, the separate inverse function; a convert-only idempotence harness never calls it
and cannot see it by construction, however thorough it is. Only round-trip testing (convert, then
deconvert, then diff against the true original) exercises the de-converter at all.

The broader lesson, in hq_B's words on accepting the report: idempotence proves `f(f(x)) == f(x)`,
which a transform that has already lost data can satisfy perfectly — it proves stability, not
losslessness. Round-trip is the bar that proves nothing was lost. **Keep both, named as separate
bars in the tool's own header, so the next person does not quietly settle for whichever one is
cheaper to write and call it sufficient.**

## Disposition

Not a live defect in SCRIP or in anything on `origin/main` — the converter never edited the working
tree and was never merged; the dialect it served was withdrawn the same day, before any corpus file
was converted under it. Nothing here needs curing. This FINDING exists solely so these three facts
about transforming Icon source text — not about braces — survive the row's retirement, for whoever
next writes an Icon source-to-source rewriter (hq_B's own semicolon-strip row now underway,
`icon-no-semicolon-after-procedure-header-corpus-stripped-everywhere`, is the immediate candidate,
though hq_B authored this report's acceptance and already knows it).

Full converter source (never merged, 672 lines) salvaged at
`/home/resources/postoffice/salvage/seat01-icon-dialect-converter-util_icon_braces-2026-09-04.py`.
Original report in full at postoffice message (hq_B's archive)
`1788546937745440954-seat01-converter-ready-with-3-real-bugs-found-and-fixed.msg`; hq_B's acceptance
at seat01's archive `1788547634478683984-hq_B-converter-accepted-three-bugs-are-the-deliverable.msg`.
