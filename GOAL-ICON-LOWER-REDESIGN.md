# GOAL-ICON-LOWER-REDESIGN.md — Icon lower pass redesign

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

**Repo:** one4all + .github
**Prereq:** GOAL-ICON-BB-JCON (ir-run target met), GOAL-ICON-BB-NATIVE ✅

---

## The problem

Today's Icon pipeline is architecturally wrong:

```
AST → lower.c → SM array of SM_BB_EVAL(ast_ptr) tokens
                        │
                        ▼ (at --sm-run time, on every call)
                   bb_eval_value(tree_t*) — re-walks raw AST
                   icn_bb_build(tree_t*)  — builds BB closures at runtime
```

`lower.c` for Icon is a no-op: every expression becomes `SM_BB_EVAL(ptr)`
pointing back at the live AST. The AST IS the IR. BB graphs are rebuilt from
scratch on every execution. The SM array for Icon carries no semantic content.

This causes:
- Correctness confusion: fixing bugs in bb_eval_value/icn_bb_build means fixing
  an AST interpreter, not a compiled representation
- Mode-4 JIT for Icon is also wrong: it emits x86 from SM_BB_EVAL tokens that
  just call back into the AST walker
- The every_table (AST pointer side-table) must be kept alive for program lifetime
- Cannot cache, cannot optimize, cannot serialize the compiled form

---

## The correct pipeline (JCON-informed)

```
Parser
  │
  ▼
AST (tree_t — unchanged)
  │
  ▼
lower_icon.c        — produces ICN_IR node tree (one node per AST node)
  │
  ▼
generator phase     — wires the four control ports (NEW PASS)
  │                   produces fully-connected directed cyclic graph (ICN_CFG)
  ▼
codegen
  ├─▶ SNOBOL4: SM array (unchanged)
  └─▶ Icon:    ICN_CFG (no SM array)
        ├─▶ --ir-run / --sm-run: graph-walk executor
        ├─▶ --jit-run (mode-3):  x86 emission from ICN_CFG nodes
        └─▶ mode-4:              stateful x86 from ICN_CFG
```

---

## Graph theory

JCON's IR (and our ICN_CFG) is a **directed cyclic graph** — not a DAG, not a tree.

Cycles are inherent to Icon semantics:
- `every expr do body`: body.failure → expr.resume  (back-edge)
- `while expr do body`: body.failure → expr.start   (back-edge)
- `suspend` inside a proc: success → caller_resume → resume (cross-proc cycle)

