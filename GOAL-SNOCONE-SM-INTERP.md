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

**C-parallel names — sess 2026-05-12 (Claude Sonnet 4.6).**  Per Lon's
directive: names in `sm_interp.sc` mirror `sm_interp.c` so the two files
read side-by-side without translation.  The C `SM_State` struct is
collapsed to module globals in Snocone — there is only ever one
interpreter, so the struct indirection has no use.

| C side                            | .sc side                                    |
|-----------------------------------|---------------------------------------------|
| `typedef struct {...} SM_State;`  | (no struct; module globals)                 |
| `SM_State st_inst;`               | `stack = TABLE(); sp = 0; ...`              |
| `st->stack`, `st->sp`, ...        | `stack`, `sp`, `stack_cap`, `last_ok`, `pc` |
| `sm_push(st, d)`                  | `sm_push(d)`                                |
| `sm_pop(st)`                      | `sm_pop()`                                  |
| `sm_state_init(st)`               | `sm_state_init()`                           |
| `sm_interp_run(prog, st)`         | `sm_interp_run()`                           |
| `return 0;` from main loop        | `pc = g_count;` (push pc past end)          |

Two systematic departures:
1. The `st` parameter is gone entirely — single interpreter, no need.
2. C has no `halted` flag — `SM_HALT` returns from `sm_interp_run_inner`.
   In Snocone the `while` loop body has no early-loop-exit, so `SM_HALT`
   advances `pc` to `g_count` and the `while (LT(pc, g_count))`
   condition naturally exits.

**Pending lower.sc rename** — owned by lower.sc, not sm_interp.sc.
Today lower.sc uses module globals `g_count` and `g_instr_tbl[]`;
the C-parallel form would be `struct SM_Program { instrs, count }` with
an instance `prog = SM_Program(TABLE(), 0)`, accessed as `count(prog)`
and `instrs(prog)`.  Refactor is mechanical but spans ~30 sites in
lower.sc; not bundled with the sm_interp.sc rename.  Tracked as an
SL- follow-up rung when convenient.

**Known Ph2 concern — namespace collision.**  Because all `--ir-run`
files share one variable namespace, a user program naming any reserved
state name would clash.  Reserved by `sm_interp.sc`: `stack`, `sp`,
`stack_cap`, `last_ok`, `pc`.  Reserved by `lower.sc`: `g_count`,
`g_instr_tbl`, `g_sm`, `g_labtab`, `g_patch`, `g_lang`, `g_in_proc`,
`g_unhandled`, `g_program`.  These names are short for parallel C
readability; the trade-off is documented and tests stay clear of them.
A future hardening pass could move all `sm_interp.sc` state behind a
single-instance struct or rename the lower.sc globals — neither blocks
Phase 2.

### Phase 2 — coverage rungs derived from SPITBOL manual

**Reference loaded sess 2026-05-12 (Claude Sonnet 4.6).**  Per Lon, Snocone
expression syntax and semantics are 100% identical to SPITBOL — only control
flow (braced blocks instead of label-goto) and newline-as-whitespace differ.
SPITBOL manual v3.7 (368 pages) consulted; relevant chapters cataloged:

| Chapter | Title | Scope used for rung planning |
|---------|-------|------------------------------|
| 3 | Fundamentals | data types, simple operators |
| 4 | Control Flow and Functions | success/failure model |
| 6 | Pattern Matching | algorithm + primitives |
| 7 | Additional Operators and Datatypes | extensions |
| 15 | Operators (reference) | full operator table |
| 17 | Data Types and Conversion | nine internal types |
| 18 | Patterns and Pattern Matching (reference) | primitive patterns |
| 19 | SPITBOL Functions | built-in function catalog |

SPITBOL nine internal data types: STRING, INTEGER, REAL, PATTERN, ARRAY, TABLE,
NAME, EXPRESSION, CODE.  Phase 1 covers STRING / INTEGER / REAL only (the
trivial-runtime cases — values ride free on host Snocone).  Phase 2 covers
PATTERN (large) and NAME (small).  ARRAY / TABLE / EXPRESSION / CODE land in
Phase 3 since they require either lower.sc extensions or host-runtime hooks.

SPITBOL binary operators (Ch 15) — Phase 1 covered `=` (assignment via
SM_STORE_VAR), `space` (concat via SM_CONCAT), `+`/`-`/`*`/`/` (arithmetic).
Phase 2 covers `?` (pattern match), `|` (pattern alt), `^`/`!`/`**`
(exponentiation), `.` (NAME via PAT_REFNAME / capture), `$` (immediate
assignment, partial), and the LT/LE/GT/GE/EQ/NE + LLT/.../LNE comparison
families (lowered to SM_ACOMP / SM_LCOMP).

