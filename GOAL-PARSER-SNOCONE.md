# GOAL-PARSER-SNOCONE.md — PARSER-SNOCONE pattern-based frontend in Snocone

**Repo:** corpus+one4all
**Branch:** `pat` (one4all only — `corpus` and `.github` stay on `main`)
**Sibling ladder:** `GOAL-LANG-SNOCONE.md` (and the closely related
`GOAL-SNOCONE-IN-SNOCONE.md`). The existing Snocone frontend
(`src/frontend/snocone/`) is the in-process oracle.

**Done when:** A Snocone program `parser_snocone.sc` reads Snocone source,
runs one `Compiland` PATTERN that builds the canonical IR tree (same
shape SM-LOWER consumes), and for every test program in the rung corpus
`tree_equal(existing_frontend_tree, parser_snocone_tree)` returns true.
Where a `.ref` file exists, executing both trees through the IR
interpreter produces byte-identical output.


> **Cross-pollination notice (session #62, 2026-05-03):** three design
> issues raised against PAT-IC apply to all six PARSER-* frontends.
> See `GOAL-PARSER-ICON.md ## Design issues` (D1: drop goto/label
> driver loops; D2: nonterminal names must mirror the existing
> frontend, not invent new ones; D3: drive from a checked-in BNF in
> `corpus/programs/ebnf/`). Tracked under PARSER-IC-INFRA-1 and
> PARSER-IC-INFRA-2 — when those rungs land, the same refactor lands
> on this parser too.

---

## Cross-pollination

All six PARSER-* parsers share `Compiland`/`Shift`/`Reduce`/`Push`/`Pop`/`Top`/
`tree`/`TDump`/`stack` from `corpus/programs/snocone/demo/beauty/`. Bug
fixes there benefit all six. PARSER-SNOCONE is the most reflexively
satisfying of the six: a Snocone program parsing Snocone using the same
pattern primitives Snocone provides. Coupled to `GOAL-SNOCONE-IN-SNOCONE`
on the long-horizon: when both rungs near completion, the bootstrap
cycle closes.

---

## Session Setup

```bash
# Switch one4all to the shared parser branch. corpus and .github stay on main.
( cd /home/claude/one4all && git fetch origin parser 2>/dev/null; git checkout parser 2>/dev/null || git checkout -b parser origin/parser 2>/dev/null || git checkout -b parser )

bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_snocone.sh        # existing frontend baseline
bash /home/claude/one4all/scripts/test_parser_snocone.sh          # NEW — written under PARSER-SC-0
```

---

## Architecture reminder

```
scrip --parser-crosscheck parser_snocone.sc tiny.sc
```

SCRIP runs `parser_snocone.sc` (which `-include`s the shared SC library from
`corpus/programs/scrip/`) against `tiny.sc` — PAT produces IR tree t2
via `Compiland`; the existing Snocone frontend produces t1. Both compared in
memory (`tree_equal`), both executed in memory. No subprocesses, no temp
files, no on-disk diffs.

**Shared SC library** (`corpus/programs/scrip/` — tracked under PARSER-SN-INFRA-1):
```
tree.sc  stack.sc  counter.sc  ShiftReduce.sc  semantic.sc
```

Compiland spine (identical across all six):
```
Compiland = nPush() ARBNO(*Command) reduce('Parse', 'nTop()') nPop();
```

Snocone-specific note: the existing Snocone frontend already lowers
to LANG_SNO IR via `snocone_lower.c`. PARSER-SC must produce the same
post-lowering shape, OR produce a pre-lowering Snocone-flavored tree
that the existing lowering pipeline can consume — Lon decides per rung
which is in scope.

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

(Full feature surface lives in `GOAL-LANG-SNOCONE.md`.)

---

## Naming & Design Principles  (added Session #62, 2026-05-03)

These map onto Lon's three issues raised against PARSER-IC in the same
session — D1 (no goto/label loops), D2 (names from existing code),
D3 (drive from checked-in BNF). See `GOAL-PARSER-ICON.md ## Design issues`
for the canonical writeup; the items below are the PARSER-SC-specific
instantiation, discovered the hard way during the SC-2 attempt.

### 1. Names come from the official BNF, not hand-rolled  *(Lon's D2 + D3)*

The official Snocone grammar is `src/frontend/snocone/snocone_parse.y`.
Its expression-tier ladder is the canonical names — pattern variables
in the parser MUST use these tier names, not hand-rolled aliases like
`RhsExpr`, `RhsAtom`, `ArithOp`, `LhsAtom`.

```
expr0   — assignment        (= += -= *= /= ^=)         → E_ASSIGN
expr1   — pattern match     (?)                         → E_SCAN
expr3   — pattern alt       (|, n-ary fold)             → E_ALT
expr4   — concat            (juxtaposition, n-ary fold) → E_SEQ
expr5   — comparison        (EQ NE LT GT LE GE LEQ ...) → E_FNC "EQ"...
expr6   — additive          (+ -)                       → E_ADD / E_SUB
expr9   — multiplicative    (* /)                       → E_MUL / E_DIV
expr11  — exponent          (^, right-assoc)            → E_POW
expr12  — pattern-bind      (binary . and $)            → E_CAPT_*
expr15  — subscript         ([ ])                       → E_INDEX
expr17  — atoms             (id, int, str, real, call)
```

`simple_stmt : expr0 T_SEMICOLON` — assignment is just an `expr0`-level
operator, NOT a statement-level construct. `sc_append_stmt` decomposes
the top `E_ASSIGN(lhs, rhs)` into `STMT { :eq=true, :subj=lhs, :repl=rhs }`
post-parse (see `snocone_parse.y` line 1283).

**D3 action item:** when PARSER-IC-INFRA-1 lands `corpus/programs/ebnf/icon.ebnf`,
the parallel item for SC is to land `corpus/programs/ebnf/snocone.ebnf` —
PARSER-SC nonterminal names then map 1-to-1 to productions there.

### 2. Names from beauty.sc when concept matches  *(Lon's D2)*

`corpus/programs/snocone/demo/beauty/beauty.sc` is the canonical Snocone
self-host pretty-printer. It already implements `Expr0..Expr17` for the
SNOBOL4 surface syntax using `shift()`/`reduce()` from `ShiftReduce.sc`.
PARSER-SC reuses these names exactly. Reading list:

```
Expr0 = *Expr1 FENCE($'=' *Expr0 reduce('=', 2) | epsilon);
Expr4 = nPush() *X4 reduce('..', '*(GT(nTop(), 1) nTop())') nPop();
X4    = nInc() *Expr5 FENCE(*White *X4 | epsilon);
Expr6 = *Expr7 FENCE($'+' *Expr6 reduce('+', 2) | $'-' *Expr6 reduce('-', 2) | epsilon);
Expr17 = ... shift(*Id, 'Id') | shift(*Integer, 'Integer') | shift(*String, 'String') ...
```

Atom recognizers: `Integer`, `String`, `Real`, `Id`, `Function`,
`BuiltinVar`, `SpecialNm`, `ProtKwd`, `UnprotKwd`. Whitespace patterns:
`Gray`, `White`. Operator wrappers: `$'='`, `$'+'`, `$'?'`, etc.

The `$'op'` form is a Snocone idiom: `$'='` accesses the variable named
`=` (which holds a pattern that matches `=` surrounded by optional
whitespace). This is what makes `Expr0 = *Expr1 FENCE($'=' *Expr0 ...)`
read like the BNF.

### 3. Use shift/reduce primitives, not manual Push(Tree(...))

`ShiftReduce.sc` provides `shift(*pat, type)` and `reduce(type, n)`.
`shift` matches `*pat` and pushes a leaf with given type. `reduce` pops
N children, builds a parent tree with given type, pushes it back.

Hand-rolled `Push(Tree('STMT', '', 3, ...))` calls inside pattern escapes
(`*build_stmt_assign(...)`) are how PARSER-SN got started, but they
**generate Snocone synthetic labels** (`_L0001`, `_L0002`, etc.) inside
the helper functions' if/else and while bodies. When loaded in the same
session as `tree.sc`, `stack.sc`, `qize.sc`, etc., these labels can
**collide silently** with labels in other files — see `INFRA-5a` in
`GOAL-PARSER-SNOBOL4.md`. The fix landed there is `g_sc_label_seq`
monotonic in `snocone_parse.y`. PARSER-SC must NOT regress this by
re-introducing manual control flow inside pattern-helper functions.

`reduce()` does its work entirely inside `ShiftReduce.sc` (one file,
labels resolved once); pattern code calls it as a primitive. No new
labels generated per-rung.

### 4. No labels and goto unless absolutely necessary  *(Lon's D1)*

The driver loop in PARSER-SC-0/1 uses `main00:` / `goto main00` /
`mainErr:` — that is the only label-and-goto idiom in the file, and it
mirrors `parser_snobol4.sc`'s structure. Per Lon's D1, the right shape
for the driver is a top-level `Compiland` PATTERN consuming the entire
input via `ARBNO(*Command)` — no goto, no `mainErr:` label, no per-line
loop. SC-2 makes the pivot.

```
Compiland = nPush() ARBNO(*Command) reduce('Parse', 'nTop()') nPop();
Command   = simple_stmt | if_head | while_head | ... ;
```

---

## Rung ladder

### PARSER-SC-0 — atom — ✅ DONE

- [x] Wrote `corpus/programs/scrip/parser_snocone.sc` — recognizes one
      identifier, integer, or string per line via `id_pat` / `int_pat` /
      `str_pat`; `build_stmt_atom` pushes `(STMT :subj (kind txt))` via
      shared Tree/Push; driver reads stdin line-by-line, pops and TDumps.
- [x] Two-frontend crosscheck at gate-script level: `parser_snocone.sc`
      driver vs `scrip --dump-ir`. Byte-identical.
- [x] Wrote `scripts/test_parser_snocone.sh` — canonical blob shape
      (global/tree/stack/ShiftReduce/qize/tdump/assign/parser_snocone);
      per-fixture `--dump-ir` oracle; self-contained per RULES.md.
- [x] Test corpus (3 NEW): `atom_id.sc`, `atom_int.sc`, `atom_str.sc`.
- **Sibling LANG rungs:** SC-0 (lexer), SC-1 (atom).
- **Gate (cleared):** PASS=3 FAIL=0. ✅

### PARSER-SC-1 — assignment — ✅ DONE

- [x] `Assign` rule handles `name = expr;` for atom rhs (id/int/str).
      `LhsAtom` captures id into `_lhs_id`; `RhsAtom` captures kind+text
      into `rhs_kind`/`rhs_text`; `build_stmt_assign` pushes
      `(STMT :eq :subj (E_VAR lhs) :repl (kind rhs))`.
      Driver tries `(Assign | AtomStmt)` — Assign first.
- [x] Test corpus: 8 cumulative (3 atom + **5 NEW**):
      `assign_int.sc`, `assign_str.sc`, `assign_var.sc`,
      `assign_seq.sc`, `assign_mixed.sc`.
- **Sibling LANG rungs:** SC-2.
- **Gate (cleared):** PASS=8 FAIL=0. ✅

### PARSER-SC-INFRA-2 — canonical BNF + Compiland refactor  ⏳ NEXT

Mirrors Lon's `PARSER-IC-INFRA-1` / `PARSER-IC-INFRA-2` for SC. Must
land before SC-2 fixtures pass.

- [ ] **BNF (D3):** check in `corpus/programs/ebnf/snocone.ebnf` —
      canonical Snocone BNF in the same EBNF dialect as `s4-sp.ebnf` /
      `s4-no.ebnf`. Source of truth: `src/frontend/snocone/snocone_parse.y`.
      Every PAT-SC nonterminal name must map 1-to-1 to a production there.
- [ ] **Names (D2):** rewrite `parser_snocone.sc` using BNF tier names
      (`Expr0`, `Expr1`, `Expr3`, `Expr4`, `Expr6`, `Expr9`, `Expr11`,
      `Expr17`) plus `beauty.sc` atom names (`Integer`, `String`, `Id`,
      `Gray`, `White`, `$'='`, `$'+'`, etc.). Drop SC-0/SC-1 hand-rolled
      `BareAtom`, `RhsAtom`, `LhsAtom`, `AtomStmt`, `Assign`.
- [ ] **Compiland (D1):** replace the `main00:`/`mainErr:` goto loop
      with a top-level `Compiland` PATTERN consuming the entire input
      via `ARBNO(*Command)` — same shape as `beauty.sc`. No goto, no
      `mainErr:` label, no per-line driver. Parse-error reporting via
      `Compiland`'s natural failure path.
- [ ] **shift/reduce:** all tree construction goes through
      `shift(*pat, type)` and `reduce(type, n)` from `ShiftReduce.sc`.
      No `Push(Tree(...))` inside pattern escapes.
- [ ] **STMT decomposition:** add `sc_decompose_stmt` (Snocone function)
      that mirrors `sc_append_stmt` in `snocone_parse.y` — when the
      result of `Expr0` is `E_ASSIGN(lhs, rhs)`, emit
      `(STMT :eq :subj lhs :repl rhs)`; else emit `(STMT :subj top)`.
- [ ] **Gate:** all 8 SC-0/SC-1 fixtures still pass (atom_*, assign_*),
      AND all 5 SC-2 fixtures now pass (arith_*, concat_seq).
      PASS=13 FAIL=0.

### PARSER-SC-2 — arith / concat (rolled into INFRA-2)

The original SC-2 step ("`Command` handles `+ - * /` and Snocone's concat
operator") is **subsumed by INFRA-2**: once the parser is rewritten with
the `Expr6`/`Expr9` tier ladder using `shift`/`reduce`, arith and concat
fall out for free — the grammar already covers them at those tiers.

The 5 SC-2 fixtures (`arith_add.sc`, `arith_sub.sc`, `arith_mul.sc`,
`arith_div.sc`, `concat_seq.sc`) committed in corpus `3c3153d` are
the gate for INFRA-2.

#### Session #62 attempt — rolled back

Tried hand-rolled `RhsExpr = (RhsAtom ws_opt ArithOp ws_opt RhsAtom2 | ...)`
plus `build_assign_dispatch()` with `if (DIFFER(_binop_kind))` dispatch.
Patterns worked in isolation (see `/tmp/test_rhsexpr_ctx.sc` reproduction)
but failed silently in the full blob. Symptom: even SC-1 fixtures regressed
to "Parse Error" once the new code was loaded. Root cause likely a label
collision between the new helper's synthetic labels and labels in
`tree.sc`/`stack.sc`/`qize.sc`. The INFRA-2 shift/reduce approach
sidesteps this entirely — no new helper functions, no synthetic labels.

### PARSER-SC-3 — control flow

- [ ] Driver loop matches `stmt` (BNF rule), which alternates between
      `simple_stmt` (already in SC-2), `if_head`, `while_head`, `do_head`.
      `if_head : T_IF T_LPAREN expr0 T_RPAREN opt_head_sep` (BNF line 583).
      `while_head : T_WHILE T_LPAREN expr0 T_RPAREN opt_head_sep` (line 587).
- [ ] Multi-line input handling: control-flow constructs span multiple
      lines, so the driver must accumulate input until a balanced
      `{ ... }` body is seen, not match line-by-line.
- [ ] Test corpus: existing snocone control programs + **NEW** edge cases.
- **Sibling LANG rungs:** SC-3, SC-4.
- **Gate:** PASS≥20.

### PARSER-SC-4 — function def + call

- [ ] `func_head : T_DEFINE T_IDENT T_LPAREN func_arglist opt_head_sep`
      (BNF line 701). Lowers to `(STMT :subj (E_FNC name (...args)))`.
      Call sites already covered in `Expr17` via `shift(*Function, 'Call')`.
- **Sibling LANG rungs:** SC-5..SC-7.
- **Gate:** PASS≥30.

### PARSER-SC-5 — pattern match `expr ? pat`

- [ ] `Expr1 = *Expr3 FENCE($'?' *Expr1 reduce('E_SCAN', 2) | epsilon)` —
      this tier was deferred in SC-2. Pattern subexpressions on the rhs
      use SNOBOL4-style `Expr3 (alternation)` and below.
      `sc_split_subject_pattern` in `snocone_parse.y` (line 1306) shows
      how `E_ASSIGN(E_SCAN(s, p), r)` decomposes into
      `STMT { :subj=s, :pat=p, :repl=r }`.
- **Sibling LANG rungs:** SC-8, SC-9 (pattern match).
- **Gate:** PASS≥40.

### PARSER-SC-6 — full beauty.sc crosscheck

- [ ] PARSER-SC parses `beauty.sc` end-to-end. `tree_equal` against the
      existing frontend's tree returns true. Both trees run identically
      under `--ir-run`.
- **Sibling LANG rung:** SC-final / `GOAL-SNOCONE-IN-SNOCONE` SS-N.
- **Gate:** beauty.sc round-trips.

---

## Invariants

- PARSER-SC never edits the existing Snocone frontend to make trees match.
- Test programs in `corpus/programs/snocone/parser-fixtures/` are owned by PARSER-SC.
- `.ref` files captured at rung-land time, checked in, not silently
  re-captured later.
- The existing Snocone lowering (`snocone_lower.c`) is treated as
  load-bearing for OTHER goals and must not be perturbed by PARSER-SC
  edits without explicit Lon approval.

---

## Watermark

**PARSER-SC-0 ✅ PARSER-SC-1 ✅ PARSER-SC-INFRA-1 ✅**

corpus `8d6bd82` (main), one4all `347d2472` (parser branch).
Gate: PASS=8 FAIL=0 on SC-0/SC-1 fixtures (atom_*, assign_*).
Five SC-2 fixtures staged in corpus as failing tests:
`arith_add.sc`, `arith_sub.sc`, `arith_mul.sc`, `arith_div.sc`,
`concat_seq.sc` — currently FAIL because parser_snocone.sc still at SC-1.
Smoke: PASS=5 FAIL=0 (test_smoke_snocone.sh).
test_scrip.sh: PASS (unchanged).

parser_snocone.sc covers: bare atom-as-statement (id/int/str),
assignment `name = atom_expr`. Driver: per-line, `(Assign | AtomStmt)`.
TDump upgraded to Gen-based multi-line fallback (gen.sc now in blob).

**Session #63 (2026-05-03):** INFRA-2 rewrite attempt — BROKEN, pushed to
corpus `170a52c` / one4all parser `b9075835`. Key findings:
- shift(p, t): t must be BARE type name (e.g. `'E_VAR'`); semantic.sc
  shift() adds its own quotes in the EVAL string. Using sq-concat type
  names like `sq 'E_VAR' sq` produces `''E_VAR''` double-escaped → snobol4:0
  parse error from sno_parse_string. Fix: s_* bare, r_* quoted split.
- reduce(t, n): t must carry its own quotes (e.g. `"'E_ASSIGN'"`).
  Built via sq concat: `r_ASSIGN = sq 'E_ASSIGN' sq`.
- semantic.sc OPSYN('~','shift',2) fires at runtime not parse time; ~ and &
  infix forms are SNOBOL4-only. Snocone parser rejects `pat ~ type` syntax
  at parse time (before OPSYN fires). Must use shift()/reduce() function
  calls in .sc source.
- semantic.sc must load BEFORE parser_snocone.sc in blob (functions needed
  at pattern-build execution time) and BEFORE ShiftReduce.sc.
- Remaining bug: Error 5 at stmt 69 (close of Expr6) in full blob but not
  in isolation. Likely: r_nTop = '*(GT(nTop(), 1) nTop())' as n-arg to
  reduce() in Expr4/Expr3 — GT/nTop not in scope at pattern-build time.
  Next session: fix r_nTop and reach PASS=13.
- BNF (D3 / snocone.ebnf): skipped per Lon — not needed.

**Session #62 (2026-05-03):** SC-2 attempt with hand-rolled `RhsExpr`
+ `build_assign_dispatch()` rolled back due to silent label collision
in full blob. Five SC-2 fixtures committed to corpus and staged as
failing tests for the next session. Naming & Design Principles section
added: tier names from `snocone_parse.y` BNF (`Expr0..Expr17`),
operator wrappers from `beauty.sc` (`$'='`, `$'+'`, `Gray`, `White`),
shift/reduce from `ShiftReduce.sc` instead of manual `Push(Tree(...))`,
no new labels and goto. SC-2 is now scoped as a tier-ladder rewrite,
not an incremental extension.

Next: **PARSER-SC-INFRA-2** — canonical BNF check-in (`snocone.ebnf`)
+ rewrite `parser_snocone.sc` using BNF tier names (`Expr0`/`Expr4`/
`Expr6`/`Expr9`/`Expr17`) with `shift()`/`reduce()` from `ShiftReduce.sc`,
top-level `Compiland` PATTERN driver (no goto), `sc_decompose_stmt` for
the `E_ASSIGN(lhs,rhs)` → `(STMT :eq :subj :repl)` split.
SC-2 (arith/concat) falls out of INFRA-2 once the tier ladder lands.

---

## TDump upgrade — prerequisite for PARSER-SC-2+

Discovered in session: `tdump.sc` uses `TLump(x, 1024)` — always one line,
never wraps. The canonical `TDump.sno` (beauty) tries `TLump(x, 140 - GetLevel())`
first (inline); if TLump fails (too wide), falls back to multi-line with
`Gen`/`IncLevel`/`DecLevel`. This is why `--dump-ir` produces indented output
for n>1 children but the current `TDump` does not.

`gen.sc` already exists in `corpus/programs/scrip/` with full `Gen`,
`IncLevel`, `DecLevel`, `SetLevel`, `GetLevel` implementations.

`corpus/programs/snocone/demo/beauty/TDump.sc` has the canonical Snocone
port of the full TDump with Gen-based multi-line fallback.

### PARSER-SC-INFRA-1 — upgrade tdump.sc to Gen-based TDump  ✅ DONE

- [x] Replace `TDump` in `corpus/programs/scrip/tdump.sc` with the
      canonical Gen-based version from `corpus/programs/snocone/demo/beauty/TDump.sc`:
      `Gen(TLump(x, 140 - GetLevel()) nl, outNm)` try-inline first;
      multi-line fallback with `IncLevel`/`DecLevel`/recursive `TDump`.
      Carry over all PARSER-SN extensions (role-slot FW-1/FW-2, generic
      IR-leaf, E_QLIT double-quote branch).
- [x] Add `gen.sc` to the canonical runtime blob in `test_parser_snocone.sh`
      (before `tdump.sc`). Update `test_parser_snobol4.sh` and `test_scrip.sh`
      the same way.
- [x] Verify `test_scrip.sh` still PASS — existing TDump smoke lines must
      produce identical output (Gen flushes on `nl`, same as current OUTPUT).
- [x] Verify `test_parser_snocone.sh` PASS=8 — atom/assign fixtures are
      simple enough that TLump inline succeeds; output unchanged.
- **Gate (cleared):** PASS=8 FAIL=0; `test_scrip.sh` PASS unchanged.

### PARSER-SC-2 — arith / concat  (after INFRA-1)

- [ ] `RhsExpr` handles `atom op atom` for `+ - * /` and Snocone concat
      (juxtaposition). Oracle: `--dump-ir` produces `(E_ADD\n  child\n  child\n))`
      after INFRA-1 TDump upgrade; gate compares directly, no normalization needed.
- [ ] Update `Assign` to use `RhsExpr` instead of `RhsAtom` on the rhs.
- [ ] Test corpus: 5 NEW programs.
- **Sibling LANG rungs:** SC-3.
- **Gate:** PASS≥13.
