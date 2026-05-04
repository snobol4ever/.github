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

## Naming & Design Principles (D1/D2/D3)

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

### 3. Use shift/reduce primitives, not manual Push(Tree(...))

`ShiftReduce.sc` provides `shift(*pat, type)` and `reduce(type, n)`. Hand-rolled
`Push(Tree(...))` inside pattern escapes generates synthetic labels per
call-site which can collide silently across the loaded blob. Don't.

### 4. Driver: top-level `Compiland`, no per-line goto loop (D1)

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

(Closed rungs — see git history for landed state.)

### PARSER-SC-3 — control flow ⏳ NEXT

- [ ] Driver matches `stmt`: `simple_stmt | if_head | while_head | do_head`.
- [ ] Multi-line input handling: control-flow constructs span lines.
- **Sibling LANG rungs:** SC-3, SC-4. **Gate:** PASS≥20.

### PARSER-SC-4 — function def + call

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

**PARSER-SC-0 ✅ PARSER-SC-1 ✅ PARSER-SC-INFRA-1 ✅ PARSER-SC-INFRA-2 ✅**

Gate: PASS=13 FAIL=0 (atom_*, assign_*, arith_*, concat_seq).
Smoke (`test_smoke_snocone.sh`): PASS=5 FAIL=0. test_scrip.sh: PASS unchanged.
Sibling parsers unaffected: test_parser_snobol4.sh PASS=23, test_parser_icon.sh PASS=14.

**Session #64 (2026-05-03) landed INFRA-2.** Five fixes in
`corpus/programs/scrip/parser_snocone.sc` plus one in
`one4all/scripts/test_parser_snocone.sh`:

1. `type(top)` → `t(top)` in `sc_decompose_stmt`. `type` is undefined; the
   struct accessor from `struct tree { t, v, n, c }` is `t()`. (Was the
   "Error 5 in statement 69" the previous watermark named.)
2. `tree(...)` → `Tree(...)` in `sc_decompose_stmt`. Lowercase `tree` is the
   4-arg struct constructor (passes `c` as a literal scalar); uppercase
   `Tree` is the variadic helper that builds an ARRAY of children.
3. Driver fall-through into `mainErr:` — added `goto mainEnd;` after the
   `emit_loop:` block.
4. **FENCE removed from tier ladder** (Expr0/Expr1/Expr3/Expr4/Expr6/Expr9,
   X3/X4). scrip's pattern engine has a defect: `*VarA FENCE(literal *VarB |
   epsilon)` with a runtime `*deref` inside the FENCE first alt fails
   silently and epsilon wins. Workaround: drop FENCE on tier patterns; the
   alts are unambiguous so backtracking is harmless. FENCE remains inside
   `Id` (no leading deref) and `Expr17` (literal-only alts inside FENCE
   work fine). The defect is unrelated to this rung — file separately.
5. **String body capture:** `shift(*String, ...)` would capture the whole
   match including outer quotes via `thx`. Replaced with a custom
   `sc_push_qlit()` that pushes `tree('E_QLIT', _sc_strbody)` — using
   `_sc_strbody` (the BREAK . capture inside SQ/DQ) directly.
6. **Gate normalize():** `test_parser_snocone.sh` now uses the
   FW-6 variant-B `normalize()` helper (`tr -s '[:space:]' ' '` plus
   ` )`-collapse) to compare parser/oracle output, mirroring
   `test_parser_snobol4.sh`/`test_parser_icon.sh`/`test_parser_prolog.sh`.
   Gen-based TDump produces inline-or-multiline depending on width budget;
   `--dump-ir` always multi-lines for n>=2. Structural divergence is not
   masked, only whitespace layout.

**Open follow-ups (out of scope for this rung):**

- File a scrip pattern-engine bug for the FENCE/`*deref` interaction.
  Repro: `*Id FENCE('=' *Id | epsilon)` against `'x=y'` captures `[x]`
  instead of `[x=y]`; without FENCE the same pattern captures `[x=y]`.
- D3 BNF (`corpus/programs/ebnf/snocone.ebnf`) check-in skipped per Lon.

**Next rung:** PARSER-SC-3 — control flow (`if_head`, `while_head`,
`do_head`, multi-line input handling).
