# GOAL-LANG-SNOCONE.md — Snocone Frontend Ladder

**Repo:** one4all
**Done when:** All 14 beauty-sc subsystems PASS under all three modes
(--ir-run, --sm-run, --jit-run). Control-flow lowering complete.
Pattern match `subject ? pattern` wired through BB_SCAN.

**Cross-pollination:** Snocone lowers to the same IR as SNOBOL4. Every
interp.c fix for SNOBOL4 (E_IF, E_WHILE, E_SEQ_EXPR) also fixes Snocone.
Pattern match shares bb_boxes.c with SNOBOL4. Write tests by eye from
working SNOBOL4 programs — the semantics are identical.
Share fixes via main — no branches.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_snocone.sh           # PASS=5
bash /home/claude/one4all/scripts/test_beauty_snocone_subsystems.sh
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh    # PASS=31
bash /home/claude/one4all/scripts/test_crosscheck_snocone.sh       # 3-mode divergence check
```

---

## Architecture reminder

```
.sc → snocone_compile() → Program* [LANG_SNO]
    (Snocone lowers to LANG_SNO — same IR as SNOBOL4)
    --ir-run  → execute_program() → interp_eval()
    --sm-run  → sm_lower() → SM_Program → sm_interp_run()
    --jit-run → sm_lower() → SM_Program → sm_codegen() → sm_jit_run()

Pattern match: subject ? pattern → STMT_t with subject+pattern fields
    → bb_broker(BB_SCAN) — identical path to SNOBOL4
