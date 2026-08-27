# FINDING 2026-08-27 seat05 — `test_corpus_prolog_parser.sh` vacuous gate fixed: wrong extension + wrong path, not deleted files

**Date:** 2026-08-27 · **Seat:** seat05 · Row: `prolog-parser-corpus-vacuous-gate-422-files`.

## Root cause, confirmed not guessed

The minting session's STEP 1 asked to check git history for the two missing `.pro` dependency files before assuming their purpose. Checked: `git log --all --diff-filter=D` and a full-history name search both return **zero hits** for `prolog_parser.pro`/`prolog_recognizer.pro` anywhere in the corpus repo. They were never deleted — they never existed under that name. The real files are `corpus/demo/prolog/prolog_parser.pl` and `prolog_recognizer.pl` (their own header comments say `% prolog_parser.pro`, a stale comment, not evidence of a real `.pro` file). Combined with the second bug the task already flagged (`$REPO_ROOT/../corpus/...` has one `..` too many and escapes the sibling root), the script's two dependency paths pointed at nothing real for either reason independently.

## Fix

`test_corpus_prolog_parser.sh`: `PARSER_SRC`/`RECOG_SRC` now point at `$S4E/corpus/demo/prolog/{prolog_parser,prolog_recognizer}.pl` — reusing `$S4E` (already correctly computed earlier in the same script) instead of the separately-computed, buggy `$REPO_ROOT/../corpus` path. One-line-per-variable change.

**Before:** `Parser: pass=0 empty=422` / `Recognizer: pass=0 empty=422` / `RESULT: PASS` (vacuous — the two `swipl -f` invocations failed to even find their script argument, silently, and empty output was never treated as failure).
**After:** `Parser: pass=406 empty=8 crash/timeout=8` / `Recognizer: pass=395 empty=27 crash/timeout=0` / `RESULT: PASS` — real signal, 96%/94% pass rates, not a rubber stamp.

Also fixed the task's own DONE-WHEN command while verifying it: its `grep -oP '(?<=Parser: *pass=)[0-9]+'` used a `*`-quantified (variable-length) lookbehind, which this box's PCRE rejects outright (`lookbehind assertion is not fixed length`) — a second, independent, pre-existing bug that would have made the verification command itself always report false-vacuous regardless of the script fix. Replaced with `\K` (match-reset), which doesn't have the fixed-length restriction.

## What this does NOT claim

Per the task's own STEP 2 warning, this script only ever measures two standalone `swipl` demo tools against the corpus — it does not invoke `./scrip` and never has. **Checked whether that leaves SCRIP's own Prolog frontend untested: it does not** — `SCRIP/scripts/` already carries 30+ dedicated `./scrip`-based Prolog runners (`test_prolog_rung13.sh` through `rung46`, `test_crosscheck_prolog.sh`, `test_smoke_prolog.sh`, `test_prolog_rung_suite.sh`, `test_prolog_swi_suite.sh`, `test_prolog_bb_honest.sh`). This one script was never meant to be *the* SCRIP-Prolog gate — the task's STEP 2 framing overstated the gap in isolation. Whether those 30+ scripts themselves currently pass is a separate, unchecked question — not this row's claim.

## Context

Landed under Lon's same-session directive (`/home/resources/postoffice/ANNOUNCEMENT.md`, CEO custody): all 7 languages ship on x86/x64 with 100% coverage — no per-language hold. This fix directly serves that: Prolog's corpus now has an honest, non-vacuous signal instead of a false green.

Verified: `bash -n` syntax check, live run against the real 422-file corpus, DONE-WHEN command re-run standalone (exit 0, prints `OK`). Zero corpus edits — SCRIP-repo script fix only.
