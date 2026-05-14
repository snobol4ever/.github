# GOAL-LOWER-REDESIGN.md — Unified SM+BB Pipeline (ir_node_t / ir_graph_t)

**Repo:** one4all + .github
**Supersedes:** GOAL-ICON-LOWER-REDESIGN.md
**Status:** DESIGN — no code yet

---

## The big picture

SCRIP has six languages. Each has two kinds of computation:

| Language | Normal expressions (scalar) | Goal-directed expressions (generator) |
|----------|-----------------------------|---------------------------------------|
| SNOBOL4  | assignments, arithmetic     | pattern language (PAT_CAT, PAT_ALT, ARB, SPAN…) |
| Snocone  | same as SNOBOL4             | unified — Snocone fixes the split; everything is a generator |
| Rebus    | assignments, arithmetic     | pattern language (like SNOBOL4 but cleaner) |
| Icon     | *everything* is a generator | everything — even `x+1` can fail |
| Prolog   | arithmetic, unification     | clause alternation, choice points, cut |
| Raku     | mostly scalar               | generators exist but rare; mostly tree-shaped |

**The SM (stack machine) drives everything.** It is the spine of execution.
**The BB (brokered-box / ir_graph_t) handles all goal-directed computation.**
Both lands coexist and call into each other seamlessly — including cross-language calls.

---

## Why the current approach was wrong

Today Icon lowers like this:

```
AST → lower.c → SM_BB_EVAL(ast_ptr) → [at runtime] bb_eval_value(tree_t*)
                                                      → icn_bb_build(tree_t*)
```

`lower.c` for Icon is a no-op: every expression becomes `SM_BB_EVAL(ptr)` pointing
back at the live AST. BB graphs are rebuilt from the raw AST **on every call**.
The SM array for Icon carries no semantic content.

The same problem exists for SNOBOL4 patterns: `rt_bb_arb`, `rt_bb_span` etc. build
BB graphs ad-hoc at runtime from C structs, not from a compiled representation.

Prolog choice points (`pl_box_choice`) have the same issue.

**Root cause:** we never had a compile-time generator IR. We deferred all generator
graph construction to runtime, using the raw AST as the IR by accident.

---

## The correct model: SM + BB, two lands, one spine

```
                    ┌─────────────────────────────────────┐
                    │         SM (stack machine)           │
                    │         drives everything            │
                    │                                      │
                    │  SM_PUSH_LIT / SM_ADD / SM_STORE …  │  ← scalar ops
                    │  SM_CALL_FN / SM_RETURN …            │  ← procedure calls
                    │  SM_EXEC_GEN(ir_graph_t*)  ←──────────────── NEW opcode
                    │                   │                  │
                    └───────────────────│──────────────────┘
                                        │ enter BB land
                                        ▼
                    ┌─────────────────────────────────────┐
                    │       BB (ir_graph_t executor)        │
                    │       goal-directed computation      │
                    │                                      │
                    │  ir_node_t graph walk               │
                    │  start / resume / succ / fail ports  │
                    │  produces values → pushed to SM stack│
                    │                                      │
                    │  can call back into SM for scalar    │
                    │  sub-expressions (seamless re-entry) │
                    └─────────────────────────────────────┘
```

`SM_EXEC_GEN(ptr)` replaces `SM_BB_EVAL(ptr)`. The pointer is now a `ir_graph_t*`
(compile-time wired graph) instead of a `tree_t*` (raw AST). This is the only
change visible at the SM level — everything else is internal to the two lands.

---

## The graph structure: directed cyclic graph (DCG)

NOT a DAG. NOT a tree. Back-edges are mandatory for generator semantics:

```
every expr do body:   body.fail  → expr.resume   (back-edge)
while expr do body:   body.fail  → expr.start    (back-edge)
SNOBOL4 PAT_CAT(A,B): B.fail    → A.resume      (back-edge)
SNOBOL4 ARB:          fail       → try-longer    (back-edge)
SNOBOL4 SPAN(c):      fail       → try-shorter   (back-edge)
Prolog A;B:           A.fail     → B.start       (back-edge/alternation)
```

