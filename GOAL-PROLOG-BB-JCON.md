# GOAL-PROLOG-BB-JCON.md — Prolog: BB-land DCG per predicate + lower_pl DCG

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ NO AST WALKING IN MODES 2/3/4 — see RULES.md § "NO AST WALKING IN MODES 2, 3, OR 4"         ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║  Sess 2026-05-15g removed all tree_t* dereferences from sm_interp.c (mode 2) and                ║
║  sm_jit_interp.c (mode 3). Stubs print [NO-AST] <opcode> on stderr.                              ║
║                                                                                                  ║
║  If a gate breaks with [NO-AST] FOO — write fresh SM/BB lowering for FOO.                       ║
║  Do NOT restore the AST-walking call.  Do NOT route through pl_pred_table_lookup_global,        ║
║  pl_unified_term_from_expr, interp_exec_pl_builtin, or any other back-door that hands a         ║
║  tree_t* to mode-2/3/4 code.                                                                     ║
║                                                                                                  ║
║  Mode 1 (`--ir-run` standalone AST interp) is unchanged and remains the reference path.        ║
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
║    • pl_lazy_box   — infrastructure shim, not a generator (to be added, mirror of icn_lazy_box) ║
║    • pl_bb_dcg     — infrastructure DCG driver, not a generator (to be added, mirror of icn_bb_dcg) ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_pl.c) driven by pl_bb_dcg.               ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template — the same   ║
║  pattern applies, just substitute Prolog port semantics for Icon's.                             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝


╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — CROSS-LANGUAGE CALLS GO SM↔SM OR BB↔BB, NEVER SM↔BB                         ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  Each language owns its own SM↔BB bridge contract WITHIN that language:                         ║
║    • Prolog:  `SM_BB_ONCE_PROC` / `pl_bb_dcg` / `dcg_table[i].ir_body`                          ║
║    • Icon:    `SM_BB_PUMP_PROC` / `icn_bb_dcg` / `proc_table[i].ir_body`                        ║
║    • SNOBOL4: `SM_PAT_*` composer family / `pat_cat`/`pat_alt` / PATND_t tree                   ║
║                                                                                                  ║
║  The α/β/γ/ω port semantics differ per language:                                                ║
║    • Prolog "β"  → pop a choice-point, unwind trail, try the next clause                         ║
║    • Icon "β"   → advance a generator's internal counter, yield next value                       ║
║    • SNOBOL4 "β" → backtrack along the pattern's anchor chain                                    ║
║                                                                                                  ║
║  These contracts are NOT interchangeable.                                                       ║
║                                                                                                  ║
║  When polyglot code crosses a language boundary, the call MUST land at the same level it       ║
║  left from:                                                                                      ║
║                                                                                                  ║
║    SM(lang_A) ──→ SM(lang_B)    via top-level dispatch (SM_CALL_FN, frontend emission)          ║
║    BB(lang_A) ──→ BB(lang_B)    via a registered BB callee at the same level                    ║
║                                                                                                  ║
║  NEVER:                                                                                          ║
║                                                                                                  ║
║    SM(lang_A) ──→ BB(lang_B)    direct reach-across — DIFFERENT port semantics                  ║
║    BB(lang_A) ──→ SM(lang_B)    direct reach-up — bypasses the bridge contract                  ║
║                                                                                                  ║
║  The SM↔BB bridge inside any one language is the ONLY place SM-level and BB-level code         ║
║  meet, and that bridge is owned by — and meaningful only for — that one language.               ║
║                                                                                                  ║
║  Polyglot composability is structural, not semantic.  Cutting and pasting BBs across            ║
║  languages produces a syntactically valid graph that runs nonsense.  Composition WITHIN a       ║
║  language is plug-and-play; composition ACROSS languages requires a deliberate ABI bridge at   ║
║  the SM↔SM or BB↔BB level that translates port semantics.                                       ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** one4all + corpus + .github
**Prereq:** GOAL-PROLOG-BB-COMPLETE (PB-8 ✅ honest 111/294 FAIL=0 ABORT=0 at one4all `c9b7428d`)
**Sister Goal:** GOAL-ICON-BB-JCON (use it as the template — same architecture, swap port semantics)

## Session Setup

  cd /home/claude/one4all && bash scripts/build_scrip.sh

