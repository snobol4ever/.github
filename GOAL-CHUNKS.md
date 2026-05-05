# GOAL-CHUNKS — Eliminate SM_PUSH_EXPR; deferred expressions become compiled SM chunks

**Repo:** one4all (primary) + .github (this file)
**Done when:** SM_PUSH_EXPR opcode is deleted from the codebase. The DT_E
descriptor (or its successor) carries a compiled SM chunk addressed by
entry-pc, never an `EXPR_t*`. The proc_table and g_pl_pred_table hold
SM entry-pcs, never raw IR pointers. The BB broker drives SM
sub-programs, not EXPR_t subtrees. After `sm_lower` returns, IR is
freed unconditionally for all six frontends. Mode 4 (`--jit-emit
--x64`) becomes implementable: the emitted asm executable contains
no EXPR_t walker because no code in the runtime walks EXPR_t any more.

---

## ⚠️ Truth-telling preamble — what this goal exists to fix

Recorded here so future sessions don't slip back into wishful framing.

1. **SM_PUSH_EXPR ships raw IR pointers.** RS-9b's `expr_gc_clone` made
   the storage GC-safe, but the cloned pointer is still un-lowered IR.
   Whatever consumes `DT_E` (pattern matcher, EVAL, BB broker) has to
   walk EXPR_t to do its job — that walker is an IR interpreter, no
   matter what file it lives in.

2. **`proc_table[i].proc` and `g_pl_pred_table` hold raw `EXPR_t*`
   pointers into the original IR.** These are populated by
   `polyglot_init` (`src/driver/polyglot.c` lines 171, 188) and never
   cloned. They are NOT carried through SM at all — they are a side
   channel that bypasses the SM_Program entirely. The code_free gate
   in `scrip_sm.c` (`if (lang_mask == (1u << LANG_SNO))`) explicitly
   keeps IR alive for non-SNO programs because of these tables.

3. **`coro_call(EXPR_t *proc, ...)` walks `proc->children[]`.** That
   includes parameter names (line 372–374), E_GLOBAL declarations
   (376–381), and an in-place mutation of E_VAR.ival via
   `icn_scope_patch` (387). This is an IR tree walk by any other name.
   The fact that it lives in `coro_runtime.c` (in the isolation-gate
   file set) does not change what it is.

4. **The BB engine is an IR walker.** `coro_eval(EXPR_t*)`,
   `coro_drive`, `bb_eval_value`, `bb_exec_stmt`, `pl_pred_table_lookup`
   — all of them ultimately switch on `e->kind` and recurse over
   `e->children[]`. RS-22/RS-23/RS-24 closed the path from these files
   into `interp_eval`, but did not close the path from these files
   into IR walking. They walk their own IR; they just don't call the
   "official" IR walker any more. The isolation gate's grep does not
   catch this and could not — it is a structural property, not a
   symbol-call property.

5. **The four-mode framing is currently aspirational, not realized.**
   Mode 4 (`--jit-emit --x64`) doesn't exist in the driver
   (`scrip.c:145–148` parses three modes plus `--monitor`). It is
   referenced in test scripts (`test_regression_full_corpus.sh`,
   `test_smoke_scrip_all_modes.sh`) under the SKIP path. Until items
   1–4 are fixed, mode 4 cannot be implemented: a separately emitted
   asm executable cannot reach into the SCRIP host process for
   EXPR_t walkers, and there is no other way to evaluate non-SNO
   programs today.

6. **What "isolation gate PASS" actually means.** It means no SM-mode
   runtime file calls a hard-coded list of five symbols
   (`execute_program`, `interp_eval`, `interp_eval_pat`,
   `interp_eval_ref`, `call_user_function`). It does NOT mean the SM
   runtime is structurally independent of IR. The proc_table side
   channel and the EXPR_t-driven BB engine are entirely outside the
   gate's vocabulary.

This goal closes items 1–4. Item 5 (mode 4 implementation) becomes
straightforward after this goal is done; it is filed as the
immediately-following goal.

---

## Architectural target — the chunk-and-pc representation

**The DT_E descriptor (or its successor DT_CHUNK / DT_THUNK) carries:**

