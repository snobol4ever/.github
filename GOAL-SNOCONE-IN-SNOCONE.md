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

**⚠️ DO NOT run `find` or `ls -R` on the repos.** The file listings are enormous
and consume most of the context window before any work is done. Navigate directly
to the files named in this goal file.

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
    parse.sc        ← compiland-pattern parser → IR Node tree (beauty.sno style)
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
```

**Tokens** (`lex.sc`):
```
struct Tok { kind, sval, ival, dval }
// kind: 'T_INT' | 'T_STR' | 'T_IDENT' | 'T_PLUS' | 'T_SEMI' | ...
```

---

## IR Interpreter Rewrite Proposal
### (SS-0 — analysis pass, Session 2026-05-02)

The C `interp.c` is **not a clean model** for `interp.sc`. Audit findings:

- **6,201 lines**, single file, one function (`interp_eval`) spanning lines 1147–5114 (~3,967 lines)
- **253 references** to Icon-specific state (`ICN_CUR`, `icn_frame_depth`, `icn_scan_*`, `icn_drive_*`)
- **98 patch-tag comments** (`SN-`, `OE-`, `DYN-`, `BUG-`, `BP-`) — accumulated fixes, not clean design
- **Control-flow nodes appear twice**: `E_IF`/`E_WHILE`/`E_RETURN` at ~line 3106 (Icon guard) and again at ~line 4409 (shared switch)
- **Builtins** dispatch through `APPLY_fn` into the binary `snobol4.c` (SPITBOL-generated data file) — not readable source
- **`execute_program()`** entangled with monitor/bridge sync events, `setjmp`/`longjmp`, polyglot dispatch, step-limit machinery
- **`call_user_function()`** (~400 lines) handles SNOBOL4 OPSYN aliases, shadow tables, bridge coverage events — Snocone needs none of this

**What Snocone actually needs from interp.c** — maybe 200 clean lines:

```
sc_eval(node):
  kind = kind(node)
  if kind == 'E_ILIT'  → val_int(ival(node))
  if kind == 'E_FLIT'  → val_real(dval(node))
  if kind == 'E_QLIT'  → val_str(sval(node))
  if kind == 'E_NUL'   → val_null()
  if kind == 'E_VAR'   → env_get(sval(node))
  if kind == 'E_ASSIGN'→ env_set(child(node,0), sc_eval(child(node,1)))
  if kind == 'E_ADD'   → val_int(val_num(sc_eval(c0)) + val_num(sc_eval(c1)))
  ... SUB MUL DIV POW MNS ...
  if kind == 'E_CAT'   → val_str(val_to_str(sc_eval(c0)) val_to_str(sc_eval(c1)))
  if kind == 'E_IF'    → if ~is_fail(sc_eval(c0)) { sc_eval(c1) } else { sc_eval(c2) }
  if kind == 'E_WHILE' → while ~is_fail(sc_eval(c0)) { sc_eval(c1) }
  if kind == 'E_FNC'   → sc_call(sval(node), args...)
  if kind == 'E_RETURN'→ set return-val, signal return
  if kind == 'E_SCAN'  → sc_scan(sc_eval(c0), sc_eval(c1))
  ...
