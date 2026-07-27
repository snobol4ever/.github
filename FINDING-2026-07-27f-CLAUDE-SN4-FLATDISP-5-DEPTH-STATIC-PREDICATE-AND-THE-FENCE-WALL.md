# FINDING 2026-07-27f — SN4 FLATDISP-5: the depth-static predicate, the rbp class partition, and the FENCE wall

**Session s192. Status: RUNG INCOMPLETE — mode-4 is RED and left red by Lon directive ("Do not revert anything, we are moving forward").**
**Baseline re-proven fresh on a clean clone BEFORE any edit: m3 185/130 · m4 183/130 · DIVERGE=1 (W06_tab) — matches the s191 cursor exactly.**
**Tree after this session: m3 185/130 (UNCHANGED) · m4 168/145 · DIVERGE=16. The 15 newly-failing m4 programs are ALL fence/abort programs.**

## 1. Lon's directive

> "Have each BB allocate its RESULT value, IF it has one and if it is used. Have each BB allocate its LOCAL STORAGE needs, IF it has any. Do it by one instruction, decrement RSP. Keep track of sliding offsets and index operands from RSP, not RBP. Continue this for every box and every construct until you hit a BRICK WALL and realize, oh I need a RBP stable base pointer for what I'm doing... Several constructs we know we'll want RBP is for a STATEMENT, FUNCTION, and for ARBNO pattern matching."

The predicted walls were STATEMENT, FUNCTION, ARBNO. **The measured wall is a fourth: FENCE.**

## 2. THE rbp CENSUS IS FOUR DIFFERENT THINGS, AND ONE OF THEM IS NOT A FRAME REFERENCE

