# FINDING 2026-08-17 s132 — THE STALL IS `x86_rsp_slide_known() { return 1; }`

**Lon, in-chat, s132 (the ruling that produced this finding), verbatim in substance:** *"Scrutinize the entire
method/technique you are using to determine offsets. Is it not just a matter of tracking the sequence of
execution of each BB in addition to how much RESULT and how much LOCALS each BB needs. And then a situation
will happen where the offset is unknown since an UNKNOWN VARIABLE number of BB's inject between the read site
and the write site of the RESULT, or that on BETA label BB's have accumulated so in order to even access a
LOCAL it must reach over an UNKNOWN number of unknown BB type boxes. These TWO problems are the ONLY ones I
know. You should not make a LIST beforehand. The list becomes the new code with that exception handled."*

## THE MODEL IS RIGHT, AND IT IS THE STANDARD RESULT

Offset determination over the BB graph is the classic **static stack-height** property: if every program
point has a depth identical on all paths reaching it, then every cell's address is
`(depth at use) − (depth at allocation)` and RSP-relative addressing is TOTAL. It fails in exactly two ways,
and Lon's two cases are those two ways, exhaustively:

| Lon's phrasing | Standard name | Where it bites here |
|---|---|---|
| unknown variable number of BBs inject between the RESULT's write site and its read site | dynamic-count allocation between def and use (backedge accumulation) | unbounded ARBNO instance growth |
| at a BETA label, BBs have accumulated, so reaching a LOCAL crosses an unknown number of unknown boxes | join/resume at a point whose height is not path-invariant | suspend/backtrack re-entry at foreign depth |

**There is no third case**, and — the part that matters — **both have the SAME cure**: address off a base that
does not move. That is what a frame pointer is for; it is why production compilers force frame-pointer
addressing the moment `alloca` enters a function. So this is ONE analysis with ONE exception handler, not a
taxonomy of special cases.

## THE ROOT CAUSE, IN ONE LINE

`src/templates/x86_asm.h:582`:
```cpp
inline int x86_rsp_slide_known() { return 1; }
```

**The lattice has no ⊤.** The one function whose job is to answer "is the depth statically known at this
point?" is hardwired to *yes, always*. Consequently `x86_frame_off`'s false branch
(`return ... : -1`, the "unknown depth" sentinel) is **DEAD CODE — the ternary cannot take it.**

The deletion was deliberate and its own comment states the reasoning and the consequence (s53,
"RSP-ONLY-EVERYWHERE"): *"Classes whose depth truly diverges across a dynamic edge (unbounded ARBNO instance
growth, suspend re-entry at foreign depth) now fail HONESTLY at run time and go on the failure list, per the
s53 ruling."*

⛔ **THAT COMMENT NAMES LON'S TWO EXCEPTION CLASSES VERBATIM AND RULES THAT THEY BE LISTED RATHER THAN
HANDLED.** Every session since has been working that list one entry at a time. **This finding is the
inversion of the s53 ruling: the list becomes the code.**

## WHY THIS EXPLAINS THE WHACK-A-MOLE, MECHANICALLY

With no ⊤ available, "should this cell be re-homed to an immovable base?" cannot be COMPUTED, so it has been
APPROXIMATED, per construct, by hand, once per session. Every one of these is a hand-written estimator of the
same missing predicate:

- `leaf_frame_candidate()` (s130/s131) — which leaf ops may frame
- `blob_choice_rbp_scan()` / s128's admission `_nc==1 ∧ !_fn ∧ !_lf ∧ registry-demand-framed ∧ !blob_wire_clobber_scan()`
- the s130 "8-byte usable-window law" (d ∈ {0,4}, d=8 is the neighbour's floor)
- the s131 BAL decline (+0/+4/+8 spends three words, so refuse)
- s127's retracted "frame zero-demand blobs by shape" (5 SEGV movers)
- s131b's reverted registry-handle re-base (broke `clob_altarm_trueinline_grn`)

Each is correct on the corner it was measured against and wrong on the next corner, **because none of them is
the property; they are all estimates of it.** That is the stall, and it is why the cadence is one corner per
session and cannot improve by working corners faster.

## THE MACHINERY FOR THE REAL PREDICATE ALREADY EXISTS — SCOPED TO ONE CONSTRUCT

`op_stmt_dyn` (`emit.h:624`) already IS Lon's case (a), correctly modelled and correctly cured:
1 = *"this statement contains a FRAMELESS_K-armed ARBNO whose committed growth (kk+16 per instance) makes the
statement extent COMPILE-TIME INDETERMINABLE"*, and the cure is exactly the depth-immune base —
`lea rsp,[___+op_zgpop]`, which *"restores the pre-claim frontier at ANY dynamic depth"* where the static
`add rsp,K` under-frees by the growth.

**So the correct answer is already implemented — for ONE construct — and proven to work there.** The defect is
scope, not concept: it is a per-construct latch instead of a graph property.

⛔ **AND THE β SIDE HAS NO VERDICT AT ALL.** `op_stmt_dyn` reaches exactly two files (`x86_asm.h`,
`bb_match_arbno.cpp`). **Nothing at a β port ever asks whether the depth is knowable.** That is precisely why
`IR_MATCH_DEFER`'s β emits a bare `jmp qword ptr [rsp]` (witness `corpus/probe/deferclob/`, s132) three lines
from `IR_MATCH_ALTERNATE`'s `mov rax,[rsp+8]`: two private layout assumptions on one shared region, neither
consulting a depth verdict, because no such verdict exists on that side.

## WHAT THIS RETIRES AND WHAT IT REPLACES

**RETIRES** the s132 ζ-ONE rung ladder as previously written (U-2..U-5 as "unify accessors, migrate families
under whitelists"). Unifying the accessors was necessary plumbing and U-0/U-1 stand (`5e35e6c2`, 62/62
byte-identical both arms), but **migrating families under whitelists is more of the disease**: the whitelists
ARE the approximations above.

**REPLACES IT WITH** restoring the lattice:
1. **Restore ⊤.** `x86_rsp_slide_known()` becomes a real per-point predicate, not `return 1`.
2. **Compute it as a forward dataflow** over the BB graph: depth ∈ ℕ ∪ {⊤}; per-BB contribution = its RESULT +
   LOCALS carve (`zls_node_bytes` / the existing zd pricing already supplies the per-node amounts); join =
   equal ⇒ that depth, unequal ⇒ ⊤; any backedge whose target depth ≠ entry depth ⇒ ⊤ for everything live
   across it. This is textbook and is the SAME analysis a JVM verifier runs for stack heights.
3. **One exception handler, both cases:** ⊤ ⇒ the cell is homed on the immovable base (RBP tier) instead of
   RSP. No list, no per-construct admission gate. `zone_ref` (U-1, already landed) is where that decision is
   already spelled once — it takes `rbp_off != -1`, so it needs no change; the PLANNER supplies the verdict.
4. **Delete the estimators** as the computed predicate subsumes each, one at a time, each deletion gated on
   its own witness set going green (leafsib, clobarm, deferclob, altdepth, arbnostore, seam, arbnofence).

## ⛔ HONEST ESTIMATE — WHY THIS IS NOT "MINUTES"

The ANALYSIS is small: a forward dataflow with a two-element-plus-⊤ lattice over an existing graph whose
per-node byte amounts are already computed. That part is hours, not days, and Lon is right that it should
never have been a multi-session grind.

**The CURE side is the measured risk, and it has already failed once under measurement.** Homing a cell on
RBP requires the RBP frame geometry to be right, and s131b attempted exactly that re-base (`frame_slot_off`
`32:64 → 40:72`) and **broke the green control `clob_altarm_trueinline_grn`** — reverted same-session under
GATE-BEFORE-LAND. Its diagnosis, still unverified: the standing (rc 1) head/carve geometry does not match the
blob-derived cell map. **So restoring ⊤ will correctly classify MORE cells as needing RBP than the frame is
currently shaped to hold**, and the standing-carve re-derivation
(`emit_match_begin_rbp` / `emit_match_begin_frame_extra`) is a prerequisite, not a follow-up. Sequencing that
ignores this will reproduce s131b at larger blast radius.

## NEXT RUNG — IN THIS ORDER
1. **Re-derive the standing head/carve geometry** (the s131b blocker) so an RBP home exists for every cell the
   restored predicate will classify ⊤. Gate: `clob_altarm_trueinline_grn` ON-arm — the named discriminating
   witness that failed s131b — plus leafsib 6/8 and clobarm unmoved.
2. **Land the dataflow behind a killswitch**, default OFF byte-identical, reporting only: for every cell,
   ⊤-or-depth, plus a census of how many cells change classification vs today's estimators. **That census is
   the falsifiable prediction**: it must explain the existing red witnesses (deferclob, leafsib_arb/bal,
   altdepth, clobarm) as ⊤ cells today spelled against RSP.
3. **Flip consumption on**, one witness family at a time, deleting the estimator each family retires.
4. Beauty re-measured at each step; expect further blockers behind this one — it is the ADDRESSING model, and
   M1 may also need the record-layout half (deferclob's two private record shapes) which is layout, not depth.