```c
typedef struct {
    int  entry_pc;    /* index into SM_Program::instrs[] where the chunk starts */
    int  arity;       /* args expected on the SM value stack at entry; 0 for thunk */
    /* RESERVED for future env capture; for now lexical scope is via the
     * frame stack which the chunk inherits from its caller. */
} SmChunk_t;
```

**Lowering pattern.** Every site that currently emits
`emit_push_expr(p, e)` (10 sites in `sm_lower.c`, listed in CH-1
below) becomes:

```
   SM_JUMP    skip_chunk_NN
chunk_NN:
   <lowered SM ops for the deferred body — same recursive lower_expr>
   SM_RETURN
skip_chunk_NN:
   ...
   SM_PUSH_CHUNK  chunk_NN, arity     ; was SM_PUSH_EXPR
```

The chunk is real SM the dispatch loop already knows how to run.
Forward-jump-around is the same idiom the label table already handles.

**Consumption pattern.** Every site that currently consumes a `DT_E`
by walking EXPR_t becomes:

- **EVAL() / `*expr` / pattern args** → `SM_CALL_CHUNK` pops the
  chunk descriptor, pushes a return frame, sets pc to `entry_pc`, runs
  until `SM_RETURN`, leaves the result on the value stack.
- **BB pump / once / suspend-resume** → the BB engine takes an
  `SmChunk_t` (or `entry_pc`) and drives it. Each tick is "advance pc
  until SM_SUSPEND or SM_RETURN." That IS what a coroutine is.

