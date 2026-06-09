# HANDOFF — 2026-06-06 — OPUS48 — PROLOG-BB — PL-GZ-6B (QUERY-PREFIX SOFT-DISJ, TWO-SEGMENT QUERY FRAME)

## WHAT LANDED
The FULL PL-GZ-0 seed runs as ONE program in all three modes → `b c d b`:
`main :- ( path(a,Q), write(Q), nl, fail ; true ), firstpath(R), write(R), nl.` The 6-CUT handoff recipe, implemented verbatim. Admission extends gz4's whole-query `(G ; true)` soft-disj to the PREFIX form: disj at goals[0] of a LONGER query conj, RESTRICTED to arm0 ending in IR_FAIL — fail-driven, arm0 never succeeds, so NO arm0-success wiring exists (an arm0 that could succeed would need success-continues-to-B PLUS B-failure-redoes-INTO-arm0 wiring — declined, that is general-disj territory). The soft landing is the seed's `q1_ω: goto q2_α` literally: unwind(query mark) + jmp B0's α, a one-way jump — no CP survives the exhausted pump.

## FILES
- src/driver/scrip.c — (1) the per-goal builder + synth pre-scan factored OUT of `pl_gz_admit` into `pl_gz_build_goal` / `pl_gz_count_synth` (NO-DUP: one builder serves both segments; head/tail/synth_next/cslot via pointers; callees array shared — A and B live in the ONE query frame, ncells covers both). (2) outer detection: any gconj with goals[0]==softdisj is the outer; ngoals>1 ⇒ `outer2` (the prefix form); when outer2, arm0's LAST goal must be IR_FAIL or decline. (3) B extraction = outer goals[1..] built into `qf->β`; `qf->dval = 2.0` iff outer2 && headB (all-SUCCEED B degenerates to dval=1.0 — observably identical: soft sb=2 unwinds then jmps land_γ ≡ sb=1's unwind+ret 1).
- src/emitter/emit_bb.c — `flat_drive_gz_query` two-segment: `twoseg = (dval==2.0 && pBB->β)`; B labels `gzq%d_b%d_α/β`; B CELL_CALLs feed the same callees array; A's first-goal ω and the frame's bound ω = `soft_ω` (new label `gzq%d_sω`); A's last γ = B0 α (unreachable — arm0 ends in FAIL, bb_fail never takes γ); between segments ONE extra frame FILL (op_sa=1, op_sb=2, lbl_δ=B0 α) emits the soft landing; B wiring: B0 ω → hard land_ω, goal[i].ω → hb[i-1] backward chain, last B γ → land_γ; final landing FILL keeps op_sb=0 in twoseg (hard: def γ = rax=1+ret, def ω = unwind+rax=0+ret).
- src/emitter/BB_templates/bb_query_frame.cpp — NEW aspect op_sa==1 && op_sb==2: `def PORT_OMEGA; mov edi,[ζ+0]; call rt_trail_unwind; jmp PORT_DELTA` — no ret, the soft-fall CONTINUES into the query tail. One x86() concatenation, medium-invisible, jmp-δ idiom = bb_callee_frame's advance block.
- scripts/test_gate_pl_gz6b.sh — NEW gate (4 positives + 2 negatives; corrupt-proven: sb=2→1 corruption leaves soft_ω undefined → loud `as` failure on the full seed).
- .github/GOAL-PROLOG-BB.md — STATE watermark + the 6b ladder entry.

## CANON GROUNDING (per session instruction: read the Prolog sources for every construct dealt with)
gprolog (uploaded zip, src/): `Pl2Wam/syn_sugar.pl` `linearize` — `(P ; Q)` in a body LINEARIZES into a 2-clause auxiliary predicate, one clause per arm; `Pl2Wam/indexing.pl` — the LAST clause is emitted under `trust_me_else_fail`; `EnginePl/wam_inst.c` `Pl_Delete_Choice_Point` — trust DELETES the choice point (B ← previous CP). Therefore once the disjunction enters its last arm (`true`), NO CP remains; a later failure in the conjunction tail does NOT re-enter the disjunction. The seed encodes the same law (`q1_ω: goto q2_α` one-way). m3/m4 match canon AND the seed.

## LOGGED LATENT m2 DIVERGENCE (do not fix silently — PT-3/PT-4b/WAM-CP-9 precedent)
Probe `main :- ( p(X), write(X), nl, fail ; true ), q(w), write(never), nl.` with p(a). q(z).: canon (and m3/m4) print exactly `a`; **m2 prints `a a`** — on B's failure the m2 resume re-walk RE-ENTERS the exhausted soft-disj and re-drives the pump once more before failing. Same family as the documented ITE-commit oracle bug and the gz6 mid-cut resume gap → all three belong to **PL-GZ-7's m2-commit cluster** (the disj/ITE/cut resume re-walk family; fix = commit/exhaustion must be detected explicitly on resume, the cp_cut_away lesson). The gz6b gate's B-fail probe pins m3==m4==canon and does NOT compare m2 for that one shape; all other probes are m2==m3==m4.

## GATES AT HANDOFF (all green, counts byte-identical to 5d4aea9)
GATE-1 5/5 · 4/0/1-EXC · 5/5 — GATE-3 m2 115/115, m3 18/0/97-EXC, m4 105/0/10-EXC (no GATE-3 rung has the prefix shape within the other admission bounds; legacy counts frozen by construction) — gz2/3/4/5a/5b/5c/6/6b PASS — one_box PASS — pl_coupling PASS (ceilings 19/10/0/39; new boxes 0 control calls) — seg_byte/SL_B 0 — g_vstack 0 — Icon m2 12/12 (m3/m4 10/12, byte-identical pre/post via git-stash A/B).

## NEXT OPENER
PL-GZ-7 — ITE, paper §4.5 ifstmt template VERBATIM (bounded condition + frame gate). Sweeps the m2 commit cluster in one design: ITE-commit (`( a(X),X>=2 -> true ; X=0 )` → `2`, absorbs WAM-CP-9), the gz6 mid-cut pre-cut-generator resume gap, and the gz6b disj-resume re-walk above — all three are the resume re-walk failing to detect a committed/exhausted control node. Re-baseline audit of any rung that matched the buggy m2.

## LESSONS
- The two-segment frame is ONE extra FILL on the same node — the aspect pattern (gz_emit_callee's op_sa ladder) scales to inter-segment landings with zero new node kinds.
- Factoring the builder BEFORE extending admission (NO-DUP first) made the B segment a 3-line loop; the alternative (copy the 85-line loop) would have been the FORM-1 disease.
- The corrupt-proof came free: an aspect mismatch leaves a label allocated-but-undefined, and `as` is the loud gate — undefined labels cannot link, so a wiring corruption can never pass silently.
- gprolog's linearize is the cleanest statement of disj semantics: a disjunction IS a fresh multi-clause predicate; everything about CP lifetime follows from clause indexing. Worth keeping in mind for the general-disj rung.
