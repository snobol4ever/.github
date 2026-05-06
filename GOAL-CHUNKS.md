# GOAL-CHUNKS — Eliminate SM_PUSH_EXPR; deferred expressions become compiled SM chunks; mode 4 unblocked for all frontends

**Repo:** one4all (primary) + .github (this file) + snobol4dotnet + snobol4jvm + snobol4js (later steps)
**Done when:** SM_PUSH_EXPR opcode is deleted from the codebase.  The
DT_E descriptor (or its successor) carries a compiled SM chunk
addressed by entry-pc, never an `EXPR_t*`.  The proc_table and
g_pl_pred_table hold SM entry-pcs, never raw IR pointers.  The BB
broker drives SM sub-programs, not EXPR_t subtrees.  After
`sm_lower` returns, IR is freed unconditionally for all six
frontends.  Mode 4 (`--jit-emit --x64` and the JVM/.NET/WASM/JS
backends) is implemented for all six frontends because no code in
the runtime walks EXPR_t any more.  Native-host SNOBOL4
interpreters (snobol4dotnet, snobol4jvm, JS) are each extended to
run Snocone, giving multiple bootstrap paths for `scrip.sc`.

---

## Truth-telling preamble — what this goal exists to fix

Recorded so future sessions don't slip back into wishful framing.

1. **SM_PUSH_EXPR ships raw IR pointers.**  RS-9b's `expr_gc_clone`
   made the storage GC-safe, but the cloned pointer is still
   un-lowered IR.  Whatever consumes `DT_E` (pattern matcher, EVAL,
   BB broker) walks EXPR_t — that walker is an IR interpreter, no
   matter what file it lives in.

2. **Even pure SNOBOL4 leaks IR through DT_E in modes 2/3.**
   `snobol4_pattern.c:222` reads `EXPR_t *frozen = (EXPR_t *)v.ptr;`
   and walks `frozen->kind`, `frozen->nchildren`, `frozen->children[i]`.
   That file is in the isolation gate's file set, but the gate
   greps for symbol calls (`interp_eval` etc.), not for EXPR_t
   field accesses.  RS-9b made the storage GC-safe; it did not
   eliminate the walking.  Until Phase 1 of this goal lands, do
   NOT claim SNOBOL4 mode 2/3 is fully isolated from IR.

3. **`proc_table[i].proc` and `g_pl_pred_table` hold raw `EXPR_t*`
   pointers into the original IR.**  Populated by `polyglot_init`
   (`polyglot.c` lines 171, 188) and never cloned.  They are NOT
   carried through SM at all — a side channel that bypasses the
   SM_Program entirely.  The `lang_mask == (1u << LANG_SNO)` gate
   on `code_free` in `scrip_sm.c` keeps IR alive for non-SNO
   programs because of these tables.

4. **`coro_call(EXPR_t *proc, ...)` walks `proc->children[]`.**
   That includes parameter names (line 372–374), E_GLOBAL
   declarations (376–381), and an in-place mutation of E_VAR.ival
   via `icn_scope_patch` (387).  This is an IR tree walk by any
   other name.  Living in `coro_runtime.c` (in the isolation-gate
   file set) does not change what it is.

5. **The BB engine is an IR walker.**  `coro_eval(EXPR_t*)`,
   `coro_drive`, `bb_eval_value`, `bb_exec_stmt`,
   `pl_pred_table_lookup` — all switch on `e->kind` and recurse
   over `e->children[]`.  RS-22/23/24 closed the path from these
   files into `interp_eval`; they did not close the path from
   these files into IR walking.  They walk their own IR; they just
   don't call the "official" walker.

6. **The four-mode framing is currently aspirational.**  Mode 4
   (`--jit-emit --x64`) doesn't exist in the driver
   (`scrip.c:145–148` parses three modes plus `--monitor`).  It is
   referenced in test scripts under SKIP paths.  Until items 1–5
   are fixed, mode 4 cannot be implemented: a separately emitted
   asm executable cannot reach into the SCRIP host process for
   EXPR_t walkers, and there is no other way to evaluate non-SNO
   programs today.

