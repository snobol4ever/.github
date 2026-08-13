# FINDING — Manual Ch.9 pp.121-123, read this session, confirms (does not merely support) that "one frame
# per recursive activation" is the correct SEMANTIC model for self-referential ARBNO/DEFER, not only an
# offset-hazard fix. Follow-up to `FINDING-2026-08-13-...-SAME-MECHANISM-DIFFERENT-MOTIVE.md` (B-12), whose
# own text flags that the manual PDF was unavailable when it was written. No code changed.

**Author:** Claude Sonnet 5 (WIRES seat, this session) · **Date:** 2026-08-13
**Repos at read time:** SCRIP `5547de99` · `.github` `c39208cb` (post B-12 finding + prune)
**Status:** diagnostic / cross-referential, same as the finding it follows up. Does not implement EARN-4 or
the W-7 fix — see "Who should act on this" below; that question is explicitly not this seat's to answer alone.

## What was asked for

B-12's finding (predecessor, this file's header) named its own gap plainly: *"Session-start reading (manual
Ch.9 pp.121-123) not yet done — the PDF was not available this session; do not treat the manual citations
... as re-verified."* It asked whoever picks this up next to close that gap "specifically to confirm what
'one frame per recursive activation' must guarantee for a self-referential `*group`."

This seat had the manual available and read pp.121-123 (`The ARBNO Function` / `Recursive Patterns`) as
part of ordinary session orientation, before either finding's content was known. Recording the confirmation
now while it's fresh, per that finding's own request.

## What the manual actually says (paraphrased, not quoted at length — pp.121-123)

- ARBNO's own retry semantics: shy, matches the null string first, and on each backtrack "supplies another
  instance of its argument pattern" — formally `("" | PAT | PAT PAT | PAT PAT PAT | ...)`. Each retry is
  described as a fresh instance of the argument pattern, not a mutation of a shared one.
- Recursive/self-referential patterns are built with the deferred-evaluation operator `*name`, which
  re-fetches its operand's current value at match time, on every use — including every retry. The manual's
  own worked example (`ITEM = SPAN(digits) | *LIST`, `LIST = "(" ITEM ARBNO("," ITEM) ")"`) is presented as
  the pattern analogue of a recursive function.
- Critically, the manual states outright that **SPITBOL "saves information on a stack during the pattern
  match process"** specifically for this case, and that heavily recursive patterns "can sometimes result in
  stack overflow" — the remedy offered is the `-s` command-line stack-size parameter, not a change to the
  matching semantics. It then gives a worked pair of examples establishing that a self-recursive arm
  (`*name` referencing its own pattern) must consume a subject character before recursing, or it plunges
  immediately: `EXPRESSION = *EXPRESSION | "(" TERM ")"` overflows on any input taking the first branch;
  `EXPRESSION = TERM | "(" *EXPRESSION ")"` does not, because `"("` is consumed first.

## Why this confirms, not just supports, the EARN-4 shape

The manual's own model of recursion here is genuine stack-based recursion — each self-referential
invocation via `*name` is described as a new instance, pushed and later popped, exactly the shape a
compiler would render as "each activation gets its own frame." This is stated as the *language's* execution
model (pattern-match stack, `-s` to size it), not as an implementation detail SCRIP is free to choose
differently. That means EARN-4's design — one frame established at α, the ARBNO control cell fixed at
`[rbp+K]`, a recursive self-reference getting its own α/frame rather than reusing the outer activation's
`[rsp+K]` — is not just an offset-hazard fix that happens to also avoid W-7's aliasing bug. It is the direct
structural translation of what the manual says recursive pattern matching *is*: independent activations on
a stack. A single shared `[rsp+K]` cell for two activations the language itself models as separate stack
entries was the wrong shape regardless of which bug exposed it first.

This does not by itself prove EARN-4 **as coded** clears the aliasing case — B-12's finding is right that
whether the implementation actually gives the recursive call a fresh `rbp` (vs. reusing the outer one) is
a code question, unchecked by either seat as of this finding. What this closes is the *semantic* question:
if EARN-4's implementation does establish a fresh frame per recursive activation, that is provably the
correct target, not merely a convenient side effect of solving RBP-EARN's offset problem. If it doesn't
(e.g. some code path reuses the outer `rbp`), that would now be checkable against a manual-backed
expectation rather than an inferred one.

## Also relevant to W-3 (this seat's live crash)

Same pages back the `zls2_mark`-fold argument for W-3 (Q7): if recursive/deferred pattern activations are
supposed to be independent per the manual's own stack model, a fixed `[rbp-56]` cell for `zls2_mark` shared
across a DEFER blob's activation and its enclosing graph is the same shape of bug as the ARBNO aliasing
case — a single address standing in for what should be two independent activations' state. Folding it into
the per-activation arena (W-4) rather than widening the depth accounting in place is the same fix pattern,
not a separate design.

## Who should act on this

Per B-12's finding: EARN-4 is RBP-EARN's rung; W-7's fix and this seat's W-3/W-4 consume it. This finding
adds manual grounding, not authorship — implementation should stay with whichever seat Lon names, per the
same in-chat coordination that finding already asked for. Recommend surfacing in chat now rather than
either seat opening EARN-4 independently.
