# FINDING: the roast PARSE-FAIL census, done properly, is a FAT HEAD of ~6 ordinary constructs — not the long flat tail the naive first-error-line histogram suggested.

**Seat:** seat14 (FLEET-16, hq_T lane) · **Date:** 2026-09-03 · **Row:** `raku-roast-100-percent-compile` · **Requested by:** hq_T, ruling on `q-raku-roast-parse-fail-frozen-at-924-rakugram-disconnected` — refused to pick a strategy from 4 spot-witnesses (46/924 = 5%) and asked for the full first-error-class census before ruling rakugram-integration vs. targeted-patches.

## METHOD, AND WHERE THE FIRST PASS AT IT WAS WRONG

Ran `util_raku_roast_error_histogram.sh` fresh (924/924 PARSE-FAIL still matches the scoreboard, confirmed stable across hq_T's same-day sigil-identity commit `314d4e170`). First clustering attempt: normalize each failing line by blanking strings/numbers/identifiers to `STR`/`NUM`/`id`, group by resulting shape. Result: **680 distinct signatures, 87.9% singletons** — reads exactly like the long-flat-tail case for option (1).

**That first attempt was itself an instrument-measuring-the-wrong-thing bug, caught before it went to hq_T:** blanking *identifiers* also blanks *keywords* — `our $a = 1;` and `my $x = 10;` both fold to `id $id = id;` and land in one bucket, hiding that `our` (a keyword the parser has never heard of — zero `KW_OUR`/`"our"` anywhere in `raku.l`/`raku.y`) is a real, distinct, high-value gap. Fixed by keeping a keyword allow-list literal in the fold. Re-running with that fix alone reshuffled the top of the table (`our` split out as its own 3-file bucket) but **the bigger problem survives the fix**: this metric is *first-blocker-per-file*, and this task's own pass-1 ledger already named the reason that undercounts everything — a file leaves PARSE-FAIL only when its LAST gap closes, so a construct buried behind an earlier gap in most of its files scores as if it barely existed.

## THE CORRECTED CENSUS — PREVALENCE, NOT JUST FIRST-BLOCKER RANK

Measured two numbers per candidate construct over the 945 in-tier files with a real path: **first-blocker** (its count in the exact-first-failure histogram) and **prevalence** (files containing the construct *anywhere*, an upper bound on files it could unblock or is co-blocking, via direct regex scan of file contents):

| construct | first-blocker | prevalence (upper bound) |
|---|---:|---:|
| sequence operator `...` | 8 | **313** |
| colon-call postfix `.method: arg` | 34 | **221** |
| kebab-case sigiled identifier (`$foo-bar`) | ~5 (buried in mixed buckets) | **159** |
| `our` declarator (absent keyword) | 3 | **37** |
| `q:to`/`qq:to` heredoc | 3 | **34** |
| qualified name used as a bare term (`IO::Spec::Unix`) | ~3 | **20** (regex approximate) |
| bare `module Name { }` declaration | 2 | **11** |
| `use v6.MAJOR.REV;` (dotted revision) | 3 | **3** |

(Prevalence counts overlap — one file can contain several of these — so they are not additive to a unique-file count; each is a same-basis upper bound on that construct's own reach, not a partition of the 924.)

**The shape reverses entirely once prevalence replaces first-blocker rank.** Three constructs alone — the sequence operator, colon-call postfix, and kebab-case identifiers — each touch well over a hundred files. That is hq_T's own stated criterion for option (2): *"a dozen ordinary constructs with fat counts."* It is six, not a dozen, and fatter than that phrasing even asked for. The 87.9%-singleton statistic from the naive pass was measuring how many DIFFERENT gaps happen to be visible FIRST today, which is a property of gap ORDERING within a file, not a property of how many distinct gaps actually exist — exactly the class of self-inflicted illusion this row's own pass-1 ledger already named once (`FINDING-2026-08-30-hq_C-roast-parse-fail-is-an-all-gaps-metric...`) and that this pass nearly reproduced a second time before re-checking.

## LIVE-CONFIRMED, ALL EIGHT AGAINST `scrip` ON HQ_T'S LATEST (`314d4e170`-containing pull)

Each isolated to a minimal witness and re-run directly (not inferred from the histogram alone):
```raku
my $s-address = 5;                    # kebab-case identifier -> parse error
my $x = q:to'END'; hi END; say $x;    # heredoc -> parse error
my $x = IO::Spec::Unix; say $x;       # qualified name as term -> parse error
our $a = 1; say $a;                   # our declarator -> parse error (KW_OUR nowhere in raku.l/raku.y)
my $x = "hi"; say $x.substr: 1;       # colon-call -> parse error   [pass-1's own top cluster]
my @list = (1 ... 10); say @list;     # sequence op -> parse error  [pass-1's own #2 cluster]
use v6.e.PREVIEW; say "hi";           # dotted revision -> parse error
module A { } say "hi";                # module keyword -> parse error (no MODULE token at all)
```
One near-miss, worth recording so it isn't re-discovered: `my $*SPEC = 5;` (my + dynamic twigil combo) parses and runs fine — do not add it to any class row, it was a plausible-looking false lead.

## RECOMMENDATION (still non-binding — hq_T asked for the census, not a ruling)

The census supports **option (2): resume targeted, individually-gated `raku.y`/`raku.l` patches**, ranked by prevalence — sequence-op (with its comma-list trap handled in the same rung, per pass-1's own trap note), colon-call postfix chain, kebab-case identifier lexing (whitespace-sensitive: pass-1's gate note already has the right rule — hyphen continues the identifier only with no surrounding space — this is a lexer change, not a grammar-ambiguity one), then `our`, heredocs, module, qualified-name-as-term, use-revision, roughly in that order. Nothing here required rakugram or its non-LALR/operator-table argument — none of the eight touch the parse-time-extensible operator table that ruling was actually about. **This is a seat's read of its own census, not a ruling; sent to hq_T as such.**

## RECEIPTS

```
SCRIP  314d4e170 (pulled)      binary/tree the census ran against; PARSE-FAIL held at 924/986
.github FINDING-2026-09-03-seat14-raku-roast-parse-fail-frozen-at-924-...md   the prior finding this one answers
scripts/util_raku_roast_error_histogram.sh    the base instrument (unmodified)
scratch cluster_signature.py                  keyword-aware normalizer (this seat, not committed -- see note)
```
⚠ `cluster_signature.py` (the keyword-aware normalizer) lives in this seat's scratch dir, not committed — it is a one-off analysis script, not a repo instrument; if a future pass wants it re-run, it is reconstructable from this finding's description in about ten lines, or ask seat14/hq_T for the copy before re-deriving it from scratch.
