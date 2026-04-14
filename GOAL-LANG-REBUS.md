# GOAL-LANG-REBUS.md — Rebus Frontend Ladder

**Repo:** one4all
**Done when:** Rebus programs pass under all three modes (--ir-run, --sm-run,
--jit-run). Core language features (functions, pattern match, generators,
records) work. A test suite of 20+ programs passes.

**Cross-pollination:** Rebus uses BB_SCAN (pattern) and BB_PUMP (generators),
the same broker modes as SNOBOL4 and Icon. bb_boxes.c fixes benefit Rebus.
interp_eval E_IF/E_WHILE/E_RETURN fixes (from SNOBOL4/Snocone) benefit Rebus.
Share fixes via main — no branches.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_rebus.sh            # PASS=4
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh   # PASS=31
```

---

## Architecture reminder

```
.reb → rebus_compile() → Program* [LANG_REB]   (FI-1 wired)
    --ir-run  → execute_program() → polyglot_execute() → execute_program()
                (Rebus lowers to SNO-style label/goto chains — FI-1B)
    --sm-run  → sm_lower() LANG_SNO path (Rebus shares LANG_SNO lowering)
    --jit-run → sm_codegen() same path

Pattern match: expr ? pat → BB_SCAN (same as SNOBOL4)
Generators:    expr | expr  (alternation) → E_ALT_GEN → BB_PUMP
```

## Rebus language reference

Rebus (Griswold TR 84-9) is goal-directed like Icon but with SNOBOL4-style
pattern primitives. Key constructs:

| Construct | Meaning |
|-----------|---------|
| `function f(args) ... end` | Function definition |
| `expr ? pat` | Pattern match (BB_SCAN) |
| `expr ? pat <- repl` | Pattern replace |
| `expr \| expr` | Alternation generator (BB_PUMP) |
| `record R(f1,f2)` | Record type |
| `OUTPUT := expr` | Print output |
| `x := expr` | Assignment |
| `if cond then stmt` | Conditional |
| `while cond do stmt` | Loop |
| `return expr` / `fail` | Function exit |

---

## Rung ladder — all modes, x86

Current baseline: PASS=4 --ir-run (output, arith, var, concat).
Rebus frontend wired (FI-1) but many language features not lowered.

### Phase 1 — IR-run: core language features

- [x] **RB-1** — Basic output/arith/var/concat: PASS=4. (done, FI-1)

- [ ] **RB-2** — Control flow: `if/then/else`, `while/do`.
  Verify snocone_lower.c control flow fixes (SC-3/SC-4) reach Rebus via
  shared interp_eval E_IF/E_WHILE. Write `test/rebus/test_control.reb`.
  Gate: PASS under --ir-run.

- [ ] **RB-3** — Functions: `function f(args) ... return val ... end`.
  Verify function def + call works. Write `test/rebus/test_func.reb`.
  Gate: recursive Fibonacci PASS.

- [ ] **RB-4** — Pattern match: `expr ? pattern`.
  Wire `expr ? pat` in rebus_lower.c → STMT_t subject+pattern → BB_SCAN.
  Write `test/rebus/test_pattern.reb` (ARB, SPAN, BREAK, literal).
  Gate: PASS under --ir-run.

- [ ] **RB-5** — Pattern replace: `expr ? pat <- repl`.
  Wire replace field in STMT_t. Gate: replace test PASS.

- [ ] **RB-6** — Alternation generator: `expr | expr`.
  E_ALT_GEN → icn_bb_alt_gen (write in icon_gen.c — shared with Icon IC-18).
  Write `test/rebus/test_altgen.reb`.
  Gate: PASS under --ir-run.

- [ ] **RB-7** — Records: `record R(f1,f2)` / `R(v1,v2)` / `r.f1`.
  E_RECORD + E_FIELD in rebus_lower.c. Wire to E_RECORD/E_FIELD in interp_eval.
  Write `test/rebus/test_record.reb`.
  Gate: PASS under --ir-run.

- [ ] **RB-8** — String builtins: `size(s)`, `type(x)`, `image(x)`.
  Map to existing SNOBOL4 builtins SIZE, DATATYPE, IMAGE.
  Write `test/rebus/test_builtins.reb`.
  Gate: PASS under --ir-run.

- [ ] **RB-9** — `fail` / `stop` / `exit` / `next`.
  fail → FAILDESCR; stop/exit → terminate; next → E_LOOP_NEXT.
  Write `test/rebus/test_flow.reb`.
  Gate: PASS under --ir-run.

- [ ] **RB-10** — Write `scripts/test_rebus_ir_suite.sh`.
  Runs RB-2 through RB-9 tests. Gate: all PASS.

- [ ] **RB-11** — 20-program corpus.
  Write 20 .reb programs in `test/rebus/` covering all features.
  Include: fibonacci, palindrome, wordcount, pattern demos, record demos.
  .ref files: derive from equivalent SNOBOL4 or Icon programs under SPITBOL/Unicon.
  Gate: all 20 PASS under --ir-run.

### Phase 2 — SM-run (x86)

- [ ] **RB-12** — RB-1 through RB-9 tests under --sm-run.
  Rebus lowers to LANG_SNO path in sm_lower.c.
  Gate: all PASS.

- [ ] **RB-13** — Full 20-program corpus under --sm-run.
  Gate: PASS=20.

### Phase 3 — JIT-run (x86 in-memory)

- [ ] **RB-14** — RB-1 through RB-9 tests under --jit-run.
  Gate: all PASS.

- [ ] **RB-15** — Full 20-program corpus under --jit-run.
  Gate: PASS=20.

---

## Key files

| File | Role |
|------|------|
| `src/frontend/rebus/rebus.y` | Bison grammar |
| `src/frontend/rebus/lex.rebus.c` | Flex lexer (generated) |
| `src/frontend/rebus/rebus_lower.c` | IR lowering — main work here |
| `src/frontend/rebus/rebus_lower.h` | `rebus_compile()` declaration |
| `src/frontend/icon/icon_gen.c` | Generator boxes — shared |
| `test/rebus/` | Test programs (create here) |
| `scripts/test_smoke_rebus.sh` | Smoke gate |

---

## Invariants

- Gate = PASS=31 FAIL=0 on test_smoke_unified_broker.sh after every commit.
- bb_broker.c is frozen.
- Share generator boxes with Icon/Raku sessions.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

---

## Current state (2026-04-14, one4all HEAD 43dc03da)

RB-1 done: PASS=4 (output, arith, var, concat) --ir-run.
RB-2 next: control flow verification.
RB-6 (alternation generator) coordinates with GOAL-LANG-ICON IC-18 (icn_bb_alt_gen).
