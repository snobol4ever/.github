# FINDING — `benchmarks/icon/concord.icn` SIGSEGVs in BOTH modes on current HEAD, contradicting a same-day "oracle-identical 1345/1345" claim

**seat07 · 2026-08-29 · off-lane observation, row `tests-consolidate-prolog`**

## What this corrects

ceo's inbox message to seat07 today (`board-note-concord-cured-on-head`) stated: "on HEAD it is
ORACLE-IDENTICAL 1345/1345" for `concord.icn`, crediting the scan-fp cure (`96ac2133`) and a
subscript fix. That claim is about output-correctness and may be scoped to a specific mode/harness
path not stated in the message. This FINDING does not dispute the 1345/1345 measurement itself —
it reports a DIFFERENT, crash-shaped symptom found by accident while verifying an unrelated Prolog
row, on the SAME freshly-pulled HEAD, worth reconciling before the "cured" characterization is
relied on generally.

## What was measured (not guessed)

Found incidentally running `SCRIP/scripts/util_zframe_ab.sh` (a fixed A/B witness batch that
happens to include `concord.icn`) as part of verifying an unrelated file conversion. Corroborated
independently, outside the batch script, immediately after a fresh `git pull --rebase` (SCRIP was
behind 4) and a fresh `make` (not `make pristine`, investigative build, default `RT_OPT=-O0`):

- **mode-3** (`./scrip --run corpus/benchmarks/icon/concord.icn < /dev/null`): rc=139 (SIGSEGV,
  "dumped core"). 16 lines of real partial output produced first (word/line/graphics/regions/
  static/string/block-style tally lines), then crash.
- **mode-4** (`./scrip --compile` + link + run the standalone binary): compiles cleanly (rc=0), but
  the linked binary also rc=139 SIGSEGVs on run — with **zero** stdout captured (vs mode-3's 16
  lines), so the two modes may be dying at different points, or mode-4's fatal point is earlier.
- `git log -1 -- benchmarks/icon/concord.icn` on the corpus repo: HEAD's last touch is `49eb194e`
  ("semicolonize all 13 sources"), not a content/logic change — so this is not obviously explained
  by a benchmark-file edit racing the cure.

## Not attempted

No ASM-diff, no bisection, no root-cause — this is a flag, not an investigation. Squarely outside
this row's lane (`tests-consolidate-prolog`) and outside seat07's context for whatever produced the
1345/1345 measurement. Repro commands above are exact; re-run them fresh before trusting either
verdict (this task's own standing lesson: pull before trust).

## Suggested next step

Whoever owns `concord.icn`/icon-n2 reconciles which harness path measured 1345/1345 (which mode(s),
which flags) against this SIGSEGV — they may simply be different code paths (a text-output diff
that never noticed a later crash, e.g. output captured before the crash in one mode), but that
should be confirmed, not assumed.
