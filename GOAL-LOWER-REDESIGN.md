# GOAL-LOWER-REDESIGN.md — Universal generator IR (gen_node_t / gen_cfg_t)

**Repo:** one4all + .github
**Supersedes:** GOAL-ICON-LOWER-REDESIGN.md (Icon-only framing was too narrow)

---

## The insight

SNOBOL4 is two languages in one:
- The **scalar lang**: assignments, arithmetic, string ops — SM array is correct here
- The **pattern lang**: `PAT1 PAT2`, `A | B`, `SPAN(L)`, `ARB` — these ARE generators

Icon is entirely generators — even `x + 1` can fail.
Snocone unifies both sides — everything is a generator.
Prolog unification and choice points are the same four-port protocol.

**The four-port generator protocol is universal across all SCRIP languages.**
It should have one implementation, language-neutral, used everywhere.

---

## The current problem

Today's pipeline for each language:

```
SNOBOL4: AST → lower.c → SM array (scalars ✓) + ad-hoc BB pattern runtime (kludge)
Icon:    AST → lower.c → SM_BB_EVAL tokens → bb_eval_value(tree_t*) at runtime (kludge)
Prolog:  AST → lower.c → SM + pl_box_choice ad-hoc (kludge)
```

Pattern matching, Icon generators, and Prolog choice points all implement
the same four-port graph — but each has its own ad-hoc runtime representation.

---

## The correct universal IR

### Graph structure: directed cyclic graph (DCG)

NOT a DAG, NOT a tree. Back-edges are mandatory:
- `every expr do body`: `body.fail → expr.resume`  (back-edge)
- `while expr do body`: `body.fail → expr.start`   (back-edge)
- SNOBOL4 `ARB`: `fail → try-one-more-char`        (back-edge)
- SNOBOL4 `SPAN(c)`: `fail → try-shorter-match`    (back-edge)
- Prolog `A ; B`: `A.fail → B.start`               (alternation)

The graph must be cyclic. The executor handles cycles via the resume port:
follow start once, then resume on each backtrack. Termination guaranteed by
generator exhaustion (resume → fail when done).

### The four-port node: gen_node_t

```c
typedef enum {
    /* Universal */
    GEN_LIT_I, GEN_LIT_S, GEN_LIT_F, GEN_LIT_NUL,
    GEN_VAR, GEN_ASSIGN, GEN_AUGOP,
    GEN_BINOP, GEN_UNOP,
    GEN_CALL,
    GEN_ALTERNATE,          /* A | B — try A, on fail try B */
    GEN_SEQ,                /* A then B (A must succeed) */
    GEN_FAIL,               /* always fails */
    GEN_SUCCEED,            /* always succeeds */
    GEN_GOTO,               /* unconditional jump (wired graph) */

    /* Generator-specific */
    GEN_TO_BY,              /* i to j by k */
    GEN_EVERY,              /* every expr do body */
    GEN_WHILE,              /* while expr do body */
    GEN_LIMIT,              /* expr \ n */
    GEN_SCAN,               /* subj ? body */
    GEN_SUSPEND,
    GEN_RETURN,
    GEN_PROC,               /* procedure root */

    /* SNOBOL4 pattern-specific */
    GEN_PAT_LIT,            /* literal string match */
    GEN_PAT_ANY,            /* ANY(cset) */
    GEN_PAT_SPAN,           /* SPAN(cset) — back-edge on fail */
    GEN_PAT_BREAK,          /* BREAK(cset) */
    GEN_PAT_ARB,            /* ARB — back-edge on fail */
    GEN_PAT_ARBNO,          /* ARBNO(p) */
    GEN_PAT_CAT,            /* P1 P2 — concatenation */
    GEN_PAT_ALT,            /* P1 | P2 — alternation */
    GEN_PAT_ASSIGN,         /* P . V / P $ V */
    GEN_PAT_POS,            /* POS(n) / RPOS(n) */
    GEN_PAT_TAB,            /* TAB(n) / RTAB(n) */
    GEN_PAT_REM,            /* REM */
    GEN_PAT_FENCE,          /* FENCE */
    GEN_PAT_ABORT,          /* ABORT */

    /* Prolog-specific */
    GEN_PL_CHOICE,          /* clause alternation */
    GEN_PL_UNIFY,           /* unification */
    GEN_PL_CUT,             /* ! */
} gen_kind_t;

typedef struct gen_node gen_node_t;
struct gen_node {
    gen_kind_t      kind;

    /* Four control ports — NULL until generator phase wires them */
    gen_node_t     *port_start;     /* entry: first evaluation */
    gen_node_t     *port_resume;    /* backtrack: try next value (NULL = scalar) */
    gen_node_t     *port_succ;      /* success: produced a value */
    gen_node_t     *port_fail;      /* failure: exhausted */

    /* Children (pre-wiring tree — becomes graph after wiring) */
    gen_node_t    **c;
    int             n;

    /* Payload */
    union {
        int64_t     ival;           /* GEN_LIT_I, GEN_BINOP op code */
        double      dval;           /* GEN_LIT_F */
        const char *sval;           /* GEN_LIT_S, GEN_VAR name, GEN_CALL name */
    };

    /* Runtime */
    DESCR_t         value;          /* result slot, filled by executor */
    int64_t         counter;        /* TO_BY current, LIMIT remaining, etc. */

    /* Graph bookkeeping */
    int             id;             /* unique node id — set by generator phase */
    int             generative;     /* 1 if port_resume is meaningful */
    int             visited;        /* traversal scratch */
};

/* A complete wired generator CFG for one procedure */
typedef struct {
    gen_node_t     *entry;          /* port_start of the root node */
    gen_node_t    **nodes;          /* all nodes (for GC / serialization) */
    int             n_nodes;
} gen_cfg_t;
```

