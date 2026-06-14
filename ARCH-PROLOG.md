# ARCH-PROLOG.md — PROLOG Frontend

Frontend: PROLOG. Produces shared IR (EXPR_t/STMT_t). See ARCH-IR.md.

## ⚠️ CORRECTION (2026-05-30): NO VALUE STACK. STACKLESS FOUR-PORT IS THE MODEL.

The prior framing below leaned on GNU Prolog's WAM CP-frame **stack** (`pl_choice` ported from
`wam_inst.h`) as the engine compass. **That was wrong.** The correct model is Proebsting's
four-port translation (`SCRIP/bench/Simple Translation of Goal Directed Evaluation.pdf`):
each operator is four labeled code chunks (`α/β/γ/ω`) threaded by `goto`, with each box's value in
a FLAT per-activation home — NOT a pushed/popped value stack, and NOT a save/restore of shared
mutable node slots. See `SCRIP/bench/test_icon.c` (flat scalar per box, one C activation) and
`SCRIP/bench/test_sno_1.c` (the one unbounded-repetition construct uses an explicit indexed frame
array `_1[64]`/`ζ`, the solved form of the EVAL/CODE/`*P`-deferred problem). The original static
Prolog emitter `SCRIP/archive/frontend/prolog/prolog_emit.c` already had this shape: a predicate
is a C function with a flat α/β/γ/ω body whose only surviving dynamic state across backtracking is a
resume cursor int (`_cs`) plus the trail mark. **The `bb_node_state_t` snapshot/restore mechanism in
the current engine IS a value stack and is being removed** (see GOAL-PROLOG-BB.md → PLG ladder).

What survives (all three are in the `.c` reference files, so they are NOT the value stack):
the **trail** (binding undo log), the **resume cursor / CP ledger** (`_cs` int / parent-linked
`pl_choice` record — irreducible "which suspended alternative is live"), and **explicit indexed
deferred-frame arrays** for genuinely-repeating constructs (ARBNO-style `_1[64]`).

## Engine model (substrate facts)

SCRIP's Prolog engine is a **boxed-cell, GC-managed** model (tagged `Term*`, GC-allocated). The
choice-point ledger is a parent-linked record, NOT a contiguous WAM stack, and NOT a value stack.
Key invariants, with the reference each was checked against (see
`SCRIP/doc/PROLOG-FEATURE-COMPARISON-2026-05-29-SONNET.md`):

- **Terms** (`src/frontend/prolog/term.h`): tagged `Term*` (ATOM/VAR/COMPOUND/INT/FLOAT/REF),
  GC-allocated. Bound vars become `TERM_REF` with a `ref` pointer; `term_deref` chases the chain
  (≡ SWI `deRef`). This is a deliberate substrate choice — it integrates with the shared AST + GC.
- **Unify + trail** (`src/frontend/prolog/prolog_unify.c`): structural unify; `bind()` records the
  var on a GC-doubling trail; `trail_unwind(mark)` restores vars to `TERM_VAR` on backtrack.
- **Choice points** (`src/runtime/interp/pl_runtime.{c,h}`): `pl_choice` is a reduced port of
  gprolog's WAM CP frame (`wam_inst.h:96-104`). Mapped: `parent≡BB`, `trail_mark≡TRB`, `env≡EB`,
  `resume≡ALTB`, `saved_args≡AB`, `stamp` (monotonic, ≡ a stand-in for HB). DEFERRED: HB/CPB/BCIB/CSB.
- **Cut**: `g_pl_cut_barrier` + `pl_cp_truncate` ≡ gprolog `Assign_B(BB(B))`. Aligned.

## Byrd-Box model — the design (2026-06-13)

The substrate facts above (`Term*`, trail, parent-linked CP ledger) are correct and survive; what
changes is the CONTROL model layered on them. Per `DESIGN-PROLOG-BB-ALL.md` + GOAL-PROLOG-BB.md →
**PL-BB** ladder, every construct compiles to four CODE CHUNKS α/β/γ/ω (Proebsting
start/resume/succeed/fail), wired by `goto`/`call` between a node's own ports and its children's
own ports. Three refinements over the WAM-mapping framing above:

- **Callee resumability is a CLOSURE VALUE, not a port.** Entering a predicate is a `call` that
  yields a closure `(value, Resume)`; re-driving it is `closure.Resume()` dispatched from the
  caller's OWN β chunk. In SCRIP the closure IS the callee's `rt_enter` frame (its cell block +
  trail/CP marks). There is no caller-side "callee-entry/resume port": the ports formerly emitted
  as `δ`/`ε` (`X86P_DELTA/EPSILON`, ports 4/5) are ABOLISHED — one was a call-opcode target, the
  other a value-resume, neither a code chunk. (JCON `ir_a_Call` + `vClosure.java`.)
- **Determinacy is first-class (`bounded`).** A box that cannot offer a second solution emits NO β
  chunk, allocates no choice point, retains no closure. β exists only for genuine generators
  (multi-clause predicates, `retract`, member-style recursion, `between`, findall's inner goal).
  Assigned at lower time (JCON F1: every `ir_a_*` guards resume with `/bounded`). Retires the
  runtime "nearest resumable predecessor" heuristic.
- **The boxes ARE the engine.** No central choice-point-STACK interpreter loop, no bytecode
  fetch-decode-execute, no C control engine / `rt_meta_solve` meta-rail. Backtracking is the ω/β
  wiring + the one shared trail + per-callee closures. `pl_choice` remains the CP-LEDGER RECORD
  (the irreducible "which suspended alternative is live") but no longer an engine that DRIVES
  control — the emitted four-port code does.

Excision (SWI/GNU out of HEAD): see GOAL-PROLOG-BB.md → PL-BB excision table — WAM CP-stack engine
loop, bytecode dispatch, C control engine/meta-rail, WAM register ABI, "always push a CP." The
ladder PL-BB-0..6 sequences LOWER (per IR kind) + EMITTER (BB template per IR), test-first, gated
against GATE-1 5/5/5 + the ratchet floor.
- **catch/throw**: catcher tried on a scratch trail before commit (correct ISO discipline). Aligned.

## Known parity gaps vs gprolog/SWI (tracked as rungs in GOAL-PROLOG-BB.md → PL-ENGINE-PARITY)

1. **Conditional trailing.** Both references trail a binding only when the var is older than the
   youngest live CP (gprolog `Word_Needs_Trailing`, `wam_inst.h:472`; SWI `GTrail`, `pl-incl.h:2194`).
   SCRIP trails unconditionally. → rung family **PL-TRAIL-COND** (add var birth-stamp, compare to
   youngest CP stamp). This is also the de-facto **HB** port (the one deferred CP-frame field with a
   real consumer).
2. **Level-2 indexing.** WAM-CP-8 gives Level-1 first-arg indexing with an O(N) linear filter scan;
   gprolog Level 2 (`indexing.pl`) and SWI (`pl-index.c` Fibonacci hash) select in O(1) via a hash
   bucket. → rung family **PL-INDEX-L2** (hash bucket at lower time; multi-arg deferred).

All parity rungs are mode-2 interpreter logic (zero emitted x86, FACT unchanged), verified against
mode-2 as the correctness reference.
