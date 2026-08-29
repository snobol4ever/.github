# FINDING — family-5 `:incl`/`:src`: SPLIT ruling (hq_C, 2026-08-29, supersedes this finding's own first draft)

**seat02 draft · hq_C ruling · 2026-08-29 · row `family5-attr-adjudication-needed` · SCRIP HEAD `fef0c2fd`**

⚠️ **This finding's first version lumped `:incl` and `:src` together and called both "a bug," reasoning
from Snocone's `stmt_new()`-synthesized block-body statements never having been exercised by either
introducing commit. While pointed the right direction, it was less precise than the ruling below, which
landed in the task file (`family5-attr-adjudication-needed.task.md`) while this session was still
drafting this finding. hq_C's ruling is authoritative; this file is rewritten to record it, with the
original archaeology (the two introducing commits) kept as corroborating background. Do not cite the
"both attributes, Snocone-specific" framing this file used to carry — it is retracted.**

## The question

`corpus/tests/snocone/parser.xfail` carried 29 identical XFAIL reason blocks (family 5) stating that
whether the live compiler's `TT_ATTR` `:incl`/`:src` attributes on Snocone block-body statements are
deliberate or a bug "requires the attr-introduction commit, which is git archaeology reserved to hq_C."

## THE RULING — hq_C, 2026-08-29: SPLIT. `:src` DELIBERATE · `:incl` A BUG

The question as posed conflates two attributes with two different provenances; ruling them together
would be wrong either way.

**The two introducing commits:**
- **`:src`**, introduced by `806508fd` ("SRC-COMMENT: emit each SNOBOL4 statement's verbatim source as
  a comment heading its BB chain (Lon directive)") — attaches the statement's sliced source text to the
  AST. Per-statement source capture is exactly what this commit was built to do; nothing about a block
  body exempts it. **Deliberate.**
- **`:incl`**, introduced by `764752c6` ("perf-per-statement-loc-emission: DWARF .file/.loc per
  statement... honest about `-INCLUDE`") — adds the attribute at exactly one site, on the `!ssrc`
  branch (`stmt_src_slice()` returned NULL): `sa_add(node, attr_int(":incl", 1))`, paired with fallback
  text `"<stmt N, line M: source not in main file (INCLUDE)>"`.

**The defect:** `806508fd`'s own "Known limits" already documented that the `!ssrc` branch has *more
than one cause* — `"second statement on a ';' line and included-file statements are guarded to
silence."` `764752c6` labelled the *entire shared branch* `:incl`, so every non-INCLUDE cause of a
failed slice now falsely asserts INCLUDE provenance, dragging the false `:src` `(INCLUDE)` fallback
text along with it (the same two lines set both).

**Measured live** (re-measured, not inherited) on a Snocone file containing zero `-INCLUDE`: every
block-body statement in both `.sc` and `.sno` emits `(TT_ATTR :incl (TT_QLIT "1"))` plus the false
`(INCLUDE)` `:src` text; top-level statements carry neither attribute at all, in either language.
Reproduced at both single-line and multi-line block layouts, ruling out the `';'`-line limit as the sole
cause. Linenos are correct (not the lineno off-by-one `stmt-src-slice-bare-label-lineno-off-by-one-
false-include-attr` already cured — that row's own counter-finding, that closing it does not clear
family 5, was right).

**Structural shape:** a shared sink makes two different conditions print the same claim, and the label
names only one of them — the same shape as a same-day, unrelated finding
(`drive_unowned` reporting "no template" for both an unimplemented op and an implemented op's internal
guard refusal). A diagnostic reachable by more than one cause must name which one it observed.

**Consequence — do NOT promote:**
1. The 29 XFAILs stay red; `ast_xpass=0` is consistent with this ruling, not against it.
2. The compiler must be cured at the one site (`stmt_ast.c`'s `!ssrc` branch): distinguish *slice
   failed because the statement is genuinely from an included file* from *slice failed for any other
   reason*. Only the former may set `:incl` or the `(INCLUDE)` text; the other causes stay silent, which
   is what `806508fd` said they were "guarded to silence" for in the first place.
3. Only then are the 29 refs re-derived from `--dump-ast`, diff-reviewed, and the XFAILs cleared —
   because the compiler stopped emitting the false attribute, not because the refs were amended to
   accept it.
4. `:src` itself stays; only its false `(INCLUDE)` fallback text goes with the same fix.

## Row ownership

This row (`family5-attr-adjudication-needed`) was claimed by seat02; hq_C's claim attempt was refused
for that reason, so the ruling was posted directly into the task file instead. hq_C's own note: the
ruling is made; applying it (the `stmt_ast.c` cure, then the 29 refs' re-derivation) is seat-work and
stays with whoever holds this claim. Not yet done as of this finding — flagged in the task file's
ledger for the next step, since it touches `stmt_ast.c`, a shared-node file reached by every frontend
that goes through `stmt_to_ast()`, and needs the corresponding cross-language regression pass before
it can be called a landed cure.

## Background: the archaeology that led here (seat02, kept for corroboration)

Independently, before hq_C's ruling landed, this session found the same two commits by `git log -S
':incl'` / `-S':src' -- src/driver/stmt_ast.c` and confirmed Snocone's grammar
(`src/frontend/snocone/snocone_parse.y`) calls `stmt_new()` directly (same as Prolog's and Rebus's
lowerers) to synthesize `STMT_t` nodes for desugared control flow (e.g. `sc_for_head_new_pst`,
`snocone_parse.y:545-616`), each `calloc`-zeroed (`scrip_cc.h:42`) and stamped
`s->lineno = st->ctx ? st->ctx->line : 0`. This is real and probably still a contributing case under
the `!ssrc` branch, but hq_C's live measurement shows the false attribute is not specific to
synthesized control-flow statements — it fires on *every* block-body statement, including a plain
assignment inside a single-line `if`. The synthesis mechanism is consistent with hq_C's ruling; it is
not the whole, or even the main, story.

`prolog_lower.c` and `rebus_lower.c` also call `stmt_new()` directly for synthesized statements and
would hit the same `!ssrc` branch. Not investigated here — flagged in case either language's own
AST-provenance fixtures ever start caring about `:incl`/`:src`.
