# FINDING — seat02: icon-corpus-semicolonize lands 395 files; a fresh m3 board reading (244/19/30) that matches neither hq_C's 232 nor hq_P's 169

**Seat:** seat02 · **Row:** `icon-corpus-semicolonize` (rank 0) · **Date:** 2026-08-24

## 1. The transform, and a harness bug found before any corpus write

Ported icont's own newline-semicolon-insertion rule (Beginner/Ender) by parsing it directly
out of Arizona Icon's canonical lexer source at transform time — `src/common/lextab.h`
(29 reserved words + 80 operators, regex-extracted, not hand-transcribed) and
`src/common/yylex.h`'s `yylex()` control flow (comment/string/number scanning, the
`nlflag && lastend && Beginner` insertion test) — rather than reimplementing from the
manual's prose, per the row's own instruction. Verified against Lon's own ambiguity
example first: `f(1)\n(2+3)` semicolonizes to `f(1);\n(2+3);` — two statements, matching
his stated icont reading.

**Per-file load-bearing check, exactly as specified:** compile+run the file with the real
`icont`/`iconx` (found already built at `/home/resources/icon-master/bin/`, not on PATH)
before and after the transform; byte-identical combined stdout+stderr+exit required, or the
file is left untouched and logged as a transform defect — never a corpus defect.

⛔ **First full sweep showed 54 files "failing" this check.** Root cause: my verify harness
compiled the transformed candidate from a differently-named temp file, and Icon's own
run-time error/traceback text embeds the source filename — so any file whose execution hit
an error showed a spurious divergence purely from the filename string, not from any actual
behavior change (confirmed by hand on `parser/augop_add.icn`: identical `Run-time error 102`
traceback, differing only in `orig.icn` vs the temp name). Fixed by compiling the transformed
candidate from a scratch directory carrying the *same* basename as the original (siblings
symlinked in for the one file using relative `$include`). Re-ran the full sweep: **zero**
`TRANSFORM-DEFECT-BEHAVIOR` results. Recorded here because the same false-positive shape
would hit anyone else building a similar before/after oracle harness on this corpus.

## 2. Result

Scope: every `.icn` under `corpus/icon/` excluding `ipl/` (497 files, matching the row's own
DONE-WHEN). Ran the transform over **all** 497, not just the 116 with zero semicolons —
correctly so: 469 of 497 needed at least one insertion despite most already carrying *some*
semicolon, so "has ≥1 semicolon" (the census metric used by this row's own prior LEDGER
entries) undercounts real conversion need. Outcome:

- **395 converted and verified** (iconx byte-identical before/after).
- **28 already fully correct** (zero insertions needed).
- **74 left untouched, unverifiable at baseline** for reasons independent of this transform:
  72 hit a genuine icont compile error on the *original* file before any transform touched
  it (2 use Icon's newer `import` module system this icont build doesn't support; the rest
  are pre-existing icont-incompatible constructs, e.g. `coverage/coverage_x64_gaps.icn:103`
  deliberately probes a SCRIP-only `(expr; expr)` sequence-expression SPITBOL/Icon-style
  extension real Icon has never supported); 2 timed out at baseline (`parser/repeat_op.icn`
  is `repeat write("x")`, a by-design infinite loop parse-probe; `rung36_jcon_toby.icn` is
  commented "only for Jcon; does not work under Icon v9" and iterates near-2^63 ranges).

