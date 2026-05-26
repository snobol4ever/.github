# GOAL-CHUNKS — Eliminate SM_PUSH_EXPR; deferred expressions become compiled SM chunks; mode 4 unblocked for all frontends

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ NO AST WALKING IN MODES 2/3/4 — see RULES.md § "NO AST WALKING IN MODES 2, 3, OR 4"         ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║  Sess 2026-05-15g removed all tree_t* dereferences from sm_interp.c (mode 2) and                ║
║  sm_jit_interp.c (mode 3). Stubs print [NO-AST] <opcode> on stderr.                              ║
║                                                                                                  ║
║  If a gate breaks with [NO-AST] FOO — write fresh SM/BB lowering for FOO.                       ║
║  Do NOT restore the AST-walking call.  Do NOT route through proc_table_call or any              ║
║  other back-door that hands a tree_t* to mode-2/3/4 code.                                       ║
║                                                                                                  ║
║  Mode 1 (`--interp` standalone AST interp) is unchanged and remains the reference path.        ║
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
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** one4all (primary) + .github (this file) + snobol4dotnet + snobol4jvm + snobol4js (later steps)
**Done when:** SM_PUSH_EXPR opcode is deleted from the codebase.  The
DT_E descriptor (or its successor) carries a compiled SM chunk
addressed by entry-pc, never an `EXPR_t*`.  The proc_table and
g_pl_pred_table hold SM entry-pcs, never raw IR pointers.  The BB
broker drives SM sub-programs, not EXPR_t subtrees.  After
`sm_lower` returns, IR is freed unconditionally for all six
frontends.  Mode 4 (`--compile` and the JVM/.NET/WASM/JS
backends) is implemented for all six frontends because no code in
the runtime walks EXPR_t any more.  Native-host SNOBOL4
interpreters (snobol4dotnet, snobol4jvm, JS) are each extended to
run Snocone, giving multiple bootstrap paths for `scrip.sc`.

**Four-mode isolation property** (this has always been the goal;
SNOBOL4 and Snocone reach it via M1+M2; Icon and Prolog reach it
via M4 + CH-17 + CH-17i — the work that finishes the same property
for the frontends that lag).  For each of the four modes — mode 1
(compile-only), mode 2 (`--interp`), mode 3 (`--interp`), mode 4
(`--compile`) — and for each of the six frontends — SNOBOL4,
Snocone, Icon, Raku, Prolog, Rebus — the *currently-supported*
program surface (defined empirically by the `--interp` PASS set
today) runs to completion through a runtime path that is
structurally isolated from any AST walk: AST is freed
unconditionally after `sm_lower` returns, in every mode.  Mode 2
runs the SM_Program the same way mode 3 does (the `--interp` /
`--interp` distinction is preserved as a *driver-side* choice for
oracle/diff convenience, not as two different runtimes), with the
exception of SNOBOL4's `execute_program` path which is its own
non-SM interpreter and is not the AST walker this goal retires.
Mode 4 emits native code from the same SM_Program; emitted artifact's
link graph closes against `libscrip_rt.so` only.

The strengthened isolation gate enforces the structural separation
(no `IR_t *` field accesses in SM-mode runtime files; no
`interp_eval` / `polyglot_execute` / `call_user_function` reachable
from `sm_interp_run`'s call graph; emitted-artifact symbol set closes
against the runtime SO).  Icon and Prolog reach this property via
the CH-17i umbrella in `GOAL-CHUNKS-STEP17.md` (survey-mode3,
mode3-completeness, mode4-icon-prolog, final-isolation).  Mode 4
corpus coverage for the remaining frontends (SNOBOL4 and Snocone
are M2; Raku and Rebus are M5; Icon and Prolog are
CH-17i-mode4-icon-prolog) lands as their respective milestones
complete.  This umbrella is *not* feature expansion: programs that
currently FAIL or XFAIL under `--interp` stay in those buckets.

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
   (`--compile`) doesn't exist in the driver
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

**Sequential within a consumer/producer pair, not across the whole
goal.**  Each rung lands fully — the legacy
`if (is_chunk) { ... } else { /* old EXPR_t path */ }` branch in
consumers is deleted within the same rung that flipped its producer.
No long-lived feature flag, no parallel branches inside one rung's
file set, no merge collisions on shared C sources.

