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

### CH-17b — sm_lower emits named-chunk SKELETONS for Icon/Raku procs

**Scope:** sm_lower.c only.  Pre-loop pass over `prog`'s
statements: for each `LANG_ICN`/`LANG_RAKU` stmt whose subject is
an `E_FNC` proc-def, emit a chunk SKELETON (no body):

  `SM_JUMP skip_proc_<name>`
  `SM_LABEL "<name>"`            (named, via sm_label_named)
  `SM_RETURN`
  `SM_LABEL skip_proc_<name>`    (anonymous skip target)

**Skeleton-only deliberate choice (sess #75):** body lowering is
non-trivial — Icon proc bodies are EXPR_t chains, not STMT_t,
and frame-slot resolution via `icn_scope_patch` happens at
runtime inside `coro_call` today.  Migrating that to lower-time
is its own architectural decision that deserves its own rung
(CH-17b').  The skeleton-only rung lands first because it is the
minimal change that lets `sm_resolve_proc_entry_pcs` (CH-17a)
populate non-(-1) entry_pcs, validating the resolver end-to-end
on real corpora.

**Producer fires; body is empty; consumer is dormant.**  CH-17a's
resolver now finds entry_pcs for every Icon/Raku proc.  Verify
via `SCRIP_PROC_ENTRY_PCS=1`.  But nothing yet calls those
chunks — `coro_call` still walks IR.  And even if a future
consumer called them today, they'd return immediately (empty
body), which is fine because no consumer flip has happened yet.

**Gates:** standard set + Icon corpus baseline (must be
byte-identical: 186/47/30 of 263).  Skeleton chunks are
forward-jumped over so execution falls through them.

### CH-17b' — Lower Icon/Raku proc bodies into the chunks

**Scope:** the actual body work.  For each chunk emitted by
CH-17b, replace the immediate `SM_RETURN` with the lowered body
SM ops (then `SM_RETURN`).  Body lowering re-uses `lower_expr`
machinery, but wrapped in a per-proc context that pre-builds the
scope so frame-slot indices are baked in instead of resolved at
runtime by `icn_scope_patch`.

**Gating note:** the body lowering hits `E_EVERY`, `E_SUSPEND`,
etc. — kinds CH-15b will later migrate.  For CH-17b', those still
emit the legacy `SM_PUSH_EXPR + SM_BB_PUMP` shape.  That's
acceptable here because (a) consumer-side proc dispatch isn't
flipped yet — these chunks won't be executed; (b) once they are
flipped (CH-17c), the `SM_PUSH_EXPR + SM_BB_PUMP` paths inside
proc bodies will start firing on real corpora, which is exactly
what unblocks CH-15b's validation (per CH-15-SURVEY).

**Gates:** standard set + Icon corpus baseline byte-identical.

### CH-17b'' — Bake frame-slot resolution into chunks at lower-time

**Scope:** the second half of CH-17b's original "scope built when
the proc body's chunk is emitted; SM ops carry slot indices already"
goal text — split out into its own rung when CH-17b' (sess #78)
deferred frame-slot baking and left chunks emitting `SM_PUSH_VAR
<name>` for params and locals.  That deferred shape would have
broken CH-17c on consumer flip: `SM_PUSH_VAR` reads the global NV
table, missing the IcnFrame.env values that `coro_call` populates
with arguments.

**Why a separate rung was carved (sess #80, 2026-05-07):** CH-17b'
landed with the closing note "Frame-slot resolution stays at runtime
(`icn_scope_patch` unchanged); E_VAR lowers to `SM_PUSH_VAR <name>`
name-keyed via NV_GET_fn — no scope-patch needed at lower-time."
That deferral, while letting CH-17b' land cleanly, leaves the
chunks semantically wrong for SM dispatch — the params/locals point
at NV instead of FRAME.env.  CH-17c was about to inherit a broken
chunk shape.  Carving CH-17b'' into its own rung (per the sub-goal
file's precedent of CH-17a / CH-17b / CH-17b' splits) keeps each
step small and gateable while honouring the original Step 17 spec.

**Implementation:**

- Two new opcodes in `sm_prog.h`: `SM_LOAD_FRAME` / `SM_STORE_FRAME`
  with `a[0].i = slot index`.  Handlers in `sm_interp.c` route
  through three pure-DESCR_t forwarders defined in `coro_runtime.c`
  (`icn_frame_env_active`, `icn_frame_env_load`, `icn_frame_env_store`)
  — no EXPR_t leakage across the SM/IR boundary.  Outside an Icon
  frame (frame_depth == 0), both opcodes push FAILDESCR / clear
  last_ok, mirroring SM_LOAD_GLOCAL's outside-of-generator
  semantics.  JIT codegen stubs are named-FATAL (M5 territory).

- `sm_lower.c` chunk-body emission loop builds a per-proc
  `IcnScope` mirroring `icn_scope_patch` but without IR mutation:
  params first (slots 0..nparams-1), then E_GLOBAL-decl names,
  then body E_VAR walk.  Globals (registered via `global_register`
  at polyglot_init) are excluded from the scope — they bridge to
  the SNO NV store, matching the IR walker's slot=-1 → NV_GET_fn
  fallback.  Keywords (`&`-prefixed names) are also excluded.
  Stored in file-static `g_chunk_scope`, gated on
  `g_chunk_body_lowering`.

- `lower_expr`'s E_VAR and E_ASSIGN(LHS=E_VAR) cases consult
  `g_chunk_scope`.  In-scope names emit `SM_LOAD_FRAME slot` /
  `SM_STORE_FRAME slot`; out-of-scope names (globals, keywords,
  unscoped) fall through to `SM_PUSH_VAR` / `SM_STORE_VAR` —
  unchanged emission for stmt-level lowering and for true globals
  inside chunks.

**Producer-side empirical proof:** `--dump-sm --sm-run
test/icon/palindrome.icn` shows the chunk for `palindrome` (pc 1–52)
now emits `SM_LOAD_FRAME` / `SM_STORE_FRAME` for `s`, `i`, `j` —
was `SM_PUSH_VAR "s"` / `SM_STORE_VAR "i"` etc. in CH-17b'.
Builtin / proc-name function references inside E_FNC argument
position (e.g. `write`, `palindrome`) also currently get slot
indices — this mirrors how `icn_scope_patch` adds them at runtime;
the slot is dead because the IR walker dispatches E_FNC by
`children[0]->sval` string before evaluating the function-name
child as a value.  CH-17c's E_FNC-shape rework will fix this in
the lowering (don't lower children[0] as a value when the call
target is name-resolvable).

**Pre-existing E_FNC malform note (uncovered by this rung,
inherited from CH-17b'):** the `case E_FNC` lowering at
sm_lower.c:832–834 does `lower_expr(children[0..nargs-1])` then
`SM_CALL s=e->sval nargs` — pushing `nargs+1` values but popping
only `nargs`.  Result: chunks containing E_FNC have a stack-leak
shape that would corrupt execution if reached.  Pre-existing in
CH-17b'; not introduced here.  CH-17c must fix.

**Chunks remain dead code.**  `coro_call` still walks IR
(`coro_value.c:495–501`); chunks are forward-jumped over by
SM_JUMP.  Gates byte-identical because the chunks are unreachable
from any real program path until CH-17c flips the consumer.

**Gates:** standard set byte-identical to baseline.  Smoke ×6
PASS (7/7, 5/5, 5/5, 5/5, 5/5, 4/4); isolation gate PASS;
csnobol4 Budne PASS=61; unified_broker PASS=49; full Icon corpus
PASS=186 FAIL=47 XFAIL=30 TOTAL=263.

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

**CARVED into three sub-rungs sess 2026-05-09** — empirical state at
CH-17f close: eight `coro_call(proc_table[i].proc, args, nargs)` consumer
sites still read `.proc` directly outside the trampoline (CH-17c only
flipped `proc_trampoline` / `gather_trampoline`).  Static-variable
storage in `coro_runtime.c:155–183` is still keyed on `EXPR_t*`.  Chunk
bodies still emit `SM_PUSH_EXPR + SM_BB_PUMP` for unmigrated generator
kinds (per CH-17b' close note).  Each precondition for the field-drop
needs its own rung.  Mirrors how CH-17b/b'/b'' were carved.

#### CH-17g-call-sites — flip the eight residual consumer sites

**Scope:** mirror CH-17c's trampoline-side flip for the call sites it
didn't reach.  Add a small dispatch helper `proc_table_call(int pi,
DESCR_t *args, int nargs)` next to `sm_call_proc` in `coro_runtime.{c,h}`:

  - if `proc_table[pi].entry_pc >= 0`, call `sm_call_proc`
  - else, fall back to `coro_call(proc_table[pi].proc, args, nargs)`

Replace `coro_call(proc_table[i].proc, args, nargs)` with
`proc_table_call(i, args, nargs)` at the eight non-trampoline call sites
in `coro_value.c`, `raku_builtins.c`, `interp_eval.c` (×3),
`interp_hooks.c`, `interp_exec.c` (×3), `polyglot.c`.  Trampoline-layer
sites in `coro_runtime.c` (lines 1125, 1213, 1503) stay as-is —
CH-17c's flip already lives inside the trampolines, reading entry_pc
out of the staging struct.

`coro_drive_fnc` (the suspend-aware generator driver,
`coro_runtime.c:1721`) is intentionally NOT flipped — it's an IR walker
by design and waits for CH-17h to migrate the remaining generator kinds.

`sm_lower.c:1742` is producer-side (sm_lower needs to read proc->...
to lower the body into a chunk) — it stays.

Pure routing reorganisation, no behavioural change: every flipped site
reaches one of the same two paths it was reaching before, just now
with the chunk path as a first-class option at the call site instead
of only at the trampoline.

**Gates:** standard CHUNKS set + full Icon corpus 186/47/30 +
unified_broker + isolation gate, all byte-identical.

#### CH-17g-statics — re-key static-variable storage off EXPR_t*

**Scope:** `coro_runtime.c:155–183` `static_tab[]` table keyed on
`(EXPR_t *proc, const char *name)` — used by `coro_call`'s param-load
preamble (line 447) and frame-pop epilogue (line 500) to persist Icon
`static x` declarations across calls.  Re-key onto `(int entry_pc,
const char *name)` (when entry_pc is resolved) or
`(const char *proc_name, const char *name)` (universal fallback).
Once this rung lands, no live runtime path keys storage on EXPR_t
identity.

**Gates:** standard set + the smoke programs that exercise Icon
`static` vars (e.g. `wordcount.icn` if present in corpus).

#### CH-17g-final — drop EXPR_t *proc; lift code_free gate

**Scope:** the actual closure.  Preconditions: CH-17g-call-sites
(eight sites flipped), CH-17g-statics (storage re-keyed), CH-17h
(remaining generator kinds migrated so chunk bodies no longer emit
`SM_PUSH_EXPR + SM_BB_PUMP`), **CH-17g-runtime-bridge** (chunks
dispatch builtins so `--sm-run` of any Icon hello-world produces
correct output instead of FATAL "Undefined function" — added as a
precondition by CH-17g-final-SURVEY 2026-05-09), **CH-17g-irrun-lowers**
(invoke `sm_lower` / `sm_resolve_proc_entry_pcs` from `--ir-run` path
before `polyglot_execute` so `entry_pc >= 0` for every proc regardless
of mode — added by the same survey).  When all five are met:

  - delete `EXPR_t *proc` field from `IcnProcEntry`
  - delete the legacy body of `coro_call(EXPR_t*, ...)` (its scope
    build, its `interp_eval` body loop) and the `coro_drive_fnc`
    wrapper
  - delete `pl_pred_table_lookup`'s legacy EXPR_t-returning overload
  - lift `lang_mask == (1u << LANG_SNO)` gate on `code_free` in
    `scrip_sm.c` — IR freed unconditionally for all six frontends
  - strengthen `test_isolation_ir_sm.sh` with the structural check
    forbidding `EXPR_t *` in `polyglot.c`, `coro_runtime.c`,
    `pl_runtime.c` proc/pred-table fields

This is the GOAL-CHUNKS.md Step 17 closure point.

**Gates:** standard set + full Icon corpus + Prolog smoke
+ structural check that `polyglot.c`, `coro_runtime.c`,
`pl_runtime.c` contain zero `EXPR_t *` field accesses on
proc_table / pred_table data.

### CH-17h — Migrate Step 15 remaining kinds (CH-15b)

**CH-17h-SURVEY LANDED sess 2026-05-09** — `docs/CHUNKS-step17h-survey.md`
documents that the line-1303 dispatcher arm (`E_EVERY`, `E_SUSPEND`,
`E_BANG_BINARY`, `E_LCONCAT`, `E_LIMIT`, `E_RANDOM`, `E_SECTION`,
`E_SECTION_PLUS`, `E_SECTION_MINUS`) is **dead code on real corpora today**:
zero fires across smoke ×6 + Icon corpus 263 + unified_broker 49 +
broad/regression runs + a hand-crafted `every`/`suspend`/section program
that produced correct output.  Same diagnosis as CH-15-SURVEY: stmt-context
generators lower via `lower_stmt`'s dedicated paths; chunk-body generators
sit in chunks that are forward-jumped over until CH-17g-final makes them
live.  **Recommendation in the survey doc: reverse the original sequencing
— land CH-17g-final first** (its legacy-body deletion is the act that
*creates* the test surface for these kinds, not the act that requires them
gone), then migrate per-kind with real corpus validation.  Awaits Lon
decision on sequencing.

**Scope (when migration starts):** as per CH-15-SURVEY's recommendation: with proc bodies
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
| CH-17b  | `SCRIP_PROC_ENTRY_PCS=1` shows non-(-1) for ICN/Raku (chunks are skeletons) |
| CH-17b' | proc-body chunks contain the actual lowered ops      |
| CH-17b''| chunk E_VARs emit SM_LOAD_FRAME / SM_STORE_FRAME for params+locals; gates byte-identical (chunks still dead code) |
| CH-17c  | Icon corpus 186/47/30 byte-identical                 |
| CH-17d  | `SCRIP_PROC_ENTRY_PCS=1` shows non-(-1) for PL       |
| CH-17e  | Prolog smoke extended to `--sm-run`                  |
| CH-17f  | Prolog `--sm-run` crosscheck vs `--ir-run`           |
| CH-17g-call-sites | Icon corpus 186/47/30 byte-identical (8 sites flipped) |
| CH-17g-statics | static-var storage no longer keyed on EXPR_t* |
| CH-17g-final-SURVEY | finding: legacy `coro_call` body is live in `--ir-run`; CH-17g-final preconditions amended |
| CH-17g-runtime-bridge-DESIGN | architectural plan: extract `icn_try_call_builtin_by_name`; wire into `SM_CALL_FN` after `INVOKE_fn` |
| CH-17g-runtime-bridge-1 | refactor: `icn_call_builtin` split into name-based helper + EXPR_t tail; corpus byte-identical |
| CH-17g-runtime-bridge-2 | `--sm-run` of trivial Icon proc produces output identical to `--ir-run` |
| CH-17g-runtime-bridge-3 | Raku/SCAN bridges (only if corpus crosscheck reveals need) |
| CH-17g-irrun-lowers | `--ir-run` invokes `sm_lower` / `sm_resolve_proc_entry_pcs`; entry_pc resolves regardless of mode |
| CH-17g-final | structural: no EXPR_t* in proc_table / pred_table    |
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

**CH-17a LANDED sess #75, 2026-05-07** — Scaffolding.  `IcnProcEntry`
and `Pl_PredEntry` gain `int entry_pc` (init -1).  New
`sm_resolve_proc_entry_pcs(SM_Program*)` in scrip_sm.c walks both
tables after sm_lower returns and populates entry_pcs via
`sm_label_pc_lookup`.  Today every entry resolves to -1 (no chunks
yet).  Pure addition; byte-identical gates.  Diagnostic env
`SCRIP_PROC_ENTRY_PCS=1`.  one4all @ `0cb31ca4`.

**CH-17b LANDED sess #75, 2026-05-07** — sm_lower emits named-chunk
skeletons (SM_JUMP + SM_LABEL + SM_RETURN + SM_LABEL) for every
entry in proc_table.  CH-17a's resolver now finds non-(-1) entry_pcs
end-to-end (Icon hello.icn: main@1; Raku rk_given: day_type@1,
season@5, main@9).  Empty bodies; chunks forward-jumped over.
Scope-reduced from "skeleton + body" mid-session — body lowering
split into CH-17b' to keep this rung small and risk-free.  one4all
@ HEAD (post `0cb31ca4`).

**CH-17b' LANDED sess #78, 2026-05-07** — proc-body lowering.  The
per-proc emission loop in sm_lower.c (CH-17b's skeleton site) now
walks `proc->children[1+nparams..nchildren-1]` and calls `lower_expr`
on each body child, followed by `SM_POP`, then a trailing `SM_RETURN`.
Chunks now contain real lowered SM ops.  Verified via `--dump-sm` on
`test/icon/palindrome.icn`: chunk 1–52 holds the full palindrome
proc body (map call, while loop with E_LCOMP, SM_AUGOP, etc.); chunk
55–74 holds main's three write+palindrome calls.  Raku rk_given:
three procs with substantial chunk bodies (day_type@1, season@81,
main@161).  Chunks remain unreachable — coro_call still walks IR,
forward-jumps skip every chunk.  Soft addition: a file-static
`g_chunk_body_lowering` flag set/cleared around the loop suppresses
lower_expr's "unhandled expr kind" stderr warning during proc-body
emission only — kinds without explicit cases (E_ALTERNATE, E_ITERATE,
E_CSET_*, E_REVASSIGN, E_REVSWAP) emit harmless SM_PUSH_NULL inside
the dead chunk; warning still fires for executable code via
lower_stmt.  Frame-slot resolution stays at runtime (`icn_scope_patch`
unchanged); E_VAR lowers to `SM_PUSH_VAR <name>` name-keyed via
NV_GET_fn — no scope-patch needed at lower-time.  Static-variable
persistence in coro_call unchanged.  Generator kinds (E_EVERY,
E_SUSPEND, E_BANG_BINARY, E_LCONCAT, E_LIMIT, E_RANDOM, E_SECTION*)
emit legacy `SM_PUSH_EXPR + SM_BB_PUMP` inside chunks — the gating
note in the spec; CH-17h reactivates CH-15b once CH-17c flips
consumers.  Gates byte-identical to baseline: smoke ×6 PASS
(7/7, 5/5, 5/5, 5/5, 5/5, 4/4), isolation gate PASS, csnobol4 Budne
PASS=61, Icon corpus PASS=186 FAIL=47 XFAIL=30 TOTAL=263,
unified_broker PASS=49, scrip_all_modes PASS=2.  Documented in
`docs/CHUNKS-step17b-prime-validation.md`.  Files touched:
`src/runtime/x86/sm_lower.c` only.  Next rung: **CH-17c** —
flip `coro_call` consumer sites to dispatch via entry_pc when
non-(-1); add companion `sm_call_proc(int entry_pc, ...)`.

**CH-17b'' LANDED sess #80, 2026-05-07** — frame-slot baking at
lower-time.  Carved as a separate rung when CH-17b' deferred
frame-slot resolution and left chunks emitting `SM_PUSH_VAR <name>`
for params/locals — a shape that would have broken CH-17c on
consumer flip (NV table reads instead of FRAME.env reads).  Two
new opcodes `SM_LOAD_FRAME` / `SM_STORE_FRAME` (a[0].i = slot)
added to `sm_prog.h`; handlers in `sm_interp.c` route through
three pure-DESCR_t forwarders in `coro_runtime.c`
(`icn_frame_env_active`, `icn_frame_env_load`, `icn_frame_env_store`)
— no EXPR_t leakage across the SM/IR boundary.  Outside an Icon
frame, both opcodes push FAILDESCR (mirrors SM_LOAD_GLOCAL).  JIT
codegen named-FATAL stubs (M5 territory).

In `sm_lower.c`, chunk-body emission loop builds a per-proc
IcnScope mirroring `icn_scope_patch` without IR mutation (params
0..nparams-1, then E_GLOBAL-decl names, then body E_VAR walk;
globals via `global_register` are excluded from scope so they
bridge to NV).  `lower_expr`'s E_VAR / E_ASSIGN(LHS=E_VAR) cases
consult the scope under `g_chunk_body_lowering`; in-scope names
emit SM_LOAD_FRAME / SM_STORE_FRAME, out-of-scope names fall
through to SM_PUSH_VAR / SM_STORE_VAR (unchanged at stmt-level).

Empirical proof: `--dump-sm --sm-run test/icon/palindrome.icn`
shows the palindrome chunk now emits SM_LOAD_FRAME / SM_STORE_FRAME
for `s`, `i`, `j` (was SM_PUSH_VAR / SM_STORE_VAR in CH-17b').

Pre-existing E_FNC malform note (inherited from CH-17b', NOT
introduced here): the `case E_FNC` lowering at sm_lower.c:832–834
does `lower_expr(children[0..nargs-1])` then `SM_CALL s=e->sval
nargs` — pushing nargs+1 values but popping only nargs.  Result:
chunks containing E_FNC have a stack-leak shape that would
corrupt execution if reached.  Chunks remain dead code today so
this is unreachable; CH-17c must fix it when wiring the consumer.

Chunks remain unreachable — `coro_call` still walks IR; chunks
forward-jumped over by SM_JUMP.  Gates byte-identical to baseline:
smoke ×6 PASS (7/7, 5/5, 5/5, 5/5, 5/5, 4/4), isolation gate PASS,
csnobol4 Budne PASS=61, unified_broker PASS=49, full Icon corpus
PASS=186 FAIL=47 XFAIL=30 TOTAL=263.

Files touched:
`src/runtime/x86/sm_prog.h`, `src/runtime/x86/sm_prog.c`,
`src/runtime/x86/sm_interp.c`, `src/runtime/x86/sm_codegen.c`,
`src/runtime/x86/sm_lower.c`, `src/runtime/x86/sm_interp_test.c`,
`src/runtime/interp/coro_runtime.c`.

Next rung: **CH-17c** — flip `coro_call` consumer sites to
dispatch via entry_pc when non-(-1); add companion
`sm_call_proc(int entry_pc, ...)`; fix the E_FNC stack-leak shape
inherited from CH-17b'.

**CH-17c LANDED sess #82, 2026-05-07** — consumer-side flip.
`sm_call_proc(int entry_pc, int nparams, DESCR_t *args, int nargs)`
added to `coro_runtime.c`: pushes `IcnFrame` with param slots bound
from args, delegates body execution to `sm_call_chunk(entry_pc)` (nested
SM_State; `SM_LOAD_FRAME`/`SM_STORE_FRAME` see the live frame via
`icn_frame_env_load/store`), pops frame on return.  `nparams` added to
`IcnProcEntry` (populated from `proc->ival` in `polyglot.c`);
`gather_entry_pc`/`gather_nparams` added to `coro_t` (icon_gen.h).
`Icn_coro_stage_t` gains `entry_pc`/`nparams`.  All three staging sites
flipped; `proc_trampoline` and `gather_trampoline` dispatch via
`sm_call_proc` when `entry_pc >= 0`, fall back to `coro_call` when `-1`.
E_FNC lowering in `sm_lower.c` fixed for Icon-style nodes (`e->sval == NULL`,
name in `children[0]->sval`): now emits `SM_CALL(fn, real_nargs)` — fixes
the empty-name / stack-shape bug in proc-body chunks.  Empirical proof:
`SCRIP_PROC_ENTRY_PCS=1 --sm-run palindrome.icn` shows palindrome@1 /
main@54; `proc_trampoline` dispatches via `sm_call_proc` for both.
Static-variable persistence deferred to CH-17g (keyed on `EXPR_t*`).
`coro_drive_fnc` left for CH-17g cleanup.  Gates byte-identical to
baseline: smoke ×6 PASS (7/7, 5/5, 5/5, 5/5, 5/5, 4/4), isolation PASS,
csnobol4 Budne PASS=61, unified_broker PASS=49, Icon corpus PASS=186
FAIL=47 XFAIL=30 TOTAL=263, scrip_all_modes PASS=2.
Documented in `docs/CHUNKS-step17c-validation.md`.
Files: `src/runtime/interp/coro_runtime.h`, `src/runtime/interp/coro_runtime.c`,
`src/driver/polyglot.c`, `src/frontend/icon/icon_gen.h`,
`src/runtime/x86/sm_lower.c`.  Next rung: **CH-17d** (sm_lower emits
named chunks for Prolog predicates).
**CH-17d LANDED sess #83, 2026-05-07** — producer-side: `sm_lower.c` now
emits named-chunk skeletons (SM_JUMP+SM_LABEL+SM_RETURN+SM_LABEL) for every
entry in `g_pl_pred_table`; loop added immediately after the Icon/Raku
proc-chunk loop.  `sm_resolve_proc_entry_pcs` (CH-17a) now finds non-(-1)
entry_pcs for all Prolog predicates: `palindrome/2@1`, `main/0@5` confirmed
via `SCRIP_PROC_ENTRY_PCS=1`.  Consumer dormant (chunks forward-jumped over).
Gates byte-identical: smoke ×5 PASS, isolation PASS, unified_broker PASS=49,
Budne PASS=61, Icon corpus PASS=186 FAIL=47 XFAIL=30 TOTAL=263.
Documented in `docs/CHUNKS-step17d-validation.md`.
Files: `src/runtime/x86/sm_lower.c`.  Next rung: **CH-17e** (flip Prolog
consumers: pl_box_choice_pc and friends; --sm-run Prolog end-to-end).
**CH-17e LANDED sess #84, 2026-05-07** — consumer-side flip. `pl_box_choice_pc(int entry_pc, Term **caller_args, int arity)` added to `pl_broker.h/c` (one-shot box calling `sm_call_chunk(entry_pc)`). `pl_pred_entry_lookup(const char*)` added to `pl_runtime.h/c`. Five consumer sites flipped: `interp_eval.c` E_FNC Prolog dispatch + E_CHOICE case; `pl_runtime.c` msort/predsort + general user-pred dispatch; `interp_hooks.c` polyglot hook; `polyglot.c` main/0 entry (sm_call_chunk when epc>=0). All sites: entry_pc>=0 → chunk path, else legacy IR fallback. Chunks skeleton-only (SM_RETURN from CH-17d); sm_call_chunk returns FAILDESCR (correct 'no solution'). No crash. Gates byte-identical: smoke x5 PASS, isolation PASS, unified_broker PASS=49, Budne PASS=61, Icon PASS=186/47/30 TOTAL=263. one4all HEAD `7cfa0a96`. Next rung: **CH-17f** (fill E_CHOICE/E_CLAUSE bodies in sm_lower.c; --sm-run Prolog produces correct output).

**CH-17f LANDED sess #85, 2026-05-07** — new `SM_BB_ONCE_PROC` opcode (`a[0].s = "name/arity"`, `a[1].i = arity`) replaces the legacy `lower_expr(E_CHOICE) + SM_BB_ONCE` path that pushed raw `EXPR_t*` to the SM value stack and called `coro_eval(E_CHOICE)` at runtime → FATAL "unhandled kind 59". `lower_stmt` LANG_PL branch emits `SM_BB_ONCE_PROC key, arity` directly from `s->subject->sval`; `lower_expr` E_CHOICE case same. Non-E_CHOICE directive subjects fall through to legacy path. Runtime: `pl_pred_table_lookup_global(key)` → `pl_box_choice(IR, g_pl_env, arity)` → `bb_broker(BB_ONCE)` — fully correct Prolog execution via the existing IR broker. No EXPR_t* pushed or walked at the SM statement-dispatch layer. Predicate chunk bodies remain skeleton-only (CH-17d SM_RETURN); chunk body fill deferred to follow-on rung. `--sm-run` Prolog programs now produce correct output: hello.pl → "Hello, World!", roman.pl → correct. Gates: smoke ×6 PASS (7/7, 5/5, 5/5, 5/5, 5/5, 4/4), isolation PASS, Budne PASS=61, unified_broker PASS=49, Icon corpus 186/47/30 TOTAL=263 (byte-identical). Documented in `docs/CHUNKS-step17f-validation.md`. Files: `sm_prog.h`, `sm_prog.c`, `sm_interp.c`, `sm_codegen.c`, `sm_lower.c`. one4all @ `a2c6c089`. Next rung: **CH-17g** (drop `EXPR_t *proc` from `IcnProcEntry`; lift `code_free` gate).

**CH-17g-call-sites LANDED sess 2026-05-09** — first of three carved sub-rungs (CH-17g-call-sites / CH-17g-statics / CH-17g-final).  CH-17g as written assumed CH-17c had flipped every `proc_table[i].proc` consumer, but empirically CH-17c flipped only the trampoline layer (`proc_trampoline`, `gather_trampoline`).  Eight `coro_call(proc_table[i].proc, args, nargs)` consumer call sites still read `.proc` directly: `coro_value.c` (E_FNC user-proc dispatch), `raku_builtins.c` (Raku method-call dispatch), `interp_eval.c` ×3 (user-proc value-context, fallback, U-22 cross-language), `interp_hooks.c` (SNO→Icon usercall), `interp_exec.c` ×3 (top-level main dispatch), `polyglot.c` (single-language Icon main).  This rung adds `proc_table_call(int pi, DESCR_t *args, int nargs)` to `coro_runtime.{c,h}` — `entry_pc >= 0 ? sm_call_proc : coro_call` — and flips the eight call sites to use it.  Trampoline-layer staging at `coro_runtime.c:1125, 1213, 1503` left as-is (CH-17c's flip already lives inside the trampolines).  `coro_drive_fnc` (`coro_runtime.c:1721`) intentionally NOT flipped — IR walker by design, M4-cleanup territory (CH-17h).  `sm_lower.c:1742` is producer-side, stays.  Pure routing reorganisation; no behavioural change because every flipped site still reaches the same two paths (chunk via `sm_call_proc` when `entry_pc >= 0`, IR via `coro_call` otherwise).  Gates byte-identical to baseline: smoke ×6 PASS (7/7, 5/5, 5/5, 5/5, 5/5, 4/4), isolation PASS, unified_broker PASS=49, csnobol4 Budne PASS=50 (this session's pre-flip baseline; differs from CH-17f's recorded PASS=61, environmental — investigation deferred), Icon corpus PASS=186 FAIL=47 XFAIL=30 TOTAL=263, scrip_all_modes PASS=2 FAIL=0.  Documented in `docs/CHUNKS-step17g-call-sites-validation.md`.  Files: `src/runtime/interp/coro_runtime.h` + `coro_runtime.c` (helper); `coro_value.c`, `raku_builtins.c`, `interp_eval.c`, `interp_hooks.c`, `interp_exec.c`, `polyglot.c` (call-site flips).  Next rung: **CH-17g-statics** (re-key static-variable storage off EXPR_t*).
**CH-17g-statics LANDED sess 2026-05-09** — `static_ent_t` struct in `coro_runtime.c` re-keyed: `EXPR_t *proc` field replaced by `int entry_pc` + `const char *proc_name`.  New file-static helper `static_proc_entry_pc(name)` walks `proc_table[]` and returns the resolved entry_pc (or -1 if not yet lowered).  New `static_entry_matches(...)` predicate: primary key `(entry_pc, var_name)` when both sides have `entry_pc >= 0`; fallback to `(proc_name, var_name)` for the legacy coro_call path where entry_pc is still -1.  Icon proc names are interned (unique per source proc), so name-string identity under `strcmp` provides the same scoping guarantee that EXPR_t* pointer identity did.  `static_get` / `static_set` signatures unchanged (still take `EXPR_t *proc` — compatible with coro_call); internally extract `proc->sval` + resolve entry_pc.  No external callers of static_get/static_set exist outside coro_runtime.c.  On set-update: if a slot was stored with entry_pc==-1 and entry_pc has since been resolved, the slot is upgraded in place.  Gates byte-identical: smoke ×6 PASS (7/7, 5/5, 5/5, 5/5, 5/5, 4/4), isolation PASS, unified_broker PASS=49, scrip_all_modes PASS=2, Icon --ir-run PASS=186 FAIL=47 XFAIL=30 TOTAL=263, rung36_jcon_statics PASS.  Documented in `docs/CHUNKS-step17g-statics-validation.md`.  Files: `src/runtime/interp/coro_runtime.c`.  Next rung: **CH-17g-final** (drop `EXPR_t *proc` from `IcnProcEntry`; lift `code_free` gate — precondition: CH-17h must land first to migrate remaining generator kinds so coro_call legacy body can be deleted).

**CH-17g-final-SURVEY LANDED sess 2026-05-09** — `docs/CHUNKS-step17g-final-survey.md` documents that **CH-17h-SURVEY's "land CH-17g-final first" recommendation is empirically wrong**.  The legacy `coro_call` body is the live, hot, only consumer of Icon/Raku user-proc dispatch in `--ir-run` mode — the same mode that the Icon corpus baseline gate (186/47/30) runs every program through.  Probe instrumentation (reverted before commit) showed that for `procedure main() write("hello") end` under `--ir-run`, `proc_table_call` is reached with `entry_pc=-1`, the `if (entry_pc >= 0)` chunk-dispatch branch is skipped, and the fallback `coro_call(proc_table[pi].proc, args, nargs)` produces the program's output.  Root cause: `sm_resolve_proc_entry_pcs` (CH-17a's resolver) is invoked from `sm_preamble`, which `--ir-run` does not call (`scrip.c:557–561` dispatches to `polyglot_execute` directly for non-SNO `--ir-run`, never reaching `sm_lower`).  Therefore every `proc_table[i].entry_pc` stays at `-1` in `--ir-run` mode and the legacy body is the only path.  CH-17h-SURVEY's audit of `sm_lower.c:1303` was correct as a lowering-site finding; its inferred runtime-side claim was not, because the lowering-site dead arm and the runtime-side `coro_call` body are different code paths.  Recommendation in the survey doc: split CH-17g-final's preconditions into two new rungs (**CH-17g-runtime-bridge** — chunks dispatch builtins so `--sm-run` of trivial Icon programs produces output instead of FATAL "Undefined function"; and **CH-17g-irrun-lowers** — invoke `sm_lower`/`sm_resolve_proc_entry_pcs` from `--ir-run` before `polyglot_execute` so `entry_pc >= 0` for every proc regardless of mode).  Once both land, CH-17g-final's deletions become safe.  Alternative: merge CH-17h, CH-17g-runtime-bridge, and CH-17g-irrun-lowers into CH-17g-final as a single coupled rung.  Gates re-confirmed byte-identical post-revert: smoke ×6 PASS, isolation PASS, unified_broker PASS=49.  Files (all reverted): `src/runtime/interp/coro_runtime.c` (probe).  Awaits Lon decision on sequencing.

**CH-17g-runtime-bridge-DESIGN LANDED sess 2026-05-09** — `docs/CHUNKS-step17g-runtime-bridge-design.md` records the architectural investigation behind the bridge rung.  Empirical mechanism of the FATAL: `--sm-run --dump-sm` shows the chunk emits `SM_PUSH_LIT_S "hello..." / SM_CALL_FN s="write" nargs=1 / SM_POP / SM_RETURN` — clean lowering, no IR leakage.  Dispatch fails because `SM_CALL_FN`'s handler in `sm_interp.c:931–1212` walks: special pseudo-calls → DATA dispatch → SM-native user fn (`sm_label_pc_lookup`) → `INVOKE_fn`/`APPLY_fn` (SNOBOL4 builtin registry).  Icon's `write` lives in `interp_eval.c:309` inside `icn_call_builtin(EXPR_t *call, DESCR_t *args, int nargs)`, which is on the legacy IR-walker path and never registered through `register_fn`.  `APPLY_fn` returns FAIL → chunk surfaces "Error 5: Undefined function or operation."  Two solutions weighed: (A) extract a name-based helper `icn_try_call_builtin_by_name(fn, args, nargs, &out)` covering ~30 EXPR_t-free Icon builtins (write, writes, integer, string, real, char, type, copy, list, table, read, repl, upto, find, any, many, tab, move, match, …) and wire it into `SM_CALL_FN` after `INVOKE_fn`'s FAIL; (B) register Icon builtins in the SNOBOL4 fn table.  Recommendation: A (B causes cross-language pollution — `write` would resolve in SNOBOL4-only programs).  Implementation split into three sub-rungs: **CH-17g-runtime-bridge-1** (refactor: extract `icn_try_call_builtin_by_name`; gate=corpus byte-identical, pure refactor); **CH-17g-runtime-bridge-2** (wire into `SM_CALL_FN`; gate=`--sm-run` of trivial Icon proc produces output identical to `--ir-run`); **CH-17g-runtime-bridge-3** (Raku/SCAN bridges if needed).  Files: `src/driver/interp_eval.{c,h}`, `src/runtime/x86/sm_interp.c`.  No new opcodes, no IR fields, no `sm_lower.c` changes.  Once the bridge lands, CH-17g-irrun-lowers can invoke `sm_lower` from `--ir-run` with chunk dispatch gated behind a runtime flag (off by default to preserve existing behavior; on for end-to-end migration).  Each line-1303 generator kind (E_EVERY, E_SUSPEND, …) becomes its own per-kind migration: a chunk-side producer (lower into pure SM) + a chunk-side consumer (new SM opcode mirroring CH-17f's `SM_BB_ONCE_PROC`).  Gates this session: smoke ×6 PASS, isolation PASS, unified_broker PASS=49 (no source touched).

**CH-17g-runtime-bridge-1 LANDED sess 2026-05-09** — pure refactor as scoped.  Added `int icn_try_call_builtin_by_name(const char *fn, DESCR_t *args, int nargs, DESCR_t *out)` to `src/driver/interp_eval.c` covering `write` and `writes` — verbatim copies of the same logic that lived inline in `icn_call_builtin`.  Reorganised `icn_call_builtin` to delegate to the new helper after the Raku/SCAN dispatch but before the user-proc / clone-or-fallback paths.  Declaration added to `src/driver/interp_private.h` next to the existing `icn_call_builtin` decl.  Behaviour identical to baseline: `icn_call_builtin` still takes `EXPR_t *call` and dispatches the same set of builtins it always did; dispatch order inside it is unchanged (Raku → SCAN → write/writes via helper → user proc → clone-or-fallback); every existing caller (`coro_bb_fnc`, BB adapters in `coro_value.c` and `coro_runtime.c`) sees identical results.  Helper's branches are exact copies of the inlined code they replace; future drift prevented by `icn_call_builtin` calling the helper directly.  Gates byte-identical: smoke ×6 PASS (7/7, 5/5, 5/5, 5/5, 5/5, 4/4), isolation PASS, unified_broker PASS=49, scrip_all_modes PASS=2, Icon corpus `--ir-run` PASS=186 FAIL=47 XFAIL=30 TOTAL=263.  `--sm-run /tmp/probe.icn` still FATALs (helper defined but not yet wired into `SM_CALL_FN`; that's CH-17g-runtime-bridge-2).  Documented in `docs/CHUNKS-step17g-runtime-bridge-1-validation.md`.  Files: `src/driver/interp_eval.c` (+79 −26), `src/driver/interp_private.h` (+5 −0), `docs/CHUNKS-step17g-runtime-bridge-1-validation.md` (new).

**CH-17g-runtime-bridge-2 LANDED sess 2026-05-09** — `icn_try_call_builtin_by_name` wired into `SM_CALL_FN`.  `./scrip --sm-run /tmp/probe.icn` now produces `hello from icon proc`, byte-identical to `--ir-run`.  Multi-call Icon programs (write + writes + numeric arg) also byte-identical.  Important placement subtlety discovered by probe: bridge-DESIGN proposed placing the helper call *after* `INVOKE_fn` returned FAIL, but `APPLY_fn` raises a SNOBOL4 runtime error via `sno_err` and **`longjmp`s out** through `g_sno_err_jmp` when a name is not in any registry — control never returns to the post-INVOKE_fn fallback.  Corrected placement: helper tried *first*, falls through to `INVOKE_fn` only when helper returns 0 (unknown name).  Safety: helper recognises only a fixed list (`write`, `writes` today); for any other name it returns 0 and `INVOKE_fn` runs unchanged.  No SNOBOL4 builtin is shadowed: SNOBOL4 has no `write`/`writes` builtin, helper's recognition list restricted to Icon-unique names.  If a future Icon builtin name overlaps with a SNOBOL4 builtin (none today), order would need to flip back with a `setjmp` wrapper around `INVOKE_fn`.  Single file change: `src/runtime/x86/sm_interp.c` (+24 −1).  Local `extern` decl of the helper inline at the call site (consistent with sm_interp.c's existing style for cross-module externs).  No new opcodes, no IR fields, no `sm_lower.c` changes.  Gates byte-identical: smoke ×6 PASS (7/7, 5/5, 5/5, 5/5, 5/5, 4/4), isolation PASS, unified_broker PASS=49, scrip_all_modes PASS=2, Icon corpus `--ir-run` PASS=186 FAIL=47 XFAIL=30 TOTAL=263.  New gate (Icon `--sm-run` of trivial program byte-identical to `--ir-run`): PASS — explicit success criterion from bridge plan met.  What still doesn't work: `--sm-run` of programs using Icon builtins not yet in helper (read, integer, string, type, copy, list, table, …) still FATAL.  Coverage extends one builtin at a time.  Documented in `docs/CHUNKS-step17g-runtime-bridge-2-validation.md`.
**CH-17g-runtime-bridge-3 LANDED sess 2026-05-09** — extended `icn_try_call_builtin_by_name` from 2 names (`write`, `writes`) to 10, adding eight pure value-transform Icon builtins: `integer`, `real`, `string`, `numeric`, `char`, `ord`, `type`, `image` (0 or 1 arg).  Each new branch is a verbatim port of the equivalent in-eval branch in `interp_eval.c`'s E_FNC switch with two mechanical changes: `interp_eval(e->children[i])` → `args[i-1]` (already pre-evaluated by the SM_CALL_FN handler before invoking the helper), and `return X;` → `*out = X; return 1;` to honour the helper's 1=handled / 0=fall-through contract.  In-eval branches retained — pure additive, legacy `--ir-run` IR-walker path unchanged.  Selection rationale: each of the eight is EXPR_t-free, single-pass arg evaluation, no write-back through `e->children[i]` lvalue identity, no `&pos`/`&subject` mutation, frame-independent.  Builtins explicitly deferred: `read`/`tab`/`move`/`find`/`upto`/`match`/`any`/`many` (scan-context state), `repl`/`left`/`right`/`center`/`reverse`/`map`/`trim`/`copy`/`list`/`table` (multi-arg with default-handling — queue for follow-on), `push`/`pop`/`pull`/`get`/`put` (write back through children[1] lvalue identity — need EXPR_t-aware path or per-kind chunk migration under CH-17h).  Gates byte-identical to baseline: smoke ×6 PASS (7/7, 5/5, 5/5, 5/5, 5/5, 4/4), isolation PASS, unified_broker PASS=49 FAIL=0, scrip_all_modes PASS=2 FAIL=0, Icon corpus `--ir-run` PASS=186 FAIL=47 XFAIL=30 TOTAL=263, csnobol4 Budne PASS=50 FAIL=100 SKIP=8 (matches CH-17g-call-sites baseline; environmental variance vs CH-17f's recorded 61).  New gate (trivial Icon proc using all 8 new builtins, `--sm-run` byte-identical to `--ir-run`): PASS — 11 calls covering all eight names.  `test/icon/generators.icn` now byte-identical between modes (previously diverged on `--sm-run`); `test/icon/meander.icn` and `test/icon/queens.icn` still diverge under `--sm-run` because they use unbridged builtins (`read`, `tab`, `find`, `move`, `repl`, `list`).  Single file change: `src/driver/interp_eval.c` (+162 −1).  No new opcodes, no IR fields, no `sm_lower.c` changes, no `sm_interp.c` changes (bridge-2's wire-up at SM_CALL_FN already routes every name through the helper).  Documented in `docs/CHUNKS-step17g-runtime-bridge-3-validation.md`.  one4all @ `57a90476`.

**CH-17g-runtime-bridge-4 LANDED sess 2026-05-09** — extended `icn_try_call_builtin_by_name` from 10 names (post-bridge-3) to 27 by adding 17 more EXPR_t-free Icon builtins: multi-arg pure transforms (`repl`, `reverse`, `map`, `trim`, `left`, `right`, `center`), math (`abs`, `max`, `min`, `sqrt`), containers (`copy`, `list`, `table`), I/O (`read`, `reads`), process control (`stop`).  Each branch verbatim-ported from in-eval E_FNC switch with `interp_eval(e->children[i])` → `args[i-1]`; in-eval branches retained; pure additive.  Subtleties handled inline: `trim`'s `g_lang` read (safe — `polyglot_execute` sets `g_lang=1` before any Icon proc in either mode); `max`/`min` loop bounds (0-indexed `args[]` vs 1-indexed `children[]`); `stop()`'s ignore-args-exit(0) behavior matched verbatim (Icon-spec gap pre-existing).  Gates byte-identical: smoke ×6 PASS (7/7, 5/5, 5/5, 5/5, 5/5, 4/4), isolation PASS, unified_broker PASS=49 FAIL=0, scrip_all_modes PASS=2 FAIL=0, Icon corpus `--ir-run` PASS=186 FAIL=47 XFAIL=30 TOTAL=263.  New gates: 14-call multi-arg probe under `--sm-run` byte-identical to `--ir-run`; `read()` under `--sm-run` byte-identical (pipe stdin).  Surfaces (not regressions): `test/icon/queens.icn` now reaches further; FATALs on `SM_ACOMP` opcode (separate `sm_interp` gap, not bridge); `test/icon/meander.icn` reaches further, FATALs on `tab()` (scan-context family — bridge-5).  Single file change: `src/driver/interp_eval.c` (+261 −1).  No new opcodes, no IR fields, no `sm_lower.c` or `sm_interp.c` changes.  Documented in `docs/CHUNKS-step17g-runtime-bridge-4-validation.md`.  one4all @ `5e526155`.  Cumulative bridge coverage: 27 names (write, writes, integer, real, string, numeric, char, ord, type, image{0,1}, repl, reverse, map, trim, left, right, center, abs, max, min, sqrt, copy, list, table, read, reads, stop).  Next rung options: (a) **bridge-5 scan-context** (`tab`/`move`/`find`/`upto`/`match`/`any`/`many` — needs `&pos`/`&subject` care, may interact with existing `scan_try_call_builtin`); (b) **CH-17g-irrun-lowers** (`--ir-run` invokes `sm_lower` so entry_pc resolves regardless of mode); (c) **SM_ACOMP opcode handler** in `sm_interp.c` (surfaced by queens.icn — small fix unblocks array-composition under chunks).

**CH-17g-runtime-bridge-acomp LANDED sess 2026-05-09** — closes the SM_ACOMP runtime gap surfaced by `queens.icn` after bridge-4 widened Icon builtin reach.  Two coupled changes — neither sufficient alone.  (1) Lowering bug at `sm_lower.c:859`: all six numeric comparison EKinds (E_EQ/E_NE/E_LT/E_LE/E_GT/E_GE) collapsed onto a single argument-less `SM_ACOMP` opcode; comparator unrecoverable at runtime.  Emit changed to `sm_emit_i(p, SM_ACOMP, (int64_t)e->kind)` so `a[0].i` carries the operator EKind.  (2) Missing `case SM_ACOMP:` in `sm_interp.c`'s switch — fell through to `default` FATAL "unhandled opcode 82".  Handler added: pops `r`/`l`, coerces SNUL→0 (matches SM_ADD convention), reads via `to_real`-shape promotion, dispatches on the EKind argument, and applies Icon-style relop semantics — on success push the RIGHT operand and set `last_ok=1` (so `every write(2 < (1 to 4))` yields `3, 4`); on failure push FAILDESCR and clear `last_ok`.  `SM_JUMP_F` already tests `last_ok` (sm_interp.c:276) so dispatch wires up automatically.  Mirrors the `NUMREL` macro at `interp_eval.c:3162–3171` line for line.  Default arm in the switch is a safety net for any pre-bridge-acomp SM_Program (unreachable on freshly lowered code).  `sm_prog.c:222` extended to print the operator EKind under `--dump-sm` (`SM_ACOMP i=67` for E_EQ, `i=63` for E_LT).  Stale `sm_codegen.c:1177` comment refreshed: SM_ACOMP/SM_LCOMP were lumped together as "stubbed by design because Icon bypasses sm_lower" — that rationale dissolved in CH-17b' (sess #78); SM_ACOMP entry removed, SM_LCOMP entry narrowed and noted as a follow-on rung (SM_LCOMP has the same shape bug for E_LLT/E_LLE/E_LGT/E_LGE/E_LEQ/E_LNE collapse, deferred to bridge-lcomp).  JIT codegen for SM_ACOMP remains `h_unimpl` (M5 territory; named-FATAL pattern).  Probe verified: `if i = 0 then write("eq"); if i < 1 then write("lt")` under `--sm-run` produces `eq\nlt\n`, byte-identical to `--ir-run` modulo the pre-existing if-then trailing-value leak (a separate, reproducible-without-SM_ACOMP issue, not introduced by this rung).  `queens.icn --sm-run` no longer FATALs on opcode 82 — runs to `0 solutions total.` (a different correctness surface; queens.icn under `--ir-run` ALSO produces wrong output, "Error 3 Erroneous array or table reference" — pre-existing).  Gates byte-identical to baseline: smoke ×6 PASS (7/7, 5/5, 5/5, 5/5, 4/4, 5/5), isolation PASS, unified_broker PASS=49, scrip_all_modes PASS=2 (NET emit SKIP — no ilasm/mono), Icon corpus `--ir-run` PASS=186 FAIL=47 XFAIL=30 TOTAL=263.  Documented in `docs/CHUNKS-step17g-runtime-bridge-acomp-validation.md`.  Files: `src/runtime/x86/sm_lower.c` (1-line behavioural), `src/runtime/x86/sm_interp.c` (+39 SM_ACOMP handler), `src/runtime/x86/sm_prog.c` (1-line print case), `src/runtime/x86/sm_codegen.c` (comment refresh, no behavioural change).  Next rung options unchanged from bridge-4's list, minus (c): (a) **bridge-5 scan-context** (`tab`/`move`/`find`/`upto`/`match`/`any`/`many`); (b) **CH-17g-irrun-lowers** (`--ir-run` invokes `sm_lower` so `entry_pc` resolves regardless of mode); (d) **bridge-lcomp** (sibling of acomp for SM_LCOMP — string relops have the same shape bug; surfaces will arrive when corpus reaches one under `--sm-run`).

**CH-17g-runtime-bridge-lcomp LANDED sess 2026-05-09** — sibling of bridge-acomp; closes the asymmetry that doc explicitly flagged as a follow-on rung.  Mirrors bridge-acomp for the string/lexicographic relops: same shape bug, same fix pattern.  (1) Lowering at `sm_lower.c:872` had collapsed all six string comparison EKinds (E_LLT/E_LLE/E_LGT/E_LGE/E_LEQ/E_LNE) onto a single argument-less `SM_LCOMP`; emit changed to `sm_emit_i(p, SM_LCOMP, (int64_t)e->kind)`.  (2) `case SM_LCOMP:` added to `sm_interp.c` switch: pops `r`/`l`, runs `strcmp(VARVAL_fn(l), VARVAL_fn(r))`, dispatches on EKind, applies Icon-style relop semantics — on success push the RIGHT operand and set `last_ok=1`; on failure push FAILDESCR and clear `last_ok`.  Mirrors the STRREL macro at `interp_eval.c:3184–3194` line for line.  Default arm in the switch is a safety net for any pre-bridge-lcomp SM_Program (unreachable on freshly lowered code).  No change to `sm_prog.c` (SM_LCOMP was already in the `i=` print case, predating bridge-acomp).  `sm_codegen.c` comment further refreshed: SM_LCOMP entry removed from the "stubbed by design" list and folded into the bridge-acomp/lcomp closing note (JIT codegen still `h_unimpl` for both — M5 territory).  No corpus surface today (no Icon program in `test/icon` reaches a string relop under `--sm-run`); landed preventatively for symmetry with bridge-acomp — half-fixed pair would leave `sm_codegen.c` telling an inconsistent story to the next reader.  Probe verified: `s := "abc"; if s == "abc" then write("seq"); if s << "abd" then write("slt"); if s >> "abb" then write("sgt")` under `--sm-run` produces `seq\nslt\nsgt\n`, byte-identical to `--ir-run` modulo the pre-existing trailing-value-after-if-then leak documented in bridge-acomp (same artifact, not introduced by this rung).  Gates byte-identical to baseline: smoke ×6 PASS (7/7, 5/5, 5/5, 5/5, 4/4, 5/5), isolation PASS, unified_broker PASS=49, scrip_all_modes PASS=2, Icon corpus `--ir-run` PASS=186 FAIL=47 XFAIL=30 TOTAL=263.  Documented in `docs/CHUNKS-step17g-runtime-bridge-lcomp-validation.md`.  Files: `src/runtime/x86/sm_lower.c` (1-line behavioural), `src/runtime/x86/sm_interp.c` (+47 SM_LCOMP handler), `src/runtime/x86/sm_codegen.c` (comment refresh).  Next rung options: (a) **bridge-5 scan-context** (`tab`/`move`/`find`/`upto`/`match`/`any`/`many` — needs `&pos`/`&subject` care, may interact with existing `scan_try_call_builtin`); (b) **CH-17g-irrun-lowers** (`--ir-run` invokes `sm_lower` so `entry_pc` resolves regardless of mode — a structural change to `scrip.c:557–561` non-SNO `--ir-run` dispatch; awaiting Lon decision per CH-17g-final-SURVEY's recommendation to split CH-17g-final's preconditions into runtime-bridge and irrun-lowers rungs).
