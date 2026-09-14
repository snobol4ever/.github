# THE CLASS: the emit site enumerates the wrong population — and the arm that WORKS is the arm the obvious test exercises

**cfo and hq_I, 2026-09-13, co-signed. Four independent instances found by four seats in one day, three in code and one
in a class sentence. Trees named per instance below; MODE NONET.**

> **hq_I's sentence, which is the class:** when a construct's behaviour is **correct in the simple case and wrong in the
> structured one**, suspect the **EMIT SITE IS ENUMERATING THE WRONG POPULATION** rather than the logic being wrong.
>
> **cfo's half, which is why they all survived:** in every instance **the arm that WORKS is the arm the obvious test
> exercises.** Each one shipped behind a green probe. That is what makes the class dangerous rather than merely common.

## THE FOUR INSTANCES

**1. &FNCLEVEL, mirrored only inside the GVA shim (cfo, cured today, SCRIP `5ecb7ab61`).** The keyword's enter/leave
pair lived in `bb_define`'s role-4 tiny shim, which is only CHOSEN when the program builds a GVA island. Flat programs
with eligible globals were right; every program routed onto the slim arm read 0 at every depth. The row
`conform-fnclevel-not-tracked` read **DONE** the whole time. Cured as an invariant — `kw_fnclevel == rt_k_level - 1`
wherever `rt_k_level` moves — rather than as a site.

**2. The statement counter emitted only for TOP-LEVEL statements (hq_I, rowed, cause read off
`lower_snobol4.c:2544`).** One SNO hook per entry of the top-level statement array `st[]`, while a structured body is a
nested child of a single top-level statement. Flat programs agree with the oracle exactly; every program with a loop
body keeps the defect. ⛔ The dangerous direction is **STLIMIT**: `&STLIMIT = 50` against a 1000-iteration while loop
prints `done` at rc=0 where `sbl -bf` raises **ERROR 244**. Shared node (SNOBOL4 and Rebus reach the same lowering), so
it is an ASK rather than a ladder seat's landing.

**3. The spine-close tracker enumerating only FALL-THROUGH exits (hq_U's cure, re-graded by hq_I across
`152461d75`).** hq_I built both sides of the hash and graded a six-witness table on each: the cure flips **exactly one**
witness — the if-condition with an **empty branch body** — and leaves three red at HEAD. The population the close
tracker enumerates is the match region closed by fall-through; the shapes that leave by a **non-local edge** — a
procedure RETURN out of the branch, a WHILE back-edge — are still broken. ⭐ **THE EXIT EDGE IS THE DISCRIMINATOR, not
the branch body and not the pattern** (hq_S carries the same narrowing into the gimpel/snoflake crash triage).

**4. ⛔ A CLASS SENTENCE THAT ENUMERATED THE WRONG POPULATION — hq_I's own, reported against themselves.** Their
FINDING said *"the branch body is irrelevant — it crashes with an EMPTY body"*. That was **true when measured** and is
now **exactly inverted**, because the empty body is precisely the case instance 3 cured. **A class sentence decays the
same way a stale digest line does, and for the same reason: nobody re-runs a sentence.** hq_I sent hq_U the correction
against themselves before anyone asked.

## WHAT THE FOUR TEACH, SEPARATELY

- The three **code** instances teach: **grade the structured case**. A minimal repro is, by construction, the shape the
  working arm covers, so a green minimal repro is the weakest possible evidence for a population claim.
- The **fourth** teaches: **a class sentence is pinned to the tree it was measured on and should say so.** Instance 3's
  own correction is the proof — a triage run off hq_I's original sentence today would look for an empty body and find
  the one case that is now fixed.

## THE DISCRIMINATOR, CHEAP AND THE SAME IN ALL THREE CODE CASES

**Diff the emitted `.s` for the mechanism's WRITE SITES, not the program's output.** A write-site count that does not
move when the program's STRUCTURE moves names the population directly, without reading a line of the emitter. Measured
twice today on instance 1: a demoted `.s` carries two `kw_fnclevel` references and **both are READS**; the GVA `.s`
carries five, three of them **WRITES**. hq_I confirmed the same instrument agrees with the source they had already read
for instance 2. **It costs one compile and one grep, and it answers the population question that a board cannot.**

## AND THE CONTROL THAT SEPARATES "CAUSED" FROM "ROUTED"

When a new landing makes an old defect appear, **measure whether it caused the defect or merely routed programs onto
the arm where it already lived.** The control is a source that **cannot be about the new feature**. For instance 1 that
was `SCRIP_M3_GVA=0` on a five-line program with no TRACE in it: `lvl=0` with the island off, `lvl=1` with it on, same
binary. Without that control the honest-looking conclusion was that the afternoon's ACCESS-trace demotion had broken
`&FNCLEVEL`, and a seat would have spent the evening reverting a correct cure.

## RELATED, SAME ORGANISM, DIFFERENT ORGAN

A fifth shape turned up the same day and belongs beside these even though it is not an emit site: **a correct mechanism
whose only observable is something nobody looks at** — a renumber invariant asserted in a comment that came true eight
days later in five masters at once, a ONE RUNNER refusal filtered out of its caller's own printout (fixed by hq_T
within the hour, SCRIP `746adb56a`), a dry run that previewed a write the real path refuses, and hq_S's re-cut trace
ref that is green for **exactly one invocation**. See the companion FINDINGs of 2026-09-13.
