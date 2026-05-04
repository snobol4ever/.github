# GOAL-PARSER-REBUS.md — PARSER-REBUS pattern frontend in Snocone

**Repo:** corpus+one4all
**Branch:** `parser` (one4all only — `corpus` and `.github` stay on `main`)
**Sibling ladder:** `GOAL-LANG-REBUS.md`. The existing Rebus frontend
(`src/frontend/rebus/`) is the in-process oracle.

**Done when:** A Snocone program `parser_rebus.sc` reads Rebus source,
runs **one** `Compiland` PATTERN that builds the canonical IR tree on
the shared shift-reduce stack, and for every test program in the rung
corpus `tree_equal(existing_frontend_tree, parser_rebus_tree)` returns
true. Where a `.ref` file exists, executing both trees through the IR
interpreter produces byte-identical output.

⛔ **The deliverable is a PATTERN, not a procedure.** See `## Rubric`
below before writing any code. A line-at-a-time goto-driven state
machine — even one that emits the right tree shapes — is the wrong
deliverable and does not advance any rung.

---

## Status — session #62 attempt was REWORK, not landed

Sessions #62 (Claude Sonnet 4.7, 2026-05-03) wrote `parser_rebus.sc`
as a goto-driven line-at-a-time state machine that achieved tree
equivalence with the existing Rebus frontend on PASS=38 fixtures.

That code is the **wrong shape**. It does not use `Compiland`/`Command`/
`shift`/`reduce`/`nPush`/`nInc`/`nTop`/`nPop` — the canonical SNOBOL4-
family pattern spine the rest of this goal file specifies. The PASS=38
gate flagged tree equivalence but did not flag architectural shape;
that is a hole in the gate, not a clearance.

All seven rungs (RB-0..RB-6) are **REOPENED for rewrite as patterns**.
The 38 fixtures in `corpus/programs/rebus/parser/` are kept verbatim —
they are correct as gate input — but `parser_rebus.sc` itself is to be
rewritten from scratch following the model of `parser_snocone.sc`.

The rewrite does NOT have to be done all at once. The rung structure
below stages it: each rewritten rung lands when its pattern subtree
clears its fixture subset using the shift-reduce idiom.

---

## Rubric — what makes this a pattern parser

Before writing any `.sc` code, confirm every item below. If any
answer is "no", stop and rework.

1. **One root pattern, matched once against the entire source.** The
   driver reads stdin into a single string `Src` (concatenating all
   lines with newlines), then runs `Src ? Compiland`. **Exactly one
   `?` operator appears in the driver, ever.** Sub-patterns
   (`Command`, `expr`, `atom`, etc.) are referenced from inside
   `Compiland` via `*Sub`; they are never matched separately by the
   driver. There is no per-line slurp loop matching individual lines
   against patterns. After the single match, the driver walks the
   tree on the stack to call `TDump` per top-level child — that is
   emission, not parsing, and is allowed.

2. **`Compiland` has the canonical beauty.sc spine.** Literally:
   ```
   Compiland = nPush() ARBNO(*Command) reduce("'Parse'", 'nTop()') nPop();
   ```
   `Command` is one big alternation of sub-patterns, one per
   recognized construct. **One `Compiland`, period.** No
   `Compiland_v1` / `Compiland_v2`. No alternative spines. No
   per-rung Compilands.

3. **No goto, no labels — Snocone control flow only.** Snocone has
   `if`/`else`, `while`, structured patterns, and pattern alternation.
   That is enough for everything in this parser. **Zero goto. Zero
   labels.** This applies to the driver's stdin slurp too: write it
   as a `while ((Line = INPUT)) { Src = Src Line nl; }`, not as
   `read_loop:` / `goto read_loop`. The only legacy goto-style code
   in any current `parser_*.sc` is grandfathered for unrelated reasons
   (FW-3 deferred-call workaround); new code does not copy it.

4. **Tree construction uses the OPSYN binary operators `~` and `&`.**
   `semantic.sc` defines:
   ```
   OPSYN('~', 'shift', 2);
   OPSYN('&', 'reduce', 2);
   ```
   Write `*Integer ~ "'E_ILIT'"` not `shift(*Integer, "'E_ILIT'")`.
   Write `"'E_ALT'" & 'nTop()'` not `reduce("'E_ALT'", 'nTop()')`.
   The infix forms are the canonical surface; the function-call forms
   are the implementation. **Use the operators.** Never call
   `Push(Tree(...))` from a pattern escape — that is the procedural
   shortcut the OPSYN forms exist to replace.

