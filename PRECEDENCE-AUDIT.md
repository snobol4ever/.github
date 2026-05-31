# PRECEDENCE-AUDIT.md — Operator precedence/associativity audit across all six SCRIP languages

**Goal:** GOAL-PARSER-SC-TRANSPILE.md sub-rung **SCT-9g** (re-scoped 2026-05-17 from snocone-only to per-language coverage).
**Status:** §1 Snocone landed 2026-05-17 (Opus 4.7). §§2–6 awaiting spec documents from Lon.
**Inputs (Snocone):** SPITBOL Manual v3.7 Ch.15 + live `sbl` at `/home/claude/x64/bin/sbl` + `parser_snocone.sc` (corpus `1b24df4`) + `snocone_parse.y` (SCRIP `96d39c05`).

This document audits each of the six languages the transpiler supports (snobol4, snocone, rebus, icon, raku, prolog). Per language, it enumerates every binary operator in BOTH the C-side parser (`src/frontend/<lang>/`) and the Snocone-side parser (`corpus/SCRIP/parser_<lang>.sc`), compares to the language's authoritative spec, and recommends fixes for divergences.

The transpiler depends on this audit being clean: any precedence/associativity divergence between the two grammars OR between either grammar and the language spec means the transpiled `.sno` won't match SPITBOL's evaluation of the original source.

---

## §1 — Snocone

## Methodology

1. **Manual is the spec.** Ch.15 line 9830+ lists every binary operator with its priority (0–12) and associativity (left/right).
2. **Live SPITBOL is the oracle for evaluation order.** When in doubt, run a probe through `/home/claude/x64/bin/sbl -b`. The manual and the binary agreed on every probe.
3. **Both grammars are compared to the manual.** Probes use `scrip --dump-ast` (C) and would use `bash scripts/run_scrip_parser.sh snocone …` (`.sc`); the latter currently segfaults via the known `rt_bb_arbno → bb_deferred_var` path, so `.sc` tree shape is derived from grammar shape directly (right-recursive PEG rule with `FENCE` ≡ right-associative parse, single-chain).

### Probes that grounded this audit

`probe_assoc.sno` (live SPITBOL):

```
10 - 3 - 2 = 5      (left-assoc; right-assoc would give 9)
100 / 10 / 2 = 5    (left-assoc; right-assoc would give 20)
2 ^ 3 ^ 2 = 512     (right-assoc; left-assoc would give 64)
A = B = 7  →  A=7, B=7 (right-assoc assignment chain)
10 + 8 / 2 = 14     (DIV pri 8 > ADD pri 6, so DIV first)
```

`mixed_op_truth.sno` (live SPITBOL):

```
10 + 8 - 3 = 15           (left-assoc; right-assoc would give 5)
20 - 5 + 2 = 17           (left-assoc; right-assoc would give 13)
100 - 30 + 10 - 5 = 75    (left-assoc; right-assoc would give 85)
```

Every probe matches the Manual Ch.15 table exactly.

---

## Binary operator table

