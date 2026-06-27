# GOAL-SNOCONE-SM — Self-host SCRIP via Snocone (lower.sc + sm_interp.sc)

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
║  Mode 1 (`--run` standalone AST interp) is unchanged and remains the reference path.        ║
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

The M2 path of SCRIP self-hosting: reimplement the SM_Program compile+execute
pipeline in Snocone so the same interpreter that runs `.sc` programs can also
lower an AST to SM and execute it.  Two halves of one goal — formerly tracked
as separate files `GOAL-SNOCONE-SM-LOWER.md` and `GOAL-SNOCONE-SM-INTERP.md`,
merged here sess 2026-05-12 (Claude Sonnet 4.6) since they share corpus,
gates, setup, and gotchas.

- **`lower.sc`** — port of `src/runtime/x86/lower.c`.  Takes the shared AST
  (TT_-tagged tree-of-trees produced by any frontend) and emits an
  `SM_Program`: flat array of `sm_instr` records.
- **`sm_interp.sc`** — port of `src/runtime/x86/sm_interp.c`.  Walks the
  `sm_instr` array and dispatches each of the 87 SM_* opcodes from
  `sm_prog.h`.

When SL-13d closes (parser_snobol4.sc driver populating Lower_collect with
the parsed tree), the full pipeline
`scrip --run tree.sc + lower.sc + parser_snobol4.sc + sm_interp.sc + <prog>.sno`
becomes self-hosting.  Until then, tests hand-build the AST that a real
parser would emit, and we cross-check byte-identical against the native C
pipeline running the same logical program.

---

## Architecture

- Every frontend (parser_snobol4, parser_snocone, parser_icon, parser_raku,
  parser_prolog, parser_rebus) emits the **shared AST**: a tree-of-trees
  with TT_-prefixed node tags and `:`-prefixed slot tags.
- The shared AST flows through `lower(g_program)` → `g_instr_tbl` (the
  SM_Program), then through `sm_interp_run()` → host I/O.
- AST shape: `Tree('STMT', '', n_children, slot1, slot2, ...)` where each
  slot is `tree(':lbl' | ':eq' | ':subj' | ':pat' | ':repl' | ':go' | ':goS' | ':goF' | ':end' | ':stno' | ':line', value [, children])`.
- Expression nodes inside slots: `TT_VAR`, `TT_QLIT`, `TT_ILIT`, `TT_FLIT`,
  `TT_FNC`, `TT_DEFER`, `TT_ADD`, `TT_SUB`, `TT_MUL`, `TT_DIV`, `TT_POW`,
  `TT_LT`, `TT_GT`, `TT_EQ`, `TT_SEQ`, `TT_ALT`, `TT_SCAN`, etc.
- All five run modes of scrip can execute the lowered SM_Program: `--run`
  (tree-walk reference), `--run` (C SM dispatch loop, default),
  `--run` (SM→x86 bytes), `--monitor` (in-process comparator).
  Our `.sc` interpreter `sm_interp.sc` runs inside `--run` of a scrip
  invocation that concatenates `tree.sc + lower.sc + sm_interp.sc + <test>.sc`.

---

## Session setup

```bash
cd /home/claude
git clone https://github.com/snobol4ever/corpus
git clone https://github.com/snobol4ever/SCRIP
git clone https://github.com/snobol4ever/.github

apt-get install -y libgc-dev      # required for scrip build
make -C SCRIP/src/runtime/x86 -j scrip
```

Working files:
- `corpus/SCRIP/tree.sc` — AST helpers (Tree, tree, t, v, c, n, Append, etc.)
- `corpus/SCRIP/lower.sc` — the lowering pass (lower(prog), lower_stmt(s), emit_*, labtab_*)
- `corpus/SCRIP/lower_driver.sc` — Lower_collect(stmt), Lower_run, Lower_dump_ast
- `corpus/SCRIP/sm_interp.sc` — the SM_Program executor (sm_interp_step, sm_interp_run)
- `corpus/SCRIP/parser_snobol4.sc` — SNOBOL4 frontend (SL-13d feeds Lower_collect from this)