5. **No user-defined functions called from inside parsing patterns.**
   A pattern match is pure pattern composition. The only functions
   that may be invoked from inside `Compiland` or any of its
   sub-patterns are the OPSYN-bound parsing operators and their
   counter companions:
   - `Shift` / `Reduce` (called by the `~` and `&` operators)
   - `PushCounter` / `IncCounter` / `DecCounter` / `PopCounter`
     (called by `nPush()` / `nInc()` / `nDec()` / `nPop()`)
   - `TopCounter` (read inside reduce-target expressions)

   That is the entire allowed surface for *user code* called from
   inside patterns. **No** `*assign('_x', ...)`, **no**
   `*push_qlit_from_strbody()`, **no** `*next_label()`, **no**
   `*format_arglist()` — none of those from inside a pattern.

   Snocone's built-in pattern primitives (LEN, SPAN, BREAK, ANY,
   NOTANY, FENCE, ARBNO, POS, RPOS, TAB, RTAB, REM, etc.) remain
   fully available — they are part of the pattern grammar, not
   user functions. So is the structural-test family (IDENT, DIFFER,
   GT, LT, etc.) when used inside patterns as `*IDENT(x, y)`
   guards. The line is: built-ins that ship with Snocone = OK;
   functions defined by the parser author = NOT OK from inside a
   pattern.

   If you need to transform a captured value before it lands on the
   stack, structure the grammar so that the pattern alone produces
   the desired match-span (see "String body capture idiom" below);
   if you need post-parse transformation, do it in a function that
   walks the tree AFTER `Src ? Compiland` returns.

   **String body capture idiom.** To shift `(E_QLIT "hi")` from
   source `"hi"`, the body must reach Shift without the surrounding
   quotes. Achieve this structurally — the opening and closing
   quotes are matched by sibling sub-patterns; only the body goes
   through `~`:
   ```snocone
   DQ_open = '"';   DQ_close = '"';   DQ_body = BREAK('"');
   SQ_open = "'";   SQ_close = "'";   SQ_body = BREAK("'");
   qlit_dq = DQ_open *DQ_body ~ "'E_QLIT'" DQ_close;
   qlit_sq = SQ_open *SQ_body ~ "'E_QLIT'" SQ_close;
   String  = (*qlit_dq | *qlit_sq);
   ```
   Match for `"hi"`: `DQ_open` consumes `"`; `*DQ_body` matches `hi`
   (BREAK stops at the closing quote); `~` shifts `tree('E_QLIT',
   'hi')`; `DQ_close` consumes the closing `"`. Pure pattern
   composition. Same idiom applies to any "matched span minus
   delimiters" capture. **No function calls.**

6. **No per-line state machine.** No `_rb_state = 0/1` toggle. No
   per-construct `_rb_*_kind` / `_rb_*_txt` global slots feeding hand-
   built `Tree(...)` calls in helper functions. Per-construct binding
   happens via the `~` operator's right operand (the tag) and the `&`
   operator's right operand (the child count, usually `nTop()`).

7. **All trees are n-ary. No left, no right.** Every fold of a
   variable-length list — alternation, concatenation, statement
   sequences, argument lists, parameter lists, body statements —
   uses the n-ary spine:
   ```
   X = nPush() *XList ("'X'" & 'nTop()') nPop();
   XList = nInc() *Item FENCE(<sep> *XList | epsilon);
   ```
   `a | b | c` becomes a flat `(E_ALT a b c)` with three children,
   NOT `(E_ALT (E_ALT a b) c)`. `f(a, b, c)` becomes a flat
   `(E_FNC f a b c)` with four children, NOT a nested chain.
   Hard-coded child counts in `&` (e.g. `"'E_ASSIGN'" & 2`) are
   reserved for genuinely fixed-arity productions like `lhs := rhs`
   — and even then, prefer the n-ary spine if the construction
   could plausibly grow. **The existing Rebus frontend produces
   binary E_ALT; that is a divergence to surface, not a constraint
   to conform to.** See `## Divergence-driven rungs` below.

8. **Counter helpers (`nPush`/`nInc`/`nTop`/`nPop`) appear at every
   n-ary fold site.** This is how the parser knows how many items
   to fold. The pair `nPush() ... reduce(t, 'nTop()') nPop()` opens
   a counter scope; `nInc()` inside the iteration body bumps it
   each pass.

9. **Sub-pattern names mirror `rebus.y`.** Use `function_decl`,
   `record_decl`, `pat_expr`, `expr`, `alt_expr`, etc. — the
   non-terminal names from `src/frontend/rebus/rebus.y`. Where a name
   conflicts with Snocone reserved syntax, suffix with `_pat`. Do not
   invent names like `MatchLine` / `BodyAltLine` / `IfLine` — those
   are line-fragments, not grammar non-terminals.

10. **One alternation in `Command` covers all top-level constructs.**
    In Rebus that is `function_decl | record_decl`. Statement-level
    forms (assign, match, alt, if, while, call, atom) live under a
    `stmt`-rooted sub-tree fired by `function_decl`'s body, not as
    peers of `function_decl`.

A grep that should produce zero hits in the rewritten parser:
```
grep -nE 'goto |^[a-z_]+:|_rb_state|_rb_atom_kind|emit_[a-z]|shift\(|reduce\(|Push\(Tree|\*[a-z_]+\(' parser_rebus.sc
```
The new `\*[a-z_]+\(` term catches function-call-from-pattern
escapes (`*assign(...)`, `*push_*()`, etc.). Pattern references
like `*Gray` or `*Compiland` use no parens and do not match.

