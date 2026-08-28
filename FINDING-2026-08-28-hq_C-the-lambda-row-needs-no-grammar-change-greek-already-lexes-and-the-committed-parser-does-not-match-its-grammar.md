# FINDING — the lambda row needs NO grammar change, Greek identifiers ALREADY lex, and (the trap) the committed `snobol4.tab.c` does not correspond to `snobol4.y`

**Seat:** hq_C · **Date:** 2026-08-28 · **Row:** `lang-lambda-pattern-primitives` (rank 1, hq_C leads parser/lower/semantics) · **Tree:** SCRIP `69178c73` · **Status:** reconnaissance only — the primitive is NOT implemented and was deliberately not half-landed.

Four of the routed design's assumptions were checked against the tree rather than reasoned about. Three are wrong in our favour; the fourth is a trap that the third one arms.

## 1. ✅ NO GRAMMAR CHANGE IS NEEDED — the assignment form already parses

The design admits statement-style assignment "INSIDE the lambda parens only", which reads as a grammar change. Measured: it is **already admitted**.

```
        X 'a' lambda(N = 1) 'b'      -> parses clean; fails only at RUN time, Error 5 "Undefined function"
--dump-ast                           -> (TT_FNC lambda (TT_ASSIGN (TT_VAR N) (TT_ILIT 1)))
```
`fnc_args` already accepts an assignment expression, and the AST is exactly the shape a lowerer wants. **So the whole primitive can be recognised BY NAME in `lower_snobol4.c`** — which is also the *correct* place: language identity is permitted to stop at the frontend/lower boundary and nowhere after it, so recognising `lambda`/`LAMBDA`/`λ`/`Λ` there introduces no `LANG_*` leakage.

## 2. ✅ GREEK IDENTIFIERS ALREADY LEX — the lexer work is done

`λ1 = 'greek-ok'` compiles and runs today (`unicode_alpha_ranges.h` is wired). Lon's "I do want to use greek letters in the SNOBOL4 source" is already satisfied at the lexer level. ⭐ And it hands the row a freebie: `λ` and `Λ` are *distinct identifiers already*, so the conditional/immediate discrimination costs nothing in the Greek spelling, exactly as `lambda`/`LAMBDA` costs nothing in the Latin one.

## 3. ✅ bison 3.8.2 AND flex ARE AVAILABLE — a digest comment is stale

They live at `/tmp/flexbison/root/usr/bin/` (staged by another seat this session). `src/frontend/snobol4/Makefile:7` states "they are never installed in the session env"; that is no longer true, and the Makefile's own conditional rule **auto-regenerates the moment `.y` is touched** with that directory on PATH. Not needed for lambda per §1 — but it is what makes §4 dangerous instead of merely untidy.

## 4. ⛔⛔ THE COMMITTED PARSER DOES NOT CORRESPOND TO THE COMMITTED GRAMMAR

Regenerating `snobol4.tab.c` from the current `snobol4.y` produces **identical parse tables** — the entire non-`#line` diff is 48 lines and contains no `yytable`/`yycheck`/`yypact` change, so the grammar itself is not in question. What differs:

* the committed file carries two hand-added `/*----*/` house-style separators that the grammar does not produce;
* its `yyrline` table is offset by **+4** throughout.

Both say the same thing: **the checked-in generated file was hand-edited after generation.** Anyone who touches `.y` with bison on PATH silently reverts those edits, and the reversion is invisible because the parser still works perfectly — the tables are the same.

⭐ **The fix is prevention, not repair: put the separators in the `.y` PROLOGUE, so generation reproduces them and regeneration becomes idempotent.**

⛔ **I did NOT apply it, and the reason is the more useful half of this finding.** Editing `.y` re-dates it against `snobol4.tab.c`, and the Makefile rule deliberately **aborts** when `.y` is newer and bison is absent — which is still every seat that does not have `/tmp/flexbison` on PATH. Fixing a cosmetic desync would have broken those builds outright. *A repair whose blast radius exceeds the defect is not a repair.* It belongs with whoever schedules grammar work, together with a toolchain decision.

## 5. WHERE LAMBDA HOOKS — it is bigger than "a template", and a naive witness will hide that

Pattern boxes lower to `IR_CALL` with a `SNO$PB*` selector (`SNO$PB0` nullary · `SNO$PBN` int-arg · `SNO$PBC` capture · `SNO$PARB` · `SNO$PFEN`). But a **runtime-built** pattern is a `dtp_rcp_t` node tree that `dtp_rcp_tree()` converts back into a `tree_t` before lowering. So a lambda inside a stored pattern — `P = lambda(...)` then `X ? P` — must survive that round trip, not merely the inline-in-a-match-statement case.

⛔ **Consequence for the row's witness:** an implementation handling only the inline case passes a naive witness and fails the stored-pattern shape. `k40_lambda_primitives.sno` must exercise **both**, on top of the four behaviours the DONE-WHEN already names.

## 6. ⭐ THE COST CENTRE THE ROW TARGETS IS CONFIRMED, IN ONE LINE OF THE LOWERER

`TT_DEFER` lowers to `SNO$MKEXPR` carrying the expression as a **source string** (`sno_expr_collect`), resolved and evaluated **by name** at match time (`lower_snobol4.c:269-276`). That is mechanism #3's callout ceremony, and it is precisely what an inline lambda subgraph replaces. The row's premise is sound and now has a named line to point at.

## 7. THE NAMING-SWAP TRAP IS REAL — AND THE REFERENCE *CODE* SETTLES IT

`_backend_pure.py`'s class comments do swap the names, as the task warned. The **behaviour** does not: `class Λ` evaluates immediately (`eval`, epsilon on truthy, fail otherwise) and `class λ` appends to `cstack`, yields epsilon, and **pops on backtrack**. That is Lon's convention exactly — lowercase CONDITIONAL, uppercase IMMEDIATE. **Implement to the reference's code, never to its comments**, and the trap disarms itself.