---

## Wiring rules (generator phase)

| Node kind     | port_start→    | port_resume→   | port_succ from       | port_fail from     |
|---------------|----------------|----------------|----------------------|--------------------|
| LIT/NUL       | self(return v) | →fail          | self                 | (never)            |
| VAR           | self(load)     | →fail          | self (if bound)      | self (if unbound)  |
| BINOP(l,r)    | l.start        | →fail (scalar) | r.succ→compute→succ  | l.fail, r.fail     |
| ALTERNATE(A,B)| A.start        | A.resume\|B.start | A.succ, B.succ    | B.fail             |
| TO_BY         | self(init)     | self(increment)| self(yield)          | self(exhausted)    |
| EVERY(e,b)    | e.start        | →fail(done)    | e.fail               | **b.fail→e.resume**|
| WHILE(e,b)    | e.start        | →fail          | e.fail               | **b.fail→e.start** |
| SCAN(s,b)     | s.start        | b.resume       | b.succ               | s.fail             |
| PAT_CAT(A,B)  | A.start        | B.resume→A.resume | B.succ            | A.fail, **B.fail→A.resume** |
| PAT_ALT(A,B)  | A.start        | A.resume\|B.start | A.succ, B.succ    | B.fail             |
| PAT_SPAN(c)   | self(match1)   | **self(try-shorter)** | self(yield)   | self(len=0)        |
| PAT_ARB       | self(try-empty)| **self(try-longer)** | self(yield)    | self(at-end)       |
| PL_CHOICE(clauses) | clause[0].start | next clause | clause[i].succ  | last.fail          |

Back-edges marked **bold** — these create the cycles in the DCG.

---

## New pipeline per language

### SNOBOL4

```
scalar stmt:  AST → SM array (unchanged — SM_ADD, SM_STORE_VAR etc.)
pattern:      AST → gen_node_t tree → generator phase → gen_cfg_t
              replaces: ad-hoc bb_node_t pattern runtime (rt.c, snobol4_pattern.c)
```

Pattern executor = gen_cfg_t walker. Subject position advances via GEN_PAT_* nodes.
Same executor as Icon — different node kinds, same four-port protocol.

### Icon

```
everything:   AST → gen_node_t tree → generator phase → gen_cfg_t
              no SM array for Icon at all
              replaces: SM_BB_EVAL / every_table / bb_eval_value / icn_bb_build
```

### Snocone

```
everything:   AST → gen_node_t tree → generator phase → gen_cfg_t
              (Snocone unifies pattern and expression — single path)
```

### Prolog

```
goals:        AST → gen_node_t tree → generator phase → gen_cfg_t
              GEN_PL_CHOICE implements clause alternation with back-edges
              replaces: pl_box_choice ad-hoc BB runtime
```

### Raku / Rebus

```
generators:   AST → gen_node_t (subset of kinds)
scalars:      SM array
```

---

## Files