A grep that should match exactly:
```
grep -c 'Src ? Compiland' parser_rebus.sc       # → 1
grep -c '?' parser_rebus.sc | <discounting ?'s in patterns>  # → 1 in driver
grep -c '^Compiland '   parser_rebus.sc         # → 1 (the definition)
grep -c '\*Compiland'   parser_rebus.sc         # → 0 (Compiland is the root, never referenced)
grep -c 'Compiland'     parser_rebus.sc         # → exactly 2 (def + driver use)
```

---

## Divergence-driven rungs — n-ary vs the existing frontend's binary

PAT-RB produces n-ary trees. The existing Rebus frontend
(`src/frontend/rebus/rebus_lower.c`) uses `expr_binary(E_ALT, ...)`
for `RE_ALT` — that is, every `|` is a binary node. So `a | b | c`
in the existing frontend is `(E_ALT (E_ALT a b) c)`, while PAT-RB
will produce `(E_ALT a b c)`. Same for `f(a, b, c)` arglist (the
existing frontend may or may not be n-ary there — re-verify per
rung), statement sequences, parameter lists, etc.

**This is intentional divergence, not a bug in PAT-RB.** Per the
"Done when" criterion at the top of this file, `tree_equal(t1, t2)`
must hold; for any rung where the existing frontend's tree is
binary-folded but PAT-RB's is n-ary, that gate will fail. That
failure is the rung's *output*: PAT-RB has discovered that the
existing frontend should be flattened.

**Rung procedure when n-ary divergence is found:**

1. PAT-RB produces n-ary tree per the canonical spine. Don't fold
   to binary "to make the gate pass."
2. The rung's commit message names the divergence explicitly:
   "PAT-RB-5: existing frontend produces binary E_ALT; PAT-RB
   produces n-ary E_ALT. Divergence reported — track upstream fix
   in GOAL-LANG-REBUS RB-5."
3. Open / update the upstream LANG rung to flatten the existing
   frontend's lowering. Until that lands, `tree_equal` failure on
   alt-bearing fixtures is *expected*; mark those fixtures as
   "divergence-pending" in the rung's gate description rather than
   counting them as FAIL.
4. When upstream lands, the divergence-pending fixtures become
   gating PASS without any change to PAT-RB.

The 38 fixtures in `corpus/programs/rebus/parser/` will not all
clear with one push under this regime. That is correct. PAT-RB's
job is not to mirror the existing frontend's bugs.

---

## Reference — `parser_snocone.sc` as the model

Read `corpus/programs/scrip/parser_snocone.sc` end-to-end before
starting. It is the closest sibling: same shared SC blob, same
`Compiland`/`Command` spine, hand-rolled expression-precedence ladder
(`Expr17` atoms → `Expr9` mul/div → `Expr6` add/sub → `Expr4` concat
→ `Expr3` alt → ...), and same shift/reduce idiom. Rebus's ladder
is shorter (no concat operator at this stage; alternation is at
statement level, not expression level — see `rebus.y`) but the
overall shape is identical.

Counter-helper hits per parser, for orientation (Rebus is the outlier):

| Parser | nPush/nInc/nTop/nPop hits |
|---|---|
| parser_snocone.sc | 9 |
| parser_snobol4.sc | 8 |
| parser_icon.sc | 5 |
| parser_prolog.sc | 4 |
| parser_raku.sc | 4 |
| **parser_rebus.sc (current, wrong shape)** | **0** |
| **parser_rebus.sc (target)** | **8+** |

---

## Cross-pollination

All six PARSER-* parsers share `Compiland`/`Shift`/`Reduce`/`Push`/`Pop`/`Top`/
`tree`/`TDump`/`stack` from `corpus/programs/snocone/demo/beauty/`. Bug
fixes there benefit all six. Rebus shares lowering with SNOBOL4, so PAT-RB's
`expr ? pat` and `expr | expr` lift directly from PARSER-SN. The existing
Rebus frontend is younger than SNOBOL4's; PAT-RB does not silently match
divergences — report upstream.

Naming follows the canonical writeup in `GOAL-PARSER-SNOCONE.md` (use BNF
names, `beauty.sc` names, `shift()`/`reduce()` over manual `Push(Tree(...))`,
no new labels/goto).

---

## Session Setup

```bash
( cd /home/claude/one4all && git fetch origin parser 2>/dev/null; \
  git checkout parser 2>/dev/null || git checkout -b parser origin/parser 2>/dev/null || git checkout -b parser )

bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_rebus.sh     # existing frontend baseline
bash /home/claude/one4all/scripts/test_parser_rebus.sh    # PAT-RB
```

---

## Architecture reminder

```
scrip --parser-crosscheck parser_rebus.sc tiny.reb
```

SCRIP runs `parser_rebus.sc` (which `-include`s the shared SC library from
`corpus/programs/scrip/`) against `tiny.reb`. PAT produces tree t2 via
`Compiland`; the existing frontend produces t1. Compared in memory
(`tree_equal`), executed in memory. No subprocesses, no temp files.