---

## Run a self-host test

```bash
SCRIP=/home/claude/SCRIP/scrip
SCRIP_DIR=/home/claude/corpus/SCRIP
$SCRIP --run \
  $SCRIP_DIR/tree.sc $SCRIP_DIR/lower.sc $SCRIP_DIR/lower_driver.sc \
  $SCRIP_DIR/sm_interp.sc $SCRIP_DIR/<test>.sc
```

scrip concatenates the `.sc` files into one Snocone program.  Each test's
`Lower_collect(...)` hand-builds the AST that a real parser would emit,
then `lower(g_program)` + `sm_interp_run()` runs at the bottom.

---

## Snocone gotchas (real bugs we hit)

1. **`~LT(x, 0)` is not boolean negation.**  `~` is **pattern alternation**
   that builds a PATTERN value (always truthy in `if`).  Use `GE(...)`.
   Caught by SL-13c-tilde-fix.
2. **`|` is pattern alternation, not boolean OR.**  Mixing predicates
   that always succeed with `IDENT(...) | IDENT(...)` breaks.
3. **`$name ? pat = repl` doesn't write back to `name`.**  Dollar-indirection
   produces an rvalue.  Use local copy + write-back.  Caught by si_07_pat_lit
   investigation.
4. **APPLY returns `''` on builtin failure.**  Detect failure via
   `if (r = APPLY(...))`, not by inspecting the return value.  Caught by SI-17b.
5. **`+x` truncates to INTEGER.**  Use `x + 0.0` when REAL is needed.
6. **SNOBOL4 needs TAB indentation, Snocone is case-sensitive.**  Lowercase
   `output` doesn't bind to host stdout in Snocone — use uppercase `OUTPUT`.
7. **Snocone `switch` compiles to linear IDENT chain, not O(1) jump.**  Future
   rung tracked to fix this via `$('case_'opc)` indirect-goto per `beauty.sno`.
8. **TT_POW (not TT_EXP) is the lower.sc tag for exponentiation.**  Caught by SI-15b.
9. **Canonical STMT tag is `'STMT'`, not `'TT_STMT'`.**  parser_snobol4.sc
   and parser_snocone.sc both emit `Tree('STMT', '', ...)`.  Slot lookups in
   lower_stmt are tag-agnostic so `'TT_STMT'` worked, but `'STMT'` is the form
   a real parser hands us.  Caught by Lon during sess 2026-05-12 handoff #2.

---

## Status — completed rungs (one-liners; pull from git history if you need detail)

### SM-LOWER ladder

