# HANDOFF 2026-05-29 — Opus 4.8 — ICON-BB IBB-9-6 user-proc dispatch

**Goal:** GOAL-ICON-BB.md · **Step:** IBB-9-6 (user-procedure dispatch) — **LANDED**

## Result

Corpus same-sweep over `/home/claude/corpus/programs/icon/*.icn` (293 files; m2-OK filter;
PASS iff m3 rc==0 && m2==m3 byte-identical):

**69 → 82 PASS (+13), SEGV 0, ABORT 0, 0 regressions** (worktree-verified: stashed changes,
rebuilt baseline, captured pass-list, restored, diffed — the regression set is empty).

The `bb_call: unsupported call shape` ABORT cluster (~158 aborts, the single largest remaining
bucket) is eliminated — ABORT count went from its prior value to 0.

Newly passing (13): rung02_proc_add_proc, rung02_proc_fact, rung03_suspend_fail,
rung03_suspend_return, rung09_loops_repeat_counter, rung09_loops_until_while,
rung21_global_initial_global_basic, rung21_global_initial_global_str,
rung21_global_initial_multi_global, rung25_global_global_basic, rung25_global_global_str,
rung25_global_global_three_procs, rung25_global_multi_global.

## Architecture

A user procedure is compiled by `bb_build_flat` into a self-contained x86 slab (`bb_box_fn`)
that leaves its return value on the value-stack and exits via `XA_FLAT_EPILOGUE`'s `ret`. The
call protocol transcribes JCON `ir_a_Call` (irgen.icn:360-403) + `ir_a_Return` (irgen.icn:867-903).

Variables in Icon BB mode-3 resolve through `NV_GET_fn`/`NV_SET_fn` (a global name table), NOT
frame slots — so a proc's params are bound as named variables and saved/restored around the call
for recursion correctness. The return value flows through the vstack (read by depth-delta).

**Lazy slab building** is the key robustness decision: the driver registers every proc's NAME +
BB entry + param-names up front (so a `BB_CALL` can recognise a callee during emission), but each
slab is built ON FIRST CALL, not eagerly. An unreached proc containing a not-yet-supported shape
(which would `abort()` inside `bb_build_flat`) therefore cannot break a program that never calls it
— this mirrors the mode-2 oracle, where an unreached proc never executes. (Eager building caused 5
transient regressions: `meander`, `rung36_jcon_{kross,meander,prefix,roman}` — all stdin-reading
programs whose proc bodies use not-yet-supported builtins like `repl`/`integer`, never reached
under `/dev/null`.)

## Files changed (SCRIP)

- **`src/runtime/rt/rt.c` / `rt.h`** — Icon proc registry + caller:
  - `rt_icn_proc_register(name, entry, pnames, nparams)` — update-if-exists; stores BB entry node
    (not a built fn) + param-name list (from `lower_sc`).
  - `rt_icn_proc_set_builder(builder)` — driver supplies `bb_build_flat` as the lazy builder.
  - `rt_icn_proc_is_registered(name)` — emitter-side predicate (consulted by `bb_call.cpp`,
    `walk_bb_flat`, `icn_binop_operand_streams`).
  - `rt_icn_call_proc(name, nargs)` — pops args (arg0 deepest), looks up proc, lazily builds the
    slab on first call, saves+binds param NV bindings, invokes slab, reads return value by vstack
    depth-delta (fall-off → FAILDESCR), restores bindings, pushes result.
- **`src/emitter/BB_templates/bb_return.cpp`** — NEW template. `return E`: value already on vstack
  (driver walked α) → `jmp γ`. Bare `return`: `rt_push_null` then `jmp γ`. (10/22 bytes.)