A DAG cannot express backtracking. The graph must be cyclic.
Termination is guaranteed by generator exhaustion: resume → fail when done.

---

## The four-port node: ir_node_t

Language-neutral. Lives in `src/runtime/common/`. Used by all six languages.

```c
/* src/runtime/common/scrip_ir.h */

typedef enum {
    /* ── Universal scalar ── */
    IR_LIT_I,          /* integer literal */
    IR_LIT_S,          /* string literal */
    IR_LIT_F,          /* real literal */
    IR_LIT_NUL,        /* &null / zero */
    IR_VAR,            /* variable read */
    IR_ASSIGN,         /* var := expr */
    IR_AUGOP,          /* var op:= expr */
    IR_BINOP,          /* l op r */
    IR_UNOP,           /* op e */
    IR_CALL,           /* proc(args…) — user or builtin */
    IR_SEQ,            /* stmt ; stmt (sequence) */
    IR_FAIL,           /* always fails */
    IR_SUCCEED,        /* always succeeds, returns &null */
    IR_GOTO,           /* unconditional jump (wired graph only) */
    IR_RETURN,         /* return expr */

    /* ── Universal generators ── */
    IR_ALTERNATE,      /* A | B */
    IR_TO_BY,          /* i to j by k */
    IR_EVERY,          /* every expr do body */
    IR_WHILE,          /* while expr do body */
    IR_LIMIT,          /* expr \ n */
    IR_SUSPEND,        /* suspend expr */
    IR_PROC,           /* procedure root node */

    /* ── Icon / Snocone specific ── */
    IR_SCAN,           /* subj ? body */
    IR_NONNULL,        /* \expr */
    IR_INTERROGATE,    /* /expr */

    /* ── SNOBOL4 / Snocone / Rebus pattern ── */
    IR_PAT_LIT,        /* literal string match */
    IR_PAT_ANY,        /* ANY(cset) */
    IR_PAT_SPAN,       /* SPAN(cset) — back-edge on fail-short */
    IR_PAT_BREAK,      /* BREAK(cset) */
    IR_PAT_ARB,        /* ARB — back-edge on fail-longer */
    IR_PAT_ARBNO,      /* ARBNO(p) */
    IR_PAT_CAT,        /* P1 P2 — B.fail→A.resume back-edge */
    IR_PAT_ALT,        /* P1 | P2 */
    IR_PAT_ASSIGN_IMM, /* P . V */
    IR_PAT_ASSIGN_COND,/* P $ V */
    IR_PAT_POS,        /* POS(n) / RPOS(n) */
    IR_PAT_TAB,        /* TAB(n) / RTAB(n) */
    IR_PAT_REM,        /* REM */
    IR_PAT_FENCE,      /* FENCE */
    IR_PAT_ABORT,      /* ABORT */
    IR_PAT_CALLOUT,    /* *Fn() deferred call */

    /* ── Prolog specific ── */
    IR_PL_CHOICE,      /* clause alternation (choice point) */
    IR_PL_UNIFY,       /* unification */
    IR_PL_CUT,         /* ! */
    IR_PL_CALL,        /* call(Goal) */
} ir_kind_t;

typedef struct ir_node ir_node_t;
struct ir_node {
    ir_kind_t      kind;

    /* Four control ports — NULL until generator phase wires them.
     * port_start  = entry: first evaluation attempt
     * port_resume = backtrack: try next value (NULL means scalar/non-generative)
     * port_succ   = success continuation (value in .value)
     * port_fail   = failure continuation (no value) */
    ir_node_t     *port_start;
    ir_node_t     *port_resume;
    ir_node_t     *port_succ;
    ir_node_t     *port_fail;

    /* Children (pre-wiring tree; becomes DCG after ir_lower_wire()) */
    ir_node_t    **c;
    int             n;

    /* Payload */
    union {
        int64_t     ival;       /* LIT_I, op code for BINOP/UNOP */
        double      dval;       /* LIT_F */
        const char *sval;       /* LIT_S, VAR name, CALL name */
        struct { ir_node_t *l, *r; int op; } binop;
        struct { const char *name; int nargs; } call;
    };

    /* Runtime execution state — live during ir_exec graph walk */
    DESCR_t         value;      /* current result value */
    int64_t         counter;    /* TO_BY position, LIMIT count, etc. */
    int             state;      /* executor state machine (0=fresh) */

    /* Graph bookkeeping */
    int             id;         /* unique within ir_graph_t — set by ir_lower */
    int             generative; /* 1 if port_resume is meaningful */
    int             visited;    /* scratch for traversal algorithms */
    int             lang;       /* which language produced this node */
};

/* A complete wired generator CFG for one procedure or pattern */
typedef struct {
    ir_node_t     *entry;      /* == root->port_start */
    ir_node_t    **all;        /* flat array of all nodes (for reset/GC) */
    int             n;          /* count */
    int             lang;       /* LANG_SNO / LANG_ICN / LANG_PL / etc. */
} ir_graph_t;
```

