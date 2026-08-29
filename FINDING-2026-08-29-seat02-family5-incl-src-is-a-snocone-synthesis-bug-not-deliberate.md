# FINDING — family-5 `:incl`/`:src` on Snocone block-body statements is A BUG, not deliberate

**seat02 · 2026-08-29 · row `family5-attr-adjudication-needed` · SCRIP HEAD `fef0c2fd`**

## The question

`corpus/tests/snocone/parser.xfail` carries 29 identical XFAIL reason blocks (family 5) stating that
whether the live compiler's `TT_ATTR` `:incl`/`:src` attributes on Snocone block-body statements are
deliberate or a bug "requires the attr-introduction commit, which is git archaeology reserved to hq_C."
This finding is that archaeology and the ruling it was blocking.

## The two introducing commits

**`806508fd`** (2026-07-26, "SRC-COMMENT") introduced `:src` and `stmt_src_slice()`
(`src/driver/stmt_ast.c`). Purpose: attach each statement's verbatim source text as a comment, for
readability. The function slices `g_src_lines` (the PRIMARY input file's lines, set once via
`stmt_src_set_file()`) at `s->lineno`, then GUARDS the result: a labeled statement's line must start
with that literal label text; an unlabeled statement's line must start with whitespace. Failing either
guard, or any bound/blank/comment check, returns `NULL` — the commit message frames this as "so
`-INCLUDE`-originated statements get NO comment rather than a wrong one." The guards are a heuristic
side effect (does the sliced text look like real source), not a targeted "is this from an include" test.

**`764752c6`** (2026-08-28, "perf-per-statement-loc-emission") introduced `:incl`, reusing that same
`NULL` signal: *"`stmt_src_slice()` returning NULL is exactly 'not in the main file', now recorded as
`:incl`."* Its entire stated purpose is DWARF `.file`/`.loc` correctness for `-INCLUDE`d statements
(measured on `beauty.sno`: 599/1,068 `.loc` rows pointed past EOF before this fix). Both commits are
rigorous, deliberate, well-tested work — **for their stated target, which is SNOBOL4 `-INCLUDE`.**

Neither commit's message or boarded gates mentions Snocone. `764752c6`'s own board section measures
SNOBOL4 (exhaustively), Icon/Rebus/Raku/Prolog (smoke-level, to confirm non-interference), and
explicitly nothing about Snocone.

## What actually happens to Snocone

Snocone's grammar (`src/frontend/snocone/snocone_parse.y`) does not build a separate AST — it calls
`stmt_new()` directly (same as Prolog's and Rebus's lowerers do) to synthesize `STMT_t` nodes for
desugared structured control flow, e.g. `sc_for_head_new_pst` / the `for`/`while`/`break` machinery
(`snocone_parse.y:545-616`), each stamped `s->lineno = st->ctx ? st->ctx->line : 0`. `stmt_new()` is
`calloc(1, sizeof(STMT_t))` (`scrip_cc.h:42`) — a fresh synthesized statement's `label` is `NULL` unless
the grammar action sets one.

Concretely, family 5's `break_for` fixture is:
```
for (i = 0; LT(i, 10); i += 1) {
    break;
}
```
Desugaring `for`/`break` into SNOBOL4-shaped goto statements produces synthesized `STMT_t` nodes that
do not correspond 1:1 with a physical source line the way a plain top-level statement does (multiple
synthesized statements can share one `lineno`; an unlabeled synthesized statement's "line" in the raw
`.sc` text is Snocone surface syntax like `for (...) {`, not the goto/label shape `stmt_src_slice`
expects). These synthesized statements fall through `stmt_src_slice`'s guards and return `NULL` for the
same *mechanical* reason a genuine `-INCLUDE` statement does — but for an unrelated cause: they are
main-file statements that don't literally appear as source text at their stamped line, not statements
from another file.

## The ruling: A BUG

The `:incl`/`:src` mechanism is not misdesigned for its actual target (SNOBOL4 `-INCLUDE`), and the
NULL-return path it rides is legitimately shared machinery, not a hack. But nobody ever decided that
Snocone's compiler-synthesized block-body control-flow statements should be attributed `:incl` — both
introducing commits' stated intent and entire test matrix are scoped to genuine cross-file inclusion,
and neither was ever run against Snocone. The attribute's presence on these nodes is an unvalidated,
unintended side effect of two SNOBOL4-only mechanisms sharing a signal (`stmt_src_slice() == NULL`)
that means different things for a synthesized statement than for an included one. `:incl` on these
nodes actively misleads a consumer (e.g. DWARF routing them to the dishonest-by-a-different-axis
bucket `"<included>"`, when they are neither included nor safely attributable to a single main-file
line).

**Per the task's branch instructions:** the 29 fixture refs are right; the compiler must stop emitting
`:incl`/`:src` on statements it synthesizes rather than parses verbatim from the primary input. This
finding does not prescribe the mechanism (a synthesized-statement flag distinct from the NULL-from-
`stmt_src_slice` signal is the obvious shape, but that decision and its implementation belong to
whoever holds `snocone-parser-fixture-ast-drift-ruling`, not to this row).

## Scope note

`prolog_lower.c` and `rebus_lower.c` also call `stmt_new()` directly for synthesized statements and
would hit the same NULL-return path. Not investigated here (out of scope for this row) — flagging in
case either language's own AST-provenance fixtures ever start caring about `:incl`/`:src`.
