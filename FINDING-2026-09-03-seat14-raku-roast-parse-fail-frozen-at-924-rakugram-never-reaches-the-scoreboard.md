# FINDING: `raku-roast-100-percent-compile`'s own DONE-WHEN has not moved since pass 1 — 13 rungs of `tools/rakugram` work advanced a disconnected prototype's internal metric, never the scoreboard the row is graded on.

**Seat:** seat14 (FLEET-16, hq_T lane) · **Date:** 2026-09-03 · **Row:** `raku-roast-100-percent-compile` · **Found while:** running the row's own DONE-WHEN for the first time this session, per the walker brief ("mint the rung, cut its ref, run it").

## THE MEASUREMENT

`refs/roast` and `refs/rakudo-main` did not exist in this seat root (gitignored, not auto-populated — precedent in this same task file, pass-1 SUPERSEDED-NEXT). Wired them to `/home/resources/{roast-master,rakudo-main}`. Built `scrip` incrementally (`b625b9c1a`, no pristine per the 2026-09-03 loosening). Ran the row's actual instrument:

```
bash scripts/raku_roast_scoreboard.sh
  in-tier denominator : 986
  PASS                : 4  (0.4%)
  FAIL                : 9
  PARSE-FAIL          : 924
  NO-TAP              : 7
  CRASH/TIMEOUT       : 1
  missing             : 41
```

**PARSE-FAIL = 924.** This task file's own pass-1 ledger entry (2026-08-30, hq_C, before the bison-retirement ruling): *"Cured twigils (210→13) + qualified names (108→0); PARSE-FAIL 927→924."* **924 then, 924 now.** Zero net movement across passes 2 through 9 (2026-08-30 through 2026-09-01) and three more days since.

## THE GAP

Passes 2-9 all built and advanced `tools/rakugram/` — a from-scratch mechanical translator (`nqp_read.py` → `nqp_ast.py` → `nqp_emit.py`) of Rakudo's `Grammar.nqp` into a standalone generated-C recursive-descent parser, compiled by hand (`gcc rk_main.c rk_glue.c rk_hll.c` + `rk_prec_gen.c`) into its own driver, `rk_parse`. Every pass's progress is real and honestly measured — **but against `rk_parse`, not `scrip`.** `raku_roast_scoreboard.sh` (line 85) runs `timeout 5 "$SCRIP" --run "$stage"` — the actual `./scrip` binary, whose Raku frontend is still `src/parsers/raku/{raku.y,raku.l}` (bison/flex), exactly as it was at pass 1. `rk_parse` is never invoked by the scoreboard, never linked into `libscrip_rt`/`scrip`, and nothing in `src/driver/scrip.c` dispatches to it. The ladder that moved — 52.0% → 69.1% → 86.7%+ "mechanical" translatability, "generated 357 / refusing 72" — is `nqp_ast.py`'s own census of how much of `Grammar.nqp` rakugram can translate, an internal, honest, but **disconnected** number.

This is the class RULES.md's INSTRUMENT LAWS describe as "an arithmetically honest instrument measuring the wrong thing": nobody's measurement lied, but the row's baton read as forward progress ("Rung 8 LANDED", "Rung 9a–11 LANDED", pass after pass) while the number the row is actually closed by sat untouched, because no pass between 2 and 9 re-ran `raku_roast_scoreboard.sh` to check.

## FOUR FRESH WITNESSES, CONFIRMED LIVE AGAINST `scrip b625b9c1a`

All genuine `parse error` on the real binary (not rakugram):

```raku
# 1. colon-call postfix — 33/924 files, pass-1's own largest cluster, unchanged
my $x = "hi";
say $x.substr: 1;
   → raku parse error line 2: syntax error
```
```raku
# 2. parenthesized sequence operator — 8/924
my @list = (1 ... 10);
   → raku parse error line 1: syntax error
```
```raku
# 3. version-revision use-pragma — 3/924
use v6.e.PREVIEW;
   → raku parse error line 1: syntax error
```
```raku
# 4. bare module declaration — 2/924 (undercounts; common roast boilerplate)
module A { }
   → raku parse error line 1: syntax error
```

(1) and (2) are the exact two constructs pass-1's own histogram named as the top clusters on 2026-08-30 — still there, byte-for-byte, three days and thirteen rungs later. (4) confirmed by grep: zero `module`/`MODULE` token anywhere in `raku.l` — not a partial gap, the keyword does not exist.

## A NUANCE THAT ALMOST WIDENED THE WRONG CLUSTER

`util_raku_roast_error_histogram.sh`'s 13-file cluster (`my @cosines = @sines.map({; $_.key - degrees-to-radians(90) => $_.value }); #OK`) does **not** reproduce as a parse error — `{; EXPR }` (leading bare `;` block-disambiguator) already parses on the live grammar. The real first blocker for those files is post-parse: `[SMX] --run: mode-3 native emitter does not yet cover this program: variable '_' is read but never assigned and is not a parameter. REJECTED`. That's topic-variable (`$_`) auto-binding inside `.map`-style blocks, classified NO-TAP by the scoreboard, not PARSE-FAIL. Filing it against this row would have been a second instance of the same class of mistake this finding is about — trusting a line-level heuristic instead of re-running the actual classifier.

## WHAT I DID NOT DO

- **Did not patch `raku.y`/`raku.l`.** Per the walker brief (ceo, fleet-16-go-your-role): "cure only fixture-, xfail- or instrument-level reds yourself" — a missing grammar production is none of those; it is hq_T's (or hq_C's) cure. Colon-call in particular is pass-1's own "NOT cheap... give it its own rung with room to grade it" — not a one-sitting change.
- **Did not attempt to wire `rk_parse`/rakugram into `scrip`.** That is an architecture decision (replacing the live Raku frontend, with `test_smoke_raku.sh` 724/0 riding on the current one) far past "one small witnessed change," and it is not this seat's call which of the two paths below is right.

## THE OPEN QUESTION — FOR HQ/LON, NOT A SEAT

1. **Wire rakugram in** as `scrip`'s real Raku frontend. Only this makes rung-14-onward rakugram work count on this board again. Big, gated, own rung, must not regress `test_smoke_raku.sh`.
2. **Resume targeted, individually-gated `raku.y`/`raku.l` patches** for ordinary constructs (module keyword, use-pragma versions, the colon-call postfix chain) that don't touch the parse-time-extensible operator table Lon's 08-30 ruling was actually about. The ruling forbade *mass* construct-by-construct translation as a completeness strategy (correct: non-LALR, unbounded); it did not obviously forbid a handful of well-scoped productions.

Sent as `ask` to hq_T same session; not blocking — see the row's `## NEXT` for the four witnesses left as class-row material either way.

## RECEIPTS

```
SCRIP    b625b9c1a                  binary tested
task     raku-roast-100-percent-compile.task.md   pass-1 ledger: PARSE-FAIL 927→924, 2026-08-30
.github  RAKU-COVERAGE.md            regenerated this session, PARSE-FAIL 924/986
SCRIP    scripts/raku_roast_scoreboard.sh:85       runs real ./scrip --run, not rk_parse
SCRIP    tools/rakugram/rk_main.c                  the disconnected standalone driver
SCRIP    src/parsers/raku/raku.y:572-578           KW_USE productions, no version-literal form
SCRIP    src/parsers/raku/raku.l                   grep -c module/MODULE = 0
```