---

## Wiring rules (generator phase — language-neutral)

The generator phase runs bottom-up after lower produces the node tree.
It wires all four ports. Back-edges create the cycles.

| Node kind       | port_start→     | port_resume→          | port_succ from          | port_fail from         |
|-----------------|-----------------|-----------------------|-------------------------|------------------------|
| LIT/NUL/SUCCEED | self(return v)  | →fail                 | self                    | (never for lit)        |
| VAR             | self(load)      | →fail                 | self(if bound)          | self(if unbound)       |
| FAIL            | →fail           | →fail                 | (never)                 | self                   |
| BINOP(l,r)      | l.start         | →fail (scalar)        | r.succ→compute→succ     | l.fail, r.fail         |
| CALL(args,proc) | args→call.start | call.resume           | call.succ               | call.fail              |
| ALTERNATE(A,B)  | A.start         | A.resume \| B.start   | A.succ, B.succ          | B.fail                 |
| SEQ(a,b)        | a.start         | b.resume              | b.succ                  | a.fail, b.fail         |
| TO_BY           | self(init)      | self(next)            | self(yield each step)   | self(past bound)       |
| EVERY(e,body)   | e.start         | →fail(loop done)      | e.fail(loop exhausted)  | **body.fail→e.resume** |
| WHILE(e,body)   | e.start         | →fail                 | e.fail                  | **body.fail→e.start**  |
| LIMIT(e,n)      | n→e.start       | e.resume(if cnt>0)    | e.succ(cnt--)           | e.fail, cnt==0         |
| SCAN(s,body)    | s.start         | body.resume           | body.succ               | s.fail, **body.fail→s.resume** |
| SUSPEND(e)      | e.start         | self(park/resume)     | self→caller.resume      | e.fail                 |
| PAT_CAT(A,B)    | A.start         | B.resume→A.resume     | B.succ                  | A.fail, **B.fail→A.resume** |
| PAT_ALT(A,B)    | A.start         | A.resume \| B.start   | A.succ, B.succ          | B.fail                 |
| PAT_SPAN(c)     | self(match≥1)   | **self(try-shorter)** | self(yield pos)         | self(len=0)            |
| PAT_ARB         | self(try empty) | **self(try-longer)**  | self(yield pos)         | self(at end)           |
| PAT_ARBNO(p)    | p.start\|succ   | p.resume\|p.start     | p.succ\|self            | p.fail(0 matches ok)   |
| PL_CHOICE(cls…) | cls[0].start    | cls[i+1].start        | cls[i].succ             | last_cls.fail          |
| PL_UNIFY(t1,t2) | self(unify)     | →fail                 | self(if unified)        | self(if clash)         |
| PL_CUT          | self            | →fail                 | self→parent.fail(prune) | (never)                |

