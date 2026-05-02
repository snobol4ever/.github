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
    value.sc        ← DESCR value representation: val_int/val_str/val_fail/is_fail/val_to_str
    ir.sc           ← IR node constructors + S-expr pretty-printer
    lex.sc          ← tokenizer: returns token-list table
    parse.sc        ← recursive-descent parser → IR tree (tables)
    interp.sc       ← tree-walk evaluator: eval(node) → value
    runtime.sc      ← builtins: OUTPUT/INPUT/SIZE/IDENT/DIFFER/etc.
```

### IR representation in Snocone

Each IR node is a Snocone table:
```
node = TABLE();
node['kind'] = 'E_ILIT';
node['ival'] = 42;
node['nchildren'] = 0;
```
Children stored as `node['child0']`, `node['child1']`, etc.

---

## Open rungs

- [x] **SS-1** — Write the step plan. Architecture decided: Stage 0 = scrip C host,
  Stage 1 = snocone.sc compiles itself. File layout above. TDD rung ladder below.
  (Session 2026-05-02)

- [ ] **SS-2** — `value.sc`: DESCR value representation.
  Implement `val_int(n)`, `val_str(s)`, `val_real(r)`, `val_fail()`, `val_null()`,
  `is_fail(v)`, `val_to_str(v)`. Values encoded as Snocone tables with `['type']`
  and `['val']` fields. Gate: inline test at bottom of file prints 5 lines,
  matches `.ref`. Run: `scrip --ir-run value.sc`.

- [ ] **SS-3** — `ir.sc`: IR node constructors + S-expr printer.
  `ir_node(kind)`, `ir_set_sval(n,s)`, `ir_set_ival(n,i)`, `ir_add_child(n,c)`,
  `ir_print(n)` → S-expr matching C `ir_print_node` format exactly.
  Gate: hand-build `(E_ADD (E_ILIT 3) (E_VAR x))` and dump it; diff vs expected `.ref`.

- [ ] **SS-4** — `lex.sc`: tokenizer.
  Input: source string. Output: array of token tables, each `['kind','sval','ival','dval']`.
  Token kinds as strings: `'T_INT'`, `'T_STR'`, `'T_IDENT'`, `'T_PLUS'`, `'T_SEMI'`, etc.
  Gate: tokenize `'42 + x;'` → 4 tokens; match `.ref`.

- [ ] **SS-5** — `parse.sc`: recursive-descent parser for literals + arithmetic.
  Pratt/recursive-descent: expr → term → factor → atom.
  Produces IR tree tables. Gate: `parse('3 + 4 * 2')` → `(E_ADD (E_ILIT 3) (E_MUL (E_ILIT 4) (E_ILIT 2)))`.

- [ ] **SS-6** — `interp.sc`: evaluator for E_ILIT, E_FLIT, E_QLIT, E_ADD/SUB/MUL/DIV/POW.
  `eval(node)` → value table. Gate: `eval(parse('3 + 4'))` = `7`.

- [ ] **SS-7** — `runtime.sc` + `snocone.sc` driver: `OUTPUT = expr;` assignment + print.
  Wire lex → parse → interp → output. Gate: `sc1_literals.sc` passes (hello/world/42).

- [ ] **SS-8** — Variables, `E_VAR`, `E_ASSIGN`. Symbol table: global array of name→value pairs.
  Gate: `sc2_assign.sc` passes.

- [ ] **SS-9** — `if/else`, `E_IF`. Gate: `sc4_control.sc` passes.

- [ ] **SS-10** — `while`, `E_WHILE`. Gate: `sc5_while.sc` passes.

- [ ] **SS-11** — `function`, call, `E_RETURN`. Gate: `sc7_procedure.sc` passes.

- [ ] **SS-12** — String concat (space), `E_CAT`, `SIZE()` builtin. Gate: `sc8_strings.sc` passes.

- [ ] **SS-13** — `for`, `INPUT`. Gate: `sc6_for.sc` + `sc10_wordcount.sc` pass.

- [ ] **SS-14** — Pattern match `?`, `E_SCAN`, pattern builtins (SPAN, LEN, ANY, etc.).
  BB broker call-out via scrip's existing pattern machinery.
  Gate: basic pattern corpus tests pass.

- [ ] **SS-15** — Self-host gate.
  `scrip --ir-run snocone.sc < snocone.sc > /tmp/stage1.out`
  `scrip --ir-run snocone.sc < /tmp/stage1.out > /tmp/stage2.out`
  `diff /tmp/stage1.out /tmp/stage2.out` → empty.

---

## Invariants

- Commit identity: LCherryholmes / lcherryh@yahoo.com.
- All `.sc` files live in `corpus/programs/snocone/interpreter/`.
- Main entry point: `snocone.sc`. Supporting files: `value.sc`, `ir.sc`, `lex.sc`,
  `parse.sc`, `interp.sc`, `runtime.sc`.
- No C glue — pure Snocone end-to-end under `scrip --ir-run`.
- No patching the runtime to make corpus files work (RULES.md).
- Each rung has a `.ref` file; gate = zero diff vs ref.
- TDD: write the `.ref` first, then the `.sc`, then verify.

---

## Notes

- The current C Snocone compiler stays as Stage 0 bootstrap host (unchanged).
- Andrew Koenig's SNOCONE (1981) compiled Snocone → SNOBOL4. We go further:
  Snocone → Snocone's own IR tables → tree-walk eval under scrip.
- IR nodes as Snocone tables is the key representation choice: no C structs,
  no external data types — pure Snocone values all the way down.
