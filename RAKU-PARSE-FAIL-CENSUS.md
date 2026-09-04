# RAKU-PARSE-FAIL-CENSUS.md — first-blocker rank vs. PREVALENCE, by class

**Row:** `raku-roast-parse-fail-census-by-class` (seat13, hq_T lane, FLEET-16) · split off
`raku-roast-100-percent-compile` under a Lon floundering ruling: the ceo cures `raku.y`/`raku.l`,
this row owns the CENSUS and the WITNESSES. **`src/parsers/raku` is single-writer (the ceo) and
was not touched to produce this file.**

## HEADLINE: first-blocker rank and prevalence disagree, sharply, per class

A roast `.t` file reports only the ONE gap that stops its parse FIRST. A construct buried behind
an earlier gap in most of its files scores as if it barely existed, even when fixing it would
still be required for those files eventually. **Prevalence — files containing the construct
ANYWHERE in their source, measured directly against file content rather than the recorded first
error — is the complementary number**, and the two disagree by an order of magnitude on the
single clearest case:

| class | first-blocker (ceo cluster, below) | prevalence (this census) |
|---|---:|---:|
| sequence operator `...` | **37** | **311** |

Curing the sequence operator moves only 37 files' *first* blocker, but sits somewhere in the
source of 311 — 8.4x more. A cure ranked by first-blocker rank alone would under-prioritize it
by roughly that factor. This is the same effect seat14's pass-11 census (FLEET-16,
`FINDING-2026-09-03-seat14-raku-roast-census-fat-head-not-long-tail-once-first-blocker-counts-are-corrected-for-prevalence.md`)
first documented, and the same effect the `kebab-case` and `module` rows below now show
LANDED and moving the flat board by zero, exactly as that finding predicted a landed
non-first-blocker construct would.

## METHODOLOGY

- **Population:** the 924 PARSE-FAIL roast files recorded in
  `.github/probes/raku-roast-parse-fail-census-2026-09-04.tsv` (in-tier 945, parse-fail 924,
  parse-ok 21, missing 41; scoreboard exclusions S01/S15/S17/S22/S24/S26 applied upstream by
  `scripts/raku_roast_scoreboard.sh`). That TSV was measured at SCRIP commit `59589ee97`;
  `git log 59589ee97..HEAD -- src/parsers/raku src/lower` is empty, so nothing raku-relevant
  moved between that measurement and this one and the 924-file population is trusted as-is
  rather than re-run.
- **First-blocker column:** the ceo's independently-built 24-feature regex ladder over the same
  TSV's recorded first-error source lines, logged in
  `raku-roast-100-percent-compile.task.md` LEDGER, `[ceo·2026-09-04 16:52 CDT]`. Cited, not
  recomputed, and only shown where a ceo bucket maps onto one of this census's classes —
  several classes below have no first-blocker analog because nothing in the ladder isolates
  them (noted per row).
- **Prevalence column (this census, fresh):** for each of the 924 files, a direct regex scan of
  the FULL roast source (not just the recorded first-error line), counting files where the
  pattern occurs anywhere. Measured against clean current `HEAD` (`2cd69baa3`) via an isolated
  `git worktree` — **not** the live working checkout, because `src/parsers/raku` there currently
  carries an uncommitted, un-pushed lexer change (a `VERSION_LIT` rule for `v1.2.3`-style version
  literals) that is this row's single-writer lane and was left untouched rather than stashed.
  `refs/roast` and `refs/rakudo-main` (gitignored symlinks to `/home/resources/roast-master` and
  `/home/resources/rakudo-main`) were recreated in the worktree; `scrip` was built there with
  plain `make` (`RT_OPT` unchanged, no `-O2`).
- **Landed-vs-open status:** verified live, not inferred — each witness below was run through the
  worktree's `scrip --dump-ast` and its real rc recorded.
- **Excluded:** the 13-file `{; $_.key ...}` topic-variable/`.map` cluster. It already PARSES; its
  failure is a post-parse NO-TAP rejection, not PARSE-FAIL, and is not a member of the 924-file
  population this census scans.
- **Overlap:** prevalence counts are not additive to a unique-file total — one file commonly
  contains several of these constructs (e.g. a roast preamble with both `use v6.e.PREVIEW;` and a
  later `...` stub). Each count is a same-basis upper bound on that one construct's own reach.

## CLASSES, ORDERED BY PREVALENCE