| # | Rung | Summary | Session |
|---|------|---------|---------|
| SL-0  | folder + skeleton                         | `corpus/SCRIP/` created with tree.sc, lower.sc, lower_driver.sc | 2026-05-11 |
| SL-1  | LabelTable                                | `g_labtab`, `labtab_define`, `labtab_find`, forward-patch list  | 2026-05-11 |
| SL-2  | emit_goto                                 | `:S(L)` / `:F(L)` / `:(L)` lower to `SM_JUMP_S`/`_F`/`SM_JUMP`   | 2026-05-12 |
| SL-3  | lower_expr literals + variables           | TT_QLIT, TT_ILIT, TT_FLIT, TT_VAR → PUSH_LIT_S/I/F, PUSH_VAR    | 2026-05-12 |
| SL-4  | lower_expr arithmetic + call + unary      | TT_ADD/SUB/MUL/DIV, TT_FNC, TT_NEG, partial concat              | 2026-05-12 |
| SL-5  | lower_expr control + comparison           | TT_LT/GT/EQ/LE/GE/NE, TT_IF/THEN/ELSE                            | 2026-05-12 |
| SL-6  | lower_expr Icon/Prolog stubs              | TT_FOR/TO/BY/WHILE stubs — emit SM_BB_PUMP placeholder           | 2026-05-12 |
| SL-7  | lower_stmt full port                      | All slot kinds: SL_LBL, SL_EQ, SL_SUBJ, SL_PAT, SL_REPL, SL_GO*  | 2026-05-12 |
| SL-8  | sm_lower main entry                       | `lower(prog)` walks g_program, dispatches per-stmt               | 2026-05-12 |
| SL-9  | test driver + .ref baked                  | `smoke_lower.sc` / `sm_lower_test.sc` byte-identical to native   | 2026-05-12 |
| SL-10 | lower_pat_expr (Phase 2)                  | Pattern expression lowering: PAT_LIT, PAT_ANY, PAT_SPAN, etc.    | 2026-05-12 |
| SL-11 | emit_thunk + lower_defer                  | TT_DEFER → SM_PUSH_EXPRESSION; thunks emit at end of program     | 2026-05-12 |
| SL-12 | EVAL(*expr) in lower_fnc                  | `EVAL(*X)` lowers to SM_CALL_EXPRESSION                         | 2026-05-12 |
| SL-13a | sc_split_subject_pattern fix              | `subject ? pat = repl` in cond context now properly splits      | 2026-05-12 |
| SL-13b | pattern captures `. var` / `$ var` fix    | --run TT_CAPT_COND_ASGN/IMMED_ASGN handle plain TT_VAR        | 2026-05-12 |
| SL-13c | deferred `*Fn(args)` captures fix         | eval_code.c + bb_flat.c: TT_DEFER(TT_FNC) capture path           | 2026-05-12 |
| SL-13c-tilde | `~` is pattern, not boolean negation | `lower.sc` forward-patch sites use `GE(...)` instead              | 2026-05-12 |

### SM-INTERP ladder

| # | Rung | Summary | Session |
|---|------|---------|---------|
| SI-1  | skeleton + dispatch loop                  | sm_interp_step/run; switch(opc) dispatch; state vars             | 2026-05-12 |
| SI-2  | STNO + literals + VOID_POP                | SM_STNO, PUSH_LIT_S/I/F, STORE_VAR, PUSH_VAR, VOID_POP           | 2026-05-12 |
| SI-3  | jumps                                     | SM_JUMP / JUMP_S / JUMP_F + SM_LABEL no-op + SM_HALT             | 2026-05-12 |
| SI-4  | arithmetic + COERCE + CONCAT              | SM_ADD/SUB/MUL/DIV, SM_COERCE_NUM, SM_CONCAT, SM_NEG, SM_MOD     | 2026-05-12 |
| SI-5  | cross-check gate                          | Closes Phase 1: smoke_interp.sc + sm_interp_test.sc baked .ref   | 2026-05-12 |
| SI-6  | exponentiation                            | SM_EXP (TT_POW)                                                  | 2026-05-12 |
| SI-7  | pattern match statement                   | SM_EXEC_STMT + SM_PAT_LIT + SM_PUSH_EXPR + SM_PAT_DEREF          | 2026-05-12 |
| SI-8  | primitive patterns                        | PAT_ABORT/ARB/FAIL/FENCE0/FENCE1/REM/SUCCEED/BAL/EPS + CAT+ALT   | 2026-05-12 |
| SI-9  | pattern function calls                    | PAT_LEN/POS/RPOS/TAB/RTAB/ANY/NOTANY/SPAN/BREAK/ARBNO            | 2026-05-12 |
| SI-10 | pattern combinators                       | (folded into SI-8: SM_PAT_CAT, SM_PAT_ALT)                       | 2026-05-12 |
| SI-11 | comparisons                               | SM_ACOMP, SM_LCOMP — and surfaced SL-13c-tilde-fix               | 2026-05-12 |
| SI-12 | function calls via APPLY                  | SM_CALL_FN; arity dispatch 0..5; switch + 120-char + +X coercion | 2026-05-12 |
| SI-13 | function returns + frame stack            | SM_CALL_EXPRESSION + SM_RETURN / FRETURN / NRETURN + frames      | 2026-05-12 |
| SI-14 | computed goto                             | SM_JUMP_INDIR (one-liner via g_labtab)                           | 2026-05-12 |
| SI-15 | Phase 2 closing gate                      | 3 hosted-vs-native mirrors of real corpus programs               | 2026-05-12 |
| SI-15-bug | SM_EXEC_STMT named-subject fix        | `$name ? pat = repl` needed local-copy + write-back              | 2026-05-12 |
| SI-16 | one-shot stub all 87 SM_* opcodes         | Silent stubs for Icon/Prolog BB_*, generators, frame slots       | 2026-05-12 |
| SI-17a | sc2_assign mirror                         | Variable r/w mixed string+int                                    | 2026-05-12 |
| SI-17b | sc4_control mirror + APPLY-failure fix    | if/else with GT/LT/EQ; surfaced SM_CALL_FN APPLY-failure bug    | 2026-05-12 |
| SI-canonical | TT_STMT → STMT normalization        | 16 test files normalized to canonical parser_*.sc wire-shape    | 2026-05-12 |

