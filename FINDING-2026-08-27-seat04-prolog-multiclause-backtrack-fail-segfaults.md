# FINDING: multi-clause backtracking through `fail` SIGSEGVs (rc=139)

**Seat:** seat04 · **Date:** 2026-08-27 · **Found while working:** `prolog-unify-var-compound-segv` (unrelated — this is a different crash, filed rather than absorbed, per row-factory convention)

## Witness

```prolog
:- initialization(main).
fact(a). fact(b). fact(c).
main :- fact(X), write(X), nl, fail ; true.
```

Expected (SWI/GNU Prolog semantics, and what `test_smoke_prolog.sh`'s `clause` case asserts): prints `a`, `b`, `c` (one per line) via backtracking over the three `fact/1` clauses, then succeeds via `; true` once `fail` exhausts them.

Actual: `rc=139` SIGSEGV, in all three modes (m2/m3/m4 — confirmed via `test_smoke_prolog.sh`).

## Pre-existing, not caused by the unify fix landed this session

Control-arm tested: `git stash` (reverting `src/templates/bb/bb_call_fn.cpp`'s `sink_trailpush` fix) → rebuild → same crash, identical shape. Confirmed on unmodified `f67f851a` (pre-session HEAD) as well as post-fix HEAD. This is an independent, pre-existing defect.

## Partial characterization

`gdb -batch -ex run -ex "bt full"` lands with `rip` in an unmapped/unsymbolized address (`0x00007fffaae00989`, no symbol table info), and the "backtrace" above it is garbage stack words, not real frames — consistent with a corrupted computed-jump (choice-point resume address, or similar), not a simple null-pointer dereference like the unify bug this session fixed. Not further isolated — this needs its own ASM-diff-first pass (minimal ablation: does a single extra clause / a single backtrack via `fail` trigger it, or is `;`/`true` implicated too?).

## Scope note

This is NOT the same mechanism as `prolog-unify-var-compound-segv` (that was a register clobber in the `$unify` fast-path inliner, `rc=139` with a clean, symbol-resolved crash at a null-pointer deref). This one lands in unmapped memory — likely a choice-point / backtracking control-flow bug specific to multi-clause resolution. Minted as its own row rather than folded in, per LINKS convention (row-factory: found in one row, filed as a fresh row).
