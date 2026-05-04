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
| SN-5 | patterns (LEN/BREAK/SPAN/ANY/NOTANY, `\|`, `.`, `$`, replacement) | **PASS=43** ✅ this session |

---

## Active rung ladder

### PARSER-SN-6 — function definition / call

- [ ] `DEFINE('f(args)label')` and call sites.
- **Sibling LANG rungs:** SN-16..SN-20.
- **Gate:** PASS≥50.

### PARSER-SN-7 — beauty.sno crosscheck

- [ ] PARSER-SN parses `beauty.sno` end-to-end. `tree_equal` against the
      existing frontend's tree returns true. Running PARSER's tree
      through `--ir-run` produces output byte-identical to the SPITBOL
      oracle (the same gate Milestone 1 uses).
- **Sibling LANG rung:** SN-32 (beauty self-host).
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

### FW-3 — `ARBNO(*Q)` suppresses deferred calls inside Q

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

**INFRA + FW + SN-0..SN-5 LANDED. Gate PASS=43, FAIL=0** (this session,
2026-05-03).

SN-5 added pattern-matching to the parser. Three changes to
`parser_snobol4.sc`:

- Pattern primitive recognizers (`LEN`, `BREAK`, `SPAN`, `ANY`, `NOTANY`)
  added to `Expr17` via shared `_pat_prim_call(name, kind)` helper.
  NOTANY before ANY (longer match wins).
- New `Expr12` tier (capture: `.` / `$`) inserted between `Expr11` (pow)
  and `Expr14` (unary). Left-associative per the oracle.
- New `Expr3` tier (alternation: `|`) inserted at top of ladder above
  `Expr4` (concat). N-ary flat per the oracle.
- `_parse_body_goto` rewritten: parses the body as one expression, then
  splits on top-level `E_SEQ` into `:subj`/`:pat`. Replaces the earlier
  separate Assign / AtomStmt branches with one expression-driven path.
- `_split_subj_pat(lhs)` helper encodes the split rule.

`tdump.sc::TValue` fix: E_QLIT branch moved before the empty-value `"."`
placeholder so `(E_QLIT "")` renders correctly (oracle always emits the
typed quoted form for empty replacements).

20 new test programs in `corpus/programs/snobol4/parser/pat_*.sno`
covering all five primitives, alternation (2/3-arm/parenthesized),
conditional/immediate capture (single/chained), pattern-replacement
(simple/complex/empty), pattern-with-goto, and label+pattern.

Sibling parser gates re-run after the `tdump.sc` change: Icon 14/14,
Prolog 18/18, Raku 5/5, Rebus 12/12 — all unchanged. Snocone parser
gate (0/13) was already broken at PARSER-SC-INFRA-2 before this session;
unrelated.

**Next milestone:** PARSER-SN-6 — function definition / call. Will need
`DEFINE` parsing and call-site recognition (probably extending Expr17's
function-call shape from SN-5's restricted primitive form into a general
`Id LPAREN args RPAREN` form). FW-2's multi-child role-slot wrapper is
already landed and waiting.
