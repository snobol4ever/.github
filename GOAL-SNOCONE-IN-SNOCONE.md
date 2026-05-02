# GOAL-SNOCONE-IN-SNOCONE — Snocone Compiler Written in Snocone

**Repo:** one4all + corpus
**Done when:** the Snocone compiler — frontend (lex + parse), IR, lowering — is
written in Snocone itself, compiles its own source through scrip, and the
resulting compiler reproduces its own output. Stage 1 output equals Stage 2
output. The Snocone compiler writes itself.

This is the **second major bootstrap moment**, following Milestone 1
(SNOBOL4 beauty self-host, Session #57, 2026-04-28). Where Milestone 1
proved that scrip's SNOBOL4 frontend is faithful enough to host
beauty.sno byte-for-byte, this goal proves that Snocone is expressive
and complete enough to host its own compiler. It pairs naturally with
Milestone 2 of the THREE-MILESTONE AUTHORSHIP AGREEMENT.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/build_scrip.sh
```

Gate after setup:
```bash
scrip --ir-run /home/claude/corpus/programs/snocone/corpus/sc1_literals.sc
# → hello / world / 42
```

---

## Architecture

**Stage 0 host:** `scrip --ir-run snocone.sc` — C Snocone frontend + C IR interpreter runs the bootstrap compiler.
**Stage 1 compiler:** `snocone.sc` itself, driven by Stage 0.
**Self-host proof:** Stage 1 compiles `snocone.sc` → same output as Stage 0. Empty diff.

### File layout

```
corpus/programs/snocone/interpreter/
    snocone.sc      ← main driver: reads source, calls lex→parse→interp
    value.sc        ← Val struct: val_int/val_str/val_real/val_fail/val_null/is_fail/val_to_str
    ir.sc           ← Node struct: ir_node/ir_set_sval/ir_set_ival/ir_add_child/ir_print
    lex.sc          ← Tok struct: tokenizer returns array of Tok structs
    parse.sc        ← recursive-descent parser → IR Node tree
    interp.sc       ← tree-walk evaluator: sc_eval(node) → Val
    runtime.sc      ← builtins: OUTPUT/INPUT/SIZE/IDENT/DIFFER/etc.
```

### Representation: Snocone struct (DATA)

Snocone `struct` lowers to SNOBOL4 `DATA()` — gives named-field constructors
and field accessor functions. This is the idiomatic representation.

**Values** (`value.sc`):
```
struct Val { type, v }
// type: 'INT' | 'STR' | 'REAL' | 'FAIL' | 'NULL'
// v:    the payload (integer, string, real, or '')
// Constructor: Val(type, v)   Field accessors: type(x)  v(x)
```

**IR nodes** (`ir.sc`):
```
struct Node { kind, sval, ival, dval, nc, c }
// kind: 'E_ILIT' | 'E_ADD' | 'E_VAR' | ...
// sval: string payload (var name, function name, quoted literal)
// ival: integer payload
// dval: real payload
// nc:   number of children (integer)
// c:    ARRAY('1:N') of child Node structs  ('' when nc=0)
// Constructor: Node(kind,sval,ival,dval,nc,c)
```

**Tokens** (`lex.sc`):
```
struct Tok { kind, sval, ival, dval }
// kind: 'T_INT' | 'T_STR' | 'T_IDENT' | 'T_PLUS' | 'T_SEMI' | ...
// Constructor: Tok(kind,sval,ival,dval)
```

---

## Open rungs

- [x] **SS-1** — Write the step plan. Architecture decided: Stage 0 = scrip C host,
  Stage 1 = snocone.sc compiles itself. File layout above. TDD rung ladder below.
  Representation corrected to Snocone `struct` (DATA) — Val/Node/Tok structs.
  (Session 2026-05-02)

- [ ] **SS-2** — `value.sc`: Val struct + value helpers.
  ```
  struct Val { type, v }
  function val_int(n)    { val_int  = Val('INT',  n);  return; }
  function val_str(s)    { val_str  = Val('STR',  s);  return; }
  function val_real(r)   { val_real = Val('REAL', r);  return; }
  function val_fail()    { val_fail = Val('FAIL', ''); return; }
  function val_null()    { val_null = Val('NULL', ''); return; }
  function is_fail(x)    { is_fail  = IDENT(type(x), 'FAIL'); return; }
  function val_to_str(x) { ... coerce Val to string for OUTPUT ... }
  ```
  Gate: inline test prints 5 lines matching `value.ref`.
  Run: `scrip --ir-run value.sc | diff - value.ref`.

- [ ] **SS-3** — `ir.sc`: Node struct + S-expr printer.
  ```
  struct Node { kind, sval, ival, dval, nc, c }
  function ir_node(kind)       { ... Node(kind,'',0,0.0,0,'') ... }
  function ir_set_sval(n, s)   { sval(n) = s; }
  function ir_set_ival(n, i)   { ival(n) = i; }
  function ir_add_child(n, ch) { ... grow c array, bump nc(n) ... }
  function ir_print(n)         { ... S-expr format matching C ir_print_node ... }
  ```
  S-expr format: `(E_ILIT 42)`  `(E_VAR x)`
  `(E_ADD\n  (E_ILIT 3)\n  (E_VAR x))` (2-space indent per depth, multi-child on newlines).
  Gate: hand-build `(E_ADD (E_ILIT 3) (E_VAR x))` tree, print it; diff vs `ir.ref`.

- [ ] **SS-4** — `lex.sc`: tokenizer.
  ```
  struct Tok { kind, sval, ival, dval }
  function lex(src) { ... returns ARRAY of Tok structs ... }
  ```
  Token kinds: `T_INT T_REAL T_STR T_IDENT T_KEYWORD`
  `T_PLUS T_MINUS T_STAR T_SLASH T_CARET T_EQ T_2EQ T_NEQ`
  `T_LT T_GT T_LE T_GE T_SEMI T_LPAREN T_RPAREN T_LBRACE T_RBRACE`
  `T_COMMA T_QMARK T_PIPE T_CONCAT T_EOF`
  Gate: lex `'42 + x;'` → 4 tokens printed 1-per-line; diff vs `lex.ref`.

- [ ] **SS-5** — `parse.sc`: recursive-descent parser, literals + arithmetic.
  Precedence: `^` (right) > unary `-` > `* /` > `+ -` > concat (space) > `|`.
  Produces Node tree. Uses token array from `lex()` with a cursor index.
  Gate: `parse('3 + 4 * 2')` → ir_print → `(E_ADD\n  (E_ILIT 3)\n  (E_MUL\n    (E_ILIT 4)\n    (E_ILIT 2)))` diff vs `parse.ref`.

- [ ] **SS-6** — `interp.sc`: evaluator, arithmetic core.
  ```
  function sc_eval(n) { ... dispatch on kind(n) ... returns Val }
  ```
  Handles: `E_ILIT E_FLIT E_QLIT E_NUL E_ADD E_SUB E_MUL E_DIV E_POW E_MNS E_PLS`.
  Gate: eval `parse('3 + 4')` → `val_to_str` → `7`; diff vs `interp.ref`.

- [ ] **SS-7** — `snocone.sc` driver + `runtime.sc`: wire lex→parse→interp, `OUTPUT =`.
  Statement loop: for each stmt, eval subject; if `OUTPUT` assign, print val_to_str.
  Gate: run `sc1_literals.sc` through `snocone.sc`; diff vs `sc1_literals.ref`.

- [ ] **SS-8** — Variables (`E_VAR`, `E_ASSIGN`), symbol table.
  Symbol table: global ARRAY or chain of name→Val pairs.
  `E_VAR` lookup; `E_ASSIGN` store.
  Gate: `sc2_assign.sc` passes; `sc3_arith.sc` passes.

- [ ] **SS-9** — `if/else` (`E_IF`). Gate: `sc4_control.sc` passes.

- [ ] **SS-10** — `while` (`E_WHILE`). Gate: `sc5_while.sc` passes.

- [ ] **SS-11** — `function` def + call + `return`/`freturn` (`E_FNC`, `E_RETURN`).
  Call stack: push/pop local symbol frames.
  Gate: `sc7_procedure.sc` passes.

- [ ] **SS-12** — String concat (space, `E_CAT`), `SIZE()` builtin.
  Gate: `sc8_strings.sc` passes.

- [ ] **SS-13** — `for`, `INPUT` keyword.
  Gate: `sc6_for.sc` passes; `sc10_wordcount.sc` passes.

- [ ] **SS-14** — Pattern match `?` (`E_SCAN`), pattern builtins.
  Call out to scrip's BB broker for actual matching.
  Gate: basic pattern corpus tests pass.

- [ ] **SS-15** — Self-host gate.
  ```bash
  SNO_LIB=. scrip --ir-run snocone.sc < snocone.sc > /tmp/stage1.out
  SNO_LIB=. scrip --ir-run snocone.sc < /tmp/stage1.out > /tmp/stage2.out
  diff /tmp/stage1.out /tmp/stage2.out   # → empty
  ```

---

## Invariants

- Commit identity: LCherryholmes / lcherryh@yahoo.com.
- All `.sc` files live in `corpus/programs/snocone/interpreter/`.
- Main entry point: `snocone.sc`. Supporting files in same folder.
- Representation: Snocone `struct` (DATA) for Val, Node, Tok — no tables, no C glue.
- No patching the runtime to make corpus files work (RULES.md).
- Each rung has a `.ref` file in same folder; gate = `diff` zero.
- TDD: write `.ref` first, then `.sc`, then verify.

---

## Notes

- The current C Snocone compiler stays as Stage 0 bootstrap host (unchanged).
- `struct` in Snocone lowers to SNOBOL4 `DATA()` — constructor + field accessors.
  `struct Val { type, v }` → `Val(type,v)` constructor, `type(x)` / `v(x)` accessors.
  Field on LHS = assignment: `type(x) = 'INT'`.
- Andrew Koenig's SNOCONE (1981) compiled Snocone → SNOBOL4. We go further:
  Snocone → Snocone's own Node IR → tree-walk eval under scrip.
