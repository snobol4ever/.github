# GOAL-PROLOG-IR-RUN — Get Prolog Working in scrip --interp

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

**Repo:** one4all
**Done when:** `.pl` files run correctly via `scrip --interp file.pl`, passing
the existing Prolog corpus rung tests.

---

## Current state (2026-04-14, one4all HEAD 5576ea9d)

S-1 through S-10c complete. Phase 1B complete (S-1B-1 through S-1B-6).
PASS=9/9 rung01-rung09 confirmed after merge.
findall/3 5/5 rung11 PASS (arith+template bugs fixed in Phase 1B rewrite).

Phase 1B DONE: `prolog_interp.c` and `prolog_interp.h` deleted. Prolog exec
logic consolidated into `scrip.c` as `pl_execute_program_unified()` + `pl_unified_*`
helpers. This was consolidation INTO scrip.c, NOT unification into `interp_eval()`.
The `lang_prolog` dispatch branch still calls a separate interpreter family
(`pl_unified_call` etc.) — it does NOT go through `interp_eval()` like Icon does.
Phase 1B steps S-1B-3/S-1B-4 were OVERCLAIMED: Prolog was never wired into
`execute_program()` or `interp_eval()`. Phase 1C below corrects this.

Next: **Phase 1C** — wire Prolog goals into `interp_eval()` using file-scope
globals (Trail, PredTable, CP stack), matching how Icon uses `icn_proc_table`
and calls `interp_eval` directly. Eliminate `pl_unified_exec_goal` and friends.
---

## Verification Technique

Claude presents each test result and asks: **T or F?**
- **T** — correct. Proceed.
- **F** — wrong. Re-diagnose before proceeding.

---

## Steps

- [x] **S-1** — Add Prolog frontend files to Makefile.
  Gate: `make scrip` clean with prolog objects included.

- [x] **S-2** — Write `prolog_driver.c` + wire `.pl` in `scrip.c`.
  Gate: `./scrip --interp hello.pl` reaches --interp (Error 5, not parse error).

- [x] **S-3** — Allocate `PlInterp` state in `scrip.c` for Prolog programs:
  `Trail`, global atom table pointer, predicate lookup table (functor/arity → `E_CHOICE*`).
  Build predicate table by walking `prog->head` stmts (each stmt subject is one `E_CHOICE`).
  Gate: predicate table built, `write/1` and `nl/0` registered as builtins.

- [x] **S-4** — Implement `pl_term_from_expr()`: convert lowered `EXPR_t` to `Term*`
  using a per-call variable env (`Term*[n_vars]`).
  Handles: `E_QLIT`→atom, `E_ILIT`→integer, `E_VAR`→env slot, `E_FNC`→compound.
  Gate: `write('Hello, World!')` argument converts to correct atom Term.

- [x] **S-5** — Implement `pl_call_builtin()`: handle `write/1`, `nl/0`, `fail/0`, `true/0`.
  Gate: `./scrip --interp test/prolog/hello.pl` prints `Hello, World!`.

- [x] **S-6** — Implement `pl_exec_body()`: execute a sequence of body goals
  (children of `E_CLAUSE` after the head args) left to right.
  Each goal is an `E_FNC` → look up predicate → call `pl_exec_choice()`.
  Gate: `main/0` body executes `write` + `nl` in sequence.

- [x] **S-7** — Implement `pl_exec_choice()`: α/β over `E_CLAUSE` children.
  For each clause: `trail_mark()`, unify head args, on success execute body,
  on fail `trail_unwind()` and try next clause.
  Gate: single-clause predicates work; `hello.pl` passes fully.

- [x] **S-8** — Implement `E_UNIFY` in body: call `unify(t1, t2, trail)`.
  Implement `E_CUT`: set a flag that prevents β from trying further clauses.
  Gate: programs using `=` and `!` work correctly.

- [x] **S-9** — Implement `E_TRAIL_MARK` / `E_TRAIL_UNWIND` in body goals.
  Gate: multi-clause predicates with backtracking work.

- [x] **S-10a** — Fix `,/N`, `;/N`, `->/N` arity guards in pl_exec_goal (lowerer emits n-ary).
  Gate: rung02 PASS.