This rule does **not** preclude two sessions working on different
rungs simultaneously when those rungs are file-disjoint.  Specifically:
the carved sub-goal `GOAL-MODE4-EMIT.md` (Step 8 / EM-1..EM-9 / Step 19
/ EM-10..EM-16) modifies a different file set than M4 (Steps 12–18) —
emitter rungs add new files and one dispatch path in `scrip.c`; M4
rungs modify `sm_lower.c`, the BB engine, `polyglot.c`, the proc/pred
tables.  These can be driven by parallel sessions; they re-converge
naturally because the emitter consumes the SM_Program produced by
sm_lower's chunk-style output, regardless of which rung enriched the
chunk coverage last.

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
scrip_all_modes PASS in --interp, --interp, --run
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
    modes 2 (--interp) and 3 (--run).  No EXPR_t reachable from
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
  - **M4.5** — Step 18.5 (CH-17i umbrella in `GOAL-CHUNKS-STEP17.md`):
    Icon and Prolog reach the four-mode-isolation property the same
    way SNOBOL4 and Snocone reached it via M1+M2.  Take the Icon
    and Prolog `--interp` PASS surface today and make that *same*
    surface run byte-identical under `--interp` and
    `--compile`.  Sub-rungs: survey-mode3 (gap audit),
    mode3-completeness (one rung per bucket), mode4-icon-prolog
    (`--compile` coverage), final-isolation (extends M1's
    isolation gate to cover the Icon+Prolog SM-mode runtime files;
    adds mode-4 link-graph check).  Not new scope, not feature
    expansion: the four-mode property has always been the goal;
    this milestone finishes it for the frontends that lag.
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

- [x] **Step 6 — Strengthen the isolation gate for SNOBOL4 files.**
  Add a structural rule to `test_isolation_ir_sm.sh`: in
  `snobol4_pattern.c`, `snobol4_invoke.c`, `snobol4_argval.c`,
  `eval_code.c`, forbid `EXPR_t *` casts and `->kind` /
  `->children` / `->nchildren` / `->sval` / `->ival` field
  accesses on EXPR_t-typed expressions.  These four files
  should now read pure SM, no IR walking.  After this step
  passes, SNOBOL4 modes 2/3 are structurally isolated from IR.

  **Session #65 status — partial close, two files deferred.**  Of
  the four files listed, only `snobol4_invoke.c` and `snobol4_argval.c`
  are zero-hit today; the structural rule in the gate covers those two.
  `snobol4_pattern.c` still contains the legacy DT_E thaw block at
  lines 229–253 (reachable via `CONVERT(s,"EXPRESSION")`) plus
  `compile_to_expression` itself at line 990 — both produce or consume
  raw `EXPR_t*`.  `eval_code.c` is `eval_node`, the IR walker itself.
  Bringing those two under the structural rule requires migrating
  CONVERT EXPRESSION to emit a chunk (own rung) and then unwinding
  the legacy `eval_node` consumer chain (M4 cleanup territory).
  Documented in CHUNKS-step06 deferral note inside the gate script.
  The "modes 2/3 structurally isolated" claim is therefore NOT yet
  true — it remains aspirational until the deferred work lands.

- [x] **Step 7 — M1 milestone close.**  Run the full gate set in
  all three modes (`--interp`, `--interp`, `--run`) on a
  curated subset: smoke_snobol4, smoke_snocone, csnobol4 Budne
  full, Snocone corpus.  Document that SNOBOL4 + Snocone are
  end-to-end isolated through modes 2/3.  Update PLAN.md step
  ID.  This is the natural pause point: the project can ship
  M1 as a milestone before M2 begins.

### M2 — Mode 4 x86 emitter for SNOBOL4 + Snocone

> **PARALLEL TRACK.**  Step 8 is fully carved out to
> `GOAL-MODE4-EMIT.md`.  A session that says "I'm doing GOAL-CHUNKS"
> does **not** by default work on Step 8 — it works on the next open
> inline step (currently Step 12, Icon main() synthesis).  The carved
> sub-goal is file-disjoint from M4 (Steps 12–18): the emitter adds
> new files (`sm_codegen_x64_emit.c`, `scrip_rt.{c,h}`) and one new
> dispatch path in `scrip.c`; M4 modifies `sm_lower.c`, the BB
> engine, `polyglot.c`, and the proc/pred tables.  Two sessions can
> work both tracks simultaneously without merge collisions.