| class | first-blocker | prevalence | status | witness |
|---|---:|---:|---|---|
| seq-op | 37 (ceo: `...`) | **311** | OPEN | `corpus/tests/raku/parse_census/seq_op.raku` |
| qualified-term | 46 (ceo: `` `::` package names ``, narrower — see caveat) | **478** | OPEN | `corpus/tests/raku/parse_census/qualified_term.raku` |
| colon-call | 11 (ceo: "colon method args", narrowest reading — see caveat) | **217** | OPEN | `corpus/tests/raku/parse_census/colon_call.raku` |
| kebab-ident | 0 (no bucket — no longer anyone's first blocker) | **150** (residual, non-causal) | **LANDED** `aef59ae38` | `corpus/tests/raku/parse_census/kebab_ident.raku` |
| bare-module | 0 (no bucket — no longer anyone's first blocker) | **16** (residual, non-causal) | **LANDED** `2db0e0421` | `corpus/tests/raku/parse_census/bare_module.raku` |
| our-decl | not broken out separately (likely folded into ceo's "my-decl" 103) | **35** | OPEN | `corpus/tests/raku/parse_census/our_decl.raku` |
| qto-heredoc | not broken out separately (likely folded into ceo's "other" 65) | **33** | OPEN | `corpus/tests/raku/parse_census/qto_heredoc.raku` |
| use-revision | not broken out separately (likely folded into ceo's "other" 65) | **3** | OPEN | `corpus/tests/raku/parse_census/use_revision.raku` |

### Per-class notes

- **seq-op** — the sequence/stub operator `...`, e.g. `my @list = (1 ... 10);`. Regex:
  `(?<!\.)\.\.\.(?!\.)`, i.e. exactly three dots. Re-measured fresh; lands within 1% of seat14's
  pass-11 number (313), i.e. stable across the intervening day of unrelated landings.
- **qualified-term** — a `Foo::Bar`-shaped capitalized, `::`-qualified identifier occurring
  anywhere in the file. ⚠ **Broader than seat14's pass-11 "qualified name used as a bare term"
  (20, their own "regex approximate")** and broader than the ceo's "`::` package names" ladder
  bucket (46, first-blocker only). This scan tried excluding declaration-keyword contexts
  (`use`/`unit`/`module`/`package`/`class`/`role`/`grammar`/`does`/`is`/`isa`/`need`/`require`
  immediately before the name) and still landed at 478 — roast files are heavy with `::`-qualified
  names in comments, POD, and test descriptions that a bare-term-only reading would exclude but
  this regex does not. Reported as-is rather than tuned further to match a prior number: it is an
  honest measurement of a broader, explicitly-stated question ("does a `::`-name occur in this
  file at all"), not a drop-in replacement for the narrower one.
- **colon-call** — a postfix method call with a colon argument list instead of parens, e.g.
  `$x.substr: 1`. Regex: `\.[A-Za-z_][A-Za-z0-9_-]*:(?!:)\s*[^\s:=]`. The ceo's ladder is
  first-match and splits related colon-syntax three ways — "colon method args" (11, the
  narrowest/closest analog), "adverb/pair `:name`" (54), and the single repeated preamble line
  `use lib $*PROGRAM.parent(2).add: '…'` (34, itself a colon-call) — so this census's 217 sits
  on top of all three without claiming a clean one-to-one mapping; the table cites only the
  narrowest (11) to avoid overstating the reversal.
- **kebab-ident** — a sigiled identifier with an internal hyphen, e.g. `$s-address`. Landed at
  `aef59ae38` (lexes as one token now, no surrounding whitespace). Witness confirmed live:
  `scrip --dump-ast` on `kebab_ident.raku` now exits 0 and prints a normal AST. The 150-file
  prevalence is what remains in the *current* 924-file PARSE-FAIL population — i.e. files that
  still fail to parse for some *other* reason and merely also happen to contain a kebab-case
  identifier. This is the row's own worked example of "a landed class moves the board by zero":
  landing this construct is real and verified, and did not, by itself, remove any of these 150
  files from PARSE-FAIL.
- **bare-module** — `module Name { }` with no `end`. Landed at `2db0e0421`. Witness confirmed
  live: `scrip --dump-ast` on `bare_module.raku` exits 0 (`TT_MODULE_DECL`). Same reading as
  kebab-ident: 16 files still contain the construct and are still PARSE-FAIL for other reasons.
- **our-decl** — `our $a = 1;`. `KW_OUR` does not exist in `raku.l`/`raku.y` as of this census;
  witness confirmed rc=1 live.
- **qto-heredoc** — `q:to'END' ... END`. Witness confirmed rc=1 live.
- **use-revision** — `use v6.e.PREVIEW;` / `use v6.MAJOR.REV;` (dotted revision after `v6`).
  Smallest class measured; witness confirmed rc=1 live.

## WITNESSES

All eight live at `corpus/tests/raku/parse_census/*.raku`, one file per class, run with
`scrip --dump-ast <file>` (parse-only, matching this census's own methodology). Each is the
smallest program that isolates its one construct — most are adapted directly from seat14's
pass-11 finding, re-verified against current `HEAD` rather than re-quoted:

| file | rc (verified live, this census) |
|---|---:|
| `seq_op.raku` | 1 (OPEN) |
| `qualified_term.raku` | 1 (OPEN) |
| `colon_call.raku` | 1 (OPEN) |
| `kebab_ident.raku` | 0 (LANDED) |
| `bare_module.raku` | 0 (LANDED) |
| `our_decl.raku` | 1 (OPEN) |
| `qto_heredoc.raku` | 1 (OPEN) |
| `use_revision.raku` | 1 (OPEN) |

These are new, additive fixtures under `corpus/tests/raku/parse_census/` — a directory of their
own, separate from the gated `parser/` (oracle-parity) and `parser-coverage/` (Grammar.nqp arm
coverage) suites, so as not to perturb either suite's existing roster or counts. They are not
wired into any gate; they exist to make this census's claims re-runnable.

## RECOMMENDATION (non-binding — this row owns the census, not the cure)

Prevalence-ranked cure order: seq-op, qualified-term, colon-call, our-decl, qto-heredoc,
use-revision — consistent with seat14's pass-11 read and unchanged by a day of intervening
landings. kebab-ident and bare-module are already cured; their nonzero, unchanged PARSE-FAIL
membership is expected and is not evidence against either landing.