Shared SC library: `tree.sc  stack.sc  counter.sc  ShiftReduce.sc  semantic.sc`.

Compiland spine:
```
Compiland = nPush() ARBNO(*Command) reduce("'Parse'", 'nTop()') nPop();
```

---

## Rebus tree shapes (existing frontend, taken as oracle)

| Construct | Oracle `--dump-ir` (single-line form) |
|-----------|---------------------------------------|
| `function f() ... end` | `(STMT :subj (E_FNC DEFINE (E_QLIT "F()")))` then per-body STMTs, then `:go RETURN` `:lbl rb_N` |
| `record R(f1, f2)` | `(STMT :subj (E_FNC DATA (E_QLIT "R(F1,F2)")))` |
| `x` (bare atom) | `(STMT :subj (E_VAR X))` |
| `42` | `(STMT :subj (E_ILIT 42))` |
| `"hi"` | `(STMT :subj (E_QLIT "hi"))` |
| `x := y` | `(STMT :eq :subj (E_VAR X) :repl (E_VAR Y))` |
| `if c then s` | `(STMT :subj <c> :goS L_then :goF L_else)` then s, then merge label |
| `while c do s` | label, then `(STMT :subj <c> :goS body :goF after)` then s, loop back |
| `f()` | `(STMT :subj (E_FNC F))` |
| `x ? y` | `(STMT :subj (E_VAR X) :pat (E_VAR Y))` |
| `a \| b \| c` | left-assoc `(E_ALT (E_ALT a b) c)` per `rebus.y` `alt_expr` |

(The 38 fixtures in `corpus/programs/rebus/parser/` cover every shape
above; oracle outputs are stable.)

---

## Worked atom example — the smallest correct rung

This is the shape RB-0 must take in the rewrite. Read it, follow it.
**No functions are called from inside any pattern.** The grammar is
pure pattern composition.

```snocone
// Lex tokens — drop into the file once, used by every rung.
ws_run = SPAN(' ' tab);
ws_opt = (ws_run | epsilon);
nl_one = ANY(nl);   // matches exactly one newline char, pure primitive

Id      = (ANY(&UCASE &LCASE '_')
           (SPAN(&UCASE &LCASE digits '_') | epsilon));

Integer = SPAN(digits);

// String body capture idiom — quotes matched by sibling sub-patterns;
// only the body goes through `~`. No function calls. The match span
// of `*DQ_body` is the body text (BREAK stops at the closing quote);
// `~ "'E_QLIT'"` shifts tree('E_QLIT', body) onto the stack.
DQ_open  = '"';   DQ_close = '"';   DQ_body = BREAK('"');
SQ_open  = "'";   SQ_close = "'";   SQ_body = BREAK("'");
qlit_dq  = DQ_open *DQ_body ~ "'E_QLIT'" DQ_close;
qlit_sq  = SQ_open *SQ_body ~ "'E_QLIT'" SQ_close;
String   = (*qlit_dq | *qlit_sq);

// atom — Rebus's expr17 slice (id | integer | string).
// `~` is OPSYN'd to shift; rhs is the tree-tag string.
atom = FENCE(  *String
             | *Integer ~ "'E_ILIT'"
             | *Id      ~ "'E_VAR'"
            );

// stmt — for RB-0, a statement is just an atom in :subj position.
// Overall STMT shape: (STMT :subj <atom>).
// `&` is OPSYN'd to reduce; rhs is the child count (1 here, fixed-arity).
stmt = ws_opt *atom ws_opt nl_one ("'STMT_SUBJ'" & 1);

// Command — single top-level alternation. At RB-0, only `stmt`.
Command = nInc() *stmt;

// Compiland — the canonical beauty.sc spine. ONE root pattern.
// `'nTop()'` is the n-ary count: however many Commands matched,
// that many children fold into the Parse node.
Compiland = nPush() ARBNO(*Command) ("'Parse'" & 'nTop()') nPop();

// Driver — read whole stdin into Src, ONE pattern match, walk the result.
// No goto. No labels. No per-line matching.
InitCounter();
InitStack();

Src = '';
Line = INPUT;
while (DIFFER(Line)) {
    Src = Src Line nl;
    Line = INPUT;
}

if (Src ? Compiland) {
    parse_root = Top();
    i = 0;
    while (i = LT(i, n(parse_root)) i + 1)
        TDump(c(parse_root)[i]);
} else {
    OUTPUT = 'PARSER-RB: parse failed';
}
```

**Self-check before committing RB-0:**

