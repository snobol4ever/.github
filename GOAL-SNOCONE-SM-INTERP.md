# GOAL-SNOCONE-SM-INTERP — Self-hosting SM interpreter in Snocone

**Repo:** corpus (primary) + one4all + .github
**Done when:** `corpus/SCRIP/sm_interp.sc` is a Snocone interpreter for the
SM_Program produced by `lower.sc`. Composed end-to-end via
`scrip --ir-run tree.sc lower.sc lower_driver.sc sm_interp.sc <prog>.sc`,
the pipeline reads a Snocone program, lowers it to SM via `lower()`, then
executes the SM in-process via `sm_interp.sc` — closing the self-hosting
loop without ever leaving the .sc world.

---

## Goal statement

The C runtime walks `SM_Program` in `src/runtime/x86/sm_interp.c` (2129 lines,
87 opcode cases).  A Snocone translation has two purposes:

1. **Self-hosting (M2).** With both `lower.sc` and `sm_interp.sc` running
   under scrip, scrip's SNOBOL4/Snocone frontends can drive an entire
   compile-and-execute pipeline written in Snocone.  This is the final
   waypoint before Milestone 2 (`scrip_stage2 = scrip_stage1(scrip_stage1)`):
   once lower+interp both self-host, a Snocone front-end translation can
   plug in and we have the full stack.

2. **The ultimate test for `lower.sc`.** Today `lower.sc` is verified
   structurally (opcode names + operands match `.ref` files).  Once
   `sm_interp.sc` exists, programs can be verified *semantically* —
   the SM emitted by `lower()` actually runs and produces the expected
   user-visible output.  Two independent code paths (C interpreter
   under `--ir-run`, and the Snocone interpreter on top of it) must
   agree on every result.

The cross-check pattern is:

```
prog.sc  --(scrip C path)-->  prog.out
prog.sc  --(lower.sc + sm_interp.sc, hosted on scrip)-->  prog.out
                                                              ^
                                          byte-identical for every test
```

---

## Architecture reminders

### How a self-hosted run looks

```
$ scrip --ir-run tree.sc lower.sc lower_driver.sc sm_interp.sc hello.sc
```

scrip concatenates all six files into one program, parses and lowers it
via the C `lower()`, then runs the result via C `sm_interp_run()`.  During
that C-side run, the Snocone-defined `sm_interp_run_sc()` function ends up
being called with the SM_Program produced by the Snocone-defined `lower()`
function — applied to whatever AST the user program had built.

### State variables

`sm_interp.sc` shares `lower.sc`'s SM_Program representation: `g_count`
(instruction count) and `g_instr_tbl[idx]` (table of `sm_instr` records,
each `op a0 a1 a2`).

Interpreter state, all module-global in `sm_interp.sc`:

| Name           | Purpose                                       |
|----------------|-----------------------------------------------|
| `si_pc`        | program counter                               |
| `si_stack`     | TABLE used as value stack (`si_stack[sp]`)    |
| `si_sp`        | stack pointer                                 |
| `si_last_ok`   | last expression succeeded (0/1)               |
| `si_stno`      | current statement number (from `SM_STNO`)     |
| `si_halted`    | set on `SM_HALT`, terminates loop             |

Value-stack entries are Snocone scalars — string, integer, or real —
plus a distinguished "FAIL" marker.  Snocone's natural `DATATYPE`
already discriminates these, so no boxing wrapper is needed for Ph1.

### Variable namespace = host namespace

`SM_PUSH_VAR "OUTPUT"` reads the host program's `OUTPUT` variable via
Snocone's `$"OUTPUT"` indirection; `SM_STORE_VAR "OUTPUT" = val` writes
it the same way.  This is intentional self-hosting: a Snocone program
executed by `sm_interp.sc` writes to the same `OUTPUT` and reads from
the same `INPUT` that scrip itself uses — its output is naturally
captured by scrip's own stdout pipeline.

---

## Scope — Phase 1 (this goal)

Translate enough of `sm_interp.c` to run programs that exercise the
opcodes `lower.sc` already emits and that `smoke_lower.sc` /
`sm_lower_test.sc` already produce.  That is the minimum bootstrap.
Phase 2 will extend coverage to patterns, calls, and generators.

### Translate fully (Phase 1)

Opcodes — minimum self-test set:

