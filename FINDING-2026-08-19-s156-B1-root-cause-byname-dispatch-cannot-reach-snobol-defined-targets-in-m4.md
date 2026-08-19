# FINDING 2026-08-19 s156 (HQ) — B1 ROOT-CAUSED: m4's BY-NAME DISPATCH CANNOT REACH SNOBOL-DEFINED TARGETS. BEAUTY'S "Parse Error" IS TOTAL, AND THE OPSYN-GRAMMAR THEORY IS DEAD.

## THE WITNESS (minted: `corpus/probe/b1/b1_opsyn_binary_snodef.sno`, 7 lines)
    DEFINE('RED(A,B)') ... RED = A '+' B ... OPSYN('&', 'RED', 2) ... X = 'l' & 'r' ... OUTPUT = X
- **oracle (sbl)**: `l+r` · **m3**: `l+r` · **m4**: EMPTY, rc=0 — silent statement failure.

## THE MECHANISM — the code names its own gap
`core.c core_call_registered_fn` (the s10 OPSYN operator dispatch): *"Returns 0 when the name is
absent or carries no C fn (**SNOBOL-defined synonym targets are a follow-on**)."* The follow-on was
never built. The m4 emission routes the OPSYN'd operator through a by-name site carrying the literal
`"&"` (`.Lbynamefnzd23` in the witness .s); the chain finds no C fn behind the alias and returns 0 →
the statement fails silently. m3's in-process route resolves the DEFINE'd target; m4's cannot.

## WHY THIS IS B1 — measured, all guard-independent (identical at SCRIP_DEFER_BETA_GUARD=0)
- beauty's grammar engine IS OPSYN dispatch: `OPSYN('~','shift',2)` + `OPSYN('&','reduce',2)`
  (semantic.inc:7-8). Every rule evaluation nulls out, so the parse tables never act.
- The wall is TOTAL: beauty m4 Parse-Errors on its FIRST input line — the bare label `START` —
  and on `X = 1` fed as the whole input. Not statement-class-specific. Not the compile-side
  grammar (SCRIP compiles beauty's `&`-expressions fine — 12.8MB .s, runs clean since B2b).
- FALSIFIED: "SCRIP lacks binary OPSYN support" (candidate #1 since s145) — parsing and m3
  dispatch are green; the gap is ONLY the m4 by-name → SNOBOL-defined-target hop.

## THE SAME MISSING MECHANISM, SECOND WITNESS
`benchmarks/snobol4/indirect_dispatch.xfail` (seat, 2026-06-20): `$FN(X)` with FN='ADD1' — oracle
errors (022), **m4 produces EMPTY output**. Indirect by-name calls to SNOBOL-defined functions and
OPSYN'd operator aliases to SNOBOL-defined functions are one dispatch chain. One fix, two cures
(and the xfail's disposition should be re-graded after it).

## FIX DIRECTION (next slice, HQ-owned — beauty-critical path)
The follow-on the s10 comment promises: when the by-name chain finds the alias target is a
SNOBOL-DEFINED function, trampoline into generated code (the machinery exists for defers/thunks:
rt_proc_call_open_fnret / CALL2BB / EXPR$ collect). Gate with the standard ladder + this witness
pair (opsyn witness green m4, xfail re-graded) + beauty m4 statement-count movement.
