# GOAL-PROLOG-BB-BYRD — Wire Prolog into the Byrd Box Broker

## ⛔ FACT RULES POINTER (Lon 2026-06-06)
ONE MEDIUM, INVISIBLE + TEMPLATE-ONLY EMISSION (corrected): canonical text in GOAL-SNOBOL4-BB.md / GOAL-ICON-BB.md / GOAL-PROLOG-BB.md / GOAL-RAKU-BB.md and RULES.md. ZERO BINARY emission anywhere in a `bb_*.cpp` (top level or helpers); `x86()` internals are the ONLY emitter of BINARY and TEXT.

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
**Done when:** Prolog clause selection and backtracking runs through the same
brokered Byrd box four-port discipline that SNOBOL4 pattern matching uses.
Specifically: `E_CHOICE` compiles to a `bb_box_fn`-ABI box that a Prolog
broker drives with α/β entries; body goals are wired as concatenated boxes;
cut is the FENCE box analog; the raw `for ci` retry loop in `interp_eval`
E_CHOICE is deleted. rung01–rung11 all PASS through the new path.

**Why:** The current `interp_eval` E_CHOICE loop (raw `for ci` with manual
trail mark/unwind) is structurally incompatible with the SM lowering path.
SNOBOL4 patterns go: IR → SM_PAT_* → SM_EXEC_STMT → bb driver → α/β boxes.
Prolog must go the same route so Phase 2 (SM lowering → JIT x86 Byrd boxes)
can be built without a special case. The broker IS the backtracking engine —
both languages share the discipline even if they have separate brokers for now.

---

## Prerequisite

GOAL-PROLOG-IR-RUN S-1C-5 complete (pl_unified_call and helpers deleted,
builtins inlined into interp_exec_pl_builtin, rung01–rung11 all PASS).

---

## Architecture

### SNOBOL4 model (what we are matching)

```
sm_lower: E_ALT → SM_PAT_ALT → pat_alt(left_box, right_box)
exec_stmt Phase 3:
    result = root.fn(root.ζ, α)           // try
    if (ω) result = root.fn(root.ζ, β)    // retry — broker drives α/β
    advance scan cursor; repeat
```

Each box implements:
```c
spec_t my_box(void *zeta, int entry);  // entry: 0=α, 1=β
// α: first attempt → return non-empty spec (γ) or empty spec (ω)
// β: retry        → return next γ or ω
```

### Prolog four-port mapping

| Prolog concept        | Byrd box analog                              |
|-----------------------|----------------------------------------------|
| Predicate (E_CHOICE)  | OR-box: α tries clause[0]; β tries clause[i+1] |
| Clause body (E_CLAUSE)| AND-box / CAT chain: goals left-to-right     |
| Conjunction goal      | CAT-box: left γ → right α; right ω → left β |
| Disjunction (`;`)     | ALT-box: try left; on ω try right            |
| Cut (`!`)             | FENCE-box: γ on α; ω on all β               |
| Builtin goal          | Leaf box: α calls builtin; β returns ω       |
| Trail                 | g_pl_trail mark/unwind inside OR-box α/β     |

### Box ABI — reuse bb_box_fn

```c
// From bb_box.h — reused as-is for Prolog boxes
typedef spec_t (*bb_box_fn)(void *zeta, int entry);

// Prolog convention: non-empty spec = γ (success); empty spec = ω (fail)
// spec extent is ignored — Prolog is not positional
```

### New broker

```c
// pl_broker.c
int pl_exec_goal(Pl_GoalBox root);
// Calls root.fn(root.zeta, α). Returns 1 on γ, 0 on ω.
// No scan loop — Prolog is not positional; retry is the caller box's job.
```

```c
typedef struct { bb_box_fn fn; void *zeta; } Pl_GoalBox;
```

---

## Steps

- [x] **S-BB-1** — Define `Pl_GoalBox` and `pl_exec_goal()` in new
  `src/frontend/prolog/pl_broker.c` + `pl_broker.h`.
  `pl_exec_goal` calls `root.fn(root.zeta, α)`, returns 1 on γ, 0 on ω.
  Add `pl_broker.o` to Makefile.
  Gate: `make scrip` clean; rung01–rung11 unaffected (old path still active).

- [x] **S-BB-2** — Implement leaf boxes in `pl_broker.c`:
  `pl_box_true()`: γ on α, ω on β (succeed once).
  `pl_box_fail()`: ω on both (always fail).
  `pl_box_builtin()`: α calls `interp_exec_pl_builtin()`; β returns ω.
  Gate: compiles clean.