**Proc/pred table change.** `proc_table[i]` stores `entry_pc` (the pc
of the procedure body's lowered chunk). `g_pl_pred_table` stores the
same. `coro_call(EXPR_t *proc, ...)` becomes `sm_call_proc(int
entry_pc, DESCR_t *args, int nargs)`.

**Result after this goal:** SM is the program. Every executable
fragment — top-level statements, procedure bodies, predicate clauses,
deferred expressions, generators — is a labeled SM chunk. The IR is
the lowering input only; after `sm_lower`, IR is gone.

---

## Migration strategy — two-system swap pattern

This is too large to land in one piece. We use a long-running
two-system pattern: the new chunk-based runtime is built alongside
the old EXPR_t-based runtime, validated under a feature flag, then
the old code is deleted. Specifically:

- **Add new opcodes (SM_PUSH_CHUNK, SM_CALL_CHUNK, eventually
  SM_SUSPEND_CHUNK) without removing SM_PUSH_EXPR.** Both can coexist
  during migration. Chunks are the new way; EXPR_t handoff is the
  old way; a feature flag controls which sm_lower emits.
- **Migrate consumers first, producers second.** Every consumer of
  DT_E learns to handle the chunk shape (a small `if (chunk_pc ==
  -1) { /* old IR-pointer path */ } else { /* new chunk-call path */
  }` switch). Once consumers handle both, the lowering can switch.
- **Migrate one frontend at a time.** SNOBOL4 first (smallest blast
  radius — its SM_PUSH_EXPR usage is leaf-deferral, not whole-tree
  handoff). Then Icon's main() synthesis (a single trivial site).
  Then Icon generators. Then Prolog. Then proc/pred tables. Then
  delete old code.
- **Gates run on every rung.** No rung lands without smoke ×6,
  isolation gate, csnobol4 Budne, Icon corpus 263, unified_broker,
  scrip_all_modes (all three modes), all green.
- **Parallel work where safe.** Rungs CH-3 (SNOBOL4), CH-5 (Icon
  main), CH-6 (Raku CASE) touch disjoint code paths and can be
  tackled by separate sessions in parallel. Rungs that touch the BB
  engine (CH-7, CH-8, CH-9) must be serialized — they share the same
  bb_broker.c and coro_runtime.c.

---

## Architectural decision (CH-DECISION-0, binding)

The BB engine becomes SM-driven. It will eventually take an
`SmChunk_t` (or entry_pc + suspend/resume protocol) and step the SM
sub-program. The BB engine does NOT take an EXPR_t after this goal.

This is the part that absolutely costs effort: every Icon generator
kind (E_EVERY, E_TO, E_TO_BY, E_SUSPEND, E_BANG_BINARY, E_LCONCAT,
E_LIMIT, E_RANDOM, E_SECTION*, E_CASE) and every Prolog backtracking
kind (E_CHOICE, E_CLAUSE, E_CUT, E_UNIFY, E_TRAIL_MARK,
E_TRAIL_UNWIND) needs a per-kind SM lowering that uses SM_SUSPEND /
SM_RESUME instead of letting BB walk the subtree.

There is no shortcut. This is the work that was avoided in RS-20 and
papered over by SM_PUSH_EXPR. We do it now.

---

## Closed rungs

(none yet — this goal is brand new in session #62, 2026-05-05)

---

## Active rungs

### Phase 0 — Survey + scaffolding

- [ ] **CH-0a — Audit all 10 `emit_push_expr` call sites in `sm_lower.c`.**
  Document each: line number, source EXPR_t kind, immediate consumer
  in the dispatch loop (`SM_PAT_CAPTURE_FN_ARGS`, `SM_BB_PUMP`,
  `SM_BB_ONCE`, etc.), what the consumer reads off the EXPR_t.
  Output: `docs/CH-0a-push-expr-audit.md`.

  Known sites (from session #62 reconnaissance):
  | Line  | Source kind                  | Consumer            | Bucket |
  |-------|------------------------------|---------------------|--------|
  | 326   | E_FNC sub-args (pat ctx)     | SM_PAT_CAPTURE_FN_ARGS | SNO   |
  | 345   | E_FNC sub-args (pat ctx)     | SM_PAT_CAPTURE_FN_ARGS | SNO   |
  | 386   | E_FNC sub-args (pat ctx)     | SM_PAT_CAPTURE_FN_ARGS | SNO   |
  | 470   | pattern non-QLIT arg         | SM_PAT_*            | SNO    |
  | 573   | E_DEFER (`*expr`)            | EVAL / pattern thaw | SNO    |
  | 975   | E_EVERY/TO/TO_BY/SUSPEND/    | SM_BB_PUMP          | ICN    |
  |       | BANG_BINARY/LCONCAT/LIMIT/   |                     |        |
  |       | RANDOM/SECTION*              |                     |        |
  | 986   | E_CHOICE/CLAUSE/CUT/UNIFY/   | SM_BB_ONCE          | PL     |
  |       | TRAIL_MARK/TRAIL_UNWIND      |                     |        |
  | 993   | E_CASE                       | SM_BB_PUMP          | RAKU   |
  | 1232  | synthesised main() E_FNC     | SM_BB_PUMP          | ICN    |

- [ ] **CH-0b — Audit all consumers of `DT_E`.** Every place that
  receives a DT_E descriptor and calls `interp_eval` or
  `interp_eval_pat` or `coro_eval` on the carried `EXPR_t*`. Output:
  `docs/CH-0b-dt-e-consumer-audit.md`.

- [ ] **CH-0c — Audit `proc_table` and `g_pl_pred_table` reach.**
  Every read of `proc_table[i].proc` and every reach into
  `g_pl_pred_table` entries' EXPR_t fields. Includes coro_call,
  `pl_pred_table_lookup` callers, the icn_record_register path,
  static-var initialization, scope_patch. Output:
  `docs/CH-0c-proc-pred-table-audit.md`.

- [ ] **CH-0d — Define new opcodes.** Add to `sm_prog.h`:
  ```c
  SM_PUSH_CHUNK,    /* push DT_E with SmChunk_t {entry_pc, arity}; a[0].i=entry_pc, a[1].i=arity */
  SM_CALL_CHUNK,    /* pop chunk descriptor, push frame, jump to entry_pc, run to SM_RETURN */
  SM_SUSPEND_CHUNK, /* yield value+resume_pc to BB broker; sets last_ok=1 */
  /* SM_PUSH_EXPR remains during migration */
  ```
  Add unimplemented stubs in sm_interp.c and sm_codegen.c that
  abort with a named FATAL ("SM_PUSH_CHUNK reached but lowering
  hasn't migrated yet"). Lets us land the opcode definitions
  separately from any consumer.

- [ ] **CH-0e — Define `SmChunk_t` and update `DESCR_t` carrier.**
  Today DT_E uses `descr.ptr` for `EXPR_t*`. Choose:
    (i) Reuse descr.ptr but point at a heap-allocated `SmChunk_t`
        struct. Simple, costs an allocation per push, but works.
    (ii) Pack `{entry_pc:32, arity:16, flags:16}` into `descr.i`.
        Faster, no alloc, but constrains entry_pc to 32 bits.
    (iii) Add new descr fields. Larger DESCR_t — touches everything.
  Recommend (ii) for chunks-by-value; (i) for legacy compatibility
  during the swap. Decide in this rung; document choice.

- [ ] **CH-0f — Feature flag.** Add `--chunks` / `-DCHUNKS_ENABLED`
  build-time or env-time switch that toggles whether `sm_lower`
  emits SM_PUSH_EXPR (legacy) or SM_PUSH_CHUNK (new). Off by
  default until enough consumers handle the new shape. After this
  goal lands the flag is removed.

### Phase 1 — SNOBOL4 leaf-deferral migration (smallest blast radius)

These five sites lower small known-shape subexpressions for
SNOBOL4-side consumption. Migrate in two halves: consumers learn
both shapes (CH-1), then producer flips (CH-2).

- [ ] **CH-1 — Teach SNOBOL4 DT_E consumers to call chunks.**
  Sites that currently take a DT_E and `interp_eval_pat` or
  `interp_eval` it: pattern argument capture
  (SM_PAT_CAPTURE_FN_ARGS implementation, `snobol4_pattern.c`),
  EVAL builtin handler, `*expr` thaw. Each grows a branch:
  ```c
  if (descr.v == DT_E && is_chunk(descr)) {
      sm_call_chunk_at_pc(chunk.entry_pc, ...);
      result = sm_pop(...);
  } else if (descr.v == DT_E) {
      /* legacy IR-pointer path */
      result = interp_eval((EXPR_t *)descr.ptr);
  }
  ```
  Both work after this rung. Gates: ×6 smoke + isolation +
  csnobol4 Budne + Icon corpus + unified_broker, all paths still
  green via the legacy branch.

- [ ] **CH-2 — Switch SNOBOL4 sm_lower sites to emit SM_PUSH_CHUNK.**
  Lines 326, 345, 386, 470, 573 in `sm_lower.c`. Each emits
  forward-jump + chunk-body + SM_RETURN + SM_PUSH_CHUNK. The
  legacy path (CH-1) is now unused for SNOBOL4 patterns; verify
  by confirming no DT_E carrying an EXPR_t* originates from these
  sites at runtime (instrumented build). Gates: ×6 smoke +
  isolation + csnobol4 Budne, all green via the new path.

### Phase 2 — Icon main() and Raku CASE (single-site swaps)

These two are the simplest BB-handoff cases — single
known-shape subtree per call, no generator state machine
needed beyond what the existing BB pump already provides.

- [ ] **CH-3 — Migrate Icon main() synthesis.** sm_lower.c:1232
  currently emits `SM_PUSH_EXPR(<call-main E_FNC>) + SM_BB_PUMP`.
  Replace with: lower the body of `main` as a chunk (entry_pc),
  emit `SM_CALL_CHUNK entry_pc, 0` directly. No BB pump needed
  for top-level main — it runs to SM_RETURN. (The BB pump was
  there because the consumer was the IR-tree-walking BB engine.)

  Risk: main() may itself contain generators that need BB pump.
  Those go through CH-7/8/9 (per-kind generator lowering) before
  this works. Decide in CH-3a whether to land CH-3 first with a
  partial scope ("main bodies that don't transitively use
  generators") or wait until CH-7+ are done.

- [ ] **CH-4 — Migrate Raku CASE.** sm_lower.c:993. The CASE
  body is a small bounded set of arms. Lower each arm as a
  chunk; emit a dispatch chain (SM_PEEK / SM_EQ / SM_CALL_CHUNK
  per arm). Doesn't need BB at all — CASE is not goal-directed.

### Phase 3 — Per-kind SM lowering for Icon generators (CH-DECISION-0)

This is the largest mechanical chunk. Each kind gets a per-kind
recipe that turns an EXPR_t subtree into an SM sub-program with
explicit SUSPEND/RESUME points. The BB broker continues to drive
EXPR_t for un-migrated kinds during the swap; once all are
migrated, BB switches to driving SM PCs.

- [ ] **CH-5a — Add SM_SUSPEND / SM_RESUME opcodes.** Define the
  yield protocol: SM_SUSPEND pushes the current pc + value onto
  a broker-visible state slot; SM_RESUME re-enters at saved pc.
  Gate: a hand-written test SM program that yields three values
  and resumes between each, driven by a stub broker.

- [ ] **CH-5b — Add `bb_broker_drive_sm(int entry_pc)` alongside
  the existing `bb_broker_drive_expr(EXPR_t*)`.** The new entry
  point pumps an SM sub-program. Both coexist during migration.

- [ ] **CH-6a — Migrate `E_TO` / `E_TO_BY`.** Simplest generators.
  Lowering: init iterator, SM_SUSPEND value, increment, repeat
  until done. Replace the SM_PUSH_EXPR + SM_BB_PUMP pair at
  sm_lower.c:975 with chunk emission + SM_PUSH_CHUNK +
  `SM_BB_PUMP_SM` (the chunk-driving variant). Gates: Icon
  corpus subset that uses `to`/`to-by`; full corpus stays green
  via legacy path for un-migrated kinds.

- [ ] **CH-6b — Migrate `E_EVERY`.** The wrapping construct.
  Body becomes a chunk; `every` lowering invokes the body chunk
  per yielded value from its argument generator. Gates: full
  Icon corpus subset using `every`.

- [ ] **CH-6c — Migrate `E_BANG_BINARY` (`!container`).** Iterates
  string / list / table elements. Per-shape suspend protocol.

- [ ] **CH-6d — Migrate `E_SUSPEND` (procedure-level suspend).**
  This one is delicate — it's the user-visible Icon `suspend`
  keyword inside a procedure. The procedure body is itself a
  chunk; SM_SUSPEND inside it yields to the procedure's caller.

- [ ] **CH-6e — Migrate `E_LCONCAT`, `E_LIMIT`, `E_RANDOM`,
  `E_SECTION` / `E_SECTION_PLUS` / `E_SECTION_MINUS`.** Bundle
  into one rung — they're shorter recipes once the pattern from
  CH-6a–d is established.

- [ ] **CH-6f — Delete `bb_broker_drive_expr`.** All Icon
  generator kinds are migrated. The EXPR_t-driving entry point
  is unreferenced. Removing it forces any straggler caller to
  fail at compile time.

### Phase 4 — Prolog clauses (CH-DECISION-0)

Same shape as Phase 3, but for the Prolog kinds. Smaller in
volume (6 kinds vs. ~10).

- [ ] **CH-7a — Migrate `E_CHOICE` (alternation / cut handling).**
- [ ] **CH-7b — Migrate `E_CLAUSE` (predicate body).**
- [ ] **CH-7c — Migrate `E_UNIFY`, `E_CUT`, `E_TRAIL_MARK`,
  `E_TRAIL_UNWIND`.**
- [ ] **CH-7d — Migrate `g_pl_pred_table` to entry-pcs.**
  `pl_pred_table_insert(name, entry_pc)` instead of `(name,
  EXPR_t *)`. `pl_pred_table_lookup` returns an entry_pc.

### Phase 5 — Proc table (Icon/Raku/Snocone procedures)

- [ ] **CH-8a — Lower each Icon/Raku/Snocone procedure body as a
  named SM chunk.** During `polyglot_init`, instead of recording
  `proc_table[i].proc = proc_expr`, lower `proc_expr`'s body
  via sm_lower into the SM_Program (as a labeled chunk) and
  record `proc_table[i].entry_pc`.

- [ ] **CH-8b — Migrate `coro_call(EXPR_t*, args, nargs)` to
  `sm_call_proc(int entry_pc, args, nargs)`.** Frame setup
  same; body execution goes through the SM dispatch loop on
  the chunk. `icn_scope_patch` (the in-place IR mutation) is
  no longer reachable — frame slot resolution happens at lower
  time.

- [ ] **CH-8c — Delete proc_table's `EXPR_t *proc` field.** Only
  entry_pc + name + arity remain. polyglot.c stops storing IR
  pointers entirely.

### Phase 6 — Free IR for all frontends

- [ ] **CH-9a — Verify no remaining EXPR_t reach from the SM
  runtime gate file set.** New sub-rule in
  `test_isolation_ir_sm.sh`: forbid `EXPR_t *` declarations in
  function signatures of the gated files. Currently they're
  full of them. After CH-1 through CH-8 land, none should
  remain.

- [ ] **CH-9b — Lift the `lang_mask == (1u << LANG_SNO)` gate on
  `code_free` in `scrip_sm.c`.** Becomes unconditional
  `code_free(prog); label_table_clear_stmts();`.

- [ ] **CH-9c — Delete `SM_PUSH_EXPR`.** Remove from sm_prog.h
  enum, from sm_interp.c handler, from sm_codegen.c handler,
  from sm_prog.c name table, from `expr_gc_clone` callers in
  `emit_push_expr` (which also disappears). The opcode is gone.

- [ ] **CH-9d — Delete `expr_gc_clone` if unused.** It was added
  by RS-9b for `emit_push_expr`. After CH-9c it may have no
  callers; if so, delete it and `ir_clone.c` shrinks.

- [ ] **CH-9e — Update isolation gate.** Add the new structural
  rule: gated files may not contain `EXPR_t` in any code (only
  in comments referencing historical state). Promote any
  remaining files to the gate.

### Phase 7 — Mode 4 unblock

- [ ] **CH-10 — File `GOAL-MODE4-EMIT.md` as the next goal.**
  After CH-9e lands, the runtime is ready: SM is the program,
  no IR walker is needed at runtime, operands are the only
  remaining mode-4 prerequisite (RS-28-style operand-bake
  codegen). That goal is what implements `--jit-emit --x64` /
  `--wasm` / `--jvm` / `--net` for all six frontends.

---

## Parallel-work plan

Sessions can work in parallel on these rungs without conflict:

- **Track A (SNOBOL4):** CH-0a → CH-0d → CH-0e → CH-0f → CH-1 → CH-2.
  Touches sm_lower.c (5 lines of source change), sm_interp.c (+1
  case), snobol4_pattern.c (+ chunk branch). Independent of all
  other tracks.

- **Track B (Icon main / Raku CASE):** CH-3 → CH-4. Touches
  sm_lower.c at lines 1232 and 993, plus CASE-specific support.
  Can run in parallel with Track A. Note: CH-3 may need to wait
  on Phase 3 if main bodies use generators.

- **Track C (Generator infrastructure):** CH-5a → CH-5b. Adds
  SM_SUSPEND/RESUME and the new BB driver entry. Pure addition;
  doesn't touch existing code paths. Can run in parallel with
  Tracks A and B.

- **Track D (Per-kind generator migrations):** CH-6a → CH-6f.
  Serializes after Track C. Within the track, kinds can be
  parallel-attacked (CH-6a and CH-6c don't share code).

- **Track E (Prolog):** CH-7a → CH-7d. Parallels Track D after
  Track C lands.

- **Track F (Proc table):** CH-8a → CH-8c. Depends on Track D
  partially; can start with statically-typed procedure bodies
  that don't use generators.

- **Track G (Cleanup + delete):** CH-9a → CH-9e → CH-10. Strict
  serial after all migrations land.

A single session typically takes one rung within one track. Two
parallel sessions can each pick up an unblocked rung from their
chosen track. The .github goal file is the synchronization point
— each session updates the rung's checkbox and watermark hash on
landing.

---

## Per-rung gates (apply to every CH-* rung unless noted)

```
smoke ×6 (snobol4 7/7, icon 5/5, prolog 5/5, raku 5/5, snocone 5/5, rebus 4/4)
isolation gate PASS
csnobol4 Budne PASS≥34
Icon corpus 263 (no PASS regression vs baseline 186/47/30)
unified_broker PASS≥48
scrip_all_modes PASS in --ir-run, --sm-run, --jit-run
```

After CH-9e specifically, also:
```
SM_PUSH_EXPR appears in zero source files (verify by grep)
EXPR_t appears in zero gated runtime file signatures (verify by grep)
```

---

## Definitions

- **chunk** — a labeled, lowered SM sub-program. Has an entry pc
  in SM_Program::instrs[] and ends in SM_RETURN (or SM_SUSPEND
  for generator chunks). Equivalent to a closure body once it
  carries an environment.

- **deferred expression** — a value that, when consumed, produces
  another value (or a stream of them). Currently represented as
  `DT_E { ptr = EXPR_t* }`; after this goal, as
  `DT_E { ptr = SmChunk_t* }` or `{ entry_pc, arity }` packed into
  the descriptor.

- **two-system swap** — old and new co-exist behind a flag; new
  is validated under both code paths producing identical output;
  old is deleted in a final rung.

- **isolation gate** — `scripts/test_isolation_ir_sm.sh`. Will be
  strengthened by CH-9e to forbid EXPR_t in gated file signatures
  in addition to its current symbol-call rules.

---

## ⚠️ Session #62 handoff note — REVISIONS REQUIRED at next session start

The plan above was drafted late in session #62 with context near 95%.
Lon and Claude continued discussing it after the file was committed
and agreed on revisions that the next session must apply BEFORE
starting CH-0a.  Recorded here so the revisions are not lost.

### Revision 1 — pure sequential, drop the parallel-tracks framing

Sessions are serial, not parallel.  Replace the "Parallel-work plan"
section (the seven-track list A–G) with a single linear sequence.
Side effects:
  - Collapse some of CH-1 / CH-2 into a single rung where practical
    (consumer + producer flip + delete legacy branch in one commit)
    since no parallel session will be holding the legacy branch open.
  - The feature flag (`--chunks` / `-DCHUNKS_ENABLED`) becomes
    transient within a single rung instead of long-lived.  Probably
    fold CH-0f into CH-0d.
  - Phase 0's audit rungs (CH-0a, CH-0b, CH-0c) can collapse into the
    preamble of the first execution rung instead of landing as
    separate commits.
  - Net: roughly 6 fewer rungs in the goal file, same destination,
    cleaner linear history.

### Revision 2 — SNOBOL4 (and Snocone) FIRST, declare done at end of Phase 1

Restructure the phase ordering around a SNOBOL4-first milestone.

  - **Phase 1: SNOBOL4 lowered completely.**  After Phase 1, pure-SNO
    programs in modes 2/3 are structurally isolated from EXPR_t —
    the SM-side pattern matcher walks chunks, not IR.  SM_PUSH_EXPR
    still exists in the codebase (kept alive temporarily for
    Icon/Prolog/Raku/Rebus) but has zero SNOBOL4 emission sites.
    `code_free` for pure-SNO already works and is unchanged.
    **Mode-4 emission becomes implementable for pure-SNOBOL4 at this
    point** — that's a shippable milestone before the Icon/Prolog
    work begins.
  - **Snocone is covered by Phase 1 automatically.**  The Snocone
    frontend produces SNOBOL4-shape IR and rides the LANG_SNO
    lowering path (verified session #62: `polyglot.c` fence parser
    has no LANG_SC tag; Snocone statements are tagged LANG_SNO; the
    sm_lower entry for LANG_SNO is the SNOBOL4 entry).  Migrating
    the five SNOBOL4 emit_push_expr sites in `sm_lower.c` (lines
    326, 345, 386, 470, 573) migrates Snocone with no additional
    rungs.  Phase 1's gate set should explicitly include
    smoke_snocone (already in the standard ×6 set) AND a Snocone
    corpus subset to confirm zero regression.
  - **Phase 2: Icon main() synthesis** (current CH-3).  Single
    trivial site, lands quickly, gives Icon a partial improvement
    before the big generator work.
  - **Phase 3: Raku CASE** (current CH-4).
  - **Phase 4: Generator infrastructure** (SM_SUSPEND/SM_RESUME,
    new BB driver entry).
  - **Phase 5: Per-kind Icon generator migrations** (E_TO, E_TO_BY,
    E_EVERY, E_BANG_BINARY, E_SUSPEND, E_LCONCAT, E_LIMIT, E_RANDOM,
    E_SECTION* — current CH-6a–e).
  - **Phase 6: Prolog clauses and backtracking kinds** (current
    CH-7a–d).
  - **Phase 7: Proc table → entry-pcs** (current CH-8a–c).
  - **Phase 8: Cleanup** — unconditional code_free, delete
    SM_PUSH_EXPR, isolation-gate strengthening (current CH-9a–e).
  - **Phase 9: File `GOAL-MODE4-EMIT.md`** (current CH-10).

The intermediate "mode-4 ready for pure-SNOBOL4 (and Snocone)"
milestone after Phase 1 is the natural checkpoint to stop, reflect,
and possibly ship a pure-SNO mode-4 emitter as a demo before
committing to the Icon/Prolog work which is the bulk.

### Revision 3 — strengthen the truth-telling preamble

The current preamble (items 1–6) emphasizes the non-SNO leaks (proc/
pred-table side channel, BB engine walking IR) and underplays the
**SNOBOL4 DT_E-as-cloned-IR leak**: even for pure-SNO programs in
modes 2/3, the SM-side pattern matcher reads `EXPR_t *frozen =
(EXPR_t *)v.ptr;` at `snobol4_pattern.c:222` and walks
`frozen->kind`, `frozen->nchildren`, `frozen->children[i]`.  RS-9b
made the storage GC-safe, but it's still IR walking inside an
SM-mode runtime file that's IN the isolation gate's file set.  The
gate doesn't catch this because it greps for the five named symbols
(`interp_eval` etc.), not for EXPR_t field accesses.

Add a new item to the preamble making this leak explicit, and
phrase the win after Phase 1 in terms of closing it.  Until Phase 1
lands, do NOT claim SNOBOL4 mode 2/3 is fully isolated from IR —
it's the closest of the six languages but the DT_E leak is real.

### Revision 4 — runtime support library implication for mode 4

The mode-4 destination is "separately emitted asm executable, no
EXPR_t walker in the executable."  That's true.  But the goal file
should also state explicitly that mode-4 executables WILL link
against a runtime support library (`libscrip_rt.so` or equivalent)
that contains C implementations of language-level builtins —
iterator advance, cset membership, string concat, regex/pattern
helpers, etc.  This is a normal language-runtime model (parallels C
runtime, Java runtime, etc.) and isn't a lie — but the current
goal-file framing could read as "fully self-contained executable
with zero runtime deps" which is unrealistic.  Mode-4 emit
generates calls into this support library; the support library is
the home for the per-language semantics that the chunks invoke.

Add a paragraph stating this near the architectural-target section
or in the Phase 9 description.

### Revision 5 — two-system swap cost (smaller now that work is serial)

Original draft said the swap pattern is "old and new co-exist behind
a flag, validated under both, old deleted in final rung."  With
serial sessions, each consumer's `if (is_chunk) { ... } else {
/* legacy IR-pointer path */ ... }` branch can be deleted within the
same rung that flipped its producer.  The dead-code maintenance
window is one rung, not many.  Update the migration-strategy
section to reflect this.

### Revision 6 — first concrete next-session task

After applying Revisions 1–5 to this file (and committing them as a
clean follow-up), the next-after-that session opens CH-0a.  CH-0a
itself stays scoped as written: audit all 10 emit_push_expr call
sites (or just the five SNOBOL4 ones if the audit-rung collapses
per Revision 1), produce `docs/CH-0a-push-expr-audit.md`, and then
proceed to the Phase 1 SNOBOL4 lowering work.

---

End of session #62 handoff note.  Apply revisions before any code
changes; do not start CH-0a until the goal file reads as the
revised plan describes.