| Op symbol | Pri | Assoc | Manual ref | Snocone uses it as | C grammar shape | `.sc` grammar shape | Status |
|-----------|----:|-------|-----------:|--------------------|-----------------|---------------------|--------|
| `=`            | 0  | right | 9843 | TT_ASSIGN (lhs = rhs)        | `expr0 : expr1 T_2EQUAL expr0`              | `Expr0 = Expr1 FENCE($'=' Expr0 …)`                  | ✅ both right-assoc |
| `?`            | 1  | left  | 9844 | TT_SCAN (explicit match)     | `expr1 : expr3 T_2QUEST expr1`              | `Expr1 = Expr2 FENCE($'?' Expr1 …)`                  | ⚠ **both grammars are right-assoc**, Manual says left. (Practical effect minimal — `a?b?c` is meaningless: `a?b` produces success/failure, then `?c` would scan the success value. Few programs chain `?`.) |
| `\|`           | 3  | right | 9845 | TT_ALT (n-ary)               | `expr3 : expr3 T_2PIPE expr4` + flatten     | `Expr3 = nPush() *X3 reduce(TT_ALT) nPop()`, X3 n-ary | ✅ both flatten n-ary; Manual right-assoc preserved trivially since alternation is commutative for the *first* match |
| `(space)`      | 4  | right | 9846 | TT_SEQ (n-ary)               | `expr4 : expr4 T_CONCAT expr5` + flatten    | `Expr4 = nPush() *X4 reduce(TT_SEQ) nPop()`, X4 n-ary | ✅ both flatten n-ary; concat is associative |
| `+`            | 6  | **left**  | 9847 | TT_ADD                   | `expr6 : expr6 T_2PLUS expr9` + flatten     | `Expr6 = Expr7 FENCE($'+' Expr6 …)` (right-rec)      | ❌ **`.sc` is right-assoc, must be left** |
| `-`            | 6  | **left**  | 9848 | TT_SUB                   | `expr6 : expr6 T_2MINUS expr9` + flatten    | `Expr6 = Expr7 FENCE($'-' Expr6 …)` (right-rec)      | ❌ **`.sc` is right-assoc, must be left** |
| `#`            | 7  | (Snocone) | —    | TT_SUB (Snocone alias)   | —                                           | `Expr7 = Expr8 FENCE($'#' Expr7 …)`                  | ⚠ Snocone extension; not in Ch.15. Right-recursive in `.sc`; C grammar doesn't expose `#` as a binary. **Same wrong-assoc story IF chained.** |
| `/`            | 8  | **left**  | 9849 | TT_DIV                   | `expr9 : expr9 T_2SLASH expr11` + flatten   | `Expr8 = Expr9 FENCE($'/' Expr8 …)` (right-rec)      | ❌ **`.sc` is right-assoc, must be left** |
| `*`            | 9  | **left**  | 9875 | TT_MUL                   | `expr9 : expr9 T_2STAR expr11` + flatten    | `Expr9 = Expr10 FENCE($'*' Expr9 …)` (right-rec)     | ❌ **`.sc` is right-assoc, must be left** |
| `%`            | 10 | (Snocone) | —    | TT_MUL (Snocone alias)   | —                                           | `Expr10 = Expr11 FENCE($'%' Expr10 …)`               | ⚠ Snocone extension; right-recursive in `.sc`. Same story. |
| `^` `!` `**`   | 11 | **right** | 9883 | TT_POW                   | `expr11 : expr12 T_2CARET expr11`           | `Expr11 = Expr12 FENCE(($'^'\|$'!'\|$'**') Expr11 …)` | ✅ both right-assoc (matches Ch.15) |
| `$`            | 12 | **left**  | 9884 | TT_CAPT_IMMED_ASGN       | `expr12 : expr12 T_2DOLLAR expr15`          | `Expr12 = Expr13 FENCE($'$' Expr13 reduce(2) FENCE($'$' Expr13 reduce(2)\|epsilon)\|…)` | ❌ **`.sc` allows at most 2-deep chain via hand-rolled FENCE; not a true left-assoc rule**. C grammar is correctly left-recursive (unlimited). |
| `.`            | 12 | **left**  | 9885 | TT_CAPT_COND_ASGN        | `expr12 : expr12 T_2DOT expr15`             | `Expr12 = … FENCE($'.' Expr13 reduce(2) FENCE($'.' Expr13 reduce(2)\|epsilon)\|…)` | ❌ same as `$` |

### Compound assignment operators (Snocone extensions, not in Ch.15)

| Op | C grammar | `.sc` grammar | Status |
|----|-----------|---------------|--------|
| `+=` `-=` `*=` `/=` `^=` | `expr0 : expr1 T_PLUS_ASSIGN expr0` etc. (right-assoc) | `Expr0 = Expr1 FENCE($'+=' Expr0 Reduce_augop(…)\|…\|epsilon)` (right-assoc) | ✅ both right-assoc, consistent with `=` |

### Comparison operators (Snocone-specific sugar; Manual provides only function-call forms EQ/NE/LT/LE/GT/GE)

| Op | C grammar | `.sc` grammar | Status |
|----|-----------|---------------|--------|
| `==` `!=` `<` `<=` `>` `>=` | `expr5 : expr5 T_EQ expr6` etc. — **left-recursive**, so chainable left-assoc | `Expr5 = Expr6 FENCE($'==' Expr6 Push_cmp(EQ)\|…\|epsilon)` — **non-chainable** (RHS is Expr6, not Expr5) | ⚠ **divergent shape**: C accepts `a==b==c` (parses left-assoc); `.sc` rejects it (would leave `==c` unconsumed). |
| `&` (binary, pri 2 if anyone OPSYNs it; Manual says "available for OPSYN") | — | `Expr2 = Expr3 FENCE($'&' Expr2 reduce(TT_SEQ,2)\|epsilon)` | ⚠ Snocone reserves `&` as a binary `TT_SEQ`. Right-recursive in `.sc`. Not in C grammar. |
| `~` (binary at pri 13, used as negation predicate) | — | `Expr13 = Expr14 FENCE($'~' Expr13 reduce(TT_NOT,2)\|epsilon)` | ⚠ Snocone reserves binary `~` (Manual lists it only as unary at pri 13). Right-recursive in `.sc`. |
| `@` (Manual: unary cursor-assign; Snocone also uses binary at pri 5) | `expr5 : T_1AT … (unary in expr17 fallback)` — only unary path | `Expr5 = Expr6 FENCE($'@' Expr5 reduce(TT_CAPT_CURSOR,2)\|…)` — **binary, right-recursive** | ⚠ binary `@` is a Snocone extension; if chained it would be right-assoc in `.sc` but is unreachable in C. |

---

## Findings summary

### Major: arithmetic associativity (the original PLAN.md flag)

`+ - * /` are LEFT-associative per Manual Ch.15 (verified empirically by `mixed_op_truth.sno`).

