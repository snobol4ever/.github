# FINDING s166 — THE EMITTED SHARED-PATTERN-GRAPH ROAD IS UNREACHABLE AT HEAD, THE INLINE-SET AND THE GRAPH-SET ARE THE SAME SET, AND 390 `.s` ARTIFACTS HAD BEEN LYING ABOUT IT

**Seat:** local, Claude Opus 5, CN front, 2026-08-19. **Trees:** SCRIP `22dc2f8c` · corpus `f5538e01`. **Provenance:** found while scoping CN-13 CONST-GRAPH rung 1 (Lon's order: *"FULL graph traversal with whole graph ZETA SPINE calculated when NOT using constant folding and use a LINKED graph; i.e. the PASS-THRU GLUE which has less baggage than today"*). Every number below is a live measurement on a pristine build, not a read of a committed artifact — which is itself the point of the finding.

## THE CLAIM

`proc_PAT$N` — the emitted, shared, four-port pattern graph with the CLASS D suspension protocol — **cannot be produced by any SNOBOL4 source program at HEAD.** It is not merely unused; it is unreachable.

## THE EVIDENCE

1. **0 of 59.** Of the 59 corpus programs whose COMMITTED `.s` contains a `proc_PAT$` graph, **zero** still emit one when recompiled at HEAD (each rc=0 with real output; `word4.sno`, `115_pat_fence_via_var_recursive`, `178_pat_recursive_star_list_zs2` spot-verified individually).
2. **No source shape resurrects it.** Swept `P = BAL` · `FENCE 'a'` · `SPAN(…) . W` · `ARB . W` · `BREAK(' ')`, each with two `*P` star-defer sites — the exact construct class the road exists for. Result: `proc_PAT$` = 0 in all five. The non-inlinable ones go to **`rt_defer_run_all`, the runtime blob INTERPRETER**; the inlinable ones inline.
3. **The builder is still wired.** `sno_pat_thunks_build(0)` is still called on the main path (`lower_snobol4.c:2834`), so this is not an unwiring — every graph it would build is suppressed by PT-2's `sno_fz_procname_is_dead` (*"all refs inlined, no `*name` consumers; proc_PAT graph is dead code"*).

## THE MECHANISM — WHY THERE IS NO MIDDLE TIER

**The fz table gates BOTH roads.** A name enters `g_sno_fz` only by passing `sno_pat_invariant` + the single-write/fz-safe sweep. `sno_fz_mark_defer` attaches a `PAT$N` procname **only** to fz-table names, and PT-2 then suppresses the graph unless that name has surviving `*name` consumers. The lowerer states the containment itself: *"inline-set ⊆ blob-linkage-set BY CONSTRUCTION"*.
So the population splits exactly two ways and nothing lands between them: **fz-qualified ⇒ inline-eligible ⇒ inlined** (PT-1, PAT-INLINE-ARBNO and CN-12 successively widened the inline set until it covered the fz set), and **not fz-qualified ⇒ no procname ⇒ interpreter**. The shapes inlining refuses (captures, FENCE, BAL) are the same shapes `sno_pat_invariant` refuses, so they never had a procname to link to in the first place. **The graph road's residents were consumed by inlining, one correct-and-gated widening at a time, and nobody decided to retire it.**

## WHAT THIS COSTS CN-13

- Rung 1 is **not** "re-link the shared graph". It is **"create the middle tier"** — a name that qualifies for a graph and is DELIBERATELY NOT inlined because it is a declared constant used at ≥2 sites — and only then link it. Defeating PT-2 for that class is step one.
- ⛔ **The revived road has had ZERO live coverage for many sessions.** No corpus program, no gate, no witness exercises the CLASS D emitted-graph protocol today; it has been bit-rotting unobserved. Reviving untested emission is the exact provenance of the B1c/B2c record-protocol crash classes already on this board. **Rung 1's first deliverable must be a witness that FORCES the road and proves the protocol green in both modes — a resurrection test — before one line of linkage is written. If that test fails, THAT is the rung.**
- The economics that motivate the rung are unchanged and were measured this session: 205 lines/site (dynamic) · **136 lines/site (today's substitution)** · ~5 instructions (target), exactly linear in site count. Of the 17 instructions a live defer site spends entering a shared graph, **13 are dynamic resolution** that a declaration makes unnecessary.

## THE SECOND FINDING — THE INSTRUMENT WAS LYING, AND THAT IS HOW THIS WAS ALMOST MISSED

The CN-14 regen owed at handoff rewrote **414 of 484 crosscheck `.s` artifacts, net −23,654 lines.** CN-14's own measured blast radius was **24 of 527** programs. **So ~390 artifacts were already stale before this session touched anything** — describing roads the compiler stopped taking sessions ago.
⛔ **This session's CONST-GRAPH design section was initially written FROM ONE OF THOSE STALE FILES** (`word4.s`), and its protocol reading — accurate for the file — described a road that no longer exists. It was corrected only because the road was then measured live. **`.s` = HONEST CURRENT OUTPUT decays silently between regens, and ASM-DIFF-FIRST is a law whose own instrument must be regenerated before it is trusted.** A dead road's artifacts keep testifying that it lives.
**Proposed standing law: regenerate before you diff.** Any session opening an asm-diff investigation regenerates the artifacts it is about to read, or reads only files it produced itself in that session.
