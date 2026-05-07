# GOAL-CHUNKS-STEP17.md — proc/pred tables to entry_pcs

**Repo:** one4all (primary) + .github (this file)
**Tracker:** sub-goal carved out of GOAL-CHUNKS.md Step 17
(session #75, 2026-05-07).  Step 17 is described in one paragraph
in the parent goal but is a multi-rung subsystem migration.

**Done when:** `IcnProcEntry` carries `int entry_pc` (no
`EXPR_t *proc` field); `g_pl_pred_table` keys map names to
`entry_pc`s (no `EXPR_t *` payload); `coro_call(entry_pc, args,
nargs)` runs proc bodies via SM dispatch on the chunk; same for
Prolog clause execution; `polyglot.c` stores no IR pointers; the
isolation gate forbids `EXPR_t *` in the gated runtime files'
function signatures.  Standard CHUNKS gate set + full Icon corpus
+ Prolog smoke (extended to `--sm-run` once consumer-side migrations
land).

---

## Why this file exists

GOAL-CHUNKS.md Step 17 reads:

> In `polyglot_init`, replace `proc_table[i].proc = proc;` with:
> lower the proc body as a named SM chunk during the same pass,
> record `proc_table[i].entry_pc = chunk_pc`.  Same for
> `pl_pred_table_insert(name, entry_pc)`.  Migrate `coro_call`
> ...  Delete `EXPR_t *proc` from proc_table struct.

That single paragraph touches:

- `polyglot.c` (proc_table / pred_table population)
- `sm_lower.c` (must emit named proc-body chunks)
- `coro_runtime.c` / `coro_runtime.h` (proc_table struct, `coro_call`)
- `coro_value.c`, `coro_stmt.c`, `raku_builtins.c`, `interp_hooks.c`,
  `interp_eval.c` (every consumer of `proc_table[i].proc` /
  `pl_pred_table_lookup`)
- `pl_runtime.c` + `pl_broker.h` (Prolog BB engine entry points
  that today take `EXPR_t *`)
- Two static-storage subsystems keyed on EXPR_t identity
  (`static_get` / `static_set` for Icon `static` vars; trail-mark
  semantics in Prolog)

This is a multi-session ladder, not a single rung.  Splitting it
into named rungs in this file gives each session a clean target
and gates.  Mirrors the precedent of `GOAL-MODE4-EMIT.md`
(carve-out of Step 8 + 19 from the same parent goal).

GOAL-CHUNKS.md Step 17 stays as a pointer — this file owns the
destination.

---

## Architectural target

**Today (pre-CH-17a):**

```
                       polyglot_init                sm_lower
                            │                          │
   prog (CODE_t*) ──► proc_table[i].proc=EXPR_t*  ──► SM_Program
                       g_pl_pred_table[name]=EXPR_t*    (skips ICN/PL stmts;
                                                         their proc bodies
                                                         walked at runtime
                                                         by coro_call /
                                                         pl_box_choice)
```

**After this sub-goal closes:**

```
                       polyglot_init           sm_lower (extended)
                            │                          │
   prog (CODE_t*) ──► proc_table[i].name      ──► SM_Program containing
                                                   named proc-body chunks
                                                   (forward-jumped around)
                            │                          │
                            └──► entry_pcs resolved ──►┘
                                 from sm_label_pc_lookup

                            ▼
                       coro_call(entry_pc, args, nargs)
                            │
                            ▼
                       SM dispatch on chunk; frame setup unchanged;
                       generators use the SUSPEND/RESUME machinery
                       laid down in CH-14
```

**The proc_table struct after migration:**

```c
typedef struct {
    const char *name;
    int         entry_pc;     /* SM_Program pc of named proc-body chunk */
    int         nparams;      /* parameter count (was: read from proc->ival) */
    /* No EXPR_t* — IR is gone after sm_preamble for non-SNO too */
} IcnProcEntry;
```

**Frame-slot resolution** moves from runtime (`icn_scope_patch`
mutates `E_VAR.ival` in place during `coro_call`) to lower-time
(scope built when the proc body's chunk is emitted; SM ops carry
slot indices already).  This eliminates the in-place IR mutation
flagged in GOAL-CHUNKS truth-telling preamble item 4.

**Static-variable storage** for Icon `static` vars switches keys
from EXPR_t identity to entry_pc + name pairs.

---

## Rungs (in order; one per session)

### CH-17a — Scaffolding: add entry_pc field, populate via existing labels

**Scope:** Pure addition.  Two file changes only.

- Add `int entry_pc` to `IcnProcEntry` (after `proc`, not
  replacing it).  Initialise to `-1` in `polyglot_init` alongside
  the existing `proc` write.
- Add a new helper `sm_resolve_proc_entry_pcs(SM_Program *p)` in
  scrip_sm.c that, after `sm_lower` returns, walks `proc_table`
  and `g_pl_pred_table` (with a parallel `entry_pc` slot added
  to the latter) and populates `entry_pc` via
  `sm_label_pc_lookup(prog, name)`.  When the lookup returns -1
  (i.e. sm_lower didn't emit a named chunk for this proc — the
  baseline today for every Icon proc and Prolog clause), leave
  the field as -1.  No assertion failure: this rung does not
  require any chunks to exist.
- Optional env-gated diagnostic `SCRIP_PROC_ENTRY_PCS=1` prints
  proc_table and pred_table contents after resolution, showing
  which procs got entry_pcs (none, in this rung).
- No consumer-side changes.  `coro_call` etc. still take
  `EXPR_t *proc` as today.

**Gates:** standard CHUNKS set + smoke ×6 + isolation gate +
unified_broker.  Because CH-17a is pure addition with no producer
or consumer flips, all gates are byte-identical to baseline.

**Rationale for landing this first:** subsequent rungs need the
entry_pc field to populate.  Splitting the scaffolding from the
real lowering work keeps each rung small enough to gate cleanly.

### CH-17b — sm_lower emits named chunks for Icon/Raku procs

**Scope:** sm_lower.c only.  Pre-loop pass over `prog`'s
statements: for each `LANG_ICN`/`LANG_RAKU` stmt whose subject is
an `E_FNC` proc-def, emit:

  `SM_JUMP skip_proc_<name>`
  `SM_LABEL "<name>"`            (named, via sm_label_named)
  `<lowered SM ops for the proc body>`
  `SM_RETURN`
  `SM_LABEL skip_proc_<name>`    (anonymous skip target)

Body lowering re-uses the existing `lower_expr` and `lower_stmt`
machinery, but wrapped in a per-proc context that pre-builds the
scope (so frame-slot indices are baked in instead of resolved at
runtime by `icn_scope_patch`).

**Gating note:** the body lowering hits `E_EVERY`, `E_SUSPEND`,
etc. — kinds CH-15b will later migrate.  For CH-17b, those still
emit the legacy `SM_PUSH_EXPR + SM_BB_PUMP` shape.  That's
acceptable here because (a) consumer-side proc dispatch isn't
flipped yet — these chunks won't be executed; (b) once they are
flipped (CH-17c), the `SM_PUSH_EXPR + SM_BB_PUMP` paths inside
proc bodies will start firing on real corpora, which is exactly
what unblocks CH-15b's validation (per CH-15-SURVEY).

**Producer fires; consumer is dormant.**  CH-17a's
`sm_resolve_proc_entry_pcs` now finds entry_pcs for every Icon/Raku
proc.  Verify via `SCRIP_PROC_ENTRY_PCS=1` env-gated dump.  But
nothing yet calls `coro_call` with `entry_pc` — `coro_call` still
takes `EXPR_t*` and walks IR.

**Gates:** standard set + Icon corpus baseline (must be
byte-identical: 186/47/30 of 263).

### CH-17c — Flip Icon/Raku consumers: coro_call(entry_pc)

**Scope:** the consumer-side migration.  `coro_call` gains a
companion `sm_call_proc(int entry_pc, DESCR_t *args, int nargs)`
that runs the chunk via SM dispatch.  Per-call-site flip:
`coro_call(proc_table[i].proc, ...)` becomes
`sm_call_proc(proc_table[i].entry_pc, ...)`, gated by
`entry_pc != -1` (fall back to the legacy `coro_call` if -1).

Per goal spec: "frame setup unchanged."  `coro_call`'s scope
build, env init, static-var persistence, and frame-stack push
move to a shared `proc_frame_setup` helper that both `coro_call`
and `sm_call_proc` use.  `sm_call_proc`'s body executes the
chunk via the existing SM dispatch loop; `coro_call`'s body
still walks IR (legacy fallback for procs whose chunks didn't
land — increasingly empty as CH-15b proceeds).

**Gates:** standard set + full Icon corpus PASS=186 +
`unified_broker` PASS≥48 + Raku full suite at baseline.

### CH-17d — sm_lower emits named chunks for Prolog predicates

**Scope:** symmetrical to CH-17b but for Prolog.  For each
`LANG_PL` stmt whose subject is `E_CHOICE` or `E_CLAUSE`, emit a
named chunk for the body.  Multi-clause predicates fold into a
single E_CHOICE chunk that internally dispatches across clauses
(SM analog of `pl_box_choice`).

Wire `pl_pred_table_insert` to record the entry_pc instead of
the raw EXPR_t.  For the OR-box semantics, the chunk's body is
itself a sequence of clause-chunks chained via SM analogs of
`bb_seq` / `pl_box_cat`.

**Producer fires; consumer is dormant** for the same reason as
CH-17b.  Standard gates pass because nothing reads the new
entry_pcs yet.

### CH-17e — Flip Prolog consumers: pl_box_choice_pc and friends

**Scope:** the consumer-side migration for Prolog.  Add chunk-
shaped variants:

  `pl_box_choice_pc(int entry_pc, Term **args, int arity)`
  `pl_box_clause_pc(int entry_pc, Term **args, int arity)`
  `pl_box_builtin_pc(int entry_pc, Term **env)`

`pl_box_cut()` already takes no args, no change.

Flip `pl_pred_table_lookup` to return `entry_pc` (or a struct
carrying it).  Each consumer site
(`interp_eval.c:2300`, `pl_runtime.c:1885,1960`,
`interp_hooks.c:163`, `polyglot.c:292`, `interp_eval.c:2749`) is
flipped; legacy `_box_*(EXPR_t *)` variants stay only for the
duration of this rung's two-system swap.

After this rung lands, **`--sm-run` Prolog should work end-to-end
for the first time** because the SM_BB_ONCE → coro_eval → bb_eval_value
crash path is replaced with proper Prolog box dispatch on chunks.
This unblocks Step 16.  Step 16 reactivates here.

**Gates:** standard set + Prolog smoke extended to `--sm-run` +
representative Prolog corpus subset.

### CH-17f — Migrate Step 16 (Prolog clause kinds at sm_lower.c:1213)

**Scope:** as per GOAL-CHUNKS.md Step 16 spec, but executed with
the entry_pc + chunk-shaped consumer infrastructure now
available.  Each of the six kinds (E_CHOICE, E_CLAUSE, E_CUT,
E_UNIFY, E_TRAIL_MARK, E_TRAIL_UNWIND) gets per-kind SM lowering;
the legacy `emit_push_expr + SM_BB_ONCE` path is deleted at the
producer; the consumer reads entry_pcs via the helpers from
CH-17e.

**Gates:** as per Step 16 + the now-reachable Prolog `--sm-run`
crosscheck against the SPITBOL oracle (well, against `--ir-run`,
since SPITBOL doesn't run Prolog).

### CH-17g — Drop EXPR_t *proc from IcnProcEntry; lift code_free gate

**Scope:** the cleanup.  After CH-17c flipped Icon/Raku consumers
and CH-17e flipped Prolog consumers, no live code reads
`proc_table[i].proc` or `pl_pred_table_*`'s EXPR_t payload.
Delete the `EXPR_t *proc` field; delete the legacy `coro_call`
body's IR walk (its scope build, its `interp_eval` body loop —
gone); delete `pl_pred_table_lookup`'s legacy EXPR_t-returning
overload.  `polyglot.c` stores no IR pointers.

Lift `lang_mask == (1u << LANG_SNO)` gate on `code_free` in
`scrip_sm.c` — IR is freed unconditionally for all six frontends.

This is the GOAL-CHUNKS.md Step 17 closure point.

**Gates:** standard set + full Icon corpus + Prolog smoke
+ structural check that `polyglot.c`, `coro_runtime.c`,
`pl_runtime.c` contain zero `EXPR_t *` field accesses on
proc_table / pred_table data.

### CH-17h — Migrate Step 15 remaining kinds (CH-15b)

**Scope:** as per CH-15-SURVEY's recommendation: with proc bodies
now lowered through sm_lower (CH-17b/d), every-bodies and
generator expressions inside Icon procs reach the line-1192
dispatcher arm.  E_EVERY, E_SUSPEND, E_BANG_BINARY, E_LCONCAT,
E_LIMIT, E_RANDOM, E_SECTION, E_SECTION_PLUS, E_SECTION_MINUS
each migrate per-kind with corpus validation now possible.

This is CH-15b's reactivation point.

---

## Per-rung gates summary (delta from CHUNKS standard set)

| Rung    | Adds gate                                            |
|---------|------------------------------------------------------|
| CH-17a  | `SCRIP_PROC_ENTRY_PCS=1` shows -1 for every proc     |
| CH-17b  | `SCRIP_PROC_ENTRY_PCS=1` shows non-(-1) for ICN/Raku |
| CH-17c  | Icon corpus 186/47/30 byte-identical                 |
| CH-17d  | `SCRIP_PROC_ENTRY_PCS=1` shows non-(-1) for PL       |
| CH-17e  | Prolog smoke extended to `--sm-run`                  |
| CH-17f  | Prolog `--sm-run` crosscheck vs `--ir-run`           |
| CH-17g  | structural: no EXPR_t* in proc_table / pred_table    |
| CH-17h  | Icon corpus per-kind crosscheck                      |

---

## File ownership

This sub-goal is **not parallelizable with M4 or M5** the way
GOAL-MODE4-EMIT.md is.  CH-17 rungs touch the same files as the
parent goal's M4 cleanup work (`coro_runtime.c`, `polyglot.c`,
`pl_runtime.c`).  Sequential execution required.

CH-17 rungs are file-disjoint from CH-15b (Icon generator kinds)
and from Step 16 (Prolog cluster), but those steps land DOWNSTREAM
of CH-17e (Step 16) and CH-17h (CH-15b).

---

## Closed rungs

(none yet)