```

**Parser decision:** The bison `.y` grammar is not a portable model.
The right shape for `parse.sc` is beauty.sno's compiland pattern:
read source line by line, apply patterns to classify tokens, build
Node structs bottom-up with a shift-reduce or Pratt approach.
**Dependency:** beauty.sc (GOAL-SNOCONE-BEAUTY) is ON HOLD. For now,
`parse.sc` will use recursive-descent (hand-written in Snocone),
treating it as replaceable when beauty.sc lands.

**Plan:** Write `interp.sc` fresh from the conceptual algorithm above —
do NOT port from `interp.c`. Use the C code only to verify which node
kinds Snocone actually emits (audited: ~20 of the 90 EKind values).

---

## Open rungs

- [x] **SS-0** — Analyze `one4all/src/driver/interp.c` and `one4all/src/frontend/snocone/`. Identify exactly which EKind values the Snocone frontend emits. Confirm the sc_eval dispatch shape for those ~20 kinds. Confirm what `val_to_str` needs to handle. Write findings in this file before writing any `.sc` files.
  **⚠️ THIS IS THE CURRENT STEP. Start here. Do not skip to SS-2.**

  **Findings (Session 2026-05-02):**

  The Snocone frontend (`snocone_parse.y`) does **not** emit `E_IF`, `E_WHILE`,
  `E_FOR`, `E_RETURN`, `E_LOOP_BREAK`, `E_LOOP_NEXT` as IR nodes. Control flow
  is **lowered to labels and gotos at parse time** — `if`/`while`/`for`/`break`/
  `return` all become `STMT_t` sequences (conditional-fail gotos, unconditional
  gotos, label pads) via `sc_make_cond_fail_stmt`, `sc_make_goto_uncond_stmt`,
  `sc_make_label_stmt`.

  **EKind values the Snocone frontend actually emits:**
  - Literals: `E_ILIT` `E_FLIT` `E_QLIT` `E_NUL`
  - Variables: `E_VAR`
  - Arithmetic: `E_ADD` `E_SUB` `E_MUL` `E_DIV` `E_POW` `E_MNS` `E_PLS`
  - String/pattern: `E_CAT`/`E_SEQ` (concat) `E_ALT` (alternation) `E_SCAN` (pattern match `?`)
  - Assignment: `E_ASSIGN`
  - Subscript: `E_IDX`
  - Function call: `E_FNC` (also used for builtins EQ/NE/LT/GT/LE/GE/LEQ/LNE/LLT/LGT/LLE/LGE/IDENT/DIFFER)

  **NOT emitted by Snocone frontend:** `E_IF` `E_WHILE` `E_FOR` `E_RETURN`
  `E_LOOP_BREAK` `E_LOOP_NEXT` `E_MOD` (no `%` operator in Snocone syntax).

  **Implication for `interp.sc`:** The interpreter only needs to handle the ~15
  EKind values above. Control flow (`if`/`while`/`for`) is already gone by the
  time the IR reaches the interpreter — it's gotos and labels at the STMT level,
  executed by the statement loop, not by `sc_eval`. This makes `interp.sc`
  significantly simpler than the goal file's original algorithm sketch implied.

  **`val_to_str` needs to handle:** INT (format as decimal integer), REAL (format
  as decimal real), STR (return as-is), NULL (return ''), FAIL (should not be
  asked to convert — caller must check `is_fail` first).

  **`E_CAT`/`E_SEQ`:** In Snocone (non-Icon) mode, `E_CAT` and `E_SEQ` are both
  string concatenation. Null string identity rule applies (null cat x = x).

  **Pattern primitives (SPAN, BREAK, ANY, LEN, POS, TAB, ARB, REM, FENCE, ARBNO, NOTANY):**
  These have dedicated `E_SPAN`, `E_BREAK` etc. IR nodes, but the Snocone frontend
  does **not** emit them — all pattern primitives go through `E_FNC` with the name
  as sval (e.g. `E_FNC("SPAN", arg)`). They are dispatched at runtime via `APPLY_fn`
  into the SNOBOL4 runtime. So `interp.sc` does not need dedicated cases for them.


  evaluates subject as string, evaluates pattern in pat context, calls `exec_stmt`,
  returns NULVCL on success or FAILDESCR on failure.



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
  Token kinds: `T_INT T_REAL T_STR T_IDENT`
  `T_PLUS T_MINUS T_STAR T_SLASH T_CARET`
  `T_EQ T_2EQ T_NEQ T_LT T_GT T_LE T_GE`
  `T_SEMI T_LPAREN T_RPAREN T_LBRACE T_RBRACE T_LBRACK T_RBRACK`
  `T_COMMA T_QMARK T_PIPE T_CONCAT T_EOF`
  Implemented as pattern matching on source string (SPAN/BREAK/LEN/ANY).
  Gate: lex `'42 + x;'` → 4 tokens printed 1-per-line; diff vs `lex.ref`.

- [ ] **SS-5** — `parse.sc`: recursive-descent parser, literals + arithmetic.
  Precedence: `^` (right) > unary `-` > `* /` > `+ -` > concat (space) > `|`.
  Produces Node tree. Token cursor via global index into Tok array.
  Gate: `parse('3 + 4 * 2')` ir_print → correct S-expr; diff vs `parse.ref`.

- [ ] **SS-6** — `interp.sc`: evaluator, arithmetic core.
  Written fresh (NOT ported from interp.c). Clean dispatch on kind(node).
  Handles: `E_ILIT E_FLIT E_QLIT E_NUL E_ADD E_SUB E_MUL E_DIV E_POW E_MNS E_PLS`.
  Gate: eval `parse('3 + 4')` → val_to_str → `7`; diff vs `interp.ref`.

- [ ] **SS-7** — `snocone.sc` driver + `runtime.sc`: wire lex→parse→interp, `OUTPUT =`.
  Statement loop: for each stmt node, eval subject; if OUTPUT assign, print val_to_str.
  Gate: run `sc1_literals.sc` through `snocone.sc`; diff vs `sc1_literals.ref`.

- [ ] **SS-8** — Variables (`E_VAR`, `E_ASSIGN`), symbol table.
  Symbol table: ARRAY of name→Val pairs (or linked list of `struct Binding { name, val }`).
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
  Call through to scrip's BB broker for actual matching.
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
- `interp.sc` written fresh from algorithm — do NOT port from interp.c.

---

## Notes

- The current C Snocone compiler stays as Stage 0 bootstrap host (unchanged).
- `struct` in Snocone lowers to SNOBOL4 `DATA()` — constructor + field accessors.
  `struct Val { type, v }` → `Val(type,v)` constructor, `type(x)` / `v(x)` accessors.
  Field on LHS = assignment: `type(x) = 'INT'`.
- beauty.sc (GOAL-SNOCONE-BEAUTY, ON HOLD) is the eventual model for parse.sc.
  Until it lands, parse.sc uses recursive-descent.
- Snocone emits ~20 of the 90 EKind values. Full list:
  `E_QLIT E_ILIT E_FLIT E_NUL E_VAR E_FNC E_ASSIGN`
  `E_ADD E_SUB E_MUL E_DIV E_POW E_MNS E_PLS E_MOD`
  `E_CAT E_ALT E_SEQ E_SCAN`
  `E_IF E_WHILE E_RETURN E_LOOP_BREAK E_LOOP_NEXT`
  `E_IDX` (array subscript)
