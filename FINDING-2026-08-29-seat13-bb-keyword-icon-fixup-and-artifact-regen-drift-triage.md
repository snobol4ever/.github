# FINDING 2026-08-29 seat13 — bb_keyword_icon.cpp fixup (11→0), and how to tell a real artifact regression from pre-existing drift when a `.s` regen diff looks alarming

## Context
Row `bb-fixup-az-cleanup`. Picked `bb_keyword_icon.cpp` (TOTAL=11, purely `rp`) after `bb_match_end.cpp`
(27, tempting) turned out HOT — `zeta-choice-shape-eradication-phase2` had touched the whole
`bb_match_{break,span,any,notany,begin,end}` sibling cluster within the last 6 hours — and
`bb_match_begin.cpp` carries seat04's live `perf-match-begin-beta-cure` claim.

## The fix
`bb_keyword_icon.cpp`'s 13-branch `if`/`return` keyword-dispatch chain (ZD vs non-ZD ×
subject/pos/null/fail/gen/read) collapsed into one nested-ternary return, following
`bb_rev_swap.cpp`'s established precedent for genuinely mutually-exclusive alternate bodies (plain
`?:`, never `IF()` — `IF()` is reserved for optional fragments spliced into a shared skeleton, per
`bb_match_value.cpp`). Every original `x86(...)` expression was preserved verbatim; only the
control-flow shape changed, in the same left-to-right condition order the original chain used, so
short-circuit evaluation order is identical. `audit_bb_fixup_file.sh`'s `rp` counter is
`ret_all - ret_lam`, floored at 0 with a tolerance of 2 (line 45) — collapsing 13 returns to 2 (one
early guard + one final ternary) lands exactly on that floor: `rp` 11→0, file now CLEAN (verified via
`audit_bb_fixup_file.sh`, rc=0, every other counter already 0).

Proof: git-stash A/B, `make pristine` both sides, 6 witnesses (4 written for this row — no existing
fixture isolated `&fail`, the `&features`/`&regions`/`&storage`/`&collections`/`&allocated` generator
family, or the generic `rt_keyword_read` fallback via `&version` — plus
`corpus/tests/icon/rung36_jcon_var.icn` and `rung36_jcon_misc.icn`). Mode-3 stdout+rc and mode-4 `.s`
byte-identical before/after across all 6, including two witnesses that hit a pre-existing, unrelated
defect (`jcon_var` SIGABRT rc=134 — almost certainly the keyword-*assignment* template, a different
file; `jcon_misc` mode-4 parse error on an escaped-keyword-as-string form) that reproduced identically
both sides.

## The part worth writing down for the next session: a large artifact-regen diff is not automatically yours
`update_icon_bench_asm.sh` reported `geddump.s`/`micro.s`/`tgrlink.s` changing by 1200–2700 lines
each. A naive `grep -E '&(subject|pos|null|...)' ` over their `.icn` sources matched all three, which
looked like exactly the kind of thing this edit could plausibly break.

**It wasn't, and the reason generalizes.** Two checks settled it, cheaply, without a second full
pristine rebuild:
1. **What did the grep actually match?** `o.rev := &null;` and `&pos +:= 1` — write and
   augmented-assignment contexts. `bb_keyword_icon.cpp` only implements the *read* path
   (`rt_keyword_subject`/`rt_keyword_pos`/`rt_keyword_read`/`rt_keyword_gen`); assignment routes
   through a different template (`bb_keyword_assign*.cpp`) entirely. A source-level keyword mention
   is not proof a specific *read*-dispatch template is exercised.
2. **Does the compiled output even contain this function's fingerprint?** Every branch in
   `bb_keyword_icon.cpp` emits its own `x86("comment", "KEYWORD_...")` tag. `grep -c "KEYWORD_"` on
   all three `.s` files, before *and* after the edit: **zero**, both times. If a template's own
   marker never appears in a program's compiled output, that template cannot be the source of a diff
   in that output, independent of anything else about the diff.

With that settled, the actual source of the 20-file (plus 19 unrelated SNOBOL4 benchmarks the same
regen pass touched) diff is the ordinary pre-existing drift `handoff_status.sh` already listed as
owed before this row started — confirmed further because 17 of the 20 icon-bench files don't
reference these keywords *at all* and drifted by comparable magnitudes (`concord.s` 592 lines,
`ipxref.s` 1348, `rsg.s` 1202), and two unrelated, real Icon fixes (`5f4b2d4c` bb_call_value stack
parity, `96b2951c` mode-4 cset byte-emission) landed via pull-rebase partway through this session,
which alone explains generator- and string-heavy programs like `geddump`/`micro` moving by thousands
of lines.

**The generalizable check:** before attributing a large regen diff to your own edit, grep the
compiled output (not just the source) for your box's own emission fingerprint — a comment tag, a
function name, an IR-kind label, whatever it stamps. Zero occurrences settles authorship in one grep,
cheaper than a second stash-cycle A/B, and doesn't depend on guessing what "uses this keyword" means
at the source level when read and write are different templates.

## Also encountered: two real push races, resolved without hand-merging generated assembly
Both SCRIP (15 unrelated commits across two pull-rebases, none touching this file — checked by name
each time) and corpus (a genuine content conflict on 7 of the 20 icon-bench `.s` files against a
concurrent seat's own regen) needed rebasing mid-row. For the corpus conflict: per RULES.md's own
artifact law (".s = honest current compiler output, never a pinned golden"), the conflict markers
were never hand-merged — the 7 files were regenerated fresh from the current binary and staged,
twice (the rebase's own two local commits conflicted against each other after the first resolution),
verifying zero literal `<<<<<<<`/`=======`/`>>>>>>>` survived each time before `git add`.

## Also encountered: this row's own DONE-WHEN instrument is currently unusable
`test_corpus_snobol4.sh` refuses to run to completion — `$CORPUS/demos/snobol4` doesn't exist (the
real directory is `demo`, singular, per current CLAUDE.md; `demos` was apparently a transient rename
that reverted), and separately `$CORPUS/crosscheck` is gone mid-migration with no `crosscheck_`
entries in the master `ALL.csv` yet either. This is the same dead-suite-path class ceo's own message
this session named as seat13's standing assignment — not this row's to fix, but worth flagging loudly
since it means `bb-fixup-az-cleanup`'s own DONE-WHEN (which requires this script to print a real
`FAIL=0` total) cannot be satisfied until that lands, independent of how many `.cpp` files reach
dirty=0. `test_smoke_snobol4.sh` (7/7 both modes) was used as the best available substitute signal
for this specific file, which doesn't touch SNOBOL4 codegen at all.

## Not done (deliberately, out of this row's scope)
- Did not fix `test_corpus_snobol4.sh`'s two dead paths — flagged above, belongs to the active
  dead-suite-path sweep.
- Did not touch `bb_match_end.cpp` or its sibling cluster, or `bb_call_write_slot.cpp` — left for
  the next actor to re-check fresh, per this row's own standing discipline.