- `SM_LABEL` — no-op
- `SM_HALT`  — set `si_halted = 1`
- `SM_STNO`  — store `si_stno`, reset `si_sp = 0`
- `SM_JUMP`  / `SM_JUMP_S` / `SM_JUMP_F` — program-counter jumps
- `SM_PUSH_LIT_S` / `SM_PUSH_LIT_I` / `SM_PUSH_LIT_F` — push scalars
- `SM_PUSH_NULL` — push the empty string `''`
- `SM_PUSH_VAR` — read host variable by name (`$name`)
- `SM_STORE_VAR` — write host variable by name (`$name = pop()`)
- `SM_VOID_POP` — discard TOS
- `SM_ADD` / `SM_SUB` / `SM_MUL` / `SM_DIV` / `SM_MOD` / `SM_NEG` — arithmetic
- `SM_CONCAT` — string concat of two TOS values
- `SM_COERCE_NUM` — numeric coercion via `+ 0`

### Stub or omit (Phase 1)

- All `SM_PAT_*` and `SM_EXEC_STMT` — stub `lower_pat_expr` already
  produces these, but Phase 1 sm_interp emits `'sm_interp: pattern opcodes
  deferred to Ph2'` on stderr and halts.
- `SM_CALL_FN` / `SM_PUSH_EXPR` / `SM_PUSH_EXPRESSION` / `SM_CALL_EXPRESSION`
  — same, deferred.
- All `SM_BB_*` (broker pumps for Icon / Prolog) — same.
- Generator opcodes (`SM_SUSPEND_VALUE`, `SM_RESUME`, `SM_GEN_TICK`) — same.

Phase 1 success: a `hello.sc` style program that does
`OUTPUT = 'hi'; END` runs end-to-end under the self-hosted pipeline and
produces `hi` on stdout, byte-identical to running the same program
under raw scrip.

---

## Corpus target

```
corpus/SCRIP/
    sm_interp.sc                 — main translation (this goal)
    smoke_interp.sc              — minimal hosted: OUTPUT = 'hi'; END    (SI-2)
    smoke_interp.ref             — baked output                          (SI-2)
    smoke_interp_native.sc       — equivalent native source              (SI-5)
    sm_interp_test.sc            — hosted arithmetic: X = 2+3; OUT=X*4   (SI-4)
    sm_interp_test.ref           — baked output                          (SI-4)
    sm_interp_test_native.sc     — equivalent native source              (SI-5)
```

Plus `one4all/scripts/test_self_host_smoke.sh` for the SI-5 cross-check.

A separate `sm_interp_driver.sc` was not needed: each hosted test
calls `lower(g_program)` then `sm_interp_run_sc()` directly inline,
keeping driver and test fused in one file.

---

## Session Setup

```bash
cd /home/claude/one4all
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
cd /home/claude/corpus
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
cd /home/claude/.github
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
bash /home/claude/one4all/scripts/build_scrip.sh
```

### How to run

```bash
SCRIP=/home/claude/one4all/scrip
SCRIP_DIR=/home/claude/corpus/SCRIP

$SCRIP --ir-run \
  $SCRIP_DIR/tree.sc \
  $SCRIP_DIR/lower.sc \
  $SCRIP_DIR/lower_driver.sc \
  $SCRIP_DIR/sm_interp.sc \
  $SCRIP_DIR/sm_interp_driver.sc \
  $SCRIP_DIR/<smoke or test>.sc
```

---

## Rungs

The rungs retrace, in order, the lower.sc rungs SL-1..SL-9 — but on the
interpreter side.  Each rung extends `sm_interp.sc` to handle the SM
opcodes produced by the corresponding lower.sc rung's tests.

### SI-1 — Skeleton + dispatch loop ✅ sess 2026-05-12

Created `sm_interp.sc` with module globals, `si_push`/`si_pop` helpers, and
the main `sm_interp_run_sc()` loop dispatching on `op(g_instr_tbl[si_pc])`.
Pre-increment `si_pc` before dispatch matches C convention.

- [x] Create `sm_interp.sc` skeleton
- [x] Implement `SM_HALT`, `SM_LABEL`
- [x] Inline smoke: `lower(empty TT_PROGRAM)` → `sm_interp_run_sc()` is silent

### SI-2 — STNO + literals + variables + VOID_POP ✅ sess 2026-05-12