**Bold** = back-edges that create cycles in the DCG.

---

## The new SM opcode: SM_EXEC_GEN

Replaces `SM_BB_EVAL`. Operand is a `ir_graph_t*` (compile-time wired graph).

```c
case SM_EXEC_GEN: {
    ir_graph_t *cfg = (ir_graph_t *)ins->a[0].ptr;
    DESCR_t val = ir_exec_once(cfg);   /* drive graph: start→succ or start→fail */
    st->last_ok = !IS_FAIL_fn(val);
    sm_push(st, val);
    break;
}
```

For generative contexts (`every`, `while`) a separate pump opcode drives resume:
```c
case SM_PUMP_GEN: {
    ir_graph_t *cfg = (ir_graph_t *)ins->a[0].ptr;
    /* drives cfg until exhausted, executing body SM block per value */
    ...
}
```

The ir_graph_t executor can call back into SM for scalar sub-expressions:
```c
/* Inside ir_exec — calling a scalar sub-expression */
DESCR_t ir_exec_call_sm(SM_State *st, SM_Program *prog, int entry_pc) {
    /* push a return frame, run SM from entry_pc, pop result */
    /* seamless re-entry — SM and BB share the same value stack */
}
```

---

## Language-by-language pipeline after redesign

### SNOBOL4

```
scalar stmts:   AST → lower_sno.c → SM array (SM_ADD, SM_STORE_VAR…) — UNCHANGED
pattern match:  AST → lower_pat.c → ir_node_t tree → ir_lower_wire() → ir_graph_t
                SM stmt emits SM_EXEC_GEN(cfg) at the pattern-match site
                ir_exec drives the pattern graph; subject position is thread-local state
                on match success → SM continues; on failure → SM branches (GOTO fail-label)
```

SNOBOL4 stays hybrid: SM spine + BB for patterns. This is already the right
model — we just compile the BB part at lower time instead of building it ad-hoc.

### Snocone

```
everything:     AST → lower_sco.c → ir_node_t tree → ir_lower_wire() → ir_graph_t
                SM_EXEC_GEN drives top-level expressions
                scalar sub-expressions fold into IR_BINOP etc. (no SM needed)
```

Snocone is the cleanest — everything is a generator, single path.

### Rebus

```
Test bed for SM+BB hybrid (like SNOBOL4 but simpler syntax):
scalar stmts:   SM array
pattern parts:  ir_node_t / ir_graph_t via SM_EXEC_GEN
Use Rebus to validate the SM↔BB boundary before touching SNOBOL4.
```

### Icon

```
everything:     AST → lower_icn.c → ir_node_t tree → ir_lower_wire() → ir_graph_t
                no SM array for Icon expressions at all
                SM_EXEC_GEN(cfg) is the only Icon opcode emitted per statement
                ir_exec handles the entire expression graph
                scalar ops (IR_BINOP etc.) execute inside ir_exec directly
```

### Prolog

```
goals:          AST → lower_pl.c → ir_node_t tree (IR_PL_CHOICE, IR_PL_UNIFY…)
                → ir_lower_wire() → ir_graph_t
                SM_EXEC_GEN drives goal resolution
                choice points = IR_PL_CHOICE with alternation back-edges
                cut = IR_PL_CUT prunes the choice graph
```

### Raku

```
mostly scalar:  AST → lower_rku.c → SM array (as today)
generators:     ir_node_t for lazy lists, gather/take, etc.
                SM_EXEC_GEN where needed
```

---

## Cross-language calls

When SNOBOL4 calls an Icon proc, or Prolog calls a SNOBOL4 pattern:

```
SM (SNOBOL4 context)
  │  SM_CALL_FN "icon_proc"
  │
  └─→ ir_exec(icon_proc_cfg)       ← enters BB land with Icon ir_graph_t
          │  IR_CALL → "sno_builtin"
          └─→ SM sub-call            ← back into SM land for SNOBOL4 scalar
                  │  returns DESCR_t
          ←───────┘                  ← returns to BB land
      ir_exec continues
  ←───┘                              ← returns to SM land
SM continues
```

