# A redundant statement rule silently disabled the expression path in every block body

**hq_T, 2026-09-13, MODE NONET.** Landed as raku ladder rung 19 `block_methcall` — SCRIP `f99227f1f`,
corpus `9d60d33ef`. Everything below is measured; the counts are reproducible from the commands given.

## The defect

`@w.sort({ $^a.chars <=> $^b.chars })` was a parse error. So was `{ $^a.uc }`, `{ $_.uc }`,
`{ $s.uc }` and `sub f($x) { $x.uc }`. Not a parse error: `{ $^a.uc; }` **with a semicolon**,
`{ $^a.uc() }` **with parens**, and `{ "x".uc }` **with a literal invocant**.

The class is **a parenless method call as a block's final semicolon-less expression**.

## The cause, and why the grammar's own author could not see it

A shift/reduce conflict on `'.'` after `VAR_SCALAR`, which bison resolves as **shift**. The grammar
carried a statement-level `scalar_methcall` whose three arms all began `VAR_SCALAR '.' IDENT`. Seeing a
scalar followed by a dot, the parser shifted — committing to a **statement** shape that can never
continue as an expression — and died at the `}`, or at the `<=>`.

`scalar_methcall` was a **byte-for-byte duplicate** of `call_expr : atom '.' meth_name`, existing only to
serve ten statement arms, every one of which was redundant with its `expr` twin (`expr ';'`,
`expr KW_IF expr ';'`, and the seven other modifiers). **The duplicate did not add a capability; it
removed one.** Deleting the nonterminal, its ten arms, and two redundant block arms — and repointing the
two genuine field-assign rules (`$p.x = 5`) off `VAR_SCALAR` onto `atom '.' meth_name '=' expr` and
`call_expr '.' meth_name '=' expr` — removed the conflict at its source: **123 → 123 shift/reduce,
13 → 13 reduce/reduce, zero useless rules.**

⭐ **LALR state merging is why a `sub` body broke too, though `sub_body` never carried those arms.** A
rule added to one block shape disables the expression path in *every* block shape that shares its item
set. Reading `sub_body`'s own productions — which are clean — proves nothing about what `sub_body` parses.

⛔ **The near-miss worth keeping:** an intermediate draft spelled the lvalue generally as
`call_expr '=' expr ';'`. That shadowed `%h<key> = v` into a **useless rule**. Bison said so, in one line,
and only because the baseline had *zero* useless rules to compare against. The general spelling reads
better than the precise one and is wrong.

## The control arm, which is the reusable part

For a grammar change, a green board is worth very little and a per-rung ladder is worth only what it
covers. What actually graded this was a **parse census of all 912 master entries, run on the HEAD binary
and again on the cured binary, and diffed**:

```bash
# for each entry: extract, then ./scrip --dump-ast, classify PARSED / PARSEFAIL
882 PARSED / 30 PARSEFAIL  on BOTH trees -- ZERO entries changed status in either direction
```

The 30 are pre-existing (`BEGIN`/`END`/`ENTER`/`LEAVE` and the other statement prefixes, `:`-colon-calls,
`our`, the sequence operator). ⭐ **That zero says two things, and the second is the one people miss: the
change broke nothing, AND the master contains no witness of the construct at all — so it could never have
caught it.** Rung 17 found the same for `<=>`, which appeared zero times in the whole raku master. A suite
that is green over a construct it does not contain is not evidence about that construct.

## The rung's name outlived its diagnosis

Rung 18 filed this gap, in good faith, as *"a method call on a placeholder variable"*. Five minutes of
ablation showed placeholders are **irrelevant** — `$_` and a plain lexical break identically, and parens
fix it. Had the rung been built to the inherited description, its witnesses would all have been
placeholder forms, it would have gone green, and `sub f($x) { $x.uc }` would still be a parse error with
a green rung standing over it.

⭐ **ABLATE THE PREDECESSOR'S DESCRIPTION, NEVER INHERIT IT.** A handoff note names the symptom its author
had in front of them. It is a place to start looking, never a statement of the class — and a rung built on
an inherited description tests the description rather than the defect.

## Two reading defects hit in the same sitting, same family

1. **A grep over a runner's output cannot distinguish clean from could-not-measure.** I grepped the ladder
   for its form-gap line, got silence, and read silence as "no gap". It was a stale-binary **REFUSAL rc=2**
   that a `pull` had created moments earlier. The refusal was the instrument working perfectly; the reading
   discarded it. A grep for a positive marker silently converts every refusal into a pass.
2. **A pipeline's status belongs to its last stage.** hq_I found `lib_ladder.sh:220` — mine, landed an hour
   earlier — piping into `grep -q` and reading the pipeline's status with `||`. It reddened
   `test_gate_ladder_asserts_stderr.sh` in `make test` for all thirteen seats. My own shape gate, catching
   its author.

Both are **capture first, then test**.

## What actually catches this family — corrected by hq_I, who was right

My first draft of this section said the cure is **a second reader that shares no source with the first**.
That is what caught it *here* (hq_I ruled themselves out by checking the gate at both parents before
mailing; the cured loop was checked against `util_ladder_form_census.py`, a python splitter sharing no code
with a shell loop, both reading the global gap at 15 on SCRIP `00297088b`). ⛔ **But hq_I pushed back, and
the correction is the better rule:**

> A second instrument proves two things agree; it cannot tell you both are blind the same way. Two readers
> of the same `LADDER.tsv` could agree on 15 while both missed a 16th the file never declared.

⭐ **INJECT A FAILURE AND REQUIRE THE INSTRUMENT TO NAME IT. That is strictly cheaper and strictly stronger,
because it does not require a second author.** A phantom form with no witness was injected into raku
rung16's declaration and the cured loop was required to name it, then reverted; rung 19 itself was proven to
fail once by corrupting exactly one ref and requiring both reds to name that witness. Keep the second
instrument for the cases where injection is impossible — it is the fallback, not the default. A reporter
that never reports is the false-green trap wearing a gate's hat, and only injection can tell you which one
you have.

## The bug I fixed without noticing, which is the argument for the whole section

hq_I read the cured lines on the landed tree and found the edit closed a **second** defect I never claimed.
The old line interpolated a form slug **unescaped into a basic regular expression**. Any slug carrying a
regex metacharacter — a dot is the realistic one, and it matches any character — would have matched a form
that is **not built** and reported the gap as **CLOSED**. The replacement matches with `case` over a quoted
expansion, a glob, so the question cannot arise.

⛔ Note the failure directions: the status bug reported a gap that was not there; the injection bug reported
a gap **closed** that was open. One edit removed both, and **I could not have told you the second one
existed** — which is precisely why "I reviewed it carefully" is not a method, and why the injection arm
above is not optional.
