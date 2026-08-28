# FINDING — an Icon board had three independent reasons it could not measure; each alone was fatal, and they were indistinguishable from outside

**Who/when:** hq_C, 2026-08-28, found while collecting the Icon control arm for row
`bb-label-prefix-pascal-suite-regression` under SHARED-NODE VERDICT SCOPE. Cure: SCRIP `43fa94a0`.

## The symptom was a scalar

```
$ bash scripts/test_corpus_icon_parser.sh
ERROR: icon_parser compile failed
rc=2
```

**Refusing was correct** — a test that cannot measure must refuse, never skip-as-success. But it had
been refusing *instead of grading*, and nothing anywhere said for how long. Icon is this seat's #2
correctness language.

## Three faults, any one of which alone produces exactly that line

1. **Bare `icont`.** Not on `PATH` here — the oracle is at `/home/resources/icon-master/bin/icont`, and
   `lib_oracle_flags.sh::icont_bin()` exists precisely so nobody re-derives it. Its own comment reads
   *"Do not hand-assemble a path or fall back to bare `icont` on PATH."* This caller predates the
   accessor and never adopted it. Same family as the seat who ran `command -v icont`, got nothing, and
   wrote *"no Icon oracle exists"* into a digest.
2. **A path one level above the seat root.** `PARSER_SRC="$REPO_ROOT/../corpus/..."` with `REPO_ROOT`
   already **being** the seat root, resolving to `/home/corpus`. ⛔ **This could never have matched, on
   any tree, ever** — it was not a path that went stale, it was a path that was never right.
3. **The sources moved** to `corpus/demo/icon/demo/` in the 2026-08-24 corpus re-grid, so even the
   *intended* `corpus/scrip/` path is dead now. Same re-grid, same silent-nothing shape that `dcbabbf9`
   cured in `util_regen_demo_s_artifacts.sh` (*"had been silently regenerating NOTHING since the s272
   corpus re-grid"*).

## ⭐ The transferable part

**Fault (2) means this board was broken BEFORE the re-grid that broke it again.** Fixing the re-grid
damage alone — the obvious, well-motivated, correctly-diagnosed repair, the one a seat arrives at by
reading the commit history — would have left the board still printing the same `rc=2` and still looking
like a single unfixed bug.

**A refusal is a scalar; the thing behind it need not be.** Three independent faults collapse to one
indistinguishable symptom, and the natural debugging loop (fix the cause you found, re-run, still red,
conclude your fix was wrong) actively misleads: it reads as *"my diagnosis was incorrect"* when the truth
is *"my diagnosis was correct and incomplete."* The cheap defence is to keep going after the first cure
until the instrument **measures**, rather than until the symptom changes — and to treat an unchanged
symptom after a well-verified fix as evidence of *another* fault, not of a bad fix.

This is the same shape as the `-O2` framing recorded in `GOAL-HQ-COMPLETE.md` (`-O1` fails identically,
so the boundary was never where the row name said) and as the m1-bisect probe that would have marked
every commit BAD: **a true observation with an unexamined multiplicity behind it.**

## The cure and its proof

`icont_bin()` for the oracle · `icn_src()` resolves each source by search under `$S4E/corpus` and
**refuses** if absent · the default directory list admits only directories that exist (a dead entry
silently shrank the denominator, because `find`'s error was swallowed by `2>/dev/null`).

| | before | after |
|---|---|---|
| files graded | **0** (rc=2) | **476** |
| parser | — | pass=476 empty=0 crash=0 |
| recognizer | — | pass=268 empty=208 crash=0 |
| exit | rc=2 | **rc=0 PASS** |

⭐ **Negative-tested both arms, because the whole point of the change is that it can still say no:**
sources absent → rc=2 `ICON SOURCE UNRESOLVABLE`; oracle absent (shadowed lib) → rc=2, and it does
**not** fall back to bare `icont`. A repair that only proves the green direction would have re-created
the `make test` trap in a new place.

Icon watermark unmoved (this touches no compiler source): **PASS=251 FAIL=15 BADEXIT=1 MISSING=0
TOTAL=297**, equal to the control recorded in `840d05f7`.

## What is still owed

The recognizer's **208 empty** results are ungraded and unexplained — the board counts them but nothing
says whether an empty parse is a defect or a legitimate outcome for those inputs. That is a real open
question this cure surfaced and did not answer; it is not a regression, it was simply invisible while the
board graded nothing.
