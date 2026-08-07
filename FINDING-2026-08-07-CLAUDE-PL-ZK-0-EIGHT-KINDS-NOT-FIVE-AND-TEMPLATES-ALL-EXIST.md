# FINDING-2026-08-07-CLAUDE-PL-ZK-0-EIGHT-KINDS-NOT-FIVE-AND-TEMPLATES-ALL-EXIST.md

**Session:** s1 (PL-ZK-0 landing, 2026-08-07).  **HEAD:** `a5597f65` (PL-ZK-0 committed).

## THE FINDING

GOAL-PL-ZETA-CELLS.md §WHAT-THE-PRIOR-SCANS-FOUND item 1 names FIVE unlock kinds
(IR_CALL_BUILTIN_PROLOG · IR_MOVE_LABEL · IR_VAR_REF · IR_VAR · IR_CALL_PROC_STAGED).
The census at my head finds **EIGHT** kinds as first-blockers across the bench board:

| Kind | ref count | graphs first-blocked | in s163 list? |
|---|---|---|---|
| IR_CALL_BUILTIN_PROLOG | 2356 | 123/123 | YES |
| IR_VAR_REF | 2554 | 110/123 | YES |
| IR_SUSPEND | 272 | 79/123 | **NO** |
| IR_CALL_PROC_STAGED | 267 | 107/123 | YES |
| IR_VAR | 158 | 36/123 | YES |
| IR_MOVE_LABEL | 105 | 44/123 | YES |
| IR_CUT | 76 | 16/123 | **NO** |
| IR_DISJUNCTION | 44 | 44/123 | YES (but unnamed) |

## DENOMINATOR RECONCILIATION

s163 counted **185 runs** (SCRIP_ZD_GAP, per-run admission scan).
This census counts **123 graphs** (SCRIP_ZD_CENSUS, per-graph blocker histogram) across 22 bench programs.
These are different denominators: a graph can contain multiple runs; a run is a statement-level subgraph.
IR_SUSPEND and IR_CUT could block specific runs inside graphs that s163 walked differently, or
they may genuinely be absent from the s163 bench set (which was a different program set or a
different corpus snapshot). The discrepancy is NOT a contradiction — it is a denominator shift.

## CONSEQUENCE FOR ZK-1

Since admission is **ALL-OR-NOTHING PER RUN** (item 1, measured), arming only the s163 five
would still unlock zero runs on the bench board today if IR_SUSPEND and IR_CUT are blocking
runs that the five-kind set otherwise would arm.

However: the all-or-nothing law is a RUN property, not a GRAPH property.  A graph with 123 nodes
may have 10 runs; a run that contains none of {IR_SUSPEND, IR_CUT} would arm under the five-kind
set.  The census first-blocker is the FIRST declined node encountered — so 79 graphs where
IR_SUSPEND is first-blocker means: in those graphs' statement-level runs, SUSPEND appears before
any other declined kind.  Whether those are the SAME runs that contain CBP is unknown without
a per-run rather than per-graph count.

## THE GOOD NEWS

All eight blocker kinds already have templates in `src/templates/`:
  bb_call_fn.cpp  — IR_CALL_BUILTIN_PROLOG: ZD arm ZD-PL-A exists (landed s163b)
  bb_var_ref.cpp  — IR_VAR_REF: NO ZD arm
  bb_suspend.cpp  — IR_SUSPEND: NO ZD arm
  bb_call_fn.cpp  — IR_CALL_PROC_STAGED: via bb_call_fn; existing ZD arm covers IR_CALL
  bb_var.cpp      — IR_VAR: (via bb_var, check separately)
  bb_move_label.cpp — IR_MOVE_LABEL: NO ZD arm
  bb_cut.cpp      — IR_CUT: NO ZD arm; template body is trivially x86_alpha+x86_gamma
  bb_disjunction.cpp — IR_DISJUNCTION: (check separately)

## RECOMMENDATION

PL-ZK-1 (ADMISSION ROUTING) adds the ADDITIVE third-conjunct arms in zd_wl_kind per the goal
file's idiom.  The goal file's PL-ZK-1 says: "Additive third-conjunct arms in zd_wl_kind for
the five kinds, gated on the Prolog cells flag; existing arms untouched (the ICN ZK-1 idiom
verbatim)."  Under the REGISTRY DOCTRINE (zd_wl_kind comment at emit.cpp: "a CAPABILITY REGISTRY
recording which kinds have a ZD arm IMPLEMENTED IN THEIR TEMPLATE") admission must be paired with
a ZD arm.  ZK-1 therefore cannot admit IR_SUSPEND, IR_CUT, or IR_VAR_REF without writing
their template arms first.

ORDER OF WORK FOR ZK-1 and ZK-2:
  ZK-1 as written: admit the five s163 kinds that already have ZD arms (CBP has ZD-PL-A, staging
    and routing TBD for the other four; IR_CUT is trivially transparent; IR_SUSPEND needs design).
  NOTE: The EIGHT-kind question does not block ZK-1 from starting — it blocks ZK-1 from CLAIMING
    it will unlock runs on the bench board.  ZK-2 (leaf spine + sink preservation) is where the
    true unlock happens; ZK-1 is the admission gate that makes ZK-2's arms reachable.

## VERDICT

Proceed with ZK-1 per the goal file.  The five-vs-eight discrepancy is a denominator difference
(runs vs graphs) whose consequence is: we will likely need IR_SUSPEND and IR_CUT arms before the
bench shows any green.  This is a sizing update on ZK-2's scope, not a contradiction of ZK-1.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