---

## Open rungs

### SL-13d — parser_snobol4.sc populates Lower_collect

The last piece for true self-hosting.  `parser_snobol4.sc` (or
`parser_snocone.sc` for `.sc` source) needs to call `Lower_collect(stmt)`
with each parsed STMT tree so the all-Snocone pipeline can compile
arbitrary source files.

Current state: `bash SCRIP/scripts/run_scrip_parser.sh snobol4 trivial.sno`
runs end-to-end without hang or Error after SL-13c.  But for input
`X = 'hello' / END` it emits `; SM_Program count=1 / SM_HALT` — the
parser-driver isn't feeding a populated tree into Lower_collect.

Target output (matches `scrip --run --dump-sm trivial.sno`):
```
; SM_Program  count=6
   0  SM_STNO              stmt=1 line=1
   1  SM_PUSH_LIT_S        s="hello"
   2  SM_STORE_VAR         s="X"
   3  SM_LABEL             s="END"
   4  SM_STNO              stmt=2 line=3
   5  SM_HALT
```

- [ ] Wire parser_snobol4.sc's main loop to `Lower_collect(stmt)` per statement
- [ ] Confirm SM dump byte-identical to C `--run --dump-sm` for trivial.sno
- [ ] Extend to multi-statement programs from `programs/snobol4/smoke/`

### Phase 3 — Run the existing test suite through sm_interp.sc

End-goal: prove sm_interp.sc can execute the broad existing test corpus,
not just hand-built si_* tests.  Three parallel tracks:

| Track | Source                              | Approach                                                  |
|-------|-------------------------------------|-----------------------------------------------------------|
| A     | `programs/snocone/corpus/sc*.sc`    | Hand-build SI-15-style mirror per program                 |
| B     | Any `.sno` / `.sc`                  | `scripts/dump_ir_to_ast_builder.py` mechanical converter  |
| C     | Any source                          | Full pipeline via SL-13d (blocked until SL-13d lands)     |

#### SI-17 — Track A: corpus mirrors

| Source             | Features                       | Mirror name           | Status |
|--------------------|--------------------------------|-----------------------|--------|
| sc1_literals.sc    | strings, int lits, multi OUTPUT| si_15a_literals       | ✅ SI-15 |
| sc2_assign.sc      | variable assign + read         | si_17a_assign         | ✅ SI-17a |
| sc3_arith.sc       | full arithmetic                | si_15b_arith          | ✅ SI-15 |
| sc4_control.sc     | if/else + GT/LT/EQ             | si_17b_control        | ✅ SI-17b |
| sc5_while.sc       | while loop                     | si_17c_while          | ⏳ open |
| sc6_for.sc         | for loop                       | si_17d_for            | ⏳ open (probe TT_FOR first) |
| sc7_procedure.sc   | user-defined function          | si_17e_proc           | ⛔ blocked (lower_proc_skeletons stub) |
| sc8_strings.sc     | concat + SIZE                  | si_17f_strings        | ⏳ open |
| sc9_multiproc.sc   | multiple procs                 | si_17g_multiproc      | ⛔ blocked (same as sc7) |
| sc10_wordcount.sc  | pattern + counter              | si_17h_wordcount      | ⏳ open (probe pattern coverage) |