```

## How to write Snocone tests from SNOBOL4 by eye

Snocone is C-syntax SNOBOL4. Translation table:

| SNOBOL4 | Snocone |
|---------|---------|
| `X = "hello"` | `x = "hello";` (at top level) or inside `procedure` |
| `OUTPUT = X` | `OUTPUT = x;` |
| `X Y :S(L)` | `if (x ? y) { goto L; }` |
| `X 'pat' = 'repl'` | `x ?= pat <- repl;` |
| `DEFINE('F(A,B)')` | `procedure F(a, b) { ... }` |
| `:S(L) :F(M)` | `if (...) { goto L; } else { goto M; }` |
| `IDENT(A,B)` | `IDENT(a, b)` (same builtin name) |
| `INTEGER(X)` | `INTEGER(x)` |
| `DIFFER(A,B)` | `DIFFER(a, b)` |

Write .sc tests in `test/snocone/` with matching .ref files.
Oracle for .ref: run the equivalent .sno under SPITBOL.

---

## Rung ladder — all modes, x86

Current baseline: 3/14 beauty-sc subsystems PASS (assign, fence, global).
Root cause of failures: control-flow lowering missing in snocone_lower.c.

### Phase 1 — IR-run: fix control flow lowering

- [x] **SC-1** — assign, fence, global: 3/14 PASS. (done)

- [x] **SC-2** — Fix procedure lowering in snocone_lower.c.
  `procedure F(args) { body }` must emit: DEFINE stmt + labeled body + RETURN.
  Write `test/snocone/test_proc.sc` by translating a simple SNOBOL4 function.
  Gate: test_proc.sc PASS under --ir-run.
  NOTE: Actual fix was break lowering in snocone_cf.c (break_stack). 8→11/14.

- [x] **SC-3** — Fix `if/else` lowering.
  `if (cond) { then } else { else }` → E_IF in IR (already in interp_eval).
  Write `test/snocone/test_if.sc`.
  Gate: PASS under --ir-run.

- [x] **SC-4** — Fix `while` loop lowering.
  `while (cond) { body }` → E_WHILE.
  Write `test/snocone/test_while.sc`.
  Gate: PASS under --ir-run. Commit: f881e97a

- [x] **SC-5** — Fix `for` loop lowering.
  `for (init; cond; step) { body }` → emit init + E_WHILE with step.
  Write `test/snocone/test_for.sc`.
  Gate: PASS under --ir-run. Commit: 4402e308

- [x] **SC-6** — Fix `break`/`return`/`freturn`/`nreturn` lowering.
  Maps to E_LOOP_BREAK, SM_RETURN, SM_FRETURN, SM_NRETURN.
  Gate: test_break_return.sc PASS. Commit: 8ed3d7a0
  Note: tests use while-loop wrappers; pre-existing IR bug causes consecutive
  top-level OUTPUT statements to emit only the last value (orthogonal to SC-6).

- [ ] **SC-7** — beauty-sc arith subsystem: PASS.
  Root cause: procedure + if + while. SC-2 through SC-6 should fix it.
  Gate: test_beauty_snocone_subsystems.sh arith PASS.

- [ ] **SC-8** — beauty-sc strings, stack, trace, counter: PASS.
  Same root causes. Gate: all four PASS.

- [ ] **SC-9** — Fix pattern match `subject ? pattern` lowering.
  `expr ? pat` → STMT_t with subject=expr, pattern=pat → BB_SCAN.
  Write `test/snocone/test_pattern.sc` translating SNOBOL4 pattern tests.
  Gate: test_pattern.sc PASS.

- [ ] **SC-10** — beauty-sc match, roman, semantic, ShiftReduce, ReadWrite: PASS.
  Root cause: pattern match + control flow. SC-9 plus SC-7/SC-8 should fix.
  Gate: all five PASS.

- [ ] **SC-11** — beauty-sc beauty subsystem (self-beautify): PASS.
  The beauty.sc subsystem runs the Snocone beautifier on itself.
  Gate: diff vs SPITBOL (running beauty.sno) is empty.

- [ ] **SC-12** — All 14 beauty-sc subsystems: 14/14 PASS --ir-run.
  Gate: test_beauty_snocone_subsystems.sh PASS=14.

### Phase 2 — Hand-crafted test suite (written by eye from SNOBOL4)

Write the following .sc tests in `test/snocone/`. Each is a Snocone
translation of a known-working SNOBOL4 program. .ref files come from
running the SNOBOL4 version under SPITBOL.

- [ ] **SC-13** — `test/snocone/fibonacci.sc` — recursive Fibonacci.
  Translate from corpus/programs/snobol4/demo/fibonacci.sno.
  Gate: output matches SPITBOL ref.

- [ ] **SC-14** — `test/snocone/palindrome.sc` — string reverse + compare.
  Gate: output matches ref.

- [ ] **SC-15** — `test/snocone/wordcount.sc` — pattern match, split, table.
  Gate: output matches ref.

- [ ] **SC-16** — `test/snocone/quicksort.sc` — recursive sort via procedure.
  Gate: output matches ref.

- [ ] **SC-17** — `test/snocone/pattern_suite.sc` — ARB, SPAN, BREAK, ANY, LEN.
  Exercises all pattern primitives via `subject ? pattern` syntax.
  Gate: output matches ref.

- [ ] **SC-18** — Write `scripts/test_snocone_hand_suite.sh`.
  Runs SC-13 through SC-17. Gate: PASS=5.

### Phase 3 — SM-run (x86)

- [ ] **SC-19** — All 14 beauty-sc subsystems under --sm-run.
  Gate: 14/14 PASS.

- [ ] **SC-20** — Hand suite under --sm-run.
  Gate: PASS=5.

### Phase 4 — JIT-run (x86 in-memory)

- [ ] **SC-21** — All 14 beauty-sc subsystems under --jit-run.
  Gate: 14/14 PASS.

- [ ] **SC-22** — Hand suite under --jit-run.
  Gate: PASS=5.

---

## Key files

| File | Role |
|------|------|
| `src/frontend/snocone/snocone_lower.c` | IR lowering — main work here |
| `src/frontend/snocone/snocone_parse.c` | Parser |
| `src/frontend/snocone/snocone_lex.c` | Lexer |
| `test/beauty-sc/` | 14 beauty-sc subsystem tests |
| `test/snocone/` | Hand-crafted test files (create here) |
| `scripts/test_beauty_snocone_subsystems.sh` | Beauty subsystem gate |

---

## Invariants

- Gate = PASS=31 FAIL=0 on test_smoke_unified_broker.sh after every commit.
- .ref files come from SPITBOL (running equivalent .sno). Never fabricate refs.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

---

## Current state (2026-04-15, one4all HEAD 8ed3d7a0)

SC-1 done: 3/14 PASS (assign, fence, global). [prior session]
SC-2 done: break lowering fixed in snocone_cf.c — 8→11/14 PASS. Commit: afe90855
SC-3 done: **14/14 PASS** (beauty SKIP expected, no driver.sc). Commit: b1e0c7a4
SC-4 done: while loop lowering — test_while.sc PASS. Commit: f881e97a
SC-5 done: for loop lowering — test_for.sc PASS. Commit: 4402e308
SC-6 done: break/return/freturn/nreturn — test_break_return.sc PASS. Commit: 8ed3d7a0

### Two fixes in SC-3:

**KW-RETFIX (interp.c):** User procedure named same as a SNOBOL4 keyword
  (e.g. "Trim" / &TRIM) caused NV_SET_fn in body to write keyword slot
  (integer), then NV_GET_fn on RETURN read back 0.
  Fix: added retval_cell/retval_set to CallFrame; set_and_trace captures
  body assignments matching fr->fname into frame cell; all RETURN/NRETURN
  readback sites use fr->retval_cell when retval_set=1.

**FENCE / E_ALT (snocone_lower.c):** SNOCONE_PIPE (|) was emitting E_CAT
  instead of E_ALT. In Snocone, | is always pattern alternation; || and &&
  are concat. Fixed to emit n-ary E_ALT. Also fixed SNOCONE_CONCAT (&&) to
  emit E_SEQ (matching SNOBOL4 juxtaposition) — lower level handles
  value-context string concat from E_SEQ correctly.

### Baseline after SC-3
  PASS: assign, fence, global, arith, ReadWrite, stack, trace, counter,
        match, roman, semantic, ShiftReduce, tree, strings  (14/14)
  SKIP: beauty (no driver.sc)

### Next: SC-7 — beauty-sc arith subsystem PASS

BLOCKER before SC-7: pre-existing IR bug — consecutive top-level `OUTPUT = ...`
statements under --ir-run emit only the last value. Root likely in IR STMT_ASSIGN
handling for the OUTPUT special variable. Must fix or work around before SC-7.

### Session 2026-04-15 completed: SC-4, SC-5, SC-6

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

**Note:** `--monitor` is incompatible with `--ir-run`/`--sm-run`/`--jit-run`
(it drives all three internally). ICN frame locals (IM-10) and Prolog trail
variables (IM-11) are not yet in the snapshot — coming in future IM steps.