- [x] **S-10b** — Fix cut scope: cut must not short-circuit forward body execution;
  only prevents retry. pl_call uses own local cut_flag, never propagates past predicate boundary.
  Gate: rung07 PASS. ✓

- [x] **S-10c** — Replace Proebsting retry-loop with proper choice point stack for recursive backtracking.
  Flat retry-loop (start++) cannot backtrack into recursive sub-calls (e.g. member/2, append/3).
  Implement ChoicePoint struct {clause_idx, trail_mark, env snapshot} pushed on each user call;
  on failure pop and resume. Mirror pl_call's clause loop but save continuation across C stack frames.
  Gate: rung05 PASS (member/2 with fail-loop finds all 3 solutions).

---

## Phase 1B — Unify: eliminate prolog_interp.c, wire Prolog into execute_program()

**⛔ DO THIS BEFORE the S-10x builtin ladder. This is the architectural foundation.**

**Architectural correction.** SCRIP has one IR and one `--interp` interpreter:
`execute_program()` in `scrip.c`. The six Prolog IR nodes (`E_CHOICE`, `E_CLAUSE`,
`E_UNIFY`, `E_CUT`, `E_TRAIL_MARK`, `E_TRAIL_UNWIND`) are already canonical in
`ir.h` alongside SNOBOL4 and Icon nodes. The separate `pl_execute_program()` /
`prolog_interp.c` tree-walker is wrong — it duplicates interpreter infrastructure
that belongs in one place. These steps eliminate it.

All Prolog runtime helpers (unify, trail, term, atom, builtin) remain as support
libraries — only the top-level dispatch loop and clause/choice execution move into
`execute_program()`.

- [x] **S-1B-1** — Add Prolog runtime state to `execute_program()`:
  Trail, atom table, predicate table (functor/arity → E_CHOICE*), CP stack.
  Build predicate table by walking `prog->head` stmts at program start,
  identical to what `pl_execute_program()` does today.
  Gate: compiles clean; no behaviour change yet.

- [x] **S-1B-2** — Add `interp_eval_prolog_term()` to `scrip.c`:
  Converts `EXPR_t*` → `Term*` using a per-clause variable env.
  Mirrors `pl_term_from_expr()` from `prolog_interp.c` — move, don't duplicate.
  Gate: compiles clean.

- [x] **S-1B-3** — Add `E_CHOICE` / `E_CLAUSE` handling to `execute_program()`
  statement loop. When the top-level stmt subject is `E_CHOICE` (predicate
  definition), register it in the predicate table. When stmt subject is `E_CLAUSE`
  (a bare clause at top level), execute it directly. Entry point: call `main/0`
  after all stmts are registered, using the shared CP-stack dispatcher.
  Gate: `./scrip --interp hello.pl` prints `Hello, World!`.

- [x] **S-1B-4** — Add `E_UNIFY`, `E_CUT`, `E_TRAIL_MARK`, `E_TRAIL_UNWIND`,
  `E_FNC` (Prolog builtins) to `interp_eval()` in `scrip.c`.
  These are goal-context evaluations: return success/failure signal rather than
  a DESCR_t value. Add a `interp_exec_goal()` wrapper that dispatches by kind.
  Gate: rung01–rung04 still PASS, rung07 still PASS.

- [x] **S-1B-5** — Delete `prolog_interp.c` and `prolog_interp.h`.
  Remove `pl_execute_program()` call from `scrip.c` main dispatch.
  Remove `lang_prolog` branch that called `pl_execute_program()` — Prolog now
  falls through to the unified `execute_program()` path.
  Gate: `make scrip` clean; all previously passing rungs still PASS.

- [x] **S-1B-6** — Run full rung01–rung09 regression. Fix any delta.
  Gate: PASS count ≥ 13/107 (session-start baseline).

---

## Phase 1C — Wire Prolog into interp_eval() (true one-interpreter goal)

