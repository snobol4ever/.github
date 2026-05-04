# GOAL-PARSER-SNOBOL4.md — PARSER-SNOBOL4 pattern-based frontend in Snocone

**Repo:** corpus+one4all
**Branch:** `parser` (one4all only — `corpus` and `.github` stay on `main`)
**Sibling ladder:** `GOAL-LANG-SNOBOL4.md` — every PARSER-SN-N rung names its
sibling SN-K rung(s). The existing SNOBOL4 frontend (`src/frontend/snobol4/`)
is the oracle; PARSER-SN is a second frontend that must agree with it.

**Done when:** A Snocone program `parser_snobol4.sc` reads SNOBOL4 source,
runs one `Compiland` PATTERN that builds the canonical IR tree, and for
every test program in the rung corpus the parser's output matches the
existing frontend's `--dump-parse` output (whitespace-normalized per
FW-6 variant B).

> **Cross-pollination notice (session #62, 2026-05-03):** three design
> issues raised against PAT-IC apply to all six PARSER-* frontends.
> See `GOAL-PARSER-ICON.md ## Design issues` (D1–D3). Tracked under
> PARSER-IC-INFRA-1/-2 — when those land, the same refactor lands here.

---

## Cross-pollination

All six PARSER-* parsers share `Compiland`/`Shift`/`Reduce`/`Push`/`Pop`/`Top`/
`tree`/`TDump`/`stack` from `corpus/programs/scrip/`. Bug fixes there
benefit all six. Token-level rules and the `Command` body are language-
specific; the spine is identical:

```
Compiland = nPush() ARBNO(<inlined Command body>) reduce("'Parse'", 'nTop()') nPop()
```

PARSER-SN gets two oracles: the existing SNOBOL4 frontend (in-process
crosscheck) AND the SPITBOL byte-identical oracle from `GOAL-LANG-SNOBOL4`.
It is the safest place to start the family.

---

## Naming & Design Principles  (canonical writeup in GOAL-PARSER-SNOCONE.md)

PARSER-* parsers must use names from:

1. The official BNF for the language being parsed. For SNOBOL4 this is
   `corpus/programs/ebnf/s4-no.ebnf` (and beauty.sno's Expr-N tier names
   `Expr`, `Expr0..Expr17`, plus atom rules `Id`, `Integer`, `Real`,
   `String`, etc.).
2. The canonical Snocone self-host `beauty.sc` when the concept matches
   (`Integer`, `String`, `Id`, `Gray`, `White`, `$'='`, etc.).
3. `shift()`/`reduce()` from `ShiftReduce.sc` rather than manual
   `Push(Tree(...))` inside pattern escapes.
4. No new labels and goto unless absolutely necessary for readability.

**Operational oracle wins where canonical BNF and existing frontend
disagree.** beauty.sno's arith rules are right-recursive; `snobol4.y` and
`--dump-parse` are left-associative. PARSER-SN follows the oracle (left-
associative iterative folding) but keeps beauty.sno's tier names.

---

## Session Setup

```bash
( cd /home/claude/one4all && git fetch origin parser 2>/dev/null; git checkout parser 2>/dev/null || git checkout -b parser origin/parser 2>/dev/null || git checkout -b parser )

bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_snobol4.sh    # existing frontend baseline
bash /home/claude/one4all/scripts/test_scrip.sh            # INFRA watermark
bash /home/claude/one4all/scripts/test_parser_snobol4.sh   # PARSER-SN gate
```

---

## Architecture

```
scrip --pat-snobol4 tiny.sno
         │
         ├─→ existing SNOBOL4 frontend  → CODE_t* t1   (in-process)
         │
         └─→ parser_snobol4.sc Compiland  → CODE_t* t2 (in-process, Snocone)

normalized stdout (parser TDump) ≡ normalized stdout (--dump-parse)  ← gate
```

Long-term, the gate becomes `tree_equal(t1, t2)` via the planned
`scrip --parser-crosscheck` flag (FW-4, deferred). Today it is shell-level
byte-diff with whitespace normalization on both sides.

The driver builds Snocone trees on the shared stack via `Push`/`Pop` from
`stack.sc` and `Tree(...)` from `tree.sc`; the main loop pops each STMT
tree and dumps it via `TDump` from `tdump.sc`.

**Shared SCRIP runtime, Snocone-hosted (`.sc` files)** — all six PARSER
sessions use the same blob. Only `parser_<lang>.sc` changes per session.
Canonical blob order:

```
global.sc tree.sc stack.sc counter.sc ShiftReduce.sc semantic.sc
qize.sc gen.sc tdump.sc assign.sc parser_<lang>.sc
```

**Role-slot / flag wrapper convention** — scrip's `--dump-parse` emits
role-keyword children (`:subj`, `:repl`, `:lbl`, `:pat`, ...) and positional
flags (`:eq`, `:end`). The Snocone `tree(t,v,n,c)` shape doesn't carry
per-child role labels, so we encode roles as wrapper nodes with `:`-prefixed
type tags. `Tree(':subj', '', 1, child)` renders as `:subj <TLump-of-child>`.
`tree(':eq', '')` renders as bare `:eq`. IR-leaf kinds (`E_VAR`, `E_ILIT`,
`E_QLIT`) self-paren in `TValue` so a slot wrapping an IR leaf renders as
`:subj (E_VAR x)`.

---

## SNOBOL4 → existing-frontend tree shapes (the oracle)

Captured from `scrip --dump-parse` on the rung corpus.

| Construct | Existing frontend tree (canonical line) |
|-----------|-----------------------------------------|
| identifier `x`              | `(STMT :subj (E_VAR x))` |
| integer `42`                | `(STMT :subj (E_ILIT 42))` |
| string `'hi'`               | `(STMT :subj (E_QLIT "hi"))` (always double-quoted in dump) |
| `END` line at column 0      | `(STMT :lbl END :end)` |
| `x = 5`                     | `(STMT :eq :subj (E_VAR x) :repl (E_ILIT 5))` |
| `x = 'a' 'b'`               | `(STMT :eq :subj (E_VAR x) :repl (E_SEQ ...))` |
| `S 'a'`                     | `(STMT :subj (E_VAR S) :pat (E_QLIT "a"))` |
| `S 'a' 'b'`                 | `(STMT :subj (E_VAR S) :pat (E_SEQ (E_QLIT "a") (E_QLIT "b")))` |
| `S 'a' \| 'b'`              | `(STMT :subj (E_ALT (E_SEQ (E_VAR S) (E_QLIT "a")) (E_QLIT "b")))` (alt eats LHS) |
| `S ('a' \| 'b')`            | `(STMT :subj (E_VAR S) :pat (E_ALT ...))` (paren keeps split) |
| `S 'a' . X`                 | `(STMT :subj (E_VAR S) :pat (E_CAPT_COND_ASGN ...))` |
| `S 'a' $ X`                 | `(STMT :subj (E_VAR S) :pat (E_CAPT_IMMED_ASGN ...))` |
| `S 'a' = 'b'`               | `(STMT :eq :subj (E_VAR S) :pat ... :repl ...)` |
| `S = `  (empty repl)        | `(STMT :eq :subj (E_VAR S) :repl (E_QLIT ""))` |
| `S 'a' :S(L1)`              | `(STMT :subj (E_VAR S) :pat ... :goS L1)` |
| `LEN(3)` etc.               | `(E_LEN (E_ILIT 3))` — also E_BREAK, E_SPAN, E_ANY, E_NOTANY |
| `F(X)` etc.                 | `(E_FNC F (E_VAR X))` — generic call; name in v, args as children |
| `DEFINE('F(X)')`            | `(E_FNC DEFINE (E_QLIT "F(X)"))` — DEFINE spec is opaque to --dump-parse (DEFINE-as-distinct-IR-kind tracked under `GOAL-IR-DEFINE-KIND.md`) |
| `NOARG()`                   | `(E_FNC NOARG)` — zero-arg call, no children |

**The `:subj` / `:pat` split rule:** parse the body as one expression. If
the top is `E_SEQ` with N≥2 children → child 1 is `:subj`, rest is `:pat`
(unwrap if N=2, otherwise wrap in fresh `E_SEQ`). Any other top (E_ALT,
single atom, E_CAPT_*, E_LEN/BREAK/SPAN/ANY/NOTANY, arith, ...) →
whole expression is `:subj`, no `:pat`.

**Operator precedence** (loose → tight): `|` < concat < `.`/`$` < `^/!/**`
< `*` < `/` < `+/-` < unary `+/-` < atom. `.` and `$` are left-associative
per the oracle (`'a' . X . Y` → `((a . X) . Y)`), even though `s4-no.ebnf`
writes them right-recursively.

---

## Closed rungs — historical record

Step-by-step detail, root-cause writeups, and session-narrative live in git
history under the listed commits. This table is the load-bearing summary.

### INFRA ladder — all GREEN

| Rung | Title | Summary |
|------|-------|---------|
| INFRA-0  | Conditional/immediate-assign capture lvalue bug | `eval_code.c E_CAPT_*_ASGN` E_VAR target path needed lvalue branch |
| INFRA-1  | SCRIP source tree | `corpus/programs/scrip/` + base `.sc` runtime files |
| INFRA-2  | `global.sc` | Named char constants, bit-prefix slices, `digits`, `TRUE`, `FALSE` |
| INFRA-3  | `tdump.sc` (tree printing) | `TLump` + `TValue` ported |
| INFRA-4  | `assign.sc` + `match.sc` | `assign(name, expr)`, membership |
| INFRA-5a | Synthetic-label collision | `snocone_parse.y` `g_sc_label_seq` made monotonic |
| INFRA-5b | `if (str ? PAT = )` in expression | `interp_eval.c E_ASSIGN` E_SCAN-as-lvalue branch |
| INFRA-5c | `E_KEYWORD` dropped in `E_FNC` arg | `eval_code.c` strip `&` on NV lookup |
| INFRA-6  | `case.sc` (lwr/upr/cap/icase) | Verbatim port from beauty/case.sc |
| INFRA-7  | `qize.sc` | Verbatim; tdump TValue uses SqlSQize |
| INFRA-7a | Inline `*assign(...)` not firing | `eval_pat.c` E_CAPT_*_ASGN cases |
| INFRA-8  | `trace.sc` | Verbatim; silent when doDebug=0 |
| INFRA-9  | `omega.sc` | Pattern-construction tracing wrapper |
| INFRA-10 | OPSYN `~` and `&` runtime | Function-call dispatch via APPLY works (→ INFRA-11b) |

### Framework rungs — landed

| Rung | Title | Summary |
|------|-------|---------|
| FW-1 | Generalize TValue for non-scrip-IR leaf kinds | Generic-leaf branch — any letter-start tag with non-empty v(x) → `(TAG val)`; E_QLIT keeps double-quote special branch |
| FW-2 | Multi-child role-slot wrapper | `:`-prefix branch in TLump for n≥2 children → `:role (c1 c2 ...)` |
| FW-3 | Compiland-spine driver loop | Whole-program `Src ? Compiland` match; **Command body inlined** inside ARBNO to dodge the `*Q` indirection bug (see workarounds below) |
| FW-6 | Multi-line TLump / TDump | **Variant B adopted**: TDump uses `gen.sc` width-budget inline-or-fallback, gates normalize whitespace |

### Language rungs — landed

| Rung | Title | Gate |
|------|-------|------|
| SN-0 | atom (literal \| identifier) | PASS=3 |
| SN-1 | assignment | PASS=8 |
| SN-2 | tree-on-stack architectural pivot | PASS=8 (refactor; same corpus) |
| SN-3 | concat / arith — beauty.sno-named Expr-N tiers | PASS=16 |
| SN-4 | control flow (`:S` / `:F` / labels) | PASS=23 |
| SN-5 | patterns (LEN/BREAK/SPAN/ANY/NOTANY, `\|`, `.`, `$`, replacement) | PASS=43 |
| SN-6 | function definition / call (generic `Id LPAREN args RPAREN` → E_FNC) | **PASS=58** ✅ this session |

---

## Active rung ladder

### ⚠ PARSER-SN-7 — canonical shape (session 2026-05-03 PIVOT)

**Context.** Session 2026-05-03 attempted to land the beauty.sno
crosscheck on top of the existing `parser_snobol4.sc` (876 lines,
SN-0..SN-6 PASS=58).  Diagnostic crosscheck revealed ~1084 oracle
stmts vs ~502 parser stmts on beauty.sno — the parser silently
collapses or drops most constructs (bracket-index, &keyword,
continuation lines, deferred `*Id`, comment/control lines, `;`
separator).  More importantly, the underlying shape is wrong
relative to beauty.sno's own self-host grammar AND relative to the
sibling parsers (PARSER-IC, PARSER-PR, PARSER-RK, PARSER-RB) that
have all landed since SN-6.

**The wrong shape.**  `parser_snobol4.sc` today drives parsing through
25 Snocone *functions* (`Expr0..Expr17`, `_try_label`,
`_parse_body_goto`, `_parse_line_cmd`, `_call_args`, ...) called
imperatively per line — `Compiland` is `ARBNO( ... LineCmd nl_one )`
where `LineCmd` captures one line into `_cur_line` and fires
`*_parse_line_cmd()`, which then calls `_try_label`, then
`_parse_body_goto`, which calls `Expr`, which dispatches through
the Expr-N tower.  This is a hand-coded recursive-descent parser
hosted on Snocone, not a Snocone PATTERN parser.

**The right shape (canonical, set by beauty.sno itself).**  beauty.sno's
own grammar — the model PARSER-SN must mirror — is one chained
PATTERN, all `~`/`&` infix (semantically Shift/Reduce), with
`Comment | Control | Stmt` as alternation children of `Command`,
and a single `Compiland` PATTERN that ARBNOs over `*Command`
against the entire source.  Functions exist only for `nPush/nInc/
nTop/nPop`, `Tree`, `Push`/`Pop`, `Shift`/`Reduce`, `pp`, `ss` —
tree-building and semantics — never for parsing dispatch.

The siblings PARSER-IC (672 lines), PARSER-PR (429 lines), PARSER-RK
(755 lines), PARSER-RB (547 lines) all land this shape today.
PARSER-SN at 876 lines is the largest and the only outlier.

**Invariants for the rewrite (all binding):**

1. **One `Compiland` PATTERN, one match against the entire `Src`.**
   The shape is: `Compiland = nPush() ARBNO( nInc() <inlined Command body> ) reduce("'Parse'", 'nTop()') nPop();`
   where the Command body is the alternation `Comment | Control | Stmt`.
   `Src ? Compiland` runs once at the bottom of the driver.  No
   per-line dispatch.

2. **`shift(p, t)` / `reduce(t, n)` from `semantic.sc` for tree
   construction inside patterns.**  These are the OPSYN'd binary
   `~` / `&` of beauty.sno — same semantics, called as functions
   because of INFRA-11b (the Snocone parser binds `~` as unary
   `not` at parse time, before runtime OPSYN takes effect).  Use
   `shift(P, "'identifier'")` everywhere beauty.sno writes
   `(P ~ 'identifier')`, and `reduce("'TAG'", N)` everywhere
   beauty.sno writes `("'TAG'" & N)`.

3. **`nPush()` / `nInc()` / `nTop()` / `nPop()` for n-ary trees.**
   Every grammar rule that produces a variable-arity child list
   (alternation, sequence, expression list, statement body) wraps
   the body in `nPush() ... reduce("'TAG'", 'nTop()') nPop()` and
   each contributing child fires `nInc()` immediately before its
   shift/reduce.  This matches the sibling parsers and beauty.sno
   exactly.

4. **No Snocone `goto` when structured control would do.**  The driver
   uses `while ((Line = INPUT)) { ... }` to accumulate `Src`,
   `if (Src ? Compiland) { ... }` for the single top-level match,
   and `while (LE(i, n_kids)) { ... }` to walk the Parse tree's
   children for `TDump`.  No labels, no `goto` anywhere.  This
   tracks the PARSER-PR style invariant ("no goto/labels in this
   file").

5. **Functions only for tree building and semantics.**  Allowed: the
   shared `tree.sc` / `stack.sc` / `counter.sc` / `ShiftReduce.sc`
   helpers; `Tree(...)` constructors; `assign(name, expr)` /
   `match(s, p)` / `icase(s)` / `lwr` / `upr` from beauty's reuse;
   small `*deferred()` escapes that capture text into a global
   slot or shape a node before pushing.  Forbidden: any function
   that drives parse dispatch (no `Expr0..Expr17`, no `_try_label`,
   no `_parse_body_goto`, no `_parse_line_cmd`).  The Expr-N tower
   becomes Expr-N PATTERNS with the same names (`Expr`, `Expr0`,
   ..., `Expr17`) — beauty.sno's own names — chained by FENCE'd
   alternation per the precedence ladder.

**The rewrite proceeds in narrow rungs, each gated by a focused
fixture in `corpus/programs/snobol4/parser/`.**  This re-uses the
existing 58 fixtures as regression coverage AND extends them.  Each
rung lands a slice of the grammar, shaped per the invariants above.

#### PARSER-SN-7-0 — scaffolding

- [ ] Open a feature branch `parser-sn-rewrite` off `parser`.  Keep
      the existing `parser_snobol4.sc` reachable on `parser` until
      the rewrite hits PASS=58 parity.
- [ ] Write `parser_snobol4_v2.sc` from scratch on the parser_prolog.sc
      / parser_icon.sc model.  Body: token-class atom recognizers
      (`Id`, `Integer`, `String`, `Real`, `White`, `Gray`), the
      Expr-N tower as PATTERNS (not functions), `Goto`, `Stmt`,
      `Comment`, `Control`, `Command`, `Compiland`, and the driver.
- [ ] Land the gate-script update: `test_parser_snobol4.sh` loads
      `parser_snobol4_v2.sc`.  Gate goal: ALL 58 existing fixtures
      pass under the new shape, no regressions.
- [ ] On parity → swap `parser_snobol4_v2.sc` → `parser_snobol4.sc`,
      delete the old, merge `parser-sn-rewrite` → `parser`.
- **Gate:** PASS=58 FAIL=0 on the new shape, byte-identical output.

#### PARSER-SN-7-1 — bare label-only line

- [x] Fixture `cf_label_bare.sno` added (session 2026-05-03 — open
      against existing parser, will pass automatically once SN-7-0
      lands the canonical Stmt pattern with `Label = BREAK(' ' tab nl ';') ~ 'Label'`).
- [ ] Confirm PASS=59 after SN-7-0.

#### PARSER-SN-7-2 — &KEYWORD recognition

- [ ] Fixtures `kw_fullscan.sno`, `kw_maxlngth.sno`, `kw_ucase.sno`,
      `kw_lcase.sno` — assignment LHS, RHS, and pattern-arg uses of
      protected and unprotected keywords.
- [ ] Per beauty.sno: `ProtKwd = '&' SPAN(&UCASE &LCASE) ~ 'ProtKwd'`,
      `UnprotKwd = '&' SPAN(&UCASE &LCASE) ~ 'UnprotKwd'`.  These
      become alternatives in `Expr14`.
- **Gate:** keywords emit `(E_KEYWORD <NAME>)` matching the oracle.

#### PARSER-SN-7-3 — bracket index `x[i]`, `x[i, j]`

- [ ] Fixtures `idx_simple.sno`, `idx_multi.sno`, `idx_nested.sno`,
      `idx_in_assign_lhs.sno`.
- [ ] Add `Expr15` / `Expr16` per beauty.sno: `Expr15 = Expr17 FENCE( nPush() Expr16 ("'[]'" & 'nTop() + 1') nPop() | epsilon )`.
- **Gate:** `(E_IDX <obj> <i> ...)` matches the oracle.

#### PARSER-SN-7-4 — `+` / `.` continuation lines

- [ ] Fixtures `cont_plus.sno`, `cont_dot.sno`, `cont_chain.sno`.
- [ ] Per beauty.sno's `White` definition: continuation is part of
      the whitespace token class, swallowed by `White` between every
      two adjacent grammar units.  Specifically: `White = SPAN(' ' tab) FENCE( nl ('+' | '.') FENCE( SPAN(' ' tab) | epsilon ) | epsilon ) | nl ('+' | '.') FENCE( SPAN(' ' tab) | epsilon )`.
- **Gate:** multi-line continued statements emit a single STMT.

#### PARSER-SN-7-5 — comment & control lines

- [ ] Fixture `mixed_comment_control.sno`.
- [ ] Per beauty.sno: `Comment = '*' BREAK(nl)`, `Control = '-' BREAK(nl ';')`.
      Both alternatives of `Command` shift their captured text via
      `*Comment ~ 'comment' ("'Comment'" & 1) nl`.  At TDump time these
      contribute STMT children — but the existing scrip frontend's
      `--dump-parse` drops comments and processes control lines via
      preprocessor-include semantics.  PARSER-SN-7-5 must
      either drop these STMT children at emit-time OR (cleaner)
      have `Command` not emit them — match whichever the oracle does.
- **Gate:** comment/control lines do not produce extra STMTs in dump.

#### PARSER-SN-7-6 — `*Id` deferred-pattern reference

- [ ] Fixtures `defer_simple.sno` (`P = *Q`), `defer_alt.sno` (`P = *Q | *R`),
      `defer_in_pat.sno` (`x ? *P`).
- [ ] `Expr14`'s prefix-`*` branch: `'*' Expr14 & "'*' 1"` — the
      unary `*` in beauty.sno's Expr14 alternation list.  Must render
      as `(E_DEFER <child>)` in the oracle's tree shape.
- **Gate:** `*Id` constructs emit `(E_DEFER (E_VAR Id))`.

#### PARSER-SN-7-7 — `;` mid-line statement separator

- [ ] Fixture `semi_separator.sno` (`x = 1 ;* comment` and `x = 1; y = 2`).
- [ ] Per beauty.sno's `Command`: alternation tail is `(nl | ';')`.
      Each Command consumes either a newline or a semicolon; multiple
      Commands per source line are supported.
- **Gate:** semi-separated statements emit two STMTs.

#### PARSER-SN-7-8 — beauty.sno full crosscheck

- [ ] `parser_snobol4_v2.sc` parses `beauty.sno` (627-line `corpus/programs/snobol4/demo/beauty/beauty.sno`).
- [ ] `tree_equal` against `--dump-parse`'s tree returns true (use
      whitespace-normalized byte-diff until PARSER-SN-FW-4 lands).
- [ ] Running the parser-built tree through `--ir-run` produces output
      byte-identical to the SPITBOL oracle (Milestone 1 gate).
- **Gate:** beauty.sno PASSES under both oracles.

### PARSER-SN-FW-4 — `scrip --parser-crosscheck` C-side flag (deferred)

- [ ] Add `--parser-crosscheck` flag to `scrip.c`. Reads two inputs:
      a `.sc` PARSER driver and a per-language source. Runs both
      frontends in-process; uses C-callable `tree_equal(CODE_t* a, CODE_t* b)`
      for structural compare; exposes Snocone `cross_emit_tree(t)` builtin
      to bridge Snocone's `struct tree { t, v, n, c }` to C-side IR.
- **Blocks:** PARSER-RK (whitespace-tolerant dump form). Others can use byte-diff.
- **Gate:** matching trees emit `OK`; PARSER-SN gate refactored to use it.

### PARSER-SN-FW-5 — root-cause TLump function-name slot wart (defensive)

- [ ] Reduce to a 4-line `.sc` repro: a function `f(x)` whose body ends
      with `f = literal f(child); return;` — does the recursive call clobber
      the parent frame's `f` slot? Bisect against the working line-63
      bracket form. Probable site: `interp_eval.c E_FNC` or `eval_code.c`
      E_ASSIGN/E_FNC interaction.
- [ ] On fix, revert the `sub`-local staging in `tdump.sc` and restore
      the canonical `TLump = TLump TLump(...)` shape.
- **Gate:** canonical shape works without staging; PARSER-SN gate stays green.

---

## Known scrip-Snocone runtime workarounds

These are real runtime bugs we route around. All six PARSER-* sessions
inherit the workarounds.

### FW-3 — inline `epsilon . *fn()` inside ARBNO/FENCE does not fire

Investigated session 2026-05-03: deferred calls written INLINE inside
ARBNO or FENCE bodies do not fire. Assigned to a NAMED pattern first,
they fire correctly — including inside ARBNO(*Q) and FENCE.

**Workaround:** assign every pattern containing `epsilon . *fn()` to a
named variable before use in ARBNO/FENCE. The original note about
ARBNO(*Q) suppressing deferred calls is incorrect — the issue is
inline vs named, not deferred-ref vs inlined body.

8-line repro:

```snocone
function fire() { OUTPUT = '  fire()'; fire = .dummy; nreturn; }
Q = (ANY('a') epsilon . *fire());
'aa' ? ARBNO(Q);    // fires fire() twice ✓
'aa' ? ARBNO(*Q);   // fires fire() zero times ✗ — pattern matches but
                    //   side-effect deferred calls inside Q never run
```

**Workaround (universal, zero-cost):** inline the Command body inside
ARBNO directly. Do not write `ARBNO(*Command)`. Probable fix-site:
`interp_eval.c` / `eval_pat.c` — pattern re-evaluation walking the cached
pattern tree without re-firing E_CAPT_*_ASGN nodes.

### INFRA-11a — `subj ? pat` returns NULSTR on success

Canonical SNOBOL4 value-context scan returns the matched substring on
success; scrip's Snocone returns NULSTR. `DIFFER(subj ? pat)` and
`IDENT(subj ? pat, expected)` are not usable as success indicators.

**Probe:** `r = ('hi' ? 'hi'); SIZE(r) == 0` (canonical: 2).

**Workaround:** bound the result as no-op receiver, test side-effect only;
or append `@cur` cursor capture and test cursor reached end; or discard
result and test stack shape.

- [ ] Reduce probe → bisect → root-cause. Determine intentional success-
      token return vs bug. Fix or document in `REPO-one4all.md`.
- [ ] On fix, revert smoke workarounds.

### INFRA-11b — OPSYN infix-grammar integration

`OPSYN('~', 'shift', 2)` declares `~` as a 2-arg synonym for `shift`, but
scrip's Snocone parser binds `~` as the unary "not" operator at parse time,
before runtime OPSYN takes effect. `'foo' ~ 'Word'` parses wrong;
`APPLY('~', 'foo', 'Word')` works. `runtime/x86/snobol4_pattern.c::opsyn`
accepts the `type` arg but ignores it (`(void)type;`).

**Workaround:** all six PARSER frontends use `shift(p, t)` / `reduce(t, n)`
direct calls instead of static-infix `~` / `&`.

- [ ] Decide scope: (1) document not-supported; (2) honour `type=2` via
      runtime alias table consulted by lexer; (3) rewrite Snocone grammar
      for `~`/`&` as binary operators resolved through OPSYN at expression-
      build time.

### INFRA-11c — quoting wart in `reduce(t, n)` callers

`semantic.sc::reduce(t, n)` interpolates `t` into an EVAL string without
re-quoting, so callers must pre-quote: `reduce("'P'", 1)` works,
`reduce('P', 1)` resolves `P` as NULSTR variable inside EVAL. Same wart
in `shift`'s tag arg for non-string-literal inputs.

- [ ] Harden `reduce` and `shift` to detect already-quoted strings, or
      route through `Qize(t)`. Mirror change in `beauty/semantic.sc`.

---

## Invariants

- PARSER-SN never edits existing-frontend code to make trees match. If
  trees diverge, report the divergence; only after Lon decides which
  side is wrong does anyone touch either frontend.
- Test programs in `corpus/programs/snobol4/parser/` are owned by
  PARSER-SN. Crosschecks against existing programs in
  `corpus/programs/snobol4/` treat those as read-only fixtures.
- `.ref` files are captured from the existing frontend at the moment
  the rung lands and are checked in. They are NOT re-captured on later
  rungs without an explicit decision.
- `corpus` and `.github` stay on `main`; only `one4all` uses the
  `parser` branch.

---

## Watermark

**INFRA + FW + SN-0..SN-6 LANDED. Gate PASS=58, FAIL=0**
(SN-6 landed session 2026-05-03 morning, 2026-04-28 evening AOE.)

**⚠ PARSER-SN-7 PIVOTED, session 2026-05-03 PM.**  Diagnostic
crosscheck of the existing `parser_snobol4.sc` against `beauty.sno`
revealed ~1084 oracle stmts vs ~502 parser stmts.  Root cause is
not a finite list of grammar gaps — the parser is the wrong shape.

SN-7-0 partial-landed session 2026-05-03 PM (corpus@8083c20):
`parser_snobol4_v2.sc` scaffold (239 lines) on the parser_prolog.sc
/ parser_icon.sc / beauty.sno model.  All 5 invariants honored.
Living alongside the wrong-shape `parser_snobol4.sc` (876 lines)
until SN-7-1..7 reach PASS=58 parity.  MVP scope:
atom STMTs, label-only line, labeled+atom-body line, END marker.
MVP gate state: PASS=4 FAIL=1 on 5 targeted fixtures (atom_id,
atom_int, atom_str, cf_label_only PASS; cf_label_bare FAIL because
its `x = 1` body needs assign — lands in SN-7-1).

**Two architectural lessons surfaced during SN-7-0**, captured
in commit message at corpus@8083c20 and reproduced here so future
sessions opening to this watermark see them immediately:

  LESSON 1 — `nInc()` / `nPush()` / `nPop()` / `nTop()` are
  PATTERN-PRODUCING FUNCTIONS, not side-effect functions.  They
  return patterns that fire IncCounter() / PushCounter() / etc.
  at MATCH time.  Embed them as patterns inside grammar rules
  (`ARBNO( nInc() ws_opt clause ws_opt ... )`); inside escape-helper
  functions, call the BARE runtime: `IncCounter()`, `Push()`,
  `Pop()`.  The first draft of `parser_snobol4_v2.sc` made the
  textbook error of writing `Stmt . *nInc()`, which evaluates
  `nInc()` to a pattern and silently discards it — `IncCounter`
  never runs.

  LESSON 2 — `POS(0)` matches only at ABSOLUTE position 0 of the
  subject, not at start-of-line.  Once the cursor advances past
  the first char of Src, `POS(0)` NEVER matches again.  EndMarker,
  Comment, Control therefore CANNOT use `POS(0)` to mean "column
  0 of this line".  The fix relies on linear cursor advance: each
  Stmt / Comment / Control consumes its own trailing `nl_one`, so
  the cursor lands exactly at start-of-next-line for the next
  Command iteration.

The right shape is set by beauty.sno itself: one `Compiland` PATTERN
matched once over the entire source, all `~`/`&` infix shift/reduce
(routed through `shift(p, t)` / `reduce(t, n)` per INFRA-11b),
n-ary trees built via `nPush/nInc/nTop/nPop`, `Comment | Control |
Stmt` as alternation children of `Command`, no Snocone goto, no
parsing-driver functions.  Sibling parsers (PARSER-IC, PARSER-PR,
PARSER-RK, PARSER-RB) all land this shape today.  PARSER-SN at 876
lines is the largest and the only outlier — by a wide margin.

PARSER-SN-7 is therefore re-scoped from "land beauty.sno gate on top
of existing parser" to "rewrite parser_snobol4.sc to canonical
shape, then land beauty.sno gate".  Eight narrow rungs: SN-7-0
scaffolding (PARTIAL-LANDED 2026-05-03), SN-7-1..7 grammar slices
each gated by a focused fixture, SN-7-8 beauty.sno crosscheck.
See "Active rung ladder" above for full ladder.

Session 2026-05-03 PM artifacts:
- `corpus/programs/snobol4/parser/cf_label_bare.sno` added — fixture
  for bare-label-only line (`START\n` form), pre-stage SN-7-1.
  Currently FAILs against existing parser, will PASS automatically
  once SN-7-0 lands the canonical Stmt pattern with
  `Label = BREAK(' ' tab nl ';') ~ 'Label'`.
- This GOAL file rewritten: PARSER-SN-7 expanded into 9 rungs.
- `parser_snobol4.sc` left UNTOUCHED on `parser` branch.  The
  rewrite work happens on a new `parser-sn-rewrite` branch off
  `parser` per SN-7-0.
- Sibling parsers untouched.  Gate state: SN PASS=58 FAIL=1 (the
  one FAIL is `cf_label_bare` — pre-staged for SN-7-1).

SN-6 history (preserved for reference): added function definition /
call to the parser. One change to `parser_snobol4.sc`:

- New `_call_args(fname)` helper parses `( args )` into an `E_FNC` tree
  with `v=fname` and one child per arg.  Empty arg list → 0-child tree.
  Supports up to 7 args via `Tree(...)` positional + overflow via
  `Append`.
- `Expr17`'s identifier branch now checks for an immediately adjacent
  `(` and dispatches to `_call_args` for generic calls, otherwise falls
  back to bare `E_VAR`.  Whitespace between `Id` and `(` is NOT a call
  — `F (X)` is concat, matching the oracle.
- The five pattern primitives (LEN/BREAK/SPAN/ANY/NOTANY) keep their
  distinct E_LEN/E_BREAK/E_SPAN/E_ANY/E_NOTANY type tags via the
  `_pat_prim_call` cascade, which runs before the generic-call path.
- DEFINE is intentionally treated as just another generic call —
  `--dump-parse` itself does not crack open the spec string at parse
  time, so `DEFINE('F(X)')` becomes `(E_FNC DEFINE (E_QLIT "F(X)"))`.

15 new test programs in `corpus/programs/snobol4/parser/fn_*.sno`
covering one/two/three-arg / zero-arg / nested calls, calls in stmt
position, calls in pattern, calls in arith, calls with string args,
and DEFINE in four forms (one-arg / multi-arg / with locals/labels /
no args / labeled line).

Sibling parser gates re-checked: `parser_snobol4.sc` is the only file
touched, no shared file changed; siblings unaffected (Icon 33/33,
Prolog 18/18, Raku 17/17, Rebus 25/25 — all green).

SN-5 history (preserved for reference): added pattern-matching to the
parser via three new tiers.  Pattern primitive recognizers (LEN/BREAK/
SPAN/ANY/NOTANY) added to `Expr17` via shared `_pat_prim_call(name, kind)`
helper.  New `Expr12` tier (capture: `.` / `$`) inserted between
`Expr11` (pow) and `Expr14` (unary), left-associative per the oracle.
New `Expr3` tier (alternation: `|`) inserted at top of ladder above
`Expr4` (concat), n-ary flat per the oracle.  `_parse_body_goto`
rewritten as expression-driven with `_split_subj_pat(lhs)` helper
encoding the subj/pat split rule.  `tdump.sc::TValue` E_QLIT branch
moved before the empty-value `"."` placeholder so `(E_QLIT "")` renders
correctly.

**Next milestone:** PARSER-SN-7-1 — labels + assignment

**Watermark (session 2026-05-03 SN-7-0 final):** corpus@afbc6be
PASS=3. $'op' whitespace operators added per beauty.sno.
Uppercase=build-time pattern-returner. lowercase=match-time nreturn.
OPEN: ARBNO(*Command) with Command=nInc() FENCE(...) gives n=0 in scrip.
Test shown to Lon for diagnosis. Next: resolve then SN-7-1 labels+assign.

**Watermark (session 2026-05-03 SN-7-0 scaffold):**
parser_snobol4.sc rewritten from scratch on canonical shape (corpus@d34b23c).
PASS=3 (atom_id, atom_int, atom_str). Shape invariants: ONE Compiland, shift/reduce
function calls, nPush/nInc/nTop/nPop as patterns, no goto, no parse functions.
Next: labels, assignment, full expression ladder. — scaffold
`parser_snobol4_v2.sc` on a `parser-sn-rewrite` branch, on the
parser_prolog.sc / parser_icon.sc / beauty.sno model, hit PASS=58
parity on existing fixtures, then move through SN-7-1..7 grammar
slices, finishing at SN-7-8 (beauty.sno full crosscheck).