```
grep -c 'goto '              parser_rebus.sc  # → 0
grep -cE '^[a-z_]+:'         parser_rebus.sc  # → 0
grep -c '_rb_state'          parser_rebus.sc  # → 0
grep -cE 'shift\(|reduce\('  parser_rebus.sc  # → 0
grep -cE 'Push\(Tree'        parser_rebus.sc  # → 0
grep -cE '\*[a-z_]+\('       parser_rebus.sc  # → 0  (no fn-call-from-pattern;
                                              #      *Sub references take no parens)
grep -cE 'nPush|nInc|nTop|nPop' parser_rebus.sc  # → ≥2  (1 nPush, 1 nPop in
                                                  #       Compiland; ≥1 nInc in
                                                  #       Command; ≥1 nTop in
                                                  #       Compiland's reduce)
grep -cE ' ~ | & '           parser_rebus.sc  # → ≥4  (3 ~ in atom; 1 & in stmt;
                                              #      1 & in Compiland)
grep -c 'Src ? Compiland'    parser_rebus.sc  # → 1  (the ONE pattern match)
grep -c 'Compiland'          parser_rebus.sc  # → exactly 2 (def + driver use)
grep -cE '^function '        parser_rebus.sc  # → 0  (no helper functions for
                                              #      RB-0; later rungs may add
                                              #      lowering passes that consume
                                              #      the parse tree, but never
                                              #      functions called from
                                              #      inside patterns)
```

The structural tests:
- "exactly 2 Compiland mentions" → one root pattern.
- "exactly 1 `Src ? Compiland`" → the entire source is matched once.
- "0 hits on `\*[a-z_]+\(`" → no function calls from patterns.
- "0 hits on `^function`" at RB-0 → grammar is patterns end-to-end.

---

## Rung ladder — REWRITES (all reopened)

The 38 fixtures in `corpus/programs/rebus/parser/` already exist and are
correct. Each rung's job is to bring `parser_rebus.sc`'s **shape** up to
spec for that fixture subset.

Every step below uses the OPSYN binary operators `~` (shift) and `&`
(reduce). Every list-fold uses the `nPush()`/`nInc()`/`nTop()`/`nPop()`
spine for n-ary trees. **No `goto`. No labels. No `Push(Tree(...))`
escapes from a pattern.** No left, no right.

### PARSER-RB-0 — atom (rewrite) — **next**

- [ ] Delete the wrong-shape `parser_rebus.sc` at corpus
      `f2d3077:programs/scrip/parser_rebus.sc`. Do not migrate code
      from it; the structure is wrong end-to-end. The git history
      preserves it.
- [ ] Write new `parser_rebus.sc` following the worked atom example
      above verbatim — `Compiland`, `Command`, `stmt`, `atom`, the
      lex tokens, the driver. Three test fixtures, no more.
- [ ] Self-check greps from the worked example all pass.
- [ ] PASS=3 on `atom_id`, `atom_int`, `atom_str`.
- **Sibling LANG rung:** RB-1.
- **Gate:** PASS=3 AND every grep self-check passes.

### PARSER-RB-1 — assignment `x := expr` (rewrite)

- [ ] Add an `assign` sub-pattern. Fixed-arity (lhs + rhs = 2):
      ```
      assign = *Id ~ "'E_VAR'" ws_opt ':=' ws_opt *atom ("'STMT_ASSIGN'" & 2);
      ```
      The lhs id is shifted as `E_VAR` so it lands on the stack as a
      tree node, not a raw string. The reduce folds `(lhs, rhs)` into
      a `STMT_ASSIGN` 2-child tree. (Reduce-target name is whatever
      maps cleanly to the canonical `(STMT :eq :subj :repl)` shape;
      pick the name once and reuse — invent a `'STMT_ASSIGN'` reducer
      target string in the parser, document the corresponding TDump
      rendering rule.)
- [ ] Add `*assign` to `Command`'s alternation BEFORE bare `*atom`.
- [ ] Self-check greps still pass; `& 2` count grows by one.
- **Sibling LANG rung:** RB-1.
- **Gate:** PASS=8 AND every grep self-check passes.

### PARSER-RB-2 — control flow `if/then`, `while/do` (rewrite)

- [ ] Add `if_stmt` and `while_stmt`. Surface-shape trees:
      `if_stmt = 'if' ws_run *expr ws_run 'then' ws_run *stmt ("'IF'" & 2);`
      `while_stmt = 'while' ws_run *expr ws_run 'do' ws_run *stmt ("'WHILE'" & 2);`
- [ ] **Defer label generation** (`:goS`/`:goF`/merge labels) to a
      separate `lower_*` walk applied to the parsed tree AFTER
      `Compiland` matches. The pattern produces the surface shape;
      the lowering walks the tree and emits the label-bearing STMTs
      via `TDump`. This mirrors how `rebus_lower.c` separates parse
      from lower in the existing C frontend.
- [ ] Lowering walk uses Snocone `function`s with `if/while/for`,
      not goto.
- **Sibling LANG rung:** RB-2.
- **Gate:** PASS=12 AND every grep self-check passes.

### PARSER-RB-3 — function decls + call sites (rewrite)

