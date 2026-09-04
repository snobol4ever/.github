# rung05 (goto/labels) FORMS complete, no SCRIP gap; a second shared-oracle SIGSEGV class found and sidestepped

**seat07, 2026-09-04. MODE `FLEET-16`. Lane hq_P. Row `snobol4-ladder-every-feature-in-isolation-with-variations`, rung05.**

## 1. rung05 FORMS complete, all green

SPITBOL manual pp.176-178 ("Label field", "Goto field") read in full. Minted 7 new witnesses alongside the
pre-existing base `ladder__rung05_conditional_goto` (which already covers the F-only case `:F(LABEL)`):
`goto_unconditional`, `goto_success_only`, `goto_success_and_failure`, `goto_indirect_label`,
`goto_lowercase_sf`, `goto_absent_statement`, `label_leading_digit`. All 8 oracle-cut from `sbl -bf`,
`scrip --run` cross-checked before absorbing, all GREEN — this rung turned up no compiler gap, unlike rung04.
`test_snobol4_ladder.sh --to 5`: 16/16 (8 witnesses × 2 modes); `--to 10` regression floor: only the
pre-existing, deliberate rung04 red, no new regressions. `util_ladder_forms_check.py --phase isolation`:
30/30 declared forms (rungs 00-05) witnessed. Discriminating power spot-checked on `goto_absent_statement`
against a hand-corrupted temp copy of its `.ref` (never the shared master) — correctly detected.

Two deliberate exclusions, noted in LADDER.tsv's own NOTE cell so a future session does not re-derive them:
- **Direct Goto via `CODE()`** (`:<VAR>`, pp.177-178) is explicitly out of scope here — rung16 owns `CODE()`
  construction and already cites this same page range for the direct-Goto form; minting it in rung05 would
  require building `CODE()` out of order.
- **Case-folding of labels** (p.176) — same rationale as rung01's exclusion: this project's oracle invocation
  is `sbl -bf` (`-f` = folding OFF, matching SCRIP's case-sensitive design), so a folding witness would test
  the book's default against an oracle configured to do the opposite.

## 2. Second shared-oracle SIGSEGV class: a digit-led label referenced via a bare paren goto target

Distinct from the rung04 `"MASH" "M" = "B"` / ERROR-212-recovery crash
(FINDING-2026-09-04-seat07-rung04-parenthesized-replace-expression-unimplemented-and-oracle-sigsegv.md §2).
Minimal repro:
```
 OUTPUT = 'before'
 :(1start)
 OUTPUT = 'skipped'
1start  OUTPUT = 'label beginning with a digit'
END
```
`sbl -bf` on this input: `ERROR 231 -- syntax error: invalid numeric item` at the `:(1start)` line, printed
**twice**, immediately followed by a SIGSEGV (rc=139, core dumped). The label FIELD rule (p.176, "Labels must
begin with a letter or digit") is fine with `1start` as a definition; the crash is specifically in how the
oracle's error-recovery path handles a digit-led token inside a bare `:(...)` goto target — it appears to try
lexing `1start` as a numeric literal first (consistent with "invalid numeric item"), and something in the
recovery from that failure walks off the end. Not re-tested for determinism (rung04's analogous crash was
3/3 vs 3/3 clean over n=6) — out of scope for this row to characterize further.

**Sidestepped, not filed as a class row**: the witness reaches `1start` by sequential fallthrough instead of
a goto reference, which cleanly isolates the label-FIELD rule actually being tested (digit-led labels are
legal to *define*) without touching the crashing *reference* path. `scrip --run` and the oracle agree
(rc=0, `before` / `label beginning with a digit`) on the fallthrough form. Whether `:(1start)`-style
references to a digit-led label are valid SPITBOL at all is a separate, unanswered question — left for
whoever next revisits shared-oracle crash inputs (same population as the rung04 finding: worth a combined
future row once there are enough of these to characterize as one class rather than two one-offs).

## Session wrap

Wrapped on operator instruction. Row left OPEN (not `done`, not `park`'d — no blocker, straightforward
continuation): see the task baton's `## NEXT` for rung06 (ARRAY, Ch7 pp.88-91). Pushed SCRIP (sync-only, no
source changes this session) / corpus (`tests/snobol4/{ALL.csv,ALL.sno,ALL.ref,ALL.excluded.txt,ALL.in,
ALL.xfail,config/LADDER.tsv}`) / .github (this FINDING) after `git pull --rebase` clean on all three.
`make test` reverified green post-rebuild (RT_OPT=-O0, incremental) before pushing.