The 323 residual rbp refs (s188's live metric, re-measured identically this session) are NOT one population. Classifier: `/tmp/rbpc/classify.py` shape — regex-partition every rbp line in the 16 benchmark `.s` files.

| Class | Refs | What it is |
|---|---|---|
| **A** seed / save / restore / teardown | 150 | `mov rbp,rsp` + `mov [rsp+K-8],rbp` + `mov rsp,rbp` + `mov rbp,[rsp+K-8]` — pure ceremony, rbp ≡ rsp at the seed |
| **B** `lea rsp,[rbp+kt]` / `mov rbp,[rbp+kt-8]` / push | 60 | genuine activation unwind from dynamic depth |
| **C** `[rbp+k]` data refs | 99 | the housekeeping record itself (result DESCR at slot 0; fence watermark at +40/+48) |
| **D** `mov rbp, qword ptr [rax+24]` | 14 | **rbp used as a plain scratch GPR — NOT a frame reference at all** |

⚠ **CLASS D MEANS EVERY rbp-COUNT GATE OVER-REPORTS.** 14 of 323 (4.3%) are a general-purpose register doing general-purpose work. Any future gate that "ratchets on compiler-output rbp count" (s188 next-rung (d)) MUST exclude class D or it can never reach zero and will look permanently stalled. This is the THIRD time an instrument in this ladder has mis-measured its own target (s184 patience-measuring FC gate; s188 FC gate counting a subset; now the raw rbp census counting non-frame rbp).

## 3. THE PREDICATE — `flat_deep_arrival` (LANDED, uncommitted at time of writing)

`emit.h`: `int flat_deep_arrival;` **appended at struct end per the s141 ABI law.**
`emit.cpp`: `emit_graph_has_deep_arrival(g)` — set beside `flat_gen` in the jmp-entry arm, cleared with it.

Semantics: 1 = some γ/ω arrival in this graph can land BELOW the activation base, so the frame-base restore must be rbp-absolute. 0 = DEPTH-STATIC: every arrival lands with rsp == base by LIFO balance, and the entire rbp quartet is deleted.

**CONSERVATIVE BY CONSTRUCTION:** null graph and every unlisted kind fall through to 1 (= today's behaviour). A miscategorised new kind degrades to correct-and-slower, never to wrong.

**NOT KEYED ON LANGUAGE** (RULES.md NO-LANGUAGE-SENTINEL). A SNOBOL4 graph qualifies because it happens to contain none of the deep-arrival kinds, not because it is SNOBOL4; an Icon graph containing none would qualify identically.

## 4. PROVENANCE — THE SOURCE ALREADY SAID SNOBOL4 DOES NOT NEED THIS

`xa_flat.cpp:448`, verbatim, on why the rsp-relative reads were retired:

> "The old rsp-relative reads ([rsp+0/8], [rsp+kt-24/-16], lea rsp,[rsp+kt]) rode the every-ω-pops GUARDED ASSUMPTION that arrivals land with rsp == base — **true for SNOBOL4's determinate procs, FALSE for Icon**: `return expr` from inside nested generator/scan depth arrives DEEP."

**SNOBOL4 has been paying the rbp-absolute epilogue across every benchmark to serve Icon's deep-arrival case.** The arm is shared; the cost is not.

## 5. MEASURED WIN (gate on, TEXT arm only)

**323 → 227 rbp refs (−96, −29.7%).** **EIGHT of sixteen benchmarks went to LITERALLY ZERO rbp:** arith_loop, eval_dynamic, eval_fixed, op_dispatch, string_concat, string_manip, table_access, var_access. Their frame pointer was seeded, saved, restored and torn down without a single read.

The depth-static exit needs no replacement instruction: `add rsp, Kt` was ALREADY in the TEXT epilogue (`xa_flat.cpp` ~595). Teardown collapses to `mov eax,1 / xor edx,edx / add rsp,Kt / ret`. rbp becomes a free GPR for the whole activation.

## 6. THE BRICK WALL — FENCE, AND THE TRIPWIRE FOUND IT UNAIDED

Gating without fence in the deep-arrival family broke **exactly 15 mode-4 programs, every one a fence/abort program and nothing else**: 058/061/062/067/068/069/100/101/103/104/105/107/173 `_pat_fence_*`, plus 170/171 `_pat_abort_*`.

The cause was already on record in TWO places before this session:
- FORTH conversion ledger: `IR_MATCH_FENCE1` = **"NO fc_geom BY DESIGN — the watermark quad must stay `[rbp+off]` (depth-immune) because the σ glue reads it at the dynamic post-P depth."**
- `bb_match_fence1.cpp:37`: **"rbp IS the activation's dynamic-ζ floor."**

A fence seals a match at whatever depth the preceding pattern left — **its arrival depth is dynamic BY CONSTRUCTION.** Same wall as a generator resumption, reached from the pattern side.

## 7. ⛔ WHY THE FIX DID NOT TAKE — THE PREDICATE IS AT THE WRONG GRANULARITY

Adding `IR_MATCH_FENCE1` + `IR_MATCH_ABORT` to the family: **no change** (168/145, DIVERGE=16).
Additionally adding the whole backtracking match family (HEAD, ALTERNATE, ARBNO, ARB, DEFER, RETRY, RELEASE, SEQUENCE, CALLOUT, VALUE): **still no change.**

**ROOT CAUSE:** the fence lives inside the `PAT$0` blob, which is a SEPARATE GRAPH. The outer statement graph contains no fence node, so it still classifies depth-static — while the depth leak crosses the σ glue from callee blob to caller. `emit_graph_has_deep_arrival` is per-graph; **depth-staticness must PROPAGATE from callee blobs to their callers.** That is a different and larger design than the one built here.

Verified on `105_pat_fence_empty.sno` (`X POS(0) FENCE(eps) LEN(2) RPOS(0)`, eps = LEN(0)): PAT$0 carves `sub rsp,80`, saves rcx/rdx wires, does the rbp dance, then reads the fence watermark at `[rbp+40]`/`[rbp+48]`, and exits `lea rsp,[rbp+80]`.

**BOTH-MEDIUM WAS NEVER SATISFIED EITHER:** only the TEXT arm was gated, which is exactly why mode-3 is untouched at 185/130. The BINARY twins (`xa_flat.cpp` ~162, ~202, ~283, ~448-460) are UNGATED. Per RULES.md BOTH-MEDIUM MANDATORY this rung cannot be called done in any form until they are.

## 8. LON DIRECTIVE ON THE PAT$ BLOB (s192, NOT YET BUILT)

> "Ensure the PAT$0 blob invariant pattern DOES NOT use RBP. It needs no prologue or epilogue as far as I know."

**`xa_pat_blob_invariant_n` DOES NOT EXIST IN THE TREE** — grep of `xa_flat.cpp` + `emit.cpp` = 0. It is a *designed but unbuilt* rung named in the s191 cursor ("FLATTEN INVARIANT PAT$N ... emit inline, no PAT$ proc, no DT_P round-trip"). Making an invariant PAT$ blob frameless is NET-NEW CONSTRUCTION, not a gate to flip. It is also plausibly the RIGHT fix for §7: a frameless invariant blob cannot leak depth across the σ glue because it has no frame to leak.

## 9. NEXT RUNGS, IN DEPENDENCY ORDER

- **(a) FLATDISP-5a — PAT$ BLOB FRAMELESS (Lon s192, the named directive).** Build `xa_pat_blob_invariant_n`; emit the invariant pattern inline with no prologue/epilogue, no DT_P round-trip. Likely subsumes (b).
- **(b) FLATDISP-5b — CROSS-GRAPH DEPTH PROPAGATION.** A caller is depth-static only if every blob it transfers into is. Needs a callee→caller pass over the chain BFS; today's predicate is per-graph and therefore blind to §7.
- **(c) FLATDISP-5c — BINARY TWINS.** Gate `xa_flat.cpp` ~162/202/283/448-460. BOTH-MEDIUM MANDATORY; nothing here is landable without it.
- **(d) FIX THE rbp GATE TO EXCLUDE CLASS D** (§2) before wiring any rbp-count ratchet, or it can never read zero.

## 10. ARTIFACT REGEN DELIBERATELY NOT RUN — SAY IT PLAINLY

RULES.md handoff step 4 mandates the three `.s` regen sweeps when codegen is touched. **They were NOT run this session, deliberately.** Mode-4 is RED (183→168); the sweeps would bake a known regression into the benchmark, feature and demo corpora across two repos, and unwinding three committed artifact sets is far more expensive than regenerating them once the rung is green. **This is a deviation from the letter of step 4 and is recorded here rather than hidden.** Run all three the moment m4 returns to ≥183.

## 11. LIMITATION

`emit_graph_has_deep_arrival` is conservative in the RIGHT direction for unlisted kinds, but its conservatism is per-graph and therefore does NOT cover the cross-graph case that actually broke — being safe about kinds it has never seen bought nothing against a leak it was structurally unable to see. **A predicate can only be conservative about the axis it is defined on.** Do not read §3's "conservative by construction" as a general safety claim; it is a claim about kind coverage only.
