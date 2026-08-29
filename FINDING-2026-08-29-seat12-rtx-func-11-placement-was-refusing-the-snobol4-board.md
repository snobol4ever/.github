# FINDING: RTX-FUNC-11/rtx11_dynvar's placement inside `tests/snobol4/probe/` was refusing the whole blocking SNOBOL4 corpus gate, not merely sitting ungraded

Row: `corpus-crosscheck-probe-total-conversion`. Origin: ceo's `## QA` entry on that row's task file (2026-08-29), which flagged three of the four affected files as boardless. This FINDING records the actual mechanism and severity, measured directly.

## What was there

seat06's 2026-08-29 sitting relocated the RTX-FUNC-11 witness pair (`rtx_func_11_{include,inline,inc}`) and its `rtx11_dynvar` sibling (`rtx11_dynvar_{include,inline}` + `rtx11_dynvar.inc`) out of `corpus/probe/` — correct per Lon's ruling that a genuinely `-INCLUDE`-driven witness may stay standalone, declared in a `KEEP.md` beside it, rather than being banner-block-converted. The relocation landed all 10 files directly inside `tests/snobol4/probe/`.

## Why that broke the board, not just those four files

`test_corpus_snobol4.sh`'s suite-family loop scans `tests/snobol4/probe/` **recursively** (`find "$SUITES/probe" -name '*.sno'`, no `-maxdepth`) and treats any `.sno` with a sibling `.ref` as a suite family. None of the four graded files (`rtx11_dynvar_include`, `rtx11_dynvar_inline`, `rtx_func_11_include`, `rtx_func_11_inline`) carry the suite banner format (`*---...--- N name`). `corpus_suite_harness.py`'s `read_suite()` has no "whole file is one implicit entry" fallback — every non-banner line reads as its own one-line entry consuming one line of `.ref`, so a real program's line count exhausts a short `.ref` almost immediately:

| file | measured failure |
|---|---|
| `rtx11_dynvar_include.sno` | `ValueError: family.ref is shorter than family.sno at seq 2` |
| `rtx11_dynvar_inline.sno` | `ValueError: family.ref is shorter than family.sno at seq 2` |
| `rtx_func_11_include.sno` | `ValueError: family.ref is shorter than family.sno at seq 4` |
| `rtx_func_11_inline.sno` | `ValueError: family.ref is shorter than family.sno at seq 4` |

`test_corpus_snobol4.sh` catches the crash (stderr discarded, no `SUITE_BOARD` line) and correctly buckets each as `MISSING` rather than grading a shrunken denominator. **But `MISSING>0` is a hard `exit 2` for the entire board** (the script's own INSTRUMENT-LAWS-derived refusal, line ~340): `if [ "$MISSING" -gt 0 ]; then ... exit 2; fi`. So this was not four ungraded witnesses sitting quietly in a warning — it was **refusing the blocking SNOBOL4 corpus gate outright** for every session that ran `test_corpus_snobol4.sh` (part of `make test`'s blocking set) since the relocation landed, until this FINDING's fix. ceo's QA entry, written from the board's own printed output, undercounted by one: it named three of the four; direct re-measurement here (running each file through the harness individually) found `rtx11_dynvar_include` breaks identically.

## The mechanism was already documented, on a different family

This is the exact trap `tests/snobol4/gimpel_triage/KEEP.md`'s own "WHY IT SITS HERE AND NOT UNDER `tests/snobol4/probe/`" section describes, word for word: a non-suite standalone keeper placed inside `probe/` is misread as a broken suite by the recursive scan, because `$SUITES` is scanned for exactly two subtrees (`crosscheck/` and `probe/`) and a **sibling** directory at `tests/snobol4/` is invisible to it. `gimpel_triage` hit this and was corrected in the same session it was first placed (2026-08-29 earlier that day); the RTX pair independently repeated it hours later, in a different sitting, on a different family — the KEEP.md pattern is documented but not yet load-bearing as a *placement check* anyone runs before landing a relocation.

## Fix

`git mv` all 10 files to a new sibling directory, `tests/snobol4/rtx_func_11/` — zero content change. Re-verified from the new location (all four graded files): live SPITBOL oracle, `scrip` mode 3, `scrip` mode 4 — all match `.ref`. `tests/snobol4/probe/KEEP.md`'s now-inaccurate section replaced with a forwarding note to the new `tests/snobol4/rtx_func_11/KEEP.md`, which carries the full history. `.github/GOAL-SNOBOL4-100.md`'s bare-name citation of `probe/rtx_func_11_include` re-pointed to the new path (same commit noted the header-claimed SIGSEGV no longer reproduces, per seat06's own already-recorded re-measurement — not re-litigated here). corpus commit `37e6473a7`.

Board re-run after the fix, full pristine rebuild first: `test_corpus_snobol4.sh` — **GATE OK: m3 PASS=1381 FAIL=0 · m4 PASS=1381 FAIL=0 SKIP=0 · MISSING=0** (previously MISSING≥4, exit 2).

## Worth someone's attention

**A `KEEP.md`-documented placement lesson isn't self-enforcing.** Two independent families (`gimpel_triage`, then RTX-FUNC-11) hit the identical recursive-scan trap in the same day, on the same row, with the fix already written down after the first occurrence. Nothing currently checks "does a new `KEEP.md`-declared standalone file live directly under `probe/`" before it lands — that's a mechanical check (`test_gate_suite_conversion_complete.sh`'s declaration matcher walks ancestor `KEEP.md`s already; it doesn't currently distinguish "declared AND badly placed" from "declared and fine") that could catch this class before a future third instance, but minting it is out of this row's own scope.