The DESCR_t value type is shared. SM stack is shared. The only boundary is
which executor (SM interp vs ir_exec graph walker) is currently active.
The `g_lang` flag is NOT needed for dispatch — the ir_graph_t carries its
own `lang` field and the ir_exec handles all kinds uniformly.

---

## Migration plan — incremental, never breaking

### Phase 0: Infrastructure (no behavior change)

**LR-0** — Define ir_node_t, ir_graph_t, ir_kind_t
- New: `src/runtime/common/scrip_ir.h` + `scrip_ir.c`
- alloc, free, print, reset
- No lowering changes. All gates pass. Commit.

**LR-1** — Generator phase: ir_lower_wire()
- New: `src/runtime/common/ir_lower.h` + `ir_lower.c`
- Input: ir_node_t tree. Output: all four ports wired → ir_graph_t.
- Standalone unit test only. All gates pass. Commit.

**LR-2** — ir_exec: graph-walk executor
- New: `src/runtime/common/ir_exec.h` + `ir_exec.c`
- ir_exec_once(ir_graph_t*) → DESCR_t
- ir_exec_pump(ir_graph_t*, body_fn) → int ticks
- Standalone unit test: `scripts/test_ir_exec_unit.sh`. All gates pass. Commit.

**LR-3** — Add SM_EXEC_GEN opcode (dead — nothing emits it yet)
- sm_prog.h: add SM_EXEC_GEN, SM_PUMP_GEN
- sm_interp.c: add handler (calls ir_exec_once / ir_exec_pump)
- sm_jit_interp.c: same
- No lower.c changes. All gates pass. Commit.

### Phase 1: Rebus as test bed for SM+BB hybrid

**LR-4** — Rebus lower: emit ir_node_t alongside existing path (additive)
- lower_rebus.c: for pattern nodes, also build ir_node_t tree + wire + cache ir_graph_t
- SM_EXEC_GEN path activated for Rebus patterns
- Fallback to old path if ir_graph_t absent
- GATE: smoke_rebus pass. Commit.

**LR-5** — Rebus: delete old pattern BB, use ir_graph_t only
- Remove old Rebus ad-hoc BB pattern code
- GATE: smoke_rebus pass. Commit.

### Phase 2: Icon migration

**LR-6** — Icon lower: emit ir_node_t alongside SM_BB_EVAL (additive)
- lower.c: LANG_ICN path builds ir_node_t tree + wire → ir_graph_t per expression
- SM_BB_EVAL handler: if ir_graph_t present → ir_exec; else → icn_bb_build fallback
- GATE-1..4 unchanged. Commit.

**LR-7** — Icon: delete SM_BB_EVAL, every_table, ICN_BB_EVAL, icn_bb_build
- SM_BB_EVAL opcode removed. every_table deleted. ICN_BB_EVAL macro deleted.
- icn_bb_build, bb_eval_value, icn_bb_scan_gen, icn_bb_fnc — all deleted.
- Icon lower emits ir_node_t only. SM_EXEC_GEN is the only Icon opcode.
- GATE-1..4 must pass. Commit.

### Phase 3: SNOBOL4 pattern migration

**LR-8** — SNOBOL4 pattern lower: emit ir_node_t alongside bb_node_t (additive)
- lower_pat.c / rt.c: IR_PAT_* nodes built at compile time
- SM_EXEC_GEN drives pattern match; SM continues on match result
- Fallback to old bb_node_t path if ir_graph_t absent
- GATE: smoke_snobol4 + beauty 195/195. Commit.

**LR-9** — SNOBOL4: delete ad-hoc bb_node_t pattern runtime
- Remove rt_bb_arb, rt_bb_span, rt_bb_arbno, etc.
- ir_exec handles all SNOBOL4 pattern matching.
- GATE: smoke_snobol4 + beauty 195/195. Commit.

