# HANDOFF — PST-PROLOG session 2026-05-16 (session 30/60)

## Repos & hashes
- one4all  @ `1efe311e`
- .github  @ `22974e55`
- corpus   @ unchanged from session start

## Goal worked: GOAL-PST-PROLOG.md

### What was done

**PST-PL-6d fix** (one4all `64948e82`) — prior session left HEAD unbuildable:
- The PST-PL-6d commit (8fee1957) accidentally dropped the `CODE_t *prolog_lower(PlProgram *pl_prog) {`
  function opening line, leaving its body as orphaned top-level code.
- Restored the signature.
- Fixed `src/lower/lower_pl.c` to handle parser-tree node types that differ from the Term* path:
  - `TT_QLIT` as 0-arity goals (`nl`, `true`, `fail`, `!`) — `lower_pl_stmt_node` was returning NULL
  - `TT_FNC("=", ...)` as unification — was falling through to generic `IR_PL_CALL`
  - `TT_FNC("+"/"-"/"*"/"//")` as arith in term position — `lower_pl_term_node` was returning NULL
- smoke_prolog restored: **0/5 → 5/5**

**PST-PL-6e** (one4all `1efe311e`, .github `22974e55`):
- `src/frontend/prolog/prolog_parse.h`: added `var_names`/`var_terms`/`nvar` fields to `PlClause`
- `src/frontend/prolog/prolog_parse.c`: removed `next_slot` from `VarScope`; `scope_get` now creates
  all vars with `saved_slot = -1`; `parse_clause()` snapshots scope entries into clause before return
- `src/frontend/prolog/prolog_lower.c`: `lower_clause()` and `assign_clause_anon_slots()` use the
  snapshot for named-var slot pre-pass (sequential 0,1,2,...); ASSIGN_ANON walk fills remaining
  `-1` slots (anonymous vars) above named slots. `TRSlotMap` remains canonical for tree_t path.
- `lower.sc`: no change needed — slot assignment is internal C lowering; tree_t shape unchanged.

## Gate results at handoff
- smoke_prolog:        PASS=5  FAIL=0
- smoke_scrip_all:     PASS=2  FAIL=0
- crosscheck_snobol4:  PASS=6  FAIL=0
- crosscheck_prolog:   PASS=127 FAIL=0 SKIP=5 ORACLE_MISS=11

## Next step: PST-PL-6f
Delete all `Term*`-returning code paths from `prolog_parse.c`. Specifically:
- Delete `lower_term()` call sites replaced by tree_t path in 6d (non-DCG clauses
  now go through `lower_clause_from_tree`, so `lower_clause` is DCG-only)
- `Term` type survives only as a runtime type (unification), not as parse output
- DCG path (`cl->tr == NULL`) still uses Term* — do not delete DCG infrastructure
- Gates: smoke_prolog, crosscheck_prolog, crosscheck_snobol4, smoke_scrip_all_modes

## Notes for next session
- Upstream pushed two commits during our session (IJ-SCAN-NULSAFE, IJ-CSET-BINOPS) — rebased cleanly
- crosscheck_prolog broker was 20/49 pre-session, now 17/49 — regression is from Icon work (IJ-*),
  not from PST-PL changes. Needs separate investigation (not PST-PL-6f scope).
- ORACLE_MISS=11 is stable — these are corpus files where all 3 modes agree but differ from .ref;
  frontend gap, not a regression.