Implemented `SM_STNO`, `SM_PUSH_LIT_S/I/F`, `SM_PUSH_NULL`, `SM_PUSH_VAR`,
`SM_STORE_VAR`, `SM_VOID_POP`.  `SM_PUSH_VAR` uses `$name` indirection to
read the host program's namespace; `SM_STORE_VAR` writes the same way.
This is the self-hosting trick: when the hosted program does `OUTPUT = ...`,
real host OUTPUT receives the value and scrip's stdout magic prints it.

`smoke_interp.sc` hand-builds AST for `OUTPUT = 'hi'; END`, lowers, runs.
Stdout: `--- interp ---\nhi\n--- done ---\n`.  First self-hosted output. ✓

- [x] Implement listed opcodes
- [x] Create `smoke_interp.sc` + `.ref`
- [x] Gate: self-hosted output byte-identical to native scrip output (see SI-5)

### SI-3 — Jumps ✅ sess 2026-05-12

Implemented `SM_JUMP`, `SM_JUMP_S`, `SM_JUMP_F` — three one-liners.
`a0(ins) + 0` coerces the stringified target back to integer pc.

- [x] Implement jumps
- [x] Test program with control flow runs end-to-end (covered by SI-4 test)

### SI-4 — Arithmetic + COERCE + CONCAT ✅ sess 2026-05-12

Implemented `SM_ADD`, `SM_SUB`, `SM_MUL`, `SM_DIV`, `SM_MOD`, `SM_NEG`,
`SM_COERCE_NUM`, `SM_CONCAT` — all one-liners riding on host Snocone
arithmetic and string-concat operators.  `a + 0` is the standard
string-to-number coercion idiom.  `SM_CONCAT` is `si_push(a b)` — Snocone
juxtaposition.

`sm_interp_test.sc` hand-builds AST for `X = 2 + 3; OUTPUT = X * 4; END`,
self-hosted execution prints `20`.

- [x] Implement arithmetic + concat
- [x] Create `sm_interp_test.sc` + `.ref`

### SI-5 — Cross-check gate ✅ sess 2026-05-12

`one4all/scripts/test_self_host_smoke.sh` runs each test program through
both the self-hosted pipeline and natively under scrip, then diffs stdout.
Two cases (`smoke_interp` and `sm_interp_test`) both pass byte-identical.

This is the operational form of "ultimate test for lower.sc" — semantic
equivalence between the SM stream produced by lower.sc and the AST
interpreter scrip uses directly.

- [x] Write test script
- [x] Two test programs pass (SI-6+ will broaden coverage)

**Runtime is trivial as expected.**  `sm_interp.sc` is ~70 lines total;
each opcode arm is a one-liner stack push/pop with a call into a host
operator.  No value boxing, no separate arithmetic engine, no string
machinery — the host IR interp handles all of that.  The .sc program is
purely stack-and-dispatch plumbing.

**Known Ph2 concern — namespace collision.**  Because all `--ir-run` files
share one variable namespace, a user program that names a variable `si_pc`
or `g_count` would clash with interpreter / lowerer state.  Phase 2 needs
either a prefix discipline (already followed: `si_*` / `g_*`) made
explicit and documented, or a TABLE-based local frame.  Not blocking SI-1..SI-5.

### SI-6..SI-N — Phase 2 (separate session)

Patterns, EXEC_STMT, calls, generators.  Each rung adds one opcode
family with a corresponding test program.  Order to be determined by
what existing corpus programs we want to run self-hosted next.

---

## Gate

```bash
SCRIP=/home/claude/one4all/scrip
SCRIP_DIR=/home/claude/corpus/SCRIP

# Gate 1: smoke_interp self-hosted byte-identical to baked .ref
$SCRIP --ir-run \
  $SCRIP_DIR/tree.sc $SCRIP_DIR/lower.sc $SCRIP_DIR/lower_driver.sc \
  $SCRIP_DIR/sm_interp.sc $SCRIP_DIR/smoke_interp.sc \
  | diff - $SCRIP_DIR/smoke_interp.ref

# Gate 2: sm_interp_test self-hosted byte-identical to baked .ref
$SCRIP --ir-run \
  $SCRIP_DIR/tree.sc $SCRIP_DIR/lower.sc $SCRIP_DIR/lower_driver.sc \
  $SCRIP_DIR/sm_interp.sc $SCRIP_DIR/sm_interp_test.sc \
  | diff - $SCRIP_DIR/sm_interp_test.ref

# Gate 3: SI-5 cross-check — hosted == native for every test
bash /home/claude/one4all/scripts/test_self_host_smoke.sh
```

All three must pass before any commit that advances SI-2 or beyond.