### Phase 4: Prolog migration

**LR-10** — Prolog lower: emit ir_node_t for goals (additive)
- lower_prolog.c: IR_PL_CHOICE, IR_PL_UNIFY nodes
- SM_EXEC_GEN drives goal resolution
- Fallback to pl_box_choice if ir_graph_t absent
- GATE: smoke_prolog + broker. Commit.

**LR-11** — Prolog: delete pl_box_choice ad-hoc BB
- ir_exec handles all Prolog goal resolution.
- GATE: smoke_prolog + broker. Commit.

### Phase 5: Snocone migration

**LR-12** — Snocone: emit ir_node_t for all expressions
- lower_sco.c: all Snocone expressions → ir_node_t
- GATE: smoke_snocone. Commit.

### Phase 6: Mode-3 / Mode-4 JIT

**LR-13** — Mode-3 JIT: emit x86 from ir_graph_t nodes
- bb_flat.c / emit_bb.c: walk ir_graph_t instead of tree_t*
- Each ir_kind_t maps to x86 emission
- GATE: --jit-run ≥ --sm-run PASS counts. Commit.

**LR-14** — Mode-4 JIT: stateful x86 from ir_graph_t
- GATE: mode-4 parity with mode-3. Commit.

### Phase 7: Cleanup

**LR-15** — Delete NO_AST_WALK_GUARD, g_sm_dispatch_active, g_ast_pump_active
- Dead code after LR-7. SM_EXEC_GEN is the only BB entry point.
- Commit.

**LR-16** — Raku: migrate generators to ir_node_t
- gather/take, lazy lists, etc.
- GATE: smoke_raku. Commit.

---

## What does NOT change

- `tree_t` (AST): unchanged — all parsers produce tree_t, always.
- `DESCR_t`: unchanged — shared value type across SM and BB.
- SM array for SNOBOL4 scalars: unchanged.
- All test scripts and gate commands: unchanged.
- `bb_node_t` / `bb_broker`: retained for SNOBOL4 patterns during transition;
  deleted after LR-9.

---

## Files summary

### New (src/runtime/common/)
```
scrip_ir.h / scrip_ir.c     — ir_node_t, ir_graph_t, ir_kind_t
ir_lower.h / ir_lower.c   — ir_lower_wire() — wiring pass
ir_exec.h / ir_exec.c     — ir_exec_once(), ir_exec_pump()
```

### Modified
```
sm_prog.h                   — add SM_EXEC_GEN, SM_PUMP_GEN
sm_interp.c                 — add SM_EXEC_GEN handler
sm_jit_interp.c             — add SM_EXEC_GEN handler
lower.c                     — Icon: emit ir_node_t; SNOBOL4 pat: emit IR_PAT_*
lower_rebus.c               — emit IR_PAT_* for patterns
lower_prolog.c              — emit IR_PL_CHOICE / IR_PL_UNIFY
```

### Deleted (incrementally, per step)
```
LR-7:  SM_BB_EVAL opcode, every_table_*, ICN_BB_EVAL macro
       icn_bb_build, bb_eval_value, icn_bb_scan_gen, icn_bb_fnc
LR-9:  rt_bb_arb, rt_bb_span, rt_bb_arbno, rt_bb_any, rt_bb_break
       ad-hoc snobol4_pattern.c bb_node_t construction
LR-11: pl_box_choice, pl_box_fail ad-hoc BB
LR-15: NO_AST_WALK_GUARD, g_sm_dispatch_active, g_ast_pump_active
```

---

## Gates summary

  LR-0..3:   all existing gates pass (additive infrastructure)
  LR-4..5:   smoke_rebus (Rebus test bed)
  LR-6:      GATE-1..4 unchanged (Icon additive)
  LR-7:      GATE-1..4 pass (Icon clean break — SM_BB_EVAL deleted)
  LR-8:      smoke_snobol4 + beauty 195/195 (SNOBOL4 patterns additive)
  LR-9:      smoke_snobol4 + beauty 195/195 (ad-hoc pattern runtime deleted)
  LR-10:     smoke_prolog + broker (Prolog additive)
  LR-11:     smoke_prolog + broker (Prolog clean break)
  LR-12:     smoke_snocone
  LR-13:     --jit-run >= --sm-run PASS counts
  LR-14:     mode-4 parity with mode-3
  LR-15:     all gates (cleanup — no behavior change)
  LR-16:     smoke_raku