For each: hand-build AST via Lower_collect, build native counterpart with
framing `'--- interp ---'` / `'--- done ---'`, bake `.ref` from native,
add to `test_self_host_smoke.sh`.  Cross-check hosted vs native must be
byte-identical.

- [ ] SI-17c — sc5_while mirror
- [ ] SI-17d — sc6_for mirror (probe TT_FOR coverage)
- [ ] SI-17f — sc8_strings mirror
- [ ] SI-17h — sc10_wordcount mirror

#### SI-18 — Track B: scripts/dump_ir_to_ast_builder.py

Convert `scrip --dump-ast <file>` text output into an AST-builder `.sc`.
Format example:
```
(STMT :eq :subj (TT_VAR S) :repl (TT_QLIT "foobarbaz"))
(STMT :eq :subj (TT_VAR S) :pat (TT_QLIT "bar") :repl (TT_QLIT "XX"))
(STMT :eq :subj (TT_VAR OUTPUT) :repl (TT_VAR S))
```

Parse with Python regex into Python AST objects; emit `.sc` boilerplate
matching the SI-15/17 pattern: helpers + `Lower_collect(...)` per stmt +
framing + `lower + sm_interp_run`.

- [ ] Python converter written
- [ ] Validated on 3+ already-mirrored programs (output matches hand-built tests)
- [ ] Run on every feasible `programs/snobol4/smoke/*.sno` + `programs/snocone/corpus/sc*.sc`

#### SI-19 — Bulk-run harness

`scripts/test_self_host_corpus.sh` driving all converted+mirror tests.

- [ ] Harness driving ≥20 tests through `sm_interp.sc`
- [ ] Triage categories: `unimpl-opcode`, `lower-bug`, `interp-bug`, `host-semantic-diff`, `pre-existing-known`

#### SI-20 — Fix bugs surfaced by Track A + Track B