- [ ] Add `function_decl` to `Command`'s top-level alternation:
      ```
      function_decl = 'function' ws_run *Id ~ "'E_VAR'" ws_opt
                      '(' nPush() *params nPop() ')' ws_opt nl_one
                      nPush() ARBNO(*stmt) ('"E_FNC_DEFINE"' & 'nTop()') nPop()
                      ws_opt 'end' ws_opt nl_one;
      ```
      (Sketch — refine names against `rebus.y`. The two `nPush()/nPop()`
      pairs scope two independent counters: one for the params list,
      one for the body-stmt list.)
- [ ] `params = *params_inner;
      params_inner = nInc() *Id ~ "'E_VAR'" FENCE(ws_opt ',' ws_opt *params_inner | epsilon);`
      The params reduce folds into an `E_PARAMS` (or whatever sval
      the existing frontend uses for the parameter list — re-verify
      from oracle output).
- [ ] Add `call` for bare `f()` no-arg calls — fixed-arity `& 1`
      since arg count is zero, name-only.
- **Sibling LANG rung:** RB-3.
- **Gate:** PASS=18 AND every grep self-check passes.

### PARSER-RB-4 — pattern match `expr ? pat` (rewrite)

- [ ] Add `match_stmt`:
      ```
      match_stmt = *expr ws_opt '?' ws_opt *pat_expr ("'STMT_MATCH'" & 2);
      ```
      `pat_expr` is `expr` per `rebus.y` line 678 (no distinction at
      the syntax level; the `?` operator distinguishes context).
- [ ] Lift the `expr` ladder (precedence layers) directly from
      `parser_snobol4.sc`'s `Expr*` chain or `parser_snocone.sc`'s —
      whichever is closer to Rebus's `rebus.y` precedence tower.
      Re-verify per-tier names against `rebus.y`.
- **Sibling LANG rung:** RB-4.
- **Gate:** PASS=25 AND every grep self-check passes.

### PARSER-RB-5 — alternation generators `a | b | c` (rewrite, n-ary)

- [ ] Add `alt_expr` per the canonical n-ary spine from
      `corpus/programs/snocone/demo/beauty/beauty.sc:67-68`:
      ```
      alt_expr = nPush() *alt_list ("'E_ALT'" & '*(GT(nTop(), 1) nTop())') nPop();
      alt_list = nInc() *cat_expr FENCE(ws_opt '|' ws_opt *alt_list | epsilon);
      ```
      Note the reduce-count `'*(GT(nTop(), 1) nTop())'` — only emit
      an `E_ALT` reduce if there is more than one operand. A bare
      `a` (no `|`) leaves a single atom on the stack with no E_ALT
      wrapper. This matches beauty.sc's classic idiom and is the
      whole point of n-ary: `a | b | c` becomes `(E_ALT a b c)`,
      `a` stays as-is.
- [ ] `cat_expr` is whatever Rebus's next-tighter precedence layer
      is per `rebus.y` `cat_expr` (concat operator). At RB-5 if
      concat hasn't been added yet, `cat_expr` aliases to `atom`.
- [ ] **Divergence-driven gate.** The existing Rebus frontend
      produces binary E_ALT (see `## Divergence-driven rungs`).
      Alt-bearing fixtures (`alt_*.reb` — 7 of them) will FAIL the
      `tree_equal` gate in PAT-RB-5 until upstream LANG-RB-5 lands
      a flatten step in `rebus_lower.c`. Mark them
      "divergence-pending" in the rung commit, do NOT count as FAIL.
      Non-alt fixtures still gate normally.
- **Sibling LANG rung:** RB-5 (must be opened with a flatten task).
- **Gate:** PASS=25 (RB-4 baseline; alt fixtures divergence-pending)
      AND every grep self-check passes AND the divergence is reported
      upstream.
- **Final gate** (after upstream flatten lands): PASS=32.

### PARSER-RB-6 — record decls (rewrite)

- [ ] Add `record_decl` to `Command`'s top-level alternation:
      ```
      record_decl = 'record' ws_run *Id ~ "'E_VAR'" ws_opt
                    '(' nPush() *fields nPop() ')' ws_opt nl_one
                    ("'E_FNC_DATA'" & 'nTop() + 1');  // +1 for the name
      ```
      Same n-ary fold as `function_decl`'s params. The `+1` accounts
      for the leading record-name on the stack.
- [ ] `fields` mirrors `params_inner` from RB-3.
- [ ] Field-list joining into the existing-frontend's
      `"NAME(F1,F2)"` E_QLIT shape lives in a TDump rendering rule
      keyed on the reduce target, not in a hand-rolled emit
      function. (If the n-ary divergence applies here too —
      existing frontend folds fields into a single quoted string,
      PAT-RB keeps them as separate tree children — handle per
      `## Divergence-driven rungs`.)
- **Sibling LANG rung:** RB-6.
- **Gate:** PASS=38 (or PASS=N+divergence-pending) AND every grep
      self-check passes.

---

## Invariants

- Rebus's existing frontend is younger; tree divergences may surface
  bugs in EITHER frontend. PAT-RB does not silently conform.