---

## Key design decisions captured

1. **DCG not DAG**: back-edges are mandatory for every/while/SPAN/ARB/choice-points.
   The executor terminates via generator exhaustion (resume→fail), not acyclicity.

2. **SM is the spine**: SM_EXEC_GEN is one opcode. The SM drives sequencing,
   procedure calls, variable storage. BB handles only goal-directed sub-computation.

3. **ir_node_t is language-neutral**: IR_PAT_*, IR_PL_*, IR_EVERY etc. are
   all kinds of the same struct. One allocator, one phase, one executor.

4. **Rebus as test bed**: validate SM+BB hybrid boundary on a smaller language
   before touching SNOBOL4. Rebus patterns are simpler but structurally identical.

5. **Cross-language calls are seamless**: ir_graph_t carries its own lang field.
   ir_exec handles IR_CALL by looking up the target proc's ir_graph_t or SM block.
   DESCR_t and the SM value stack are shared across both lands.

6. **Incremental — never break**: each step is additive with fallback until
   the clean break step explicitly deletes the old path. Gates must pass at
   every commit.

7. **Snocone is the purest**: everything is a generator, single path, no hybrid.
   The cleanest validation of the new pipeline before Milestone 2 (self-hosting).

---

## Watermark

  one4all: f1dbb78b  .github: cb23fc50
  Status: DESIGN — no code yet
  NEXT: LR-0 — define ir_node_t in src/runtime/common/scrip_ir.h

---

## PIVOT: Start with SNOBOL4 patterns (not Icon, not Rebus)

**Revised migration order:** SNOBOL4 patterns first.

### Why SNOBOL4 patterns are the perfect first target

1. **Self-contained BB land.** Patterns are completely separable from scalar SNOBOL4.
   SM array for scalars is untouched. The only change: pattern match site emits
   `SM_EXEC_GEN(ir_graph_t*)` instead of building bb_node_t ad-hoc at runtime.

2. **Clearest SM↔BB boundary.** One entry (`SM_EXEC_GEN`), one exit (match
   success/failure returned to SM). This is the two-as-one theory in its simplest form.

3. **Best oracle.** beauty.sno — Milestone 1 locked at md5 `abfd19a7a834484a96e824851caee159`.
   If beauty passes byte-identical after replacing ad-hoc BB with ir_graph_t, the
   design is validated on a real 646-line program with ARB, SPAN, alternation, ARBNO.

4. **No Icon disruption.** Icon stays exactly as-is (SM_BB_EVAL / icn_bb_build)
   during the entire SNOBOL4 pattern migration. Don't touch Icon until LR-S is done.

### Revised step order

**LR-0..3: Infrastructure** (unchanged — ir_node_t, ir_lower, ir_exec, SM_EXEC_GEN)

**LR-S1 — SNOBOL4 pattern lower: emit ir_node_t (additive)**
- lower_pat path: for each pattern constructor, build IR_PAT_* nodes + wire + ir_graph_t
- SM_EXEC_GEN path activated at the pattern-match site
- Old bb_node_t path kept as fallback
- GATE: smoke_snobol4 pass + beauty 195/195. Commit.

**LR-S2 — SNOBOL4: delete ad-hoc bb_node_t pattern runtime (clean break)**
- Remove rt_bb_arb, rt_bb_span, rt_bb_arbno, rt_bb_any, rt_bb_break
- Remove ad-hoc bb_node_t construction in snobol4_pattern.c
- ir_exec handles all SNOBOL4 pattern matching via IR_PAT_* nodes
- GATE: smoke_snobol4 + beauty 195/195. Commit.