**Why:** Phase 1B consolidated `pl_unified_*` into `scrip.c` but left Prolog as
a separate interpreter family. Icon calls `interp_eval()` directly from
`icn_call_proc`. Prolog must do the same: `E_CHOICE`, `E_CLAUSE`, `E_UNIFY`,
`E_CUT`, `E_TRAIL_MARK`, `E_TRAIL_UNWIND` must become cases in `interp_eval()`'s
switch, using file-scope globals (Trail, PredTable, CP stack) exactly as Icon
uses `icn_proc_table`, `icn_returning`, `icn_return_val`, `icn_gen_stack`.

**The model:** `icn_execute_program_unified()` builds proc table → calls
`icn_call_proc()` → calls `interp_eval()`. Prolog's `pl_execute_program_unified()`
must become: build pred table (globals) → call `pl_call_goal()` → which dispatches
through `interp_eval()` for every Prolog IR node. `pl_unified_exec_goal` and all
`pl_unified_*` helpers that duplicate what `interp_eval` already does are deleted.

**What stays:** Trail, Term, unify(), prolog_atom_*, pl_write, pl_env_new,
pl_pred_table_*, pl_cp_stack. These are support infrastructure, not interpreter.

**What moves into interp_eval():**
- `E_CHOICE` → register in g_pl_pred_table (at program-load time, not eval time)
- `E_CLAUSE` → execute clause: unify head args into env, run body via interp_eval
- `E_UNIFY`  → call unify(t1,t2,g_pl_trail); return INTVAL(1) or FAILDESCR
- `E_CUT`    → set g_pl_cut_flag; return INTVAL(1)
- `E_TRAIL_MARK` / `E_TRAIL_UNWIND` → operate on g_pl_trail; return NULVCL
- `E_FNC` (Prolog goal context) → dispatch via new `interp_exec_pl_goal()` called
  from interp_eval when g_pl_active is set

**File-scope globals to add (near icn_proc_table block):**
```c
static Pl_PredTable g_pl_pred_table;
static Trail        g_pl_trail;
static int          g_pl_cut_flag = 0;
static Term       **g_pl_env      = NULL;   /* current clause env */
static int          g_pl_active   = 0;      /* 1 when executing Prolog */
```

- [x] **S-1C-1** — Promote Trail and PredTable to file-scope globals `g_pl_trail`,
  `g_pl_pred_table`, `g_pl_cut_flag`, `g_pl_env`, `g_pl_active`.
  Added near `icn_proc_table` block. `pl_execute_program_unified()` inits globals.
  Gate: compiles clean, rung01-rung09 9/9 PASS. ✓

- [x] **S-1C-2** — Add `E_UNIFY`, `E_CUT`, `E_TRAIL_MARK`, `E_TRAIL_UNWIND` cases
  to `interp_eval()` switch. Forward decls added for `pl_unified_term_from_expr`,
  `pl_env_new`, `pl_pred_table_lookup`, `is_pl_user_call`, `pl_unified_exec_goal`.
  Gate: compiles clean, rung01-rung09 9/9 PASS. ✓

- [x] **S-1C-3** — Add `E_CHOICE` case to `interp_eval()`: iterates E_CLAUSE children
  with backtracking via `g_pl_trail`. `E_CLAUSE` is not a standalone case — handled
  inline by E_CHOICE. `pl_execute_program_unified` now calls `interp_eval(main_choice)`
  directly instead of `pl_unified_call`.
  Gate: hello.pl passes through new path. ✓

- [x] **S-1C-4** — User-defined predicate calls in body loop now route through
  `interp_eval(choice_node)` instead of `pl_unified_call`. Builtins still through
  `pl_unified_exec_goal` (to be inlined in future step).
  Gate: rung01-rung11 5/5+9/9 PASS. ✓

- [x] **S-1C-5** — Unified interpreter complete. E_CHOICE/E_CLAUSE/E_UNIFY/E_CUT/
  E_TRAIL_* cases in interp_eval(). pl_exec_body/pl_exec_one_goal deleted.
  pl_box_alt added for ;/2. regression PASS=149. one4all HEAD 9fc8e599. ✓
  `pl_unified_call`, `pl_unified_exec_body`, `pl_unified_exec_body_k`,
  `pl_unified_exec_clause`. Inline builtins from `pl_unified_exec_goal` into
  a new `interp_exec_pl_builtin()` called from E_CHOICE body loop.
  Gate: make scrip clean, rung01-rung11 all PASS, no pl_unified_call remaining.

  ⚠️ Session 2026-04-13: INCOMPLETE. Dead functions deleted, interp_exec_pl_builtin
  written, but pl_exec_body (wrong approach) introduced regression: 7/14 PASS
  (rung02/05/07/11 fail). one4all HEAD 1bfdd9c9. PIVOT next session to
  GOAL-PROLOG-BB-BYRD — remove pl_exec_body, wire backtracking via Byrd boxes.

