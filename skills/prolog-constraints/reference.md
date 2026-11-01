# Prolog constraints: the reference

Verified 2026-11-01 against SCRIP 9cb24d2ca. Consolidated from ARCH-PROLOG-CLPFD, ARCH-PROLOG-CONSTRAINTS and ARCH-PROLOG-CLPR-CHR (retired; `.github/RETIRED-ARCH-PAGES.tsv`). The 10-10 design's marker in `slen` (`PL_ATTV_SLEN`) and the leaf `'$attv_new'` were not what landed: the flag is `PL_VAR_ATTV` in the tag word and a variable is made by `pl_var_make`.

## 1. The bind roads a change to attributed variables must cover

Emitted inline (the `PL_TRAIL` shape of `src/templates/bb/bb_pl_cell.h`) in the unify boxes (`bb_unify_value.cpp`, `bb_unify_const.cpp`, `bb_unify_struct.cpp`) and `bb_call_pl_leaf.cpp`; the asm unifier in `src/runtime/rtx/rtx_plunify.s`; the C binders in `src/runtime/by_name_dispatch.c` and `src/runtime/unification.c`. A gate for this layer has one arm per road: head constant, head structure, head value, `=/2` inline, a deep unify both ways, variable-variable plain and attributed in both orders, a builtin binding through C (`functor/3`, `arg/3`, `=../2`, `is/2`), `memberchk/2`, a binding undone by backtracking that must not wake, a failing unification after an attributed bind; each against swipl in both modes, plus the collector arm under `SCRIP_GC_STRESS` 1 and 3 with `SCRIP_GC_CHAIN_CHECK=3`.

## 2. CHR as lowered

- Declarations `:- chr_constraint c/1, d/2.` (modes and types optional) and `:- chr_type`; rules `Name @ H <=> G | B` (simplification), `H ==> G | B` (propagation), `H1 \ H2 <=> G | B` (simpagation).
- `lower_prolog_chr.c` turns each rule into ordinary Prolog over the vendored `chr_runtime.pl` (the store as attributed variables per variable plus a global store, suspensions, the propagation history, `chr_show_store`). The 25,000-line bootstrapped translator is not vendored.

## 3. CLP(Q) and CLP(R)

One shared core (`clpqr_itf.pl`, `clpqr_geler.pl`, `clpqr_dump.pl`, `clpqr_class.pl`, `clpqr_project.pl`, `clpqr_redund.pl`, `clpqr_ordering.pl`) with parallel pairs (`bv_q`/`bv_r`, `nf_q`/`nf_r`, `ineq_q`/`ineq_r`, `store_q`/`store_r`, `fourmotz_q`/`fourmotz_r`, `bb_q`/`bb_r`, `itf_q`/`itf_r`), vendored verbatim; the braces syntax `{X > 1}` is the reader's. CLP(B) is `clpb.pl`, vendored verbatim.

## 4. Grading

The SWI runner over `clpfd`, `clpqr` and `chr` test files; ProPuzzles and ProRosetta programs that load `library(clpfd)` (the `OUTSIDE_CLPFD` exclusion class is retired: Lon chose "Return all 251", CEO-1966); the design harness `test_design_clpr_chr_steps.sh --step N` for regression; `test_smoke_prolog.sh` and all eight smokes for a prelude change.