Zero-semicolon census (this row's own DONE-WHEN metric): **116 → 1**. The one holdout is
`parser/repeat_op.icn` — left unconverted on purpose: I can compute the correct insertion by
hand (single Ender→Beginner transition before `end`, the same shape verified safe on
hundreds of other files) but refuse to apply it without the load-bearing check, and that
check cannot run on a program that never terminates. DONE-WHEN therefore reads `1`, not `0`,
for a documented, deliberate reason — not an oversight.

`corpus/benchmarks/icon/` (a *separate* top-level dir the DONE-WHEN command doesn't even
walk, despite the row's SCOPE prose naming "the bench suite") was **not touched this
session**, per the row's own QA note: icon-n2 is live on that exact denominator. Pinged
hq_P (`s4e_msg.sh send hq_P icon-semicolonize-bench-coordination`) before starting; no reply
by session end. Left for the next session/seat — either resume this row for that slice, or
hq_P clears it directly.

## 3. ⭐ Board movement — re-measured fresh, and it doesn't match your 169

Corpus changes touched 227 `rung*.icn` files (the ones `test_icon_all_rungs.sh` actually
grades), so I re-ran the m3 board rather than assuming semicolon-only edits are board-inert.
First pass was on a stale SCRIP checkout; pulled to current main (`be376a2f`, which includes
your disjunction-cell fix) and rebuilt clean (`-O0`, no `-O2` anywhere) before trusting
anything. **Two agreeing runs, `pgrep -c scrip`==0 before/after both times, clean tree,
binary hash stable across the two runs:**

```
Icon --run: PASS=244 FAIL=19 XFAIL=30 TOTAL=293   (SCRIP be376a2f)
```

This is **higher than both** numbers in your same-day FINDING
(`hq_P-disjunction-cell-was-16-for-a-20-byte-template-and-icon-has-regressed-232-to-169.md`):
hq_C's morning 232 baseline, and your own 169 regression reading (same suite, same
TOTAL=293, same XFAIL=30 — directly comparable shape). I am **not** claiming this delta as
this row's own — SCRIP source moved independently of anything in this row (I never touched
`SCRIP/`), and per the just-landed SHARED-NODE VERDICT SCOPE law this is a shared-node
number, not an attributable one. I flag it because your FINDING marked 169 "URGENT AND NOT
MINE" and still open — 244 at current HEAD is a data point for that investigation (possibly:
whatever caused 169 already has a fix in `be376a2f..HEAD`'s other 8 commits; possibly your
169 reading was a load/contention artifact worth a second agreeing run at your end too — I
can't tell which from here). m4 twin (`test_icon_x64_all_rungs.sh`) not re-measured this
session (time).

## 4. Two STEP-0 digest corrections worth the other top-four rows' attention

Doing this row's mandated STEP-0 self-fix (CEO-19: every top-four baton fixes its own root's
CLAUDE.md) surfaced two things the shared STEP-0 boilerplate text itself gets wrong, which
means the *other three* rows sharing that boilerplate (`corpus-suites-consolidation`,
`strip-mechanical-carve`, `instrument-repair-bundle`) may carry the same two mistakes when
their seats do their own STEP-0:

1. **The lon-folder tombstone instruction says "OFF-LIMITS is unchanged and absolute."**
   That's stale — `RULES.md` (`df31ea82`) and `GOAL-CEO.md` CEO-14 both already record Lon's
   **full** retraction of the rule (2026-08-24 s269, verbatim: *"Remove all references to the
   lon folder being special. I retract all of it."*), landed as ORDINARY CORPUS, no
   restrictions. I wrote my CLAUDE.md to match RULES.md's actual (retracted) text, per this
   project's own general law (a stale digest loses to RULES.md, and you tell HQ) rather than
   the STEP-0 boilerplate's paraphrase. Whoever wrote that boilerplate line was working from
   older information than what's already landed.
2. **"copy the expected SNOBOL4 total WITH its provenance sentence from ceo's digest"** — two
   different, disagreeing numbers exist in `GOAL-CEO.md`'s own LIVE CURSOR: CEO-18 (s271)
   gives **364/364 both modes** with full methodology (six gates rc=0, computed+negative-
   tested); CEO-20 (s272) separately says **"SNOBOL4 362-green"** as a bare floor constraint,
   no provenance sentence of its own. I copied CEO-18's (the one that actually has a
   provenance sentence, as instructed) and flagged the disagreement inline in my CLAUDE.md
   rather than silently picking one. Worth someone reconciling once, centrally, rather than
   four seats independently guessing which number is current.

Also: `/home/claude02` is not itself a git repo (confirmed — CLAUDE.md lives outside all
three tracked repos), so "one attributed commit" for the STEP-0 fix isn't literally
satisfiable; the file edit itself is the record.

## 5. Sequencing note

Per this row's own SEQUENCING section: Icon's corpus-suites-consolidation family can now
start — the bulk of `corpus/icon/` is born in the correct dialect. Sent via
`s4e_msg.sh send` to the suites-consolidation custodian.