- [x] **Step 8 — File `GOAL-MODE4-EMIT.md` and execute it
  to completion.**  (See file — owns both M2 and M5 phases of
  the x86 mode-4 emitter, rungs EM-1 through EM-9 cover this
  step.)  This is itself a multi-rung sub-goal **executed in a
  separate session track**; it does not gate Steps 12–18 of this
  file and is not gated by them.
  Initial scope: `--compile file.sno` and `--compile
  --target=x86 file.sc` produce a standalone asm/binary.  The emitted
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

- [x] **Step 12 — Migrate sm_lower.c:1232 (Icon main() synthesis).**
  Single trivial site — synthesised E_FNC for `call_main`.
  Change shape: lower main's body as a chunk during
  polyglot_init's pre-lower pass; emit `SM_CALL_CHUNK
  main_entry_pc, 0` directly (no BB pump needed for top-level
  main once it runs to SM_RETURN).  Note: this only works if
  main's body doesn't transitively use generators.  If it does,
  defer this step until step 14 lands; or scope this step to
  generator-free main bodies and finish it after step 14.
  Decide in the rung.  Gates: standard set + smoke_icon.

- [x] **Step 13 — Migrate sm_lower.c:993 (Raku CASE).**  CASE
  body is a small bounded set of arms.  Lower each arm as a
  chunk; emit a dispatch chain (SM_PEEK / SM_EQ /
  SM_CALL_CHUNK per arm).  Doesn't need BB at all — CASE is
  not goal-directed.  Gates: standard set + smoke_raku CASE
  tests.

- [x] **Step 14 — Generator infrastructure.**  Add `SM_SUSPEND`
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
  **CH-15a LANDED sess #73, 2026-05-07** — E_TO + E_TO_BY migrated
  (SM_ICMP_GT + SM_ICMP_LT opcodes added; gen-locals 0=lo, 1=hi,
  2=cur, 3=step; E_TO_BY dispatches on step-sign each iteration).
  Remaining kinds in this step: E_EVERY, E_SUSPEND, E_BANG_BINARY,
  E_LCONCAT, E_LIMIT, E_RANDOM, E_SECTION, E_SECTION_PLUS,
  E_SECTION_MINUS.

  **CH-15-SURVEY sess #74, 2026-05-07** — empirical reachability
  audit (`docs/CHUNKS-step15-survey.md`).  Across 46 `test/`
  programs + 317 cross-corpus programs (200 Icon, 47 snocone,
  39 Raku, 21 scrip, 6 SNOBOL4, 4 Prolog) = **363 audited
  programs** under `--interp` with `SCRIP_CHUNKS_AUDIT=1`: zero
  fire `SM_PUSH_EXPR`.  The remaining-kinds dispatcher arm at
  sm_lower.c:1192–1204 is dead code on real corpora today.
  Cause (per CH-15a closed note): Icon proc bodies are walked by
  `coro_eval`, not lowered through `sm_lower`, until Step 17
  lands.  Implication: CH-15b is infrastructure-prep, not a
  behaviour change, and the standard "real program + diff against
  oracle" validation pattern does not apply.  **Recommendation:
  defer CH-15b until Step 17 is complete**, then migrate
  remaining kinds with full corpus validation.  Next inline
  goal-default: **Step 16** (Prolog clauses — smaller and
  self-contained) or **Step 17** (proc/pred table → entry_pcs —
  the architectural unblock).  Lon's call.

- [ ] **Step 16 — Migrate Prolog clauses (sm_lower.c:1213,
  formerly :986).**  Six kinds: `E_CHOICE`, `E_CLAUSE`, `E_CUT`,
  `E_UNIFY`, `E_TRAIL_MARK`, `E_TRAIL_UNWIND`.  Same shape as
  step 15 but smaller in volume.  Each kind gets a per-kind SM
  lowering with backtracking-aware SUSPEND/RESUME.  At end,
  delete `bb_broker_drive_expr` for Prolog (combined with step
  15's Icon delete).

  **CH-16-SURVEY LANDED sess #75, 2026-05-07** —
  `docs/CHUNKS-step16-survey.md` documents two findings:
  (A) the line-1213 producer DOES fire for every Prolog
  statement on real programs (unlike CH-15-SURVEY's dead Icon
  arm), and (B) the consumer (`SM_BB_ONCE` → `coro_eval` →
  `bb_eval_value`) FATALs on every Prolog kind today —
  every program in `test/prolog/*.pl` aborts under `--interp`
  with "kind 59 unhandled" (where 59 = E_CHOICE in the runtime
  enum, NOT E_DEFER as ir.h's SIL-reference comments would
  suggest).  Prolog smoke gate hides this because it only
  exercises `--interp`.  Migration without consumer-side fix
  is no-op-or-worse; consumer fix needs the chunk-shaped
  Prolog runtime entry points that Step 17's `entry_pc`
  infrastructure unblocks.  Also documents a second
  SM_BB_ONCE producer at sm_lower.c:1402 (statement-level
  wrapper) that emits stacked SM_BB_ONCE on Prolog clauses —
  pre-existing bug in `--interp` Prolog, Step 16-adjacent.
  **Recommendation: defer Step 16 until Step 17 lands**, then
  migrate with full Prolog corpus validation under an extended
  smoke gate that includes `--interp`.  Next inline:
  **Step 17** (proc/pred table → entry_pcs — architectural
  unblock for both Step 15 remaining kinds and Step 16).

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

  **CARVED to `GOAL-CHUNKS-STEP17.md` sess #75, 2026-05-07.**
  Step 17 is a multi-rung subsystem migration; the sub-goal
  file names rungs CH-17a..CH-17h with per-rung gates.  This
  pointer line stays as the navigational anchor; the destination
  is owned by the sub-goal file.

  **CH-17a LANDED sess #75, 2026-05-07** —
  `docs/CHUNKS-step17a-validation.md` documents the scaffolding:
  `IcnProcEntry` and `Pl_PredEntry` gain `int entry_pc` fields
  (initialised -1); new `sm_resolve_proc_entry_pcs(SM_Program*)`
  in scrip_sm.c walks both tables after sm_lower returns and
  populates entry_pcs via `sm_label_pc_lookup`.  Today every
  lookup returns -1 because sm_lower does not yet emit named
  proc-body chunks (CH-17b/d territory).  Pure addition: zero
  observable behaviour change; gates byte-identical to baseline.
  Diagnostic env var `SCRIP_PROC_ENTRY_PCS=1` shows the
  scaffold's reach: Icon hello.icn registers 1 proc (`main`),
  test/prolog `main + fact` registers 2 predicates, all -1.

  **CH-17b LANDED sess #75, 2026-05-07** —
  `docs/CHUNKS-step17b-validation.md` documents the next half:
  sm_lower emits named-chunk SKELETONS (SM_JUMP + SM_LABEL +
  SM_RETURN + SM_LABEL) for every entry in proc_table.  CH-17a's
  resolver now finds non-(-1) entry_pcs end-to-end (Icon hello.icn:
  main@1; Raku rk_given: day_type@1, season@5, main@9).  Empty
  bodies; chunks forward-jumped over.  Body lowering split into
  separate rung CH-17b' because Icon proc bodies are EXPR_t chains
  (not STMT_t) and frame-slot resolution via `icn_scope_patch` at
  runtime is its own architectural decision.  Next rung: **CH-17b'**
  — lower Icon/Raku proc bodies into the chunks.

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

- [ ] **Step 18.5 — Icon and Prolog: complete the currently-supported
  surface in all four modes (M4.5; CH-17i umbrella).**  This is not
  new scope — the four-mode-isolation property has been GOAL-CHUNKS's
  done-when from the start.  SNOBOL4 and Snocone reached it via M1+M2.
  Step 18.5 is the rung set that finishes the *same* property for
  Icon and Prolog (the frontends that lag because the proc/pred-table
  side channel and the AST-driven BB engine kept them un-isolated).
  Take the Icon and Prolog feature surface SCRIP supports today —
  defined empirically by the programs that pass under `--interp`
  today (Icon corpus 186 PASS / 47 FAIL / 30 XFAIL = 263; Prolog
  `test/prolog/*.pl` baseline) — and make that *same* surface run
  byte-identical through modes 2, 3, 4.  Programs in the FAIL/XFAIL
  set stay there; this step does not patch them.  Spec lives in
  `GOAL-CHUNKS-STEP17.md` under `### CH-17i`.

  **Sub-rungs (defined in `GOAL-CHUNKS-STEP17.md`):**
    - **CH-17i-survey-mode3** — empirical audit of the Icon+Prolog
      `--interp` PASS subset under SM dispatch (post-CH-17g-irrun-execution
      modes 2 and 3 share the runtime); produces a prioritised,
      countable gap list bucketed by failure mode (missing builtin /
      missing opcode handler / producer gap / semantic divergence).
      Survey doc: `docs/CHUNKS-step17i-survey-mode3.md`.
    - **CH-17i-mode3-completeness** — one sub-rung per bucket from
      the survey, named `CH-17i-mode3-{builtin,opcode,lower,semantic}-NAME`.
      Each lands byte-identical for its corpus subset.  Terminal
      gate: Icon `--interp` PASS == Icon `--interp` PASS exactly,
      same for Prolog.
    - **CH-17i-mode4-icon-prolog** — extend `GOAL-MODE4-EMIT.md`'s
      rung set to handle the SM opcodes Icon and Prolog use; Icon
      and Prolog `--compile` PASS == `--interp` PASS exactly.
    - **CH-17i-final-isolation** — strengthened isolation gate
      extends to cover the full SM-mode runtime file set
      (`coro_runtime.c`, `coro_value.c`, `coro_stmt.c`, `pl_runtime.c`,
      `interp_hooks.c`, `polyglot.c`); mode 4 link-graph check via
      `nm`/`readelf`; coverage matrix doc records {Icon, Prolog} ×
      {modes 2, 3, 4} all-green.  This is the same isolation gate
      M1's Step 6 strengthened for SNOBOL4 files; CH-17i-final-isolation
      strengthens it for the Icon and Prolog files.

  **Done when:** Icon and Prolog each have an all-green
  coverage matrix across modes 2, 3, 4 (PASS count exactly equal
  to the `--interp` baseline in each mode); the strengthened
  isolation gate covers the SM-mode runtime file set; the
  coverage matrix doc lands.

  **Why this is its own step.**  Step 18 is mechanical (delete
  SM_PUSH_EXPR, lift the `code_free` gate, strengthen the isolation
  gate's symbol-call blacklist).  Step 19 (M5) is full Mode 4
  corpus across *all six* frontends.  Step 18.5 is the
  *runtime-completeness* work specifically for Icon and Prolog,
  whose surface CH-17g's bridge-1..4 work showed is broader than
  the SNOBOL4 surface and warrants its own rung group rather than
  inlining into Step 18.

  **Gates:** all four sub-rungs' gates land, then
  CH-17i-final-isolation locks the property in CI.

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

**Step 15a (CH-15a)** — E_TO + E_TO_BY producer migration.  First producer
for `SM_BB_PUMP_SM` and the gen-local opcodes.  Two new comparison opcodes
added to support generator loop-exit tests:

```
SM_ICMP_GT   ; pop r,l ; last_ok = (l.i > r.i) ; push nothing
SM_ICMP_LT   ; pop r,l ; last_ok = (l.i < r.i) ; push nothing  (E_TO_BY neg-step)
```

`SM_ACOMP` was considered but rejected: it pushes -1/0/1 (extra cleanup),
has no SM-interp handler today (JIT-only by design), and includes string-
coerce paths unnecessary at this site.  `SM_ICMP_*` are minimal,
`last_ok`-only, named after operand kind.

In `sm_lower.c`, `case E_TO:` and `case E_TO_BY:` carved out of the shared
generator block at line 1033 (was: 10 kinds fall-through to
`emit_push_expr + SM_BB_PUMP`; now: 8 kinds remain).  Per-kind chunk
emission uses the canonical jump-around shape with `SM_PUSH_CHUNK +
SM_BB_PUMP_SM` as consumer.  Gen-local slots: 0=lo, 1=hi, 2=cur, 3=step
(E_TO_BY only); see `docs/CHUNKS-step15a-validation.md` for full chunk
listings.  E_TO_BY dispatches on step-sign each iteration via SM_ICMP_LT
against 0 — mirrors `coro_bb_to_by` semantics (`step>0: cur>hi → ω;
step<0: cur<hi → ω`).

Empirical proof: a Raku range expression `say 1..3` audits as
`SM_PUSH_CHUNK=1, SM_PUSH_EXPR=0` under `--interp` with `SCRIP_CHUNKS_AUDIT=1`;
the chunk yields 1, 2, 3 in both `--interp` and `--run`.  Icon
`every i := 1 to 5 do …` does NOT audit a chunk emission — that path
runs through `coro_pump_proc_by_name(\"main\", …)` → `coro_eval(main_body)`,
pure IR walking inside the proc body.  Once Step 17 lowers Icon proc
bodies through sm_lower, every-bodies containing `1 to n` will hit
the new chunk emission automatically; the Raku-side firing today
proves the producer wiring is end-to-end.

Gates: smoke ×6 PASS (7/7, 5/5, 5/5, 5/5, 5/5, 4/4); isolation gate
PASS; csnobol4 Budne PASS=36 (≥34, exact baseline); unified_broker
PASS=49; full Icon corpus PASS=186 FAIL=47 XFAIL=30 TOTAL=263
(byte-identical to baseline 186/47/30); Raku full suite ir 29/0,
sm 0/29, jit 0/29 (unchanged baseline per CH-13 note); SNOBOL4 jit
smoke ir 139, sm 101, jit 101 (unchanged baseline per Step 7 close);
`scrip_all_modes` PASS=2 FAIL=0.
Documented in `docs/CHUNKS-step15a-validation.md`.
one4all @ `dd673da1`.  Session #73, 2026-05-07.

**Step 14b (CH-14b)** — Gen-local slot infrastructure. Added `SM_LOAD_GLOCAL` and
`SM_STORE_GLOCAL` opcodes (a[0].i = slot 0..7); added `locals[SM_GEN_LOCAL_MAX]`
(=8) array to `SmGenState`; survives SUSPEND/RESUME automatically because
`SmGenState` is the persistent envelope `bb_broker_drive_sm` allocates per
generator invocation. Outside a generator drive both opcodes push FAILDESCR
+ clear last_ok (mirrors SM_PUSH_VAR's FAIL discipline). `g_current_gen_state`
promoted from `static` to file-extern + declared in `sm_interp.h` so JIT
codegen mirrors can reach it. Two new tests in `sm_interp_test.c`:
`test_gen_locals_survive_suspend` (init 100, ++, ++ across two suspends —
verifies 100/101/102) and `test_gen_locals_isolated_per_invocation` (two
SmGenStates same chunk — both see private 100/101). CH-14 gate now 18/18 PASS
(was 7/7). Pure addition: no producer emits the new opcodes yet, so no
behaviour change for any existing program. Also added `SM_BB_PUMP_SM` opcode
+ handler + JIT mirror (consumer entry point for migrated generator kinds —
pops chunk descriptor, allocates SmGenState rooted at entry_pc, drives via
bb_broker_drive_sm with pump_print body). First producer for SM_BB_PUMP_SM
and the gen-local opcodes is CHUNKS-step15a (E_TO + E_TO_BY).
Gates: smoke ×6 PASS (7/7, 5/5, 5/5, 5/5, 5/5, 4/4); isolation gate PASS;
csnobol4 Budne PASS=36 (≥34, byte-identical to baseline); unified_broker
PASS=49; full Icon corpus PASS=186 FAIL=47 XFAIL=30 TOTAL=263 (byte-identical
to baseline 186/47/30).
Documented in `docs/CHUNKS-step14b-validation.md`.
one4all @ HEAD. Session #71, 2026-05-07.

**Step 14 (CH-14)** — Generator infrastructure. `SM_SUSPEND` and `SM_RESUME` opcodes added
to `sm_prog.h`; `SM_INTERP_SUSPENDED = 1` return-code constant; forward typedef `SmGenState`.
`struct SmGenState` defined in `sm_interp.h` (resume_pc, stack snapshot, last_ok, started).
`g_current_gen_state` pointer in `sm_interp.c`; SM_SUSPEND handler snapshots pc+stack into
SmGenState and returns SM_INTERP_SUSPENDED; SM_RESUME is a no-op documentation marker.
`sm_gen_state_new(entry_pc)` and `bb_broker_drive_sm(gs, body_fn, arg)` implemented —
drive an SM generator chunk through all its ticks (BB_PUMP semantics for SM chunks).
`sm_codegen.c`: named-FATAL stubs for SM_SUSPEND/SM_RESUME (JIT gen is M5/EM-10 territory).
Gate: hand-written SM program yields 10/20/30 via SM_SUSPEND; re-drive of exhausted gen
returns 0; 17/17 tests PASS including 7 new generator tests. Smoke ×6 PASS. Isolation PASS.
`scripts/test_sm_generator_ch14.sh` added.
Documented in `docs/CHUNKS-step14-validation.md`. one4all @ HEAD. Session #70, 2026-05-06.

**Step 13** — Migrate `sm_lower.c:1062` (Raku CASE / given-when) to chunk-based
dispatch. Replaces the legacy `emit_push_expr + SM_BB_PUMP` wrapper with a new
`SM_BB_PUMP_CASE` opcode (`a[0].i = ncases`, `a[1].i = has_default`).  The
producer lowers each piece — topic, per-arm value and body, optional default
body — as its own forward-jump-around chunk, pushes them in canonical order
(topic, then `cmp_kind / val / body` triples, then optional default), and
emits the dispatch opcode.  The runtime helper (in both `sm_interp.c` and
`sm_codegen.c` as lockstep mirrors) reverse-pops, evaluates topic via
`sm_call_chunk`, walks arms with the same string-vs-int comparison logic as
`coro_value.c:947` (E_LEQ → string equality, else integer-or-string), runs
the matching body chunk, leaves result on the stack.

Wrapper-level synthesis is now EXPR_t-free for the Raku CASE path —
empirically: `SCRIP_CHUNKS_AUDIT=1 ./scrip --interp test/raku/rk_given.raku`
reports `SM_PUSH_CHUNK=20 SM_PUSH_EXPR=0 out_of_range=0` (20 = 2 CASEs ×
(1 topic + 4 arms × 2 chunks-per-arm + 1 default)).

Scope boundary (honest): the value-context `bb_eval_value(E_CASE)` path in
`coro_value.c:947` still walks E_CASE's children via EXPR_e cmp-kind
dispatch.  That path is unreachable from the SM-mode Raku given-stmt route
after CH-13 but lives on for future value-context CASE use and for any
future Icon E_CASE.  Cleaning the IR walk inside `coro_value.c:947` is
M4-cleanup territory (mirrors how CH-12 deferred the `coro_call` proc_table
walk to Step 17).

Pre/post execution on `rk_given.raku`: `--interp` and `--run` previously
stack-underflowed and aborted; post-CH-13 they reach the dispatch and run
the default branch.  Full Raku --interp/--run remains broken at the
surrounding `say`/sub-call infrastructure level, consistent with the
Raku full-suite baseline (29/0/0 across IR/SM/JIT) — fixing that is not
CH-13's scope.

Gates: build clean; smoke ×6 PASS (SNOBOL4 7/7, Icon 5/5, Prolog 5/5,
Raku 5/5, Snocone 5/5, Rebus 4/4); isolation gate PASS; csnobol4 Budne
PASS=36 (≥34, exact baseline match); full Icon corpus PASS=186 FAIL=47
XFAIL=30 (TOTAL=263, byte-identical to baseline); unified_broker PASS=49.
Raku full suite 29/0/0 unchanged (no regression on the broken-already
modes; no CASE-specific test in the suite to regress).
Documented in `docs/CHUNKS-step13-validation.md`.

After CH-13, surviving `emit_push_expr` call sites in `sm_lower.c` are
lines 1046 and 1057 (the Prolog backtracking cluster — Step 16 territory),
plus the helper definition at line 39.  Two real producer sites remain.

**Step 12** — Migrate `sm_lower.c:1292–1308` (Icon main() synthesis). The
synthesised `E_FNC("main")` + `emit_push_expr` + `SM_BB_PUMP` wrapper is
replaced by a single `sm_emit_si(p, SM_BB_PUMP_PROC, "main", 0)`. New
opcode `SM_BB_PUMP_PROC` added to `sm_prog.h` (name + nargs operands);
handler in `sm_interp.c` and `sm_codegen.c` (`h_bb_pump_proc`); helper
`coro_pump_proc_by_name(name, args, nargs) → bb_node_t` factored out of
the E_FNC user-proc branch of `coro_eval` and exposed in
`coro_runtime.h`. The handler does the proc_table lookup + coroutine
staging without constructing or walking any EXPR_t at the wrapper layer.
Generator-orthogonal: works whether or not main's body uses generators,
because main's body execution path (`coro_call` → IR walk inside
`proc_table[i].proc`) is unchanged — that IR walk is Step 17's territory
(proc_table → entry_pcs).

Scope boundary (honest): this rung migrates the wrapper-level synthesis
only. The three remaining `emit_push_expr` call sites in `sm_lower.c`
(lines 1046, 1057, 1064 — `SM_PUSH_EXPR + SM_BB_PUMP` and
`SM_PUSH_EXPR + SM_BB_ONCE` for per-statement Icon/Prolog statement
walks) are owned by Steps 15 (Icon generators per-kind) and 16 (Prolog
clauses).

Audit-counter sweep with `SCRIP_CHUNKS_AUDIT=1` across all Icon test
programs in `test/icon/*.icn` (skipping `meander.icn` which hangs on
baseline pre-existing) under both `--interp` and `--run`: every
program reports `SM_PUSH_CHUNK=0  SM_PUSH_EXPR=0  out_of_range=0`.
Empirical proof that the wrapper-level synthesis is now genuinely
EXPR_t-free for the Icon path.

Gates: build clean; smoke ×6 PASS (SNOBOL4 7/7, Icon 5/5, Prolog 5/5,
Raku 5/5, Snocone 5/5, Rebus 4/4); isolation gate PASS; csnobol4 Budne
PASS=36 (≥34, exact baseline match); full Icon corpus PASS=186 FAIL=47
XFAIL=30 (TOTAL=263, byte-identical to baseline 186/47/30 — zero
regression). one4all @ `0a38d055`. Session #66, 2026-05-06.

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

**Step 7** — M1 milestone close. Three-mode sweep + curated subset gates
documented in `docs/CHUNKS-M1-close.md`. Findings:
- Producer-side migration complete: smoke ×6 PASS, isolation gate (with new
  structural rule) PASS, Budne PASS=36, Step 5 audit clean.
- HONEST: `test_smoke_snobol4_jit.sh` shows 38-program gap between `--interp`
  (139 PASS) and `--interp` / `--run` (101 PASS each). Verified
  pre-existing: same gap at pre-Step-4 commit c6862096. CHUNKS Steps 2–6 are
  net-flat on this gate — independent of CHUNKS scope.
- HONEST: Snocone all-modes 28/14 — same pre-existing pattern.
M1 is shippable as "producer-side chunk migration complete + chunk
infrastructure in place"; it is NOT "modes 2/3 bug-for-bug compatible with
mode 1 on real programs". Broad-corpus parity is a separate (SN-*) ladder.
M2 (mode-4 x86 emitter) is now unblocked.
one4all @ `28020a0a`. Session #65, 2026-05-06.

**Step 6** — Structural rule added to `test_isolation_ir_sm.sh` forbidding
EXPR_t* casts and `->kind`/`->children`/`->nchildren`/`->sval`/`->ival`
field accesses. Initial scope: `snobol4_invoke.c`, `snobol4_argval.c` —
both zero-hit today, the gate now enforces this post-Step-4 reality.
**Honest deferral**: `snobol4_pattern.c` (legacy DT_E thaw at lines 229–253
reachable via CONVERT EXPRESSION; `compile_to_expression` at line 990) and
`eval_code.c` (contains `eval_node` itself) remain outside the structural
rule until CONVERT EXPRESSION migrates to chunk emission and the legacy
`eval_node` consumer chain unwinds. Negative-test verified the new rule
fires on injected `(EXPR_t *)` casts.
Gates: smoke ×6 PASS; isolation gate (with new structural rule) PASS;
csnobol4 Budne PASS=36 (≥34).
one4all @ `27b0a102`. Session #65, 2026-05-06.

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