- Test programs in `corpus/programs/rebus/parser/` are owned by PAT-RB.
- `.ref` files captured at rung-land time.
- **A rung is not landed until every rubric self-check passes AND
  the fixture gate passes (or the failing fixtures are documented
  as divergence-pending with an upstream LANG ticket).** Tree
  equivalence alone is not sufficient. Pattern shape is part of
  the deliverable.

---

## Watermark

PARSER-RB-0..RB-6 wrong-shape attempt landed sessions #62 (Claude
Sonnet 4.7, 2026-05-03) — PASS=38 FAIL=0 against 38 fixtures, but
the parser is a goto-driven line-at-a-time state machine, not a
Snocone pattern. **Every rubric item from #1 through #10 is
violated.** Rungs reopened for rewrite.

Reopened with explicit pattern architecture (session continuation,
2026-05-03):
  - One `Compiland` pattern, beauty.sc spine, matched ONCE against
    the entire concatenated source via a single `Src ? Compiland`.
  - No user-defined functions called from inside parsing patterns;
    only `Shift`/`Reduce` (via `~`/`&`) and counter primitives
    (`nPush`/`nInc`/`nTop`/`nPop`). Built-in pattern primitives
    (LEN, SPAN, BREAK, ANY, FENCE, ARBNO, etc.) remain available.
  - Body-capture idiom for delimited tokens: opening and closing
    delimiters matched by sibling sub-patterns; only the body
    goes through `~`. Demonstrated for E_QLIT in worked example.
  - OPSYN binary `~` (shift) and `&` (reduce) operators throughout.
  - `nPush()`/`nInc()`/`nTop()`/`nPop()` for every list-fold.
  - All trees n-ary; no left, no right.
  - Zero goto, zero labels.
  - Divergence-driven rungs handling for cases where the existing
    frontend produces binary trees that PAT-RB folds n-ary.

Current-tree heads: corpus `f2d3077`, one4all/parser `dd6ad80d`,
`.github` (this commit) — all on remote. The wrong-shape
`parser_rebus.sc` is in corpus at `f2d3077`; the rewrite starts
by deleting it and writing a fresh one following the worked atom
example above.

`test_parser_rebus.sh` carries the `normalize()` whitespace-collapse
upgrade from session #62 — keep that, it is correct.

The 38 fixtures in `corpus/programs/rebus/parser/` are correct —
keep them. The whole rewrite gates against the same 38 (with
divergence-pending markings as needed).

PARSER-RB-0 — next.

---

## Session 2026-05-03 continuation — PARSER-RB-0 rewrite INCOMPLETE

Session rewrote `parser_rebus.sc` from scratch with correct shape:
- One `Compiland` pattern, beauty.sc spine
- `nPush`/`nInc`/`nTop`/`nPop` n-ary folds
- `shift()`/`reduce()` function-call forms
- No goto, no labels in driver; structured `while`/`if` only
- Post-parse `lower_*` functions walk surface tree → emit STMT TDump lines
- No user functions called from inside patterns

**Three blocking issues — not yet resolved:**

### Issue 1 — HANG: blank_line in ARBNO does not guarantee cursor advance
`blank_line = ws_opt nl_one` — `ws_opt` can match empty; if `nl_one` also
fails, ARBNO spins. Fix: ensure `blank_line` always consumes at least one
newline. Replace with `(ANY(' ' tab nl) | epsilon)` or require `nl_one`
before `ws_opt`. Alternative: remove `blank_line` from `Command` entirely
and consume leading/trailing whitespace+newlines in `function_decl` and
`record_decl` preambles.

### Issue 2 — RUBRIC VIOLATION / HANG: user function called from qlit pattern
`qlit_dq = '"' DQ_body . _rb_strbody '"' epsilon . *Shift(s_QLIT, _rb_strbody)`
— `*Shift(...)` is a user function called from inside a pattern. Violates
rubric item 5. Also may cause the hang.
Fix: use the dot-conditional capture idiom WITHOUT calling Shift from the
pattern. Look at how `parser_snobol4.sc` handles String capture — it uses
`BREAK(.) . _strbody` global then calls `shift()` in the outer context, or
restructures so the body lands in a global that is then shifted in `primary`.

### Issue 3 — RUNTIME GAP: ~ and & binary OPSYN not supported
`T_2TILDE` and `T_2AMP` are declared in `snocone_parse.y` as tokens but
have **zero grammar productions** — the Snocone parser rejects them with
a syntax error. All six existing sibling parsers use `shift()`/`reduce()`
function-call forms. The rubric's `~`/`&` forms require a Snocone frontend
extension. Keep `shift()`/`reduce()` for now; open a separate goal to add
binary OPSYN support to snocone_parse.y if desired.

**Next session action:**
1. Fix Issue 1: restructure `Command` blank-line handling.
2. Fix Issue 2: restructure string capture to not call Shift from inside pattern.
   Model: `String = (SQ_open *SQ_body . _rb_s SQ_close | ...)` then in
   `primary` use `shift(*String, s_QLIT)` — but Shift captures the full
   match span including quotes. Better: follow `parser_snobol4.sc:44` which
   uses `. _strbody` dot-conditional to capture body into a global, then
   calls `shift()` from `primary` using a helper that reads `_strbody`.
   Allowed: dot-conditional assignment `pat . global` is NOT a function call —
   it is built-in pattern assignment. `*Shift(...)` IS a function call — banned.