**LR-S3 — Cross-check: Snocone and Rebus patterns still pass**
- Snocone and Rebus pattern matching also routes through ir_exec (same IR_PAT_* nodes)
- GATE: smoke_snocone + smoke_rebus. Commit.

**Then proceed to Icon (LR-6..7), Prolog (LR-10..11), etc. as originally planned.**

### Naming fix

`ir_graph_t` renamed to `ir_graph_t` throughout — "CFG" is overloaded
(Control-Flow Graph AND Context-Free Grammar in parsing contexts).
`ir_graph_t` is unambiguous: a generator directed cyclic graph.

---

## CLARIFICATION: No separate generator phase — lower wires directly

A tree is a subset of a DCG (no back-edges, one parent per node).
lower.c produces a ir_graph_t (DCG) in ONE pass — the wiring of
port_start/resume/succ/fail happens during lowering, not in a separate phase.

```
Parser → tree_t (pure tree) → lower → ir_graph_t (DCG) → ir_exec / emit
```

The "generator phase" described earlier is WRONG as a separate pass.
Fold it into lower: each lower_* function builds its ir_node_t AND wires
its four ports using the already-wired children. Bottom-up, one pass.

The SM array is NOT a separate IR — it is one possible serialization of the
acyclic (tree-shaped) portions of the ir_graph_t. SNOBOL4 scalars happen
to produce acyclic ir_graph_t subgraphs that can be serialized as SM instructions.
SNOBOL4 patterns and all Icon expressions produce cyclic subgraphs — these
cannot be serialized as flat SM arrays, so ir_exec drives them directly.

SM_EXEC_GEN is the handoff: SM array execution hits SM_EXEC_GEN(ir_graph_t*)
and transfers to ir_exec for the cyclic subgraph. On return (succ or fail),
SM array execution resumes.

Delete LR-1 (ir_lower.c) from the step list — it does not exist.
lower.c IS the generator phase.

---

## FINAL PIPELINE (canonical)

```
Parser
  │
  ▼
AST (tree_t)          — pure tree, language-specific, unchanged
  │
  ▼
lower                 — one pass, bottom-up, wires DCG as it goes
  │
  ▼
DCG (ir_graph_t)     — directed cyclic graph, language-neutral
  │                     tree-shaped subgraphs: scalar expressions
  │                     cyclic subgraphs: patterns, generators, choice points
  │
  ├──▶ SM emitter     — walks acyclic subgraphs → SM array
  │         │            cyclic subgraphs → SM_EXEC_GEN(ir_graph_t* subgraph)
  │         ▼
  │       SM array → sm_interp (--sm-run)
  │                → JIT mode-3 x86 emission (--jit-run)
  │                → JIT mode-4 stateful x86 (--mode4-run)
  │
  └──▶ BB emitter     — walks cyclic subgraphs → ir_graph_t execution nodes
            │            (for --ir-run: ir_exec drives the graph directly)
            ▼
          BB graph  → ir_exec (--ir-run)
                    → JIT x86 direct from DCG nodes
```

**Per language:**

| Language | SM emitter        | BB emitter                     |
|----------|-------------------|-------------------------------|
| SNOBOL4  | scalar stmts ✓    | patterns (IR_PAT_*)           |
| Snocone  | nothing           | everything                     |
| Rebus    | scalar stmts ✓    | patterns (IR_PAT_*)           |
| Icon     | nothing (or stub) | everything (IR_EVERY etc.)    |
| Prolog   | nothing           | goals (IR_PL_CHOICE etc.)     |
| Raku     | scalar stmts ✓    | generators (subset)            |

**Terms dropped:**
- "generator phase" — never existed; lower wires the DCG directly
- "generator IR" — the DCG is just the DCG; no special name for a phase
- SM array as primary IR — it is now a derived emission from the DCG

**The DCG is the IR. Lower produces it. Everything fans out from it.**
