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
    sm_interp.sc           — main translation (this goal)
    sm_interp_driver.sc    — wires Lower_run() into Run() (Phase 1: takes
                             the SM table built by lower() in module globals
                             and invokes sm_interp_run_sc())
    smoke_interp.sc        — minimal program: OUTPUT = 'hi'; END
    smoke_interp.ref       — expected stdout: 'hi'
    sm_interp_test.sc      — broader test: assignment + arithmetic
    sm_interp_test.ref     — baked output
```

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

### SI-1 — Skeleton + dispatch loop ⏳ NEXT

Create `sm_interp.sc` with module globals, `si_push`/`si_pop` helpers,
and the main `sm_interp_run_sc()` loop dispatching on `op(g_instr_tbl[si_pc])`.
Empty switch arms for every opcode (each just emits to stderr "unimpl <op>").
Implement `SM_HALT` and `SM_LABEL` only.

Done when: an empty SM_Program with only `SM_HALT` runs through
`sm_interp_run_sc()` without error.  Stderr is silent.

- [ ] Create `sm_interp.sc` skeleton
- [ ] Implement `SM_HALT`, `SM_LABEL`
- [ ] Inline smoke: `lower(empty TT_PROGRAM)` → `sm_interp_run_sc()` is silent

### SI-2 — STNO + literals + variables + VOID_POP

Implement `SM_STNO`, `SM_PUSH_LIT_S/I/F`, `SM_PUSH_NULL`, `SM_PUSH_VAR`,
`SM_STORE_VAR`, `SM_VOID_POP`.

Done when: `smoke_interp.sc` (a hand-built AST equivalent to
`OUTPUT = 'hi'; END`) lowers and runs, producing `hi` on stdout.

- [ ] Implement listed opcodes
- [ ] Create `smoke_interp.sc` + `.ref`
- [ ] Gate: self-hosted output byte-identical to native scrip output

### SI-3 — Jumps

Implement `SM_JUMP`, `SM_JUMP_S`, `SM_JUMP_F`.  Needed for any program
with `:(label)` gotos.

Done when: a 3-statement program with an unconditional goto runs to
completion.

- [ ] Implement jumps
- [ ] Test program with `:(label)` runs end-to-end

### SI-4 — Arithmetic + COERCE + CONCAT

Implement `SM_ADD`, `SM_SUB`, `SM_MUL`, `SM_DIV`, `SM_MOD`, `SM_NEG`,
`SM_COERCE_NUM`, `SM_CONCAT`.

Done when: `sm_interp_test.sc` (assignment + arithmetic, e.g. `X = 2 + 3;
OUTPUT = X * 4; END`) runs and prints `20`.

- [ ] Implement arithmetic + concat
- [ ] Create `sm_interp_test.sc` + `.ref`

### SI-5 — Cross-check gate

Add `scripts/test_self_host_smoke.sh`: for each `*.sc` test in a small
fixed list, run twice — once natively under scrip, once via the
self-hosted lower+interp pipeline — and diff stdout.

Done when: 3+ test programs pass byte-identical diff.

- [ ] Write test script
- [ ] Three test programs pass

### SI-6..SI-N — Phase 2 (separate session)

Patterns, EXEC_STMT, calls, generators.  Each rung adds one opcode
family with a corresponding test program.  Order to be determined by
what existing corpus programs we want to run self-hosted next.

---

## Gate

```bash
SCRIP=/home/claude/one4all/scrip
SCRIP_DIR=/home/claude/corpus/SCRIP

# Gate 1: smoke_interp self-hosted output matches native scrip on same program
NATIVE=$($SCRIP --ir-run $SCRIP_DIR/smoke_interp_native.sc)
HOSTED=$($SCRIP --ir-run $SCRIP_DIR/tree.sc $SCRIP_DIR/lower.sc \
                          $SCRIP_DIR/lower_driver.sc \
                          $SCRIP_DIR/sm_interp.sc \
                          $SCRIP_DIR/sm_interp_driver.sc \
                          $SCRIP_DIR/smoke_interp.sc)
[ "$NATIVE" = "$HOSTED" ] && echo PASS || echo FAIL
```

Both byte-identical.  Must pass before any commit that advances SI-2 or beyond.