Each bug fix:
1. Minimal reproducer hand-built as `si_20X_<bug>.sc`
2. Fix in `sm_interp.sc` (or note if it's a `lower.sc` / parser issue)
3. Full harness re-run; no regression

- [ ] ≥3 bug fixes landed (or honest report of no bugs found)

#### SI-21 — Phase 3 closing gate

- [ ] Total self-host tests ≥ 30 (currently 16)
- [ ] All PASS or documented blocker
- [ ] `corpus/SCRIP/coverage_report.md` committed

---

## Phase 4 — deferred (real implementations of stubbed opcodes)

These opcodes have silent or TERMINAL-noted stubs in `sm_interp.sc` today.
Real implementations require host infrastructure beyond plain Snocone:

- **BB scheduler**: `SM_BB_PUMP`, `SM_BB_ONCE`, `SM_BB_ONCE_PROC`,
  `SM_BB_PUMP_PROC`, `SM_BB_PUMP_CASE`, `SM_BB_PUMP_SM`, `SM_BB_PUMP_EVERY`.
  Needs the Byrd-box scheduler ported or a host-side hook.
- **Generator coroutines**: `SM_SUSPEND`, `SM_SUSPEND_VALUE`, `SM_RESUME`,
  `SM_GEN_TICK`.  Needs swapcontext-style yield/resume.
- **Frame slots**: `SM_LOAD_FRAME`, `SM_STORE_FRAME`.  Needs Icon
  `icn_frame_env_load/store` hooks exposed to `.sc`.
- **Pattern callbacks**: `SM_PAT_CAPTURE_FN`, `_FN_ARGS`, `SM_PAT_USERCALL`,
  `_ARGS`.  Needs host pattern-engine callback hook.
- **lower_proc_skeletons**: currently `function lower_proc_skeletons() { return; }`
  at lower.sc:1024.  Blocks SI-17e/g and any Icon proc body.

---

## Session note — 2026-05-12 (Claude Sonnet 4.6, handoff #4)

**Strategic direction from Lon:** The high-value next move is to run `sm_interp.sc`
end-to-end from three frontend parsers — SNOBOL4, Snocone, Rebus — and compare
output against REF files using the existing crosscheck/regression suite.
Pipeline: `parser_*.sc → tree → lower.sc → sm_interp.sc`.

**SL-13d investigation results:**
- `parser_snobol4.sc` main loop already calls `Lower_collect(result)` (line 350) and `Lower_run()` — code is wired correctly.
- Running `bash scripts/run_scrip_parser.sh snobol4 trivial.sno` shows `SM_Program count=1 / SM_HALT` — Lower_collect is never triggered.
- Root cause isolated: after `Src ? Compiland` matches, `Top()` returns empty — the value stack is empty. `ptree = Pop()` returns `''` so `n(ptree) = ''` → zero children → the `while (LE(i, nk))` loop body never fires.
- Two `Error 5` at stmt 45 at load time are likely `SQize` or OPSYN/EVAL failures inside `_qtag()` (semantic.sc) during grammar construction, corrupting shift/reduce patterns so `Command`/`Stmt` rules don't push to the value stack during scanning.
- **Not pursued further per Lon directive.** SL-13d remains `- [ ]`. True self-hosting (Track C) is blocked on this.

**New primary objective:** Three-frontend crosscheck via Track B (Python converter).
Pipeline: `parser_*.sc → scrip --dump-ast → dump_ir_to_ast_builder.py → .sc test file → sm_interp.sc → diff .ref`.
Frontends: SNOBOL4, Snocone, Rebus.

**Corpus cleanup (sess 2026-05-12 handoff #5):** 53 test files (si_*, sm_interp_test*, sm_lower_test*, smoke_interp*, smoke_lower*, smoke.sc) moved from `corpus/SCRIP/` root into `corpus/SCRIP/tests/`. Runtime files (tree.sc, lower.sc, sm_interp.sc, parser_*.sc, etc.) remain in root. `test_self_host_smoke.sh` updated; gate 16/16 PASS confirmed. corpus `cee6722`, SCRIP `185c9832`.

**NEXT: SI-18** — write `scripts/dump_ir_to_ast_builder.py`, validate on 3+ already-mirrored programs, run on broad smoke corpus across all three frontends.

---

## Gate

```bash
SCRIP=/home/claude/SCRIP/scrip
SCRIP_DIR=/home/claude/corpus/SCRIP

# Gate 1: SL-9 / SI-5 baseline — smoke_lower + smoke_interp byte-identical
$SCRIP --run \
  $SCRIP_DIR/tree.sc $SCRIP_DIR/lower.sc $SCRIP_DIR/lower_driver.sc \
  $SCRIP_DIR/sm_interp.sc $SCRIP_DIR/smoke_interp.sc \
  | diff - $SCRIP_DIR/smoke_interp.ref

# Gate 2: Full self-host suite (all SI rungs)
bash /home/claude/SCRIP/scripts/test_self_host_smoke.sh

# Gate 3: No regressions in the broader matrix
bash /home/claude/SCRIP/scripts/test_smoke_snobol4.sh
bash /home/claude/SCRIP/scripts/test_smoke_snocone.sh
bash /home/claude/SCRIP/scripts/test_smoke_icon.sh
bash /home/claude/SCRIP/scripts/test_smoke_prolog.sh
bash /home/claude/SCRIP/scripts/test_smoke_rebus.sh
bash /home/claude/SCRIP/scripts/test_smoke_raku.sh
bash /home/claude/SCRIP/scripts/test_smoke_scrip_all_modes.sh
```

All must pass.  Cross-check gates (test_crosscheck_snobol4, _snocone,
test_lower_byte_identical) have pre-existing FAILs unrelated to this work;
verify "zero regressions" by stash-and-rerun against current HEAD.