⚠ Read `.github/GOAL-ICON-BB-JCON.md` first — the architecture is identical; this Goal is the Prolog instantiation of the same pattern.
⚠ Read `ARCH-PROLOG.md` for Prolog port semantics (α/β/γ/ω meaning in clause-resolution context).
⚠ No C BB functions anywhere. A C BB is a `DESCR_t foo(void *zeta, int entry)`
  function that implements four-port logic (α/β/γ/ω) in C. These must not exist.
  `pl_lazy_box` and `pl_bb_dcg` are infrastructure bridges — not generator logic — keep them.

---

## Current state (one4all c2c20d1a+)

- `pl_runtime.c` still walks `tree_t*` heavily — `pl_pred_table_lookup_global`,
  `pl_unified_term_from_expr`, `interp_exec_pl_builtin` all dereference AST.
- These call sites are now stubbed out from modes 2/3/4 per the NO-AST-WALK directive.
- Build is CLEAN. Gates: smoke_prolog 0/5 (all stub).  ir-run still works
  via mode 1 (AST interp) — that path is unchanged.
- Prolog SM emission already produces the target shape: a program like
  `:- initialization(main). main :- write(hello), nl.` compiles to
  `SM_STNO + SM_STNO + SM_BB_ONCE_PROC "main"/0 + SM_HALT` (4 SM instructions).
- `SM_BB_ONCE_PROC` is currently a `[NO-AST]` stub in sm_interp.c —
  it must be filled in mirror of `SM_BB_PUMP_PROC` for Icon.

---

## Architecture — what we are building

### Three layers, with the SM↔BB bridge as the only contact point:

```
AST  -- (lower time) -->  SM_Program     [contains SM_BB_ONCE_PROC bridge opcodes]
                          IR_block_t *   [pre-built per predicate, lives in BB land]

Runtime: SM interp / SM JIT / SM emit-text runs SM_Program.
         An SM_BB_ONCE_PROC instruction brokers from SM into BB land by handing the
         pre-built IR_block_t* to bb_broker (driving pl_bb_dcg, which calls
         IR_exec_once / IR_exec_resume).  SM never sees tree_t*; BB never sees
         tree_t*; modes 2/3/4 are AST-free.
```

The SM_Program is the entry point.  Execution starts in SM.  A Prolog program
compiles down to an SM_Program containing `SM_BB_ONCE_PROC` bridge opcodes
(one per predicate call, plus the directive launchers like `:- initialization(main)`).
Those bridges hand pre-built IR_block_t*'s to bb_broker.  The IR_block_t*
registry is BB-land state, indexed by the bridge opcode's operand (predicate
name + arity).  Nothing at runtime dereferences a tree_t*.

### ⚡ Target shape: composition by SM bridges (SNOBOL4 pattern parallel)

End-state for Prolog (same model as Icon, different port semantics):

  • Each Prolog **predicate** compiles to **one IR_block_t* per predicate**,
    registered in BB-land by name/arity (`dcg_table[i].ir_body`).  This is
    the natural unit — analogous to Icon's `proc_table[i].ir_body`.
  • Predicates are **composable**: an `IR_PL_CALL` node inside one predicate's
    body holds a reference (by name+arity or by direct pointer) to another
    predicate's IR_block_t.  Choice-point and trail-mark/unwind machinery is
    encoded in IR nodes around the call.
  • The whole program ends up as one BB DAG in BB-land — but the DAG is
    *built by the SM stream postorder-style*, exactly like SNOBOL4 patterns.

The same SNOBOL4 postorder-composition path applies here.  SM-level
composer bridges for Prolog could include:

  SM bridge instruction          → BB-land composer / driver
  ───────────────────────────────────────────────────────────────────────
  SM_BB_PL_LIT_I  <int>          → push IR_block_t for IR_LIT_I
  SM_BB_PL_LIT_S  <str>          → push IR_block_t for IR_LIT_S
  SM_BB_PL_VAR    <name>         → push IR_block_t for IR_VAR (Prolog logical var)
  SM_BB_PL_UNIFY                 → pop 2, push ir_pl_unify_compose(L, R)
  SM_BB_PL_CALL   <name> <arity> → pop arity, push ir_pl_call_compose(name, args)
  SM_BB_PL_CONJ   <ngoals>       → pop ngoals, push ir_pl_seq_compose(goals)
  SM_BB_PL_DISJ   <nalts>        → pop nalts, push ir_pl_choice_compose(alts)
  SM_BB_PL_CUT                   → push IR_block_t for IR_PL_CUT
  SM_BB_PL_PRED   <name> <arity> → pop 1 body, register predicate in dcg_table
  SM_BB_ONCE_PROC <name> <arity> → pop 1 IR_block_t*, drive via pl_bb_dcg