- **`src/emitter/BB_templates/bb_templates.h`** — declare `bb_return`.
- **`src/emitter/emit_core.c`** — `BB_RETURN` now dispatches to `bb_return` (was `bb_alt` no-op).
- **`src/emitter/BB_templates/bb_call.cpp`** — userproc arm (`movabs rdi,name; mov esi,nargs;
  call rt_icn_call_proc; jmp γ`) gated on `rt_icn_proc_is_registered`; `BB_CALL` added to
  `is_write_intexpr` and `arg_is_any` so `write(proc())` routes the pushed result through
  `rt_pop_write_any_nl`.
- **`src/emitter/emit_bb.c`**:
  - `flat_drive_return` — routes the success edge to the **slab-level exit** (`g_emit.flat_succ_p`),
    NOT the local γ (next SEQ statement): a `return` exits the procedure, mirroring mode-2's
    FRAME.returning chain-stop. `flat_succ_p`/`flat_fail_p` hoisted to BEFORE the `walk_bb_flat` call.
  - `flat_drive_call_userproc` — walks the arg γ-chain (arg0..argN-1, each pushes one value), then
    emits the call trailer via EMIT_PAIR_FILL.
  - `icn_binop_operand_streams` + `BB_BINOP_GEN` dispatch — `n * fact(n-1)` lowers to `BB_BINOP_GEN`
    because `is_suspendable` flags ALL calls (TT_FNC) as generators, but the mode-2 oracle discovers
    neither operand actually streams and does ONE multiply. Mode-3 now detects this (a registered
    user-proc call is single-shot) and routes to the plain `flat_drive_binop_tree`, temporarily
    coercing `nd->t` to `BB_BINOP` so the apply emits `rt_arith` (restored immediately;
    single-threaded emission, node not re-entered).
  - `BB_RETURN` case added to `walk_bb_flat` → `flat_drive_return`.
- **`src/driver/scrip.c`** — mode-3 Icon driver: `rt_icn_proc_reset`, set lazy builder, register
  every non-main proc's entry + param-names, then build + call `main`.
- **`Makefile`** — `bb_return.cpp` source-list entry + compile rule.

## Two bugs hit and fixed (for the record)

1. **Early return continued to the next statement.** The proc-body SEQ wires each statement's γ to
   the next statement, so `bb_return` jumping to its local γ landed on the following statement
   (`f(0)` returned 2 instead of 1). Fix: route to the slab-level success exit `flat_succ_p`.
2. **`n * fact(n-1)` returned 1 (no multiply).** The multiply node was `BB_BINOP_GEN` (because the
   call operand is "suspendable"), and `flat_drive_binop_gen_tree`'s odometer mis-pumps a single-shot
   call — the multiply never fired. Fix: collapse non-streaming gen-binops to a plain binop walk
   (matching the mode-2 oracle's "neither side is a generator → one pair" path).

## Gates (all green)

- Same-sweep: PASS=82 SEGV=0 ABORT=0 FAIL=177 SKIP=34; regressions vs baseline 69 = 0.
- FACT primary gate: 0 (the 12 `bytes()/u32le` matches outside templates are the pre-existing
  definitions in `emit_str.cpp` + `bomb_bytes` + header decls — none added by this change).
- zero-SM: `--dump-sm rung02_proc_fact.icn | grep -c '^   [0-9]'` == 0.
- smoke icon 5/5, smoke prolog 5/5, broker 51/11.
- Edge cases byte-identical (m2==m3): 0-arg proc, nested calls `twice(greet())`/`twice(twice(3))`,
  recursion `fact(5)=120`, early `return`, bare `return`.

## Deferred / NEXT

- **Generator procs** (a called proc that `suspend`s) — needs the odometer/GeneratorState path, not
  the single-shot slab. `rung02_proc_locals` is blocked separately on `every ival=2` (IBB-9-4), not
  on proc dispatch.
- NEXT candidates: scanning subsystem (~11 FAILs); `every ival=2/3` (IBB-9-4/5); generator-proc
  dispatch; finish unop family (SIZE/RANDOM); `||` lconcat; BB_CASE; BB_AUGOP-in-every (rung10).
  Deferred refactor IBB-9-RELOP-PORTS.