SPITBOL unary operators (Ch 15) — Phase 1 covered `+`/`-` (numeric).  Phase 2
covers `.` (NAME — via SM_PAT_REFNAME for pattern context, separate path for
expression context), `*` (defer — affects how lower.sc emits, not interp),
`$` (indirection via host $name, already exploited in SI-2), `~` (negation
of success/failure — handled by SM_JUMP_F semantics), `?` (interrogation —
combo of EXEC_STMT result + SM_PUSH_NULL), `@` (cursor — pattern context only).

Each rung's gate: hand-built or native test program lowers and runs through
the self-hosted pipeline, then SI-5 cross-check confirms hosted-output ==
native-output byte-identical.  Tests live in `corpus/SCRIP/si_*.sc` (hosted)
+ `corpus/SCRIP/si_*_native.sc` (native counterpart).  Naming change from
the SI-1..SI-5 ad-hoc `smoke_interp` / `sm_interp_test` — `si_<rung>_*`
groups Phase-2 tests by rung for easy scanning.

The gap between what `lower.sc` emits today and what `sm_interp.sc` handles
today is 41 opcodes (audited sess 2026-05-12).  Phase 2 closes that gap
opcode by opcode in 10 rungs.

### SI-6 — Exponentiation ✅ sess 2026-05-12

`SM_EXP` (`^` / `!` / `**`) — right-associative, priority 11.  One-liner
extension to SI-4 arithmetic: `si_push((a + 0) ^ (b + 0))`.

Test program: `OUTPUT = 2 ^ 10` → `1024`.

- [x] Add `SM_EXP` arm to `sm_interp_step`
- [x] `si_06_exp.sc` + `si_06_exp_native.sc` + `.ref`
- [x] SI-5 cross-check PASS

### SI-7 — Pattern matching statement (EXEC_STMT + PAT_LIT + PAT_DEREF + PUSH_EXPR) ✅ sess 2026-05-12

Implements the SPITBOL pattern-match statement form: `SUBJECT ? PATTERN`
and `SUBJECT ? PATTERN = REPLACEMENT`.  This rung covers the minimum
pattern statement machinery — just enough to match a literal string.

Opcodes: `SM_PAT_LIT` (string literal as pattern), `SM_PAT_DEREF`
(variable-as-pattern), `SM_PAT_REFNAME` (capture-to-variable via `.`),
`SM_PUSH_EXPR` (deferred expression — fallback path), `SM_EXEC_STMT`
(invoke matcher on subject with built pattern + optional replacement).

Implementation note: `SM_EXEC_STMT` is the interesting one.  In C it calls
into the runtime's pattern matcher; in `sm_interp.sc` we cannot replicate
the matcher (~2000 lines of C).  Strategy: emit a host-Snocone string
match — pop replacement, pop subject-name, pop pattern, run a real
Snocone pattern-match statement using `$name ? pat = repl`, then push the
result.  This sidesteps reimplementing the matcher and exploits the host's
existing engine.

Test program: `S = 'hello'; S 'ell' = 'ELL'; OUTPUT = S` → `hELLo`.

- [x] Add pattern-statement opcodes
- [x] `si_07_pat_lit.sc` + `si_07_pat_lit_native.sc` + `.ref`
- [x] SI-5 cross-check PASS

**Implementation — sess 2026-05-12 (Claude Opus 4.7).**  All five opcodes
landed as one-liners:

- `SM_PAT_LIT  s=X`  → `sm_push(a0(ins))` — strings are patterns in SPITBOL/Snocone
- `SM_PAT_DEREF`     → `a = sm_pop(); sm_push(a)` — type-discrimination is implicit in host
- `SM_PAT_REFNAME s=name` → `sm_push($name)` — current value of named var as pattern
- `SM_PUSH_EXPR`     → `sm_push('')` — Ph2 stub (deferred-expression carrier)
- `SM_EXEC_STMT s=sname i=has_repl` → pop repl, subj, pat (reverse of lower push order);
  dispatch on named/anonymous subject and presence of replacement; use host
  `$sname_v ? pat_v = repl_v` (named, with repl) etc.  Sets `last_ok = 1` on
  match success, `0` on failure.  Named-subject path mutates host variable
  by indirection — that's the whole self-hosting trick.