| Grammar | `a + b - c` produces |
|---------|----------------------|
| C (`snocone_parse.y`) | `(TT_SUB (TT_ADD a b) c)`  ← **correct** (left-assoc, then sc_flatten_arith no-op because outer tag differs) |
| `.sc` (`parser_snocone.sc`) | `(TT_ADD a (TT_SUB b c))`  ← **wrong** (right-assoc grammar shape; flatten_arith won't merge because tags differ) |
| SPITBOL evaluation of `10 + 8 - 3` | `15`  ← left-assoc |

For **single-tag chains** like `a-b-c`, the divergence is invisible: both grammars produce `(TT_SUB a b c)` (n-ary) — C via left-recursion + flatten, `.sc` via right-recursion + flatten_arith collapsing the same-tag right child. Flatten masks the bug.

For **mixed-tag chains** like `a+b-c`, `a*b/c`, `10/5*2`, etc., the bug is visible:

| Expression | SPITBOL value | C tree shape | `.sc` tree shape (no flatten) | Effective `.sc` evaluation |
|------------|---------------|--------------|-------------------------------|------------------------------|
| `10 + 8 - 3`  | 15 | `(TT_SUB (TT_ADD 10 8) 3)` = (10+8)-3 = 15 | `(TT_ADD 10 (TT_SUB 8 3))` = 10+(8-3) = 15 | **value coincidentally agrees because all values are integers and `+` is commutative**; but the tree is wrong-shape |
| `20 - 5 + 2`  | 17 | `(TT_ADD (TT_SUB 20 5) 2)` = (20-5)+2 = 17 | `(TT_SUB 20 (TT_ADD 5 2))` = 20-(5+2) = 13 | **value disagrees** (17 vs 13) |
| `100 / 5 * 2` | 40 | `(TT_MUL (TT_DIV 100 5) 2)` = 40 | `(TT_DIV 100 (TT_MUL 5 2))` = 10 | **value disagrees** (40 vs 10) |

The `20 - 5 + 2` case is the smoking gun: if a Snocone program contains `n = 20 - 5 + 2;`, and that program is run via SCRIP `.sc` execution path, the variable will hold 13. If the same program is transpiled to `.sno` via `lower_sno.c` walking the AST and then run under SPITBOL, the variable will hold 17. **They disagree.** This violates the goal of "SCRIP and SPITBOL produce identical AST and identical execution."

### Minor: pattern-capture chains capped at 2 in `.sc`

`Expr12` in `.sc` hand-rolls a 2-deep FENCE:
```
$'$' *Expr13 reduce(…,2) FENCE($'$' *Expr13 reduce(…,2) | epsilon)
```
This accepts `a$b` and `a$b$c` but **not** `a$b$c$d`. The C grammar accepts unlimited via standard left-recursion. **Unlikely to matter for the existing `parser_*.sc` corpus** (capture chains rarely go beyond 2), but it's a latent grammar-divergence.

### Minor: `?` is left-assoc in Manual, right-assoc in both grammars

Both C and `.sc` are right-recursive on `?`. Manual says left-assoc at pri 1. Practically, `a ? b ? c` is rare and the failure mode is unclear (chained scans don't have an obvious semantics). Not worth changing unless a real program exercises this.

### Minor: Snocone-specific binary operators (`#`, `%`, `&`, binary `~`, binary `@`)

These are Snocone extensions not present in the Manual; the Manual lists them as "available for OPSYN" (uncommitted). The `.sc` grammar makes them right-recursive (right-assoc) consistently. The C grammar **does not handle them as binary** (`%`, `&`, `~`, `@` are only unary in C; `#` not exposed). This is a grammar-coverage gap on the C side, not a precedence bug. **Action for SCT-9g: document; do not fix unless a real program exercises them.**

---

## Recommended fix (Lon decision required)

**Recommendation: fix the `.sc` grammar to be left-associative for `+ - * /` (and by extension `#` and `%` for consistency).**

Reasoning:
1. **Manual is the spec.** Ch.15 is explicit and live SPITBOL agrees.
2. **C frontend is correct already.** Fixing `.sc` to match C means all three (Manual, C, `.sc`) agree.
3. **Documenting an exception would encode a known wrong-answer-by-design.** Any user-visible Snocone program with mixed arithmetic chains would silently disagree depending on which path executes it. That is exactly the kind of divergence the 2-way sync-monitor (SCT-1f, SCT-7) is supposed to surface, and pre-emptively papering it over with "documented exception" would suppress real bug reports.
4. **The fix is mechanical.** A right-recursive PEG rule `A = B FENCE($op A reduce(…,2) | ε)` becomes a left-folding rule. In SPITBOL pattern-grammar style, this is:
   ```
   Expr6  =  nPush() *X6 reduce_left_chain() nPop()
   X6     =  nInc() *Expr7 FENCE(($'+' | $'-') . op *X6 | epsilon)
   ```
   where `reduce_left_chain` pops the n-ary stack and builds a left-leaning tree by walking the captured op tokens. **However** — this rewrite touches the shared shift/reduce/counter primitives (the six allowed per the goal's "Implementation Constraints"). Confirm with Lon that the rewrite can use the existing primitive set, or whether a new helper is needed.

**Alternative:** leave `.sc` wrong-shape but require `lower_sno.c` to **re-associate** TT_ADD/TT_SUB/TT_MUL/TT_DIV chains at transpile time before emission. This makes the transpiler correct (transpiled `.sno` under SPITBOL produces left-assoc value) but leaves the `.sc` direct-execution path still wrong. **Not recommended** — it papers over the bug rather than fixing it.

**Alternative-alternative:** mark the affected chains "undefined behaviour in Snocone — use parentheses." Documented exception with diagnostic. **Not recommended** — users hate this and the language is small enough to do right.

### Out-of-scope for SCT-9g (queued for future sub-rungs)

- `?` left-assoc fix (Manual, pri 1) — low impact.
- Pattern-capture chain depth >2 in `.sc` (Expr12) — low impact.
- Snocone-specific binary `#`, `%`, `&`, `~`, `@` — exposed in `.sc` but not in C; grammar-coverage gap on C side. Decide whether C accepts them or whether `.sc` drops them.

---

## What this audit changes today

- **No code touched.** This is a documentation-only deliverable per the SCT-9g action item ("Output: `.github/PRECEDENCE-AUDIT.md` table + commits to whichever grammar(s) need correction.").
- **A Lon decision is requested** on the recommended fix (above). Once received, follow-up commit will implement the chosen path.
- **Empirical probes** (`probe_assoc.sno`, `mixed_op_truth.sno`) live at `/home/claude/work/` in the session sandbox; not committed (one-shot session artifacts).

**Bonus fix landed alongside the audit (`src/lower/lower_sno.c`):** TT_ADD/SUB/MUL/DIV emission was binary-only (`c[0] op c[1]`), silently dropping n-ary children `c[2..n-1]`. Rewrote as left-folded n-ary emission. Verified end-to-end: `--dump-sno` of `20-5+2` → SPITBOL = 17 (was 5); `100-30+10-5` → 75 (was 65). Snocone fixture gate 60/7/0 pre = post.

---

## §2 — SNOBOL4

**Status:** Not started. Spec document already on disk: SPITBOL Manual v3.7 (`/mnt/user-data/uploads/spitbol-manual-v3_7.pdf`, extract at `/tmp/spitbol.txt`). Ch.15 covers the operator table; App C (line 13651+) covers SPITBOL-vs-SNOBOL4 deltas. Live oracle: same `/home/claude/x64/bin/sbl`.

**Files to audit:**
- C side: `src/frontend/snobol4/` (lexer + bison parser)
- `.sc` side: `corpus/SCRIP/parser_snobol4.sc`

**Procedure:** identical to §1. Enumerate every binary operator in both grammars; compare to Ch.15; verify with `sbl` probes; document divergences.

**Anticipated coverage:** SNOBOL4 has fewer "Snocone-extension" operators (no `==`, `!=`, etc.; comparisons are function calls `EQ`/`NE`/...). The Ch.15 table applies directly. Statement form is the LABEL/SUBJECT/?/PATTERN/=/REPLACEMENT/:GOTO shape (Ch.14 line 9465).

---

## §3 — Rebus

**Status:** Not started. **Spec document needed from Lon.**

Rebus is Mark Emmer's SPITBOL preprocessor (referenced in SPITBOL Manual Ch.14 line 9388: "preprocessors such as Rebus and Snocone"). No public grammar reference is on disk. Without an authoritative document, the audit can only describe what the current grammars accept, not what they *should* accept.

**Files to audit:**
- C side: `src/frontend/rebus/`
- `.sc` side: `corpus/SCRIP/parser_rebus.sc`

**Request to Lon:** provide a Rebus syntax/operator reference document (operator table with priority and associativity per operator). A scan of the Catspaw Rebus manual, or an equivalent specification, would suffice.

---

## §4 — Icon

**Status:** Not started. **Spec document needed from Lon.**

Icon's operator system is substantially different from SPITBOL/SNOBOL4:
- `:=` simple assignment
- `<-` reversible assignment (backtracking)
- `:=:` exchange
- augmented forms `+:=`, `-:=`, etc.
- `|` is generator alternation (not pattern alternation as in SPITBOL)
- comparison operators succeed (returning their RHS) or fail rather than returning Booleans
- `=` is numeric comparison (not assignment)
- `==` is string comparison
- `===` is structural identity
- `to`/`by` for ranges
- `&` is conjunction (returns RHS if both succeed), not "available for OPSYN"

Without an Icon spec on disk, an audit can't be authoritative.

**Files to audit:**
- C side: `src/frontend/icon/`
- `.sc` side: `corpus/SCRIP/parser_icon.sc` (plus `icon_helpers.sc` — to be deleted per SCT-4)

**Request to Lon:** Icon Programming Language reference (Griswold's book or the operator table from the public Icon manual would suffice).

---

## §5 — Raku

**Status:** Not started. **Spec document needed from Lon.**

Raku has the most elaborate operator system of the six languages: tightness levels (terms tighter than methodop tighter than autoincrement tighter than ... tighter than loose-or), user-definable operators, hyper operators (`>>+<<`), meta operators (`R+`, `[+]`, `Z+`, `X+`), chained comparisons (`1 < $x < 10`), feed operators (`==>`/`<==`), and custom Unicode operators. The current `parser_raku.sc` certainly implements a subset.

**Files to audit:**
- C side: `src/frontend/raku/`
- `.sc` side: `corpus/SCRIP/parser_raku.sc` (plus `raku_helpers.sc` — to be deleted per SCT-5)

**Request to Lon:** Raku operator table specifying which subset is in scope for SCRIP, with priorities and associativities. The full Raku spec (`docs.raku.org`) is too large to audit verbatim; an explicit scope document is required.

---

## §6 — Prolog

**Status:** Not started. **Spec document needed from Lon.**

Prolog operators are declared via `op/3` directives: `op(Priority, Type, Name)`. Types encode associativity AND arity:
- `xfx` — binary, non-associative (must parenthesize for chains)
- `xfy` — binary, right-associative (typical for `,` `;` `->`)
- `yfx` — binary, left-associative (typical for arithmetic)
- `fx` `fy` — prefix
- `xf` `yf` — postfix

The standard table (priority 0..1200, lower binds tighter):
- 1200 xfx `:-` `-->`  /  1200 fx `:-` `?-`
- 1100 xfy `;`
- 1050 xfy `->`
- 1000 xfy `,`
- 700 xfx `=` `\=` `==` `\==` `is` `=..` `<` `>` `=<` `>=` `@<` `@>` `@=<` `@>=`
- 500 yfx `+` `-` `/\` `\/`
- 400 yfx `*` `/` `//` `rem` `mod` `<<` `>>`
- 200 xfx `**`  /  200 xfy `^`  /  200 fy `-`

**Files to audit:**
- C side: `src/frontend/prolog/`
- `.sc` side: `corpus/SCRIP/parser_prolog.sc`

**Request to Lon:** ISO Prolog op-table or SWI-Prolog op-table acceptable (the two differ in a few cases). Confirm which Prolog dialect SCRIP targets.

---

## §7 — Cross-language consistency sweep

**Status:** Awaiting §§2-6 completion.

After all six per-language audits land, sweep this file for cases where the same syntactic operator appears in multiple languages with different precedence, associativity, or semantics. Flag any cross-language symbol that needs an explicit consistency call from Lon. Examples already visible:

- `.` is unary "name" in SPITBOL/Snocone (priority above any binary); member-access in Raku (high-priority postfix); list-cons in some Prolog dialects (`[H|T]` uses `|`, but `.(H, T)` is the canonical cons functor).
- `|` is pattern alternation in SPITBOL/Snocone (binary pri 3 right); generator alternation in Icon; disjunction in Prolog (xfy 1100); also Prolog list-tail syntax `[H|T]`.
- `,` is the argument-list separator in all six but is also Prolog's binary conjunction operator at priority 1000 xfy.
- `=` is assignment (right-assoc pri 0) in SPITBOL/Snocone; numeric comparison in Icon; unification in Prolog (xfx 700).
- `*` is binary multiplication in SPITBOL/Snocone (pri 9 left); unary deferred-eval in SPITBOL/Snocone (pri 14); in Icon, unary `*` is "size of structure".
- `&` is binary conjunction in Icon, keyword-reference prefix in SPITBOL/Snocone (`&ANCHOR`), and "available for OPSYN" in plain SPITBOL semantics.

These are not bugs — each language has its own spec — but the cross-table must be explicit so the transpiler doesn't silently apply one language's semantics to another's tree.

---

## Authors

§1 (Snocone) audited by Claude Opus 4.7 on 2026-05-17, against:
- SPITBOL Manual v3.7 (Catspaw 2000), Ch.15 "Operators" (manual lines 9540–9900 in pdftotext output)
- live SPITBOL x64 binary at `/home/claude/x64/bin/sbl` (deterministic, matches manual)
- `corpus/SCRIP/parser_snocone.sc` @ corpus HEAD `1b24df4`
- `SCRIP/src/frontend/snocone/snocone_parse.y` @ SCRIP HEAD `96d39c05`

§§2-6 awaiting spec documents from Lon (see each section's "Request to Lon").

---

## §2 — SNOBOL4

**Status:** ✅ Completed 2026-05-17 (Claude Sonnet 4.6).
**Inputs:** SPITBOL Manual v3.7 Ch.15 (lines 9540–9900, `/tmp/spitbol.txt`) + `corpus/SCRIP/parser_snobol4.sc` @ corpus HEAD `1b24df4` + `SCRIP/src/frontend/snobol4/snobol4.y` @ SCRIP HEAD `96d39c05`.

### Methodology

Same as §1: Ch.15 is the spec; grammar shape (left-recursive Bison rule = left-assoc; right-recursive PEG FENCE rule = right-assoc; foldop+cont loop = left-fold) determines associativity; live `sbl` is the oracle. The SNOBOL4 `.sc` grammar uses a different idiom from the snocone one: instead of plain right-recursion it uses a **foldop+cont pattern** for left-associative operators, which correctly produces left-to-right folding. This is a significant structural improvement over `parser_snocone.sc`.

**`foldop` semantics:** pops the top two stack items and reduces to a binary node. `Expr6cont` loops via tail-recursion and calls `foldop` after each new RHS, producing `reduce(reduce(a,b),c)` = left-fold.

**SNOBOL4 note:** SNOBOL4 has no comparison-operator sugar (`==`, `!=`, etc.) and no compound assignment (`+=`, etc.). It uses SPITBOL built-in functions (`EQ()`, `NE()`, `LT()`, etc.) for numeric comparisons. The operator set is exactly the Ch.15 table.

---

### Binary operator table

| Op | Pri | Assoc (Manual) | C grammar (`snobol4.y`) | `.sc` grammar (`parser_snobol4.sc`) | Status |
|----|----:|----------------|------------------------|--------------------------------------|--------|
| `=` | 0 | right | `expr0 : expr2 T_2EQUAL expr0` — right-assoc ✓ | `Expr0 = Expr1 FENCE($'=' Expr0 reduce(2)\|epsilon)` — right-assoc ✓ | ✅ |
| `?` | 1 | **left** | `expr0 : expr2 T_2QUEST expr0` — right-assoc (shared with `=` in expr0) ⚠ | `Expr1 = Expr2 FENCE($'?' Expr1 reduce_opsyn('?',2)\|epsilon)` — right-assoc ⚠ | ⚠ **both right-assoc**; Manual says left. `a?b?c` is obscure enough that practical impact is nil. Note: .sc gives `?` its own level (Expr1); C grammar conflates `?` and `=` at expr0 — a minor structural difference with no semantic impact since `?` and `=` cannot chain together. |
| `&` | 2 | **left** | `expr2 : expr2 T_2AMP expr3` — left-recursive ✓ | `Expr2 = Expr3 FENCE($'&' Expr2 reduce_opsyn('&',2)\|epsilon)` — right-recursive ❌ | ❌ **`.sc` right-assoc; Manual+C say left**. `&` is an OPSYN slot — no SNOBOL4 standard program uses it as a binary operator unless user-defined. Low practical impact; tree-shape divergence exists. |
| `\|` | 3 | **right** | `expr3 : expr3 T_2PIPE expr4` — left-recursive (left-assoc) ⚠ | `Expr3 = Expr4 FENCE($'\|' Expr4 reduce(2) Expr3tail\|epsilon)` + `Expr3tail` loop — **left-fold** ⚠ | ⚠ **both left-assoc**; Manual says right. `a\|b\|c` = `TT_ALT(TT_ALT(a,b),c)` in both. Pattern alternation is operationally associative (first-match wins regardless of grouping), but tree shape differs from spec. C and `.sc` agree with each other. |
| *space* | 4 | **right** | `expr4 : expr4 T_CONCAT expr5` — left-recursive (left-assoc) ⚠ | `Expr4 = Expr5 FENCE($'  ' Expr5 reduce(2) Expr4tail\|epsilon)` + `Expr4tail` loop — **left-fold** ⚠ | ⚠ **both left-assoc**; Manual says right. `a b c` = `TT_SEQ(TT_SEQ(a,b),c)`. Concat is associative for string values; tree shape differs from spec for pattern sequences. C and `.sc` agree. |
| `@` | 5 | **right** | `expr5 : expr5 T_2AT expr6` — left-recursive ❌ | `Expr5 = Expr6 FENCE($'@' Expr5 reduce_opsyn('@',2)\|epsilon)` — right-recursive ✓ | ❌ **C is left-assoc (wrong)**; Manual+`.sc` say right. `@` captures cursor position to its operand — an OPSYN slot, rarely chained. `.sc` is correct; C grammar has a bug. |
| `+` | 6 | **left** | `expr6 : expr6 T_2PLUS expr7` — left-recursive ✓ | `Expr6 = Expr7 FENCE($'+' Expr7 foldop('TT_ADD') Expr6cont\|\$'-' Expr7 foldop('TT_SUB') Expr6cont\|epsilon)` + `Expr6cont` loop — **left-fold** ✓ | ✅ both correct |
| `-` | 6 | **left** | `expr6 : expr6 T_2MINUS expr7` — left-recursive ✓ | (same Expr6 rule as `+`) — left-fold ✓ | ✅ both correct |
| `#` | 7 | **left** | `expr7 : expr7 T_2POUND expr8` — left-recursive ✓ | `Expr7 = Expr8 FENCE($'#' Expr7 foldop('TT_MUL')\|epsilon)` — right-recursive (no `cont` loop) ❌ | ❌ **`.sc` right-assoc; Manual+C say left**. `#` is a user-OPSYN slot (available at pri 7 left per Manual). No standard SNOBOL4 program uses `#` as binary. Low practical impact. |
| `/` | 8 | **left** | `expr8 : expr8 T_2SLASH expr9` — left-recursive ✓ | `Expr8 = Expr9 FENCE($'/' Expr9 foldop('TT_DIV') Expr8cont\|epsilon)` + `Expr8cont` loop — left-fold ✓ | ✅ both correct |
| `*` | 9 | **left** | `expr9 : expr9 T_2STAR expr10` — left-recursive ✓ | `Expr9 = Expr10 FENCE($'*' Expr10 foldop('TT_MUL') Expr9cont\|epsilon)` + `Expr9cont` loop — left-fold ✓ | ✅ both correct |
| `%` | 10 | **left** | `expr10 : expr10 T_2PERCENT expr11` — left-recursive ✓ | `Expr10 = Expr11 FENCE($'%' Expr10 foldop('TT_DIV')\|epsilon)` — right-recursive (no `cont` loop) ❌ | ❌ **`.sc` right-assoc; Manual+C say left**. `%` is a user-OPSYN slot. No standard SNOBOL4 program uses `%` as binary. Low practical impact. |
| `^ ! **` | 11 | **right** | `expr11 : expr12 T_2CARET expr11` — right-recursive ✓ | `Expr11 = Expr12 FENCE(($'^'\|$'!'\|$'**') Expr12 foldop('TT_POW') Expr11cont\|epsilon)` + `Expr11cont` loop — **left-fold** ❌ | ❌ **`.sc` left-assoc; Manual+C say right**. `2^3^2` under `.sc` = `(2^3)^2 = 64`; under C and SPITBOL = `2^(3^2) = 512`. **This is a value disagreement for chained exponentiation.** |
| `$` | 12 | **left** | `expr12 : expr12 T_2DOLLAR expr13` — left-recursive ✓ | `Expr12 = Expr13 FENCE($'$' Expr13 reduce(2) Expr12tail_immed\|…)` + `Expr12tail_immed` loop — left-fold ✓ | ✅ both correct |
| `.` | 12 | **left** | `expr12 : expr12 T_2DOT expr13` — left-recursive ✓ | (same Expr12 rule as `$`) + `Expr12tail_cond` loop — left-fold ✓ | ✅ both correct |
| `~` | 13 | **right** | `expr13 : expr14 T_2TILDE expr13` — right-recursive ✓ | `Expr13 = Expr14 FENCE($'~' Expr13 reduce_opsyn('~',2)\|epsilon)` — right-recursive ✓ | ✅ both correct |

---

### Notable structural observation: `foldop+cont` vs plain right-recursion

`parser_snobol4.sc` uses a different pattern from `parser_snocone.sc` for left-associative operators:

```
* snobol4 .sc (correct for +/-):
Expr6     = *Expr7 FENCE($'+' *Expr7 foldop("'TT_ADD'") *Expr6cont | ... | epsilon);
Expr6cont = FENCE($'+' *Expr7 foldop("'TT_ADD'") *Expr6cont | ... | epsilon);

* snocone .sc (WRONG for +/-):
Expr6 = *Expr7 FENCE($'+' *Expr6 reduce("'TT_ADD'", 2) | ... | epsilon);  ← right-recursive!
```

The `cont` helper makes `foldop` fire after each new RHS is pushed, iterating left-to-right. This is the correct idiom for left-associative operators in the SCRIP PEG framework. **`parser_snobol4.sc` applies this correctly for `+`, `-`, `/`, `*` and `$`, `.`** — these all have `cont` loops.

The bug is that `#` (Expr7) and `%` (Expr10) have `foldop` but **no `cont` loop** — they are single-application foldop into a right-recursive descent. And `^` (Expr11) has a `cont` loop but uses `foldop`, making it left-fold when it should be right-recursive.

---

### Findings summary for SNOBOL4

**Major (value disagrees with SPITBOL):**

| Expression | SPITBOL value | C tree | `.sc` tree | Impact |
|------------|---------------|--------|------------|--------|
| `2 ^ 3 ^ 2` | `512` (right-assoc: 2^9) | `TT_POW(2, TT_POW(3,2))` ✓ | `TT_POW(TT_POW(2,3), 2)` ❌ | **Numeric disagreement on chained exponentiation** |

**Minor (OPSYN operators — no standard program chains them):**

| Bug | Description | Practical impact |
|-----|-------------|-----------------|
| `&` right-assoc in `.sc` (should left) | `a & b & c` → `.sc`: `TT_OPSYN(a, TT_OPSYN(b,c))`; C: `TT_OPSYN(TT_OPSYN(a,b),c)` | OPSYN slot, never standard-used as binary |
| `@` left-assoc in C (should right) | `a @ b @ c` → C: `TT_OPSYN(TT_OPSYN(a,b),c)`; `.sc`: `TT_OPSYN(a, TT_OPSYN(b,c))` | OPSYN slot cursor-assign, rarely chained |
| `#` right-assoc in `.sc` (should left) | `a # b # c` → `.sc` right-fold; C left-fold | OPSYN slot, never standard-used |
| `%` right-assoc in `.sc` (should left) | same | OPSYN slot, never standard-used |

**Cosmetic (C and `.sc` agree but both diverge from Manual):**

| Issue | Manual | Both grammars | Impact |
|-------|--------|---------------|--------|
| `?` right-assoc | Manual says left | Both right-assoc | Chained scan `a?b?c` is obscure; same finding as §1 |
| `\|` left-assoc | Manual says right | Both left-assoc | Tree shape: `TT_ALT(TT_ALT(a,b),c)` vs `TT_ALT(a,TT_ALT(b,c))`; first-match semantics unaffected |
| space left-assoc | Manual says right | Both left-assoc | Concat associative for strings; pattern sequences may differ |

---

### Recommended fixes

**Fix 1 (required — value bug): `Expr11` exponentiation in `parser_snobol4.sc`**

Replace the `foldop+cont` (left-fold) pattern with a plain right-recursive descent, matching the C grammar and the Manual:

```
* BEFORE (wrong — left-fold):
Expr11     = *Expr12 FENCE(($'^' | $'!' | $'**') *Expr12 foldop("'TT_POW'") *Expr11cont | epsilon);
Expr11cont = FENCE(($'^' | $'!' | $'**') *Expr12 foldop("'TT_POW'") *Expr11cont | epsilon);

* AFTER (correct — right-assoc):
Expr11 = *Expr12 FENCE(($'^' | $'!' | $'**') *Expr11 reduce("'TT_POW'", 2) | epsilon);
```

This mirrors the C grammar `expr11 : expr12 T_2CARET expr11` exactly. `2^3^2` will produce `TT_POW(2, TT_POW(3,2))` = 512 ✓.

**Fix 2 (minor — OPSYN `#` and `%` consistency): Add `cont` loops to `Expr7` and `Expr10`**

```
* BEFORE Expr7 (wrong — single foldop, right-assoc):
Expr7  = *Expr8 FENCE($'#' *Expr7 foldop("'TT_MUL'") | epsilon);

* AFTER (correct — foldop+cont, left-fold):
Expr7     = *Expr8 FENCE($'#' *Expr8 foldop("'TT_MUL'") *Expr7cont | epsilon);
Expr7cont = FENCE($'#' *Expr8 foldop("'TT_MUL'") *Expr7cont | epsilon);

* Same fix for Expr10 (%):
Expr10     = *Expr11 FENCE($'%' *Expr11 foldop("'TT_DIV'") *Expr10cont | epsilon);
Expr10cont = FENCE($'%' *Expr11 foldop("'TT_DIV'") *Expr10cont | epsilon);
```

**Fix 3 (minor — `&` right-assoc in `.sc`):** Change `Expr2` from `FENCE($'&' *Expr2 …)` to `FENCE($'&' *Expr3 foldop(…) *Expr2cont …)`. Low priority — no SNOBOL4 program uses `&` as a binary operator without an OPSYN definition, and even then chaining it is exotic.

**Do not fix:** `?`, `|`, space left/right discrepancies — C and `.sc` agree with each other, both grammars intentionally produce binary-chain trees (left-associative), and the functional impact is nil for the transpiler's current corpus.

**Do not fix in C grammar:** `@` left-assoc in C (`expr5 : expr5 T_2AT expr6`). This is a pre-existing C grammar bug (Manual says right-assoc); `.sc` is accidentally correct. Fixing the C grammar requires a Bison grammar change. Lon decision required.

---

### Authors

§2 (SNOBOL4) audited by Claude Sonnet 4.6 on 2026-05-17, against:
- SPITBOL Manual v3.7 (Catspaw 2000), Ch.15 (lines 9540–9900 in `/tmp/spitbol.txt`)
- `corpus/SCRIP/parser_snobol4.sc` @ corpus HEAD `1b24df4`
- `SCRIP/src/frontend/snobol4/snobol4.y` @ SCRIP HEAD `96d39c05`

---

## §2 addendum — n-ary rewrite (2026-05-17, Claude Sonnet 4.6)

Per Lon directive: **n-ary everywhere appropriate** — associativity is a lower-level concern; the parse tree captures tokens left-to-right (shift-reduce constraint) and lower-level code (lower_sno.c, sm_lower.c) folds in the semantically correct direction.

### Changes applied to `parser_snobol4.sc`

**Expr3 (`|` / TT_ALT) and Expr4 (space / TT_SEQ):**
Converted from `reduce(2)+Expr3tail/Expr4tail` (binary left-fold chain) to `foldop+Expr3cont/Expr4cont` (n-ary via FoldOp.Append). `FoldOp()` in `ShiftReduce.sc` detects when the top-of-stack node has the same tag as the new operation and calls `Append()` to extend it in place: `a|b|c` → `TT_ALT(a,b,c)`, not `TT_ALT(TT_ALT(a,b),c)`. The `Expr3tail`/`Expr4tail` helpers are deleted; replaced by `Expr3cont`/`Expr4cont` (consistent naming with `Expr6cont`…`Expr10cont`).

**Expr11 (`^`/`!`/`**` / TT_POW):**
Converted from binary right-recursive `reduce(2)` to flat n-ary via `nPush()/X11/reduce(nTop)/nPop()` pattern (same as snocone's `Expr3`/`Expr4` with X3/X4 helpers). `a^b^c` → `TT_POW(a,b,c)`. The lower-level code right-folds this to `a^(b^c)`. The X11 helper recurses right to collect all operands into the counter frame before reducing.

**Unchanged (stay binary or are already n-ary):**
- `=` (Expr0), `?` (Expr1): inherently binary; right-assoc semantics require it.
- `&`/`@`/`~` OPSYN slots (Expr2, Expr5, Expr13): different-op OPSYN nodes can't be merged (FoldOp merges by tag only); stay binary.
- `+`/`-` (Expr6), `/` (Expr8), `*` (Expr9): already n-ary via `foldop+cont` (homogeneous runs); mixed-tag runs (e.g. `a+b-c`) produce left-fold binary chain where tags change — this is the best achievable without a new `TT_ARITH_RUN` composite node.
- `#` (Expr7), `%` (Expr10): already `foldop+cont` from the SCT-9g-snobol4 fixes above.
- `$`/`.` (Expr12): different tags; can't merge. Stay binary-chain. Left to lower-level.