7. **What "isolation gate PASS" actually means.**  No SM-mode
   runtime file calls a hard-coded list of five symbols
   (`execute_program`, `interp_eval`, `interp_eval_pat`,
   `interp_eval_ref`, `call_user_function`).  It does NOT mean
   the SM runtime is structurally independent of IR.  The
   proc_table side channel and the EXPR_t-driven BB engine are
   entirely outside the gate's vocabulary.

This goal closes items 1–5.  Item 6 (mode 4) is implemented as
later phases of this same goal.

---

## Architectural target

**The DT_E descriptor (or its successor) carries:**

```c
typedef struct {
    int  entry_pc;    /* index into SM_Program::instrs[] where the chunk starts */
    int  arity;       /* args expected on the SM value stack at entry; 0 for thunk */
} SmChunk_t;
```

**Lowering pattern.**  Every site that today emits
`emit_push_expr(p, e)` becomes:

```
   SM_JUMP    skip_chunk_NN
chunk_NN:
   <lowered SM ops for the deferred body — same recursive lower_expr>
   SM_RETURN
skip_chunk_NN:
   ...
   SM_PUSH_CHUNK  chunk_NN, arity     ; was SM_PUSH_EXPR
```

The chunk is real SM that the dispatch loop already runs.
Forward-jump-around uses the same label-table machinery already
in place.

**Consumption pattern.**  Every site that today consumes a `DT_E`
by walking EXPR_t becomes:

- **EVAL() / `*expr` / pattern args** → `SM_CALL_CHUNK` pops the
  descriptor, pushes a return frame, sets pc to `entry_pc`, runs
  until `SM_RETURN`, leaves the result on the value stack.
- **BB pump / once / suspend-resume** → the BB engine takes an
  `SmChunk_t` (or entry_pc) and drives it.  Each tick is "advance
  pc until SM_SUSPEND or SM_RETURN."  That IS what a coroutine is.