Each predicate body is one IR_block_t* (one BB per predicate); predicates
reference each other through `IR_PL_CALL` nodes; the whole program is one
composable BB DAG.

**Either path lands at the same endpoint.**  Composition at lower time
(today's path — build `dcg_table[i].ir_body` from AST during `lower()`)
or composition at startup via composer bridges (SNOBOL4-style postorder)
are equivalent.

### Earlier directive (preserved): Prolog program = SMALL fixed SM prefix + ONE bridge per call

A simple Prolog program like
```
:- initialization(main).
main :- write(hello), nl.
```
compiles to ~4 SM instructions:
```
SM_STNO
SM_STNO
SM_BB_ONCE_PROC "main"/0
SM_HALT
```
The whole program runs through ONE bridge instruction
(`SM_BB_ONCE_PROC main/0`), which brokers into BB land where
`dcg_table[main/0].ir_body` lives.  Body goals (`write(hello)`, `nl`)
are nested IR_CALL/IR_PL_CALL nodes inside that IR_block_t.

### Lessons from prologue languages — flat label-threaded code

The same lessons that apply to Icon (jcon model) apply here:

  1. **Four-port labels per AST node.**  Allocate four named labels for
     every Prolog goal:

         p.ir.start    -- entry (α-port: first attempt)
         p.ir.resume   -- re-entry to try next clause (β-port)
         p.ir.success  -- continuation on goal success (γ-port)
         p.ir.failure  -- continuation on goal failure (ω-port)

     For Prolog the β port is choice-point retry: pop the trail back to
     the saved mark, advance to the next matching clause, re-enter at
     that clause's start.

  2. **Composition = pure label-stitching.**  A conjunction `(A, B)`:
     `A.success → B.start; B.success → outer.success; B.failure → A.resume`
     A disjunction `(A ; B)`:
     `A.start → first; A.failure → B.start; B.failure → outer.failure`

  3. **Choice-point state carries no opaque struct.**  Trail mark / unwind
     is just two IR instructions (TRAIL_MARK, TRAIL_UNWIND).  The "next
     clause index" is a normal IR register advanced on resume.

  4. **One IR instruction set, no per-construct opcodes.**  `IR_PL_CHOICE`,
     `IR_PL_UNIFY`, `IR_PL_CUT`, `IR_PL_CALL` are already in the enum.
     Their executors should be label-stitching composition over the
     universal `IR_MOVE/GOTO/OPFN/...` triad — same lesson as Icon.

#### Concrete next-step impact

For the immediate work (close smoke_prolog 5/5):

  • **write_atom, unify, arith** — these need a working `SM_BB_ONCE_PROC` body
    handler that drives the pre-built IR_block_t for `main` (which contains
    IR_CALL to builtins like `write`, `nl`, `=`, `is`).  Mirror of Icon's
    `SM_BB_PUMP_PROC` body handler.

  • **clause** — `fact(X)` with multiple clauses: needs `IR_PL_CHOICE`
    executor to iterate clauses, try unification, succeed-or-backtrack.
    Trail mark/unwind required.

  • **recursion** — `count(N) :- N > 0, write(N), nl, N1 is N-1, count(N1).`
    needs `IR_PL_CALL` to recursively invoke a predicate via its IR_block_t.

### Same pattern as SNOBOL4 and Icon — only the port semantics differ

| Language | SM bridge | BB driver | BB-land registry | β port semantics |
|---|---|---|---|---|
| Icon | `SM_BB_PUMP_PROC` | `icn_bb_dcg` | `proc_table[i].ir_body` | advance generator counter |
| Prolog | `SM_BB_ONCE_PROC` | `pl_bb_dcg` (to be added) | `dcg_table[i].ir_body` (to be added) | retry next clause + trail unwind |
| SNOBOL4 | `SM_PAT_*` family | direct via `pat_match` | composed PATND_t on SM stack | anchor-chain backtrack |

The structural pattern is the same.  The α/β/γ/ω semantics differ.
Cross-language calls go SM↔SM or BB↔BB, never SM↔BB across languages
(see absolute banner box at top).

### Two execution paths for Prolog backtracking:

**Path A — `--ir-run` / `--sm-run` (interpreter):**
`pl_bb_build(tree_t*)` → `bb_node_t{fn, zeta, 0}` → `bb_broker` drives fn(zeta,α/β).
The `fn` pointer must be `pl_bb_dcg` which drives an `IR_block_t` DCG built at
lower time (or built fresh from `lower_pl_*` at runtime).

**Path B — `--sm-native` / mode-4 (JIT emitter):**
`emit_bb_pl_*(s, f, b)` emits inline x86 implementing α/β directly.
No C function called by the blob. Trail/binding tables in `.data`, blob
reads/writes fields via [rip+offset].

### The `pl_bb_dcg` bridge (infrastructure, not a C BB — to be added):

```c
typedef struct { IR_block_t *cfg; int first; } pl_dcg_state_t;
DESCR_t pl_bb_dcg(void *zeta, int entry) {
    pl_dcg_state_t *z = zeta;
    if (entry == α) { z->first = 1; }
    return z->first ? (z->first=0, IR_exec_once(z->cfg)) : IR_exec_resume(z->cfg);
}
```

`pl_bb_build` creates a `pl_dcg_state_t` with a freshly built `IR_block_t` and
returns `(bb_node_t){ pl_bb_dcg, dz, 0 }`. The broker calls `pl_bb_dcg(zeta, α)`
on first call, `pl_bb_dcg(zeta, β)` for backtrack retry.

This is byte-for-byte identical to `icn_bb_dcg` — the only difference is the
name and the fact that the IR_block_t it drives contains Prolog-flavored IR
nodes (IR_PL_CHOICE, IR_PL_UNIFY, ...) instead of Icon ones.

### IR executor cases needed (ir_exec.c):

```c
case IR_PL_UNIFY: {
    /* c[0]=lhs term, c[1]=rhs term.  Attempt unification, push trail entries
       on success, return γ.  On failure return ω.  Backtracking via β re-tries
       (currently a no-op since unification doesn't introduce choice points;
       β is for the surrounding IR_PL_CHOICE).  */
    ...
}
case IR_PL_CALL: {
    /* nd->sval = "pred/arity"; nd->c[0..n-1] = arg IR nodes.
       Look up dcg_table[name].ir_body, drive via pl_bb_dcg recursion.  */
    ...
}
case IR_PL_CHOICE: {
    /* c[0..n-1] = clause bodies.  Iterate.  α path: trail_mark, try c[0].
       β path: trail_unwind, advance index, try c[next].  When exhausted, ω.  */
    ...
}
case IR_PL_CUT: {
    /* Discard all choice points up to the parent predicate's entry.
       Set the cut barrier so β backtrack will skip past them.  */
    ...
}
```

### IR_exec_resume (ir_exec.c):
Same as IR_exec_once but skips IR_reset — continues from current node state.
For Prolog: α path resets clause counter to 0; β path advances it.

### `dcg_table` (BB-land registry, to be added):

Mirror of `proc_table` for Icon, but for Prolog predicates:

```c
typedef struct {
    char           *name;       /* "pred/arity" key */
    int             arity;
    IR_block_t     *ir_body;    /* the compiled clause-list as one IR */
    PlScope         lower_sc;   /* scope/var table built at lower time */
    /* Note: NO tree_t* fields — modes 2/3/4 never see AST */
} Pl_PredEntry_BB;

extern Pl_PredEntry_BB g_dcg_table[MAX_DCG];
extern int g_dcg_count;
```

The existing `Pl_PredEntry` in `pl_runtime.c` carries `tree_t*` — that table
is now mode-1-only.  Modes 2/3/4 use `g_dcg_table` exclusively.

---

## How to implement each Prolog construct

Mirror of the Icon "How to implement each of the 43 BB" section.

### Step 1 — Understand alpha/beta
For Prolog: α = "first attempt at this goal"; β = "retry after failure
(backtrack from a later goal)".  γ = goal succeeded; ω = goal failed.

For a clause head match: α tries to unify head with goal; β re-tries
with the next clause in the predicate's clause list.

### Step 2 — Add IR kind (IR.h)
`IR_PL_CHOICE`, `IR_PL_UNIFY`, `IR_PL_CUT`, `IR_PL_CALL` are already declared.
Add new kinds for any construct not covered by these.

### Step 3 — Add executor case (ir_exec.c)
Add `case IR_PL_CONSTRUCT:` to `IR_exec_node` switch.  Use `nd->state` for
clause index, `nd->counter` for trail position, `nd->opaque` for the
bindings table pointer.  Set `nd->value` and return `nd->γ` (success)
or `nd->ω` (fail).

### Step 4 — Add DCG builder (lower_pl.c — to be created)
Mirror `lower_icn.c`.  Functions like:
```c
IR_block_t *lower_pl_predicate(tree_t *pred);     /* mirror of lower_icn_proc_body */
IR_block_t *lower_pl_choice(IR_t **clauses, int n);
IR_block_t *lower_pl_unify(IR_t *lhs, IR_t *rhs);
IR_block_t *lower_pl_call(const char *name, int arity, IR_t **args);
```

### Step 5 — Wire into pl_bb_build (pl_runtime.c — to be expanded)
Currently pl_runtime.c walks AST.  Add `pl_bb_build(tree_t *e)` mirror of
`icn_bb_build` — return `(bb_node_t){pl_bb_dcg, dz, 0}` where dz holds a
freshly lowered IR_block_t for the goal.

### Step 6 — Write inline x86 emitter (emit_bb.c)
For mode 4 / JIT: emit inline x86 implementing α/β directly, no C call.
Zeta layout: `.quad 0` per 8-byte field (trail pos, clause idx, bindings ptr),
accessed as `[rip + zlbl + offset]`.

### Step 7 — GATE-1..4, commit

---

## Gates

  GATE-1  bash scripts/test_smoke_prolog.sh                # PASS=5 (currently 0)
  GATE-2  bash scripts/test_smoke_unified_broker.sh        # PASS >= current
  GATE-3  bash scripts/test_prolog_ir_all_rungs.sh         # PASS >= prev (if script exists)
  GATE-4  bash scripts/test_icon_sm_no_ast_walk.sh         # honest PASS >= 277 (cross-lang gate)

If a Prolog-specific honest-mode gate script does not yet exist,
write one mirroring `test_icon_sm_no_ast_walk.sh` — set
`SCRIP_NO_AST_WALK=1`, run all Prolog rungs through `--sm-run`,
count PASS / FAIL / ABORT.

---

## Active steps

### PJ-1 — pl_bb_dcg + dcg_table skeleton

- [ ] Add `pl_bb_dcg` infrastructure bridge (C function, but NOT a Byrd box —
      it's a DCG driver, same exemption as `icn_bb_dcg`).
      Add `g_dcg_table[]` registry (mirror of `proc_table`).
      Build: clean. Gates: unchanged.  Commit.

### PJ-2 — lower_pl_predicate skeleton

- [ ] Create `src/lower/lower_pl.c` + `lower_pl.h`.
      Implement `lower_pl_predicate(tree_t *pred)` returning NULL initially
      (placeholder; allows `lower()` to populate `dcg_table[i].ir_body = NULL`
      for now).  Wire `lower()` to call it during proc-table skeleton emission.
      Build: clean. Gates: unchanged.  Commit.

### PJ-3 — SM_BB_ONCE_PROC handler

- [ ] Replace the `[NO-AST]` stub in `sm_interp.c` `case SM_BB_ONCE_PROC` with
      a body handler that:
        (a) looks up `dcg_table[name/arity]`
        (b) if `ir_body != NULL`, wraps in `pl_dcg_state_t`, returns
            `bb_node_t{pl_bb_dcg, dz, 0}`, drives via `bb_broker`
        (c) if `ir_body == NULL`, fall back to legacy path (but legacy path is
            stubbed — so this fails the gate; that's expected until PJ-4+)
      Mirror of `SM_BB_PUMP_PROC` body handler for Icon.
      Build: clean.  smoke_prolog still 0/5 (no IR yet).  Commit.

### PJ-4 — lower_pl_expr_node: write/nl/=/is + simple goals

- [ ] Add `lower_pl_expr_node(IR_block_t *cfg, tree_t *e)` in `lower_pl.c`
      handling:
        TT_FNC for builtin Prolog calls (write, nl)
        TT_UNIFY for `X = Y`
        TT_FNC "is" for arithmetic
        TT_VAR for logical variables
        TT_ILIT / TT_QLIT / TT_NAME for literals
      Wire into `lower_pl_predicate` to build the body IR_SEQ.
      Gate: smoke_prolog write_atom + unify + arith PASS.
      Mirror of recent Icon `lower_icn_expr_node` work (sess 2026-05-15
      Opus 4.7, one4all `c2c20d1a` — IR_IF/IR_EVERY landing).  Commit.

### PJ-5 — IR_PL_CHOICE executor + lower_pl_choice (multi-clause predicates)

- [ ] Implement `IR_PL_CHOICE` executor in `ir_exec.c` using `nd->state`
      as clause index, `nd->counter` as trail position.
      α path: trail_mark, try clause 0.
      β path: trail_unwind to saved position, advance state, try next clause.
      ω: all clauses exhausted.
      Build `lower_pl_choice(IR_t **clauses, int n)` in `lower_pl.c`.
      Gate: smoke_prolog clause PASS.  Commit.

### PJ-6 — IR_PL_CALL executor (recursion)

- [ ] Implement `IR_PL_CALL` executor: look up `dcg_table[name/arity]`,
      build fresh `pl_dcg_state_t`, drive via inner `IR_exec_once`.
      Cut barrier setup: save current choice-point depth so a CUT inside
      the callee can unwind correctly.
      Gate: smoke_prolog recursion PASS.  smoke_prolog 5/5 target reached.  Commit.

### PJ-7 — IR_PL_CUT executor

- [ ] Implement `IR_PL_CUT` executor: discard choice points back to the
      enclosing predicate's barrier.  Mark the surrounding IR_PL_CHOICE
      so β-retry skips past cut clauses.
      Gate: broker tests with `!` PASS.  Commit.

### PJ-8 — delete pl_runtime.c AST-walking paths

- [ ] With smoke_prolog 5/5 and broker covering the cut paths, delete the
      AST-walking call sites in `pl_runtime.c`:
        pl_pred_table_lookup_global → returns NULL for modes 2/3/4
        pl_unified_term_from_expr → mode-1-only (interp_eval gates it)
        interp_exec_pl_builtin → mode-1-only
      The `Pl_PredEntry` table with `tree_t*` becomes mode-1-only.
      Modes 2/3/4 use `g_dcg_table` exclusively.
      Build: clean.  Gates: smoke_prolog 5/5, honest_prolog gate green.  Commit.

---

## Done when

  All `SM_BB_ONCE_PROC` calls route through `pl_bb_dcg` + `dcg_table[i].ir_body`.
  All `pl_bb_build` lazy fallbacks replaced with `pl_bb_dcg` + IR_block_t.
  All inline x86 emitters for Prolog primitives written (mode 4).
  smoke_prolog 5/5.  Broker non-regressive on Prolog tests.
  pl_runtime.c AST-walking deleted for modes 2/3/4 (mode 1 retains it as
  the reference interpreter).
  GATE-1..4 green.

---

## Invariants

1. GATE-1: smoke_prolog PASS=5. Restore before any other work.
2. GATE-2: broker PASS — never regress below committed baseline.
3. GATE-3: any Prolog rung-suite PASS must not decrease.
4. GATE-4: honest PASS must not decrease (cross-language gate).
5. No `DESCR_t foo(void *zeta, int entry)` four-port C BB functions.
   `pl_lazy_box` and `pl_bb_dcg` are infrastructure — keep them.
6. One construct per commit (or small coherent batch).
7. No corpus source modified to work around runtime bugs.
8. Cross-language calls go SM↔SM or BB↔BB, never SM↔BB across languages
   (see absolute banner box at top).

---

## Watermark

  one4all: c2c20d1a  corpus: 1fe096c
  smoke_prolog: 0/5  (all five stub on SM_BB_ONCE_PROC NO-AST)
  Other smokes unchanged: snobol4 7/7, icon 5/5, snocone 5/5, rebus 4/4, raku 5/5.
  honest icon-suite: 277 PASS / 0 FAIL / 0 ABORT.
  broker: 16/49.

  Session 2026-05-15 (Claude Opus 4.7, one4all `c2c20d1a`):
    File created mirroring GOAL-ICON-BB-JCON.md exactly, with Prolog port
    semantics substituted throughout.  The architectural model — SM↔BB
    bridge per language, one IR_block_t per top-level definition (predicate
    here, procedure for Icon), composability by reference via IR_PL_CALL —
    is identical between the two Goals.  The CROSS-LANGUAGE absolute rule
    is reproduced verbatim and listed in the invariants.

    Prereq is GOAL-PROLOG-BB-COMPLETE at one4all `c9b7428d` (PB-8 honest
    111/294 FAIL=0 ABORT=0).  Sister Goal is GOAL-ICON-BB-JCON at one4all
    `c2c20d1a` (smoke_icon 5/5 after IJ-AST-IR-BB-if-every-to closed this
    same session).  This file picks up where PB-8 left off and follows
    the Icon JCON pattern.

  NEXT: PJ-1 — add `pl_bb_dcg` infrastructure bridge and `g_dcg_table[]`
        registry skeleton.  Mirror of Icon `icn_bb_dcg` / `proc_table` in
        every byte — only names change.
