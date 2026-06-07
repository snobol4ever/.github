# GOAL-IR-REDESIGN.md — Slim IR_t: structural data only, exec state out

**Owner repo:** SCRIP + this file. **Scope: ALL LANGUAGES** — IR_t is shared.

## THE PROBLEM

`IR_t` conflates static IR structure with mutable runtime execution state.
`value` / `counter` / `state` are written and read 876 times in `IR_interp.c`
and zero times in `emit_bb.c`. They do not belong in the IR node. Consequences:
the graph is not reentrant, nodes double as their own execution frames, and
every IR_t carries ~36 bytes of overhead the emitter never touches.

`α` and `β` are `IR_t *` operand/child pointers with names that clash fatally
with Byrd Box α/β entry-port vocabulary — they are not ports, they are operands.

## TARGET SHAPE

```c
struct IR_t {
    IR_e         t;      /* node kind                        KEEP  */
    IR_t        *γ;      /* success port (control flow)      KEEP  */
    IR_t        *ω;      /* failure port (control flow)      KEEP  */
    IR_t        *a;      /* first operand / child            NEW NAME (was α) */
    IR_t        *b;      /* second operand / child           NEW NAME (was β) */
    const char  *sval;   /* string payload / var name        KEEP  */
    int64_t      ival;   /* integer payload / slot index     KEEP  */
    double       dval;   /* real payload                     KEEP  */
    int          idx;    /* node index in graph->all[]       NEW   */
};
```

Dropped from IR_t: `value` (DESCR_t, ~24 bytes), `counter` (int64_t), `state` (int).

## EXEC STATE — parallel array in IR_graph_t

```c
typedef struct {
    DESCR_t  value;    /* produced value for this node      */
    int64_t  counter;  /* iteration counter / state pointer */
    int      state;    /* state machine phase               */
} IR_exec_t;
```

`IR_graph_t` gains one field: `IR_exec_t *exec` — allocated alongside `all[]`,
`n` entries, zeroed at `IR_alloc`. Access: `g->exec[bb->idx].value` etc.
`bb->idx` is set once at `IR_node_alloc` time and never changes.
Per-execution reset: `memset(g->exec, 0, g->n * sizeof(IR_exec_t))` at entry.

## LADDER

- [ ] **IRD-0 — define IR_exec_t; wire exec[] into IR_graph_t**
  Add `IR_exec_t` typedef to `IR.h`. Add `IR_exec_t *exec` field to
  `IR_graph_t`. Allocate and zero in `IR_alloc`. Add `int idx` to `IR_t`; set
  in `IR_node_alloc`. NO other changes. GATE: `make scrip` rc=0; all smokes pass.

- [ ] **IRD-1 — rename α→a, β→b everywhere**
  Mechanical sed/replace across all of `src/`. Update `IR.h` struct. GATE:
  `make scrip` rc=0; `grep -rn 'α\|β' src/ | grep -v γ | grep -v ω` == 0
  (only γ/ω Greek remaining); all smokes pass.

- [ ] **IRD-2 — drop value/counter/state from IR_t; route interp to exec[]**
  Remove the three fields from `IR_t`. In `IR_interp.c`: replace every
  `bb->value` → `g->exec[bb->idx].value`, `bb->counter` → `g->exec[bb->idx].counter`,
  `bb->state` → `g->exec[bb->idx].state`. Requires threading `g` (the
  `IR_graph_t *`) to call sites that currently only hold `bb`. GATE:
  `make scrip` rc=0; all smokes pass; `grep -rn '->value\|->counter\|->state'
  src/ | grep -v exec | grep -v IR_exec` == 0.

- [ ] **IRD-3 — fix all remaining consumers; full green**
  Audit `src/` for any residual direct field access. Fix `lower_*.c`,
  `emit_bb.c`, `driver/scrip.c`, `tools/`. GATE: build green; smoke
  icon 12/12, prolog 5/5, unified-broker >=25; corpus baseline unchanged.

## DO NOT

- Change γ or ω — they stay `IR_t *` pointers.
- Touch the `bb_operand_aux_t` / `operand_aux` mechanism — out of scope.
- Touch chunk.h/.c or the JCON chunk IR path.
- Generalize exec[] to multi-threaded use — single-threaded interpreter only.

## Watermark

**OPEN — plan written 2026-06-07. No steps landed yet.**

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