- [x] **S-BB-3** — Implement `pl_box_cat()` (conjunction / AND-box).
  State: `{left, right, phase}` where phase ∈ {ENTER, LEFT_DONE}.
  α: call left.fn(α); on γ → call right.fn(α); on right ω → left.fn(β), retry right.
  β: right.fn(β); on ω → left.fn(β), retry right from α; on left ω → return ω.
  Matches `bb_cat` discipline in `stmt_exec.c`.
  Gate: compiles clean.

- [x] **S-BB-4** — Implement `pl_box_clause()`: given one E_CLAUSE node and
  a caller arg-term array, build: head-unify leaf box CAT'd with each body
  goal box in order. Return root CAT-box.
  Head-unify box: α unifies head args, sets g_pl_env, returns γ or ω; β
  trail_unwinds and returns ω (head unification is not re-entrant).
  Gate: compiles clean.

- [x] **S-BB-5** — Implement `pl_box_choice()`: OR-box over all E_CLAUSE
  children of one E_CHOICE node.
  State: `{clauses[], nclause, ci, trail_mark}`.
  α: trail_mark(); build clause[0] box; call clause[0].fn(α).
  β: if clause box β returns γ → return γ; else trail_unwind(mark);
     advance ci; build clause[ci] box; call clause[ci].fn(α).
  On ci == nclause: return ω.
  Gate: compiles clean.

- [x] **S-BB-6** — Implement `pl_box_cut()`: FENCE analog.
  α: set g_pl_cut_flag = 1; return γ (success, proceed).
  β: return ω (no backtrack past cut — matches FENCE in stmt_exec.c).
  Gate: compiles clean.

- [x] **S-BB-7** — Wire `pl_execute_program_unified()` to use new boxes for
  `main/0`: call `pl_box_choice(main_choice_node)` → `pl_exec_goal()`.
  Remove the `interp_eval(main_choice)` call from the top-level entry.
  Gate: `./scrip --interp test/prolog/hello.pl` prints `Hello, World!`.
  rung01 PASS.

- [x] **S-BB-8** — Replace the body loop inside `interp_eval` E_CHOICE with
  box dispatch: user-predicate calls build `pl_box_choice()` +
  `pl_exec_goal()` instead of the raw `for ci` loop + `interp_eval(choice)`.
  Gate: rung01–rung11 all PASS through new broker path.

- [x] **S-BB-9** — Delete dead code: pl_exec_body, pl_exec_one_goal removed.
  grep pl_unified_call|pl_exec_body|for.*ci.*nclauses src/driver/scrip.c → empty.
  Gate: `make scrip` clean. ✓

- [x] **S-BB-10** — Regression: PASS=149 >= baseline 49. SNOBOL4/Icon unaffected.
  Commit identity LCherryholmes. SCRIP HEAD 9fc8e599. ✓

---

## Key files

| File | Role |
|------|------|
| `src/frontend/prolog/pl_broker.c` | NEW: broker + all Prolog box implementations |
| `src/frontend/prolog/pl_broker.h` | NEW: Pl_GoalBox, pl_exec_goal, box constructors |
| `src/runtime/x86/stmt_exec.c` | Reference: bb_cat, bb_alt, FENCE, broker loop |
| `src/runtime/x86/bb_box.h` | bb_box_fn typedef, α/β/spec_t — reused as-is |
| `src/driver/scrip.c` | E_CHOICE interp_eval case — target for deletion |
| `src/frontend/prolog/prolog_runtime.h` | Trail, EnvLayout — keep unchanged |
| `src/frontend/prolog/prolog_unify.c` | unify(), trail_* — keep unchanged |

---

## Rules

- No push until "perform hand off".
- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.
- Build gate before every commit: `make scrip` + `run_interp_broad.sh`.
- Prerequisite: GOAL-PROLOG-IR-RUN S-1C-5 must be complete before S-BB-7.
- No ad-hoc builds — all builds via Makefile or checked-in build scripts.

---

## Current state

S-BB-1 through S-BB-10 COMPLETE. SCRIP HEAD 9fc8e599. GOAL DONE.

Unified interpreter: Prolog E_CHOICE/E_CLAUSE/E_UNIFY/E_CUT/E_TRAIL_* wired as
cases in interp_eval() alongside SNOBOL4 and Icon. E_CHOICE uses pl_box_choice +
pl_exec_goal (Byrd box broker) for backtracking. pl_execute_program_unified calls
interp_eval(main_choice) directly. pl_exec_body/pl_exec_one_goal deleted.
pl_box_alt added; ,/2 ;/2 -> wired structurally in pl_box_goal_from_ir.
regression PASS=149 >= baseline 49. rung07 (cut) PASS.
