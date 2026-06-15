# HANDOFF 2026-06-15 — CLAUDE — PROLOG-BB — DYNAMIC CLAUSE STORE (WIP)

Goal: GOAL-PROLOG-BB. Topic: close the last 10 reds — `retract` ×5 (rung14) + `abolish` ×5 (rung15) —
by giving runtime dynamic predicates a clause store and a dispatcher, built on the EVAL/CODE rail.

## STATE AT HANDOFF

- HEAD `023fb43` (PL-GZ rung28 rethrow). Two live modes only: m3 (`--run`), m4 (`--compile x86`).
- Baseline (rebuilt + reconfirmed this session): **m3 105 / m4 105 / 115**, the 10 reds are exactly
  `rung14_retract_*` (5) + `rung15_abolish_*` (5). No-new-global gate **green, doomed floor 15**.
- Working tree: ONE uncommitted change — `src/runtime/unification.c` (the store slice below).
  Left uncommitted **by design** (adds symbols nothing calls yet); it should land as ONE gate-moving
  rung together with the dispatcher (piece 3), not as a dead-symbol commit. Exact diff embedded below.
- Harness note: `--mode all` still drives the deleted m2 (`--interp`) arm and reports false FAILs.
  Use `--mode run` and `--mode compile` separately.

## DESIGN — RATIFIED BY LON THIS SESSION

"If it is like EVAL then it should go through front door or Prolog parse, lower, and emit stages.
If not then it is not. But we are using BBs for things here."

- `assertz` IS EVAL. It goes through the **real lower + emit stages**; its output is a **BB**, the same
  artifact a static clause becomes. Therefore:
- **Path A is chosen**: runtime `Term` → flat `TT_CLAUSE` → `lower_prolog_clause` → `pl_gz_build`.
  The rejected Path B (a parallel `Term`-based lowerer, à la the attic's `lower_clause`/`PlClause`) is
  out: it would bypass the real lower stage AND duplicate logic (WRITE-EACH-PIECE-ONCE).
- `tree_t`-at-runtime on the Prolog path is **new** but **sanctioned via the EVAL/CODE exception** —
  that is the one place RULES permits runtime AST, and it is exactly where the SNOBOL4 EVAL rail already
  lives. The lowerer (`lower_prolog.c`) and emitter (`emit_bb.c`, home of `pl_gz_build`) are **already
  linked into `libscrip_rt.so`** (RT_PIC_SRCS), so the capability is pre-positioned.
- Store = **widen the dead-but-sanctioned `g_pl_pred_table`** (no new global, no allowlist edit).
- Sequencing = **deletion-first** (pieces 1–3 close 9 reds with zero runtime codegen; piece 4 closes the 10th).
- The dynamic predicate is **data threaded by a BB**: clauses are a mutable list; one dispatcher box
  drives them. assertz = compile-a-clause; retract/abolish = list edits. Nothing walks an AST to dispatch.

## VERIFIED FACTS THIS SESSION (pinned to lines — trust these over memory)

- Static clauses ARE compiled to BBs. `lower_prolog_clause` (lower_prolog.c:318) is THE clause lowerer;
  `lower_pl_register_all_preds` (lower_prolog.c:405) lowers every predicate. With m2 deleted, everything
  that runs is a BB.
- The `assertz` argument is a runtime `Term*` (TERM_ATOM/INT/COMPOUND/VAR), NOT the compile-time `tree_t`.
  Same logical clause, two representations; they converge only at the IR after transcription.
- `pl_assert_term` is a **dead orphan**: defined only under `src/attic/`, never called live. The attic
  version builds the WRONG (nested `TT_CLAUSE{head, TT_PROGRAM{goals}}`) shape and routes to the dead
  `lower_clause`. DO NOT resurrect it verbatim.
- The Prolog EXECUTION runtime is `tree_t`/`TT_`-free: `grep -c "tree_t\|\bTT_"` on `unification.c` and
  `arithmetic.c` = 0. `resolution.c` holds clause `tree_t*` only as OPAQUE pred-table handles
  (insert/lookup never inspect `->t`/`->c[]`); that table is part of compile-time `g_stage2`, consumed at
  lower time and not consulted at run time.
- Flat `TT_CLAUSE` shape that `lower_prolog_clause` consumes: `c[0..arity-1]` = head-arg subtrees,
  `c[arity..n-1]` = body goals, `v.dval` = arity, `v.sval` = `"name/arity"`. **Working in-tree template
  to build it programmatically: `pl_ll_maybe_lift` (lower_prolog.c:456)** — the findall lambda-lift does
  exactly this construct → `lower_pl_clause_graph` → register. The runtime transcriber mirrors it.
- Directive-assertz fold: `prolog_lower.c:619-660`. A top-level `:- assertz(X)` synthesizes a `TT_CLAUSE`
  and appends it to the predicate's static `TT_CHOICE` at line 631 (asserta prepends, 647-651).
  `:- dynamic` is already parsed (line 666 `callable_with_args`) but degrades to a no-op `pj_dir_N`
  init helper — it does NOT currently make a predicate dynamic.
- Call ABI (bb_cell_call.cpp): caller `rt_enter(slot,nslots)` builds the callee frame (→ rax),
  moves args into rsi/rdx/rcx from frame cells, calls callee **α** via `x86_call_tgt(X86T_TGT0)`,
  then `test eax,eax; jne γ; jmp ω`; the **β** path reloads the frame ptr and calls callee **lblB**
  (`X86T_TGT1`) to resume. Callee α/β labels are resolved at EMIT time from `cs->callee->lblA/lblB`
  (emit_bb.c:490-522). A statically-compiled call therefore needs the callee's labels at emit time;
  a dynamically-asserted predicate has none → it needs a STABLE emit-time entry (the trampoline, piece 3).

## WORK DONE THIS SESSION — the store slice (VERIFIED: compiles, baseline 105/105 unchanged, gate green)

Replaces the dead `g_pl_pred_table` declaration in `src/runtime/unification.c` (was the 3 lines
`typedef struct { const char *name; long arity; void *alpha; void *redo; } pl_pred_row_t;` /
`static pl_pred_row_t *g_pl_pred_table = ...;` / `static long g_pl_pred_n = 0;`) with:

```c
typedef struct { Term *head; Term *body; void *box; void *pool; int bounded; } pl_dyn_clause_t;
typedef struct { int functor; long arity; pl_dyn_clause_t *cl; long n; long cap; } pl_pred_row_t;
static pl_pred_row_t *g_pl_pred_table = (pl_pred_row_t *)0;
static long           g_pl_pred_n     = 0;
/*--- separator ---*/
pl_pred_row_t *rt_pl_dyn_find(int functor, long arity)
{
    for (long i = 0; i < g_pl_pred_n; i++) if (g_pl_pred_table[i].functor == functor && g_pl_pred_table[i].arity == arity) return &g_pl_pred_table[i];
    return (pl_pred_row_t *)0;
}
/*--- separator ---*/
pl_pred_row_t *rt_pl_dyn_intern(int functor, long arity)
{
    pl_pred_row_t *r = rt_pl_dyn_find(functor, arity);
    if (r) return r;
    g_pl_pred_table = (pl_pred_row_t *)realloc(g_pl_pred_table, (size_t)(g_pl_pred_n + 1) * sizeof(pl_pred_row_t));
    r = &g_pl_pred_table[g_pl_pred_n++];
    r->functor = functor; r->arity = arity; r->cl = (pl_dyn_clause_t *)0; r->n = 0; r->cap = 0;
    return r;
}
/*--- separator ---*/
void rt_pl_dyn_add(int functor, long arity, Term *head, Term *body, void *box, void *pool, int prepend)
{
    pl_pred_row_t *r = rt_pl_dyn_intern(functor, arity);
    if (r->n >= r->cap) { r->cap = r->cap ? r->cap * 2 : 4; r->cl = (pl_dyn_clause_t *)realloc(r->cl, (size_t)r->cap * sizeof(pl_dyn_clause_t)); }
    long at = r->n;
    if (prepend) { for (long j = r->n; j > 0; j--) r->cl[j] = r->cl[j - 1]; at = 0; }
    r->cl[at].head = head; r->cl[at].body = body; r->cl[at].box = box; r->cl[at].pool = pool; r->cl[at].bounded = 0;
    r->n++;
}
/*--- separator ---*/
int rt_pl_abolish(int functor, long arity)
{
    pl_pred_row_t *r = rt_pl_dyn_find(functor, arity);
    if (r) r->n = 0;
    return 1;
}
/*--- separator ---*/
int rt_pl_retract(int functor, long arity, void *request_cell)
{
    extern Trail g_resolve_trail;
    pl_pred_row_t *r = rt_pl_dyn_find(functor, arity);
    if (!r || r->n == 0) return 0;
    Term *req = term_deref((Term *)request_cell);
    for (long i = 0; i < r->n; i++) {
        int mark = trail_mark(&g_resolve_trail);
        if (unify(req, r->cl[i].head, &g_resolve_trail)) { for (long j = i; j + 1 < r->n; j++) r->cl[j] = r->cl[j + 1]; r->n--; return 1; }
        trail_unwind(&g_resolve_trail, mark);
    }
    return 0;
}
```

(Use the real 200-dash separator the file uses, not `/*--- separator ---*/`. Names `g_pl_pred_table` /
`g_pl_pred_n` are kept verbatim for the gate; the table grows exactly and per-row capacity is the struct
field `cap`, so NO new `g_*` symbol is introduced — gate stays green.)

## REMAINING WORK — dependency order

1. **Dynamic-marking prepass** (`prolog_lower.c`, sibling to the fold loop near 619): scan the program for
   every functor that is a target of `assertz`/`asserta`/`retract`/`retractall`/`abolish`, plus any
   `:- dynamic(F/A)`. Mark those functor/arity pairs dynamic. Everything else stays statically folded.
2. **Seeding** (at the fold, `prolog_lower.c:631`): for a MARKED functor, route the synthesized clause to
   `rt_pl_dyn_add(...)` (install into the store at startup) INSTEAD of appending to the static `TT_CHOICE`,
   so `retract` has live clauses to delete and the predicate isn't baked static.
3. **Dispatcher + trampoline (HARD CORE — the segfault-prone piece; do this with full budget).**
   A marked predicate gets a STABLE emit-time entry (its own `pl_gz_callee_t` with `lblA/lblB`, so all
   call sites resolve normally per emit_bb.c:490). Its emitted body, instead of an `IR_CELL_CHOICE` over
   static clauses, drives the runtime clause LIST **nondeterministically**: call clause[k].α with the
   entered frame+args, on `ω` advance to clause[k+1].α, and resume the live clause through its β on
   backtrack — i.e. `bb_cell_choice`'s logic sourced from the `pl_pred_row_t` row rather than a
   compile-time array, honoring the `rt_enter → α → test/jne γ → β(lblB)` ABI. Closes retract ×5 and the
   four non-reassert abolish cases (9 reds).
4. **assertz-while-running** (closes the 10th, `rung15_abolish_abolish_then_reassert`):
   - Transcriber `Term → flat TT_CLAUSE` (live in `lower_prolog.c` to keep `unification.c` `Term`-only),
     modeled on `pl_ll_maybe_lift`: deref-and-FREEZE the argument (ISO `copy_term` snapshot of current
     bindings), map TERM_ATOM→TT_NAME/QLIT, TERM_INT→TT_INT, TERM_COMPOUND→TT_FNC, TERM_VAR→TT_VAR,
     split the `:-`/`,` spine into head args (c[0..arity-1]) + body goals (c[arity..]).
   - Feed unchanged `lower_prolog_clause` → `pl_gz_build`; install the resulting `bb_box_fn` + head `Term`
     into the row via `rt_pl_dyn_add`.
   - Make `pl_gz_build` **re-entrant**: save/restore its file-static codegen state (`g_flat_slot_count`,
     `g_flat_node_id`, `g_bb_slotmap_n`, `g_bb_varslot_n`, …) so an `assertz` fired from inside a running
     predicate does not clobber the caller's codegen context. This same fix hands the SNOBOL4 B-ladder
     its runtime compiler.

## STORE API (already built, for pieces 2-4 to call)

```
pl_pred_row_t *rt_pl_dyn_find  (int functor, long arity);
pl_pred_row_t *rt_pl_dyn_intern(int functor, long arity);
void           rt_pl_dyn_add   (int functor, long arity, Term *head, Term *body, void *box, void *pool, int prepend);
int            rt_pl_abolish   (int functor, long arity);                 // always 1
int            rt_pl_retract   (int functor, long arity, void *request_cell); // first-match remove; 1 if removed
```

## NOTES / RISKS

- `rt_pl_retract` is currently **first-match-remove**, which is correct for these rungs (verified the test
  bodies: retract_basic removes one specific clause then enumerates the rest; retract_all loops
  retract/1 until it fails). Full nondeterministic retract cursor is a later refinement, NOT needed here.
- **Logical-update view** (generation numbers / seeing call-time clauses across concurrent assert+retract)
  is deferred — none of the 10 rungs stress it. Future rung if ever needed.
- The dispatcher drives EMITTED boxes from the runtime with nondeterministic resumption — highest-risk
  piece; budget for careful work and don't leave the tree broken.
- Gate every rung against GATE-3 m3≡m4 and the no-new-global ratchet; floor stays 15, never drops; land
  one rung per commit.

## OPEN ITEMS FOR LON (flagged, not acted on)

- Re-baseline the gate scripts off the deleted `--interp`/m2 arm (false FAILs in `--mode all`).
- With m2 gone, several of the 15 doomed globals may now be genuinely dead → floor possibly droppable.