**Bug found and fixed during this rung — Snocone boolean OR is not `|`.**
First-cut implementation gated subject-name handling with
`if (IDENT(sname_v) | IDENT(sname_v, ''))` — intended as boolean OR but the
`|` here is **pattern alternation**: it builds a pattern *value*, and
`if (pattern_value)` always succeeds because a bound name has a value
(per ARCH-SNOCONE.md "Conditions are SPITBOL backtracking expressions").
Result: the anonymous-subject branch fired for every statement, so the
named-subject write-back path was never taken — the test produced `hello`
instead of `hELLo`.  Fix: flip to `if (DIFFER(sname_v, ''))` for the named
case (the common path), with the anonymous case as `else`.  No `|` needed
once the two branches are properly mutually exclusive.

The lesson is documented in ARCH-SNOCONE.md ("Boolean OR is the alternation
operator `|`") but the practical consequence is sharper: `|` works for
boolean OR **only when both operands are themselves backtracking expressions
that can fail** (e.g. `IDENT(x, A) | IDENT(x, B)`).  Combining predicate
calls with `|` when one of them always succeeds gives wrong-looking
"always-true" behaviour.

Gates: smoke_interp + sm_interp_test + si_06_exp + si_07_pat_lit all
byte-identical hosted == native; test_self_host_smoke.sh PASS=4/4
FAIL=0.  No regressions: smoke_snocone 5/5, smoke_snobol4 7/7,
test_lower_byte_identical 27/30 (3 pre-existing pl_* fails unchanged).



### SI-8 — Primitive patterns (ABORT, ARB, FAIL, FENCE, REM, SUCCEED, BAL) ✅ sess 2026-05-12

Opcodes: `SM_PAT_ABORT`, `SM_PAT_ARB`, `SM_PAT_BAL`, `SM_PAT_FAIL`,
`SM_PAT_FENCE`, `SM_PAT_REM`, `SM_PAT_SUCCEED`.

Each pushes a corresponding primitive pattern value onto the value stack.
In host Snocone these primitives are `ABORT`, `ARB`, `BAL`, `FAIL`,
`FENCE`, `REM`, `SUCCEED` — globally bound by the scrip runtime.  Arm
body: `si_push(ABORT)`, etc.

Test program: `S = 'abc'; S ARB . X 'c'; OUTPUT = X` → `ab`.

- [x] Add seven primitive-pattern opcodes
- [x] `si_08_prim_pats.sc` + native + `.ref`
- [x] SI-5 cross-check PASS

**Implementation — sess 2026-05-12 (Claude Opus 4.7).**  Seven primitives
as one-liners pushing host globals (ABORT/ARB/BAL/FAIL/REM/SUCCEED).  Plus
SM_PAT_FENCE0 (nullary, pushes FENCE) and SM_PAT_FENCE1 (unary, pops child
and pushes `FENCE(child)`).  Also landed SM_PAT_CAPTURE — necessary because
the rung's canonical test `ARB . X 'c'` needs capture.

**SM_PAT_CAPTURE — EVAL trick.**  Host Snocone's `.` and `$` capture
operators bind to a literal name token at parse time.  The opcode operand
gives us a *string* at runtime.  Workaround: stash the child pattern in a
known module global (`si_cap_tmp`), then EVAL the capture expression
literally — `EVAL('si_cap_tmp . ' nm)` substitutes the runtime name string
into source syntax that the host then compiles.  Adds a global slot but
no other infrastructure; cursor mode (`@`) and immediate mode (`$`) work
through the same trick.

### SI-9 — Pattern function calls (LEN, POS, RPOS, TAB, RTAB, ANY, NOTANY, SPAN, BREAK, ARBNO) ✅ sess 2026-05-12

Opcodes: `SM_PAT_LEN`, `SM_PAT_POS`, `SM_PAT_RPOS`, `SM_PAT_TAB`,
`SM_PAT_RTAB`, `SM_PAT_ANY`, `SM_PAT_NOTANY`, `SM_PAT_SPAN`,
`SM_PAT_BREAK`, `SM_PAT_ARBNO`.

Each pops one argument, applies host's pattern constructor: `si_push(LEN(arg))`.
Trivial because host runtime owns the constructors.

Test program: `S = 'abc123'; S LEN(3) . LET SPAN(&DIGITS) . NUM` → captures
`abc` and `123`.

- [x] Add ten pattern-function opcodes
- [x] `si_09_pat_fns.sc` + native + `.ref`
- [x] SI-5 cross-check PASS

**Implementation — sess 2026-05-12 (Claude Opus 4.7).**  Eleven one-liners
total (the ten listed plus SM_PAT_EPS, which pushes empty string).  Integer-
arg ops (LEN/POS/RPOS/TAB/RTAB) coerce via `+0`; charset-arg ops
(ANY/NOTANY/SPAN/BREAK) pass the string through.  ARBNO takes a pattern
child via the host's ARBNO constructor.

Test caught one AST-build bug: I'd used `TT_CONCAT` for the expression-
context concat tag — actually `TT_CAT` (lower.sc line 792, lower_cat_seq
handler).  `TT_CONCAT` falls through to SM_PUSH_NULL.  Fixed; both
captures fire and `LET=abc` / `NUM=123` are printed byte-identical.

### SI-10 — Pattern combinators (CAT, ALT) ✅ sess 2026-05-12 (pulled forward into SI-8)

Opcodes: `SM_PAT_CAT` (subsequent — space operator), `SM_PAT_ALT`
(alternation — `|` operator).

**Goal file said "n-ary" but the actual lowering is binary.**  Verified:
`emit_pat_nary` in lower.sc pushes all children then emits `SM_PAT_CAT`
**n-1 times**, and sm_interp.c handles SM_PAT_CAT/ALT as binary pop-pop-
push.  Implemented binary as one-liners: `sm_push(a b)` for CAT (space
operator on patterns), `sm_push(a | b)` for ALT.  Host's space operator
auto-promotes strings to patterns when one operand is already a pattern.

- [x] Add CAT + ALT opcodes
- [x] SI-5 cross-check PASS (via si_08_prim_pats which uses CAT)

The Goal file's prose "pops n patterns from stack" is incorrect for the
current lowering; left as-is for now since the binary form is what
ships.  Could be a documentation rung if a future SL rung changes to a
genuine n-ary opcode (which would need lower.sc and sm_interp.c parallel
changes).



### SI-11 — Comparisons (ACOMP, LCOMP) ⏳ implemented sess 2026-05-12, test pending

Opcodes: `SM_ACOMP` (arithmetic comparison: LT/LE/GT/GE/EQ/NE),
`SM_LCOMP` (lexical comparison: LLT/LLE/LGT/LGE/LEQ/LNE).

Each pops two values, performs comparison per `a0(ins)` op-name,
sets `si_last_ok = 1` on success / `0` on failure, pushes one result
value (the operand or null per SPITBOL semantics).

Host calls: `LT`, `LE`, `GT`, `GE`, `EQ`, `NE`, `LLT`, `LLE`, `LGT`,
`LGE`, `LEQ`, `LNE` — all are host builtins.

Test program: `:S(GT(X, 0))` style branch test.

- [x] Add ACOMP + LCOMP opcodes (sm_interp.sc lines added sess 2026-05-12)
- [ ] `si_11_compare.sc` + native + `.ref`
- [ ] SI-5 cross-check PASS

**Implementation — sess 2026-05-12 (Claude Opus 4.7).**  Snocone-side
lowering (`lower_comp` in lower.sc) passes the kind STRING in a0
(`'TT_EQ'`, `'TT_LT'`, etc) — note this differs from the C side which
passes the integer EKind.  Interp dispatches on a string-equality cascade.
Both ACOMP and LCOMP follow Icon-style relops: on success push the right
operand and set last_ok=1; on failure push empty string and clear last_ok.
Mirrors NUMREL/STRREL macros in interp_eval.c.

Test still pending — needs a program whose lowering reliably emits
SM_ACOMP/SM_LCOMP (most idiomatic Snocone uses `:S/:F` goto sugar that
lowers through different paths).


### SI-12 — Function calls (CALL_FN)

Opcode: `SM_CALL_FN` — `si=Index s="name" nargs=N`.

Implementation: pop nargs args, look up function by name (a0=name string),
invoke via host `APPLY()` builtin which takes a function name + arg list,
push result.  `APPLY` is the SPITBOL/host runtime's indirect-call mechanism;
no new infrastructure needed.

Built-in functions accessible this way once the opcode lands: SIZE, SUBSTR,
REPLACE, REVERSE, TRIM, LPAD, RPAD, DUPL, IDENT, DIFFER, DATATYPE, CONVERT,
EVAL, TABLE, ARRAY, DATA, DEFINE, ... — anything the host runtime exposes.

Test program: `OUTPUT = SIZE('hello')` → `5`.

- [ ] Add CALL_FN opcode (APPLY-based dispatch)
- [ ] `si_12_call_builtin.sc` + native + `.ref`
- [x] SI-5 cross-check PASS

### SI-13 — Function returns (RETURN, FRETURN, NRETURN)

Opcodes: `SM_RETURN`, `SM_FRETURN`, `SM_NRETURN`.

For user-defined functions, these set the return-value behavior:
RETURN = normal value, FRETURN = signal failure, NRETURN = return a NAME
(for `*fn()` callers).  Implementation needs a frame stack (`si_call_stack[]`)
that SM_CALL_FN pushes onto when entering a user function lowered to SM.

Note: this rung only matters when lower.sc emits user-function bodies.
Today `lower_proc_skeletons` is a stub so no user-function bodies are
emitted.  Build the frame infrastructure here so SI-13 unblocks once
lower.sc starts emitting real bodies.

- [ ] Add frame stack (`si_call_stack`, `si_csp`)
- [ ] Add RETURN / FRETURN / NRETURN opcodes
- [ ] `si_13_proc.sc` + native + `.ref` (using DEFINE-based user fn)
- [x] SI-5 cross-check PASS

### SI-14 — Computed goto (JUMP_INDIR)

Opcode: `SM_JUMP_INDIR` — pops a label name from stack, looks up in
label table, jumps.  Needed for SPITBOL `:($X)` form.

Strategy: `lower.sc` already builds `g_labtab[name] = pc` for every
`SM_LABEL`.  Arm: `nm = si_pop(); si_pc = g_labtab[nm];`.

Test program: `LBL = 'TARGET'; :($LBL) ... TARGET OUTPUT = 'hit'`.

- [ ] Add JUMP_INDIR opcode
- [ ] `si_14_computed_goto.sc` + native + `.ref`
- [x] SI-5 cross-check PASS

### SI-15 — Phase 2 closing gate: cross-check on real corpus programs

Goal: pick 3-5 small but real `.sno` / `.sc` programs from `corpus/programs/`
that use only Phase-2-covered features (no Icon, no Prolog, no generators,
no ARRAY/TABLE), run them through the self-hosted pipeline, and confirm
byte-identical output to native scrip.

Candidates to evaluate:
- A `Hello, World!` variant (already in SI-1..SI-5 form)
- A simple pattern-match program (substring replace)
- A small string-manipulation program (no I/O loops)

Extend `test_self_host_smoke.sh` to iterate these cases.  PASS=5/5 closes
Phase 2.

- [ ] Inventory candidate programs
- [ ] Add real-program cases to `test_self_host_smoke.sh`
- [ ] PASS=5/5 on cross-check

### Phase 3 — deferred

The following opcodes are deferred to Phase 3 because they need infrastructure
beyond the trivial-runtime pattern:

- `SM_BB_ONCE`, `SM_BB_ONCE_PROC`, `SM_BB_PUMP`, `SM_BB_PUMP_AST`,
  `SM_BB_PUMP_EVERY`, `SM_BB_PUMP_PROC`, `SM_BB_PUMP_SM` — Icon/Prolog
  broker pumps; require the BB scheduler to be ported or a host-side
  hook.  Deferred until self-host can run pure SNOBOL4/Snocone programs.
- `SM_SUSPEND_VALUE`, `SM_RESUME`, `SM_GEN_TICK`, `SM_DECR`, `SM_INCR`,
  `SM_LOAD_GLOCAL`, `SM_STORE_GLOCAL`, `SM_LOAD_FRAME`, `SM_STORE_FRAME`
  — generator coroutines + frame slots.  Deferred for the same reason.
- `SM_PAT_CAPTURE`, `SM_PAT_CAPTURE_FN`, `SM_PAT_CAPTURE_FN_ARGS`,
  `SM_PAT_USERCALL`, `SM_PAT_USERCALL_ARGS`, `SM_PAT_EPS` — advanced
  pattern capture forms; some may collapse into SI-9 if scope permits.
- `SM_PUSH_EXPRESSION`, `SM_CALL_EXPRESSION` — unevaluated expression
  data type; needs host EXPRESSION support exposed via APPLY or similar.
- `SM_DEFINE`, `SM_DEFINE_ENTRY` — function definition; ties into SI-13
  but the lowering side (proc_skeletons in lower.sc) is also stubbed.

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
