# GOAL-PARSER-SNOCONE.md — PARSER-SNOCONE pattern-based frontend in Snocone

**Repo:** corpus+one4all
**Branch:** `parser` (one4all only — `corpus` and `.github` stay on `main`)
**Sibling ladder:** `GOAL-LANG-SNOCONE.md` and `GOAL-SNOCONE-IN-SNOCONE.md`.
The existing Snocone frontend (`src/frontend/snocone/`) is the in-process oracle.

**Done when:** A Snocone program `parser_snocone.sc` reads Snocone source,
runs one `Compiland` PATTERN that builds the canonical IR tree (same shape
SM-LOWER consumes), and for every test program in the rung corpus
`tree_equal(existing_frontend_tree, parser_snocone_tree)` returns true.
Where a `.ref` file exists, executing both trees through the IR interpreter
produces byte-identical output.

> **Cross-pollination (session #62):** D1 (no goto/label loops),
> D2 (names mirror the existing frontend), D3 (drive from a checked-in BNF
> in `corpus/programs/ebnf/`). See `GOAL-PARSER-ICON.md ## Design issues`
> for the canonical writeup. PARSER-SC-INFRA-2 is the SC instantiation.
>
> **Cross-PARSER-* style (session #65):** the canonical beauty.sno /
> beauty.sc–derived style guide is
> `GOAL-PARSER-SNOBOL4.md ## Style Guidelines for parser_*.sc` —
> binding on every PARSER-* (SNOBOL4, Snocone, Icon, Prolog, Raku, Rebus).
> Read that section first; the principles below are Snocone-specific
> extensions.  PARSER-SC-INFRA-3 brings `parser_snocone.sc` into
> conformance.

---

## Cross-pollination

All six PARSER-* parsers share `Compiland`/`Shift`/`Reduce`/`Push`/`Pop`/`Top`/
`tree`/`TDump`/`stack` from `corpus/programs/snocone/demo/beauty/`. Bug fixes
there benefit all six. PARSER-SNOCONE is the most reflexive: a Snocone program
parsing Snocone using the same pattern primitives Snocone provides. Coupled to
`GOAL-SNOCONE-IN-SNOCONE` long-term: when both rungs near completion the
bootstrap cycle closes.

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
bash /home/claude/one4all/scripts/test_smoke_snocone.sh        # existing frontend baseline
bash /home/claude/one4all/scripts/test_parser_snocone.sh       # this goal's gate
```

---

## Architecture reminder

```
scrip --parser-crosscheck parser_snocone.sc tiny.sc
```

SCRIP runs `parser_snocone.sc` (which `-include`s the shared SC library from
`corpus/programs/scrip/`) against `tiny.sc` — PAT produces IR tree t2 via
`Compiland`; the existing Snocone frontend produces t1. Both compared in
memory (`tree_equal`), both executed in memory. No subprocesses, no temp
files, no on-disk diffs.

**Shared SC library** (`corpus/programs/scrip/`):
```
tree.sc  stack.sc  counter.sc  ShiftReduce.sc  semantic.sc  gen.sc  tdump.sc
```

Compiland spine (identical across all six):
```
Compiland = nPush() ARBNO(*Command) reduce('Parse', 'nTop()') nPop();
```

Snocone-specific note: the existing Snocone frontend already lowers to LANG_SNO
IR via `snocone_lower.c`. PARSER-SC must produce the same post-lowering shape,
OR a pre-lowering tree the existing pipeline can consume — Lon decides per rung.

---

## Snocone language reference (atom slice)

| Construct | Tree shape |
|-----------|------------|
| identifier `x` | `Name x` |
| integer `42` | `integer 42` |
| string `"hi"` | `string 'hi'` |
| `x = expr;` | `(Stmt (Assign Name(x) ...))` |
| `function f(a,b) { ... }` | `(Function f (Params a b) Body)` |
| `if (c) { ... } else { ... }` | `(If c Then Else)` |
| `while (c) { ... }` | `(While c Body)` |
| `expr ? pat` | `(Match expr pat)` |

Full feature surface in `GOAL-LANG-SNOCONE.md`.

---

## Naming & Design Principles — Snocone-specific (D1/D2/D3)

> ⛔ **Cross-PARSER-* style guidelines are canonical in
> `GOAL-PARSER-SNOBOL4.md ## Style Guidelines for parser_*.sc`.**
> That section is binding on every PARSER-* (SNOBOL4, Snocone, Icon,
> Prolog, Raku, Rebus): `White`/`Gray` baked into `$'tok'`, language
> keywords as `$'kw'`, non-keyword word-tokens as plain idents (`S = $' '
> 'S'`), `$' '`/`$'  '` invisible whitespace tokens, Shift via `~` and
> Reduce via `&` OPSYN, `nPush`/`nInc`/`nTop`/`nPop` n-ary counters,
> `E_*` IR tags, no leading underscores in user code, no `{ stmt; }`
> single-statement bodies, 120-char `/*===*/` and `/*---*/` dividers,
> horizontal-dense vertically-balanced wrapping. Read that section first;
> the principles below extend it with Snocone-specific decisions only.

### 1. Names from the official BNF (D2/D3)

`src/frontend/snocone/snocone_parse.y` is the canonical grammar. Pattern-variable
names in the parser MUST mirror its expression-tier ladder:

```
expr0   assignment        (= += -= *= /= ^=)         → E_ASSIGN
expr1   pattern match     (?)                         → E_SCAN
expr3   pattern alt       (|, n-ary fold)             → E_ALT
expr4   concat            (juxtaposition, n-ary fold) → E_SEQ
expr5   comparison        (EQ NE LT GT LE GE LEQ ...) → E_FNC "EQ"...
expr6   additive          (+ -)                       → E_ADD / E_SUB
expr9   multiplicative    (* /)                       → E_MUL / E_DIV
expr11  exponent          (^, right-assoc)            → E_POW
expr12  pattern-bind      (binary . and $)            → E_CAPT_*
expr15  subscript         ([ ])                       → E_INDEX
expr17  atoms             (id, int, str, real, call)
```

`simple_stmt : expr0 T_SEMICOLON` — assignment is an `expr0`-level operator,
NOT statement-level. `sc_append_stmt` decomposes the top `E_ASSIGN(lhs, rhs)`
into `STMT { :eq=true, :subj=lhs, :repl=rhs }` post-parse
(`snocone_parse.y` line 1283).

### 2. Names from beauty.sc when concept matches (D2)

`corpus/programs/snocone/demo/beauty/beauty.sc` is the canonical Snocone self-host
pretty-printer; its `Expr0..Expr17` use `shift()`/`reduce()` from `ShiftReduce.sc`.
PARSER-SC reuses these names exactly.

```
Expr0 = *Expr1 FENCE($'=' *Expr0 reduce('=', 2) | epsilon);
Expr4 = nPush() *X4 reduce('..', '*(GT(nTop(), 1) nTop())') nPop();
X4    = nInc() *Expr5 FENCE(*White *X4 | epsilon);
Expr6 = *Expr7 FENCE($'+' *Expr6 reduce('+', 2) | $'-' *Expr6 reduce('-', 2) | epsilon);
Expr17 = ... shift(*Id, 'Id') | shift(*Integer, 'Integer') | shift(*String, 'String') ...
```

`$'='` accesses the variable named `=` (a pattern matching `=` surrounded by
optional whitespace) — embedding the pattern at build time, no runtime
indirection.

### 3. Driver: top-level `Compiland`, no per-line goto loop (D1)

```
Compiland = nPush() ARBNO(*Command) reduce('Parse', 'nTop()') nPop();
Command   = simple_stmt | if_head | while_head | ... ;
```

---

## Rung ladder

### PARSER-SC-0 — atom — ✅ DONE
### PARSER-SC-1 — assignment — ✅ DONE
### PARSER-SC-INFRA-1 — Gen-based TDump — ✅ DONE
### PARSER-SC-INFRA-2 — canonical Compiland + tier ladder — ✅ DONE
### PARSER-SC-3 — control flow — ✅ DONE (PASS=21, session #65)

(Closed rungs — see git history for landed state.)

### PARSER-SC-INFRA-3 — style cleanup against canonical guide ⏳ NEXT

The canonical Style Guidelines for `parser_*.sc`
(`GOAL-PARSER-SNOBOL4.md ## Style Guidelines for parser_*.sc`) were
landed in session #65.  The existing `parser_snocone.sc` predates them
and violates several.  These are guidelines not laws — the parser
produces correct IR — but conformance makes it a clean reference for
the other PARSER-* sessions and prevents drift in SC-4/SC-5/SC-6.

The audit done in session #65 (canonical §-numbering):

| Canonical § | Guideline | Current state in `parser_snocone.sc` |
|---|---|---|
| §7 | No leading `_` in user identifiers | 8 violations: `_sc_lbl_n`, `_sc_while_ltop`, `_sc_while_lend`, `_sc_do_lcont`, `_sc_do_lend`, `_sc_strbody`, `_kw_rest`, `_parser_sc_done` |
| §8 | No `{ stmt; }` for single-statement body | 1 violation: line 383 `while (Line = INPUT) { Src = Src Line nl; }` |
| §8 | No blank lines as separators; use 120-char `/*===*/` / `/*---*/` rules | 63 blank lines; dividers are `//-----` at 71 chars (not 120) |
| §4 | `~` / `&` OPSYN over `shift(…)` / `reduce(…)` longhand | 4 `shift(` + 11 `reduce(` calls; only 2 `~` uses, 0 `&` uses |
| §3 | `$' '` / `$'  '` invisible-whitespace tokens defined once and reused | Not defined; grammar uses raw `*Gray` / `*White` / `nl_opt` ad-hoc |

Not violations (canonical guide explicitly permits or prefers):

- `sc_*` lower-case match-time helpers paired with `SC_*` upper-case
  build-time pattern-builder wrappers — §7's identifier table allows
  function names of the form `Push`, `IncCounter`, `nPush`; the lower/
  upper paired scheme is a Snocone-specific extension that does not
  contradict §7.  Keep.
- `E_*` IR tags (`E_ASSIGN`, `E_SCAN`, `E_ADD`, …) per §6 — already
  used throughout. Good.
- Line widths per §8 — zero lines exceed 120 chars. Good.

#### Steps

- [x] **Step 3a — drop leading underscores (§7).** Rename
  `_sc_lbl_n` → `sc_lbl_n`,
  `_sc_while_ltop` → `sc_while_ltop`,
  `_sc_while_lend` → `sc_while_lend`,
  `_sc_do_lcont` → `sc_do_lcont`,
  `_sc_do_lend` → `sc_do_lend`,
  `_sc_strbody` → `sc_strbody`,
  `_kw_rest` → `kw_rest`,
  `_parser_sc_done` → `parser_sc_done`.
  Verify nothing inside an EVAL string also references the underscored
  forms (the original comment block explained the EVAL constraint that
  motivated the underscores; that constraint goes away once the names
  no longer start with `_`).  Re-run gate; expect PASS=21 unchanged.
  **DONE session #65: 17 use sites renamed across 8 identifiers; two
  comment blocks trimmed of stale leading-underscore rationale; gate
  PASS=21 FAIL=0.**

- [x] **Step 3b — fix single-stmt `{ }` body (§8).** Line 383:
  `while (Line = INPUT) { Src = Src Line nl; }` →
  `while (Line = INPUT)   Src = Src Line nl;`.  Audit for any other
  single-stmt `{ }` bodies introduced after the initial scan.  Re-run
  gate. **DONE session #65: only one violation found (the driver's
  input-reader loop); fixed; gate PASS=21 FAIL=0.**

- [ ] **Step 3c — replace 71-char dividers with 120-char comment rules
  (§8).** Major boundaries (token defs, helpers, builders, grammar tier,
  driver) get `/*===*/`; minor sub-boundaries get `/*---*/`. Drop the
  blank lines that currently separate sections — the rule now adjoins
  the next code block directly.  Re-run gate.

- [ ] **Step 3d — convert longhand `shift`/`reduce` to `~`/`&` OPSYN
  (§4).** Convert `shift(p, 't')` → `p ~ 't'` and `reduce('t', n)` →
  `('t' & n)` at all 15 call sites. Verify `semantic.sc` is in the
  runtime blob (it is — `test_parser_snocone.sh` loads it). The
  shift/reduce *functions* stay (still called by the OPSYN-installed
  `~`/`&`); only the *call form at the grammar* sites changes.  Re-run
  gate; expect PASS=21 unchanged.

- [ ] **Step 3e — define `$' '` / `$'  '` once; sweep grammar (§3).**
  Add at the top of the token-defs block:
  ```
  $' '  = *Gray;       // optional whitespace
  $'  ' = *White;      // required whitespace
  ```
  Then sweep the grammar replacing inline `*Gray` and `*White` with
  `$' '` and `$'  '` at composition sites. Token definitions themselves
  still use `*Gray` / `*White` directly (the `$' '` definition is itself
  `*Gray`, so re-using it inside `$'='` would be a self-reference).
  Re-run gate.

- **Sibling LANG rungs:** none — pure style.
- **Gate:** PASS=21 FAIL=0 unchanged after every step.

### PARSER-SC-4 — function def + call

Canonical Style Guidelines apply (see top of file) — write this rung
clean from the start.  Use `~`/`&` for all new shift/reduce sites; use
`$'function'`/`$'return'`/`$'freturn'`/`$'nreturn'` keyword tokens; no
leading underscores in any new identifiers; no `{ stmt; }` single-
statement bodies; 120-char dividers.

- [ ] `func_head : T_DEFINE T_IDENT T_LPAREN func_arglist opt_head_sep`
      (BNF line 701). Lowers to `(STMT :subj (E_FNC name (...args)))`.
- **Sibling LANG rungs:** SC-5..SC-7. **Gate:** PASS≥30.

### PARSER-SC-5 — pattern match `expr ? pat`

- [ ] `Expr1 = *Expr3 FENCE($'?' *Expr1 reduce('E_SCAN', 2) | epsilon)`.
      `sc_split_subject_pattern` (`snocone_parse.y` 1306) shows
      `E_ASSIGN(E_SCAN(s, p), r)` → `STMT { :subj=s, :pat=p, :repl=r }`.
- **Sibling LANG rungs:** SC-8, SC-9. **Gate:** PASS≥40.

### PARSER-SC-6 — full beauty.sc crosscheck

- [ ] PARSER-SC parses `beauty.sc` end-to-end. `tree_equal` against the
      existing frontend returns true. Both trees run identically under
      `--ir-run`.
- **Sibling LANG rung:** SC-final / `GOAL-SNOCONE-IN-SNOCONE` SS-N.
- **Gate:** beauty.sc round-trips.

---

## Invariants

- PARSER-SC never edits the existing Snocone frontend to make trees match.
- Test programs in `corpus/programs/snocone/parser-fixtures/` are owned by
  PARSER-SC.
- `.ref` files captured at rung-land time, checked in, not silently
  re-captured.
- The existing Snocone lowering (`snocone_lower.c`) is load-bearing for OTHER
  goals; don't perturb without explicit Lon approval.

---

## Watermark

**PARSER-SC-0 ✅ PARSER-SC-1 ✅ PARSER-SC-INFRA-1 ✅ PARSER-SC-INFRA-2 ✅
PARSER-SC-3 ✅**

Gate: PASS=21 FAIL=0 (atom_*, assign_*, arith_*, concat_seq, if_simple,
if_else, if_seq, if_multi_body, while_simple, while_seq, do_simple,
do_with_stmt). Smoke (`test_smoke_snocone.sh`): PASS=5 FAIL=0.
Sibling parsers unaffected.

**Session #65 (2026-05-04) — PARSER-SC-3 watermark bump; cross-PARSER
style guidelines integrated; INFRA-3 Steps 3a + 3b banked.**

PARSER-SC-3 (control flow: `if_head`, `if_else`, `while_head`, `do_head`,
multi-line input handling) was implemented in a previous session but the
watermark was never bumped from PASS=13.  This session ran the gate, saw
PASS=21 FAIL=0 across the full control-flow fixture set, and bumped the
watermark to match reality.

Cross-PARSER-* style — derived from `beauty.sno` / `beauty.sc` and
called out by Lon this session — was promoted by sibling sessions to a
canonical home at
`GOAL-PARSER-SNOBOL4.md ## Style Guidelines for parser_*.sc`,
binding on every PARSER-* (SNOBOL4, Snocone, Icon, Prolog, Raku, Rebus).
Read that section for the full nine-section guide:

1. Names match the official language specification.
2. `White` / `Gray` are attached to tokens, never referenced in the
   main grammar.
3. Reserved-word and special-character tokens use `$'name'` form.
4. Tree-build decorations use `shift`/`reduce` (or the `~`/`&` OPSYN
   shorthand), not bare deferred calls.
5. n-ary trees use `nPush()` / `nInc()` / `nTop()` / `nPop()`.
6. AST/IR tag names use `E_*` from `EXPR_t`.
7. Identifier conventions (no leading `_`; pattern names UpperCamel;
   functions UpperCamelSnake; variables lowercase snake_case).
8. Layout: 120-char lines; single-statement bodies one-line no braces;
   `/*===*/` major and `/*---*/` minor dividers; no blank lines as
   separators.
9. Read beauty.sno / beauty.sc end-to-end before authoring.

These are guidelines not laws — existing parsers that violate them
still produce correct IR.  PARSER-SC-INFRA-3 is the cleanup rung that
brings `parser_snocone.sc` into conformance; sibling sessions can run
analogous cleanups (or absorb the corrections during their own next
rung).  The audit found 5 violation classes (8 leading underscores,
1 single-stmt body, 63 blank lines, 15 longhand `shift`/`reduce` call
sites, no `$' '`/`$'  '` whitespace tokens) and 3 already-clean items
(no lines >120, `E_*` tags throughout, paired `sc_*`/`SC_*` helpers
permitted).

INFRA-3 progress this session:

- **Step 3a (drop leading underscores) ✅** — 17 use sites renamed
  across 8 identifiers (`_sc_lbl_n` → `sc_lbl_n` and 7 others).  Two
  comment blocks trimmed of stale leading-underscore rationale.  Gate
  PASS=21 FAIL=0.
- **Step 3b (single-stmt `{ }` body) ✅** — driver's input-reader loop
  rewritten without braces; only one violation in the whole file.  Gate
  PASS=21 FAIL=0.
- **Steps 3c, 3d, 3e** — pending next session (divider sweep,
  `shift`/`reduce` → `~`/`&` conversion across 15 sites, `$' '`/`$'  '`
  token sweep).

**Open follow-ups (out of scope for this rung):**

- File a scrip pattern-engine bug for the FENCE/`*deref` interaction.
  Repro: `*Id FENCE('=' *Id | epsilon)` against `'x=y'` captures `[x]`
  instead of `[x=y]`; without FENCE the same pattern captures `[x=y]`.
- D3 BNF (`corpus/programs/ebnf/snocone.ebnf`) check-in skipped per Lon.

**Next rung:** PARSER-SC-INFRA-3 Step 3c — replace 71-char `//---`
dividers with 120-char `/*===*/` / `/*---*/` rules; drop blank lines as
separators.
