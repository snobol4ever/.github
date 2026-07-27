# FINDING-2026-07-27g — SN4 FLATDISP-5b/5c + FLATDISP-6 + ABORT-NODE + BRACKET-GATE (s193)

**Session:** s193 · **Date:** 2026-07-27 · **Author:** Claude Sonnet 4.6
**Repos:** SCRIP `b3996516` (bracket gate), `646e29ae` (feature sweep), `9edc982c` (census gate), `185e24f0` (5b/5c), `2932c4ee` (FLATDISP-6), `83114981` (ABORT-NODE), `b3996516` (BRACKET-GATE); corpus `7730a7b5`, `259b71e9`.
**Watermark:** m3 185/130 · m4 183/130 · DIVERGE=1 (W06_tab). Full recovery from s192 RED (m4 168/145 · DIVERGE=16).

---

## The directive

Lon: "Have each BB allocate its RESULT value, IF it has one and if it is used. Have each BB allocate its LOCAL STORAGE needs, IF it has any. Do it by one instruction, decrement RSP. Keep track of sliding offsets and index operands from RSP, not RBP. Continue this for every box and every construct until you hit a BRICK WALL and realize, oh I need a RBP stable base pointer for what I'm doing, so add the RBP/RSP dance to create the frame pointer going forward and roll it back on the way backward. Several constructs we know we'll want RBP is for a STATEMENT, FUNCTION and ARBNO and FENCE1 for pattern matching. We do not need to put much of anything at the RBP based part of the stack, 99.999% will be RSP based. ARBNO will have its housekeeping information about variable length children based off of RBP. Those are the only four I can think of. Continue."

---

## 1. The real s192 wall: arming coverage, not kind list

s192 classified `emit_graph_has_deep_arrival()` inside `emit_jmp_entry_for_proc` only. But the gates that READ `flat_deep_arrival` live on the **outer call-regime prologue arm** (`xa_flat.cpp` lines 382/383) — the path taken by outer `main` graphs. Those graphs never go through `emit_jmp_entry_for_proc`; they arm via `emit_jmp_entry_arm_region` directly. So outer mains inherited the cleared-0 value, emitted no rbp seed, and then `n11_match_fence1_α` executed `mov rsp, rbp` into the CRT caller's frame — test 058 fails both modes.

**Fix:** moved the classification call into `emit_chain`, the single choke point every graph emission passes regardless of kind. Null cfg → conservative 1. Per-emission write makes leaks from hand-armed callers (bb_pat_build) structurally impossible.

---

## 2. FLATDISP-5c: BOTH-MEDIUM — `xaf_deep()` unifies all six gates

Introduced `xaf_deep() = flat_deep_arrival || outer_nparams >= 1`. The six outer-frame rbp gate sites (TEXT anchor-leave, TEXT prologue save, TEXT prologue seed, TEXT epilogue reload, BINARY anchor-leave, BINARY epilogue success+fail reload) now all read the same predicate. The BINARY anchor-leave gate was entirely absent in s192 — that is why m3 held at 185 while m4 fell to 168 (BOTH-MEDIUM violation, exactly the failure mode RULES.md predicts).

The `nparams >= 1` conjunct: the ICNBENCH-ARGS param-0 bind stores through `[rbp+16]`/`[rbp+24]`. The s192 TEXT arm gated the seed on the raw field but stored through rbp unconditionally — latent, unhit because Icon mains carry scan/gen kinds (always deep). Unified predicate closes it.

---

## 3. FLATDISP-6: kind list narrowed by template census

Dropped from the deep list: `IR_MATCH_HEAD`, `IR_MATCH_ALTERNATE`, `IR_MATCH_SEQUENCE`, `IR_MATCH_ARB`, `IR_MATCH_RETRY`, `IR_MATCH_RELEASE`. Census result: comment-only or save/restore-of-caller-value (value-neutral without a seed). Match protocol rebalances rsp through the head snapshot at both exits.

`IR_MATCH_HEAD` was retained temporarily: TT_ABORT lowered to a bare `IR_GOTO` (no node in the graph), making abort-bearing statements classifier-invisible. A dropped HEAD cost exactly 170/171 (m4 183→181), the tripwire. Reintroduced HEAD; noted ABORT-NODE as the unlock.

---

## 4. ABORT-NODE

TT_ABORT had been lowering to `IR_GOTO` since before the gz5 parked file. The `IR_MATCH_ABORT` enum, template (`bb_match_abort.cpp`), and `flat_trivial_beta` case all pre-existed but the template was never linked in the Makefile and the dispatch case was absent. Three touchpoints needed:

1. **Lower site** (`lower_snobol4.c`): `IR_MATCH_ABORT` node, kill via ω, γ→kill defensively (TT_FAIL precedent).
2. **Dispatch case** (`emit.cpp` ~938): mirrors `IR_MATCH_FENCE1`.
3. **Drive arm** (`emit.cpp` ~1296): `op_off = -1`, `DRIVE_PAIR_RESET()`, `DRIVE_FILL`. No slot grant — FENCE0 grants a quad its template leaves unused; ABORT is truly operand-free.
4. **Makefile**: `bb_match_abort.cpp` added beside `bb_match_fence1.cpp`.

The box's β→ω is more manual-faithful than the goto. SPITBOL manual Ch. 9: "the FAIL pattern signals the failure of this portion of the pattern match, causing the pattern matcher to backtrack and seek other alternatives. Note the difference between ABORT and FAIL. ABORT stops all pattern matching." A β arrival = the matcher backing into ABORT = kills. The goto had no β surface at all.

With ABORT-NODE landed, `IR_MATCH_HEAD` was removed from the deep list. The crosscheck confirmed: 170/171 healed, W06_tab remains the sole diverge.

---

## 5. BRACKET-GATE

The `+40` slot in head's quad serves one purpose: bracket the ARBNO `zv()` borrow. ARBNO re-points rbp as its element-view register (`zv() = "rbp"` under ZC_FRAME_RSP). Head saves caller-rbp at `+40` before rbp gets re-pointed; release/replace restore it at γ. In a depth-static (no ARBNO/FENCE1/DEFER) graph, `zv()` is never re-pointed, so the save and both restores are provably dead.

Gated all four instructions on `_.flat_deep_arrival` (the same field the outer quartet reads). **Probe result:** simple inline match (`X 'B' :S(Y)F(N)`) compiles to **zero rbp references** — output correct in both modes.

---

## 6. rbp census gate (`test_gate_rbp_census_ratchet.sh`)

Three predecessor instruments each reported convergence the bytes contradicted:
- s184: patience-FC gate (measured a patience metric, not rbp presence)
- s188: `x86_fc_hit` subset gate (scored OWN+full-cell misses only; CROSS and OWN+window-only are correct-by-design AND still emit `[rbp+N]`)
- s192: raw `grep -cw rbp` (counted class D — scratch GPR uses — which no frame-pointer rung can ever remove)

The new gate: compiler sweep (never artifacts), class D excluded (`mov rbp, qword ptr [<non-rsp base> + N]`), manual ratchet. Baseline: ALL=251, CLASS_D=14, **NET=237**. Benchmarks with zero: arith_loop, eval_dynamic, eval_fixed, op_dispatch, string_concat, string_manip, table_access, var_access. Nonzero: fibonacci (26), func_call (26), func_call_overhead (26), indirect_dispatch (26) — all DEFINE-bearing; mixed_workload (51), roman (46) — DEFINE + patterns; pattern_bt (25), string_pattern (25) — patterns with FENCE/DEFER.

---

## 7. What is left on rbp and why

| Count | Population | Why rbp stays |
|-------|-----------|---------------|
| ~104 | DEFINE-bearing jmp-entry blobs | Jmp-entry arm seeds unconditionally (correct: those blobs contain FENCE/DEFER/ARBNO by construction today); FLATDISP-7 gates this once invariant blobs are frameless |
| ~119 | FENCE1/ARBNO/DEFER patterns | rbp IS the design: floor for fence, zv borrow for arbno, depth-immune watermark for defer |
| 14 | Class D scratch | `mov rbp, qword ptr [rax+24]` — rbp as a plain GPR destination; a ratchet that counts these cannot read zero (fourth mis-measuring instrument, identified and excluded) |

---

## 8. Next rungs

**(a) FLATDISP-5a — frameless invariant PAT$ blobs.** `xa_pat_blob_invariant_n`: emit invariant pattern inline, no PAT$ proc, no DT_P round-trip. Plausibly removes the 26-each in fibonacci/func_call/func_call_overhead/indirect_dispatch (DEFINE-bearing, jmp-entry seeded for containing FENCE/DEFER — but *invariant* blobs contain neither).

**(b) FLATDISP-7 — gate jmp-entry seed per-graph.** Once invariant blobs are frameless, the jmp-entry arm can check per-graph rather than seeding unconditionally.

**(c) rt_dcap_pump SIGSEGV** (`pattern_match.c:673`): `memcpy(copy, c->subj + e->saved_delta, len)` with garbage `saved_delta`≈2³². Blocking ~130 tests, pre-existing since s191. MONITOR-FIRST: 2-way monitor on `039_pat_any`.
