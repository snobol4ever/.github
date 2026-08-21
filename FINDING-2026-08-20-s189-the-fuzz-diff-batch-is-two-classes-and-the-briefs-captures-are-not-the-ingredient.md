# FINDING — s189 (seat6) · THE `fuzz-diff-batch` IS **TWO** CLASSES, NOT ONE, AND IN EVERY WITNESS THE **CAPTURE THE BRIEF NAMES IS NOT THE INGREDIENT** — THE ALTERNATION IS

**Row:** `fuzz-diff-batch` (QUEUE rank 2). **Disposition: CLASSIFICATION COMPLETE, NO FIX** — the row's own clause ("YOUR FIRST
DELIVERABLE IS THE CLASSIFICATION, NOT A FIX") governs, and the classification splits the batch in a way that routes half of it
to an existing row and half of it away from one.

**Tree:** SCRIP `2c8d2b34` · corpus `e48763a2` + the 12 witnesses below · **`make pristine` before every verdict** (EXIT=0),
RT_OPT `-O0` (O0-DEV). **NO COMPILER FILE TOUCHED** — this rung adds corpus witnesses only.
⭐ **RE-PROVED AT SCRIP `3dc52576` (corpus `7aa87e81`) AFTER A MID-RUNG REBASE MOVED SCRIP SIX COMMITS**, second `make pristine`
EXIT=0: **every verdict in this FINDING is unchanged** — all 18 witnesses identical, board identical, the D-1 inline controls
stable 6/6 `match`, the D-2 inline forms stable 6/6 HANG/SIGSEGV, `160_pat_alt_inner_gen_resume` SIGSEGV rc=139 4/4. The six
commits (monitor instrument, scorecard oracle-flag, lon-suite deletion, keyword tooling) are inert to this class.

---

## 1. DIRECTION — ASKED FIRST, BECAUSE THE ROW PROMOTES A FALSE ACCEPT IMMEDIATELY

**ALL SIX ARE FALSE REJECTS. THERE IS NO FALSE ACCEPT IN THIS BATCH. NOTHING IS ESCALATED.**

Every `.ref` reads `match`; SCRIP answers `nomatch`. The oracle is match-side in all six, so a false accept is impossible here
**by construction** — and that is a measurement, not an assumption: the six `.ref`s were **re-derived from the live oracle**, not
trusted from the file.

⭐ **AND THE RANK-0 ORACLE-FLAG HAZARD DOES NOT TOUCH THIS BATCH — MEASURED, NOT ASSUMED.** Row `scorecard-oracle-case` warns that
13 of 14 suites grade a case-SENSITIVE engine against a case-FOLDING oracle. All six witnesses were run under **both** arms:
`sbl -b` and `sbl -bf` return **identical** verdicts on all six (every identifier is internally case-consistent, so folding is a
no-op here). The batch's `.ref`s are honest under either flag.

## 2. ⭐ ONE WITNESS HAS HEALED SINCE s183 — `fz_diff_01` IS GREEN AT HEAD

`fz_diff_01` (`(((ARBNO(ARB)) . v0 | '' ARB)) $ v0`) passes **both modes** on the pristine tree. It is a mover, not a defect;
the row's "6 WRONG-ANSWER witnesses" is **5** at HEAD. Stable over 6 consecutive runs.

**m3 ≡ m4 ON ALL SIX.** No mode divergence anywhere in this batch — the 1:1 invariant holds, so nothing here is an m4-lane issue.

## 3. ⭐⭐⭐ THE SPLIT — INLINE-vs-STORED SEPARATES THE FIVE INTO TWO CLASSES

Every witness is a **stored** pattern (`P = …` then `*P`). Every one of them contains a construct `sno_pat_inline_ok`
(`lower_snobol4.c:1326`) has **no case for** — BAL, FENCE, ARB, or a capture — so all five fall through `default: return 0` to
the `PAT$` blob path. The decisive experiment is therefore to write the *same pattern inline* and re-measure:

| witness | reduced RED witness | stored | **inline** | class |
|---|---|---|---|---|
| `fz_diff_13` | `(ARBNO(*G0) \| ARBNO(ARBNO(FENCE(POS(1)))))` | nomatch | **match** | **D-1** |
| `fz_diff_22` | `('' \| '') ARBNO(ARBNO(REM) FENCE(SPAN('abc')))` | nomatch | **match** | **D-1** |
| `fz_diff_07` | `(BREAKX('abc') \| FENCE('a'))` unanchored | nomatch | **nondeterministic** | **D-2** |
| `fz_diff_08` | `(ANY('abc') \| (BAL \| ''))` | nomatch | **HANG rc=124** | **D-2** |
| `fz_diff_20` | `(ARBNO(REM) BAL \| '')` | nomatch | **SIGSEGV rc=139** | **D-2** |