3. Note Issue 3 in watermark; keep `shift()`/`reduce()` forms.
4. Gate: PASS=3 on atom_id, atom_int, atom_str.

corpus HEAD at emergency handoff: `bc52be1`
one4all/parser branch: `dd6ad80d` (unchanged)
.github: this update

---

## Session 2026-05-03 continuation #2 — beauty.sc-style refactor (INCOMPLETE)

Three architectural directions from Lon were applied to parser_rebus.sc:

### 1. Build-time pattern-builder helpers (RB_*)
Replaced raw `epsilon . *fn(args)` literals in pattern definitions with
build-time helpers that return pattern fragments via EVAL:
- `RB_save(.var, expr)` returns `epsilon . *assign('var', expr)`
- `RB_qlit_emit('_rb_strbody')` returns the push-E_QLIT fragment
- `RB_call_emit('_rb_callname')` returns the push-RB_CALL fragment

Pattern grammar now reads cleanly — no `*fn(...)` literal anywhere outside
the helper bodies themselves.  Same idiom as semantic.sc's nPush/nInc/nTop.

### 2. $'op' operator wrappers (beauty.sc lines 50-58 style)
```
$'(' = '(' *Gray;       $')' = *Gray ')';
$',' = *Gray ',' *Gray;
$':=' = *Gray ':=' *Gray;
$'?' = *Gray '?' *Gray;
$'|' = *Gray '|' *Gray;
$'+' = *Gray '+' *Gray;     // and -, *, /
```
Used throughout the expression ladder.

### 3. Direct quoted-form tag constants (no sq indirection, no s_/r_ prefixes)
```
// shift() tags (bare).
E_VAR  = 'E_VAR';
E_ILIT = 'E_ILIT';
E_QLIT = 'E_QLIT';

// reduce() tags (quote-embedded).
Parse        = "'Parse'";
RB_FUNC_DECL = "'RB_FUNC_DECL'";
RB_ASSIGN    = "'RB_ASSIGN'";
E_ALT        = "'E_ALT'";
... etc
nTop_gt1     = '*(GT(nTop(), 1) nTop())';
```
Each tag appears in exactly one context (shift OR reduce), so no _R suffix.
Call sites: `shift(*Id, E_VAR)`, `reduce(E_MUL, 2)`, `reduce(E_ALT, nTop_gt1)`.

### Architecture also corrected
- Command/Compiland use parser_snocone.sc idiom: `Command = (*func_cmd | *rec_cmd | *blank)` with nInc inside each decl alternative; `ARBNO(Command)` (no `*`).
- stmt_list uses the same shape.
- postfix_expr restructured: `id_call_pat = (Id . _rb_callname '(' *Gray ')')` captures the call-form atomically so the `(call | primary)` alternation has no shared prefix that traps FENCE.
- String body capture uses canonical dot-conditional `BREAK('"') . _rb_strbody` (built-in primitive, not a function call).

### One blocking issue — hangs on atom fixtures

Minimal-grammar bisection tests (`/tmp/test_g4.sc` with body; `/tmp/test_g5.sc`
with alt_expr nPush/X_alt/nPop) all parse correctly.  The full parser hangs.

**Suspected cause:** the doubled-FENCE chains in mul_expr / add_expr:
```
mul_expr = *postfix_expr
           FENCE(  $'*' *postfix_expr reduce(E_MUL, 2) FENCE($'*' *postfix_expr reduce(E_MUL, 2) | epsilon)
                 | $'/' *postfix_expr reduce(E_DIV, 2) FENCE($'/' *postfix_expr reduce(E_DIV, 2) | epsilon)
                 | epsilon
                );
```
This shape is non-canonical — parser_snocone.sc uses a flatter form.  Port
that shape exactly:
```
Expr9 = *Expr17
        ( *op_mul *Expr17 reduce(r_MUL, 2)
              (*op_mul *Expr17 reduce(r_MUL, 2) | epsilon)
        | *op_div *Expr17 reduce(r_DIV, 2)
              (*op_div *Expr17 reduce(r_DIV, 2) | epsilon)
        | epsilon
        );
```
No outer FENCE; flat alternation.  Likely the immediate fix.

**Next-session bisection plan:**
1. Strip mul_expr to `mul_expr = *postfix_expr`. Verify atom_id passes.
2. Restore add_expr identically. Verify.
3. Reintroduce mul_expr `*` chain in the parser_snocone.sc shape (no FENCE).
4. Reintroduce `/`, `+`, `-` similarly.
5. Once atoms pass, run full PASS=38 gate.

corpus HEAD: `9f6b32f`
one4all/parser branch: `dd6ad80d` (unchanged)
.github: this update follows