---

## S-10x builtin ladder — do AFTER Phase 1C complete

- [x] **S-10d** — `findall/3`: 5/5 rung11 PASS (fixed in Phase 1B rewrite).
  Note: findall currently in `pl_unified_exec_goal`; moves to `interp_exec_pl_goal`
  in Phase 1C.

- [ ] **S-10e** — `assertz/asserta/retract/abolish`: dynamic predicate table mutation.
  Gate: rung13 5/5, rung14 5/5, rung15 5/5.

- [ ] **S-10f** — atom builtins: `atom_length/2`, `atom_chars/2`, `atom_codes/2`, `atom_concat/3`.
  Gate: rung12 5/5.

- [ ] **S-10g** — `@</2`, `@>/2`, `@=</2`, `@>=/2` term ordering comparisons.
  Gate: rung16 5/5.

- [ ] **S-10h** — `sort/2`, `msort/2`.
  Gate: rung17 5/5.

- [ ] **S-10i** — `succ/2`, `plus/3`.
  Gate: rung18 5/5.

- [ ] **S-10j** — `format/2` (`~w`, `~a`, `~d`, `~i`, `~n`).
  Gate: rung19 5/5.

- [ ] **S-10k** — `numbervars/3`.
  Gate: rung20 5/5.

- [ ] **S-10l** — `char_type/2`.
  Gate: rung21 5/5.

- [ ] **S-10m** — `write_canonical/1`, `writeq/1`, `print/1`.
  Gate: rung22 5/5.

- [ ] **S-10n** — arith ext: bitwise ops, `max/min`, `**`, `sign`, `truncate/round/floor/ceiling`.
  Gate: rung23 5/5.

- [ ] **S-10o** — string/IO builtins: `atom_string`, `number_string`, `string_concat`, `string_length`, `string_lower/upper`.
  Gate: rung24 5/5.

- [ ] **S-10p** — `term_string/2`, `term_to_atom/2`.
  Gate: rung25 5/5.

- [ ] **S-10q** — `copy_term/2`, `concat_atom/2`, `atom_to_term/3`.
  Gate: rung26 5/5.

- [ ] **S-10r** — aggregate: `nb_setval/nb_getval`, `aggregate_all`.
  Gate: rung27 5/5.

- [ ] **S-10s** — exceptions: `throw/1`, `catch/3`.
  Gate: rung28 5/5.

- [ ] **S-10t** — float ops: `float/1`, `float_integer_part`, `float_fractional_part`, `sin/cos/exp/log`, `gcd`.
  Gate: rung29 5/5.

- [ ] **S-10u** — DCG: `phrase/2,3`, `-->` rule expansion.
  Gate: rung30 5/5.

- [ ] **S-11** — Run rung01–rung05 full Prolog corpus ladder.
  Gate: PASS count matches or exceeds prior JVM-emitter baseline.

- [ ] **S-12** — Add `test/frontend/prolog/run_prolog_ir_rung.sh` runner.
  Gate: script runs clean, results reproducible.

- [ ] **S-13** — Update PLAN.md ☑ done.

---

## Key files
| File | Role |
|------|------|
| `src/ir/ir.h` | Canonical IR node kinds — 6 Prolog nodes already defined |
| `src/driver/scrip.c` | `execute_program()` — THE one IR interpreter; Prolog goes here |
| `src/frontend/prolog/prolog_lower.c` | `prolog_lower()` → `CODE_t*` (frontend, keep) |
| `src/frontend/prolog/prolog_lower.h` | E_CLAUSE layout documentation (keep) |
| `src/frontend/prolog/prolog_unify.c` | `unify()`, `trail_*` — runtime support, keep |
| `src/frontend/prolog/prolog_runtime.h` | `Trail`, `EnvLayout` types — keep |
| `src/frontend/prolog/term.h` | `Term` type — keep |
| `src/frontend/prolog/prolog_interp.c` | DELETE after Phase 1B complete |
| `src/frontend/prolog/prolog_interp.h` | DELETE after Phase 1B complete |
| `test/prolog/hello.pl` | Primary smoke test |
| `test/prolog/palindrome.pl` | Secondary smoke test |