**CLASS D-1 (2 witnesses) — BLOB-RESUME ONLY.** The inline form is **correct and deterministic** (8/8 runs `match`); only the
stored blob wrong-answers. These are **faces of the existing `blob-resume-refusals` row** (rank 2) and its s183 root cause — the
untiered disjunction: `zdp_seam_tier` (`zeta_depth.c:38`) models two β motions (tier 1 EXTEND, tier 2 self-undo-LEFTWARD) and an
`IR_MATCH_ALTERNATE`'s β is a THIRD motion (TRY THE NEXT ARM) that scores 0. **They should not be worked as new defects.**

**CLASS D-2 (3 witnesses) — BROKEN ON BOTH PATHS.** The stored form wrong-answers **and** the inline form hangs, crashes, or is
nondeterministic. These are **not** blob-resume issues and do **not** duplicate an existing row: the blob is wrong-answering a
shape the statement regime cannot execute either. ⛔ **THE INLINE BEHAVIOUR IS STRICTLY WORSE THAN THE STORED ONE** — a wrong
answer became a crash — so "just inline it" is not a cure for this half, and admitting these shapes to `sno_pat_inline_ok`
without first fixing the statement regime would convert 3 silent wrong answers into 2 crashes and a coin flip.

## 4. ⛔ THE BRIEF'S TWO NAMED SHAPES ARE BOTH FALSIFIED

The row names its shapes as "`(*G0) $ v1` unanchored" and "a capture whose target is itself a capture". **In both, the capture is
inert** — removed by ablation, one ingredient at a time, each step re-measured:

- **`fz_diff_07`** — drop the `$ v1` capture entirely: **still nomatch**. Inline `G0` so no defer remains: **still nomatch**. So
  neither the capture nor the deferral is load-bearing. The true minimum is `(BREAKX('abc') | FENCE('a'))` matched **unanchored**,
  and it needs **both** arms: `('zz' | FENCE('a'))` passes, `(BREAKX('abc') | 'a')` passes. **The ingredient is a retreat-scanning
  generator in arm 1 whose implicit alternatives must exhaust before the explicit arm 2 is tried** — manual p.208 verbatim:
  *"ARB and BAL have implicit alternatives which are tried before your explicit ones … Only then are other pattern alternatives
  tried."* SCRIP exhausts arm 1 and concedes instead of falling to arm 2.
- **`fz_diff_20`** — the `. v1` capture whose target is a capture: remove it and `(ARBNO(REM) BAL | '')` **still fails**, while
  `ARBNO(REM) BAL` (same arm, alternation removed) **passes**. The ingredient is the alternation, not the capture.

⭐ **AND THE OBVIOUS SUSPECT IS EXONERATED — WITH ONE MEASURED BOUNDARY.** `BAL` appears in three of the five and the natural
hypothesis — that BAL fails to offer its implicit longer alternatives (manual p.125: *shortest non-null balanced string*,
extended on retry) — is **false for this batch**: bare `BAL` under `POS(0)…RPOS(0)` extends correctly to `'ab'` and `'aaa'`,
**inline and stored alike**, and it keeps extending correctly even with a capture in the retreat path
(`POS(0) BAL $ OUTPUT RPOS(0)` prints `A / AB / ABC / match`, oracle-identical). BAL is a carrier of the defect, never its site.
⛔ **THE BOUNDARY, RECORDED SO THE NEXT SEAT DOES NOT MERGE TWO CLASSES:** BAL *does* under-enumerate when the retreat driver is
the **`FAIL` primitive** rather than a failing continuation — `'ABC' ? POS(0) BAL $ OUTPUT FAIL` prints `A / done` where the
oracle prints `A / AB / ABC / done`. That is standing crosscheck witness `175_pat_bal_generator_retry`, and it is **NOT this
batch's mechanism**: swap `FAIL` for `RPOS(0)` and the same line agrees. Driver-is-`FAIL` is its own defect and its own row.

## 5. THE ONE-INGREDIENT LADDER (the whole classification in four rows, subject `'ab'`, anchored, stored)

```
(ANY('abc') | BAL)             orc=match  m3=match    <- generator directly in the outer arm: RE-ENTERABLE
(ANY('abc') | (BAL))           orc=match  m3=match    <- bare parens are inert
(ANY('abc') | (BAL | ''))      orc=match  m3=nomatch  <- ONE alternation deeper: REFUSED
(ANY('abc') | ('ab' | ''))     orc=match  m3=match    <- same nesting, DETERMINISTIC arm: fine
```
**The refusal is not about depth and not about BAL — it is about a retreat that must cross an `ALTERNATE` boundary to reach a
generator that still has alternatives to offer.** Substituting `ARB` for `BAL` in row 3 does not wrong-answer, it **hangs**,
which is the D-1/D-2 boundary showing up inside a single ablation.

## 5b. ⭐⭐⭐ THE CLASS ALREADY HAS A NAMED, STANDING CORPUS WITNESS — AND IT CRASHES

The fuzzer did not find a new class; it **rediscovered one the corpus already names and already grades RED in the standing
fail-set**. `corpus/crosscheck/patterns/160_pat_alt_inner_gen_resume.sno` is one line:

```
 'aXb' ? ('a' ARB . V | 'q') 'b'          expected: V=[X]
```

An alternation whose arm 1 holds a generator (`ARB`) that must EXTEND after the continuation `'b'` fails — **class D-2 exactly,
and written INLINE**, which independently corroborates §3's finding that this half is broken on the statement path and not only
in the blob. ⛔ **It SIGSEGVs — rc=139, stable 6/6 in m3 and core-dumping in m4 too.** It is already carried in the board's
standing fail-set (`FAIL-M3` + `FAIL`), so **this class is worth board points by name, not just fuzz witnesses**: curing D-2
should turn `160_pat_alt_inner_gen_resume` green in both modes, and that is the cheapest available proof that a candidate cure
is real. ⛔ Do NOT bundle `175_pat_bal_generator_retry` with it — measured a different mechanism (§4).

## 6. TWO FINDS OUTSIDE THIS ROW'S FRAME (reported, not chased — no row claimed)

1. ⛔ **A LEGAL INLINE PATTERN IS NONDETERMINISTIC THREE WAYS, IN BOTH MODES.** `'aa a' ((BREAKX('abc') | FENCE('a'))) $ v1
   RPOS(0)` written inline returns `match`, `[ZHP] heap exhausted`, or SIGSEGV **from the same unmodified binary across
   consecutive runs** (12 runs, m3 and m4 alike). ⭐ **THIS IS A HARNESS HAZARD BEFORE IT IS A DEFECT** — a single-run board row
   on this shape is an arbitrary draw, exactly the class seat6 recorded at s186 for the OR family. It was caught here only
   because every verdict in this rung was re-run for stability; the five checked-in witnesses are **stable 6/6** and the two D-1
   inline controls **stable 8/8**, so the classification above is not resting on a draw.
2. **The inline forms of `fz_diff_08` and `fz_diff_20` hang (rc=124) and SIGSEGV (rc=139) respectively.** Reduced witnesses are
   checked in as the `fzr_*` D-2 rows; the hang is a candidate face of `fuzz-hang-batch` and the SIGSEGV of `fuzz-segv-batch`,
   but both are stored-vs-inline twins of THIS batch's shapes and neither is claimed here.

## 7. WITNESSES CHECKED IN (`corpus/probe/fuzz/`, live-oracle `.ref`s, checked in RED per law 0d)

**5 RED, and 7 GREEN CONTROLS — one control per removed ingredient**, because a passing sibling with one ingredient removed is
worth more than a trace (RULES ASM-DIFF-FIRST):

| RED | its GREEN control(s) | ingredient the control removes |
|---|---|---|
| `fzr_07_breakx_alt_fence` | `fzr_07_control_lit_arm1` · `fzr_07_control_lit_arm2` | generator in arm 1 · FENCE in arm 2 |
| `fzr_08_alt_nested_bal` | `fzr_08_control_unnested` | the inner alternation around the generator |
| `fzr_13_alt_of_arbno` | `fzr_13_control_arm1_alone` | the alternation (arm 1 passes alone) |
| `fzr_20_alt_arm_bal_extend` | `fzr_20_control_no_alt` | the alternation (the capture was already inert) |
| `fzr_22_nested_arbno_not_first` | `fzr_22_control_single_arbno` · `fzr_22_control_first_elem` | one ARBNO level · the preceding element |

## 8. WHAT THE NEXT SEAT SHOULD DO WITH THIS

- **D-1 (`fz_diff_13`, `fz_diff_22`) is NOT new work.** Fold into `blob-resume-refusals`; its s183 FINDING already names the root
  (`ALTERNATE` has no seam tier) and already measured the row's implied cure (`SCRIP_RSEAL_OFF`) **inert**. Two more witnesses
  for that row, no more.
- **D-2 (`fz_diff_07`, `fz_diff_08`, `fz_diff_20`) is the real find** and wants its own row: *a generator's implicit alternatives
  and an enclosing `ALTERNATE`'s arm dispatch do not compose*, on **both** the blob and the statement path. The statement path is
  the one to fix first — it crashes, and it is the path any future `sno_pat_inline_ok` widening would route these shapes onto.
- ⛔ **Do not "fix" this by admitting BAL/FENCE/captures to `sno_pat_inline_ok`.** Measured: that trades 3 wrong answers for
  2 crashes and a nondeterministic draw.

## 9. GATES

`make pristine` EXIT=0 before verdicts · corpus board on the pristine tree **m3 332/5 · m4 325/11 · SKIP 1 (337)** — seat4's
s188 numbers exactly, **fail-set identical by name** (no compiler
file touched, and `test_corpus_snobol4.sh` enumerates `crosscheck` + `beauty_suite` + `demo` only — it never reaches `probe/`,
so this rung is a no-op there by construction) · ⛔ the SNOBOL4 **scorecard was NOT run**: it executes `corpus/programs/lon/`
through `run_one`, which RULES.md forbids outright until the harness is taught to skip that suite.
