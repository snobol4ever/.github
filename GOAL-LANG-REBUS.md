# GOAL-LANG-REBUS.md — Rebus Frontend Ladder

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ NO AST WALKING IN MODES 2/3/4 — see RULES.md § "NO AST WALKING IN MODES 2, 3, OR 4"         ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║  Sess 2026-05-15g removed all tree_t* dereferences from sm_interp.c (mode 2) and                ║
║  sm_jit_interp.c (mode 3). Stubs print [NO-AST] <opcode> on stderr.                              ║
║                                                                                                  ║
║  If a gate breaks with [NO-AST] FOO — write fresh SM/BB lowering for FOO.                       ║
║  Do NOT restore the AST-walking call.  Do NOT route through proc_table_call or any              ║
║  other back-door that hands a tree_t* to mode-2/3/4 code.                                       ║
║                                                                                                  ║
║  Mode 1 (`--interp` standalone AST interp) is unchanged and remains the reference path.        ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝


╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** SCRIP
**Done when:** Rebus programs pass under all three modes (--interp, --interp,
--run). Core language features (functions, pattern match, generators,
records) work. A test suite of 20+ programs passes.

**Cross-pollination:** Rebus uses BB_SCAN (pattern) and BB_PUMP (generators),
the same broker modes as SNOBOL4 and Icon. bb_boxes.c fixes benefit Rebus.
interp_eval E_IF/E_WHILE/E_RETURN fixes (from SNOBOL4/Snocone) benefit Rebus.
Share fixes via main — no branches.

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
bash /home/claude/SCRIP/scripts/build_spitbol_oracle.sh
```

Gate after setup:
```bash
bash /home/claude/SCRIP/scripts/test_smoke_rebus.sh            # PASS=4
bash /home/claude/SCRIP/scripts/test_smoke_unified_broker.sh   # PASS=31
bash /home/claude/SCRIP/scripts/test_crosscheck_rebus.sh       # 3-mode divergence check
```

---

## Architecture reminder

```
.reb → rebus_compile() → CODE_t* [LANG_REB]   (FI-1 wired)
    --interp  → execute_program() → polyglot_execute() → execute_program()
                (Rebus lowers to SNO-style label/goto chains — FI-1B)
    --interp  → sm_lower() LANG_SNO path (Rebus shares LANG_SNO lowering)
    --run → sm_codegen() same path

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

Current baseline: PASS=4 --interp (output, arith, var, concat).
Rebus frontend wired (FI-1) but many language features not lowered.

### Phase 1 — IR-run: core language features

- [x] **RB-1** — Basic output/arith/var/concat: PASS=4. (done, FI-1)

- [ ] **RB-2** — Control flow: `if/then/else`, `while/do`.
  Verify snocone_lower.c control flow fixes (SC-3/SC-4) reach Rebus via
  shared interp_eval E_IF/E_WHILE. Write `test/rebus/test_control.reb`.
  Gate: PASS under --interp.

- [ ] **RB-3** — Functions: `function f(args) ... return val ... end`.
  Verify function def + call works. Write `test/rebus/test_func.reb`.
  Gate: recursive Fibonacci PASS.

- [ ] **RB-4** — Pattern match: `expr ? pattern`.
  Wire `expr ? pat` in rebus_lower.c → STMT_t subject+pattern → BB_SCAN.
  Write `test/rebus/test_pattern.reb` (ARB, SPAN, BREAK, literal).
  Gate: PASS under --interp.

- [ ] **RB-5** — Pattern replace: `expr ? pat <- repl`.
  Wire replace field in STMT_t. Gate: replace test PASS.

- [ ] **RB-6** — Alternation generator: `expr | expr`.
  E_ALT_GEN → icn_bb_alt_gen (write in icon_gen.c — shared with Icon IC-18).
  Write `test/rebus/test_altgen.reb`.
  Gate: PASS under --interp.

- [ ] **RB-7** — Records: `record R(f1,f2)` / `R(v1,v2)` / `r.f1`.
  E_RECORD + E_FIELD in rebus_lower.c. Wire to E_RECORD/E_FIELD in interp_eval.
  Write `test/rebus/test_record.reb`.
  Gate: PASS under --interp.

- [ ] **RB-8** — String builtins: `size(s)`, `type(x)`, `image(x)`.
  Map to existing SNOBOL4 builtins SIZE, DATATYPE, IMAGE.
  Write `test/rebus/test_builtins.reb`.
  Gate: PASS under --interp.

- [ ] **RB-9** — `fail` / `stop` / `exit` / `next`.
  fail → FAILDESCR; stop/exit → terminate; next → E_LOOP_NEXT.
  Write `test/rebus/test_flow.reb`.
  Gate: PASS under --interp.

- [ ] **RB-10** — Write `scripts/test_rebus_ir_suite.sh`.
  Runs RB-2 through RB-9 tests. Gate: all PASS.

- [ ] **RB-11** — 20-program corpus.
  Write 20 .reb programs in `test/rebus/` covering all features.
  Include: fibonacci, palindrome, wordcount, pattern demos, record demos.
  .ref files: derive from equivalent SNOBOL4 or Icon programs under SPITBOL/Unicon.
  Gate: all 20 PASS under --interp.

### Phase 2 — SM-run (x86)

- [ ] **RB-12** — RB-1 through RB-9 tests under --interp.
  Rebus lowers to LANG_SNO path in sm_lower.c.
  Gate: all PASS.

- [ ] **RB-13** — Full 20-program corpus under --interp.
  Gate: PASS=20.

### Phase 3 — JIT-run (x86 in-memory)

- [ ] **RB-14** — RB-1 through RB-9 tests under --run.
  Gate: all PASS.

- [ ] **RB-15** — Full 20-program corpus under --run.
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
- Share generator boxes with Icon/Raku sessions.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

---

## Current state (2026-04-14, SCRIP HEAD 43dc03da)

RB-1 done: PASS=4 (output, arith, var, concat) --interp.
RB-2 next: control flow verification.
RB-6 (alternation generator) coordinates with GOAL-LANG-ICON IC-18 (icn_bb_alt_gen).

---

## --monitor: in-process sync comparator (IM-7/IM-8 complete)

`--monitor` runs IR, SM, and JIT step-by-step over the same program,
snapshot/restoring all mutable state between runs, and reports the first
statement where any two executors diverge.

```bash
./scrip --monitor file.sno    # SNOBOL4
./scrip --monitor file.icn    # Icon
./scrip --monitor file.pl     # Prolog
./scrip --monitor file.raku   # Raku
./scrip --monitor file.snc    # Snocone
./scrip --monitor file.reb    # Rebus
```

**On agreement:** prints per-stmt progress, exits 0.
**On divergence:** exits 1 and prints:
```
DIVERGE at stmt N [label: LABEL, line LL]
  IR   last_ok=?
  SM   last_ok=1
  JIT  last_ok=1
  IR vs SM (N var(s) differ):
    VARNAME    IR=<value>    SM=<value>
```

**Workflow for finding bugs:**
1. Run `./scrip --monitor suspect.sno` to find the first diverging statement.
2. The statement number + variable name pinpoint the root cause.
3. Fix in the appropriate layer (interp.c for IR bugs, sm_interp.c or
   sm_codegen.c for SM/JIT bugs).
4. Re-run `--monitor` to confirm divergence is gone.
5. Run `test_smoke_unified_broker.sh` — must stay PASS=31 FAIL=0.

**Note:** `--monitor` is incompatible with `--interp`/`--run`
(it drives all three internally). ICN frame locals (IM-10) and Prolog trail
variables (IM-11) are not yet in the snapshot — coming in future IM steps.