---

## Rules
- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.
- Build gate before every commit: `make scrip` + `run_interp_broad.sh` must not regress.
- No ad-hoc builds — use/extend `Makefile` and `test/` scripts.

---

## Phase 2 — Stack Machine and x86 Byrd Box execution

Once `--interp` (tree-walk interpreter) is passing corpus tests, Prolog should
graduate to the same execution pipeline as SNOBOL4: SM lowering → SM interpreter
→ JIT x86 Byrd boxes. The Proebsting technique that `prolog_emit.c` already
implements in C output maps directly to the SM instruction set.

- [ ] **S-14** — Wire Prolog IR through `sm_lower.c`:
  Add cases for `E_CLAUSE`, `E_CHOICE`, `E_UNIFY`, `E_CUT`, `E_TRAIL_MARK`,
  `E_TRAIL_UNWIND` in `sm_lower()`. Each Byrd box port (α/β/γ/ω) maps to
  SM instructions exactly as SNOBOL4 patterns do.
  Gate: `./scrip --interp hello.pl` produces `Hello, World!`.

- [ ] **S-15** — Wire Prolog IR through `sm_codegen.c` (x86 JIT):
  Add x86 emission for the Prolog SM opcodes. The Byrd box wiring (α→β→γ→ω)
  is identical to the pattern engine — reuse the existing four-port infrastructure.
  Gate: `./scrip --run hello.pl` produces `Hello, World!`.

- [ ] **S-16** — Run full Prolog corpus on `--run`. Fix failures.
  Gate: PASS count matches `--interp` baseline.

- [ ] **S-17** — Update PLAN.md ☑ done (Phase 2).

---

## Phase 2 architecture note

`prolog_emit.c` already generates C with labeled gotos that is structurally
identical to what `sm_codegen.c` emits for SNOBOL4 patterns. The mapping is:

| Prolog emit_clause construct | SM instruction |
|------------------------------|---------------|
| α entry label                | `SM_CLAUSE_ALPHA` |
| β retry label                | `SM_CLAUSE_BETA` |
| `trail_mark()` + head unify  | `SM_UNIFY` |
| `trail_unwind()` on fail     | `SM_TRAIL_UNWIND` |
| body goal call               | `SM_CALL` |
| γ success goto               | `SM_GOTO_GAMMA` |
| ω failure goto               | `SM_GOTO_OMEGA` |

These SM opcodes may need to be added to `sm_prog.h` if not already present.
Check `sm_prog.h` and `sm_lower.c` before starting S-14.

---
## Current state (2026-04-14, one4all HEAD d37dc9ef)

S-1 through S-1C-5 complete. Phase 1C done. BB-BYRD done. rung11 5/5.

**Session 2026-04-14 fixes (commit d37dc9ef):**

**Bug C — FIXED:** `pl_write` in `prolog_builtin.c` wrapped every binary operator
compound in unconditional parens, producing `[(a-1),(b-2),(c-3)]` instead of `[a-1,b-2,c-3]`.
Fix: replaced simple ops[] table with a full precedence-aware table. Added file-scope
`pl_op_prec(name,arity)` helper returning standard Prolog operator precedence. Binary op
printing now only adds parens when an argument is an operator with higher prec number
(lower binding) or same prec + wrong associativity. Alphabetic operators get spaces.
rung11: **5/5 PASS**. rung01–09: **9/9 PASS** (no regression).

**Score: PASS=19/107** (was 18). rung01–11 scope: **14/14 PASS**.

**Next step:** S-10e — assertz/asserta/retract/abolish dynamic predicate table mutation.
assertz/asserta/retract are currently stubs (return 1 always) in `interp_exec_pl_goal`
in scrip.c (~line 3083). Gate: rung13 5/5, rung14 5/5, rung15 5/5.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
```