The four-port model (from JCON's irgen.icn):

```
         ┌─────────────────────┐
start ──▶│                     │──▶ success  (produced a value)
         │   icn_ir_node_t     │
resume──▶│                     │──▶ failure  (exhausted)
         └─────────────────────┘
```

Every Icon expression has all four ports. Scalars: resume→failure always.
Generators: resume→success(next value) until exhausted→failure.

---

## New struct: icn_ir_node_t

```c
typedef enum {
    ICN_IR_LIT_I, ICN_IR_LIT_S, ICN_IR_LIT_F, ICN_IR_LIT_NUL,
    ICN_IR_VAR, ICN_IR_ASSIGN, ICN_IR_AUGOP,
    ICN_IR_BINOP, ICN_IR_UNOP,
    ICN_IR_CALL,                    /* user proc or builtin */
    ICN_IR_ALTERNATE,               /* A | B */
    ICN_IR_TO_BY,                   /* i to j by k */
    ICN_IR_EVERY,                   /* every expr do body */
    ICN_IR_WHILE,                   /* while expr do body */
    ICN_IR_LIMIT,                   /* expr \ n */
    ICN_IR_SCAN,                    /* subj ? body */
    ICN_IR_SUSPEND,
    ICN_IR_RETURN,
    ICN_IR_FAIL,
    ICN_IR_PROC,                    /* procedure root */
    ICN_IR_SEQ,                     /* stmt ; stmt */
    ICN_IR_GOTO,                    /* unconditional jump (wired graph) */
} icn_ir_kind_t;

typedef struct icn_ir_node icn_ir_node_t;
struct icn_ir_node {
    icn_ir_kind_t   kind;

    /* Four control ports — NULL until generator phase wires them */
    icn_ir_node_t  *port_start;     /* entry */
    icn_ir_node_t  *port_resume;    /* backtrack entry (NULL = not generative) */
    icn_ir_node_t  *port_succ;      /* success continuation */
    icn_ir_node_t  *port_fail;      /* failure continuation */

    /* Children (pre-wiring tree structure) */
    icn_ir_node_t **c;
    int             n;

    /* Payload */
    union {
        int64_t     ival;           /* ICN_IR_LIT_I */
        double      dval;           /* ICN_IR_LIT_F */
        const char *sval;           /* ICN_IR_LIT_S, VAR, CALL name */
        int         op;             /* BINOP/UNOP operator code */
    };

    /* Runtime value slot — filled by executor during graph walk */
    DESCR_t         value;

    /* Graph bookkeeping */
    int             id;             /* unique node id (set by generator phase) */
    int             visited;        /* traversal flag */
    int             generative;     /* 1 if resume port is meaningful */
};
```

---

## Generator phase — wiring rules

Bottom-up pass after lower produces the node tree. Wires four ports per node:

| Node kind     | start→         | resume→        | succ wires from      | fail wires from    |
|---------------|----------------|----------------|----------------------|--------------------|
| LIT/VAR/NUL   | self (compute) | →failure       | self after compute   | start if fail      |
| BINOP(l,r)    | l.start        | r.resume→l.resume | r.succ(compute)  | l.fail, r.fail     |
| ALTERNATE(A,B)| A.start        | A.resume or B.start | A.succ, B.succ  | B.fail             |
| TO_BY         | self(init)     | self(next)     | self each step       | self(exhausted)    |
| EVERY(e,body) | e.start        | →failure(done) | e.fail (loop done)   | **body.fail→e.resume** (back-edge) |
| WHILE(e,body) | e.start        | →failure       | e.fail               | **body.fail→e.start** (back-edge)  |
| LIMIT(e,n)    | n.start→e.start| e.resume       | e.succ (count--)     | e.fail, count=0    |
| SCAN(s,body)  | s.start        | body.resume→s.resume | body.succ     | s.fail, body.fail→s.resume |
| SEQ(a,b)      | a.start        | b.resume       | b.succ               | a.fail, b.fail     |
| CALL(proc,args)| args→call     | call.resume    | call.succ            | call.fail          |
| SUSPEND(e)    | e.start        | self(park)     | self (caller drives) | e.fail             |
| RETURN(e)     | e.start        | →failure       | e.succ→proc.succ     | e.fail             |

---

## Migration steps

### IL-0 — Define icn_ir_node_t; allocator; printer (no behavior change)

- New file: `src/runtime/interp/icn_ir.h` — struct + kind enum + macros
- New file: `src/runtime/interp/icn_ir.c` — `icn_ir_alloc()`, `icn_ir_print()`
- No lowering changes. No gate impact.
- Commit.

### IL-1 — lower_icon: produce icn_ir_node_t tree alongside SM_BB_EVAL

- `lower.c`: when `g_lang == LANG_ICN`, after emitting `SM_BB_EVAL`, ALSO build
  `icn_ir_node_t` tree and attach to the `every_table` entry alongside the `tree_t*`.
- Keep existing path fully working — this is additive.
- GATE-1..4 unchanged. Commit.

### IL-2 — generator phase: wire four ports

- New file: `src/runtime/interp/icn_ir_gen.c` — `icn_ir_wire(icn_ir_node_t *proc)`
- Implements wiring rules table above. Bottom-up recursion.
- Called after `lower_icon` builds the tree (IL-1).
- Add `--dump-icn-ir` flag to print the wired CFG.
- No execution path changed yet. GATE-1..4 unchanged. Commit.

### IL-3 — executor: walk ICN_CFG instead of icn_bb_build(tree_t*)

- New file: `src/runtime/interp/icn_ir_exec.c` — `icn_ir_exec(icn_ir_node_t *start)`
  Graph-walk executor: follows port_start, port_resume, port_succ, port_fail.
  Returns DESCR_t. Replaces `bb_eval_value(tree_t*)` call site in SM_BB_EVAL handler.
- SM_BB_EVAL handler: if wired icn_ir_node_t exists, use icn_ir_exec; else fall back.
- GATE-3 ir-run must not regress. Commit.

### IL-4 — delete SM_BB_EVAL, every_table, ICN_BB_EVAL macro for Icon

- Remove `ICN_BB_EVAL(t)` intercepts from lower.c.
- lower_icon now ONLY builds icn_ir_node_t (no SM emissions for Icon expressions).
- Delete `every_table_register`, `every_table_lookup`, `every_table_reset`.
- Delete `SM_BB_EVAL` opcode from sm_prog.h and sm_interp.c handler.
- Delete `ICN_BB_EVAL` macro from lower.c.
- GATE-1..4 must all pass. This is the clean break. Commit.

### IL-5 — delete icn_bb_build / bb_eval_value / icn_runtime AST walker

- `icn_bb_build(tree_t*)` goes away — replaced by icn_ir_exec(icn_ir_node_t*).
- `bb_eval_value(tree_t*)` goes away — callers use icn_ir_exec.
- `icn_runtime.c` generator-build functions (`icn_bb_fnc`, `icn_bb_scan_gen`, etc.)
  go away — replaced by icn_ir_gen.c wiring.
- `NO_AST_WALK_GUARD` macro becomes `assert(0)` — dead code detector.
- GATE-1..4. This is the payoff. Commit.

### IL-6 — mode-3 JIT emits x86 from ICN_CFG directly

- `emit_bb.c` / `bb_flat.c`: instead of walking `tree_t*` via bb_boxes,
  walk `icn_ir_node_t*` nodes directly.
- Each ICN_IR kind maps to an x86 emission function.
- GATE: `--jit-run` ≥ `--sm-run` PASS counts. Commit.

---

## What does NOT change

- SNOBOL4 pipeline: unchanged. lower.c → SM array → sm_interp. Patterns → BB graphs at match time.
- Prolog pipeline: unchanged (separate lower_prolog).
- Raku/Rebus/Snocone: unchanged.
- `tree_t` (AST): unchanged — still produced by all parsers.
- `bb_node_t` / `bb_broker`: kept for SNOBOL4 patterns and Prolog.
- All test scripts, gate commands: unchanged.

---

## Why not a DAG?

`every` and `while` create back-edges (body.fail → generator.resume/start).
`suspend` inside a recursive proc creates cross-proc cycles.
A true DAG would require unrolling loops — not feasible for arbitrary generators.
The graph must be cyclic. The executor handles cycles via the resume port protocol:
follow port_start once, then port_resume on each backtrack. Cycles are bounded
by generator exhaustion (resume → port_fail when done).

---

## Gates

  IL-0..3: additive — GATE-1..4 unchanged throughout
  IL-4:    GATE-1..4 must pass (clean break — SM_BB_EVAL deleted)
  IL-5:    GATE-1..4 must pass (AST walker deleted)
  IL-6:    --jit-run >= --sm-run PASS counts

---

## Watermark

  one4all: f1dbb78b  .github: 8c7ec8ff
  Status: DESIGN — no code yet
  NEXT: IL-0 — define icn_ir_node_t, allocator, printer
