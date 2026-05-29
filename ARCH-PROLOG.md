# ARCH-PROLOG.md — PROLOG Frontend

Frontend: PROLOG. Produces shared IR (EXPR_t/STMT_t). See ARCH-IR.md.

## Engine model (substrate facts)

SCRIP's Prolog engine is a **boxed-cell, GC-managed** model, closer to SWI-Prolog's
heap-of-cells than to GNU Prolog's raw-WamWord stack. Key invariants, with the
reference each was checked against (see `one4all/doc/PROLOG-FEATURE-COMPARISON-2026-05-29-SONNET.md`):

- **Terms** (`src/frontend/prolog/term.h`): tagged `Term*` (ATOM/VAR/COMPOUND/INT/FLOAT/REF),
  GC-allocated. Bound vars become `TERM_REF` with a `ref` pointer; `term_deref` chases the chain
  (≡ SWI `deRef`). This is a deliberate substrate choice — it integrates with the shared AST + GC.
- **Unify + trail** (`src/frontend/prolog/prolog_unify.c`): structural unify; `bind()` records the
  var on a GC-doubling trail; `trail_unwind(mark)` restores vars to `TERM_VAR` on backtrack.
- **Choice points** (`src/runtime/interp/pl_runtime.{c,h}`): `pl_choice` is a reduced port of
  gprolog's WAM CP frame (`wam_inst.h:96-104`). Mapped: `parent≡BB`, `trail_mark≡TRB`, `env≡EB`,
  `resume≡ALTB`, `saved_args≡AB`, `stamp` (monotonic, ≡ a stand-in for HB). DEFERRED: HB/CPB/BCIB/CSB.
- **Cut**: `g_pl_cut_barrier` + `pl_cp_truncate` ≡ gprolog `Assign_B(BB(B))`. Aligned.
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