### New
- `src/runtime/common/gen_node.h`   — gen_node_t, gen_cfg_t, gen_kind_t
- `src/runtime/common/gen_node.c`   — alloc, free, print
- `src/runtime/common/gen_phase.h`  — generator phase API
- `src/runtime/common/gen_phase.c`  — wiring pass (language-neutral)
- `src/runtime/common/gen_exec.h`   — executor API
- `src/runtime/common/gen_exec.c`   — gen_cfg_t graph-walk executor

### Modified
- `src/runtime/x86/lower.c`         — Icon: emit gen_node_t; SNOBOL4 patterns: emit gen_node_t
- `src/runtime/interp/icn_runtime.c` — remove icn_bb_build, icn_bb_fnc, etc.
- `src/runtime/interp/icn_value.c`  — remove bb_eval_value
- `src/runtime/x86/sm_interp.c`     — remove SM_BB_EVAL handler, every_table
- `src/runtime/x86/rt.c`            — SNOBOL4 patterns: remove ad-hoc bb_node_t, use gen_cfg_t

### Deleted (eventually)
- `SM_BB_EVAL` opcode
- `every_table_register/lookup/reset`
- `ICN_BB_EVAL` macro
- `icn_bb_build`, `icn_bb_scan_gen`, `icn_bb_fnc`, etc.
- `bb_eval_value`
- `rt_bb_arb`, `rt_bb_span`, `rt_bb_arbno`, etc. (replaced by GEN_PAT_* executor)

---

## Steps

### LR-0 — Define gen_node_t, gen_cfg_t; allocator; printer
- `src/runtime/common/gen_node.h` + `gen_node.c`
- No behavior change. All gates unchanged. Commit.

### LR-1 — generator phase: wire four ports (language-neutral)
- `src/runtime/common/gen_phase.c`
- Input: gen_node_t tree. Output: gen_cfg_t with all ports wired.
- `--dump-gen-cfg` flag prints the wired graph.
- No execution path changed. Commit.

### LR-2 — gen_exec: graph-walk executor
- `src/runtime/common/gen_exec.c`
- Follows port_start, port_succ, port_fail, port_resume.
- Tested standalone with unit test: `scripts/test_gen_exec_unit.sh`
- No integration yet. Commit.

### LR-3 — Icon: lower to gen_node_t (additive — keep SM_BB_EVAL fallback)
- lower.c: for LANG_ICN, emit gen_node_t tree in addition to SM_BB_EVAL.
- SM_BB_EVAL handler: if gen_cfg_t present, use gen_exec; else icn_bb_build fallback.
- GATE-1..4 unchanged. Commit.

### LR-4 — Icon: delete SM_BB_EVAL, every_table, ICN_BB_EVAL, icn_bb_build
- Clean break. SM array gone for Icon.
- GATE-1..4 must pass. Commit.

### LR-5 — SNOBOL4 patterns: lower to gen_node_t (additive)
- lower_pattern path: emit GEN_PAT_* nodes alongside existing bb_node_t.
- Pattern executor: try gen_exec path, fall back to bb_node_t if needed.
- GATE: smoke_snobol4 + beauty unchanged. Commit.

### LR-6 — SNOBOL4 patterns: delete ad-hoc bb_node_t pattern runtime
- Remove rt_bb_arb, rt_bb_span, rt_bb_arbno, etc.
- gen_exec handles all pattern matching.
- GATE: smoke_snobol4 + beauty 195/195. Commit.

### LR-7 — Prolog: lower choice points to gen_node_t
- GEN_PL_CHOICE replaces pl_box_choice.
- GATE: smoke_prolog + broker. Commit.

### LR-8 — mode-3 JIT: emit x86 from gen_cfg_t nodes
- bb_flat.c / emit_bb.c walk gen_cfg_t instead of tree_t*.
- GATE: jit-run >= sm-run PASS counts. Commit.

---

## Gates

  LR-0..2:  additive — no gate impact
  LR-3:     GATE-1..4 unchanged (Icon fallback still present)
  LR-4:     GATE-1..4 pass (Icon clean break)
  LR-5:     smoke_snobol4 + beauty 195/195 (SNOBOL4 patterns additive)
  LR-6:     smoke_snobol4 + beauty 195/195 (ad-hoc pattern runtime deleted)
  LR-7:     smoke_prolog + broker (Prolog clean break)
  LR-8:     --jit-run >= --sm-run PASS counts

---

## Watermark

  one4all: f1dbb78b  .github: 91f2a860
  Status: DESIGN — no code yet
  Supersedes: GOAL-ICON-LOWER-REDESIGN.md
  NEXT: LR-0 — define gen_node_t in src/runtime/common/gen_node.h