**Proc/pred table change.**  `proc_table[i]` stores `entry_pc`
(the pc of the procedure body's lowered chunk).  `g_pl_pred_table`
stores the same.  `coro_call(EXPR_t *proc, ...)` becomes
`sm_call_proc(int entry_pc, DESCR_t *args, int nargs)`.

**Result after this goal:**  SM is the program.  Every executable
fragment — top-level statements, procedure bodies, predicate
clauses, deferred expressions, generators — is a labeled SM
chunk.  The IR is the lowering input only; after `sm_lower`, IR
is gone.  Mode 4 emission becomes possible because the emitted
asm executable contains no EXPR_t walker — it contains compiled
chunks plus calls into a runtime support library
(`libscrip_rt.so` or the JVM/.NET/JS host equivalent) that
implements language-level builtins (pattern matcher, NV table,
iterator advance, cset membership, etc.).

---

## Migration strategy

**Sequential, not parallel.**  One session at a time.  Each rung
lands fully — the legacy `if (is_chunk) { ... } else { /* old
EXPR_t path */ }` branch in consumers is deleted within the same
rung that flipped its producer.  No long-lived feature flag, no
parallel branches, no merge collisions.

**Two-system swap is short-lived.**  The new opcodes
(SM_PUSH_CHUNK, SM_CALL_CHUNK, later SM_SUSPEND/SM_RESUME)
coexist with SM_PUSH_EXPR only during the migration of a single
consumer/producer pair.  At rung end, the old branch is gone.

**Per-frontend phasing.**  SNOBOL4 first (smallest blast radius —
its SM_PUSH_EXPR usage is leaf-deferral, not whole-tree handoff).
**Snocone rides SNOBOL4's lowering path automatically** —
verified: `polyglot.c` fence parser has no LANG_SC tag, Snocone
statements are tagged LANG_SNO, the sm_lower entry for LANG_SNO
is the SNOBOL4 entry.  Migrating the five SNOBOL4
emit_push_expr sites migrates Snocone with no additional rungs.
Then Icon main(), Raku CASE, generator infrastructure, per-kind
Icon generators, Prolog, proc/pred tables, cleanup.

**Per-rung gates** (apply to every step unless the step says
otherwise):

```
smoke ×6 (snobol4 7/7, icon 5/5, prolog 5/5, raku 5/5,
          snocone 5/5, rebus 4/4)
isolation gate PASS
csnobol4 Budne PASS≥34
Icon corpus 263 (no PASS regression vs baseline 186/47/30)
unified_broker PASS≥48
scrip_all_modes PASS in --ir-run, --sm-run, --jit-run
```

After step 14 specifically (and all later steps): grep
SM_PUSH_EXPR across the source tree must return zero hits in
non-comment lines; and EXPR_t in gated runtime file signatures
must return zero hits.

---

## Milestone roadmap (high-level reference)

The goal's individual steps below are grouped under these
milestones:

  - **M1** — Steps 1–7: SNOBOL4 + Snocone fully isolated through
    modes 2 (sm-run) and 3 (jit-run).  No EXPR_t reachable from
    any SM-mode runtime path during pure-SNO/Snocone execution.
    First shippable milestone.
  - **M2** — Step 8: Mode 4 x86 emitter for SNOBOL4 + Snocone
    only.  Standalone executable, links against
    `libscrip_rt.so`.  Demonstrates the full pipeline works
    end-to-end before non-SNO complexity is added.
  - **M3** — Steps 9–11: Native-host SNOBOL4 interpreters
    (snobol4dotnet, snobol4jvm, JS) each extended to run
    Snocone.  Three independent bootstrap paths for `scrip.sc`.
    Can run in any order relative to M2.
  - **M4** — Steps 12–18: Icon main(), Raku CASE, generator
    infrastructure, per-kind Icon generators, Prolog clauses,
    proc/pred tables, final SM_PUSH_EXPR delete.
  - **M5** — Step 19: Mode 4 x86 emitter extended to all six
    frontends.
  - **M6** — Steps 20–23: Mode 4 JVM, .NET, WASM, JS backends —
    the full Milestone-3 matrix in PLAN.md.

---

## Steps (in order — execute one per session, sequentially)

### M1 — SNOBOL4 + Snocone isolated through modes 2 and 3

- [x] **Step 1 — Survey + scaffolding.**
  Audit all 10 `emit_push_expr` call sites in `sm_lower.c`
  (lines 326, 345, 386, 470, 573, 975, 986, 993, 1232 — the
  10th is the helper definition at line 39).  For each site,
  record source EXPR_t kind, immediate consumer, what the
  consumer reads from EXPR_t.  Produce
  `docs/CHUNKS-step01-audit.md`.
  Define `SmChunk_t` (struct or descriptor packing — decide in
  this step and document choice).
  Add new opcodes to `sm_prog.h`:
  ```c
  SM_PUSH_CHUNK,    /* a[0].i = entry_pc, a[1].i = arity */
  SM_CALL_CHUNK,    /* pop chunk descriptor, run as sub-program */
  ```
  Add unimplemented stubs in `sm_interp.c` and `sm_codegen.c`
  that abort with named FATAL ("SM_PUSH_CHUNK reached but no
  producer migrated yet").  Build green; opcodes exist; nothing
  emits them yet.  This step is pure addition — no behaviour
  change.  Gates: standard set, all green.

- [x] **Step 2 — Migrate sm_lower.c:573 (E_DEFER / `*expr`).**
  Single-site warm-up.  The simplest emit_push_expr site —
  `*expr` in value context.  Change the lowering: emit
  forward-jump + chunk body (`lower_expr` of the child) +
  SM_RETURN + SM_PUSH_CHUNK.  Update the consumer in
  `snobol4_pattern.c`'s DT_E thaw path (line 222 area) to handle
  both the legacy EXPR_t pointer AND the new chunk descriptor.
  Validate with a SNOBOL4 program that uses `*expr`.  Once green,
  delete the legacy branch in the consumer.  Same rung.  Gates:
  standard set + a focused test for `*expr`.

- [x] **Step 3 — Migrate sm_lower.c:470 (pattern non-QLIT arg).**
  Same shape as step 2 but for the non-QLIT pattern argument
  case.  Two-system swap inside the rung; legacy branch deleted
  at rung end.  Gates: standard set.

- [x] **Step 4 — Migrate sm_lower.c:326 / 345 / 386 (E_FNC sub-args
  in pattern context — three sites with the same shape).**
  Bundle into one rung since they share the consumer
  (SM_PAT_CAPTURE_FN_ARGS).  Migrate consumer to call chunks;
  flip all three producers; delete legacy branch.  Gates:
  standard set + Snocone corpus subset (Snocone hits these via
  pattern-using code).

- [x] **Step 5 — Verify SNOBOL4 + Snocone DT_E carriers no longer
  carry EXPR_t.**  Instrumented build that asserts every DT_E
  pushed by sm_lower at runtime has a chunk shape (arity ≥ 0,
  entry_pc within prog->count).  Run smoke + Snocone corpus +
  csnobol4 Budne.  Zero assertion failures.  This is the
  empirical proof that Phase 1's lowering is complete for
  SNOBOL4-shape programs.  Document outcome in
  `docs/CHUNKS-step05-validation.md`.

- [ ] **Step 6 — Strengthen the isolation gate for SNOBOL4 files.**
  Add a structural rule to `test_isolation_ir_sm.sh`: in
  `snobol4_pattern.c`, `snobol4_invoke.c`, `snobol4_argval.c`,
  `eval_code.c`, forbid `EXPR_t *` casts and `->kind` /
  `->children` / `->nchildren` / `->sval` / `->ival` field
  accesses on EXPR_t-typed expressions.  These four files
  should now read pure SM, no IR walking.  After this step
  passes, SNOBOL4 modes 2/3 are structurally isolated from IR.

- [ ] **Step 7 — M1 milestone close.**  Run the full gate set in
  all three modes (`--ir-run`, `--sm-run`, `--jit-run`) on a
  curated subset: smoke_snobol4, smoke_snocone, csnobol4 Budne
  full, Snocone corpus.  Document that SNOBOL4 + Snocone are
  end-to-end isolated through modes 2/3.  Update PLAN.md step
  ID.  This is the natural pause point: the project can ship
  M1 as a milestone before M2 begins.

### M2 — Mode 4 x86 emitter for SNOBOL4 + Snocone

- [ ] **Step 8 — File `GOAL-MODE4-EMIT.md` and execute it
  to completion.**  (See file — owns both M2 and M5 phases of
  the x86 mode-4 emitter, rungs EM-1 through EM-9 cover this
  step.)  This is itself a multi-rung sub-goal.
  Initial scope: `--jit-emit --x64 file.sno` and `--jit-emit
  --x64 file.sc` produce a standalone asm/binary.  The emitted
  executable links against `libscrip_rt.so` — a runtime support
  library carrying the pattern matcher, NV table, builtins.
  Sub-goal handles operand-bake codegen (RS-28-style work) and
  the `libscrip_rt.so` build / link / package pipeline.
  Other backends and other frontends do NOT extend in this
  step — keep scope tight.  Gates: emitted SNOBOL4 binary
  passes Beauty + smoke_snobol4 source set; emitted Snocone
  binary passes smoke_snocone; gate runs the standalone binary
  via `./prog < input` and compares to scrip in-memory output.

### M3 — Native-host SNOBOL4 interpreters extended to Snocone

These three steps are independent of each other and of M2.
Order them however convenient based on platform availability.

- [ ] **Step 9 — File `GOAL-NATIVE-SNOCONE-DOTNET.md` and execute
  it.**  Extend the in-tree .NET host at `one4all/src/driver/net/`
  (NOT the standalone `snobol4dotnet` org repo) to parse and run
  Snocone source. Done when `scrip.sc` runs end-to-end on the
  .NET interpreter. Provides bootstrap path B for `scrip.sc`.

- [ ] **Step 10 — File `GOAL-NATIVE-SNOCONE-JVM.md` and execute it.**
  Extend the in-tree JVM host at `one4all/src/driver/jvm/` (Java;
  NOT the standalone `snobol4jvm` org repo, which is Clojure) to
  parse and run Snocone source. Done when `scrip.sc` runs
  end-to-end on the JVM interpreter. Provides bootstrap path C.

- [ ] **Step 11 — File `GOAL-NATIVE-SNOCONE-JS.md` and execute it.**
  Extend the in-tree JS host at `one4all/src/driver/js/sno-interp.js`
  (Node) to parse and run Snocone source. Done when `scrip.sc`
  runs end-to-end on Node. Browser support is out of scope for
  this step. Provides bootstrap path D.

### M4 — Icon, Raku, Prolog, Rebus migrate; SM_PUSH_EXPR deleted

- [ ] **Step 12 — Migrate sm_lower.c:1232 (Icon main() synthesis).**
  Single trivial site — synthesised E_FNC for `call_main`.
  Change shape: lower main's body as a chunk during
  polyglot_init's pre-lower pass; emit `SM_CALL_CHUNK
  main_entry_pc, 0` directly (no BB pump needed for top-level
  main once it runs to SM_RETURN).  Note: this only works if
  main's body doesn't transitively use generators.  If it does,
  defer this step until step 14 lands; or scope this step to
  generator-free main bodies and finish it after step 14.
  Decide in the rung.  Gates: standard set + smoke_icon.

- [ ] **Step 13 — Migrate sm_lower.c:993 (Raku CASE).**  CASE
  body is a small bounded set of arms.  Lower each arm as a
  chunk; emit a dispatch chain (SM_PEEK / SM_EQ /
  SM_CALL_CHUNK per arm).  Doesn't need BB at all — CASE is
  not goal-directed.  Gates: standard set + smoke_raku CASE
  tests.

- [ ] **Step 14 — Generator infrastructure.**  Add `SM_SUSPEND`
  and `SM_RESUME` opcodes.  Add `bb_broker_drive_sm(int
  entry_pc)` alongside the existing `bb_broker_drive_expr`.
  Both coexist during the migration of individual generator
  kinds.  Gate: a hand-written test SM program that yields
  three values and resumes between each, driven by the new
  broker entry.  Standard gates green; new entry untested in
  production code yet.

- [ ] **Step 15 — Migrate Icon generators (per-kind, one rung
  per kind or small bundle).**  `E_TO`, `E_TO_BY`, `E_EVERY`,
  `E_BANG_BINARY`, `E_SUSPEND`, `E_LCONCAT`, `E_LIMIT`,
  `E_RANDOM`, `E_SECTION` / `E_SECTION_PLUS` / `E_SECTION_MINUS`.
  Each kind's lowering recipe converts its EXPR_t shape into
  an SM sub-program with explicit SUSPEND/RESUME points.  At
  the SM_PUSH_EXPR + SM_BB_PUMP emission site (sm_lower.c:975),
  each kind branches: migrated kinds use chunk + SM_BB_PUMP_SM;
  un-migrated kinds keep the legacy emission.  Land each kind
  as its own rung (or bundle 2–3 closely-related kinds per
  rung, e.g., E_TO + E_TO_BY).  Gates: standard set + Icon
  corpus subset for the kinds touched by each rung.  When the
  last kind lands, delete `bb_broker_drive_expr` for Icon —
  the EXPR_t-driving entry point becomes unreferenced for
  Icon.

- [ ] **Step 16 — Migrate Prolog clauses (sm_lower.c:986).**
  Six kinds: `E_CHOICE`, `E_CLAUSE`, `E_CUT`, `E_UNIFY`,
  `E_TRAIL_MARK`, `E_TRAIL_UNWIND`.  Same shape as step 15 but
  smaller in volume.  Each kind gets a per-kind SM lowering
  with backtracking-aware SUSPEND/RESUME.  At end, delete
  `bb_broker_drive_expr` for Prolog (combined with step 15's
  Icon delete).

- [ ] **Step 17 — Migrate proc_table and g_pl_pred_table to
  entry-pcs.**  In `polyglot_init`, replace `proc_table[i].proc
  = proc;` with: lower the proc body as a named SM chunk during
  the same pass, record `proc_table[i].entry_pc = chunk_pc`.
  Same for `pl_pred_table_insert(name, entry_pc)`.  Migrate
  `coro_call(EXPR_t*, args, nargs)` to `sm_call_proc(int
  entry_pc, args, nargs)` — frame setup unchanged, body
  execution goes through SM dispatch on the chunk.
  `icn_scope_patch`'s in-place IR mutation is no longer
  reachable; frame-slot resolution happens at lower time.
  Delete `EXPR_t *proc` from proc_table struct.  Gates:
  standard set + full Icon corpus + Prolog smoke.  After this
  step, `polyglot.c` stores no IR pointers.

- [ ] **Step 18 — Final cleanup: delete SM_PUSH_EXPR; lift
  code_free gate; strengthen isolation gate.**
  - Lift the `lang_mask == (1u << LANG_SNO)` gate on
    `code_free` in `scrip_sm.c`.  Becomes unconditional.
  - Delete `SM_PUSH_EXPR` from `sm_prog.h` enum, from
    `sm_interp.c` handler, from `sm_codegen.c` handler, from
    `sm_prog.c` name table.  Delete `emit_push_expr` from
    `sm_lower.c`.  Delete `expr_gc_clone` if unreferenced
    (likely is, after this step).
  - Strengthen `test_isolation_ir_sm.sh`: forbid `EXPR_t` in
    function signatures of every gated file (currently
    coro_runtime.c, coro_value.c, coro_stmt.c, pl_runtime.c
    plus all the snobol4_* files); they should all read pure
    SM/chunk by now.
  - Promote any newly-clean files into the gate.
  - Verify: grep SM_PUSH_EXPR across source tree returns zero
    hits in non-comment lines.  M4 milestone close.

### M5 — Mode 4 x86 emitter extends to all six frontends

- [ ] **Step 19 — Extend `GOAL-MODE4-EMIT.md` (rungs EM-10
  through EM-16, the M5 phase) to cover Icon, Raku, Prolog,
  Rebus.**  At this point the lowerer produces pure SM for all
  frontends; mode-4 codegen extends to handle the full opcode
  set including SM_SUSPEND/SM_RESUME and SM_CALL_CHUNK.
  `libscrip_rt.so` extends to include the runtime support for
  generators (BB broker as a runtime library, not as a
  driver-time component) and Prolog backtracking machinery.
  Gates: emitted binaries pass smoke for each frontend and a
  curated corpus subset.

### M6 — Mode 4 JVM, .NET, WASM, JS backends

- [ ] **Step 20 — File `GOAL-MODE4-EMIT-JVM.md` and execute.**
  Mode 4 JVM backend.  Emit JVM bytecode (or Jasmin-assembled
  .class) for SM_Program; runtime support is `scrip-rt.jar`.
  Initial scope: SNOBOL4 + Snocone, then extend per
  step-15-style rungs to all frontends.

- [ ] **Step 21 — File `GOAL-MODE4-EMIT-NET.md` and execute.**
  Mode 4 .NET backend.  Emit IL or assembled .dll; runtime
  support is `scrip-rt.dll`.  Same scoping.

- [ ] **Step 22 — File `GOAL-MODE4-EMIT-WASM.md` and execute.**
  Mode 4 WASM backend.  Emit WAT/WASM; runtime support is a
  WASM module.  Browser-hostable.

- [ ] **Step 23 — File `GOAL-MODE4-EMIT-JS.md` and execute.**
  Mode 4 JS backend.  Emit JavaScript; runtime support is a
  JS module.

When step 23 closes, the full Milestone-3 matrix in PLAN.md
(every cell × × every backend) is the natural follow-on goal.

---

## Closed steps

**Step 1** — Survey + scaffolding. `SmChunk_t`, `SM_PUSH_CHUNK`, `SM_CALL_CHUNK` added to
`sm_prog.h`; FATAL stubs in `sm_interp.c` and `sm_codegen.c`; `docs/CHUNKS-step01-audit.md`
produced. one4all @ `a79b09f0`. Session #63, 2026-05-05.

**Step 2** — Migrate `sm_lower.c:573` (E_DEFER / `*expr`). `SM_PUSH_CHUNK` emitted for
E_DEFER in value context. `SM_CALL_CHUNK` implemented in `sm_interp.c` and `sm_codegen.c`
with minimal SmCallFrame (retval_name=NULL). `EVAL(*expr)` special-cased in E_FNC
lowering to emit chunk inline + `SM_CALL_CHUNK` — same SM stack, no nested run.
Scope boundary: stored-chunk `E=*expr; EVAL(E)` deferred (EXPVAL_fn returns FAILDESCR
for slen==1 DT_E until NV integer-carry infrastructure lands).
one4all @ `1b42498f`. Session #63, 2026-05-05.

**Step 5** — Verify SNOBOL4 + Snocone DT_E carriers no longer carry EXPR_t.
`sm_interp.c` instrumented with three audit counters (`g_chunks_audit_push_expr`,
`g_chunks_audit_push_chunk`, `g_chunks_audit_chunk_oor`) gated on
`SCRIP_CHUNKS_AUDIT` env var; atexit summary line. SM_PUSH_CHUNK validates
entry_pc within prog->count. Sweep results: smoke ×6, Budne 112 progs, SNOBOL4
patterns/control/coverage/functions/capture (17 progs), targeted probe — zero
SM_PUSH_EXPR fires, zero out-of-range, across all SNOBOL4/Snocone programs.
M1 invariant holds for the producer side. Documented in
`docs/CHUNKS-step05-validation.md`.
Gates: smoke ×6 PASS; isolation gate PASS; csnobol4 Budne PASS=36 (≥34).
one4all @ `2e0777d0`. Session #65, 2026-05-06.

**Step 4** — Migrate `sm_lower.c:326 / 345 / 386` (E_CAPT_COND_ASGN `. *fn(args)` and
E_CAPT_IMMED_ASGN `$ *fn(args)` — two sites, same SM_PAT_CAPTURE_FN_ARGS consumer).
Both for-loops that called `emit_push_expr(p, arg)` for non-E_QLIT args now emit the
canonical chunk pattern (SM_JUMP skip + `lower_expr` body + SM_RETURN + SM_PUSH_CHUNK).
Consumer SM_PAT_CAPTURE_FN_ARGS unchanged — at match time EVAL_fn → EXPVAL_fn dispatches
the slen==1 DT_E path via `sm_call_chunk(entry_pc)` (in place since Step 2).
Gates: smoke ×6 PASS (SNOBOL4 7/7, Snocone 5/5, Icon 5/5, Prolog 5/5, Raku 5/5,
Rebus 4/4); isolation gate PASS; csnobol4 Budne PASS=36 (≥34).
one4all @ `3be281e8`. Session #65, 2026-05-06.

**Step 3** — Migrate `sm_lower.c:470` (pattern non-QLIT arg of `SM_PAT_USERCALL_ARGS`).
Producer migrated to canonical chunk shape (jump-around + entry_pc + body + SM_RETURN +
SM_PUSH_CHUNK), mirroring Step 2's E_DEFER lowering. Consumer chain unchanged: bb_usercall
in stmt_exec.c thaws each DT_E arg via EVAL_fn → EXPVAL_fn, which since Step 2 already
dispatches slen==1 DT_E through sm_call_chunk(entry_pc). Legacy `EXPR_t*` branch in
EXPVAL_fn remains to serve the still-unmigrated emit_push_expr sites owned by Step 4
and later rungs. Gates green: build clean; smoke ×6 (SNOBOL4 7/7, Snocone 5/5, Icon 5/5,
Prolog 5/5, Raku 5/5, Rebus 4/4); isolation gate PASS; csnobol4 Budne PASS=36 (≥34).
one4all @ `c6862096`. Session #64, 2026-05-06.

**Prep work, session #62 (no rungs closed):** sub-goal files
written for Steps 8/9/10/11 + 19 (rungs deferred until prereqs
land):

- `GOAL-MODE4-EMIT.md` — owns Steps 8 (M2) and 19 (M5)
- `GOAL-NATIVE-SNOCONE-DOTNET.md` — owns Step 9; targets
  `one4all/src/driver/net/`
- `GOAL-NATIVE-SNOCONE-JVM.md` — owns Step 10; targets
  `one4all/src/driver/jvm/` (Java)
- `GOAL-NATIVE-SNOCONE-JS.md` — owns Step 11; targets
  `one4all/src/driver/js/sno-interp.js` (Node)

---

## Definitions

- **chunk** — a labeled, lowered SM sub-program.  Has an entry pc
  in SM_Program::instrs[] and ends in SM_RETURN (or SM_SUSPEND for
  generator chunks).  Equivalent to a closure body once it carries
  an environment.

- **deferred expression** — a value that, when consumed, produces
  another value (or a stream of them).  Currently represented as
  `DT_E { ptr = EXPR_t* }`; after this goal, as `DT_E { entry_pc,
  arity }` or equivalent.

- **two-system swap (sequential variant)** — within a single rung,
  the new code path is added, validated, and the old branch is
  deleted before the rung commits.  No long-lived feature flag.

- **isolation gate** — `scripts/test_isolation_ir_sm.sh`.
  Strengthened by step 6 (SNOBOL4 file structural rule) and step
  18 (full structural rule for all gated files).

- **bootstrap path** — a way to run `scrip.sc` independent of
  `scrip` itself.  Path A: scrip-on-scrip (after M1).  Paths B/C/D:
  scrip-on-{.NET, JVM, JS} via the extended native-host SNOBOL4
  interpreters (after M3).
