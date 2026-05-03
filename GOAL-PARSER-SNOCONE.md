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

Three principles discovered the hard way during the SC-2 attempt below.
All future PARSER-SC rungs follow these.

### 1. Names come from the official BNF, not hand-rolled

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

### 2. Names from beauty.sc when concept matches

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

### 4. No labels and goto unless absolutely necessary

The driver loop in PARSER-SC-0/1 uses `main00:` / `goto main00` /
`mainErr:` — that is the only label-and-goto idiom in the file, and it
mirrors `parser_snobol4.sc`'s structure. New code should prefer
Snocone's structured forms (`if`/`while`/`function`) and avoid adding
new labels. When forced to use labels (driver loop control), the names
must be unique within the file and start with a distinctive prefix.

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

### PARSER-SC-2 — arith / concat  ⏳ NEXT

**Pivot from SC-0/SC-1 hand-rolled approach to BNF-aligned tier ladder.**
SC-0/SC-1 succeeded with a flat `(Assign | AtomStmt)` driver and manual
`Push(Tree(...))` builds. That approach does NOT scale to `expr6` /
`expr9` precedence — the SC-2 attempt in Session #62 hit silent label
collisions when adding `if/else` dispatch inside pattern-helper functions
loaded into the same blob as `tree.sc`, `stack.sc`, etc.

#### Design (per Naming & Design Principles above)

Replace the hand-rolled patterns in `parser_snocone.sc` with the
canonical tier ladder, using `shift()`/`reduce()` from `ShiftReduce.sc`:

```
//  Atom recognizers (names from beauty.sc)
Integer = SPAN(digits);
DQ      = '"' BREAK('"' nl) '"';
SQ      = "'" BREAK("'" nl) "'";
String  = *SQ | *DQ;
Id      = ANY(&UCASE &LCASE '_') FENCE(SPAN(digits &UCASE &LCASE '_.') | epsilon);

//  Operator wrappers
$'=' = *White '=' *White; $'+' = *White '+' *White;
$'-' = *White '-' *White; $'*' = *White '*' *White;
$'/' = *White '/' *White;

//  Tier ladder — each tier names exactly the BNF rule.
//  reduce(kind, 2) pops 2 children and builds the IR node.
//  Atom-leaf names ('Id'/'Integer'/'String') get mapped to E_VAR/E_ILIT/E_QLIT
//  by sc_lower (or by an INFRA-2 mapping table in tdump.sc).
Expr0  = *Expr1  FENCE($'=' *Expr0 reduce('E_ASSIGN', 2) | epsilon);
Expr1  = *Expr4;                              // SC-2 stops at concat/arith
Expr4  = nPush() *X4 reduce('E_SEQ', '*(GT(nTop(), 1) nTop())') nPop();
X4     = nInc() *Expr6 FENCE(*White *X4 | epsilon);
Expr6  = *Expr9 FENCE(  $'+' *Expr6 reduce('E_ADD', 2)
                      | $'-' *Expr6 reduce('E_SUB', 2)
                      | epsilon);
Expr9  = *Expr17 FENCE( $'*' *Expr9 reduce('E_MUL', 2)
                      | $'/' *Expr9 reduce('E_DIV', 2)
                      | epsilon);
Expr17 = shift(*Id, 'E_VAR') | shift(*Integer, 'E_ILIT') | shift(*String, 'E_QLIT');

simple_stmt = *Expr0 ws_opt semi_opt;
```

Driver matches `simple_stmt`, pops the result, hands to `sc_append_stmt`-
equivalent decomposition (when top is `E_ASSIGN`, split into `STMT :eq
:subj :repl`), TDumps. No `(Assign | AtomStmt)` alternation needed —
both forms pass through `Expr0` naturally.

#### Steps

- [ ] Rewrite `parser_snocone.sc` using `Expr0`/`Expr4`/`Expr6`/`Expr9`/
      `Expr17` tier names with `shift()`/`reduce()`. Drop `BareAtom`,
      `RhsAtom`, `LhsAtom`, `AtomStmt`, `Assign` (SC-0/SC-1 names).
- [ ] Add `sc_decompose_stmt` (Snocone function): when top tree is
      `E_ASSIGN`, build `(STMT :eq :subj L :repl R)`; else build
      `(STMT :subj top)`. Mirrors `sc_append_stmt` in `snocone_parse.y`.
- [ ] Verify all 13 fixtures (8 SC-0/1 + 5 SC-2) pass against `--dump-ir`.
- [ ] Test corpus already added under SC-2 attempt:
      `arith_add.sc`, `arith_sub.sc`, `arith_mul.sc`, `arith_div.sc`,
      `concat_seq.sc` (corpus `8d6bd82` and after).
- **Sibling LANG rungs:** SC-3.
- **Gate:** PASS=13 FAIL=0.

#### Session #62 attempt — rolled back

Tried hand-rolled `RhsExpr = (RhsAtom ws_opt ArithOp ws_opt RhsAtom2 | ...)`
plus `build_assign_dispatch()` with `if (DIFFER(_binop_kind))` dispatch.
Patterns worked in isolation (see `/tmp/test_rhsexpr_ctx.sc` reproduction)
but failed silently in the full blob. Symptom: even SC-1 fixtures regressed
to "Parse Error" once the new code was loaded. Root cause likely a label
collision between the new helper's synthetic labels and labels in
`tree.sc`/`stack.sc`/`qize.sc`. The shift/reduce approach above sidesteps
this entirely — no new helper functions, no synthetic labels.

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

**Session #62 (2026-05-03):** SC-2 attempt with hand-rolled `RhsExpr`
+ `build_assign_dispatch()` rolled back due to silent label collision
in full blob. Five SC-2 fixtures committed to corpus and staged as
failing tests for the next session. Naming & Design Principles section
added: tier names from `snocone_parse.y` BNF (`Expr0..Expr17`),
operator wrappers from `beauty.sc` (`$'='`, `$'+'`, `Gray`, `White`),
shift/reduce from `ShiftReduce.sc` instead of manual `Push(Tree(...))`,
no new labels and goto. SC-2 is now scoped as a tier-ladder rewrite,
not an incremental extension.

Next: **PARSER-SC-2** — rewrite parser_snocone.sc with `Expr0`/`Expr4`/
`Expr6`/`Expr9`/`Expr17` tier ladder using `shift()`/`reduce()` from
`ShiftReduce.sc`. Atom recognizer names from `beauty.sc` (`Integer`,
`String`, `Id`). Decompose `E_ASSIGN(lhs,rhs)` → `(STMT :eq :subj :repl)`
in `sc_decompose_stmt` mirroring `sc_append_stmt` in `snocone_parse.y`.

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
